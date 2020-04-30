from PyQt5.QtWidgets import QTableWidget, QSpinBox
from ...config import tableConfig


class ResultCalculator:

    def __init__(self, gui, sim_gui):
        self.sim_gui = sim_gui

    def get_heating_hot_extracted(self):
        return self.__get_hot_extracted(tableConfig.hig_temp_techs, self.sim_gui.sbs_heat, self.sim_gui.share_heat)

    def get_heating_medium_extracted(self):
        return self.__get_hot_extracted(tableConfig.med_temp_techs, self.sim_gui.sbs_heat, self.sim_gui.share_heat)

    def get_heating_low_extracted(self):
        return self.__get_hot_extracted(tableConfig.low_temp_techs, self.sim_gui.sbs_heat, self.sim_gui.share_heat)

    def get_heating_dhw_extracted(self):
        return self.__get_hot_extracted(tableConfig.data_rows, self.sim_gui.sbs_dhw, self.sim_gui.share)

    def get_cooling_extracted(self):
        return self.__get_total_useful(self.__build_config(self.sim_gui.sim_sbs_cool_source,
                                                           self.sim_gui.dist_cool_net,
                                                           None, None, tableConfig.data_rows_cool, 0))

    def __get_hot_extracted(self, temp_techs: list, SBS_param: QSpinBox, district_param: QSpinBox):
        return self.__get_total_useful(self.__build_config(self.sim_gui.sim_sbs_hdhw_Source,
                                                           self.sim_gui.dist_heat_source,
                                                           SBS_param, district_param, temp_techs, 0))

    def __build_config(self, SBS_widget: QTableWidget, district_widget: QTableWidget, SBS_param: QSpinBox or None,
                       district_param: QSpinBox or None, tech_list: list, column: int):
        config = {"tables": [{"widget": SBS_widget, "type": "SBS"}, {"widget": district_widget, "type": "district"}],
                  "parameters": {"SBS": 1.0 if SBS_param is None else SBS_param.value()/100,
                                 "district": 1.0 if district_param is None else district_param.value()/100},
                  "tech_list": tech_list, "column": column}
        return config

    def __get_total_useful(self, config: dict):
        total = 0.0
        for table in config["tables"]:
            for tech_index in config["tech_list"]:
                try:
                    total += float(table["widget"].item(tech_index, config["column"]).text()) * config["parameters"][
                        table["type"]]
                except:
                    pass
        return total
