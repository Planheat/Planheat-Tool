from PyQt5 import QtWidgets, uic
# Import PyQt5
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
# Import the custom tree widget items
from .technology.Technology import *
from .VITO.Prioritization_algorithm import *

from .utility.data_manager.PlanningCriteriaTransfer import PlanningCriteriaTransfer
from .utility.filters.FECvisualizerService import FECvisualizerService
from .config.PlanningCriteriaHelper import PlanningCriteriaHelper

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
        # self.resetTargets.clicked.connect(self.reset_table)

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

        self.planning_criteria_helper = PlanningCriteriaHelper()

        self.set_table_flags()

        self.criteria_transfer = PlanningCriteriaTransfer(self.energy_criteria, self.environmental_criteria,
                                                          self.economic_criteria, self.social_criteria)
        self.format_tables()
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(0)
        self.tableEnStep3.hideRow(3)
        self.tableEnStep3.hideRow(4)
        self.fec_visualizer_service = FECvisualizerService(self.output_table, self.fec_filter_combo_box,
                                                           self.description_filter_label, mode="baseline")
        for i in range(self.tableEcoStep3.rowCount()):
            if i not in [0, 5]:
                self.tableEcoStep3.hideRow(i)

    def load_scv(self, data):
        self.data = data

    def itemSelection(self, item, column):
        p = item.text(column)
        help_text = self.planning_criteria_helper.insert_text_help(p)
        if not isinstance(help_text, str):
            print("Step3.itemSelection(): help is not a string", type(help_text))
        else:
            self.helpText.setText(help_text)
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
        criterion_to_rows = {"EN1": [1, 2, 3, 4, 5, 6, 7],
                             "EN2": [8, 9, 10, 11, 12, 13],
                             "EN3": [14, 15, 16, 17, 18, 19, 20],
                             "EN4": [21, 22, 23, 24],
                             "EN5": [25, 26, 27, 28],
                             "EN6": [29, 30, 31, 32],
                             "EN7": [33, 34, 35, 36],
                             "EN9": [37, 38],
                             "EN11": [39, 40, 41],
                             "EN12": [42, 43],
                             "EN13a": [44, 45, 10, 11, 12, 13],
                             "EN13b": [46, 47],
                             "EN14a": [48, 49],
                             "EN14b": [50, 51],
                             "EN15": [52, 53],
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
                        print(criteria, row)
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
                                   3: 8,
                                   4: 9,
                                   5: 15,
                                   6: 16,
                                   7: 21,
                                   8: 22,
                                   9: 25,
                                   10: 26,
                                   11: 29,
                                   12: 30,
                                   13: 33,
                                   14: 34,
                                   15: 37,
                                   16: 39,
                                   17: 42,
                                   18: 44,
                                   19: 46,
                                   20: 48,
                                   21: 50,
                                   22: 52,
                                   23: 54
                                  }

        self.row_association_Env = {1: 1,
                                    2: 2,
                                    3: 7,
                                    4: 8,
                                    5: 13,
                                    6: 14,
                                    7: 19,
                                    8: 20,
                                    9: 25
                                }

        self.row_association_Eco = {5: 5}

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

        for i in range(self.step2_economic_tab.rowCount()):
            for tb in [self.tableVisKpiEco, self.tableEcoStep3]:
                try:
                    tb.setItem(self.row_association_Eco[i], 5, self.step2_economic_tab.item(i, 5).clone())
                    tb.setItem(self.row_association_Eco[i], 4, self.step2_economic_tab.item(i, 4).clone())
                    tb.setItem(self.row_association_Eco[i], 3, self.step2_economic_tab.item(i, 3).clone())
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
        energy_not_editable = [1, 2, 8, 9, 15, 16, 21, 22, 25, 26, 29, 30, 33, 34, 37, 39, 41, 43, 45, 47,
                               49, 51]
        self.set_table_flags_target(self.tableVisKpiEn, energy_not_editable)
        environmental_not_editable = [1, 2, 7, 8, 13, 14, 19, 20, 25]
        self.set_table_flags_target(self.tableVisKpiEnv, environmental_not_editable)
        economic_not_editable = [5]
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

    def receive_KPIs(self, KPIs):
        self.fec_visualizer_service.set_KPIs(KPIs)
