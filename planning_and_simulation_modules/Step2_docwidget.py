import os, shutil
import math

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
import os.path
import logging
import sys
import traceback

# Import PyQt5
from PyQt5.QtWidgets import QTreeWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QThread

# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# Import the custom tree widget items
from .building.Building import *
from .utility.filters.FECvisualizerService import FECvisualizerService
from .utility.easy_progress_bar import Actions
from .building.DPM import *
from .dialogSources import CheckSourceDialog
from .technology.Technology import *
from .Tjulia.Heat_pump_COP import generate_fileEta_forJulia
from .Tjulia.Solar_thermal_production import generate_solar_thermal_forJulia
from .Tjulia.single_building.Dem_cool_heating import generafile, gen_dem_time_district
from .Tjulia.single_building.eta_cool_heat_pump import eta_cool_heat_pump
from .Tjulia.district.heating.Waste_heat_heat_pumps_heating import generate_file_Waste_heat_pump_heating
from .Tjulia.district.cooling.Waste_heat_heat_pumps_cooling import generate_file_Waste_heat_pump_cooling
from .Tjulia.DistrictSimulator import DistrictSimulator


from .Tjulia.Heat_pump_cool_COP import genera_file_etaHP_cool

from .dhcoptimizerplanheat.optimizer.automatic_design.ad_network_optimization import ADNetworkOptimizer
from . import master_planning_config

import requests

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'Step2dockwidget.ui'))


class Step2_widget(QtWidgets.QDockWidget, FORM_CLASS):
    step2_closing_signal = pyqtSignal()
    send_KPIs_to_future = pyqtSignal(dict)
    update_progress_bar = pyqtSignal(int)
    stop_progress_bar = pyqtSignal()

    def __init__(self, work_folder=None, parent=None):
        """Constructor."""
        super(Step2_widget, self).__init__(parent)

        self.logger = logging.getLogger(__name__)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.baseline_buildings_widget = None
        self.baseline_sources_table = None
        self.baseline_scenario = None
        self.DHN_network_list = []
        self.DCN_network_list = []
        self.step0 = None
        self.step1 = None
        self.KPIs = None
        self.work_folder = work_folder
        self.simulator = None

        self.sources = CheckSourceDialog()

        for table in [self.tableWidget_5, self.tableWidget_2, self.tableWidget_3, self.tableWidget_4]:
            for i in range(table.rowCount()):
                for j in range(table.columnCount()):
                    widget_item = table.item(i, j)
                    if widget_item is not None:
                        widget_item.setFlags(Qt.ItemIsEnabled)
                        if j == 0:
                            widget_item.setBackground(QBrush(QColor(Qt.white)))


        self.progressBar.hide()
        # self.tableWidget_5.setSpan(1, 0, 2, 1)
        # self.tableWidget_5.setSpan(3, 0, 2, 1)
        # self.tableWidget_5.setSpan(5, 0, 2, 1)
        # self.tableWidget_5.setSpan(7, 0, 2, 1)
        # self.tableWidget_5.setSpan(9, 0, 2, 1)
        # self.tableWidget_5.setSpan(11, 0, 2, 1)
        # self.tableWidget_5.setSpan(13, 0, 2, 1)
        # self.tableWidget_5.setSpan(16, 0, 2, 1)
        # self.tableWidget_2.setSpan(1, 0, 2, 1)
        # self.tableWidget_2.setSpan(3, 0, 6, 1)
        self.heat = None
        self.temperature = None

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "edit.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.calculateKpi.setIcon(icon)

        self.calculateKpi.clicked.connect(self.show_progress_bar)

        self.fec_visualizer_service = FECvisualizerService(self.output_table, self.fec_filter_combo_box,
                                                           self.description_filter_label, mode="baseline")

        self.mode_individual_buildings_active = False
        self.mode_networks_active = False

        self.tableWidget_5.hideRow(3)
        self.tableWidget_5.hideRow(4)
        self.tableWidget_5.hideRow(23)
        self.tableWidget_2.hideRow(9)

        self.tabWidget.setCurrentIndex(0)
        self.pop_up_progress_bar = None

    def closeEvent(self, event):
        self.closeStep2()
        event.accept()

    def closeStep2(self):
        if self.KPIs is None:
            msg = QMessageBox(self)    
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setWindowTitle("KPIs uncomputed")
            msg.setText("The KPIs have not been calculated. They need to be computed to run the simulation."
                        +" Do you want to continue anyway ?")
            retval = msg.exec_()
            if retval == QMessageBox.No:
                return
        self.hide()
        self.step2_closing_signal.emit()

    def show_progress_bar(self):

        max_progress = 0
        max_progress = max_progress + (
                len(self.DHN_network_list) + len(self.DCN_network_list)) * 4
        try:
            for _ in self.baseline_scenario.getFeatures():
                max_progress = max_progress + 1
        except:
            pass
        #self.progressBar.setMaximum(max_progress)
        #self.progressBar.setMinimum(0)
        #self.progressBar.setValue(0)
        #self.progressBar.show()
        #self.label_3.setText("Starting computation...")

    def update_mode_networks(self, isactive):
        self.mode_networks_active = isactive

    def update_mode_single_buildings(self, isactive):
        self.mode_individual_buildings_active = isactive

    def KPIs_baselineScenario(self):
        # print("Main plugin thread:", int(QThread.currentThreadId()))
        # pop_up_progress_bar = Actions()
        # thread = QThread()
        # pop_up_progress_bar.moveToThread(thread)
        # thread.started.connect(pop_up_progress_bar.start)
        # # self.update_progress_bar.connect(pop_up_progress_bar.add_progress)
        # # self.stop_progress_bar.connect(pop_up_progress_bar.stop)
        # pop_up_progress_bar.finished.connect(thread.quit)
        # # self.pop_up_progress_bar.finished.connect(self.pop_up_progress_bar.deleteLater)
        # thread.finished.connect(thread.deleteLater)
        #
        # thread.start()
        #
        # self.stop_progress_bar.emit()
        #
        # return


        kpis_folder = os.path.join( master_planning_config.CURRENT_PLANNING_DIRECTORY,
                                    master_planning_config.DISTRICT_FOLDER,
                                    master_planning_config.KPIS_FOLDER)

        #======================= Network approach =========================

        if True:#self.mode_networks_active:

            #dr = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tjulia", "district", "heating")
            dr = os.path.join(kpis_folder, "Tjulia", "district", "heating")
            self.remove_files(os.path.join(dr, "Results"), "Result")
            #dr_sim = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tjulia", "district")
            dr_sim = os.path.join(kpis_folder, "Tjulia", "district")

            if len(self.DHN_network_list) > 0:
                cinput = os.path.join(  master_planning_config.CURRENT_MAPPING_DIRECTORY,
                                    master_planning_config.DMM_FOLDER,
                                    master_planning_config.DMM_PREFIX+master_planning_config.DMM_HOURLY_SUFFIX+".csv")
                gen_dem_time_district(cinput=cinput, coutput=os.path.join(dr, "input"), energy="Heating")
                self.district_heating_preprocessing(dr_sim)
            if len(self.DCN_network_list) > 0:
                cinput = os.path.join(  master_planning_config.CURRENT_MAPPING_DIRECTORY,
                                    master_planning_config.DMM_FOLDER,
                                    master_planning_config.DMM_PREFIX+master_planning_config.DMM_HOURLY_SUFFIX+".csv")
                gen_dem_time_district(cinput=cinput, coutput=os.path.join(dr, "input"), energy="Cooling")
                self.district_cooling_preprocessing(dr_sim)

            print("Step2.py, KPIs_baselineScenario(): setting up simulator")
            self.set_up_simulator()
            print("Step2.py, KPIs_baselineScenario(): running district simulator")
            # thread_networks = QThread()
            # self.simulator.main_thread = QtCore.QThread.currentThread()
            # self.simulator.moveToThread(thread_networks)
            # self.simulator.finished.connect(thread_networks.quit)
            # thread_networks.finished.connect(thread_networks.deleteLater)
            # thread_networks.started.connect(lambda: self.simulator.run_district(dr_sim))
            # thread_networks.start()
            self.simulator.run_district(dr_sim)

        #======================= Buildings approach =========================

        if True:#self.mode_individual_buildings_active:

            #dr = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Tjulia", "single_building")
            dr = os.path.join(kpis_folder, "Tjulia", "single_building")
            # ==> [PlanHeatProjectName]_hourly.csv
            # DEM_cool_time.csv
            # DEM_time.csv
            # DEM_DHW_time.csv
            print("Step2.py, KPIs_baselineScenario(): generating hourly profiles")
            cinput = os.path.join(  master_planning_config.CURRENT_MAPPING_DIRECTORY,
                                    master_planning_config.DMM_FOLDER,
                                    master_planning_config.DMM_PREFIX+master_planning_config.DMM_HOURLY_SUFFIX+".csv")
            n, buildings = generafile(cinput=cinput, coutput=os.path.join(dr, "input"))

            self.remove_files(os.path.join(dr, "Results"), "Result")
            print("Step2.py, KPIs_baselineScenario(): single building common precalculations")
            self.single_building_common_precalculation(dr)
            print("Step2.py, KPIs_baselineScenario(): running building calculation*")
            self.simulator.run_buildings(buildings, dr)
            self.simulator.progress_bar = self.progressBar
            KPIs = self.simulator.close_simulation()
            self.fec_visualizer_service.set_KPIs(KPIs)

        #================================================================


        self.KPIs = KPIs

        self.send_KPIs_to_future.emit(KPIs)

        cellr =QTableWidgetItem(str(KPIs["EN_1.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_1.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_1.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(1, 3, cellr)
        self.tableWidget_5.setItem(1, 4, cellt)
        self.tableWidget_5.setItem(1, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_1.2R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_1.2T"]))
        cell = QTableWidgetItem(str(KPIs["EN_1.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(2, 3, cellr)
        self.tableWidget_5.setItem(2, 4, cellt)
        self.tableWidget_5.setItem(2, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_2.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_2.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_2.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(3, 3, cellr)
        self.tableWidget_5.setItem(3, 4, cellt)
        self.tableWidget_5.setItem(3, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_2.2R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_2.2T"]))
        cell = QTableWidgetItem(str(KPIs["EN_2.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(4, 3, cellr)
        self.tableWidget_5.setItem(4, 4, cellt)
        self.tableWidget_5.setItem(4, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_3.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_3.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_3.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(5, 3, cellr)
        self.tableWidget_5.setItem(5, 4, cellt)
        self.tableWidget_5.setItem(5, 5, cell)


        cellr = QTableWidgetItem(str(KPIs["EN_3.2R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_3.2T"]))
        cell = QTableWidgetItem(str(KPIs["EN_3.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(6, 3, cellr)
        self.tableWidget_5.setItem(6, 4, cellt)
        self.tableWidget_5.setItem(6, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_4.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_4.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_4.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(7, 3, cellr)
        self.tableWidget_5.setItem(7, 4, cellt)
        self.tableWidget_5.setItem(7, 5, cell)

        cellr = QTableWidgetItem(self.round_to_string(KPIs["EN_4.2R"]))
        cellt = QTableWidgetItem(self.round_to_string(KPIs["EN_4.2T"]))
        cell = QTableWidgetItem(self.round_to_string(KPIs["EN_4.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(8, 3, cellr)
        self.tableWidget_5.setItem(8, 4, cellt)
        self.tableWidget_5.setItem(8, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_5.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_5.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_5.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(9, 3, cellr)
        self.tableWidget_5.setItem(9, 4, cellt)
        self.tableWidget_5.setItem(9, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_5.2R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_5.2T"]))
        cell = QTableWidgetItem(str(KPIs["EN_5.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(10, 3, cellr)
        self.tableWidget_5.setItem(10, 4, cellt)
        self.tableWidget_5.setItem(10, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_6.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_6.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_6.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(11, 3, cellr)
        self.tableWidget_5.setItem(11, 4, cellt)
        self.tableWidget_5.setItem(11, 5, cell)

        cellr = QTableWidgetItem(self.round_to_string(KPIs["EN_6.2R"]))
        cellt = QTableWidgetItem(self.round_to_string(KPIs["EN_6.2T"]))
        cell = QTableWidgetItem(self.round_to_string(KPIs["EN_6.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(12, 3, cellr)
        self.tableWidget_5.setItem(12, 4, cellt)
        self.tableWidget_5.setItem(12, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_7.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_7.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_7.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(13, 3, cellr)
        self.tableWidget_5.setItem(13, 4, cellt)
        self.tableWidget_5.setItem(13, 5, cell)

        cellr = QTableWidgetItem(self.round_to_string(KPIs["EN_7.2R"]))
        cellt = QTableWidgetItem(self.round_to_string(KPIs["EN_7.2T"]))
        cell = QTableWidgetItem(self.round_to_string(KPIs["EN_7.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(14, 3, cellr)
        self.tableWidget_5.setItem(14, 4, cellt)
        self.tableWidget_5.setItem(14, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_9.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_9.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_9.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(15, 3, cellr)
        self.tableWidget_5.setItem(15, 4, cellt)
        self.tableWidget_5.setItem(15, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_11.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_11.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_11.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(16, 3, cellr)
        self.tableWidget_5.setItem(16, 4, cellt)
        self.tableWidget_5.setItem(16, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_11.2R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_11.2T"]))
        cell = QTableWidgetItem(str(KPIs["EN_11.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(17, 3, cellr)
        self.tableWidget_5.setItem(17, 4, cellt)
        self.tableWidget_5.setItem(17, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_12.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_12.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_12.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(18, 3, cellr)
        self.tableWidget_5.setItem(18, 4, cellt)
        self.tableWidget_5.setItem(18, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_13.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_13.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_13.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(19, 3, cellr)
        self.tableWidget_5.setItem(19, 4, cellt)
        self.tableWidget_5.setItem(19, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_13.1bR"]))
        cellt = QTableWidgetItem(str(KPIs["EN_13.1bT"]))
        cell = QTableWidgetItem(str(KPIs["EN_13.1b"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(20, 3, cellr)
        self.tableWidget_5.setItem(20, 4, cellt)
        self.tableWidget_5.setItem(20, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_14.1R"]))
        cellt = QTableWidgetItem(str(KPIs["EN_14.1T"]))
        cell = QTableWidgetItem(str(KPIs["EN_14.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(21, 3, cellr)
        self.tableWidget_5.setItem(21, 4, cellt)
        self.tableWidget_5.setItem(21, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["EN_14.1bR"]))
        cellt = QTableWidgetItem(str(KPIs["EN_14.1bT"]))
        cell = QTableWidgetItem(str(KPIs["EN_14.1b"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(22, 3, cellr)
        self.tableWidget_5.setItem(22, 4, cellt)
        self.tableWidget_5.setItem(22, 5, cell)
        self.tableWidget_5.setItem(22, 5, cell)

        cellr = QTableWidgetItem("Nan")
        cellt = QTableWidgetItem("Nan")
        cell = QTableWidgetItem("Nan")
        # cellr = QTableWidgetItem(str(KPIs["EN_15.1R"]))
        # cellt = QTableWidgetItem(str(KPIs["EN_15.1T"]))
        # cell = QTableWidgetItem(str(KPIs["EN_15.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(23, 3, cellr)
        self.tableWidget_5.setItem(23, 4, cellt)
        self.tableWidget_5.setItem(23, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.3R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_1.3T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_1.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(1, 3, cellr)
        self.tableWidget_2.setItem(1, 4, cellt)
        self.tableWidget_2.setItem(1, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.4R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_1.4T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_1.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(2, 3, cellr)
        self.tableWidget_2.setItem(2, 4, cellt)
        self.tableWidget_2.setItem(2, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_2.1R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_2.1T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_2.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(3, 3, cellr)
        self.tableWidget_2.setItem(3, 4, cellt)
        self.tableWidget_2.setItem(3, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_2.2R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_2.2T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_2.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(4, 3, cellr)
        self.tableWidget_2.setItem(4, 4, cellt)
        self.tableWidget_2.setItem(4, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_2.7R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_2.7T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_2.7"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(5, 3, cellr)
        self.tableWidget_2.setItem(5, 4, cellt)
        self.tableWidget_2.setItem(5, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_2.8R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_2.8T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_2.8"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(6, 3, cellr)
        self.tableWidget_2.setItem(6, 4, cellt)
        self.tableWidget_2.setItem(6, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_2.13R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_2.13T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_2.13"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(7, 3, cellr)
        self.tableWidget_2.setItem(7, 4, cellt)
        self.tableWidget_2.setItem(7, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ENV_2.14R"]))
        cellt = QTableWidgetItem(str(KPIs["ENV_2.14T"]))
        cell = QTableWidgetItem(str(KPIs["ENV_2.14"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_2.setItem(8, 3, cellr)
        self.tableWidget_2.setItem(8, 4, cellt)
        self.tableWidget_2.setItem(8, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["SO_3.1R"]))
        cellt = QTableWidgetItem(str(KPIs["SO_3.1T"]))
        cell = QTableWidgetItem(str(KPIs["SO_3.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_4.setItem(4, 3, cellr)
        self.tableWidget_4.setItem(4, 4, cellt)
        self.tableWidget_4.setItem(4, 5, cell)

        cellr = QTableWidgetItem(str(KPIs["ECO_2.1R"]))
        cellt = QTableWidgetItem(str(KPIs["ECO_2.1T"]))
        cell = QTableWidgetItem(str(KPIs["ECO_2.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        cellt.setFlags(QtCore.Qt.ItemIsEnabled)
        cell.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_3.setItem(5, 3, cellr)
        self.tableWidget_3.setItem(5, 4, cellt)
        self.tableWidget_3.setItem(5, 5, cell)

        print("KPIs done!")
        self.stop_progress_bar.emit()


    def set_up_simulator(self):
        self.simulator = DistrictSimulator()
        self.simulator.DHN_network_list = self.DHN_network_list
        self.simulator.DCN_network_list = self.DCN_network_list

        self.simulator.sources_tab = self.baseline_sources_table
        self.simulator.ef_sources_tab = self.baseline_sources_table
        print("Step2_dockwidget.set_up_simulator: self.baseline_sources_table, self.simulator.sources_tab, self.simulator.ef_sources_tab",
              self.baseline_sources_table, self.simulator.sources_tab, self.simulator.ef_sources_tab)
        self.simulator.sources = self.sources
        self.simulator.step1_network_tree_widget = self.step1.dmmTreeNetwork
        self.simulator.step1_building_tree_widget = self.step1.dmmTree
        self.simulator.step0_district_sources_tab = self.step0.sources_available
        self.simulator.step4_network_tree_widget = None
        self.simulator.step4_building_tree_widget = None

        self.simulator.logger = self.logger

        self.simulator.baseline_scenario = self.baseline_scenario
        self.simulator.future_scenario = None

        self.simulator.baseline_KPIs = None
        self.simulator.KPIs_additional_data = self.step1.KPIs_additional_data

        self.simulator.heat = self.heat
        self.simulator.temperature = self.temperature

        self.simulator.set_up_new_simulation()

    def district_cooling_preprocessing(self, dr):

        # Global_solar_irradiation.csv
        # Global_solar_irradiation_2.csv
        # Global_solar_irradiation_seasonal.csv
        # Outside_temperature.csv
        # default (Antwerp): lat=51, lon=4, startyear=2015, endyear=2015, peakpower=3, loss=0, angle=0
        self.download_data_from_PVGIS(dr=dr)


    def district_heating_preprocessing(self, dr):
        # Global_solar_irradiation.csv
        # Global_solar_irradiation_2.csv
        # Global_solar_irradiation_seasonal.csv
        # Outside_temperature.csv
        # default (Antwerp): lat=51, lon=4, startyear=2015, endyear=2015, peakpower=3, loss=0, angle=0
        self.download_data_from_PVGIS(dr=dr)


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
        #generate_file_Waste_heat_pump_heating(None, input_folder=dr, output_folder=os.path.join(dr, "heating", "input"))

    # def single_building_preprocessing(self, j, dr, building_id):
    #     expr = QgsExpression("BuildingID=" + building_id)
    #     if self.baseline_scenario is None:
    #
    #         return
    #     fs = [ft for ft in self.baseline_scenario.getFeatures(QgsFeatureRequest(expr))]
    #
    #     if len(fs) > 0:
    #         feature_0 = fs[0]
    #     else:
    #
    #         return
    #
    #     item = self.get_widget_item_from_feature(feature_0)
    #     if item is None:
    #
    #         return None
    #     tech_infos = self.create_base_tech_infos()
    #
    #     self.update_tech_from_widget_item(tech_infos, item)
    #
    #     input_folder = os.path.join(dr, "input")
    #     output_folder = os.path.join(dr, "Results")
    #
    #     # building_id = "toy"
    #     j.individual_H_and_C(input_folder, output_folder, tech_infos, building_id, self.logger.info)
    #
    #     return item

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
        # generate_fileEta_forJulia(None, input_folder=dr, output_folder=os.path.join(dr, "input"))

        # ==> Outside_temperature.csv
        # eta_HP_cool.csv
        # eta_HP_cool_2.csv
        # eta_cool_heat_pump(input_folder=dr, output_folder=os.path.join(dr, "input"))

        # ==> Global_solar_irradiation.csv
        # ==> Global_solar_irradiation_2.csv
        # ==> Global_solar_irradiation_seasonal.csv
        # ==> Outside_temperature.csv
        # ST_specific_time_seasonal.csv
        # ST_specific_time_2.csv
        # ST_specific_time.csv
        generate_solar_thermal_forJulia(None, input_folder=dr, output_folder=os.path.join(dr, "input"))


    def get_area(self, building_id):
        expr = QgsExpression("BuildingID=" + building_id)
        if self.baseline_scenario is None:

            return
        fs = [ft for ft in self.baseline_scenario.getFeatures(QgsFeatureRequest(expr))]
        if len(fs) > 0:
            feature_0 = fs[0]
        else:

            return 0
        return feature_0.geometry().area()

    def sum_file(self, file, column=0, separator=";"):
        total = 0.0
        try:
            with open(file) as fp:
                for i, line in enumerate(fp):
                    total = total + float(line.split(separator)[column])
        except:

            print("file", file, "column", column, "separator", separator)
            return 0.0

        return total

    def get_source_infos(self, widget, source):
        for i in range(widget.rowCount()):
            if widget.verticalHeaderItem(i).text() == source:
                try:
                    return [float(widget.item(i, 0).text()),
                            float(widget.item(i, 1).text())]
                except:
                    print("Step2_dockwidget.py, get_source_infos: impossible to get row", i)

        return [0, 0]

    def remove_files(self, dr, start):
        if not os.path.isdir(dr):
            return
        for f in os.listdir(dr):
            fn = os.fsdecode(f)
            if fn.startswith(start):
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

    def reset_tech_info_to_0(self, tech_info=None):
        if tech_info is None:
            tech_info = self.create_base_tech_infos()
            tech_info = self.reset_tech_info_to_0(tech_info=tech_info)
            return tech_info
        else:
            for key in tech_info.keys():
                tech_info[key] = 0
            return tech_info

    def receive_widget(self, widget, sources, dhn, dcn):
        self.baseline_buildings_widget = widget
        self.baseline_sources_table = sources
        self.DHN_network_list = dhn
        self.DCN_network_list = dcn
        print("Step2.py, receive_widget(). DHN and DCN", [n.name for n in self.DHN_network_list],
              [n.name for n in self.DCN_network_list])
        print("Step2.py, receive_widget(). widget, sources:", widget, sources)


    def receive_baseline_scenario(self, layer):
        self.baseline_scenario = layer

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
        # url_PVGIS = self.PVGIS_url_gen(lat, lon, startyear, endyear, peakpower, loss, angle)
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

    def get_step0_data(self, heat, temperature):
        self.heat = heat
        self.temperature = temperature

    def round_to_string(self, in_value):
        try:
            return str(round(float(in_value), 2))
        except:
            return "Nan"

