from PyQt5.QtWidgets import QTreeWidgetItem


class SolarParameterBuilder:

    def __init__(self):
        self.solar_params = {"gsi_1": {"T_mean": 70, "eta_opt": 0.7, "a1": 3.1, "a2": 0.0005},
                             "gsi_2": {"T_mean": 70, "eta_opt": 0.7, "a1": 3.1, "a2": 0.0005},
                             "gsi_s": {"T_mean": 70, "eta_opt": 0.7, "a1": 3.1, "a2": 0.0005}}

    def update_param_from_tech_widget(self, julia_category, item: QTreeWidgetItem, switcher):
        key = self.julia_category_to_key(julia_category)
        if key is None:
            return
        print("SolarParameterBuilder:", switcher("temperature"))
        print("SolarParameterBuilder:", item.text(switcher("temperature")))
        self.solar_params[key]["T_mean"] = float(item.text(switcher("temperature")))
        self.solar_params[key]["eta_opt"] = float(item.text(switcher("eta_optical")))
        self.solar_params[key]["a1"] = float(item.text(switcher("first_order_coeff")))
        self.solar_params[key]["a2"] = float(item.text(switcher("second_order_coeff")))

    def julia_category_to_key(self, julia_category):
        if julia_category == "ST":
            return "gsi_1"
        if julia_category == "ST_2":
            return "gsi_2"
        if julia_category == "ST_seasonal":
            return "gsi_s"



