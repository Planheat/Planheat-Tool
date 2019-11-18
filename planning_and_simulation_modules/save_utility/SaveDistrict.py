from .SaveScenario import SaveScenario
from ..layer_utils import save_layer_to_shapefile
from PyQt5.QtWidgets import QMessageBox
import os.path
import os
from .. import master_planning_config as mp_config


class SaveDistrict(SaveScenario):
    dpmdialog = None
    district = None
    step0 = None
    step1 = None
    step2 = None
    step3 = None
    step4 = None
    simulation = None

    work_folder = None

    def __init__(self, folder=None):
        SaveScenario.__init__(self, folder)
        # self.progress_bar = Actions()
        # self.progress_bar.hide()
        # self.progress_bar.progress.setMinimum(0)

    def initialize(self):
        self.step0.save_plugin.clicked.connect(self.save_plugin_clicked)

    def save_plugin_clicked(self):
        print("Save plugin clicked")
        text = mp_config.CURRENT_PROJECT_NAME #self.file_manager.get_file_name_from_user(self.step0)
        if text is None:
            message = "File name is missing. No files produced."
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("Invalid file name.")
            msgBox.setInformativeText(message)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec()
        else:
            self.override_save_plugin_state(text)

    def override_save_plugin_state(self, file):
        self.save_general_state(file)
        self.save_step0(str(file))
        self.save_step_1(str(file))
        self.save_step_2()
        self.save_step_3()
        self.save_step_4(file)
        self.save_simulation()
        self.save(file + ".json")

    def save_general_state(self, file):
        if self.work_folder is None:
            folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder"))
        else:
            folder = self.work_folder  # os.path.join(self.work_folder, "DefaultSaveFolder", file)
        self.data["work_folder"] = folder
        self.data["save_file_name"] = file
        self.data["btnPlanning"] = self.district.btnPlanning.isEnabled()
        self.data["btnSimulation"] = self.district.btnSimulation.isEnabled()
        self.data["step0btn"] = self.dpmdialog.step0btn.isEnabled()
        self.data["step1btn"] = self.dpmdialog.step1btn.isEnabled()
        self.data["step2btn"] = self.dpmdialog.step2btn.isEnabled()
        self.data["step3btn"] = self.dpmdialog.step3btn.isEnabled()
        self.data["step4btn"] = self.dpmdialog.step4btn.isEnabled()

    def save_step0(self, file):
        self.data["baseline buildings"] = save_layer_to_shapefile(self.step1.building_layer,
                                                                  os.path.join(self.folder, "Baseline",
                                                                               file, "buildings.shp"))
        self.data["streets"] = save_layer_to_shapefile(self.step1.street_layer,
                                                       os.path.join(self.folder, "Baseline",
                                                                    file, "streets.shp"))
        self.data["future buildings"] = save_layer_to_shapefile(self.step0.future_scenario_layer,
                                                                os.path.join(self.folder, "Future",
                                                                             file, "buildings.shp"))
        self.data["comboBox layer"] = save_layer_to_shapefile(self.step0.combo_box_layer,
                                                              os.path.join(self.folder, "Tools", file, "shape.shp"))
        self.data["SMMfolder"] = self.step0.folder.text()
        # self.add_tree_widget_to_saved_data(self.step0.pmTree)
        # self.add_tree_widget_to_saved_data(self.step0.pmTree2)
        self.add_table_widget_to_saved_data(self.step0.sources_available)

    def save_step_1(self, file):
        if self.work_folder is None:
            folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder"))
        else:
            folder = self.work_folder  # os.path.join(self.work_folder, "DefaultSaveFolder", file)
        self.data["checkBox"] = self.step1.checkBox.isChecked()
        self.data["checkBox_buildingSolution"] = self.step1.checkBox_buildingSolution.isChecked()
        self.data["checkBox_3"] = self.step1.checkBox_3.isChecked()
        self.data["checkBox_4"] = self.step1.checkBox_4.isChecked()
        self.add_list_widget_to_saved_data(self.step1.listWidget_4)
        # self.add_list_widget_to_saved_data(self.step1.streetsListWidget)
        # self.add_list_widget_to_saved_data(self.step1.buildingListWidget)
        self.add_list_widget_to_saved_data(self.step1.listNetworkDCN)
        # self.add_list_widget_to_saved_data(self.step1.buildingListDCN)
        # self.add_list_widget_to_saved_data(self.step1.streetsListDCN)
        self.add_tree_widget_to_saved_data(self.step1.dmmTreeNetwork)
        self.add_tree_widget_to_saved_data(self.step1.dmmTree)
        self.add_table_widget_to_saved_data(self.step1.sourcesTable)
        self.data["averegeGasoline"] = self.step1.averegeGasoline.value()
        self.data["averageCO2gasoline"] = self.step1.averageCO2gasoline.value()
        self.data["gasoline"] = self.step1.gasoline.value()
        self.data["averageDiesel"] = self.step1.averageDiesel.value()
        self.data["diesel"] = self.step1.diesel.value()
        self.data["averageCO2diesel"] = self.step1.averageCO2diesel.value()
        self.data["personalVehicles"] = self.step1.personalVehicles.value()
        self.data["gasolineVehicles"] = self.step1.gasolineVehicles.value()
        self.data["dailyDistance"] = self.step1.dailyDistance.value()
        self.data["electricVehicles"] = self.step1.electricVehicles.value()
        self.data["energyConsum"] = self.step1.energyConsum.value()
        self.data["co2ElectricalSector"] = self.step1.co2ElectricalSector.value()
        self.data["avarageBattery"] = self.step1.avarageBattery.value()
        self.data["avarageChargingDischarging"] = self.step1.avarageChargingDischarging.value()
        self.data["dieselVehicles"] = self.step1.dieselVehicles.value()
        self.data["weekend"] = self.step1.weekend.value()
        self.data["btnWinter"] = self.step1.btnWinter.value()
        self.data["btnSpring"] = self.step1.btnSpring.value()
        self.data["btnSummer"] = self.step1.btnSummer.value()
        self.data["btnAutumn"] = self.step1.btnAutumn.value()
        self.data["networks"] = {}
        self.data["networks"]["baseline"] = {}
        self.data["networks"]["baseline"]["DHN"] = []
        self.data["networks"]["baseline"]["DCN"] = []
        for n in self.step1.DHN_network_list:
            self.data["networks"]["baseline"]["DHN"].append(n.get_ID())
        for n in self.step1.DCN_network_list:
            self.data["networks"]["baseline"]["DCN"].append(n.get_ID())
        self.file_manager.remove_folder(os.path.join(folder, "Baseline", file, "Networks"))
        self.file_manager.copy_folder(os.path.join(folder, "__unsaved_networks__", "Baseline", "Networks"),
                                      os.path.join(folder, "Baseline", file))

    def save_step_2(self):
        self.add_table_widget_to_saved_data(self.step2.tableWidget_5)
        self.add_table_widget_to_saved_data(self.step2.tableWidget_2)
        self.add_table_widget_to_saved_data(self.step2.tableWidget_3)
        self.add_table_widget_to_saved_data(self.step2.tableWidget_4)
        self.data["KPIs"] = self.step2.KPIs

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
        self.data["prioritizzation weights"] = self.step3.weights

    def save_step_4(self, file):
        if self.work_folder is None:
            folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder"))
        else:
            folder = self.work_folder  # os.path.join(self.work_folder, "DefaultSaveFolder", file)
        self.data["futureDistrictSolution"] = self.step4.futureDistrictSolution.isChecked()
        self.data["checkBox_buildingSolution_future"] = self.step4.futureBuildingSolution.isChecked()
        self.data["futureDHN"] = self.step4.futureDHN.isChecked()
        self.data["futureDCN"] = self.step4.futureDCN.isChecked()
        self.add_list_widget_to_saved_data(self.step4.listWidget_future)
        # self.add_list_widget_to_saved_data(self.step4.streetsListWidget_future)
        # self.add_list_widget_to_saved_data(self.step4.buildingListWidget_future)
        self.add_list_widget_to_saved_data(self.step4.listNetworkDCN)
        # self.add_list_widget_to_saved_data(self.step4.streetsListDCN_future)
        # self.add_list_widget_to_saved_data(self.step4.buildingListDCN)
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
        self.data["networks"]["future"] = {}
        self.data["networks"]["future"]["DHN"] = []
        self.data["networks"]["future"]["DCN"] = []
        for n in self.step4.futureDHN_network_list:
            self.data["networks"]["future"]["DHN"].append(n.get_ID())
        for n in self.step4.futureDCN_network_list:
            self.data["networks"]["future"]["DCN"].append(n.get_ID())
        self.file_manager.remove_folder(os.path.join(folder, "Future", file, "Networks"))
        self.file_manager.move_folder(os.path.join(folder, "__unsaved_networks__", "Future", "Networks"),
                                      os.path.join(folder, "Future", file))

    def save_simulation(self):
        self.data["KPIs"] = self.simulation.baseline_KPIs
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_10, name="tableWidget_10sim")
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_5, name="tableWidget_5sim")
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_6, name="tableWidget_6sim")
        self.add_table_widget_to_saved_data(self.simulation.tableWidget_7, name="tableWidget_7sim")
