class SourcesTableFactors:

    def __init__(self):
        self.table_data = {
            "Biomass Forestry": {"pef": 1, "CO2": 1, "NOx": 1, "SOx": 1, "PM10": 1, "hidden": False},
            "Deep geothermal": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Geothermal - Shallow - Ground heat extraction": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Geothermal - Shallow - Ground cold extraction": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Solar thermal": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Excess heat Industry": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Excess heat - Data centers": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Excess heat - Supermarkets": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Excess heat - Refrigerated storage facilities": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Excess heat - Indoor carparkings": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Excess heat - Subway networks": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Urban waste water treatment plant": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Water - Waste water - Sewer system": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Water - Surface water - Rivers cold extraction heat pump": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Water - Surface water - Rivers cold extraction from free cooling": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Water - Surface water - Lakes heat extraction with heat pump": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Water - Surface water - Lakes cold extraction with heat pump": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Excess cooling - LNG terminals": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Generic heating/cooling source": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Water - Surface water - Rivers heat extraction heat pump": {"pef": 1, "CO2": 0, "NOx": 0, "SOx": 0, "PM10": 0, "hidden": True},
            "Natural gas": {"pef": 1, "CO2": 1, "NOx": 1, "SOx": 1, "PM10": 1, "hidden": False},
            "Electricity": {"pef": 1, "CO2": 1, "NOx": 1, "SOx": 1, "PM10": 1, "hidden": False},
            "Heating Oil": {"pef": 1, "CO2": 1, "NOx": 1, "SOx": 1, "PM10": 1, "hidden": False},
            "Coal and Peat": {"pef": 1, "CO2": 1, "NOx": 1, "SOx": 1, "PM10": 1, "hidden": False}
        }

    def get_hidden_rows(self):
        output_list = []
        try:
            for key in self.table_data.keys():
                if self.table_data[key]["hidden"]:
                    output_list.append(key)
            return output_list
        except Exception:
            return output_list


    def get_params(self, key):
        output_list = []
        try:
            output_list.append(self.table_data[key]["pef"])
            output_list.append(self.table_data[key]["CO2"])
            output_list.append(self.table_data[key]["NOx"])
            output_list.append(self.table_data[key]["SOx"])
            output_list.append(self.table_data[key]["PM10"])
            return output_list
        except Exception:
            return output_list
