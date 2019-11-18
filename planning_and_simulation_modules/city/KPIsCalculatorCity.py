import os

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTreeWidget, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
from .load_to_table import calcola_prodotto
from .load_to_table import calc_dif_pro
import os.path
import logging
import sys
import traceback
import copy

# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# Import the custom tree widget items
from .. import Network


class KPIsCalculator:
    def __init__(self):
        self.pec_base_tot_cool = 0
        self.pec_base_tot = 0
        self.spec_base_tot = 0
        self.ued_base_tot = 0
        self.sued_base_tot = 0
        self.res_base_tot = 0
        self.res_perc_BASE = 0
        self.Wh_base = 0
        self.Wh_perc_base = 0
        self.CF_base = 0
        self.CF_perc_base = 0
        self.El_base = 0
        self.El_perc_tot = 0

        self.spec_base_tot_cool = 0
        self.ued_base_tot_cool = 0
        self.sued_base_tot_cool = 0
        self.res_base = 0
        self.res_perc_BASE_cool = 0
        self.Wh_base_tot_cool = 0
        self.Wh_perc_base_cool = 0
        self.CF_base_tot_cool = 0
        self.CF_perc_base_cool = 0
        self.El_base_tot_cool = 0
        self.El_perc_tot_cool = 0
        self.Wh_base = 0
        self.res_perc_base = 0

        self.lista_fec_baseline = []
        self.lista_UED_hDHW = []
        self.lista_cool = []

        self.ued_base_tot = 0
        self.lista_fec_baseline = []
        self.pec_base = 0

        self.Pec_sav_tot = 0
        self.pec_adj_base = 0
        self.pec_fut_tot = 0
        self.ued_fut_tot = 0
        self.res_base_tot = 0
        self.wh_fut_tot = 0
        self.Wh_base = 0
        self.Cf_base = 0
        self.El_base = 0
        self.pec_base_adj = 0
        self.pec_base_sourc = []
        self.pec_fut_ngas=0






    def KPIs_baseline(self, lista_UED, lista_cool, primary_En_fact, tot_footArea, lista_fec_baseline):
        self.lista_UED = lista_UED
        self.lista_cool = lista_cool
        self.primary_En_fact = primary_En_fact
        self.tot_footArea = tot_footArea
        self.lista_fec_baseline = lista_fec_baseline

        self.ued_electricity_cool = self.lista_cool[2] + self.lista_cool[3] + self.lista_cool[4]
        self.ued_naturalGas_cool = self.lista_cool[6] + self.lista_cool[7] + self.lista_cool[8]
        self.ued_wasteHeat_cool = self.lista_cool[10]
        self.ued_geothermal_cool = self.lista_cool[12]
        self.ued_other_cool = self.lista_cool[14]

        self.Ued_Natural_gas =self.lista_UED[7] +self.lista_UED[8] +self.lista_UED[9] +self.lista_UED[10] +self.lista_UED[11]
        self.Ued_electricity =self.lista_UED[2] + self.lista_UED[3] +self.lista_UED[4] +self.lista_UED[5]
        self.Ued_boimass = self.lista_UED[13] + self.lista_UED[14]
        self.Ued_wasteHeat = self.lista_UED[16]
        self.Ued_geothermal = self.lista_UED[18]
        self.Ued_heatingOil = self.lista_UED[20]
        self.Ued_coal = self.lista_UED[22]
        self.Ued_solar =self.lista_UED[24] + self.lista_UED[25]
        self.Ued_other = self.lista_UED[27]
        ##per tabella del cooling

        self.Ued_Natural_gas_tot = self.Ued_Natural_gas + self.ued_naturalGas_cool
        self.Ued_electricity_tot = self.Ued_electricity + self.ued_electricity_cool
        self.Ued_boimass_tot = self.Ued_boimass
        self.Ued_wasteHeat_tot = self.Ued_wasteHeat+self.ued_wasteHeat_cool
        self.Ued_geothermal_tot = self.Ued_geothermal + self.ued_geothermal_cool
        self.Ued_heatingOil_tot= self.Ued_heatingOil
        self.Ued_coal_tot = self.Ued_coal
        self.Ued_solar_tot = self.Ued_solar
        self.Ued_other_tot=  self.Ued_other + self.ued_other_cool



        self.ued_base_tot_cool = self.ued_electricity_cool + self.ued_naturalGas_cool + self.ued_wasteHeat_cool + self.ued_geothermal_cool + self.ued_other_cool
        self.ued_base_tot = self.Ued_electricity+self.Ued_Natural_gas+self.Ued_wasteHeat + self.Ued_geothermal + self.Ued_other

        self.pec_base_sourc=[] #colonna J
        for i in lista_fec_baseline:
            for j in self.primary_En_fact:
                pec_b = i*j
            self.pec_base_sourc.append(pec_b)

        self.pec_base = sum(self.pec_base_sourc)

        self.spec_base_tot =(self.pec_base/self.tot_footArea)*100
        self.ued_base = self.ued_base_tot_cool+ self.ued_base_tot
        self.sued_base_tot = self.ued_base / self.tot_footArea
        self.res_base =((self.Ued_boimass_tot*primary_En_fact[2])+(self.Ued_wasteHeat_tot*primary_En_fact[3])+
                        (self.Ued_geothermal_tot*primary_En_fact[4]) + self.Ued_solar_tot*primary_En_fact[7])
        self.res_perc_base =(self.res_base/self.pec_base)*100
        self.Wh_base = self.Ued_wasteHeat_tot*primary_En_fact[3]
        self.Wh_perc_base = (self.Wh_base /self.pec_base )*100
        self.Cf_base =(self.Ued_Natural_gas_tot*primary_En_fact[1])+(self.Ued_heatingOil_tot*primary_En_fact[5])+(self.Ued_coal_tot*primary_En_fact[6])
        self.CF_perc_base = (self.Cf_base/self.pec_base)*100
        self.El_base =((self.Ued_electricity_tot*primary_En_fact[0])+(self.Ued_Natural_gas_tot*primary_En_fact[1])+
                       (self.Ued_heatingOil_tot*primary_En_fact[5])+(self.Ued_coal_tot*primary_En_fact[6]))
        self.El_perc_tot = ( self.El_base/self.pec_base)*100

        KPIs={}

        KPIs["EN_1.1"] = round(self.pec_base, 2)
        try:
            KPIs["EN_1.2"] = round(self.spec_base_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs["EN_1.2"] = "Nan"
        KPIs["EN_3.1"] = round(self.ued_base)
        try:
            KPIs["EN_3.2"] = round(self.sued_base_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs["EN_3.2"] = "Nan"

        KPIs["EN_4.1"] = round(self.res_base,2)
        try:
            KPIs["EN_4.2"] =round(self.res_perc_base,2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs["EN_4.2"] = "Nan"
        KPIs["EN_5.1"] = round(self.Wh_base,2)
        try:
            KPIs["EN_5.2"] = round(self.Wh_perc_base, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs["EN_5.2"] = "Nan"
        KPIs["EN_6.1"] = round(self.Cf_base, 2)
        try:
            KPIs["EN_6.2"] = round(self.CF_perc_base,2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs["EN_6.2"] = "Nan"

        KPIs["EN_7.1"] = round(self.El_base, 2)
        try:
            KPIs["EN_7.2"] = round(self.El_perc_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs["EN_7.2"] = "Nan"

        return KPIs


    def KPIS_future(self,fec_sbs, fec_cool_sbs, fec_dist, fec_cool_dist, primary_En_fact, ued_fut, ued_fut_cool,demo_factor,dh_losses_cool,
                    dh_losses_heating, grid_lenght, tot_ued_heating, tot_ued_cool,tot_footArea, val,valNG,valBiomass, valEl, valWh, valTecEff, valCapex,
                                        valS, valSol):
        if valNG is not 0:
            primary_En_fact[0] = valNG
        if valEl is not 0:
            primary_En_fact[1] = valEl
        if valBiomass is not 0:
            primary_En_fact[2] = valBiomass
        if valWh is not 0:
            primary_En_fact[3] = valWh
        if valSol is not 0:
            primary_En_fact[7]= valSol

        fec_fut_elect =(fec_sbs[0] + fec_sbs[1] + fec_sbs[2] + fec_sbs[3] + fec_cool_sbs[0] + fec_cool_sbs[1] + fec_cool_sbs[2] +
                             fec_dist[0]+ fec_dist[1]+ fec_dist[2]+ fec_dist[3] + fec_cool_dist[0] + fec_cool_dist[1] +fec_cool_dist[2])
        fec_fut_ngas =(fec_sbs[4]+ fec_sbs[5] + fec_sbs[6] +fec_sbs [7] + fec_sbs[8] + fec_cool_sbs[3]+fec_cool_sbs[4]+fec_cool_sbs[5] +
                              fec_dist[4] +fec_dist[5] + fec_dist[6] +fec_dist[7] +fec_dist[8] +fec_cool_dist[3] +fec_cool_dist[4]+fec_cool_dist[5])
        fec_fut_biomass = (fec_sbs[9] + fec_sbs[10] +fec_dist[9] +fec_dist[10])
        fec_fut_wh = (fec_sbs[11] +fec_cool_sbs[6] + fec_dist[11] + fec_cool_sbs[6])# prima bisogna fare incoccio fonti
        fec_fut_geothermal = (fec_sbs[12]+fec_cool_sbs[7] + fec_dist[12] +fec_cool_dist[7])
        fec_fut_heatOil = (fec_sbs[13] + fec_dist[13])
        fec_fut_coal = (fec_sbs[14] + fec_dist[14])
        fec_fut_solar = (fec_sbs[15] +fec_dist[15])
        fec_fut=[ fec_fut_elect, fec_fut_ngas,fec_fut_biomass,fec_fut_wh,fec_fut_geothermal, fec_fut_heatOil,fec_fut_coal, fec_fut_solar]


        # col L
        pec_fut_elect = fec_fut_elect*primary_En_fact[0]
        pec_fut_ngas = fec_fut_ngas * primary_En_fact[1]
        pec_fut_biomassa = fec_fut_biomass * primary_En_fact[2]
        pec_fut_wh = fec_fut_wh * primary_En_fact[3]
        pec_fut_geothermal = fec_fut_geothermal*primary_En_fact[4]
        pec_fut_oil = fec_fut_heatOil * primary_En_fact[5]
        pec_fut_coal = fec_fut_coal *primary_En_fact[6]
        pec_fut_solar = fec_fut_solar * primary_En_fact[7]



        # pec_fut=[]

        self.pec_fut = [pec_fut_elect,pec_fut_ngas,pec_fut_biomassa,pec_fut_wh, pec_fut_geothermal,pec_fut_oil, pec_fut_coal,pec_fut_solar]

        self.co2_em_fac = [1, 1, 1, 1, 1, 1, 1, 1]
        self.sox_em_fac = [1, 1, 1, 1, 1, 1, 1, 1]
        self.nox_em_fac = [1, 1, 1, 1, 1, 1, 1, 1]
        self.pm10_em_fac = [1, 1, 1, 1, 1, 1, 1, 1]

        self.pec_fut_tot = sum(self.pec_fut)#pec_fut_elect+pec_fut_ngas +pec_fut_biomassa +pec_fut_wh +pec_fut_geothermal +pec_fut_oil +pec_fut_solar +pec_fut_other

        self.Spec_fut_tot = self.pec_fut_tot/tot_footArea

        self.pec_var_tot = round(((self.pec_fut_tot/(self.pec_base - 1)) * 100),2)


        adj_base = calcola_prodotto(self.lista_fec_baseline,primary_En_fact)
        self.pec_adj_base = sum(adj_base)

        self.Pec_sav_tot = self.pec_adj_base - self.pec_fut_tot

        uedfut=[]
        for i in ued_fut_cool:
            for j in ued_fut:
                ued = i+j
                uedfut.append(ued)

        self.ued_fut_tot= sum(uedfut)
        try:
            self.Sued_fut_tot = round(self.ued_fut_tot / tot_footArea, 2)
        except ZeroDivisionError:
            self.Sued_fut_tot=0.0
        try:
            self.Ued_var_tot =round((self.ued_fut_tot/(self.ued_base_tot-1))*100, 2)
        except ZeroDivisionError:
            self.Ued_var_tot = 0.0
        try:
            self.res_fut_tot = pec_fut_biomassa + pec_fut_wh + pec_fut_geothermal + pec_fut_solar
        except ZeroDivisionError:
            self.res_fut_tot=0.0
        try:
            self.res_perc_fut  =  self.res_fut_tot/ self.pec_fut_tot *100
        except ZeroDivisionError:
            self.res_perc_fut
        try:
            self.res_var_tot = ((self.res_fut_tot/(self.res_base_tot*(1+0.005))-1)*100)
        except ZeroDivisionError:
            self.res_var_tot=0.0

            self.wh_fut_tot = pec_fut_wh
        try:
            self.wh_per_fut_tot = self.wh_fut_tot / self.pec_fut_tot * 100
        except ZeroDivisionError:
            self.wh_per_fut_tot=0.0
        try:
            self.wh_var_tot = (self.wh_fut_tot / (self.Wh_base * (1 + demo_factor)) - 1) * 100
        except ZeroDivisionError:
            self.wh_var_tot=0.0

        try:
            self.cf_fut_tot = self.pec_fut[1] + self.pec_fut[5] + self.pec_fut[6]
        except ZeroDivisionError:
            self.cf_fut_tot=0.0
        try:
            self.cf_per_fut_tot = self.cf_fut_tot / self.pec_fut_tot * 100
        except ZeroDivisionError:
            self.cf_per_fut_tot=0.0
        try:
            self.cf_var_fut_tot = (self.cf_fut_tot / (self.Cf_base * (1 + demo_factor)) - 1) * 100
        except ZeroDivisionError:
            self.cf_var_fut_tot=0.0
        try:
            self.ef_fut_tot = pec_fut_elect + pec_fut_ngas + pec_fut_oil + pec_fut_coal
        except ZeroDivisionError:
            self.ef_fut_tot=0.0
        try:
            self.el_perc_fut_tot = self.ef_fut_tot / self.pec_fut_tot * 100
        except ZeroDivisionError:
            self.el_perc_fut_tot=0.0
        try:
            self.el_var_fut_tot = (self.ef_fut_tot / (self.El_base * (1 + demo_factor)) - 1) * 100
        except ZeroDivisionError:
            self.el_var_fut_tot=0.0

        try:
            self.DCN_loss_fut = sum(dh_losses_cool)
        except ZeroDivisionError:
            self.DCN_loss_fut=0.0
        try:
            self.DHN_loss_fut = sum(dh_losses_heating)
        except ZeroDivisionError:
            self.DHN_loss_fut=0.0
        try:
            self.DHN_hd_fut = tot_ued_heating / (grid_lenght * 1000)
        except ZeroDivisionError:
            self.DHN_hd_fut=0.0
        try:
            self.DCN_hd_fut = tot_ued_cool / (grid_lenght * 1000)
        except ZeroDivisionError:
            self.DCN_hd_fut=0.0

        CO2_fut = calcola_prodotto(self.pec_fut, self.co2_em_fac)  # col R
        CO2_base = calcola_prodotto(self.pec_base_sourc,self.co2_em_fac) # col Q

        self.pec_base_adj = []
        for i in self.lista_fec_baseline:
            pec_adj = i *( 1+demo_factor)
            self.pec_base_adj.append(pec_adj)

        co2_sav = calc_dif_pro(self.pec_base_adj,self.pec_fut,self.co2_em_fac)

        self.NOx_fut = calcola_prodotto(self.pec_fut, self.nox_em_fac)# col V
        self.tNOx_base = calcola_prodotto(self.pec_base_sourc,self.nox_em_fac) # col U
        self.SOx_fut=calcola_prodotto( self.pec_fut,self.sox_em_fac) # col T
        self.Sox_base = calcola_prodotto( self.pec_base_sourc,self.sox_em_fac) # col S
        self.PM10_fut = calcola_prodotto(self.pec_fut, self.pm10_em_fac)# col x
        self.PM10_base =calcola_prodotto(self.pec_base_sourc, self.pm10_em_fac) #col w

        self.CO2_var_tot = (sum(CO2_fut)/(sum(CO2_base)-1))*100
        self.CO2_sav_tot = sum(co2_sav)
        self.NOx_var_tot=(sum(self.NOx_fut)/(sum(self.tNOx_base)-1))*100

        NOx_sav = calc_dif_pro(self.pec_base_adj,self.pec_fut,self.nox_em_fac)

        self.Nox_sav_tot = sum(NOx_sav)

        self.So_var =(sum(self.SOx_fut)/(sum(self.Sox_base)-1))*100 #somma T / somma S -1 *100
        self.So_sav_tot = sum(calc_dif_pro(self.pec_base_adj, self.pec_fut,self.sox_em_fac))

        self.PM10_var_tot=(sum( self.PM10_fut )/(sum(self.PM10_base)-1))*100
        self.PM10_sav_tot = sum(calc_dif_pro( self.pec_base_adj,self.pec_fut, self.pm10_em_fac))



        KPIs_future = {}

        KPIs_future["EN_1.3"] = round( self.pec_fut_tot, 2)
        try:
            KPIs_future["EN_1.4"] = round(self.Spec_fut_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_1.4"] = "Nan"
        KPIs_future["EN_1.5"] = round(self.pec_var_tot)
        KPIs_future["EN_1.6"] = round(self.Pec_sav_tot)


        KPIs_future["EN_3.3"] = round(self.ued_fut_tot, 2)
        try:
            KPIs_future["EN_3.4"] = round(self.Sued_fut_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_3.4"] = "Nan"
        try:
            KPIs_future["EN_3.5"] = round(self.Ued_var_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_3.5"] = "Nan"
        KPIs_future["EN_4.3"] = round( self.res_fut_tot,2)
        try:
            KPIs_future["EN_4.4"] = round(self.res_perc_base, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_4.4"] = "Nan"
        try:
            KPIs_future["EN_4.5"] = round(self.res_var_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_4.5"] = "Nan"
        KPIs_future["EN_5.3"] = round(self.wh_fut_tot, 2)
        try:
            KPIs_future["EN_5.4"] = round(self.wh_per_fut_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_5.4"] = "Nan"
        try:
            KPIs_future["EN_5.5"] = round(self.wh_var_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_5.5"] = "Nan"

        KPIs_future["EN_6.3"] = round(self.cf_fut_tot, 2)
        try:
            KPIs_future["EN_6.4"] = round(self.cf_per_fut_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_6.4"] = "Nan"
        try:
            KPIs_future["EN_6.5"] = round(self.cf_var_fut_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_6.5"] = "Nan"

        KPIs_future["EN_7.3"] = round(self.ef_fut_tot, 2)
        try:
            KPIs_future["EN_7.4"] = round(self.el_perc_fut_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_7.4"] = "Nan"
        try:
            KPIs_future["EN_7.5"] = round(self.el_var_fut_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_7.5"] = "Nan"
        try:
            KPIs_future["EN_13.2.1"] = round(self.DHN_loss_fut, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_13.2.1"] = "Nan"
        try:
            KPIs_future["EN_13.2.2"] = round(self.DCN_loss_fut, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_13.2.2"] = "Nan"
        try:
            KPIs_future["EN_14.2.1"] = round(self.DHN_hd_fut, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_14.2.1"] = "Nan"
        try:
            KPIs_future["EN_14.2.2"] = round(self.DCN_hd_fut, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["EN_14.2.2"] = "Nan"

        try:
            KPIs_future["ENV_1.1"] = round(self.CO2_var_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.1"] = "Nan"

        try:
            KPIs_future["ENV_1.2"] = round(self.CO2_sav_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.2"] = "Nan"

        try:
            KPIs_future["ENV_1.3"] = round(self.NOx_var_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.3"] = "Nan"

        try:
            KPIs_future["ENV_1.4"] = round(self.Nox_sav_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.4"] = "Nan"

        try:
            KPIs_future["ENV_1.5"] = round(self.So_var, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.5"] = "Nan"

        try:
            KPIs_future["ENV_1.6"] = round(self.So_sav_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.6"] = "Nan"
        try:
            KPIs_future["ENV_1.7"] = round(self.PM10_var_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.7"] = "Nan"

        try:
            KPIs_future["ENV_1.8"] = round(self.PM10_sav_tot, 2)
        except(ZeroDivisionError, TypeError) as e:
            KPIs_future["ENV_1.8"] = "Nan"

        return KPIs_future