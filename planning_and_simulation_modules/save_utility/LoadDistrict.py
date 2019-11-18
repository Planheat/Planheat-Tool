from .LoadScenario import LoadScenario
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject
import os
import os.path
from ..utility.easy_progress_bar import Actions
from ..utility.data_manager.DataTransfer import DataTransfer
from ..Network import Network
from PyQt5.QtCore import pyqtSignal
import time, datetime


def progress_bar(easy_progress_bar):
    while True: 
        value = (yield)
        easy_progress_bar.add_progress(value)


def set_progress_bar_label_text(easy_progress_bar):
    while True:
        text = (yield)
        easy_progress_bar.set_label(text)


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

    def __init__(self, folder=None):
        LoadScenario.__init__(self, folder)
        self.easy_progress_bar = None
        self.progress_label = None
        self.refreshing_combo_box = False

    def initialize(self):
        self.refresh_file_selection_combo_box()
        self.step0.pushButton_5.clicked.connect(self.run)
        self.step0.comboBox.currentTextChanged.connect(self.combo_box_changed)

    def combo_box_changed(self, text):
        if not self.refreshing_combo_box:
            file_path = self.file_manager.get_path_from_file_name(text, end_char=-5,
                                                                  search_folders=[self.file_manager.work_folder])
            if file_path is None:
                return
            info = os.stat(file_path).st_mtime
            year, month, day, hour, minute, second = time.localtime(info)[:-3]
            self.step0.input_file_description.setText(
                "Saved: %02d/%02d/%d %02d:%02d:%02d" % (day, month, year, hour,
                                                                minute, second))


    def refresh_file_selection_combo_box(self):
        self.refreshing_combo_box = True
        self.file_manager.import_and_fill_combo_box(self.step0.comboBox, ".json")
        self.refreshing_combo_box = False
        self.combo_box_changed(self.step0.comboBox.currentText())

    def run(self):
        if self.step0.comboBox.currentText() == " " or self.step0.comboBox.currentText() == "" or self.step0.comboBox.currentText() is None:
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
        if r == QMessageBox.Ok:

            easy_progress_bar = Actions()
            easy_progress_bar.label.setText("Retrieving saved data")
            easy_progress_bar.setWindowTitle('Loading...')
            easy_progress_bar.progress.setMinimum(0)
            easy_progress_bar.progress.setValue(0)
            easy_progress_bar.progress.setMaximum(22)
            self.easy_progress_bar = progress_bar(easy_progress_bar)
            self.easy_progress_bar.__next__()
            self.progress_label = set_progress_bar_label_text(easy_progress_bar)
            self.progress_label.__next__()
            self.easy_progress_bar.send(1)

            layer_removed = self.remove_unwanted_layers()
            if not layer_removed:
                self.easy_progress_bar.hide()
                return
            self.easy_progress_bar.send(1)
            file = self.step0.comboBox.currentText()
            self.load(file + ".json")
            load = self.step0.comboBox.currentText() + ".json"
            self.easy_progress_bar.send(1)
            result = self.load_general_state()
            if result:
                self.progress_label.send("Downloading streets from OSM... (step0)")
                result = self.load_step0()
            if result:
                self.progress_label.send("Loading baseline scenario (step1)")
                result = self.load_step1(file)
            if result:
                self.progress_label.send("Searching for saved KPIs (step2)")
                result = self.load_step2()
            if result:
                self.progress_label.send("Building planning criteria (step3)")
                result = self.load_step3()
            if result:
                self.progress_label.send("Loading future scenario (step4)")
                result = self.load_step4(file)

            self.progress_label.send("Done!")
            self.easy_progress_bar.send(1)
            try:
                self.easy_progress_bar.close()
            except GeneratorExit:
                pass
            try:
                self.progress_label.close()
            except GeneratorExit:
                pass
            easy_progress_bar.hide()
            easy_progress_bar.deleteLater()
            self.update_labels(load)
        self.finished.emit()

            # self.easy_progress_bar.hide()

    def load_step4(self, file):
        self.set_check_state(self.step4.futureDistrictSolution, self.get_data("futureDistrictSolution"))
        self.set_check_state(self.step4.futureBuildingSolution, self.get_data("futureBuildingSolution"))
        self.set_check_state(self.step4.futureDHN, self.get_data("futureDHN"))
        self.set_check_state(self.step4.futureDCN, self.get_data("futureDCN"))
        self.file_manager.copy_folder(os.path.join(self.folder, "Future", file, "Networks"),
                                      os.path.join(self.folder, "__unsaved_networks__", "Future"))
        self.step4.futureDHN_network_list = self.import_networks("future", "DHN")
        self.step4.refresh_DHN_network()
        self.step4.futureDCN_network_list = self.import_networks("future", "DCN")
        self.step4.refresh_DCN_network()
        self.easy_progress_bar.send(1)
        self.fill_tre_widget_item(self.step4.futureDmmTreeNetwork)
        self.easy_progress_bar.send(1)
        self.fill_table_widget_item(self.step4.suppliesTable_future)
        self.easy_progress_bar.send(1)
        self.fill_tre_widget_item(self.step4.dmmTree_future)
        self.easy_progress_bar.send(1)
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
        self.easy_progress_bar.send(1)
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
        self.step3.weights = self.get_data("prioritizzation weights")
        self.step3.refresh_vito_report()
        self.easy_progress_bar.send(1)
        if self.get_data("step4btn") is not None:
            if self.get_data("step4btn"):
                self.step3.oktargets.clicked.emit()
                self.dpmdialog.hide()
                return True
        return False

    def load_step2(self):
        self.step2.KPIs = self.get_data("KPIs")
        self.fill_table_widget_item(self.step2.tableWidget_5)
        self.fill_table_widget_item(self.step2.tableWidget_2)
        self.fill_table_widget_item(self.step2.tableWidget_3)
        self.fill_table_widget_item(self.step2.tableWidget_4)
        self.easy_progress_bar.send(1)
        if self.get_data("step3btn") is not None:
            if self.get_data("step3btn"):
                self.step2.okbtn.clicked.emit()
                self.dpmdialog.hide()
                return True
        return False

    def load_step1(self, file):
        self.set_check_state(self.step1.checkBox, self.get_data("checkBox"))
        self.set_check_state(self.step1.checkBox_buildingSolution, self.get_data("checkBox_buildingSolution"))
        self.set_check_state(self.step1.checkBox_3, self.get_data("checkBox_3"))
        self.set_check_state(self.step1.checkBox_4, self.get_data("checkBox_4"))
        # for n in self.import_networks("baseline", "DHN")
        #     self.step1.DHN_network_list.append(n)
        # self.step1.refresh_DHN_network()
        # for n in self.import_networks("baseline", "DCN"):
        #     self.step1.DCN_network_list.append(n)
        print("Mi copio le NETWORK!!! da", os.path.join(self.folder, "Baseline", file, "Networks"), "a",
              os.path.join(self.folder, "__unsaved_networks__", "Baseline"))
        self.file_manager.copy_folder(os.path.join(self.folder, "Baseline", file, "Networks"),
                                      os.path.join(self.folder, "__unsaved_networks__", "Baseline"))
        self.step1.DHN_network_list = self.import_networks("baseline", "DHN")
        self.step1.refresh_DHN_network()
        self.step1.DCN_network_list = self.import_networks("baseline", "DCN")
        self.step1.refresh_DCN_network()
        self.easy_progress_bar.send(1)
        self.step1.dmmTree.clear()
        self.fill_tre_widget_item(self.step1.dmmTree)
        self.easy_progress_bar.send(1)
        self.fill_table_widget_item(self.step1.sourcesTable)
        self.easy_progress_bar.send(1)
        self.fill_tre_widget_item(self.step1.dmmTreeNetwork)
        self.easy_progress_bar.send(1)
        self.fill_double_spin_box(self.step1.averegeGasoline, self.get_data("averegeGasoline"))
        self.fill_double_spin_box(self.step1.averageCO2gasoline, self.get_data("averageCO2gasoline"))
        self.fill_double_spin_box(self.step1.gasoline, self.get_data("gasoline"))
        self.fill_double_spin_box(self.step1.averageDiesel, self.get_data("averageDiesel"))
        self.fill_double_spin_box(self.step1.diesel, self.get_data("diesel"))
        self.fill_double_spin_box(self.step1.averageCO2diesel, self.get_data("averageCO2diesel"))
        self.fill_double_spin_box(self.step1.personalVehicles, self.get_data("personalVehicles"))
        self.fill_double_spin_box(self.step1.gasolineVehicles, self.get_data("gasolineVehicles"))
        self.fill_double_spin_box(self.step1.dailyDistance, self.get_data("dailyDistance"))
        self.fill_double_spin_box(self.step1.electricVehicles, self.get_data("electricVehicles"))
        self.fill_double_spin_box(self.step1.energyConsum, self.get_data("energyConsum"))
        self.fill_double_spin_box(self.step1.co2ElectricalSector, self.get_data("co2ElectricalSector"))
        self.fill_double_spin_box(self.step1.avarageBattery, self.get_data("avarageBattery"))
        self.fill_double_spin_box(self.step1.avarageChargingDischarging, self.get_data("avarageChargingDischarging"))
        self.fill_double_spin_box(self.step1.dieselVehicles, self.get_data("dieselVehicles"))
        self.fill_double_spin_box(self.step1.weekend, self.get_data("weekend"))
        self.fill_double_spin_box(self.step1.btnWinter, self.get_data("btnWinter"))
        self.fill_double_spin_box(self.step1.btnSpring, self.get_data("btnSpring"))
        self.fill_double_spin_box(self.step1.btnSummer, self.get_data("btnSummer"))
        self.fill_double_spin_box(self.step1.btnAutumn, self.get_data("btnAutumn"))
        self.easy_progress_bar.send(1)
        if self.get_data("step2btn") is not None:
            if self.get_data("step2btn"):
                self.step1.muted = True
                self.step1.save.clicked.emit()
                self.step1.muted = False
                self.dpmdialog.hide()
                return True
        return False

    def load_step0(self):
        self.line_edit_set_text(self.step0.layerPath, "baseline buildings")
        self.step0.load4.clicked.emit()
        self.step0.data_transfer = DataTransfer()
        layer = self.load_layer_from_shapefile(self.get_data("comboBox layer"))
        if layer is not None:
            for i in range(self.step0.comboLayer.count()):
                if layer.name() == self.step0.comboLayer.itemText(i):
                    self.step0.comboLayer.setCurrentIndex(i)
                    #self.step0.pushButton_4.clicked.emit()
                    break
        self.easy_progress_bar.send(3)
        self.easy_progress_bar.send(1)
        self.line_edit_set_text(self.step0.layerPath1, "future buildings")
        self.step0.load3.clicked.emit()
        self.easy_progress_bar.send(1)
        self.line_edit_set_text(self.step0.folder, "SMMfolder")
        # self.step0.load.clicked.emit()
        self.fill_table_widget_item(self.step0.sources_available)
        self.easy_progress_bar.send(1)
        if self.get_data("step1btn") is not None:
            if self.get_data("step1btn"):
                self.step0.ok.clicked.emit()
                self.dpmdialog.hide()
                return True
        return False

    def load_general_state(self):
        self.file_manager.remove_folder(os.path.join(self.folder, "__unsaved_networks__", "Baseline"))
        self.file_manager.remove_folder(os.path.join(self.folder, "__unsaved_networks__", "Future"))

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
        first_time_warning = True
        for child in root.children():
            if child.name() == "Shapefiles from SMM":
                continue
            if child.name() == "Raster layers from SMM":
                continue
            if child.name() == "OSM":
                continue
            if first_time_warning:
                first_time_warning = False
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                main_text = "Delete unsaved layers?"
                msgBox.setText(main_text)
                msgBox.setInformativeText(
                    "This procedure will discard all the unsaved QGIS layers. Be sure to save them before continue. Press Ok to continue, Cancel to abort the procedure.")
                msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msgBox.setDefaultButton(QMessageBox.Cancel)
                r = msgBox.exec()
                if not r == QMessageBox.Ok:
                    return False
            try:
                id_list = child.findLayerIds()
            except AttributeError:
                id_list = [child.layerId()]
            for layer_id in id_list:
                QgsProject.instance().removeMapLayer(layer_id)
            try:
                root.removeChildNode(child)
            except RuntimeError:
                pass
        return True

    def import_networks(self, scenario_type, n_type):
        if scenario_type == "baseline":
            m_scenario_type = "Baseline"
        else:
            m_scenario_type = "Future"

        n_list = []
        ids = self.get_data(n_type, self.data["networks"][scenario_type])
        if ids is None:
            return n_list

        for network_id in ids:
            folder = self.get_data("work_folder")
            # print("work_folder", folder)
            if folder is None:
                folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")
            # file = self.get_data("save_file_name")
            folder = os.path.join(folder, "__unsaved_networks__", m_scenario_type, "Networks", n_type)
            # print("folder", folder)
            if os.path.isdir(folder):
                network_folder_path = os.path.join(folder, network_id)
                # print("network_folder_path", network_folder_path)
                if os.path.isdir(network_folder_path):
                    # print("network_folder_path esiste")
                    for file in os.listdir(network_folder_path):
                        # print(file)
                        if file[-4:] == ".zip":
                            n = Network(name=file[0:-4], n_type=n_type)
                            n.save_file_path = os.path.join(network_folder_path, file)
                            n.ID = str(network_id)
                            n.scenario_type = scenario_type
                            root = QgsProject.instance().layerTreeRoot()
                            if not self.node_has_child_name(root, n.get_group_name()):
                                root.addGroup(n.get_group_name())
                            n_list.append(n)
                            break
        return n_list

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






# class C:
#     def __init__(self):
#         self.value_list = [1, 1]
#         self.value = 1
#
# def mod_value(o):
#     o = 2
#
# def mod_value_list(o):
#     o[1] = 2




