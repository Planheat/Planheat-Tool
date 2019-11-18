import os
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSignal, QVariant
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


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

    def send_table_toSim(self):
        self.send_toSim.emit(self.sbs_hdhw_Source, self.sbs_cool_source)

    def load_step3(self):
        self.loadCity.refresh_file_selection_combo_box(3)
        self.loadCity.run(3)