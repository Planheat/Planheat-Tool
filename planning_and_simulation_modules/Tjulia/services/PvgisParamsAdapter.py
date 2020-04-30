from ...config.pvgis import default_params
from ...utility.pvgis.PvgisApi import PvgisApi
from ...building.Building import Building
from ...Network import Network
from ...VITO.mapping.MappingModuleInterface import MappingModuleInterface

class PvgisParamsAdapter:

    def __init__(self, pvgis_api: PvgisApi):
        self.pvgis_api = pvgis_api

    def update_params(self, item: Building or Network, scenario="baseline"):
        # mapping_module_interface = MappingModuleInterface()
        lat, lon = item.get_coordinates()
        # scenario = item.scenario_type
        # if scenario == "baseline":
        #     startyear = mapping_module_interface.get_baseline_year()
        # else:
        #     startyear = mapping_module_interface.get_future_year()
        startyear = 2015
        endyear = startyear
        self.pvgis_api.update_common_params(lat=lat, lon=lon, startyear=startyear, endyear=endyear)
        if isinstance(item, Building):
            self.pvgis_api.key_to_query["ot"] = True
            self.pvgis_api.key_to_query["gsi_1"] = True
            self.pvgis_api.key_to_query["gsi_2"] = False
            self.pvgis_api.key_to_query["gsi_s"] = False
            self.pvgis_api.params["gsi_1"]["optimalangles"] = 0
            self.pvgis_api.params["gsi_1"]["aspect"] = 0
            # self.pvgis_api.params["gsi_1"]["angle"] = 0 <- set by DistrictSimulator
        if isinstance(item, Network):
            self.pvgis_api.key_to_query["ot"] = True
            self.pvgis_api.key_to_query["gsi_1"] = True
            self.pvgis_api.key_to_query["gsi_2"] = True
            self.pvgis_api.key_to_query["gsi_s"] = True
            self.pvgis_api.params["gsi_1"]["optimalangles"] = 1
            self.pvgis_api.params["gsi_2"]["optimalangles"] = 1
            self.pvgis_api.params["gsi_s"]["optimalangles"] = 1

    def set_only_ot(self):
        self.pvgis_api.key_to_query["ot"] = True
        self.pvgis_api.key_to_query["gsi_1"] = False
        self.pvgis_api.key_to_query["gsi_2"] = False
        self.pvgis_api.key_to_query["gsi_s"] = False



