import os
import os.path
from PyQt5 import uic, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QVariant, Qt
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from .load_to_table import insert_toTable
from .load_to_table import insert_toTableCool
from .src.qt_utils import copy_table
from .load_to_table import calcola_tot
from .load_to_table import copy_table
from .updataTableKpi import tab_not_editable
from .config import tableConfig
from .src.qt_utils import auto_add_percent_symbol
from .src.results.ResultWriter import ResultWriter




FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'city_step2.ui'))


class CityStep2Dialog(QtWidgets.QDockWidget, FORM_CLASS):
    step2_closing_signal = pyqtSignal()
    send = pyqtSignal(QTableWidget, QTableWidget)
    send_corrected_ued = pyqtSignal(list, list, float)

    def __init__(self, iface,work_folder=None, parent=None):
        """Constructor."""
        super(CityStep2Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.work_folder = work_folder
        self.iface = iface

        folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images",
                                 "calculator.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.calculate_dhw.setIcon(icon)
        self.btn_calculate_cool.setIcon(icon)
        self.btn_ued.setIcon(icon)
        self.pushButton.setIcon(icon)
        self.btn_ued_cool.setIcon(icon)

        self.calculate_dhw.clicked.connect(self.future_ued_dhw)
        self.calculate_dhw.clicked.connect(self.read_percent_input)

        self.btn_calculate_cool.clicked.connect(self.future_ued_cool)
        self.btn_calculate_cool.clicked.connect(self.read_table_cool)

        self.btn_ued.clicked.connect(self.prodMix_inputcol3)
        self.pushButton.clicked.connect(self.ued_SBSonly_future)
        self.btn_ued_cool.clicked.connect(self.ued_futurecoolDCN)
        self.ok.clicked.connect(self.send_table)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images",
                                 "open_file.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)

        tab_not_editable(self.table_sd_cool_targ, 3)
        tab_not_editable(self.table_sd_target, 3)
        tab_not_editable(self.table_cool, 4)
        tab_not_editable(self.table_cool, 3)
        tab_not_editable(self.table_dhw_source_targ, 4)
        tab_not_editable(self.table_dhw_source_targ, 3)

        tab_not_editable(self.table_HeDHW_source_targ, 3)
        tab_not_editable(self.table_cool_source, 3)
        self.table_HeDHW_source_targ.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.table_HeDHW_source_targ, i, j))
        self.table_cool_source.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.table_cool_source, i, j))
        self.table_sd_target.cellChanged.connect(lambda i, j: auto_add_percent_symbol(self.table_sd_target,
                                                                                           i, j))
        self.table_dhw_source_targ.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.table_dhw_source_targ, i, j)
        )
        self.table_sd_cool_targ.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.table_sd_cool_targ, i, j))
        self.table_cool.cellChanged.connect(
            lambda i, j: auto_add_percent_symbol(self.table_cool, i, j))
        self.tables_formatted = False

        self.aaa.hide()

        self.list_ued_cool = []
        self.list_ued = []

        self.data_rows = tableConfig.data_rows
        self.data_rows_cool = tableConfig.data_rows_cool
        self.color = QColor(tableConfig.no_imput_rows_color[0],
                            tableConfig.no_imput_rows_color[1],
                            tableConfig.no_imput_rows_color[2])



    def send_table(self):
        self.send.emit(self.table_dhw_source_targ, self.table_cool)
        self.send_corrected_ued.emit(self.list_ued, self.list_ued_cool, self.demoFact_dhw)

    def closeEvent(self, event):
        self.closeStep2()
        event.accept()

    def closeStep2(self):
        self.hide()
        self.step2_closing_signal.emit()

    def read_percent_input_district(self, totUed_tech):
        try:
            table = self.table_sd_target
            self.currItem1 = (table.item(2, 1)).text()
            self.currItem = (table.item(2, 2)).text()
            percent_district = float(self.currItem1.strip(' %')) / 100.0
            percend_sb = float(self.currItem.strip(' %')) / 100.0

            self.sbs_ued = round((totUed_tech * percend_sb), 2)
            self.dist = round((totUed_tech * percent_district), 2)

            cellr = QTableWidgetItem(str(self.sbs_ued))
            cellr.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(1, 3, cellr)
            self.total_dhw_source.setItem(1, 4, cellr)

            cellr = QTableWidgetItem(str(self.dist))
            cellr.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(2, 3, cellr)
            self.total_dhw_source.setItem(1,3, cellr)

            cellr = QTableWidgetItem(str(self.dist + self.sbs_ued))
            cellr.setFlags(QtCore.Qt.ItemIsEnabled)
            table.setItem(3, 3, cellr)

            table.setItem(3, 2, QTableWidgetItem(str((percent_district+percend_sb)*100) + " %"))
            table.item(3, 2).setFlags(QtCore.Qt.ItemIsEnabled)
        except Exception:
            pass


    def read_percent_input(self):
        self.demoFact_dhw = float((self.demoFactor_dhw.value()) / 100.0)
        self.corrective_factor = float((self.envelope_dhw.value()) / 100.0)

        table = self.table_HeDHW_source_targ
        self.lista_perc_input = []
        self.perc_base = []
        self.ued_base=[]
        for i in range(table.rowCount()-1):
            try:
                currItem2 = float((table.item(i, 0)).text())
                self.ued_base.append(currItem2)
                currItem1 = table.item(i, 1).text()
                val_input = float(currItem1.strip(' %'))
                self.perc_base.append(val_input/100)
                currItem = table.item(i, 2).text()
                val_input = float(str(currItem).strip(' %')) #/100
                self.lista_perc_input.append(val_input)
            except (AttributeError, ValueError):
                if i in self.data_rows:
                    self.ued_base.append(0.0)
                    self.perc_base.append(0.0)
                    self.lista_perc_input.append(0.0)


        sumTotperc = round((sum(self.lista_perc_input)), 2)
        tot_sum = QTableWidgetItem(str(sumTotperc))
        tot_sum.setFlags(Qt.ItemIsEnabled)
        if sumTotperc >= 100:
            tot_sum.setForeground(QColor(0, 255, 0))
        else:
            tot_sum.setForeground(QColor(255, 0, 0))
        table.setItem((table.rowCount() - 1), 2, tot_sum)

        self.calculate_corrected_demand()

    def calculate_corrected_demand(self):
        table = self.table_HeDHW_source_targ
        self.list_ued = []
        for i in range(table.rowCount()):
            try:
                ued_base=float((table.item(i,0)).text())
                val = (table.item(i, 2)).text()
                perc_input = float(val.strip(' %')) / 100
                valued = (table.item(i, 1)).text()
                ued = float(valued.strip(' %')) / 100
                ued_fut = (ued_base*(perc_input/ued)*(1+ self.demoFact_dhw-self.corrective_factor))
                ued_fut_arr = round(ued_fut, 2)
                table.setItem(i,3, QTableWidgetItem(str(ued_fut_arr)))
                table.item(i, 3).setFlags(Qt.ItemIsEnabled)
                self.list_ued.append(ued_fut_arr)
            except:
                if i in self.data_rows:
                    self.list_ued.append(0.0)
                    table.setItem(i, 3, QTableWidgetItem(str("0.00")))
                    table.item(i, 3).setFlags(Qt.ItemIsEnabled)

        totUed_base =sum(self.list_ued)
        insert_toTable(self.table_HeDHW_source_targ, 3, self.list_ued)
        table.setItem((table.rowCount() - 1), 3, QTableWidgetItem(str(totUed_base)))
        table.item((table.rowCount() - 1), 3).setFlags(Qt.ItemIsEnabled)

        self.read_percent_input_district(totUed_base)

        self.production_mix_base()

    def production_mix_base(self):

        table = self.table_sd_target
        # self.currItem = (table.item(1, 1)).text()
        # pfact_sbs = float(self.currItem1.strip(' %')) / 100.0

        currItem = (table.item(2, 1)).text()
        pFact_dist = float(currItem.strip(' %')) / 100.0
        currItem = (table.item(2, 2)).text()
        pFact_dist_fut = float(currItem.strip(' %')) / 100.0

        self.ued_sbs = float((table.item(1, 0)).text())
        self.ued_dist = float((table.item(2, 0)).text())

        # tot = pfact_sbs + pFact_dist
        # table.setItem(3, 2, QTableWidgetItem(str(round(tot, 2)) + " %"))

        val_col1=[]
        self.prodMix_baseline = []
        for j in range(self.table_dhw_source_targ.rowCount()):
            try:

                valore=round(((float(self.table_HeDHW_source_targ.item(j, 0).text()))*pFact_dist*100)/self.ued_dist, 2)
                self.table_dhw_source_targ.setItem(j, 1, QTableWidgetItem(str(valore)+ " %"))
                self.table_dhw_source_targ.item(j, 1).setFlags(Qt.ItemIsEnabled)
                self.prodMix_baseline.append(valore)
            except Exception as e:
                print("Step2.py, production mix base():", e)

        tot = sum(self.prodMix_baseline)

        for j in range(self.table_dhw_source_targ.rowCount()):
            try:
                self.table_dhw_source_targ.setItem(j, 0, self.table_HeDHW_source_targ.item(j, 2).clone())
                self.table_dhw_source_targ.item(j, 0).setFlags(Qt.ItemIsEnabled)
                #valore = round(
                #    ((float(self.table_HeDHW_source_targ.item(j, 3).text())) * pFact_dist_fut * 100) / self.ued_dist, 2)
                val1 = float(self.table_dhw_source_targ.item(j, 0).text().strip(" %"))
                val_col1.append(val1)
            except Exception as e:
                if j in self.data_rows:
                    item = QTableWidgetItem()
                    item.setFlags(Qt.ItemIsEnabled)
                    self.table_dhw_source_targ.setItem(j, 0, item)


        totcol1=sum(val_col1)
        self.total_dhw_source.setItem(0, 1, QTableWidgetItem(str(round(tot, 2))))
        self.total_dhw_source.setItem(0, 0, QTableWidgetItem(str(round(totcol1, 2)) + " %"))
        self.total_dhw_source.item(0, 1).setFlags(Qt.ItemIsEnabled)
        self.total_dhw_source.item(0, 0).setFlags(Qt.ItemIsEnabled)

        self.unlock_cells()

    def unlock_cells(self):
        table: QTableWidget = self.table_dhw_source_targ
        for j in range(table.rowCount()):
            table.item(j, 2).setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)


    def prodMix_inputcol3(self):
        prod_perc_input = []
        table = self.table_dhw_source_targ
        for i in range(table.rowCount()):
             try:
                 currItem2 = (table.item(i, 2)).text()
                 val_vero = float(currItem2.strip(' %')) / 100.0
                 prod_perc_input.append(val_vero)
             except (AttributeError, ValueError):
                 if i in self.data_rows:
                     prod_perc_input.append(0.0)

        self.uedFuture_calculate(prod_perc_input)
        tot = sum(prod_perc_input)

        self.total_dhw_source.setItem(0, 2, QTableWidgetItem(str(round(tot, 2))))
        self.total_dhw_source.item(0, 2).setFlags(Qt.ItemIsEnabled)

    def uedFuture_calculate(self, prod_perc_input):

        tab = self.table_sd_target
        dist_ued = float((tab.item(2, 3)).text())

        self.ued_calc_dhn =[]
        for i in prod_perc_input:
            try:
                calc = i * dist_ued
                self.ued_calc_dhn.append(calc)
            except (AttributeError, ValueError):
                pass

        insert_toTable(self.table_dhw_source_targ, 3, self.ued_calc_dhn)

        tot = sum(self.ued_calc_dhn)
        item = QTableWidgetItem(str(round(tot, 2)))
        item.setFlags(Qt.ItemIsEnabled)
        self.total_dhw_source.setItem(0, 3, item)

    def ued_SBSonly_future(self):
        table = self.table_dhw_source_targ
        self.listCol4=[]
        for j in range(table.rowCount()):
            try:
                table.setItem(j, 4, QTableWidgetItem(str(
                    round(float(self.table_HeDHW_source_targ.item(j, 3).text()) - float(table.item(j, 3).text()),
                          2))))
            except Exception as e:
                print("Step2.py, ued_SBSonly_future():", e)
            try:
                valore = float((table.item(j, 4)).text())
                if valore >= 0:
                    table.item(j, 4).setForeground(QColor(0, 255, 0))
                if valore < 0:
                    table.item(j, 4).setForeground(QColor(255, 0, 0))
                self.listCol4.append(valore)
            except Exception as e:
                print("Step2.py, ued_SBSonly_future(): stavo mettendo il foreground, ma è successo qualcosa di male", e)

        tot = sum(self.listCol4)
        self.total_dhw_source.setItem(0, 4, QTableWidgetItem(str(round(tot, 2))))
        self.table_and_check(self.table_dhw_source_targ, self.total_dhw_source,self.table_sd_target)


    def read_table_cool(self):
        self.demoFact_dhw = float((self.demoFact_cool.value()) / 100.0)
        self.corrective_factor = float((self.envelope_cool.value()) / 100.0)
        self.increase =float((self.increase_cool.value()) / 100.0)
        self.list_ued_cool=[]

        table = self.table_cool_source

        for i in range(self.table_cool_source.rowCount()):
            try:
                self.itemB = float(table.item(i, 0).text())

                currItem = table.item(i, 1).text()
                itemC = float(currItem.strip(' %')) / 100

                currIt = (table.item(i, 2)).text()
                itemD = float(currIt.strip(' %')) / 100

                val = (self.itemB * (itemD / itemC) * (1 + self.demoFact_dhw - self.corrective_factor + self.increase))
                table.setItem(i, 3, QTableWidgetItem(str(round(val, 2))))
                table.item(i, 3). setFlags(Qt.ItemIsEnabled)
                self.list_ued_cool.append(val)
            except Exception as e:
                print("Step2.py, read_table_cool():", e)


        tab =self.table_sd_cool_targ
        currIt = tab.item(1, 2).text()
        ssUed = float(currIt.strip(' %')) / 100
        tot_uedcool =sum(self.list_ued_cool)*ssUed
        tab.setItem(1, 3, QTableWidgetItem(str(tot_uedcool)))
        tab.item(1, 3).setFlags(Qt.ItemIsEnabled)

        currIt = (tab.item(2, 2)).text()
        ssUed = float(currIt.strip(' %')) / 100
        tot_uedcool2 = round((sum(self.list_ued_cool) * ssUed), 2)
        tab.setItem(2, 3, QTableWidgetItem(str(tot_uedcool2)))
        tab.setItem(3, 3, QTableWidgetItem(str(tot_uedcool + tot_uedcool2)))
        table.item(2, 3).setFlags(Qt.ItemIsEnabled)
        table.item(3, 3).setFlags(Qt.ItemIsEnabled)

        tot_perc = round((ssUed+ssUed)*100, 2)
        tab.setItem(3, 2, QTableWidgetItem(str(tot_perc) + " %"))
        tab.item(3, 2).setFlags(Qt.ItemIsEnabled)


    def ued_dist_cool(self, totUed_tech):
        table =self.table_sd_cool_targ

        self.currItem1 = (table.item(1, 1)).text()
        self.currItem = (table.item(2, 1)).text()

        val_vero = float(self.currItem1.strip(' %')) / 100.0
        val_input = float(self.currItem.strip(' %')) / 100

        sbs_ued= round((totUed_tech*val_vero), 2)
        dist = round((totUed_tech*val_input), 2)

        cellr = QTableWidgetItem(str(sbs_ued))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(1, 3, cellr)

        cellr = QTableWidgetItem(str(dist))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(2, 3, cellr)

        cellr = QTableWidgetItem(str(dist+sbs_ued))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        table.setItem(3, 3, cellr)

        tot = (val_vero + val_input)*10
        table.setItem(table.rowCount() - 1, 2, QTableWidgetItem(str(tot) + " %"))

    def future_ued_dhw(self):
        copy_table(self.table_HeDHW_source_targ, self.table_dhw_source_targ, 2, 0)
        target = self.table_dhw_source_targ
        ris = calcola_tot(target, 0)
        target.setItem((target.rowCount() - 1), 0, QTableWidgetItem(str(ris)))

    def future_ued_cool(self):
        copy_table(self.table_cool_source, self.table_cool, 2, 0)
        for i in range(self.table_cool.rowCount()):
            if i in self.data_rows_cool:
                self.table_cool.item(i, 0).setFlags(Qt.ItemIsEnabled)
        self.prod_mix_cool()

    def prod_mix_cool(self):
        list_ued_per_tecnology=[]
        table = self.table_cool_source
        for i in range(table.rowCount()-1):
            try:
                val = float((table.item(i, 0)).text())
                list_ued_per_tecnology.append(val)
            except:
                if i in self.data_rows_cool:
                    list_ued_per_tecnology.append(0.0)

        prod_mix_col1 = []
        tot = sum(list_ued_per_tecnology)
        for i in list_ued_per_tecnology:
            prod = round(((i/tot)*100), 2)
            prod_mix_col1.append(prod)

        insert_toTableCool(self.table_cool, 1, prod_mix_col1)

        tot = sum(prod_mix_col1)
        self.total_cool_source.setItem(0, 1, QTableWidgetItem(str(round(tot))))
        self.total_cool_source.item(0, 1).setFlags(Qt.ItemIsEnabled)

        tab = self.table_cool
        lista=[]
        for i in range(tab.rowCount()):
            try:
                val = float((tab.item(i, 0)).text().strip(' %'))
                val_vero = val / 100.0
                lista.append(val_vero)
            except:
                if i in self.data_rows_cool:
                    lista.append(0.0)

        tot = sum(lista)
        self.total_cool_source.setItem(0, 0, QTableWidgetItem(str(round(tot*100))))
        self.total_cool_source.item(0, 0,).setFlags(Qt.ItemIsEnabled)

        for i in range(self.table_cool.rowCount()):
            if i in self.data_rows_cool:
                self.table_cool.item(i, 2).setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable)

    def ued_futurecoolDCN(self):
        table = self.table_sd_cool_targ
        tab = self.table_cool
        dist_ued = float((table.item(2, 3)).text())
        listCol3=[]
        listCol2=[]
        for i in range(tab.rowCount()):
            try:
                currItem = (tab.item(i, 2)).text()
                val_vero = round((float(currItem.strip(' %')) / 100.0),2)
                calc =round((dist_ued * val_vero), 2)
                listCol3.append(calc)
                listCol2.append(val_vero)
            except (AttributeError, ValueError):
                if i in self.data_rows_cool:
                    listCol3.append(0.0)
                    listCol2.append(0.0)
        tab = self.table_cool
        insert_toTableCool(tab, 3, listCol3)

        tot = sum(listCol3)
        tot2 = sum(listCol2)

        self.total_cool_source.setItem(0, 3, QTableWidgetItem(str(round(tot, 2))))
        self.total_cool_source.item(0, 3).setFlags(Qt.ItemIsEnabled)
        self.total_cool_source.setItem(0, 2, QTableWidgetItem(str(round(tot2, 2))))
        self.total_cool_source.item(0, 2).setFlags(Qt.ItemIsEnabled)

        self.ued_sbs_future()
        self.table_and_check(self.table_cool, self.total_cool_source, self.table_sd_cool_targ)

    def ued_sbs_future(self):
        table =self.table_cool
        self.ued_sbs_col4 = []
        for j in range(table.rowCount()):
            try:
                table.setItem(j, 4, QTableWidgetItem(str(
                    round(float(self.table_cool_source.item(j,3).text()) - float(table.item(j, 3).text()),
                          2))))
            except Exception as e:
                print("Step2.py, ued_sbs_future():", e)
            try:
                valore = float((table.item(j, 4)).text())
                if valore >= 0:
                    table.item(j, 4).setForeground(QColor(0, 255, 0))
                if valore < 0:
                    table.item(j, 4).setForeground(QColor(255, 0, 0))
                self.ued_sbs_col4.append(valore)
            except Exception as e:
                print("Step2.py, ued_sbs_future(): stavo mettendo il foreground, ma è successo qualcosa di male", e)

        tot = sum(self.ued_sbs_col4)
        self.total_cool_source.setItem(0, 4, QTableWidgetItem(str(round(tot, 2))))

    def table_and_check(self, tab_list, tab_tot, tab_ued):
        table = tab_list
        table_tot = tab_tot

        val =100
        refCol3 = float((tab_ued.item(1, 3)).text())
        refCol4 = float((tab_ued.item(2, 3)).text())

        table_tot.setItem(1, 0, QTableWidgetItem(str(round(val, 2)) + " %"))
        table_tot.setItem(1, 1, QTableWidgetItem(str(round(val, 2)) + " %"))
        table_tot.setItem(1, 2, QTableWidgetItem(str(round(val, 2)) + " %"))
        table_tot.setItem(1, 3, QTableWidgetItem(str(round(refCol3, 2))))
        table_tot.setItem(1, 4, QTableWidgetItem(str(round(refCol4, 2))))

        stillCol0 =float(table_tot.item(0, 0).text().strip(" %")) - val
        stillCol1 =float(table_tot.item(0, 1).text()) - val
        stillCol2 =float(table_tot.item(0, 2).text()) - val
        stillCol3 =float(table_tot.item(0, 3).text()) - refCol3
        stillCol4 =float(table_tot.item(0, 4).text()) - refCol4
        table_tot.setItem(2, 0, QTableWidgetItem(str(round(stillCol0, 2))))
        table_tot.setItem(2, 1, QTableWidgetItem(str(round(stillCol1, 2))))
        table_tot.setItem(2, 2, QTableWidgetItem(str(round(stillCol2, 2))))
        table_tot.setItem(2, 3, QTableWidgetItem(str(round(stillCol3, 2))))
        table_tot.setItem(2, 4, QTableWidgetItem(str(round(stillCol4, 2))))

        if stillCol0 == float(0.0) or stillCol1 == float(0.0) or stillCol2 == float(0.0) or stillCol3 == float(0.0) or stillCol4 == float(0.0):
            val = "ok!"
            table_tot.setItem(3, 0, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 1, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 2, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 3, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 4, QTableWidgetItem(str(val)))
            table_tot.item(3, 0).setForeground(QColor(0, 255, 0))
            table_tot.item(3, 1).setForeground(QColor(0, 255, 0))
            table_tot.item(3, 2).setForeground(QColor(0, 255, 0))
            table_tot.item(3, 3).setForeground(QColor(0, 255, 0))
            table_tot.item(3, 4).setForeground(QColor(0, 255, 0))
        else:
            val = " Wrong!"
            table_tot.setItem(3, 0, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 1, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 2, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 3, QTableWidgetItem(str(val)))
            table_tot.setItem(3, 4, QTableWidgetItem(str(val)))
            table_tot.item(3, 0).setForeground(QColor(255, 0, 0))
            table_tot.item(3, 1).setForeground(QColor(255, 0, 0))
            table_tot.item(3, 2).setForeground(QColor(255, 0, 0))
            table_tot.item(3, 3).setForeground(QColor(255, 0, 0))
            table_tot.item(3, 4).setForeground(QColor(255, 0, 0))

    def format_tables(self):
        flag = QtCore.Qt.ItemIsEnabled
        empty_item = QTableWidgetItem()
        empty_item.setFlags(flag)
        if self.tables_formatted:
            return
        self.format_table_rows(self.table_HeDHW_source_targ, [1, 6, 12, 15, 17, 19, 21, 23, 26])
        self.format_table_rows(self.table_dhw_source_targ, [1, 6, 12, 15, 17, 19, 21, 23, 26])
        self.format_table_rows(self.table_cool_source, [1, 5, 9, 11, 13])
        self.format_table_rows(self.table_cool, [1, 5, 9, 11, 13])
        self.table_sd_target.setItem(3, 2, empty_item.clone())
        self.table_sd_cool_targ.setItem(3, 2, empty_item.clone())
        # self.table_sd_cool_targ.item(2, 2).setFlags(Qt.ItemIsEnabled)
        for table in [self.table_sd_cool_targ, self.table_sd_target]:
            for i in range(table.columnCount()):
                table.item(0, i).setFlags(Qt.NoItemFlags)

        self.tables_formatted = True

    def format_table_rows(self, table: QTableWidget, rows: list):
        for row in rows:
            for i in range(table.columnCount()):
                try:
                    table.item(row, i).setBackground(QBrush(self.color))
                    table.item(row, i).setFlags(Qt.NoItemFlags)
                except Exception:
                    new_item = QTableWidgetItem()
                    new_item.setBackground(QBrush(self.color))
                    new_item.setFlags(Qt.NoItemFlags)
                    table.setItem(row, i, new_item)
        for i in range(table.rowCount()):
            if i not in rows:
                try:
                    len_text = len(table.item(i, 0).text())
                except:
                    len_text = 0
                if not len_text > 0:
                    for j in range(table.columnCount()):
                        new_item = QTableWidgetItem()
                        new_item.setFlags(Qt.NoItemFlags)
                        table.setItem(i, j, new_item)



