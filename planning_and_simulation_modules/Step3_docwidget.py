from PyQt5 import QtWidgets, uic
# Import PyQt5
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
# Import the custom tree widget items
from .building.DPM import *
from .technology.Technology import *
from .VITO.Prioritization_algorithm import *
from .result_utils import PlotCanvas
from .Tjulia.DistrictSimulator import DistrictSimulator

from .utility.data_manager.PlanningCriteriaTransfer import PlanningCriteriaTransfer

from matplotlib.font_manager import FontProperties

from matplotlib.font_manager import FontProperties
from matplotlib.figure import Figure

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import sip
import pandas

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'Step3dockwidget.ui'))


class Step3_widget(QtWidgets.QDockWidget, FORM_CLASS):
    step3_closing_signal = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(Step3_widget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.helpText.hide()

        self.treeWidget.itemPressed.connect(self.itemSelection)
        self.add_criteria.clicked.connect(self.insert_criteria)
        self.resetTargets.clicked.connect(self.reset_table)

        self.remove_criteria.clicked.connect(self.delete_criteria)
        self.energy_criteria.currentItemChanged.connect(self.current_item_changed)

        self.step2_energy_tab = None
        self.step2_environmental_tab = None
        self.step2_economic_tab = None
        self.step2_social_tab = None
        self.step0_sources_availability_tab = None
        self.data = None

        for table in [self.tableVisKpiEn, self.tableVisKpiEnv, self.tableVisKpiEco, self.tableVisKpiSo,
                      self.tableEnStep3, self.tableENVStep3, self.tableEcoStep3, self.tableSoStep3]:
            for i in range(1, table.rowCount()):
                widget_item = table.item(i, 0)
                if widget_item is not None:
                    table.item(i, 0).setBackground(QBrush(QColor(Qt.white)))

        self.weights = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        # self.plot = PlotCanvas(self, width=10, height=4, dpi=100)
        # layout = self.gridLayout
        # layout.addWidget(self.plot)
        # self.ax = self.plot.figure.add_subplot(111)

        self.simulator=DistrictSimulator()

        self.set_table_flags()

        self.criteria_transfer = PlanningCriteriaTransfer(self.energy_criteria, self.environmental_criteria,
                                                          self.economic_criteria, self.social_criteria)
        self.format_tables()
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(0)


    def load_scv(self, data):
        self.data = data



    def itemSelection(self, item, column):
        p = item.text(column)
        help = self.simulator.insert_text_help(p)
        self.helpText.setText(help)
        self.show_help()

    def show_help(self):
        if self.helpText is not None:
            self.helpText.show()

    def closeEvent(self, event):
        self.closeStep3()
        event.accept()

    def closeStep3(self):
        self.hide()
        self.step3_closing_signal.emit()

    def insert_criteria(self):
        if self.treeWidget.currentItem() is None:
            return
        text = self.treeWidget.currentItem().text(0).split(':')

        if len(text) == 0:
            return
        if len(text[0]) < 3:
            return
        if text[0][0:3] == "ENV":
            if self.environmental_criteria.count() >= 3:
                QMessageBox.warning(None, "Warning", "You can select up to 3 environmental planning criteria")
            else:
                if self.treeWidget.currentItem().text(0) not in [self.environmental_criteria.item(i).text() for i in
                                                                 range(self.environmental_criteria.count())]:
                    self.environmental_criteria.addItem(self.treeWidget.currentItem().text(0) + " - W=" + str(self.weight_spin_box.value()))
                    self.update_weights(self.treeWidget.currentItem().text(0), self.weight_spin_box.value())
            self.update_KPIs_visualization_tab()
            return
        if text[0][0:3] == "ECO":
            if self.economic_criteria.count() >= 1:
                QMessageBox.warning(None, "Warning", "You can select only 1 economic planning criteria")
            else:
                if self.treeWidget.currentItem().text(0) not in [self.economic_criteria.item(i).text() for i in
                                                                 range(self.economic_criteria.count())]:
                    self.economic_criteria.addItem(self.treeWidget.currentItem().text(0) + " - W=" + str(self.weight_spin_box.value()))
                    self.update_weights(self.treeWidget.currentItem().text(0), self.weight_spin_box.value())
            self.update_KPIs_visualization_tab()
            return
        if text[0][0:2] == "SO":
            if self.social_criteria.count() >= 3:
                QMessageBox.warning(None, "Warning", "You can select up to 3 social planning criteria")
            else:
                if self.treeWidget.currentItem().text(0) not in [self.social_criteria.item(i).text() for i in
                                                                 range(self.social_criteria.count())]:
                    self.social_criteria.addItem(self.treeWidget.currentItem().text(0) + " - W=" + str(self.weight_spin_box.value()))
                    self.update_weights(self.treeWidget.currentItem().text(0), self.weight_spin_box.value())
            self.update_KPIs_visualization_tab()
            return
        if text[0][0:2] == "EN":
            if self.energy_criteria.count() >= 3:
                QMessageBox.warning(None, "Warning", "You can select up to 3 energy planning criteria")
            else:
                if self.treeWidget.currentItem().text(0) not in [self.energy_criteria.item(i).text() for i in
                                                                 range(self.energy_criteria.count())]:
                    self.energy_criteria.addItem(self.treeWidget.currentItem().text(0) + " - W=" + str(self.weight_spin_box.value()))
                    self.update_weights(self.treeWidget.currentItem().text(0), self.weight_spin_box.value())
            self.update_KPIs_visualization_tab()
            return

    def update_KPIs_visualization_tab(self):
        criterion_to_rows = {"EN1": [1, 2, 3, 4, 5, 6],
                             "EN2": [7, 8, 9, 10, 11, 12],
                             "EN3": [13, 14, 15, 16, 17, 18],
                             "EN4": [19, 20, 21, 22],
                             "EN5": [23, 24, 25, 26],
                             "EN6": [27, 28, 29, 30],
                             "EN7": [31, 32, 33, 34],
                             "EN9": [35, 36],
                             "EN11": [37, 38, 39],
                             "EN12": [40, 41],
                             "EN13a": [42, 43, 9, 10, 11, 12],
                             "EN13b": [44, 45],
                             "EN14a": [46, 47],
                             "EN14b": [48, 49],
                             "EN15": [50, 51],
                             "ENV1": [1, 2, 3, 4, 5],
                             "ENV2": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                             "ENV3": [21, 22],
                             "ECO1": [1, 2, 3, 4],
                             "ECO2": [5, 6, 7],
                             "ECO3": [8],
                             "ECO4": [9],
                             "SO1": [1, 2],
                             "SO2": [3, 4],
                             "SO3": [5, 6]
                             }
        self.hide_visualization_rows()
        for widgets in [[self.tableVisKpiEn, self.energy_criteria], [self.tableVisKpiEnv, self.environmental_criteria],
                        [self.tableVisKpiEco, self.economic_criteria], [self.tableVisKpiSo, self.social_criteria]]:
            for criteria in criterion_to_rows.keys():
                if self.chech_criterion_is_selected(widgets[1], criteria):
                    for row in criterion_to_rows[criteria]:
                        widgets[0].showRow(row)
        self.criteria_transfer.push_districtSim_table_update(self.chech_criterion_is_selected)

    def chech_criterion_is_selected(self, widget, criteria):
        for i in range(widget.count()):
            texts = widget.item(i).text().split(':')
            if not (len(texts) > 0):
                continue
            if criteria in texts[0]:
                return True
        return False

    def hide_visualization_rows(self):
        for table in [self.tableVisKpiEn, self.tableVisKpiEnv, self.tableVisKpiEco, self.tableVisKpiSo]:
            for i in range(1, table.rowCount()):
                table.hideRow(i)

    def reset_table(self):
        self.hide_visualization_rows()
        for widget in [self.energy_criteria, self.environmental_criteria, self.economic_criteria, self.social_criteria]:
            widget.clear()

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

        self.update_KPIs_visualization_tab()

    def current_item_changed(self, current, previous):
        try:
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
        except:
            return

    def vis_tab3(self):


        self.row_association_En = {1: 1,
                                   2: 2,
                                   3: 7,
                                   4: 8,
                                   5: 13,
                                   6: 14,
                                   7: 19,
                                   8: 20,
                                   9: 23,
                                   10: 24,
                                   11: 27,
                                   12: 28,
                                   13: 31,
                                   14: 32,
                                   15: 35,
                                   16: 37,
                                   17: 40,
                                   18: 42,
                                   19: 44,
                                   20: 46,
                                   21: 48,
                                   22: 50,
                                   23: 52
                                  }

        self.row_association_Env = {1: 1,
                                    2: 2,
                                    3: 6,
                                    4: 7,
                                    5: 11,
                                    6: 12,
                                    7: 16
                                }

        self.row_association_Eco = {1: 5}

        self.row_association_So = {1: 1,
                                   2: 4,
                                   3: 7}

        for t in [self.step2_energy_tab]:
            for i in range(t.rowCount()):
                try:
                    item = t.item(i, 5)
                    item1 = t.item(i, 4)
                    item2 = t.item(i, 3)
                    callVis = QTableWidgetItem(str(item.text()))
                    callVisR = QTableWidgetItem(str(item1.text()))
                    callVisT = QTableWidgetItem(str(item2.text()))
                    try:

                        self.tableVisKpiEn.setItem(self.row_association_En[i], 5, callVis)
                        self.tableVisKpiEn.setItem(self.row_association_En[i], 4, callVisR)
                        self.tableVisKpiEn.setItem(self.row_association_En[i], 3, callVisT)

                    except:
                        pass
                except:
                    pass

        for t in [self.step2_environmental_tab]:
            for i in range(t.rowCount()):
                try:
                    item = t.item(i, 5)
                    item1 = t.item(i, 4)
                    item2 = t.item(i, 3)
                    callVis = QTableWidgetItem(str(item.text()))
                    callVisR = QTableWidgetItem(str(item1.text()))
                    callVisT = QTableWidgetItem(str(item2.text()))
                    try:

                        self.tableVisKpiEnv.setItem(self.row_association_Env[i], 5, callVis)
                        self.tableVisKpiEnv.setItem(self.row_association_Env[i], 4, callVisR)
                        self.tableVisKpiEnv.setItem(self.row_association_Env[i], 3, callVisT)

                    except:
                        pass
                except:
                    pass

    def load_table(self):
        for t in [self.step2_energy_tab]:
            for i in range(t.rowCount()):
                try:
                    item = t.item(i, 5)
                    item1 = t.item(i, 4)
                    item2 = t.item(i, 3)
                    call = QTableWidgetItem(str(item.text()))
                    call1 = QTableWidgetItem(str(item1.text()))
                    call2 = QTableWidgetItem(str(item2.text()))

                    try:
                        self.tableEnStep3.setItem(i, 5, call)
                        self.tableEnStep3.setItem(i, 4, call1)
                        self.tableEnStep3.setItem(i, 3, call2)

                    except:
                        pass
                except:
                        pass

        for z in [self.step2_environmental_tab]:
            for j in range(z.rowCount()):
                try:
                    itemENV = z.item(j, 5)
                    itemENVt = z.item(j, 4)
                    itemENVr = z.item(j, 3)
                    val = QTableWidgetItem(str(itemENV.text()))
                    valt = QTableWidgetItem(str(itemENVt.text()))
                    valr = QTableWidgetItem(str(itemENVr.text()))

                    try:
                        self.tableENVStep3.setItem(j, 5, val)
                        self.tableENVStep3.setItem(j, 4, valt)
                        self.tableENVStep3.setItem(j, 3, valr)

                    except:
                        pass
                except:
                    pass


        for p in [self.step2_social_tab]:
            for k in range(p.rowCount()):
                try:
                    itemSo = p.item(k, 5)
                    itemSot = p.item(k, 4)
                    itemSor = p.item(k, 3)

                    valSo = QTableWidgetItem(str(itemSo.text()))
                    valSot = QTableWidgetItem(str(itemSot.text()))
                    valSor = QTableWidgetItem(str(itemSor.text()))

                    valSoVis = QTableWidgetItem(str(itemSo.text()))
                    valSotVist = QTableWidgetItem(str(itemSot.text()))
                    valSorVisr = QTableWidgetItem(str(itemSor.text()))
                    try:
                        self.tableSoStep3.setItem(k, 5, valSo)
                        self.tableSoStep3.setItem(k, 4, valSot)
                        self.tableSoStep3.setItem(k, 3, valSor)

                        self.tableVisKpiSo.setItem(self.row_association[k], 5, valSoVis)
                        self.tableVisKpiSo.setItem(self.row_association[k], 4, valSotVist)
                        self.tableVisKpiSo.setItem(self.row_association[k], 3, valSorVisr)

                    except:
                        pass
                except:
                    pass

        for table in [self.tableVisKpiSo, self.tableVisKpiEco, self.tableVisKpiEnv, self.tableVisKpiEn]:
            for i in range(1, table.rowCount()):

                for j in range(1, table.columnCount()-1):

                    item = table.item(i, j)
                    if item is not None:
                        if not item.text() == "":
                            item.setFlags(Qt.ItemIsEnabled)
                        else:
                            item.setFlags(Qt.ItemIsEnabled)
                            item.setBackground(QBrush(QColor(Qt.darkGray)))
                    else:
                        item = QTableWidgetItem()
                        item.setFlags(Qt.ItemIsEnabled)
                        item.setBackground(QBrush(QColor(Qt.darkGray)))
                        table.setItem(i, j, item)

        for table in [self.tableEnStep3, self.tableENVStep3, self.tableEcoStep3, self.tableSoStep3]:
            for i in range(1, table.rowCount()):
                for j in range(1, table.columnCount()):
                    item = table.item(i, j)
                    if item is not None:
                        if not item.text() == "":
                            item.setFlags(Qt.ItemIsEnabled)
                        else:
                            item.setFlags(Qt.ItemIsEnabled)
                            item.setBackground(QBrush(QColor(Qt.darkGray)))
                    else:
                        item = QTableWidgetItem()
                        item.setFlags(Qt.ItemIsEnabled)
                        item.setBackground(QBrush(QColor(Qt.darkGray)))
                        table.setItem(i, j, item)

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
        if cod == "EN9":
            self.weights[13] = value
        if cod == "SO2":
            self.weights[14] = value
        if cod == "SO1":
            self.weights[15] = value
        self.refresh_vito_report()

    def refresh_vito_report(self):
        tables = prioritization_algorithm(self.weights)
        tables_dict = {"Space heating high temperature": self.tableWidgetp,
                       "Space heating medium temperature": self.tableWidget_2p,
                       "Space heating low temperature": self.tableWidget_3p,
                       "Domestic hot water": self.tableWidget_4p,
                       "Space cooling": self.tableWidget_5p
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

        # self.Check_of_planningcriteria()

    def Check_of_planningcriteria(self):
        self.list_PlanningCriteria_energy = {'EN1: Reduction of primary energy consumption': [1, 2, 3, 4, 5, 6],#[0]
                                         'EN2: Reduction of final energy consumption': [7, 8, 9, 10, 11, 12],#[1]
                                         'EN3: Reduction of useful energy demand': [13, 14, 15, 16, 17, 18],#[2]
                                         'EN4: Increase share of renewable energy sources': [19, 20, 21, 22],#[3]
                                         'EN5: Increase utilization of energy from waste heat sources': [23, 24, 25, 26],#[4]
                                         'EN6: Reduction of energy consumption from conventional fuels': [27, 28, 29, 30],#[5]
                                         'EN7: Reduction of energy consumption  from Imported Sources': [31, 32, 33, 34],#[6]
                                         'EN9: Cooling penetration': [35, 36],#[7]
                                         'EN11: Solar thermal penetration': [37, 38, 39],#[8]
                                         'EN12: Use of local sources': [40, 41],#[9]
                                         'EN13a:  DHN thermal losses reduction': [42, 43],#[10]
                                         'EN13b: DCN thermal losses reduction': [44, 45],#[11]
                                         'EN14a: DHN heat density reduction': [46, 47],#[12]
                                         'EN14b: DCN heat density reduction': [48, 49],#[13]
                                         'EN15: Operating hours increase': [50, 51]}#[14]

        self.list_PlanningCriteria_evairmental ={'ENV1: CO2 reduction':[1, 2, 3, 4, 5, 6],#[0]
                                                 'ENV2: Pollutants emission reduction':[7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21] ,#[1]
                                                 'ENV3: Noise pollution reduction': [22, 23]}#[2]

        self.list_PlanningCriteria_economic= {'ECO1: Creation of economically feasible H&C scenarios':[1, 2, 3, 4],#[0]
                                              'ECO2: Operational costs reduction':[5, 6, 7],#[1]
                                              'ECO3: Levelised cost of heat':[8],#[2]
                                              'ECO4: CO2 reduction cost':[9]}#[3]

        self.list_PlanningCriteria_social ={'SO1: Energy poverty reduction':[1, 2],#[0]
                                            'SO2: Job increase':[3, 4],#[1]
                                            'SO3: Security of supply increase':[5, 6]}#[2]
        righe_En = []
        for i in [self.energy_criteria]:
             for j in [self.list_PlanningCriteria_energy[i]]:
                righe_En.append(j)


        for i in range(self.tableVisKpiEn.rowCount()-1, -1, -1):
            if i in righe_En:

                pass
            else:
                self.tableVisKpiEn.remove(i)

        righe_Env = []
        for l in [self.environmental_criteria]:
            for k in self.list_PlanningCriteria_evairmental[l]:
                righe_Env.append(k)

        for l in range(self.tableVisKpiEnv.rowCount()-1, -1, -1):
            if l in righe_Env:
                pass
            else:
                self.tableVisKpiEn.remove(l)


    def recive_tab_sources(self, step0_sources_availability_tab):

        table =step0_sources_availability_tab

        list_valx=[]
        list_valy=[]

        for i in range(table.rowCount()):
            val = table.item(i, 0).text()
            val2 = float(table.item(i, 1).text())
            if val2 > 0:
                list_valy.append(val2)
                val = table.item(i, 0).text()
                if val == "Geothermal - Shallow - Ground heat extraction":
                    val = "G.Sh_Ground heat extraction"
                if val=="Geothermal - Shallow - Ground cold extraction":
                    val ="G.Sh_Ground cold extraction"
                list_valx.append(val)


        # self.ax.margins(0, 0.15)
        # self.plot.figure.tight_layout()  # funziona ma brutto hdfhhhfhh
        # self.ax.plot(list_valx, list_valy)
        # self.plot.draw()

    def set_table_flags(self):
        energy_not_editable = [1, 2, 7, 8, 13, 14, 19, 20, 23, 24, 27, 28, 31, 32, 35, 37, 39, 41, 43, 45,
                               47, 49]
        self.set_table_flags_target(self.tableVisKpiEn, energy_not_editable)
        environmental_not_editable = [1, 2, 6, 7, 11, 12, 16, 17, 21]
        self.set_table_flags_target(self.tableVisKpiEnv, environmental_not_editable)
        economic_not_editable = []
        self.set_table_flags_target(self.tableVisKpiEco, economic_not_editable)
        social_not_editable = []
        self.set_table_flags_target(self.tableVisKpiSo, social_not_editable)

    def set_table_flags_target(self, table, not_editable):
        for i in range(table.rowCount()):
            for j in range(table.columnCount()):
                item = table.item(i, j)
                if item is None:
                    item = QTableWidgetItem()
                    table.setItem(i, j, item)
                if j == 6 and i not in not_editable:
                    table.item(i, j).setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)
                else:
                    table.item(i, j).setFlags(Qt.ItemIsEnabled)

    def format_tables(self):
        for i in range(self.tableVisKpiEn.rowCount()):
            for j in range(3):
                try:
                    self.tableVisKpiEn.item(i, j).font().setPointSize(7)
                except:
                    pass
