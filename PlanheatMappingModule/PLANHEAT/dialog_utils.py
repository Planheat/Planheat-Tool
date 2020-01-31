from pathlib import Path
import pandas
import os, shutil
import csv
import subprocess
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QCursor, QDoubleValidator, QBrush, QGuiApplication
from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem, QMessageBox, QMenu, QAction, QProgressDialog, QApplication, QWidget, QTreeWidgetItemIterator

from .algorithm_node_popup import AlgorithmNodePopup
from .supply_algorithm_node_popup import SupplyAlgorithmNodePopup
from .algorithm_utils import valid_structure, run_all, set_progress, run_algorithm_for_node, get_crop_and_straw_yield_value, get_crop_yield_value, \
    calculate_straw_yield, clear_all_caches, get_buffer_extent_and_crs
from .database_utils import get_algorithms, get_trees, copy_tree_into_new, initialize_tree_from_db, get_tree_by_id, get_node_file_by_id, save_tree, delete_tree, \
    get_algorithm_by_id_and_default, get_energy_production_factor, get_algorithms_for_type, get_next_node_id, get_tooltip, get_node_map_selection_by_id
from .input_node_popup import InputNodePopup
from .io_utils import get_shape_attributes_list, is_shape_file_polygons, get_temp_folder_name
from .layer_utils import load_file_as_layer, load_open_street_maps
from .load_tree_popup import LoadTreePopup
from .models import Parameter, TreeNode
from .node_utils import set_node_icon, get_node_data, add_node, find_parent_node, has_checked_input_file_node_children, delete_node, is_input_file_node, count_items
from .result_popup import ResultPopup
from .result_utils import PlotCanvas, fill_sector_table, fill_district_table
from .enums import AlgorithmEnum, TypeEnum, ProjectTypeEnum
from .client_api_utils import get_available_maps, get_map, get_available_fields

PROD = True

from planheat.PlanheatMappingModule import master_mapping_config as mm_config



def load_file_from_menu_as_layer(node, node_data):
    if node_data.file:
        file_name = node_data.file
    else:
        selected_map = node_data.map_selection
        buffer_extent, crs, area_file = get_buffer_extent_and_crs(node)
        file_name, _ = get_map(selected_map, buffer_extent, crs, area_file)
    load_file_as_layer(file_name, node_data.description)


def load_file_from_dialog_as_layer(dialog, node):
    if dialog.fileNameText.isVisible() and dialog.fileNameText.text():
        file_name = dialog.fileNameText.text()
    else:
        selected_map = dialog.mapSelect.currentText()
        buffer_extent, crs, area_file = get_buffer_extent_and_crs(node)
        file_name, _ = get_map(selected_map, buffer_extent, crs,area_file)
    if not file_name or file_name == "None":
        QMessageBox.information(None, "Error", "No file specified.")
    else:
        layer_name = dialog.descriptionText.text()
        load_file_as_layer(file_name, layer_name)


def open_right_click_menu(tree):
    menu = QMenu(tree)
    if tree.selectedItems():
        node = tree.selectedItems()[0]
        node_data = get_node_data(node)

        properties = QAction("Properties", tree)
        properties.triggered.connect(lambda: node_preferences_action(node, 0))
        menu.addAction(properties)

        if node_data.file is not None or node_data.map_selection is not None:
            open_layer = QAction("Open file as layer", tree)
            open_layer.triggered.connect(lambda: load_file_from_menu_as_layer(node, node_data))
            menu.addAction(open_layer)
            delete = QAction("Delete item", tree)
            delete.triggered.connect(lambda: delete_node(node))
            menu.addAction(delete)
        else:
            calculate = QAction("Add input data", tree)
            calculate.triggered.connect(lambda: add_input_file_node_to_algorithm_node_action(None, node))
            menu.addAction(calculate)
            calculate = QAction("Calculate", tree)
            calculate.triggered.connect(lambda: calculate_algorithm_node_action(node))
            menu.addAction(calculate)

        if not PROD:
            if node_data.file is None:
                delete = QAction("Delete item", tree)
                delete.triggered.connect(lambda: delete_node(node))
                menu.addAction(delete)
                delete = QAction("Add Child node", tree)
                delete.triggered.connect(lambda: add_child_to_node_action(node))
                menu.addAction(delete)

        menu.popup(QCursor.pos())


def node_preferences_action(node, column):
    if is_input_file_node(node):
        select_input_file_node_dialog(node)
    else:
        select_algoritm_node_dialog(node)


def select_algoritm_node_dialog(node, new=False):
    if get_node_data(node).type == TypeEnum.SUPPLY:
        select_supply_algoritm_node_dialog(node, new)
    else:
        select_demand_algoritm_node_dialog(node, new)


def select_demand_algoritm_node_dialog(node, new):
    node_data = get_node_data(node)
    if new or not node_data.algorithm_selection:
        algorithms = get_algorithms_for_type(TypeEnum.DEMAND)
    else:
        algorithms = get_algorithm_by_id_and_default(node_data.algorithm_selection)
    dialog = AlgorithmNodePopup()
    if PROD:
        dialog.descriptionText.setEnabled(False)

    dialog.okButton.clicked.connect(lambda: save_algorithm_node_attributes_dialog(dialog, node, new))
    dialog.cancelButton.clicked.connect(lambda: close_and_remove_empty_node(dialog, node, new))

    dialog.calculateButton.clicked.connect(lambda: calculate_algorithm_node_action(node, dialog))
    dialog.algorithmSelect.currentIndexChanged.connect(lambda: update_algorithm_selection(dialog, algorithms[dialog.algorithmSelect.currentData()]))

    dialog.param3Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param3IdFieldSelect, file=find_node_file_by_id(node.treeWidget(), dialog.param3Select.currentData())))
    dialog.param3Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param3DataFieldSelect, file=find_node_file_by_id(node.treeWidget(), dialog.param3Select.currentData())))

    dialog.param4Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param4IdFieldSelect, file=find_node_file_by_id(node.treeWidget(), dialog.param4Select.currentData())))
    dialog.param4Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param4DataFieldSelect, file=find_node_file_by_id(node.treeWidget(), dialog.param4Select.currentData())))

    dialog.algorithmSelect.clear()
    for key, value in algorithms.items():
        dialog.algorithmSelect.addItem(value.description, key)

    fill_select_boxes_with_data_nodes(dialog, node)

    if not new:
        dialog.descriptionText.setText(str(node_data.description))
        if node_data.algorithm_id:
            index = dialog.algorithmSelect.findData(int(node_data.algorithm_id))
            if index != -1:
                dialog.algorithmSelect.setCurrentIndex(index)

        for key, value in node_data.parameters.items():
            if key == 1:
                index = dialog.param1Select.findData(value.value)
                if index != -1:
                    dialog.param1Select.setCurrentIndex(index)
            elif key == 2:
                index = dialog.param2Select.findData(value.value)
                if index != -1:
                    dialog.param2Select.setCurrentIndex(index)
                dialog.param2InputText.setText(str(value.value))
            elif key == 3:
                index = dialog.param3Select.findData(value.value)
                if index != -1:
                    dialog.param3Select.setCurrentIndex(index)
                if value.value:
                    selection_file = find_node_file_by_id(node.treeWidget(), value.value)
                    fill_attributes_select_box(dialog.param3IdFieldSelect, file=selection_file)
                    fill_attributes_select_box(dialog.param3DataFieldSelect, file=selection_file)
                dialog.param3IdFieldSelect.setCurrentIndex(dialog.param3IdFieldSelect.findText(value.id_field))
                dialog.param3DataFieldSelect.setCurrentIndex(dialog.param3DataFieldSelect.findText(value.data_field))
            elif key == 4:
                index = dialog.param4Select.findData(value.value)
                if index != -1:
                    dialog.param4Select.setCurrentIndex(index)
                if value.value:
                    selection_file = find_node_file_by_id(node.treeWidget(), value.value)
                    fill_attributes_select_box(dialog.param4IdFieldSelect, file=selection_file)
                    fill_attributes_select_box(dialog.param4DataFieldSelect, file=selection_file)
                dialog.param4IdFieldSelect.setCurrentIndex(dialog.param4IdFieldSelect.findText(value.id_field))
                dialog.param4DataFieldSelect.setCurrentIndex(dialog.param4DataFieldSelect.findText(value.data_field))

    dialog.algorithmSelect.setEnabled(False)
    dialog.setWindowModality(Qt.ApplicationModal)
    layout = dialog.layout()
    layout.setAlignment(Qt.AlignTop)
    dialog.setLayout(layout)
    dialog.adjustSize()
    dialog.exec_()


def select_supply_algoritm_node_dialog(node, new):
    node_data = get_node_data(node)
    if new:
        algorithms = get_algorithms_for_type(TypeEnum.SUPPLY)
    else:
        algorithms = get_algorithm_by_id_and_default(node_data.algorithm_selection)
    dialog = SupplyAlgorithmNodePopup()

    if PROD:
        dialog.descriptionText.setEnabled(False)

    validator = QDoubleValidator()
    validator.setNotation(0)
    dialog.param2InputText.setValidator(validator)
    dialog.okButton.clicked.connect(lambda: save_algorithm_node_attributes_dialog(dialog, node, new))
    dialog.cancelButton.clicked.connect(lambda: close_and_remove_empty_node(dialog, node, new))

    dialog.calculateButton.clicked.connect(lambda: calculate_algorithm_node_action(node, dialog))
    dialog.algorithmSelect.currentIndexChanged.connect(lambda: update_supply_algorithm_selection(dialog, algorithms[dialog.algorithmSelect.currentData()], node))

    dialog.param2InputText.textChanged.connect(lambda: refresh_straw_yield(dialog, node, algorithms[dialog.algorithmSelect.currentData()]))
    dialog.param4InputText.textChanged.connect(lambda: refresh_energy_production_factor(dialog, algorithms[dialog.algorithmSelect.currentData()]))

    fill_select_boxes_with_data_nodes(dialog, node)

    dialog.param1Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param1IdFieldSelect, file=find_node_file_by_id(node.treeWidget(), dialog.param1Select.currentData()),
                                           map_selection=find_node_map_selection_by_id(node.treeWidget(), dialog.param1Select.currentData()),
                                           custom_value="calculate feature areas", shp_only=True))

    dialog.algorithmSelect.clear()
    for key, value in algorithms.items():
        dialog.algorithmSelect.addItem(value.description, key)

    dialog.bufferText.setText(str(node_data.buffer))


    if not new:
        dialog.descriptionText.setText(str(node_data.description))
        if node_data.algorithm_id:
            index = dialog.algorithmSelect.findData(int(node_data.algorithm_id))
            if index != -1:
                dialog.algorithmSelect.setCurrentIndex(index)

            for key, value in node_data.parameters.items():
                if key == 1:
                    index = dialog.param1Select.findData(value.value)
                    if index != -1:
                        dialog.param1Select.setCurrentIndex(index)
                    if value.value is not None and dialog.findChild(QWidget, "param1IdFieldSelect"):
                        # selection_file = find_node_file_by_id(node.treeWidget(), value.value)
                        # selection_map = find_node_map_selection_by_id(node.treeWidget(), value.value)
                        # fill_attributes_select_box(dialog.param1IdFieldSelect, file=selection_file, map_selection=selection_map, custom_value="calculate feature areas", shp_only=True)
                        dialog.param1IdFieldSelect.setCurrentIndex(dialog.param1IdFieldSelect.findText(value.id_field))
                elif key == 2:
                    index = dialog.param2Select.findData(value.value)
                    if index != -1:
                        dialog.param2Select.setCurrentIndex(index)
                    dialog.param2InputText.setText(str(value.value))
                elif key == 3:
                    index = dialog.param3Select.findData(value.value)
                    if index != -1:
                        dialog.param3Select.setCurrentIndex(index)
                    dialog.param3InputText.setText(str(value.value))
                elif key == 4:
                    index = dialog.param4Select.findData(value.value)
                    if index != -1:
                        dialog.param4Select.setCurrentIndex(index)
                    dialog.param4InputText.setText(str(value.value))
                elif key == 5:
                    index = dialog.param5Select.findData(value.value)
                    if index != -1:
                        dialog.param5Select.setCurrentIndex(index)
                elif key == 6:
                    dialog.param6InputText.setText(str(value.value))
                elif key == 99:
                    monthly_values = value.value
                    monthly_values = monthly_values.split(';') if monthly_values else monthly_values
                    for i in range(1, 13):
                        getattr(dialog, "month_" + str(i)).setText(str(monthly_values[i - 1]))

    resize_dialog(dialog, 200)

    dialog.exec_()


def fill_select_boxes_with_data_nodes(dialog, node):
    if dialog.findChild(QWidget, "param1Select") is not None:
        dialog.param1Select.clear()
        dialog.param1Select.addItem("None", -1)
    if dialog.findChild(QWidget, "param2Select") is not None:
        dialog.param2Select.clear()
        dialog.param2Select.addItem("None", -1)
    if dialog.findChild(QWidget, "param3Select") is not None:
        dialog.param3Select.clear()
        dialog.param3Select.addItem("None", -1)
    if dialog.findChild(QWidget, "param4Select") is not None:
        dialog.param4Select.clear()
        dialog.param4Select.addItem("None", -1)
    if dialog.findChild(QWidget, "param5Select") is not None:
        dialog.param5Select.clear()
        dialog.param5Select.addItem("None", -1)
    # add maps from node
    for pos in range(0, node.childCount()):
        child_node = node.child(pos)
        if is_input_file_node(child_node):
            child_node_id = get_node_data(child_node).node_id
            if dialog.findChild(QWidget, "param1Select") is not None:
                dialog.param1Select.addItem(child_node.text(0), child_node_id)
            if dialog.findChild(QWidget, "param2Select") is not None:
                dialog.param2Select.addItem(child_node.text(0), child_node_id)
            if dialog.findChild(QWidget, "param3Select") is not None:
                dialog.param3Select.addItem(child_node.text(0), child_node_id)
            if dialog.findChild(QWidget, "param4Select") is not None:
                dialog.param4Select.addItem(child_node.text(0), child_node_id)
            if dialog.findChild(QWidget, "param5Select") is not None:
                dialog.param5Select.addItem(child_node.text(0), child_node_id)

    # add maps from parent node
    node_data = get_node_data(node)
    tree = node.treeWidget()
    parent_node = find_parent_node(tree, node_data.main_node_id)
    if parent_node:
        for pos in range(0, parent_node.childCount()):
            child_node = parent_node.child(pos)
            if is_input_file_node(child_node):
                child_node_id = get_node_data(child_node).node_id
                if dialog.findChild(QWidget, "param1Select") is not None:
                    dialog.param1Select.addItem(child_node.text(0), child_node_id)
                if dialog.findChild(QWidget, "param2Select") is not None:
                    dialog.param2Select.addItem(child_node.text(0), child_node_id)
                if dialog.findChild(QWidget, "param3Select") is not None:
                    dialog.param3Select.addItem(child_node.text(0), child_node_id)
                if dialog.findChild(QWidget, "param4Select") is not None:
                    dialog.param4Select.addItem(child_node.text(0), child_node_id)
                if dialog.findChild(QWidget, "param5Select") is not None:
                    dialog.param5Select.addItem(child_node.text(0), child_node_id)


def toggle_table_3_fields(dialog, boolean):
    toggle_table_3_id_field(dialog, boolean)
    dialog.param3DataFieldSelect.setVisible(boolean)
    dialog.dataField3Label.setVisible(boolean)


def toggle_table_3_id_field(dialog, boolean):
    dialog.param3IdFieldSelect.setVisible(boolean)
    dialog.idField3Label.setVisible(boolean)


def update_algorithm_selection(dialog, algorithm):
    number_of_parameters = algorithm.number_of_parameters
    dialog.param2InputText.setVisible(False)
    dialog.param2Select.setVisible(True)
    dialog.param1Group.setVisible(False)
    dialog.param2Group.setVisible(False)
    dialog.param3Group.setVisible(False)
    dialog.param4Group.setVisible(False)
    toggle_table_3_fields(dialog, True)
    for i in range(1, number_of_parameters + 1):
        if i == 1:
            dialog.param1Group.setVisible(True)
        if i == 2:
            dialog.param2Group.setVisible(True)
        if i == 3:
            dialog.param3Group.setVisible(True)
        if i == 4:
            dialog.param4Group.setVisible(True)
    if algorithm.algorithm_id == AlgorithmEnum.NONE:
        dialog.calculateButton.setEnabled(False)
    else:
        dialog.calculateButton.setEnabled(True)

    if algorithm.algorithm_id == AlgorithmEnum.DASYMAP:
        dialog.param1Label.setText("Zone map:")
        dialog.param2Label.setText("Class map:")
        dialog.param3Label.setText("Class weight table:")
        dialog.param4Label.setText("Zone value table:")

    if algorithm.algorithm_id == AlgorithmEnum.W_DIST:
        dialog.param1Label.setText("Spatial indicator:")
        dialog.param1Label.setToolTip(
            "<span>Select the spatial indicator that corresponds best to the spatial distribution of the specific type of useful demand. This map will be converted to a weights map in the top-down mapping of the useful demand. Examples are: floor area map of residential/tertiary buildings, footprint map of buildins, population density, employment density, etc</span>")
        dialog.param2Label.setText("HD map:")
        dialog.param2Label.setToolTip(
            "<span>Heating degree hours map available from PLANHEAT webserver. The option 'None' means that the map will not be taken into account.</span>")
    if algorithm.algorithm_id == AlgorithmEnum.W_DIST2:
        dialog.param1Label.setText("Spatial indicator:")
        dialog.param1Label.setToolTip(
            "<span>Select the spatial indicator that corresponds best to the spatial distribution of the specific type of useful demand. This map will be converted to a weights map in the top-down mapping of the useful demand. Examples are: floor area map of residential/tertiary buildings, footprint map of buildins, population density, employment density, etc</span>")
        dialog.param2Label.setText("CD map:")
        dialog.param2Label.setToolTip(
            "<span>Cooling degree hours map available from PLANHEAT webserver. The option 'None' means that the map will not be taken into account.</span>")
    if algorithm.algorithm_id == AlgorithmEnum.MULTI_FACT:
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param1Label.setText("Value map:")
        dialog.param2Label.setText("Multiplication factor:")
    if algorithm.algorithm_id == AlgorithmEnum.SPREAD:
        dialog.param1Label.setText("Input map:")
        dialog.param2Label.setText("Value:")
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
    dialog.adjustSize()


def update_supply_algorithm_selection(dialog, algorithm, node):
    number_of_parameters = algorithm.number_of_parameters
    dialog.idField1Label.setVisible(False)
    dialog.param1IdFieldSelect.setVisible(False)
    dialog.param2InputText.setVisible(False)
    dialog.param2UnitLabel.setVisible(False)
    dialog.param2ValueLabel_2.setVisible(False)
    dialog.param2UnitLabel_2.setVisible(False)
    dialog.param2Label_2.setVisible(False)
    dialog.param2Select.setVisible(True)
    dialog.param3InputText.setVisible(False)
    dialog.param3UnitLabel.setVisible(False)
    dialog.param3Select.setVisible(True)
    dialog.param4Select.setVisible(False)
    dialog.param1Group.setMinimumHeight(82)
    dialog.param2Group.setMinimumHeight(82)
    dialog.param1GroupBox.setVisible(False)
    dialog.param2GroupBox.setVisible(False)
    dialog.scrollArea.setVisible(True)
    for i in range(1, 6):
        getattr(dialog, "param" + str(i) + "Group").setVisible(False)
    dialog.monthGroup.setVisible(False)
    dialog.bufferGroup.setVisible(False)
    dialog.algorithmLabel.setToolTip(get_tooltip(algorithm.algorithm_id, 0))
    for i in range(1, number_of_parameters + 1):
        if i == 1:
            dialog.param1Group.setVisible(True)
            dialog.param1Label.setToolTip(get_tooltip(algorithm.algorithm_id, 1))
            dialog.idField1Label.setToolTip(get_tooltip(algorithm.algorithm_id, 1.2))
        if i == 2:
            dialog.param2Group.setVisible(True)
            dialog.param2Label.setToolTip(get_tooltip(algorithm.algorithm_id, 2))
        if i == 3:
            dialog.param3Group.setVisible(True)
            dialog.param3Label.setToolTip(get_tooltip(algorithm.algorithm_id, 3))
        if i == 4:
            dialog.param4Group.setVisible(True)
            dialog.param4Label.setToolTip(get_tooltip(algorithm.algorithm_id, 4))
        if i == 5:
            dialog.param5Group.setVisible(True)
            dialog.param5Label.setToolTip(get_tooltip(algorithm.algorithm_id, 5))
        if i == 6:
            dialog.param6Group.setVisible(True)
            dialog.param6Label.setToolTip(get_tooltip(algorithm.algorithm_id, 6))
    if algorithm.algorithm_id == AlgorithmEnum.NONE:
        dialog.calculateButton.setEnabled(False)
    else:
        dialog.calculateButton.setEnabled(True)

    if algorithm.algorithm_id == AlgorithmEnum.SUM:
        dialog.param6Group.setVisible(False)
        dialog.scrollArea.setVisible(False)
    if algorithm.algorithm_id == AlgorithmEnum.PROVIDED:
        dialog.param1Label.setText("Supply map:")
        dialog.param2Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)
    if algorithm.algorithm_id == AlgorithmEnum.SOLAR:
        dialog.idField1Label.setVisible(True)
        # dialog.param1IdFieldSelect.setVisible(True)
        # dialog.param1Group.setMinimumHeight(140)
        # dialog.param1GroupBox.setVisible(True)
        dialog.param1Label.setText("Map of the available area:")
        # dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Label.setText("Technical suitability:")
        dialog.param2InputText.setVisible(True)
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("%")
        dialog.param2Select.setVisible(False)
        dialog.param3Label.setText("Solar radiation data:")
        dialog.param5Label.setText("Spatial constraints:")
        dialog.param4Group.setVisible(False)
        dialog.param6InputText.setText("75")
        dialog.param6Label.setToolTip(get_tooltip(algorithm.algorithm_id, 6))
    if algorithm.algorithm_id == AlgorithmEnum.BIO_FORESTERY:
        dialog.param1Label.setText("Map of the forest areas:")
        dialog.idField1Label.setVisible(True)
        # dialog.param1IdFieldSelect.setVisible(True)
        # dialog.param1Group.setMinimumHeight(140)
        # dialog.param1GroupBox.setVisible(True)
        # dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Label.setText("Energy production factor:")
        dialog.param3Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)
    if algorithm.algorithm_id == AlgorithmEnum.CEREALS \
        or algorithm.algorithm_id == AlgorithmEnum.GRAIN_MAIZE \
        or algorithm.algorithm_id == AlgorithmEnum.WHEAT \
        or algorithm.algorithm_id == AlgorithmEnum.BARLEY \
        or algorithm.algorithm_id == AlgorithmEnum.RAPE_SEEDS:
        dialog.param1Label.setText("Map of the crop type:")
        # dialog.idField1Label.setVisible(True)
        # dialog.param1IdFieldSelect.setVisible(True)
        # dialog.param1Group.setMinimumHeight(140)
        # dialog.param1GroupBox.setVisible(True)
        # dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Label_2.setVisible(True)
        dialog.param2InputText.setVisible(True)
        dialog.param2Label.setText("Average crop yield:")
        dialog.param2Label_2.setText("Average straw yield:")
        dialog.param2Label_2.setToolTip(get_tooltip(algorithm.algorithm_id, 3))
        dialog.param2Group.setMinimumHeight(140)
        dialog.param2GroupBox.setVisible(True)
        dialog.param2ValueLabel_2.setVisible(True)
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel_2.setVisible(True)
        dialog.param2UnitLabel.setText("ton/ha")
        dialog.param2UnitLabel_2.setText("ton/ha")
        dialog.param2Select.setVisible(False)
        dialog.param3Label.setText("Technical availability:")
        dialog.param3InputText.setVisible(True)
        dialog.param3UnitLabel.setVisible(True)
        dialog.param3Select.setVisible(False)
        dialog.param4Label.setText("Energy production factor:")
        dialog.param5Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)
        dialog.param3Label.setToolTip(get_tooltip(algorithm.algorithm_id, 4))
        dialog.param4Label.setToolTip(get_tooltip(algorithm.algorithm_id, 5))
        dialog.param5Label.setToolTip(get_tooltip(algorithm.algorithm_id, 6))

        crop_yield, straw_yield = get_crop_and_straw_yield_value(node, algorithm)
        dialog.param2InputText.setText(str(crop_yield))
        dialog.param2ValueLabel_2.setText(str(straw_yield))
        dialog.param3InputText.setText("50")
        dialog.param4InputText.setText(str(get_energy_production_factor(algorithm.algorithm_id)))
        dialog.param4UnitLabel.setText("MWh/kg")
    if algorithm.algorithm_id == AlgorithmEnum.BASIC_AGRICULTURE:
        dialog.param1Label.setText("Map of the agricultural area:")
        # dialog.idField1Label.setVisible(True)
        # dialog.param1IdFieldSelect.setVisible(True)
        # dialog.param1Group.setMinimumHeight(140)
        # dialog.param1GroupBox.setVisible(True)
        # dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Select.setVisible(False)
        dialog.param2InputText.setVisible(True)
        dialog.param2Label.setText("Energy production factor:")
        crop_yield = get_crop_yield_value(node, algorithm)
        dialog.param2InputText.setText(str(crop_yield))
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("MWh/ha")
        dialog.param3Label.setText("Technical availability:")
        dialog.param3InputText.setVisible(True)
        dialog.param3UnitLabel.setVisible(True)
        dialog.param3Select.setVisible(False)
        dialog.param4Label.setText("Spatial constraints:")
        dialog.param4InputText.setVisible(False)
        dialog.param4UnitLabel.setVisible(False)
        dialog.param4Select.setVisible(True)
        dialog.bufferGroup.setVisible(True)
    if algorithm.algorithm_id == AlgorithmEnum.SEWER_SYSTEM:
        dialog.param1Label.setText("Population density map:")
        dialog.monthGroup.setVisible(True)
        dialog.monthTitle.setText("Average effluent temperature")
        dialog.monthTitle.setToolTip(get_tooltip(algorithm.algorithm_id, 4))
    if algorithm.algorithm_id in [AlgorithmEnum.RIVERS_HEAT, AlgorithmEnum.RIVERS_COLD, AlgorithmEnum.RIVERS_FREE_COLD]:
        dialog.monthGroup.setVisible(True)
        dialog.param1Label.setText("Map of the river network:")
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.idField1Label.setText("Label of the discharge data:")
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param2Label.setText("Average discharge:")
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("m³/h")
        dialog.param2InputText.setText("100")
        dialog.param3Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)
        dialog.monthTitle.setText("Average water temperature")
        dialog.monthTitle.setToolTip(get_tooltip(algorithm.algorithm_id, 5))
    if algorithm.algorithm_id == AlgorithmEnum.LAKES_HEAT:
        dialog.param1Label.setText("Map of the lakes:")
        dialog.monthGroup.setVisible(True)
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.idField1Label.setText("Depth of the lake:")
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param2Label.setText("Hours of the heating season:")
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("hours")
        dialog.param3InputText.setVisible(True)
        dialog.param3UnitLabel.setVisible(True)
        dialog.param3Select.setVisible(False)
        dialog.param3Label.setText("Average depth:")
        dialog.param3UnitLabel.setText("m")
        dialog.param4Label.setText("Spatial constraints:")
        dialog.param4InputText.setVisible(False)
        dialog.param4UnitLabel.setVisible(False)
        dialog.param4Select.setVisible(True)
        dialog.bufferGroup.setVisible(True)
        dialog.monthTitle.setText("Average water temperature")
        dialog.monthTitle.setToolTip(get_tooltip(algorithm.algorithm_id, 6))
        dialog.bufferLabel.setToolTip(get_tooltip(algorithm.algorithm_id, 5))
    if algorithm.algorithm_id == AlgorithmEnum.LAKES_COLD:
        dialog.param1Label.setText("Map of the lakes:")
        dialog.monthGroup.setVisible(True)
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param2Label.setText("Hours of the heating season:")
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("hours")
        dialog.param3InputText.setVisible(True)
        dialog.param3UnitLabel.setVisible(True)
        dialog.param3UnitLabel.setText("m")
        dialog.param3Select.setVisible(False)
        dialog.param3Label.setText("Average depth:")
        dialog.param4Label.setText("Spatial constraints:")
        dialog.param4InputText.setVisible(False)
        dialog.param4UnitLabel.setVisible(False)
        dialog.param4Select.setVisible(True)
        dialog.bufferGroup.setVisible(True)
        dialog.monthTitle.setText("Average water temperature")
        dialog.monthTitle.setToolTip(get_tooltip(algorithm.algorithm_id, 6))
        dialog.bufferLabel.setToolTip(get_tooltip(algorithm.algorithm_id, 5))
    if algorithm.algorithm_id == AlgorithmEnum.SHALLOW_GEOTHERMAL:
        dialog.param1Label.setText("Map of the area:")
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param2Label.setText("Yearly potential:")
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("kWh/year")
        dialog.param3Label.setText("Spatial constraints:")
    if algorithm.algorithm_id == AlgorithmEnum.DEEP_GEOTHERMAL:
        dialog.param1Label.setText("Result map:")
        dialog.param2Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)


def refresh_straw_yield(dialog, node, algorithm):
    if algorithm.algorithm_id == AlgorithmEnum.CEREALS \
        or algorithm.algorithm_id == AlgorithmEnum.GRAIN_MAIZE \
        or algorithm.algorithm_id == AlgorithmEnum.WHEAT \
        or algorithm.algorithm_id == AlgorithmEnum.BARLEY \
        or algorithm.algorithm_id == AlgorithmEnum.RAPE_SEEDS:
        if is_float(dialog.param2InputText.text()):
            straw_yield = calculate_straw_yield(float(dialog.param2InputText.text()))
            dialog.param2ValueLabel_2.setText(str(straw_yield))
        if dialog.param2InputText.text() == '':
            crop_yield, straw_yield = get_crop_and_straw_yield_value(node, algorithm)
            dialog.param2InputText.setText(str(crop_yield))
            dialog.param2ValueLabel_2.setText(str(straw_yield))

    if algorithm.algorithm_id == AlgorithmEnum.BASIC_AGRICULTURE:
        if dialog.param2InputText.text() == '':
            crop_yield = get_crop_yield_value(node, algorithm)
            dialog.param2InputText.setText(str(crop_yield))


def refresh_energy_production_factor(dialog, algorithm):
    if algorithm.algorithm_id == AlgorithmEnum.CEREALS \
        or algorithm.algorithm_id == AlgorithmEnum.GRAIN_MAIZE \
        or algorithm.algorithm_id == AlgorithmEnum.WHEAT \
        or algorithm.algorithm_id == AlgorithmEnum.BARLEY \
        or algorithm.algorithm_id == AlgorithmEnum.RAPE_SEEDS:
        if dialog.param4InputText.text() == '':
            dialog.param4InputText.setText(str(get_energy_production_factor(algorithm.algorithm_id)))


def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def calculate_algorithm_node_action(node, dialog=None):
    if dialog is not None:
        save_algorithm_node_attributes_dialog(dialog, node, False, False)
        algorithm_id = dialog.algorithmSelect.currentData()
    else:
        algorithm_id = get_node_data(node).algorithm_id

    tree = node.treeWidget()
    save_tree(tree)

    if not has_checked_input_file_node_children(node):
        QMessageBox.information(None, "Error", "Please select at least one child node.")
    elif algorithm_id == 1:
        QMessageBox.information(None, "Error", "Please select a algorithm.")
    elif get_node_data(node).parameters and 1 not in get_node_data(node).parameters:
        QMessageBox.information(None, "Error", "Please select a input map.")
    else:
        if valid_structure(node):
            progress = show_calculating_dialog(2)
            set_progress(progress)
            old_state = node.checkState(0)
            node.setCheckState(0, Qt.Checked)
            run_algorithm_for_node(node, algorithm_id)
            node.setCheckState(0, old_state)
            progress.setValue(2)


def show_calculating_dialog(time):
    progress = QProgressDialog("Calculating...", "Abort", 0, time)
    progress.setCancelButton(None)
    progress.setMinimumDuration(0)
    progress.setWindowModality(Qt.WindowModal)
    progress.setWindowTitle("Progress")
    progress.show()
    QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
    return progress


def save_algorithm_node_attributes_dialog(dialog, node, new, close=True):
    node_data = get_node_data(node)
    node_data.description = str(dialog.descriptionText.text())
    node.setText(0, str(dialog.descriptionText.text()))
    if dialog.algorithmSelect.currentText() != "":
        node_data.set_algorithm(dialog.algorithmSelect.currentData(), get_algorithms()[dialog.algorithmSelect.currentData()])
        set_node_icon(node)
    else:
        node_data.set_algorithm(None, None)
    if node_data.algorithm_selection is None:
        node_data.algorithm_selection = dialog.algorithmSelect.currentData()
    parameter_dict = dict()
    if dialog.param1Label.isVisible():
        if dialog.param1Select.currentData() == -1:
            node.setForeground(0, QBrush(Qt.lightGray))
        else:
            node.setForeground(0, QBrush(Qt.black))
        p1id = None
        if dialog.findChild(QWidget, "param1IdFieldSelect"):
            p1id = str(dialog.param1IdFieldSelect.currentText())
        print(p1id)
        parameter = Parameter(None, node_data.node_id, 1, dialog.param1Select.currentData(), p1id, None)
        if node_data.parameters and 1 in node_data.parameters:
            parameter.parameter_id = node_data.parameters[1].parameter_id
        parameter_dict[1] = parameter
    if dialog.param2Label.isVisible():
        if dialog.param2Select.isVisible():
            input_value = dialog.param2Select.currentData()
        elif dialog.param2InputText.isVisible():
            input_value = dialog.param2InputText.text()
        parameter = Parameter(None, node_data.node_id, 2, input_value, None, None)
        if node_data.parameters and 2 in node_data.parameters:
            parameter.parameter_id = node_data.parameters[2].parameter_id
        parameter_dict[2] = parameter
    if dialog.param3Label.isVisible():
        parameter_id = None
        if node_data.parameters and 3 in node_data.parameters:
            parameter_id = node_data.parameters[3].parameter_id
        if dialog.param3Select.isVisible():
            p3data = None
            if dialog.findChild(QWidget, "param3DataFieldSelect"):
                p3data = str(dialog.param3DataFieldSelect.currentText())
            p3id = None
            if dialog.findChild(QWidget, "param3IdFieldSelect"):
                p3id = str(dialog.param3IdFieldSelect.currentText())
            p = Parameter(parameter_id, node_data.node_id, 3, dialog.param3Select.currentData(), p3id, p3data)
        elif dialog.param3InputText.isVisible():
            p = Parameter(parameter_id, node_data.node_id, 3, dialog.param3InputText.text(), None, None)
        parameter_dict[3] = p
    if dialog.param4Label.isVisible():
        parameter_id = None
        if node_data.parameters and 4 in node_data.parameters:
            parameter_id = node_data.parameters[4].parameter_id
        if dialog.findChild(QWidget, "param4Select") and dialog.param4Select.isVisible():
            parameter_dict[4] = Parameter(parameter_id, node_data.node_id, 4, dialog.param4Select.currentData(), None, None)
        else:
            parameter_dict[4] = Parameter(parameter_id, node_data.node_id, 4, dialog.param4InputText.text(), None, None)
    if dialog.findChild(QWidget, "param5Label") and dialog.param5Label.isVisible():
        parameter_id = None
        if node_data.parameters and 5 in node_data.parameters:
            parameter_id = node_data.parameters[5].parameter_id
        parameter_dict[5] = Parameter(parameter_id, node_data.node_id, 5, dialog.param5Select.currentData(), None, None)
    if dialog.findChild(QWidget, "param6Label") and dialog.param6Label.isVisible():
        parameter_id = None
        if node_data.parameters and 6 in node_data.parameters:
            parameter_id = node_data.parameters[6].parameter_id
        parameter_dict[6] = Parameter(parameter_id, node_data.node_id, 6, dialog.param6InputText.text(), None, None)
    if dialog.findChild(QWidget, "month_1") and dialog.month_1.isVisible():
        parameter_id = None
        if node_data.parameters and 99 in node_data.parameters:
            parameter_id = node_data.parameters[99].parameter_id
        month_results = []
        for i in range(1, 13):
            month_results.append(float(getattr(dialog, "month_" + str(i)).text()))
        parameter_dict[99] = Parameter(parameter_id, node_data.node_id, 99, ';'.join(format(x, ".1f") for x in month_results), None, None)
    node_data.set_parameters(parameter_dict)
    if dialog.findChild(QWidget, "bufferText") and dialog.bufferText.isVisible():
        node_data.buffer = dialog.bufferText.text()
    if new:
        tree = node.treeWidget()
        parent_node = find_parent_node(tree, node_data.main_node_id)
        parent_node.removeChild(node)
        add_node(tree, node_data)
    if close:
        dialog.close()


def select_input_file_node_dialog(node, new=False):
    node_data = get_node_data(node)

    dialog = InputNodePopup()

    dialog.fileButton.clicked.connect(lambda: select_file_for_dialog_action(dialog.fileNameText))
    dialog.loadLayerButton.clicked.connect(lambda: load_file_from_dialog_as_layer(dialog, node))
    dialog.okButton.clicked.connect(lambda: save_input_file_node_dialog_action(dialog, node, new))
    dialog.cancelButton.clicked.connect(lambda: close_and_remove_empty_node(dialog, node, new))
    dialog.fileNameText.textChanged.connect(lambda: fill_attributes_select_box(dialog.attributeSelect, file=dialog.fileNameText.text()))
    dialog.mapSelect.currentIndexChanged.connect(lambda: map_select_changed(dialog))
    dialog.radioButtonServer.clicked.connect(lambda: radio_selection_changed(dialog))
    dialog.radioButtonFile.clicked.connect(lambda: radio_selection_changed(dialog))

    dialog.mapSelect.clear()
    for map_name in get_available_maps():
        dialog.mapSelect.addItem(map_name)
    dialog.mapSelect.addItem("OSM buildings")

    if not new:
        if node_data.file:
            dialog.fileNameText.setText(str(node_data.file))
            map_select_changed(dialog)
            dialog.radioButtonFile.setChecked(True)
            radio_selection_changed(dialog)
            dialog.attributeSelect.setCurrentIndex(dialog.attributeSelect.findText(node_data.shape_attribute))
        else:
            dialog.mapSelect.setCurrentIndex(dialog.mapSelect.findText(node_data.map_selection))
            dialog.radioButtonServer.setChecked(True)
            radio_selection_changed(dialog)
            dialog.attributeSelect.setCurrentIndex(dialog.attributeSelect.findText(node_data.shape_attribute))
        dialog.descriptionText.setText(str(node_data.description))
    else:
        dialog.radioButtonFile.setChecked(True)
        radio_selection_changed(dialog)
    dialog.buttonGroup.setExclusive(True)
    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.exec_()


def radio_selection_changed(dialog):
    if dialog.radioButtonServer.isChecked():
        dialog.fileButton.setVisible(False)
        dialog.fileNameText.setVisible(False)
        dialog.fileLabel.setVisible(False)
        dialog.mapSelect.setVisible(True)
        dialog.mapLabel.setVisible(True)
        map_select_changed(dialog)
    elif dialog.radioButtonFile.isChecked():
        dialog.mapSelect.setVisible(False)
        dialog.mapLabel.setVisible(False)
        dialog.fileButton.setVisible(True)
        dialog.fileNameText.setVisible(True)
        dialog.fileLabel.setVisible(True)
        fill_attributes_select_box(dialog.attributeSelect, file=dialog.fileNameText.text())


def map_select_changed(dialog):
    dialog.attributeSelect.clear()
    map_selection = dialog.mapSelect.currentText()
    attributes = get_available_fields(map_selection)
    if map_selection == 'OSM buildings':
        attributes.append("")
        attributes.append("calculate feature areas")
    for item in attributes:
        dialog.attributeSelect.addItem(item)


def close_and_remove_empty_node(dialog, node, new):
    if new:
        node_data = get_node_data(node)
        tree = node.treeWidget()
        parent_node = find_parent_node(tree, node_data.main_node_id)
        parent_node.removeChild(node)
    dialog.close()


def add_input_file_node_to_algorithm_node_action(from_dialog, existing_node):
    existing_node_data = get_node_data(existing_node)
    if not existing_node_data.node_id:
        QMessageBox.information(None, "Error", "Please save first before adding items to a new child node.")
    else:
        new_node = create_new_node(existing_node)
        select_input_file_node_dialog(new_node, True)
        if from_dialog:
            fill_select_boxes_with_data_nodes(from_dialog, existing_node)


def create_new_node(existing_node):
    existing_node_data = get_node_data(existing_node)
    new_node = QTreeWidgetItem(existing_node)

    new_node_data = TreeNode(get_next_node_id(), existing_node_data.tree_id, existing_node_data.node_id, 0, None, None, None, None, None, None, None, None,
                             existing_node_data.type, None, existing_node_data.buffer)
    new_node.setData(0, Qt.UserRole, new_node_data)
    return new_node


def add_child_to_node_action(existing_node):
    existing_node_data = get_node_data(existing_node)
    if not existing_node_data.node_id:
        QMessageBox.information(None, "Error", "Please save first before adding items to a new child node.")
    else:
        new_node = create_new_node(existing_node)
        select_algoritm_node_dialog(new_node, True)


def select_file_for_dialog_action(text_box):
    qfd = QFileDialog()
    title = 'Select file'
    path = text_box.text()
    if path == 'None' or path == '':
        path = None
    if not path:
        try:
            path = os.path.expanduser("~\\Documents")
        except:
            path = ""
    file_path = QFileDialog.getOpenFileName(qfd, title, path, "Map files (*.shp *.tif *.img *.asc)")[0]
    if file_path:
        text_box.setText(str(file_path))


def select_planner_file_for_dialog_action(text_box):
    qfd = QFileDialog()
    title = 'Select planner file'
    path = text_box.text()
    if path == 'None':
        path = None
    if not path:
        path = os.path.join(mm_config.CURRENT_MAPPING_DIRECTORY,
                            mm_config.CMM_BASELINE_FOLDER,
                            mm_config.CMM_WIZARD_FOLDER)
        os.makedirs(path, exist_ok=True)

    file_path = QFileDialog.getOpenFileName(qfd, title, path, "Planner files (*.csv)")[0]
    if file_path:
        text_box.setText(str(file_path))


def save_input_file_node_dialog_action(dialog, node, new):
    if dialog.mapSelect.currentText() != 'From file' or (dialog.fileNameText.text() and dialog.fileNameText.text() != "None"):
        node_data = get_node_data(node)
        node_data.description = str(dialog.descriptionText.text())
        node.setText(0, str(dialog.descriptionText.text()))
        if dialog.fileNameText.isVisible() and dialog.fileNameText.text() and dialog.fileNameText.text() != "None":
            node_data.file = str(dialog.fileNameText.text())
            node_data.map_selection = None
        elif not dialog.fileNameText.isVisible() and dialog.fileNameText.text():
            node_data.file = None
        if dialog.attributeSelect.currentText() and dialog.attributeSelect.currentText() != "None":
            node_data.shape_attribute = str(dialog.attributeSelect.currentText())
        if dialog.mapSelect.isVisible() and dialog.mapSelect.currentText() != "None":
            node_data.map_selection = str(dialog.mapSelect.currentText())
            node_data.file = None
        set_node_icon(node)
        if new:
            tree = node.treeWidget()
            parent_node = find_parent_node(tree, node_data.main_node_id)
            parent_node.removeChild(node)
            add_node(tree, node_data)
        dialog.close()
    else:
        QMessageBox.information(None, "Error", "Selecting a file is mandatory.")
        return


def load_tree_dialog(dockwidget, type, base_path):
    tree_dict = get_trees(type)
    print("tree_dict=", tree_dict)
    dialog = LoadTreePopup()
    # Master Integration
    dialog.nameText.setVisible(True)
    dialog.nameText.setText(str(mm_config.CURRENT_PROJECT_NAME))
    dialog.nameText.setEnabled(False)
    if type == ProjectTypeEnum.SUPPLY:
        title = "Supply mapping"
    elif type == ProjectTypeEnum.DEMAND_CURRENT:
        title = "Current demand mapping"
    elif type == ProjectTypeEnum.DEMAND_FUTURE:
        title = "Future demand mapping"
    else:
        raise ValueError("Invalid Mapping Module type")
    dialog.titleLabel.setText(title)
    dialog.treeSelect.setVisible(False)
    dialog.createButton.setVisible(True)
    dialog.copyButton.setVisible(False)
    dialog.deleteButton.setVisible(False)
    dialog.descriptionTitleLabel.setVisible(False)
    dialog.descriptionLabel.setVisible(False)
    dialog.createButton.clicked.connect(lambda: tree_copy_clicked(dockwidget, dialog, type))
    # End Master Integration
    # dialog.titleLabel.setText("Open a project")
    dialog.okButton.setText("Continue")
    dialog.cancelButton.setVisible(False)
    dialog.descriptionText.setVisible(False)
    # dialog.nameText.setVisible(False)
    dialog.copyCheckBox.setChecked(False)
    dialog.copyCheckBox.setVisible(False)
    dialog.fileButton.clicked.connect(lambda: load_file_for_tree_dialog(dialog))
    dialog.areaFileButton.clicked.connect(lambda: select_file_for_dialog_action(dialog.areaFileText))
    dialog.plannerButton.clicked.connect(lambda: select_planner_file_for_dialog_action(dialog.plannerText))
    dialog.okButton.clicked.connect(lambda: initialize_tree(dockwidget, dialog, type, base_path))
    #dialog.copyButton.clicked.connect(lambda: tree_copy_clicked(dockwidget, dialog, type))
    #dialog.createButton.clicked.connect(lambda: tree_create_clicked(dockwidget, dialog, type))
    dialog.cancelButton.clicked.connect(lambda: tree_cancel_clicked(dockwidget, dialog, type))
    #dialog.deleteButton.clicked.connect(lambda: remove_tree(dockwidget, dialog, type, base_path))
    dialog.treeSelect.currentIndexChanged.connect(lambda: update_tree_selection(dialog))
    if ProjectTypeEnum.DEMAND_CURRENT == type or ProjectTypeEnum.DEMAND_FUTURE == type:
        dialog.bufferText.setVisible(False)
        dialog.bufferText.setText(str(0))
        dialog.bufferLabel.setVisible(False)
        dialog.bufferUnitLabel.setVisible(False)
    if ProjectTypeEnum.SUPPLY == type:
        dialog.plannerText.setVisible(False)
        dialog.plannerLabel.setVisible(False)
        dialog.plannerButton.setVisible(False)
    valid_trees_keys = set()
    dialog.treeSelect.clear()
    for key, value in tree_dict.items():
        if key not in [1, 2, 3]:
            dialog.treeSelect.addItem(value.name, value)
            valid_trees_keys.add(key)
    # Master Integration
    if len(valid_trees_keys) == 0:
        tree_create_clicked(dockwidget, dialog, type)
        dialog.cancelButton.setVisible(False)
    # End Master Integration
    resize_dialog(dialog, 200)
    dialog.exec_()


def resize_dialog(dialog, rest_height):
    dialog.setWindowModality(Qt.ApplicationModal)

    layout = dialog.scrollAreaWidgetContents_2.layout()
    layout.setAlignment(Qt.AlignTop)
    dialog.scrollAreaWidgetContents_2.setLayout(layout)
    dialog.scrollAreaWidgetContents_2.adjustSize()
    res_min = 9999
    for screen in QGuiApplication.screens():
        res_min = min(screen.geometry().height(), res_min)
    dialog.scrollArea.adjustSize()
    dialog.scrollArea.setMinimumHeight(min(dialog.height() - rest_height, res_min - 400, dialog.scrollArea.height()))
    dialog.scrollArea.adjustSize()

    layout = dialog.layout()
    layout.setAlignment(Qt.AlignTop)
    dialog.setLayout(layout)
    dialog.adjustSize()


def load_file_for_tree_dialog(dialog):
    select_file_for_dialog_action(dialog.fileNameText)
    fill_attributes_select_box(dialog.nameSelect, file=dialog.fileNameText.text())


def remove_tree(dockwidget, dialog, type, base_path):
    qm = QMessageBox
    ret = qm.question(None, 'Warning', "Delete this project?", qm.Yes | qm.No)

    if ret == qm.Yes:
        tree = dockwidget.treeWidget
        tree.clear()
        dockwidget.titleLabel.setText("")
        delete_tree(dialog.treeSelect.currentData().tree_id)
        dialog.close()
        load_tree_dialog(dockwidget, type, base_path)


def update_tree_selection(dialog):
    print("update_tree_selection")
    if dialog.treeSelect.currentData() is not None:
        # if dialog.treeSelect.currentData().tree_id not in [1, 2, 3]:
        #     dialog.nameText.setText(dialog.treeSelect.currentData().name)
        # else:
        #     dialog.nameText.setText('')
        # dialog.descriptionText.setText(dialog.treeSelect.currentData().description)
        # dialog.descriptionLabel.setText(dialog.treeSelect.currentData().description)

        dialog.areaFileText.setText(dialog.treeSelect.currentData().area_file)
        dialog.fileNameText.setText(dialog.treeSelect.currentData().file)
        if dialog.treeSelect.currentData().resolution:
            dialog.resolutionText.setText(str(dialog.treeSelect.currentData().resolution))
        else:
            dialog.resolutionText.setText('')
        if dialog.treeSelect.currentData().buffer_size:
            dialog.bufferText.setText(str(dialog.treeSelect.currentData().buffer_size))
        elif not dialog.bufferText.isVisible():
            dialog.bufferText.setText('0')
        else:
            dialog.bufferText.setText('')
        fill_attributes_select_box(dialog.nameSelect, file=dialog.treeSelect.currentData().file)
        dialog.nameSelect.setCurrentIndex(dialog.nameSelect.findText(str(dialog.treeSelect.currentData().attribute_name)))
        dialog.plannerText.setText(str(dialog.treeSelect.currentData().planner_file))

    # Master integration
    
    # add "results.csv" to Usefull Energy Demand field    
    if dialog.treeSelect.currentData() is None\
    or str(dialog.treeSelect.currentData().planner_file) == str(None)\
    or not os.path.exists(dialog.treeSelect.currentData().planner_file):
        file_path = os.path.join(mm_config.CURRENT_MAPPING_DIRECTORY,
                                 mm_config.INPUT_FOLDER,
                                 mm_config.CMM_WIZARD_RESULT_FILE_NAME)

        if os.path.exists(file_path):
            dialog.plannerText.setText(file_path)

    # check fileNameText and areaFileText
    emit_modify = False
    for fileText in [dialog.areaFileText, dialog.fileNameText]:
        if not dialog.treeSelect.currentData() is None and not os.path.exists(fileText.text()):
            fileText.setText("")
            emit_modify = True
    for fileText in [dialog.plannerText]:
        if not dialog.treeSelect.currentData() is None and not os.path.exists(fileText.text()):
            fileText.setText("")

    if emit_modify:
        dialog.createButton.clicked.emit()

    # End master integration


def tree_cancel_clicked(dockwidget, dialog, type):
    # dialog.titleLabel.setText("Open a project")
    dialog.okButton.setText("Continue")
    dialog.cancelButton.setVisible(False)
    # dialog.descriptionText.setVisible(False)
    # dialog.nameText.setVisible(False)
    dialog.copyCheckBox.setChecked(False)
    dialog.buttonGroup.setVisible(True)
    # dialog.deleteButton.setVisible(True)
    # dialog.descriptionLabel.setVisible(True)
    dialog.fileButton.setEnabled(False)
    dialog.areaFileButton.setEnabled(False)
    dialog.nameSelect.setEnabled(False)
    dialog.resolutionText.setEnabled(False)
    dialog.bufferText.setEnabled(False)
    dialog.plannerButton.setEnabled(False)
    # dialog.treeSelect.setVisible(True)

    if ProjectTypeEnum.DEMAND_CURRENT == type or ProjectTypeEnum.DEMAND_FUTURE == type:
        dialog.bufferText.setVisible(False)
        dialog.bufferLabel.setVisible(False)
        dialog.bufferUnitLabel.setVisible(False)
    if ProjectTypeEnum.SUPPLY == type:
        dialog.plannerText.setVisible(False)
        dialog.plannerButton.setVisible(False)
        dialog.plannerLabel.setVisible(False)
    dialog.treeSelect.clear()
    tree_dict = get_trees(type)
    for key, value in tree_dict.items():
        if key not in [1, 2, 3]:
            dialog.treeSelect.addItem(value.name, value)

    dialog.adjustSize()


def tree_copy_clicked(dockwidget, dialog, type):
    dialog.titleLabel.setText("Modifying mapping inputs")
    dialog.okButton.setText("Validate inputs")
    dialog.nameText.setVisible(True)
    dialog.buttonGroup.setVisible(False)
    dialog.cancelButton.setVisible(True)
    dialog.deleteButton.setVisible(False)
    # dialog.descriptionText.setVisible(True)
    # dialog.descriptionLabel.setVisible(False)
    # dialog.descriptionText.setEnabled(True)
    dialog.fileButton.setEnabled(True)
    dialog.areaFileButton.setEnabled(True)
    dialog.nameSelect.setEnabled(True)
    dialog.resolutionText.setEnabled(True)
    dialog.bufferText.setEnabled(True)
    dialog.plannerButton.setEnabled(True)
    dialog.treeSelect.setVisible(False)
    dialog.copyCheckBox.setChecked(True)
    dialog.adjustSize()


def tree_create_clicked(dockwidget, dialog, type):
    dialog.treeSelect.clear()
    tree_dict = get_trees(type)
    for key, value in tree_dict.items():
        if key in [1, 2, 3]:
            dialog.treeSelect.addItem(value.name, value)
    dialog.titleLabel.setText("Setting mapping inputs")
    dialog.okButton.setText("Validate inputs")
    dialog.nameText.setVisible(True)
    dialog.buttonGroup.setVisible(False)
    dialog.cancelButton.setVisible(True)
    dialog.deleteButton.setVisible(False)
    # dialog.descriptionText.setVisible(True)
    # dialog.descriptionLabel.setVisible(False)
    dialog.treeSelect.setCurrentIndex(0)
    # dialog.descriptionText.setEnabled(True)
    dialog.fileButton.setEnabled(True)
    dialog.areaFileButton.setEnabled(True)
    dialog.nameSelect.setEnabled(True)
    dialog.resolutionText.setEnabled(True)
    dialog.bufferText.setEnabled(True)
    dialog.plannerButton.setEnabled(True)
    dialog.treeSelect.currentIndexChanged.emit(1)
    dialog.treeSelect.setVisible(False)
    dialog.copyCheckBox.setChecked(True)
    dialog.adjustSize()


def initialize_tree(dockwidget, dialog, type, base_path):
    tree = dockwidget.treeWidget
    tree.clear()
    clear_all_caches()

    if ProjectTypeEnum.DEMAND_CURRENT == type:
        isok = check_planner_file(dialog.plannerText.text())
        if not isok:
            dialog.createButton.clicked.emit()
            return

    if dialog.copyCheckBox.isChecked():
        if all_fields_filled(dialog):
            old_tree_id = dialog.treeSelect.currentData().tree_id
            tree_id = copy_tree_into_new(dialog, type)
            delete_tree(old_tree_id)
            initialize_tree_from_db(dockwidget, tree_id)
        else:
            QMessageBox.information(None, "Error", "Please fill in all fields.")
            return
    else:
        tree_id = dialog.treeSelect.currentData().tree_id
        initialize_tree_from_db(dockwidget, dialog.treeSelect.currentData().tree_id)
    tree.expandAll()
    tree_node = get_tree_by_id(tree_id)
    load_file_as_layer(tree_node.file, tree_node.name)
    load_open_street_maps()
    # initialize temp folder
    type_prefix = ''
    if ProjectTypeEnum.SUPPLY == type:
        type_prefix = tree_node.name + '_supply_'
    elif ProjectTypeEnum.DEMAND_CURRENT == type:
        type_prefix = tree_node.name + '_demand_current_'
    elif ProjectTypeEnum.DEMAND_FUTURE == type:
        type_prefix = tree_node.name + '_demand_future_'
    from .io_utils import get_temp_folder_name

    # clean temp folder
    if os.path.exists(base_path):
        for f in os.listdir(base_path):
            if os.path.isfile(os.path.join(base_path, f)):
                try:
                    os.remove(os.path.join(base_path, f))
                except:
                    pass
            elif os.path.isdir(os.path.join(base_path, f)):
                shutil.rmtree(os.path.join(base_path, f), ignore_errors=True)
    else:
        os.makedirs(base_path)
    get_temp_folder_name(prefix=type_prefix, base_path=base_path)

    dialog.loadDockwidget.emit()
    dialog.close()


def all_fields_filled(dialog):
    return dialog.treeSelect.currentData().tree_id \
           and dialog.nameText.text() \
           and dialog.fileNameText.text() \
           and dialog.resolutionText.text() \
           and dialog.nameSelect.currentText() \
           and dialog.nameText.text() != "" \
           and dialog.fileNameText.text() != "" \
           and dialog.resolutionText.text() != "" \
           and dialog.nameSelect.currentText() != "" \
           and (not dialog.bufferText.isVisible() or (dialog.bufferText.text() and dialog.bufferText.text() != ""))
            # and dialog.descriptionText.text() \


def fill_attributes_select_box(box, file=None, custom_value=None, shp_only=False, map_selection=None):
    attributes = []
    print("triggered")
    if file:
        attributes = get_shape_attributes_list(str(file))
    elif map_selection:
        attributes = get_available_fields(map_selection)
        if map_selection == 'OSM buildings':
            attributes.append("calculate feature areas")
    box.clear()
    box.addItem("None")
    for attribute in attributes:
        box.addItem(attribute)
    if custom_value:
        if shp_only and is_shape_file_polygons(str(file)):
            box.addItem(custom_value)


def run_all_nodes(tree, tree_type, only_checked=False):
    save_tree(tree)
    child_count = count_items(tree)
    progress = show_calculating_dialog(child_count)
    result = run_all(tree, progress, only_checked=only_checked)
    progress.setValue(child_count)
    if result:
        show_result_dialog(tree_type)


def show_result_dialog(tree_type):
    # test = get_map()
    # load_file_as_layer("c:/temp/data.json", "test")
    my_file = Path(get_temp_folder_name() + "/planheat_result_" + str(tree_type) + ".csv")
    if my_file.is_file():
        dialog = ResultPopup()
        try:
            data = pandas.read_csv(my_file, sep="\t")
        except pandas.errors.EmptyDataError:
            QMessageBox.information(None, "Error", "No results found. Please run calculations first.")
        if data.shape[1] > 5:
            data['All districts'] = data.iloc[:, 4:].sum(1)
        dialog.exportButton.clicked.connect(lambda: export_data(data))
        dialog.folderButton.clicked.connect(lambda: open_result_folder(data))
        data.set_index(data['Class'] + " - " + data["Description"], inplace=True)
        dialog.sectorTable.setRowCount(data.shape[0] + 1)
        dialog.sectorTable.setColumnCount(1)
        dialog.districtTable.setRowCount(data.shape[1] - 2)
        dialog.districtTable.setColumnCount(1)
        plot = PlotCanvas(dialog, width=10, height=4, dpi=100)
        layout = dialog.verticalLayout
        layout.addWidget(plot)

        dialog.sectorTable.clearContents()
        dialog.districtTable.clearContents()
        fill_sector_table(data, dialog.sectorTable, plot)
        fill_district_table(data, dialog.districtTable, plot)
        dialog.districtTable.sortItems(0)
        dialog.sectorTable.sortItems(0)
        dialog.sectorTable.itemSelectionChanged.connect(lambda: plot.plot(dialog.sectorTable, dialog.districtTable, data))
        dialog.districtTable.itemSelectionChanged.connect(lambda: plot.plot(dialog.sectorTable, dialog.districtTable, data))
        dialog.setWindowModality(Qt.ApplicationModal)
        h_min = 9999
        w_min = 9999
        for screen in QGuiApplication.screens():
            h_min = min(screen.geometry().height(), h_min)
            w_min = min(screen.geometry().width(), w_min)
        dialog.adjustSize()
        dialog.resize(min(dialog.width(), w_min - 200), min(dialog.height(), h_min - 200))

        dialog.exec_()
    else:
        QMessageBox.information(None, "Error", "No results found. Please run calculations first.")


def open_result_folder(data):
    folder = get_temp_folder_name().replace("/", "\\") # "explorer /open" can't handle forward slashes
    print(folder)
    subprocess.Popen(r'explorer /open,"' + folder + "\\" + '"')


def export_data(data):
    file_name = QFileDialog.getSaveFileName(None, 'Export Data', '', 'CSV (*.csv)')[0]
    if file_name:
        data.to_csv(file_name, sep="\t")


def find_node_file_by_id(tree, node_id):
    iterator = QTreeWidgetItemIterator(tree)
    while iterator.value():
        node = iterator.value()
        if get_node_data(node).node_id == node_id:
            if get_node_data(node).file:
                return get_node_data(node).file
        iterator += 1
    return None


def find_node_map_selection_by_id(tree, node_id):
    iterator = QTreeWidgetItemIterator(tree)
    while iterator.value():
        node = iterator.value()
        if get_node_data(node).node_id == node_id:
            #print(get_node_data(node))
            if get_node_data(node).map_selection:
                return get_node_data(node).map_selection
        iterator += 1
    return None

def check_planner_file(planner_file):
    print("check_planner_file")

    planner_result_dict = dict()
    available_fields = {}
    available_fields["tertiary_heating_hot_extracted"] = None
    available_fields["tertiary_heating_medium_extracted"] = None
    available_fields["tertiary_heating_low_extracted"] = None
    available_fields["tertiary_heating_dhw_extracted"] = None
    available_fields["tertiary_heating_cooling_extracted"] = None
    available_fields["residential_heating_hot_extracted"] = None
    available_fields["residential_heating_medium_extracted"] = None
    available_fields["residential_heating_low_extracted"] = None
    available_fields["residential_heating_dhw_extracted"] = None
    available_fields["residential_heating_cooling_extracted"] = None
    unit, timestep = "MWh", "y"

    with open(planner_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row and len(row) > 1:
                description, value = row[0], float(row[1])
                unit, timestep = description.split("_")[-3:-1]
                for key in available_fields.keys():
                    if description.startswith(key):
                        available_fields[key] = description

    warning_message, warn_user = "Be carefull, the values for:\n", False
    for k in available_fields:
        if not available_fields[k]:
            warn_user = True
            warning_message += "\t- {0}_{1}_{2}\n".format(k, unit, timestep)
    warning_message += "are not available in the usefull energy demand file.\n" 
    warning_message += "Would you like to continue ?"
    if warn_user:
        msg = QMessageBox()    
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        msg.setWindowTitle("Warning ")
        msg.setText(warning_message)
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            return True
        else:
            return False
    return True
