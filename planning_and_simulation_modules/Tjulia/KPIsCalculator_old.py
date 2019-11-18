import os

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTreeWidget, QTableWidgetItem

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

    pef_sources_tab = None
    ef_sources_tab = None
    tech_tab = None
    work_folder = None
    network = None
    building_id = None
    building_tag = None
    step0_district_sources_tab = None
    future_scenario = None
    baseline_scenario = None
    sources = None
    individual_tech_power_column = None
    district_tech_power_column = None
    eco_param = None
    KPIs_input = None

    YEOHbase = None
    YEOHbaseR = None
    YEOHbaseT = None
    pec = 0
    pecR = 0
    pecT = 0
    temp_pec = 0
    fec = 0
    fecT = 0
    fecR = 0
    pecRENs = 0
    pecRENsR = 0
    pecRENsT = 0
    fecWH = 0
    fecWHR = 0
    fecWHT = 0
    pecCF = 0
    pecCFR = 0
    pecCFT = 0
    pecIS = 0
    pecISR = 0
    pecIST = 0
    area = 0
    areaR = 0
    CO2 = 0
    CO2R = 0
    CO2T = 0
    NOx = 0
    SOx = 0
    PM10 = 0
    NOxR = 0
    SOxR = 0
    PM10R = 0
    NOxT = 0
    SOxT = 0
    PM10T = 0
    stp = 0
    stpR = 0
    stpT = 0
    c_fec_eta = 0
    h_fec_eta = 0
    c_fec_etaR = 0
    h_fec_etaR = 0
    c_fec_etaT = 0
    h_fec_etaT = 0
    h_length = 0
    c_length = 0
    h_ued = 0
    c_ued = 0
    h_uedR = 0
    c_uedR = 0
    h_uedT = 0
    c_uedT = 0
    grant = 0
    grantR = 0
    grantT = 0
    ssbase = 0
    ssbaseR = 0
    ssbaseT =0
    fuel_cost_saving = 0
    fuel_cost_savingR = 0
    fuel_cost_savingT = 0
    OeM_cost_saving = 0
    OeM_cost_savingR = 0
    OeM_cost_savingT = 0
    opex = 0
    opexR = 0
    opexT = 0
    capext = 0
    capextR = 0
    capextT = 0

    def __init__(self, pef_sources_tab=None, ef_sources_tab=None, tech_tab=None, work_folder=None, network=None,
                 building_id=None):
        self.pef_sources_tab = pef_sources_tab
        self.ef_sources_tab = ef_sources_tab
        self.tech_tab = tech_tab
        self.work_folder = work_folder
        self.network = network
        self.building_id = building_id

    def initialize(self):
        self.eco_param = {}
        self.eco_param["r"] = 0.1
        self.eco_param["years"] = 5

        self.pec = 0
        self.pecT = 0
        self.pecR = 0
        self.temp_pec = 0

        self.fec = 0
        self.fecT = 0
        self.fecR = 0

        self.pecRENs = 0
        self.pecRENsR = 0
        self.pecRENsT = 0
        self.fecWH = 0
        self.fecWHR = 0
        self.fecWHT = 0
        self.pecCF = 0
        self.pecCFR = 0
        self.pecCFT = 0
        self.pecIS = 0
        self.pecISR = 0
        self.pecIST = 0
        self.area = 0
        self.areaR = 0
        self.CO2 = 0
        self.CO2R = 0
        self.CO2T = 0
        self.NOx = 0
        self.SOx = 0
        self.PM10 = 0
        self.NOxR = 0
        self.SOxR = 0
        self.PM10R = 0
        self.NOxT = 0
        self.SOxT = 0
        self.PM10T = 0
        self.stp = 0
        self.stpR = 0
        self.stpT = 0
        self.c_fec_eta = 0
        self.h_fec_eta = 0
        self.c_fec_etaR = 0
        self.h_fec_etaR = 0
        self.c_fec_etaT = 0
        self.h_fec_etaT = 0
        self.h_length = 0
        self.c_length = 0
        self.h_ued = 0
        self.c_ued = 0
        self.h_uedR = 0
        self.c_uedR = 0
        self.h_uedT = 0
        self.c_uedT = 0
        self.grant = 0
        self.grantR = 0
        self.grantT = 0
        self.YEOHbase = {}
        self.YEOHbaseR = {}
        self.YEOHbaseT = {}

        self.fuel_cost_saving = 0
        self.fuel_cost_savingR = 0
        self.fuel_cost_savingT = 0
        self.OeM_cost_saving = 0
        self.OeM_cost_savingR = 0
        self.OeM_cost_savingT = 0
        self.opex = 0
        self.opexR = 0
        self.opexT = 0
        self.capext = 0
        self.capextR = 0
        self.capextT = 0

        self.FEavailability = 0  # output del MM

    def district_KPIs_update(self):
        if not self.district_var_check():
            return
        residential_factor = self.network.get_residential_factor()
        self.temp_pec = self.district_pec()
        self.pec = self.pec + self.temp_pec
        self.pecR = self.pecR + self.temp_pec*residential_factor
        self.pecT = self.pecT + self.temp_pec*(1-residential_factor)
        tmp = self.district_fec(self.work_folder, self.network.get_ID(), self.tech_tab)
        self.fec = self.fec + tmp
        self.fecR = self.fecR + tmp*residential_factor
        self.fecT = self.fecT + tmp*(1 - residential_factor)
        tmp = self.district_pecRENs(self.work_folder, self.network.get_ID(),
                                    self.tech_tab, self.pef_sources_tab)
        self.pecRENs = self.pecRENs + tmp
        self.pecRENsR = self.pecRENsR + tmp*residential_factor
        self.pecRENsT = self.pecRENsT + tmp*(1 - residential_factor)
        temp = self.district_fecWH(self.work_folder, self.network.get_ID(), self.tech_tab)
        self.fecWH = self.fecWH + temp
        self.fecWHR = self.fecWHR + tmp*residential_factor
        self.fecWHT = self.fecWHT + tmp*(1 - residential_factor)
        tmp = self.district_pecCF(self.work_folder, self.network.get_ID(), self.tech_tab, self.pef_sources_tab)
        self.pecCF = self.pecCF + tmp
        self.pecCFR = self.pecCFR + tmp*residential_factor
        self.pecCFT = self.pecCFT + tmp*(1 - residential_factor)
        tmp = self.district_pecIS(self.work_folder, self.network.get_ID(), self.tech_tab, self.pef_sources_tab)
        self.pecIS = self.pecIS + tmp
        self.pecISR = self.pecISR + tmp*residential_factor
        self.pecIST = self.pecIST + tmp*(1 - residential_factor)
        self.district_YEOHbase_calculation(self.work_folder, self.network.get_ID(), self.YEOHbase,
                                           self.tech_tab, self.pef_sources_tab)
        self.district_YEOHbase_calculation(self.work_folder, self.network.get_ID(), self.YEOHbaseR,
                                           self.tech_tab, self.pef_sources_tab)
        self.district_YEOHbase_calculation(self.work_folder, self.network.get_ID(), self.YEOHbaseT,
                                           self.tech_tab, self.pef_sources_tab)
        if self.network.optimized_buildings_layer is not None:
            layer = self.network.optimized_buildings_layer
        else:
            layer = self.network.buildings_layer
        if layer is not None:
            for feature in layer.getFeatures():
                self.area = self.area + feature.geometry().area()
                if feature.attribute("Use") == "Residential":
                    self.areaR = self.areaR + feature.geometry().area()
        else:
            self.area = 1.0
            self.areaR = 1.0
        if not self.ENV_KPIs_check():
            return
        tmp = self.district_emission(1)
        self.CO2 = self.CO2 + tmp
        self.CO2R = self.CO2R + tmp*residential_factor
        self.CO2T = self.CO2T + tmp*(1-residential_factor)
        tmp = self.district_emission(2)
        self.NOx = self.NOx + tmp
        self.NOxR = self.NOxR + tmp*residential_factor
        self.NOxT = self.NOxT + tmp*(1-residential_factor)
        tmp = self.district_emission(3)
        self.SOx = self.SOx + tmp
        self.SOxR = self.SOxT + tmp*residential_factor
        self.SOxR = self.SOxT + tmp*(1-residential_factor)
        tmp = self.district_emission(4)
        self.PM10 = self.PM10 + tmp
        self.PM10R = self.PM10R + tmp*residential_factor
        self.PM10T = self.PM10T + tmp*(1-residential_factor)
        tmp = self.district_solar_penetration()
        self.stp = self.stp + tmp
        self.stpR = self.stpR + tmp*residential_factor
        self.stpT = self.stpT + tmp*(1-residential_factor)
        if self.network.n_type == "DCN":
            self.c_ued = self.c_ued + self.get_UED_cooling(self.network.buildings_layer)
            self.c_uedR = self.c_uedR + self.get_UED_cooling(self.network.buildings_layer, use="R")
            self.c_uedT = self.c_uedT + self.get_UED_cooling(self.network.buildings_layer, use="T")
            self.c_fec_eta = self.c_fec_eta + self.fec*self.network.efficiency
            self.c_fec_etaR = self.c_fec_etaR + self.fec * self.network.efficiency * residential_factor
            self.c_fec_etaT = self.c_fec_etaT + self.fec * self.network.efficiency * (1-residential_factor)
            self.c_length = self.c_length + self.network.pipes_length()
        if self.network.n_type == "DHN":
            self.h_ued = self.h_ued + self.get_UED_heating(self.network.buildings_layer)
            self.h_uedR = self.h_uedR + self.get_UED_heating(self.network.buildings_layer, use="R")
            self.h_uedT = self.h_uedT + self.get_UED_heating(self.network.buildings_layer, use="T")
            self.h_length = self.h_length + self.network.pipes_length()
            self.h_fec_eta = self.h_fec_eta + self.fec*self.network.efficiency
            self.h_fec_etaR = self.h_fec_etaR + self.fec * self.network.efficiency * residential_factor
            self.h_fec_etaT = self.h_fec_etaT + self.fec * self.network.efficiency * (1-residential_factor)
        self.grant = self.grant + self.district_grant_contribution()
        self.grantR = self.grant + self.district_grant_contribution(use="R")
        self.grantT = self.grant + self.district_grant_contribution(use="T")
        if self.future_scenario is not None:
            self.opex = self.opex + self.district_FECfut_tech_per_energy_tariff()
            self.opexR = self.opexR + self.district_FECfut_tech_per_energy_tariff(use="R")
            self.opexT = self.opexT + self.district_FECfut_tech_per_energy_tariff(use="T")
            self.KPIs_input["fuel_cost_saving"] = self.KPIs_input["fuel_cost_saving"] - self.district_FECfut_tech_per_energy_tariff()
            self.KPIs_input["fuel_cost_savingR"] = self.KPIs_input[
                                                      "fuel_cost_savingR"] - self.district_FECfut_tech_per_energy_tariff(use="R")
            self.KPIs_input["fuel_cost_savingT"] = self.KPIs_input[
                                                      "fuel_cost_savingT"] - self.district_FECfut_tech_per_energy_tariff(use="T")
        else:
            self.fuel_cost_saving = self.fuel_cost_saving + self.district_FECfut_tech_per_energy_tariff()
            self.fuel_cost_savingR = self.fuel_cost_savingT + self.district_FECfut_tech_per_energy_tariff(use="R")
            self.fuel_cost_savingR = self.fuel_cost_savingT + self.district_FECfut_tech_per_energy_tariff(use="T")
        if self.future_scenario is not None:
            self.capext = self.capext + self.district_capex()
            self.capextR = self.capextR + self.district_capex(use="R")
            self.capextT = self.capextT + self.district_capex(use="T")
            self.opex = self.opex + self.district_UEDfut_tech_per_energy_tariff()
            self.opexR = self.opexR + self.district_UEDfut_tech_per_energy_tariff(use="R")
            self.opexT = self.opexT + self.district_UEDfut_tech_per_energy_tariff(use="T")
            self.KPIs_input["OeM_cost_saving"] = self.KPIs_input["OeM_cost_saving"] - self.district_UEDfut_tech_per_energy_tariff()
            self.KPIs_input["OeM_cost_savingR"] = self.KPIs_input[
                                                      "OeM_cost_savingR"] - self.district_UEDfut_tech_per_energy_tariff(use="R")
            self.KPIs_input["OeM_cost_savingT"] = self.KPIs_input[
                                                      "OeM_cost_savingT"] - self.district_UEDfut_tech_per_energy_tariff(use="T")
        else:
            self.OeM_cost_saving = self.OeM_cost_saving + self.district_UEDfut_tech_per_energy_tariff()
            self.OeM_cost_savingR = self.OeM_cost_savingT + self.district_UEDfut_tech_per_energy_tariff(use="R")
            self.OeM_cost_savingR = self.OeM_cost_savingT + self.district_UEDfut_tech_per_energy_tariff(use="T")


    def individual_KPIs_update(self):
        if not self.individual_var_check():
            return
        self.temp_pec = self.building_PEC_calculation()
        self.pec = self.pec + self.temp_pec
        if self.building_tag == "Residential":
            self.pecR = self.pecR + self.temp_pec
        else:
            self.pecT = self.pecT + self.temp_pec

        tmp = self.building_FEC_calculation(self.work_folder, self.tech_tab, self.building_id)
        self.fec = self.fec + tmp
        if self.building_tag == "Residential":
            self.fecR = self.fecR + tmp
        else:
            self.fecT = self.fecT + tmp

        # # mi serve per ECOOOOO
        # tmp = self.building_OPEX_calculation(self.work_folder, self.tech_tab, self.building_id)
        # self.opex = self.opex + tmp
        # if self.building_tag == "Residential":
        #     self.opexR = self.opexR + tmp
        # else:
        #     self.opexT = self.opexT + tmp

        tmp = self.building_pecRENs_calculation(self.work_folder, self.tech_tab, self.building_id)
        self.pecRENs = self.pecRENs + tmp
        if self.building_tag == "Residential":
            self.pecRENsR = self.pecRENsR + tmp
        else:
            self.pecRENsT = self.pecRENsT + tmp

        tmp = self.building_fecWH_calculation(self.work_folder, self.tech_tab, self.building_id)
        self.fecWH = self.fecWH + tmp
        if self.building_tag == "Residential":
            self.fecWHR = self.fecWHR + tmp
        else:
            self.fecWHT = self.fecWHT + tmp

        tmp = self.building_pecCF_calculation(self.work_folder, self.tech_tab, self.building_id)
        self.pecCF = self.pecCF + tmp
        if self.building_tag == "Residential":
            self.pecCFR = self.pecCFR + tmp
        else:
            self.pecCFT = self.pecCFT + tmp

        tmp = self.building_pecIS_calculation(self.work_folder, self.tech_tab, self.building_id)
        self.pecIS = self.pecIS + tmp
        if self.building_tag == "Residential":
            self.pecISR = self.pecISR + tmp
        else:
            self.pecIST = self.pecIST + tmp

        self.building_YEOHbase_calculation(self.work_folder, self.tech_tab, self.building_id, self.YEOHbase)
        if self.building_tag == "Residential":
            self.building_YEOHbase_calculation(self.work_folder, self.tech_tab, self.building_id, self.YEOHbaseR)
        else:
            self.building_YEOHbase_calculation(self.work_folder, self.tech_tab, self.building_id, self.YEOHbaseT)
        tmp = self.get_area(self.building_id)
        self.area = self.area + tmp
        if self.building_tag == "Residential":
            self.areaR = self.areaR + tmp
        if not self.ENV_KPIs_check():
            return
        tmp = self.individual_emission(1)
        self.CO2 = self.CO2 + tmp
        if self.building_tag == "Residential":
            self.CO2R = self.CO2R + tmp
        else:
            self.CO2T = self.CO2T + tmp
        tmp = self.individual_emission(2)
        self.NOx = self.NOx + tmp
        if self.building_tag == "Residential":
            self.NOxR = self.NOxR + tmp
        else:
            self.NOxT = self.NOxT + tmp
        tmp = self.individual_emission(3)
        self.SOx = self.SOx + tmp
        if self.building_tag == "Residential":
            self.SOxR = self.SOxR + tmp
        else:
            self.SOxT = self.SOxT + tmp
        tmp = self.individual_emission(4)
        self.PM10 = self.PM10 + tmp
        if self.building_tag == "Residential":
            self.PM10R = self.PM10R + tmp
        else:
            self.PM10T = self.PM10T + tmp
        tmp = self.individual_solar_penetration()
        self.stp = self.stp + tmp
        if self.building_tag == "Residential":
            self.stpR = self.stpR + tmp
        else:
            self.stpT = self.stpT + tmp
        self.grant = self.grant + self.individual_grant_contribution()
        if self.building_tag == "Residential":
            self.grantR = self.grantR + self.individual_grant_contribution()
        else:
            self.grantT = self.grantT + self.individual_grant_contribution()
        if self.future_scenario is not None:
            self.KPIs_input["fuel_cost_saving"] = self.KPIs_input["fuel_cost_saving"] - self.building_FECfut_tech_per_energy_tariff()
        else:
            self.fuel_cost_saving = self.fuel_cost_saving + self.building_FECfut_tech_per_energy_tariff()
        if self.building_tag == "Residential":
            if self.future_scenario is not None:
                self.KPIs_input["fuel_cost_savingR"] = self.KPIs_input[
                                                          "fuel_cost_savingR"] - self.building_FECfut_tech_per_energy_tariff(use="R")
            else:
                self.fuel_cost_savingR = self.fuel_cost_savingR + self.building_FECfut_tech_per_energy_tariff(use="R")
        else:
            if self.future_scenario is not None:
                self.KPIs_input["fuel_cost_savingT"] = self.KPIs_input[
                                                          "fuel_cost_savingT"] - self.building_FECfut_tech_per_energy_tariff(use="T")
            else:
                self.fuel_cost_savingT = self.fuel_cost_savingT + self.building_FECfut_tech_per_energy_tariff(use="T")
        if self.future_scenario is not None:
            self.KPIs_input["OeM_cost_saving"] = self.KPIs_input["OeM_cost_saving"] - self.building_UEDfut_tech_per_energy_tariff()
        else:
            self.OeM_cost_saving = self.OeM_cost_saving + self.building_UEDfut_tech_per_energy_tariff()
        if self.building_tag == "Residential":
            if self.future_scenario is not None:
                self.KPIs_input["OeM_cost_savingR"] = self.KPIs_input[
                                                          "OeM_cost_savingR"] - self.building_UEDfut_tech_per_energy_tariff(use="R")
            else:
                self.OeM_cost_savingR = self.OeM_cost_savingR + self.building_UEDfut_tech_per_energy_tariff(use="R")
        else:
            if self.future_scenario is not None:
                self.KPIs_input["OeM_cost_savingT"] = self.KPIs_input[
                                                          "OeM_cost_savingT"] - self.building_UEDfut_tech_per_energy_tariff(use="T")
            else:
                self.OeM_cost_savingT = self.OeM_cost_savingT + self.building_UEDfut_tech_per_energy_tariff(use="T")

        if self.future_scenario is not None:
            self.opex = self.opex + self.building_UEDfut_tech_per_energy_tariff() + self.building_FECfut_tech_per_energy_tariff()
            self.opexR = self.opexR + self.building_UEDfut_tech_per_energy_tariff(use="R") + self.building_FECfut_tech_per_energy_tariff(use="R")
            self.opexT = self.opexT + self.building_UEDfut_tech_per_energy_tariff(use="T") + self.building_FECfut_tech_per_energy_tariff(use="T")

        if self.future_scenario is not None:
            self.capext = self.capext + self.building_capex()
            if self.building_tag == "Residential":
                self.capextR = self.capextR + self.building_capex()
            else:
                self.capextT = self.capextT + self.building_capex()

    def close_calculation(self, KPIs_baseline=None):
        if KPIs_baseline is None:
            KPIs_baseline = self.KPIs_input
        try:
            FEavailability = self.eco_param["FEavailability"]
        except:
            FEavailability = 1
        if self.area == 0:
            self.area = 1
        KPIs = {}
        if KPIs_baseline is not None:
            for key in KPIs_baseline.keys():
                print("baseline KPI key:", key)
                KPIs[key] = copy.deepcopy(KPIs_baseline[key])
            KPIs["EN_1.3"] = self.pec
            KPIs["EN_1.3R"] = self.pecR
            KPIs["EN_1.3T"] = self.pecT
            try:
                KPIs["EN_1.4"] = round(self.pec/self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.4"] = "Nan"
            try:
                KPIs["EN_1.4R"] = round(self.pecR / self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.4R"] = "Nan"
            try:
                KPIs["EN_1.4T"] = round(self.pecT / (self.area-self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.4T"] = "Nan"
            try:
                KPIs["EN_1.5"] = ((KPIs["EN_1.3"]-KPIs["EN_1.1"])/KPIs["EN_1.1"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.5"] = "Nan"
            try:
                KPIs["EN_1.5R"] = ((KPIs["EN_1.3R"] - KPIs["EN_1.1R"]) / KPIs["EN_1.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.5R"] = "Nan"
            try:
                KPIs["EN_1.5T"] = ((KPIs["EN_1.3T"] - KPIs["EN_1.1T"]) / KPIs["EN_1.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.5T"] = "Nan"
            try:
                KPIs["EN_1.7"] = ((KPIs["EN_1.4"] - KPIs["EN_1.2"]) / KPIs["EN_1.2"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.7"] = "Nan"
            try:
                KPIs["EN_1.7R"] = ((KPIs["EN_1.4R"] - KPIs["EN_1.2R"]) / KPIs["EN_1.2R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.7R"] = "Nan"
            try:
                KPIs["EN_1.7T"] = ((KPIs["EN_1.4T"] - KPIs["EN_1.2T"]) / KPIs["EN_1.2T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.7T"] = "Nan"
            KPIs["EN_1.6"] = KPIs["EN_1.3"] - KPIs["EN_1.1"]
            KPIs["EN_1.6R"] = KPIs["EN_1.3R"] - KPIs["EN_1.1R"]
            KPIs["EN_1.6T"] = KPIs["EN_1.3T"] - KPIs["EN_1.1T"]
            KPIs["EN_2.3"] = self.fec
            KPIs["EN_2.3R"] = self.fecR
            KPIs["EN_2.3T"] = self.fecT
            try:
                KPIs["EN_2.4"] = round(self.fec/self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.4"] = "Nan"
            try:
                KPIs["EN_2.4R"] = round(self.fecR / self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.4R"] = "Nan"
            try:
                KPIs["EN_2.4T"] = round(self.fecT / (self.area-self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.4T"] = "Nan"
            try:
                KPIs["EN_2.5"] = ((KPIs["EN_2.3"]-KPIs["EN_2.1"])/KPIs["EN_2.1"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.5"] = "Nan"
            try:
                KPIs["EN_2.5R"] = ((KPIs["EN_2.3R"] - KPIs["EN_2.1R"]) / KPIs["EN_2.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.5R"] = "Nan"
            try:
                KPIs["EN_2.5T"] = ((KPIs["EN_2.3T"] - KPIs["EN_2.1T"]) / KPIs["EN_2.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.5T"] = "Nan"
            try:
                KPIs["EN_2.7"] = ((KPIs["EN_2.4"] - KPIs["EN_2.2"]) / KPIs["EN_2.2"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.7"] = "Nan"
            try:
                KPIs["EN_2.7R"] = ((KPIs["EN_2.4R"] - KPIs["EN_2.2R"]) / KPIs["EN_2.2R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.7R"] = "Nan"
            try:
                KPIs["EN_2.7T"] = ((KPIs["EN_2.4T"] - KPIs["EN_2.2T"]) / KPIs["EN_2.2T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.7T"] = "Nan"
            KPIs["EN_2.6"] = KPIs["EN_2.3"] - KPIs["EN_2.1"]
            KPIs["EN_2.6R"] = KPIs["EN_2.3R"] - KPIs["EN_2.1R"]
            KPIs["EN_2.6T"] = KPIs["EN_2.3T"] - KPIs["EN_2.1T"]
            KPIs["EN_3.3"] = self.get_UED(self.future_scenario)
            KPIs["EN_3.3R"] = self.get_UED(self.future_scenario, use="R")
            KPIs["EN_3.3T"] = self.get_UED(self.future_scenario, use="T")
            try:
                KPIs["EN_3.4"] = round(KPIs["EN_3.3"]/self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.4"] = "Nan"
            try:
                KPIs["EN_3.4R"] = round(KPIs["EN_3.3R"] / self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.4R"] = "Nan"
            try:
                KPIs["EN_3.4T"] = round(KPIs["EN_3.3T"] / (self.area-self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.4T"] = "Nan"
            try:
                KPIs["EN_3.5"] = ((KPIs["EN_3.3"] - KPIs["EN_3.1"])/KPIs["EN_3.1"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.5"] = "Nan"
            try:
                KPIs["EN_3.5R"] = ((KPIs["EN_3.3R"] - KPIs["EN_3.1R"]) / KPIs["EN_3.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.5R"] = "Nan"
            try:
                KPIs["EN_3.5T"] = ((KPIs["EN_3.3T"] - KPIs["EN_3.1T"]) / KPIs["EN_3.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.5T"] = "Nan"
            try:
                KPIs["EN_3.7"] = KPIs["EN_3.4"] - KPIs["EN_3.2"]
            except TypeError:
                KPIs["EN_3.7"] = "Nan"
            try:
                KPIs["EN_3.7R"] = KPIs["EN_3.4R"] - KPIs["EN_3.2R"]
            except TypeError:
                KPIs["EN_3.7R"] = "Nan"
            try:
                KPIs["EN_3.7T"] = KPIs["EN_3.4T"] - KPIs["EN_3.2T"]
            except TypeError:
                KPIs["EN_3.7T"] = "Nan"
            try:
                KPIs["EN_3.6"] = KPIs["EN_3.3"] - KPIs["EN_3.1"]
            except TypeError:
                KPIs["EN_3.6"] = "Nan"
            try:
                KPIs["EN_3.6R"] = KPIs["EN_3.3R"] - KPIs["EN_3.1R"]
            except TypeError:
                KPIs["EN_3.6R"] = "Nan"
            try:
                KPIs["EN_3.6T"] = KPIs["EN_3.3T"] - KPIs["EN_3.1T"]
            except TypeError:
                KPIs["EN_3.6T"] = "Nan"
            KPIs["EN_4.3"] = self.pecRENs
            KPIs["EN_4.3R"] = self.pecRENsR
            KPIs["EN_4.3T"] = self.pecRENsT
            try:
                KPIs["EN_4.4"] = round(self.pecRENs/self.pec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.4"] = "Nan"
            try:
                KPIs["EN_4.4R"] = round(self.pecRENsR / self.pecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.4R"] = "Nan"
            try:
                KPIs["EN_4.4T"] = round(self.pecRENsT / self.pecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.4T"] = "Nan"
            try:
                KPIs["EN_4.5"] = ((KPIs["EN_4.3"] - KPIs["EN_4.1"]) / KPIs["EN_4.1"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.5"] = "Nan"
            try:
                KPIs["EN_4.5R"] = ((KPIs["EN_4.3R"] - KPIs["EN_4.1R"]) / KPIs["EN_4.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.5R"] = "Nan"
            try:
                KPIs["EN_4.5T"] = ((KPIs["EN_4.3T"] - KPIs["EN_4.1T"]) / KPIs["EN_4.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.5T"] = "Nan"
            KPIs["EN_5.3"] = self.fecWH
            KPIs["EN_5.3R"] = self.fecWHR
            KPIs["EN_5.3T"] = self.fecWHT
            try:
                KPIs["EN_5.4"] = round(self.fecWH/self.fec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.4"] = "Nan"
            try:
                KPIs["EN_5.4R"] = round(self.fecWHR / self.fecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.4R"] = "Nan"
            try:
                KPIs["EN_5.4T"] = round(self.fecWHT / self.fecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.4T"] = "Nan"
            try:
                KPIs["EN_5.5"] = ((KPIs["EN_5.3"] - KPIs["EN_5.1"]) / KPIs["EN_5.1"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.5"] = "Nan"
            try:
                KPIs["EN_5.5R"] = ((KPIs["EN_5.3R"] - KPIs["EN_5.1R"]) / KPIs["EN_5.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.5R"] = "Nan"
            try:
                KPIs["EN_5.5T"] = ((KPIs["EN_5.3T"] - KPIs["EN_5.1T"]) / KPIs["EN_5.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.5T"] = "Nan"
            KPIs["EN_6.3"] = self.pecCF
            KPIs["EN_6.3R"] = self.pecCFR
            KPIs["EN_6.3T"] = self.pecCFT
            try:
                KPIs["EN_6.4"] = round(self.pecCF/self.pec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.4"] = "Nan"
            try:
                KPIs["EN_6.4R"] = round(self.pecCFR / self.pecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.4R"] = "Nan"
            try:
                KPIs["EN_6.4T"] = round(self.pecCFT / self.pecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.4T"] = "Nan"
            try:
                KPIs["EN_6.5"] = ((KPIs["EN_6.3"] - KPIs["EN_6.1"]) / KPIs["EN_6.1"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.5"] = "Nan"
            try:
                KPIs["EN_6.5R"] = ((KPIs["EN_6.3R"] - KPIs["EN_6.1R"]) / KPIs["EN_6.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.5R"] = "Nan"
            try:
                KPIs["EN_6.5T"] = ((KPIs["EN_6.3T"] - KPIs["EN_6.1T"]) / KPIs["EN_6.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.5T"] = "Nan"
            KPIs["EN_7.3"] = self.pecIS
            KPIs["EN_7.3R"] = self.pecISR
            KPIs["EN_7.3T"] = self.pecIST
            try:
                KPIs["EN_7.4"] = round(self.pecIS/self.pec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.4"] = "Nan"
            try:
                KPIs["EN_7.4R"] = round(self.pecISR / self.pecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.4R"] = "Nan"
            try:
                KPIs["EN_7.4T"] = round(self.pecIST / self.pecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.4T"] = "Nan"
            try:
                KPIs["EN_7.5"] = ((KPIs["EN_7.3"] - KPIs["EN_7.1"]) / KPIs["EN_7.1"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.5"] = "Nan"
            try:
                KPIs["EN_7.5R"] = ((KPIs["EN_7.3R"] - KPIs["EN_7.1R"]) / KPIs["EN_7.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.5R"] = "Nan"
            try:
                KPIs["EN_7.5T"] = ((KPIs["EN_7.3T"] - KPIs["EN_7.1T"]) / KPIs["EN_7.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.5T"] = "Nan"
            try:
                KPIs["EN_9.2"] = (self.get_UED_cooling(self.future_scenario)/KPIs["EN_3.3"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.2"] = "Nan"
            try:
                KPIs["EN_9.2R"] = (self.get_UED_cooling(self.future_scenario, use="R") / KPIs["EN_3.3R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.2R"] = "Nan"
            try:
                KPIs["EN_9.2T"] = (self.get_UED_cooling(self.future_scenario, use="T") / KPIs["EN_3.3T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.2T"] = "Nan"
            KPIs["EN_11.1"] = self.stp
            KPIs["EN_11.1R"] = self.stpR
            KPIs["EN_11.1T"] = self.stpT
            KPIs["EN_12.2"] = self.locsourbase_KPi(KPIs["EN_1.3"])
            KPIs["EN_12.2R"] = self.locsourbase_KPi(KPIs["EN_1.3R"])
            KPIs["EN_12.2T"] = self.locsourbase_KPi(KPIs["EN_1.3T"])
            try:
                KPIs["EN_12.3"] = ((KPIs["EN_12.2"]-KPIs["EN_12.1"])/KPIs["EN_12.1"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.3"] = "Nan"
            try:
                KPIs["EN_12.3R"] = ((KPIs["EN_12.2R"] - KPIs["EN_12.1R"]) / KPIs["EN_12.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.3R"] = "Nan"
            try:
                KPIs["EN_12.3T"] = ((KPIs["EN_12.2T"] - KPIs["EN_12.1T"]) / KPIs["EN_12.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.3T"] = "Nan"
            KPIs["EN_13.2a"] = self.h_fec_eta - self.get_UED_heating(self.future_scenario)
            KPIs["EN_13.2aR"] = self.h_fec_etaR - self.get_UED_heating(self.future_scenario, use="R")
            KPIs["EN_13.2aT"] = self.h_fec_etaT - self.get_UED_heating(self.future_scenario, use="T")
            KPIs["EN_13.2b"] = self.c_fec_eta - self.get_UED_cooling(self.future_scenario)
            KPIs["EN_13.2bR"] = self.c_fec_etaR - self.get_UED_cooling(self.future_scenario, use="R")
            KPIs["EN_13.2bT"] = self.c_fec_etaT - self.get_UED_cooling(self.future_scenario, use="T")
            try:
                KPIs["EN_13.3a"] = ((KPIs["EN_13.2a"] - KPIs["EN_13.1a"]) / KPIs["EN_13.1a"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3a"] = "Nan"
            try:
                KPIs["EN_13.3aR"] = ((KPIs["EN_13.2aR"] - KPIs["EN_13.1aR"]) / KPIs["EN_13.1aR"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3aR"] = "Nan"
            try:
                KPIs["EN_13.3aT"] = ((KPIs["EN_13.2aT"] - KPIs["EN_13.1aT"]) / KPIs["EN_13.1aT"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3aT"] = "Nan"
            try:
                KPIs["EN_13.3b"] = ((KPIs["EN_13.2b"] - KPIs["EN_13.1b"]) / KPIs["EN_13.1b"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3b"] = "Nan"
            try:
                KPIs["EN_13.3bR"] = ((KPIs["EN_13.2bR"] - KPIs["EN_13.1bR"]) / KPIs["EN_13.1bR"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3bR"] = "Nan"
            try:
                KPIs["EN_13.3bT"] = ((KPIs["EN_13.2bT"] - KPIs["EN_13.1bT"]) / KPIs["EN_13.1bT"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3bT"] = "Nan"
            try:
                KPIs["EN_14.2a"] = self.h_ued/self.h_length
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2a"] = "Nan"
            try:
                KPIs["EN_14.2aR"] = self.h_uedR / self.h_length
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2aR"] = "Nan"
            try:
                KPIs["EN_14.2aT"] = self.h_uedT / self.h_length
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2aT"] = "Nan"
            try:
                KPIs["EN_14.2b"] = self.c_ued/self.c_length
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2b"] = "Nan"
            try:
                KPIs["EN_14.2bR"] = self.c_uedR / self.c_length
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2bR"] = "Nan"
            try:
                KPIs["EN_14.2bT"] = self.c_uedT / self.c_length
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2bT"] = "Nan"
            try:
                KPIs["EN_14.3a"] = ((KPIs["EN_14.2a"] - KPIs["EN_14.1a"]) / KPIs["EN_14.1a"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3a"] = "Nan"
            try:
                KPIs["EN_14.3aR"] = ((KPIs["EN_14.2aR"] - KPIs["EN_14.1aR"]) / KPIs["EN_14.1aR"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3aR"] = "Nan"
            try:
                KPIs["EN_14.3aT"] = ((KPIs["EN_14.2aT"] - KPIs["EN_14.1aT"]) / KPIs["EN_14.1aT"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3aT"] = "Nan"
            try:
                KPIs["EN_14.3b"] = ((KPIs["EN_14.2b"] - KPIs["EN_14.1b"]) / KPIs["EN_14.1b"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3b"] = "Nan"
            try:
                KPIs["EN_14.3bR"] = ((KPIs["EN_14.2bR"] - KPIs["EN_14.1bR"]) / KPIs["EN_14.1bR"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3bR"] = "Nan"
            try:
                KPIs["EN_14.3bT"] = ((KPIs["EN_14.2bT"] - KPIs["EN_14.1bT"]) / KPIs["EN_14.1bT"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3bT"] = "Nan"
            try:
                KPIs["EN_15.2"] = round(sum([self.YEOHbase[key][0]/self.YEOHbase[key][1] for key in self.YEOHbase.keys()]), 2)
                KPIs["EN_15.2R"] = round(
                    sum([self.YEOHbaseR[key][0] / self.YEOHbaseR[key][1] for key in self.YEOHbaseR.keys()]), 2)
                KPIs["EN_15.2T"] = round(
                    sum([self.YEOHbaseT[key][0] / self.YEOHbaseT[key][1] for key in self.YEOHbaseT.keys()]), 2)
            except:
                KPIs["EN_15.2"] = -274
                KPIs["EN_15.2R"] = -274
                KPIs["EN_15.2T"] = -274

            KPIs["ENV_1.5"] = self.CO2
            KPIs["ENV_1.5R"] = self.CO2R
            KPIs["ENV_1.5T"] = self.CO2T
            try:
                KPIs["ENV_1.6"] = KPIs["ENV_1.5"] / KPIs["EN_1.3"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.6"] = "Nan"
            try:
                KPIs["ENV_1.6R"] = KPIs["ENV_1.5R"] / KPIs["EN_1.3R"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.6R"] = "Nan"
            try:
                KPIs["ENV_1.6T"] = KPIs["ENV_1.5T"] / KPIs["EN_1.3T"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.6T"] = "Nan"
            try:
                KPIs["ENV_1.1"] = ((KPIs["ENV_1.5"] - KPIs["ENV_1.3"]) / KPIs["ENV_1.3"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.1"] = "Nan"
            try:
                KPIs["ENV_1.1R"] = ((KPIs["ENV_1.5R"] - KPIs["ENV_1.3R"]) / KPIs["ENV_1.3R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.1R"] = "Nan"
            try:
                KPIs["ENV_1.1T"] = ((KPIs["ENV_1.5T"] - KPIs["ENV_1.3T"]) / KPIs["ENV_1.3T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.1T"] = "Nan"
            try:
                KPIs["ENV_1.2"] = KPIs["ENV_1.5"] - KPIs["ENV_1.3"]
            except TypeError:
                KPIs["ENV_1.2"] = "Nan"
            try:
                KPIs["ENV_1.2R"] = KPIs["ENV_1.5R"] - KPIs["ENV_1.3R"]
            except TypeError:
                KPIs["ENV_1.2R"] = "Nan"
            try:
                KPIs["ENV_1.2T"] = KPIs["ENV_1.5T"] - KPIs["ENV_1.3T"]
            except TypeError:
                KPIs["ENV_1.2T"] = "Nan"
            KPIs["ENV_2.3"] = self.NOx
            KPIs["ENV_2.3R"] = self.NOxR
            KPIs["ENV_2.3T"] = self.NOxT
            try:
                KPIs["ENV_2.4"] = KPIs["ENV_2.3"] / KPIs["EN_1.3"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.4"] = "Nan"
            try:
                KPIs["ENV_2.4R"] = KPIs["ENV_2.3R"] / KPIs["EN_1.3R"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.4R"] = "Nan"
            try:
                KPIs["ENV_2.4T"] = KPIs["ENV_2.3T"] / KPIs["EN_1.3T"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.4T"] = "Nan"
            try:
                KPIs["ENV_2.5"] = ((KPIs["ENV_2.3"] - KPIs["ENV_2.1"]) / KPIs["ENV_2.1"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.5"] = "Nan"
            try:
                KPIs["ENV_2.5R"] = ((KPIs["ENV_2.3R"] - KPIs["ENV_2.1R"]) / KPIs["ENV_2.1R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.5R"] = "Nan"
            try:
                KPIs["ENV_2.5T"] = ((KPIs["ENV_2.3T"] - KPIs["ENV_2.1T"]) / KPIs["ENV_2.1T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.5T"] = "Nan"
            try:
                KPIs["ENV_2.6"] = KPIs["ENV_2.3"] - KPIs["ENV_2.1"]
            except TypeError:
                KPIs["ENV_2.6"] = "Nan"
            try:
                KPIs["ENV_2.6R"] = KPIs["ENV_2.3R"] - KPIs["ENV_2.1R"]
            except TypeError:
                KPIs["ENV_2.6R"] = "Nan"
            try:
                KPIs["ENV_2.6T"] = KPIs["ENV_2.3T"] - KPIs["ENV_2.1T"]
            except TypeError:
                KPIs["ENV_2.6T"] = "Nan"
            KPIs["ENV_2.9"] = self.SOx
            KPIs["ENV_2.9R"] = self.SOxR
            KPIs["ENV_2.9T"] = self.SOxT
            try:
                KPIs["ENV_2.10"] = KPIs["ENV_2.9"] / KPIs["EN_1.3"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.10"] = "Nan"
            try:
                KPIs["ENV_2.10R"] = KPIs["ENV_2.9R"] / KPIs["EN_1.3R"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.10R"] = "Nan"
            try:
                KPIs["ENV_2.10T"] = KPIs["ENV_2.9T"] / KPIs["EN_1.3T"]
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.10T"] = "Nan"
            try:
                KPIs["ENV_2.11"] = ((KPIs["ENV_2.9"] - KPIs["ENV_2.7"]) / KPIs["ENV_2.7"])*100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.11"] = "Nan"
            try:
                KPIs["ENV_2.11R"] = ((KPIs["ENV_2.9R"] - KPIs["ENV_2.7R"]) / KPIs["ENV_2.7R"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.11R"] = "Nan"
            try:
                KPIs["ENV_2.11T"] = ((KPIs["ENV_2.9T"] - KPIs["ENV_2.7T"]) / KPIs["ENV_2.7T"]) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.11T"] = "Nan"
            try:
                KPIs["ENV_2.12"] = KPIs["ENV_2.9"] - KPIs["ENV_2.7"]
            except TypeError:
                KPIs["ENV_2.12"] = "Nan"
            try:
                KPIs["ENV_2.12R"] = KPIs["ENV_2.9R"] - KPIs["ENV_2.7R"]
            except TypeError:
                KPIs["ENV_2.12R"] = "Nan"
            try:
                KPIs["ENV_2.12T"] = KPIs["ENV_2.9T"] - KPIs["ENV_2.7T"]
            except TypeError:
                KPIs["ENV_2.12T"] = "Nan"
            KPIs["ENV_2.15"] = self.PM10
            KPIs["ENV_2.15R"] = self.PM10R
            KPIs["ENV_2.15T"] = self.PM10T
            try:
                KPIs["ENV_2.16"] = KPIs["ENV_2.15"] / KPIs["EN_1.3"]
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.16"] = "Nan"
            try:
                KPIs["ENV_2.16R"] = KPIs["ENV_2.15R"] / KPIs["EN_1.3R"]
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.16R"] = "Nan"
            try:
                KPIs["ENV_2.16T"] = KPIs["ENV_2.15T"] / KPIs["EN_1.3T"]
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.16T"] = "Nan"
            try:
                KPIs["ENV_2.17"] = ((KPIs["ENV_2.15"] - KPIs["ENV_2.13"]) / KPIs["ENV_2.13"])*100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.17"] = "Nan"
            try:
                KPIs["ENV_2.17R"] = ((KPIs["ENV_2.15R"] - KPIs["ENV_2.13R"]) / KPIs["ENV_2.13R"]) * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.17R"] = "Nan"
            try:
                KPIs["ENV_2.17T"] = ((KPIs["ENV_2.15T"] - KPIs["ENV_2.13T"]) / KPIs["ENV_2.13T"]) * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.17T"] = "Nan"
            try:
                KPIs["ENV_2.18"] = KPIs["ENV_2.15"] - KPIs["ENV_2.13"]
            except TypeError:
                KPIs["ENV_2.18"] = "Nan"
            try:
                KPIs["ENV_2.18R"] = KPIs["ENV_2.15R"] - KPIs["ENV_2.13R"]
            except TypeError:
                KPIs["ENV_2.18R"] = "Nan"
            try:
                KPIs["ENV_2.18T"] = KPIs["ENV_2.15T"] - KPIs["ENV_2.13T"]
            except TypeError:
                KPIs["ENV_2.18T"] = "Nan"

            KPIs["ECO_1.4"] = self.capext
            KPIs["ECO_1.4R"] = self.capextR
            KPIs["ECO_1.4T"] = self.capextT
            KPIs["ECO_1.2"] = self.eco_uno_punto_due()
            KPIs["ECO_1.2R"] = self.eco_uno_punto_due(use="R")
            KPIs["ECO_1.2T"] = self.eco_uno_punto_due(use="T")
            KPIs["ECO_1.3"] = self.eco_uno_punto_tre()
            KPIs["ECO_1.3R"] = self.eco_uno_punto_tre(use="R")
            KPIs["ECO_1.3T"] = self.eco_uno_punto_tre(use="T")
            KPIs["ECO_1.1"] = self.eco_1_punto_1()
            KPIs["ECO_1.1R"] = self.eco_1_punto_1(use="R")
            KPIs["ECO_1.1T"] = self.eco_1_punto_1(use="T")
            KPIs["ECO_2.1"] = self.opex
            KPIs["ECO_2.1R"] = self.opexR
            KPIs["ECO_2.1T"] = self.opexT
            KPIs["ECO_2.2"] = self.eco_2_punto_2()
            KPIs["ECO_2.2R"] = self.eco_2_punto_2(use="R")
            KPIs["ECO_2.2T"] = self.eco_2_punto_2(use="T")
            KPIs["ECO_3.1"] = self.eco_3_punto_1()
            KPIs["ECO_3.1R"] = self.eco_3_punto_1(use="R")
            KPIs["ECO_3.1T"] = self.eco_3_punto_1(use="T")
            KPIs["ECO_3.2"] = self.eco_3_punto_2(KPIs["ENV_1.2"], use=None)
            KPIs["ECO_3.2R"] = self.eco_3_punto_2(KPIs["ENV_1.2R"], use="R")
            KPIs["ECO_3.2T"] = self.eco_3_punto_2(KPIs["ENV_1.2T"], use="T")


            # SO 3.2 FEavailability è un output del MM
            try:
                KPIs["SO_3.2"] = round((1 - (KPIs["EN_2.3"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.2"] = "Nan"
            try:
                KPIs["SO_3.2R"] = round((1 - (KPIs["ENV_2.3R"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.2R"] = "Nan"
            try:
                KPIs["SO_3.2T"] = round((1 - (KPIs["ENV_2.3T"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.2T"] = "Nan"

            try:
                KPIs["SO_3.3"] = round(((KPIs["SO_3.2"] / KPIs["SO_3.1"]) - 1) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.3"] = "Nan"
            try:
                KPIs["SO_3.3R"] = round(((KPIs["SO_3.2R"] / KPIs["SO_3.1R"]) - 1) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.3R"] = "Nan"
            try:
                KPIs["SO_3.3T"] = round(((KPIs["SO_3.2T"] / KPIs["SO_3.1T"]) - 1) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.3T"] = "Nan"




            for key in KPIs.keys():
                try:
                    KPIs[key] = round(KPIs[key], 2)
                except:
                    pass
        # ------------------------ ###
        # --- BASELINE KPIs!!! --- ###
        # ------------------------ ###
        # ------------------------ ###
        # --- BASELINE KPIs!!! --- ###
        # ------------------------ ###
        # ------------------------ ###
        # --- BASELINE KPIs!!! --- ###
        # ------------------------ ###
        else:
            KPIs["EN_1.1"] = round(self.pec, 2)
            KPIs["EN_1.1R"] = round(self.pecR, 2)
            KPIs["EN_1.1T"] = round(self.pecT, 2)
            try:
                KPIs["EN_1.2"] = round(self.pec/self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.2"] = "Nan"
            try:
                KPIs["EN_1.2R"] = round(self.pecR/self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.2R"] = "Nan"
            try:
                KPIs["EN_1.2T"] = round(self.pecT/(self.area-self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.2T"] = "Nan"
            KPIs["EN_2.1"] = round(self.fec, 2)
            KPIs["EN_2.1R"] = round(self.fecR, 2)
            KPIs["EN_2.1T"] = round(self.fecT, 2)
            try:
                KPIs["EN_2.2"] = round(self.fec/self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.2"] = "Nan"
            try:
                KPIs["EN_2.2R"] = round(self.fecR/self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.2R"] = "Nan"
            try:
                KPIs["EN_2.2T"] = round(self.fecT/(self.area-self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.2T"] = "Nan"

            KPIs["EN_3.1"] = round(self.get_UED(self.baseline_scenario), 2)
            KPIs["EN_3.1R"] = round(self.get_UED(self.baseline_scenario, use="R"), 2)
            KPIs["EN_3.1T"] = round(self.get_UED(self.baseline_scenario, use="T"), 2)
            try:
                KPIs["EN_3.2"] = round(KPIs["EN_3.1"]/self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.2"] = "Nan"
            try:
                KPIs["EN_3.2R"] = round(KPIs["EN_3.1R"]/self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.2R"] = "Nan"
            try:
                KPIs["EN_3.2T"] = round(KPIs["EN_3.1T"] / (self.area-self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.2T"] = "Nan"
            KPIs["EN_4.1"] = round(self.pecRENs, 2)
            KPIs["EN_4.1T"] = round(self.pecRENsT, 2)
            KPIs["EN_4.1R"] = round(self.pecRENsR, 2)
            try:
                KPIs["EN_4.2"] = round(self.pecRENs/self.pec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.2"] = "Nan"
            try:
                KPIs["EN_4.2R"] = round(self.pecRENsR/self.pecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.2R"] = "Nan"
            try:
                KPIs["EN_4.2T"] = round(self.pecRENsT/self.pecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.2T"] = "Nan"
            KPIs["EN_5.1"] = round(self.fecWH, 2)
            KPIs["EN_5.1R"] = round(self.fecWHR, 2)
            KPIs["EN_5.1T"] = round(self.fecWHT, 2)
            try:
                KPIs["EN_5.2"] = round(self.fecWH/self.fec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.2"] = "Nan"
            try:
                KPIs["EN_5.2R"] = round(self.fecWHR/self.fecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.2R"] = "Nan"
            try:
                KPIs["EN_5.2T"] = round(self.fecWHT/self.fecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.2T"] = "Nan"
            KPIs["EN_6.1"] = round(self.pecCF, 2)
            KPIs["EN_6.1R"] = round(self.pecCFR, 2)
            KPIs["EN_6.1T"] = round(self.pecCFT, 2)
            try:
                KPIs["EN_6.2"] = round(self.pecCF/self.pec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.2"] = "Nan"
            try:
                KPIs["EN_6.2R"] = round(self.pecCFR/self.pecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.2R"] = "Nan"
            try:
                KPIs["EN_6.2T"] = round(self.pecCFT/self.pecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.2T"] = "Nan"
            KPIs["EN_7.1"] = round(self.pecIS, 2)
            KPIs["EN_7.1R"] = round(self.pecISR, 2)
            KPIs["EN_7.1T"] = round(self.pecIST, 2)
            try:
                KPIs["EN_7.2"] = round(self.pecIS/self.pec, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.2"] = "Nan"
            try:
                KPIs["EN_7.2R"] = round(self.pecISR/self.pecR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.2R"] = "Nan"
            try:
                KPIs["EN_7.2T"] = round(self.pecIST/self.pecT, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.2T"] = "Nan"
            try:
                KPIs["EN_9.1"] = round((self.get_UED_cooling(self.baseline_scenario)/KPIs["EN_3.1"])*100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.1"] = "Nan"
            try:
                KPIs["EN_9.1R"] = round((self.get_UED_cooling(self.baseline_scenario, use="R")/KPIs["EN_3.1R"])*100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.1R"] = "Nan"
            try:
                KPIs["EN_9.1T"] = round((self.get_UED_cooling(self.baseline_scenario, use="T")/KPIs["EN_3.1T"])*100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.1T"] = "Nan"
            KPIs["EN_11.2"] = round(self.stp, 2)
            KPIs["EN_11.2R"] = round(self.stpR, 2)
            KPIs["EN_11.2T"] = round(self.stpT, 2)
            try:
                KPIs["EN_11.3"] = round(KPIs["EN_11.2"]/KPIs["EN_2.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_11.3"] = "Nan"
            try:
                KPIs["EN_11.3R"] = round(KPIs["EN_11.2R"]/KPIs["EN_2.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_11.3R"] = "Nan"
            try:
                KPIs["EN_11.3T"] = round(KPIs["EN_11.2T"]/KPIs["EN_2.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_11.3T"] = "Nan"
            KPIs["EN_12.1"] = round(self.locsourbase_KPi(KPIs["EN_1.1"]), 2)
            KPIs["EN_12.1R"] = round(self.locsourbase_KPi(KPIs["EN_1.1R"]), 2)
            KPIs["EN_12.1T"] = round(self.locsourbase_KPi(KPIs["EN_1.1T"]), 2)
            KPIs["EN_13.1a"] = round(self.h_fec_eta - self.get_UED_heating(self.baseline_scenario), 2)
            KPIs["EN_13.1aR"] = round(self.h_fec_etaR - self.get_UED_heating(self.baseline_scenario, use="R"), 2)
            KPIs["EN_13.1aT"] = round(self.h_fec_etaT - self.get_UED_heating(self.baseline_scenario, use="T"), 2)
            KPIs["EN_13.1b"] = round(self.c_fec_eta - self.get_UED_cooling(self.baseline_scenario), 2)
            KPIs["EN_13.1bR"] = round(self.c_fec_etaR - self.get_UED_cooling(self.baseline_scenario, use="R"), 2)
            KPIs["EN_13.1bT"] = round(self.c_fec_etaT - self.get_UED_cooling(self.baseline_scenario, use="T"), 2)
            try:
                KPIs["EN_14.1a"] = round(self.h_ued/self.h_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1a"] = "Nan"
            try:
                KPIs["EN_14.1aR"] = round(self.h_uedR/self.h_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1aR"] = "Nan"
            try:
                KPIs["EN_14.1aT"] = round(self.h_uedT/self.h_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1aT"] = "Nan"
            try:
                KPIs["EN_14.1b"] = round(self.c_ued/self.c_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1b"] = "Nan"
            try:
                KPIs["EN_14.1bR"] = round(self.c_uedR/self.c_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1bR"] = "Nan"
            try:
                KPIs["EN_14.1bT"] = round(self.c_uedT/self.c_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1bT"] = "Nan"
            try:
                KPIs["EN_15.1"] = round(
                    sum([self.YEOHbase[key][0] / self.YEOHbase[key][1] for key in self.YEOHbase.keys()]), 2)
            except:
                KPIs["EN_15.1"] = -274
            try:
                KPIs["EN_15.1R"] = round(
                    sum([self.YEOHbaseR[key][0] / self.YEOHbaseR[key][1] for key in self.YEOHbaseR.keys()]), 2)
            except:
                KPIs["EN_15.1R"] = -274
            try:
                KPIs["EN_15.1T"] = round(
                    sum([self.YEOHbaseT[key][0] / self.YEOHbaseT[key][1] for key in self.YEOHbaseT.keys()]), 2)
            except:
                KPIs["EN_15.1T"] = -274
            KPIs["ENV_1.3"] = round(self.CO2, 2)
            KPIs["ENV_1.3R"] = round(self.CO2R, 2)
            KPIs["ENV_1.3T"] = round(self.CO2T, 2)
            try:
                KPIs["ENV_1.4"] = round(KPIs["ENV_1.3"]/KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.4"] = "Nan"
            try:
                KPIs["ENV_1.4R"] = round(KPIs["ENV_1.3R"]/KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.4R"] = "Nan"
            try:
                KPIs["ENV_1.4T"] = round(KPIs["ENV_1.3T"]/KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.4T"] = "Nan"
            KPIs["ENV_2.1"] = round(self.NOx, 2)
            KPIs["ENV_2.1R"] = round(self.NOxR, 2)
            KPIs["ENV_2.1T"] = round(self.NOxT, 2)
            try:
                KPIs["ENV_2.2"] = round(KPIs["ENV_2.1"]/KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.2"] = "Nan"
            try:
                KPIs["ENV_2.2R"] = round(KPIs["ENV_2.1R"]/KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.2R"] = "Nan"
            try:
                KPIs["ENV_2.2T"] = round(KPIs["ENV_2.1T"]/KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.2T"] = "Nan"
            KPIs["ENV_2.7"] = round(self.SOx, 2)
            KPIs["ENV_2.7R"] = round(self.SOxR, 2)
            KPIs["ENV_2.7T"] = round(self.SOxT, 2)
            try:
                KPIs["ENV_2.8"] = round(KPIs["ENV_2.7"]/KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.8"] = "Nan"
            try:
                KPIs["ENV_2.8R"] = round(KPIs["ENV_2.7R"]/KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.8R"] = "Nan"
            try:
                KPIs["ENV_2.8T"] = round(KPIs["ENV_2.7T"]/KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.8T"] = "Nan"
            KPIs["ENV_2.13"] = round(self.PM10, 2)
            KPIs["ENV_2.13R"] = round(self.PM10R, 2)
            KPIs["ENV_2.13T"] = round(self.PM10T, 2)
            try:
                KPIs["ENV_2.14"] = round(KPIs["ENV_2.13"]/KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.14"] = "Nan"
            try:
                KPIs["ENV_2.14R"] = round(KPIs["ENV_2.13R"]/KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.14R"] = "Nan"
            try:
                KPIs["ENV_2.14T"] = round(KPIs["ENV_2.13T"]/KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.14T"] = "Nan"

                #SO 3.1 FEavailability è un output del MM
            try:
                KPIs["SO_3.1"] = round((1 - (KPIs["EN_2.1"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.1"] = "Nan"
            try:
                KPIs["SO_3.1R"] =round((1 - (KPIs["EN_2.1R"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.1R"] = "Nan"
            try:
                KPIs["SO_3.1T"] = round((1 - (KPIs["EN_2.1T"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError) as e:
                KPIs["SO_3.1T"] = "Nan"

        return KPIs

    def input_reset(self):
        self.pef_sources_tab = None
        self.ef_sources_tab = None
        self.tech_tab = None
        self.work_folder = None
        self.network = None
        self.building_id = None
        self.step0_district_sources_tab = None
        self.future_scenario = None
        self.baseline_scenario = None
        self.sources = None
        self.individual_tech_power_column = None
        self.district_tech_power_column = None
        self.step0_district_sources_tab = None

    def reset(self, reset_interface=False):
        self.input_reset()
        self.initialize()

    def district_var_check(self):
        if self.pef_sources_tab is None:
            return False
        if self.tech_tab is None:
            return False
        if self.work_folder is None:
            return False
        if self.network is None:
            return False
        return True

    def individual_var_check(self):
        if self.tech_tab is None:
            return False
        if self.work_folder is None:
            return False
        if self.building_id is None:
            return False
        return True

    def ENV_KPIs_check(self):
        if self.ef_sources_tab is None:
            return False
        return True

    def get_source_infos(self, widget, source):
        for i in range(widget.rowCount()):
            if widget.verticalHeaderItem(i).text() == source:
                try:
                    return [float(widget.item(i, 0).text()),
                            float(widget.item(i, 1).text())]
                except:
                    print("KPIsCalculator.py, get_source_infos: impossible to get row", i)

        return [0, 0]

    def district_emission(self, ef_column_index=1):
        CO2 = 0
        for i in range(self.tech_tab.topLevelItemCount()):
            n = self.tech_tab.topLevelItem(i)
            if n.data(0, Qt.UserRole) == self.network.get_ID():
                for j in range(n.childCount()):
                    for k in range(self.ef_sources_tab.rowCount()):
                        if self.ef_sources_tab.verticalHeaderItem(k).text() == n.child(j).text(2):
                            try:
                                emission_factor = self.ef_sources_tab.text(k, ef_column_index)
                                pef, _ = self.get_source_infos(self.pef_sources_tab, n.child(j).text(2))
                            except:
                                emission_factor = 1
                                print("KPIsCalculator, district_CO2. Item", k, ef_column_index, "failed to get from",
                                      self.ef_sources_tab, "table")
                            break
                    else:
                        print("KPIsCalculator, district_CO2. Item", k, 1, "not found in ", self.ef_sources_tab,
                              "table")
                        emission_factor = 1
                    category = n.child(j).data(1, Qt.UserRole)
                    file = os.path.join(self.work_folder, "Results_" + category + "_" + self.network.get_ID() + ".csv")
                    CO2 = CO2 + pef * emission_factor * self.sum_file(file)
        return CO2

    def individual_emission(self, ef_column_index=1):
        CO2 = 0
        for i in range(self.tech_tab.childCount()):
            scope_item = self.tech_tab.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)
                for k in range(self.ef_sources_tab.rowCount()):
                    if self.ef_sources_tab.verticalHeaderItem(k).text() == technology.text(2):
                        try:
                            pef, _ = self.get_source_infos(self.pef_sources_tab, technology.text(2))
                            emission_factor = self.ef_sources_tab.text(k, ef_column_index)
                        except:
                            pef = 1
                            emission_factor = 1
                            print("KPIsCalculator, individual_emission. Item", k, ef_column_index, "failed to get from",
                                  self.ef_sources_tab, "table")
                        break
                else:
                    print("KPIsCalculator, individual_emission. Emission factor of pef not found")
                    emission_factor = 1
                    pef = 1
                julia_category = str(technology.data(0, Qt.UserRole))
                file = os.path.join(self.work_folder, "Result_" + julia_category + "_" + self.building_id + ".csv")
                CO2 = CO2 + emission_factor*pef*(self.sum_file(file))
        return CO2

    def get_UED(self, layer, use=None):
        total = 0
        for f in layer.getFeatures():
            if use == "R":
                check = f.attribute("Use") == "Residential"
            elif use == "T":
                check = not f.attribute("Use") == "Residential"
            else:
                check = True
            if check:
                try:
                    total = total + float(f.attribute("AHeatDem")) + float(f.attribute("ACoolDem"))\
                            + float(f.attribute("ADHWDem"))
                except:
                    print("KPIsCalculator, get_UED. Problems calculating UED for layer", layer.name())
        return total/1000

    def get_UED_cooling(self, layer, use=None):
        total = 0
        for f in layer.getFeatures():
            if use == "R":
                check = f.attribute("Use") == "Residential"
            elif use == "T":
                check = not f.attribute("Use") == "Residential"
            else:
                check = True
            if check:
                try:
                    total = total + float(f.attribute("ACoolDem"))
                except:
                    print("KPIsCalculator, get_UED_cooling. Problems calculating UED for layer", layer.name())
        return total/1000

    def get_UED_heating(self, layer, use=None):
        total = 0
        for f in layer.getFeatures():
            if use == "R":
                check = f.attribute("Use") == "Residential"
            elif use == "T":
                check = not f.attribute("Use") == "Residential"
            else:
                check = True
            if check:
                try:
                    total = total + float(f.attribute("AHeatDem"))
                except:
                    print("KPIsCalculator, get_UED_cooling. Problems calculating UED for layer", layer.name())
        return total/1000

    def district_solar_penetration(self):
        stp = 0
        dr = os.path.join(self.work_folder, "..", "..")
        st_irradiation = os.path.join(dr, "Global_solar_irradiation.csv")
        st_2_irradiation = os.path.join(dr, "Global_solar_irradiation_2.csv")
        sts_irradiation = os.path.join(dr, "Global_solar_irradiation_seasonal.csv")
        for i in range(self.tech_tab.topLevelItemCount()):
            n = self.tech_tab.topLevelItem(i)
            if n.data(0, Qt.UserRole) == self.network.get_ID():
                for j in range(n.childCount()):
                    if n.child(j).data(1, Qt.UserRole) == "ST":
                        stp = stp + float(n.child(j).text(3)) * self.sum_file(st_irradiation)
                    if n.child(j).data(1, Qt.UserRole) == "ST_2":
                        stp = stp + float(n.child(j).text(3)) * self.sum_file(st_2_irradiation)
                    if n.child(j).data(1, Qt.UserRole) == "ST":
                        stp = stp + float(n.child(j).text(3)) * self.sum_file(sts_irradiation)
        return stp

    def individual_solar_penetration(self):
        stp = 0
        dr = os.path.join(self.work_folder, "..")
        st_irradiation = os.path.join(dr, "Global_solar_irradiation.csv")
        st_2_irradiation = os.path.join(dr, "Global_solar_irradiation_2.csv")
        sts_irradiation = os.path.join(dr, "Global_solar_irradiation_seasonal.csv")
        for i in range(self.tech_tab.childCount()):
            t = self.tech_tab.child(i)
            for j in range(t.childCount()):
                technology = t.child(j)
                if technology.data(0, Qt.UserRole) == "ST":
                    stp = stp + float(technology.text(3)) * self.sum_file(st_irradiation)
                if technology.data(0, Qt.UserRole) == "ST_2":
                    stp = stp + float(technology.text(3)) * self.sum_file(st_2_irradiation)
                if technology.data(0, Qt.UserRole) == "ST_seasonal":
                    stp = stp + float(technology.text(3)) * self.sum_file(sts_irradiation)
        return stp

    def building_PEC_calculation(self):
        dr = self.work_folder
        item = self.tech_tab
        building_id = self.building_id
        pec = 0.0
        for i in range(item.childCount()):
            scope_item = item.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)
                pef, _ = self.get_source_infos(self.pef_sources_tab, technology.text(2))
                print("building_PEC_calculation, technology.text(2)", technology.text(2), "pef", pef)
                julia_category = str(technology.data(0, Qt.UserRole))
                print("building_PEC_calculation, julia_category", julia_category)
                file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                print("building_PEC_calculation, file", file)
                pec = pec + pef*(self.sum_file(file))
        return pec

    def district_pec(self):
        dr = self.work_folder
        network_id = self.network.get_ID()
        widget = self.tech_tab
        sources_widget = self.pef_sources_tab
        if widget is None:
            return 0
        if sources_widget is None:
            return 0
        pec = 0
        for i in range(widget.topLevelItemCount()):
            try:
                item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
                # moved to children items
                # item_julia_category = str(widget.topLevelItem(i).data(1, Qt.UserRole))
            except:
                print("KPIsCalculator, district_pec. Network:", network_id, "Failed to retrieve item_network_id and/or "
                                                                   "item_julia_categoty from widget", widget)
                continue
            if item_network_id == network_id:
                for j in range(widget.topLevelItem(i).childCount()):
                    tech = widget.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    try:
                        pef, _ = self.get_source_infos(sources_widget, tech.text(2))
                    except:
                        pef = 1
                        print("KPIsCalculator, district_pec. Problems with method get_source_infos: ", widget.topLevelItem(i).text(2))
                    file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                    try:
                        pec = pec + pef*(self.sum_file(file))
                    except:
                        print("KPIsCalculator, district_pec. Error summing file", file)
        return pec

    def building_pecRENs_calculation(self, dr, item, building_id):
        pecRENs = 0.0
        for i in range(item.childCount()):
            scope_item = item.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)
                pef, _ = self.get_source_infos(self.pef_sources_tab, technology.text(2))
                print("building_pecRENs_calculation, technology.text(2)", technology.text(2), "pef", pef)
                # select only specific sources
                if technology.text(2) in self.sources.sources_rens:
                    julia_category = str(technology.data(0, Qt.UserRole))
                    print("building_pecRENs_calculation, technology.data(0, Qt.UserRole)", julia_category)
                    file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                    print("building_pecRENs_calculation, file", file)
                    pecRENs = pecRENs + pef*(self.sum_file(file))
        return pecRENs

    def district_pecRENs(self, dr, network_id, widget=None, sources_widget=None):
        pecRENs = 0.0
        if widget is None:
            return pecRENs
        if sources_widget is None:
            return pecRENs
        for i in range(widget.topLevelItemCount()):
            try:
                item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
            except:
                print("KPIsCalculator, district_pecRENs. Network:", network_id, "Failed to retrieve item_network_id and/or "
                                                                   "item_julia_categoty from widget", widget)
                continue
            if item_network_id == network_id:
                for j in range(widget.topLevelItem(i).childCount()):
                    tech = widget.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    try:
                        pef, _ = self.get_source_infos(sources_widget, tech.text(2))
                    except:
                        print("KPIsCalculator, district_pecRENs. Problems with method get_source_infos: ", tech.text(2))
                    if tech.text(2) in self.sources.sources_rens:
                        file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                        try:
                            pecRENs = pecRENs + pef*(self.sum_file(file))
                        except:
                            print("KPIsCalculator, district_pecRENs. Error summing file", file)
        return pecRENs

    def building_fecWH_calculation(self, dr, item, building_id):
        fecWH = 0.0
        for i in range(item.childCount()):
            scope_item = item.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)
                # select only specific sources
                if technology.text(2) in self.sources.sources_fecWH:
                    julia_category = str(technology.data(0, Qt.UserRole))
                    print("building_fecWH_calculation, technology.data(0, Qt.UserRole)", julia_category)
                    file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                    print("building_fecWH_calculation, file", file)
                    fecWH = fecWH + (self.sum_file(file))
        return fecWH

    def district_fecWH(self, dr, network_id, widget=None):
        fecWH = 0.0
        if widget is None:
            return fecWH
        for i in range(widget.topLevelItemCount()):
            try:
                item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
            except:
                print("KPIsCalculator, district_fecWH. Network:", network_id, "Failed to retrieve item_network_id and/or "
                                                                   "item_julia_categoty from widget", widget)
                continue
            if item_network_id == network_id:
                for j in range(widget.topLevelItem(i).childCount()):
                    tech = widget.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    if tech.text(2) in self.sources.sources_fecWH:
                        file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                        try:
                            fecWH = fecWH + self.sum_file(file)
                        except:
                            print("KPIsCalculator, district_fecWH. Error summing file", file)
        return fecWH

    def building_pecCF_calculation(self, dr, item, building_id):
        pecCF = 0.0
        for i in range(item.childCount()):
            scope_item = item.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)
                pef, _ = self.get_source_infos(self.pef_sources_tab, technology.text(2))
                print("building_pecCF_calculation, technology.text(2)", technology.text(2), "pef", pef)
                print("building_pecCF_calculation, technology.text(2)", technology.text(2), "pef", pef)
                # select only specific sources
                if technology.text(2) in self.sources.sources_pecCF:
                    julia_category = str(technology.data(0, Qt.UserRole))
                    print("building_pecCF_calculation, technology.data(0, Qt.UserRole)", julia_category)
                    file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                    print("building_pecCF_calculation, file", file)
                    pecCF = pecCF + pef*(self.sum_file(file))
        return pecCF

    def district_pecCF(self, dr, network_id, widget=None, sources_widget=None):
        pecCF = 0.0
        if widget is None:
            return pecCF
        if sources_widget is None:
            return pecCF
        for i in range(widget.topLevelItemCount()):
            try:
                item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
                item_julia_category = str(widget.topLevelItem(i).data(1, Qt.UserRole))
            except:
                print("KPIsCalculator, district_pecCF. Network:", network_id, "Failed to retrieve item_network_id and/or "
                                                                   "item_julia_categoty from widget", widget)
                continue
            if item_network_id == network_id:
                for j in range(widget.topLevelItem(i).childCount()):
                    tech = widget.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    try:
                        pef, _ = self.get_source_infos(sources_widget, tech.text(2))
                    except:
                        print("KPIsCalculator, district_pecCF. Problems with method get_source_infos: ", tech.text(2))
                    if tech.text(2) in self.sources.sources_pecCF:
                        file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                        try:
                            pecCF = pecCF + pef*(self.sum_file(file))
                        except:
                            print("KPIsCalculator, district_pecCF. Error summing file", file)
        return pecCF

    def locsourbase_KPi(self, pec):
        sour = 0.0
        column = self.step0_district_sources_tab.columnCount()
        for i in range(self.step0_district_sources_tab.rowCount()):
            try:
                sour = sour + float(self.step0.tableWidget.item(i, column-1))
            except:
                print("KPIsCalculator, locsourbase_KPi. float(self.step0_district_sources_tab.item(i, column-1) rises some error")
                return 0
        try:
            v = sour / pec
        except(ZeroDivisionError, TypeError) as e:
            v = -274.0
        return v

    def building_pecIS_calculation(self, dr, item, building_id):
        pecIS = 0.0
        for i in range(item.childCount()):
            for j in range(item.child(i).childCount()):
                technology = item.child(i).child(j)
                pef, _ = self.get_source_infos(self.pef_sources_tab, technology.text(2))
                # select only specific sources
                if technology.text(2) in self.sources.sources_pecIS:
                    julia_category = str(technology.data(0, Qt.UserRole))
                    file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                    pecIS = pecIS + pef * (self.sum_file(file))
        return pecIS

    def district_pecIS(self, dr, network_id, widget=None, sources_widget=None):
        pecIS = 0.0
        if widget is None:
            return pecIS
        if sources_widget is None:
            return pecIS
        for i in range(widget.topLevelItemCount()):
            try:
                item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
                item_julia_category = str(widget.topLevelItem(i).data(1, Qt.UserRole))
            except:
                print("KPIsCalculator, district_pecIS. Network:", network_id, "Failed to retrieve item_network_id and/or "
                                                                     "item_julia_category from widget", widget)
                continue
            if item_network_id == network_id:
                for j in range(widget.topLevelItem(i).childCount()):
                    tech = widget.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    try:
                        pef, _ = self.get_source_infos(sources_widget, tech.text(2))
                    except:
                        print("KPIsCalculator, district_pecIS. Problems with method get_source_infos: ",
                              tech.text(2))
                    if tech.text(2) in self.sources.sources_pecIS:
                        file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                        try:
                            pecIS = pecIS + pef * (self.sum_file(file))
                        except:
                            print("KPIsCalculator, district_pecIS. Error summing file", file)
        return pecIS

    def building_FEC_calculation(self, dr, item, building_id):
        fec = 0.0
        for i in range(item.childCount()):
            scope_item = item.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)
                julia_category = str(technology.data(0, Qt.UserRole))
                file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                fec = fec + self.sum_file(file)
        return fec

    # def building_OPEX_calculation(self, dr, item, building_id,):
    #     demo_factor = 1
    #     fec_adjbase = 0
    #     fec = 0
    #     for i in range(item.childCount()):
    #         scope_item = item.child(i)
    #         for j in range(scope_item.childCount()):
    #             technology = scope_item.child(j)
    #             julia_category = str(technology.data(0, Qt.UserRole))
    #             file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
    #             try:
    #                 fec = fec + (self.sum_file(file))
    #                 fec_adjbase = fec
    #             except:
    #                 print("KPIsCalculator, OPEX. Error summing file", file)

    def district_fec(self, dr, network_id, widget=None):
        fec = 0
        if widget is None:
            return fec
        for i in range(widget.topLevelItemCount()):
            try:
                item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
                item_julia_category = str(widget.topLevelItem(i).data(1, Qt.UserRole))
            except:
                print("KPIsCalculator, district_pec. Network:", network_id, "Failed to retrieve item_network_id and/or "
                                                                   "item_julia_categoty from widget", widget)
                continue
            if item_network_id == network_id:
                for j in range(widget.topLevelItem(i).childCount()):
                    tech = widget.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                    try:
                        fec = fec + (self.sum_file(file))
                    except:
                        print("KPIsCalculator, district_pec. Error summing file", file)
        return fec

    def building_YEOHbase_calculation(self, dr, item, building_id, YEOHbase):
        for i in range(item.childCount()):
            for j in range(item.child(i).childCount()):
                technology = item.child(i).child(j)
                pef, _ = self.get_source_infos(self.pef_sources_tab, technology.text(2))
                # select only specific sources
                if technology.text(0) in YEOHbase.keys():
                    julia_category = str(technology.data(0, Qt.UserRole))
                    file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                    YEOHbase[technology.text(0)][0] = YEOHbase[technology.text(0)][0] + pef*(self.sum_file(file))
                    try:
                        YEOHbase[technology.text(0)][1] = YEOHbase[technology.text(0)][1] + float(technology.text(self.individual_tech_power_column))
                    except:
                        print("KPIsCalculator, building_YEOHbase_calculation")
                        print("YEOHbase:", YEOHbase, "technology.text(self.name_to_index(\"capacity\"))", technology.text(self.individual_tech_power_column))
                        pass

    def district_YEOHbase_calculation(self, dr, network_id, YEOHbase, widget=None, sources_widget=None):
        for j in range(widget.topLevelItemCount()):
            technology = widget.topLevelItem(j)
            for i in range(technology.childCount()):
                tech = technology.child(i)
                pef, _ = self.get_source_infos(sources_widget, tech.text(2))
                # select only specific sources
                if tech.text(1) in YEOHbase.keys():
                    julia_category = str(tech.data(1, Qt.UserRole))
                    file = os.path.join(dr, "Result_" + julia_category + "_" + network_id + ".csv")
                    YEOHbase[tech.text(1)][0] = YEOHbase[tech.text(1)][0] + pef*(self.sum_file(file))
                    try:
                        YEOHbase[tech.text(1)][1] = YEOHbase[tech.text(1)][1] + float(tech.text(self.district_tech_power_column))
                    except:
                        print("KPIsCalculator, building_YEOHbase_calculation")
                        print("YEOHbase:", YEOHbase, "technology.text(self.name_to_index(\"capacity\"))", technology.text(self.district_tech_power_column))
                        pass

    def sum_file(self, file, column=0, separator=";"):
        total = 0.0
        try:
            with open(file) as fp:
                for i, line in enumerate(fp):
                    total = total + float(line.split(separator)[column])
        except:
            print("KPIsCalculator, sum_file error!")
            print("file", file, "column", column, "separator", separator)
            return 0.0
        print("KPIsCalculator, sum_file, total", total)
        return total

    def get_area(self, building_id):
        expr = QgsExpression("BuildingID=" + building_id)
        if self.baseline_scenario is None:
            print("KPIsCalculator, KPIs_baselineScenario: baseline_scenario is not defined")
            return
        fs = [ft for ft in self.baseline_scenario.getFeatures(QgsFeatureRequest(expr))]
        if len(fs) > 0:
            feature_0 = fs[0]
        else:
            print("get_area: FALLITO MALE", building_id)
            return 0
        return feature_0.geometry().area()

    def initialize_YEOHbase(self):
        self.YEOHbase = {}
        self.YEOHbaseT = {}
        self.YEOHbaseR = {}
        for key in self.sources.sources:
            self.YEOHbase[key] = [0, 0]
            self.YEOHbaseR[key] = [0, 0]
            self.YEOHbaseT[key] = [0, 0]

    def district_grant_contribution(self, use=None):
        grant = 0
        if self.tech_tab is None:
            return grant
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
                print("KPIsCalculator.py, district_grant_contribution(): item_network_id, item_julia_category", network_id, item_julia_category)
            except:
                print("KPIsCalculator, district_pec. Network:", self.network.get_ID(), "Failed to retrieve item_network_id and/or "
                                                                   "item_julia_categoty from widget", self.tech_tab)
                continue
            if network_id == self.network.get_ID():
                if self.network.n_type == "DCN":
                    if self.network.optimized_buildings_layer is not None:
                        grant_temp = self.get_UED_cooling(self.network.optimized_buildings_layer, use)
                    else:
                        grant_temp = self.get_UED_cooling(self.network.network.buildings_layer, use)
                else:
                    if self.network.optimized_buildings_layer is not None:
                        grant_temp = self.get_UED_heating(self.network.optimized_buildings_layer, use)
                    else:
                        grant_temp = self.get_UED_heating(self.network.network.buildings_layer, use)

                item = self.tech_tab.topLevelItem(i)
                for j in item.childCount():
                    tech = item.child(j)
                    try:
                        julia_category = str(tech.data(1, Qt.UserRole))
                    except:
                        print("KpiCalculator, district_grant_contribution: failed to retrive julia_category")
                        continue
                    # TODO: correctly define column
                    if julia_category[0:2] == "CHP":
                        # electricity_sale_tariff, Power_To_Heat_ratio
                        try:
                            grant = grant + grant_temp * float(tech.text(8)) * float(tech.text(8))
                        except:
                            grant = 0
                            print("KpiCalculator, district_grant_contribution: to evaluate CHP grant")
                    else:
                        # thermal_feeding_tariff
                        try:
                            grant = grant + grant_temp * float(tech.text(8))
                        except:
                            grant = 0
                            print("KpiCalculator, district_grant_contribution: to evaluate grant")

                return grant

    def individual_grant_contribution(self):
        grant = 0
        if self.baseline_scenario is not None:
            layer = self.baseline_scenario
        else:
            layer = self.future_scenario
        for f in layer.getFeatures():
            if f.attribute("BuildingID") == self.building_id:
                feature = f
                break
        for i in range(self.tech_tab.childCount()):
            service = self.tech_tab.child(i)
            for j in range(service.childCount()):
                tech = service.child(j)
                julia_category = str(tech.data(1, Qt.UserRole))
                grant_contribution = float(feature.attribute("AHeatDem")) + float(feature.attribute("ACoolDem")) \
                                   + float(feature.attribute("ADHWDem"))

                # TODO: correctly define column
                if julia_category[0:2] == "CHP":
                    # electricity_sale_tariff, Power to Heat Ratio
                    try:
                        grant_contribution = grant_contribution * float(tech.text(8)) * float(tech.text(8))
                    except:
                        print("KPIscalcualtor, individual_grant_contribution: CHP grant_contribution fail")
                        grant_contribution = 0
                else:
                    # thermal_feeding_tariff
                    try:
                        grant_contribution = grant_contribution * float(tech.text(8))
                    except:
                        print("KPIscalcualtor, individual_grant_contribution: grant_contribution fail")
                        grant_contribution = 0
                grant = grant + grant_contribution
        return grant

    def district_FECfut_tech_per_energy_tariff(self, use=None):
        fec = 0
        if self.tech_tab is None:
            return fec
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                print("KPIsCalculator, district_FECfut_tech_per_energy_tariff. Network:", self.network.get_ID(), "Failed to retrieve item_network_id and/or "
                                                                   "item_julia_categoty from widget", self.tech_tab)
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    tech = self.tech_tab.topLevelItem(i).child(j)
                    julia_category = str(tech.data(1, Qt.UserRole))
                    file = os.path.join(self.work_folder, "Result_" + julia_category + "_" + self.network.get_ID() + ".csv")
                    # TODO: column of energy tariff per il fuel cost saving
                    try:
                        coeff = float(tech.text(8))
                    except:
                        coeff = 1
                    try:
                        fec = fec + (self.sum_file(file))*coeff
                    except:
                        print("KPIsCalculator, district_pec. Error summing file", file)
        if use is None:
            return fec
        elif use == "R":
            try:
                return fec*self.areaR/self.area
            except:
                return 0
        else:
            try:
                return fec * (1 - self.areaR / self.area)
            except:
                return 0

    def building_FECfut_tech_per_energy_tariff(self, use=None):
            fec = 0.0
            for i in range(self.tech_tab.childCount()):
                scope_item = self.tech_tab.child(i)
                for j in range(scope_item.childCount()):
                    technology = scope_item.child(j)
                    julia_category = str(technology.data(0, Qt.UserRole))
                    file = os.path.join(self.work_folder, "Result_" + julia_category + "_" + self.building_id + ".csv")
                    # TODO: column of energy tariff per il fuel cost saving
                    try:
                        coeff = float(technology.text(8))
                    except:
                        coeff = 1
                    try:
                        fec = fec + (self.sum_file(file))*coeff
                    except:
                        print("KPIsCalculator, district_pec. Error summing file", file)
            if use is None:
                return fec
            if self.building_tag == use:
                return fec
            else:
                return 0

    def district_UEDfut_tech_per_energy_tariff(self, use=None):
        fec = 0
        if self.tech_tab is None:
            return fec
        if self.network.optimized_buildings_layer is not None:
            layer = self.network.optimized_buildings_layer
        else:
            layer = self.network.buildings_layer
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                print("KPIsCalculator, district_UEDfut_tech_per_energy_tariff. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id")
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    tech = self.tech_tab.topLevelItem(i).child(j)
                    ued = self.get_UED(layer,use)

                    # TODO: column of energy tariff per il fuel cost saving
                    try:
                        coeff = float(tech.text(8))
                    except:
                        coeff = 1
                    fec = fec + ued * coeff
        if use is None:
            return fec
        elif use == "R":
            try:
                return fec * self.areaR / self.area
            except:
                return 0
        else:
            try:
                return fec * (1 - self.areaR / self.area)
            except:
                return 0

    def building_UEDfut_tech_per_energy_tariff(self, use=None):
        fec = 0.0
        if self.baseline_scenario is not None:
            layer = self.baseline_scenario
        else:
            layer = self.future_scenario
        for f in layer.getFeatures():
            if f.attribute("BuildingID") == self.building_id:
                feature = f
                break
        for i in range(self.tech_tab.childCount()):
            scope_item = self.tech_tab.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)

                # TODO: column of energy tariff per il O&M cost saving
                try:
                    coeff = float(technology.text(8))
                except:
                    coeff = 1
                try:
                    fec = fec + (float(feature.attribute("AHeatDem")) + float(feature.attribute("ACoolDem")) \
                                   + float(feature.attribute("ADHWDem"))) * coeff
                except:
                    print("KPIsCalculator, building_UEDfut_tech_per_energy_tariff. Error ")
        if use is None:
            return fec
        if self.building_tag == use:
            return fec
        else:
            return 0

    def eco_2_punto_2(self, use=None):
        try:
            revt = self.KPIs_input["fuel_cost_saving"] + self.KPIs_input["OeM_cost_saving"]
        except:
            revt = 0
        try:
            revtR = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtR = 0
        try:
            revtT = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtT = 0
        if use is None:
            return revt
        elif use == "R":
            return revtR
        else:
            return revtT

    def building_capex(self, use=None):
        capex = 0.0
        layer = self.future_scenario
        for f in layer.getFeatures():
            if f.attribute("BuildingID") == self.building_id:
                feature = f
                break
        for i in range(self.tech_tab.childCount()):
            scope_item = self.tech_tab.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)

                # TODO: column of energy tariff per il O&M cost saving
                # campo capacity x campo fixed_cost
                try:
                    capex = float(technology.text(8)) * float(technology.text(8))
                except:
                    print("KPIsCalculator, building_UEDfut_tech_per_energy_tariff. Error ")
        if use is None:
            return capex
        if feature.attribute("Use") == "Residential" and use == "R":
            return capex
        if not feature.attribute("Use") == "Residential" and not use == "R":
            return capex
        else:
            return 0

    def district_capex(self, use=None):
        capex = 0
        if self.tech_tab is None:
            return capex
        if self.network.optimized_buildings_layer is not None:
            layer = self.network.optimized_buildings_layer
        else:
            layer = self.network.buildings_layer
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                print("KPIsCalculator, district_capex. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id")
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    tech = self.tech_tab.topLevelItem(i).child(j)

                    # TODO: column of energy tariff per il fuel cost saving
                    # campo capacity x campo fixed_cost
                    try:
                        capex = float(tech.text(8)) * float(tech.text(8))
                    except:
                        capex = 1
        if use is None:
            return capex
        elif use == "R":
            try:
                return capex * self.areaR / self.area
            except:
                return 0
        else:
            try:
                return capex * (1 - self.areaR / self.area)
            except:
                return 0



    def eco_1_punto_1(self, use=None):
        try:
            revt = self.KPIs_input["fuel_cost_saving"] + self.KPIs_input["OeM_cost_saving"]
        except:
            revt = 0
        try:
            revtR = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtR = 0
        try:
            revtT = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtT = 0

        caft = revt + self.grant - self.opex
        caftR = revtR + self.grantR - self.opexR
        caftT = revtT + self.grantT - self.opexT

        caft0 = -1*self.capext
        caft0R = -1*self.capextR
        caft0T = -1*self.capextT

        try:
            years = int(self.eco_param["years"])
        except:
            years = 5
        try:
            years = self.eco_param["r"]
        except:
            r = 0.1

        dcaft = []
        cdcaft = []
        years_nr = int(years)
        for i in range(years_nr):
            if i == 0:
                dcaft.append(caft0/(1/r**i))
                cdcaft.append(dcaft[i])
            else:
                dcaft.append(caft / (1 / r ** i))
                cdcaft.append(cdcaft[i-1] + dcaft[i])

        for i in range(years_nr-1, -1, -1):
            if cdcaft[i] < 0:
                A = i + 1
                B = abs(cdcaft[i])
                try:
                    C = sum(dcaft[i+1:-1])
                except:
                    C = 1
                break
        if use is None:
            try:
                return round(A + B / C, 2)
            except:
                return "Nan"

        dcaftR = []
        cdcaftR = []
        for i in range(years_nr):
            if i == 0:
                dcaftR.append(caft0R / (1 / r ** i))
                cdcaftR.append(dcaftR[i])
            else:
                dcaftR.append(caftR / (1 / r ** i))
                cdcaftR.append(cdcaftR[i - 1] + dcaft[i])

        for i in range(years_nr - 1, -1, -1):
            if cdcaftR[i] < 0:
                A = i + 1
                B = abs(cdcaftR[i])
                try:
                    C = sum(dcaftR[i + 1:-1])
                except:
                    C = 1
                break
        if use == "R":
            try:
                return round(A + B / C, 2)
            except:
                return "Nan"

        dcaftT = []
        cdcaftT = []
        for i in range(years_nr):
            if i == 0:
                dcaftT.append(caft0T / (1 / r ** i))
                cdcaftT.append(dcaftT[i])
            else:
                dcaftT.append(caftT / (1 / r ** i))
                cdcaftT.append(cdcaftT[i - 1] + dcaft[i])

        for i in range(years_nr - 1, -1, -1):
            if cdcaftT[i] < 0:
                A = i + 1
                B = abs(cdcaftT[i])
                try:
                    C = sum(dcaftT[i + 1:-1])
                except:
                    C = 1
                break
        if use == "T":
            try:
                return round(A + B / C, 2)
            except:
                return "Nan"

    def eco_uno_punto_due(self, use=None):
        try:
            revt = self.KPIs_input["fuel_cost_saving"] + self.KPIs_input["OeM_cost_saving"]
        except:
            revt = 0
        try:
            revtR = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtR = 0
        try:
            revtT = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtT = 0

        try:
            years = self.eco_param["years"]
        except:
            years = 5
        try:
            r = self.eco_param["r"]
        except:
            r = 0.1


        caft = revt + self.grant - self.opex
        caftR = revtR + self.grantR - self.opexR
        caftT = revtT + self.grantT - self.opexT

        years_nr = int(years)
        if use is None:
            npv = self.capext

            for i in range(years_nr):
                npv = npv + caft/(1+r)**i
            return round(npv, 2)

        if use == "R":
            npv = self.capextR
            for i in range(years_nr):
                npv = npv + caftR/(1+r)**i
            return round(npv, 2)

        if use == "T":
            npv = self.capextT
            for i in range(years_nr):
                npv = npv + caftT/(1+r)**i
            return round(npv, 2)

        return "Nan"

    def eco_uno_punto_tre(self, use=None):
        try:
            revt = self.KPIs_input["fuel_cost_saving"] + self.KPIs_input["OeM_cost_saving"]
        except:
            revt = 0
        try:
            revtR = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtR = 0
        try:
            revtT = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtT = 0

        try:
            years = self.eco_param["years"]
        except:
            years = 5

            years_nr = int(years)
        caft = revt + self.grant - self.opex
        caftR = revtR + self.grantR - self.opexR
        caftT = revtT + self.grantT - self.opexT

        if use is None:
            try:
                a = -self.capext/caft
            except (ZeroDivisionError, TypeError) as e:
                return "Nan"
            return self.bisezione(a, years_nr)
        if use == "R":
            try:
                a = -self.capextR/caftR
            except (ZeroDivisionError, TypeError) as e:
                return "Nan"
            return self.bisezione(a, years_nr)
        if use == "T":
            try:
                a = -self.capextT/caftT
            except (ZeroDivisionError, TypeError) as e:
                return "Nan"
            return self.bisezione(a, years_nr)


    def bisezione(self, val, years_nr):
        if val == "Nan":
            return "Nan"
        if val < 0:

            return "Nan"
        else:
            # la funzione sum(1/(1+r)^i) è compresa tra 0 e 1
            a = 0
            b = 1
            half = 0.5
            flag = True
            i = 0
            while flag:
                i = i +1
                tot_a = 0
                tot_b = 0
                tot_half = 0

                for i in range(years_nr):
                    tot_a = tot_a + 1/((1 + a)**i)
                    tot_b = tot_b + 1 / ((1 + b) ** i)
                    tot_half = tot_half + 1 / ((1 + half) ** i)
                if abs(tot_half-val)<0.01:
                    return round(half, 2)
                else:
                    if tot_half>val:
                        a = half
                    else:
                        b = half
                    half = (a + b) / 2
                if i > 1000:
                    flag = False
            else:

                return "Nan"

    def eco_3_punto_1(self, use=None):
        total = 0
        try:
            years = self.eco_param["years"]
        except:
            years = 5
        try:
            r = self.eco_param["r"]
        except:
            r = 0.1
        years_nr=int(years)

        for i in range(years_nr):
            total = total + 1/((1+r)**i)
        if use is None:
            try:
                return round(total*(self.capext+self.opex), 2)
            except:
                return "Nan"
        if use == "R":
            try:
                return round(total*(self.capextR+self.opexR), 2)
            except:
                return "Nan"
        if use == "T":
            try:
                return round(total*(self.capextT+self.opexT), 2)
            except:
                return "Nan"

    def eco_3_punto_2(self, val, use=None):
        try:
            val = float(val)
        except:
            val = 0
        try:
            years = int(self.eco_param["years"])
        except:
            years = 5
        if use is None:
            try:
                return round((self.capext/years+self.opex)/val, 2)
            except:
                return "Nan"
        if use == "R":
            try:
                return round((self.capextR/years+self.opexR)/val, 2)
            except:
                return "Nan"
        if use == "T":
            try:
                return round((self.capextT/years+self.opexT)/val, 2)
            except:
                return "Nan"

















