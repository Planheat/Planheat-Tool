
import json
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtSignal
from .src.FileManager import FileManager
from .src.ImportManager import ImportManager
from PyQt5.QtGui import QPixmap
from ..VITO.Prioritization_algorithm import *
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from .KPIsCalculatorCity import KPIsCalculator
from .db import recive_country
from .db import recive_primary_energy_factor
from .updataTableKpi import update_KPIs_visualization_tab
from .updataTableKpi import tab_not_editable
from ..config.PlanningCriteriaHelper import PlanningCriteriaHelper
from .. import master_planning_config
from .config import scenarioAttributes
import pandas as pd

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'city_step01.ui'))


class CityStep01Dialog(QtWidgets.QDockWidget, FORM_CLASS):
    step01_closing_signal = pyqtSignal()
    refresh_step2 = pyqtSignal()
    send_sources = pyqtSignal(QTableWidget)

    def __init__(self, iface, work_folder=None, parent=None):
        """Constructor."""
        super(CityStep01Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.work_folder = work_folder
        self.iface = iface

        self.citySim = None

        self.KPIs= {}
        self.file_manager = FileManager(work_folder=self.work_folder)

        self.refresh_combobox()
        self.radioButton.toggled.connect(self.radio_clicked)
        self.radioButton_2.toggled.connect(self.radio_clicked)
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images",
                                 "calculator.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.btn_Kpis.setIcon(icon)

        self.btn_Kpis.clicked.connect(self.read_table)

        self.delate.clicked.connect(self.delete_file)
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images",
                                 "red_cross.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.delate.setIcon(icon)
        self.remove_criteria.setIcon(icon)
        self.delate.clicked.connect(self.load_json)
        self.add_criteria.clicked.connect(self.insert_criteria)
        self.tree_planning.itemPressed.connect(self.itemSelection)
        self.remove_criteria.clicked.connect(self.delete_criteria)
        self.energy_criteria.currentItemChanged.connect(self.current_item_changed)
        self.ok.clicked.connect(self.send_kPI)
        self.string= None
        self.comboBox_CMM_import.currentTextChanged.connect(self.comboBox_changed)
        self.country_comboBox.currentTextChanged.connect(self.save_country)

        self.weights = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.calculator = KPIsCalculator()

        self.planning_criteria_helper = PlanningCriteriaHelper()

        self.load_city = None
        valore_comboBox = recive_country()

        self.country_comboBox.addItems(valore_comboBox)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images",
                                 "open_file.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)

        self.upload.setIcon(icon)
        self.upload.clicked.connect(self.load_step2)
        self.ok.clicked.connect(self.manda_tab)
        #self.ok.clicked.connect(self.send_tab_source)

        self.source_base()


    def comboBox_changed(self, file):
        import_manager = ImportManager(self.file_manager)
        import_manager.load_DMM_output_to_table(file, self.tb_HeDHW_source,
                                                self.table_cool_source, self.table_fec_baseline,
                                                self.table_sd_HeDHW, self.table_sd_cool)
        self.refresh_step2.emit()
        self.read_table()


    def save_country(self):
        country = self.country_comboBox.currentText()
        # print("country selezionato", country)
        primary_energy = recive_primary_energy_factor(country)

    def closeEvent(self, event):
        self.closeStep01()
        event.accept()

    def closeStep01(self):
        self.hide()
        self.step01_closing_signal.emit()

    def delete_file(self):
        file = self.comboBox_CMM_import.currentText()
        if file is None:
            return
        if file == "":
            return
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Are you sure?")
        msgBox.setInformativeText("The selected file will be permanently removed from your disk/memory."
                                  "\nPress Cancel to abort this procedure."
                                  "\nPress Ok to delete " + file)
        msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.Cancel:
            return
        if self.radioButton.isChecked():
            file = file + "_R.json"
        else:
            file = file + "_T.json"
        self.file_manager.delete_files_from_mapping_default_folders([file])
        self.refresh_combobox()

    def refresh_combobox(self):
        if self.radioButton.isChecked():
            self.file_manager.import_and_fill_combo_box_from_DMM_planheat_mapping_wizard(self.comboBox_CMM_import,
                                                                                         sector="R")
            scenarioAttributes.sector = "residential"
            return
        if self.radioButton_2.isChecked():
            self.file_manager.import_and_fill_combo_box_from_DMM_planheat_mapping_wizard(self.comboBox_CMM_import,
                                                                                         sector="T")
            scenarioAttributes.sector = "tertiary"
            return


    def radio_clicked(self):
        self.refresh_combobox()

    def itemSelection(self, item, column):
        p = item.text(column)
        help = self.planning_criteria_helper.insert_text_help(p)
        self.helpText.setText(help)
        self.show_help()

    def show_help(self):
        if self.helpText is not None:
            self.helpText.show()

    def insert_criteria(self):
        if self.tree_planning.currentItem() is None:
            return
        text = self.tree_planning.currentItem().text(0).split(':')

        if len(text) == 0:
            return
        if len(text[0]) < 3:
            return
        if text[0][0:3] == "ENV":
            if self.environmental_criteria.count() >= 3:
                QMessageBox.warning(None, "Warning", "You can select up to 3 environmental planning criteria")
            else:
                if self.tree_planning.currentItem().text(0) not in [self.environmental_criteria.item(i).text() for i in
                                                                 range(self.environmental_criteria.count())]:
                    self.environmental_criteria.addItem(self.tree_planning.currentItem().text(0) + " - W=" + str(self.weight_plan.value()))
                    self.update_weights(self.tree_planning.currentItem().text(0), self.weight_plan.value())
            self.update_KPIs_visualization_tab()
            return
        if text[0][0:3] == "ECO":
            if self.economic_criteria.count() >= 1:
                QMessageBox.warning(None, "Warning", "You can select only 1 economic planning criteria")
            else:
                if self.tree_planning.currentItem().text(0) not in [self.economic_criteria.item(i).text() for i in
                                                                 range(self.economic_criteria.count())]:
                    self.economic_criteria.addItem(self.tree_planning.currentItem().text(0) + " - W=" + str(self.weight_plan.value()))
                    self.update_weights(self.tree_planning.currentItem().text(0), self.weight_plan.value())
            self.update_KPIs_visualization_tab()
            return
        if text[0][0:2] == "SO":
            if self.social_criteria.count() >= 3:
                QMessageBox.warning(None, "Warning", "You can select up to 3 social planning criteria")
            else:
                if self.tree_planning.currentItem().text(0) not in [self.social_criteria.item(i).text() for i in
                                                                 range(self.social_criteria.count())]:
                    self.social_criteria.addItem(self.tree_planning.currentItem().text(0) + " - W=" + str(self.weight_plan.value()))
                    self.update_weights(self.tree_planning.currentItem().text(0), self.weight_plan.value())
            self.update_KPIs_visualization_tab()
            return
        if text[0][0:2] == "EN":
            if self.energy_criteria.count() >= 3:
                QMessageBox.warning(None, "Warning", "You can select up to 3 energy planning criteria")
            else:
                if self.tree_planning.currentItem().text(0) not in [self.energy_criteria.item(i).text() for i in
                                                                 range(self.energy_criteria.count())]:
                    self.energy_criteria.addItem(self.tree_planning.currentItem().text(0) + " - W=" + str(self.weight_plan.value()))
                    self.update_weights(self.tree_planning.currentItem().text(0), self.weight_plan.value())
            self.update_KPIs_visualization_tab()
            return

    def delete_criteria(self):
        for item in self.energy_criteria.selectedItems():
            self.update_weights(item.text(), 0)
            self.energy_criteria.takeItem(self.energy_criteria.row(item))

        for itemSocial in self.social_criteria.selectedItems():
            self.update_weights(itemSocial.text(), 0)
            self.social_criteria.takeItem(self.social_criteria.row(itemSocial))

        for itemEnv in self.environmental_criteria.selectedItems():
            self.update_weights(itemEnv.text(), 0)
            self.environmental_criteria.takeItem(self.environmental_criteria.row(itemEnv))

        for itemEco in self.economic_criteria.selectedItems():
            self.update_weights(itemEco.text(), 0)
            self.economic_criteria.takeItem(self.economic_criteria.row(itemEco))

    def current_item_changed(self, current, previous):
        if self.energy_criteria.currentItem().text() == current.text():
            self.social_criteria.setCurrentItem(None)
            self.economic_criteria.setCurrentItem(None)
            self.environmental_criteria.setCurrentItem(None)
            return
        if self.social_criteria.currentItem().text() == current.text():
            self.energy_criteria.setCurrentItem(None)
            self.economic_criteria.setCurrentItem(None)
            self.environmental_criteria.setCurrentItem(None)
            return
        if self.economic_criteria.currentItem().text() == current.text():
            self.social_criteria.setCurrentItem(None)
            self.energy_criteria.setCurrentItem(None)
            self.environmental_criteria.setCurrentItem(None)
            return
        if self.environmental_criteria.currentItem().text() == current.text():
            self.social_criteria.setCurrentItem(None)
            self.economic_criteria.setCurrentItem(None)
            self.energy_criteria.setCurrentItem(None)
            return

    def update_weights(self, criteria, value):
        cod = criteria.split(":")[0]
        if cod == "ECO3":
            self.weights[0] = value
        if cod == "ECO2":
            self.weights[1] = value
        if cod == "Reduction of energy tariffs":
            self.weights[2] = value
        if cod == "SO3":
            self.weights[3] = value
        if cod == "ENV1":
            self.weights[4] = value
        if cod == "ENV2":
            self.weights[5] = value
        if cod == "ENV3":
            self.weights[6] = value
        if cod == "EN1":
            self.weights[7] = value
        if cod == "EN4":
            self.weights[8] = value
        if cod == "EN5":
            self.weights[9] = value
        if cod == "EN6":
            self.weights[10] = value
        if cod == "EN7":
            self.weights[11] = value
        if cod == "Increased share of DHC":
            self.weights[12] = value
        if cod == "SO2":
            self.weights[14] = value
        if cod == "SO1":
            self.weights[15] = value
        self.refresh_vito_report()


    def update_KPIs_visualization_tab(self):
        update_KPIs_visualization_tab(self.table_KPIsEn, self.energy_criteria, self.table_KPIsEnv, self.environmental_criteria,
                                      self.table_KPIsEco, self.economic_criteria, self.table_KPIsSo, self.social_criteria)

    def refresh_vito_report(self):
        tables = prioritization_algorithm(self.weights)
        tables_dict = {"Space heating high temperature": self.tableWidget,
                       "Space heating medium temperature": self.tableWidget_HeatingM,
                       "Space heating low temperature": self.tableWidget_heatinhH,
                       "Domestic hot water": self.tableWidget_dhw,
                       "Space cooling": self.tableWidget_cool
                       }

        for key in tables.keys():
                for j in range(tables_dict[key].rowCount()):
                    if tables_dict[key].verticalHeaderItem(j).text() == "natural gas":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][0]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "oil":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][1]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "coal":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][2]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "solar thermal":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][3]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "deep geothermy":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][4]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "shallow geothermy":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][5]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "biomass":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][6]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "excess heat":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][7]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "air":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][8]))
                        tables_dict[key].setItem(j, 0, item)
                    if tables_dict[key].verticalHeaderItem(j).text() == "cold water bodies":
                        item = QTableWidgetItem(1)
                        item.setText(str(tables[key][9]))
                        tables_dict[key].setItem(j, 0, item)
                tables_dict[key].sortItems(0)


    def load_json(self):
        self.folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_and_simulation_modules\\save_utility\\DefaultSaveFolder"
        file = self.folder + "\\gigi.json"
        with open(file) as f:
            data = json.load(f)


    def read_table(self):
        # table heating + DHW baseline
        table = self.tb_HeDHW_source
        self.lista_UED = []
        for i in range(table.rowCount()):
            try:
                currItem =float((table.item(i,0)).text())
                #valTxt = currItem.text()
                self.lista_UED.append(currItem)
            except (AttributeError, ValueError):
                self.lista_UED.append(0.0)

        # table cool baseline
        table_cool = self.table_cool_source
        self.lista_cool = []
        for j in range(table_cool.rowCount()):
            try:
                value=float((table_cool.item(j,0)).text())
                self.lista_cool.append(value)
            except (AttributeError, ValueError):
                self.lista_cool.append(0.0)


        table2 = self.table_fec_baseline
        self.lista_fec_baseline = []
        for j in range(table2.rowCount()):
            try:
                valItem =float((table2.item(j, 0)).text())
                self.lista_fec_baseline.append(valItem)
            except (AttributeError, ValueError):
                self.lista_fec_baseline.append(0.0)

        # valore che deve essere preso dal db
        primary_En_fact = self.get_baseline_pef() # [1, 1, 1, 1, 1, 1, 1, 1]
        self.tot_footArea = self.footArea.value()


        self.KPIs = self.calculator.KPIs_baseline(self.lista_UED, self.lista_cool, primary_En_fact, self.tot_footArea, self.lista_fec_baseline)


        if self.radioButton.isChecked():
            self.string="r"
        if self.radioButton_2.isChecked():
            self.string="t"

        self.KPIs_table(self.KPIs, self.string)
        self.KPIs_table_generic(self.KPIs, self.string)


    def KPIs_table(self, KPIs, string):
        if string=="r":
            ncol=3
        else:
            ncol = 4

        cellr = QTableWidgetItem(str(KPIs["EN_1.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(1, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_1.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(2, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(7, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(8, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(12, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(13, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(17, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(18, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(22, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(23, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(27, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.table_KPIsEn.setItem(28, ncol, cellr)

    def KPIs_table_generic(self,KPIs, string):
        if string=="r":
            ncol=3
        else:
            ncol=4

        cellr = QTableWidgetItem(str(KPIs["EN_1.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(1, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_1.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(2, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(7, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(8, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(12, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(13, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(17, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(18, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(22, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(23, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(27, ncol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.generic_KPIsEn.setItem(28, ncol, cellr)

        tab_not_editable(self.table_KPIsEn,  4)
        tab_not_editable(self.table_KPIsEn, 3)
        tab_not_editable(self.table_KPIsEnv, 4)
        tab_not_editable(self.table_KPIsEnv, 3)
        tab_not_editable(self.table_KPIsEco, 4)
        tab_not_editable(self.table_KPIsEco, 3)
        tab_not_editable(self.table_KPIsSo, 4)
        tab_not_editable(self.table_KPIsSo, 3)
        tab_not_editable(self.generic_KPIsEn, 4)
        tab_not_editable(self.generic_KPIsEn, 3)
        tab_not_editable(self.generic_KPIsEco_2, 4)
        tab_not_editable(self.generic_KPIsEco_2, 3)
        tab_not_editable(self.generic_KPIsEnv_2, 4)
        tab_not_editable(self.generic_KPIsEnv_2, 3)
        tab_not_editable(self.generic_KPIsSo_2, 4)
        tab_not_editable(self.generic_KPIsSo_2, 3)



    def tab_not_edit(self, table, ncol):
        table = table
        rows = [1, 2, 7, 8, 12, 13, 17, 18, 22, 23, 27, 28]
        for i in range(table.rowCount()):
            if i in rows:
                item = table.item(i, ncol)
                item.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(i, ncol, item.clone())
            else:
                pass


    def send_kPI(self):
        target =[]
        table = self.table_KPIsEn
        for i in range(table.rowCount()):
            try:
                item = float((table.item(i, 5)).text())
            except:
                item =""
            target.append(item)

        self.citySim.recive_KPIs_baseline(self.KPIs, self.string)
        self.citySim.insert_target(table)


    def load_step2(self):
        self.load_city.refresh_file_selection_combo_box()
        self.load_city.run()


    def manda_tab(self):
        self.citySim.updataTab(self.energy_criteria, self.environmental_criteria, self.economic_criteria,  self.social_criteria)

        tab_cool = self.table_cool_source
        tab_HeDHw = self.tb_HeDHW_source

        try:
            val1 = float(tab_cool.item(3, 0).text())
        except:
            val1 = 0
        try:
            val2 = float(tab_cool.item(7, 0).text())
        except:
            val2 = 0
        try:
            val3 = float(tab_HeDHw.item(4, 0).text())
        except:
            val3 = 0
        try:
            val4 = float(tab_HeDHw.item(7, 0).text())
        except:
            val4 = 0
        wh_base = val1 + val2 + val3 + val4
        try:
            ind1 =float(tab_HeDHw.item(16, 0).text())
        except:
            ind1 = 0
        try:
            ind2 =float(tab_HeDHw.item(18, 0).text())
        except:
            ind2 = 0
        try:
            ind3 =float(tab_cool.item(10, 0).text())
        except:
            ind3 = 0
        try:
            ind4 =float(tab_cool.item(12, 0).text())
        except:
            ind4 = 0
        wh_ind = ind1 + ind2 + ind3 + ind4
        try:
            val_bio = float(self.table_fec_baseline.item(3, 0).text())
        except:
            val_bio = 0
        try:
            val_geoth = float(self.table_fec_baseline.item(5, 0).text())
        except:
            val_geoth = 0
        try:
            val_sol = float(self.table_fec_baseline.item(8, 0).text())
        except:
            val_sol = 0
        self.citySim.vis_cat_wh(wh_base, wh_ind, val_bio, val_geoth, val_sol)

        self.citySim.load_source_base(self.sources_base)


    def source_base(self):
        self.sources_base.clear()
        dr = os.path.join(master_planning_config.CURRENT_MAPPING_DIRECTORY, master_planning_config.SMM_FOLDER)
        dr = os.path.realpath(dr)
        file = os.path.join(dr, "planheat_result_2.csv")
        data = pd.read_csv(file, delimiter='\t')
        columns = list(data)
        self.sources_base.setHorizontalHeaderLabels(['Source', 'Availability [MW/y]'])
        self.sources_base.setRowCount(len(data.index))
        self.sources_base.setColumnCount(2)
        for i in range(self.sources_base.rowCount()):
                self.sources_base.setItem(i, 0, QTableWidgetItem(data[columns[1]][i]))
                self.sources_base.setItem(i, 1, QTableWidgetItem("{:.2f}".format(data[columns[4]][i]/1000)))

    def get_baseline_pef(self):
        table: QTableWidget = self.pef_table
        pef = []
        for i in range(table.rowCount()):
            try:
                pef.append(float(table.item(i, 0).text()))
            except ValueError:
                pef.append(1.0)
        return pef
