import os
import os.path
# Import PyQt5
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QImage, QBrush, QColor
from PyQt5.QtWidgets import QTableWidgetItem, QTableWidget, QHeaderView

from .utility.filters.FECvisualizerService import FECvisualizerService

# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# Import the custom tree widget items
from .building.DPM import *
from .technology.Technology import *
from .utility.plots.PlotService import PlotService

from .Tjulia.Heat_pump_COP import generate_fileEta_forJulia
from .Tjulia.single_building.Dem_cool_heating import generafile
from .Tjulia.single_building.eta_cool_heat_pump import eta_cool_heat_pump
from .Tjulia.DistrictSimulator import DistrictSimulator
from .Tjulia.test.MyLog import MyLog
from .dialogSources import CheckSourceDialog
from .city.load_to_table import updata_dic
from .city.load_to_table import Qdialog_save_file

import logging
import sys

import shutil


from . import master_planning_config

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'districtSim.ui'))


class DistrictSimunation_Widget(QtWidgets.QDockWidget, FORM_CLASS):
    districtSimulation_closing_signal = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(DistrictSimunation_Widget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface

        self.logger = logging.getLogger(__name__)

        self.sources = CheckSourceDialog()

        self.target_input_table_en = None
        self.target_input_table_env = None
        self.target_input_table_eco = None
        self.target_input_table_so = None
        self.baseline_tech_tab = None
        self.baseline_network_tech_tab = None

        #self.btnExport.clicked.connect(self.export_table)

        self.pushButton.clicked.connect(self.run)
        self.pushButton.clicked.connect(self.grafico_for_district)
        self.pushButton.clicked.connect(self.grafico_for_individualSolution)
        self.progressBar.hide()
        self.label_3.hide()
        self.label_4.hide()
        self.step4 = None
        self.step0 = None
        self.step1 = None

        self.baseline_KPIs = {}
        self.KPIs = {}
        # key must be the table row
        self.EN_keys = { 1: "EN_1.1",
                         2: "EN_1.2",
                         3: "EN_1.3",
                         4: "EN_1.4",
                         5: "EN_1.5",
                         6: "EN_1.6",
                         7: "EN_1.7",
                         8: "EN_2.1",
                         9: "EN_2.2",
                         10: "EN_2.3",
                         11: "EN_2.4",
                         12: "EN_2.5",
                         13: "EN_2.7",
                         14: "EN_2.6",
                         15: "EN_3.1",
                         16: "EN_3.2",
                         17: "EN_3.3",
                         18: "EN_3.4",
                         19: "EN_3.5",
                         20: "EN_3.6",
                         21: "EN_3.7",
                         22: "EN_4.1",
                         23: "EN_4.2",
                         24: "EN_4.3",
                         25: "EN_4.4",
                         26: "EN_4.5",
                         27: "EN_5.1",
                         28: "EN_5.2",
                         29: "EN_5.3",
                         30: "EN_5.4",
                         31: "EN_5.5",
                         32: "EN_6.1",
                         33: "EN_6.2",
                         34: "EN_6.3",
                         35: "EN_6.4",
                         36: "EN_6.5",
                         37: "EN_7.1",
                         38: "EN_7.2",
                         39: "EN_7.3",
                         40: "EN_7.4",
                         41: "EN_7.5",
                         42: "EN_9.1",
                         43: "EN_9.2",
                         44: "EN_11.1",
                         45: "EN_11.2",
                         46: "EN_11.3",
                         47: "EN_12.1",
                         48: "EN_12.2",
                         49: "EN_12.3",
                         50: "EN_13.1",
                         51: "EN_13.2",
                         52: "EN_13.3",
                         53: "EN_13.1b",
                         54: "EN_13.2b",
                         55: "EN_13.3b",
                         56: "EN_14.2",
                         57: "EN_14.1",
                         58: "EN_14.3",
                         59: "EN_14.1b",
                         60: "EN_14.2b",
                         61: "EN_14.3b",
                         62: "EN_15.1",
                         63: "EN_15.2",
                         64: "EN_15.3"
                         }

        self.ENV_keys = {1: "ENV_1.3",
                         2: "ENV_1.4",
                         3: "ENV_1.5",
                         4: "ENV_1.6",
                         5: "ENV_1.1",
                         6: "ENV_1.2",
                         7: "ENV_2.1",
                         8: "ENV_2.2",
                         9: "ENV_2.3",
                         10: "ENV_2.4",
                         11: "ENV_2.5",
                         12: "ENV_2.6",
                         13: "ENV_2.7",
                         14: "ENV_2.8",
                         15: "ENV_2.9",
                         16: "ENV_2.10",
                         17: "ENV_2.11",
                         18: "ENV_2.12",
                         19: "ENV_2.13",
                         20: "ENV_2.14",
                         21: "ENV_2.15",
                         22: "ENV_2.16",
                         23: "ENV_2.17",
                         24: "ENV_2.18",
                         25: "ENV_3.1",
                         26: "ENV_3.2",
                         27: "ENV_3.3"}


        self.SO_keys = {1: "SO_3.1",
                        2: "SO_3.2",
                        3: "SO_3.3"}

        self.ECO_keys = {1: "ECO_1.1",
                         2: "ECO_1.2",
                         3: "ECO_1.3",
                         4: "ECO_1.4",
                         5: "ECO_2.1",
                         6: "ECO_2.2",
                         7: "ECO_2.3",
                         8: "ECO_3.1",
                         9: "ECO_4",
                         }

        for table in [self.tableWidget_10, self.tableWidget_5, self.tableWidget_6, self.tableWidget_7]:
            for i in range(1, table.rowCount()):
                widget_item = table.item(i, 0)
                if widget_item is not None:
                    table.item(i, 0).setBackground(QBrush(QColor(Qt.white)))
        self.set_tables_flag()

        self.tableWidget_10.setSpan(1, 0, 7, 1)
        self.tableWidget_10.setSpan(8, 0, 7, 1)
        self.tableWidget_10.setSpan(15, 0, 7, 1)
        self.tableWidget_10.setSpan(22, 0, 5, 1)
        self.tableWidget_10.setSpan(27, 0, 5, 1)
        self.tableWidget_10.setSpan(32, 0, 5, 1)
        self.tableWidget_10.setSpan(37, 0, 5, 1)
        self.tableWidget_10.setSpan(42, 0, 5, 1)
        self.tableWidget_10.setSpan(47, 0, 3, 1)
        self.tableWidget_10.setSpan(50, 0, 6, 1)
        self.tableWidget_10.setSpan(56, 0, 6, 1)
        # self.tableWidget_10.setSpan(57, 0, 2, 1)
        # self.tableWidget_10.setSpan(59, 0, 2, 1)
        self.tableWidget_5.setSpan(1, 0, 6, 1)
        self.tableWidget_5.setSpan(7, 0, 18, 1)
        self.tableWidget_5.setSpan(25, 0, 3, 1)
        self.tableWidget_6.setSpan(1, 0, 4, 1)
        self.tableWidget_6.setSpan(5, 0, 3, 1)
        self.tableWidget_6.setSpan(8, 0, 1, 1)
        self.tableWidget_6.setSpan(9, 0, 1, 1)
        self.tableWidget_7.setSpan(1, 0, 3, 1)
        self.tableWidget_7.setSpan(4, 0, 3, 1)
        self.tableWidget_7.setSpan(7, 0, 3, 1)

        self.simulator = None

        self.fec_visualizer_service = FECvisualizerService(self.output_table, self.fec_filter_combo_box,
                                                           self.description_filter_label)
        self.tabWidget_2.setCurrentIndex(0)
        self.plot_service = PlotService(os.path.join(master_planning_config.CURRENT_PLANNING_DIRECTORY,
                                        master_planning_config.DISTRICT_FOLDER,
                                        master_planning_config.KPIS_FOLDER, "Tjulia"), self)
        self.district_min_spinBox.valueChanged.connect(self.plot_service.plot_district)
        self.district_max_spinBox.valueChanged.connect(self.plot_service.plot_district)
        self.building_min_spinBox.valueChanged.connect(self.plot_service.plot_buildings)
        self.building_max_spinBox.valueChanged.connect(self.plot_service.plot_buildings)

    def run(self):
        max_progress = 0
        max_progress = max_progress + (
                    len(self.step4.futureDHN_network_list) + len(self.step4.futureDCN_network_list)) * 4
        try:
            for _ in self.step4.future_scenario.getFeatures():
                max_progress = max_progress + 1
        except AttributeError:
            pass
        self.progressBar.setMaximum(max_progress)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.label_3.setText("Starting computation...")
        self.label_4.setText("...")
        self.label_3.show()
        self.label_4.show()

        self.set_up_logger()

        kpis_folder = os.path.join(master_planning_config.CURRENT_PLANNING_DIRECTORY, 
                                   master_planning_config.DISTRICT_FOLDER,
                                   master_planning_config.KPIS_FOLDER)

        old_dr = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tjulia", "district", "heating")
        dr = os.path.join(kpis_folder, "Tjulia", "district", "heating")
        os.makedirs(dr, exist_ok=True)
        for f in os.listdir(old_dr):
            if f.endswith(".csv"):
                shutil.copy2(os.path.join(old_dr, f), os.path.join(dr, f))
        self.remove_files(os.path.join(dr, "Results"), "Result")
        #dr_sim = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tjulia", "district")
        dr_sim = os.path.join(kpis_folder, "Tjulia", "district")

        self.label_3.setText("Setting up simulator for district solution...")

        self.simulator = DistrictSimulator()

        self.set_up_simulator()

        self.simulator.run_district(dr_sim)

        #dr = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tjulia", "single_building")
        dr = os.path.join(kpis_folder, "Tjulia", "single_building")

        self.remove_files(os.path.join(dr, "Results"), "Result")
        self.label_3.setText("Single building solution pre-processing...")

        # ==> [PlanHeatProjectName]_hourly.csv
        # DEM_cool_time.csv
        # DEM_time.csv
        # DEM_DHW_time.csv
        cinput = os.path.join(  master_planning_config.CURRENT_MAPPING_DIRECTORY,
                                master_planning_config.DMM_FOLDER,
                                master_planning_config.DMM_PREFIX+master_planning_config.DMM_FUTURE_HOURLY_SUFFIX+".csv")
        n, buildings = generafile(self.step4.dmmTree_future, cinput=cinput, coutput=os.path.join(dr, "input"))
        my_log = MyLog(os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tjulia", "test",
                                    "log", "future_building_simulation.txt"))
        self.simulator.run_buildings(buildings, dr, log=my_log)
        self.label_3.setText("KPIs calculation...")
        KPIs = self.simulator.close_simulation(self.baseline_KPIs)
        self.KPIs = KPIs
        # print("districtSimulation.run() self.baseline_KPIs is KPIs: ", self.baseline_KPIs is KPIs)
        # for key in self.baseline_KPIs.keys():
        #     try:
        #         if self.baseline_KPIs[key] is KPIs[key]:
            #             print("districtSimulation.run() keys check TRUE: ", key)
                    #     except:
        #         pass
        # print("districtSimulation.run() self.baseline_KPIs is self.KPIs: ", self.baseline_KPIs is self.KPIs)
        # print("districtSimulation.run() self.KPIs is KPIs: ", self.KPIs is KPIs)
        self.fec_visualizer_service.set_KPIs(KPIs)
        self.label_3.setText("DONE!")
        self.fill_table(KPIs)
        self.progressBar.hide()
        self.label_4.hide()
        self.label_3.hide()
        self.finish_simulation()
        print(KPIs)
        print("KPIs DONE!")

    def set_up_simulator(self):
        self.simulator.DHN_network_list = self.step4.futureDHN_network_list
        self.simulator.DCN_network_list = self.step4.futureDCN_network_list
        # print('!!!', self.step4.suppliesTable_future)
        self.simulator.sources_tab = self.step4.suppliesTable_future
        self.simulator.ef_sources_tab = self.step4.suppliesTable_future
        self.simulator.sources = self.sources
        self.simulator.step1_network_tree_widget = None
        self.simulator.step1_building_tree_widget = None
        self.simulator.step0_district_sources_tab = self.step0.sources_available
        self.simulator.step4_network_tree_widget = self.step4.futureDmmTreeNetwork
        self.simulator.step4_building_tree_widget = self.step4.dmmTree_future

        self.simulator.logger = self.logger
        self.simulator.progress_bar = self.progressBar
        self.simulator.progress_label = self.label_3
        self.simulator.progess_time = self.label_4

        self.simulator.baseline_scenario = None
        self.simulator.future_scenario = self.step4.future_scenario

        self.simulator.heat = self.step0.sources_availability
        self.simulator.temperature = self.step0.sources_temperature

        self.simulator.KPIs_additional_data = self.step4.KPIs_additional_data
        self.simulator.baseline_KPIs = self.baseline_KPIs

        self.simulator.baseline_tech_tab = self.baseline_tech_tab
        self.simulator.baseline_tech_tab2 = self.step1.dmmTree
        self.simulator.baseline_network_tech_tab = self.baseline_network_tech_tab
        self.simulator.future_tech_tab = self.step4.dmmTree_future
        self.simulator.future_network_tech_tab = self.step4.futureDmmTreeNetwork

        self.simulator.set_up_new_simulation()


    def closeEvent(self, event):
        self.closedistrictSim()
        event.accept()

    def closedistrictSim(self):
        self.hide()
        self.districtSimulation_closing_signal.emit()

    def receive_KPIs(self, KPIs):
        self.baseline_KPIs = KPIs
        print("districtSimulation.receive_KPIs(): self.baseline_KPIs", self.baseline_KPIs)
        self.fill_table(self.baseline_KPIs)
        self.fec_visualizer_service.set_KPIs(self.baseline_KPIs)

    def fill_table(self, KPIs):
        EN_baseline_rows = [1, 2, 8, 9, 15, 16, 22, 23, 27, 28, 32, 33, 37, 38, 42, 44, 45, 47, 50, 53, 57, 59, 62]
        ENV_baseline_rows = [1, 2, 7, 8, 13, 14, 19, 20, 25]
        SO_baseline_row = [1, 7]
        ECO_baseline_row = [5]

        for key in self.EN_keys.keys():
            if key not in EN_baseline_rows:
                try:
                    self.tableWidget_10.setItem(key, 9, QTableWidgetItem(str(KPIs[self.EN_keys[key]])))
                    self.tableWidget_10.setItem(key, 8, QTableWidgetItem(str(KPIs[self.EN_keys[key]+"T"])))
                    self.tableWidget_10.setItem(key, 7, QTableWidgetItem(str(KPIs[self.EN_keys[key]+"R"])))
                except:
                    # print("districtSimulator.py, fill_table, tableWidget_10 (future KPIs): exception. Ignoring it.")
                    pass
            else:
                try:
                    self.tableWidget_10.setItem(key, 5, QTableWidgetItem(str(KPIs[self.EN_keys[key]])))
                    self.tableWidget_10.setItem(key, 4, QTableWidgetItem(str(KPIs[self.EN_keys[key]+"T"])))
                    self.tableWidget_10.setItem(key, 3, QTableWidgetItem(str(KPIs[self.EN_keys[key]+"R"])))

                except:
                    # print("districtSimulator.py, fill_table, tableWidget_10 (baseline KPIs): exception. Ignoring it.")
                    pass

        for key in self.ENV_keys.keys():
            if key not in ENV_baseline_rows:
                try:
                    self.tableWidget_5.setItem(key, 9, QTableWidgetItem(str(KPIs[self.ENV_keys[key]])))
                    self.tableWidget_5.setItem(key, 8, QTableWidgetItem(str(KPIs[self.ENV_keys[key]+"T"])))
                    self.tableWidget_5.setItem(key, 7, QTableWidgetItem(str(KPIs[self.ENV_keys[key]+"R"])))
                except:
                    # print("districtSimulator.py, fill_table, tableWidget_5 (future KPIs): exception. Ignoring it.")
                    pass
            else:
                try:
                    self.tableWidget_5.setItem(key, 5, QTableWidgetItem(str(KPIs[self.ENV_keys[key]])))
                    self.tableWidget_5.setItem(key, 4, QTableWidgetItem(str(KPIs[self.ENV_keys[key]+"T"])))
                    self.tableWidget_5.setItem(key, 3, QTableWidgetItem(str(KPIs[self.ENV_keys[key]+"R"])))
                except:
                    # print("districtSimulator.py, fill_table, tableWidget_5 (baseline KPIs): exception. Ignoring it.")
                    pass

        for key in self.SO_keys.keys():
            if key not in SO_baseline_row:
                try:
                    self.tableWidget_7.setItem(key, 9, QTableWidgetItem(str(KPIs[self.SO_keys[key]])))
                    self.tableWidget_7.setItem(key, 8, QTableWidgetItem(str(KPIs[self.SO_keys[key] + "T"])))
                    self.tableWidget_7.setItem(key, 7, QTableWidgetItem(str(KPIs[self.SO_keys[key] + "R"])))
                except:
                    # print("districtSimulator.py, fill_table, tableWidget_7(future KPIs): exception. Ignoring it.")
                    pass
            else:
                try:
                    self.tableWidget_7.setItem(key, 5, QTableWidgetItem(str(KPIs[self.SO_keys[key]])))
                    self.tableWidget_7.setItem(key, 4, QTableWidgetItem(str(KPIs[self.SO_keys[key] + "T"])))
                    self.tableWidget_7.setItem(key, 3, QTableWidgetItem(str(KPIs[self.SO_keys[key] + "R"])))
                except:
                    # print(
                    #     "districtSimulator.py, fill_table, tableWidget_7 (baseline KPIs): exception. Ignoring it.")
                    pass

        for key in self.ECO_keys.keys():
            if key not in ECO_baseline_row:
                try:
                    self.tableWidget_6.setItem(key, 9, QTableWidgetItem(str(KPIs[self.ECO_keys[key]])))
                    self.tableWidget_6.setItem(key, 8, QTableWidgetItem(str(KPIs[self.ECO_keys[key] + "T"])))
                    self.tableWidget_6.setItem(key, 7, QTableWidgetItem(str(KPIs[self.ECO_keys[key] + "R"])))
                except:
                    # print("districtSimulator.py, fill_table, tableWidget_6 (future KPIs): exception. Ignoring it.")
                    pass
            else:
                try:
                    self.tableWidget_6.setItem(key, 5, QTableWidgetItem(str(KPIs[self.ECO_keys[key]])))
                    self.tableWidget_6.setItem(key, 4, QTableWidgetItem(str(KPIs[self.ECO_keys[key] + "T"])))
                    self.tableWidget_6.setItem(key, 3, QTableWidgetItem(str(KPIs[self.ECO_keys[key] + "R"])))
                except:
                    # print(
                    #     "districtSimulator.py, fill_table, tableWidget_6 (baseline KPIs): exception. Ignoring it.")
                    pass

        for table in [self.tableWidget_10, self.tableWidget_5, self.tableWidget_6, self.tableWidget_7]:
            for i in range(table.columnCount()):
                for j in range(table.rowCount()):
                    try:
                        self.tableWidget_10.item(i, j).setFlags(QtCore.Qt.ItemIsEnabled)
                    except:
                        pass
        self.check_targets()
        self.tableWidget_10.hideRow(8)
        self.tableWidget_10.hideRow(9)
        self.tableWidget_10.hideRow(10)
        self.tableWidget_10.hideRow(11)
        self.tableWidget_10.hideRow(12)
        self.tableWidget_10.hideRow(13)
        self.tableWidget_10.hideRow(14)
        self.tableWidget_10.hideRow(53)
        self.tableWidget_10.hideRow(54)
        self.tableWidget_10.hideRow(55)
        self.tableWidget_10.hideRow(59)
        self.tableWidget_10.hideRow(60)
        self.tableWidget_10.hideRow(61)
        self.tableWidget_10.hideRow(62)
        self.tableWidget_10.hideRow(63)
        self.tableWidget_10.hideRow(64)

        for table in [self.tableWidget_10, self.tableWidget_5, self.tableWidget_6, self.tableWidget_7]:
            header = table.horizontalHeader()
            for i in range(9):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def remove_files(self, dr, start):
        if not os.path.isdir(dr):
            os.makedirs(dr, exist_ok=True)
        for f in os.listdir(dr):
            fn = os.fsdecode(f)
            if fn.startswith(start):
                self.label_3.setText("Deleting file: " + str(os.path.join(dr, fn)))
                os.remove(os.path.join(dr, fn))

    def set_up_logger(self):
        class Printer:
            def write(self, x):
                print(x)

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        output_stream = sys.stdout if sys.stdout is not None else Printer()
        stream_handler = logging.StreamHandler(output_stream)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(stream_handler)

    def target_update(self):
        for tables in [[self.target_input_table_en, self.tableWidget_10],
                       [self.target_input_table_env, self.tableWidget_5],
                       [self.target_input_table_eco, self.tableWidget_6],
                       [self.target_input_table_so, self.tableWidget_7]]:
            for i in range(tables[0].rowCount()):
                try:
                    widget_item_input = tables[0].item(i,6)
                except:
                    continue
                if widget_item_input is not None:
                    input_text = widget_item_input.text()
                    widget_item_output = tables[1].item(i, 6)
                    if widget_item_output is not None:
                        widget_item_output.setText(input_text)
                    else:
                        tables[1].setItem(i, 6, widget_item_input.clone())
        self.check_targets()

    def check_targets(self):
        for table in [self.tableWidget_10, self.tableWidget_5, self.tableWidget_6, self.tableWidget_7]:
            for i in range(table.rowCount()):
                target = table.item(i, 6)
                if target is None:
                    continue
                check_result = False
                try:
                    target_val = float(target.text())
                except (ValueError, AttributeError) as e:
                    target_val = None
                future_scenario = table.item(i, 9)
                try:
                    future_scenario_val = float(future_scenario.text())
                except (ValueError, AttributeError) as e:
                    future_scenario_val = None
                if future_scenario_val is not None and target_val is not None:
                    if abs(target_val) < abs(future_scenario_val):
                        check_result = True
                if not check_result:
                    target.setForeground(QBrush(QColor(Qt.red)))
                else:
                    target.setForeground(QBrush(QColor(Qt.blue)))

    def grafico_for_district(self, i=0):
        self.plot_service.plot_district()

    def grafico_for_individualSolution(self):
        self.plot_service.plot_buildings()

    def export_table(self, work_folder = None):
        if work_folder is None:
            folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "save_utility" ,"DefaultSaveFolder")
        else:
            folder = os.path.join(work_folder, "KPIs")
        os.makedirs(folder, exist_ok=True)
        name = Qdialog_save_file(folder)
        if not name.endswith(".csv"):
            name = name + ".csv"
        print("Output csv file saved at : '{0}'".format(name))
        self.saveToFile(name)


    def saveToFile(self, filename):
        self.data = {}
        self.crea_dic(self.tableWidget_10, filename)
        updata_dic(self.tableWidget_5, filename)
        updata_dic(self.tableWidget_6, filename)
        updata_dic(self.tableWidget_7, filename)



    def crea_dic(self, table, filename):
        self.data={}
        for i in range(table.columnCount()):
             item_val = []
             for j in range(table.rowCount()):
                 it = table.item(j, i)
                 item_val.append(it.text() if it is not None else "")
             h_item = table.horizontalHeaderItem(i)
             n_column = str(i) if h_item is None else h_item.text()
             self.data[n_column + "_" + table.objectName()] = item_val

        with open(filename,'w') as filename:
            for key in self.data.keys():
                filename.write("%s,%s\n" % (key, self.data[key]))

    def check_sources_frombaseline(self, tab_sources_base):
        table_sim=self.tableCheck
        table_sim.clear()
        header = ['Source', 'Availability [MWh/y]', 'Final energy consumption']
        self.table_sim.setHorizontalHeaderLabels(header)

        source = tab_sources_base

        for i in range(source.rowCount()):
            item = table_sim.item(i, 0)
            try:
                table_sim.setItem(i, col_dest, QTableWidgetItem(item))
            except:
                pass

    def finish_simulation(self):
        fec = self.fec_visualizer_service.get_fec_fut()
        sources = self.fec_visualizer_service.get_sources()
        print("districtSimulation.finish_simulation():", fec)
        self.tableWidget.setRowCount(len(sources))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Source", "Availability [MWh/y]", "Simulation [MWh/y]"])

        index = 0
        for k, source in enumerate(sources):
            old_value = "-"
            for i in range(self.step0.sources_available.rowCount()):
                if self.step0.sources_available.item(i, 0).text() == source:
                    old_value = self.step0.sources_available.item(i, 1).text()
                    self.tableWidget.setItem(index, 0, QTableWidgetItem(source))
                    self.tableWidget.setItem(index, 1, QTableWidgetItem(old_value))
                    self.tableWidget.setItem(index, 2, QTableWidgetItem(str(fec[k])))
                    index += 1
                    break
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)


        for i in range(self.tableWidget.rowCount()):
            try:
                if float(self.tableWidget.item(i, 1).text()) < float(self.tableWidget.item(i, 2).text()):
                    self.tableWidget.item(i, 1).setForeground(QColor(255, 0, 0))
                    self.tableWidget.item(i, 2).setForeground(QColor(255, 0, 0))
                    # icon = QIcon()
                    # icon_path = os.path.join(self.file_manager.city_plugin_folder, "../", "images",
                    #                          "green_check.png")
                    # icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
                    # total_percent.setIcon(icon)
                else:
                    self.tableWidget.item(i, 1).setForeground(QColor(0, 0, 255))
                    self.tableWidget.item(i, 2).setForeground(QColor(0, 0, 255))
                    # icon = QIcon()
                    # icon_path = os.path.join(self.file_manager.city_plugin_folder, "../", "images",
                    #                          "red_cross.png")
                    # icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
                    # total_percent.setIcon(icon)
            except:
                pass

    def set_table_not_editable(self, table):
        if not isinstance(table, QTableWidget):
            return
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                try:
                    table.item(i, j,).setFlags(Qt.ItemIsEnabled)
                except AttributeError:
                    table.setItem(i, j, QTableWidgetItem())
                    table.item(i, j, ).setFlags(Qt.ItemIsEnabled)

    def set_tables_flag(self):
        self.set_table_not_editable(self.tableWidget_7)
        self.set_table_not_editable(self.tableWidget_6)
        self.set_table_not_editable(self.tableWidget_5)
        self.set_table_not_editable(self.tableWidget_10)
        self.set_table_not_editable(self.tableWidget)

