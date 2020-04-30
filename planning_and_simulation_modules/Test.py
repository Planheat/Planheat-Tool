from PyQt5.QtWidgets import QTreeWidgetItem

from .technology.Technology import Technology


class Test:

    def __init__(self):
        self.active = False  # completely enable or disable tests
        self.tech_tab = None  # baseline_buildings
        self.tech_future_buildings_widget_tab = None
        self.network_tree_widget_baseline = None
        self.network_tree_widget_future = None
        self.step5 = None
        self.KPIs = {'sources': ['Heating Oil', 'Natural gas', 'Electricity', 'Deep geothermal',
                                 'Geothermal - Shallow - Ground heat extraction',
                                 'Geothermal - Shallow - Ground cold extraction', 'Solar thermal',
                                 'Excess heat Industry', 'Excess heat - Data centers', 'Excess heat - Supermarkets',
                                 'Excess heat - Refrigerated storage facilities', 'Excess heat - Indoor carparkings',
                                 'Excess heat - Subway networks', 'Urban waste water treatment plant',
                                 'Water - Waste water - Sewer system',
                                 'Water - Surface water - Rivers cold extraction heat pump',
                                 'Water - Surface water - Rivers cold extraction from free cooling HEX',
                                 'Water - Surface water - Lakes heat extraction with heat pump',
                                 'Water - Surface water - Lakes cold extraction with heat pump',
                                 'Water - Surface water - Rivers heat extraction heat pump',
                                 'LNG terminals excess cooling', 'Biomass Forestry', 'generic source'], 'EN_1.1': 34.2,
                     'EN_1.1R': 34.2, 'EN_1.1T': 0.0, 'EN_1.2': 0.17, 'EN_1.2R': 0.17, 'EN_1.2T': 'Nan', 'EN_2.1': 'Nan',
                     'EN_2.1R': 'Nan', 'EN_2.1T': 'Nan', 'EN_2.2': 'Nan', 'EN_2.2R': 'Nan', 'EN_2.2T': 'Nan',
                     'EN_2.1_s0': 0.0, 'EN_2.1_s1': 0.0, 'EN_2.1_s2': 0.0, 'EN_2.1_s3': 0.0, 'EN_2.1_s4': 0.0,
                     'EN_2.1_s5': 0.0, 'EN_2.1_s6': 0.0, 'EN_2.1_s7': 0.0, 'EN_2.1_s8': 0.0, 'EN_2.1_s9': 0.0,
                     'EN_2.1_s10': 0.0, 'EN_2.1_s11': 0.0, 'EN_2.1_s12': 0.0, 'EN_2.1_s13': 0.0, 'EN_2.1_s14': 0.0,
                     'EN_2.1_s15': 0.0, 'EN_2.1_s16': 0.0, 'EN_2.1_s17': 0.0, 'EN_2.1_s18': 0.0, 'EN_2.1_s19': 0.0,
                     'EN_2.1_s20': 0.0, 'EN_2.1_s21': 34.2, 'EN_2.1_s22': 0.0, 'EN_2.1R_s0': 0.0, 'EN_2.1R_s1': 0.0,
                     'EN_2.1R_s2': 0.0, 'EN_2.1R_s3': 0.0, 'EN_2.1R_s4': 0.0, 'EN_2.1R_s5': 0.0, 'EN_2.1R_s6': 0.0,
                     'EN_2.1R_s7': 0.0, 'EN_2.1R_s8': 0.0, 'EN_2.1R_s9': 0, 'EN_2.1R_s10': 0.0, 'EN_2.1R_s11': 0.0,
                     'EN_2.1R_s12': 0.0, 'EN_2.1R_s13': 0.0, 'EN_2.1R_s14': 0.0, 'EN_2.1R_s15': 0.0, 'EN_2.1R_s16': 0.0,
                     'EN_2.1R_s17': 0.0, 'EN_2.1R_s18': 0.0, 'EN_2.1R_s19': 0.0, 'EN_2.1R_s20': 0.0,
                     'EN_2.1R_s21': 34.2, 'EN_2.1R_s22': 0.0, 'EN_2.1T_s0': 0, 'EN_2.1T_s1': 0, 'EN_2.1T_s2': 0,
                     'EN_2.1T_s3': 0, 'EN_2.1T_s4': 0, 'EN_2.1T_s5': 0, 'EN_2.1T_s6': 0, 'EN_2.1T_s7': 0,
                     'EN_2.1T_s8': 0, 'EN_2.1T_s9': 0, 'EN_2.1T_s10': 0, 'EN_2.1T_s11': 0, 'EN_2.1T_s12': 0,
                     'EN_2.1T_s13': 0, 'EN_2.1T_s14': 0, 'EN_2.1T_s15': 0, 'EN_2.1T_s16': 0, 'EN_2.1T_s17': 0,
                     'EN_2.1T_s18': 0, 'EN_2.1T_s19': 0, 'EN_2.1T_s20': 0, 'EN_2.1T_s21': 0, 'EN_2.1T_s22': 0,
                     'EN_2.2_s0': 0.0, 'EN_2.2_s1': 0.0, 'EN_2.2_s2': 0.0, 'EN_2.2_s3': 0.0, 'EN_2.2_s4': 0.0,
                     'EN_2.2_s5': 0.0, 'EN_2.2_s6': 0.0, 'EN_2.2_s7': 0.0, 'EN_2.2_s8': 0.0, 'EN_2.2_s9': 0.0,
                     'EN_2.2_s10': 0.0, 'EN_2.2_s11': 0.0, 'EN_2.2_s12': 0.0, 'EN_2.2_s13': 0.0, 'EN_2.2_s14': 0.0,
                     'EN_2.2_s15': 0.0, 'EN_2.2_s16': 0.0, 'EN_2.2_s17': 0.0, 'EN_2.2_s18': 0.0, 'EN_2.2_s19': 0.0,
                     'EN_2.2_s20': 0.0, 'EN_2.2_s21': 0.17, 'EN_2.2_s22': 0.0, 'EN_2.2R_s0': 0.0, 'EN_2.2R_s1': 0.0,
                     'EN_2.2R_s2': 0.0, 'EN_2.2R_s3': 0.0, 'EN_2.2R_s4': 0.0, 'EN_2.2R_s5': 0.0, 'EN_2.2R_s6': 0.0,
                     'EN_2.2R_s7': 0.0, 'EN_2.2R_s8': 0.0, 'EN_2.2R_s9': 0.0, 'EN_2.2R_s11': 0.0, 'EN_2.2R_s12': 0.0,
                     'EN_2.2R_s13': 0.0, 'EN_2.2R_s14': 0.0, 'EN_2.2R_s15': 0.0, 'EN_2.2R_s16': 0.0, 'EN_2.2R_s18': 0.0,
                     'EN_2.2R_s19': 0.0, 'EN_2.2R_s20': 0.0, 'EN_2.2R_s21': 0.17, 'EN_2.2R_s22': 0.0, 'EN_2.2T_s0': 0.0,
                     'EN_2.2T_s1': 0.0, 'EN_2.2T_s2': 0.0, 'EN_2.2T_s3': 0.0, 'EN_2.2T_s4': 0.0, 'EN_2.2T_s5': 0.0,
                     'EN_2.2T_s6': 0.0, 'EN_2.2T_s7': 0.0, 'EN_2.2T_s8': 0.0, 'EN_2.2T_s9': 0.0, 'EN_2.2T_s10': 0.0,
                     'EN_2.2T_s11': 0.0, 'EN_2.2T_s12': 0.0, 'EN_2.2T_s13': 0.0, 'EN_2.2T_s14': 0.0, 'EN_2.2T_s15': 0.0,
                     'EN_2.2T_s16': 0.0, 'EN_2.2T_s17': 0.0, 'EN_2.2T_s18': 0.0, 'EN_2.2T_s19': 0.0, 'EN_2.2T_s20': 0.0,
                     'EN_2.2T_s21': 0.0, 'EN_2.2T_s22': 0.0,
                     'pecADG_baseline': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                         0.0, 0.0, 0.0, 0.0, 0.0, 68.4, 0.0],
                     'pecADG_baselineR': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 68.4, 0.0],
                     'pecADG_baselineT': [0, 0.0, 0.0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0,
                                          0.0, 0.0, 0.0, 0, 0.0, 0], 'EN_3.1': 34.2, 'EN_3.1R': 34.2, 'EN_3.1T': 0.0,
                     'EN_3.2': 0.17, 'EN_3.2R': 0.17, 'EN_3.2T': 'Nan', 'EN_4.1': 34.2, 'EN_4.1T': 0.0, 'EN_4.1R': 34.2,
                     'EN_4.2': 100.0, 'EN_4.2R': 100.0, 'EN_4.2T': 'Nan', 'EN_5.1': 0.0, 'EN_5.1R': 0.0, 'EN_5.1T': 0.0,
                     'EN_5.2': 0.0, 'EN_5.2R': 0.0, 'EN_5.2T': 0.0, 'EN_6.1': 0.0, 'EN_6.1R': 0.0, 'EN_6.1T': 0.0,
                     'EN_6.2': 0.0, 'EN_6.2R': 0.0, 'EN_6.2T': 0.0, 'EN_7.1': 0.0, 'EN_7.1R': 0.0, 'EN_7.1T': 0.0,
                     'EN_7.2': 0.0, 'EN_7.2R': 0.0, 'EN_7.2T': 0.0, 'EN_9.1': 0.0, 'EN_9.1R': 0.0, 'EN_9.1T': 'Nan',
                     'EN_11.3': 0.0, 'EN_11.3R': 0.0, 'EN_11.3T': 'Nan', 'EN_11.2': 0.0, 'EN_11.2R': 0.0, 'EN_11.2T': 0,
                     'EN_12.1': 100.0, 'EN_12.1R': 100.0, 'EN_12.1T': 'inf', 'EN_13.1': '-', 'EN_13.1R': '-',
                     'EN_13.1T': '-', 'EN_13.1b': '-', 'EN_13.1bR': '-', 'EN_13.1bT': '-', 'EN_14.1': '-',
                     'EN_14.1R': '-', 'EN_14.1T': '-', 'EN_14.1b': '-', 'EN_14.1bR': '-', 'EN_14.1bT': '-',
                     'EN_15.1': {'Biomass Forestry': [34.20194167999973, 20.0], 'Deep geothermal': [0, 0],
                                 'Geothermal - Shallow - Ground heat extraction': [0, 0],
                                 'Geothermal - Shallow - Ground cold extraction': [0, 0], 'Solar thermal': [0, 0],
                                 'Excess heat Industry': [0, 0], 'Excess heat - Data centers': [0, 0],
                                 'Excess heat - Supermarkets': [0, 0],
                                 'Excess heat - Refrigerated storage facilities': [0, 0],
                                 'Excess heat - Indoor carparkings': [0, 0], 'Excess heat - Subway networks': [0, 0],
                                 'Urban waste water treatment plant': [0, 0],
                                 'Water - Waste water - Sewer system': [0, 0],
                                 'Water - Surface water - Rivers cold extraction heat pump': [0, 0],
                                 'Water - Surface water - Rivers cold extraction from free cooling': [0, 0],
                                 'Water - Surface water - Lakes heat extraction with heat pump': [0, 0],
                                 'Water - Surface water - Lakes cold extraction with heat pump': [0, 0],
                                 'Excess cooling - LNG terminals': [0, 0], 'Generic heating/cooling source': [0, 0],
                                 'Water - Surface water - Rivers heat extraction heat pump': [0, 0]}, 'EN_15.1R': 'Nan',
                     'EN_15.1T': 'Nan', 'ENV_1.3': 34.2, 'ENV_1.3R': 34.2, 'ENV_1.3T': 0.0, 'ENV_1.4': 1.0,
                     'ENV_1.4R': 1.0, 'ENV_1.4T': 'Nan', 'ENV_2.1': 34.2, 'ENV_2.1R': 34.2, 'ENV_2.1T': 0.0,
                     'ENV_2.2': 1.0, 'ENV_2.2R': 1.0, 'ENV_2.2T': 'Nan', 'ENV_2.7': 34.2, 'ENV_2.7R': 34.2,
                     'ENV_2.7T': 0.0, 'ENV_2.8': 1.0, 'ENV_2.8R': 1.0, 'ENV_2.8T': 'Nan', 'ENV_2.13': 34.2,
                     'ENV_2.13R': 34.2, 'ENV_2.13T': 0.0, 'ENV_2.14': 1.0, 'ENV_2.14R': 1.0, 'ENV_2.14T': 'Nan',
                     'SO_3.1': 'Nan', 'SO_3.1R': 'Nan', 'SO_3.1T': 'Nan',
                     'ECO_2.1': 'Nan', 'ECO_2.1R': 'Nan', 'ECO_2.1T': 'Nan',
                     'OeM_cost_saving': 0.0, 'OeM_cost_savingR': 0.0, 'OeM_cost_savingT': 0.0,
                     'fuel_cost_saving': 0.0, 'fuel_cost_savingR': 0.0, 'fuel_cost_savingT': 0.0}

        tech_cooling = ["Air source compression chiller",
                        "Shallow geothermal compression chiller",
                        "Air source gas absorption chiller",
                        "Shallow geothermal Gas absorption chiller"]

        tech_heating = ["Thermal energy storage",
                        "Gas Boiler",
                        "Biomass Boiler",
                        "Oil Boiler",
                        "Gas CHP",
                        "Oil CHP",
                        "Biomass CHP",
                        "Air Source Compression Heat Pump",
                        "Shallow geothermal compression heat pump",
                        "Air source gas absorption heat pump",
                        "Shallow geothermal gas absorption heat pump",
                        "Evacuated tube solar collectors",
                        "Flat plate solar collectors"]

        tech_DHW = ["Thermal energy storage",
                    "Gas Boiler",
                    "Biomass Boiler",
                    "Oil Boiler",
                    "Electrical Heater",
                    "Gas CHP",
                    "Oil CHP",
                    "Biomass CHP",
                    "Air Source Compression Heat Pump",
                    "Shallow geothermal compression heat pump",
                    "Air source gas absorption heat pump",
                    "Shallow geothermal gas absorption heat pump",
                    "Evacuated tube solar collectors",
                    "Flat plate solar collectors"]

        sources = ['Biomass Forestry',  # [0]
                   'Deep geothermal',  # [1]
                   'Geothermal - Shallow - Ground heat extraction',  # [2]
                   'Geothermal - Shallow - Ground cold extraction',  # [3]
                   'Solar thermal',  # [4]
                   'Solar thermal',  # [5]
                   'Excess heat Industry',  # [6]
                   'Excess heat - Data centers',  # [7]
                   'Excess heat - Data centers',  # [8]
                   'Excess heat - Supermarkets',  # [9]
                   'Excess heat - Refrigerated storage facilities',  # [10]
                   'Excess heat - Indoor carparkings',  # [11]
                   'Excess heat - Subway networks',  # [12]
                   'Urban waste water treatment plant',  # [13]
                   'Water - Waste water - Sewer system',  # [14]
                   'Water - Surface water - Rivers cold extraction heat pump',  # [15]
                   'Water - Surface water - Rivers cold extraction from free cooling',  # [16]
                   'Water - Surface water - Lakes heat extraction with heat pump',  # [17]
                   'Water - Surface water - Lakes cold extraction with heat pump',  # [18]
                   'Excess cooling - LNG terminals',  # [19]
                   'Generic heating/cooling source',  # [20]
                   'Water - Surface water - Rivers heat extraction heat pump'  # [21]
                   ]

        technology018 = Technology(technology="Oil CHP",
                                   source="Heating Oil",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=0.1,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=30.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=31.25,
                                   variable_cost=0.001,
                                   fuel_cost=0.08,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=1.0)

        technology019 = Technology(technology="Air source gas absorption heat pump",
                                   source="Air",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=1,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=16.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=31.25,
                                   variable_cost=0.001,
                                   fuel_cost=0.08,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=1.0)

        technology020 = Technology(technology="Oil CHP",
                                   source="Heating Oil",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=0.1,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=16.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=31.25,
                                   variable_cost=0.001,
                                   fuel_cost=0.08,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=1.0)

        technology021 = Technology(technology="Shallow geothermal compression heat pump",
                                   source="Geothermal - Shallow - Ground heat extraction",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=1,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=8.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=31.25,
                                   variable_cost=0.01,
                                   fuel_cost=0.08,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=1.0)

        technology022 = Technology(technology="Air source gas absorption heat pump",
                                   source="Air",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=1,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=35.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=31.25,
                                   variable_cost=0.001,
                                   fuel_cost=0.08,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=1.0)

        technology023 = Technology(technology="Gas Boiler",
                                   source="Natural gas",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=0.9,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=30.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=6250,
                                   variable_cost=1,
                                   fuel_cost=1,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=0.0)

        technology024 = Technology(technology="Biomass Boiler",
                                   source="Biomass Forestry",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=0.9,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=20.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=200,
                                   variable_cost=0.1,
                                   fuel_cost=0.1,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=1.0)

        technology025 = Technology(technology="Biomass Boiler",
                                   source="Biomass Forestry",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=0.95,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=30.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=5000,
                                   variable_cost=0.1,
                                   fuel_cost=0.1,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=0.0)

        technology026 = Technology(technology="Biomass Boiler",
                                   source="Biomass Forestry",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=0.95,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=20.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=5000,
                                   variable_cost=100,
                                   fuel_cost=100,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=0.0)

        technology027 = Technology(technology="Flat plate solar collectors",
                                   source="Solar thermal",
                                   inclinazione=33.0,
                                   temperature=40,
                                   eta_optical=1.00,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=30.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=0.01,
                                   variable_cost=0.01,
                                   fuel_cost=0.01,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=0.0)

        technology028 = Technology(technology="Biomass Boiler",
                                   source="Biomass Forestry",
                                   inclinazione=33.0,
                                   temperature=75,
                                   eta_optical=0.95,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=40.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=5000,
                                   variable_cost=100,
                                   fuel_cost=100,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=0.0)

        technology029 = Technology(technology="Flat plate solar collectors",
                                   source="Solar thermal",
                                   inclinazione=33.0,
                                   temperature=40,
                                   eta_optical=1.00,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=30.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=0.5,
                                   variable_cost=0.01,
                                   fuel_cost=0.01,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=0.0)

        technology030 = Technology(technology="Flat plate solar collectors",
                                   source="Solar thermal",
                                   inclinazione=33.0,
                                   temperature=40,
                                   eta_optical=1.00,
                                   first_order_coeff=0.5,
                                   second_order_coeff=0.006,
                                   p_max=30.0,
                                   p_min=0.0,
                                   power_to_heat_ratio=1.0,
                                   tech_min=0.0,
                                   ramp_up=100,
                                   fixed_cost=0.5,
                                   variable_cost=0.01,
                                   fuel_cost=0.01,
                                   tes_size=1.0,
                                   SOC_min=1.0,
                                   tes_startEnd=1,
                                   tes_discharge=1,
                                   cop_absorption=1.0,
                                   el_sale=0.0)

        technology100 = QTreeWidgetItem([str(" "),
                                         str("Gas Boiler"),  # technology
                                         str("Natural gas"),  # source
                                         str(3.0),  # area
                                         str(4.0),  # temperature
                                         str(0.5),  # efficiency
                                         str(6.0),  # first_order
                                         str(7.0),  # second_order
                                         str(123.0),  # p_max
                                         str(9.0),  # p_min
                                         str(10.0),  # powerToRation
                                         str(11.0),  # tech_min
                                         str(100.0),  # ramp_upDown
                                         str(13.0),  # fix
                                         str(14.0),  # fuel
                                         str(15.0),  # variable
                                         str(16.0),  # tes_size
                                         str(17.0),  # soc_min
                                         str(18.0),  # tes_startEnd
                                         str(19.0),  # tes_discharge
                                         str(20.0),  # COP_absorption
                                         str(21.0)])  # el_sale

        technology101 = QTreeWidgetItem([str(" "),
                                         str("Gas Boiler"),  # technology
                                         str("Natural gas"),  # source
                                         str(3.0),  # area
                                         str(4.0),  # temperature
                                         str(1.0),  # efficiency
                                         str(6.0),  # first_order
                                         str(7.0),  # second_order
                                         str(123.0),  # p_max
                                         str(9.0),  # p_min
                                         str(10.0),  # powerToRation
                                         str(11.0),  # tech_min
                                         str(100.0),  # ramp_upDown
                                         str(13.0),  # fix [13]
                                         str(14.0),  # fuel [14]
                                         str(15.0),  # variable [15]
                                         str(16.0),  # tes_size
                                         str(17.0),  # soc_min
                                         str(18.0),  # tes_startEnd
                                         str(19.0),  # tes_discharge
                                         str(20.0),  # COP_absorption
                                         str(21.0)])  # el_sale

        # possible service: "Heating", "Cooling", "DHW"
        self.tech = {"16": {"Heating": [technology028]}}
        self.tech_buildings_future = {"16": {"Heating": [technology028]}}  # "15": {"Heating": [technology028, technology029]}}

        self.baseline_networks = [technology100]
        self.future_networks = [technology101]

    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---
    # --- END __init__() ---

    # auto fill tech for step1 buildings
    def run_test_step1(self):
        if not self.active:
            return
        Test.copy_building_tab(self.tech, self.tech_tab)

    def fill_baseline_network_widget(self):
        if not self.active:
            return
        Test.copy_networks(self.baseline_networks, self.network_tree_widget_baseline)

    # auto fill tech for step4 buildings
    def run_end_step3(self):
        if not self.active:
            return
        Test.clear_technologies_from_buildings_tree_widget(self.tech_future_buildings_widget_tab)
        Test.copy_building_tab(self.tech_buildings_future, self.tech_future_buildings_widget_tab)

    # inject fake baseline KPIs into the simulation module at the end of step4
    def run_end_step4(self):
        if not self.active:
            return
        self.step5.receive_KPIs(self.KPIs)

    # auto fill tech for step4 networks
    def run_end_step4_add_tech_network(self):
        if not self.active:
            return
        Test.copy_networks(self.future_networks, self.network_tree_widget_future)

    @staticmethod
    def clear_technologies_from_buildings_tree_widget(widget):
        for i in range(widget.topLevelItemCount()):
            building = widget.topLevelItem(i)
            for j in range(building.childCount()):
                service = building.child(j)
                for k in range(service.childCount()-1, -1, -1):
                    service.removeChild(service.child(k))

    @staticmethod
    def copy_building_tab(tech, tech_tab):
        for key in tech.keys():
            for i in range(tech_tab.topLevelItemCount()):
                building = tech_tab.topLevelItem(i)
                if building.text(0) == key:
                    for j in range(building.childCount()):
                        service = building.child(j)
                        try:
                            for tech_input in tech[key][service.text(0)]:
                                service.addChild(tech_input)
                        except KeyError:
                            pass

    @staticmethod
    def copy_networks(tech, tech_tab):
        if tech_tab.topLevelItemCount() == 0:
            return
        for technology in tech:
            for i in range(tech_tab.topLevelItemCount()):
                try:
                    tech_tab.topLevelItem(i).addChild(technology)
                    break
                except RuntimeError:
                    pass
