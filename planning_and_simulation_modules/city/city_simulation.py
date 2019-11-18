
import os
import pandas as pd
import sys, csv
import codecs
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets


from .load_to_table import calculate_fec
from .load_to_table import insert_toTable
from .KPIsCalculatorCity import KPIsCalculator
from .load_to_table import insert_toTableCool
from .load_to_table import insert_to_source_table
from .load_to_table import updata_dic
from .load_to_table import Qdialog_save_file
from .KPIsCalculatorCity import KPIsCalculator
from .updataTableKpi import update_KPIs_visualization_tab


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'city_sim.ui'))


class CitySimulation(QtWidgets.QDockWidget, FORM_CLASS):

    simulation_closing_signal = pyqtSignal()


    def __init__(self, iface, parent=None):
        """Constructor."""
        super(CitySimulation, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface


        self.calculator= KPIsCalculator()
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "images",
                                 "calculator.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.btn_fec.setIcon(icon)
        self.btn_fec_afec.setIcon(icon)
        self.DHCN_heating_fec.setIcon(icon)
        self.DHCN_net_losses.setIcon(icon)
        self.fec_cool_dist.setIcon(icon)
        self.dh_loss_dist.setIcon(icon)
        self.btn_KPIsFuture.setIcon(icon)

        self.btn_fec.clicked.connect(self.calculate_fec)
        self.btn_fec_afec.clicked.connect(self.calculate_fec_cooling)
        self.DHCN_heating_fec.clicked.connect(self.calculate_fec_afec_heating)
        self.DHCN_net_losses.clicked.connect(self.calculate_netLosses)

        self.fec_cool_dist.clicked.connect(self.calculate_fec_afec_cool_net)
        self.dh_loss_dist.clicked.connect(self.calculate_netDHCNLosses_cool)
        self.btn_KPIsFuture.clicked.connect(self.calculate_KPIs_future)
        self.btn_refershKPI.clicked.connect(self.calculate_KPIs_future)
        self.btnExport.clicked.connect(self.export_to_csv)

        self.primary_En_fact = [2.37, 1, 1, 1, 1, 1, 1, 1]
        self.ued_fut = []
        self.dh_losses_cool = []
        self.dh_losses_heating = []
        self.tot_ued_heating = 0
        self.tot_ued_cool = 0
        self.string = None
        self.valString = None
        self.fec_dhcn_cool=[]
        self.fec_cool_district=[]
        self.fec = []
        self.val = 0
        self.valNG = 0
        self.valBiomass = 0
        self.valEl = 0
        self.valWh = 0
        self.valTecEff = 0
        self.valCapex = 0
        self.valS = 0
        self.valSol = 0
        self.ued_fut_cool=[]
        self.demo_factor = 0
        self.grid_lenght=0
        self.baseline_KPIs = {}
        self.target = []
        self.nCol=0
        self.dial.valueChanged.connect(self.sliderMoved)
        self.dial_2.valueChanged.connect(self.sliderMoved)
        self.dial_3.valueChanged.connect(self.sliderMoved)
        self.dial_4.valueChanged.connect(self.sliderMoved)
        self.dial_5.valueChanged.connect(self.sliderMoved)
        self.dial_6.valueChanged.connect(self.sliderMoved)
        self.dial_7.valueChanged.connect(self.sliderMoved)
        self.dial_8.valueChanged.connect(self.sliderMoved)
        self.dial_9.valueChanged.connect(self.sliderMoved)



    def sliderMoved(self):
        self.val = self.dial.value()
        self.valNG = self.dial_2.value()
        self.valBiomass = self.dial_3.value()
        self.valEl = self.dial_4.value()
        self.valWh = self.dial_5.value()
        self.valTecEff = self.dial_6.value()
        self.valCapex = self.dial_7.value()
        self.valS = self.dial_8.value()
        self.valSol = self.dial_9.value()
        self.lineEdit_1.setText(str(self.val))
        self.lineEdit_2.setText(str(self.valNG))
        self.lineEdit_3.setText(str(self.valBiomass))
        self.lineEdit_4.setText(str(self.valEl))
        self.lineEdit_5.setText(str(self.valWh))
        self.lineEdit_6.setText(str(self.valTecEff))
        self.lineEdit_7.setText(str(self.valCapex))
        self.lineEdit_8.setText(str(self.valS))
        self.lineEdit_9.setText(str(self.valSol))

    def closeEvent(self, event):
        self.closeSimulation()
        event.accept()

    def closeSimulation(self):
        self.hide()
        self.simulation_closing_signal.emit()


    def load_from_ste3(self, table, table_cool):
        tabStep3 =table
        tabSim = self.sim_sbs_hdhw_Source
        tab_sim_DHCN = self.dist_heat_source

        for i in range(tabStep3.rowCount()):
                item = tabStep3.item(i, 0)
                item1 = tabStep3.item(i, 1)
                item2 = tabStep3.item(i, 2)
                item3 = tabStep3.item(i, 3)
                try:
                    tabSim.setItem(i, 0, QTableWidgetItem(item))
                    tabSim.setItem(i, 1, QTableWidgetItem(item1))
                    tabSim.setItem(i, 2, QTableWidgetItem(item2))
                    tabSim.setItem(i, 3, QTableWidgetItem(item3))

                    tab_sim_DHCN.setItem(i, 0, QTableWidgetItem(item))
                    tab_sim_DHCN.setItem(i, 1, QTableWidgetItem(item1))
                    tab_sim_DHCN.setItem(i, 2, QTableWidgetItem(item2))
                    tab_sim_DHCN.setItem(i, 3, QTableWidgetItem(item3))
                except:
                    pass


        DHCN_tab_cool_step3 = table_cool
        tab_sbs_cool = self.sim_sbs_cool_source
        DHCN_dist_coll = self.dist_cool_net
        for i in range(DHCN_tab_cool_step3.rowCount()):
                item = DHCN_tab_cool_step3.item(i, 0)
                item1 = DHCN_tab_cool_step3.item(i, 1)

                try:
                    tab_sbs_cool.setItem(i, 0, QTableWidgetItem(item))
                    tab_sbs_cool.setItem(i, 1, QTableWidgetItem(item1))
                    DHCN_dist_coll.setItem(i, 0, QTableWidgetItem(item))
                    DHCN_dist_coll.setItem(i, 1, QTableWidgetItem(item1))

                except:
                    pass


 # SBS solution
    def calculate_fec(self):
        table = self.sim_sbs_hdhw_Source
        self.ued = []
        self.avg_cop = []
        for j in range(table.rowCount()):
            try:
                currItem = float(table.item(j, 0).text())
                self.ued.append(currItem)
            except:
                pass
        for i in range(table.rowCount()):
            try:
                currItem1 = (table.item(i, 1)).text()
                val_vero = float(currItem1.strip(' %')) / 100.0
                self.avg_cop.append(val_vero)
            except:
                pass
        self.fec_cal(self.ued, self.avg_cop)


    def fec_cal(self, ued, avg_cop):
        table = self.sim_sbs_hdhw_Source
        self.fec = []
        for i in ued:
            for j in avg_cop:
                try:
                    val = (i/j)

                except ZeroDivisionError:
                    val = 0.0
            self.fec.append(val)
        insert_toTable(table, 4, self.fec)

        self.fec_hp()

    def fec_hp(self):
        table = self.sim_sbs_hdhw_Source

        avg_air = float(((table.item(3, 1)).text()).strip(' %')) / 100.0
        avg_wast = float(((table.item(4, 1)).text()).strip(' %')) / 100.0
        avg_ground = float(((table.item(5, 1)).text()).strip(' %')) / 100.0
        avg_GAHp = float(((table.item(9, 1)).text()).strip(' %')) / 100.0
        avg_GAHPw = float(((table.item(10, 1)).text()).strip(' %')) / 100.0
        avg_GAHPg = float(((table.item(11, 1)).text()).strip(' %')) / 100.0

        ued_airHp = float(table.item(3, 0).text())
        ued_wast = float(table.item(4, 0).text())
        ued_ground = float(table.item(5, 0).text())
        ued_airGAHP= float(table.item(9, 0).text())
        ued_wastGAHP =float(table.item(10, 0).text())
        ued_ground_GAHP = float(table.item(11, 0).text())

        fec_air=round(((avg_air-1)/avg_air * ued_airHp), 2)
        fec_wast = round(((avg_wast-1)/avg_wast*ued_wast), 2)
        fec_ground = round(((avg_ground - 1) / avg_ground * ued_ground), 2)
        fec_wastG = round(((avg_GAHp - 1) / avg_GAHp * ued_airGAHP), 2)
        fec_airG = round(((avg_GAHPw - 1) / avg_GAHPw * ued_wastGAHP), 2)
        fec_graundG = round(((avg_GAHPg - 1) / avg_GAHPg * ued_ground_GAHP), 2)

        table.setItem(3, 5, QTableWidgetItem(str(fec_air)))
        table.setItem(4, 5, QTableWidgetItem(str(fec_wast)))
        table.setItem(5, 5, QTableWidgetItem(str(fec_ground)))
        table.setItem(9, 5, QTableWidgetItem(str(fec_wastG)))
        table.setItem(10, 5, QTableWidgetItem(str(fec_airG)))
        table.setItem(11, 5, QTableWidgetItem(str(fec_graundG)))


    def calculate_fec_cooling(self):
        table = self.sim_sbs_cool_source
        self.ued = []
        self.avg_cop = []

        for j in range(table.rowCount()):
            try:
                currItem = float((table.item(j, 0)).text())
                self.ued.append(currItem)

                currItem1 = (table.item(j, 1)).text()
                val_vero = float(currItem1.strip(' %')) / 100.0
                self.avg_cop.append(val_vero)
            except:
                pass
        self.fec_calc_cool(self.ued, self.avg_cop)



    def fec_calc_cool(self, ued, avg_cop):
        table = self.sim_sbs_cool_source

        self.fec_cool = []
        self.list_hp_cool = []
        val=0
        hp_cool=0
        for i in ued:
            for j in avg_cop:
                val = round((i / j), 2)
                hp_cool = round((i-1)/(i*j), 2)
            self.fec_cool.append(val)
            self.list_hp_cool.append(hp_cool)

        insert_toTableCool(table, 2, self.fec_cool)
        insert_toTableCool(table, 3,  self.list_hp_cool)


    def calculate_fec_afec_heating(self):
        table = self.dist_heat_source
        share_heating = self.share_heat.value()
        share_dhw = self.share.value()
        self.heat_grid_lenght = self.leng.value()
        self.ued =[]
        self.avg_cop=[]
        self.fec_dhcn = []
        for i in range(table.rowCount()):
            try:
                currItem = float((table.item(i, 0)).text())
                self.ued.append(currItem)
            except:
                pass
        self.Col1Tab2()

    def Col1Tab2(self):
        table = self.dist_heat_source
        gridEfficency = float(self.eff.value())/1000
        for j in range(table.rowCount()):
            try:
                currItem1 = (table.item(j, 1)).text()
                val_vero = float(currItem1.strip(' %')) / 100.0
                self.avg_cop.append(val_vero)
            except:
                pass
        for k in self.ued:
            try:
                for z in self.avg_cop:
                    fec_dis = (k/z)/gridEfficency
                self.fec_dhcn.append(fec_dis)
            except:
                pass

        insert_toTable(table, 4, self.fec_dhcn)

        afec1 = round(((self.avg_cop[1] - 1) / self.avg_cop[1] * (self.ued[1] / gridEfficency)),2)
        afec2 = round(((self.avg_cop[2] - 1) / self.avg_cop[2] * (self.ued[2] / gridEfficency)),2)
        afec3 =round(((self.avg_cop[3] - 1) / self.avg_cop[3] * (self.ued[3] / gridEfficency)),2)
        afec7 = round(((self.avg_cop[7] - 1) / self.avg_cop[7] * (self.ued[7] / gridEfficency)),2)
        afec8 = round(((self.avg_cop[8] - 1) / self.avg_cop[8] * (self.ued[8] / gridEfficency)),2)

        table.setItem(3, 5, QTableWidgetItem(str(afec1)))
        table.setItem(4, 5, QTableWidgetItem(str(afec2)))
        table.setItem(5, 5, QTableWidgetItem(str(afec3)))
        table.setItem(10, 5, QTableWidgetItem(str(afec7)))
        table.setItem(11, 5, QTableWidgetItem(str(afec8)))

    def calculate_netLosses(self):
        table = self.dist_heat_source

        self.dh_losses_heating = []
        for f in self.fec_dhcn:
            for c in self.avg_cop:
                for b in self.ued:
                    loss = round((f * c - b), 2)
            self.dh_losses_heating.append(loss)
        insert_toTable(table, 6,  self.dh_losses_heating)


    def calculate_fec_afec_cool_net(self):
        table = self.dist_cool_net
        self.ued_cool = []
        for i in range(table.rowCount()):
            try:
                currItem = float((table.item(i, 0)).text())
                self.ued_cool.append(currItem)
            except:
                pass
        self.cal_uedAndInsert(table,  self.ued_cool)

    def cal_uedAndInsert(self,table, ued_cool):
        self.avg_cop_cool = []
        for i in range(table.rowCount()):
            try:
                currItem1 = (table.item(i, 1)).text()
                val_vero = float(currItem1.strip(' %')) / 100.0
                self.avg_cop_cool.append(val_vero)
            except:
                pass

        self.ued_cool = ued_cool
        efficency = float(self.btn_eff.value()) / 100

        self.fec_dhcn_cool =[]
        for i in self.ued_cool:
            for j in self.avg_cop_cool:
                try:
                    fec = (i / j)/(efficency)
                except ZeroDivisionError:
                    fec = 0
            self.fec_dhcn_cool.append(fec)

        insert_toTableCool(table, 2,  self.fec_dhcn_cool)

        afec1 = round(((self.avg_cop_cool[1] - 1) / self.avg_cop_cool[1] * (self.ued_cool[1] / efficency)),2)
        afec2 = round(((self.avg_cop_cool[2] - 1) / self.avg_cop_cool[2] * (self.ued_cool[2] / efficency)),2)
        afec3 = round(((self.avg_cop_cool[4] - 1) / self.avg_cop_cool[3] * (self.ued_cool[3] / efficency)),2)
        afec7 = round(((self.avg_cop_cool[5] - 1) / self.avg_cop_cool[6] * (self.ued_cool[6] / efficency)),2)
        afec8 = round(((self.avg_cop_cool[7] - 1) / self.avg_cop_cool[7] * (self.ued_cool[7] / efficency)),2)

        table.setItem(3, 3, QTableWidgetItem(str(round(afec1, 2))))
        table.setItem(4, 3, QTableWidgetItem(str(round(afec2, 2))))
        table.setItem(7, 3, QTableWidgetItem(str(round(afec3, 2))))
        table.setItem(8, 3, QTableWidgetItem(str(round(afec7, 2))))
        table.setItem(10, 3, QTableWidgetItem(str(round(afec8, 2))))


    def calculate_netDHCNLosses_cool(self):
        table = self.dist_cool_net
        self.dh_losses_cool = []
        for f in self.fec_dhcn_cool:
            for c in self.avg_cop_cool:
                for b in self.ued_cool:
                    loss = round((f * c - b), 2)
            self.dh_losses_cool.append(loss)

        insert_toTableCool(table, 4, self.dh_losses_cool)
        self.source_util_future()


    def calculationKPIs(self,lista_ued_courred, list_ued_curred_cool, demo_factor):
        self.ued_fut = lista_ued_courred
        self.ued_fut_cool = list_ued_curred_cool
        self.demo_factor = demo_factor

        self.primary_En_fact=[2.37, 1, 1, 1, 1, 1, 1, 1]

        table = self.dist_heat_source
        val=[]
        for i in range(table.rowCount()):
            try:
                currItem = float((table.item(i, 0)).text())
                val.append(currItem)
            except:
                pass

        self.tot_ued_heating = sum(val)

        tab = self.dist_cool_net
        value = []
        for i in range(table.rowCount()):
            try:
                currItem = float((tab.item(i, 0)).text())
                value.append(currItem)
            except:
                pass
        self.tot_ued_cool = sum(value)




    def source_util_future(self):
        table = self.table_source
        sum_fec_biomass = self.fec[9] + self.fec[10] + self.fec_dhcn[9] + self.fec_dhcn[10]
        table.setItem(0, 2, QTableWidgetItem(str(sum_fec_biomass)))

        tab_sbs_fec = self.sim_sbs_hdhw_Source
        fec_hp_sbs = []
        for i in range(tab_sbs_fec.rowCount()):
            try:
                val = i
                fec_hp_sbs.append(val)
            except:
                pass


        fec_hp_dist=[]
        tab_fec = self.dist_cool_net
        for i in range(tab_fec.rowCount()):
            try:
                val = i
                fec_hp_dist.append(val)
            except:
                pass
        tab = self.dist_heat_source
        fec_wh_industry = self.fec[11] + self.list_hp_cool[7] + self.fec_dhcn[11] + self.fec_cool[6]

        fechp_sbs = (fec_hp_sbs[1] + fec_hp_sbs[4])
        fecCol_sbs = self.list_hp_cool[1] + self.list_hp_cool[4]
        try:
            val = float((tab.item(9, 5)).text())
        except:
            val = 0.0
        fechp_dist = val
        fecCool_dist = fec_hp_dist[0] + fec_hp_dist[2] + self.fec_dhcn_cool[8]
        sum_fec_wH = fechp_sbs + fecCol_sbs + fechp_dist + fecCool_dist

        table.setItem(1, 2, QTableWidgetItem(str(sum_fec_wH)))

        sum_fec_geothermal = fec_hp_sbs[2] + fec_hp_sbs[5] + self.fec[12] + self.list_hp_cool[2] + self.fec_cool[5] + self.fec_cool[7] + \
                             fec_hp_dist[2] + fec_hp_dist[4] + self.fec_dhcn[12] + fec_hp_dist[1] + fec_hp_dist[3] + self.fec_dhcn_cool[7]

        table.setItem(2, 2, QTableWidgetItem(str(sum_fec_geothermal)))
        table.setItem(4, 2, QTableWidgetItem(str(fec_wh_industry)))

        try:
            sbs_sol1 = float(self.sim_sbs_hdhw_Source.item(24,4).text())
            sbs_sol2= float(self.sim_sbs_hdhw_Source.item(25,4).text())

            dist_sol1=float(self.dist_heat_source.item(24,4).text())
            dist_sol2 = float(self.dist_heat_source.item(25,4).text())


            sum_fec_solar =round(sbs_sol1+sbs_sol2+dist_sol1+dist_sol2,2)
        except:
            sum_fec_solar = 0.0

        table.setItem(3, 2, QTableWidgetItem(str(sum_fec_solar)))
        source_future=[sum_fec_biomass, sum_fec_wH, sum_fec_geothermal, sum_fec_solar,fec_wh_industry]

        self.check_source()

    def check_source(self):
        source=[]
        source_util=[]
        self.val_ser=[]
        en_12_3=[]
        for i in range(self.table_source.rowCount()):
            try:
                source_base = float(self.table_source.item(i, 1).text()) # colB

                source_ut= float(self.table_source.item(i, 2).text())  # colC

                #source_util_base = float(self.table_sutil.item(i, 2).text())  # colF
                if source_base >= source_ut:
                    val ="source available"
                    source.append(val)
                    val2 = round(((source_base/source_ut) *100),2)
                    source_util.append(val2)
                    #self.table_source.setItem(i, 3, QTableWidgetItem(str(val)))
                    self.val_ser.append(val2)
                    #en_123 = ((val2/(source_util_base/source_base)*100)-1)*100
                    #en_12_3.append(en_123)
                if source_base < source_ut:
                    val="source not available"
                    val2 = "falso"
                    source.append(val)
                    source_util.append(val2)
                    #self.table_source.setItem(i, 3, QTableWidgetItem(str(val)))

            except:
                 pass

        insert_to_source_table(self.table_source, 3, source)
        insert_to_source_table(self.table_sutil, 1, source_util)
        self.calcola_en_12_3(self.val_ser)

    def vis_cat_wh(self, wh_base, wh_ind, val_bio, val_geoth, val_sol):

        self.table_sutil.setItem(0, 2, QTableWidgetItem(str(val_bio)))
        self.table_sutil.setItem(1, 2, QTableWidgetItem(str(wh_base)))
        self.table_sutil.setItem(2, 2, QTableWidgetItem(str(val_geoth)))
        self.table_sutil.setItem(3, 2, QTableWidgetItem(str(val_sol)))
        self.table_sutil.setItem(4, 2, QTableWidgetItem(str(wh_ind)))



    def calcola_en_12_3(self, val_ser):
        tab_source_base = self.table_source
        tab_source = self.table_sutil
        en12_2 = val_ser
        en_12_3l=[]
        for j in en12_2:
            for i in range(tab_source.rowCount()):
                try:
                    source_base =float(tab_source_base.item(i, 1).text()) #colB
                    #en_12_2 = float(tab_source.item(i, 1).text())  # colE
                    source_util_base = float(tab_source.item(i, 2).text())  # colF
                    en_12_3 =((j/(source_util_base/source_base)*100)-1)
                    en_12_3l.append(en_12_3)
                except ZeroDivisionError:
                    en_12_3 = 0.0
                    en_12_3l.append(en_12_3)

        insert_to_source_table(self.table_sutil, 3, en_12_3l)






    def calculate_KPIs_future(self):

        self.fec_cool_sbs = self.fec_cool
        self.fec_sbs = self.fec  # self.fec
        self.fec_dist = self.fec_dhcn
        self.fec_cool_district = self.fec_dhcn_cool
        self.grid_lenght= self.leng.value()
        tot_footArea=self.spinBox_9.value()
        fec_sbs = self.fec

        fec_cool_sbs=self.fec_cool_sbs
        fec_dist=self.fec_dist
        fec_cool_district= self.fec_cool_district
        primary_En_fact=self.primary_En_fact
        ued_fut= self.ued_fut
        ued_fut_cool=self.ued_fut_cool
        demo_factor=self.demo_factor
        dh_losses_cool= self.dh_losses_cool
        dh_losses_heating= self.dh_losses_heating
        grid_lenght=self.grid_lenght
        tot_ued_heating= self.tot_ued_heating
        tot_ued_cool=self.tot_ued_cool

        efficiencyCOP_elect=[1, 3.5, 3.5, 3.5]
        efficiencyCOP_NatGas=[0.95,0.95, 1, 1, 1]
        efficiencyCOP_bio =[1,1,1]
        efficiencyCOP_Wh = [1]
        efficiencyCOP_geoth=[1,1,1]
        efficiencyCOP_oil= [1]
        efficiencyCOP_coalPat = [1]
        efficiencyCOP_solar = [1, 1, 1]


        KPIs_fut= self.calculator.KPIS_future(fec_sbs, fec_cool_sbs, fec_dist, fec_cool_district, primary_En_fact,
                                        ued_fut, ued_fut_cool, demo_factor, dh_losses_cool,
                                          dh_losses_heating, grid_lenght, tot_ued_heating, tot_ued_cool, tot_footArea,
                                        self.val, self.valNG, self.valBiomass, self.valEl, self.valWh, self.valTecEff, self.valCapex,
                                        self.valS, self.valSol)


        self.KPIs_table(KPIs_fut)
        self.check_target()

    def ncol_val_fut(self, valstring):
        if valstring == "r":
            self.nCol = 6
        if valstring == "t":
            self.nCol = 7

    def KPIs_table(self, KPIs):
        self.nCol= self.nCol
        cellr = QTableWidgetItem(str(KPIs["EN_1.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(3, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_1.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(4, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_1.5"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(5, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_1.6"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(6, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(9, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(10, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.5"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(11, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(14, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(15, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.5"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(16, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(19, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(20, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.5"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(21, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(24, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(25, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.5"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(26, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(30, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(31, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.5"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(32, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_13.2.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(33, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_13.2.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(34, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_14.2.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(35, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_14.2.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(36, self.nCol, cellr)



        cellr = QTableWidgetItem(str(KPIs["ENV_1.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(1, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(2, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.3"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(3, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.4"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(4, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.5"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(5, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.6"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(6, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.7"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(7, self.nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["ENV_1.8"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_5.setItem(8, self.nCol, cellr)


    def recive_KPIs_baseline(self, KPIs, string):
        if string =="r":
            self.valString="r"
            nCol = 3

        if string=="t":
            self.valString="t"
            nCol = 4

        self.insert_KPIs_baseline(KPIs, nCol)
        self.ncol_val_fut(self.valString)


    def insert_KPIs_baseline(self, KPIs, nCol):

        cellr = QTableWidgetItem(str(KPIs["EN_1.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(1, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_1.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(2, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(7, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_3.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(8, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(12, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_4.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(13, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(17, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_5.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(18, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(22, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_6.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(23, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.1"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(27, nCol, cellr)

        cellr = QTableWidgetItem(str(KPIs["EN_7.2"]))
        cellr.setFlags(QtCore.Qt.ItemIsEnabled)
        self.tableWidget_10.setItem(28, nCol, cellr)


    def check_target(self):
        table = self.tableWidget_10

        for i in range(table.rowCount()):
             try:
                value = table.item(i, 5).text()
                valKPi = table.item(i, 6).text()
                val = QTableWidgetItem(str(value))
                if value == valKPi:
                    val.setForeground(QColor(0, 255, 0))
                    table.setItem(i, 5, val)
                else:
                    val.setForeground(QColor(255, 0, 0))
                    table.setItem(i, 5, val)
             except:
                pass

    def insert_target(self, table_target):
        table =self.tableWidget_10 #tab di destinazione
        for i in range(table_target.rowCount()):
            item = table_target.item(i, 5)
            try:
                table.setItem(i, 5, QTableWidgetItem(item))
            except:
                pass

    def save_step(self):
        self.city.save_steps()

    def export_to_csv(self):
        folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")
        name = Qdialog_save_file(folder)
        self.saveToFile(name)

    def saveToFile(self, filename):
        self.data = {}
        self.crea_dic(self.tableWidget_10, filename)
        updata_dic(self.tableWidget_5, filename)
        updata_dic(self.tableWidget_7, filename)
        updata_dic(self.tableWidget_6, filename)

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

    def updataTab(self,table_criteriaEn,table_criteriaEnv,table_criteriaEco,table_criteriaSo):

        update_KPIs_visualization_tab(self.tableWidget_10, table_criteriaEn, self.tableWidget_5, table_criteriaEnv,
                                      self.tableWidget_7,table_criteriaSo, self.tableWidget_6, table_criteriaEco)



    def insert_input_factor(self):
        table = self.sourcesTable
        self.prim_fact=[]
        self.fact_geoth=[]
        self.fact_wh=[]
        self.fact_whInd=[]
        self.fact_solar=[]

        for i in range(table.rowCount()):
            try:
                prim_fact =float(table.item(i, 0).text())
                fact_geoth =float(table.item(i, 1).text())
                fact_wh = float(table.item(i, 2).text())
                fact_whi = float(table.item(i, 3).text())
                fact_sol = float(table.item(i, 4).text())
                self.prim_fact.append(prim_fact)
                self.fact_geoth.append(fact_geoth)
                self.fact_wh.append(fact_wh)
                self.fact_whInd.append(fact_whi)
                self.fact_solar.append(fact_sol)
            except:
                pass

        if self.prim_fact is not None:
            self.primary_En_fact = self.prim_fact

    def load_source_base(self, table):

        tab = table

        biomass =[]
        wh=['Effluent of UWWTPs','Sewer system','Waste water','Rivers heat extraction with heat pump',
            'Lakes heat extraction with heat pump', 'Lakes cold extraction with heat pump','Surface water','Water']
        geothermal =['Potential till 1 km','Additional 1-2 km','Additional 2-3 km','Additional 3-4 km','Additional 4-5 km',
                     'Additional 5-7 km','Deep geothermal', 'Ground heat extraction','Ground cold extraction']
        solar = ['Rooftops']
        wh_industry = ['Large industries']
        tot_bio=0.0
        tot_wh = 0.0
        tot_geo = 0.0
        tot_sol=0.0
        tot_whInd =0.0

        for i in range(tab.rowCount()):
            val = table.item(i, 0).text()
            if val in wh:
                num = float(table.item(i, 1).text())
                tot_wh= tot_wh + num

            if val in geothermal:
                num = float(table.item(i, 1).text())
                tot_geo = tot_geo + num

            if val in solar:
                num = float(table.item(i, 1).text())
                tot_sol = tot_sol + num
            if val in wh_industry:
                num = float(table.item(i, 1).text())
                tot_whInd = tot_whInd + num


        table = self.table_source

        table.setItem(0, 1, QTableWidgetItem(str(tot_bio)))
        table.setItem(1, 1, QTableWidgetItem(str(round(tot_wh, 2))))
        table.setItem(2, 1, QTableWidgetItem(str(round(tot_geo, 2))))
        table.setItem(3, 1, QTableWidgetItem(str(round(tot_sol, 2))))
        table.setItem(4, 1, QTableWidgetItem(str(round(tot_whInd, 2))))
        #table.setItem(0, 1, QTableWidgetItem(str(round(tot_wh, 2))))


