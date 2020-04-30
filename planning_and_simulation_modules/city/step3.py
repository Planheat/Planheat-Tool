import os
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSignal, QVariant, Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from .config import tableConfig
from .src.qt_utils import auto_add_percent_symbol


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'city_step3.ui'))


class CityStep3Dialog(QtWidgets.QDockWidget, FORM_CLASS):
    step3_closing_signal = pyqtSignal()
    send_toSim = pyqtSignal(QTableWidget, QTableWidget)

    def __init__(self, iface, work_folder=None, parent=None):
        """Constructor."""
        super(CityStep3Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.work_folder = work_folder
        self.iface = iface
        self.ok.clicked.connect(self.send_table_toSim)

        self.data_rows = tableConfig.data_rows
        self.data_rows_cool = tableConfig.data_rows_cool
        self.color = QColor(tableConfig.no_imput_rows_color[0],
                            tableConfig.no_imput_rows_color[1],
                            tableConfig.no_imput_rows_color[2])

        self.sbs_hdhw_Source.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.sbs_hdhw_Source, i, j, allowed_columns=[1, 2]))
        self.dist_hdhw_source.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.dist_hdhw_source, i, j, allowed_columns=[1, 2]))
        self.sbs_cool_source.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.sbs_cool_source, i, j, allowed_columns=[1]))
        self.dist_cool_source.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.dist_cool_source, i, j, allowed_columns=[1]))
        self.tables_formatted = False

    def closeEvent(self, event):
        self.closeStep3()
        event.accept()

    def closeStep3(self):
        self.hide()
        self.step3_closing_signal.emit()

    def load_from_step2(self, table, tab_cool):
        tabStep2 = table
        tabStep3 = self.sbs_hdhw_Source
        tab3dist= self.dist_hdhw_source

        for i in range(tabStep2.rowCount()):
                item = tabStep2.item(i, 3)
                item1 = tabStep2.item(i, 4)
                try:
                    tabStep3.setItem(i, 0, QTableWidgetItem(item1))
                    tab3dist.setItem(i, 0, QTableWidgetItem(item))
                    tabStep3.item(i, 0).setFlags(Qt.ItemIsEnabled)
                    tab3dist.item(i, 0).setFlags(Qt.ItemIsEnabled)
                except:
                    pass

        tab_cool_step2 = tab_cool
        sbs_tab_cool_step3 = self.sbs_cool_source

        for i in range(tab_cool_step2.rowCount()):
                item = tab_cool_step2.item(i, 4)
                itemdist = tab_cool_step2.item(i, 3)
                try:
                    sbs_tab_cool_step3.setItem(i, 0, QTableWidgetItem(item))
                    self.dist_cool_source.setItem(i,0, QTableWidgetItem(itemdist))
                    sbs_tab_cool_step3.item(i, 0).setFlags(Qt.ItemIsEnabled)
                    self.dist_cool_source.item(i, 0).setFlags(Qt.ItemIsEnabled)
                except:
                     pass
        self.calcola_tot()

    def calcola_tot(self):
        list = []
        table = self.sbs_hdhw_Source
        for i in range(table.rowCount()):
            try:
                val = float((table.item(i, 0)).text())
                list.append(val)
            except:
                pass
        tot_input = round((sum(list)), 2)
        table.setItem(table.rowCount() - 1, 0, QTableWidgetItem(str(tot_input)))
        table.item(table.rowCount() - 1, 0).setFlags(Qt.ItemIsEnabled)

        list2=[]
        table = self.sbs_cool_source
        for i in range(table.rowCount()):
            try:
                val = float((table.item(i, 0)).text())
                list2.append(val)
            except:
                pass
        tot_input = round((sum(list2)), 2)
        table.setItem((table.rowCount() - 1), 0, QTableWidgetItem(str(tot_input)))
        table.item(table.rowCount() - 1, 0).setFlags(Qt.ItemIsEnabled)

        self.format_tables()

    def format_tables(self):
        if self.tables_formatted:
            return
        item = QTableWidgetItem()
        brush = QBrush(self.color)
        item.setBackground(brush)
        item.setFlags(Qt.NoItemFlags)
        item_with_no_flags = QTableWidgetItem()
        item_with_no_flags.setFlags(Qt.NoItemFlags)
        item_editable = QTableWidgetItem()
        item_editable.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
        for table in [self.sbs_hdhw_Source, self.dist_hdhw_source]:
            for i in range(1, table.rowCount()-1):
                if i not in self.data_rows:
                    for j in range(table.columnCount()):
                        try:
                            table.item(i, j).setBackground(brush)
                            table.item(i, j).setFlags(Qt.NoItemFlags)
                        except Exception:
                            table.setItem(i, j, item.clone())
                else:
                    try:
                        table.item(i, 0).setFlags(Qt.NoItemFlags)
                    except Exception:
                        table.setItem(i, 0, item_with_no_flags.clone())
                    try:
                        table.item(i, 1).setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
                    except Exception:
                        table.setItem(i, 1, item_editable.clone())
                    try:
                        table.item(i, 2).setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable) if i == 14 else table.item(i,
                                                                                                                  2).setFlags(
                            Qt.NoItemFlags)
                    except Exception:
                        table.setItem(i, 2, item_editable.clone()) if i == 14 else table.setItem(i, 2,
                                                                                               item_with_no_flags.clone())
                    try:
                        table.item(i, 3).setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
                    except Exception:
                        table.setItem(i, 3, item_editable.clone())
        for table in [self.sbs_cool_source, self.dist_cool_source]:
            for i in range(1, table.rowCount()-1):
                if i not in self.data_rows_cool:
                    for j in range(table.columnCount()):
                        try:
                            table.item(i, j).setBackground(brush)
                            table.item(i, j).setFlags(Qt.NoItemFlags)
                        except Exception:
                            table.setItem(i, j, item.clone())
                else:
                    try:
                        table.item(i, 0).setFlags(Qt.NoItemFlags)
                    except Exception:
                        table.setItem(i, 0, item_with_no_flags.clone())
                    try:
                        table.item(i, 1).setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)
                    except Exception:
                        table.setItem(i, 1, item_editable.clone())
        self.tables_formatted = True



    def send_table_toSim(self):
        self.send_toSim.emit(self.sbs_hdhw_Source, self.sbs_cool_source)

    def load_step3(self):
        self.loadCity.refresh_file_selection_combo_box(3)
        self.loadCity.run(3)