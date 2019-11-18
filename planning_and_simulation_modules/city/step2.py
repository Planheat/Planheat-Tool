import os
import os.path
from PyQt5 import uic, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QVariant
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from .load_to_table import insert_toTable
from .load_to_table import insert_toTableCool
from .src.qt_utils import copy_table
from .load_to_table import calcola_tot
from .load_to_table import copy_table
from .updataTableKpi import tab_not_editable




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

        self.btn_calculate_cool.clicked.connect(self.future_ued_cool)
        self.calculate_dhw.clicked.connect(self.future_ued_dhw)
        self.calculate_dhw.clicked.connect(self.read_percent_input)
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
        table = self.table_sd_target
        self.currItem1 = (table.item(1, 2)).text()
        self.currItem = (table.item(2, 2)).text()
        val_vero = float(self.currItem1.strip(' %')) / 100.0
        val_input = float(self.currItem.strip(' %')) / 100

        self.sbs_ued = round((totUed_tech * val_vero), 2)
        self.dist = round((totUed_tech * val_input), 2)

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

        val = (val_vero+val_input)*1000
        table.setItem(3, 2, QTableWidgetItem(str(val) + " %"))



    def read_percent_input(self):
        self.demoFact_dhw = float((self.demoFactor_dhw.value()) / 100.0)
        self.corrective_factor = float((self.envelope_dhw.value()) / 100.0)

        table = self.table_HeDHW_source_targ
        self.lista_perc_input = []
        self.perc_base = []
        self.ued_base=[]
        for i in range(table.rowCount()):
            try:
                self.currItem2 = float((table.item(i, 0)).text())
                self.ued_base.append(self.currItem2)
            except (AttributeError, ValueError):
                pass

        for j in range(table.rowCount()):
            try:
                self.currItem1 =(table.item(j, 1)).text()
                self.currItem = (table.item(j, 2)).text()
                val_vero = float(self.currItem1.strip(' %')) / 100
                val_input = float(self.currItem.strip(' %')) #/100
                self.perc_base.append(val_vero)
                self.lista_perc_input.append(val_input)
            except:
                pass

        sumTot = sum(self.perc_base)


        sumTotperc = round((sum(self.lista_perc_input)), 2)
        tot_sum = QTableWidgetItem(str(sumTotperc))
        if sumTotperc >= 100:
            tot_sum.setForeground(QColor(0, 255, 0))
        else:
            tot_sum.setForeground(QColor(255, 0, 0))
        table.setItem((table.rowCount() - 1), 2, tot_sum)

        self.calculate_corrected_demand()

    def calculate_corrected_demand(self):
        table = self.table_HeDHW_source_targ
        self.list_ued=[]
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
                self.list_ued.append(ued_fut_arr)
            except:
                pass

        totUed_base =sum(self.list_ued)
        insert_toTable(self.table_HeDHW_source_targ, 3, self.list_ued)
        table.setItem((table.rowCount() - 1), 3, QTableWidgetItem(str(totUed_base)))

        self.read_percent_input_district(totUed_base)

        self.production_mix_base()

    def production_mix_base(self):

        table = self.table_sd_target
        self.currItem = (table.item(1, 1)).text()
        pfact_sbs = float(self.currItem1.strip(' %')) / 100.0

        self.currItem = (table.item(2, 1)).text()
        pFact_dist = float(self.currItem1.strip(' %')) / 100.0

        self.ued_sbs = float((table.item(1, 0)).text())
        self.ued_dist = float((table.item(2, 0)).text())

        tot = pfact_sbs + pFact_dist
        table.setItem(3, 2, QTableWidgetItem(str(round(tot, 2)) + " %"))

        val_col1=[]
        self.prodMix_baseline = []
        for j in range(self.table_dhw_source_targ.rowCount()):
            try:

                valore=round(((float(self.table_HeDHW_source_targ.item(j, 0).text()))*pFact_dist)/self.ued_dist, 2)
                self.table_dhw_source_targ.setItem(j, 1, QTableWidgetItem(str(valore)+ " %"))
                self.prodMix_baseline.append(valore)
            except Exception as e:
                print("Step2.py, production mix base():", e)

        tot = sum(self.prodMix_baseline)

        for j in range(self.table_dhw_source_targ.rowCount()):
            try:
                val1 = float(self.table_dhw_source_targ.item(j, 0).text())
                val_col1.append(val1)
            except Exception as e:
                pass

        totcol1=sum(val_col1)
        self.total_dhw_source.setItem(0, 1, QTableWidgetItem(str(round(tot, 2))))
        self.total_dhw_source.setItem(0, 0, QTableWidgetItem(str(round(totcol1, 2))))


    def prodMix_inputcol3(self):
        prod_perc_input = []
        table = self.table_dhw_source_targ
        for i in range(table.rowCount()):
             try:
                 self.currItem2 = (table.item(i, 2)).text()
                 val_vero = float(self.currItem2.strip(' %')) / 100.0
                 prod_perc_input.append(val_vero)
             except (AttributeError, ValueError):
                pass

        self.uedFuture_calculate(prod_perc_input)
        tot = sum(prod_perc_input)

        self.total_dhw_source.setItem(0, 2, QTableWidgetItem(str(round(tot, 2))))

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
        self.total_dhw_source.setItem(0, 3, QTableWidgetItem(str(round(tot, 2))))

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
                self.list_ued_cool.append(val)
            except Exception as e:
                print("Step2.py, read_table_cool():", e)


        tab =self.table_sd_cool_targ
        currIt = tab.item(1, 2).text()
        ssUed = float(currIt.strip(' %')) / 100
        tot_uedcool =sum(self.list_ued_cool)*ssUed
        tab.setItem(1, 3, QTableWidgetItem(str(tot_uedcool)))

        currIt = (tab.item(2, 2)).text()
        ssUed = float(currIt.strip(' %')) / 100
        tot_uedcool2 = round((sum(self.list_ued_cool) * ssUed), 2)
        tab.setItem(2, 3, QTableWidgetItem(str(tot_uedcool2)))
        tab.setItem(3, 3, QTableWidgetItem(str(tot_uedcool + tot_uedcool2)))

        tot_perc = round(ssUed+ssUed, 2)
        tab.setItem(3, 2, QTableWidgetItem(str(tot_perc) + " %"))



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
        self.prod_mix_cool()

    def prod_mix_cool(self):

        list_ued_per_tecnology=[]
        table = self.table_cool_source
        for i in range(table.rowCount()-1):
            try:
                val = float((table.item(i, 0)).text())
                list_ued_per_tecnology.append(val)
            except:
                pass

        prod_mix_col1 = []
        tot = sum(list_ued_per_tecnology)
        for i in list_ued_per_tecnology:
            prod = round(((i/tot)*100), 2)
            prod_mix_col1.append(prod)

        insert_toTableCool(self.table_cool, 1, prod_mix_col1)

        tot = sum(prod_mix_col1)
        self.total_cool_source.setItem(0, 1, QTableWidgetItem(str(round(tot, 2))))


        tab = self.table_cool
        list=[]
        for i in range(tab.rowCount()):
            try:
                val = float((tab.item(i, 0)).text())
                val_vero = float(val.strip(' %')) / 100.0
                list.append(val_vero)
            except:
                pass

        tot = sum(list)
        self.total_cool_source.setItem(0, 0, QTableWidgetItem(str(round(tot, 2))))

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
                listCol2.append(val_vero)
                calc =round((dist_ued * val_vero), 2)
                listCol3.append(calc)
            except (AttributeError, ValueError):
                 pass
        tab = self.table_cool
        insert_toTableCool(tab, 3, listCol3)

        tot = sum(listCol3)
        tot2 = sum(listCol2)

        self.total_cool_source.setItem(0, 3, QTableWidgetItem(str(round(tot, 2))))
        self.total_cool_source.setItem(0, 2, QTableWidgetItem(str(round(tot2, 2))))

        self.ued_sbs_future()
        self.table_and_check(self.table_cool, self.total_cool_source,self.table_sd_cool_targ)

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

    def table_and_check(self,tab_list, tab_tot,tab_ued):
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

        stillCol0 =float(table_tot.item(0, 0).text()) - val
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

    def table_and_check(self,tab_list, tab_tot):
        table = tab_list
        prod_mix_fut=[]
        prod_mix_dhn_base=[]
        prod_mix_dhn_fut=[]
        ued_dhn_fut=[]
        ued_sbs_fut=[]

        table_tot = tab_tot
        for i in range(table.rowCount()):
            try:
                val = float(table.item(i, 0)).text()
                val_vero = float(val.strip(' %')) / 100.0
                prod_mix_fut.append(val_vero)
                print("prod_mix_fut", prod_mix_fut)

                val = float((table.item(i, 1)).text())
               # val_vero = float(val.strip(' %')) / 100.0
                prod_mix_dhn_base.append(val)
                print("prod_mix_dhn_base", prod_mix_dhn_base)

                val = float((table.item(i, 2)).text())
                val_vero = float(val.strip(' %')) / 100.0
                prod_mix_dhn_fut.append(val_vero)
                print("prod_mix_dhn_fut", prod_mix_dhn_fut)

                val = float((table.item(i, 3)).text())
                ued_dhn_fut.append(val)
                print("ued_dhn_fut", ued_dhn_fut)

                val = float((table.item(i, 4)).text())
                ued_sbs_fut.append(val)
                print("ued_sbs_fut", ued_sbs_fut)
            except:
                pass

        print("prod_mix_fut",prod_mix_fut)
        print("prod_mix_dhn_base", prod_mix_dhn_base)
        print("prod_mix_dhn_fut", prod_mix_dhn_fut)
        print("ued_dhn_fut", ued_dhn_fut)
        print("ued_sbs_fut", ued_sbs_fut)

        tot_mix_fut = sum(prod_mix_fut)
        tot_dhn_base = sum(prod_mix_dhn_base)
        tot_dhn_fut =sum(prod_mix_dhn_fut)
        ued_dhn =sum(ued_dhn_fut)
        ued_sbs =sum(ued_sbs_fut)
        table_tot.setItem(0, 0, QTableWidgetItem(str(round(tot_mix_fut, 2)) + " %"))
        table_tot.setItem(0, 1, QTableWidgetItem(str(round(tot_dhn_base, 2)) + " %"))
        table_tot.setItem(0, 2, QTableWidgetItem(str(round(tot_dhn_fut, 2)) + " %"))
        table_tot.setItem(0, 3, QTableWidgetItem(str(round(ued_dhn, 2))))
        table_tot.setItem(0, 4, QTableWidgetItem(str(round(ued_sbs, 2))))

        val =100
        table_tot.setItem(1, 0, QTableWidgetItem(str(round(val, 2)) + " %"))
        table_tot.setItem(1, 1, QTableWidgetItem(str(round(val, 2)) + " %"))
        table_tot.setItem(1, 2, QTableWidgetItem(str(round(val, 2)) + " %"))

        table_tot.setItem(1, 3, QTableWidgetItem(str(round(val, 2))))
        table_tot.setItem(1, 4, QTableWidgetItem(str(round(val, 2))))

        refCol3 = float((table_tot.item(1, 3)).text())
        refCol4 = float((table_tot.item(1, 4)).text())

        stillCol0=sum(prod_mix_fut) - val
        stillCol1 = sum(prod_mix_dhn_base) - val
        stillCol2 = sum(prod_mix_dhn_fut) - val
        stillCol3 =sum(ued_dhn_fut) - refCol3
        stillCol4 =sum(ued_sbs_fut) - refCol4
        table_tot.setItem(2, 0, QTableWidgetItem(str(round(stillCol0, 2))))
        table_tot.setItem(2, 1, QTableWidgetItem(str(round(stillCol1, 2))))
        table_tot.setItem(2, 2, QTableWidgetItem(str(round(stillCol2, 2))))
        table_tot.setItem(2, 3, QTableWidgetItem(str(round(stillCol3, 2))))
        table_tot.setItem(2, 4, QTableWidgetItem(str(round(stillCol4, 2))))

        if stillCol0 == float(0.0) or stillCol1 == float(0.0) or stillCol2==float(0.0) or stillCol3 == float(0.0) or stillCol4==float(0.0):
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


