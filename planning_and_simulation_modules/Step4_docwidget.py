import os
import sys
import logging
import os.path
import shutil
import traceback
# Import pandas to manage data into DataFrames
import pandas

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
# Import PyQt5
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import QAction, QMenu, QInputDialog, QLineEdit, QListWidgetItem
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem

# Import qgis main libraries
from qgis.core import *
from qgis.core import QgsProject
from qgis.gui import *
from qgis.utils import *
# Import the custom tree widget items
from .building.Building import *
from .building.DPM import *
from .building.TreeItemManager import TreeItemManager
from .technology.Technology import *
from .Network import Network
from .layer_utils import load_file_as_layer, add_layer_to_group, get_only_new_features
from .dialogSources import CheckSourceDialog
from .simpleDialog import Form
from .Tjulia.DistrictSimulator import DistrictSimulator
from .Tjulia.test.MyLog import MyLog
from .Transport.Transport_electrical_vehicles_demand import Transport_sector
from .AdditionalSimulationParameterGUI import AdditionalSimulationParameterGUI
from .VITO.mapping.MappingModuleInterface import MappingModuleInterface

from .dhcoptimizerplanheat.ui.ui_utils import add_group
from .dhcoptimizerplanheat.dhcoptimizer_planheat import DHCOptimizerPlanheat
from .building.CustomContextMenu import CustomContextMenu
from .utility.BuildingCharacterization.BuildingCharacterizationService import BuildingCharacterizationService
from .utility.NetworkCharacterization.NetworkCharacterizationService import NetworkCharacterizationService
from .utility.NetworkCharacterization.NetworkEfficiency import NetworkEfficiency
from .utility.DataTransfer import DataTransfer
from .config.services.SourcesTableDefaultLoader import SourcesTableDefaultLoader


from .test.QtTreeWidgetPrinter import QtTreeWidgetPrinter

from .save_utility.AoutLoadNetwork import AutoLoadNetwork



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'Step4.ui'))


class Step4_widget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    step4_closing_signal = pyqtSignal()

    street_layer = None
    building_layer = None

    # network_type = None

    def __init__(self, data_transfer=None, work_folder=None, parent=None):
        """Constructor."""
        super(Step4_widget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface

        locale_en_us = QLocale(QLocale.English, QLocale.UnitedStates)
        self.setLocale(locale_en_us)

        self.phases.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        self.future_scenario = None
        self.init_connections_future()
        self.work_folder = work_folder


        #self.futureDHN_network_list = []
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "add.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.addNetwork.setIcon(icon)
        self.addDCN.setIcon(icon)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "app.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.insertNetwork.setIcon(icon)
        self.insertCooling.setIcon(icon)
        self.insertDHW.setIcon(icon)
        self.insertHeating.setIcon(icon)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "delete.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.remove_cool.setIcon(icon)
        self.removeDhw.setIcon(icon)
        self.remove_heat.setIcon(icon)
        self.remove_tech_network.setIcon(icon)
        self.remove_tech_network.clicked.connect(self.remove_tech_from_network)
        self.remove_cool.clicked.connect(lambda: self.remove_tech("Cooling"))
        self.remove_heat.clicked.connect(lambda: self.remove_tech("Heating"))
        self.removeDhw.clicked.connect(lambda: self.remove_tech("DHW"))

        self.additional_parameters_btn.clicked.connect(self.additional_parameters_btn_handler)

        self.listNetworkDCN.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listNetworkDCN.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.futureDHN.hide()
        self.futureDCN.hide()
        self.label_22.hide()
        self.phases.setTabEnabled(1, False)
        self.phases.setTabEnabled(2, False)
        self.tabWidget.setTabEnabled(0, False)
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)
        self.trasport_sector_calc = Transport_sector()
        self.future_list_input=[]
        self.futureDHN_network_list = []
        self.futureDCN_network_list = []


        # self.setPipeDiameter.clicked.connect(self.futureDHN_pipes_selected)
        # self.setPipeDiameter_DCN.clicked.connect(self.futureDCN_pipes_selected)

        # self.connect_future.clicked.connect(self.future_insert_point)
        self.addNetwork.clicked.connect(self.add_DHN_network)
        self.remove_network.clicked.connect(self.remove_DHN_networks)
        # self.connectBuildingsToDHN.clicked.connect(self.connect_building_toDHN)
        # self.connect_future.clicked.connect(self.connect_building_toDCN)
        # self.add_buildings_DHN.clicked.connect(self.add_buildings_to_DHN_networks)
        # self.remove_buildings_DHN.clicked.connect(self.remove_buildings_from_DHN_networks)
        # self.add_streets_DHN.clicked.connect(self.add_streets_to_networks)
        # self.remove_streets_DHN.clicked.connect(self.remove_streets_from_DHN_networks)
        self.listWidget_future.itemSelectionChanged.connect(self.refresh_DHN_network_buildings)
        self.listWidget_future.itemSelectionChanged.connect(self.refresh_DHN_network_streets)
        self.listNetworkDCN.itemSelectionChanged.connect(self.refresh_DCN_network_buildings)
        self.listNetworkDCN.itemSelectionChanged.connect(self.refresh_DCN_network_streets)
        self.addDCN.clicked.connect(self.add_DCN_network)
        self.removeDCN.clicked.connect(self.remove_DCN_networks)
        # self.add_buildings_DCN.clicked.connect(self.add_buildings_to_DCN_networks)
        # self.remove_buildings_DCN.clicked.connect(self.remove_buildings_from_DCN_networks)
        # self.add_streets_DCN.clicked.connect(self.add_streets_to_DCN_networks)
        # self.remove_streets_DCN.clicked.connect(self.remove_streets_from_DCN_networks)
        self.AD_optimizer_DHN.clicked.connect(self.DHN_optimization)
        self.AD_optimizer_DCN.clicked.connect(self.DCN_optimization)
        self.futurePeakDemandCooling.clicked.connect(self.insert_PeakDemandCooling_future)
        self.futurePeakDemandDhw.clicked.connect(self.insert_PeakDemandDhw_future)
        self.futurePeakDemandHeating.clicked.connect(self.insert_PeakDemandHeating_future)
        self.dmmTree_future.itemChanged.connect(self.building_characterizzation_changed)

        self.futureDmmTreeNetwork.itemClicked.connect(self.network_tree_widget_clicked)

        self.opt = None

        #self.future_dialog = None
        self.future_dialog = Form()
        self.future_dialog.futureInputDemand.connect(self.future_val_demand)

        # self.future_source_dhw.clicked.connect(self.allocateFuture_sources_DHW)
        # self.future_source_heating.clicked.connect(self.allocateFuture_sources_heating)
        # self.future_source_cooling.clicked.connect(self.allocateFuture_source_cooling)
        self.future_dialog_source = CheckSourceDialog()
        # self.future_source_network.clicked.connect(self.allocateFuture_source_network)
        self.future_dialog_source.okButton.clicked.connect(self.future_recived_sources_selected)

        self.heatingTechnology.currentIndexChanged.connect(self.futureActive_source_dialog)
        self.coolingTechnology.currentIndexChanged.connect(self.futureActive_input_cooling)
        self.dhwTechnology.currentIndexChanged.connect(self.futureActive_source_dialogDHW)
        self.networkTechnology.currentIndexChanged.connect(self.futureActive_source_dialogNetwork)

        self.tabWidget.currentChanged.connect(self.tab_current_changed)

        self.disable_all_cooling()
        self.disable_all_heating_input()
        self.disable_all_dhw_input()

        self.disable_all_network_input()

        self.future_sourceRead = ""
        self.future_sourceNet = ""
        self.future_sourceDhw = ""
        self.future_sourceCool = ""

        self.data_transfer = None
        self.dialog_dock = True
        self.muted = False

        self.save_to_webserver.clicked.connect(self.check_tech_capacity)
        self.future_simulator = DistrictSimulator()

        self.heatingTechnology.setItemData(2, 0, Qt.UserRole - 1)
        self.heatingTechnology.setItemData(10, 0, Qt.UserRole - 1)
        self.heatingTechnology.setItemData(17, 0, Qt.UserRole - 1)
        self.dhwTechnology.setItemData(2, 0, Qt.UserRole - 1)
        self.dhwTechnology.setItemData(11, 0, Qt.UserRole - 1)
        self.dhwTechnology.setItemData(18, 0, Qt.UserRole - 1)
        self.networkTechnology.setItemData(0, 0, Qt.UserRole - 1)
        self.networkTechnology.setItemData(8, 0, Qt.UserRole - 1)
        self.networkTechnology.setItemData(12, 0, Qt.UserRole - 1)
        self.networkTechnology.setItemData(28, 0, Qt.UserRole - 1)
        self.networkTechnology.setItemData(36, 0, Qt.UserRole - 1)
        # self.saveDCN_future.clicked.connect(self.future_DCN_to_save)
        # self.saveDhn_future.clicked.connect(self.future_DHN_to_save)

        self.network_service = NetworkCharacterizationService(self)
        self.building_service = BuildingCharacterizationService(self)

        self.dhwhCheck.hide()

        self.DCN_state = False
        self.DHN_state = False

        self.technology_temp_70 = ["Waste Heat Compression Heat Pump High T"]
        self.technology_temp40_70 = ["Air Source Compression Heat Pump", "Shallow geothermal compression heat pump",
                                     "Evacuated tube solar collectors",
                                     "Waste heat compression heat pump medium T", "Seasonal waste heat heat pumps",
                                     "Waste heat absorption heat pump",
                                     "Waste heat - heat pump – temperature group 2"]

        self.technology_temp_40 = ["Flat plate solar collectors", "Waste heat compression heat pump low T",
                                   "Waste heat - heat pump – temperature group 1 "]

        mapping_module_interface = MappingModuleInterface()
        self.KPIs_additional_data = {
            "years": mapping_module_interface.get_future_year() - mapping_module_interface.get_baseline_year()}


        SourcesTableDefaultLoader.load_default(self.suppliesTable_future)
        SourcesTableDefaultLoader.hide_default_rows(self.suppliesTable_future)
        self.suppliesTable_future.hideRow(7)
        # self.show

        self.step0_source_availability_table = None
        self.tree_item_manager = TreeItemManager(self.iface, self.dmmTree_future, self.futureDmmTreeNetwork,
                                                 [self.futureDCN_network_list, self.futureDHN_network_list])
        self.network_efficiency = NetworkEfficiency(self.efficiency_label, self.efficiency_spin_box,
                                                    self.futureDHN_network_list, self.futureDCN_network_list,
                                                    self.futureDmmTreeNetwork)
        self.efficiency_push_button.clicked.connect(self.network_efficiency.update_network_efficiency)

        self.print_network_tree.clicked.connect(lambda: QtTreeWidgetPrinter.printer(self.futureDmmTreeNetwork))
        self.print_network_tree.hide()

    def closeEvent(self, event):
        #self.closingPlugin.emit()
        self.closeStep4()
        event.accept()

    def closeStep4(self):
        try:
            self.dialog_additional_parameters.cancel.clicked.emit()
        except AttributeError:
            pass
        self.hide()
        self.step4_closing_signal.emit()

    def init_connections_future(self):
        # add context menu to the tree widget
        self.dmmTree_future.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )
        self.dmmTree_future.customContextMenuRequested.connect(
            self._menu
        )

        self.insertHeating.clicked.connect(
            lambda: self.insert_tech_future('heating')
        )

        self.insertCooling.clicked.connect(
            lambda: self.insert_tech_future('cooling')
        )

        self.insertDHW.clicked.connect(
            lambda: self.insert_tech_future('dhw')
        )

        self.dhwhCheck.stateChanged.connect(
            self.toggle_dhw_input
        )

        self.insertNetwork.clicked.connect(self.insert_technology)

    @staticmethod
    def load_layer(qgs_iface, path: str):
        """
        Load the selected layer into the canvas
        :param qgs_iface: main QGis interface
        :param path: path to the layer file (*.shp/*.tif)
        :return: the path to the layer and the Qgs layer object
        """
        if os.path.exists(path):
            layer_path, ext = os.path.splitext(path)
            name = layer_path.split('/')[-1]

            # If the layer is a shapefile copy it into memory
            if ext == '.shp':
                # Load the specified layer
                layer = QgsVectorLayer( path, 'dmm_output_source',  'ogr' )
                # Create the memory layer
                layer = qgs_iface.addVectorLayer(path, name, 'ogr')
            else:
                # Raise exception for unsupported files
                raise IOError(f'Unsupported file type: {path}')

            # Raise an exception if loading fails
            if not layer:
                raise IOError('Unable to load layer')
            elif not layer.isValid():
                raise IOError('Invalid Layer')
            else:
                return layer
        else:
            raise FileNotFoundError('Layer does not exist')

    @staticmethod
    def unload_layer(layer: QgsVectorLayer):
        """
        Unload the layer from the interface
        :param layer: the layer to be removed
        :return: Success or failure
        """
        try:
            QgsProject.instance().removeMapLayer(layer.id())
            return True
        except Exception as e:
            raise e

    @staticmethod
    def add_layer_fields(layer: QgsVectorLayer, new_fields: list):
        """
        Add fields to a layer
        :param layer: the layer to load the field into
        :param new_fields: the fields to be created as
        :return:
        """
        try:
            layer_dp = layer.dataProvider()
            caps = layer_dp.capabilities()
            if caps & QgsVectorDataProvider.AddAttributes:
                res = layer_dp.addAttributes(new_fields)
                if res:
                    QgsMessageLog.logMessage(
                        'Adding fields!!',
                        level=Qgis.Info
                    )
                else:
                    QgsMessageLog.logMessage(
                        'Impossible to add fields',
                        level=Qgis.Critical
                    )
                layer.updateFields()
        except Exception as e:
            raise e

    @staticmethod
    def delete_layer_fields(layer: QgsVectorLayer, fields: list):
        """
        Delete a list of fields
        :param layer:
        :param fields:
        :return:
        """
        try:
            layer_dp = layer.dataProvider()
            caps = layer_dp.capabilities()
            del_fields = [
                i for i, n in enumerate(
                    layer.getFeatures()) if n.name() in fields
            ]
            if caps & QgsVectorDataProvider.DeleteAttributes:
                res = layer_dp.deleteAttributes(del_fields)
                if res:
                    QgsMessageLog.logMessage(
                        'Deleting fields!!',
                        level=Qgis.Info
                    )
                else:
                    QgsMessageLog.logMessage(
                        'Impossible to delete fields',
                        level=Qgis.Critical
                    )
        except Exception as e:
            raise e

    @staticmethod
    def update_feature_attribute(layer, fid, attributes):
        """
        Modify attributes of a feature.
        :param layer: the layer the feature belongs to
        :param fid: the id of the feature
        :param attributes: the array with the attributes to be changed
        :return:
        """
        layer_dp = layer.dataProvider()
        caps = layer_dp.capabilities()
        if caps & QgsVectorDataProvider.ChangeAttributeValues:
            caps.changeAttributeValues({fid: attributes})

    def load_dpm_layer(self, layer):
        """
        Load the residential layer from dialog
        :return:
        """
        self.dmmTree_future.clear()
        # path_to_layer = self.layerPath.filePath()
        # if os.path.exists(path_to_layer):
        self.dpm_layer = layer
        # if self.dpm_layer.isValid()

        # The buildings in the baseline scenario
        self.building_layer = layer

        # Connect the layer selection to the tree selection
        self.dpm_layer.selectionChanged.connect(
            self.item_from_feature
        )
        # Load features in the DMM tree
        dmm_tree_root = self.dmmTree_future.invisibleRootItem()
        for feature in self.dpm_layer.getFeatures():
            building = Building(feature)
            building.scenario_type = "future"
            building.layer = self.dpm_layer
            dmm_tree_root.addChild(building)

    def unload_dpm_layer(self):
        """
        Unload the currently loaded residential layer
        :return:
        """
        QgsMessageLog.logMessage(
            f'Removing residential layer {self.dpm_layer.id()}',
            level=Qgis.Warning
        )
        PlanHeatDPM.unload_layer(self.dpm_layer)
        r = self.dmmTree_future.invisibleRootItem()
        for i in reversed(range(r.childCount())):
            r.removeChild(r.child(i))

    def insert_tech_future(self, demand: str):
        """
        Insert the given technology into the correct demand item of the
        building tree
        :param demand: the demand item of the building tree
        :return:
        """
        selected = self.dmmTree_future.selectedItems()

        i = 0
        if demand == 'cooling':

            t = str(
                self.coolingTechnology.currentText()
            )
            source = self.future_sourceCool
            inclinazione = self.coolingInclinazione.value()
            temperature = self.coolingTemp.value()
            eta_optical = self.coolingEfficiency.value()
            first_order = self.cooling1coeff.value()
            second_order = self.cooling2coeff.value()
            # capacity = self.coolingCapacity.value()

            p_max = self.P_max_cooling.value()
            p_min = self.P_min_cooling.value()
            powerToRatio = self.cb_CHP_cooling.value()

            tech_min = self.coolingTechMin.value()

            ramp_up_down = self.coolingRampUpDown.value()
            fix = self.coolingFixedCost.value()
            fuel = self.coolingFuelCost.value()
            variable = self.coolingVariableCost.value()

            tes_size = self.Tes_size_cooling.value()
            soc_min = self.cooling_socMin.value()
            tes_startEnd = self.cooling_tesStartEnd.value()
            tes_discharge = self.tes_discharge_cooling.value()
            COP_absorption = self.Cop_absorption_cooling.value()
            el_sale = 1
            tes_loss = 1


        elif demand == 'heating':

            t = str(
                self.heatingTechnology.currentText()
            )
            source = self.future_sourceRead
            inclinazione = self.heatingInclinazione.value()
            temperature = self.heatingTemp.value()
            eta_optical = self.heatingEfficiency.value()
            first_order = self.heating1coeff.value()
            second_order = self.heating2coeff.value()
            # capacity = self.heatingCapacity.value()
            p_max = self.P_max_heating.value()
            p_min = self.P_min_heating.value()
            powerToRatio = self.cb_CHP_heating.value()
            tech_min = self.heatingTechMin.value()
            ramp_up_down = self.heatingRampUpDown.value()
            fix = self.heatingFixedCost.value()
            fuel = self.heatingFuelCost.value()
            variable = self.heatingVariableCost.value()

            tes_size = self.Tes_size_heating.value()
            soc_min = self.Soc_min_heating.value()
            tes_startEnd = self.tes_startEnd_heating.value()
            tes_discharge = self.tes_discharge_heating.value()
            COP_absorption = self.COP_heating.value()
            el_sale = self.heatingElsale.value()
            tes_loss = self.heatingTES_loss.value()

            if self.dhwhCheck.isChecked():
                i = 3
            else:
                i = 1
        else:

            if self.dhwTechnology.currentIndexChanged:
                        print("dentro if")
            t=self.dhwTechnology.currentText()

            #t = str(
            #    self.dhwTechnology.currentText()
            #)
            source =self.future_sourceDhw
            inclinazione = self.dhwInclinazione.value()
            temperature = self.dhwTemp.value()
            eta_optical = self.dhwEfficiency.value()
            first_order = self.dhw1coeff.value()
            second_order = self.dhw2coeff.value()
            # capacity = self.dhwCapacity.value()
            p_max = self.dhwP_max.value()
            p_min = self.dhwP_min.value()
            powerToRatio = self.dhwCb_CHP.value()

            tech_min = self.dhwTechMin.value()

            ramp_up_down = self.dhwRampUpDown.value()
            fix = self.dhwFixedCost.value()
            fuel = self.dhwFuelCost.value()
            variable = self.dhwVariableCost.value()

            tes_size = self.dhwTes_size.value()
            soc_min = self.dhwSoc_min.value()
            tes_startEnd = self.dhwTes_startEnd.value()
            tes_discharge = self.dhwTes_discharge.value()
            COP_absorption = self.dhwCop.value()
            el_sale = self.dhwElsale.value()
            tes_loss = self.DHWTES_loss.value()

            i=2

        technology = t
        for b in selected:
            if b.isHidden():
                continue
            if b.child(i) is not None and not b.child(i).isHidden():
                b.child(i).addChild(
                    Technology(
                        technology,
                        source,
                        inclinazione,
                        temperature,
                        eta_optical,
                        first_order,
                        second_order,
                        p_max,
                        p_min,
                        powerToRatio,
                        tech_min,
                        ramp_up_down,
                        fix,
                        fuel,
                        variable,
                        tes_size,
                        soc_min,
                        tes_startEnd,
                        tes_discharge,
                        COP_absorption,
                        el_sale,
                        tes_loss
                    )
                )
                b.set_modified()

            # tmp = pandas.DataFrame()
        if technology in self.technology_temp40_70:
            if temperature > 70:
                self.vis_MsgError()

        if technology in self.technology_temp_40:
            if temperature > 40:
                self.vis_MsgError()

    def vis_MsgError(self):
        msgBox = QMessageBox()
        msgBox.setText("WARNING: the input supply temperature does not match the temperature level of the selected technology.")
        msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.Cancel:
            return False
        else:
            return True

    def item_from_feature(self, selected, deselected, clear_select):
        """
        Select a building in the tree. This is a pyqtSlot catching the
        selectionChanged signal
        :return:
        """
        buildings = self.dmmTree_future.invisibleRootItem()
        if clear_select:
            for i in selected:
                buildings.child(i).setSelected(True)
            for j in deselected:
                buildings.child(j).setSelected(False)

    def allocateFuture_source_network(self):
        self.dialog_source.tech_source = "network"
        self.dialog_source.vis_interfaccia(self.networkTechnology.currentText())
        self.dialog_source.show()




    def connect_to_dcn_future(self):
        """
        Connect selected buildings to the DCN.
        :return:
        """
        selected = self.dmmTree_future.selectedItems()
        dcn = self.dcnSelector.currentText()
        for b in selected:
            if isinstance(b, Building):
                b.toggle_dcn(dcn)

    def _menu(self, point):
        """
        Open the context menu for the trees of the widget
        :return:
        """
        print("Step4._menu point:", type(point), point)
        selected = self.dmmTree_future.itemAt(point)
        print("Step4._menu point:", type(selected), selected)
        menu = QMenu()
        if isinstance(selected, Technology):
            remove = QAction(
                '&Remove Techonolgy',
                self.dmmTree_future,
            )
            remove.triggered.connect(selected.remove_technology)
            menu.addAction(remove)
        elif isinstance(selected, Building):
            if selected.dcn:
                disconnect_from_dcn = QAction(
                    '&Disconnect from DCN',
                    self.dmmTree_future
                )
                disconnect_from_dcn.triggered.connect(selected.toggle_dcn)
                menu.addAction(disconnect_from_dcn)
            if selected.dhn:
                disconnect_from_dhn = QAction(
                    '&Disconnect from DHN'
                )
                disconnect_from_dhn.triggered.connect(selected.toggle_dhn)
                menu.addAction(disconnect_from_dhn)
        menu.exec (self.dmmTree_future.viewport().mapToGlobal(point))

    def toggle_cooling_input(self, state):
        """
        Activate/Deactivate cooling input
        :return:
        """
        if state > 0:
            self.cooling.setEnabled(False)
            self.dcnSelector.setEnabled(True)
            self.connectDCN.setEnabled(True)
        else:
            self.cooling.setEnabled(True)
            self.dcnSelector.setEnabled(False)
            self.connectDCN.setEnabled(False)

    def toggle_heating_input(self, state):
        """
        Activate/Deactivate heating input
        :param state: state of the checkbox
        :return:
        """
        if state > 0:
            self.heating.setEnabled(False)
            self.dhw.setEnabled(False)
            self.dhnSelector.setEnabled(True)
            self.connectDHN.setEnabled(True)
        else:
            self.heating.setEnabled(True)
            self.dhw.setEnabled(True)
            self.dhnSelector.setEnabled(False)
            self.connectDHN.setEnabled(False)

    def toggle_dhw_input(self, state):
        """
        Activate/Deactivate the DHW input
        :param state: state of the checkbox
        :return:
        """
        if state > 0:
            self.dhw.setEnabled(False)
        else:
            self.dhw.setEnabled(True)

    def set_street_layer(self, layer):
        self.street_layer = layer
        # self.street_layer.selectionChanged.connect(self.add_streets_to_networks)

    def set_building_layer(self, layer):
        self.building_layer = layer
        # self.building_layer.selectionChanged.connect(self.add_buildings_to_networks)

    def upload_shp_DHNnetwork(self):
        space = "                                       "
        text, ok_pressed = QInputDialog.getText(self, "Create new network", "Type the DHN name:" + space, QLineEdit.Normal, "")
        if ok_pressed and text != '':
            n = Network(text)
            sh_fileDHN = self.layerPath_buildingNetwork_2.filePath()
            buildings = load_file_as_layer(sh_fileDHN, "buildings - " + text, "DHN: " + text + " - ID:" + n.get_ID(), min_val=None,
                                           max_val=None, mean_val=None, value_color=None, area=None)
            shp_file = self.layerPath_shpNetwork_2.filePath()
            streets = load_file_as_layer(shp_file, "streets - " + text, "DHN: " + text + " - ID:" + n.get_ID(), min_val=None,
                                         max_val=None, mean_val=None, value_color=None, area=None)
            n.buildings_layer = buildings
            n.streets_layer = streets
            self.futureDHN_network_list.append(n)
            self.refresh_DHN_network_future()

    def upload_shp_DCNnetwork(self):
        space = "                                       "
        text, ok_pressed = QInputDialog.getText(self, "Create new network", "Type the DCN name:" + space, QLineEdit.Normal, "")
        if ok_pressed and text != '':
            n = Network(text)
            shp_bulidingDCN = self.layerPath_buildingDCNNetwork.filePath()
            buildings = load_file_as_layer(shp_bulidingDCN, "buildings - " + text, "DCN: " + text + " - ID:" + n.get_ID(), min_val=None,
                                           max_val=None, mean_val=None, value_color=None, area=None)
            shpDCN_file = self.layerPath_shpDCNNetwork.filePath()
            streets = load_file_as_layer(shpDCN_file, "streets - " + text, "DCN: " + text + " - ID:" + n.get_ID(), min_val=None,
                                         max_val=None, mean_val=None, value_color=None, area=None)
            n.buildings_layer = buildings
            n.streets_layer = streets
            self.futureDCN_network_list.append(n)
            self.refresh_DCN_network_future()

    def add_network(self, n_type):
        space = "                                       "
        text, ok_pressed = QInputDialog.getText(self, "Create new network", "Type the {0} name:".format(n_type) + space, QLineEdit.Normal, "")
        if ok_pressed and text != '':
            flag = True
            while flag:
                text2, ok_pressed = QInputDialog.getText(self, "Additional information",
                                                        "Please enter the network efficiency \n(usually between 0.00 and 1.00):",
                                                        QLineEdit.Normal, "")
                try:
                    if ok_pressed:
                        efficiency = float(text2)
                        flag = False
                    else:
                        efficiency = 1.0
                        flag = False
                except ValueError:
                    flag = True
            n = Network(text, n_type)
            n.efficiency = efficiency
            n.scenario_type = "future"

            group_name = n.n_type + " (" + n.scenario_type + "): " + text + " - ID:" + n.get_ID()

            if n.n_type == "DHN":
                self.futureDHN_network_list.append(n)
                self.refresh_DHN_network()
            if n.n_type == "DCN":
                self.futureDCN_network_list.append(n)
                self.refresh_DCN_network()

            root = QgsProject.instance().layerTreeRoot()
            group = root.findGroup(group_name)
            if group is None:
                root.insertGroup(0, group_name)

    def add_DHN_network(self):
        self.add_network("DHN")

    def add_DCN_network(self):
        self.add_network("DCN")

    def remove_DHN_networks(self):
        network_to_be_removed = []
        for item in self.listWidget_future.selectedItems():
            network_to_be_removed.append(self.listWidget_future.row(item))
        network_to_be_removed.sort()
        for i in range(len(network_to_be_removed)-1, -1, -1):
            self.futureDHN_network_list[network_to_be_removed[i]].remove_group()
            del self.futureDHN_network_list[network_to_be_removed[i]]
        self.refresh_DHN_network()
        self.tree_item_manager.update_buildings_visualizzation()

    def remove_DCN_networks(self):
        network_to_be_removed = []
        for item in self.listNetworkDCN.selectedItems():
            network_to_be_removed.append(self.listNetworkDCN.row(item))
        network_to_be_removed.sort()
        for i in range(len(network_to_be_removed)-1, -1, -1):
            self.futureDCN_network_list[network_to_be_removed[i]].remove_group()
            del self.futureDCN_network_list[network_to_be_removed[i]]
        self.refresh_DCN_network()
        self.tree_item_manager.update_buildings_visualizzation()

    def refresh_DHN_network(self):
        self.listWidget_future.clear()
        self.listWidget_future.addItems(n.name for n in self.futureDHN_network_list)
        # self.insert_techNetwork()

    def refresh_DCN_network(self):
        self.listNetworkDCN.clear()
        self.listNetworkDCN.addItems([n.name for n in self.futureDCN_network_list])
        # self.insert_techNetwork()

    def add_buildings_to_DHN_networks(self):
        self.add_buildings_to_networks("DHN")
        return

    def add_buildings_to_DCN_networks(self):
        self.add_buildings_to_networks("DCN")
        return

    def add_buildings_to_networks(self, n_type):
        if n_type == "DHN":
            n_list = self.futureDHN_network_list
            widget = self.listWidget_future
        else:
            if n_type == "DCN":
                n_list = self.futureDCN_network_list
                widget = self.listNetworkDCN
            else:

                return
        if self.building_layer is None:
            return
        try:
            if not self.building_layer.isValid():
                return
        except:
            return
        for item in widget.selectedItems():
            network_index = widget.row(item)
            n_list[network_index].buildings_layer.startEditing()
            pr = n_list[network_index].buildings_layer.dataProvider()
            pr.addFeatures(get_only_new_features(self.building_layer,
                                                 n_list[network_index].buildings_layer,
                                                 'BuildingID'))
            n_list[network_index].buildings_layer.commitChanges()
        if n_type == "DCN":
            self.refresh_DCN_network_buildings()
        if n_type == "DHN":
            self.refresh_DHN_network_buildings()

    def remove_buildings_from_DHN_networks(self):
        if self.building_layer is None:
            return
        if not self.building_layer.isValid():
            return
        for item in self.listWidget_future.selectedItems():
            network_index = self.listWidget_future.row(item)
            self.futureDHN_network_list[network_index].buildings_layer.startEditing()
            for building in self.building_layer.selectedFeatures():
                # self.DHN_network_list[network_index].remove_building(building.attribute("BuildingID"))
                for f in self.futureDHN_network_list[network_index].buildings_layer.getFeatures():
                    if f.attribute("BuildingID") == building.attribute("BuildingID"):
                        self.futureDHN_network_list[network_index].buildings_layer.deleteFeature(f.id())
            self.futureDHN_network_list[network_index].buildings_layer.commitChanges()
        self.refresh_DHN_network_buildings()

    def remove_buildings_from_DCN_networks(self):
        if self.building_layer is None:
            return
        if not self.building_layer.isValid():
            return
        for item in self.listNetworkDCN.selectedItems():
            network_index = self.listNetworkDCN.row(item)
            self.futureDCN_network_list[network_index].buildings_layer.startEditing()
            for building in self.building_layer.selectedFeatures():
                # self.DCN_network_list[network_index].remove_building(building.attribute("BuildingID"))
                for f in self.futureDCN_network_list[network_index].buildings_layer.getFeatures():
                    if f.attribute("BuildingID") == building.attribute("BuildingID"):
                        self.futureDCN_network_list[network_index].buildings_layer.deleteFeature(f.id())
            self.futureDCN_network_list[network_index].buildings_layer.commitChanges()
        self.refresh_DCN_network_buildings()

    def add_streets(self, widget, n_type):
        for item in widget.selectedItems():
            network_index = widget.row(item)
            if n_type == "DHN":
                layer = self.futureDHN_network_list[network_index].streets_layer
                self.futureDHN_network_list[network_index].street_quality_status = False
            if n_type == "DCN":
                layer = self.futureDCN_network_list[network_index].streets_layer
                self.futureDCN_network_list[network_index].street_quality_status = False
            layer.startEditing()
            pr = layer.dataProvider()
            new_features = get_only_new_features(self.street_layer, layer, 'osmid')
            pr.addFeatures(new_features)
            layer.commitChanges()
            if n_type == "DHN":
                self.futureDHN_network_list[network_index].update_street_backup(new_features, "add")
            if n_type == "DCN":
                self.futureDCN_network_list[network_index].update_street_backup(new_features, "add")

    def add_streets_to_networks(self):
        if self.street_layer is None:
            return
        if not self.street_layer.isValid():
            return
        widget = self.listWidget_future
        self.add_streets(widget, "DHN")
        self.refresh_DHN_network_streets()

    def add_streets_to_DCN_networks(self):
        if self.street_layer is None:
            return
        if not self.street_layer.isValid():
            return
        widget = self.listNetworkDCN
        self.add_streets(widget, "DCN")
        self.refresh_DCN_network_streets()

    def remove_streets_from_DHN_networks(self):
        self.remove_streets_from_networks("DHN")
        self.refresh_DHN_network()

    def remove_streets_from_DCN_networks(self):
        self.remove_streets_from_networks("DCN")
        self.refresh_DCN_network()

    def remove_streets_from_networks(self, n_type):
        pipes_widget = None
        if n_type == "DHN":
            n_list = self.futureDHN_network_list
            pipes_widget = self.streetsListWidget_future
        if n_type == "DCN":
            n_list = self.futureDCN_network_list
            pipes_widget = self.streetsListDCN
        if pipes_widget is None:
            return
        for n in n_list:
            n.streets_layer.startEditing()
            print("Looking at:", n.streets_layer.name())
            for pipe in pipes_widget.selectedItems():
                row = pipe.text().split('|')
                try:
                    pipe_id = int(row[0][9:-1])
                except:
                    continue
                try:
                    network_id = str(pipe.data(Qt.UserRole))
                except:
                    continue
                print("n.get_ID() vs network_id", n.get_ID(), network_id)
                if n.get_ID() == network_id:
                    expr = QgsExpression("\"ID\"=" + str(pipe_id))
                    ids = [ft.id() for ft in n.streets_layer.getFeatures(QgsFeatureRequest(expr))]
                    n.streets_layer.deleteFeature(ids[0])
                    print(True)
                    print("ids:", ids)
                    for e in n.graph.edges(data=True):
                        if e[2]['feature_ID'] == pipe_id:
                            n.graph.remove_edge(e[0], e[1])
                else:
                    print(False)
            n.streets_layer.commitChanges()

    def refresh_DHN_network_buildings(self):
        return
        self.buildingListWidget_future.clear()
        buildings_to_display = []
        #if self.building_layer is not None:
        #    self.make_feature_transparent(self.building_layer)
        for item in self.listWidget_future.selectedItems():
            network_index = self.listWidget_future.row(item)
            for building in self.futureDHN_network_list[network_index].get_building_list():
                buildings_to_display.append(str(building) + " | " + self.futureDHN_network_list[network_index].name)
        self.buildingListWidget_future.addItems(buildings_to_display)

    def refresh_DHN_network_streets(self):
        return
        self.streetsListWidget_future.clear()
        check = True
        loop = False
        for item in self.listWidget_future.selectedItems():
            loop = True
            network_index = self.listWidget_future.row(item)
            for street in self.futureDHN_network_list[network_index].get_street_list():
                q = QListWidgetItem()
                q.setData(Qt.UserRole, QVariant(self.futureDHN_network_list[network_index].get_ID()))
                q.setText(str(street))
                self.streetsListWidget_future.addItem(q)
            check = check and self.futureDHN_network_list[network_index].street_quality_status
        if check and loop:
            self.setPipeDiameter.setEnabled(True)
        else:
            self.setPipeDiameter.setEnabled(False)

    def refresh_DCN_network_buildings(self):
        return
        self.buildingListDCN.clear()
        buildings_to_display = []
        for item in self.listNetworkDCN.selectedItems():
            network_index = self.listNetworkDCN.row(item)
            for building in self.futureDCN_network_list[network_index].get_building_list():
                buildings_to_display.append(str(building) + " - " + self.futureDCN_network_list[network_index].get_ID())
        self.buildingListDCN.addItems(buildings_to_display)

    def refresh_DCN_network_streets(self):
        return
        self.streetsListDCN.clear()
        check = True
        loop = False
        for item in self.listNetworkDCN.selectedItems():
            network_index = self.listNetworkDCN.row(item)
            for street in self.futureDCN_network_list[network_index].get_street_list():
                q = QListWidgetItem()
                q.setData(Qt.UserRole, QVariant(self.futureDCN_network_list[network_index].get_ID()))
                q.setText(str(street))
                self.streetsListWidget_future.addItem(q)
            check = check and self.futureDCN_network_list[network_index].street_quality_status
        if check and loop:
            self.setPipeDiameter_DCN.setEnabled(True)
        else:
            self.setPipeDiameter_DCN.setEnabled(False)

    def district_solution_checked(self, state):
        if not state:
            self.futureDCN.hide()
            self.futureDHN.hide()
            self.label_22.hide()
        else:
            self.futureDCN.show()
            self.futureDHN.show()
            self.label_22.show()

    def DHN_checked(self, state_DHN, state_DCN):
        if state_DHN or state_DCN:
            self.phases.setTabEnabled(1, True)
        else:
            self.phases.setTabEnabled(1, False)
        if not state_DHN:
            self.tabWidget.setTabEnabled(1, False)
            self.tabWidget.setTabEnabled(3, False)
        else:
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setTabEnabled(3, True)


    def DCN_checked(self, state_DHN, state_DCN):
        if state_DHN or state_DCN:
            self.phases.setTabEnabled(1, True)
        else:
            self.phases.setTabEnabled(1, False)
        if not state_DCN:
            self.tabWidget.setTabEnabled(2, False)
            self.tabWidget.setTabEnabled(3, False)
        else:
            self.tabWidget.setTabEnabled(2, True)
            self.tabWidget.setTabEnabled(3, True)

    def Building_checked(self,state):
        if not state:
            self.phases.setTabEnabled(2, False)
        else:
            self.phases.setTabEnabled(2, True)

    def insert_technology(self):
        old_data = "old_tech"
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText("Is this a new technology?")
        msgBox.setInformativeText("")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.Yes)
        msgBox.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        ret = msgBox.exec()
        if ret == QMessageBox.Yes:
            old_data = "new_tech"
        self.apply_technology(old_data)

    def apply_technology(self, old_data: str):
            technology = self.networkTechnology.currentText()
            source = self.future_sourceNet
            area = self.networkarea.value()
            temperature = self.networkTemp.value()
            efficiency = self.networkEta.value()
            first_order = self.network1coeff.value()
            second_order = self.network2coeff.value()
            # capacity = self.networkCapacity.value()
            p_max = self.networkP_max.value()
            p_min = self.networkP_min.value()
            powerToRatio = self.networkcb_CHP.value()
            tech_min = self.networkTechMin.value()
            ramp_up = self.networkRampUpDown.value()
            ramp_down = self.networkRampUpDown.value()
            variable = self.networkVariableCost.value()
            fix = self.networkFixedCost.value()
            fuel = self.networkFuelCost.value()
            tes_size = self.networkTes_size.value()
            soc_min = self.networkSocMin.value()
            tes_startEnd = self.networkTesStartEnd.value()
            tes_discharge = self.networkTes_discharge.value()
            COP_absorption = self.networkCop_absorption.value()
            el_sale = self.network_el_sale.value()
            tes_loss = self.networkTES_loss.value()

            child = [str(" "),
                     str(technology),
                     str(source),
                     str(area),
                     str(temperature),
                     str(efficiency),
                     str(first_order),
                     str(second_order),
                     str(p_max),
                     str(p_min),
                     str(powerToRatio),
                     str(tech_min),
                     str(ramp_up),
                     str(fix),
                     str(variable),
                     str(fuel),
                     str(tes_size),
                     str(soc_min),
                     str(tes_startEnd),
                     str(tes_discharge),
                     str(COP_absorption),
                     str(el_sale),
                     str(tes_loss)]
            new_child = QTreeWidgetItem(child)

            new_child.setData(2, Qt.UserRole, old_data)

            parent = self.futureDmmTreeNetwork.currentItem()
            if parent is None:
                return
            if parent.parent() is not None:
                return
            if parent is None:
                self.futureDmmTreeNetwork.invisibleRootItem()
            else:
                parent.addChild(new_child)

            if technology in self.technology_temp_70:
                if temperature < 70:
                    self.vis_MsgError()

    def insert_techNetwork(self):
        return
        self.futureDmmTreeNetwork.clear()
        for lista in [self.futureDHN_network_list, self.futureDCN_network_list]:
            for i in lista:
                supplies = i.get_supplies_names()
                if supplies is None:
                    continue
                if len(supplies) < 1:
                    continue
                for supply in supplies:
                    tree = QTreeWidgetItem()
                    tree.setText(0, supply[0])
                    tree.setData(0, Qt.UserRole, QVariant(str(i.get_ID())))
                    tree.setData(8, Qt.UserRole, QVariant(str(supply[1])))
                    self.futureDmmTreeNetwork.insertTopLevelItem(0, tree)

    def future_locate_sources_DHN(self):
        for item in self.listWidget_future.selectedItems():
            network_index = self.listWidget_future.row(item)

            # If supply_layer is none, create it
            if self.futureDHN_network_list[network_index].supply_layer is None:
                # set generic crs here
                generate= self.futureDHN_network_list[network_index].name
                self.futureDHN_network_list[network_index].supply_layer = QgsVectorLayer("Point?crs=epsg:4326",
                                                                                   "generation_point" + " - " + generate,
                                                                                   "memory")
                # Show the layer
                group_name = "DHN: " + self.futureDHN_network_list[network_index].name + " - ID:" + self.futureDHN_network_list[network_index].get_ID()
                add_layer_to_group(self.futureDHN_network_list[network_index].supply_layer, group_name)
                # Add fields :
                self.futureDHN_network_list[network_index].supply_layer.startEditing()
                self.futureDHN_network_list[network_index].supply_layer.dataProvider().addAttributes(
                    [QgsField("name", QVariant.String), QgsField("capacity_MW", QVariant.Double)])
                self.futureDHN_network_list[network_index].supply_layer.commitChanges()
            # Set update table when feature is added:
            self.futureDHN_network_list[network_index].supply_layer.featureAdded.connect(
                self.futureDHN_network_list[network_index].validate_sources)
            # Set active layer
            self.iface.setActiveLayer(self.futureDHN_network_list[network_index].supply_layer)
            # Start editing the layer
            if not self.futureDHN_network_list[network_index].supply_layer.isEditable():
                self.futureDHN_network_list[network_index].supply_layer.startEditing()
            # Start new point creation tool
            self.iface.actionAddFeature().trigger()
            # Enable validate and discard button
            # self.dock.clear_sources_button.setEnabled(True)
            # TODO : what if layer already exists ?

            for feature in self.futureDHN_network_list[network_index].supply_layer.getFeatures():
                geom = feature.geometry()
                print(self.futureDHN_network_list[network_index].supply_layer.name(), ": coordinates -", geom.asPoint().x(),
                      geom.asPoint().x())

    def future_locate_sources_DCN(self):
        for item in self.listNetworkDCN.selectedItems():
            network_index = self.listNetworkDCN.row(item)

            # If supply_layer is none, create it
            if self.futureDCN_network_list[network_index].supply_layer is None:
                generate = self.futureDHN_network_list[network_index].name
                # set generic crs here
                self.futureDCN_network_list[network_index].supply_layer = QgsVectorLayer("Point?crs=epsg:4326",
                                                                                   "all_supply_%d" + generate,
                                                                                   "memory")
                # Show the layer
                group_name = "DCN: " + self.futureDCN_network_list[network_index].name + " - ID:" + self.futureDCN_network_list[network_index].get_ID()
                add_layer_to_group(self.futureDCN_network_list[network_index].supply_layer, group_name)
                # Add fields :
                self.futureDCN_network_list[network_index].supply_layer.startEditing()
                self.futureDCN_network_list[network_index].supply_layer.dataProvider().addAttributes(
                    [QgsField("name", QVariant.String), QgsField("capacity_MW", QVariant.Double)])
                self.futureDCN_network_list[network_index].supply_layer.commitChanges()
            # Set update table when feature is added:
            self.futureDCN_network_list[network_index].supply_layer.featureAdded.connect(
                self.futureDCN_network_list[network_index].validate_sources)
            # Set active layer
            self.iface.setActiveLayer(self.futureDCN_network_list[network_index].supply_layer)
            # Start editing the layer
            if not self.futureDCN_network_list[network_index].supply_layer.isEditable():
                self.futureDCN_network_list[network_index].supply_layer.startEditing()
            # Start new point creation tool
            self.iface.actionAddFeature().trigger()
            # Enable validate and discard button
            # self.dock.clear_sources_button.setEnabled(True)
            # TODO : what if layer already exists ?

            for feature in self.futureDCN_network_list[network_index].supply_layer.getFeatures():
                geom = feature.geometry()
                print(self.futureDCN_network_list[network_index].supply_layer.name(), ": coordinates -", geom.asPoint().x(),
                      geom.asPoint().x())

    def connect_building_toDHN(self):
        for i in self.futureDHN_network_list:
            i.connect_building_to_streets("DHN")

    def connect_building_toDCN(self):
        for i in self.futureDCN_network_list:
            i.connect_building_to_streets("DCN")

    def futureDCN_pipes_selected(self):
        self.pipes_selected(self.streetsListDCN_future, "DCN")

    def futureDHN_pipes_selected(self):
        self.pipes_selected(self.streetsListWidget_future, "DHN")

    def future_insert_point(self):
        self.insert_techNetwork()

    def receive_networks(self, networks, building_layer, street_layer, technologies_transfer, source_transfer):
        root = QgsProject.instance().layerTreeRoot()
        for n in self.futureDHN_network_list:
            root.removeChildNode(root.findGroup(n.get_group_name()))
            try:
                print("Step_4.py, receive_networks(). Deleting folder",
                      os.path.realpath(os.path.join(n.save_file_path, "../")))
                shutil.rmtree(os.path.realpath(os.path.join(n.save_file_path, "../")),
                              ignore_errors=True)
            except Exception as e:
                print("Step_4.py, receive_networks(). Error removing folder")
                traceback.print_exc()
        for n in self.futureDCN_network_list:
            root.removeChildNode(root.findGroup(n.get_group_name()))
            print("Step_4.py, receive_networks(). Deleting folder",
                  os.path.realpath(os.path.join(n.save_file_path, "../")))
            try:
                shutil.rmtree(os.path.realpath(os.path.join(n.save_file_path, "../")),
                              ignore_errors=True)
            except Exception as e:
                print("Step_4.py, receive_networks(). Error removing",
                      os.path.realpath(os.path.join(n.save_file_path, "../")),
                      e)

        self.futureDHN_network_list = []
        self.futureDCN_network_list = []
        self.network_efficiency.DCN_network_list = self.futureDCN_network_list
        self.network_efficiency.DHN_network_list = self.futureDHN_network_list

        for dhn in networks[0]:
            new_dhn = Network(orig=dhn)
            self.futureDHN_network_list.append(new_dhn)
            print("Step4.py, receive_networks(). Old network path:", dhn.get_save_file_path())
            if dhn.get_save_file_path() is not None:
                new_dhn.save_file_path = os.path.realpath(os.path.join(dhn.get_save_file_path(), "../../../../../",
                                                                       "Future", "Networks", new_dhn.n_type,
                                                                       new_dhn.get_ID(), new_dhn.name + ".zip"))
                print("Step4.py, receive_networks(). New network path:", new_dhn.get_save_file_path())
                new_dir_path, _ = os.path.split(new_dhn.get_save_file_path())
                old_dir_path, _ = os.path.split(dhn.get_save_file_path())
                print("Step4.receive_networks():", new_dir_path, old_dir_path)
                shutil.copytree(old_dir_path, new_dir_path)

        for dcn in networks[1]:
            new_dcn = Network(orig=dcn)
            self.futureDHN_network_list.append(new_dcn)
            print("Step4.py, receive_networks(). Old network path:", dcn.get_save_file_path())
            if dcn.get_save_file_path() is not None:
                new_dcn.save_file_path = os.path.realpath(os.path.join(dcn.get_save_file_path(), "../../../../../",
                                                                       "Future", "Networks", new_dcn.n_type,
                                                                       new_dcn.get_ID(), new_dcn.name + ".zip"))
                print("Step4.py, receive_networks(). Old network path:", new_dcn.get_save_file_path())
                new_dir_path, _ = os.path.split(new_dcn.get_save_file_path())
                old_dir_path, _ = os.path.split(dcn.get_save_file_path())
                print("Step4.receive_networks():", new_dir_path, old_dir_path)
                shutil.copytree(old_dir_path, new_dir_path)

        # self.futureDHN_network_list = [Network(orig=dhn) for dhn in networks[0]]
        # self.futureDCN_network_list = [Network(orig=dcn) for dcn in networks[1]]
        self.port_tech_from_baseline(technologies_transfer, building_layer, source_transfer)

        self.set_building_layer(building_layer)
        self.set_street_layer(street_layer)

        for n in self.futureDHN_network_list:
            n.scenario_type = "future"
            add_group(n.get_group_name())
            # group_name = "DHN" + " (" + n.scenario_type + "): " + n.name + " - ID:" + n.get_ID()
            # if n.buildings_layer is not None:
            #     add_layer_to_group(n.buildings_layer, group_name)
            # if n.streets_layer is not None:
            #     add_layer_to_group(n.streets_layer, group_name)
            # if n.supply_layer is not None:
            #     add_layer_to_group(n.supply_layer, group_name)
            #add_layer_to_group(n.supply_layer, n.get_group_name())
            AutoLoadNetwork(self.work_folder).load(n, self.data_transfer)

        for n in self.futureDCN_network_list:
            n.scenario_type = "future"
            add_group(n.get_group_name())
            # group_name = "DCN" + " (" + n.scenario_type + "): " + n.name + " - ID:" + n.get_ID()
            # if n.buildings_layer is not None:
            #     add_layer_to_group(n.buildings_layer, group_name)
            # if n.streets_layer is not None:
            #     add_layer_to_group(n.streets_layer, group_name)
            # if n.supply_layer is not None:
            #     add_layer_to_group(n.supply_layer, group_name)
            #add_layer_to_group(n.supply_layer, n.get_group_name())
            AutoLoadNetwork(self.work_folder).load(n, self.data_transfer)

        self.refresh_DCN_network()
        self.refresh_DHN_network()

    def port_tech_from_baseline(self, technologies_transfer, building_layer, source_transfer):
        technologies_transfer.buildings_tree_widget_transfer(self.dmmTree_future, building_layer, self.future_scenario)
        tmp = technologies_transfer.widget_input
        technologies_transfer.widget_input = technologies_transfer.n_tree
        technologies_transfer.tree_widget_transfer(self.futureDmmTreeNetwork)
        technologies_transfer.update_network_id_user_role_data([self.futureDHN_network_list,
                                                                self.futureDCN_network_list])
        technologies_transfer.widget_input = tmp
        source_transfer.transfer_sources_table(self.suppliesTable_future)

    def recive_treeWidget_baseline(self, dmmTree):
        print(dmmTree)

    def receive_future_scenario(self, layer):
        self.future_scenario = layer

    def receive_baseline_scenario(self, layer):
        self.baseline_scenario = layer

#    def optimize_network(self, network, objective=None):
#        valid = False
#        space = "                                       "
#        tot_supply = 0
#        tot_demand = 0
#        for feature in network.supply_layer.getFeatures():
#            tot_supply = tot_supply + float(feature.attribute("capacity_MW"))
#
#        if network.n_type == "DHN":
#            attr_list = network.H_dem_attributes
#        if network.n_type == "DCN":
#            attr_list = network.C_dem_attributes
#        for feature in network.buildings_layer.getFeatures():
#            for attr in attr_list:
#                tot_demand = tot_demand + float(feature.attribute(attr))/1000
#
#        max_percent = (tot_supply/tot_demand)*100
#        if max_percent > 100:
#            max_percent = 100
#        advice = "Total production capacity: " + str(round(tot_supply, 2)) + " MW"
#        advice = advice + "\nTotal demand: " + str(round(tot_demand, 2)) + " MW"
#        advice = advice + "\nMax coverage objective: " + str(round(max_percent, 2)) + "%. \nNote: input cannot exceed max coverage.\n\n"
#
#        while not valid:
#            text, ok_pressed = QInputDialog.getText(self, "Coverage objective",
#                                                    advice + "Please enter the coverage objective [%]" + space,
#                                                    QLineEdit.Normal, "")
#            if not ok_pressed:
#                valid = True
#            try:
#                objective = float(text)
#                if objective < 0 or objective > max_percent:
#                    continue
#                valid = True
#            except:
#                pass
#        if not ok_pressed:
#            return
#
#        self.opt = ADNetworkOptimizer(optimization_graph=network.graph, network_objective=tot_demand*objective/100)
#        network.print_graph(do_it=True)
#        try:
#            if not os.environ[
#                       "JULIA_HOME"] == "C:\\Program Files\\QGIS 3.2\\apps\\qgis\\python\\plugins\\dhcoptimizerplanheat\\deps\\Julia-0.6.2/bin":
#                print("Need to set environ")
#        except:
#            print("Except: Need to set environ")
#            self.opt.set_julia_environment_variables()
#            ADNetworkOptimizer.set_julia_working_directory()
#        self.set_up_logger()
#        # try:
#        flows, obj_val, edges_to_keep = self.opt.optimize()
#
#        self.build_optimized_layers(network, flows, obj_val, edges_to_keep)

    def set_up_logger(self):
        class Printer:
            def write(self, x):
                print(x)

        self.opt.logger = logging.getLogger()
        self.opt.logger.setLevel(logging.INFO)

        output_stream = sys.stdout if sys.stdout is not None else Printer()
        stream_handler = logging.StreamHandler(output_stream)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        self.opt.logger.addHandler(stream_handler)

    def DHN_optimization(self):
        # for n in self.futureDHN_network_list:
        #     self.optimize_network(n)
        self.router_optimizer(self.listWidget_future)

    def DCN_optimization(self):
        # for n in self.futureDCN_network_list:
        #     self.optimize_network(n)
        self.router_optimizer(self.listNetworkDCN)

    def router_optimizer(self, widget):
        if len(widget.selectedItems()) > 1:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("Too many networks selected")
            msgBox.setInformativeText("Please, select a single network before running the Router Optimizer.")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            ret = msgBox.exec()
            return
        if len(widget.selectedItems()) < 1:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setText("No network selected.")
            msgBox.setInformativeText("Please, select a network before running the Router Optimizer.")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            ret = msgBox.exec()
            return
        network_index = widget.row(widget.selectedItems()[0])
        if widget == self.listWidget_future:
            network = self.futureDHN_network_list[network_index]
        else:
            network = self.futureDCN_network_list[network_index]
        root = QgsProject.instance().layerTreeRoot()
        network_node = root.findGroup(network.get_group_name())
        if network_node is None:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("Critical error.")
            msgBox.setInformativeText("Network node not found. Expecting group " + network.get_group_name())
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            ret = msgBox.exec()
            return
        else:
            result_node = network_node.findGroup("Router Optimizer RESULTS")
            if result_node is not None:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("Router Optimizer already executed.")
                msgBox.setInformativeText(
                    "To execute another instance of the Router Optimizer for network " + network.name + " old result data must be discarded. If you press Ok, old data for this network will be override.")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Cancel)
                ret = msgBox.exec()
                if ret == QMessageBox.Ok:
                    network_node.removeChildNode(result_node)
                else:
                    return
        if network.scenario_type == "baseline":
            scenario_type = "Baseline"
        else:
            scenario_type = "Future"

        if self.work_folder is not None:
            folder = os.path.join(self.work_folder, scenario_type, "Networks", network.n_type, network.get_ID())
        else:
            folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "save_utility", "DefaultSaveFolder",
                                  scenario_type, "Networks", network.n_type, network.get_ID())
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            self.data_transfer.automatic_upload_network = False
        elif os.path.isfile(os.path.join(folder, network.name + ".zip")) and scenario_type == "Future":
            self.data_transfer.automatic_upload_network = True
        else:
            self.data_transfer.automatic_upload_network = False
        network.save_file_path = os.path.join(folder, network.name + ".zip")

        self.data_transfer.network = network
        self.data_transfer.buildings = self.future_scenario
        self.data_transfer.baseline_scenario = self.baseline_scenario
        self.data_transfer.study_id += 1
        self.data_transfer.step1_mode = False
        self.data_transfer.print_state()
        dhcoptimizerplanheat = DHCOptimizerPlanheat(self.iface,
                                                    working_directory=folder, 
                                                    data_transfer=self.data_transfer)
        dhcoptimizerplanheat.dock.closed.connect(lambda: self.dhcoptimizerplanheat_closed(dhcoptimizerplanheat))
        dhcoptimizerplanheat.manual_dock.closed.connect(lambda: self.dhcoptimizerplanheat_closed(dhcoptimizerplanheat))
        dhcoptimizerplanheat.dialog_menu.closed.connect(lambda: self.dhcoptimizerplanheat_closed(dhcoptimizerplanheat,
                                                                                                 dialog_dock=self.dialog_dock))

        if widget == self.listWidget_future:
            # print("Heating mode")
            dhcoptimizerplanheat.dock.radioButton_Heating.setVisible(False)
            dhcoptimizerplanheat.dock.radioButton_Cooling.setVisible(False)
            dhcoptimizerplanheat.dock.radioButton_Heating.setChecked(True)
            dhcoptimizerplanheat.dock.radioButton_Cooling.setChecked(False)
        else:
            # print("Cooling mode")
            dhcoptimizerplanheat.dock.radioButton_Heating.setVisible(False)
            dhcoptimizerplanheat.dock.radioButton_Cooling.setVisible(False)
            dhcoptimizerplanheat.dock.radioButton_Heating.setChecked(False)
            dhcoptimizerplanheat.dock.radioButton_Cooling.setChecked(True)

        if self.dialog_dock:
            self.hide()
        self.dialog_dock = True
        self.dhcoptimizerplanheat = dhcoptimizerplanheat
        dhcoptimizerplanheat.run()

    def dhcoptimizerplanheat_closed(self, dhcoptimizerplanheat, dialog_dock=False):
        if dialog_dock:
            self.dialog_dock = False
        else:
            if self.data_transfer.dock_type == "manual":
                dhcoptimizerplanheat.manual_dock.save_existing_network_button.clicked.emit()
            if self.data_transfer.dock_type == "automatic":
                dhcoptimizerplanheat.dock.save_existing_network_button.clicked.emit()
            root = QgsProject.instance().layerTreeRoot()
            network_group_name = dhcoptimizerplanheat.data_transfer.network.get_group_name()
            network_node = root.findGroup(network_group_name)
            if network_node is None:
                print("Step4_dockwidget.py, dhcoptimizerplanheat_closed(). ERROR: network node not found")
            old = dhcoptimizerplanheat.data_transfer.tree_group
            try:
                new = old.clone()
            except RuntimeError:
                root = QgsProject.instance().layerTreeRoot()
                old = root.findGroup(dhcoptimizerplanheat.data_transfer.tree_group_name)
                new = old.clone()
            network_node.addChildNode(new)
            network_node.removeChildNode(old)
            new.setName("Router Optimizer RESULTS")

            self.network_optimizer_post_processing(dhcoptimizerplanheat.data_transfer)
            self.show()

    def network_optimizer_post_processing(self, data_transfer):
        data_transfer.network.optimized = True
        self.insert_techNetwork()
        self.update_network_after_router_optimizer(data_transfer)
        self.tree_item_manager.update_buildings_visualizzation()

    def update_network_after_router_optimizer(self, data_transfer: DataTransfer):
        log = MyLog(None, file_name="update_future_tree_network_log")
        new_items = []
        log.log("data_transfer.network.get_supplies_names()", data_transfer.network.get_supplies_names())
        for gen_point in data_transfer.network.get_supplies_names():
            log.log("iterating over", gen_point)
            for i in range(self.futureDmmTreeNetwork.topLevelItemCount()):
                network_id = self.futureDmmTreeNetwork.topLevelItem(i).data(0, Qt.UserRole)
                log.log("checking it against", self.futureDmmTreeNetwork.topLevelItem(i).text(0), network_id)
                if not network_id == data_transfer.network.get_ID():
                    log.log("tree item rejected")
                    continue
                log.log("tree item approved!")
                log.log("no I'll compare check:", self.futureDmmTreeNetwork.topLevelItem(i).text(0),
                        gen_point[0] + " - " + data_transfer.network.name)
                if self.futureDmmTreeNetwork.topLevelItem(i).text(0) == gen_point[0] + " - " + data_transfer.network.name:
                    log.log("comparison is TRUE")
                    self.redistribuite_gen_point_capacity(log, self.futureDmmTreeNetwork.topLevelItem(i), gen_point[1])
                    break
                log.log("comparison is FALSE")
            else:  # if I don't find the generation point in the tree widget
                log.log("I did not found an item for that generation point. I'll reate a new one:",
                        data_transfer.network.name + " - " + gen_point[0], data_transfer.network.get_ID())
                new_item = QTreeWidgetItem()
                new_item.setText(0, gen_point[0] + " - " + data_transfer.network.name)
                new_item.setData(0, Qt.UserRole, QVariant(data_transfer.network.get_ID()))
                new_item.setData(8, Qt.UserRole, QVariant(str(gen_point[1])))
                new_items.append(new_item)
        log.log("adding new top level items", len(new_items))
        for new_item in new_items:
            self.futureDmmTreeNetwork.insertTopLevelItem(0, new_item)

    def redistribuite_gen_point_capacity(self, log, item: QTreeWidgetItem, value: float, column=8):
        log.log("redistribuite_gen_point_capacity() new_value:", value)
        item.setData(8, Qt.UserRole, QVariant(str(value)))
        capacity = 0.0
        for i in range(item.childCount()):
            tech = item.child(i)
            try:
                capacity += float(tech.text(column))
                log.log("redistribuite_gen_point_capacity(): new_capacity, contrinution:", capacity,
                        float(tech.text(column)))
            except Exception:
                pass
        if capacity == 0.0:
            log.log("capacity is 0! return")
            return
        for i in range(item.childCount()):
            tech = item.child(i)
            try:
                log.log("redistribuite_gen_point_capacity(): ", tech.text(column), value/capacity)
                formatted_new_capacity = "{:.2f}".format(float(tech.text(column))*(value/capacity))
                tech.setText(column, formatted_new_capacity)
            except Exception:
                pass

    def get_data_transfer(self, _, data_transfer):
        self.data_transfer = data_transfer

    def insert_PeakDemandCooling_future(self):
        self.future_dialog.show()
        self.future_dialog.attribute_column_name = "MaxCoolDem"

    def future_val_demand(self, peak, peak_range, attribute_column_name):
        demand = []
        ids = []
        val_inf = peak - (peak_range / 2)
        val_sup = peak + (peak_range / 2)

        for f in self.building_layer.getFeatures():
            a = f.attribute(attribute_column_name)
            demand.append(a)

            if a >= val_inf and a <= val_sup:
                ids.append(f.id())
        self.building_layer.modifySelection(ids, [])

    def insert_PeakDemandDhw_future(self):
        self.future_dialog.show()
        self.future_dialog.attribute_column_name = "MaxDHWDem"
    def insert_PeakDemandHeating_future(self):
        self.future_dialog.show()
        self.future_dialog.attribute_column_name = "MaxHeatDem"



    def future_recived_sources_selected(self):

        self.futureList_sources_network = []

        for i in range(self.future_dialog_source.model.rowCount()):
            item = self.future_dialog_source.model.item(i)
            self.futureList_sources_network.append(item.text())

        self.future_dialog_source.hide()

    def build_optimized_layers(self, network, flows, obj_val, edges_to_keep):
        buildings_list = []
        streets_dict = {}
        for node in network.graph.nodes(data=True):
            try:
                node_type = node[1]['nodetype']
            except KeyError:
                print("Step4, build_optimized_layers: KeyError. nodetype is not a key for node", node)
                continue
            if node_type == "building":
                for edge in edges_to_keep:
                    if node[0] in edge:
                        flow = flows[edge]
                        if not flow == 0.0:
                            break
                else:
                    continue
                try:
                    node_building_id = node[1]['building_id']
                except KeyError:
                    print("Step4, build_optimized_layers: KeyError. building_id is not a key for node", node)
                    continue
                if network.buildings_layer is None:
                    print("Step4, build_optimized_layers: network.buildings_layer is None")
                    continue
                for feature in network.buildings_layer.getFeatures():
                    if feature.attribute("BuildingID") == node_building_id:
                        if node_building_id not in [building.attribute("BuildingID") for building in buildings_list]:
                            buildings_list.append(feature)
        for edge in edges_to_keep:
            edge_data = network.graph.get_edge_data(edge[0], edge[1], edge[2])

            try:
                street_id = edge_data["feature_ID"]
            except KeyError:
                print("Step4, build_optimized_layers: KeyError. ID is not a key for edge", edge_data)
                continue
            if network.streets_layer is None:
                print("Step4, build_optimized_layers: network.streets_layer is None")
                continue
            for feature in network.streets_layer.getFeatures():

                if feature.attribute("ID") == street_id:

                    if street_id not in [streets_dict[key][0].attribute("ID") for key in streets_dict.keys()]:

                        for e, flow in flows.items():

                            if e == edge:
                                streets_dict[street_id] = [feature, flow]

                                break
                        else:
                            continue
                        break
        if network.optimized_buildings_layer is not None:
            QgsProject.instance().removeMapLayer(network.optimized_buildings_layer.id())
            network.optimized_buildings_layer = None
        if network.optimized_streets_layer is not None:
            QgsProject.instance().removeMapLayer(network.optimized_streets_layer.id())
            network.optimized_streets_layer = None
        network.optimized_buildings_layer = QgsVectorLayer(network.buildings_layer.source().split("&")[0],
                                                           "Optimized buildings layer" + " - " + network.name,
                                                           network.buildings_layer.providerType())
        network.optimized_streets_layer = QgsVectorLayer(network.streets_layer.source().split("&")[0],
                                                         "Optimized streets layer" + " - " + network.name,
                                                         network.streets_layer.providerType())
        network.optimized_buildings_layer.startEditing()
        network.optimized_buildings_layer.dataProvider().addAttributes([f for f in network.buildings_layer.fields()])
        network.optimized_buildings_layer.updateFields()
        network.optimized_buildings_layer.dataProvider().addFeatures(buildings_list)
        network.optimized_buildings_layer.commitChanges()

        network.optimized_streets_layer.startEditing()
        network.optimized_streets_layer.dataProvider().addAttributes([f for f in network.streets_layer.fields()])
        network.optimized_streets_layer.updateFields()
        network.optimized_streets_layer.dataProvider().addFeatures([streets_dict[key][0] for key in streets_dict.keys()])

        network.optimized_streets_layer.commitChanges()
        network.optimized_streets_layer.startEditing()
        network.optimized_streets_layer.dataProvider().addAttributes([QgsField("flow",  QVariant.Double, "double", 10, 3)])
        network.optimized_streets_layer.updateFields()
        network.optimized_streets_layer.commitChanges()

        for feature in network.optimized_streets_layer.getFeatures():
            try:
                flow = streets_dict[feature.attribute("ID")][1]
            except:
                print("Step4, build_optimized_layers: streets_dict, feature.id()", streets_dict, feature.id())
                continue
            network.optimized_streets_layer.startEditing()
            feature['flow'] = flow
            network.optimized_streets_layer.updateFeature(feature)
            network.optimized_streets_layer.commitChanges()
        group_name = network.n_type + " (" + network.scenario_type + "): " + network.name + " - ID:" + network.get_ID()
        add_layer_to_group(network.optimized_streets_layer, group_name)
        r = QgsGraduatedSymbolRenderer("flow")
        r.setGraduatedMethod(QgsGraduatedSymbolRenderer.GraduatedSize)
        r.updateClasses(network.optimized_streets_layer, QgsGraduatedSymbolRenderer.EqualInterval, 10)
        r.setSymbolSizes(0.26, 1.0)
        s = QgsLineSymbol().createSimple({"color_border": "255, 30, 0"})
        s.setColor(QColor.fromRgb(255, 30, 0))
        r.updateSymbols(s)
        network.optimized_streets_layer.setRenderer(r)
        group_name = network.n_type + " (" + network.scenario_type + "): " + network.name + " - ID:" + network.get_ID()
        add_layer_to_group(network.optimized_buildings_layer, group_name)
        return

    def futureActive_input_cooling(self, p):
        self.disable_all_cooling()
        techn = str(self.coolingTechnology.currentText())
        if techn == self.future_simulator.technology_for_cooling[0] or techn == self.future_simulator.technology_for_cooling[1]:
            if techn == self.future_simulator.technology_for_cooling[0]:
                self.future_sourceCool = self.future_simulator.sources_for_technology[0]
            if techn == self.future_simulator.technology_for_cooling[1]:
                self.future_sourceCool = self.future_simulator.sources_for_technology[8]
            self.coolingTemp.setEnabled(True)
            self.coolingTemp.setEnabled(True)
            self.P_max_cooling.setEnabled(True)
            self.coolingTechMin.setEnabled(True)
            self.coolingRampUpDown.setEnabled(True)
            self.coolingVariableCost.setEnabled(True)
            self.coolingFixedCost.setEnabled(True)
            self.coolingFuelCost.setEnabled(True)

        if techn == self.future_simulator.technology_for_cooling[2] or techn == self.future_simulator.technology_for_cooling[3]:
            if techn == self.future_simulator.technology_for_cooling[2]:
                self.future_sourceCool = self.future_simulator.sources_for_technology[9]
            if techn == self.future_simulator.technology_for_cooling[3]:
                self.future_sourceCool = self.future_simulator.sources_for_technology[8]
            self.coolingTechMin.setEnabled(True)
            self.coolingRampUpDown.setEnabled(True)
            self.coolingVariableCost.setEnabled(True)
            self.coolingFixedCost.setEnabled(True)
            self.Cop_absorption_cooling.setEnabled(True)
            self.P_max_cooling.setEnabled(True)
            self.coolingFuelCost.setEnabled(True)

    def futureActive_source_dialog(self, gf):
        self.disable_all_heating_input()
        t = str(self.heatingTechnology.currentText())

        key_list = self.future_simulator.individual_H_C_dict_var.keys()

        for key in key_list:
            z = self.future_simulator.individual_H_C_dict_var[key]
            # first category HOB
            if t in z:
                if key == list(key_list)[0]:  # heat_only_boiler
                    self.heatingEfficiency.setEnabled(True)
                    # self.heatingCapacity.lineEdit().setEnabled(True)
                    self.P_max_heating.setEnabled(True)
                    self.heatingTechMin.setEnabled(True)
                    self.heatingRampUpDown.setEnabled(True)
                    self.heatingFixedCost.setEnabled(True)
                    self.heatingFuelCost.setEnabled(True)
                    self.heatingVariableCost.setEnabled(True)

                    if t == z[0]:  # Gas Boiler
                        self.future_sourceRead = self.future_simulator.sources_for_technology[9]  # 'Natural gas'
                    if t == z[2]:  # "Oil Boiler"
                        self.future_sourceRead = self.future_simulator.sources_for_technology[10]  # 'Heating Oil'
                    if t == z[1]:  # "Biomass Boiler"
                        self.future_sourceRead = self.future_simulator.sources_for_technology[1]  # 'Biomass foresty'

                if key == list(key_list)[1]:  # electrical_heater
                    # self.heatingCapacity.lineEdit().setEnabled(True)
                    self.P_max_heating.setEnabled(True)
                    self.heatingTechMin.setEnabled(True)
                    self.heatingEfficiency.setEnabled(True)
                    self.heatingVariableCost.setEnabled(True)
                    self.heatingFuelCost.setEnabled(True)
                    self.heatingFixedCost.setEnabled(True)
                    self.future_sourceRead = self.future_simulator.sources_for_technology[11]  # 'Electricity'

                if key == list(key_list)[2]:  # heat_pump
                    self.P_max_heating.setEnabled(True)
                    self.heatingTechMin.setEnabled(True)
                    self.heatingRampUpDown.setEnabled(True)
                    self.heatingVariableCost.setEnabled(True)
                    self.heatingFixedCost.setEnabled(True)
                    self.heatingTemp.setEnabled(True)
                    self.heatingFuelCost.setEnabled(True)
                    if t == z[0]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[5]
                    if t == z[1]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[12]
                    if t == z[2]:
                        self.future_sourceRead = self.future_simulator.ask_for_sources(t, serv="heating")

                if key == list(key_list)[3]:  # cogeneration
                    self.P_max_heating.setEnabled(True)
                    self.heatingTechMin.setEnabled(True)
                    self.heatingEfficiency.setEnabled(True)
                    self.cb_CHP_heating.setEnabled(True)
                    self.heatingRampUpDown.setEnabled(True)
                    self.heatingVariableCost.setEnabled(True)
                    self.heatingFuelCost.setEnabled(True)
                    self.heatingFixedCost.setEnabled(True)
                    self.heatingElsale.setEnabled(True)
                    if t == z[0]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[9]  # 'Natural gas'
                    elif t == z[1]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[10]  # 'Heating Oil'
                    elif t == z[2]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[1]  # 'Biomass foresty'

                if key == list(key_list)[4]:  # solar_thermal
                    self.heatingEfficiency.setEnabled(True)
                    self.heatingInclinazione.setEnabled(True)
                    self.heating1coeff.setEnabled(True)
                    self.heating2coeff.setEnabled(True)
                    self.heatingTemp.setEnabled(True)
                    self.heatingVariableCost.setEnabled(True)
                    self.heatingFixedCost.setEnabled(True)
                    self.future_sourceRead = self.future_simulator.sources_for_technology[2]

                if key == list(key_list)[5]:  # cooling_heat_pump
                    # self.heatingCapacity.lineEdit().setEnabled(True)
                    self.heatingVariableCost.lineEdit().setEnabled(True)

                    if t == z[0]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[
                            8]  # 'Geothermal - Shallow - Ground cold extraction'
                    elif t == z[1]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[5]  # 'Air'

                # 7 thermal energy storage
                # 8 domestic_hot_water_thermal_energy_storage
                if key == list(key_list)[8] or key == list(key_list)[7]:
                    self.Tes_size_heating.setEnabled(True)
                    self.Soc_min_heating.setEnabled(True)
                    self.tes_startEnd_heating.setEnabled(True)
                    self.tes_discharge_heating.setEnabled(True)
                    self.heatingFixedCost.setEnabled(True)
                    self.heatingTES_loss.setEnabled(True)
                    self.heatingVariableCost.setEnabled(True)
                    self.future_sourceRead = self.future_simulator.sources_for_technology[0]

                if key == list(key_list)[12]:  # absorption_heat_pump
                    self.P_max_heating.setEnabled(True)
                    self.COP_heating.setEnabled(True)
                    self.heatingVariableCost.setEnabled(True)
                    self.heatingFixedCost.setEnabled(True)
                    self.heatingFuelCost.setEnabled(True)
                    self.heatingTechMin.setEnabled(True)
                    self.heatingRampUpDown.setEnabled(True)
                    if t == z[0]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[5]  # 'Air'
                    if t == z[1]:
                        self.future_sourceRead = self.future_simulator.sources_for_technology[
                            12]  # 'Geothermal - Shallow - Ground heat extraction'
                    if t == z[2]:  # "Absorption Heat Pump"
                        self.future_sourceRead = self.future_simulator.sources_for_technology[0]  # ' 'logy[0]  #
        return


    def futureActive_source_dialogDHW(self,p):
        self.future_sourceDHW = ''

        q = str(self.dhwTechnology.currentText())

        self.disable_all_dhw_input()

        key_list = self.future_simulator.individual_H_C_dict_var.keys()

        for key in key_list:
            z = self.future_simulator.individual_H_C_dict_var[key]

            if q in z:
                if key == list(key_list)[0]:  # heat_only_boiler

                    self.dhwEfficiency.setEnabled(True)
                    self.dhwP_max.setEnabled(True)
                    self.dhwTechMin.setEnabled(True)
                    self.dhwRampUpDown.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.dhwFuelCost.setEnabled(True)
                    if q == z[0]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[9]  # 'Natural gas'
                    if q == z[1]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[1]  # 'Biomass foresty'
                    if q == z[2]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[10]  # 'Heating Oil'

                if key == list(key_list)[1]:  # electrical_heater
                    # self.dhwCapacity.lineEdit().setEnabled(True)
                    self.dhwEfficiency.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.dhwFuelCost.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.dhwTechMin.setEnabled(True)
                    self.dhwRampUpDown.setEnabled(True)
                    self.dhwP_max.setEnabled(True)
                    self.future_sourceDhw = self.future_simulator.sources_for_technology[11]  # 'Electricity'

                if key == list(key_list)[2]:  # heat_pump
                    self.dhwP_max.setEnabled(True)
                    self.dhwTechMin.setEnabled(True)
                    self.dhwRampUpDown.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.dhwTemp.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.dhwFuelCost.setEnabled(True)
                    # self.simulator.ask_for_sources(q, serv="dhw")
                    if q == z[0]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[5]
                    if q == z[1]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[12]
                    if q == z[2]:
                        self.future_sourceDhw = self.future_simulator.ask_for_sources(t, serv="heating")

                    # self.sourceDhw = self.simulator.sources_for_technology[0]
                    # if q == z[1]:
                    #    self.sourceDhw = self.simulator.sources_for_technology[5] # 'Air'

                if key == list(key_list)[3]:  # cogeneration
                    self.dhwP_max.setEnabled(True)
                    self.dhwTechMin.setEnabled(True)
                    self.dhwEfficiency.setEnabled(True)
                    self.dhwRampUpDown.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.dhwFuelCost.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.dhwElsale.setEnabled(True)
                    self.dhwCb_CHP.setEnabled(True)
                    if q == z[0]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[9]  # 'Natural gas'
                    elif q == z[1]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[10]  # 'Heating Oil'
                    elif q == z[2]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[1]  # 'Biomass foresty'

                if key == list(key_list)[4]:  # solar_thermal
                    self.dhwEfficiency.setEnabled(True)
                    self.dhwInclinazione.setEnabled(True)
                    self.dhw1coeff.setEnabled(True)
                    self.dhw2coeff.setEnabled(True)
                    self.dhwTemp.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)

                    self.future_sourceDhw = self.future_simulator.sources_for_technology[2]  # ' '

                if key == list(key_list)[5]:  # cooling_heat_pump
                    # self.heatingCapacity.lineEdit().setEnabled(True)
                    self.heatingVariableCost.lineEdit().setEnabled(True)

                    if q == z[0]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[
                            8]  # 'Geothermal - Shallow - Ground cold extraction'
                    elif q == z[1]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[5]  # 'Air'

                if key == list(key_list)[8] or key == list(key_list)[7]:  # 8 domestic_hot_water_thermal_energy_storage
                    self.dhwTes_size.setEnabled(True)
                    self.dhwSoc_min.setEnabled(True)
                    self.dhwTes_startEnd.setEnabled(True)
                    self.dhwTes_discharge.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.DHWTES_loss.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.future_sourceDhw = self.future_simulator.sources_for_technology[0]  # ' '

                if key == list(key_list)[9] or key == list(key_list)[10] or key == list(key_list)[11]:
                    # 12-13-14 Waste Heat Compression Heat Pump Low T/Medium T/High T
                    self.dhwP_max.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.dhwFuelCost.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.dhwTechMin.setEnabled(True)

                if key == list(key_list)[12]:  # absorption_heat_pump
                    self.dhwP_max.setEnabled(True)
                    self.dhwCop.setEnabled(True)
                    self.dhwVariableCost.setEnabled(True)
                    self.dhwFuelCost.setEnabled(True)
                    self.dhwFixedCost.setEnabled(True)
                    self.dhwTechMin.setEnabled(True)
                    self.dhwRampUpDown.setEnabled(True)
                    # self.ask_for_sources(q)
                    if q == z[0]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[5]  # 'Air'
                    if q == z[1]:
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[
                            12]  # 'Geothermal - Shallow - Ground heat extraction'
                    if q == z[2]:  # "Absorption Heat Pump"
                        self.future_sourceDhw = self.future_simulator.sources_for_technology[0]  # ' '
        return

    def futureActive_source_dialogNetwork(self):
        self.disable_all_network_input()
        self.future_sourceNet = ""

        t = str(self.networkTechnology.currentText())
        key_list = self.future_simulator.district_function.keys()

        for key in key_list:
            print(key)
            z = self.future_simulator.district_function[key]

            if t in z:
                if key == list(key_list)[0]:  # heat_only_boiler
                    self.networkEta.setEnabled(True)
                    self.networkP_max.setEnabled(True)
                    self.networkTechMin.setEnabled(True)
                    self.networkRampUpDown.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    if t == z[0]:  # Gas Boiler
                        self.future_sourceNet = self.future_simulator.sources_for_technology[9]
                    if t == z[1]:  # Biomass Boiler
                        self.future_sourceNet = self.future_simulator.sources_for_technology[1]
                    if t == z[2]:  # Oil Boiler
                        self.future_sourceNet = self.future_simulator.sources_for_technology[10]
                    if t == z[3]:  # Boiler
                        self.future_sourceNet = self.future_simulator.sources_for_technology[0]
                    return

                if key == list(key_list)[1]:  # electrical_heater

                    # self.networkCapacity.lineEdit().setEnabled(True)
                    self.networkEta.setEnabled(True)
                    self.networkP_max.setEnabled(True)
                    self.networkTechMin.setEnabled(True)
                    self.networkRampUpDown.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.future_sourceNet = self.future_simulator.sources_for_technology[11]
                    return

                if key == list(key_list)[2]:  # heat_pump

                    self.networkP_max.setEnabled(True)
                    self.networkTechMin.setEnabled(True)
                    self.networkTemp.setEnabled(True)
                    self.networkRampUpDown.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    if t == z[0]:  # Air source compression heat pump
                        self.future_sourceNet = self.future_simulator.sources_for_technology[5]
                    if t == z[1]:  # Shallow geothermal compression heat pump
                        self.future_sourceNet = self.future_simulator.sources_for_technology[12]
                    if t == z[2]:  # Heat pump
                        self.future_sourceNet = self.future_simulator.sources_for_technology[0]
                    return
                else:
                    pass
                    # self.networkSources.setEnabled(False)

                if key == list(key_list)[3]:  # cogeneration

                    self.networkP_max.setEnabled(True)
                    self.networkTechMin.setEnabled(True)
                    self.networkEta.setEnabled(True)
                    self.networkRampUpDown.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    self.network_el_sale.setEnabled(True)

                    if t == z[0]:  # Gas CHP
                        self.future_sourceNet = self.future_simulator.sources_for_technology[9]
                    if t == z[1]:  # Oil CHP
                        self.future_sourceNet = self.future_simulator.sources_for_technology[10]
                    if t == z[2]:
                        self.future_sourceNet = self.future_simulator.sources_for_technology[1]
                    if t == z[3]:  # Cogeneration
                        self.future_sourceNet = self.future_simulator.sources_for_technology[0]
                    return

                if key == list(key_list)[4]:  # solar_thermal

                    self.networkarea.setEnabled(True)
                    self.networkEta.setEnabled(True)
                    self.network1coeff.setEnabled(True)
                    self.network2coeff.setEnabled(True)
                    self.networkTemp.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.future_sourceNet = self.future_simulator.sources_for_technology[2]
                    return

                if key == list(key_list)[5]:  # 16 seasonal_solar_thermal

                    self.networkTes_size.setEnabled(True)
                    self.networkSocMin.setEnabled(True)
                    self.networkTesStartEnd.setEnabled(True)
                    self.networkTes_discharge.setEnabled(True)
                    self.future_sourceNet = self.future_simulator.sources_for_technology[2]
                    return

                if key == list(key_list)[6]:  # absorption_heat_pump

                    self.networkTechMin.setEnabled(True)
                    self.networkCop_absorption.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    self.networkP_max.setEnabled(True)
                    # self.networkSources.setEnabled(True)
                    # self.future_sourceNet = self.future_simulator.ask_tchnology_for_absoptionHeatPump(t)
                    if t == z[0]:  # Air source gas absorption heat pump
                        self.future_sourceNet = self.future_simulator.sources_for_technology[9]
                    if t == z[1]:  # Shallow geothermal gas absorption heat pump
                        self.future_sourceNet = self.future_simulator.sources_for_technology[12]
                    if t == z[2]:  # Absorption heat pump
                        self.future_sourceNet = self.future_simulator.sources_for_technology[0]
                    return

                if key == list(key_list)[7] or key == list(key_list)[
                    8]:  # 7 waste_heat_heat_exchangers # 8 waste_cooling_heat_exchangers
                    # self.networkCapacity.lineEdit().setEnabled(True)
                    self.networkP_min.setEnabled(True)
                    #self.networkTechMin.setEnabled(True)
                    self.networkP_max.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    if key == list(key_list)[8]:  # waste_cooling_heat_exchangers
                        self.future_simulator.ask_for_sources(t, serv="network")
                        self.future_sourceNet = self.future_simulator.selected_source
                    else:  # 7 waste_heat_heat_exchangers
                        if t == z[0]:  # Deep geothermal HEX
                            self.future_sourceNet = self.future_simulator.sources_for_technology[3]
                        if t == z[1]:  # Industrial waste heat HEX
                            self.future_sourceNet = self.future_simulator.sources_for_technology[14]
                        if t == z[2]:  # Waste heat – HEX
                            self.future_simulator.ask_for_sources(t, serv="network")
                            self.future_sourceNet = self.future_simulator.selected_source
                    return

                if key == list(key_list)[9] or key == list(key_list)[10] or key == list(key_list)[
                    11]:  # waste_heat_heat_pumps_temperature_group1 ,2 ,3

                    self.networkP_max.setEnabled(True)
                    self.networkTemp.setEnabled(True)
                    self.networkTechMin.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    self.future_simulator.ask_for_sources(t, serv="network")
                    self.future_sourceNet = self.future_simulator.selected_source
                    return

                if key == list(key_list)[13]:  # seasonal_waste_heat_pump

                    # self.networkCapacity.lineEdit().setEnabled(True)
                    self.networkTechMin.setEnabled(True)
                    self.networkTemp.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.future_simulator.ask_for_sources(t, serv="network")
                    self.future_sourceNet = self.future_simulator.selected_source
                    # self.networkSources.setEnabled(True)
                    return
                else:
                    # self.networkSources.setEnabled(False)
                    pass

                # seasonal_solar_thermal energy storage
                # thermal energy storage
                if key == list(key_list)[14] or key == list(key_list)[12]:  # seasonal_solar_thermal
                    self.networkTes_size.setEnabled(True)
                    self.networkSocMin.setEnabled(True)
                    self.networkTesStartEnd.setEnabled(True)
                    self.networkTes_discharge.setEnabled(True)
                    self.networkTES_loss.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.future_sourceNet = self.future_simulator.sources_for_technology[2]
                    return

                if key == list(key_list)[15]:  # waste_heat_absorption_heat_pump
                    self.networkTechMin.setEnabled(True)
                    self.networkCop_absorption.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    self.networkP_max.setEnabled(True)
                    self.future_simulator.ask_for_sources(t, serv="network")
                    self.future_sourceNet = self.future_simulator.selected_source
                    return

                if key == list(key_list)[16]:  # ORC Cogeneration

                    self.networkP_max.setEnabled(True)
                    self.networkTechMin.setEnabled(True)
                    self.networkEta.setEnabled(True)
                    self.networkRampUpDown.setEnabled(True)
                    self.networkVariableCost.setEnabled(True)
                    self.networkFixedCost.setEnabled(True)
                    self.networkFuelCost.setEnabled(True)
                    self.network_el_sale.setEnabled(True)
                    self.networkcb_CHP.setEnabled(True)
                    self.networkP_min.setEnabled(True)
                    if t == z[0]:  # Waste heat ORC
                        self.future_sourceNet = self.future_simulator.sources_for_technology[14]
                    if t == z[1]:  # Deep geothermal ORC
                        self.future_sourceNet = self.future_simulator.sources_for_technology[3]
                    if t == z[2]:  # Gas ORC
                        self.future_sourceNet = self.future_simulator.sources_for_technology[9]
                    if t == z[3]:  # Biomass ORC
                        self.future_sourceNet = self.future_simulator.sources_for_technology[1]
                    return
        return

    def future_input_transportSector(self):
        consumption_gasoline = self.averegeGasoline.value()
        emissions_gasoline = self.averageCO2gasoline.value()
        gasoline_calorific = self.gasoline.value()
        consumption_diesel = self.averageDiesel.value()
        diesel_calorific = self.diesel.value()
        emissions_diesel = self.averageCO2diesel.value()
        nr_ofPerson = self.personalVehicles.value()
        gasoline_vehicle = self.gasolineVehicles.value()
        daily_distance = self.dailyDistance.value()
        nr_electricalVeicle = self.electricVehicles.value()
        specific_energy = self.energyConsum.value()
        electrical_sector = self.co2ElectricalSector.value()
        battery_capacity = self.avarageBattery.value()
        charging_discharging = self.avarageChargingDischarging.value()
        diesel_vehicles = self.dieselVehicles.value()
        weekend = self.weekend.value()
        winter = self.btnWinter.value()
        spring = self.btnSpring.value()
        summer = self.btnSummer.value()
        autumn = self.btnAutumn.value()

        self.future_list_input = [
            consumption_gasoline,
            emissions_gasoline,
            gasoline_calorific,
            consumption_diesel,
            diesel_calorific,
            emissions_diesel,
            nr_ofPerson,
            gasoline_vehicle,
            daily_distance,
            nr_electricalVeicle,
            nr_electricalVeicle,
            specific_energy,
            electrical_sector,
            battery_capacity,
            charging_discharging,
            diesel_vehicles, weekend, winter,
            spring,
            summer,
            autumn]

        self.trasport_sector_calc.cacluation_transport(self.future_list_input)


    def check_tech_capacity(self):
        if self.muted:
            return True
        if not self.check_sources():
            return
        building_list = []
        for i in range(self.dmmTree_future.topLevelItemCount()):
            building = self.dmmTree_future.topLevelItem(i)
            for j in range(building.childCount()):
                tech_type = building.child(j)
                capacity = 0.0
                if tech_type.childCount() == 0:
                    continue
                for k in range(tech_type.childCount()):
                    technology = tech_type.child(k)
                    try:
                        capacity = capacity + float(technology.text(8))
                    except:
                        print("Step1, check_tech_capacity. Float conversion failed:", technology.text(8))
                if capacity < float(tech_type.text(1)):
                    building_list.append(building.text(0))
                    break
        msgBox = QMessageBox()
        s = "\n"
        i = 0
        if not len(building_list) == 0:
            for building in building_list:
                s = s + "-> " + building + "\n"
                i = i + 1
                if i > 20:
                    s = s + "-> " + "... other " + str(len(building_list) - 1) + " buildings..."
                    break
            msgBox.setText("Are you sure to continue?")
            msgBox.setInformativeText("The technologies of the following buildings do not cover the peak demand: " + s)
            msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            ret = msgBox.exec()
            if ret == QMessageBox.Cancel:
                return False
            else:
                return True
        else:
            return True

    def tab_current_changed(self, index):
        self.insert_techNetwork()

    def network_tree_widget_clicked(self, item, _):
        try:
            P_max = round(float(item.data(8, Qt.UserRole)), 2)
        except:
            P_max = None
        if P_max is not None:
            self.networkP_max.setValue(P_max)
        self.network_efficiency.change_spin_box_value(item)

    def disable_all_dhw_input(self):
        self.safe_disable_input(self.dhwElsale)
        self.safe_disable_input(self.dhwInclinazione)
        self.safe_disable_input(self.dhwTemp)
        self.safe_disable_input(self.dhwEfficiency)
        self.safe_disable_input(self.dhw1coeff)
        self.safe_disable_input(self.dhw2coeff)
        # self.safe_disable_input(self.dhwCapacity)
        self.safe_disable_input(self.dhwP_max)
        self.safe_disable_input(self.dhwP_min)
        self.safe_disable_input(self.dhwCb_CHP)
        self.safe_disable_input(self.dhwTechMin)
        self.safe_disable_input(self.dhwRampUpDown)
        self.safe_disable_input(self.dhwFixedCost)
        self.safe_disable_input(self.dhwFuelCost)
        self.safe_disable_input(self.dhwVariableCost)
        self.safe_disable_input(self.dhwTes_size)
        self.safe_disable_input(self.dhwSoc_min)
        self.safe_disable_input(self.dhwTes_startEnd)
        self.safe_disable_input(self.dhwTes_discharge)
        self.safe_disable_input(self.dhwCop)
        self.safe_disable_input(self.DHWTES_loss)

    def disable_all_heating_input(self):
        self.safe_disable_input(self.heatingElsale)
        self.safe_disable_input(self.heatingInclinazione)
        self.safe_disable_input(self.heatingTemp)
        self.safe_disable_input(self.heatingEfficiency)
        self.safe_disable_input(self.heating1coeff)
        self.safe_disable_input(self.heating2coeff)
        # self.safe_disable_input(self.heatingCapacity)
        self.safe_disable_input(self.P_max_heating)
        self.safe_disable_input(self.P_min_heating)
        self.safe_disable_input(self.cb_CHP_heating)
        self.safe_disable_input(self.heatingTechMin)
        self.safe_disable_input(self.heatingRampUpDown)
        self.safe_disable_input(self.heatingFixedCost)
        self.safe_disable_input(self.heatingFuelCost)
        self.safe_disable_input(self.heatingVariableCost)
        self.safe_disable_input(self.Tes_size_heating)
        self.safe_disable_input(self.Soc_min_heating)
        self.safe_disable_input(self.tes_startEnd_heating)
        self.safe_disable_input(self.tes_discharge_heating)
        self.safe_disable_input(self.COP_heating)
        self.safe_disable_input(self.heatingTES_loss)

    def disable_all_cooling(self):
        self.safe_disable_input(self.coolingInclinazione)
        self.safe_disable_input(self.coolingTemp)
        self.safe_disable_input(self.coolingEfficiency)
        self.safe_disable_input(self.cooling1coeff)
        self.safe_disable_input(self.cooling2coeff)
        self.safe_disable_input(self.P_max_cooling)
        self.safe_disable_input(self.P_min_cooling)
        self.safe_disable_input(self.cb_CHP_cooling)
        self.safe_disable_input(self.coolingTechMin)
        self.safe_disable_input(self.coolingRampUpDown)
        self.safe_disable_input(self.coolingFixedCost)
        self.safe_disable_input(self.coolingFuelCost)
        self.safe_disable_input(self.coolingVariableCost)
        self.safe_disable_input(self.Tes_size_cooling)
        self.safe_disable_input(self.cooling_socMin)
        self.safe_disable_input(self.cooling_tesStartEnd)
        self.safe_disable_input(self.tes_discharge_cooling)
        self.safe_disable_input(self.Cop_absorption_cooling)

    def disable_all_network_input(self):
        self.networkarea.setEnabled(False)
        self.networkP_min.setEnabled(False)
        self.networkTemp.setEnabled(False)
        self.networkEta.setEnabled(False)
        self.network1coeff.setEnabled(False)
        self.network2coeff.setEnabled(False)
        self.networkP_max.setEnabled(False)
        self.networkP_min.setEnabled(False)
        self.networkcb_CHP.setEnabled(False)
        self.networkTechMin.setEnabled(False)
        self.networkRampUpDown.setEnabled(False)
        self.networkVariableCost.setEnabled(False)
        self.networkFixedCost.setEnabled(False)
        self.networkFuelCost.setEnabled(False)
        self.networkTes_size.setEnabled(False)
        self.networkSocMin.setEnabled(False)
        self.networkTesStartEnd.setEnabled(False)
        self.networkTes_discharge.setEnabled(False)
        self.networkCop_absorption.setEnabled(False)
        self.network_el_sale.setEnabled(False)
        self.safe_disable_input(self.networkTES_loss)

    def safe_disable_input(self, widget):
        try:
            widget.setEnabled(False)
        except Exception as e:
            print("Step4_dockwidget.py, safe_disable_input():", e)

    def remove_tech(self, service):
        item: Building = CustomContextMenu.get_top_level(self.dmmTree_future.currentItem())
        removed = CustomContextMenu.erode_method(item, service=service)
        if removed and not item.modified:
            item.set_modified()

    def remove_tech_from_network(self):
        selected = self.futureDmmTreeNetwork.currentItem()
        if selected.parent() is not None:
            selected.parent().removeChild(selected)
        else:
            for i in range(selected.childCount()-1, -1, -1):
                selected.removeChild(selected.child(i))

    def additional_parameters_btn_handler(self):
        print(self.KPIs_additional_data)
        self.dialog_additional_parameters = AdditionalSimulationParameterGUI(data=self.KPIs_additional_data,
                                                                             description="Future Scenario additional parameters:")
        self.dialog_additional_parameters.data_emitter.connect(self.receive_additional_parameters)
        self.dialog_additional_parameters.show()

    def receive_additional_parameters(self, data):
        print("Step4.receive_additional_parameters(). data:", data)
        if isinstance(data, dict):
            self.KPIs_additional_data = data

    def check_sources(self):
        if self.muted:
            return True
        check_result = {}
        for i in range(self.step0_source_availability_table.rowCount()):
            try:
                source = self.step0_source_availability_table.item(i, 0).text()
            except:
                source = ""
            try:
                availability = float(self.step0_source_availability_table.item(i, 1).text())
                availability = round(availability, 2)
            except:
                availability = 0
            if not source == "":
                used = self.sum_sources_used(source)
                if availability < used:
                    check_result[source] = [availability, used]
        if len(check_result) == 0:
            message = ""
        else:
            message = "Source availability: " + str(len(check_result)) + " warnings!\n\n"
        for key in check_result.keys():
            message = message + "- " + str(key) + " available: " + str(check_result[key][0]) + "MW, used: " + str(check_result[key][1]) + "MW\n"

        msgBox = QMessageBox()
        msgBox.setText("Are you sure to continue?")
        msgBox.setInformativeText(message)
        msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()

        if ret == QMessageBox.Cancel:
            return False
        else:
            return True

    def sum_sources_used(self, source):
        output = 0
        for i in range(self.dmmTree_future.topLevelItemCount()):
            building = self.dmmTree_future.topLevelItem(i)
            for j in range(building.childCount()):
                H_C_DHW_DHWH = building.child(j)
                for k in range(H_C_DHW_DHWH.childCount()):
                    technology = H_C_DHW_DHWH.child(k)
                    if technology.text(2) == source:
                        try:
                            output = output + float(technology.text(8))/1000.0  #1000.0 if step0 tab is in MW
                        except:
                            pass
        for i in range(self.futureDmmTreeNetwork.topLevelItemCount()):
            network = self.futureDmmTreeNetwork.topLevelItem(i)
            for j in range(network.childCount()):
                gen_point = network.child(j)
                if gen_point.text(2) == source:
                    try:
                        output = output + float(technology.text(8))
                    except:
                        pass
        try:
            output = round(output, 2)
        except:
            pass
        return output

    def building_characterizzation_changed(self, item: QTreeWidgetItem, column: int):
        try:
            building: Building = item.parent().parent()
            if not building.modified:
                building.set_modified()
        except:
            pass
