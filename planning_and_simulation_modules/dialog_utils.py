import importlib
import site

importlib.reload(site)
from pathlib import Path
import pandas
import os

importlib.reload(pandas)
from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QCursor, QDoubleValidator, QBrush, QGuiApplication
from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem, QMessageBox, QMenu, QAction, QProgressDialog, QApplication, QWidget, QTreeWidgetItemIterator

from .algorithm_node_popup import AlgorithmNodePopup
from .supply_algorithm_node_popup import SupplyAlgorithmNodePopup
from .algorithm_utils import valid_structure, get_selected_energy_types, run_all, set_progress, run_algorithm_for_node, get_crop_and_straw_yield_value, get_crop_yield_value,calculate_straw_yield, clear_all_caches
from .database_utils import get_energy_types, get_algorithms, get_trees, copy_tree_into_new, initialize_tree_from_db, get_tree_by_id, get_node_file_by_id, save_tree, delete_tree, \
    get_algorithm_by_id_and_default, get_energy_production_factor, get_algorithms_for_type, get_next_node_id
from .energy_node_popup import EnergyNodePopup
from .io_utils import get_shape_attributes_list, is_shape_file_polygons
from .layer_utils import load_file_from_dialog_as_layer, load_file_as_layer, load_open_street_maps
from .load_tree_popup import LoadTreePopup
from .models import Parameter, TreeNode
from .node_utils import set_node_icon, get_node_data, add_node, find_parent_node, has_checked_energy_node_children, delete_node, is_energy_node, count_items
from .result_popup import ResultPopup
from .result_utils import PlotCanvas, fill_sector_table, fill_district_table
from .enums import AlgorithmEnum, TypeEnum, ProjectTypeEnum

PROD = True


def open_right_click_menu(tree):
    menu = QMenu(tree)
    if tree.selectedItems():
        node = tree.selectedItems()[0]
        node_data = get_node_data(node)

        properties = QAction("Properties", tree)
        properties.triggered.connect(lambda: node_preferences_action(node, 0))
        menu.addAction(properties)



        if node_data.file is not None:
            open_layer = QAction("Open file as layer", tree)
            open_layer.triggered.connect(lambda: load_file_as_layer(node_data.file, node_data.description))
            menu.addAction(open_layer)
        else:
            calculate = QAction("Add input data", tree)
            calculate.triggered.connect(lambda: add_energy_node_to_algorithm_node_action(None, node))
            menu.addAction(calculate)
            calculate = QAction("Calculate", tree)
            calculate.triggered.connect(lambda: calculate_algorithm_node_action(node))
            menu.addAction(calculate)

        if not PROD:
            delete = QAction("Delete item", tree)
            delete.triggered.connect(lambda: delete_node(node))
            menu.addAction(delete)
            if node_data.file is None:
                delete = QAction("Add Child node", tree)
                delete.triggered.connect(lambda: add_child_to_node_action(node))
                menu.addAction(delete)

        menu.popup(QCursor.pos())


def node_preferences_action(node, column):
    if is_energy_node(node):
        select_energy_node_dialog(node)
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
        lambda: fill_attributes_select_box(dialog.param3IdFieldSelect, find_node_file_by_id(node.treeWidget(), dialog.param3Select.currentData())))
    dialog.param3Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param3DataFieldSelect, find_node_file_by_id(node.treeWidget(), dialog.param3Select.currentData())))

    dialog.param4Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param4IdFieldSelect, find_node_file_by_id(node.treeWidget(), dialog.param4Select.currentData())))
    dialog.param4Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param4DataFieldSelect, find_node_file_by_id(node.treeWidget(), dialog.param4Select.currentData())))

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

        if node.childCount() > 0:
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
                        fill_attributes_select_box(dialog.param3IdFieldSelect, selection_file)
                        fill_attributes_select_box(dialog.param3DataFieldSelect, selection_file)
                    dialog.param3IdFieldSelect.setCurrentIndex(dialog.param3IdFieldSelect.findText(value.id_field))
                    dialog.param3DataFieldSelect.setCurrentIndex(dialog.param3DataFieldSelect.findText(value.data_field))
                elif key == 4:
                    index = dialog.param4Select.findData(value.value)
                    if index != -1:
                        dialog.param4Select.setCurrentIndex(index)
                    if value.value:
                        selection_file = find_node_file_by_id(node.treeWidget(), value.value)
                        fill_attributes_select_box(dialog.param4IdFieldSelect, selection_file)
                        fill_attributes_select_box(dialog.param4DataFieldSelect, selection_file)
                    dialog.param4IdFieldSelect.setCurrentIndex(dialog.param4IdFieldSelect.findText(value.id_field))
                    dialog.param4DataFieldSelect.setCurrentIndex(dialog.param4DataFieldSelect.findText(value.data_field))
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

    dialog.param1Select.currentIndexChanged.connect(
        lambda: fill_attributes_select_box(dialog.param1IdFieldSelect, find_node_file_by_id(node.treeWidget(), dialog.param1Select.currentData()), "calculate feature areas", True))

    dialog.algorithmSelect.clear()
    for key, value in algorithms.items():
        dialog.algorithmSelect.addItem(value.description, key)

    dialog.bufferText.setText(str(node_data.buffer))

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
                    if value.value:
                        selection_file = find_node_file_by_id(node.treeWidget(), value.value)
                        fill_attributes_select_box(dialog.param1IdFieldSelect, selection_file, "calculate feature areas", True)
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
        if is_energy_node(child_node):
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
            if is_energy_node(child_node):
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
        dialog.param1Label.setText("Weights map:")
        dialog.param2Label.setText("Urban heat island indicator map:")

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
    for i in range(1, number_of_parameters + 1):
        if i == 1:
            dialog.param1Group.setVisible(True)
        if i == 2:
            dialog.param2Group.setVisible(True)
        if i == 3:
            dialog.param3Group.setVisible(True)
        if i == 4:
            dialog.param4Group.setVisible(True)
        if i == 5:
            dialog.param5Group.setVisible(True)
    if algorithm.algorithm_id == AlgorithmEnum.NONE:
        dialog.calculateButton.setEnabled(False)
    else:
        dialog.calculateButton.setEnabled(True)

    if algorithm.algorithm_id == AlgorithmEnum.SUM:
        dialog.param6Group.setVisible(False)
        dialog.scrollArea.setVisible(False)
    if algorithm.algorithm_id == AlgorithmEnum.PROVIDED:
        dialog.param1Label.setText("Result map:")
        dialog.param2Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)
    if algorithm.algorithm_id == AlgorithmEnum.SOLAR:
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.param1Label.setText("Solar input:")
        dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Label.setText("Technical suitability:")
        dialog.param2InputText.setVisible(True)
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("%")
        dialog.param2Select.setVisible(False)
        dialog.param3Label.setText("PVGIS dataset:")
        dialog.param5Label.setText("Spatial constraints:")
        dialog.param4Group.setVisible(False)
        dialog.param6InputText.setText("75")
    if algorithm.algorithm_id == AlgorithmEnum.BIO_FORESTERY:
        dialog.param1Label.setText("Forest areas:")
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Label.setText("Energy production factor:")
        dialog.param3Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)
    if algorithm.algorithm_id == AlgorithmEnum.CEREALS \
            or algorithm.algorithm_id == AlgorithmEnum.GRAIN_MAIZE \
            or algorithm.algorithm_id == AlgorithmEnum.WHEAT \
            or algorithm.algorithm_id == AlgorithmEnum.BARLEY \
            or algorithm.algorithm_id == AlgorithmEnum.RAPE_SEEDS:
        dialog.param1Label.setText("Agriculture areas:")
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Label_2.setVisible(True)
        dialog.param2InputText.setVisible(True)
        dialog.param2Label.setText("Average crop yield:")
        dialog.param2Label_2.setText("Average straw yield:")
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
        crop_yield, straw_yield = get_crop_and_straw_yield_value(node, algorithm)
        dialog.param2InputText.setText(str(crop_yield))
        dialog.param2ValueLabel_2.setText(str(straw_yield))
        dialog.param3InputText.setText("50")
        dialog.param4InputText.setText(str(get_energy_production_factor(algorithm.algorithm_id)))
        dialog.param4UnitLabel.setText("MWh/kg")
    if algorithm.algorithm_id == AlgorithmEnum.BASIC_AGRICULTURE:
        dialog.param1Label.setText("Agriculture areas:")
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param2InputText.setVisible(True)
        dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2Label.setText("Energy production factor:")
        crop_yield= get_crop_yield_value(node, algorithm)
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
        dialog.param1Label.setText("Sewer system:")
        dialog.monthGroup.setVisible(True)
        dialog.monthTitle.setText("Average effluent temperature")
    if algorithm.algorithm_id in [AlgorithmEnum.RIVERS_HEAT, AlgorithmEnum.RIVERS_COLD, AlgorithmEnum.RIVERS_FREE_COLD]:
        dialog.monthGroup.setVisible(True)
        dialog.param1Label.setText("Rivers:")
        dialog.idField1Label.setVisible(True)
        dialog.param1IdFieldSelect.setVisible(True)
        dialog.param1Group.setMinimumHeight(140)
        dialog.param1GroupBox.setVisible(True)
        dialog.idField1Label.setText("Value to rasterize:")
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param2Label.setText("Global water flow value:")
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("m³/h")
        dialog.param3Label.setText("Spatial constraints:")
        dialog.bufferGroup.setVisible(True)
        dialog.monthTitle.setText("Average water temperature")
    if algorithm.algorithm_id == AlgorithmEnum.LAKES_HEAT:
        dialog.param1Label.setText("Lakes:")
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
        dialog.param3Select.setVisible(False)
        dialog.param3Label.setText("Fixed global depth:")
        dialog.param3UnitLabel.setText("m")
        dialog.param4Label.setText("Spatial constraints:")
        dialog.param4InputText.setVisible(False)
        dialog.param4UnitLabel.setVisible(False)
        dialog.param4Select.setVisible(True)
        dialog.bufferGroup.setVisible(True)
        dialog.monthTitle.setText("Average water temperature")
    if algorithm.algorithm_id == AlgorithmEnum.LAKES_COLD:
        dialog.param1Label.setText("Lakes:")
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
        dialog.param3Label.setText("Fixed global depth:")
        dialog.param4Label.setText("Spatial constraints:")
        dialog.param4InputText.setVisible(False)
        dialog.param4UnitLabel.setVisible(False)
        dialog.param4Select.setVisible(True)
        dialog.bufferGroup.setVisible(True)
        dialog.monthTitle.setText("Average water temperature")
    if algorithm.algorithm_id == AlgorithmEnum.SHALLOW_GEOTHERMAL:
        dialog.param1Label.setText("Area:")
        dialog.param2InputText.setVisible(True)
        dialog.param2Select.setVisible(False)
        dialog.param2Label.setText("Yearly potential:")
        dialog.param2UnitLabel.setVisible(True)
        dialog.param2UnitLabel.setText("kWh/year")
        dialog.param3Label.setText("Spatial constraints:")
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

    if not has_checked_energy_node_children(node):
        QMessageBox.information(None, "Error", "Please select at least one child node.")
    elif algorithm_id == 1:
        QMessageBox.information(None, "Error", "Please select a algorithm.")
    else:
        if valid_structure(node):
            progress = show_calculating_dialog(2)
            set_progress(progress)
            for energy_type in get_selected_energy_types(node):
                run_algorithm_for_node(node, energy_type, algorithm_id)
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


def select_energy_node_dialog(node, new=False):
    node_data = get_node_data(node)

    dialog = EnergyNodePopup()
    dialog.fileButton.clicked.connect(lambda: select_file_for_dialog_action(dialog.fileNameText))
    dialog.loadLayerButton.clicked.connect(lambda: load_file_from_dialog_as_layer(dialog))
    dialog.okButton.clicked.connect(lambda: save_energy_node_dialog_action(dialog, node, new))
    dialog.cancelButton.clicked.connect(lambda: close_and_remove_empty_node(dialog, node, new))
    dialog.fileNameText.textChanged.connect(lambda: fill_attributes_select_box(dialog.attributeSelect, dialog.fileNameText.text()))

    if not new:
        dialog.fileNameText.setText(str(node_data.file))
        fill_attributes_select_box(dialog.attributeSelect, dialog.fileNameText.text())
        dialog.attributeSelect.setCurrentIndex(dialog.attributeSelect.findText(node_data.shape_attribute))
        dialog.descriptionText.setText(str(node_data.description))

    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.exec_()


def close_and_remove_empty_node(dialog, node, new):
    if new:
        node_data = get_node_data(node)
        tree = node.treeWidget()
        parent_node = find_parent_node(tree, node_data.main_node_id)
        parent_node.removeChild(node)
    dialog.close()


def add_energy_node_to_algorithm_node_action(from_dialog, existing_node):
    existing_node_data = get_node_data(existing_node)
    if not existing_node_data.node_id:
        QMessageBox.information(None, "Error", "Please save first before adding items to a new child node.")
    else:
        new_node = create_new_node(existing_node)
        select_energy_node_dialog(new_node, True)
        if from_dialog:
            fill_select_boxes_with_data_nodes(from_dialog, existing_node)


def create_new_node(existing_node):
    existing_node_data = get_node_data(existing_node)
    new_node = QTreeWidgetItem(existing_node)

    new_node_data = TreeNode(get_next_node_id(), existing_node_data.tree_id, existing_node_data.node_id, 0, None, None, None, None, None, None, None, None, None,
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
    if path == 'None':
        path = None
    if not path:
        path = "c:/TEMP/"
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
        directory = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(directory, "saves")

    file_path = QFileDialog.getOpenFileName(qfd, title, path, "Planner files (*.csv)")[0]
    if file_path:
        text_box.setText(str(file_path))


def save_energy_node_dialog_action(dialog, node, new):
    if dialog.fileNameText.text() and dialog.fileNameText.text() != "None":
        node_data = get_node_data(node)
        node_data.description = str(dialog.descriptionText.text())
        node.setText(0, str(dialog.descriptionText.text()))
        if dialog.fileNameText.text() and dialog.fileNameText.text() != "None":
            node_data.file = str(dialog.fileNameText.text())
        if dialog.attributeSelect.currentText() and dialog.attributeSelect.currentText() != "None":
            node_data.shape_attribute = str(dialog.attributeSelect.currentText())
        node_data.set_energy_type(1, get_energy_types()[1])
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


def load_tree_dialog(dockwidget, type):
    tree_dict = get_trees(type)
    dialog = LoadTreePopup()
    dialog.titleLabel.setText("Open a project")
    dialog.okButton.setText("Continue")
    dialog.cancelButton.setVisible(False)
    dialog.descriptionText.setVisible(False)
    dialog.nameText.setVisible(False)
    dialog.copyCheckBox.setChecked(False)
    dialog.copyCheckBox.setVisible(False)
    dialog.fileButton.clicked.connect(lambda: load_file_for_tree_dialog(dialog))
    dialog.areaFileButton.clicked.connect(lambda: select_file_for_dialog_action(dialog.areaFileText))
    dialog.plannerButton.clicked.connect(lambda: select_planner_file_for_dialog_action(dialog.plannerText))
    dialog.okButton.clicked.connect(lambda: initialize_tree(dockwidget, dialog, type))
    dialog.copyButton.clicked.connect(lambda: tree_copy_clicked(dockwidget, dialog, type))
    dialog.createButton.clicked.connect(lambda: tree_create_clicked(dockwidget, dialog, type))
    dialog.cancelButton.clicked.connect(lambda: tree_cancel_clicked(dockwidget, dialog, type))
    dialog.deleteButton.clicked.connect(lambda: remove_tree(dockwidget, dialog, type))
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
    dialog.treeSelect.clear()
    for key, value in tree_dict.items():
        if key not in [1, 2, 3]:
            dialog.treeSelect.addItem(value.name, value)

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
    fill_attributes_select_box(dialog.nameSelect, dialog.fileNameText.text())


def remove_tree(dockwidget, dialog, type):
    qm = QMessageBox
    ret = qm.question(None, 'Warning', "Delete this project?", qm.Yes | qm.No)

    if ret == qm.Yes:
        tree = dockwidget.treeWidget
        tree.clear()
        dockwidget.titleLabel.setText("")
        delete_tree(dialog.treeSelect.currentData().tree_id)
        dialog.close()
        load_tree_dialog(dockwidget, type)


def update_tree_selection(dialog):
    if dialog.treeSelect.currentData() is not None:
        if dialog.treeSelect.currentData().tree_id not in [1, 2, 3]:
            dialog.nameText.setText(dialog.treeSelect.currentData().name)
        else:
            dialog.nameText.setText('')
        dialog.descriptionText.setText(dialog.treeSelect.currentData().description)
        dialog.descriptionLabel.setText(dialog.treeSelect.currentData().description)

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
        fill_attributes_select_box(dialog.nameSelect, dialog.treeSelect.currentData().file)
        dialog.nameSelect.setCurrentIndex(dialog.nameSelect.findText(str(dialog.treeSelect.currentData().attribute_name)))
        dialog.plannerText.setText(str(dialog.treeSelect.currentData().planner_file))


def tree_cancel_clicked(dockwidget, dialog, type):
    dialog.titleLabel.setText("Open a project")
    dialog.okButton.setText("Continue")
    dialog.cancelButton.setVisible(False)
    dialog.descriptionText.setVisible(False)
    dialog.nameText.setVisible(False)
    dialog.copyCheckBox.setChecked(False)
    dialog.buttonGroup.setVisible(True)
    dialog.deleteButton.setVisible(True)
    dialog.descriptionLabel.setVisible(True)
    dialog.fileButton.setEnabled(False)
    dialog.areaFileButton.setEnabled(False)
    dialog.nameSelect.setEnabled(False)
    dialog.resolutionText.setEnabled(False)
    dialog.bufferText.setEnabled(False)
    dialog.plannerButton.setEnabled(False)
    dialog.treeSelect.setVisible(True)

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
    dialog.titleLabel.setText("Create a project")
    dialog.okButton.setText("Create Project")
    dialog.nameText.setVisible(True)
    dialog.buttonGroup.setVisible(False)
    dialog.cancelButton.setVisible(True)
    dialog.deleteButton.setVisible(False)
    dialog.descriptionText.setVisible(True)
    dialog.descriptionLabel.setVisible(False)
    dialog.descriptionText.setEnabled(True)
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
    dialog.titleLabel.setText("Create a project")
    dialog.okButton.setText("Create Project")
    dialog.nameText.setVisible(True)
    dialog.buttonGroup.setVisible(False)
    dialog.cancelButton.setVisible(True)
    dialog.deleteButton.setVisible(False)
    dialog.descriptionText.setVisible(True)
    dialog.descriptionLabel.setVisible(False)
    dialog.treeSelect.setCurrentIndex(0)
    dialog.descriptionText.setEnabled(True)
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


def initialize_tree(dockwidget, dialog, type):
    tree = dockwidget.treeWidget
    tree.clear()
    clear_all_caches()
    if dialog.copyCheckBox.isChecked():
        if all_fields_filled(dialog):
            tree_id = copy_tree_into_new(dialog, type)
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

    dialog.close()


def all_fields_filled(dialog):
    return dialog.treeSelect.currentData().tree_id \
           and dialog.descriptionText.text() \
           and dialog.nameText.text() \
           and dialog.fileNameText.text() \
           and dialog.resolutionText.text() \
           and dialog.nameSelect.currentText() \
           and dialog.nameText.text() != "" \
           and dialog.fileNameText.text() != "" \
           and dialog.resolutionText.text() != "" \
           and dialog.nameSelect.currentText() != "" \
           and (not dialog.bufferText.isVisible() or (dialog.bufferText.text() and dialog.bufferText.text() != ""))


def fill_attributes_select_box(box, file, custom_value=None, shp_only=False):
    attributes = get_shape_attributes_list(str(file))
    box.clear()
    box.addItem("None")
    for attribute in attributes:
        box.addItem(attribute)
    if custom_value:
        if shp_only and is_shape_file_polygons(str(file)):
            box.addItem(custom_value)


def run_all_nodes(tree, tree_type):
    save_tree(tree)
    child_count = count_items(tree)
    progress = show_calculating_dialog(child_count)
    result = run_all(tree, progress)
    progress.setValue(child_count)
    if result:
        show_result_dialog(tree_type)


def show_result_dialog(tree_type):
    # test = get_map()
    # load_file_as_layer("c:/temp/data.json", "test")
    my_file = Path("C:/TEMP/planheat_result_" + str(tree_type) + ".csv")
    if my_file.is_file():
        dialog = ResultPopup()
        data = pandas.read_csv(my_file, sep="\t")
        if data.shape[1] > 5:
            data['All districts'] = data.iloc[:, 4:].sum(1)
        dialog.exportButton.clicked.connect(lambda: export_data(data))
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


def export_data(data):
    file_name = QFileDialog.getSaveFileName(None, 'Export Data', '', 'CSV (*.csv)')[0]
    if file_name:
        data.to_csv(file_name, sep="\t")


def find_node_file_by_id(tree, node_id):
    file = get_node_file_by_id(node_id)
    if file:
        return file
    iterator = QTreeWidgetItemIterator(tree)
    while iterator.value():
        node = iterator.value()
        if get_node_data(node).node_id == node_id:
            return get_node_data(node).file
        iterator += 1
    return None
