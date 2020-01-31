from .LoadScenario import LoadScenario
from PyQt5.QtWidgets import QMessageBox, QTreeWidget, QTreeWidgetItem
from PyQt5 import QtCore
from qgis.core import QgsProject
import os
import os.path
from ..utility.data_manager.DataTransfer import DataTransfer
from ..utility.data_manager.TechnologiesTransfer import TechnologiesTransfer
from ..utility.data_manager.SourceTransfer import SourceTransfer
from .AoutLoadNetwork import AutoLoadNetwork
from .NetworkBuilder import NetworkBuilder
from ..LoadInterface import LoadInterface
from PyQt5.QtCore import pyqtSignal
import time
import traceback


class LoadDistrict(LoadScenario):

    finished = pyqtSignal()

    dpmdialog = None
    district = None
    step0 = None
    step1 = None
    step2 = None
    step3 = None
    step4 = None
    simulation = None

    save_interface: LoadInterface = None

    def __init__(self, folder=None, version=None):
        save_folder_name: str = "Save"
        if folder is None:
            self.work_folder = None
        else:
            self.work_folder = os.path.abspath(os.path.join(folder, save_folder_name))
        LoadScenario.__init__(self, self.work_folder, version=version)
        self.initialized = False
        self.progress_bar_limit = 6

    def initialize(self):
        if not self.initialized:
            self.save_interface.effectiveLoad.connect(self.run)
            self.initialized = True

    def run(self, file_name):
        try:
            print("LoadDistrict.run(). folder", self.folder)
            if file_name is None:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                main_text = "Please select a file."
                msgBox.setText(main_text)
                msgBox.setInformativeText("You need to select a saved file before loading a project version.")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.exec()
                return
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            main_text = "Load and override data?"
            msgBox.setText(main_text)
            msgBox.setInformativeText("All the unsaved data wil be lost. Continue?")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            r = msgBox.exec()
            if not r == QMessageBox.Ok:
                return

            self.load(file_name)

            result = self.version_check(self.get_data("plugin_version", self.data))
            if not result:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText("Version mismatch.")
                msgBox.setInformativeText("You are loading a file saved with a different version of the pluging.\n"
                                          "Data may not be correctly loaded!\nContinue anyway?")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Ok)
                r = msgBox.exec()
                if not r == QMessageBox.Ok:
                    return

            result = self.load_general_state()
            if result:
                self.progressBarUpdate.emit(1, self.progress_bar_limit, True)
                result = self.load_step0()
            if result:
                self.import_base_fut_networks()
                self.progressBarUpdate.emit(2, self.progress_bar_limit, True)
                result = self.load_step1(file_name)
            if result:
                self.progressBarUpdate.emit(3, self.progress_bar_limit, True)
                result = self.load_step2()
            if result:
                self.progressBarUpdate.emit(4, self.progress_bar_limit, True)
                result = self.load_step3()
            if result:
                self.progressBarUpdate.emit(5, self.progress_bar_limit, True)
                result = self.load_step4(file_name)
            self.progressBarUpdate.emit(6, self.progress_bar_limit, True)
            self.finished.emit()
            self.prepare_UI()
            print("LoadDIstrict.run(): DONE")
        except Exception:
            self.progressBarUpdate.emit(0, self.progress_bar_limit, False)
            self.prepare_UI()
            print("LoadDIstrict.run(): ERROR")
            traceback.print_exc()

    def prepare_UI(self):
        self.step0.hide()
        self.step1.hide()
        self.step2.hide()
        self.step3.hide()
        self.step4.hide()
        self.simulation.hide()
        self.dpmdialog.show()

    def import_base_fut_networks(self):
        auto_loader = AutoLoadNetwork(self.step1.work_folder)

        networks_dict = self.import_networks("baseline")
        self.create_network_groups(networks_dict)
        self.step1.DHN_network_list = networks_dict["DHN"]
        self.step1.DCN_network_list = networks_dict["DCN"]
        self.step1.refresh_DHN_network()
        self.step1.refresh_DCN_network()
        for networks in [self.step1.DHN_network_list, self.step1.DCN_network_list]:
            for network in networks:
                auto_loader.load(network, self.step1.data_transfer)

        networks_dict = self.import_networks("future")
        self.create_network_groups(networks_dict)
        self.step4.futureDHN_network_list = networks_dict["DHN"]
        self.step4.futureDCN_network_list = networks_dict["DCN"]
        self.step4.refresh_DHN_network()
        self.step4.refresh_DCN_network()
        for networks in [self.step4.futureDHN_network_list, self.step4.futureDCN_network_list]:
            for network in networks:
                auto_loader.load(network, self.step4.data_transfer)

    def load_step4(self, file):
        self.set_check_state(self.step4.futureDistrictSolution, self.get_data("futureDistrictSolution"))
        self.set_check_state(self.step4.futureBuildingSolution, self.get_data("futureBuildingSolution"))
        self.set_check_state(self.step4.futureDHN, self.get_data("futureDHN"))
        self.set_check_state(self.step4.futureDCN, self.get_data("futureDCN"))
        self.step4.KPIs_additional_data = self.get_object_from_zip("KPIs_additional_data")
        self.fill_tre_widget_item(self.step4.futureDmmTreeNetwork)
        self.fill_table_widget_item(self.step4.suppliesTable_future)
        self.update_buildings_tre_widget_item(self.step4.dmmTree_future)
        self.fill_double_spin_box(self.step4.averegeGasoline, self.get_data("averegeGasoline_future"))
        self.fill_double_spin_box(self.step4.averageCO2gasoline, self.get_data("averageCO2gasoline_future"))
        self.fill_double_spin_box(self.step4.gasoline, self.get_data("gasoline_future"))
        self.fill_double_spin_box(self.step4.averageDiesel, self.get_data("averageDiesel_future"))
        self.fill_double_spin_box(self.step4.diesel, self.get_data("diesel_future"))
        self.fill_double_spin_box(self.step4.averageCO2diesel, self.get_data("averageCO2diesel_future"))
        self.fill_double_spin_box(self.step4.personalVehicles, self.get_data("personalVehicles_future"))
        self.fill_double_spin_box(self.step4.gasolineVehicles, self.get_data("gasolineVehicles_future"))
        self.fill_double_spin_box(self.step4.dailyDistance, self.get_data("dailyDistance_future"))
        self.fill_double_spin_box(self.step4.electricVehicles, self.get_data("electricVehicles_future"))
        self.fill_double_spin_box(self.step4.energyConsum, self.get_data("energyConsum_future"))
        self.fill_double_spin_box(self.step4.co2ElectricalSector, self.get_data("co2ElectricalSector_future"))
        self.fill_double_spin_box(self.step4.avarageBattery, self.get_data("avarageBattery_future"))
        self.fill_double_spin_box(self.step4.avarageChargingDischarging,
                                  self.get_data("avarageChargingDischarging_future"))
        self.fill_double_spin_box(self.step4.dieselVehicles, self.get_data("dieselVehicles_future"))
        self.fill_double_spin_box(self.step4.weekend, self.get_data("weekend_future"))
        self.fill_double_spin_box(self.step4.btnWinter, self.get_data("btnWinter_future"))
        self.fill_double_spin_box(self.step4.btnSpring, self.get_data("btnSpring_future"))
        self.fill_double_spin_box(self.step4.btnSummer, self.get_data("btnSummer_future"))
        self.fill_double_spin_box(self.step4.btnAutumn, self.get_data("btnAutumn_future"))
        self.fill_table_widget_item(self.step4.tableWidget_3f)
        self.fill_table_widget_item(self.step4.tableWidget_4f)
        if self.get_data("btnSimulation") is not None:
            if self.get_data("btnSimulation"):
                self.step4.muted = True
                self.step4.save_to_webserver.clicked.emit()
                self.step4.muted = False
                self.dpmdialog.hide()
                self.district.hide()
                return True
        return False

    def load_step3(self):
        self.fill_table_widget_item(self.step3.tableEnStep3)
        self.fill_table_widget_item(self.step3.tableENVStep3)
        self.fill_table_widget_item(self.step3.tableEcoStep3)
        self.fill_table_widget_item(self.step3.tableSoStep3)
        self.fill_table_widget_item(self.step3.tableVisKpiEn)
        self.fill_table_widget_item(self.step3.tableVisKpiEnv)
        self.fill_table_widget_item(self.step3.tableVisKpiEco)
        self.fill_table_widget_item(self.step3.tableVisKpiSo)
        self.fill_table_widget_item(self.step3.tableWidgetp)
        self.fill_table_widget_item(self.step3.tableWidget_2p)
        self.fill_table_widget_item(self.step3.tableWidget_3p)
        self.fill_table_widget_item(self.step3.tableWidget_4p)
        self.fill_table_widget_item(self.step3.tableWidget_5p)
        self.fill_list_widget_item(self.step3.energy_criteria)
        self.fill_list_widget_item(self.step3.environmental_criteria)
        self.fill_list_widget_item(self.step3.economic_criteria)
        self.fill_list_widget_item(self.step3.social_criteria)
        self.step3.update_KPIs_visualization_tab()
        self.step3.fec_visualizer_service.set_KPIs(self.step2.KPIs)
        self.step3.weights = self.get_object_from_zip("weights")
        self.step3.refresh_vito_report()
        if self.get_data("step4btn") is not None:
            if self.get_data("step4btn"):
                self.step3.oktargets.clicked.emit()
                self.dpmdialog.hide()
                return True
        return False

    def load_step2(self):
        self.step2.loading_mode_on = True
        self.step2.KPIs = self.get_object_from_zip("KPIs")
        self.step2.fec_visualizer_service.set_KPIs(self.step2.KPIs)
        self.fill_table_widget_item(self.step2.tableWidget_5)
        self.fill_table_widget_item(self.step2.tableWidget_2)
        self.fill_table_widget_item(self.step2.tableWidget_3)
        self.fill_table_widget_item(self.step2.tableWidget_4)
        self.step2.send_KPIs_to_future.emit(self.step2.KPIs if self.step2.KPIs is not None else {})
        if self.get_data("step3btn") is not None:
            if self.get_data("step3btn"):
                self.step2.okbtn.clicked.emit()
                self.dpmdialog.hide()
                self.step2.loading_mode_on = False
                return True
        self.step2.loading_mode_on = False
        return False

    def load_step1(self, file):
        self.step1.networks_send = self.get_data("networks_send", dict_data=self.get_data("STEP_1"))
        self.set_check_state(self.step1.checkBox, self.get_data("checkBox", dict_data=self.get_data("STEP_1")))
        self.set_check_state(self.step1.checkBox_buildingSolution,
                             self.get_data("checkBox_buildingSolution", dict_data=self.get_data("STEP_1")))
        self.set_check_state(self.step1.checkBox_3, self.get_data("checkBox_3", dict_data=self.get_data("STEP_1")))
        self.set_check_state(self.step1.checkBox_4, self.get_data("checkBox_4", dict_data=self.get_data("STEP_1")))
        self.update_buildings_tre_widget_item(self.step1.dmmTree)

        self.fill_table_widget_item(self.step1.sourcesTable)
        self.fill_tre_widget_item(self.step1.dmmTreeNetwork)
        self.fill_double_spin_box(self.step1.averegeGasoline, self.get_data("averegeGasoline",
                                                                            dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.averageCO2gasoline, self.get_data("averageCO2gasoline",
                                                                               dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.gasoline, self.get_data("gasoline", dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.averageDiesel, self.get_data("averageDiesel",
                                                                          dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.diesel, self.get_data("diesel", dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.averageCO2diesel, self.get_data("averageCO2diesel",
                                                                             dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.personalVehicles, self.get_data("personalVehicles",
                                                                             dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.gasolineVehicles, self.get_data("gasolineVehicles",
                                                                             dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.dailyDistance, self.get_data("dailyDistance",
                                                                          dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.electricVehicles, self.get_data("electricVehicles",
                                                                             dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.energyConsum, self.get_data("energyConsum",
                                                                         dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.co2ElectricalSector, self.get_data("co2ElectricalSector",
                                                                                dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.avarageBattery, self.get_data("avarageBattery",
                                                                           dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.avarageChargingDischarging,
                                  self.get_data("avarageChargingDischarging", dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.dieselVehicles, self.get_data("dieselVehicles",
                                                                           dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.weekend, self.get_data("weekend", dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.btnWinter, self.get_data("btnWinter", dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.btnSpring, self.get_data("btnSpring", dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.btnSummer, self.get_data("btnSummer", dict_data=self.get_data("STEP_1")))
        self.fill_double_spin_box(self.step1.btnAutumn, self.get_data("btnAutumn", dict_data=self.get_data("STEP_1")))
        if self.get_data("step2btn") is not None:
            if self.get_data("step2btn"):
                self.step1.muted = True
                self.step1.save.clicked.emit()
                if self.step1.networks_send:
                    self.force_techologies_transfer()
                self.step1.muted = False
                self.dpmdialog.hide()
                return True
        return False

    def load_step0(self):
        self.step0.pushButton_load_all_files.clicked.emit()

        self.step0.data_transfer = DataTransfer()
        self.step0.data_transfer.geo_graph = self.step0.geo_graph
        self.step0.data_transfer.buildings = self.step0.baseline_scenario_layer
        self.step0.sources_temperature = self.get_object_from_zip("sources_temperature")
        self.step0.sources_availability = self.get_object_from_zip("sources_availability")
        if not isinstance(self.step0.sources_availability, dict) or not isinstance(self.step0.sources_temperature, dict):
            self.step0.send_data_to_step2.emit({}, {})
            print("LoadDIstrict.load_step0: sources_temperature e/o sources_temperature non erano dei dict")
        else:
            self.step0.send_data_to_step2.emit(self.step0.sources_availability, self.step0.sources_temperature)

        self.fill_table_widget_item(self.step0.sources_available)
        if self.get_data("step1btn") is not None:
            if self.get_data("step1btn"):
                self.step0.ok2.clicked.emit()
                self.dpmdialog.hide()
                return True
        return False

    def load_general_state(self):
        self.step1.dmmTree.clear()
        self.step0.folder.setText(self.get_data("step0.folder", self.data))
        self.step0.layerPath.setFilePath(self.get_data("step0.layerPath", self.data))
        self.step0.layerPath1.setFilePath(self.get_data("step0.layerPath1", self.data))
        layer_removed = self.remove_unwanted_layers()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        main_text = "All layers have been deleted!"
        msgBox.setText(main_text)
        msgBox.setInformativeText(
            "It's now possible to load saved data.\nThis process may take some minutes.")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        r = msgBox.exec()
        if r == QMessageBox.Ok:
            pass
        else:
            pass

        self.set_enabled_state(self.district.btnPlanning, self.get_data("btnPlanning"))
        self.set_enabled_state(self.district.btnSimulation, self.get_data("btnSimulation"))

        # self.set_enabled_state(self.dpmdialog.step0btn, self.get_data("step0btn"))
        self.set_enabled_state(self.dpmdialog.step1btn, False)
        self.set_enabled_state(self.dpmdialog.step2btn, False)
        self.set_enabled_state(self.dpmdialog.step3btn, False)
        self.set_enabled_state(self.dpmdialog.step4btn, False)
        return True

    def line_edit_set_text(self, widget, key):
        try:
            data = self.get_data(key)
            if data is not None:
                widget.setText(data)
        except KeyError:
            pass
        except AttributeError:
            data = self.get_data(key)
            if data is not None:
                widget.setFilePath(os.path.join(data))

    def saved_done(self):
        self.refresh_file_selection_combo_box()

    def remove_unwanted_layers(self):
        root = QgsProject.instance().layerTreeRoot()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        main_text = "All layers are about to be removed!"
        msgBox.setText(main_text)
        msgBox.setInformativeText(
            "This procedure will discard all the QGIS layers. Be sure to save them before continue. "
            "Press Ok to continue, Cancel to abort the procedure.")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        r = msgBox.exec()
        if not r == QMessageBox.Ok:
            return False
        try:
            root.removeAllChildren()
        except Exception:
            traceback.print_exc()
            return False
        return True

    def import_networks(self, scenario_type):
        if scenario_type == "baseline":
            m_scenario_type = "Baseline"
        else:
            m_scenario_type = "Future"

        networks_rel_path = self.get_data("zipPath." + scenario_type + "_networks", self.data)
        cooling_network_list = []
        heating_network_list = []
        if networks_rel_path is None or len(networks_rel_path) == 0:
            return {"DCN": cooling_network_list, "DHN": heating_network_list}
        self.wipe_out_existing_networks_files_and_folders(m_scenario_type)
        for network_rel_path in networks_rel_path:
            network_builder = NetworkBuilder()
            network_full_path = self.extract_network_from_zip(network_rel_path, scenario_type)
            network_builder.save_file_path = network_full_path
            network_builder.ID = os.path.split(network_full_path)[1]
            network_infos = self.get_object_from_zip("network_infos." + str(network_builder.ID))
            network_builder.efficiency = self.get_data("efficiency", network_infos, default=1)
            network_builder.scenario_type = scenario_type
            print("LoadDistrict.import_networks(). Imported:", network_full_path)
            for folder, sub_folders, file_names in os.walk(network_full_path):
                for file_name in file_names:
                    if file_name.endswith(".zip"):
                        network_builder.name = file_name[:-4]
            if "DHN" in network_full_path:
                network_builder.n_type = "DHN"
                heating_network_list.append(network_builder.build())
            if "DCN" in network_full_path:
                network_builder.n_type = "DCN"
                cooling_network_list.append(network_builder.build())
            print("LoadDistrict.import_networks()")

        return {"DCN": cooling_network_list, "DHN": heating_network_list}

    def node_has_child_name(self, node, child_name):
        for c in node.children():
            if child_name == c.name():
                return True
        return False

    def update_labels(self, file_name):
        file_path = self.file_manager.get_path_from_file_name(file_name, end_char=len(file_name),
                                                              search_folders=[self.file_manager.work_folder])
        if file_path is None:
            print(file_name, self.file_manager.work_folder)
            return
        info = os.stat(file_path).st_mtime
        year, month, day, hour, minute, second = time.localtime(info)[:-3]
        self.step0.project_creation_date.setText("Date modified: %02d/%02d/%d %02d:%02d:%02d" % (day, month, year, hour,
                                                                                                 minute, second))
        self.step0.project_version.setText("Project version: " + file_name[0:-5])
        year, month, day, hour, minute, second = time.localtime(time.time())[:-3]
        self.step0.project_load_date.setText("Loaded: %02d/%02d/%d %02d:%02d:%02d" % (day, month, year, hour,
                                                                                                 minute, second))

    def wipe_out_existing_networks_files_and_folders(self, m_scenario_type):
        save_path = self.file_manager.work_folder
        print("LoadDistrict.wipe_out_existing_networks_files_and_folders(): clearing",
              os.path.join(save_path, "../", m_scenario_type, "Networks"))
        self.file_manager.remove_folder(os.path.realpath(os.path.join(save_path, "../", m_scenario_type,
                                                                      "Networks", "DHN")))
        self.file_manager.remove_folder(os.path.realpath(os.path.join(save_path, "../", m_scenario_type,
                                                                      "Networks", "DCN")))

    def extract_network_from_zip(self, network_rel_path, m_scenario_type):
        try:
            save_path = self.file_manager.work_folder
            destination_path = None
            if "DHN" in network_rel_path:
                destination_path = os.path.join(save_path, "../", m_scenario_type, "Networks", "DHN")
            if "DCN" in network_rel_path:
                destination_path = os.path.join(save_path, "../", m_scenario_type, "Networks", "DCN")
            if destination_path is None:
                return
            zip_file_path = os.path.join(self.file_manager.work_folder, "data", self.file_loaded_name[0:-5] + ".zip")
            if not os.path.isfile(zip_file_path):
                print("LoadDistrict().extract_network_from_zip: file not found", zip_file_path)
                return
            if not os.path.isdir(destination_path):
                print("LoadDistrict().extract_network_from_zip: folder not found, trying to creating it",
                      destination_path)
                os.makedirs(destination_path, exist_ok=True)
            return self.extract_folder_from_zip(zip_file_path, network_rel_path, destination_path)
        except Exception as e:
            traceback.print_exc()
            print("Network extraction failed", e)

    def update_buildings_tre_widget_item(self, widget: QTreeWidget, name=None):
        if name is None:
            name = widget.objectName()
        if name not in [key for key in self.data.keys()]:
            print("SaveScenario.py, fill_tre_widget_item(). Error: widget item not found.")
            return
        if not self.data[name]["widgetType"] == "QTreeWidget":
            print("SaveScenario.py, fill_tre_widget_item(). Error: widget is not QTreeWidget.")
            return
        for i in range(widget.topLevelItemCount()):
            for j in range(widget.topLevelItem(i).childCount()):
                widget.topLevelItem(i).child(j).takeChildren()
        item = 0
        building_found = True
        while building_found:
            data = self.get_data("0_" + str(item), self.data[name])
            if data is None:
                building_found = False
                continue
            for j in range(3):
                service = self.get_data("1_" + str(j), data)
                if service is None:
                    continue
                technology_found = True
                technology_index = 0
                while technology_found:
                    technology = self.get_data("2_" + str(technology_index), service)
                    if technology is None:
                        technology_found = False
                        continue
                    self.update_tree_widget_building_technology(widget,
                                                                self.get_data("data", data),
                                                                self.get_data("data", service),
                                                                self.get_data("data", technology),
                                                                self.get_data("Qt.UserRole", technology))
                    technology_index += 1
            item += 1

    def update_tree_widget_building_technology(self, widget: QTreeWidget,
                                               building, service, technology, tech_user_role_data):
        if widget is None or building is None or service is None or technology is None:
            return
        for i in range(widget.topLevelItemCount()):
            building_item = widget.topLevelItem(i)
            if not building_item.text(0) == building[0]:
                continue
            for j in range(building_item.childCount()):
                service_item = building_item.child(j)
                if not service_item.text(0) == service[0]:
                    continue
                new_technology_item: QTreeWidgetItem = QTreeWidgetItem(service_item, technology)
                if tech_user_role_data is not None:
                    for k in range(len(tech_user_role_data)):
                        new_technology_item.setData(k, QtCore.Qt.UserRole, QtCore.QVariant(tech_user_role_data[i]))

    def create_network_groups(self, networks_dict):
        root = QgsProject.instance().layerTreeRoot()
        for network_list in [networks_dict[key] for key in networks_dict.keys()]:
            for n in network_list:
                group_name = n.n_type + " (" + n.scenario_type + "): " + n.name + " - ID:" + n.get_ID()
                group = root.findGroup(group_name)
                if group is None:
                    root.insertGroup(0, group_name)

    def force_techologies_transfer(self):
        self.step4.port_tech_from_baseline(TechnologiesTransfer(self.step1.dmmTree,
                                                n_tree=self.step1.dmmTreeNetwork), self.step1.building_layer,
                                           SourceTransfer(self.step1.sourcesTable))
