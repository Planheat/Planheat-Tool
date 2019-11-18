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
from .building.Building import *
from .building.DPM import *
from .technology.Technology import *
from .Network import Network
from .utility.plots.PlotService import PlotService

from .Tjulia.Heat_pump_COP import generate_fileEta_forJulia
from .Tjulia.Solar_thermal_production import generate_solar_thermal_forJulia
from .Tjulia.single_building.Dem_cool_heating import generafile
from .Tjulia.single_building.eta_cool_heat_pump import eta_cool_heat_pump
from .Tjulia.district.heating.Waste_heat_heat_pumps_heating import generate_file_Waste_heat_pump_heating
from .Tjulia.district.cooling.Waste_heat_heat_pumps_cooling import generate_file_Waste_heat_pump_cooling
from .Tjulia.Solar_thermal_production import generate_solar_thermal_forJulia
from .Tjulia.DistrictSimulator import DistrictSimulator
from .dialogSources import CheckSourceDialog
from .city.load_to_table import updata_dic
from .city.load_to_table import Qdialog_save_file


from .utility.data_manager.PlanningCriteriaTransfer import PlanningCriteriaTransfer

import requests
import logging
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.figure import Figure
import csv
import sip
import pandas as pd
import shutil

from .layer_utils import load_file_as_layer, load_open_street_maps

from . import master_planning_config

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'districtSim.ui'))


class DistrictSimunation_Widget(QtWidgets.QDockWidget, FORM_CLASS):
    districtSimulation_closing_signal = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(DistrictSimunation_Widget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.logger = logging.getLogger(__name__)

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

        self.baseline_KPIs = {}
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

        self.sources = CheckSourceDialog()

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

        self.label_3.setText("District Heating Networks pre-processing...")
        if len(self.step4.futureDHN_network_list) > 0:

            self.district_heating_preprocessing(dr_sim)
        self.label_3.setText("District Cooling Networks pre-processing...")
        if len(self.step4.futureDCN_network_list) > 0:

            self.district_cooling_preprocessing(dr_sim)

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
        n, buildings = generafile(cinput=cinput, coutput=os.path.join(dr, "input"))
        self.single_building_common_precalculation(dr)
        self.simulator.run_buildings(buildings, dr)
        self.label_3.setText("KPIs calculation...")
        KPIs = self.simulator.close_simulation(self.baseline_KPIs)
        self.fec_visualizer_service.set_KPIs(KPIs)
        self.label_3.setText("DONE!")
        self.fill_table(KPIs)
        self.progressBar.hide()
        self.label_4.hide()
        self.label_3.hide()
        self.finish_simulation()
        print("KPIs DONE!")
        print(KPIs)

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


        self.simulator.KPIs_additional_data = self.step4.KPIs_additional_data
        self.simulator.baseline_KPIs = self.baseline_KPIs

        self.simulator.baseline_tech_tab = self.baseline_tech_tab
        self.simulator.baseline_network_tech_tab = self.baseline_network_tech_tab
        self.simulator.future_tech_tab = self.step4.dmmTree_future
        self.simulator.future_network_tech_tab = self.step4.futureDmmTreeNetwork

        self.simulator.set_up_new_simulation()

    def district_cooling_preprocessing(self, dr):

        # Global_solar_irradiation.csv
        # Global_solar_irradiation_2.csv
        # Global_solar_irradiation_seasonal.csv
        # Outside_temperature.csv
        # default (Antwerp): lat=51, lon=4, startyear=2015, endyear=2015, peakpower=3, loss=0, angle=0
        self.download_data_from_PVGIS(dr=dr)

        # ==> Outside_temperature.csv
        # eta_HP_1.csv
        # eta_HP_2.csv
        # eta_HP_3.csv
        generate_fileEta_forJulia(None, input_folder=dr, output_folder=os.path.join(dr, "cooling", "input"))

        # ==> Available_waste_heat_heat_pump_source_group_1.csv
        # ==> Available_waste_heat_heat_pump_source_group_2.csv
        # ==> Available_waste_heat_heat_pump_source_group_3.csv
        # ==> COP_heat_pump_temperature_group_1.csv
        # ==> COP_heat_pump_temperature_group_2.csv
        # ==> COP_heat_pump_temperature_group_3.csv
        # Waste_heat_heat_pump_available_temperature_group_1.csv
        # Waste_heat_heat_pump_available_temperature_group_2.csv
        # Waste_heat_heat_pump_available_temperature_group_3.csv
        #generate_file_Waste_heat_pump_cooling(input_folder=dr, output_folder=os.path.join(dr, "cooling", "input"))

    def district_heating_preprocessing(self, dr):
        # Global_solar_irradiation.csv
        # Global_solar_irradiation_2.csv
        # Global_solar_irradiation_seasonal.csv
        # Outside_temperature.csv
        # default (Antwerp): lat=51, lon=4, startyear=2015, endyear=2015, peakpower=3, loss=0, angle=0
        self.download_data_from_PVGIS(dr=dr)

        # ==> Outside_temperature.csv
        # eta_HP_1.csv
        # eta_HP_2.csv
        # eta_HP_3.csv
        generate_fileEta_forJulia(None, input_folder=dr, output_folder=os.path.join(dr, "heating", "input"))

        # ==> Global_solar_irradiation.csv
        # ==> Global_solar_irradiation_2.csv
        # ==> Global_solar_irradiation_seasonal.csv
        # ==> Outside_temperature.csv
        # ST_specific_time_seasonal.csv
        # ST_specific_time_2.csv
        # ST_specific_time.csv
        generate_solar_thermal_forJulia(None, input_folder=dr, output_folder=os.path.join(dr, "heating", "input"))

        # ==> Available_waste_heat_heat_pump_source_group_1.csv
        # ==> Available_waste_heat_heat_pump_source_group_2.csv
        # ==> Available_waste_heat_heat_pump_source_group_3.csv
        # ==> Available_waste_heat_heat_pump_source_group_seasonal.csv
        # ==> Available_waste_heat_heat_pump_absorption.csv
        # ==> COP_heat_pump_temperature_group_1.csv
        # ==> COP_heat_pump_temperature_group_2.csv
        # ==> COP_heat_pump_temperature_group_3.csv
        # ==> COP_heat_pump_temperature_group_seasonal.csv
        # Waste_heat_heat_pump_available_temperature_group_1.csv
        # Waste_heat_heat_pump_available_temperature_group_2.csv
        # Waste_heat_heat_pump_available_temperature_group_3.csv
        # Waste_heat_heat_pump_available_temperature_group_seasonal.csv
        # Waste_heat_heat_pump_available_absorption.csv
        #generate_file_Waste_heat_pump_heating(input_folder=dr, output_folder=os.path.join(dr, "heating", "input"))

    def single_building_preprocessing(self, j, dr, building_id):
        expr = QgsExpression("BuildingID=" + building_id)
        if self.baseline_scenario is None:
            print("Step2_dockwidget, KPIs_baselineScenario: baseline_scenario is not defined")
            return
        fs = [ft for ft in self.baseline_scenario.getFeatures(QgsFeatureRequest(expr))]

        if len(fs) > 0:
            feature_0 = fs[0]
        else:
            print("FALLITO MALE", building_id)
            return

        item = self.get_widget_item_from_feature(feature_0)
        if item is None:
            print("Step2_dockwidget, single_building_simulation: cannot find feature",
                  feature_0.id(), "building", building_id)
            return None
        tech_infos = self.create_base_tech_infos()

        self.update_tech_from_widget_item(tech_infos, item)

        input_folder = os.path.join(dr, "input")
        output_folder = os.path.join(dr, "Results")

        j.individual_H_and_C(input_folder, output_folder, tech_infos, building_id, self.logger.info)
        return item

    def single_building_common_precalculation(self, dr):
        # Global_solar_irradiation.csv
        # Global_solar_irradiation_2.csv
        # Global_solar_irradiation_seasonal.csv
        # Outside_temperature.csv
        # default (Antwerp): lat=51, lon=4, startyear=2015, endyear=2015, peakpower=3, loss=0, angle=0
        self.download_data_from_PVGIS(dr=dr)

        # ==> Outside_temperature.csv
        # eta_HP_1.csv
        # eta_HP_2.csv
        # eta_HP_3.csv
        generate_fileEta_forJulia(None, input_folder=dr, output_folder=os.path.join(dr, "input"))

        # ==> Outside_temperature.csv
        # eta_HP_cool.csv
        # eta_HP_cool_2.csv
        eta_cool_heat_pump(input_folder=dr, output_folder=os.path.join(dr, "input"))

        # ==> Global_solar_irradiation.csv
        # ==> Global_solar_irradiation_2.csv
        # ==> Global_solar_irradiation_seasonal.csv
        # ==> Outside_temperature.csv
        # ST_specific_time_seasonal.csv
        # ST_specific_time_2.csv
        # ST_specific_time.csv
        generate_solar_thermal_forJulia(None, input_folder=dr, output_folder=os.path.join(dr, "input"))

    def closeEvent(self, event):
        self.closedistrictSim()
        event.accept()

    def closedistrictSim(self):
        self.hide()
        self.districtSimulation_closing_signal.emit()

    def receive_KPIs(self, KPIs):
        self.baseline_KPIs = KPIs
        print(self.baseline_KPIs)
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

    def PVGIS_url_gen(self, lat=51, lon=4, startyear=2015, endyear=2015, peakpower=3, loss=0, angle=0):
        # for documentation refer to http://re.jrc.ec.europa.eu/pvg_static/web_service.html#HR

        url_PVGIS = 'http://re.jrc.ec.europa.eu/pvgis5/seriescalc.php?'
        url_PVGIS = url_PVGIS + "lat=" + str(lat)
        url_PVGIS = url_PVGIS + "&lon=" + str(lon)
        url_PVGIS = url_PVGIS + "&startyear=" + str(startyear)
        url_PVGIS = url_PVGIS + "&endyear=" + str(endyear)
        url_PVGIS = url_PVGIS + "&peakpower=" + str(peakpower)
        url_PVGIS = url_PVGIS + "&loss=" + str(loss)
        url_PVGIS = url_PVGIS + "&angle=" + str(angle)

        return url_PVGIS

    def download_data_from_PVGIS(self, dr, lat=51, lon=4, startyear=2015, endyear=2015, peakpower=3, loss=0, angle=0):
        url_PVGIS = self.PVGIS_url_gen(lat, lon, startyear, endyear, peakpower, loss, angle)
        # url_PVGIS = 'http://re.jrc.ec.europa.eu/pvgis5/seriescalc.php?lat=51&lon=4&startyear=2015&endyear=2015&peakpower=3&loss=0&angle=0'
        r = requests.get(url_PVGIS)
        if r.status_code == 200:
            global_solar_irradiation = dr + "\\Global_solar_irradiation.csv"
            outside_temperature = dr + "\\Outside_temperature.csv"
            global_solar_irradiation_2 = dr + "\\Global_solar_irradiation_2.csv"
            global_solar_irradiation_seasonal = dr + "\\Global_solar_irradiation_seasonal.csv"
            gsi = open(global_solar_irradiation, 'w')
            ot = open(outside_temperature, 'w')
            gsi2 = open(global_solar_irradiation_2, 'w')
            gsis = open(global_solar_irradiation_seasonal, 'w')
            data = r.text.split("\r\n")
            for i in range(8760):
                try:
                    value = data[11+i].split(",")[1]
                except:
                    print("Critical error retrieving data from PVGIS: unexpected kind or data format. "
                          "Output may be corrupted")
                    break
                gsi.write(value + "\n")
                gsi2.write(value + "\n")
                gsis.write(value + "\n")
                try:
                    ot.write(data[11+i].split(",")[3] + "\n")
                except:
                    print("Critical error retrieving data from PVGIS: unexpected kind or data format. "
                          "Output may be corrupted")
                    break
            gsi.close()
            gsi2.close()
            gsis.close()
            ot.close()
        else:
            print("Error connecting", url_PVGIS, "Status code: ", r.status_code)
            print("Solar irradiation could not be retrieved.")

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
        fec = self.fec_visualizer_service.get_fec()
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
                    self.tableWidget.item(i, 1).setForeground(QColor(0, 255, 0))
                    self.tableWidget.item(i, 2).setForeground(QColor(0, 255, 0))
                    # icon = QIcon()
                    # icon_path = os.path.join(self.file_manager.city_plugin_folder, "../", "images",
                    #                          "green_check.png")
                    # icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
                    # total_percent.setIcon(icon)
                else:
                    self.tableWidget.item(i, 1).setForeground(QColor(255, 0, 0))
                    self.tableWidget.item(i, 2).setForeground(QColor(255, 0, 0))
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

