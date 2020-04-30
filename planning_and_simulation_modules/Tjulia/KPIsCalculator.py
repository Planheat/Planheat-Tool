import os
import numpy as np

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
import time
from PyQt5.QtWidgets import QTreeWidget, QTableWidgetItem, QTreeWidgetItem

import os.path
import copy
import traceback
import logging

from .test.MyLog import MyLog
from .services.NetworkTechCapex import NetworkTechCapex
from .services.BuildingTechCapex import BuildingTechCapex

# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import pandas
# Import the custom tree widget items
from .. import Network


class KPIsCalculator:
    h8760 = 8760

    sourceName = ["Heating Oil", "Natural gas", "Electricity", "Deep geothermal",
                  "Geothermal - Shallow - Ground heat extraction",
                  "Geothermal - Shallow - Ground cold extraction", "Solar thermal", "Excess heat Industry",
                  "Excess heat - Data centers",
                  "Excess heat - Supermarkets", "Excess heat - Refrigerated storage facilities",
                  "Excess heat - Indoor carparkings",
                  "Excess heat - Subway networks", "Urban waste water treatment plant",
                  "Water - Waste water - Sewer system",
                  "Water - Surface water - Rivers cold extraction heat pump",
                  "Water - Surface water - Rivers cold extraction from free cooling", "Water - Surface water - Lakes heat extraction with heat pump",
                  "Water - Surface water - Lakes cold extraction with heat pump", "Water - Surface water - Rivers heat extraction heat pump",
                  "Excess cooling - LNG terminals", "Biomass Forestry",
                  "Generic heating/cooling source"]  # insert all the 23 sources

    opex_conventional_fuels = [sourceName[0], # Heating Oil
                               sourceName[1], # Natural gas
                               sourceName[2], # Electricity
                               sourceName[21]  # Biomass Forestry
                               ]

    const_eff = ["Gas Boiler", "Biomass Boiler", "Oil Boiler", "Electrical Heater", "Gas CHP", "Oil CHP",
                 "Biomass CHP",
                 "Industrial waste heat ORC", "Deep geothermal ORC", "Gas ORC", "Biomass ORC", "Deep geothermal HEX",
                 "Industrial waste heat HEX",
                 "Evacuated tube solar collectors", "Flat plate solar collectors",
                 "Waste heat absorption heat pump",
                 "Air source gas absorption heat pump", "Shallow geothermal gas absorption heat pump",
                 "Air source gas absorption chiller", "Shallow geothermal Gas absorption chiller"]

    variable_eff_ng = ["Waste heat absorption heat pump"]

    variable_eff_el = ["Air Source Compression Heat Pump", "Shallow geothermal compression heat pump",
                       "Air source compression chiller", "Shallow geothermal compression chiller",
                       "Waste Heat Compression Heat Pump Medium T", "Seasonal waste heat heat pumps",
                       "Cooling heat pump",
                       "Waste Heat Compression Heat Pump Low T", "Waste Heat Compression Heat Pump High T"]
    solar_technologies = ["Evacuated tube solar collectors", "Flat plate solar collectors", "Seasonal Solar Thermal"]

    pollutant_colum_index = {"CO2": 1, "NOx": 2, "SOx": 3, "PM10": 4}


    def __init__(self, pef_sources_tab=None, ef_sources_tab=None, tech_tab=None, work_folder=None, network=None,
                 building_id=None):
        self.pef_sources_tab = pef_sources_tab
        self.ef_sources_tab = ef_sources_tab
        self.tech_tab = tech_tab
        self.work_folder = work_folder
        self.network = network
        self.building_id = building_id
        self.logger = logging.getLogger(__name__)
        self.my_log = MyLog(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         "test", "log", "log_KPIs_calculator.txt"))

        self.baseline_tech_tab = None  # only used in future (??? really not true ???)
        self.baseline_tech_tab2 = None
        self.baseline_network_tech_tab = None  # only used in future
        self.future_tech_tab = None  # only used in future
        self.future_network_tech_tab = None  # only used in future

        self.building_tag = None
        self.step0_district_sources_tab = None
        self.future_scenario = None
        self.baseline_scenario = None
        self.sources = None
        self.individual_tech_power_column = None
        self.district_tech_power_column = None
        self.eco_param = None
        self.KPIs_input = None
        self.dcaft = []
        self.dcaftR = []
        self.dcaftT = []

        self.building_connection_map = None

        self.KPIs_additional_data = None

    def initialize(self):
        self.eco_param = {}
        try:
            self.eco_param["r_factor"] = self.KPIs_additional_data["r_factor"]
        except:
            self.eco_param["r_factor"] = 0.11
        try:
            self.eco_param["years"] = self.KPIs_additional_data["years"]
        except:
            self.eco_param["years"] = 5
        try:
            self.eco_param["demo_factor"] = self.KPIs_additional_data["demo_factor"]
        except:
            self.eco_param["demo_factor"] = 0.0
        self.my_log.log("parametri aggiuntivi (eco_params):", self.eco_param)
        self.my_log.log("KPIs_additional_data", self.KPIs_additional_data)
        self.eco_param["eta_DHN"] = []
        self.eco_param["eta_DCN"] = []
        try:
            self.eco_param["FEavailability"] = self.KPIs_additional_data["FEavailability"]
        except:
            self.eco_param["FEavailability"] = 1.0
        self.eco_param["residential_factors"] = []

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
        self.el_sale = 0
        self.el_saleR = 0
        self.el_saleT = 0

        self.fec_s0 = 0
        self.fec_s1 = 0
        self.fec_s2 = 0
        self.fec_s3 = 0
        self.fec_s4 = 0
        self.fec_s5 = 0
        self.fec_s6 = 0
        self.fec_s7 = 0
        self.fec_s8 = 0
        self.fec_s9 = 0
        self.fec_s10 = 0
        self.fec_s11 = 0
        self.fec_s12 = 0
        self.fec_s13 = 0
        self.fec_s14 = 0
        self.fec_s15 = 0
        self.fec_s16 = 0
        self.fec_s17 = 0
        self.fec_s18 = 0
        self.fec_s19 = 0
        self.fec_s20 = 0
        self.fec_s21 = 0
        self.fec_s22 = 0

        self.fecR_s0 = 0
        self.fecR_s1 = 0
        self.fecR_s2 = 0
        self.fecR_s3 = 0
        self.fecR_s4 = 0
        self.fecR_s5 = 0
        self.fecR_s6 = 0
        self.fecR_s7 = 0
        self.fecR_s8 = 0
        self.fecR_s9 = 0
        self.fecR_s10 = 0
        self.fecR_s11 = 0
        self.fecR_s12 = 0
        self.fecR_s13 = 0
        self.fecR_s14 = 0
        self.fecR_s15 = 0
        self.fecR_s16 = 0
        self.fecR_s17 = 0
        self.fecR_s18 = 0
        self.fecR_s19 = 0
        self.fecR_s20 = 0
        self.fecR_s21 = 0
        self.fecR_s22 = 0

        self.fecT_s0 = 0
        self.fecT_s1 = 0
        self.fecT_s2 = 0
        self.fecT_s3 = 0
        self.fecT_s4 = 0
        self.fecT_s5 = 0
        self.fecT_s6 = 0
        self.fecT_s7 = 0
        self.fecT_s8 = 0
        self.fecT_s9 = 0
        self.fecT_s10 = 0
        self.fecT_s11 = 0
        self.fecT_s12 = 0
        self.fecT_s13 = 0
        self.fecT_s14 = 0
        self.fecT_s15 = 0
        self.fecT_s16 = 0
        self.fecT_s17 = 0
        self.fecT_s18 = 0
        self.fecT_s19 = 0
        self.fecT_s20 = 0
        self.fecT_s21 = 0
        self.fecT_s22 = 0

        self.fecDistrict_DHN = 0
        self.fecDistrictR_DHN = 0
        self.fecDistrictT_DHN = 0
        self.fecDistrict_DCN = 0
        self.fecDistrictR_DCN = 0
        self.fecDistrictT_DCN = 0

        self.FEavailability = 0  # output del MM


        self.my_log.log("!!!---   KPIsCalculator INITIALIZED   ---!!!")
        if self.future_scenario is None:
            self.my_log.log("Scenario Type: BASELINE")
            status = "2"
        else:
            self.my_log.log("Scenario Type: FUTURE")
            status = "1"

    def district_KPIs_update(self):
        if self.network.n_type == "DHN":
            self.eco_param["eta_DHN"].append(self.network.get_efficiency())
        if self.network.n_type == "DCN":
            self.eco_param["eta_DCN"].append(self.network.get_efficiency())
        self.eco_param["residential_factors"].append(self.network.get_residential_factor())
        if not self.district_var_check():
            return
        try:
            self.network.optimized_buildings_layer = self.network.search_and_fix_layers()
            self.network.buildings_layer = self.network.optimized_buildings_layer
            if self.network.buildings_layer is None:
                print("KPiCalculator.district_KPIs_update() Cannot find the building layer for network", str(self.network.name))
        except:
                print("KPiCalculator.district_KPIs_update() Error finding the building layer for the current network.")
                traceback.print_exc()

        residential_factor = self.network.get_residential_factor()
        self.residential_factor = residential_factor
        self.my_log.log("residential_factor for network " + str(self.network.name) + " : " + str(residential_factor))
        self.temp_pec = self.district_pec()
        self.pec = self.pec + self.temp_pec
        self.pecR = self.pecR + self.temp_pec * residential_factor
        self.pecT = self.pecT + self.temp_pec * (1 - residential_factor)
        tmp_fec = self.district_fec(self.work_folder, self.network.get_ID(), self.tech_tab)
        self.my_log.log("fec contribution tmp for network:", self.network.name, tmp_fec)

        self.fec_s0 = self.fec_s0 + tmp_fec[0]
        self.fec_s1 = self.fec_s1 + tmp_fec[1]
        self.fec_s2 = self.fec_s2 + tmp_fec[2]
        self.fec_s3 = self.fec_s3 + tmp_fec[3]
        self.fec_s4 = self.fec_s4 + tmp_fec[4]
        self.fec_s5 = self.fec_s5 + tmp_fec[5]
        self.fec_s6 = self.fec_s6 + tmp_fec[6]
        self.fec_s7 = self.fec_s7 + tmp_fec[7]
        self.fec_s8 = self.fec_s8 + tmp_fec[8]
        self.fec_s9 = self.fec_s9 + tmp_fec[9]
        self.fec_s10 = self.fec_s10 + tmp_fec[10]
        self.fec_s11 = self.fec_s11 + tmp_fec[11]
        self.fec_s12 = self.fec_s12 + tmp_fec[12]
        self.fec_s13 = self.fec_s13 + tmp_fec[13]
        self.fec_s14 = self.fec_s14 + tmp_fec[14]
        self.fec_s15 = self.fec_s15 + tmp_fec[15]
        self.fec_s16 = self.fec_s16 + tmp_fec[16]
        self.fec_s17 = self.fec_s17 + tmp_fec[17]
        self.fec_s18 = self.fec_s18 + tmp_fec[18]
        self.fec_s19 = self.fec_s19 + tmp_fec[19]
        self.fec_s20 = self.fec_s20 + tmp_fec[20]
        self.fec_s21 = self.fec_s21 + tmp_fec[21]
        self.fec_s22 = self.fec_s22 + tmp_fec[22]

        if self.network.n_type == "DHN":
            self.fecDistrict_DHN = self.fecDistrict_DHN + np.sum(tmp_fec)
            self.fecDistrictR_DHN = self.fecDistrictR_DHN + np.sum(tmp_fec) * residential_factor
            self.fecDistrictT_DHN = self.fecDistrictT_DHN + np.sum(tmp_fec) * (1 - residential_factor)
        if self.network.n_type == "DCN":
            self.fecDistrict_DCN = self.fecDistrict_DCN + np.sum(tmp_fec)
            self.fecDistrictR_DCN = self.fecDistrictR_DCN + np.sum(tmp_fec) * residential_factor
            self.fecDistrictT_DCN = self.fecDistrictT_DCN + np.sum(tmp_fec) * (1 - residential_factor)

        #self.fecR = self.fecR + tmp * residential_factor
        self.fecR_s0 += tmp_fec[0] * residential_factor
        self.fecR_s1 += tmp_fec[1] * residential_factor
        self.fecR_s2 += tmp_fec[2] * residential_factor
        self.fecR_s3 += tmp_fec[3] * residential_factor
        self.fecR_s4 += tmp_fec[4] * residential_factor
        self.fecR_s5 += tmp_fec[5] * residential_factor
        self.fecR_s6 += tmp_fec[6] * residential_factor
        self.fecR_s7 += tmp_fec[7] * residential_factor
        self.fecR_s8 += tmp_fec[8] * residential_factor
        self.fecR_s9 += tmp_fec[9] * residential_factor
        self.fecR_s10 += tmp_fec[10] * residential_factor
        self.fecR_s11 += tmp_fec[11] * residential_factor
        self.fecR_s12 += tmp_fec[12] * residential_factor
        self.fecR_s13 += tmp_fec[13] * residential_factor
        self.fecR_s14 += tmp_fec[14] * residential_factor
        self.fecR_s15 += tmp_fec[15] * residential_factor
        self.fecR_s16 += tmp_fec[16] * residential_factor
        self.fecR_s17 += tmp_fec[17] * residential_factor
        self.fecR_s18 += tmp_fec[18] * residential_factor
        self.fecR_s19 += tmp_fec[19] * residential_factor
        self.fecR_s20 += tmp_fec[20] * residential_factor
        self.fecR_s21 += tmp_fec[21] * residential_factor
        self.fecR_s22 += tmp_fec[22] * residential_factor

        self.fecT_s0 += tmp_fec[0] * (1 - residential_factor)
        self.fecT_s1 += tmp_fec[1] * (1 - residential_factor)
        self.fecT_s2 += tmp_fec[2] * (1 - residential_factor)
        self.fecT_s3 += tmp_fec[3] * (1 - residential_factor)
        self.fecT_s4 += tmp_fec[4] * (1 - residential_factor)
        self.fecT_s5 += tmp_fec[5] * (1 - residential_factor)
        self.fecT_s6 += tmp_fec[6] * (1 - residential_factor)
        self.fecT_s7 += tmp_fec[7] * (1 - residential_factor)
        self.fecT_s8 += tmp_fec[8] * (1 - residential_factor)
        self.fecT_s9 += tmp_fec[9] * (1 - residential_factor)
        self.fecT_s10 += tmp_fec[10] * (1 - residential_factor)
        self.fecT_s11 += tmp_fec[11] * (1 - residential_factor)
        self.fecT_s12 += tmp_fec[12] * (1 - residential_factor)
        self.fecT_s13 += tmp_fec[13] * (1 - residential_factor)
        self.fecT_s14 += tmp_fec[14] * (1 - residential_factor)
        self.fecT_s15 += tmp_fec[15] * (1 - residential_factor)
        self.fecT_s16 += tmp_fec[16] * (1 - residential_factor)
        self.fecT_s17 += tmp_fec[17] * (1 - residential_factor)
        self.fecT_s18 += tmp_fec[18] * (1 - residential_factor)
        self.fecT_s19 += tmp_fec[19] * (1 - residential_factor)
        self.fecT_s20 += tmp_fec[20] * (1 - residential_factor)
        self.fecT_s21 += tmp_fec[21] * (1 - residential_factor)
        self.fecT_s22 += tmp_fec[22] * (1 - residential_factor)

        tmp = self.district_pecRENs(self.work_folder, self.network.get_ID(),
                                    self.tech_tab, self.pef_sources_tab)
        self.pecRENs = self.pecRENs + tmp
        self.pecRENsR = self.pecRENsR + tmp * residential_factor
        self.pecRENsT = self.pecRENsT + tmp * (1 - residential_factor)
        temp = self.district_fecWH(self.work_folder, self.network.get_ID(), self.tech_tab)
        self.fecWH = self.fecWH + temp
        self.fecWHR = self.fecWHR + tmp * residential_factor
        self.fecWHT = self.fecWHT + tmp * (1 - residential_factor)
        tmp = self.district_pecCF(self.work_folder, self.network.get_ID(), self.tech_tab, self.pef_sources_tab)
        self.pecCF = self.pecCF + tmp
        self.pecCFR = self.pecCFR + tmp * residential_factor
        self.pecCFT = self.pecCFT + tmp * (1 - residential_factor)
        tmp = self.district_pecIS(self.work_folder, self.network.get_ID(), self.tech_tab, self.pef_sources_tab)
        self.pecIS = self.pecIS + tmp
        self.pecISR = self.pecISR + tmp * residential_factor
        self.pecIST = self.pecIST + tmp * (1 - residential_factor)
        self.district_YEOHbase_calculation(self.work_folder, self.network.get_ID(), self.YEOHbase,
                                           self.tech_tab, self.pef_sources_tab)
        self.district_YEOHbase_calculation(self.work_folder, self.network.get_ID(), self.YEOHbaseR,
                                           self.tech_tab, self.pef_sources_tab)
        self.district_YEOHbase_calculation(self.work_folder, self.network.get_ID(), self.YEOHbaseT,
                                           self.tech_tab, self.pef_sources_tab)
        if self.network.optimized_buildings_layer is not None:
            layer = self.network.optimized_buildings_layer
        else:
            layer = self.network.search_and_fix_layers()
        try:
            self.my_log.log("district_KPIs_update: layer: " + str(layer.name()))
        except:
            self.my_log.log("district_KPIs_update: calling function str(layer.name()) caused an unexpected error")

        if not self.ENV_KPIs_check():
            return
        tmp = self.district_emission(1)
        self.CO2 = self.CO2 + tmp
        self.CO2R = self.CO2R + tmp * residential_factor
        self.CO2T = self.CO2T + tmp * (1 - residential_factor)
        tmp = self.district_emission(2)
        self.NOx = self.NOx + tmp
        self.NOxR = self.NOxR + tmp * residential_factor
        self.NOxT = self.NOxT + tmp * (1 - residential_factor)
        tmp = self.district_emission(3)
        self.SOx = self.SOx + tmp
        self.SOxR = self.SOxT + tmp * residential_factor
        self.SOxR = self.SOxT + tmp * (1 - residential_factor)
        tmp = self.district_emission(4)
        self.PM10 = self.PM10 + tmp
        self.PM10R = self.PM10R + tmp * residential_factor
        self.PM10T = self.PM10T + tmp * (1 - residential_factor)
        tmp = self.district_solar_penetration()
        self.stp = self.stp + tmp
        self.stpR = self.stpR + tmp * residential_factor
        self.stpT = self.stpT + tmp * (1 - residential_factor)
        status = 2
        if self.network.n_type == "DCN":
            self.c_ued = self.c_ued + self.get_UED_network("Cooling", status)
            self.c_uedR = self.c_uedR + self.get_UED_network("Cooling", status) * residential_factor
            self.c_uedT = self.c_uedT + self.get_UED_network("Cooling", status) * (1 - residential_factor)
            self.c_fec_eta = self.c_fec_eta + self.fec * self.network.efficiency
            self.c_fec_etaR = self.c_fec_etaR + self.fec * self.network.efficiency * residential_factor
            self.c_fec_etaT = self.c_fec_etaT + self.fec * self.network.efficiency * (1 - residential_factor)
            self.c_length = self.c_length + self.network.pipes_length()
        if self.network.n_type == "DHN":
            self.h_ued = self.h_ued + self.get_UED_network("Heating", status)
            self.h_uedR = self.h_uedR + self.get_UED_network("Heating", status) * residential_factor
            self.h_uedT = self.h_uedT + self.get_UED_network("Heating", status) * (1 - residential_factor)
            self.h_length = self.h_length + self.network.pipes_length(log=self.my_log)
            self.h_fec_eta = self.h_fec_eta + self.fec * self.network.efficiency
            self.h_fec_etaR = self.h_fec_etaR + self.fec * self.network.efficiency * residential_factor
            self.h_fec_etaT = self.h_fec_etaT + self.fec * self.network.efficiency * (1 - residential_factor)
        self.grant = self.grant + self.district_grant_contribution()
        self.grantR = self.grant + self.district_grant_contribution(use="R")
        self.grantT = self.grant + self.district_grant_contribution(use="T")

        self.opex = self.opex + self.district_UEDfut_tech_per_energy_tariff()  # + fec contribution in fec_district()
        self.opexR = self.opexR + self.district_UEDfut_tech_per_energy_tariff() * residential_factor
        self.opexT = self.opexT + self.district_UEDfut_tech_per_energy_tariff() * (1 - residential_factor)

        if self.future_scenario is not None:
            self.KPIs_input["fuel_cost_saving"] = self.KPIs_input[
                                                      "fuel_cost_saving"] - self.district_FECfut_tech_per_energy_tariff()
            self.KPIs_input["fuel_cost_savingR"] = self.KPIs_input[
                                                       "fuel_cost_savingR"] - self.district_FECfut_tech_per_energy_tariff(
                use="R")
            self.KPIs_input["fuel_cost_savingT"] = self.KPIs_input[
                                                       "fuel_cost_savingT"] - self.district_FECfut_tech_per_energy_tariff(
                use="T")
        else:
            self.fuel_cost_saving = self.fuel_cost_saving + self.district_FECfut_tech_per_energy_tariff() * (1 + self.eco_param["demo_factor"])
            self.fuel_cost_savingR = self.fuel_cost_savingR + self.district_FECfut_tech_per_energy_tariff(use="R") * (1 + self.eco_param["demo_factor"])
            self.fuel_cost_savingT = self.fuel_cost_savingT + self.district_FECfut_tech_per_energy_tariff(use="T") * (1 + self.eco_param["demo_factor"])
        if self.future_scenario is not None:
            # self.capext = self.capext + self.district_capex()
            # self.capextR = self.capextR + self.district_capex(use="R")
            # self.capextT = self.capextT + self.district_capex(use="T")
            self.KPIs_input["OeM_cost_saving"] = self.KPIs_input[
                                                     "OeM_cost_saving"] - self.district_UEDfut_tech_per_energy_tariff()
            self.KPIs_input["OeM_cost_savingR"] = self.KPIs_input[
                                                      "OeM_cost_savingR"] - self.district_UEDfut_tech_per_energy_tariff(use="R")
            self.KPIs_input["OeM_cost_savingT"] = self.KPIs_input[
                                                      "OeM_cost_savingT"] - self.district_UEDfut_tech_per_energy_tariff(use="T")
        else:
            self.OeM_cost_saving = self.OeM_cost_saving + self.district_UEDfut_tech_per_energy_tariff()
            self.OeM_cost_savingR = self.OeM_cost_savingR + self.district_UEDfut_tech_per_energy_tariff(use="R")
            self.OeM_cost_savingT = self.OeM_cost_savingT + self.district_UEDfut_tech_per_energy_tariff(use="T")

        incr_el_sale = self.get_el_sale_increment_district()
        self.el_sale += incr_el_sale
        self.el_saleR += incr_el_sale * residential_factor
        self.el_saleT += incr_el_sale * (1 - residential_factor)


    def individual_KPIs_update(self):
        if not self.individual_var_check():
            return
        self.my_log.log("---   individual_KPIs_update   ---")
        self.my_log.log("self.building_tag")
        self.my_log.log("eco params:", self.eco_param)
        self.my_log.log(self.building_tag)

        self.temp_pec = self.building_PEC_calculation()
        self.pec = self.pec + self.temp_pec
        if self.building_tag == "Residential":
            self.pecR = self.pecR + self.temp_pec
        else:
            self.pecT = self.pecT + self.temp_pec

        tmp = self.building_FEC_calculation(self.work_folder, self.tech_tab, self.building_id)

        self.my_log.log("tmp")
        self.my_log.log(tmp)

        self.fec_s0 += tmp[0]
        self.fec_s1 += tmp[1]
        self.fec_s2 += tmp[2]
        self.fec_s3 += tmp[3]
        self.fec_s4 += tmp[4]
        self.fec_s5 += tmp[5]
        self.fec_s6 += tmp[6]
        self.fec_s7 += tmp[7]
        self.fec_s8 += tmp[8]
        self.fec_s9 += tmp[9]
        self.fec_s10 += tmp[10]
        self.fec_s11 += tmp[11]
        self.fec_s12 += tmp[12]
        self.fec_s13 += tmp[13]
        self.fec_s14 += tmp[14]
        self.fec_s15 += tmp[15]
        self.fec_s16 += tmp[16]
        self.fec_s17 += tmp[17]
        self.fec_s18 += tmp[18]
        self.fec_s19 += tmp[19]
        self.fec_s20 += tmp[20]
        self.fec_s21 += tmp[21]
        self.fec_s22 += tmp[22]


        if self.building_tag == "Residential":
            self.fecR_s0 += tmp[0]
            self.fecR_s1 += tmp[1]
            self.fecR_s2 += tmp[2]
            self.fecR_s3 += tmp[3]
            self.fecR_s4 += tmp[4]
            self.fecR_s5 += tmp[5]
            self.fecR_s6 += tmp[6]
            self.fecR_s7 += tmp[7]
            self.fecR_s8 += tmp[8]
            self.fecR_s9 += tmp[9]
            self.fecR_s10 += tmp[10]
            self.fecR_s11 += tmp[11]
            self.fecR_s12 += tmp[12]
            self.fecR_s13 += tmp[13]
            self.fecR_s14 += tmp[14]
            self.fecR_s15 += tmp[15]
            self.fecR_s16 += tmp[16]
            self.fecR_s17 += tmp[17]
            self.fecR_s18 += tmp[18]
            self.fecR_s19 += tmp[19]
            self.fecR_s20 += tmp[20]
            self.fecR_s21 += tmp[21]
            self.fecR_s22 += tmp[22]
        else:
            self.fecT_s0 += tmp[0]
            self.fecT_s1 += tmp[1]
            self.fecT_s2 += tmp[2]
            self.fecT_s3 += tmp[3]
            self.fecT_s4 += tmp[4]
            self.fecT_s5 += tmp[5]
            self.fecT_s6 += tmp[6]
            self.fecT_s7 += tmp[7]
            self.fecT_s8 += tmp[8]
            self.fecT_s9 += tmp[9]
            self.fecT_s10 += tmp[10]
            self.fecT_s11 += tmp[11]
            self.fecT_s12 += tmp[12]
            self.fecT_s13 += tmp[13]
            self.fecT_s14 += tmp[14]
            self.fecT_s15 += tmp[15]
            self.fecT_s16 += tmp[16]
            self.fecT_s17 += tmp[17]
            self.fecT_s18 += tmp[18]
            self.fecT_s19 += tmp[19]
            self.fecT_s20 += tmp[20]
            self.fecT_s21 += tmp[21]
            self.fecT_s22 += tmp[22]



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
            self.KPIs_input["fuel_cost_saving"] = self.KPIs_input[
                                                      "fuel_cost_saving"] - self.building_FECfut_tech_per_energy_tariff()
        else:
            self.fuel_cost_saving = self.fuel_cost_saving + self.building_FECfut_tech_per_energy_tariff() * (1 + self.eco_param["demo_factor"])
        if self.building_tag == "Residential":
            if self.future_scenario is not None:
                self.KPIs_input["fuel_cost_savingR"] = self.KPIs_input[
                                                           "fuel_cost_savingR"] - self.building_FECfut_tech_per_energy_tariff(
                    use="R")
            else:
                self.fuel_cost_savingR = self.fuel_cost_savingR + self.building_FECfut_tech_per_energy_tariff(use="R") * (1 + self.eco_param["demo_factor"])
        else:
            if self.future_scenario is not None:
                self.KPIs_input["fuel_cost_savingT"] = self.KPIs_input[
                                                           "fuel_cost_savingT"] - self.building_FECfut_tech_per_energy_tariff(use="T")
            else:
                self.fuel_cost_savingT = self.fuel_cost_savingT + self.building_FECfut_tech_per_energy_tariff(use="T") * (1 + self.eco_param["demo_factor"])

        if self.future_scenario is not None:
            self.KPIs_input["OeM_cost_saving"] = self.KPIs_input[
                                                     "OeM_cost_saving"] - self.building_UEDfut_tech_per_energy_tariff()
        else:
            self.OeM_cost_saving = self.OeM_cost_saving + self.building_UEDfut_tech_per_energy_tariff()

        if self.building_tag == "Residential":
            if self.future_scenario is not None:
                self.KPIs_input["OeM_cost_savingR"] = self.KPIs_input[
                                                          "OeM_cost_savingR"] - self.building_UEDfut_tech_per_energy_tariff(
                    use="R")
            else:
                self.OeM_cost_savingR = self.OeM_cost_savingR + self.building_UEDfut_tech_per_energy_tariff(use="R")
        else:
            if self.future_scenario is not None:
                self.KPIs_input["OeM_cost_savingT"] = self.KPIs_input[
                                                          "OeM_cost_savingT"] - self.building_UEDfut_tech_per_energy_tariff(
                    use="T")
            else:
                self.OeM_cost_savingT = self.OeM_cost_savingT + self.building_UEDfut_tech_per_energy_tariff(use="T")

        self.opex = self.opex + self.building_UEDfut_tech_per_energy_tariff() + self.building_FECfut_tech_per_energy_tariff()
        self.opexR = self.opexR + self.building_UEDfut_tech_per_energy_tariff(
            use="R") + self.building_FECfut_tech_per_energy_tariff(use="R")
        self.opexT = self.opexT + self.building_UEDfut_tech_per_energy_tariff(
            use="T") + self.building_FECfut_tech_per_energy_tariff(use="T")

        # if self.future_scenario is not None:
            # self.capext = self.capext + self.building_capex()
            # if self.building_tag == "Residential":
            #    self.capextR = self.capextR + self.building_capex()
            # else:
            #    self.capextT = self.capextT + self.building_capex()

        incr_el_sale = self.get_el_sale_increment_building()
        self.el_sale += incr_el_sale
        self.el_saleR += incr_el_sale if self.building_tag == "Residential" else 0
        self.el_saleT += incr_el_sale if not self.building_tag == "Residential" else 0


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
                KPIs[key] = copy.deepcopy(KPIs_baseline[key])

            self.add_networks_area_contribution(self.future_scenario)

            self.my_log.log("area: " + str(self.area))
            self.my_log.log("areaR: " + str(self.areaR))

            self.PEC_base = self.PECbaseSource(self.getPEF_source(), [self.fec_s0, self.fec_s1, self.fec_s2,
                                               self.fec_s3, self.fec_s4, self.fec_s5, self.fec_s6, self.fec_s7,
                                               self.fec_s8, self.fec_s9, self.fec_s10, self.fec_s11, self.fec_s12,
                                               self.fec_s13, self.fec_s14, self.fec_s15, self.fec_s16, self.fec_s17,
                                               self.fec_s18, self.fec_s19, self.fec_s20, self.fec_s21, self.fec_s22])
            self.PEC_baseR = self.PECbaseSource(self.getPEF_source(), [self.fecR_s0, self.fecR_s1, self.fecR_s2,
                                                self.fecR_s3, self.fecR_s4, self.fecR_s5, self.fecR_s6, self.fecR_s7,
                                                self.fecR_s8, self.fecR_s9, self.fecR_s10, self.fecR_s11, self.fecR_s12,
                                                self.fecR_s13, self.fecR_s14, self.fecR_s15, self.fecR_s16,
                                                self.fecR_s17, self.fecR_s18, self.fecR_s19, self.fecR_s20,
                                                self.fecR_s21, self.fecR_s22])
            self.PEC_baseT = self.PECbaseSource(self.getPEF_source(), [self.fecT_s0, self.fecT_s1, self.fecT_s2,
                                                self.fecT_s3, self.fecT_s4, self.fecT_s5, self.fecT_s6, self.fecT_s7,
                                                self.fecT_s8, self.fecT_s9, self.fecT_s10, self.fecT_s11, self.fecT_s12,
                                                self.fecT_s13, self.fecT_s14, self.fecT_s15, self.fecT_s16,
                                                self.fecT_s17, self.fecT_s18, self.fecT_s19, self.fecT_s20,
                                                self.fecT_s21, self.fecT_s22])

            self.PEC_base_SUM = np.sum(self.PEC_base)
            self.PEC_baseR_SUM = np.sum(self.PEC_baseR)
            self.PEC_baseT_SUM = np.sum(self.PEC_baseT)

            self.PEC_baseCF = [self.PEC_base[0], self.PEC_base[1], self.PEC_base[2]]
            self.PEC_baseCFR = [self.PEC_baseR[0], self.PEC_baseR[1], self.PEC_baseR[2]]
            self.PEC_baseCFT = [self.PEC_baseT[0], self.PEC_baseT[1], self.PEC_baseT[2]]

            self.my_log.log("close_calculation (future). self.PEC_base: " + str(self.PEC_base))
            self.my_log.log("close_calculation (future). self.getPEF_source(): " + str(self.getPEF_source()))
            self.my_log.log("close_calculation (future). self.PEC_base_SUM: " + str(self.PEC_base_SUM))

            self.PEC_RESWH = self.PEC_base[21] + self.PEC_base[3] + self.PEC_base[4] + self.PEC_base[5] + self.PEC_base[
                6] + self.PEC_base[7] + self.PEC_base[8] + self.PEC_base[9] + self.PEC_base[10] + self.PEC_base[11] + \
                             self.PEC_base[12] + self.PEC_base[13] + self.PEC_base[14] + self.PEC_base[15] + \
                             self.PEC_base[16] + self.PEC_base[17] + self.PEC_base[18] + self.PEC_base[19] + \
                             self.PEC_base[20]
            self.PEC_RESWHR = self.PEC_baseR[21] + self.PEC_baseR[3] + self.PEC_baseR[4] + self.PEC_baseR[5] + \
                              self.PEC_baseR[6] + self.PEC_baseR[7] + self.PEC_baseR[8] + self.PEC_baseR[9] + \
                              self.PEC_baseR[10] + self.PEC_baseR[11] + self.PEC_baseR[12] + self.PEC_baseR[13] + \
                              self.PEC_baseR[14] + self.PEC_baseR[15] + self.PEC_baseR[16] + self.PEC_baseR[17] + \
                              self.PEC_baseR[18] + self.PEC_baseR[19] + self.PEC_baseR[20]
            self.PEC_RESWHT = self.PEC_baseT[21] + self.PEC_baseT[3] + self.PEC_baseT[4] + self.PEC_baseT[5] + \
                              self.PEC_baseT[6] + self.PEC_baseT[7] + self.PEC_baseT[8] + self.PEC_baseT[9] + \
                              self.PEC_baseT[10] + self.PEC_baseT[11] + self.PEC_baseT[12] + self.PEC_baseT[13] + \
                              self.PEC_baseT[14] + self.PEC_baseT[15] + self.PEC_baseT[16] + self.PEC_baseT[17] + \
                              self.PEC_baseT[18] + self.PEC_baseT[19] + self.PEC_baseT[20]

            KPIs["EN_1.3"] = round(self.PEC_base_SUM, 2)
            KPIs["EN_1.3R"] = round(self.PEC_baseR_SUM, 2)
            KPIs["EN_1.3T"] = round(self.PEC_baseT_SUM, 2)

            try:
                KPIs["EN_1.4"] = round(KPIs["EN_1.3"] / self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.4"] = "Nan"
            try:
                KPIs["EN_1.4R"] = round(KPIs["EN_1.3R"] / self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.4R"] = "Nan"
            try:
                KPIs["EN_1.4T"] = round(KPIs["EN_1.3T"] / (self.area - self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.4T"] = "Nan"
            try:
                KPIs["EN_1.5"] = (KPIs["EN_1.3"] / KPIs["EN_1.1"] - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.5"] = "Nan"
            try:
                KPIs["EN_1.5R"] = (KPIs["EN_1.3R"] / KPIs["EN_1.1R"] - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.5R"] = "Nan"
            try:
                KPIs["EN_1.5T"] = (KPIs["EN_1.3T"] / KPIs["EN_1.1T"] - 1) * 100
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

            KPIs["EN_2.3"] = "Nan"
            KPIs["EN_2.3R"] = "Nan"
            KPIs["EN_2.3T"] = "Nan"
            KPIs["EN_2.4"] = "Nan"
            KPIs["EN_2.4R"] = "Nan"
            KPIs["EN_2.4T"] = "Nan"
            KPIs["EN_2.5"] = "Nan"
            KPIs["EN_2.5R"] = "Nan"
            KPIs["EN_2.5T"] = "Nan"
            KPIs["EN_2.6"] = "Nan"
            KPIs["EN_2.6R"] = "Nan"
            KPIs["EN_2.6T"] = "Nan"

            KPIs["EN_2.3_s0"] = self.fec_s0
            KPIs["EN_2.3_s1"] = self.fec_s1
            KPIs["EN_2.3_s2"] = self.fec_s2
            KPIs["EN_2.3_s3"] = self.fec_s3
            KPIs["EN_2.3_s4"] = self.fec_s4
            KPIs["EN_2.3_s5"] = self.fec_s5
            KPIs["EN_2.3_s6"] = self.fec_s6
            KPIs["EN_2.3_s7"] = self.fec_s7
            KPIs["EN_2.3_s8"] = self.fec_s8
            KPIs["EN_2.3_s9"] = self.fec_s9
            KPIs["EN_2.3_s10"] = self.fec_s10
            KPIs["EN_2.3_s11"] = self.fec_s11
            KPIs["EN_2.3_s12"] = self.fec_s12
            KPIs["EN_2.3_s13"] = self.fec_s13
            KPIs["EN_2.3_s14"] = self.fec_s14
            KPIs["EN_2.3_s15"] = self.fec_s15
            KPIs["EN_2.3_s16"] = self.fec_s16
            KPIs["EN_2.3_s17"] = self.fec_s17
            KPIs["EN_2.3_s18"] = self.fec_s18
            KPIs["EN_2.3_s19"] = self.fec_s19
            KPIs["EN_2.3_s20"] = self.fec_s20
            KPIs["EN_2.3_s21"] = self.fec_s21
            KPIs["EN_2.3_s22"] = self.fec_s22

            KPIs["EN_2.3R_s0"] = self.fecR_s0
            KPIs["EN_2.3R_s1"] = self.fecR_s1
            KPIs["EN_2.3R_s2"] = self.fecR_s2
            KPIs["EN_2.3R_s3"] = self.fecR_s3
            KPIs["EN_2.3R_s4"] = self.fecR_s4
            KPIs["EN_2.3R_s5"] = self.fecR_s5
            KPIs["EN_2.3R_s6"] = self.fecR_s6
            KPIs["EN_2.3R_s7"] = self.fecR_s7
            KPIs["EN_2.3R_s8"] = self.fecR_s8
            KPIs["EN_2.3R_s9"] = self.fecR_s9
            KPIs["EN_2.3R_s10"] = self.fecR_s10
            KPIs["EN_2.3R_s11"] = self.fecR_s11
            KPIs["EN_2.3R_s12"] = self.fecR_s12
            KPIs["EN_2.3R_s13"] = self.fecR_s13
            KPIs["EN_2.3R_s14"] = self.fecR_s14
            KPIs["EN_2.3R_s15"] = self.fecR_s15
            KPIs["EN_2.3R_s16"] = self.fecR_s16
            KPIs["EN_2.3R_s17"] = self.fecR_s17
            KPIs["EN_2.3R_s18"] = self.fecR_s18
            KPIs["EN_2.3R_s19"] = self.fecR_s19
            KPIs["EN_2.3R_s20"] = self.fecR_s20
            KPIs["EN_2.3R_s21"] = self.fecR_s21
            KPIs["EN_2.3R_s22"] = self.fecR_s22

            KPIs["EN_2.3T_s0"] = self.fecT_s0
            KPIs["EN_2.3T_s1"] = self.fecT_s1
            KPIs["EN_2.3T_s2"] = self.fecT_s2
            KPIs["EN_2.3T_s3"] = self.fecT_s3
            KPIs["EN_2.3T_s4"] = self.fecT_s4
            KPIs["EN_2.3T_s5"] = self.fecT_s5
            KPIs["EN_2.3T_s6"] = self.fecT_s6
            KPIs["EN_2.3T_s7"] = self.fecT_s7
            KPIs["EN_2.3T_s8"] = self.fecT_s8
            KPIs["EN_2.3T_s9"] = self.fecT_s9
            KPIs["EN_2.3T_s10"] = self.fecT_s10
            KPIs["EN_2.3T_s11"] = self.fecT_s11
            KPIs["EN_2.3T_s12"] = self.fecT_s12
            KPIs["EN_2.3T_s13"] = self.fecT_s13
            KPIs["EN_2.3T_s14"] = self.fecT_s14
            KPIs["EN_2.3T_s15"] = self.fecT_s15
            KPIs["EN_2.3T_s16"] = self.fecT_s16
            KPIs["EN_2.3T_s17"] = self.fecT_s17
            KPIs["EN_2.3T_s18"] = self.fecT_s18
            KPIs["EN_2.3T_s19"] = self.fecT_s19
            KPIs["EN_2.3T_s20"] = self.fecT_s20
            KPIs["EN_2.3T_s21"] = self.fecT_s21
            KPIs["EN_2.3T_s22"] = self.fecT_s22

            # setta le cose del tipo self.FECadjBase_s0 usate qui sotto usando gli EN_2.3 di cui sopra
            self.FECadj_future(KPIs)

            pef = self.getPEF_source()
            self.pecADJ_s0 = self.FECadjBase_s0 * pef[0]
            self.pecADJ_s1 = self.FECadjBase_s1 * pef[1]
            self.pecADJ_s2 = self.FECadjBase_s2 * pef[2]
            self.pecADJ_s3 = self.FECadjBase_s3 * pef[3]
            self.pecADJ_s4 = self.FECadjBase_s4 * pef[4]
            self.pecADJ_s5 = self.FECadjBase_s5 * pef[5]
            self.pecADJ_s6 = self.FECadjBase_s6 * pef[6]
            self.pecADJ_s7 = self.FECadjBase_s7 * pef[7]
            self.pecADJ_s8 = self.FECadjBase_s8 * pef[8]
            self.pecADJ_s9 = self.FECadjBase_s9 * pef[9]
            self.pecADJ_s10 = self.FECadjBase_s10 * pef[10]
            self.pecADJ_s11 = self.FECadjBase_s11 * pef[11]
            self.pecADJ_s12 = self.FECadjBase_s12 * pef[12]
            self.pecADJ_s13 = self.FECadjBase_s13 * pef[13]
            self.pecADJ_s14 = self.FECadjBase_s14 * pef[14]
            self.pecADJ_s15 = self.FECadjBase_s15 * pef[15]
            self.pecADJ_s16 = self.FECadjBase_s16 * pef[16]
            self.pecADJ_s17 = self.FECadjBase_s17 * pef[17]
            self.pecADJ_s18 = self.FECadjBase_s18 * pef[18]
            self.pecADJ_s19 = self.FECadjBase_s19 * pef[19]
            self.pecADJ_s20 = self.FECadjBase_s20 * pef[20]
            self.pecADJ_s21 = self.FECadjBase_s21 * pef[21]
            self.pecADJ_s22 = self.FECadjBase_s22 * pef[22]


            self.fecADJpesR_s0 = self.FECadjBaseR_s0 * pef[0]
            self.fecADJpesR_s1 = self.FECadjBaseR_s1 * pef[1]
            self.fecADJpesR_s2 = self.FECadjBaseR_s2 * pef[2]
            self.fecADJpesR_s3 = self.FECadjBaseR_s3 * pef[3]
            self.fecADJpesR_s4 = self.FECadjBaseR_s4 * pef[4]
            self.fecADJpesR_s5 = self.FECadjBaseR_s5 * pef[5]
            self.fecADJpesR_s6 = self.FECadjBaseR_s6 * pef[6]
            self.fecADJpesR_s7 = self.FECadjBaseR_s7 * pef[7]
            self.fecADJpesR_s8 = self.FECadjBaseR_s8 * pef[8]
            self.fecADJpesR_s9 = self.FECadjBaseR_s9 * pef[9]
            self.fecADJpesR_s10 = self.FECadjBaseR_s10 * pef[10]
            self.fecADJpesR_s11 = self.FECadjBaseR_s11 * pef[11]
            self.fecADJpesR_s12 = self.FECadjBaseR_s12 * pef[12]
            self.fecADJpesR_s13 = self.FECadjBaseR_s13 * pef[13]
            self.fecADJpesR_s14 = self.FECadjBaseR_s14 * pef[14]
            self.fecADJpesR_s15 = self.FECadjBaseR_s15 * pef[15]
            self.fecADJpesR_s16 = self.FECadjBaseR_s16 * pef[16]
            self.fecADJpesR_s17 = self.FECadjBaseR_s17 * pef[17]
            self.fecADJpesR_s18 = self.FECadjBaseR_s18 * pef[18]
            self.fecADJpesR_s19 = self.FECadjBaseR_s19 * pef[19]
            self.fecADJpesR_s20 = self.FECadjBaseR_s20 * pef[20]
            self.fecADJpesR_s21 = self.FECadjBaseR_s21 * pef[21]
            self.fecADJpesR_s22 = self.FECadjBaseR_s22 * pef[22]

            self.fecADJpesT_s0 = self.FECadjBaseT_s0 * pef[0]
            self.fecADJpesT_s1 = self.FECadjBaseT_s1 * pef[1]
            self.fecADJpesT_s2 = self.FECadjBaseT_s2 * pef[2]
            self.fecADJpesT_s3 = self.FECadjBaseT_s3 * pef[3]
            self.fecADJpesT_s4 = self.FECadjBaseT_s4 * pef[4]
            self.fecADJpesT_s5 = self.FECadjBaseT_s5 * pef[5]
            self.fecADJpesT_s6 = self.FECadjBaseT_s6 * pef[6]
            self.fecADJpesT_s7 = self.FECadjBaseT_s7 * pef[7]
            self.fecADJpesT_s8 = self.FECadjBaseT_s8 * pef[8]
            self.fecADJpesT_s9 = self.FECadjBaseT_s9 * pef[9]
            self.fecADJpesT_s10 = self.FECadjBaseT_s10 * pef[10]
            self.fecADJpesT_s11 = self.FECadjBaseT_s11 * pef[11]
            self.fecADJpesT_s12 = self.FECadjBaseT_s12 * pef[12]
            self.fecADJpesT_s13 = self.FECadjBaseT_s13 * pef[13]
            self.fecADJpesT_s14 = self.FECadjBaseT_s14 * pef[14]
            self.fecADJpesT_s15 = self.FECadjBaseT_s15 * pef[15]
            self.fecADJpesT_s16 = self.FECadjBaseT_s16 * pef[16]
            self.fecADJpesT_s17 = self.FECadjBaseT_s17 * pef[17]
            self.fecADJpesT_s18 = self.FECadjBaseT_s18 * pef[18]
            self.fecADJpesT_s19 = self.FECadjBaseT_s19 * pef[19]
            self.fecADJpesT_s20 = self.FECadjBaseT_s20 * pef[20]
            self.fecADJpesT_s21 = self.FECadjBaseT_s21 * pef[21]
            self.fecADJpesT_s22 = self.FECadjBaseT_s22 * pef[22]

            self.fecPES_s0 = self.fec_s0 * pef[0]
            self.fecPES_s1 = self.fec_s1 * pef[1]
            self.fecPES_s2 = self.fec_s2 * pef[2]
            self.fecPES_s3 = self.fec_s3 * pef[3]
            self.fecPES_s4 = self.fec_s4 * pef[4]
            self.fecPES_s5 = self.fec_s5 * pef[5]
            self.fecPES_s6 = self.fec_s6 * pef[6]
            self.fecPES_s7 = self.fec_s7 * pef[7]
            self.fecPES_s8 = self.fec_s8 * pef[8]
            self.fecPES_s9 = self.fec_s9 * pef[9]
            self.fecPES_s10 = self.fec_s10 * pef[10]
            self.fecPES_s11 = self.fec_s11 * pef[11]
            self.fecPES_s12 = self.fec_s12 * pef[12]
            self.fecPES_s13 = self.fec_s13 * pef[13]
            self.fecPES_s14 = self.fec_s14 * pef[14]
            self.fecPES_s15 = self.fec_s15 * pef[15]
            self.fecPES_s16 = self.fec_s16 * pef[16]
            self.fecPES_s17 = self.fec_s17 * pef[17]
            self.fecPES_s18 = self.fec_s18 * pef[18]
            self.fecPES_s19 = self.fec_s19 * pef[19]
            self.fecPES_s20 = self.fec_s20 * pef[20]
            self.fecPES_s21 = self.fec_s21 * pef[21]
            self.fecPES_s22 = self.fec_s22 * pef[22]

            self.fecPESR_s0 = self.fecR_s0 * pef[0]
            self.fecPESR_s1 = self.fecR_s1 * pef[1]
            self.fecPESR_s2 = self.fecR_s2 * pef[2]
            self.fecPESR_s3 = self.fecR_s3 * pef[3]
            self.fecPESR_s4 = self.fecR_s4 * pef[4]
            self.fecPESR_s5 = self.fecR_s5 * pef[5]
            self.fecPESR_s6 = self.fecR_s6 * pef[6]
            self.fecPESR_s7 = self.fecR_s7 * pef[7]
            self.fecPESR_s8 = self.fecR_s8 * pef[8]
            self.fecPESR_s9 = self.fecR_s9 * pef[9]
            self.fecPESR_s10 = self.fecR_s10 * pef[10]
            self.fecPESR_s11 = self.fecR_s11 * pef[11]
            self.fecPESR_s12 = self.fecR_s12 * pef[12]
            self.fecPESR_s13 = self.fecR_s13 * pef[13]
            self.fecPESR_s14 = self.fecR_s14 * pef[14]
            self.fecPESR_s15 = self.fecR_s15 * pef[15]
            self.fecPESR_s16 = self.fecR_s16 * pef[16]
            self.fecPESR_s17 = self.fecR_s17 * pef[17]
            self.fecPESR_s18 = self.fecR_s18 * pef[18]
            self.fecPESR_s19 = self.fecR_s19 * pef[19]
            self.fecPESR_s20 = self.fecR_s20 * pef[20]
            self.fecPESR_s21 = self.fecR_s21 * pef[21]
            self.fecPESR_s22 = self.fecR_s22 * pef[22]

            self.fecPEST_s0 = self.fecT_s0 * pef[0]
            self.fecPEST_s1 = self.fecT_s1 * pef[1]
            self.fecPEST_s2 = self.fecT_s2 * pef[2]
            self.fecPEST_s3 = self.fecT_s3 * pef[3]
            self.fecPEST_s4 = self.fecT_s4 * pef[4]
            self.fecPEST_s5 = self.fecT_s5 * pef[5]
            self.fecPEST_s6 = self.fecT_s6 * pef[6]
            self.fecPEST_s7 = self.fecT_s7 * pef[7]
            self.fecPEST_s8 = self.fecT_s8 * pef[8]
            self.fecPEST_s9 = self.fecT_s9 * pef[9]
            self.fecPEST_s10 = self.fecT_s10 * pef[10]
            self.fecPEST_s11 = self.fecT_s11 * pef[11]
            self.fecPEST_s12 = self.fecT_s12 * pef[12]
            self.fecPEST_s13 = self.fecT_s13 * pef[13]
            self.fecPEST_s14 = self.fecT_s14 * pef[14]
            self.fecPEST_s15 = self.fecT_s15 * pef[15]
            self.fecPEST_s16 = self.fecT_s16 * pef[16]
            self.fecPEST_s17 = self.fecT_s17 * pef[17]
            self.fecPEST_s18 = self.fecT_s18 * pef[18]
            self.fecPEST_s19 = self.fecT_s19 * pef[19]
            self.fecPEST_s20 = self.fecT_s20 * pef[20]
            self.fecPEST_s21 = self.fecT_s21 * pef[21]
            self.fecPEST_s22 = self.fecT_s22 * pef[22]

            self.sumPECsav = (self.pecADJ_s0 - self.fecPES_s0) + (self.pecADJ_s1 - self.fecPES_s1) + (
                        self.pecADJ_s2 - self.fecPES_s2) + (self.pecADJ_s3 - self.fecPES_s3) + (
                                         self.pecADJ_s4 - self.fecPES_s4) + (self.pecADJ_s5 - self.fecPES_s5) + (
                                         self.pecADJ_s6 - self.fecPES_s6) + (self.pecADJ_s7 - self.fecPES_s7) + (
                                         self.pecADJ_s8 - self.fecPES_s8) + (self.pecADJ_s9 - self.fecPES_s9) + (
                                         self.pecADJ_s10 - self.fecPES_s10) + (self.pecADJ_s11 - self.fecPES_s11) + (
                                         self.pecADJ_s12 - self.fecPES_s12) + (self.pecADJ_s13 - self.fecPES_s13) + (
                                         self.pecADJ_s14 - self.fecPES_s14) + (self.pecADJ_s15 - self.fecPES_s15) + (
                                         self.pecADJ_s16 - self.fecPES_s16) + (self.pecADJ_s17 - self.fecPES_s17) + (
                                         self.pecADJ_s18 - self.fecPES_s18) + (self.pecADJ_s19 - self.fecPES_s19) + (
                                         self.pecADJ_s20 - self.fecPES_s20) + (self.pecADJ_s21 - self.fecPES_s21) + (
                                         self.pecADJ_s22 - self.fecPES_s22)
            self.sumPECsavR = (self.fecADJpesR_s0 - self.fecPESR_s0) + (self.fecADJpesR_s1 - self.fecPESR_s1) + (
                        self.fecADJpesR_s2 - self.fecPESR_s2) + (self.fecADJpesR_s3 - self.fecPESR_s3) + (
                                          self.fecADJpesR_s4 - self.fecPESR_s4) + (self.fecADJpesR_s5 - self.fecPESR_s5) + (
                                          self.fecADJpesR_s6 - self.fecPESR_s6) + (self.fecADJpesR_s7 - self.fecPESR_s7) + (
                                          self.fecADJpesR_s8 - self.fecPESR_s8) + (self.fecADJpesR_s9 - self.fecPESR_s9) + (
                                          self.fecADJpesR_s10 - self.fecPESR_s10) + (self.fecADJpesR_s11 - self.fecPESR_s11) + (
                                          self.fecADJpesR_s12 - self.fecPESR_s12) + (self.fecADJpesR_s13 - self.fecPESR_s13) + (
                                          self.fecADJpesR_s14 - self.fecPESR_s14) + (self.fecADJpesR_s15 - self.fecPESR_s15) + (
                                          self.fecADJpesR_s16 - self.fecPESR_s16) + (self.fecADJpesR_s17 - self.fecPESR_s17) + (
                                          self.fecADJpesR_s18 - self.fecPESR_s18) + (self.fecADJpesR_s19 - self.fecPESR_s19) + (
                                          self.fecADJpesR_s20 - self.fecPESR_s20) + (self.fecADJpesR_s21 - self.fecPESR_s21) + (
                                          self.fecADJpesR_s22 - self.fecPESR_s22)
            self.sumPECsavT = (self.fecADJpesT_s0 - self.fecPEST_s0) + (self.fecADJpesT_s1 - self.fecPEST_s1) + (
                        self.fecADJpesT_s2 - self.fecPEST_s2) + (self.fecADJpesT_s3 - self.fecPEST_s3) + (
                                          self.fecADJpesT_s4 - self.fecPEST_s4) + (self.fecADJpesT_s5 - self.fecPEST_s5) + (
                                          self.fecADJpesT_s6 - self.fecPEST_s6) + (self.fecADJpesT_s7 - self.fecPEST_s7) + (
                                          self.fecADJpesT_s8 - self.fecPEST_s8) + (self.fecADJpesT_s9 - self.fecPEST_s9) + (
                                          self.fecADJpesT_s10 - self.fecPEST_s10) + (self.fecADJpesT_s11 - self.fecPEST_s11) + (
                                          self.fecADJpesT_s12 - self.fecPEST_s12) + (self.fecADJpesT_s13 - self.fecPEST_s13) + (
                                          self.fecADJpesT_s14 - self.fecPEST_s14) + (self.fecADJpesT_s15 - self.fecPEST_s15) + (
                                          self.fecADJpesT_s16 - self.fecPEST_s16) + (self.fecADJpesT_s17 - self.fecPEST_s17) + (
                                          self.fecADJpesT_s18 - self.fecPEST_s18) + (self.fecADJpesT_s19 - self.fecPEST_s19) + (
                                          self.fecADJpesT_s20 - self.fecPEST_s20) + (self.fecADJpesT_s21 - self.fecPEST_s21) + (
                                          self.fecADJpesT_s22 - self.fecPEST_s22)

            KPIs["EN_1.6"] = -self.sumPECsav
            KPIs["EN_1.6R"] = -self.sumPECsavR
            KPIs["EN_1.6T"] = -self.sumPECsavT

            try:
                KPIs["EN_2.4_s0"] = round(self.fec_s0 / self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.4_s0"] = "Nan"
            try:
                KPIs["EN_2.4_s1"] = round(self.fec_s1 / self.area, 2)
                KPIs["EN_2.4_s2"] = round(self.fec_s2 / self.area, 2)
                KPIs["EN_2.4_s3"] = round(self.fec_s3 / self.area, 2)
                KPIs["EN_2.4_s4"] = round(self.fec_s4 / self.area, 2)
                KPIs["EN_2.4_s5"] = round(self.fec_s5 / self.area, 2)
                KPIs["EN_2.4_s6"] = round(self.fec_s6 / self.area, 2)
                KPIs["EN_2.4_s7"] = round(self.fec_s7 / self.area, 2)
                KPIs["EN_2.4_s0"] = round(self.fec_s8 / self.area, 2)
                KPIs["EN_2.4_s9"] = round(self.fec_s9 / self.area, 2)
                KPIs["EN_2.4_s10"] = round(self.fec_s10 / self.area, 2)
                KPIs["EN_2.4_s11"] = round(self.fec_s11 / self.area, 2)
                KPIs["EN_2.4_s12"] = round(self.fec_s12 / self.area, 2)
                KPIs["EN_2.4_s13"] = round(self.fec_s13 / self.area, 2)
                KPIs["EN_2.4_s14"] = round(self.fec_s14 / self.area, 2)
                KPIs["EN_2.4_s15"] = round(self.fec_s15 / self.area, 2)
                KPIs["EN_2.4_s16"] = round(self.fec_s16 / self.area, 2)
                KPIs["EN_2.4_s17"] = round(self.fec_s17 / self.area, 2)
                KPIs["EN_2.4_s18"] = round(self.fec_s18 / self.area, 2)
                KPIs["EN_2.4_s19"] = round(self.fec_s19 / self.area, 2)
                KPIs["EN_2.4_s20"] = round(self.fec_s20 / self.area, 2)
                KPIs["EN_2.4_s21"] = round(self.fec_s21 / self.area, 2)
                KPIs["EN_2.4_s22"] = round(self.fec_s22 / self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.4"] = "Nan"
            try:
                KPIs["EN_2.4R_s0"] = round(self.fecR_s0 / self.areaR, 2)
                KPIs["EN_2.4R_s1"] = round(self.fecR_s1 / self.areaR, 2)
                KPIs["EN_2.4R_s2"] = round(self.fecR_s2 / self.areaR, 2)
                KPIs["EN_2.4R_s3"] = round(self.fecR_s3 / self.areaR, 2)
                KPIs["EN_2.4R_s4"] = round(self.fecR_s4 / self.areaR, 2)
                KPIs["EN_2.4R_s5"] = round(self.fecR_s5 / self.areaR, 2)
                KPIs["EN_2.4R_s6"] = round(self.fecR_s6 / self.areaR, 2)
                KPIs["EN_2.4R_s7"] = round(self.fecR_s7 / self.areaR, 2)
                KPIs["EN_2.4R_s8"] = round(self.fecR_s8 / self.areaR, 2)
                KPIs["EN_2.4R_s9"] = round(self.fecR_s9 / self.areaR, 2)
                KPIs["EN_2.4R_s10"] = round(self.fecR_s10 / self.areaR, 2)
                KPIs["EN_2.4R_s11"] = round(self.fecR_s11 / self.areaR, 2)
                KPIs["EN_2.4R_s12"] = round(self.fecR_s12 / self.areaR, 2)
                KPIs["EN_2.4R_s13"] = round(self.fecR_s13 / self.areaR, 2)
                KPIs["EN_2.4R_s14"] = round(self.fecR_s14 / self.areaR, 2)
                KPIs["EN_2.4R_s15"] = round(self.fecR_s15 / self.areaR, 2)
                KPIs["EN_2.4R_s16"] = round(self.fecR_s16 / self.areaR, 2)
                KPIs["EN_2.4R_s17"] = round(self.fecR_s17 / self.areaR, 2)
                KPIs["EN_2.4R_s18"] = round(self.fecR_s18 / self.areaR, 2)
                KPIs["EN_2.4R_s19"] = round(self.fecR_s19 / self.areaR, 2)
                KPIs["EN_2.4R_s20"] = round(self.fecR_s20 / self.areaR, 2)
                KPIs["EN_2.4R_s21"] = round(self.fecR_s21 / self.areaR, 2)
                KPIs["EN_2.4R_s22"] = round(self.fecR_s22 / self.areaR, 2)

            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.4R"] = "Nan"
            try:
                KPIs["EN_2.4T_s0"] = round(self.fecT_s0 / self.area, 2)
                KPIs["EN_2.4T_s1"] = round(self.fecT_s1 / self.area, 2)
                KPIs["EN_2.4T_s2"] = round(self.fecT_s2 / self.area, 2)
                KPIs["EN_2.4T_s3"] = round(self.fecT_s3 / self.area, 2)
                KPIs["EN_2.4T_s4"] = round(self.fecT_s4 / self.area, 2)
                KPIs["EN_2.4T_s5"] = round(self.fecT_s5 / self.area, 2)
                KPIs["EN_2.4T_s6"] = round(self.fecT_s6 / self.area, 2)
                KPIs["EN_2.4T_s7"] = round(self.fecT_s7 / self.area, 2)
                KPIs["EN_2.4T_s0"] = round(self.fecT_s8 / self.area, 2)
                KPIs["EN_2.4T_s9"] = round(self.fecT_s9 / self.area, 2)
                KPIs["EN_2.4T_s10"] = round(self.fecT_s10 / self.area, 2)
                KPIs["EN_2.4T_s11"] = round(self.fecT_s11 / self.area, 2)
                KPIs["EN_2.4T_s12"] = round(self.fecT_s12 / self.area, 2)
                KPIs["EN_2.4T_s13"] = round(self.fecT_s13 / self.area, 2)
                KPIs["EN_2.4T_s14"] = round(self.fecT_s14 / self.area, 2)
                KPIs["EN_2.4T_s15"] = round(self.fecT_s15 / self.area, 2)
                KPIs["EN_2.4T_s16"] = round(self.fecT_s16 / self.area, 2)
                KPIs["EN_2.4T_s17"] = round(self.fecT_s17 / self.area, 2)
                KPIs["EN_2.4T_s18"] = round(self.fecT_s18 / self.area, 2)
                KPIs["EN_2.4T_s19"] = round(self.fecT_s19 / self.area, 2)
                KPIs["EN_2.4T_s20"] = round(self.fecT_s20 / self.area, 2)
                KPIs["EN_2.4T_s21"] = round(self.fecT_s21 / self.area, 2)
                KPIs["EN_2.4T_s22"] = round(self.fecT_s22 / self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.4T"] = "Nan"
            try:
                KPIs["EN_2.5_s0"] = (KPIs["EN_2.3_s0"] / KPIs["EN_2.1_s0"] - 1) * 100
                KPIs["EN_2.5_s1"] = (KPIs["EN_2.3_s1"] / KPIs["EN_2.1_s1"] - 1) * 100
                KPIs["EN_2.5_s2"] = (KPIs["EN_2.3_s2"] / KPIs["EN_2.1_s2"] - 1) * 100
                KPIs["EN_2.5_s3"] = (KPIs["EN_2.3_s3"] / KPIs["EN_2.1_s3"] - 1) * 100
                KPIs["EN_2.5_s4"] = (KPIs["EN_2.3_s4"] / KPIs["EN_2.1_s4"] - 1) * 100
                KPIs["EN_2.5_s5"] = (KPIs["EN_2.3_s5"] / KPIs["EN_2.1_s5"] - 1) * 100
                KPIs["EN_2.5_s6"] = (KPIs["EN_2.3_s6"] / KPIs["EN_2.1_s6"] - 1) * 100
                KPIs["EN_2.5_s7"] = (KPIs["EN_2.3_s7"] / KPIs["EN_2.1_s7"] - 1) * 100
                KPIs["EN_2.5_s8"] = (KPIs["EN_2.3_s8"] / KPIs["EN_2.1_s8"] - 1) * 100
                KPIs["EN_2.5_s9"] = (KPIs["EN_2.3_s9"] / KPIs["EN_2.1_s9"] - 1) * 100
                KPIs["EN_2.5_s10"] = (KPIs["EN_2.3_s10"] / KPIs["EN_2.1_s10"] - 1) * 100
                KPIs["EN_2.5_s11"] = (KPIs["EN_2.3_s11"] / KPIs["EN_2.1_s11"] - 1) * 100
                KPIs["EN_2.5_s12"] = (KPIs["EN_2.3_s12"] / KPIs["EN_2.1_s12"] - 1) * 100
                KPIs["EN_2.5_s13"] = (KPIs["EN_2.3_s13"] / KPIs["EN_2.1_s13"] - 1) * 100
                KPIs["EN_2.5_s14"] = (KPIs["EN_2.3_s14"] / KPIs["EN_2.1_s14"] - 1) * 100
                KPIs["EN_2.5_s15"] = (KPIs["EN_2.3_s15"] / KPIs["EN_2.1_s15"] - 1) * 100
                KPIs["EN_2.5_s16"] = (KPIs["EN_2.3_s16"] / KPIs["EN_2.1_s16"] - 1) * 100
                KPIs["EN_2.5_s17"] = (KPIs["EN_2.3_s17"] / KPIs["EN_2.1_s17"] - 1) * 100
                KPIs["EN_2.5_s18"] = (KPIs["EN_2.3_s18"] / KPIs["EN_2.1_s18"] - 1) * 100
                KPIs["EN_2.5_s19"] = (KPIs["EN_2.3_s19"] / KPIs["EN_2.1_s19"] - 1) * 100
                KPIs["EN_2.5_s20"] = (KPIs["EN_2.3_s20"] / KPIs["EN_2.1_s20"] - 1) * 100
                KPIs["EN_2.5_s21"] = (KPIs["EN_2.3_s21"] / KPIs["EN_2.1_s21"] - 1) * 100
                KPIs["EN_2.5_s22"] = (KPIs["EN_2.3_s22"] / KPIs["EN_2.1_s22"] - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.5"] = "Nan"
            try:
                KPIs["EN_2.5R_s0"] = (KPIs["EN_2.3R_s0"] / KPIs["EN_2.1R_s0"] - 1) * 100
                KPIs["EN_2.5R_s1"] = (KPIs["EN_2.3R_s1"] / KPIs["EN_2.1R_s1"] - 1) * 100
                KPIs["EN_2.5R_s2"] = (KPIs["EN_2.3R_s2"] / KPIs["EN_2.1R_s2"] - 1) * 100
                KPIs["EN_2.5R_s3"] = (KPIs["EN_2.3R_s3"] / KPIs["EN_2.1R_s3"] - 1) * 100
                KPIs["EN_2.5R_s4"] = (KPIs["EN_2.3R_s4"] / KPIs["EN_2.1R_s4"] - 1) * 100
                KPIs["EN_2.5R_s5"] = (KPIs["EN_2.3R_s5"] / KPIs["EN_2.1R_s5"] - 1) * 100
                KPIs["EN_2.5R_s6"] = (KPIs["EN_2.3R_s6"] / KPIs["EN_2.1R_s6"] - 1) * 100
                KPIs["EN_2.5R_s7"] = (KPIs["EN_2.3R_s7"] / KPIs["EN_2.1R_s7"] - 1) * 100
                KPIs["EN_2.5R_s8"] = (KPIs["EN_2.3R_s8"] / KPIs["EN_2.1R_s8"] - 1) * 100
                KPIs["EN_2.5R_s9"] = (KPIs["EN_2.3R_s9"] / KPIs["EN_2.1R_s9"] - 1) * 100
                KPIs["EN_2.5R_s10"] = (KPIs["EN_2.3R_s10"] / KPIs["EN_2.1R_s10"] - 1) * 100
                KPIs["EN_2.5R_s11"] = (KPIs["EN_2.3R_s11"] / KPIs["EN_2.1R_s11"] - 1) * 100
                KPIs["EN_2.5R_s12"] = (KPIs["EN_2.3R_s12"] / KPIs["EN_2.1R_s12"] - 1) * 100
                KPIs["EN_2.5R_s13"] = (KPIs["EN_2.3R_s13"] / KPIs["EN_2.1R_s13"] - 1) * 100
                KPIs["EN_2.5R_s14"] = (KPIs["EN_2.3R_s14"] / KPIs["EN_2.1R_s14"] - 1) * 100
                KPIs["EN_2.5R_s15"] = (KPIs["EN_2.3R_s15"] / KPIs["EN_2.1R_s15"] - 1) * 100
                KPIs["EN_2.5R_s16"] = (KPIs["EN_2.3R_s16"] / KPIs["EN_2.1R_s16"] - 1) * 100
                KPIs["EN_2.5R_s17"] = (KPIs["EN_2.3R_s17"] / KPIs["EN_2.1R_s17"] - 1) * 100
                KPIs["EN_2.5R_s18"] = (KPIs["EN_2.3R_s18"] / KPIs["EN_2.1R_s18"] - 1) * 100
                KPIs["EN_2.5R_s19"] = (KPIs["EN_2.3R_s19"] / KPIs["EN_2.1R_s19"] - 1) * 100
                KPIs["EN_2.5R_s20"] = (KPIs["EN_2.3R_s20"] / KPIs["EN_2.1R_s20"] - 1) * 100
                KPIs["EN_2.5R_s21"] = (KPIs["EN_2.3R_s21"] / KPIs["EN_2.1R_s21"] - 1) * 100
                KPIs["EN_2.5R_s22"] = (KPIs["EN_2.3R_s22"] / KPIs["EN_2.1R_s22"] - 1) * 100

            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.5R"] = "Nan"
            try:
                KPIs["EN_2.5T_s0"] = (KPIs["EN_2.3T_s0"] / KPIs["EN_2.1T_s0"] - 1) * 100
                KPIs["EN_2.5T_s1"] = (KPIs["EN_2.3T_s1"] / KPIs["EN_2.1T_s1"] - 1) * 100
                KPIs["EN_2.5T_s2"] = (KPIs["EN_2.3T_s2"] / KPIs["EN_2.1T_s2"] - 1) * 100
                KPIs["EN_2.5T_s3"] = (KPIs["EN_2.3T_s3"] / KPIs["EN_2.1T_s3"] - 1) * 100
                KPIs["EN_2.5T_s4"] = (KPIs["EN_2.3T_s4"] / KPIs["EN_2.1T_s4"] - 1) * 100
                KPIs["EN_2.5T_s5"] = (KPIs["EN_2.3T_s5"] / KPIs["EN_2.1T_s5"] - 1) * 100
                KPIs["EN_2.5T_s6"] = (KPIs["EN_2.3T_s6"] / KPIs["EN_2.1T_s6"] - 1) * 100
                KPIs["EN_2.5T_s7"] = (KPIs["EN_2.3T_s7"] / KPIs["EN_2.1T_s7"] - 1) * 100
                KPIs["EN_2.5T_s8"] = (KPIs["EN_2.3T_s8"] / KPIs["EN_2.1T_s8"] - 1) * 100
                KPIs["EN_2.5T_s9"] = (KPIs["EN_2.3T_s9"] / KPIs["EN_2.1T_s9"] - 1) * 100
                KPIs["EN_2.5T_s10"] = (KPIs["EN_2.3T_s10"] / KPIs["EN_2.1T_s10"] - 1) * 100
                KPIs["EN_2.5T_s11"] = (KPIs["EN_2.3T_s11"] / KPIs["EN_2.1T_s11"] - 1) * 100
                KPIs["EN_2.5T_s12"] = (KPIs["EN_2.3T_s12"] / KPIs["EN_2.1T_s12"] - 1) * 100
                KPIs["EN_2.5T_s13"] = (KPIs["EN_2.3T_s13"] / KPIs["EN_2.1T_s13"] - 1) * 100
                KPIs["EN_2.5T_s14"] = (KPIs["EN_2.3T_s14"] / KPIs["EN_2.1T_s14"] - 1) * 100
                KPIs["EN_2.5T_s15"] = (KPIs["EN_2.3T_s15"] / KPIs["EN_2.1T_s15"] - 1) * 100
                KPIs["EN_2.5T_s16"] = (KPIs["EN_2.3T_s16"] / KPIs["EN_2.1T_s16"] - 1) * 100
                KPIs["EN_2.5T_s17"] = (KPIs["EN_2.3T_s17"] / KPIs["EN_2.1T_s17"] - 1) * 100
                KPIs["EN_2.5T_s18"] = (KPIs["EN_2.3T_s18"] / KPIs["EN_2.1T_s18"] - 1) * 100
                KPIs["EN_2.5T_s19"] = (KPIs["EN_2.3T_s19"] / KPIs["EN_2.1T_s19"] - 1) * 100
                KPIs["EN_2.5T_s20"] = (KPIs["EN_2.3T_s20"] / KPIs["EN_2.1T_s20"] - 1) * 100
                KPIs["EN_2.5T_s21"] = (KPIs["EN_2.3T_s21"] / KPIs["EN_2.1T_s21"] - 1) * 100
                KPIs["EN_2.5T_s22"] = (KPIs["EN_2.3T_s22"] / KPIs["EN_2.1T_s22"] - 1) * 100
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

            KPIs["EN_2.6_s0"] = self.FECadjBase_s0 - KPIs["EN_2.3_s0"]
            KPIs["EN_2.6_s1"] = self.FECadjBase_s1 - KPIs["EN_2.3_s1"]
            KPIs["EN_2.6_s2"] = self.FECadjBase_s2 - KPIs["EN_2.3_s2"]
            KPIs["EN_2.6_s3"] = self.FECadjBase_s3 - KPIs["EN_2.3_s3"]
            KPIs["EN_2.6_s4"] = self.FECadjBase_s4 - KPIs["EN_2.3_s4"]
            KPIs["EN_2.6_s5"] = self.FECadjBase_s5 - KPIs["EN_2.3_s5"]
            KPIs["EN_2.6_s6"] = self.FECadjBase_s6 - KPIs["EN_2.3_s6"]
            KPIs["EN_2.6_s7"] = self.FECadjBase_s7 - KPIs["EN_2.3_s7"]
            KPIs["EN_2.6_s8"] = self.FECadjBase_s8 - KPIs["EN_2.3_s8"]
            KPIs["EN_2.6_s9"] = self.FECadjBase_s9 - KPIs["EN_2.3_s9"]
            KPIs["EN_2.6_s10"] = self.FECadjBase_s10 - KPIs["EN_2.3_s10"]
            KPIs["EN_2.6_s11"] = self.FECadjBase_s11 - KPIs["EN_2.3_s11"]
            KPIs["EN_2.6_s12"] = self.FECadjBase_s12 - KPIs["EN_2.3_s12"]
            KPIs["EN_2.6_s13"] = self.FECadjBase_s13 - KPIs["EN_2.3_s13"]
            KPIs["EN_2.6_s14"] = self.FECadjBase_s14 - KPIs["EN_2.3_s14"]
            KPIs["EN_2.6_s15"] = self.FECadjBase_s15 - KPIs["EN_2.3_s15"]
            KPIs["EN_2.6_s16"] = self.FECadjBase_s16 - KPIs["EN_2.3_s16"]
            KPIs["EN_2.6_s17"] = self.FECadjBase_s17 - KPIs["EN_2.3_s17"]
            KPIs["EN_2.6_s18"] = self.FECadjBase_s18 - KPIs["EN_2.3_s18"]
            KPIs["EN_2.6_s19"] = self.FECadjBase_s19 - KPIs["EN_2.3_s19"]
            KPIs["EN_2.6_s20"] = self.FECadjBase_s20 - KPIs["EN_2.3_s20"]
            KPIs["EN_2.6_s21"] = self.FECadjBase_s21 - KPIs["EN_2.3_s21"]
            KPIs["EN_2.6_s22"] = self.FECadjBase_s22 - KPIs["EN_2.3_s22"]

            KPIs["EN_2.6R_s0"] = self.FECadjBaseR_s0 - KPIs["EN_2.3R_s0"]
            KPIs["EN_2.6R_s1"] = self.FECadjBaseR_s1 - KPIs["EN_2.3R_s1"]
            KPIs["EN_2.6R_s2"] = self.FECadjBaseR_s2 - KPIs["EN_2.3R_s2"]
            KPIs["EN_2.6R_s3"] = self.FECadjBaseR_s3 - KPIs["EN_2.3R_s3"]
            KPIs["EN_2.6R_s4"] = self.FECadjBaseR_s4 - KPIs["EN_2.3R_s4"]
            KPIs["EN_2.6R_s5"] = self.FECadjBaseR_s5 - KPIs["EN_2.3R_s5"]
            KPIs["EN_2.6R_s6"] = self.FECadjBaseR_s6 - KPIs["EN_2.3R_s6"]
            KPIs["EN_2.6R_s7"] = self.FECadjBaseR_s7 - KPIs["EN_2.3R_s7"]
            KPIs["EN_2.6R_s8"] = self.FECadjBaseR_s8 - KPIs["EN_2.3R_s8"]
            KPIs["EN_2.6R_s9"] = self.FECadjBaseR_s9 - KPIs["EN_2.3R_s9"]
            KPIs["EN_2.6R_s10"] = self.FECadjBaseR_s10 - KPIs["EN_2.3R_s10"]
            KPIs["EN_2.6R_s11"] = self.FECadjBaseR_s11 - KPIs["EN_2.3R_s11"]
            KPIs["EN_2.6R_s12"] = self.FECadjBaseR_s12 - KPIs["EN_2.3R_s12"]
            KPIs["EN_2.6R_s13"] = self.FECadjBaseR_s13 - KPIs["EN_2.3R_s13"]
            KPIs["EN_2.6R_s14"] = self.FECadjBaseR_s14 - KPIs["EN_2.3R_s14"]
            KPIs["EN_2.6R_s15"] = self.FECadjBaseR_s15 - KPIs["EN_2.3R_s15"]
            KPIs["EN_2.6R_s16"] = self.FECadjBaseR_s16 - KPIs["EN_2.3R_s16"]
            KPIs["EN_2.6R_s17"] = self.FECadjBaseR_s17 - KPIs["EN_2.3R_s17"]
            KPIs["EN_2.6R_s18"] = self.FECadjBaseR_s18 - KPIs["EN_2.3R_s18"]
            KPIs["EN_2.6R_s19"] = self.FECadjBaseR_s19 - KPIs["EN_2.3R_s19"]
            KPIs["EN_2.6R_s20"] = self.FECadjBaseR_s20 - KPIs["EN_2.3R_s20"]
            KPIs["EN_2.6R_s21"] = self.FECadjBaseR_s21 - KPIs["EN_2.3R_s21"]
            KPIs["EN_2.6R_s22"] = self.FECadjBaseR_s22 - KPIs["EN_2.3R_s22"]

            KPIs["EN_2.6T_s0"] = self.FECadjBaseT_s0 - KPIs["EN_2.3T_s0"]
            KPIs["EN_2.6T_s1"] = self.FECadjBaseT_s1 - KPIs["EN_2.3T_s1"]
            KPIs["EN_2.6T_s2"] = self.FECadjBaseT_s2 - KPIs["EN_2.3T_s2"]
            KPIs["EN_2.6T_s3"] = self.FECadjBaseT_s3 - KPIs["EN_2.3T_s3"]
            KPIs["EN_2.6T_s4"] = self.FECadjBaseT_s4 - KPIs["EN_2.3T_s4"]
            KPIs["EN_2.6T_s5"] = self.FECadjBaseT_s5 - KPIs["EN_2.3T_s5"]
            KPIs["EN_2.6T_s6"] = self.FECadjBaseT_s6 - KPIs["EN_2.3T_s6"]
            KPIs["EN_2.6T_s7"] = self.FECadjBaseT_s7 - KPIs["EN_2.3T_s7"]
            KPIs["EN_2.6T_s8"] = self.FECadjBaseT_s8 - KPIs["EN_2.3T_s8"]
            KPIs["EN_2.6T_s9"] = self.FECadjBaseT_s9 - KPIs["EN_2.3T_s9"]
            KPIs["EN_2.6T_s10"] = self.FECadjBaseT_s10 - KPIs["EN_2.3T_s10"]
            KPIs["EN_2.6T_s11"] = self.FECadjBaseT_s11 - KPIs["EN_2.3T_s11"]
            KPIs["EN_2.6T_s12"] = self.FECadjBaseT_s12 - KPIs["EN_2.3T_s12"]
            KPIs["EN_2.6T_s13"] = self.FECadjBaseT_s13 - KPIs["EN_2.3T_s13"]
            KPIs["EN_2.6T_s14"] = self.FECadjBaseT_s14 - KPIs["EN_2.3T_s14"]
            KPIs["EN_2.6T_s15"] = self.FECadjBaseT_s15 - KPIs["EN_2.3T_s15"]
            KPIs["EN_2.6T_s16"] = self.FECadjBaseT_s16 - KPIs["EN_2.3T_s16"]
            KPIs["EN_2.6T_s17"] = self.FECadjBaseT_s17 - KPIs["EN_2.3T_s17"]
            KPIs["EN_2.6T_s18"] = self.FECadjBaseT_s18 - KPIs["EN_2.3T_s18"]
            KPIs["EN_2.6T_s19"] = self.FECadjBaseT_s19 - KPIs["EN_2.3T_s19"]
            KPIs["EN_2.6T_s20"] = self.FECadjBaseT_s20 - KPIs["EN_2.3T_s20"]
            KPIs["EN_2.6T_s21"] = self.FECadjBaseT_s21 - KPIs["EN_2.3T_s21"]
            KPIs["EN_2.6T_s22"] = self.FECadjBaseT_s22 - KPIs["EN_2.3T_s22"]

            try:
                KPIs["EN_2.6T"] = KPIs["EN_2.3T"] - KPIs["EN_2.1T"]
            except Exception as e:
                traceback.print_exc
                KPIs["EN_2.6T"] = "Nan"

            KPIs["EN_3.3"] = self.get_UED(self.future_scenario) + self.get_UED_networks(self.future_scenario, n_type=None, use=None)
            KPIs["EN_3.3R"] = self.get_UED(self.future_scenario, use="R") + self.get_UED_networks(self.future_scenario, n_type=None, use="R")
            KPIs["EN_3.3T"] = self.get_UED(self.future_scenario, use="T") + self.get_UED_networks(self.future_scenario, n_type=None, use="T")
            try:
                self.my_log.log("EN_3.4: numeratore, area", KPIs["EN_3.3"], self.area)
                KPIs["EN_3.4"] = round(KPIs["EN_3.3"] / self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.4"] = "Nan"
            try:
                KPIs["EN_3.4R"] = round(KPIs["EN_3.3R"] / self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.4R"] = "Nan"
            try:
                KPIs["EN_3.4T"] = round(KPIs["EN_3.3T"] / (self.area - self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.4T"] = "Nan"
            try:
                KPIs["EN_3.5"] = ((KPIs["EN_3.3"] - KPIs["EN_3.1"]) / KPIs["EN_3.1"]) * 100
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
                KPIs["EN_3.6"] = round(((KPIs["EN_3.4"] / KPIs["EN_3.2"]) -1)*100, 2)
            except Exception:
                KPIs["EN_3.6"] = "Nan"
            try:
                KPIs["EN_3.6R"] = round(((KPIs["EN_3.4R"] / KPIs["EN_3.2R"]) -1)*100, 2)
            except Exception:
                KPIs["EN_3.6R"] = "Nan"
            try:
                KPIs["EN_3.6T"] = round(((KPIs["EN_3.4T"] / KPIs["EN_3.2T"]) -1)*100, 2)
            except Exception:
                KPIs["EN_3.6T"] = "Nan"
            try:
                KPIs["EN_3.7"] = KPIs["EN_3.3"] - KPIs["EN_3.1"]
            except TypeError:
                KPIs["EN_3.7"] = "Nan"
            try:
                KPIs["EN_3.7R"] = KPIs["EN_3.3R"] - KPIs["EN_3.1R"]
            except TypeError:
                KPIs["EN_3.7R"] = "Nan"
            try:
                KPIs["EN_3.7T"] = KPIs["EN_3.3T"] - KPIs["EN_3.1T"]
            except TypeError:
                KPIs["EN_3.7T"] = "Nan"
            KPIs["EN_4.3"] = self.PEC_base[-2] + self.PEC_base[3] + self.PEC_base[4] + self.PEC_base[5] + self.PEC_base[6]
            KPIs["EN_4.3R"] = self.PEC_baseR[-2] + self.PEC_baseR[3] + self.PEC_baseR[4] + self.PEC_baseR[5] + self.PEC_baseR[6]
            KPIs["EN_4.3T"] = self.PEC_baseT[-2] + self.PEC_baseT[3] + self.PEC_baseT[4] + self.PEC_baseT[5] + self.PEC_baseT[6]

            self.RESadjBase = KPIs["EN_4.1"] * (1 + self.eco_param["demo_factor"])
            self.RESadjBaseR = KPIs["EN_4.1R"] * (1 + self.eco_param["demo_factor"])
            self.RESadjBaseT = KPIs["EN_4.1T"] * (1 + self.eco_param["demo_factor"])

            self.WHadjBase = KPIs["EN_5.1"] * (1 + self.eco_param["demo_factor"])
            self.WHadjBaseR = KPIs["EN_5.1R"] * (1 + self.eco_param["demo_factor"])
            self.WHadjBaseT = KPIs["EN_5.1T"] * (1 + self.eco_param["demo_factor"])

            self.FCadjBase = KPIs["EN_6.1"] * (1 + self.eco_param["demo_factor"])
            self.FCadjBaseR = KPIs["EN_6.1R"] * (1 + self.eco_param["demo_factor"])
            self.FCadjBaseT = KPIs["EN_6.1T"] * (1 + self.eco_param["demo_factor"])

            self.RESWHadjBase = KPIs["EN_12.1"] * (1 + self.eco_param["demo_factor"])
            self.RESWHadjBaseR = KPIs["EN_12.1R"] * (1 + self.eco_param["demo_factor"])
            self.RESWHadjBaseT = KPIs["EN_12.1T"] * (1 + self.eco_param["demo_factor"])

            self.PEC_baseCF_sum = sum(self.PEC_baseCF)
            self.PEC_baseCFR_sum = sum(self.PEC_baseCFR)
            self.PEC_baseCFT_sum = sum(self.PEC_baseCFT)

            try:
                KPIs["EN_4.4"] = KPIs["EN_4.3"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.4"] = "Nan"
            try:
                KPIs["EN_4.4R"] = KPIs["EN_4.3R"] / KPIs["EN_1.3R"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.4R"] = "Nan"
            try:
                KPIs["EN_4.4T"] = KPIs["EN_4.3T"] / KPIs["EN_1.3T"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.4T"] = "Nan"
            try:
                KPIs["EN_4.5"] = (KPIs["EN_4.3"] / self.RESadjBase - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.5"] = "Nan"
            try:
                KPIs["EN_4.5R"] = (KPIs["EN_4.3R"] / self.RESadjBaseR - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.5R"] = "Nan"
            try:
                KPIs["EN_4.5T"] = (KPIs["EN_4.3T"] / self.RESadjBaseT - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.5T"] = "Nan"
            KPIs["EN_5.3"] = self.PEC_base[7] + self.PEC_base[8] + self.PEC_base[9] + self.PEC_base[10] + self.PEC_base[11] + \
                             self.PEC_base[12] + self.PEC_base[13] + self.PEC_base[14] + self.PEC_base[15] + self.PEC_base[16] + \
                             self.PEC_base[17] + self.PEC_base[18] + self.PEC_base[19] + self.PEC_base[20]
            KPIs["EN_5.3R"] = self.PEC_baseR[7] + self.PEC_baseR[8] + self.PEC_baseR[9] + self.PEC_baseR[10] + self.PEC_baseR[11] + \
                              self.PEC_baseR[12] + self.PEC_baseR[13] + self.PEC_baseR[14] + self.PEC_baseR[15] + self.PEC_baseR[
                                  16] + self.PEC_baseR[17] + self.PEC_baseR[18] + self.PEC_baseR[19] + self.PEC_baseR[20]
            KPIs["EN_5.3T"] = self.PEC_baseT[7] + self.PEC_baseT[8] + self.PEC_baseT[9] + self.PEC_baseT[10] + self.PEC_baseT[11] + \
                              self.PEC_baseT[12] + self.PEC_baseT[13] + self.PEC_baseT[14] + self.PEC_baseT[15] + self.PEC_baseT[
                                  16] + self.PEC_baseT[17] + self.PEC_baseT[18] + self.PEC_baseT[19] + self.PEC_baseT[20]
            try:
                KPIs["EN_5.4"] = KPIs["EN_5.3"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.4"] = "Nan"
            try:
                KPIs["EN_5.4R"] = KPIs["EN_5.3R"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.4R"] = "Nan"
            try:
                KPIs["EN_5.4T"] = KPIs["EN_5.3T"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.4T"] = "Nan"
            try:
                KPIs["EN_5.5"] = (KPIs["EN_5.3"] / self.WHadjBase - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.5"] = "Nan"
            try:
                KPIs["EN_5.5R"] = (KPIs["EN_5.3R"] / self.WHadjBaseR - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.5R"] = "Nan"
            try:
                KPIs["EN_5.5T"] = (KPIs["EN_5.3T"] / self.WHadjBaseT - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.5T"] = "Nan"
            KPIs["EN_6.3"] = self.PEC_base[0] + self.PEC_base[1] + self.PEC_base[2]
            KPIs["EN_6.3R"] = self.PEC_baseR[0] + self.PEC_baseR[1] + self.PEC_baseR[2]
            KPIs["EN_6.3T"] = self.PEC_baseT[0] + self.PEC_baseT[1] + self.PEC_baseT[2]
            try:
                KPIs["EN_6.4"] = KPIs["EN_6.3"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.4"] = "Nan"
            try:
                KPIs["EN_6.4R"] = KPIs["EN_6.3R"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.4R"] = "Nan"
            try:
                KPIs["EN_6.4T"] = KPIs["EN_6.3T"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.4T"] = "Nan"
            try:
                KPIs["EN_6.5"] = (KPIs["EN_6.3"] / self.FCadjBase - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.5"] = "Nan"
            try:
                KPIs["EN_6.5R"] = (KPIs["EN_6.3R"] / self.FCadjBaseR - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.5R"] = "Nan"
            try:
                KPIs["EN_6.5T"] = (KPIs["EN_6.3T"] / self.FCadjBaseT - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.5T"] = "Nan"
            KPIs["EN_7.3"] = round(self.PEC_baseCF_sum, 2)
            KPIs["EN_7.3R"] = round(self.PEC_baseCFR_sum, 2)
            KPIs["EN_7.3T"] = round(self.PEC_baseCFT_sum, 2)
            try:
                KPIs["EN_7.4"] = KPIs["EN_7.3"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.4"] = "Nan"
            try:
                KPIs["EN_7.4R"] = KPIs["EN_7.3R"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.4R"] = "Nan"
            try:
                KPIs["EN_7.4T"] = KPIs["EN_7.3T"] / KPIs["EN_1.3"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.4T"] = "Nan"
            try:
                KPIs["EN_7.5"] = (KPIs["EN_7.3"] / self.FCadjBase - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.5"] = "Nan"
            try:
                KPIs["EN_7.5R"] = (KPIs["EN_7.3R"] / self.FCadjBaseR - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.5R"] = "Nan"
            try:
                KPIs["EN_7.5T"] = (KPIs["EN_7.3T"] / self.FCadjBaseT - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.5T"] = "Nan"
            try:
                KPIs["EN_9.2"] = (self.get_UED_cooling(self.future_scenario) / KPIs["EN_3.3"]) * 100
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
            try:
                KPIs["EN_11.3"] = round((self.PEC_base[6] / KPIs["EN_1.3"]) * 100, 2)
            except (ZeroDivisionError, TypeError, KeyError) as e:
                KPIs["EN_11.3"] = "Nan"
            KPIs["EN_11.3R"] = round((self.PEC_baseR[6] / KPIs["EN_1.3R"]) * 100, 2)
            KPIs["EN_11.3T"] = round((self.PEC_baseT[6] / KPIs["EN_1.3T"]) * 100, 2)

            # KPIs["EN_11.3"] = self.fec_s6
            # KPIs["EN_11.3R"] = self.fecR_s6
            # KPIs["EN_11.3R"] = self.fecT_s6

            try:
                KPIs["EN_12.2"] = round((self.PEC_RESWH  / KPIs["EN_1.3"])*100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.2"] = "Nan"
            try:
                KPIs["EN_12.2R"] = round((self.PEC_RESWHR  / KPIs["EN_1.3R"])*100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.2R"] = "Nan"
            try:
                KPIs["EN_12.2T"] = round((self.PEC_RESWHT  / KPIs["EN_1.3T"])*100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.2T"] = "Nan"

            try:
                KPIs["EN_12.3"] = "{:.2f}".format(round((self.PEC_RESWH / KPIs["EN_12.1_baseline"] - 1) * 100, 2))
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.3"] = "Nan"
            try:
                KPIs["EN_12.3R"] = "{:.2f}".format(round((self.PEC_RESWHR / KPIs["EN_12.1_baselineR"] - 1) * 100, 2))
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.3R"] = "Nan"
            try:
                KPIs["EN_12.3T"] = "{:.2f}".format(round((self.PEC_RESWHT / KPIs["EN_12.1_baselineT"] - 1) * 100, 2))
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.3T"] = "Nan"

            try:
                self.my_log.log("self.eco_param[\"eta_DHN\"]:", self.eco_param["eta_DHN"])
                eta_DHN_average = sum(self.eco_param["eta_DHN"])/len(self.eco_param["eta_DHN"])
            except ZeroDivisionError:
                eta_DHN_average = 0.0
            try:
                eta_DCN_average = sum(self.eco_param["eta_DCN"]) / len(self.eco_param["eta_DCN"])
            except ZeroDivisionError:
                eta_DCN_average = 0.0
            try:
                KPIs["EN_13.2"] = round(self.get_UED_networks(self.future_scenario, "DHN") * ((1 / eta_DHN_average)-1), 2)
            except:
                self.my_log.log("ERROR KPIs[\"EN_13.2\"]")
                KPIs["EN_13.2"] = "Nan"
            try:
                KPIs["EN_13.2R"] = round(self.get_UED_networks(self.future_scenario, "DHN", use="R") * ((1 / eta_DHN_average)-1), 2)
            except:
                self.my_log.log("ERROR KPIs[\"EN_13.2R\"]")
                KPIs["EN_13.2R"] = "Nan"
            try:
                KPIs["EN_13.2T"] = round(self.get_UED_networks(self.future_scenario, "DHN", use="T") * ((1 / eta_DHN_average)-1), 2)
            except:
                self.my_log.log("ERROR KPIs[\"EN_13.2T\"]")
                KPIs["EN_13.2T"] = "Nan"


            # KPIs["EN_13.2a"] = self.h_fec_eta - self.get_UED_heating(self.future_scenario)
            # KPIs["EN_13.2aR"] = self.h_fec_etaR - self.get_UED_heating(self.future_scenario, use="R")
            # KPIs["EN_13.2aT"] = self.h_fec_etaT - self.get_UED_heating(self.future_scenario, use="T")
            # KPIs["EN_13.2b"] = self.c_fec_eta - self.get_UED_cooling(self.future_scenario)
            # KPIs["EN_13.2bR"] = self.c_fec_etaR - self.get_UED_cooling(self.future_scenario, use="R")
            # KPIs["EN_13.2bT"] = self.c_fec_etaT - self.get_UED_cooling(self.future_scenario, use="T")
            try:
                KPIs["EN_13.3"] = (KPIs["EN_13.2"] / KPIs["EN_13.1"] - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3"] = "Nan"
            try:
                KPIs["EN_13.3R"] = (KPIs["EN_13.2R"] / KPIs["EN_13.1R"] - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3R"] = "Nan"
            try:
                KPIs["EN_13.3T"] = (KPIs["EN_13.2T"] / KPIs["EN_13.1T"] - 1) * 100
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_13.3T"] = "Nan"
            # try:
            # KPIs["EN_13.3b"] = ((KPIs["EN_13.2b"] - KPIs["EN_13.1b"]) / KPIs["EN_13.1b"])*100
            # except (ZeroDivisionError, TypeError) as e:
            # KPIs["EN_13.3b"] = "Nan"
            # try:
            # KPIs["EN_13.3bR"] = ((KPIs["EN_13.2bR"] - KPIs["EN_13.1bR"]) / KPIs["EN_13.1bR"]) * 100
            # except (ZeroDivisionError, TypeError) as e:
            # KPIs["EN_13.3bR"] = "Nan"
            # try:
            # KPIs["EN_13.3bT"] = ((KPIs["EN_13.2bT"] - KPIs["EN_13.1bT"]) / KPIs["EN_13.1bT"]) * 100
            # except (ZeroDivisionError, TypeError) as e:
            # KPIs["EN_13.3bT"] = "Nan"
            try:
                KPIs["EN_14.2"] = round((self.fecDistrict_DHN / self.h_length), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2"] = "Nan"
            try:
                KPIs["EN_14.2R"] = round((self.fecDistrictR_DHN / self.h_length), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2R"] = "Nan"
            try:
                KPIs["EN_14.2T"] = round((self.fecDistrictT_DHN / self.h_length), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.2T"] = "Nan"
            try:
                KPIs["EN_14.3"] = "{:.2f}".format(round((KPIs["EN_14.2"] / KPIs["EN_14.1"] - 1) * 100))
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3"] = "Nan"
            try:
                KPIs["EN_14.3R"] = "{:.2f}".format(round((KPIs["EN_14.2R"] / KPIs["EN_14.1R"] - 1) * 100))
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3R"] = "Nan"
            try:
                KPIs["EN_14.3T"] = "{:.2f}".format(round((KPIs["EN_14.2T"] / KPIs["EN_14.1T"] - 1) * 100))
            except (ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.3T"] = "Nan"
            try:
                KPIs["EN_15.2"] = self.YEOHbase
            except:
                KPIs["EN_15.2"] = -274
            try:
                KPIs["EN_15.3"] = (KPIs["EN_15.2"] / KPIs["EN_15.1"] - 1) * 100
            except:
                KPIs["EN_15.3"] = "Nan"
            fec = [KPIs["EN_2.3_s" + str(i)] for i in range(len(self.sourceName))]
            fecR = [KPIs["EN_2.3R_s" + str(i)] for i in range(len(self.sourceName))]
            fecT = [KPIs["EN_2.3T_s" + str(i)] for i in range(len(self.sourceName))]
            KPIs["ENV_1.5"] = self.get_t_pollutant_future(fec, self.pollutant_colum_index["CO2"])
            KPIs["ENV_1.5R"] = self.get_t_pollutant_future(fecR, self.pollutant_colum_index["CO2"])
            KPIs["ENV_1.5T"] = self.get_t_pollutant_future(fecT, self.pollutant_colum_index["CO2"])
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
                KPIs["ENV_1.1"] = ((KPIs["ENV_1.5"] - KPIs["ENV_1.3"]) / KPIs["ENV_1.3"]) * 100
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
                KPIs["ENV_1.2"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["CO2"])
            except TypeError:
                KPIs["ENV_1.2"] = "Nan"
            try:
                KPIs["ENV_1.2R"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["CO2"], type="R")
            except TypeError:
                KPIs["ENV_1.2R"] = "Nan"
            try:
                KPIs["ENV_1.2T"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["CO2"], type="T")
            except TypeError:
                KPIs["ENV_1.2T"] = "Nan"

            KPIs["ENV_2.3"] = self.get_t_pollutant_future(fec, self.pollutant_colum_index["NOx"])
            KPIs["ENV_2.3R"] = self.get_t_pollutant_future(fecR, self.pollutant_colum_index["NOx"])
            KPIs["ENV_2.3T"] = self.get_t_pollutant_future(fecT, self.pollutant_colum_index["NOx"])
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
                KPIs["ENV_2.5"] = ((KPIs["ENV_2.3"] - KPIs["ENV_2.1"]) / KPIs["ENV_2.1"]) * 100
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
                KPIs["ENV_2.6"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["NOx"])
            except TypeError:
                KPIs["ENV_2.6"] = "Nan"
            try:
                KPIs["ENV_2.6R"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["NOx"], type="R")
            except TypeError:
                KPIs["ENV_2.6R"] = "Nan"
            try:
                KPIs["ENV_2.6T"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["NOx"], type="T")
            except TypeError:
                KPIs["ENV_2.6T"] = "Nan"

            KPIs["ENV_2.9"] = self.get_t_pollutant_future(fec, self.pollutant_colum_index["SOx"])
            KPIs["ENV_2.9R"] = self.get_t_pollutant_future(fecR, self.pollutant_colum_index["SOx"])
            KPIs["ENV_2.9T"] = self.get_t_pollutant_future(fecT, self.pollutant_colum_index["SOx"])
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
                KPIs["ENV_2.11"] = ((KPIs["ENV_2.9"] - KPIs["ENV_2.7"]) / KPIs["ENV_2.7"]) * 100
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
                KPIs["ENV_2.12"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["SOx"])
            except TypeError:
                KPIs["ENV_2.12"] = "Nan"
            try:
                KPIs["ENV_2.12R"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["SOx"], type="R")
            except TypeError:
                KPIs["ENV_2.12R"] = "Nan"
            try:
                KPIs["ENV_2.12T"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["SOx"], type="T")
            except TypeError:
                KPIs["ENV_2.12T"] = "Nan"

            KPIs["ENV_2.15"] = self.get_t_pollutant_future(fec, self.pollutant_colum_index["PM10"])
            KPIs["ENV_2.15R"] = self.get_t_pollutant_future(fecR, self.pollutant_colum_index["PM10"])
            KPIs["ENV_2.15T"] = self.get_t_pollutant_future(fecT, self.pollutant_colum_index["PM10"])
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
                KPIs["ENV_2.17"] = ((KPIs["ENV_2.15"] - KPIs["ENV_2.13"]) / KPIs["ENV_2.13"]) * 100
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
                KPIs["ENV_2.18"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["PM10"])
            except TypeError:
                KPIs["ENV_2.18"] = "Nan"
            try:
                KPIs["ENV_2.18R"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["PM10"], type="R")
            except TypeError:
                KPIs["ENV_2.18R"] = "Nan"
            try:
                KPIs["ENV_2.18T"] = self.get_t_pollutant_sav(KPIs, self.pollutant_colum_index["PM10"], type="T")
            except TypeError:
                KPIs["ENV_2.18T"] = "Nan"
            try:
                district_factor = self.eco_param["residential_factors"]/len(self.eco_param["residential_factors"])
            except:
                district_factor = 0.5
            self.capext, self.capextR, self.capextT = self.get_capex(self.baseline_tech_tab2, self.future_tech_tab,
                                                                     None, self.future_network_tech_tab, district_factor)
            KPIs["ECO_1.4"] = self.capext
            KPIs["ECO_1.4R"] = self.capextR
            KPIs["ECO_1.4T"] = self.capextT
            KPIs["ECO_1.1"], _, _= self.eco_1_punto_1()
            KPIs["ECO_1.1R"] = "-" # TODO check formula for RES and TER
            KPIs["ECO_1.1T"] = "-" # TODO check formula for RES and TER
            self.my_log.log("Calcolo ECO_1.2")
            KPIs["ECO_1.2"] = self.eco_uno_punto_due()
            self.my_log.log("ECO_1.2: " + str(KPIs["ECO_1.2"]))
            self.my_log.log("Calcolo ECO_12.1R")
            KPIs["ECO_1.2R"] = "-" # TODO self.eco_uno_punto_due(use="R")
            self.my_log.log("ECO_1.2R: " + str(KPIs["ECO_1.2R"]))
            self.my_log.log("Calcolo ECO_12.1T")
            KPIs["ECO_1.2T"] = "-"  # TODO self.eco_uno_punto_due(use="T")
            self.my_log.log("ECO_1.2T: " + str(KPIs["ECO_1.2T"]))

            KPIs["ECO_1.3"] = self.eco_uno_punto_tre()
            KPIs["ECO_1.3R"] = self.eco_uno_punto_tre(use="R")
            KPIs["ECO_1.3T"] = self.eco_uno_punto_tre(use="T")
            KPIs["ECO_2.2"] = self.opex
            KPIs["ECO_2.2R"] = self.opexR
            KPIs["ECO_2.2T"] = self.opexT
            KPIs["ECO_2.3"] = KPIs["ECO_2.2"] - KPIs["ECO_2.1"]
            KPIs["ECO_2.3R"] = KPIs["ECO_2.2R"] - KPIs["ECO_2.1R"]
            KPIs["ECO_2.3T"] = KPIs["ECO_2.2T"] - KPIs["ECO_2.1T"]
            KPIs["ECO_3.1"] = self.eco_3_punto_1()
            KPIs["ECO_3.1R"] = self.eco_3_punto_1(use="R")
            KPIs["ECO_3.1T"] = self.eco_3_punto_1(use="T")
            KPIs["ECO_4"] = self.eco_3_punto_2(KPIs["ENV_1.2"], use=None)
            KPIs["ECO_4R"] = self.eco_3_punto_2(KPIs["ENV_1.2R"], use="R")
            KPIs["ECO_4T"] = self.eco_3_punto_2(KPIs["ENV_1.2T"], use="T")

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

            return KPIs
            # ------------------------ ###
            # --- BASELINE KPIs!!! --- ###
            # ------------------------ ###
            # ------------------------ ###
            # --- BASELINE KPIs!!! --- ###
            # ------------------------ ###
            # ------------------------ ###
            # --- BASELINE KPIs!!! --- ###
            # ------------------------ ###
            # |||||||||||||||||||||||| ###
        else:
            self.add_networks_area_contribution(self.baseline_scenario)
            KPIs["sources"] = self.sourceName
            self.PEC_base = self.PECbaseSource(self.getPEF_source(), [self.fec_s0, self.fec_s1, self.fec_s2, self.fec_s3,
                                               self.fec_s4, self.fec_s5, self.fec_s6, self.fec_s7, self.fec_s8, self.fec_s9,
                                               self.fec_s10, self.fec_s11, self.fec_s12, self.fec_s13, self.fec_s14, self.fec_s15,
                                               self.fec_s16, self.fec_s17, self.fec_s18, self.fec_s19, self.fec_s20, self.fec_s21,
                                               self.fec_s22])
            self.PEC_baseR = self.PECbaseSource(self.getPEF_source(), [self.fecR_s0, self.fecR_s1, self.fecR_s2, self.fecR_s3,
                                                self.fecR_s4, self.fecR_s5, self.fecR_s6, self.fecR_s7, self.fecR_s8, self.fecR_s9,
                                                self.fecR_s10, self.fecR_s11, self.fecR_s12, self.fecR_s13, self.fecR_s14,
                                                self.fecR_s15, self.fecR_s16, self.fecR_s17, self.fecR_s18, self.fecR_s19,
                                                self.fecR_s20, self.fecR_s21, self.fecR_s22])
            self.PEC_baseT = self.PECbaseSource(self.getPEF_source(), [self.fecT_s0, self.fecT_s1, self.fecT_s2, self.fecT_s3,
                                                self.fecT_s4, self.fecT_s5, self.fecT_s6, self.fecT_s7, self.fecT_s8, self.fecT_s9,
                                                self.fecT_s10, self.fecT_s11, self.fecT_s12, self.fecT_s13, self.fecT_s14,
                                                self.fecT_s15, self.fecT_s16, self.fecT_s17, self.fecT_s18, self.fecT_s19,
                                                self.fecT_s20, self.fecT_s21, self.fecT_s22])

            self.PEC_baseRes = [self.PEC_base[21], self.PEC_base[3], self.PEC_base[4], self.PEC_base[5], self.PEC_base[6]]
            self.PEC_baseResR = [self.PEC_baseR[21], self.PEC_baseR[3], self.PEC_baseR[4], self.PEC_baseR[5], self.PEC_baseR[6]]
            self.PEC_baseResT = [self.PEC_baseT[21], self.PEC_baseT[3], self.PEC_baseT[4], self.PEC_baseT[5], self.PEC_baseT[6]]

            self.PEC_baseWH = [self.PEC_base[7], self.PEC_base[8], self.PEC_base[9], self.PEC_base[10], self.PEC_base[11],
                               self.PEC_base[12], self.PEC_base[13], self.PEC_base[14], self.PEC_base[15], self.PEC_base[16],
                               self.PEC_base[17], self.PEC_base[18], self.PEC_base[19], self.PEC_base[20]]
            self.PEC_baseWHR = [self.PEC_baseR[7], self.PEC_baseR[8], self.PEC_baseR[9], self.PEC_baseR[10], self.PEC_baseR[11],
                                self.PEC_baseR[12], self.PEC_baseR[13], self.PEC_baseR[14], self.PEC_baseR[15], self.PEC_baseR[16],
                                self.PEC_baseR[17], self.PEC_baseR[18], self.PEC_baseR[19], self.PEC_baseR[20]]
            self.PEC_baseWHT = [self.PEC_baseT[7], self.PEC_baseT[8], self.PEC_baseT[9], self.PEC_baseT[10], self.PEC_baseT[11],
                                self.PEC_baseT[12], self.PEC_baseT[13], self.PEC_baseT[14], self.PEC_baseT[15], self.PEC_baseT[16],
                                self.PEC_baseT[17], self.PEC_baseT[18], self.PEC_baseT[19], self.PEC_baseT[20]]

            self.PEC_baseCF = [self.PEC_base[0], self.PEC_base[1], self.PEC_base[2]]
            self.PEC_baseCFR = [self.PEC_baseR[0], self.PEC_baseR[1], self.PEC_baseR[2]]
            self.PEC_baseCFT = [self.PEC_baseT[0], self.PEC_baseT[1], self.PEC_baseT[2]]

            self.PEC_base_SUM = sum(self.PEC_base)
            self.PEC_baseR_SUM = sum(self.PEC_baseR)
            self.PEC_baseT_SUM = sum(self.PEC_baseT)

            self.PEC_baseRes_sum = sum(self.PEC_baseRes)
            self.PEC_baseResR_sum = sum(self.PEC_baseResR)
            self.PEC_baseResT_sum = sum(self.PEC_baseResT)

            self.PEC_baseWH_sum = sum(self.PEC_baseWH)
            self.PEC_baseWHR_sum = sum(self.PEC_baseWHR)
            self.PEC_baseWHT_sum = sum(self.PEC_baseWHT)

            self.PEC_baseCF_sum = sum(self.PEC_baseCF)
            self.PEC_baseCFR_sum = sum(self.PEC_baseCFR)
            self.PEC_baseCFT_sum = sum(self.PEC_baseCFT)

            self.my_log.log("self.PEC_baseWH")
            self.my_log.log(self.PEC_baseWH)
            self.my_log.log("self.PEC_baseRes")
            self.my_log.log(self.PEC_baseRes)
            self.PEC_baseRESWH_sum = sum(self.PEC_baseWH) + sum(self.PEC_baseRes)
            self.PEC_baseRESWHR_sum = sum(self.PEC_baseWHR) + sum(self.PEC_baseResR)
            self.PEC_baseRESWHT_sum = sum(self.PEC_baseWHT) + sum(self.PEC_baseResT)

            KPIs["EN_1.1"] = round(self.PEC_base_SUM, 2)
            KPIs["EN_1.1R"] = round(self.PEC_baseR_SUM, 2)
            KPIs["EN_1.1T"] = round(self.PEC_baseT_SUM, 2)
            try:
                KPIs["EN_1.2"] = round(KPIs["EN_1.1"] / self.area, 2)
                self.my_log.log("KPI EN_1.2 self.area:", self.area)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.2"] = "Nan"
            try:
                KPIs["EN_1.2R"] = round(KPIs["EN_1.1R"] / self.areaR, 2)
                self.my_log.log("KPI EN_1.2 self.areaR:", self.areaR)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.2R"] = "Nan"
            try:
                KPIs["EN_1.2T"] = round(KPIs["EN_1.1T"] / (self.area - self.areaR), 2)
                self.my_log.log("KPI EN_1.2 (self.area - self.areaR):", (self.area - self.areaR))
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_1.2T"] = "Nan"

            KPIs["EN_2.1"] = round(self.fec, 2)

            #################
            ########ADD FEC FOR SOURCES
            #################
            KPIs["EN_2.1"] = "Nan"
            KPIs["EN_2.1R"] = "Nan"
            KPIs["EN_2.1T"] = "Nan"
            KPIs["EN_2.2"] = "Nan"
            KPIs["EN_2.2R"] = "Nan"
            KPIs["EN_2.2T"] = "Nan"
            KPIs["EN_2.1_s0"] = round(self.fec_s0, 2)
            KPIs["EN_2.1_s1"] = round(self.fec_s1, 2)
            KPIs["EN_2.1_s2"] = round(self.fec_s2, 2)
            KPIs["EN_2.1_s3"] = round(self.fec_s3, 2)
            KPIs["EN_2.1_s4"] = round(self.fec_s4, 2)
            KPIs["EN_2.1_s5"] = round(self.fec_s5, 2)
            KPIs["EN_2.1_s6"] = round(self.fec_s6, 2)
            KPIs["EN_2.1_s7"] = round(self.fec_s7, 2)
            KPIs["EN_2.1_s8"] = round(self.fec_s8, 2)
            KPIs["EN_2.1_s9"] = round(self.fec_s9, 2)
            KPIs["EN_2.1_s10"] = round(self.fec_s10, 2)
            KPIs["EN_2.1_s11"] = round(self.fec_s11, 2)
            KPIs["EN_2.1_s12"] = round(self.fec_s12, 2)
            KPIs["EN_2.1_s13"] = round(self.fec_s13, 2)
            KPIs["EN_2.1_s14"] = round(self.fec_s14, 2)
            KPIs["EN_2.1_s15"] = round(self.fec_s15, 2)
            KPIs["EN_2.1_s16"] = round(self.fec_s16, 2)
            KPIs["EN_2.1_s17"] = round(self.fec_s17, 2)
            KPIs["EN_2.1_s18"] = round(self.fec_s18, 2)
            KPIs["EN_2.1_s19"] = round(self.fec_s19, 2)
            KPIs["EN_2.1_s20"] = round(self.fec_s20, 2)
            KPIs["EN_2.1_s21"] = round(self.fec_s21, 2)
            KPIs["EN_2.1_s22"] = round(self.fec_s22, 2)

            # ..............

            KPIs["EN_2.1R_s0"] = round(self.fecR_s0, 2)
            KPIs["EN_2.1R_s1"] = round(self.fecR_s1, 2)
            KPIs["EN_2.1R_s2"] = round(self.fecR_s2, 2)
            KPIs["EN_2.1R_s3"] = round(self.fecR_s3, 2)
            KPIs["EN_2.1R_s4"] = round(self.fecR_s4, 2)
            KPIs["EN_2.1R_s5"] = round(self.fecR_s5, 2)
            KPIs["EN_2.1R_s6"] = round(self.fecR_s6, 2)
            KPIs["EN_2.1R_s7"] = round(self.fecR_s7, 2)
            KPIs["EN_2.1R_s8"] = round(self.fecR_s8, 2)
            KPIs["EN_2.1R_s9"] = round(self.fecR_s9, 2)
            KPIs["EN_2.1R_s10"] = round(self.fecR_s10, 2)
            KPIs["EN_2.1R_s11"] = round(self.fecR_s11, 2)
            KPIs["EN_2.1R_s12"] = round(self.fecR_s12, 2)
            KPIs["EN_2.1R_s13"] = round(self.fecR_s13, 2)
            KPIs["EN_2.1R_s14"] = round(self.fecR_s14, 2)
            KPIs["EN_2.1R_s15"] = round(self.fecR_s15, 2)
            KPIs["EN_2.1R_s16"] = round(self.fecR_s16, 2)
            KPIs["EN_2.1R_s17"] = round(self.fecR_s17, 2)
            KPIs["EN_2.1R_s18"] = round(self.fecR_s18, 2)
            KPIs["EN_2.1R_s19"] = round(self.fecR_s19, 2)
            KPIs["EN_2.1R_s20"] = round(self.fecR_s20, 2)
            KPIs["EN_2.1R_s21"] = round(self.fecR_s21, 2)
            KPIs["EN_2.1R_s22"] = round(self.fecR_s22, 2)

            # ..............
            KPIs["EN_2.1T_s0"] = round(self.fecT_s0, 2)
            KPIs["EN_2.1T_s1"] = round(self.fecT_s1, 2)
            KPIs["EN_2.1T_s2"] = round(self.fecT_s2, 2)
            KPIs["EN_2.1T_s3"] = round(self.fecT_s3, 2)
            KPIs["EN_2.1T_s4"] = round(self.fecT_s4, 2)
            KPIs["EN_2.1T_s5"] = round(self.fecT_s5, 2)
            KPIs["EN_2.1T_s6"] = round(self.fecT_s6, 2)
            KPIs["EN_2.1T_s7"] = round(self.fecT_s7, 2)
            KPIs["EN_2.1T_s8"] = round(self.fecT_s8, 2)
            KPIs["EN_2.1T_s9"] = round(self.fecT_s9, 2)
            KPIs["EN_2.1T_s10"] = round(self.fecT_s10, 2)
            KPIs["EN_2.1T_s11"] = round(self.fecT_s11, 2)
            KPIs["EN_2.1T_s12"] = round(self.fecT_s12, 2)
            KPIs["EN_2.1T_s13"] = round(self.fecT_s13, 2)
            KPIs["EN_2.1T_s14"] = round(self.fecT_s14, 2)
            KPIs["EN_2.1T_s15"] = round(self.fecT_s15, 2)
            KPIs["EN_2.1T_s16"] = round(self.fecT_s16, 2)
            KPIs["EN_2.1T_s17"] = round(self.fecT_s17, 2)
            KPIs["EN_2.1T_s18"] = round(self.fecT_s18, 2)
            KPIs["EN_2.1T_s19"] = round(self.fecT_s19, 2)
            KPIs["EN_2.1T_s20"] = round(self.fecT_s20, 2)
            KPIs["EN_2.1T_s21"] = round(self.fecT_s21, 2)
            KPIs["EN_2.1T_s22"] = round(self.fecT_s22, 2)

            try:
                KPIs["EN_2.2_s0"] = round(self.fec_s0 / self.area, 2)
                self.my_log.log("EN_2.2_s1 self.fec_s1:", str(self.fec_s1))
                self.my_log.log("EN_2.2_s1 self.area:", str(self.area))
                self.my_log.log("EN_2.2_s1 self.fec_s1 / self.area:", str(self.fec_s1 / self.area))
                self.my_log.log("EN_2.2_s1 round(self.fec_s1 / self.area, 2):", str(round(self.fec_s1 / self.area, 2)))
                KPIs["EN_2.2_s1"] = round(self.fec_s1 / self.area, 2)
                KPIs["EN_2.2_s2"] = round(self.fec_s2 / self.area, 2)
                KPIs["EN_2.2_s3"] = round(self.fec_s3 / self.area, 2)
                KPIs["EN_2.2_s4"] = round(self.fec_s4 / self.area, 2)
                KPIs["EN_2.2_s5"] = round(self.fec_s5 / self.area, 2)
                KPIs["EN_2.2_s6"] = round(self.fec_s6 / self.area, 2)
                KPIs["EN_2.2_s7"] = round(self.fec_s7 / self.area, 2)
                KPIs["EN_2.2_s8"] = round(self.fec_s8 / self.area, 2)
                KPIs["EN_2.2_s9"] = round(self.fec_s9 / self.area, 2)
                KPIs["EN_2.2_s10"] = round(self.fec_s10 / self.area, 2)
                KPIs["EN_2.2_s11"] = round(self.fec_s11 / self.area, 2)
                KPIs["EN_2.2_s12"] = round(self.fec_s12 / self.area, 2)
                KPIs["EN_2.2_s13"] = round(self.fec_s13 / self.area, 2)
                KPIs["EN_2.2_s14"] = round(self.fec_s14 / self.area, 2)
                KPIs["EN_2.2_s15"] = round(self.fec_s15 / self.area, 2)
                KPIs["EN_2.2_s16"] = round(self.fec_s16 / self.area, 2)
                KPIs["EN_2.2_s17"] = round(self.fec_s17 / self.area, 2)
                KPIs["EN_2.2_s18"] = round(self.fec_s18 / self.area, 2)
                KPIs["EN_2.2_s19"] = round(self.fec_s19 / self.area, 2)
                KPIs["EN_2.2_s20"] = round(self.fec_s20 / self.area, 2)
                KPIs["EN_2.2_s21"] = round(self.fec_s21 / self.area, 2)
                KPIs["EN_2.2_s22"] = round(self.fec_s22 / self.area, 2)

            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.2"] = "Nan"
            try:
                KPIs["EN_2.2R_s0"] = round(self.fecR_s0 / self.areaR, 2)
                KPIs["EN_2.2R_s1"] = round(self.fecR_s1 / self.areaR, 2)
                KPIs["EN_2.2R_s2"] = round(self.fecR_s2 / self.areaR, 2)
                KPIs["EN_2.2R_s3"] = round(self.fecR_s3 / self.areaR, 2)
                KPIs["EN_2.2R_s4"] = round(self.fecR_s4 / self.areaR, 2)
                KPIs["EN_2.2R_s5"] = round(self.fecR_s5 / self.areaR, 2)
                KPIs["EN_2.2R_s6"] = round(self.fecR_s6 / self.areaR, 2)
                KPIs["EN_2.2R_s7"] = round(self.fecR_s7 / self.areaR, 2)
                KPIs["EN_2.2R_s8"] = round(self.fecR_s8 / self.areaR, 2)
                KPIs["EN_2.2R_s9"] = round(self.fecR_s9 / self.areaR, 2)
                KPIs["EN_2.2R_s10"] = round(self.fecR_s10 / self.areaR, 2)
                KPIs["EN_2.2R_s11"] = round(self.fecR_s11 / self.areaR, 2)
                KPIs["EN_2.2R_s12"] = round(self.fecR_s12 / self.areaR, 2)
                KPIs["EN_2.2R_s13"] = round(self.fecR_s13 / self.areaR, 2)
                KPIs["EN_2.2R_s14"] = round(self.fecR_s14 / self.areaR, 2)
                KPIs["EN_2.2R_s15"] = round(self.fecR_s15 / self.areaR, 2)
                KPIs["EN_2.2R_s16"] = round(self.fecR_s16 / self.areaR, 2)
                KPIs["EN_2.2R_s17"] = round(self.fecR_s17 / self.areaR, 2)
                KPIs["EN_2.2R_s18"] = round(self.fecR_s18 / self.areaR, 2)
                KPIs["EN_2.2R_s19"] = round(self.fecR_s19 / self.areaR, 2)
                KPIs["EN_2.2R_s20"] = round(self.fecR_s20 / self.areaR, 2)
                KPIs["EN_2.2R_s21"] = round(self.fecR_s21 / self.areaR, 2)
                KPIs["EN_2.2R_s22"] = round(self.fecR_s22 / self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.2R"] = "Nan"
            tmp_area = self.area - self.areaR
            try:
                KPIs["EN_2.2T_s0"] = round(self.fecT_s0 / tmp_area, 2)
                KPIs["EN_2.2T_s1"] = round(self.fecT_s1 / tmp_area, 2)
                KPIs["EN_2.2T_s2"] = round(self.fecT_s2 / tmp_area, 2)
                KPIs["EN_2.2T_s3"] = round(self.fecT_s3 / tmp_area, 2)
                KPIs["EN_2.2T_s4"] = round(self.fecT_s4 / tmp_area, 2)
                KPIs["EN_2.2T_s5"] = round(self.fecT_s5 / tmp_area, 2)
                KPIs["EN_2.2T_s6"] = round(self.fecT_s6 / tmp_area, 2)
                KPIs["EN_2.2T_s7"] = round(self.fecT_s7 / tmp_area, 2)
                KPIs["EN_2.2T_s8"] = round(self.fecT_s8 / tmp_area, 2)
                KPIs["EN_2.2T_s9"] = round(self.fecT_s9 / tmp_area, 2)
                KPIs["EN_2.2T_s10"] = round(self.fecT_s10 / tmp_area, 2)
                KPIs["EN_2.2T_s11"] = round(self.fecT_s11 / tmp_area, 2)
                KPIs["EN_2.2T_s12"] = round(self.fecT_s12 / tmp_area, 2)
                KPIs["EN_2.2T_s13"] = round(self.fecT_s13 / tmp_area, 2)
                KPIs["EN_2.2T_s14"] = round(self.fecT_s14 / tmp_area, 2)
                KPIs["EN_2.2T_s15"] = round(self.fecT_s15 / tmp_area, 2)
                KPIs["EN_2.2T_s16"] = round(self.fecT_s16 / tmp_area, 2)
                KPIs["EN_2.2T_s17"] = round(self.fecT_s17 / tmp_area, 2)
                KPIs["EN_2.2T_s18"] = round(self.fecT_s18 / tmp_area, 2)
                KPIs["EN_2.2T_s19"] = round(self.fecT_s19 / tmp_area, 2)
                KPIs["EN_2.2T_s20"] = round(self.fecT_s20 / tmp_area, 2)
                KPIs["EN_2.2T_s21"] = round(self.fecT_s21 / tmp_area, 2)
                KPIs["EN_2.2T_s22"] = round(self.fecT_s22 / tmp_area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_2.2T"] = "Nan"

            self.FECadjBase_s0 = KPIs["EN_2.1_s0"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s1 = KPIs["EN_2.1_s1"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s2 = KPIs["EN_2.1_s2"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s3 = KPIs["EN_2.1_s3"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s4 = KPIs["EN_2.1_s4"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s5 = KPIs["EN_2.1_s5"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s6 = KPIs["EN_2.1_s6"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s7 = KPIs["EN_2.1_s7"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s8 = KPIs["EN_2.1_s8"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s9 = KPIs["EN_2.1_s9"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s10 = KPIs["EN_2.1_s10"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s11 = KPIs["EN_2.1_s11"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s12 = KPIs["EN_2.1_s12"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s13 = KPIs["EN_2.1_s13"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s14 = KPIs["EN_2.1_s14"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s15 = KPIs["EN_2.1_s15"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s16 = KPIs["EN_2.1_s16"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s17 = KPIs["EN_2.1_s17"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s18 = KPIs["EN_2.1_s18"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s19 = KPIs["EN_2.1_s19"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s20 = KPIs["EN_2.1_s20"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s21 = KPIs["EN_2.1_s21"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBase_s22 = KPIs["EN_2.1_s22"] * (1 + self.eco_param["demo_factor"])

            self.FECadjBaseR_s0 = KPIs["EN_2.1R_s0"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s1 = KPIs["EN_2.1R_s1"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s2 = KPIs["EN_2.1R_s2"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s3 = KPIs["EN_2.1R_s3"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s4 = KPIs["EN_2.1R_s4"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s5 = KPIs["EN_2.1R_s5"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s6 = KPIs["EN_2.1R_s6"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s7 = KPIs["EN_2.1R_s7"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s8 = KPIs["EN_2.1R_s8"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s9 = KPIs["EN_2.1R_s9"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s10 = KPIs["EN_2.1R_s10"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s11 = KPIs["EN_2.1R_s11"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s12 = KPIs["EN_2.1R_s12"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s13 = KPIs["EN_2.1R_s13"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s14 = KPIs["EN_2.1R_s14"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s15 = KPIs["EN_2.1R_s15"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s16 = KPIs["EN_2.1R_s16"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s17 = KPIs["EN_2.1R_s17"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s18 = KPIs["EN_2.1R_s18"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s19 = KPIs["EN_2.1R_s19"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s20 = KPIs["EN_2.1R_s20"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s21 = KPIs["EN_2.1R_s21"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseR_s22 = KPIs["EN_2.1R_s22"] * (1 + self.eco_param["demo_factor"])

            self.FECadjBaseT_s0 = KPIs["EN_2.1T_s0"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s1 = KPIs["EN_2.1T_s1"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s2 = KPIs["EN_2.1T_s2"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s3 = KPIs["EN_2.1T_s3"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s4 = KPIs["EN_2.1T_s4"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s5 = KPIs["EN_2.1T_s5"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s6 = KPIs["EN_2.1T_s6"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s7 = KPIs["EN_2.1T_s7"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s8 = KPIs["EN_2.1T_s8"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s9 = KPIs["EN_2.1T_s9"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s10 = KPIs["EN_2.1T_s10"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s11 = KPIs["EN_2.1T_s11"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s12 = KPIs["EN_2.1T_s12"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s13 = KPIs["EN_2.1T_s13"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s14 = KPIs["EN_2.1T_s14"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s15 = KPIs["EN_2.1T_s15"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s16 = KPIs["EN_2.1T_s16"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s17 = KPIs["EN_2.1T_s17"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s18 = KPIs["EN_2.1T_s18"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s19 = KPIs["EN_2.1T_s19"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s20 = KPIs["EN_2.1T_s20"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s21 = KPIs["EN_2.1T_s21"] * (1 + self.eco_param["demo_factor"])
            self.FECadjBaseT_s22 = KPIs["EN_2.1T_s22"] * (1 + self.eco_param["demo_factor"])

            self.FECadjBase = [self.FECadjBase_s0, self.FECadjBase_s1, self.FECadjBase_s2, self.FECadjBase_s3,
                               self.FECadjBase_s4, self.FECadjBase_s5, self.FECadjBase_s6, self.FECadjBase_s7,
                               self.FECadjBase_s8, self.FECadjBase_s9, self.FECadjBase_s10, self.FECadjBase_s11,
                               self.FECadjBase_s12, self.FECadjBase_s13, self.FECadjBase_s14, self.FECadjBase_s15,
                               self.FECadjBase_s16, self.FECadjBase_s17, self.FECadjBase_s18, self.FECadjBase_s19,
                               self.FECadjBase_s20, self.FECadjBase_s21, self.FECadjBase_s22]
            self.FECadjBaseR= [self.FECadjBaseR_s0, self.FECadjBaseR_s1, self.FECadjBaseR_s2, self.FECadjBaseR_s3,
                               self.FECadjBaseR_s4, self.FECadjBaseR_s5, self.FECadjBaseR_s6, self.FECadjBaseR_s7,
                               self.FECadjBaseR_s8, self.FECadjBaseR_s9, self.FECadjBaseR_s10, self.FECadjBaseR_s11,
                               self.FECadjBaseR_s12, self.FECadjBaseR_s13, self.FECadjBaseR_s14, self.FECadjBaseR_s15,
                               self.FECadjBaseR_s16, self.FECadjBaseR_s17, self.FECadjBaseR_s18, self.FECadjBaseR_s19,
                               self.FECadjBaseR_s20, self.FECadjBaseR_s21, self.FECadjBaseR_s22]
            self.FECadjBaseT= [self.FECadjBaseT_s0, self.FECadjBaseT_s1, self.FECadjBaseT_s2, self.FECadjBaseT_s3,
                               self.FECadjBaseT_s4, self.FECadjBaseT_s5, self.FECadjBaseT_s6, self.FECadjBaseT_s7,
                               self.FECadjBaseT_s8, self.FECadjBaseT_s9, self.FECadjBaseT_s10, self.FECadjBaseT_s11,
                               self.FECadjBaseT_s12, self.FECadjBaseT_s13, self.FECadjBaseT_s14, self.FECadjBaseT_s15,
                               self.FECadjBaseT_s16, self.FECadjBaseT_s17, self.FECadjBaseT_s18, self.FECadjBaseT_s19,
                               self.FECadjBaseT_s20, self.FECadjBaseT_s21, self.FECadjBaseT_s22]

            pef = self.getPEF_source()
            self.pecADJ_baseline_s0 = self.FECadjBase_s0 * pef[0]
            self.pecADJ_baseline_s1 = self.FECadjBase_s1 * pef[1]
            self.pecADJ_baseline_s2 = self.FECadjBase_s2 * pef[2]
            self.pecADJ_baseline_s3 = self.FECadjBase_s3 * pef[3]
            self.pecADJ_baseline_s4 = self.FECadjBase_s4 * pef[4]
            self.pecADJ_baseline_s5 = self.FECadjBase_s5 * pef[5]
            self.pecADJ_baseline_s6 = self.FECadjBase_s6 * pef[6]
            self.pecADJ_baseline_s7 = self.FECadjBase_s7 * pef[7]
            self.pecADJ_baseline_s8 = self.FECadjBase_s8 * pef[8]
            self.pecADJ_baseline_s9 = self.FECadjBase_s9 * pef[9]
            self.pecADJ_baseline_s10 = self.FECadjBase_s10 * pef[10]
            self.pecADJ_baseline_s11 = self.FECadjBase_s11 * pef[11]
            self.pecADJ_baseline_s12 = self.FECadjBase_s12 * pef[12]
            self.pecADJ_baseline_s13 = self.FECadjBase_s13 * pef[13]
            self.pecADJ_baseline_s14 = self.FECadjBase_s14 * pef[14]
            self.pecADJ_baseline_s15 = self.FECadjBase_s15 * pef[15]
            self.pecADJ_baseline_s16 = self.FECadjBase_s16 * pef[16]
            self.pecADJ_baseline_s17 = self.FECadjBase_s17 * pef[17]
            self.pecADJ_baseline_s18 = self.FECadjBase_s18 * pef[18]
            self.pecADJ_baseline_s19 = self.FECadjBase_s19 * pef[19]
            self.pecADJ_baseline_s20 = self.FECadjBase_s20 * pef[20]
            self.pecADJ_baseline_s21 = self.FECadjBase_s21 * pef[21]
            self.pecADJ_baseline_s22 = self.FECadjBase_s22 * pef[22]

            KPIs["pecADG_baseline"] = [self.pecADJ_baseline_s0, self.pecADJ_baseline_s1, self.pecADJ_baseline_s2,
                                       self.pecADJ_baseline_s3, self.pecADJ_baseline_s4, self.pecADJ_baseline_s5,
                                       self.pecADJ_baseline_s6, self.pecADJ_baseline_s7, self.pecADJ_baseline_s8,
                                       self.pecADJ_baseline_s9, self.pecADJ_baseline_s10, self.pecADJ_baseline_s11,
                                       self.pecADJ_baseline_s12, self.pecADJ_baseline_s13, self.pecADJ_baseline_s14,
                                       self.pecADJ_baseline_s15, self.pecADJ_baseline_s16, self.pecADJ_baseline_s17,
                                       self.pecADJ_baseline_s18, self.pecADJ_baseline_s19, self.pecADJ_baseline_s20,
                                       self.pecADJ_baseline_s21, self.pecADJ_baseline_s22]

            KPIs["pecADG_baselineR"] = [self.FECadjBaseR_s0 * pef[0], self.FECadjBaseR_s1 * pef[1], self.FECadjBaseR_s2 * pef[2],
                                        self.FECadjBaseR_s3 * pef[3], self.FECadjBaseR_s4 * pef[4], self.FECadjBaseR_s5 * pef[5],
                                        self.FECadjBaseR_s6 * pef[6], self.FECadjBaseR_s7 * pef[7], self.FECadjBaseR_s8 * pef[8],
                                        self.FECadjBaseR_s9 * pef[9], self.FECadjBaseR_s10 * pef[10], self.FECadjBaseR_s11 * pef[11],
                                        self.FECadjBaseR_s12 * pef[12], self.FECadjBaseR_s13 * pef[13], self.FECadjBaseR_s14 * pef[14],
                                        self.FECadjBaseR_s15 * pef[15], self.FECadjBaseR_s16 * pef[16], self.FECadjBaseR_s17 * pef[17],
                                        self.FECadjBaseR_s18 * pef[18], self.FECadjBaseR_s19 * pef[19], self.FECadjBaseR_s20 * pef[20],
                                        self.FECadjBaseR_s21 * pef[21], self.FECadjBaseR_s22 * pef[22]]

            KPIs["pecADG_baselineT"] = [self.FECadjBaseT_s0 * pef[0], self.FECadjBaseT_s1 * pef[1], self.FECadjBaseT_s2 * pef[2],
                                        self.FECadjBaseT_s3 * pef[3], self.FECadjBaseT_s4 * pef[4], self.FECadjBaseT_s5 * pef[5],
                                        self.FECadjBaseT_s6 * pef[6], self.FECadjBaseT_s7 * pef[7], self.FECadjBaseT_s8 * pef[8],
                                        self.FECadjBaseT_s9 * pef[9], self.FECadjBaseT_s10 * pef[10], self.FECadjBaseT_s11 * pef[11],
                                        self.FECadjBaseT_s12 * pef[12], self.FECadjBaseT_s13 * pef[13], self.FECadjBaseT_s14 * pef[14],
                                        self.FECadjBaseT_s15 * pef[15], self.FECadjBaseT_s16 * pef[16], self.FECadjBaseT_s17 * pef[17],
                                        self.FECadjBaseT_s18 * pef[18], self.FECadjBaseT_s19 * pef[19], self.FECadjBaseT_s20 * pef[20],
                                        self.FECadjBaseT_s21 * pef[21], self.FECadjBaseT_s22 * pef[22]]

            KPIs["EN_3.1"] = round(self.get_UED(self.baseline_scenario) + self.get_UED_networks(self.baseline_scenario, n_type=None, use=None), 2)
            KPIs["EN_3.1R"] = round(self.get_UED(self.baseline_scenario, use="R") + self.get_UED_networks(self.baseline_scenario, n_type=None, use="R"), 2)
            KPIs["EN_3.1T"] = round(self.get_UED(self.baseline_scenario, use="T") + self.get_UED_networks(self.baseline_scenario, n_type=None, use="T"), 2)
            try:
                KPIs["EN_3.2"] = round(KPIs["EN_3.1"] / self.area, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.2"] = "Nan"
            try:
                KPIs["EN_3.2R"] = round(KPIs["EN_3.1R"] / self.areaR, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.2R"] = "Nan"
            try:
                KPIs["EN_3.2T"] = round(KPIs["EN_3.1T"] / (self.area - self.areaR), 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_3.2T"] = "Nan"
            KPIs["EN_4.1"] = round(self.PEC_baseRes_sum, 2)
            KPIs["EN_4.1T"] = round(self.PEC_baseResT_sum, 2)
            KPIs["EN_4.1R"] = round(self.PEC_baseResR_sum, 2)
            try:
                KPIs["EN_4.2"] = KPIs["EN_4.1"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.2"] = "Nan"
            try:
                KPIs["EN_4.2R"] = KPIs["EN_4.1R"] / KPIs["EN_1.1R"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.2R"] = "Nan"
            try:
                KPIs["EN_4.2T"] = KPIs["EN_4.1T"] / KPIs["EN_1.1T"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_4.2T"] = "Nan"
            KPIs["EN_5.1"] = round(self.PEC_baseWH_sum, 2)
            KPIs["EN_5.1R"] = round(self.PEC_baseWHR_sum, 2)
            KPIs["EN_5.1T"] = round(self.PEC_baseWHT_sum, 2)
            try:
                KPIs["EN_5.2"] = KPIs["EN_5.1"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.2"] = "Nan"
            try:
                KPIs["EN_5.2R"] = KPIs["EN_5.1R"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.2R"] = "Nan"
            try:
                KPIs["EN_5.2T"] = KPIs["EN_5.1T"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_5.2T"] = "Nan"
            KPIs["EN_6.1"] = round(self.PEC_baseCF_sum, 2)
            KPIs["EN_6.1R"] = round(self.PEC_baseCFR_sum, 2)
            KPIs["EN_6.1T"] = round(self.PEC_baseCFT_sum, 2)
            try:
                KPIs["EN_6.2"] = KPIs["EN_6.1"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.2"] = "Nan"
            try:
                KPIs["EN_6.2R"] = KPIs["EN_6.1R"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.2R"] = "Nan"
            try:
                KPIs["EN_6.2T"] = KPIs["EN_6.1T"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_6.2T"] = "Nan"
            KPIs["EN_7.1"] = round(self.PEC_baseCF_sum, 2)
            KPIs["EN_7.1R"] = round(self.PEC_baseCFR_sum, 2)
            KPIs["EN_7.1T"] = round(self.PEC_baseCFT_sum, 2)
            try:
                KPIs["EN_7.2"] = KPIs["EN_7.1"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.2"] = "Nan"
            try:
                KPIs["EN_7.2R"] = KPIs["EN_7.1R"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.2R"] = "Nan"
            try:
                KPIs["EN_7.2T"] = KPIs["EN_7.1T"] / KPIs["EN_1.1"] * 100
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_7.2T"] = "Nan"
            try:
                KPIs["EN_9.1"] = round((self.get_UED_cooling(self.baseline_scenario) / self.get_total_UED_cooling(self.baseline_scenario)) * 100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.1"] = "Nan"
            try:
                KPIs["EN_9.1R"] = round((self.get_UED_cooling(self.baseline_scenario, use="R") / self.get_total_UED_cooling(self.baseline_scenario, use="R")) * 100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.1R"] = "Nan"
            try:
                KPIs["EN_9.1T"] = round((self.get_UED_cooling(self.baseline_scenario, use="T") / self.get_total_UED_cooling(self.baseline_scenario, use="T")) * 100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_9.1T"] = "Nan"
            KPIs["EN_11.2"] = round(100 * self.PEC_base[6] / self.PEC_base_SUM, 2)
            KPIs["EN_11.2R"] = round(100 * self.PEC_baseR[6] / self.PEC_baseR_SUM, 2)
            KPIs["EN_11.2T"] = round(100 * self.PEC_baseT[6] / self.PEC_baseT_SUM, 2)

            KPIs["EN_11.1"] = self.fec_s6
            KPIs["EN_11.1R"] = self.fecR_s6
            KPIs["EN_11.1T"] = self.fecT_s6

            try:
                KPIs["EN_12.1"] = round(self.PEC_baseRESWH_sum / KPIs["EN_1.1"] * 100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.1"] = "Nan"
            try:
                KPIs["EN_12.1R"] = round(self.PEC_baseRESWHR_sum / KPIs["EN_1.1R"] * 100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.1R"] = "Nan"
            try:
                KPIs["EN_12.1T"] = round(self.PEC_baseRESWHT_sum / KPIs["EN_1.1T"] * 100, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_12.1T"] = "Nan"

            KPIs["EN_12.1_baseline"] = self.PEC_baseRESWH_sum
            KPIs["EN_12.1_baselineR"] = self.PEC_baseRESWHR_sum
            KPIs["EN_12.1_baselineT"] = self.PEC_baseRESWHT_sum

            try:
                eta_DHN_average = sum(self.eco_param["eta_DHN"])/len(self.eco_param["eta_DHN"])
            except ZeroDivisionError:
                eta_DHN_average = 0.0
            try:
                eta_DCN_average = sum(self.eco_param["eta_DCN"]) / len(self.eco_param["eta_DCN"])
            except ZeroDivisionError:
                eta_DCN_average = 0.0

            self.my_log.log("self.eco_param[\"eta_DHN\"]: " + str(self.eco_param["eta_DHN"]))
            self.my_log.log("self.eco_param[\"eta_DCN\"]: " + str(self.eco_param["eta_DCN"]))
            self.my_log.log("eta_DHN_average: " + str(eta_DHN_average))
            self.my_log.log("eta_DCN_average: " + str(eta_DCN_average))
            try:
                value = self.get_UED_networks(self.baseline_scenario, "DHN")
                self.my_log.log("EN_13.1 self.get_UED_networks(self.baseline_scenario, \"DHN\"):", str(value))
                self.my_log.log("EN_13.1 ((1 / eta_DHN_average) - 1)):", str(((1 / eta_DHN_average) - 1)))
                KPIs["EN_13.1"] = round(self.get_UED_networks(self.baseline_scenario, "DHN") * ((1 / eta_DHN_average) - 1), 2)
            except ZeroDivisionError:
                KPIs["EN_13.1"] = "-"
            try:
                KPIs["EN_13.1R"] = round(self.get_UED_networks(self.baseline_scenario, "DHN", use="R") * ((1 / eta_DHN_average) - 1), 2)
            except ZeroDivisionError:
                KPIs["EN_13.1R"] = "-"
            try:
                KPIs["EN_13.1T"] = round(self.get_UED_networks(self.baseline_scenario, "DHN", use="T") * ((1 / eta_DHN_average) - 1), 2)
            except ZeroDivisionError:
                KPIs["EN_13.1T"] = "-"
            try:
                KPIs["EN_13.1b"] = round(self.get_UED_networks(self.baseline_scenario, "DCN") * ((1 / eta_DCN_average) - 1), 2)
            except ZeroDivisionError:
                KPIs["EN_13.1b"] = "-"
            try:
                KPIs["EN_13.1bR"] = round(self.get_UED_networks(self.baseline_scenario, "DCN", use="R") * ((1 / eta_DCN_average) - 1), 2)
            except ZeroDivisionError:
                KPIs["EN_13.1bR"] = "-"
            try:
                KPIs["EN_13.1bT"] = round(self.get_UED_networks(self.baseline_scenario, "DCN", use="T") * ((1 / eta_DCN_average) - 1), 2)
            except ZeroDivisionError:
                KPIs["EN_13.1bT"] = "-"
            try:
                KPIs["EN_14.1"] = round(self.fecDistrict_DHN / self.h_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1"] = "-"
            try:
                KPIs["EN_14.1R"] = round(self.fecDistrictR_DHN / self.h_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1R"] = "-"
            try:
                KPIs["EN_14.1T"] = round(self.fecDistrictT_DHN / self.h_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1T"] = "-"
            try:
                KPIs["EN_14.1b"] = round(self.fecDistrict_DCN / self.c_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1b"] = "-"
            try:
                KPIs["EN_14.1bR"] = round(self.fecDistrictR_DCN / self.c_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1bR"] = "-"
            try:
                KPIs["EN_14.1bT"] = round(self.fecDistrictT_DCN / self.c_length, 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["EN_14.1bT"] = "-"
            try:
                KPIs["EN_15.1"] = self.YEOHbase
            except:
                KPIs["EN_15.1"] = "Nan"
            try:
                KPIs["EN_15.1R"] = round(
                    sum([self.YEOHbaseR[key][0] / self.YEOHbaseR[key][1] for key in self.YEOHbaseR.keys()]), 2)
            except:
                KPIs["EN_15.1R"] = "Nan"
            try:
                KPIs["EN_15.1T"] = round(
                    sum([self.YEOHbaseT[key][0] / self.YEOHbaseT[key][1] for key in self.YEOHbaseT.keys()]), 2)
            except:
                KPIs["EN_15.1T"] = "Nan"

            fec = [KPIs["EN_2.1_s" + str(i)] for i in range(len(self.sourceName))]
            fecR = [KPIs["EN_2.1R_s" + str(i)] for i in range(len(self.sourceName))]
            fecT = [KPIs["EN_2.1T_s" + str(i)] for i in range(len(self.sourceName))]
            KPIs["ENV_1.3"] = self.get_t_pollutant_baseline(fec, self.pollutant_colum_index["CO2"])
            KPIs["ENV_1.3R"] = self.get_t_pollutant_baseline(fecR, self.pollutant_colum_index["CO2"])
            KPIs["ENV_1.3T"] = self.get_t_pollutant_baseline(fecT, self.pollutant_colum_index["CO2"])
            try:
                KPIs["ENV_1.4"] = round(KPIs["ENV_1.3"] / KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.4"] = "Nan"
            try:
                KPIs["ENV_1.4R"] = round(KPIs["ENV_1.3R"] / KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.4R"] = "Nan"
            try:
                KPIs["ENV_1.4T"] = round(KPIs["ENV_1.3T"] / KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_1.4T"] = "Nan"

            KPIs["ENV_2.1"] = self.get_t_pollutant_baseline(fec, self.pollutant_colum_index["NOx"])
            KPIs["ENV_2.1R"] = self.get_t_pollutant_baseline(fecR, self.pollutant_colum_index["NOx"])
            KPIs["ENV_2.1T"] = self.get_t_pollutant_baseline(fecT, self.pollutant_colum_index["NOx"])
            try:
                KPIs["ENV_2.2"] = round(KPIs["ENV_2.1"] / KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.2"] = "Nan"
            try:
                KPIs["ENV_2.2R"] = round(KPIs["ENV_2.1R"] / KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.2R"] = "Nan"
            try:
                KPIs["ENV_2.2T"] = round(KPIs["ENV_2.1T"] / KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.2T"] = "Nan"

            KPIs["ENV_2.7"] = self.get_t_pollutant_baseline(fec, self.pollutant_colum_index["SOx"])
            KPIs["ENV_2.7R"] = self.get_t_pollutant_baseline(fecR, self.pollutant_colum_index["SOx"])
            KPIs["ENV_2.7T"] = self.get_t_pollutant_baseline(fecT, self.pollutant_colum_index["SOx"])
            try:
                KPIs["ENV_2.8"] = round(KPIs["ENV_2.7"] / KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.8"] = "Nan"
            try:
                KPIs["ENV_2.8R"] = round(KPIs["ENV_2.7R"] / KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.8R"] = "Nan"
            try:
                KPIs["ENV_2.8T"] = round(KPIs["ENV_2.7T"] / KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.8T"] = "Nan"

            KPIs["ENV_2.13"] = self.get_t_pollutant_baseline(fec, self.pollutant_colum_index["PM10"])
            KPIs["ENV_2.13R"] = self.get_t_pollutant_baseline(fecR, self.pollutant_colum_index["PM10"])
            KPIs["ENV_2.13T"] = self.get_t_pollutant_baseline(fecT, self.pollutant_colum_index["PM10"])
            try:
                KPIs["ENV_2.14"] = round(KPIs["ENV_2.13"] / KPIs["EN_1.1"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.14"] = "Nan"
            try:
                KPIs["ENV_2.14R"] = round(KPIs["ENV_2.13R"] / KPIs["EN_1.1R"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.14R"] = "Nan"
            try:
                KPIs["ENV_2.14T"] = round(KPIs["ENV_2.13T"] / KPIs["EN_1.1T"], 2)
            except(ZeroDivisionError, TypeError) as e:
                KPIs["ENV_2.14T"] = "Nan"
                # SO 3.1 FEavailability è un output del MM
            try:
                KPIs["SO_3.1"] = round((1 - (KPIs["EN_2.1"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError, KeyError) as e:
                traceback.print_exc()
                KPIs["SO_3.1"] = "Nan"
            try:
                KPIs["SO_3.1R"] = round((1 - (KPIs["EN_2.1R"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError, KeyError) as e:
                traceback.print_exc()
                KPIs["SO_3.1R"] = "Nan"
            try:
                KPIs["SO_3.1T"] = round((1 - (KPIs["EN_2.1T"] / FEavailability)) * 100, 2)
            except (ZeroDivisionError, TypeError, KeyError) as e:
                traceback.print_exc()
                KPIs["SO_3.1T"] = "Nan"

            try:
                KPIs["ECO_2.1"] = round(float(self.opex), 2)
            except:
                KPIs["ECO_2.1"] = "Nan"
            try:
                KPIs["ECO_2.1R"] = round(float(self.opexR), 2)
            except:
                KPIs["ECO_2.1R"] = "Nan"
            try:
                KPIs["ECO_2.1T"] = round(float(self.opexT), 2)
            except:
                KPIs["ECO_2.1T"] = "Nan"

            KPIs["fuel_cost_saving"] = self.fuel_cost_saving
            KPIs["fuel_cost_savingR"] = self.fuel_cost_savingR
            KPIs["fuel_cost_savingT"] = self.fuel_cost_savingT
            KPIs["OeM_cost_saving"] = self.OeM_cost_saving
            KPIs["OeM_cost_savingR"] = self.OeM_cost_savingR
            KPIs["OeM_cost_savingT"] = self.OeM_cost_savingT

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
        self.KPIs_input = None

    def reset(self, reset_interface=False):
        self.input_reset()
        # self.initialize()

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
                    return [float(widget.item(i, 0).text().replace(",", ".")),
                            float(widget.item(i, 1).text().replace(",", "."))]
                except:
                    print("KPIsCalculator.py, get_source_infos: impossible to get row", i)
        return [0, 0]

    def getPEF_source(self):
        PEF = [1.0 for i in range(len(self.sourceName))]

        for k in range(len(self.sourceName)):
            PEF[k], _ = self.get_source_infos(self.pef_sources_tab, self.sourceName[k])
        return PEF

    def PECbaseSource(self, pef, fec):
        pecBase = np.zeros(23)
        self.my_log.log("---   PECbaseSource   ---")
        self.my_log.log(self.building_id)
        self.my_log.log("pef")
        self.my_log.log(pef)
        self.my_log.log("pec")
        self.my_log.log(fec)

        for k in range(len(pecBase)):
            pecBase[k] = fec[k] * pef[k]
        self.my_log.log("pecBase")
        self.my_log.log(pecBase)
        return pecBase


    def district_emission(self, ef_column_index=1):
        CO2, pef = 0, 0
        for i in range(self.tech_tab.topLevelItemCount()):
            n = self.tech_tab.topLevelItem(i)
            if n.data(0, Qt.UserRole) == self.network.get_ID():
                for j in range(n.childCount()):
                    for k in range(self.ef_sources_tab.rowCount()):
                        if self.ef_sources_tab.verticalHeaderItem(k).text() == n.child(j).text(2):
                            try:
                                emission_factor = float(self.ef_sources_tab.item(k, ef_column_index).text())
                                pef, _ = self.get_source_infos(self.pef_sources_tab, n.child(j).text(2))
                            except:
                                pef = 1
                                emission_factor = 1
                                traceback.print_exc()
                                print("KPIsCalculator, district_CO2. Item", k, ef_column_index, "failed to get from",
                                      self.ef_sources_tab.objectName(), "table")
                            break
                    else:
                        print("KPIsCalculator, district_CO2. Item", k, 1, "not found in ", self.ef_sources_tab,
                              "table")
                        pef = 1
                        emission_factor = 1
                    category = n.child(j).data(1, Qt.UserRole)
                    file = os.path.join(self.work_folder, "Results_" + str(category) + "_" + self.network.get_ID() + ".csv")
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
                CO2 = CO2 + emission_factor * pef * (self.sum_file(file))
        return CO2

    def safe_get_float_feature_attribute(self, feature, attribute):
        try:
            return float(feature.attribute(attribute))
        except:
            traceback.print_exc()
            return 0.0

    def get_UED(self, layer, use=None):
        self.my_log.log("---   get_UED()   ---")
        widget = None
        if self.baseline_tech_tab is not None:
            widget = self.baseline_tech_tab
        else:
            widget = self.future_tech_tab
        if widget is None:
            self.my_log.log("ERROR: widget is None!")
            return 0.0
        if layer is None:
            self.my_log.log("ERROR: layer is None!")
            return 0.0
        total = 0
        self.my_log.log("widget.objectName(): " + str(widget.objectName()))
        for f in layer.getFeatures():
            self.my_log.log("loop on building: " + str(f.attribute("BuildingID")) + " with f.id(): " + str(f.id()))
            self.my_log.log("loop iterations: " + str(widget.topLevelItemCount()))
            UED_contribution = 0
            for i in range(widget.topLevelItemCount()):
                building_item = widget.topLevelItem(i)
                self.my_log.log("building_item.text(0): " + str(building_item.text(0)))
                if str(building_item.text(0)) == str(f.id()):
                    self.my_log.log("found item in the QTreeWidget: " + str(f.id()))
                    for j in range(building_item.childCount()):
                        scope_item = building_item.child(j)
                        if not scope_item.childCount() == 0:
                            scope_tipe = scope_item.text(0)
                            self.my_log.log("Checking service : " + str(scope_tipe))
                            if scope_tipe == "Cooling":
                                UED_contribution += self.safe_get_float_feature_attribute(f, "ACoolDem")
                            if scope_tipe == "Heating":
                                UED_contribution += self.safe_get_float_feature_attribute(f, "AHeatDem")
                            if scope_tipe == "DHW":
                                UED_contribution += self.safe_get_float_feature_attribute(f, "ADHWDem")
                            self.my_log.log("UED_contribution : " + str(UED_contribution))
                    break
            if use == "R":
                check = f.attribute("Use") == "Residential"
            elif use == "T":
                check = not f.attribute("Use") == "Residential"
            else:
                check = True
            if check:
                try:
                    total = total + UED_contribution
                except:
                    print("KPIsCalculator, get_UED. Problems calculating UED for layer", layer.name())
        self.my_log.log("total/1000: " + str(total/1000))
        return total / 1000

    def initialize_YEOHbase(self):
        self.YEOHbase = {}
        self.YEOHbaseT = {}
        self.YEOHbaseR = {}
        for key in self.sources.sources:
            self.YEOHbase[key] = [0, 0]
            self.YEOHbaseR[key] = [0, 0]
            self.YEOHbaseT[key] = [0, 0]

    def get_UED_cooling(self, layer, use=None):
        widget = None
        if self.baseline_tech_tab is not None:
            widget = self.baseline_tech_tab
        else:
            widget = self.future_tech_tab
        if widget is None:
            self.my_log.log("---   get_UED_cooling()   ---")
            self.my_log.log("ERROR: widget is None!")
            return 0.0
        if layer is None:
            self.my_log.log("---   get_UED()   ---")
            self.my_log.log("ERROR: layer is None!")
            return 0.0
        total = 0
        # self.my_log.log("---   get_UED_cooling()   ---")
        # self.my_log.log("self.baseline_tech_tab.objectName(): " + str(self.baseline_tech_tab.objectName()))
        for f in layer.getFeatures():
            # self.my_log.log("loop on building: " + str(f.attribute("BuildingID")) + " with f.id(): " + str(f.id()))
            # self.my_log.log("loop iterations: " + str(self.baseline_tech_tab.topLevelItemCount()))
            UED_contribution = 0
            for i in range(widget.topLevelItemCount()):
                building_item = widget.topLevelItem(i)
                # self.my_log.log("building_item.text(0): " + str(building_item.text(0)))
                if str(building_item.text(0)) == str(f.id()):
                    # self.my_log.log("found item in the QTreeWidget: " + str(f.id()))
                    for j in range(building_item.childCount()):
                        scope_item = building_item.child(j)
                        if not scope_item.childCount() == 0:
                            scope_tipe = scope_item.text(0)
                            # self.my_log.log("Checking service : " + str(scope_tipe))
                            if scope_tipe == "Cooling":
                                UED_contribution += self.safe_get_float_feature_attribute(f, "ACoolDem")
                            # self.my_log.log("UED_contribution : " + str(UED_contribution))
                    break
            if use == "R":
                check = f.attribute("Use") == "Residential"
            elif use == "T":
                check = not f.attribute("Use") == "Residential"
            else:
                check = True
            if check:
                try:
                    total = total + UED_contribution
                except:
                    print("KPIsCalculator, get_UED. Problems calculating UED for layer", layer.name())
        return total / 1000

    def get_total_UED_cooling(self, layer, use=None):
        if layer is None:
            return 0.0
        UED_contribution = 0
        UED_contributionR = 0
        UED_contributionT = 0
        for f in layer.getFeatures():
            if use is None:
                UED_contribution += self.safe_get_float_feature_attribute(f, "ACoolDem")
            if use == "T":
                UED_contributionT += self.safe_get_float_feature_attribute(f, "ACoolDem")
            if use == "R":
                UED_contributionR += self.safe_get_float_feature_attribute(f, "ACoolDem")
        if use is None:
            return UED_contribution/1000
        if use == "R":
            return UED_contributionR/1000
        if use == "T":
            return UED_contributionT/1000
        return 0.0

    def district_solar_penetration(self):
        stp = 0
        try:
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
        except:
            traceback.print_exc()
            return stp
        return stp


    def individual_solar_penetration(self):
        stp = 0
        try:
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
        except:
            traceback.print_exc()
            return stp
        return stp


    def building_PEC_calculation(self):
        dr = self.work_folder
        item = self.tech_tab
        building_id = self.building_id
        pec = 0.0
        try:
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
                    pec = pec + pef * (self.sum_file(file))
        except:
            traceback.print_exc()
            return pec
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
        try:
            for i in range(widget.topLevelItemCount()):
                try:
                    item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
                    # moved to children items
                    # item_julia_category = str(widget.topLevelItem(i).data(1, Qt.UserRole))
                except:
                    print("KPIsCalculator, district_pec. Network:", network_id,
                          "Failed to retrieve item_network_id and/or item_julia_category from widget",
                          widget.objectName())
                    traceback.print_exc()
                    continue
                if item_network_id == network_id:
                    for j in range(widget.topLevelItem(i).childCount()):
                        tech = widget.topLevelItem(i).child(j)
                        item_julia_category = str(tech.data(1, Qt.UserRole))
                        try:
                            pef, _ = self.get_source_infos(sources_widget, tech.text(2))
                        except:
                            pef = 1
                            print("KPIsCalculator, district_pec. Problems with method get_source_infos: ",
                                widget.topLevelItem(i).text(2))
                        file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                        try:
                            pec = pec + pef * (self.sum_file(file))
                        except:
                            print("KPIsCalculator, district_pec. Error summing file", file)
        except:
            traceback.print_exc()
            return pec
        return pec


    def building_pecRENs_calculation(self, dr, item, building_id):
        pecRENs = 0.0
        try:
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
                        pecRENs = pecRENs + pef * (self.sum_file(file))
        except:
            traceback.print_exc()
            return pecRENs
        return pecRENs


    def district_pecRENs(self, dr, network_id, widget=None, sources_widget=None):
        pecRENs = 0.0
        if widget is None:
            return pecRENs
        if sources_widget is None:
            return pecRENs
        try:
            for i in range(widget.topLevelItemCount()):
                try:
                    item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
                except:
                    traceback.print_exc()
                    print("KPIsCalculator, district_pecRENs. Network:", network_id,
                          "Failed to retrieve item_network_id and/or item_julia_categoty from widget", widget.objectName())
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
                                pecRENs = pecRENs + pef * (self.sum_file(file))
                            except:
                                print("KPIsCalculator, district_pecRENs. Error summing file", file)
        except:
            traceback.print_exc()
            return pecRENs
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
                traceback.print_exc()
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
                    pecCF = pecCF + pef * (self.sum_file(file))
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
                traceback.print_exc()
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
                            pecCF = pecCF + pef * (self.sum_file(file))
                        except:
                            print("KPIsCalculator, district_pecCF. Error summing file", file)
        return pecCF


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
                traceback.print_exc()
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
        self.my_log.log("---   building_FEC_calculation   ---")

        fec_source = np.zeros(len(self.sourceName))

        const_eff = self.const_eff
        variable_eff_ng = self.variable_eff_ng
        variable_eff_el = self.variable_eff_el

        column = 0
        separator = ";"
        for i in range(item.childCount()):  # cooling heating DHW #technology
            scope_item = item.child(i)
            for j in range(scope_item.childCount()):  # technology
                tech = scope_item.child(j)
                source = tech.text(2)

                self.my_log.log("source")
                self.my_log.log(source)
                efficiency = tech.text(5)
                technology = tech.text(0)
                self.my_log.log("technology")
                self.my_log.log(technology)
                efficiency = round(float(efficiency), 2)

                if technology in const_eff:
                    if technology not in ["Air source gas absorption heat pump",
                                          "Shallow geothermal gas absorption heat pump",
                                          "Air source gas absorption chiller"]:
                        julia_category = str(tech.data(0, Qt.UserRole))
                        self.my_log.log("julia_category")
                        self.my_log.log(julia_category)
                        file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                        self.my_log.log("file")
                        self.my_log.log(file)
                        for k in range(len(self.sourceName)):
                            self.my_log.log("Confronto" + str(source) + " - " + str(self.sourceName[k]))
                            if source == self.sourceName[k]:
                                self.my_log.log("FOUND!")
                                self.my_log.log("fec_source[k] before")
                                self.my_log.log(fec_source[k])
                                self.my_log.log("self.sum_file(file)")
                                self.my_log.log(self.sum_file(file))
                                fec_source[k] = fec_source[k] + self.sum_file(file) / efficiency
                                self.my_log.log("fec_source[k] after")
                                self.my_log.log(fec_source[k])
                                break  # stops sources loop
                    else:
                        julia_category = str(tech.data(0, Qt.UserRole))
                        file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                        efficiency = float(tech.text(20))  # eta_absorption
                        self.my_log.log("elif case!")
                        self.my_log.log("file:")
                        self.my_log.log(file)
                        self.my_log.log("efficiency:")
                        self.my_log.log(efficiency)
                        self.my_log.log("fec_source[1] before")
                        self.my_log.log(fec_source[1])
                        self.my_log.log("self.sum_file(file)")
                        self.my_log.log(self.sum_file(file))
                        self.my_log.log("fec_source[1] after")
                        self.my_log.log(fec_source[1])
                        # natural gas contribution
                        somma_file = self.sum_file(file)
                        fec_source[1] += somma_file / efficiency
                        for k in range(len(self.sourceName)):
                            if source == self.sourceName[k]:
                                fec_source[k] = fec_source[k] + somma_file*(efficiency-1)/efficiency
                                break  # stops sources loop
                elif technology in variable_eff_el:
                    # if technology not in ["Air source compression chiller",
                    #                       "Shallow geothermal compression chiller"]:
                    julia_category = str(tech.data(0, Qt.UserRole))
                    file_julia = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                    file_eta_HP_1 = os.path.realpath(os.path.join(dr, "../", "input", "eta_" + julia_category + ".csv"))
                    self.my_log.log("file_julia: " + str(file_julia))
                    self.my_log.log("file_eta_HP_X: " + str(file_eta_HP_1))

                    with open(file_eta_HP_1, "r") as fp:
                        COP_var = np.zeros(self.h8760)
                        for ii, line in enumerate(fp):
                            COP_var[ii] = float(line.split(separator)[column])

                    with open(file_julia, "r") as fp:
                        Q1 = np.zeros(self.h8760)
                        for ii, line in enumerate(fp):
                            Q1[ii] = float(line.split(separator)[column])  # check syntax

                    fec_i = np.zeros_like(Q1)
                    for ii in range(len(fec_i)):
                        if COP_var[ii] > 0:
                            fec_i[ii] = Q1[ii] / COP_var[ii]
                    self.my_log.log("Average eta: " + str(sum(COP_var) / self.h8760))
                    self.my_log.log("Average sum(fec_i): " + str(sum(fec_i)))
                    self.my_log.log("Average sum(Q1): " + str(sum(Q1)))
                    self.my_log.log("Contributo fec prima: " + str(fec_source))

                    fec_2 = sum(fec_i)
                    self.my_log.log("fec_2: " + str(fec_2))
                    fec_source[2] = fec_source[2] + fec_2
                    self.my_log.log("Contributo fec dopo: " + str(fec_source))

                    for k in range(len(self.sourceName)):
                        if source == self.sourceName[k]:
                            self.my_log.log("Trovato fonte: " + str(source))
                            for ii in range(len(fec_i)):
                                if COP_var[ii] > 0:
                                    fec_i[ii] = Q1[ii] * (COP_var[ii] - 1) / COP_var[ii]
                            fec_k = sum(fec_i)
                            fec_source[k] = fec_source[k] + fec_k
                            break  # stops the sources loop
        print("KpisCalculator.building_FEC_calculation fec_source:", fec_source)
        return fec_source


    def district_fec(self, dr, network_id, widget=None):
        self.my_log.log("---   district_fec()   ---")
        fec_source = np.zeros(len(self.sourceName))
        opex = 0
        opexR = 0
        opexT = 0
        column = 0
        separator = ";"
        eta_d = self.network.get_efficiency()
        self.my_log.log("network_id: " + str(network_id))
        self.my_log.log("eta_d: " + str(eta_d))
        self.my_log.log("dr: " + str(dr))
        if widget is None:
            return fec_source
        for i in range(widget.topLevelItemCount()):
            try:
                item_network_id = str(widget.topLevelItem(i).data(0, Qt.UserRole))
                self.my_log.log("network_id vs network in list: " + str(network_id) + " - " + str(item_network_id))
            except:
                traceback.print_exc()
                print("KPIsCalculator, district_pec. Network:", network_id, "Failed to retrieve item_network_id and/or ",
                                                                            "item_julia_categoty from widget", widget)
                continue
            if item_network_id == network_id:
                self.my_log.log("FOUND: " + str(network_id))
                for j in range(widget.topLevelItem(i).childCount()):
                    tech = widget.topLevelItem(i).child(j)
                    source = tech.text(2)
                    efficiency = tech.text(5)

                    efficiency = round(float(efficiency), 2)
                    technology = tech.text(1)
                    fuel_cost = float(tech.text(15))
                    self.my_log.log("technology: " + str(technology))
                    self.my_log.log("Source:", source)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    self.my_log.log("item_julia_category: " + str(item_julia_category))
                    if technology in self.const_eff:
                        if technology not in ["Air source gas absorption heat pump",
                                              "Shallow geothermal gas absorption heat pump",
                                              "Waste heat absorption heat pump",
                                              "Air source gas absorption chiller"]:
                            self.my_log.log("Tech in const_eff but not in micro list")
                            file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                            self.my_log.log("file: " + str(file))
                            for k in range(len(self.sourceName)):
                                self.my_log.log("Testing", self.sourceName[k], "VS", source)
                                if source == self.sourceName[k]:
                                    self.my_log.log("Source FOUND!")
                                    fec_contribution = self.sum_file(file) / efficiency / eta_d
                                    fec_source[k] = fec_source[k] + fec_contribution
                                    self.my_log.log("fec_source after: " + str(fec_source))
                                    if source in self.opex_conventional_fuels:
                                        opex += fec_contribution * fuel_cost
                                        opexR += fec_contribution * fuel_cost * self.residential_factor
                                        opexT += fec_contribution * fuel_cost * (1 - self.residential_factor)
                                        self.my_log.log("FEC contribution to opex:", fec_contribution * fuel_cost)
                                    break
                        else:
                            self.my_log.log("Tech in const_eff and in micro list")
                            efficiency = float(tech.text(20))  # eta_absorption
                            file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                            self.my_log.log("file: " + str(file))
                            self.my_log.log("fec_source before: " + str(fec_source))
                            # natural gas contribution:
                            somma_file = self.sum_file(file)
                            fec_contribution = somma_file / (efficiency * eta_d)
                            fec_source[1] += fec_contribution
                            for k in range(len(self.sourceName)):
                                if source == self.sourceName[k]:
                                    self.my_log.log("Source FOUND!")
                                    fec_contribution = somma_file * (efficiency - 1) / efficiency / eta_d
                                    fec_source[k] += fec_contribution
                                    if source in self.opex_conventional_fuels:
                                        opex += fec_contribution * fuel_cost
                                        opexR += fec_contribution * fuel_cost * self.residential_factor
                                        opexT += fec_contribution * fuel_cost * (1 - self.residential_factor)
                                        self.my_log.log("FEC contribution to opex:", fec_contribution * fuel_cost)
                                    break
                            self.my_log.log("fec_source after: " + str(fec_source))

                    if technology in self.variable_eff_el:
                        self.my_log.log("Tech in variable_eff_el")
                        file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                        self.my_log.log("julia output file:", file)
                        file_eta_HP_1 = os.path.normpath(os.path.join(dr, "../", "input",
                                                     "eta_" + item_julia_category.replace("waste_heat_", "") + ".csv"))
                        self.my_log.log("file degli eta:", file_eta_HP_1)
                        if not os.path.isfile(file_eta_HP_1) or not os.path.isfile(file):
                            self.my_log.log("Problems with files!!!")
                            continue
                        with open(file_eta_HP_1) as fp:
                            COP_var = np.zeros(self.h8760)
                            for ii, line in enumerate(fp):
                                COP_var[ii] = float(line.split(separator)[column])

                        with open(file) as fp:
                            Q1 = np.zeros(self.h8760)
                            for ii, line in enumerate(fp):
                                Q1[ii] = float(line.split(separator)[column])
                        fec_i = np.zeros_like(Q1)
                        for ii in range(len(fec_i)):
                            if COP_var[ii] > 0:
                                fec_i[ii] = Q1[ii] / COP_var[ii] / eta_d
                        fec_2 = sum(fec_i)
                        fec_source[2] = fec_source[2] + fec_2
                        opex += fec_2 * fuel_cost
                        opexR += fec_2 * fuel_cost * self.residential_factor
                        opexT += fec_2 * fuel_cost * (1 - self.residential_factor)
                        self.my_log.log("fec_2 - fec_source (after electricity):", fec_2, fec_source)

                        self.my_log.log("searching source:", source, "in", self.sourceName)
                        for k in range(len(self.sourceName)):
                            if source == self.sourceName[k]:
                                self.my_log.log("Source found!")
                                for ii in range(len(fec_i)):
                                    if COP_var[ii] > 0:
                                        fec_i[ii] = Q1[ii] * (COP_var[ii] - 1) / COP_var[ii] / eta_d
                                fec_k = sum(fec_i)
                                fec_source[k] = fec_source[k] + fec_k
                                if source in self.opex_conventional_fuels:
                                    opex += fec_k * fuel_cost
                                    opexR += fec_k * fuel_cost * self.residential_factor
                                    opexT += fec_k * fuel_cost * (1 - self.residential_factor)
                                    self.my_log.log("FEC contribution to opex:", fec_k * fuel_cost)
                                self.my_log.log("COntribution to", k, source, fec_k)
                                break

                    if technology in self.variable_eff_ng:
                        julia_category = str(tech.data(0, Qt.UserRole))
                        file = os.path.join(dr, "Result_" + item_julia_category + "_" + network_id + ".csv")
                        fec_source[1] = fec_source[1] + self.sum_file(file) / efficiency / eta_d
                        for k in range(len(self.sourceName)):
                            if source == self.sourceName[k]:
                                fec_contribution = self.sum_file(file) * (efficiency - 1) / efficiency / eta_d
                                fec_source[k] = fec_source[k] + fec_contribution
                                if source in self.opex_conventional_fuels:
                                    opex += fec_contribution * fuel_cost
                                    opexR += fec_contribution * fuel_cost * self.residential_factor
                                    opexT += fec_contribution * fuel_cost * (1 - self.residential_factor)
                                    self.my_log.log("FEC contribution to opex:", fec_contribution * fuel_cost)
                                break
                    if not technology in self.solar_technologies:
                        self.opex += opex
                        self.opexR += opexR
                        self.opexT += opexT
        self.my_log.log("function ends with output fec:", fec_source)
        return fec_source

    def building_YEOHbase_calculation(self, dr, item, building_id, YEOHbase):
        self.my_log.log("---   building_YEOHbase_calculation()   ---")
        for i in range(item.childCount()):
            for j in range(item.child(i).childCount()):
                technology = item.child(i).child(j)
                pef, _ = self.get_source_infos(self.pef_sources_tab, technology.text(2))
                # select only specific sources
                self.my_log.log("YEOHbase contribution from: " + str(building_id) + " " + str(technology.text(0)) + " " + str(technology.text(2)))
                self.my_log.log("YEOHbase.keys(): " + str(YEOHbase.keys()))
                if technology.text(2) in YEOHbase.keys():
                    julia_category = str(technology.data(0, Qt.UserRole))
                    file = os.path.join(dr, "Result_" + julia_category + "_" + building_id + ".csv")
                    self.my_log.log("file: " + str(file))
                    self.my_log.log("YEOHbase[technology.text(2)] before: " + str(YEOHbase[technology.text(2)]))
                    YEOHbase[technology.text(2)][0] = YEOHbase[technology.text(2)][0] + (self.sum_file(file))
                    try:
                        YEOHbase[technology.text(2)][1] = YEOHbase[technology.text(2)][1] + float(
                            technology.text(self.individual_tech_power_column))
                    except:
                        print("KPIsCalculator, building_YEOHbase_calculation")
                        print("YEOHbase:", YEOHbase, "technology.text(self.name_to_index(\"capacity\"))",
                              technology.text(self.individual_tech_power_column))
                        pass
                    self.my_log.log("YEOHbase[technology.text(2)] after: " + str(YEOHbase[technology.text(2)]))

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
                    YEOHbase[tech.text(1)][0] = YEOHbase[tech.text(1)][0] + (self.sum_file(file)) / float(
                        technology.text(self.individual_tech_power_column))
                    try:
                        YEOHbase[tech.text(1)][1] = YEOHbase[tech.text(1)][1] + float(
                            tech.text(self.district_tech_power_column))
                    except:
                        print("KPIsCalculator, building_YEOHbase_calculation")
                        print("YEOHbase:", YEOHbase, "technology.text(self.name_to_index(\"capacity\"))",
                              technology.text(self.district_tech_power_column))
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
            #raise Exception()
            return 0.0
        print("KPIsCalculator, sum_file, total", total)
        return total

    def sum_derivative_of_file(self, file, column=0, separator=";"):
        total = 0.0
        with open(file, "r") as fp:
            lines = fp.readlines()
        for i in range(len(lines)-1):
            try:
                total += abs(float(lines[i+1])-float(lines[i]))
            except:
                pass
        return total


    def building_has_technologies(self, layer, building_id):
        if self.future_scenario is None:
            building_tree_widget = self.baseline_tech_tab
        else:
            building_tree_widget = self.future_tech_tab
        if building_tree_widget is None:
            return False
        building_feature_id = str(self.get_feature_id_from_building_id(layer, building_id))
        if building_feature_id is None:
            return False
        for i in range(building_tree_widget.topLevelItemCount()):
            if building_tree_widget.topLevelItem(i).text(0) == building_feature_id:
                building = building_tree_widget.topLevelItem(i)
                for j in range(building.childCount()):
                    service = building.child(j)
                    if not service.childCount() == 0:
                        return True
                return False
        return False

    def get_feature_id_from_building_id(self, layer, building_id):
        feature_id = None
        if layer is None:
            return feature_id
        fs = [ft for ft in layer.getFeatures(QgsFeatureRequest(QgsExpression("BuildingID=" + building_id)))]
        if len(fs) > 0:
            feature_id = fs[0].id()
        return feature_id

    def get_area(self, building_id):
        expr = QgsExpression("BuildingID=" + building_id)
        if self.baseline_scenario is not None:
            layer = self.baseline_scenario
        else:
            layer = self.future_scenario
        if layer is None:
            print("KPIsCalculator, KPIs_baselineScenario: layer is not defined")
            return 0.0
        fs = [ft for ft in layer.getFeatures(QgsFeatureRequest(expr))]
        if not self.building_has_technologies(layer, building_id):
            return 0.0
        if len(fs) > 0:
            feature_0 = fs[0]
        else:
            print("get_area: FALLITO MALE", building_id)
            return 0.0
        try:
            gross_floor_area_building = float(feature_0.attribute("GrossFA"))
        except:
            traceback.print_exc()
            gross_floor_area_building = 1.0
        return gross_floor_area_building

    def district_grant_contribution(self, use=None):
        grant = 0
        if self.tech_tab is None:
            return grant
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
                print("KPIsCalculator.py, district_grant_contribution(): item_network_id, item_julia_category",
                      network_id)
            except:
                traceback.print_exc()
                print("KPIsCalculator, district_pec. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id and/or "
                      "item_julia_categoty from widget", self.tech_tab)
                continue
            if network_id == self.network.get_ID():
                if self.network.n_type == "DCN":
                    if self.network.optimized_buildings_layer is not None:
                        grant_temp = self.get_UED_cooling(self.network.optimized_buildings_layer, use)
                    else:
                        grant_temp = self.get_UED_cooling(self.network.buildings_layer, use)
                else:
                    if self.network.optimized_buildings_layer is not None:
                        grant_temp = self.get_UED_heating(self.network.optimized_buildings_layer, use)
                    else:
                        grant_temp = self.get_UED_heating(self.network.buildings_layer, use)

                item: QTreeWidget = self.tech_tab.topLevelItem(i)
                for j in range(item.childCount()):
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

    def districtOeM_cost(self, use=None):
        opex = 0
        if self.tech_tab is None:
            return opex
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                traceback.print_exc()
                print("KPIsCalculator, district_FECfut_tech_per_energy_tariff. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id and/or "
                      "item_julia_categoty from widget", self.tech_tab)
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    tech = self.tech_tab.topLevelItem(i).child(j)
                    julia_category = str(tech.data(1, Qt.UserRole))
                    file = os.path.join(self.work_folder, "Result_" + julia_category + "_" + self.network.get_ID() + ".csv")
                    try:
                        opex += self.sum_file(file)*float(tech.text(15))
                    except:
                        print("KPIsCalculator, district_pec. Error summing file", file)
        if use is None:
            return opex
        elif use == "R":
            try:
                return opex * self.areaR / self.area
            except:
                return 0
        else:
            try:
                return opex * (1 - self.areaR / self.area)
            except:
                return 0


    def district_FECfut_tech_per_energy_tariff(self, use=None):
        self.my_log.log("---   district_FECfut_tech_per_energy_tariff()   ---")
        self.my_log.log("use:", use)
        opex = 0
        if self.tech_tab is None:
            return opex
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                traceback.print_exc()
                print("KPIsCalculator, district_FECfut_tech_per_energy_tariff. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id and/or "
                      "item_julia_categoty from widget", self.tech_tab)
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    fec = 0.0
                    tech = self.tech_tab.topLevelItem(i).child(j)
                    source = tech.text(2)
                    if source not in self.opex_conventional_fuels:
                        continue
                    julia_category = str(tech.data(1, Qt.UserRole))
                    file_eta = os.path.realpath(os.path.join(self.work_folder, "../",
                                                             "Input", "eta_" + julia_category + ".csv"))
                    file = os.path.join(self.work_folder, "Result_" + julia_category + "_" + self.network.get_ID() + ".csv")
                    self.my_log.log("file julia:", file)
                    self.my_log.log("file degli eta", file_eta)
                    if tech.text(1) in self.variable_eff_el:
                        self.my_log.log("In variable_eff_el")
                        if os.path.isfile(file_eta) and os.path.isfile(file):
                            self.my_log.log("files found!")
                            with open(file) as julia_ued, open(file_eta) as eta:
                                for k in range(self.h8760):
                                    try:
                                        fec += float(julia_ued.readline()) / float(eta.readline())
                                    except:
                                        pass
                            self.my_log.log("fec", fec)
                    else:
                        try:
                            efficiency = float(tech.text(5))
                        except:
                            efficiency = 1.0
                        fec = (self.sum_file(file)/efficiency)
                    try:
                        coeff = float(tech.text(15))  # fuel cost
                    except:
                        coeff = 1
                    try:
                        opex = opex + fec * coeff
                        self.my_log.log("opex contribution", opex)
                    except:
                        print("KPIsCalculator, district_pec. Error summing file", file)
        if use is None:
            return opex
        elif use == "R":
            try:
                return opex * self.areaR / self.area
            except:
                return 0
        else:
            try:
                return opex * (1 - self.areaR / self.area)
            except:
                return 0

    def building_UEDfut_tech_per_energy_tariff(self, use=None):
        self.my_log.log("---   building_UEDfut_tech_per_energy_tariff   ---")
        fec = 0.0
        for i in range(self.tech_tab.childCount()):
            scope_item = self.tech_tab.child(i)
            for j in range(scope_item.childCount()):
                technology = scope_item.child(j)
                julia_category = str(technology.data(0, Qt.UserRole))
                file = os.path.join(self.work_folder, "Result_" + julia_category + "_" + self.building_id + ".csv")
                # column of energy tariff per il fuel cost saving = 15
                try:
                    coeff = float(technology.text(15))*1000
                except:
                    coeff = 1
                try:
                    fec = fec + (self.sum_file(file)) * coeff
                except:
                    print("KPIsCalculator, district_pec. Error summing file", file)
        self.my_log.log("fec, self.building_tag, use: " + str([fec, self.building_tag, use]))
        if use is None:
            return fec
        if use == "R":
            if self.building_tag == "Residential":
                return fec
            else:
                return 0
        if use == "T":
            if not self.building_tag == "Residential":
                return fec
            else:
                return 0
        return 0

    def district_UEDfut_tech_per_energy_tariff(self, use=None):
        fec = 0
        if self.tech_tab is None:
            return fec
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                traceback.print_exc()
                print("KPIsCalculator, district_UEDfut_tech_per_energy_tariff. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id")
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    tech = self.tech_tab.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    file = os.path.join(self.work_folder, "Result_" + item_julia_category + "_" + str(self.network.get_ID()) + ".csv")
                    ued = 0
                    if os.path.isfile(file):
                        if item_julia_category.startswith("SOC"):
                            self.sum_derivative_of_file(file)
                        else:
                            ued = self.sum_file(file)
                    try:
                        coeff = float(tech.text(14))  # variable cost
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

    def building_FECfut_tech_per_energy_tariff(self, use=None):
        self.my_log.log("---   building_FECfut_tech_per_energy_tariff   ---")
        if self.future_scenario is not None:
            self.my_log.log("Simulation: FUTURE")
        else:
            self.my_log.log("Simulation: BASELINE")
        opex = 0.0
        if self.baseline_scenario is not None:
            layer = self.baseline_scenario
        else:
            layer = self.future_scenario
        #for f in layer.getFeatures():
        #    if f.attribute("BuildingID") == self.building_id:
        #        feature = f
        #        break
        self.my_log.log("self.tech_tab.text(0): " + str(self.tech_tab.text(0)))
        for i in range(self.tech_tab.childCount()):
            scope_item = self.tech_tab.child(i)
            for j in range(scope_item.childCount()):
                opex_increment = 0.0
                technology = scope_item.child(j)
                if technology.text(0) in self.solar_technologies:
                    continue
                julia_category = str(technology.data(0, Qt.UserRole))
                file_eta = os.path.realpath(os.path.join(self.work_folder, "../",
                                                         "Input", "eta_" + julia_category + ".csv"))
                file = os.path.join(self.work_folder, "Result_" + julia_category + "_" + self.building_id + ".csv")
                self.my_log.log("file_eta" + str(file_eta))
                self.my_log.log("file julia" + str(file))
                if technology.text(0) in self.variable_eff_el:
                    if os.path.isfile(file_eta) and os.path.isfile(file):
                        julia_data_frame = pandas.read_csv(file, header=None)
                        eta_data_frame = pandas.read_csv(file_eta, header=None)
                        final_energy_frame = julia_data_frame/eta_data_frame
                        self.my_log.log("final_energy_frame", final_energy_frame)
                        for index, row in final_energy_frame.iterrows():
                            try:
                                increment = row[0]
                                if increment == increment and increment > 0:
                                    opex_increment += increment
                            except:
                                self.my_log.log("failed to compute opex increment")
                    self.my_log.log("Increment based on the above files: " + str(opex_increment))
                else:
                    try:
                        efficiency = float(technology.text(5))
                    except:
                        efficiency = 1.0
                    opex_increment = (self.sum_file(file) / efficiency)
                try:
                    coeff = float(technology.text(14))*1000.0
                except:
                    coeff = 1
                self.my_log.log("self.sum_file(file), coeff " + str([self.sum_file(file), coeff]))
                self.my_log.log(
                    "opex_increment * coeff " + str(opex_increment * coeff))
                self.my_log.log("old opex: " + str(opex))
                try:
                    opex = opex + opex_increment * coeff
                except:
                    print("KPIsCalculator, district_pec. Error summing file", file)
        self.my_log.log("opex contribution for building " + str(self.building_id) + " : " + str(opex))

        return self.output_based_on_use(opex, use)

    def output_based_on_use(self, val, use, coeff=1):
        if use is None:
            return val
        if use == "R":
            if self.building_tag == "Residential":
                return val*coeff
        else:
            if not self.building_tag == "Residential":
                return val*coeff
        return 0

    def eco_2_punto_3(self, use=None):
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
        if layer is None:
            return capex
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
                    capex = float(technology.text(8)) * float(technology.text(13))
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
        self.my_log.log("---   district_capex   ---")
        capex = 0
        if self.tech_tab is None:
            return capex
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                traceback.print_exc()
                print("KPIsCalculator, district_capex. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id")
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    tech = self.tech_tab.topLevelItem(i).child(j)

                    # campo capacity x campo fixed_cost
                    try:
                        capex = float(tech.text(8)) * float(tech.text(13))
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

    def eco_1_punto_1(self):
        self.my_log.log("---   eco_1_punto_1   ---")
        try:
            revt = self.KPIs_input["fuel_cost_saving"] + self.KPIs_input["OeM_cost_saving"]
        except:
            revt = 0
        try:
            revtR = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingR"]
        except:
            revtR = 0
        try:
            revtT = self.KPIs_input["fuel_cost_savingT"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtT = 0

        self.my_log.log("self.KPIs_input[\"fuel_cost_saving\"]: " + str(self.KPIs_input["fuel_cost_saving"]))
        self.my_log.log("self.KPIs_input[\"OeM_cost_saving\"]: " + str(self.KPIs_input["OeM_cost_saving"]))
        self.my_log.log("self.KPIs_input[\"fuel_cost_savingR\"]: " + str(self.KPIs_input["fuel_cost_savingR"]))
        self.my_log.log("self.KPIs_input[\"OeM_cost_savingR\"]: " + str(self.KPIs_input["OeM_cost_savingR"]))
        self.my_log.log("self.KPIs_input[\"fuel_cost_savingT\"]: " + str(self.KPIs_input["fuel_cost_savingT"]))
        self.my_log.log("self.KPIs_input[\"OeM_cost_savingT\"]: " + str(self.KPIs_input["OeM_cost_savingT"]))
        self.my_log.log("self.el_sale, self.el_saleR, self.el_saleT: ", self.el_sale, self.el_saleR, self.el_saleT)
        revt += self.el_sale
        revtR += self.el_saleR
        revtT += self.el_saleT
        self.my_log.log("revt: " + str(revt))
        self.my_log.log("revtR: " + str(revtR))
        self.my_log.log("revtT: " + str(revtT))

        try:
            years = int(self.eco_param["years"])
        except:
            years = 5
        try:
            r = self.eco_param["r_factor"]
        except:
            r = 0.11
        caft = revt - self.opex
        self.dcaft = []
        caft0 = -1 * self.capext
        self.dcaft.append(caft0)
        for i in range(1, years + 1):
            self.dcaft.append(caft / ((1 + r) ** i))

        return [self.capext/(revt-self.opex) if not revt == 0 else "Nan",
                self.capextR/(revtR-self.opexR) if not revtR == 0 else "Nan",
                self.capextT/(revtT-self.opexT) if not revtT == 0 else "Nan"]


    def eco_uno_punto_due(self, use=None):
        self.my_log.log("---   eco_uno_punto_due   ---")

        if use is None:
            npv = -self.capext + sum(self.dcaft[1:])
            self.my_log.log("capext: " + str(self.capext))
            self.my_log.log("npv: " + str(npv))
            self.my_log.log("self.dcaft[1:]: " + str(self.dcaft[1:]))
            return npv

        if use == "R":
            npv = -self.capextR + sum(self.dcaftR[1:])
            return round(npv, 2)

        if use == "T":
            npv = -self.capextT + sum(self.dcaftT[1:])
            return round(npv, 2)

        return "Nan"

    def eco_uno_punto_tre(self, use=None):
        self.my_log.log("--- eco_1_punto_3 ---")
        self.my_log.log("use:", use)
        # return self.get_capex(self.baseline_tech_tab, self.future_tech_tab,
        #                       self.baseline_network_tech_tab, self.future_network_tech_tab)
        return self.get_NPV(use)

    def get_NPV(self, use):
        try:
            revt = self.KPIs_input["fuel_cost_saving"] + self.KPIs_input["OeM_cost_saving"]
        except:
            revt = 0
        try:
            revtR = self.KPIs_input["fuel_cost_savingR"] + self.KPIs_input["OeM_cost_savingR"]
        except:
            revtR = 0
        try:
            revtT = self.KPIs_input["fuel_cost_savingT"] + self.KPIs_input["OeM_cost_savingT"]
        except:
            revtT = 0
        caft = revt - self.opex
        caftR = revtR - self.opexR
        caftT = revtT - self.opexT

        try:
            years = self.eco_param["years"]
        except:
            years = 5
        years_nr = int(years)

        if use is None:
            try:
                a = self.capext / caft
            except (ZeroDivisionError, TypeError) as e:
                return "Nan"
            return self.bisezione(a, years_nr)
        if use == "R":
            try:
                a = self.capextR / caftR
            except (ZeroDivisionError, TypeError) as e:
                return "Nan"
            return self.bisezione(a, years_nr)
        if use == "T":
            try:
                a = self.capextT / caftT
            except (ZeroDivisionError, TypeError) as e:
                return "Nan"
            return self.bisezione(a, years_nr)

    def bisezione(self, val, years_nr):
        self.my_log.log("---   bisezione() ---")
        self.my_log.log("val: " + str(val))
        if val == "Nan":
            return "Nan"
        if val < 0:
            return "Nan"
        else:
            # funzione sum(1/(1+r)^i) i={1, ..., years}
            range_calculation = 5

            for attempt in range(20):
                a = attempt * range_calculation
                b = a + range_calculation
                half = (a + b)/2
                flag = True
                i = 0
                self.my_log.log("Attempt " + str(attempt) + ":")
                self.my_log.log("a: " + str(a))
                self.my_log.log("b: " + str(b))
                self.my_log.log("half: " + str(half))
                while flag:
                    i = i + 1
                    tot_a = 0
                    tot_b = 0
                    tot_half = 0

                    for j in range(1, years_nr+1):
                        tot_a = tot_a + 1 / ((1 + a) ** j)
                        tot_b = tot_b + 1 / ((1 + b) ** j)
                        tot_half = tot_half + 1 / ((1 + half) ** j)
                    self.my_log.log("Bisezione - a: " +str(a) + " => " + str(tot_a))
                    self.my_log.log("Bisezione - b: " + str(b) + " => " + str(tot_b))
                    self.my_log.log("Bisezione - half: " + str(half) + " => " + str(tot_half))
                    if val < tot_b and val < tot_a:
                        flag = False
                    if abs(tot_half - val) < 0.01:
                        self.my_log.log("Return: " + str(round(half, 2)))
                        return round(half, 2)
                    else:
                        if tot_half > val:
                            a = half
                        else:
                            b = half
                        half = (a + b) / 2
                    if i > 100:
                        flag = False
        return "Nan"


    def eco_3_punto_1(self, use=None):
        # TODO manca il denominatore
        total = 0
        try:
            years = self.eco_param["years"]
        except:
            years = 5
        try:
            r = self.eco_param["r_factor"]
        except:
            r = 0.11
        years_nr = int(years)

        ued_network = self.h_ued + self.c_ued
        power_sum = 0

        if use is None:
            try:
                total = self.capext + self.opex
                return round(total / ued_network, 2)
            except:
                return "Nan"
        return "-"

    def eco_3_punto_2(self, val, use=None):
        try:
            val = float(val) # ENV_1.2
        except:
            val = 0
        try:
            years = int(self.eco_param["years"])
        except:
            years = 5
        if use is None:
            try:
                return round((self.capext / years + self.opex) / val, 2)
            except:
                return "Nan"
        if use == "R":
            try:
                return round((self.capextR / years + self.opexR) / val, 2)
            except:
                return "Nan"
        if use == "T":
            try:
                return round((self.capextT / years + self.opexT) / val, 2)
            except:
                return "Nan"
            
    def get_t_pollutant_future(self, pec, pollutant_column):
        return self.get_t_pollutant_baseline(pec, pollutant_column)

    def get_t_pollutant_baseline(self, pec, pollutant_column):
        tCO2_baseline = [0.0 for i in range(len(self.sourceName))]
        for k, source in enumerate(self.sourceName):
            tCO2_baseline[k] = pec[k] * self.get_emission_factor(source, pollutant_column)
        return round(sum(tCO2_baseline), 2)

    def get_emission_factor(self, source, column):
        for i in range(self.ef_sources_tab.rowCount()):
            if self.ef_sources_tab.verticalHeaderItem(i).text() == source:
                try:
                    return round(float(self.ef_sources_tab.item(i, column).text().replace(",", ".")), 2)
                except Exception as e:
                    return 0.0
        return 0.0
    
    def get_t_pollutant_sav(self, KPIs, pollutant_column, type="TOT"):
        self.my_log.log("--- get_t_pollutant_sav ---")
        self.my_log.log("pollutant column:", pollutant_column, "type:", type)
        tCO2sav = [0.0 for i in range(len(self.sourceName))]
        adg_base = [0.0 for i in range(len(self.sourceName))]
        fecs = self.get_fec(KPIs)
        index = 0
        if type == "TOT":
            adg_base = self.FECadjBase
            index = 0
        if type == "R":
            adg_base = self.FECadjBaseR
            index = 1
        if type == "T":
            adg_base = self.FECadjBaseT
            index = 2
        for k, source in enumerate(self.sourceName):
            emission_factor = self.get_emission_factor(source, pollutant_column)
            tCO2sav[k] = (adg_base[k] - fecs[index][k]) * emission_factor
            self.my_log.log(source, emission_factor, "adg_base[k]:", adg_base[k], "fec[k]:", fecs[index][k])
        return round(sum(tCO2sav), 2)

    def get_capex(self, baseline_tech_tree, future_tech_tree, _, future_network_tech_tab, district_factor):
        self.my_log.log("--- get_capex ---")
        self.my_log.log(baseline_tech_tree.objectName(), future_tech_tree.objectName())
        capex = 0.0
        capexR = 0.0
        capexT = 0.0
        if future_tech_tree is None or baseline_tech_tree is None:
            return capex
        for i in range(future_tech_tree.topLevelItemCount()):
            for j in range(baseline_tech_tree.topLevelItemCount()):
                self.my_log.log("Comparing", future_tech_tree.topLevelItem(i).building_id,
                                baseline_tech_tree.topLevelItem(j).building_id)
                if future_tech_tree.topLevelItem(i).building_id == baseline_tech_tree.topLevelItem(j).building_id:
                    self.my_log.log("Building FOUND!")
                    contribution = self.capex_building_comparison(baseline_tech_tree.topLevelItem(j),
                                                            future_tech_tree.topLevelItem(i))
                    capex += contribution
                    try:
                        if future_tech_tree.topLevelItem(i).get_sector() == "RES":
                            capexR += contribution
                        if future_tech_tree.topLevelItem(i).get_sector() == "TER":
                            capexT += contribution
                    except Exception:
                        self.my_log("get_sector() failed")
                    self.my_log.log("new capex:", capex)
                    self.my_log.log("new capexR:", capexR)
                    self.my_log.log("new capexT:", capexT)
                    break
            else:
                capex += self.capex_add_full_building_contribution(future_tech_tree.topLevelItem(i))
        for i in range(future_network_tech_tab.topLevelItemCount()):
            for j in range(future_network_tech_tab.topLevelItem(i).childCount()):
                tech = future_network_tech_tab.topLevelItem(i).child(j)
                if tech.data(2, Qt.UserRole) == "new_tech":
                    contribution = NetworkTechCapex.capext(tech)
                    capex += contribution
                    capexR += contribution * district_factor
                    capexT += contribution * (1 - district_factor)
        return capex, capexR, capexT

    def capex_building_comparison(self, baseline_building, future_building):
        capex = 0.0
        # cooling contribution
        capex += self.capex_service_comparison(baseline_building.child(0), future_building.child(0), 0, 5, 8, 13)
        # heating contribution
        capex += self.capex_service_comparison(baseline_building.child(1), future_building.child(1), 0, 5, 8, 13)
        # dhw contribution
        capex += self.capex_service_comparison(baseline_building.child(2), future_building.child(2), 0, 5, 8, 13)
        return capex

    def capex_service_comparison(self, baseline_service, future_service, tech_name_index, efficiency_index,
                                 capacity_index, fixed_cost_index):
        capex = 0.0
        if not baseline_service.text(0) == future_service.text(0):
            print("KPIsCalculator.capex_service_comparison(). Services does not match:",
                  baseline_service.text(0), future_service.text(0))
            return capex
        for i in range(future_service.childCount()):
            future_tech = future_service.child(i)
            for j in range(baseline_service.childCount()):
                baseline_tech = baseline_service.child(j)
                if BuildingTechCapex.compare(baseline_tech, future_tech):
                    break
            else:
                try:
                    capex += BuildingTechCapex.capext(future_tech)
                except ValueError:
                    pass
        return capex

    def capex_add_full_building_contribution(self, building: QTreeWidgetItem):
        capex = 0.0
        for i in range(building.childCount()):
            for j in range(building.child(i).childCount()):
                tech = building.child(i).child(j)
                capex += tech.text(8)*float(tech.text(13))
        return capex

    def get_fec(self, KPIs):
        if self.future_scenario is not None:
            fec = [KPIs["EN_2.3_s" + str(i)] for i in range(len(self.sourceName))]
            fecR = [KPIs["EN_2.3R_s" + str(i)] for i in range(len(self.sourceName))]
            fecT = [KPIs["EN_2.3T_s" + str(i)] for i in range(len(self.sourceName))]
        else:
            fec = [KPIs["EN_2.1_s" + str(i)] for i in range(len(self.sourceName))]
            fecR = [KPIs["EN_2.1R_s" + str(i)] for i in range(len(self.sourceName))]
            fecT = [KPIs["EN_2.1T_s" + str(i)] for i in range(len(self.sourceName))]
        return [fec, fecR, fecT]

    def get_el_sale_increment_district(self):
        self.my_log.log("---   get_el_sale_increment_district   ---")
        time_0 = time.time()
        el_sale = 0
        if self.tech_tab is None:
            return el_sale
        for i in range(self.tech_tab.topLevelItemCount()):
            try:
                item_network_id = str(self.tech_tab.topLevelItem(i).data(0, Qt.UserRole))
            except:
                traceback.print_exc()
                print("KPIsCalculator, get_el_sale_increment_district. Network:", self.network.get_ID(),
                      "Failed to retrieve item_network_id")
                continue
            if item_network_id == self.network.get_ID():
                for j in range(self.tech_tab.topLevelItem(i).childCount()):
                    tech = self.tech_tab.topLevelItem(i).child(j)
                    item_julia_category = str(tech.data(1, Qt.UserRole))
                    if not item_julia_category in ["CHP", "CHP_2"]:
                        break
                    file = os.path.join(self.work_folder, "Results_" + item_julia_category + ".csv")
                    try:
                        el_sale += self.sum_file(file)*float(tech.text(10))*float(tech.text(21))
                    except:
                        self.my_log.log("file")
                        self.my_log.log(file)
                        self.my_log.log("tech.text(10)")
                        self.my_log.log(tech.text(10))
                        self.my_log.log("tech.text(21)")
                        self.my_log.log(tech.text(21))
        self.my_log.log("get_el_sale_increment_district FINITO:", time.time() - time_0)
        return el_sale

    def get_el_sale_increment_building(self):
        self.my_log.log("---   get_el_sale_increment_building   ---")
        el_sale = 0.0
        for i in range(self.tech_tab.childCount()):
            serv = self.tech_tab.child(i)
            for j in range(serv.childCount()):
                tech = serv.child(j)
                item_julia_category = str(tech.data(0, Qt.UserRole))
                if not item_julia_category in ["CHP", "CHP_2"]:
                    break
                file = os.path.join(self.work_folder, "Results_" + item_julia_category + ".csv")
                self.my_log.log("self.sum_file(file): " + str(self.sum_file(file)))
                try:
                    el_sale += self.sum_file(file)*float(tech.text(21)*1000)
                    self.my_log.log("float(tech.text(21): " + str(tech.text(21)))
                except:
                    self.my_log.log("file")
                    self.my_log.log(file)
                    self.my_log.log("tech.text(10)")
                    self.my_log.log(tech.text(10))
                    self.my_log.log("tech.text(21)")
                    self.my_log.log(tech.text(21))
        self.my_log.log("el_sale: " + str(el_sale))
        return el_sale

    def get_UED_networks(self, layer, n_type=None, use=None):
        total = 0
        self.my_log.log("---   get_UED_networks()   ---")
        self.my_log.log("n_type richiesto: " + str(n_type), "WARNING: this parameter is obsolete")

        for f in layer.getFeatures():
            self.my_log.log("loop on building: " + str(f.attribute("BuildingID")) + " with f.id(): " + str(f.id()))
            connected = False
            connection = None
            for item in self.building_connection_map:
                if str(item[0]) == str(f.id()):
                    self.my_log.log("Found item in the connection map. Item:\n " + str(item))
                    if item[2] is not None:
                        connected = True
                        connection = item
                        break
            self.my_log.log("Sentenza: connected? " + str(connected))
            try:
                building_use = "R" if f.attribute("Use") == "Residential" else "T"
            except:
                building_use = None
            self.my_log.log("Uso edificio: " + str(building_use))
            if not connected or connection is None or building_use is None:
                continue

            if connection[2] == "DHN":
                UED_contribution = self.safe_get_float_feature_attribute(f, "AHeatDem") + self.safe_get_float_feature_attribute(f, "ADHWDem")
            elif connection[2] == "DCN":
                UED_contribution = self.safe_get_float_feature_attribute(f, "ACoolDem")
            self.my_log.log("UED_contribution after: " + str(UED_contribution))
            if use is None:
                total += UED_contribution
            elif use == building_use:
                total += UED_contribution
        self.my_log.log("total/1000: " + str(total/1000))
        return total / 1000

    def FECadj_future(self, KPIs):
        self.FECadjBase_s0 = KPIs["EN_2.1_s0"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s1 = KPIs["EN_2.1_s1"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s2 = KPIs["EN_2.1_s2"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s3 = KPIs["EN_2.1_s3"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s4 = KPIs["EN_2.1_s4"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s5 = KPIs["EN_2.1_s5"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s6 = KPIs["EN_2.1_s6"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s7 = KPIs["EN_2.1_s7"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s8 = KPIs["EN_2.1_s8"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s9 = KPIs["EN_2.1_s9"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s10 = KPIs["EN_2.1_s10"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s11 = KPIs["EN_2.1_s11"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s12 = KPIs["EN_2.1_s12"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s13 = KPIs["EN_2.1_s13"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s14 = KPIs["EN_2.1_s14"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s15 = KPIs["EN_2.1_s15"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s16 = KPIs["EN_2.1_s16"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s17 = KPIs["EN_2.1_s17"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s18 = KPIs["EN_2.1_s18"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s19 = KPIs["EN_2.1_s19"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s20 = KPIs["EN_2.1_s20"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s21 = KPIs["EN_2.1_s21"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBase_s22 = KPIs["EN_2.1_s22"] * (1 + self.eco_param["demo_factor"])

        self.FECadjBaseR_s0 = KPIs["EN_2.1R_s0"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s1 = KPIs["EN_2.1R_s1"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s2 = KPIs["EN_2.1R_s2"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s3 = KPIs["EN_2.1R_s3"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s4 = KPIs["EN_2.1R_s4"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s5 = KPIs["EN_2.1R_s5"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s6 = KPIs["EN_2.1R_s6"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s7 = KPIs["EN_2.1R_s7"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s8 = KPIs["EN_2.1R_s8"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s9 = KPIs["EN_2.1R_s9"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s10 = KPIs["EN_2.1R_s10"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s11 = KPIs["EN_2.1R_s11"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s12 = KPIs["EN_2.1R_s12"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s13 = KPIs["EN_2.1R_s13"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s14 = KPIs["EN_2.1R_s14"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s15 = KPIs["EN_2.1R_s15"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s16 = KPIs["EN_2.1R_s16"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s17 = KPIs["EN_2.1R_s17"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s18 = KPIs["EN_2.1R_s18"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s19 = KPIs["EN_2.1R_s19"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s20 = KPIs["EN_2.1R_s20"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s21 = KPIs["EN_2.1R_s21"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseR_s22 = KPIs["EN_2.1R_s22"] * (1 + self.eco_param["demo_factor"])

        self.FECadjBaseT_s0 = KPIs["EN_2.1T_s0"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s1 = KPIs["EN_2.1T_s1"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s2 = KPIs["EN_2.1T_s2"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s3 = KPIs["EN_2.1T_s3"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s4 = KPIs["EN_2.1T_s4"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s5 = KPIs["EN_2.1T_s5"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s6 = KPIs["EN_2.1T_s6"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s7 = KPIs["EN_2.1T_s7"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s8 = KPIs["EN_2.1T_s8"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s9 = KPIs["EN_2.1T_s9"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s10 = KPIs["EN_2.1T_s10"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s11 = KPIs["EN_2.1T_s11"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s12 = KPIs["EN_2.1T_s12"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s13 = KPIs["EN_2.1T_s13"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s14 = KPIs["EN_2.1T_s14"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s15 = KPIs["EN_2.1T_s15"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s16 = KPIs["EN_2.1T_s16"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s17 = KPIs["EN_2.1T_s17"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s18 = KPIs["EN_2.1T_s18"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s19 = KPIs["EN_2.1T_s19"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s20 = KPIs["EN_2.1T_s20"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s21 = KPIs["EN_2.1T_s21"] * (1 + self.eco_param["demo_factor"])
        self.FECadjBaseT_s22 = KPIs["EN_2.1T_s22"] * (1 + self.eco_param["demo_factor"])

        self.FECadjBase = [self.FECadjBase_s0, self.FECadjBase_s1, self.FECadjBase_s2, self.FECadjBase_s3,
                           self.FECadjBase_s4, self.FECadjBase_s5, self.FECadjBase_s6, self.FECadjBase_s7,
                           self.FECadjBase_s8, self.FECadjBase_s9, self.FECadjBase_s10, self.FECadjBase_s11,
                           self.FECadjBase_s12, self.FECadjBase_s13, self.FECadjBase_s14, self.FECadjBase_s15,
                           self.FECadjBase_s16, self.FECadjBase_s17, self.FECadjBase_s18, self.FECadjBase_s19,
                           self.FECadjBase_s20, self.FECadjBase_s21, self.FECadjBase_s22]
        self.FECadjBaseR = [self.FECadjBaseR_s0, self.FECadjBaseR_s1, self.FECadjBaseR_s2, self.FECadjBaseR_s3,
                            self.FECadjBaseR_s4, self.FECadjBaseR_s5, self.FECadjBaseR_s6, self.FECadjBaseR_s7,
                            self.FECadjBaseR_s8, self.FECadjBaseR_s9, self.FECadjBaseR_s10, self.FECadjBaseR_s11,
                            self.FECadjBaseR_s12, self.FECadjBaseR_s13, self.FECadjBaseR_s14, self.FECadjBaseR_s15,
                            self.FECadjBaseR_s16, self.FECadjBaseR_s17, self.FECadjBaseR_s18, self.FECadjBaseR_s19,
                            self.FECadjBaseR_s20, self.FECadjBaseR_s21, self.FECadjBaseR_s22]
        self.FECadjBaseT = [self.FECadjBaseT_s0, self.FECadjBaseT_s1, self.FECadjBaseT_s2, self.FECadjBaseT_s3,
                            self.FECadjBaseT_s4, self.FECadjBaseT_s5, self.FECadjBaseT_s6, self.FECadjBaseT_s7,
                            self.FECadjBaseT_s8, self.FECadjBaseT_s9, self.FECadjBaseT_s10, self.FECadjBaseT_s11,
                            self.FECadjBaseT_s12, self.FECadjBaseT_s13, self.FECadjBaseT_s14, self.FECadjBaseT_s15,
                            self.FECadjBaseT_s16, self.FECadjBaseT_s17, self.FECadjBaseT_s18, self.FECadjBaseT_s19,
                            self.FECadjBaseT_s20, self.FECadjBaseT_s21, self.FECadjBaseT_s22]

    def get_UED_heating(self, layer, use=None):
        total = 0
        try:
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
        except:
            traceback.print_exc()
            return total / 1000
        return total / 1000

    def get_UED_network(self, service, status):
        total = 0.0
        if self.network.optimized_buildings_layer is None:
            return total
        attributes = []
        if service == "All":
            attributes.append("ACoolDem")
            attributes.append("AHeatDem")
            attributes.append("ADHWDem")
        elif service == "Cooling":
            attributes.append("ACoolDem")
        else:
            attributes.append("AHeatDem")
            attributes.append("ADHWDem")
        for f in self.network.optimized_buildings_layer.getFeatures():
            if str(f.attribute("Status")) == str(status):
                for attribute in attributes:
                    try:
                        total = total + float(f.attribute(attribute))
                    except:
                        pass
        self.my_log.log("---   get_UED_network   ---")
        self.my_log.log("network id: " + str(self.network.get_ID()))
        self.my_log.log("status: " + str(status))
        self.my_log.log("service: " + str(service))
        self.my_log.log("attributes: " + str(attributes))
        self.my_log.log("total: " + str(total/1000))
        return total/1000

    def FECadj_future(self, KPIs):
        uno_plus_demo_factor = 1 + self.eco_param["demo_factor"]
        self.FECadjBase_s0 = KPIs["EN_2.1_s0"] * uno_plus_demo_factor
        self.FECadjBase_s1 = KPIs["EN_2.1_s1"] * uno_plus_demo_factor
        self.FECadjBase_s2 = KPIs["EN_2.1_s2"] * uno_plus_demo_factor
        self.FECadjBase_s3 = KPIs["EN_2.1_s3"] * uno_plus_demo_factor
        self.FECadjBase_s4 = KPIs["EN_2.1_s4"] * uno_plus_demo_factor
        self.FECadjBase_s5 = KPIs["EN_2.1_s5"] * uno_plus_demo_factor
        self.FECadjBase_s6 = KPIs["EN_2.1_s6"] * uno_plus_demo_factor
        self.FECadjBase_s7 = KPIs["EN_2.1_s7"] * uno_plus_demo_factor
        self.FECadjBase_s8 = KPIs["EN_2.1_s8"] * uno_plus_demo_factor
        self.FECadjBase_s9 = KPIs["EN_2.1_s9"] * uno_plus_demo_factor
        self.FECadjBase_s10 = KPIs["EN_2.1_s10"] * uno_plus_demo_factor
        self.FECadjBase_s11 = KPIs["EN_2.1_s11"] * uno_plus_demo_factor
        self.FECadjBase_s12 = KPIs["EN_2.1_s12"] * uno_plus_demo_factor
        self.FECadjBase_s13 = KPIs["EN_2.1_s13"] * uno_plus_demo_factor
        self.FECadjBase_s14 = KPIs["EN_2.1_s14"] * uno_plus_demo_factor
        self.FECadjBase_s15 = KPIs["EN_2.1_s15"] * uno_plus_demo_factor
        self.FECadjBase_s16 = KPIs["EN_2.1_s16"] * uno_plus_demo_factor
        self.FECadjBase_s17 = KPIs["EN_2.1_s17"] * uno_plus_demo_factor
        self.FECadjBase_s18 = KPIs["EN_2.1_s18"] * uno_plus_demo_factor
        self.FECadjBase_s19 = KPIs["EN_2.1_s19"] * uno_plus_demo_factor
        self.FECadjBase_s20 = KPIs["EN_2.1_s20"] * uno_plus_demo_factor
        self.FECadjBase_s21 = KPIs["EN_2.1_s21"] * uno_plus_demo_factor
        self.FECadjBase_s22 = KPIs["EN_2.1_s22"] * uno_plus_demo_factor

        self.FECadjBaseR_s0 = KPIs["EN_2.1R_s0"] * uno_plus_demo_factor
        self.FECadjBaseR_s1 = KPIs["EN_2.1R_s1"] * uno_plus_demo_factor
        self.FECadjBaseR_s2 = KPIs["EN_2.1R_s2"] * uno_plus_demo_factor
        self.FECadjBaseR_s3 = KPIs["EN_2.1R_s3"] * uno_plus_demo_factor
        self.FECadjBaseR_s4 = KPIs["EN_2.1R_s4"] * uno_plus_demo_factor
        self.FECadjBaseR_s5 = KPIs["EN_2.1R_s5"] * uno_plus_demo_factor
        self.FECadjBaseR_s6 = KPIs["EN_2.1R_s6"] * uno_plus_demo_factor
        self.FECadjBaseR_s7 = KPIs["EN_2.1R_s7"] * uno_plus_demo_factor
        self.FECadjBaseR_s8 = KPIs["EN_2.1R_s8"] * uno_plus_demo_factor
        self.FECadjBaseR_s9 = KPIs["EN_2.1R_s9"] * uno_plus_demo_factor
        self.FECadjBaseR_s10 = KPIs["EN_2.1R_s10"] * uno_plus_demo_factor
        self.FECadjBaseR_s11 = KPIs["EN_2.1R_s11"] * uno_plus_demo_factor
        self.FECadjBaseR_s12 = KPIs["EN_2.1R_s12"] * uno_plus_demo_factor
        self.FECadjBaseR_s13 = KPIs["EN_2.1R_s13"] * uno_plus_demo_factor
        self.FECadjBaseR_s14 = KPIs["EN_2.1R_s14"] * uno_plus_demo_factor
        self.FECadjBaseR_s15 = KPIs["EN_2.1R_s15"] * uno_plus_demo_factor
        self.FECadjBaseR_s16 = KPIs["EN_2.1R_s16"] * uno_plus_demo_factor
        self.FECadjBaseR_s17 = KPIs["EN_2.1R_s17"] * uno_plus_demo_factor
        self.FECadjBaseR_s18 = KPIs["EN_2.1R_s18"] * uno_plus_demo_factor
        self.FECadjBaseR_s19 = KPIs["EN_2.1R_s19"] * uno_plus_demo_factor
        self.FECadjBaseR_s20 = KPIs["EN_2.1R_s20"] * uno_plus_demo_factor
        self.FECadjBaseR_s21 = KPIs["EN_2.1R_s21"] * uno_plus_demo_factor
        self.FECadjBaseR_s22 = KPIs["EN_2.1R_s22"] * uno_plus_demo_factor

        self.FECadjBaseT_s0 = KPIs["EN_2.1T_s0"] * uno_plus_demo_factor
        self.FECadjBaseT_s1 = KPIs["EN_2.1T_s1"] * uno_plus_demo_factor
        self.FECadjBaseT_s2 = KPIs["EN_2.1T_s2"] * uno_plus_demo_factor
        self.FECadjBaseT_s3 = KPIs["EN_2.1T_s3"] * uno_plus_demo_factor
        self.FECadjBaseT_s4 = KPIs["EN_2.1T_s4"] * uno_plus_demo_factor
        self.FECadjBaseT_s5 = KPIs["EN_2.1T_s5"] * uno_plus_demo_factor
        self.FECadjBaseT_s6 = KPIs["EN_2.1T_s6"] * uno_plus_demo_factor
        self.FECadjBaseT_s7 = KPIs["EN_2.1T_s7"] * uno_plus_demo_factor
        self.FECadjBaseT_s8 = KPIs["EN_2.1T_s8"] * uno_plus_demo_factor
        self.FECadjBaseT_s9 = KPIs["EN_2.1T_s9"] * uno_plus_demo_factor
        self.FECadjBaseT_s10 = KPIs["EN_2.1T_s10"] * uno_plus_demo_factor
        self.FECadjBaseT_s11 = KPIs["EN_2.1T_s11"] * uno_plus_demo_factor
        self.FECadjBaseT_s12 = KPIs["EN_2.1T_s12"] * uno_plus_demo_factor
        self.FECadjBaseT_s13 = KPIs["EN_2.1T_s13"] * uno_plus_demo_factor
        self.FECadjBaseT_s14 = KPIs["EN_2.1T_s14"] * uno_plus_demo_factor
        self.FECadjBaseT_s15 = KPIs["EN_2.1T_s15"] * uno_plus_demo_factor
        self.FECadjBaseT_s16 = KPIs["EN_2.1T_s16"] * uno_plus_demo_factor
        self.FECadjBaseT_s17 = KPIs["EN_2.1T_s17"] * uno_plus_demo_factor
        self.FECadjBaseT_s18 = KPIs["EN_2.1T_s18"] * uno_plus_demo_factor
        self.FECadjBaseT_s19 = KPIs["EN_2.1T_s19"] * uno_plus_demo_factor
        self.FECadjBaseT_s20 = KPIs["EN_2.1T_s20"] * uno_plus_demo_factor
        self.FECadjBaseT_s21 = KPIs["EN_2.1T_s21"] * uno_plus_demo_factor
        self.FECadjBaseT_s22 = KPIs["EN_2.1T_s22"] * uno_plus_demo_factor

        self.FECadjBase = [self.FECadjBase_s0, self.FECadjBase_s1, self.FECadjBase_s2, self.FECadjBase_s3,
                           self.FECadjBase_s4, self.FECadjBase_s5, self.FECadjBase_s6, self.FECadjBase_s7,
                           self.FECadjBase_s8, self.FECadjBase_s9, self.FECadjBase_s10, self.FECadjBase_s11,
                           self.FECadjBase_s12, self.FECadjBase_s13, self.FECadjBase_s14, self.FECadjBase_s15,
                           self.FECadjBase_s16, self.FECadjBase_s17, self.FECadjBase_s18, self.FECadjBase_s19,
                           self.FECadjBase_s20, self.FECadjBase_s21, self.FECadjBase_s22]
        self.FECadjBaseR = [self.FECadjBaseR_s0, self.FECadjBaseR_s1, self.FECadjBaseR_s2, self.FECadjBaseR_s3,
                            self.FECadjBaseR_s4, self.FECadjBaseR_s5, self.FECadjBaseR_s6, self.FECadjBaseR_s7,
                            self.FECadjBaseR_s8, self.FECadjBaseR_s9, self.FECadjBaseR_s10, self.FECadjBaseR_s11,
                            self.FECadjBaseR_s12, self.FECadjBaseR_s13, self.FECadjBaseR_s14, self.FECadjBaseR_s15,
                            self.FECadjBaseR_s16, self.FECadjBaseR_s17, self.FECadjBaseR_s18, self.FECadjBaseR_s19,
                            self.FECadjBaseR_s20, self.FECadjBaseR_s21, self.FECadjBaseR_s22]
        self.FECadjBaseT = [self.FECadjBaseT_s0, self.FECadjBaseT_s1, self.FECadjBaseT_s2, self.FECadjBaseT_s3,
                            self.FECadjBaseT_s4, self.FECadjBaseT_s5, self.FECadjBaseT_s6, self.FECadjBaseT_s7,
                            self.FECadjBaseT_s8, self.FECadjBaseT_s9, self.FECadjBaseT_s10, self.FECadjBaseT_s11,
                            self.FECadjBaseT_s12, self.FECadjBaseT_s13, self.FECadjBaseT_s14, self.FECadjBaseT_s15,
                            self.FECadjBaseT_s16, self.FECadjBaseT_s17, self.FECadjBaseT_s18, self.FECadjBaseT_s19,
                            self.FECadjBaseT_s20, self.FECadjBaseT_s21, self.FECadjBaseT_s22]

    def add_networks_area_contribution(self, active_scenario_layer):
        try:
            if active_scenario_layer is None:
                return
            for feature in active_scenario_layer.getFeatures():
                for building_mapped in self.building_connection_map:
                    if building_mapped[0] == feature.id():
                        if building_mapped[2] is not None:
                            areaR_old = self.areaR
                            self.area += float(feature.attribute("GrossFA"))
                            self.areaR += float(feature.attribute("GrossFA")) if feature.attribute(
                                "Use") == "Residential" else 0
                            self.my_log.log(
                                "areaR contribution network: " + str(self.areaR - areaR_old))
        except Exception:
            self.area = 1.0
            self.areaR = 1.0
            self.my_log.log("FATAL ERROR during area calculation!: ")
            traceback.print_exc