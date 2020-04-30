from .SaveScenario import SaveScenario
from ..LoadInterface import LoadInterface
from ..step1_v2 import PlanHeatDPMDockWidget
from ..Step4_docwidget import Step4_widget
from ..building.TreeItemManager import TreeItemManager
from PyQt5.QtWidgets import QMessageBox
import os.path
import os
from .. import master_planning_config as mp_config


class SaveDistrict(SaveScenario):
    dpmdialog = None
    district = None
    step0 = None
    step1: PlanHeatDPMDockWidget = None
    step2 = None
    step3 = None
    step4: Step4_widget = None
    simulation = None
    save_interface: LoadInterface = None

    work_folder = None

    def __init__(self, folder=None, version=None):
        save_folder_name: str = "Save"
        if folder is None:
            self.work_folder = None
        else:
            self.work_folder = os.path.abspath(os.path.join(folder, save_folder_name))
        SaveScenario.__init__(self, self.work_folder, version=version)
        self.save_steps_number = 7
        self.initialized = False

    def initialize(self):
        if not self.initialized:
            self.save_interface.effectiveSave.connect(self.save_plugin_clicked)
            self.initialized = True

    def save_plugin_clicked(self, file_name):
        project_name = mp_config.CURRENT_PROJECT_NAME #self.file_manager.get_file_name_from_user(self.step0)
        if project_name is None:
            message = "File name is missing. No files produced."
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("Invalid file name.")
            msgBox.setInformativeText(message)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec()
        else:
            self.override_save_plugin_state(project_name, file_name)

    def autosave(self):
        if not self.step1.autosave_done:
            self.step1.autosave_done = True
            self.save_interface.autosave()

    def override_save_plugin_state(self, project_name, file_name):
        self.clear_data()
        print("Ora raccolgo i dati da salvare:")
        print(self.data)
        self.save_general_state(project_name, file_name)
        self.save_step0()
        self.save_step_1(str(file_name))
        self.save_step_2()
        self.save_step_3()
        self.save_step_4(file_name)
        self.save_simulation()
        print("Ora salvo:")
        print(self.data)
        self.save(file_name + ".json")

    def save_general_state(self, project_name, file):
        self.data["plugin_version"] = self.version
        if self.work_folder is None:
            folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder"))
        else:
            folder = self.work_folder  # os.path.join(self.work_folder, "DefaultSaveFolder", file)
        self.data["work_folder"] = folder
        self.data["save_file_name"] = file + ".json"
        self.data["zip_file_name"] = file + ".zip"
        self.data["zip_file_path"] = os.path.realpath(os.path.join(folder, "Save", "data"))
        self.data["project_name"] = project_name
        self.data["btnPlanning"] = self.district.btnPlanning.isEnabled()
        self.data["btnSimulation"] = self.district.btnSimulation.isEnabled()
        self.data["step0btn"] = self.dpmdialog.step0btn.isEnabled()
        self.data["step1btn"] = self.dpmdialog.step1btn.isEnabled()
        self.data["step2btn"] = self.dpmdialog.step2btn.isEnabled()
        self.data["step3btn"] = self.dpmdialog.step3btn.isEnabled()
        self.data["step4btn"] = self.dpmdialog.step4btn.isEnabled()
        self.progressBarUpdate.emit(1, self.save_steps_number, True)

    def save_step0(self):
        self.data["zipPath.sources_availability"] = "step0/sources_availability.json"
        self.data["zipPath.sources_temperature"] = "step0/sources_temperature.json"
        self.add_file(self.zip_manager.OBJECT,
                      self.step0.sources_availability,
                      "step0/sources_availability.json")
        self.add_file(self.zip_manager.OBJECT,
                      self.step0.sources_temperature,
                      "step0/sources_temperature.json")
        self.add_table_widget_to_saved_data(self.step0.sources_available)
        self.data["step0.folder"] = self.step0.folder.text()
        self.data["step0.layerPath"] = self.step0.layerPath.filePath()
        self.data["step0.layerPath1"] = self.step0.layerPath1.filePath()
        self.progressBarUpdate.emit(2, self.save_steps_number, True)

    def save_step_1(self, file):
        self.data["STEP_1"] = {}
        if self.work_folder is None:
            folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder"))
        else:
            folder = self.work_folder  # os.path.join(self.work_folder, "DefaultSaveFolder", file)
        self.data["STEP_1"]["checkBox"] = self.step1.checkBox.isChecked()
        self.data["STEP_1"]["checkBox_buildingSolution"] = self.step1.checkBox_buildingSolution.isChecked()
        self.data["STEP_1"]["checkBox_3"] = self.step1.checkBox_3.isChecked()
        self.data["STEP_1"]["checkBox_4"] = self.step1.checkBox_4.isChecked()
        self.data["STEP_1"]["networks_send"] = self.step1.networks_send
        self.data["STEP_1"]["autosave_done"] = self.step1.autosave_done
        self.add_list_widget_to_saved_data(self.step1.listWidget_4)
        self.add_list_widget_to_saved_data(self.step1.listNetworkDCN)
        self.add_tree_widget_to_saved_data(self.step1.dmmTreeNetwork)
        self.add_tree_widget_to_saved_data(self.step1.dmmTree)
        self.add_table_widget_to_saved_data(self.step1.sourcesTable)
        self.data["STEP_1"]["averegeGasoline"] = self.step1.averegeGasoline.value()
        self.data["STEP_1"]["averageCO2gasoline"] = self.step1.averageCO2gasoline.value()
        self.data["STEP_1"]["gasoline"] = self.step1.gasoline.value()
        self.data["STEP_1"]["averageDiesel"] = self.step1.averageDiesel.value()
        self.data["STEP_1"]["diesel"] = self.step1.diesel.value()
        self.data["STEP_1"]["averageCO2diesel"] = self.step1.averageCO2diesel.value()
        self.data["STEP_1"]["personalVehicles"] = self.step1.personalVehicles.value()
        self.data["STEP_1"]["gasolineVehicles"] = self.step1.gasolineVehicles.value()
        self.data["STEP_1"]["dailyDistance"] = self.step1.dailyDistance.value()
        self.data["STEP_1"]["electricVehicles"] = self.step1.electricVehicles.value()
        self.data["STEP_1"]["energyConsum"] = self.step1.energyConsum.value()
        self.data["STEP_1"]["co2ElectricalSector"] = self.step1.co2ElectricalSector.value()
        self.data["STEP_1"]["avarageBattery"] = self.step1.avarageBattery.value()
        self.data["STEP_1"]["avarageChargingDischarging"] = self.step1.avarageChargingDischarging.value()
        self.data["STEP_1"]["dieselVehicles"] = self.step1.dieselVehicles.value()
        self.data["STEP_1"]["weekend"] = self.step1.weekend.value()
        self.data["STEP_1"]["btnWinter"] = self.step1.btnWinter.value()
        self.data["STEP_1"]["btnSpring"] = self.step1.btnSpring.value()
        self.data["STEP_1"]["btnSummer"] = self.step1.btnSummer.value()
        self.data["STEP_1"]["btnAutumn"] = self.step1.btnAutumn.value()
        self.data["zipPath.KPIs_additional_data"] = "step1/KPIs_additional_data.json"
        self.add_file(self.zip_manager.OBJECT,
                      self.step1.KPIs_additional_data,
                      "step1/KPIs_additional_data.json")
        self.data["zipPath.baseline_networks"] = []
        for network_list in [self.step1.DCN_network_list, self.step1.DHN_network_list]:
            for network in network_list:
                if network.get_save_file_path() is None:
                    continue
                if os.path.isdir(os.path.dirname(network.get_save_file_path())):
                    self.data["zipPath.baseline_networks"].append(os.path.join("step1",
                                                                               network.n_type, str(network.get_ID())))
                    self.add_file(self.zip_manager.FOLDER, os.path.dirname(network.get_save_file_path()),
                                  os.path.join("step1", network.n_type, str(network.get_ID())))
                    zip_path = "step1/" + network.n_type + "/" + str(network.get_ID()) + ".json"
                    self.data["zipPath.network_infos." + str(network.get_ID())] = zip_path
                    self.add_file(self.zip_manager.OBJECT, network.export_network_data(), zip_path)
        tree_item_manager = TreeItemManager(self.step1.iface, self.step1.dmmTree, self.step1.dmmTreeNetwork,
                                            [self.step1.DCN_network_list, self.step1.DHN_network_list])
        self.data["zipPath.baseline_buildings_status"] = "step0/baseline_buildings_status.json"
        self.add_file(self.zip_manager.OBJECT,
                      tree_item_manager.get_building_status(),
                      "step0/baseline_buildings_status.json")
        self.progressBarUpdate.emit(3, self.save_steps_number, True)

    def save_step_2(self):
        self.data["STEP_2"] = {}
        self.add_table_widget_to_saved_data(self.step2.tableWidget_5)
        self.add_table_widget_to_saved_data(self.step2.tableWidget_2)
        self.add_table_widget_to_saved_data(self.step2.tableWidget_3)
        self.add_table_widget_to_saved_data(self.step2.tableWidget_4)
        self.data["zipPath.KPIs"] = "step2/KPIs.json"
        self.add_file(self.zip_manager.OBJECT,
                      self.step2.KPIs,
                      "step2/KPIs.json")
        self.progressBarUpdate.emit(4, self.save_steps_number, True)

    def save_step_3(self):
        self.add_table_widget_to_saved_data(self.step3.tableEnStep3)
        self.add_table_widget_to_saved_data(self.step3.tableENVStep3)
        self.add_table_widget_to_saved_data(self.step3.tableEcoStep3)
        self.add_table_widget_to_saved_data(self.step3.tableSoStep3)
        self.add_tree_widget_to_saved_data(self.step3.treeWidget)
        self.data["Weight"] = self.step3.weight_spin_box.value()
        self.add_list_widget_to_saved_data(self.step3.energy_criteria)
        self.add_list_widget_to_saved_data(self.step3.environmental_criteria)
        self.add_list_widget_to_saved_data(self.step3.economic_criteria)
        self.add_list_widget_to_saved_data(self.step3.social_criteria)
        self.add_table_widget_to_saved_data(self.step3.tableWidgetp)
        self.add_table_widget_to_saved_data(self.step3.tableWidget_2p)
        self.add_table_widget_to_saved_data(self.step3.tableWidget_3p)
        self.add_table_widget_to_saved_data(self.step3.tableWidget_4p)
        self.add_table_widget_to_saved_data(self.step3.tableWidget_5p)
        self.add_table_widget_to_saved_data(self.step3.tableVisKpiEn)
        self.add_table_widget_to_saved_data(self.step3.tableVisKpiEnv)
        self.add_table_widget_to_saved_data(self.step3.tableVisKpiEco)
        self.add_table_widget_to_saved_data(self.step3.tableVisKpiSo)
        self.data["zipPath.weights"] = "step3/weights.json"
        self.add_file(self.zip_manager.OBJECT,
                      self.step3.weights,
                      "step3/weights.json")
        self.progressBarUpdate.emit(5, self.save_steps_number, True)

    def save_step_4(self, file):
        self.data["STEP_4"] = {}
        if self.work_folder is None:
            folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder"))
        else:
            folder = self.work_folder  # os.path.join(self.work_folder, "DefaultSaveFolder", file)
        self.data["futureDistrictSolution"] = self.step4.futureDistrictSolution.isChecked()
        self.data["checkBox_buildingSolution_future"] = self.step4.futureBuildingSolution.isChecked()
        self.data["futureDHN"] = self.step4.futureDHN.isChecked()
        self.data["futureDCN"] = self.step4.futureDCN.isChecked()
        self.data["zipPath.KPIs_additional_data"] = "step4/KPIs_additional_data.json"
        self.add_file(self.zip_manager.OBJECT, self.step4.KPIs_additional_data,
                      self.data["zipPath.KPIs_additional_data"])
        self.add_list_widget_to_saved_data(self.step4.listWidget_future)
        self.add_list_widget_to_saved_data(self.step4.listNetworkDCN)
        self.add_table_widget_to_saved_data(self.step4.tableWidget_4f)
        self.add_tree_widget_to_saved_data(self.step4.futureDmmTreeNetwork)
        self.add_tree_widget_to_saved_data(self.step4.dmmTree_future)
        self.add_table_widget_to_saved_data(self.step4.suppliesTable_future)
        self.add_table_widget_to_saved_data(self.step4.tableWidget_3f)
        self.data["averegeGasoline_future"] = self.step4.averegeGasoline.value()
        self.data["averageCO2gasoline_future"] = self.step4.averageCO2gasoline.value()
        self.data["gasoline_future"] = self.step4.gasoline.value()
        self.data["averageDiesel_future"] = self.step4.averageDiesel.value()
        self.data["diesel_future"] = self.step4.diesel.value()
        self.data["averageCO2diesel_future"] = self.step4.averageCO2diesel.value()
        self.data["personalVehicles_future"] = self.step4.personalVehicles.value()
        self.data["gasolineVehicles_future"] = self.step4.gasolineVehicles.value()
        self.data["dailyDistance_future"] = self.step4.dailyDistance.value()
        self.data["electricVehicles_future"] = self.step4.electricVehicles.value()
        self.data["energyConsum_future"] = self.step4.energyConsum.value()
        self.data["co2ElectricalSector_future"] = self.step4.co2ElectricalSector.value()
        self.data["avarageBattery_future"] = self.step4.avarageBattery.value()
        self.data["avarageChargingDischarging_future"] = self.step4.avarageChargingDischarging.value()
        self.data["dieselVehicles_future"] = self.step4.dieselVehicles.value()
        self.data["weekend_future"] = self.step4.weekend.value()
        self.data["btnWinter_future"] = self.step4.btnWinter.value()
        self.data["btnSpring_future"] = self.step4.btnSpring.value()
        self.data["btnSummer_future"] = self.step4.btnSummer.value()
        self.data["btnAutumn_future"] = self.step4.btnAutumn.value()
        self.data["zipPath.future_networks"] = []
        for network_list in [self.step4.futureDHN_network_list, self.step4.futureDCN_network_list]:
            for network in network_list:
                if network.get_save_file_path() is None:
                    continue
                if os.path.isdir(os.path.dirname(network.get_save_file_path())):
                    self.data["zipPath.future_networks"].append(os.path.join("step4",
                                                                               network.n_type, str(network.get_ID())))
                    self.add_file(self.zip_manager.FOLDER, os.path.dirname(network.get_save_file_path()),
                                  os.path.join("step4", network.n_type, str(network.get_ID())))
                    zip_path = "step4/" + network.n_type + "/" + str(network.get_ID()) + ".json"
                    self.data["zipPath.network_infos." + str(network.get_ID())] = zip_path
                    self.add_file(self.zip_manager.OBJECT, network.export_network_data(), zip_path)
        tree_item_manager = TreeItemManager(self.step1.iface, self.step4.dmmTree_future, self.step4.futureDmmTreeNetwork,
                                            [self.step4.futureDCN_network_list, self.step4.futureDHN_network_list])
        self.data["zipPath.future_buildings_status"] = "step4/future_buildings_status.json"
        self.add_file(self.zip_manager.OBJECT,
                      tree_item_manager.get_building_status(),
                      "step4/future_buildings_status.json")
        self.progressBarUpdate.emit(6, self.save_steps_number, True)

    def save_simulation(self):
        self.data["zipPath.step5KPIs"] = "step5/KPIs.json"
        self.add_file(self.zip_manager.OBJECT,
                      self.simulation.KPIs,
                      "step5/KPIs.json")
        base_path = os.path.join(mp_config.CURRENT_PLANNING_DIRECTORY, "District", "KPIs", "Tjulia")
        julia_paths = {"single_building": os.path.join(base_path, "single_building", "Results"),
                       "district/heating": os.path.join(base_path, "district", "heating", "Results"),
                       "district/cooling": os.path.join(base_path, "district", "cooling", "Results")}
        for key in julia_paths.keys():
            try:
                if not os.path.isdir(julia_paths[key]):
                    continue
            except Exception:
                continue
            self.data["zipPath.julia_results." + key] = os.path.join("step5/julia", key)
            for folder_name, sub_folders, file_names in os.walk(julia_paths[key]):
                for filename in file_names:
                    if filename.startswith("Result_") and filename.endswith(".csv"):
                        self.add_file(self.zip_manager.FILE,
                                      os.path.join(folder_name, filename),
                                      os.path.join("step5/julia", key, filename))
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_10, name="tableWidget_10sim")
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_5, name="tableWidget_5sim")
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_6, name="tableWidget_6sim")
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_7, name="tableWidget_7sim")
        self.progressBarUpdate.emit(7, self.save_steps_number, True)
