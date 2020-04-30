import json

import math

from PyQt5.QtCore import Qt, QVariant

import os.path
import time
import copy

# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import os
import os.path

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QPushButton)
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

# Import PyQt5
from PyQt5.QtWidgets import QLabel
# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.core import QgsProject

# Import the custom tree widget items
from .KPIsCalculator import KPIsCalculator
from .base_tech import *
from .district.heating.Booster_heat_pump_COP import Booster_COP
from .district.heating.Waste_heat_heat_pumps_heating import generate_file_Waste_heat_pump_heating
from .single_building.Dem_cool_heating import gen_dem_time_district
from .checks.JuliaOutputChecker import JuliaOutputChecker
from .checks.JuliaBuildingsChecker import JuliaBuildingChecker
from .test.MyLog import MyLog

from .Heat_pump_COP import generate_fileEta_forJulia
from .Heat_pump_cool_COP import genera_file_etaHP_cool

from ..utility.pvgis.PvgisApi import PvgisApi
from .services.PvgisParamsAdapter import PvgisParamsAdapter

from .. import master_planning_config as mp_config
from ..building.Building import Building
from .Solar_thermal_production import generate_solar_thermal_forJulia
from .services.SolarParameterBuilder import SolarParameterBuilder

from ..python_julia_interface import JuliaQgisInterface


class DistrictSimulator:

    # These lists are essential. Maybe put them in a config file?
    heat_only_boiler = ["Gas Boiler", "Biomass Boiler", "Oil Boiler", "Boiler"]  #[0]
    electrical_heater = ["Electrical Heater"] #[1]
    heat_pump = ["Air Source Compression Heat Pump","Shallow geothermal compression heat pump", "Heat pump"] #[2]
    cogeneration = ["Gas CHP", "Oil CHP", "Biomass CHP", "Cogeneration"] #[3]
    solar_thermal = ["Flat plate solar collectors", "Evacuated tube solar collectors"] #[4]
    cooling_heat_pump = ["Air source compression chiller", "Shallow geothermal compression chiller"] #[5]
    combined_heat_pump = []  #[6]
    thermal_energy_storage = ["Thermal energy storage"]  #[7]

    domestic_hot_water_thermal_energy_storage = ["DHW thermal energy storage"] #[8]

    absorption_heat_pump = ["Air source gas absorption heat pump", "Shallow geothermal gas absorption heat pump","Absorption heat pump"] #[9]

    waste_heat_heat_exchangers = ["Deep geothermal HEX", "Industrial waste heat HEX", "Waste heat – HEX"] #[10]
    waste_cooling_heat_exchangers = ["Waste cooling heat exchanger","Waste cooling – HEX"] #[11]
    waste_heat_heat_pumps_temperature_group1 = ["waste_heat_heat_pumps_temperature_group1", "Waste Heat Compression Heat Pump Low T"] #[12]
    waste_heat_heat_pumps_temperature_group2 = ["waste_heat_heat_pumps_temperature_group2", "Waste Heat Compression Heat Pump Medium T"]#[13]
    waste_heat_heat_pumps_temperature_group3 = ["waste_heat_heat_pumps_temperature_group3", "Waste Heat Compression Heat Pump High T"]#[14]
    ORC_cogeneration = ["Industrial waste heat ORC", "Deep geothermal ORC", "Gas ORC", "Biomass ORC"] #[15]
    seasonal_solar_thermal = ["Seasonal Solar Thermal"] #[16]
    seasonal_waste_heat_pump = ["Seasonal waste heat heat pumps"] #[17]
    waste_heat_absorption_heat_pump = ["Waste heat absorption heat pump"] #[18]
    seasonal_thermal_energy_storage = ["Seasonal thermal energy storage"] #[19]
    absorption_cooling_heat_pump = ["Air source gas absorption chiller", "Shallow geothermal Gas absorption chiller"]

    individual_H_C_dict_var = {"heat only boiler": heat_only_boiler, #0
                               "electrical heater": electrical_heater, # 1
                               "heat pump": heat_pump, #2
                               "cogeneration": cogeneration, #3
                               "solar thermal": solar_thermal, #4
                               "cooling heat pump": cooling_heat_pump, #5
                               "combined heat pump": combined_heat_pump, #6
                               "thermal energy storage": thermal_energy_storage, #7
                               "domestic hot water thermal energy storage": domestic_hot_water_thermal_energy_storage, #8
                               "waste_heat_heat_pumps_temperature_group1": waste_heat_heat_pumps_temperature_group1, #9
                               "waste_heat_heat_pumps_temperature_group2": waste_heat_heat_pumps_temperature_group2, #10
                               "waste_heat_heat_pumps_temperature_group3": waste_heat_heat_pumps_temperature_group3, #11
                               "Absorption heat pump": absorption_heat_pump, #12
                               "absorption cooling heat pump": absorption_cooling_heat_pump #13
                               }

    district_C_dict_var = {"heat only boiler": heat_only_boiler,
                           "heat pump": heat_pump,
                           "cogeneration": cogeneration,
                           "thermal energy storage": thermal_energy_storage,
                           "absorption_heat_pump": absorption_heat_pump,
                           "waste_heat_heat_exchangers": waste_heat_heat_exchangers,
                           "waste_cooling_heat_exchangers": waste_cooling_heat_exchangers,
                           "waste_heat_heat_pumps_temperature_group1": waste_heat_heat_pumps_temperature_group1,
                           "waste_heat_heat_pumps_temperature_group2": waste_heat_heat_pumps_temperature_group2,
                           "waste_heat_heat_pumps_temperature_group3": waste_heat_heat_pumps_temperature_group3
                           }

    district_H_dict_var = {"heat only boiler": heat_only_boiler,
                           "electrical heater": electrical_heater,
                           "heat pump": heat_pump,
                           "cogeneration": cogeneration,
                           "absorption_heat_pump": absorption_heat_pump,
                           "solar thermal": solar_thermal,
                           "seasonal solar thermal": seasonal_solar_thermal,
                           "waste_heat_heat_exchangers": waste_heat_heat_exchangers,
                           "waste_heat_heat_pumps_temperature_group1": waste_heat_heat_pumps_temperature_group1,
                           "waste_heat_heat_pumps_temperature_group2": waste_heat_heat_pumps_temperature_group2,
                           "waste_heat_heat_pumps_temperature_group3": waste_heat_heat_pumps_temperature_group3,
                           "seasonal waste heat pump": seasonal_waste_heat_pump,
                           "waste heat absorption heat pump": waste_heat_absorption_heat_pump,
                           "thermal energy storage": thermal_energy_storage,
                           "seasonal thermal energy storage": seasonal_thermal_energy_storage,
                           "ORC cogeneration": ORC_cogeneration
                           }

    district_function = {"heat only boiler": heat_only_boiler,  # [0]
                         "electrical heater":electrical_heater,  # [1]
                         "heat pump": heat_pump,  # [2]
                         "cogeneration":cogeneration,  # [3]
                         "solar thermal":solar_thermal,  # [4]
                         "seasonal solar thermal": seasonal_solar_thermal,  # [5]
                         "absorption_heat_pump":absorption_heat_pump,  # [6]
                         "waste_heat_heat_exchangers":waste_heat_heat_exchangers,  # [7]
                         "waste_cooling_heat_exchangers":waste_cooling_heat_exchangers,  # [8]
                         "waste_heat_heat_pumps_temperature_group1":waste_heat_heat_pumps_temperature_group1,
                         # [9]
                         "waste_heat_heat_pumps_temperature_group2":waste_heat_heat_pumps_temperature_group2,
                         # [10]
                         "waste_heat_heat_pumps_temperature_group3":waste_heat_heat_pumps_temperature_group3,
                         # [11]
                         "thermal energy storage": thermal_energy_storage,  # [12]
                         "seasonal waste heat pump": seasonal_waste_heat_pump,  # [13]
                         "seasonal thermal energy storage": seasonal_thermal_energy_storage,  # [14]
                         "waste heat absorption heat pump": waste_heat_absorption_heat_pump,  # [15]
                         "ORC cogeneration": ORC_cogeneration  # 16
                         }

    work_directory = ""

    def __init__(self):
        self.sim_time = 0
        self.baseline_tech_tab = None
        self.baseline_tech_tab2 = None
        self.baseline_network_tech_tab = None
        self.future_tech_tab = None
        self.future_network_tech_tab = None

        self.DHN_network_list = None
        self.DCN_network_list = None
        self.sources_tab = None
        self.ef_sources_tab = None
        self.sources = None
        self.step1_network_tree_widget = None
        self.step1_building_tree_widget: QTreeWidget = None
        self.step4_network_tree_widget = None
        self.step4_building_tree_widget: QTreeWidget = None
        self.step0_district_sources_tab = None

        self.baseline_KPIs = None
        self.KPIs_additional_data = None

        self.logger = None

        self.baseline_scenario = None
        self.future_scenario = None

        self.j = None

        self.h8760 = 8760

        self.heat = None
        self.temperature = None

        self.pvgis_api: PvgisApi = None

        self.tech_infos_district_heating = None
        self.tech_infos_district_cooling = None
        self.tech_infos_individual = None
        self.district_H_dict_func = {"heat only boiler": self.DHN_heat_only_boiler,
                                     "electrical heater": self.DHN_electrical_heater,
                                     "heat pump": self.DHN_heat_pump,
                                     "cogeneration": self.DHN_cogeneration,
                                     "absorption_heat_pump": self.DHN_absorption_heat_pump,
                                     "solar thermal": self.DHN_add_solar_thermal,
                                     "seasonal solar thermal": self.DHN_seasonal_solar_thermal,
                                     "waste_heat_heat_exchangers": self.DHN_waste_heat_heat_exchangers,
                                     "waste_heat_heat_pumps_temperature_group1": self.DHN_waste_heat_heat_pumps_temperature_group1,
                                     "waste_heat_heat_pumps_temperature_group2": self.DHN_waste_heat_heat_pumps_temperature_group2,
                                     "waste_heat_heat_pumps_temperature_group3": self.DHN_waste_heat_heat_pumps_temperature_group3,
                                     "seasonal waste heat pump": self.DHN_seasonal_waste_heat_pump,
                                     "waste heat absorption heat pump": self.DHN_waste_heat_absorption_heat_pump,
                                     "thermal energy storage": self.DHN_thermal_energy_storage,
                                     "seasonal thermal energy storage": self.DHN_seasonal_thermal_energy_storage,
                                     "ORC cogeneration": self.DHN_ORC_cogeneration   # 16
                                     }

        self.district_C_dict_func = {"heat only boiler": self.DCN_heat_only_boiler,
                                     "heat pump": self.DCN_heat_pump,
                                     "cogeneration": self.DCN_cogeneration,
                                     "thermal energy storage": self.DCN_thermal_energy_storage,
                                     "absorption_heat_pump": self.DCN_absorption_heat_pump,
                                     "waste_heat_heat_exchangers": self.DCN_waste_heat_heat_exchangers,
                                     "waste_cooling_heat_exchangers": self.DCN_waste_cooling_heat_exchangers,
                                     "waste_heat_heat_pumps_temperature_group1": self.DCN_waste_heat_heat_pumps_temperature_group1,
                                     "waste_heat_heat_pumps_temperature_group2": self.DCN_waste_heat_heat_pumps_temperature_group2,
                                     "waste_heat_heat_pumps_temperature_group3": self.DCN_waste_heat_heat_pumps_temperature_group3
                                     }

        self.individual_H_C_dict_func = {"heat only boiler": self.add_heat_only_boiler,
                                         "electrical heater": self.add_electrical_heater,
                                         "heat pump": self.add_heat_pump,
                                         "cogeneration": self.add_cogeneration,
                                         "solar thermal": self.add_solar_thermal,
                                         "cooling heat pump": self.add_cooling_heat_pump,
                                         "combined heat pump": self.add_combined_heat_pump,
                                         "thermal energy storage": self.add_thermal_energy_storage,
                                         "domestic hot water thermal energy storage": self.add_domestic_hot_water_thermal_energy_storage,
                                         "Absorption heat pump": self.add_absorption_heat_pump,
                                         "absorption cooling heat pump": self.add_absorption_cooling_heat_pump
                                         }

        self.sources_for_technology = [' ', #[0]
                                       'Biomass Forestry',  #[1]
                                       'Solar thermal', #[2]
                                       'Deep geothermal' ,#[3]
                                       'Excess heat Industrial', #[4]
                                       'Air', #[5]
                                       'Rivers - Lakes - Waste water', #[6]
                                       'Excess cooling - LNG terminals', #[7]
                                       'Geothermal - Shallow - Ground cold extraction', #[8]
                                       'Natural gas',  # [9]
                                       'Heating Oil',  # [10]
                                       'Electricity',  # [11]
                                       'Geothermal - Shallow - Ground heat extraction',  # 12
                                       'Geothermal - Shallow - Ground heat extraction',  # 13
                                       'Excess heat Industry',  # 14
                                       'Excess heat - Data centers',  # 15
                                       'Excess heat - Supermarkets',  # 16
                                       'Excess heat - Refrigerated storage facilities',  # 17
                                       'Excess heat - Indoor carparkings',  # 18
                                       'Excess heat - Subway networks',  # 19
                                       'Urban waste water treatment plant',  # [20]
                                       'Water - Surface water - Lakes heat extraction with heat pump' ,#21
                                       'Water - Waste water - Sewer system', #22
                                       'Gas', #23
                                       'Oil', #24
                                       'Water - Surface water - Rivers cold extraction heat pump', #25
                                       'Water - Surface water - Rivers cold extraction from free cooling HEX', #26
                                       'Water - Surface water - Lakes cold extraction with heat pump', #27
                                       'Water - Surface water - Rivers heat extraction heat pump' #28
                                       ]

        self.technology_for_cooling = ['Air source compression chiller', #[0]
                                       'Shallow geothermal compression chiller', #[1]
                                       'Air source gas absorption chiller',#[2]
                                       'Shallow geothermal Gas absorption chiller'] #[3]


        self.technology_for_absorption = ['Boiler',
                                          'Cogeneration',
                                         'Waste heat – HEX']
        self.booster = Booster_COP()

        self.selected_source = ""
        self.julia_output_checker = None
        self.calc = KPIsCalculator()


    def close_simulation(self, KPIs_baseline=None):
        return self.calc.close_calculation(KPIs_baseline)

    def set_up_new_simulation(self):
        self.calc.reset(True)
        self.tech_infos_district_heating = create_base_tech_district()
        self.tech_infos_district_cooling = create_base_tech_cooling()
        self.tech_infos_individual = create_base_tech_infos()

        self.calc.input_reset()
        self.calc.baseline_tech_tab = self.step1_building_tree_widget
        self.calc.baseline_tech_tab2 = self.baseline_tech_tab2
        self.calc.future_tech_tab = self.future_tech_tab
        self.calc.future_network_tech_tab = self.future_network_tech_tab
        self.calc.baseline_network_tech_tab = self.baseline_network_tech_tab
        self.calc.pef_sources_tab = self.sources_tab
        self.calc.ef_sources_tab = self.ef_sources_tab

        self.calc.step0_district_sources_tab = self.step0_district_sources_tab
        self.calc.baseline_scenario = self.baseline_scenario
        self.calc.future_scenario = self.future_scenario
        self.calc.sources = self.sources
        self.calc.district_tech_power_column = 8
        self.calc.individual_tech_power_column = 8

        self.calc.KPIs_input = copy.deepcopy(self.baseline_KPIs)
        self.calc.KPIs_additional_data = self.KPIs_additional_data

        if self.baseline_scenario is not None:
            self.calc.building_connection_map = self.get_buildings_connection_list(self.baseline_scenario)
        else:
            self.calc.building_connection_map = self.get_buildings_connection_list(self.future_scenario)
        self.calc.initialize()
        self.calc.initialize_YEOHbase()

    def run_buildings(self, buildings, dr, log: MyLog):
        self.sim_time = time.time()
        log.log("BUILDING SIMULATION STARTS")
        self.work_directory = dr
        self.calc.work_folder = os.path.join(dr, "Results")
        self.julia_output_checker = JuliaOutputChecker(os.path.join(dr, "Results"))
        self.julia_output_checker.clear_report()
        if self.baseline_scenario is not None:
            layer = self.baseline_scenario
        else:
            layer = self.future_scenario
        building_counter = 0
        buildings_connection_checker = JuliaBuildingChecker()
        log.log("Buildings:", buildings)
        for building in buildings:
            log.log("Checking building:", building)
            building_counter += 1
            if building_counter < 0:
                continue
            if buildings_connection_checker.building_needs_simulation(
                    self.step1_building_tree_widget if self.step1_building_tree_widget is not None else self.step4_building_tree_widget,
                    building, log=log):
                log.log("Iteration:", str(building_counter), "/", str(len(buildings)))
                log.log("Start computing building " + str(building) + ". Time: " + str(
                    time.time() - self.sim_time) + " seconds.")
                item = self.single_building_simulation(dr, building, log)
                log.log("Computation of building " + str(building) + " done. Time: " + str(
                    time.time() - self.sim_time) + " seconds.")
                if item is None:
                    log.log("DistrictSimulator.py, run_buildings: item is None for building_id:", building)
                    continue
                self.calc.building_id = building
                self.calc.tech_tab = item
                for feature in layer.getFeatures():
                    if str(feature.attribute("BuildingID")) == str(building):
                        if str(feature.attribute("Use")) == "Residential":
                            self.calc.building_tag = "Residential"
                        else:
                            self.calc.building_tag = "Tertiary"
                log.log(
                    "Computation of KPIs contribution for building " + str(building) + " starts. Time: " + str(
                        time.time() - self.sim_time) + " seconds.")
                self.calc.individual_KPIs_update()
                log.log(
                    "Computation of KPIs contribution for building " + str(building) + " done. Time: " + str(
                        time.time() - self.sim_time) + " seconds.")
        self.julia_output_checker.check()
        self.julia_output_checker.visualize()

    def run_district(self, dr):
        district_log = MyLog(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test", "log", "last_district_log.txt"))
        time_0 = time.time()
        self.work_directory = dr
        if self.step1_network_tree_widget is not None:
            self.calc.tech_tab = self.step1_network_tree_widget
        else:
            self.calc.tech_tab = self.step4_network_tree_widget

        result_folder = os.path.join(dr, "heating", "Results")
        self.julia_output_checker = JuliaOutputChecker(result_folder)
        input_folder = os.path.join(dr, "heating", "input")
        print("DistrictSimulator.run_district() dr:", dr)
        self.calc.work_folder = result_folder
        print("DistrictSimulator.py, run_district(). DHN and DCN", [n.name for n in self.DHN_network_list],
              [n.name for n in self.DCN_network_list])
        for network in self.DHN_network_list:
            district_log.log("STARTING COMPUTING DHN NETWORKS", network.name, "RELATIVE TIME:",
                             str(time.time() - time_0))
            self.gen_default_julia_files(input_folder)
            district_log.log("default julia files done", "RELATIVE TIME:", str(time.time()-time_0))
            self.calc.network = network
            print('!! network.buildings_layer', network.buildings_layer)

            district_log.log("Starting simulation...", "RELATIVE TIME:", str(time.time() - time_0))
            self.district_heating_simulation(input_folder, result_folder, network=network, log=district_log)
            district_log.log("Simulation DONE.", "RELATIVE TIME:", str(time.time() - time_0))
            district_log.log("Starting KPIs update...", "RELATIVE TIME:", str(time.time() - time_0))
            self.calc.district_KPIs_update()
            district_log.log("KPIs update done", "RELATIVE TIME:", str(time.time() - time_0))
            district_log.log("Network", network.name, "DONE")
        self.julia_output_checker.check()

        result_folder = os.path.join(dr, "cooling", "Results")
        input_folder = os.path.join(dr, "cooling", "input")
        self.julia_output_checker.set_folder(result_folder)
        self.calc.work_folder = result_folder
        for network in self.DCN_network_list:
            district_log.log("STARTING COMPUTING DCN NETWORKS", network.name, "RELATIVE TIME:",
                             str(time.time() - time_0))
            self.gen_default_julia_files(input_folder)
            district_log.log("default julia files done", "RELATIVE TIME:", str(time.time() - time_0))
            self.calc.network = network
            district_log.log("Starting simulation...", "RELATIVE TIME:", str(time.time() - time_0))
            self.district_cooling_simulation(input_folder, result_folder, network=network)
            district_log.log("Simulation DONE.", "RELATIVE TIME:", str(time.time() - time_0))
            district_log.log("Starting KPIs update...", "RELATIVE TIME:", str(time.time() - time_0))
            self.calc.district_KPIs_update()
            district_log.log("KPIs update done", "RELATIVE TIME:", str(time.time() - time_0))
            district_log.log("Network", network.name, "DONE")
        self.julia_output_checker.check()
        self.julia_output_checker.visualize()
        # self.moveToThread(self.main_thread)

    def district_heating_simulation(self, input_folder, result_folder, network, log: MyLog):
        print("DistrictSimulator.district_heating_simulation")
        print("input_folder:", input_folder)
        print("result_folder:", result_folder)
        tech_infos = create_base_tech_district()
        if network is None:
            network_id = "toy"
        else:
            self.pvgis_api = PvgisApi()
            pvgis_param_adapter = PvgisParamsAdapter(self.pvgis_api)
            pvgis_param_adapter.update_params(network, "baseline" if self.baseline_scenario is not None else "future")
            self.update_district_H_C_tech(tech_infos, network, log)
            print("create_file_for_julia_district() called")
            self.create_file_for_julia_district(self.calc.tech_tab, self.calc.network, input_folder, result_folder, log)
            print("create_file_for_julia_district() exits")
            network_id = network.get_ID()
        print("Simulating network ", network_id)
        file_directory = os.path.dirname(os.path.realpath(__file__))
        log.log("tech_infos for network:", network.name, network.get_ID())
        log.log(tech_infos)
        with JuliaQgisInterface() as j:
            j.include(os.path.join(file_directory, "Absorption_heat_pump_district_heating.jl"))
            j.using("Main.Absorption_heat_pump_district_heating: district_solver")
            j.district_solver(input_folder, result_folder, tech_infos, network_id, self.logger.info)
            print("Exit optimization")

    def district_cooling_simulation(self, input_folder, result_folder, network):
        tech_infos = create_base_tech_cooling()
        if network is None:
            network_id = "toy"
        else:
            self.update_district_H_C_tech(tech_infos, network)
            network_id = network.get_ID()
        file_directory = os.path.dirname(os.path.realpath(__file__))
        with JuliaQgisInterface() as j:
            j.include(os.path.join(file_directory, "district_cooling.jl"))
            j.using("Main.district_cooling: district_cooling_simulation")
            j.district_cooling_simulation(input_folder, result_folder, tech_infos, network_id, self.logger.info)

    def single_building_simulation(self, dr, building_id, log: MyLog):
        expr = QgsExpression("BuildingID=" + building_id)
        if self.baseline_scenario is not None:
            layer = self.baseline_scenario
        else:
            layer = self.future_scenario
        if layer is None:
            print("DistrictSimulator, KPIs_baselineScenario: layer is not defined")
            return None
        fs = [ft for ft in layer.getFeatures(QgsFeatureRequest(expr))]

        if len(fs) > 0:
            feature_0 = fs[0]
        else:
            print("FALLITO MALE", building_id)
            return
        item = self.get_widget_item_from_feature(feature_0)
        if item is None:
            print("DistrictSimulator, single_building_simulation: cannot find feature",
                  feature_0.id(), "building", building_id)
            return None
        if not item.has_any_technology():
            return None
        tech_infos = create_base_tech_infos()
        #print("tech infos che passiamo a julia", tech_infos)
        input_folder = os.path.join(dr, "input")
        output_folder = os.path.join(dr, "Results")
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)
        self.pvgis_api = PvgisApi()
        pvgis_param_adapter = PvgisParamsAdapter(self.pvgis_api)
        pvgis_param_adapter.update_params(item, "baseline" if self.baseline_scenario is not None else "future")
        log.log("PVGIS params:", self.pvgis_api.params)
        self.update_tech_from_widget_item(tech_infos, item, input_folder=input_folder)
        log.log("tech_infos:", tech_infos)
        
        output_file = os.path.join(dr, "TECH_INFOS" + str(building_id) + ".json")
        with open(output_file, 'w') as outfile:
            json.dump(tech_infos, outfile, indent=4)
        self.remove_file_for_julia_single_building(dr)
        self.create_file_for_julia_single_building(item, dr, building_id, log)

        # building_id = "toy"
        print("Running Julia single building simulation for feature: ", building_id)
        #print("tech infos che passo riga 37 single_building_simulation", tech_infos)
        file_directory = os.path.dirname(os.path.realpath(__file__))
        with JuliaQgisInterface() as j:
            j.include(os.path.join(file_directory, "Individual_heating_and_cooling.jl"))
            j.using("Main.individual_heating_and_cooling: individual_H_and_C")
            j.individual_H_and_C(input_folder, output_folder, tech_infos, building_id, self.logger.info)
        print("DONE!")
        return item

    def get_widget_item_from_feature(self, feature):
        buildingID = feature.id()
        if self.step1_building_tree_widget is not None:
            widget = self.step1_building_tree_widget
        if self.step4_building_tree_widget is not None:
            widget = self.step4_building_tree_widget
        for i in range(widget.topLevelItemCount()):
            item = widget.topLevelItem(i)
            try:
                id_item = int(item.text(0))
            except:
                print("ERROR! DistrictSimulator.py, get_widget_item_from_feature. id = int(item.text(0)) failed to",
                      "parse int from widget. item.text(0):", item.text(0))
                id_item = -1
                continue
            if id_item == buildingID:
                print("DistrictSimulator.py, get_widget_item_from_feature.",
                      "item found!", buildingID, "==", id_item)
                return item
        return None

    def get_service_tree_item(self, item, service):
        for i in range(item.childCount()):
            if item.child(i).text(0) == service:
                return item.child(i)
        return None


    def update_tech_from_widget_item(self, tech_infos, item, input_folder=None):
        keys_list = self.individual_H_C_dict_var.keys()
        self.update_tech_from_widget_item_H_C_DHW(tech_infos, self.get_service_tree_item(item, "Cooling"), keys_list, input_folder=input_folder)
        self.update_tech_from_widget_item_H_C_DHW(tech_infos, self.get_service_tree_item(item, "Heating"), keys_list, input_folder=input_folder)
        self.update_tech_from_widget_item_H_C_DHW(tech_infos, self.get_service_tree_item(item, "DHW"), keys_list, input_folder=input_folder)
        # self.update_tech_from_widget_item_H_C_DHW(tech_infos, self.get_service_tree_item(item, "DHW and Heating"),
        #                                           keys_list, , input_folder=input_folder)

    def update_tech_from_widget_item_H_C_DHW(self, tech_infos, item, keys_list, input_folder=None):
        #print("tech infos che vengono aggiornati", tech_infos)
        #print("key list ", keys_list)
        for i in range(item.childCount()):
            for key in keys_list:
                if item.child(i).text(0) in self.individual_H_C_dict_var[key]:
                    val_list = [int(item.parent().text(0)), item.child(i).text(0), 0.0] #item.child(i).text(2) corrisponde alla fonte
                    for j in range(item.child(i).columnCount()):
                        if j > 2:
                            try:
                                val_list.append(float(item.child(i).text(j)))

                            except:
                                print("DistrictSimulator.py, update_tech_from_widget_item.",
                                      "conversion to float FAILED", item.child(i).text(j))
                    self.tech_paramaters_conversion(val_list)
                    julia_category = self.individual_H_C_dict_func[key](tech_infos, val_list, input_folder=input_folder)
                    item.child(i).setData(0, Qt.UserRole, QVariant(julia_category))
                    self.write_solar_panel_area_in_widget(item.child(i), tech_infos)
                # generate_fileEta_forJulia(val_list, input_folder, output_folder)
                #     genera_file_etaHP_cool(val_list, input_folder=self.work_directory,
                #                            output_folder=os.path.join(self.work_directory, "input"))


    # beware: district_H_dict_var it's not used...
    def update_district_H_C_tech(self, tech_infos, network, log: MyLog):
        if self.step1_network_tree_widget is not None:
            widget = self.step1_network_tree_widget
        else:
            widget = self.step4_network_tree_widget
        for i in range(widget.topLevelItemCount()):
            n = widget.topLevelItem(i)
            if n.data(0, Qt.UserRole) == str(network.ID):
                for j in range(n.childCount()):
                    item = n.child(j)
                    log.log("Technology found and tryin to add:", item.text(1))
                    for key in self.district_function.keys():
                        log.log("looking in", key, "wich contains:", self.district_function[key])
                        if item.text(1) in self.district_function[key]:
                            log.log(item.text(1), "is marked as", key)
                            list_val = []
                            for k in range(item.columnCount()):
                                try:
                                   list_val.append(float(item.text(k)))
                                except:
                                    list_val.append(item.text(k))
                            self.tech_paramaters_district_conversion(list_val)
                            if network.n_type == "DCN":
                                out_folder = os.path.join(self.work_directory, "cooling", "Input")
                                julia_category = self.district_C_dict_func[key](tech_infos, list_val, input_folder=out_folder)
                            if network.n_type == "DHN":
                                out_folder = os.path.join(self.work_directory, "heating", "Input")
                                julia_category = self.district_H_dict_func[key](tech_infos, list_val, input_folder=out_folder)
                            log.log("Technology added:", item.text(1))
                            log.log("julia_category:", julia_category)
                            item.setData(1, Qt.UserRole, QVariant(julia_category))
                            #Booster_COP.generate_fileEta_forHeating(list_val, julia_category, input_folder=self.work_directory, output_folder=out_folder)
                            #generate_solar_thermal_forJulia(list_val, input_folder=self.work_directory, output_folder=out_folder)
                            #generate_file_Waste_heat_pump_heating(list_val, julia_category, input_folder=self.work_directory, output_folder=out_folder)
                            #generate_file_Waste_heat_pump_cooling(list_val,input_folder=self.work_directory, output_folder=out_folder)
                            break

    def add_heat_only_boiler(self, tech_infos, val_list, input_folder=None):
        if tech_infos["P_max_HOB"] == 0:
            tech_infos["P_max_HOB"] = val_list[self.name_to_index("p_max")]
            tech_infos["eta_HOB"] = val_list[self.name_to_index("eta_optical")]
            tech_infos["cost_var_HOB"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["cost_fuel_HOB"] = val_list[self.name_to_index("fuel_cost")]
            tech_infos["tec_min_HOB"] = val_list[self.name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HOB"] = val_list[self.name_to_index("ramp_up_down")]
            return "HOB"
        else:
            tech_infos["P_max_HOB_2"] = val_list[self.name_to_index("p_max")]
            tech_infos["eta_HOB_2"] = val_list[self.name_to_index("eta_optical")]
            tech_infos["cost_var_HOB_2"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["cost_fuel_HOB_2"] = val_list[self.name_to_index("fuel_cost")]
            tech_infos["tec_min_HOB_2"] = val_list[self.name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HOB_2"] = val_list[self.name_to_index("ramp_up_down")]
            return "HOB_2"

    def add_electrical_heater(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file(input_folder, val_list)

        if tech_infos["P_max_EH"] == 0:
            tech_infos["P_max_EH"] = val_list[self.name_to_index("p_max")]
            tech_infos["Technical_minimum_EH"] = val_list[self.name_to_index("tech_min")]
            tech_infos["cost_var_EH"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["eta_EH"] = val_list[self.name_to_index("eta_optical")]
            tech_infos["Percentage_ramp_up_down_EH"] = val_list[self.name_to_index("ramp_up_down")]
            tech_infos["cost_fuel_EH"] = val_list[self.name_to_index("fuel_cost")]
            return "EH"
        else:
            tech_infos["P_max_EH_2"] = val_list[self.name_to_index("p_max")]
            tech_infos["eta_EH_2"] = val_list[self.name_to_index("eta_optical")]
            tech_infos["cost_var_EH_2"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["Technical_minimum_EH_2"] = val_list[self.name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_EH_2"] = val_list[self.name_to_index("ramp_up_down")]
            tech_infos["cost_fuel_EH_2"] = val_list[self.name_to_index("fuel_cost")]
            return "EH_2"

    def add_heat_pump(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file(input_folder, val_list)
        if tech_infos["P_max_HP"] == 0:
            tech_infos["P_max_HP"] = val_list[self.name_to_index("p_max")]
            tech_infos["cost_var_HP"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["Technical_minimum_HP"] = val_list[self.name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP"] = val_list[self.name_to_index("ramp_up_down")]
            tech_infos["cost_fuel_HP"] = val_list[self.name_to_index("fuel_cost")]
            return "HP_1"
        else:
            tech_infos["P_max_HP_2"] = val_list[self.name_to_index("p_max")]
            tech_infos["cost_var_HP_2"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["Technical_minimum_HP_2"] = val_list[self.name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_2"] = val_list[self.name_to_index("ramp_up_down")]
            tech_infos["cost_fuel_HP_2"] = val_list[self.name_to_index("fuel_cost")]
            return "HP_2"

    def add_absorption_heat_pump(self, tech_infos, val_list, input_folder=None):
        tech_infos["eta_HP"] = val_list[self.name_to_index("cop_absorption")]
        tech_infos["P_max_HP_absorption"] = val_list[self.name_to_index("p_max")]
        tech_infos["eta_HP_absorption"] = val_list[self.name_to_index("cop_absorption")]
        tech_infos["cost_var_HP_absorption"] = val_list[self.name_to_index("variable_cost")]
        tech_infos["cost_fuel_HP_absorption"] = val_list[self.name_to_index("fuel_cost")]
        tech_infos["tec_min_HP_absorption"] = val_list[self.name_to_index("tech_min")]
        tech_infos["Percentage_ramp_up_down_HP_absorption"] = val_list[self.name_to_index("ramp_up_down")]
        return "HP_absorption"

    def add_cogeneration(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file(input_folder, val_list)
        tech_infos["P_max_CHP"] = val_list[self.name_to_index("p_max")]
        tech_infos["eta_CHP_th"] = val_list[self.name_to_index("eta_optical")]
        tech_infos["cb_CHP"] = val_list[self.name_to_index("power_to_heat_ratio")]
        tech_infos["cost_var_CHP"] = val_list[self.name_to_index("variable_cost")]
        tech_infos["cost_fuel_CHP"] = val_list[self.name_to_index("fuel_cost")]
        tech_infos["Tecnical_minimum_CHP"] = val_list[self.name_to_index("tech_min")]
        tech_infos["Percentage_ramp_up_down_CHP"] = val_list[self.name_to_index("ramp_up_down")]
        tech_infos["CHP_electricity_price"] = val_list[self.name_to_index("el_sale")]
        return "CHP"

    def add_solar_thermal(self, tech_infos, val_list, input_folder=None):
        layer = self.baseline_scenario if self.baseline_scenario is not None else self.future_scenario
        try:
            area = layer.getFeature(val_list[0]).attribute("FootPrintA")
        except:
            print("DistrictSimulator, add_solar_thermal. Failed to get FootPrintA attribute")
            area = 1
        effective_area = area/math.cos((val_list[self.name_to_index("inclination")])*(math.pi/180.0))
        print("DistrictSimulator, add_solar_thermal. area", area, "effective_area", effective_area)
        tech_infos["A_ST"] = effective_area
        tech_infos["cost_var_ST"] = val_list[self.name_to_index("variable_cost")]
        self.pvgis_api.params["gsi_1"]["angle"] = val_list[self.name_to_index("inclination")]
        return "ST"

    def add_cooling_heat_pump(self, tech_infos, val_list, input_folder=None):
        if tech_infos["P_max_HP_cool"] == 0:
            tech_infos["P_max_HP_cool"] = val_list[self.name_to_index("p_max")]
            tech_infos["cost_var_HP_cool"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["Tecnical_minimum_HP_cool"] = val_list[self.name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_cool"] = val_list[self.name_to_index("ramp_up_down")]
            tech_infos["cost_fuel_HP_cool"] = val_list[self.name_to_index("fuel_cost")]
            return "HP_cool"
        else:
            tech_infos["P_max_HP_cool_2"] = val_list[self.name_to_index("p_max")]
            tech_infos["cost_var_HP_cool_2"] = val_list[self.name_to_index("variable_cost")]
            tech_infos["Tecnical_minimum_HP_cool_2"] = val_list[self.name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_cool_2"] = val_list[self.name_to_index("ramp_up_down")]
            tech_infos["cost_fuel_HP_cool_2"] = val_list[self.name_to_index("fuel_cost")]
            return "HP_cool_2"

    def add_combined_heat_pump(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_max_HP_comb"] = val_list[self.name_to_index("p_max")]
        tech_infos["cost_var_HP_comb"] = val_list[self.name_to_index("variable_cost")]
        return "CHP"

    def add_absorption_cooling_heat_pump(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_max_HP_cool_absorption"] = val_list[self.name_to_index("p_max")]
        tech_infos["eta_HP_cool_absorption"] = val_list[self.name_to_index("eta_optical")]
        tech_infos["cost_var_HP_cool_absorption "] = val_list[self.name_to_index("variable_cost")]
        tech_infos["cost_fuel_HP_cool_absorption"] = val_list[self.name_to_index("fuel_cost")]
        tech_infos["Tecnical_minimum_HP_cool_absorption"] = val_list[self.name_to_index("tech_min")]
        tech_infos["Percentage_ramp_up_down_HP_cool_absorption"] = val_list[self.name_to_index("ramp_up_down")]
        return "HP_cool_absorption"


    def add_thermal_energy_storage(self, tech_infos, val_list, input_folder=None):
        tech_infos["TES_size"] = val_list[self.name_to_index("tes_size")]
        tech_infos["SOC_min"] = val_list[self.name_to_index("soc_min")]
        tech_infos["TES_start_end"] = val_list[self.name_to_index("tes_startEnd")]
        tech_infos["TES_charge_discharge_time"] = val_list[self.name_to_index("tes_discharge")]
        tech_infos["Tes_loss"] = val_list[self.name_to_index("tes_loss")]
        return "SOC"

    def add_domestic_hot_water_thermal_energy_storage(self, tech_infos, val_list, input_folder=None):
        tech_infos["TES_size_DHW"] = val_list[self.name_to_index("tes_size")]
        tech_infos["SOC_min_DHW"] = val_list[self.name_to_index("soc_min")]  # soc_min si chiama tes_max!!!!
        tech_infos["TES_start_end_DHW"] = val_list[self.name_to_index("tes_startEnd")]
        tech_infos["TES_charge_discharge_time_DHW"] = val_list[self.name_to_index("tes_discharge")]
        tech_infos["Tes_loss_DHW"] = val_list[self.name_to_index("tes_loss")]
        return "SOC_DHW"

    def name_to_index(self, column):
        switcher = {
            "Source": 2,
            #"technology": 2,
            "inclination": 3,
            "temperature": 4,
            "eta_optical": 5,
            "first_order_coeff": 6,
            "second_order_coeff": 7,
            #"capacity": 8,
            "p_max": 8,
            "p_min": 9,
            "power_to_heat_ratio": 10,
            "tech_min": 11,
            "ramp_up_down": 12,
            "fixed_cost": 13,
            "variable_cost": 15,
            "fuel_cost": 14,
            "tes_size": 16,
            "soc_min": 17,
            "tes_startEnd": 18,
            "tes_discharge": 19,
            "cop_absorption": 20,
            "el_sale": 21,
            "tes_loss": 22
        }
        return switcher.get(column, 8)

    def DCN_heat_only_boiler(self, tech_infos, val_list, input_folder=None):
        if tech_infos["P_max_HOB"] == 0:
            tech_infos["P_max_HOB"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Tecnical_minimum_HOB"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HOB"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HOB"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HOB"] = val_list[self.district_name_to_index("fuel_cost")]
            tech_infos["eta_HOB"] = val_list[self.district_name_to_index("eta_optical")]
            return "HOB"
        else:
            if tech_infos["P_max_HOB_2"] == 0:
                tech_infos["P_max_HOB_2"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Tecnical_minimum_HOB_2"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HOB_2"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HOB_2"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_HOB_2"] = val_list[self.district_name_to_index("fuel_cost")]
                tech_infos["eta_HOB_2"] = val_list[self.district_name_to_index("eta_optical")]
                return "HOB_2"
            else:
                tech_infos["P_max_HOB_3"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Tecnical_minimum_HOB_3"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HOB_3"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HOB_3"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_HOB_3"] = val_list[self.district_name_to_index("fuel_cost")]
                tech_infos["eta_HOB_3"] = val_list[self.district_name_to_index("eta_optical")]
                return "HOB_3"

    def DCN_heat_pump(self, tech_infos, val_list, input_folder=None):
        if tech_infos["P_max_HP"] == 0:
            tech_infos["P_max_HP"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP"] = val_list[self.district_name_to_index("variable_cost")]
            return "HP"
        else:
            if tech_infos["P_max_HP_2"] == 0:
                tech_infos["P_max_HP_2"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Technical_minimum_HP_2"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HP_2"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HP_2"] = val_list[self.district_name_to_index("variable_cost")]
                return "HP_2"
            else:
                tech_infos["P_max_HP_3"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Technical_minimum_HP_3"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HP_3"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HP_3"] = val_list[self.district_name_to_index("variable_cost")]
                return "HP_3"

    def DCN_cogeneration(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        if tech_infos["P_max_CHP"] == 0:
            tech_infos["P_max_CHP"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_CHP"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_CHP"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_CHP"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_CHP"] = val_list[self.district_name_to_index("fuel_cost")]
            tech_infos["eta_CHP_th"] = val_list[self.district_name_to_index("eta_optical")]
            tech_infos["cb_CHP"] = val_list[self.district_name_to_index("power_to_heat_ratio")]
            return "CHP"
        else:
            tech_infos["P_max_CHP_2"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_CHP_2"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_CHP_2"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_CHP_2"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_CHP_2"] = val_list[self.district_name_to_index("fuel_cost")]
            tech_infos["eta_CHP_th_2"] = val_list[self.district_name_to_index("eta_optical")]
            tech_infos["cb_CHP_2"] = val_list[self.district_name_to_index("power_to_heat_ratio")]
            return "CHP_2"

    def DCN_thermal_energy_storage(self, tech_infos, val_list, input_folder=None):
        tech_infos["TES_size"] = val_list[self.district_name_to_index("tes_size")]
        tech_infos["SOC_min"] = val_list[self.district_name_to_index("soc_min")]
        tech_infos["TES_start_end"] = val_list[self.district_name_to_index("tes_startEnd")]
        tech_infos["TES_charge_discharge_time"] = val_list[self.district_name_to_index("tes_discharge")]
        tech_infos["TES_loss"] = val_list[self.district_name_to_index("tes_loss")]
        return "TES"

    def DCN_absorption_heat_pump(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_max_HP_abs"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_HP_abs"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["eta_HP_abs"] = val_list[self.district_name_to_index("eta_optical")]
        tech_infos["Percentage_ramp_up_down_HP_abs"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_HP_abs"] = val_list[self.district_name_to_index("variable_cost")]
        return "HP_abs"

    def DCN_waste_heat_heat_exchangers(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_HEX_capacity"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["P_min_HEX"] = val_list[self.district_name_to_index("p_min")]
        tech_infos["cost_var_HEX"] = val_list[self.district_name_to_index("variable_cost")]
        return "HEX"

    def DCN_waste_cooling_heat_exchangers(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_HEX_capacity_cool"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["P_min_HEX_cool"] = val_list[self.district_name_to_index("p_min")]
        tech_infos["cost_var_HEX_cool"] = val_list[self.district_name_to_index("variable_cost")]
        return "HEX_cool"

    def DCN_waste_heat_heat_pumps_temperature_group1(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        tech_infos["P_max_HP_waste_heat_1"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_HP_waste_heat_1"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["Percentage_ramp_up_down_HP_waste_heat_1"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_HP_waste_heat_1"] = val_list[self.district_name_to_index("variable_cost")]
        return "HP_waste_heat_1"

    def DCN_waste_heat_heat_pumps_temperature_group2(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        tech_infos["P_max_HP_waste_heat_2"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_HP_waste_heat_2"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["Percentage_ramp_up_down_HP_waste_heat_2"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_HP_waste_heat_2"] = val_list[self.district_name_to_index("variable_cost")]
        return "HP_waste_heat_2"

    def DCN_waste_heat_heat_pumps_temperature_group3(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        tech_infos["P_max_HP_waste_heat_3"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_HP_waste_heat_3"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["Percentage_ramp_up_down_HP_waste_heat_3"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_HP_waste_heat_3"] = val_list[self.district_name_to_index("variable_cost")]
        return "HP_waste_heat_3"

    def DHN_heat_only_boiler(self, tech_infos, val_list, input_folder=None):
        if tech_infos["P_max_HOB"] == 0:
            tech_infos["P_max_HOB"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Tecnical_minimum_HOB"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HOB"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HOB"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HOB"] = val_list[self.district_name_to_index("fuel_cost")]
            tech_infos["eta_HOB"] = val_list[self.district_name_to_index("eta_optical")]
            return "HOB"
        else:
            if tech_infos["P_max_HOB_2"] == 0:
                tech_infos["P_max_HOB_2"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Tecnical_minimum_HOB_2"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HOB_2"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HOB_2"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_HOB_2"] = val_list[self.district_name_to_index("fuel_cost")]
                tech_infos["eta_HOB_2"] = val_list[self.district_name_to_index("eta_optical")]
                return "HOB_2"
            else:
                tech_infos["P_max_HOB_3"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Tecnical_minimum_HOB_3"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HOB_3"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HOB_3"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_HOB_3"] = val_list[self.district_name_to_index("fuel_cost")]
                tech_infos["eta_HOB_3"] = val_list[self.district_name_to_index("eta_optical")]
                return "HOB_3"

    def DHN_electrical_heater(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        if tech_infos["P_max_EH"] == 0:
            tech_infos["P_max_EH"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_EH"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["eta_EH"] = val_list[self.district_name_to_index("eta_optical")]
            tech_infos["Percentage_ramp_up_down_EH"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_EH"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_EH"] = val_list[self.district_name_to_index("fuel_cost")]
            return "EH"
        else:
            if tech_infos["P_max_EH_2"] == 0:
                tech_infos["P_max_EH_2"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Technical_minimum_EH_2"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["eta_EH_2"] = val_list[self.district_name_to_index("eta_optical")]
                tech_infos["Percentage_ramp_up_down_EH_2"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_EH_2"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_EH_2"] = val_list[self.district_name_to_index("fuel_cost")]
                return "EH_2"
            else:
                tech_infos["P_max_EH_3"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Technical_minimum_EH_3"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["eta_EH_3"] = val_list[self.district_name_to_index("eta_optical")]
                tech_infos["Percentage_ramp_up_down_EH_3"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_EH_3"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_EH_3"] = val_list[self.district_name_to_index("fuel_cost")]
                return "EH_3"

    def DHN_heat_pump(self, tech_infos, val_list, input_folder=None):
        if tech_infos["P_max_HP"] == 0:
            tech_infos["P_max_HP"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_1"
        else:
            if tech_infos["P_max_HP_2"] == 0:
                tech_infos["P_max_HP_2"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Technical_minimum_HP_2"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HP_2"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HP_2"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_HP_2"] = val_list[self.district_name_to_index("fuel_cost")]
                return "HP_2"
            else:
                tech_infos["P_max_HP_3"] = val_list[self.district_name_to_index("p_max")]
                tech_infos["Technical_minimum_HP_3"] = val_list[self.district_name_to_index("tech_min")]
                tech_infos["Percentage_ramp_up_down_HP_3"] = val_list[self.district_name_to_index("ramp_up_down")]
                tech_infos["cost_var_HP_3"] = val_list[self.district_name_to_index("variable_cost")]
                tech_infos["cost_fuel_HP_3"] = val_list[self.district_name_to_index("fuel_cost")]
                return "HP_3"

    def DHN_cogeneration(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        if tech_infos["P_max_CHP"] == 0:
            tech_infos["P_max_CHP"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_CHP"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_CHP"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_CHP"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_CHP"] = val_list[self.district_name_to_index("fuel_cost")]
            tech_infos["eta_CHP_th"] = val_list[self.district_name_to_index("eta_optical")]
            tech_infos["cb_CHP"] = val_list[self.district_name_to_index("power_to_heat_ratio")]
            tech_infos["CHP_electricity_price"] = val_list[self.district_name_to_index("el_sale")]
            return "CHP"
        else:
            tech_infos["P_max_CHP_2"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_CHP_2"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_CHP_2"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_CHP_2"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_CHP_2"] = val_list[self.district_name_to_index("fuel_cost")]
            tech_infos["eta_CHP_th_2"] = val_list[self.district_name_to_index("eta_optical")]
            tech_infos["cb_CHP_2"] = val_list[self.district_name_to_index("power_to_heat_ratio")]
            tech_infos["CHP_electricity_price_2"] = val_list[self.district_name_to_index("el_sale")]
            return "CHP_2"

    def DHN_absorption_heat_pump(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_max_HP_absorption"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_HP_absorption"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["eta_HP_absorption"] = val_list[self.district_name_to_index("eta_optical")]
        tech_infos["Percentage_ramp_up_down_HP_absorption"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_HP_absorption"] = val_list[self.district_name_to_index("variable_cost")]
        tech_infos["cost_fuel_HP_absorption"] = val_list[self.district_name_to_index("fuel_cost")]
        return "HP_absorption"

    def DHN_add_solar_thermal(self, tech_infos, val_list, input_folder=None):
        if tech_infos["A_ST"] == 0:
            tech_infos["A_ST"] = val_list[self.district_name_to_index("area")]
            tech_infos["cost_var_ST"] = val_list[self.district_name_to_index("variable_cost")]
            return "ST"
        else:
            tech_infos["A_ST_2"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["cost_var_ST_2"] = val_list[self.district_name_to_index("variable_cost")]
            return "ST_2"

    def DHN_seasonal_solar_thermal(self, tech_infos, val_list, input_folder=None):
        tech_infos["A_ST_seasonal"] = val_list[self.district_name_to_index("area")]
        tech_infos["cost_var_ST_seasonal"] = val_list[self.district_name_to_index("variable_cost")]
        return "ST_seasonal"

    def DHN_waste_heat_heat_exchangers(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        tech_infos["P_HEX_capacity"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["P_min_HEX"] = val_list[self.district_name_to_index("p_min")]
        tech_infos["cost_var_HEX"] = val_list[self.district_name_to_index("variable_cost")]
        return "HEX"

    def DHN_waste_heat_heat_pumps_temperature_group1(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        if tech_infos["P_max_HP_waste_heat_I_1"] == 0.0:
            tech_infos["P_max_HP_waste_heat_I_1"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_I_1"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_1"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_I_1"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_I_1"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_I_1"
        elif tech_infos["P_max_HP_waste_heat_I_2"] == 0.0:
            tech_infos["P_max_HP_waste_heat_I_2"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_I_2"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_2"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_I_2"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_I_2"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_I_2"
        else:
            tech_infos["P_max_HP_waste_heat_I_3"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_I_3"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_3"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_I_3"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_I_3"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_I_3"

    def DHN_waste_heat_heat_pumps_temperature_group2(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        if tech_infos["P_max_HP_waste_heat_II_1"] == 0.0:
            tech_infos["P_max_HP_waste_heat_II_1"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_II_1"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_1"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_II_1"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_II_1"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_II_1"
        elif tech_infos["P_max_HP_waste_heat_II_2"] == 0.0:
            tech_infos["P_max_HP_waste_heat_II_2"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_II_2"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_2"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_II_2"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_II_2"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_II_2"
        else:
            tech_infos["P_max_HP_waste_heat_II_3"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_II_3"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_3"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_II_3"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_II_3"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_II_3"

    def DHN_waste_heat_heat_pumps_temperature_group3(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        if tech_infos["P_max_HP_waste_heat_III_1"] == 0.0:
            tech_infos["P_max_HP_waste_heat_III_1"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_III_1"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_1"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_III_1"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_III_1"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_III_1"
        elif tech_infos["P_max_HP_waste_heat_III_2"] == 0.0:
            tech_infos["P_max_HP_waste_heat_III_2"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_III_2"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_2"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_III_2"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_III_2"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_III_2"
        else:
            tech_infos["P_max_HP_waste_heat_III_3"] = val_list[self.district_name_to_index("p_max")]
            tech_infos["Technical_minimum_HP_waste_heat_III_3"] = val_list[self.district_name_to_index("tech_min")]
            tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_3"] = val_list[self.district_name_to_index("ramp_up_down")]
            tech_infos["cost_var_HP_waste_heat_III_3"] = val_list[self.district_name_to_index("variable_cost")]
            tech_infos["cost_fuel_HP_waste_heat_III_3"] = val_list[self.district_name_to_index("fuel_cost")]
            return "HP_III_3"

    def DHN_seasonal_waste_heat_pump(self, tech_infos, val_list, input_folder=None):
        self.write_electricity_file_district(input_folder, val_list)
        tech_infos["P_max_HP_waste_heat_seasonal"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_HP_waste_heat_seasonal"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["Percentage_ramp_up_down_HP_waste_heat_seasonal"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_HP_waste_heat_seasonal"] = val_list[self.district_name_to_index("variable_cost")]
        tech_infos["cost_fuel_HP_waste_heat_seasonal"] = val_list[self.district_name_to_index("fuel_cost")]
        return "HP_waste_heat_seasonal"

    def DHN_waste_heat_absorption_heat_pump(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_max_HP_waste_heat_absorption"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_HP_waste_heat_absorption"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["eta_HP_waste_heat_absorption"] = val_list[self.district_name_to_index("cop_absorption")]
        tech_infos["Percentage_ramp_up_down_HP_waste_heat_absorption"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_HP_waste_heat_absorption"] = val_list[self.district_name_to_index("variable_cost")]
        tech_infos["cost_fuel_HP_waste_heat_absorption"] = val_list[self.district_name_to_index("fuel_cost")]
        return "HP_waste_heat_absorption"

    def DHN_thermal_energy_storage(self, tech_infos, val_list, input_folder=None):
        tech_infos["TES_size"] = val_list[self.district_name_to_index("tes_size")]
        tech_infos["SOC_min"] = val_list[self.district_name_to_index("soc_min")]
        tech_infos["TES_start_end"] = val_list[self.district_name_to_index("tes_startEnd")]
        tech_infos["TES_charge_discharge_time"] = val_list[self.district_name_to_index("tes_discharge")]
        tech_infos["TES_loss"] = val_list[self.district_name_to_index("tes_loss")]
        return "TES"

    def DHN_seasonal_thermal_energy_storage(self, tech_infos, val_list, input_folder=None):
        tech_infos["TES_size_seasonal"] = val_list[self.district_name_to_index("tes_size")]
        tech_infos["SOC_min_seasonal"] = val_list[self.district_name_to_index("soc_min")]
        tech_infos["TES_start_end_seasonal"] = val_list[self.district_name_to_index("tes_startEnd")]
        tech_infos["TES_charge_discharge_time_seasonal"] = val_list[self.district_name_to_index("tes_discharge")]
        tech_infos["TES_loss_seasonal"] = val_list[self.district_name_to_index("tes_loss")]
        return "TES_seasonal"

    def DHN_ORC_cogeneration(self, tech_infos, val_list, input_folder=None):
        tech_infos["P_max_CHP_ORC"] = val_list[self.district_name_to_index("p_max")]
        tech_infos["Technical_minimum_CHP_ORC"] = val_list[self.district_name_to_index("tech_min")]
        tech_infos["eta_CHP_el"] = val_list[self.district_name_to_index("eta_optical")]
        tech_infos["cb_CHP_ORC"] = val_list[self.district_name_to_index("cop_absorption")]
        tech_infos["Percentage_ramp_up_down_CHP_ORC"] = val_list[self.district_name_to_index("ramp_up_down")]
        tech_infos["cost_var_CHP_ORC"] = val_list[self.district_name_to_index("variable_cost")]
        tech_infos["CHP_ORC_electricity_price"] = val_list[self.district_name_to_index("el_sale")]
        return "CHP_ORC"

    def district_name_to_index(self, column):
        switcher = {
            "Source": 2,
            "area": 3,
            "temperature": 4,
            "eta_optical": 5,
            "first_order_coeff": 6,
            "second_order_coeff": 7,
            #"capacity": 8,
            "p_max": 8,
            "p_min": 9,
            "power_to_heat_ratio": 10,
            "tech_min": 11,
            "ramp_up_down": 12,
            "fixed_cost": 13,
            "variable_cost": 14,
            "fuel_cost": 15,
            "tes_size": 16,
            "soc_min": 17,
            "tes_startEnd": 18,
            "tes_discharge": 19,
            "cop_absorption": 20,
            "el_sale": 21,
            "tes_loss": 22,
            "inclination": 23
        }
        return switcher.get(column, 8)

    def is_building_connected_type(self, building_id):
        root = QgsProject.instance().layerTreeRoot()
        status = "2"
        for lst in [self.DHN_network_list, self.DCN_network_list]:
            for n in lst:
                network_node = root.findGroup(n.get_group_name())
                buildings_layer = None
                for l in network_node.findLayers():
                    if l.name()[0:19] == "selected_buildings_":
                        buildings_layer = l.layer()
                        status = None
                        break
                if buildings_layer is None:
                    for l in network_node.findLayers():
                        if l.name()[0:14] == "all_buildings_":
                            buildings_layer = l.layer()
                            status = "2"
                            break
                if buildings_layer is None:
                    continue
                for feature in buildings_layer.getFeatures():
                    if status is None:
                        if feature.attribute("BuildingID") == building_id:
                            return n.n_type
                    elif str(feature.attribute("Status")) == status:
                        if feature.attribute("BuildingID") == building_id:
                            return n.n_type
        return None

    def get_buildings_connection_list(self, layer):
        output = []
        for f in layer.getFeatures():
            output.append([f.id(), f.attribute("BuildingID"), self.is_building_connected_type(f.attribute("BuildingID"))])
        return output

    def reprint_progress_label(self, s):
        if self.progress_label is not None:
            self.progress_label.setText(s)

    def add_progress_value(self, i):
        if self.progress_bar is not None:
            self.progress_bar.setValue(self.progress_bar.value() + i)

    def estimated_time_update(self):
        if (self.progress_bar is not None) and (self.progress_time is not None):
            if self.progress_bar.value() < 2:
                message = "Evaluating time left..."
            else:
                now = time.time()
                t = ((now - self.start_time) / (self.progress_bar.value() / self.progress_bar.maximum)) - (
                            now - self.start_time)
                h = int(t / 3600)
                m = t % 3600
                message = "Estimated time left: "
                if not h == 0:
                    message = message + str(h) + " h "
                message = message + str(m) + " min"
            self.progress_time.setText(message)

    def remove_file_for_julia_single_building(self, dr):
        T_source = "T_source_"
        input_folder = os.path.join(dr, "input")
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.startswith(T_source):
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception:
                        pass


    def create_file_for_julia_single_building(self, item, dr, building_id, log: MyLog):
        solar_parameter_builder = SolarParameterBuilder()
        input_folder = os.path.join(dr, "input")
        output_folder = os.path.join(dr, "Results")

        COP_val_list = [90.0, 1.0, 90.0, 1.0, 90.0, 1.0]
        cool_COP_val_list = [90.0, 1.0, 90.0, 1.0, 90.0, 1.0]
        self.create_default_files(input_folder)
        for i in range(item.childCount()):
            service = item.child(i)
            if service.childCount() == 0:
                self.set_single_solution_demand_to_zero(building_id, service, input_folder)
            for j in range(service.childCount()):
                technology = service.child(j)
                print("DistrictSimulator.py, create_file_for_julia_single_building():", technology.text(0),
                      "hidden data (Qt.UserRole)", technology.data(0, Qt.UserRole))
                self.create_electricity_file(input_folder, price=technology.text(21))
                julia_category = technology.data(0, Qt.UserRole)
                solar_parameter_builder.update_param_from_tech_widget(julia_category, technology, self.name_to_index)
                if julia_category in ["HP_1", "HP_2", "HP_3"]:
                    self.build_file_HP(julia_category, technology, input_folder, COP_val_list, item)
                if julia_category in ["HP_cool", "HP_cool_2", "HP_cool_3"]:
                    self.build_file_HP_cool(julia_category, technology, input_folder, cool_COP_val_list)
        pvgis_files = self.pvgis_api.write_to_files()
        self.pvgis_api.gen_dummy_output(pvgis_files)
        log.log("pvgis_files", pvgis_files)
        generate_solar_thermal_forJulia(solar_parameter_builder.solar_params, pvgis_files,
                                        output_folder=input_folder)
        #generate_fileEta_forJulia(COP_val_list, input_folder=input_folder, output_folder=output_folder)
        genera_file_etaHP_cool(cool_COP_val_list, input_folder=input_folder, output_folder=input_folder, item=item)

    def create_default_files(self, folder):
        self.create_default_file_8760_rep(folder, "Electricity_price_time.csv", "1.0")
        self.create_default_file_8760_rep(folder, "eta_HP_1.csv", "0.9")
        self.create_default_file_8760_rep(folder, "eta_HP_2.csv", "0.9")
        self.create_default_file_8760_rep(folder, "eta_HP_cool.csv", "0.9")
        self.create_default_file_8760_rep(folder, "eta_HP_cool_2.csv", "0.9")

    def create_default_file_8760_rep(self, folder, name, text):
        if not os.path.isdir(folder):
            return
        filepath = os.path.join(folder, name)
        if os.path.isfile(filepath):
            return
        with open(filepath, "w+") as file:
            for i in range(self.h8760):
                file.write(str(text) + "\n")

    def create_electricity_file(self, folder, price=None):
        if price is None:
            price = 1.0
        print("Creating electricity price file in folder:", folder)
        with open(os.path.join(folder, "Electricity_price_time.csv"), "w+") as file:
            for i in range(self.h8760):
                file.write(str(price) + "\n")

    def gen_T_Source_X_file(self, source, file_path):
        try:
            os.remove(file_path)
        except FileNotFoundError as e:
            pass
        if self.temperature is None:
            print("DistrictSimulator.gen_T_Source_X_file() ERROR: self.temperature is None, bo back to step 0 and calculate sources availability.")
            return
        if source not in self.temperature.keys():
            print("DistrictSimulator.py, gen_T_Source_X_file(): source", source, "not found in dict keys:",
                  self.temperature.keys())
        else:
            try:
                test = float(self.temperature[source][0])
            except (ValueError, KeyError) as e:
                print("DistrictSimulator.py, gen_T_Source_X_file(): temperature is not a number or KeyError!", e)
                return
            if test < -273.15:
                print("DistrictSimulator.py, gen_T_Source_X_file(): temperature is below 0 K")
                return
            file_object = open(file_path, "w")
            print("DistrictSimulator.py, gen_T_Source_X_file(): writing:", file_path)
            for t in self.temperature[source]:
                file_object.write(str(t) + "\n")

    def build_file_HP(self, julia_category, technology, input_folder, COP_val_list, building):
        if julia_category == "HP_1":
            index = 0
        if julia_category == "HP_2":
            index = 2
        if julia_category == "HP_3":
            index = 4
        try:
            COP_val_list[index] = float(technology.text(self.name_to_index("temperature")))
        except ValueError:
            COP_val_list[index] = 90.0  # default
        try:
            COP_val_list[index + 1] = float(technology.text(self.name_to_index("eta_optical")))
        except ValueError:
            COP_val_list[index + 1] = 1.0  # default
        source = technology.text(2)
        file_path = os.path.realpath(os.path.join(input_folder, "../", "T_source_" + julia_category + ".csv"))
        self.gen_T_Source_X_file(source, file_path)
        generate_fileEta_forJulia(COP_val_list, input_folder=os.path.realpath(os.path.join(input_folder, "../")),
                                  output_folder=os.path.realpath(os.path.join(input_folder, "../", "input")),
                                  item=building)

    def build_file_HP_cool(self, julia_category, technology, input_folder, COP_val_list):
        if julia_category == "HP_cool":
            index = 0
        if julia_category == "HP_cool_2":
            index = 2
        if julia_category == "HP_cool_3":
            index = 4
        try:
            COP_val_list[index] = float(technology.text(self.name_to_index("temperature")))
        except ValueError:
            COP_val_list[index] = 90.0  # default
        try:
            COP_val_list[index + 1] = float(technology.text(self.name_to_index("eta_optical")))
        except ValueError:
            COP_val_list[index + 1] = 1.0  # default
        source = technology.text(2)
        file_path = os.path.join(input_folder, "T_source_" + julia_category + ".csv")
        self.gen_T_Source_X_file(source, file_path)

    def set_single_solution_demand_to_zero(self, building_id, service, input_folder):
        file_path = None
        if service.text(0) == "Cooling":
            file_path = os.path.realpath(os.path.join(input_folder, "DEM_cool_time_" + building_id + ".csv"))
        if service.text(0) == "Heating":
            file_path = os.path.realpath(os.path.join(input_folder, "DEM_time_" + building_id + ".csv"))
        if service.text(0) == "DHW":
            file_path = os.path.realpath(os.path.join(input_folder, "DEM_DHW_time_" + building_id + ".csv"))
        if file_path is None:
            return
        if os.path.isfile(file_path):
            file_object = open(file_path, "w")
            for i in range(self.h8760):
                file_object.write("0.0\n")

    def create_file_for_julia_district(self, widget, network, input_folder, result_folder, log: MyLog):
        solar_params_builder = SolarParameterBuilder()
        self.check_and_create_folders([input_folder, result_folder])
        cinput = ""
        if network.scenario_type == "baseline":
            cinput = os.path.join(mp_config.CURRENT_MAPPING_DIRECTORY, 
                                  mp_config.DMM_FOLDER,
                                  mp_config.DMM_PREFIX+mp_config.DMM_HOURLY_SUFFIX+".csv")
        if network.scenario_type == "future":
            cinput = os.path.join(mp_config.CURRENT_MAPPING_DIRECTORY, 
                                  mp_config.DMM_FOLDER,
                                  mp_config.DMM_PREFIX+mp_config.DMM_FUTURE_SUFFIX+mp_config.DMM_HOURLY_SUFFIX+".csv")
        if os.path.isfile(cinput):
            services = []
            if network.n_type == "DHN":
                services.append("Heating")
                services.append("DHW")
            if network.n_type == "DCN":
                services.append("Cooling")

            gen_dem_time_district(cinput=cinput, coutput=os.path.join(input_folder, "DEM_time.csv"), services=services,
                                  buildings=[str(b.attribute("BuildingID")) for b in network.get_connected_buildings()],
                                  log=log)
            log.log("Demand profile created. Connected buildings:",
                    [b.attribute("BuildingID") for b in network.get_connected_buildings()])
        else:
            log.log("Creating the demand profile FAILED because", str(cinput), "is not a file_path")
        COP_val_list = [90.0, 1.0, 90.0, 1.0, 90.0, 1.0]
        COP_val_list_temperature_groups = [20.0, 1.0, 20.0, 1.0, 20.0, 1.0, 50.0, 1.0, 50.0, 1.0, 50.0, 1.0, 90.0, 1.0,
                                           90.0, 1.0, 90.0, 1.0, 90.0, 1.0]
        waste_heat_val_list = {"HP_I_1": 1.0, "HP_I_2": 1.0, "HP_I_3": 1.0,
                               "HP_II_1": 1.0, "HP_II_2": 1.0,
                               "HP_II_3": 1.0, "HP_III_1": 1.0,
                               "HP_III_2": 1.0, "HP_III_3": 1.0,
                               "HP_waste_heat_seasonal": 1.0, "COP_absorption": 10.0}
        log.log("Collecting file list...")
        files = self.waste_heat_file_list(os.path.realpath(os.path.join(input_folder, "../../")))
        log.log("DistrictSimulator.create_file_for_julia_district() files:", files)
        for i in range(widget.topLevelItemCount()):
            n = widget.topLevelItem(i)
            if n.data(0, Qt.UserRole) == network.get_ID():
                for j in range(n.childCount()):
                    item: QTreeWidgetItem = n.child(j)
                    julia_category = item.data(1, Qt.UserRole)
                    solar_params_builder.update_param_from_tech_widget(julia_category, item,
                                                                       self.district_name_to_index)
                    if julia_category in ["HP", "HP_2", "HP_3"]:
                        self.build_file_HP_district(julia_category, item, input_folder, COP_val_list)
                    if julia_category in [key for key in waste_heat_val_list.keys()]:  # HP_waste_heat_V_X
                        if julia_category == "COP_absorption":
                            waste_heat_val_list[julia_category] = float(item.text(20))  # eta_absorption
                        log.log("self.build_file_waste_heat_HP_district()...")
                        self.build_file_waste_heat_HP_district(julia_category, item, input_folder, files,
                                                               COP_val_list_temperature_groups, log)
                    if julia_category in ["absorption_HP"]:
                        self.build_absorption_HP_district(item, input_folder)
                    log.log("Generating file eta for julia...")
                    generate_fileEta_forJulia(COP_val_list,
                                              os.path.realpath(os.path.join(input_folder, "../../")),
                                              input_folder, network)
                    log.log("Booster_COP.generate_fileEta_forHeating()...")
                    Booster_COP.generate_fileEta_forHeating(COP_val_list_temperature_groups,
                                                            input_folder, input_folder, item=network)
                    self.check_and_fix_waste_heat_files(files, result_folder)
                    log.log("generate_file_Waste_heat_pump_heating()...", waste_heat_val_list, input_folder,
                            result_folder)
                    generate_file_Waste_heat_pump_heating(waste_heat_val_list, input_folder, result_folder)
        pvgis_files = self.pvgis_api.write_to_files()
        self.pvgis_api.gen_dummy_output(pvgis_files)
        print(pvgis_files)
        generate_solar_thermal_forJulia(solar_params_builder.solar_params, pvgis_files,
                                        output_folder=input_folder)

    def build_absorption_HP_district(self, item, input_folder):
        source = item.text(2)
        file_path = os.path.join(input_folder, "Available_waste_heat_heat_pump_absorption.csv")
        self.gen_HEAT_Source_X_file(source, file_path)

    def waste_heat_file_list(self, folder):
        files = [os.path.join(folder, "Available_waste_heat_heat_pump_source_group_I_1.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_I_2.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_I_3.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_II_1.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_II_2.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_II_3.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_III_1.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_III_2.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_III_3.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_source_group_seasonal.csv"),
                 os.path.join(folder, "Available_waste_heat_heat_pump_absorption.csv")]
        return files

    def check_and_fix_waste_heat_files(self, files, result_folder):
        for file in files:
            if not os.path.isfile(file):
                file_object = open(file, "w")
                for i in range(self.h8760):
                    file_object.write("0.0\n")

    def check_and_create_folders(self, folders):
        for folder in folders:
            if not os.path.isdir(folder):
                os.makedirs(folder, exist_ok=True)

    def build_file_waste_heat_HP_district(self, julia_category, item, input_folder, files,
                                          COP_val_list_temperature_groups, log: MyLog):
        julia_category_index = ["HP_I_1", "HP_I_2", "HP_I_3",
                                "HP_II_1", "HP_II_2", "HP_II_3",
                                "HP_III_1", "HP_III_2", "HP_III_3",
                                "HP_waste_heat_seasonal"].index(julia_category)
        double_julia_category_index = 2*julia_category_index
        try:
            COP_val_list_temperature_groups[double_julia_category_index] = float(
                item.text(self.district_name_to_index("temperature")))
        except ValueError:
            COP_val_list_temperature_groups[double_julia_category_index] = 90.0  # default
        try:
            COP_val_list_temperature_groups[double_julia_category_index + 1] = float(
                item.text(self.district_name_to_index("eta_optical")))
        except ValueError:
            COP_val_list_temperature_groups[double_julia_category_index + 1] = 1.0  # default
        file_path = os.path.join(input_folder, "T_source_" + julia_category + ".csv")
        source = item.text(2)
        self.gen_T_Source_X_file(source, file_path)
        log.log("build_file_waste_heat_HP_district() julia_category_index:", julia_category_index, "files:", files)
        waste_heat_file_path = files[int(julia_category_index)]
        log.log("waste_heat_file_path:", waste_heat_file_path)
        self.gen_HEAT_Source_X_file(source, waste_heat_file_path)

    def gen_HEAT_Source_X_file(self, source, waste_heat_file_path):
        try:
            os.remove(waste_heat_file_path)
        except FileNotFoundError:
            pass
        if source not in self.heat.keys():
            print("DistrictSimulator.py, gen_HEAT_Source_X_file(): source", source, "not found in dict keys:",
                  self.heat.keys())
        else:
            try:
                test = float(self.heat[source][0])
            except (ValueError, KeyError) as e:
                print("DistrictSimulator.py, gen_HEAT_Source_X_file(): temperature is not a number or KeyError!", e)
                return
            if test < -273.15:
                print("DistrictSimulator.py, gen_HEAT_Source_X_file(): temperature is below 0 K")
                return
            try:
                file_object = open(waste_heat_file_path, "w")
                print("DistrictSimulator.py, gen_HEAT_Source_X_file(): writing:", waste_heat_file_path)
                for t in self.heat[source]:
                    file_object.write(str(t)+"\n")
                file_object.close()
            except Exception:
                print("DistrictSimulator.py, gen_HEAT_Source_X_file(): problems writing file", waste_heat_file_path)
                file_object.close()


    def build_file_HP_district(self, julia_category, technology, input_folder, COP_val_list):
        if julia_category == "HP":
            index = 0
        if julia_category == "HP_2":
            index = 2
        if julia_category == "HP_3":
            index = 4
        try:
            COP_val_list[index] = float(technology.text(self.district_name_to_index("temperature")))
        except ValueError:
            COP_val_list[index] = 90.0  # default
        try:
            COP_val_list[index + 1] = float(technology.text(self.district_name_to_index("eta_optical")))
        except ValueError:
            COP_val_list[index + 1] = 1.0  # default
        source = technology.text(2)
        file_path = os.path.join(input_folder, "T_source_" + julia_category + ".csv")
        self.gen_T_Source_X_file(source, file_path)

    def ask_for_sources(self, technology, serv=""):
        self.selected_source = ""
        dialog = QDialog()
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.setWindowTitle('Source selection')
        label = QLabel(dialog)
        label.setGeometry(15, 20, 315, 40)
        label.setText("Select the source for your technology")
        combo_box = QComboBox(dialog)
        combo_box.setGeometry(15, 50, 300, 30)
        combo_box.setObjectName("combo_box")

        if technology == self.seasonal_waste_heat_pump[0]:
            combo_box.addItems([self.sources_for_technology[15],
                                self.sources_for_technology[16],
                                self.sources_for_technology[17]])

        if technology =="Waste heat ORC":
            combo_box.addItems([self.sources_for_technology[14]])

        if technology == self.waste_heat_heat_pumps_temperature_group1[0] or technology == self.waste_heat_heat_pumps_temperature_group1[1]:
            combo_box.addItems([self.sources_for_technology[21],
                                self.sources_for_technology[28],
                                self.sources_for_technology[18],
                                self.sources_for_technology[19],
                                self.sources_for_technology[20],
                                self.sources_for_technology[22]
                                ])
        elif technology == self.waste_heat_heat_pumps_temperature_group2[0] or technology == self.waste_heat_heat_pumps_temperature_group2[1]:  # Medium T
            combo_box.addItems([self.sources_for_technology[14],
                                self.sources_for_technology[15],
                                self.sources_for_technology[16],
                                self.sources_for_technology[17]])

        elif technology == self.waste_heat_heat_pumps_temperature_group3[0] or technology == self.waste_heat_heat_pumps_temperature_group3[1]:  # High T
            combo_box.addItems([self.sources_for_technology[16],
                                self.sources_for_technology[15],
                                self.sources_for_technology[14],
                                self.sources_for_technology[17]])

        elif technology == self.heat_pump[0]:
            combo_box.addItems([self.sources_for_technology[5],
                                self.sources_for_technology[8]
                                ])
        elif technology == self.heat_pump[1]:
            combo_box.addItems([self.sources_for_technology[5],
                                self.sources_for_technology[8]
                                ])

        elif technology == self.waste_heat_absorption_heat_pump[0]:
            combo_box.addItems([self.sources_for_technology[15],
                                self.sources_for_technology[8],
                                self.sources_for_technology[14],
                                self.sources_for_technology[16],
                                self.sources_for_technology[20],
                                self.sources_for_technology[21],
                                self.sources_for_technology[17],
                                self.sources_for_technology[22],
                                self.sources_for_technology[19]
                                ])

        button = QPushButton(dialog)
        button.setGeometry(200, 85, 115, 20)
        button.setText("Select source")
        button.clicked.connect(lambda: self.source_for_tech_selected(dialog, combo_box))
        dialog.exec()

    def source_for_tech_selected(self, dialog, combo_box):
        text = combo_box.currentText()
        self.selected_source = text
        dialog.close()

    def tech_paramaters_conversion(self, val_list):
        val_list[self.name_to_index("p_max")] = val_list[self.name_to_index("p_max")] / 1000
        val_list[self.name_to_index("p_min")] = val_list[self.name_to_index("p_min")] / 1000
        val_list[self.name_to_index("fuel_cost")] = val_list[self.name_to_index("fuel_cost")] * 1000
        val_list[self.name_to_index("variable_cost")] = val_list[self.name_to_index("variable_cost")] * 1000
        val_list[self.name_to_index("fixed_cost")] = val_list[self.name_to_index("fixed_cost")] * 1000
        # val_list[self.name_to_index("tech_min")] = val_list[self.name_to_index("tech_min")] / 1000
        val_list[self.name_to_index("ramp_up_down")] = val_list[self.name_to_index("ramp_up_down")] / 100  # 100 not 1000
        val_list[self.name_to_index("tes_size")] = val_list[self.name_to_index("tes_size")] / 1000
        val_list[self.name_to_index("tes_loss")] = val_list[self.name_to_index("tes_loss")] / 100  # 100 not 1000
        val_list[self.name_to_index("tes_startEnd")] = val_list[self.name_to_index("tes_startEnd")] / 1000

    def tech_paramaters_district_conversion(self, val_list):
        val_list[self.district_name_to_index("ramp_up_down")] = val_list[self.district_name_to_index("ramp_up_down")] / 100  # 100 not 1000
        val_list[self.district_name_to_index("tes_loss")] = val_list[self.district_name_to_index("tes_loss")] / 100  # 100 not 1000

    def write_electricity_file(self, dr, val_list):
        print("DistrictSImulator.write_electricity_file(), dr:", dr)
        if dr is None:
            print("DistrictSimulator.write_electricity_file(). Directory is None!")
            return
        file_path = os.path.join(dr, "Electricity_price_time.csv")
        if os.path.isfile(file_path):
            file_object = open(file_path, "w")
            for i in range(self.h8760):
                file_object.write(str(val_list[self.name_to_index("fuel_cost")])+"\n")
            file_object.close()

    def write_electricity_file_district(self, dr, val_list):
        print("DistrictSImulator.write_electricity_file_district(), dr:", dr)
        if dr is None:
            print("DistrictSimulator.write_electricity_file(). Directory is None!")
            return
        file_path = os.path.join(dr, "Electricity_price_time.csv")
        if os.path.isfile(file_path):
            file_object = open(file_path, "w")
            for i in range(self.h8760):
                file_object.write(str(val_list[self.district_name_to_index("fuel_cost")])+"\n")
            file_object.close()
				
    def gen_default_julia_files(self, dr):
        print("DistrictSimulator.gen_default_julia_files() dr:", dr)
        if dr is None:
            print("DistrictSimulator.gen_default_julia_files(). Directory is None!")
            return

        file_path = os.path.join(dr, "Electricity_price_time.csv")
        if not os.path.isfile(file_path):
            file_object = open(file_path, "w")
            for i in range(self.h8760):
                file_object.write(str("0.1\n"))
            file_object.close()

        file_path = os.path.join(dr, "Heat_exchanger_specific_time.csv")
        if not os.path.isfile(file_path):
            input_default_file = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "default_data", "Heat_exchanger_specific_time.csv"), "r")
            input_default_data = []
            for i in range(self.h8760):
                input_default_data.append(input_default_file.readline())
            input_default_file.close()

            file_object = open(file_path, "w")
            for i in range(self.h8760):
                file_object.write(str(input_default_data[i]))
            file_object.close()

        file_path = os.path.join(dr, "COP_heat_pump_temperature_group_seasonal.csv")
        if not os.path.isfile(file_path):
            file_object = open(file_path, "w")
            for i in range(self.h8760):
                file_object.write(str("1.0\n"))
            file_object.close()

        file_path = os.path.join(dr, "ORC_waste_heat_availability.csv")
        if not os.path.isfile(file_path):
            file_object = open(file_path, "w")
            for i in range(self.h8760):
                file_object.write(str("1.0\n"))
            file_object.close()

    def write_solar_panel_area_in_widget(self, tech: QTreeWidgetItem, tech_infos: dict):
        if tech.text(0) in ["Seasonal Solar Thermal", "Evacuated tube solar collectors", "Flat plate solar collectors"]:
            tech.setData(3, Qt.UserRole, QVariant(str(tech_infos["A_ST"])))

            

