def create_base_tech_infos():
    tech_infos = {}
    ####### Technology input data ########
    ## Heat only boiler ##

    # Installed capacity [MW]
    tech_infos["P_max_HOB"] = 1
    # Efficiency [-]
    tech_infos["eta_HOB"] = 0.8
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB"] = 5.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB"] = 10
    tech_infos["tec_min_HOB"] = 0.0
    tech_infos["Percentage_ramp_up_down_HOB"] = 1

    ## Heat only boiler 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HOB_2"] = 1
    # Efficiency [-]
    tech_infos["eta_HOB_2"] = 0.8
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB_2"] = 5.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB_2"] = 12.5
    tech_infos["tec_min_HOB_2"] = 0.0
    tech_infos["Percentage_ramp_up_down_HOB_2"] = 1

    ## Electrical heater ##

    # Installed capacity [MW]
    tech_infos["P_max_EH"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_EH"] = 0
    # Efficiency [-]
    tech_infos["eta_EH"] = 0.98
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_EH"] = 0.5
    tech_infos["Technical_minimum_EH"] = 0
    tech_infos["Percentage_ramp_up_down_EH"] = 1
    tech_infos["cost_fuel_EH"] = 1.0

    ## Electrical heater 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_EH_2"] = 0
    # Efficiency [-]
    tech_infos["eta_EH_2"] = 0.98
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_EH_2"] = 0.7
    tech_infos["Technical_minimum_EH_2"] = 0
    tech_infos["Percentage_ramp_up_down_EH_2"] = 1
    tech_infos["cost_fuel_EH_2"] = 1.0

    ## Heat pump ##

    # Installed capacity [MW]
    tech_infos["P_max_HP"] = 1
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP"] = 0.5
    tech_infos["Technical_minimum_HP"] = 0.0
    tech_infos["Percentage_ramp_up_down_HP"] = 1
    tech_infos["cost_fuel_HP"] = 1

    ## Heat pump 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_2"] = 1
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_2"] = 0.5
    tech_infos["Technical_minimum_HP_2"] = 0.0
    tech_infos["Percentage_ramp_up_down_HP_2"] = 1
    tech_infos["cost_fuel_HP_2"] = 1

    ## Absorption heat pump ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_absorption"] = 1  # 1
    # Efficiency [-]
    tech_infos["eta_HP"] = 1.5
    tech_infos["cost_var_HP_absorption"] = 0.5
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HP_absorption"] = 20
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HP_absorption"] = 0.0
    tech_infos["Percentage_ramp_up_down_HP_absorption"] = 1


    ## Cogeneration ##

    # Installed capacity [MW]
    tech_infos["P_max_CHP"] = 0
    # Efficiency [-]
    tech_infos["eta_CHP_th"] = 0.65
    # Power-to-heat ratio [-]
    tech_infos["cb_CHP"] = 0.3
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_CHP"] = 3.9
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_CHP"] = 20
    tech_infos["Tecnical_minimum_CHP"] = 0.2
    tech_infos["Percentage_ramp_up_down_CHP"] = 0.7
    tech_infos["CHP_electricity_price"] = 1

    ## Solar thermal ##

    # Installed solar thermal collector area [m2]
    tech_infos["A_ST"] = 100
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_ST"] = 0.5

    ## Cooling heat pump ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_cool"] = 0.5
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_cool"] = 0.5
    tech_infos["Tecnical_minimum_HP_cool"] = 0.0
    tech_infos["Percentage_ramp_up_down_HP_cool"] = 1
    tech_infos["cost_fuel_HP_cool"] = 1

    ## Cooling heat pump 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_cool_2"] = 0.5
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_cool_2"] = 0.5
    tech_infos["Tecnical_minimum_HP_cool_2"] = 0.0
    tech_infos["Percentage_ramp_up_down_HP_cool_2"] = 1
    tech_infos["cost_fuel_HP_cool_2"] = 1

    ## Absorption Cooling heat pump ##
    tech_infos["P_max_HP_cool_absorption"] = 1.5
    tech_infos["eta_HP_cool_absorption"] = 0.9
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_cool_absorption"] = 0.5
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HP_cool_absorption"] = 20
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HP_cool_absorption"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_cool_absorption"] = 1

    ## Thermal energy storage ##

    # Thermal energy storage size [MWh]
    tech_infos["TES_size"] = 0
    # Minimum percentage of state of charge of thermal energy storage [-]
    tech_infos["SOC_min"] = 0.15
    # Thermal energy storage state of charge at the start/end of the year [-]
    tech_infos["TES_start_end"] = 0.5
    # Thermal storage charge/discharge capacity [MW]
    tech_infos["TES_charge_discharge_time"] = 5
    tech_infos["TES_loss"] = 0.5 / (24 * 7)

    ## Domestic hot water thermal energy storage ##

    # Thermal energy storage size [MWh]
    tech_infos["TES_size_DHW"] = 1
    # Minimum percentage of state of charge of thermal energy storage [-]
    tech_infos["SOC_min_DHW"] = 0.0
    # Thermal energy storage state of charge at the start/end of the year [-]
    tech_infos["TES_start_end_DHW"] = 0.0
    # Thermal storage charge/discharge capacity [MW]
    tech_infos["TES_charge_discharge_time_DHW"] = 5
    tech_infos["TES_loss_DHW"] = 0.5/(24*7)

    # Setting stuff to 0!
    tech_infos["TES_size_DHW"] = 0.0
    tech_infos["P_max_HP_cool_absorption"] = 0.0
    tech_infos["P_max_HP_cool_2"] = 0.0
    tech_infos["P_max_HP_cool"] = 0.0
    tech_infos["A_ST"] = 0.0
    tech_infos["P_max_HP_absorption"] = 0.0
    tech_infos["P_max_HP_2"] = 0.0
    tech_infos["P_max_HP"] = 0.0
    tech_infos["P_max_HOB_2"] = 0.0
    tech_infos["P_max_HOB"] = 0.0


    return tech_infos


def create_base_tech_district():
    tech_infos = {}
    ####### Technology input data ########

    ## Heat only boiler ##

    # Installed capacity [MW]
    tech_infos["P_max_HOB"] = 90
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HOB"] = 0.0
    # Efficiency [-]
    tech_infos["eta_HOB"] = 0.8
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HOB"] = 0.99
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB"] = 5.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB"] = 25

    ## Heat only boiler 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HOB_2"] = 0
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HOB_2"] = 0.0
    # Efficiency [-]
    tech_infos["eta_HOB_2"] = 0.8
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HOB_2"] = 0.8
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB_2"] = 5.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB_2"] = 12.5

    ## Heat only boiler 3 ##

    # Installed capacity [MW]
    tech_infos["P_max_HOB_3"] = 0
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HOB_3"] = 0.8
    # Efficiency [-]
    tech_infos["eta_HOB_3"] = 0.8
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HOB_3"] = 0.8
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB_3"] = 3.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB_3"] = 10

    ## Electrical heater ##

    # Installed capacity [MW]
    tech_infos["P_max_EH"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_EH"] = 0.1
    # Efficiency [-]
    tech_infos["eta_EH"] = 0.98
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_EH"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_EH"] = 0.5
    tech_infos["cost_fuel_EH"] = 1.0

    ## Electrical heater 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_EH_2"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_EH_2"] = 0.15
    # Efficiency [-]
    tech_infos["eta_EH_2"] = 0.98
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_EH_2"] = 0.9
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_EH_2"] = 0.7
    tech_infos["cost_fuel_EH_2"] = 1.0

    ## Electrical heater 3 ##

    # Installed capacity [MW]
    tech_infos["P_max_EH_3"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_EH_3"] = 0.1
    # Efficiency [-]
    tech_infos["eta_EH_3"] = 0.98
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_EH_3"] = 0.99
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_EH_3"] = 0.8
    tech_infos["cost_fuel_EH_3"] = 1.0

    ## Heat pump ##
    # Installed capacity [MW]
    tech_infos["P_max_HP"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP"] = 0.5
    tech_infos["cost_fuel_HP"] = 1.0

    ## Heat pump 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_2"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_2"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_2"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_2"] = 0.5
    tech_infos["cost_fuel_HP_2"] = 1.0

    ## Heat pump 3 ##
    # Installed capacity [MW]
    tech_infos["P_max_HP_3"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_3"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_3"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_3"] = 0.5
    tech_infos["cost_fuel_HP_3"] = 1.0

    ## Absorption heat pump ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_absorption"] = 30
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_absorption"] = 0.0
    # Efficiency [-]
    tech_infos["eta_HP_absorption"] = 1.4
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_absorption"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_absorption"] = 0.5
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HP_absorption"] = 25

    ## Cogeneration ##

    # Installed capacity [MW]
    tech_infos["P_max_CHP"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_CHP"] = 0.4
    # Efficiency [-]
    tech_infos["eta_CHP_th"] = 0.65
    # Power-to-heat ratio [-]
    tech_infos["cb_CHP"] = 0.3
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_CHP"] = 0.2
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_CHP"] = 3.9
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_CHP"] = 20
    tech_infos["CHP_electricity_price"] = 1.0

    ## Cogeneration 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_CHP_2"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_CHP_2"] = 0.4
    # Efficiency [-]
    tech_infos["eta_CHP_th_2"] = 0.65
    # Power-to-heat ratio [-]
    tech_infos["cb_CHP_2"] = 0.3
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_CHP_2"] = 0.2
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_CHP_2"] = 3.9
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_CHP_2"] = 15
    tech_infos["CHP_electricity_price_2"] = 1.0

    ## ORC Cogeneration ##

    # THERMAL installed capacity [MW]
    tech_infos["P_max_CHP_ORC"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_CHP_ORC"] = 0
    # Electrical efficiency [-]
    tech_infos["eta_CHP_el"] = 0.2
    # Power-to-heat ratio [-]
    tech_infos["cb_CHP_ORC"] = 0.25
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_CHP_ORC"] = 0.2
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_CHP_ORC"] = 0.5
    tech_infos["CHP_ORC_electricity_price"] = 1.0

    ## Solar thermal ##

    # Installed solar thermal collector area [m2]
    tech_infos["A_ST"] = 0
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_ST"] = 0.5

    ## Solar thermal 2 ##

    # Installed solar thermal collector area [m2]
    tech_infos["A_ST_2"] = 0
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_ST_2"] = 0.5

    ## Seasonal solar thermal ##
    # Installed solar thermal collector area [m2]
    tech_infos["A_ST_seasonal"] = 0
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_ST_seasonal"] = 0.5

    ## Waste heat - heat exchangers ##

    # Installed capacity [MW]
    tech_infos["P_HEX_capacity"] = 0
    # Technical minimum [MW]
    tech_infos["P_min_HEX"] = 0
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HEX"] = 0.25

    ## Waste heat - heat pumps - temperature group 1 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_I_1"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_I_1"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_1"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_I_1"] = 0.7
    tech_infos["cost_fuel_HP_waste_heat_I_1"] = 1.0

    ## Waste heat - heat pumps 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_I_2"] = 0  # 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_I_2"] = 0.0 # 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_2"] = 0.95
    tech_infos["cost_var_HP_waste_heat_I_2"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_I_2"] = 1.0

    ## Waste heat - heat pumps 3##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_I_3"] = 0  # 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_I_3"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_3"]= 0.95  # 0.95
    tech_infos["cost_var_HP_waste_heat_I_3"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_I_3"] = 1.0


    # Heat pump II_1 #

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_II_1"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_II_1"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_1"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_II_1"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_II_1"] = 1.0


    # Heat pump II_2 #

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_II_2"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_II_2"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_2"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_II_2"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_II_2"] = 1.0

    # Heat pump II_3 #

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_II_3"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_II_3"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_3"] = 0.95
    tech_infos["cost_var_HP_waste_heat_II_3"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_II_3"] = 1.0

    ## Waste heat - heat pumps - temperature group 3 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_III_1"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_III_1"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_1"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_III_1"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_III_1"] = 1.0

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_III_2"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_III_2"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_2"] = 0.95
    tech_infos["cost_var_HP_waste_heat_III_2"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_III_2"] = 1.0

    # Heat pump III_3 #

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_III_3"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_III_3"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_3"] = 0.95
    tech_infos["cost_var_HP_waste_heat_III_3"] = 1.5
    tech_infos["cost_fuel_HP_waste_heat_III_3"] = 1.0

    ## Seasonal waste heat heat pumps ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_seasonal"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_seasonal"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_seasonal"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_seasonal"] = 0.5
    tech_infos["cost_fuel_HP_waste_heat_seasonal"] = 1.0

    ## Waste heat absorption heat pump ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_absorption"] = 30
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_absorption"] = 0.0
    # Efficiency [-]
    tech_infos["eta_HP_waste_heat_absorption"] = 1.5
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_absorption"] = 0.99
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_absorption"] = 0.5
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HP_waste_heat_absorption"] = 25
    tech_infos["cost_fuel_HP_waste_heat_absorption"] = 1.0

    ## Thermal energy storage ##
    # Thermal energy storage size [MWh]
    tech_infos["TES_size"] = 50
    # Minimum percentage of state of charge of thermal energy storage [-]
    tech_infos["SOC_min"] = 0.15
    # Thermal energy storage state of charge at the start/end of the year [-]
    tech_infos["TES_start_end"] = 0.5
    # Thermal storage charge/discharge capacity [MW]
    tech_infos["TES_charge_discharge_time"] = 5
    tech_infos["TES_loss"] = 0.1 / (24 * 7)

    ## Seasonal thermal energy storage ##

    # Thermal energy storage size [MWh]
    tech_infos["TES_size_seasonal"] = 0
    # Minimum percentage of state of charge of thermal energy storage [-]
    tech_infos["SOC_min_seasonal"] = 0.0
    # Thermal energy storage state of charge at the start/end of the year [-]
    tech_infos["TES_start_end_seasonal"] = 0.0
    # Thermal storage charge/discharge capacity [MW]
    tech_infos["TES_charge_discharge_time_seasonal"] = 2000
    tech_infos["TES_loss_seasonal"] = 0.01 / (24 * 7)

    # Setting stuff to 0!!!
    tech_infos["P_max_HP_waste_heat_absorption"] = 0.0
    tech_infos["P_max_HP_absorption"] = 0.0
    tech_infos["P_max_HOB"] = 0.0
    tech_infos["TES_size"] = 0.0

    return tech_infos


def create_base_tech_cooling():
    ####### Technology input data ########

    ## Heat only boiler ##
    tech_infos = {}

    # Installed capacity [MW]
    tech_infos["P_max_HOB"] = 2
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HOB"] = 0.2
    # Efficiency [-]
    tech_infos["eta_HOB"] = 0.8
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HOB"] = 0.5
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB"] = 5.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB"] = 10

    ## Heat only boiler 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HOB_2"] = 2
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HOB_2"] = 0
    # Efficiency [-]
    tech_infos["eta_HOB_2"] = 0.8
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HOB_2"] = 0.5
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB_2"] = 5.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB_2"] = 12.5

    ## Heat only boiler 3 ##

    # Installed capacity [MW]
    tech_infos["P_max_HOB_3"] = 2
    # Technical minimum [MW]
    tech_infos["Tecnical_minimum_HOB_3"] = 0.2
    # Efficiency [-]
    tech_infos["eta_HOB_3"] = 0.8
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HOB_3"] = 0.6
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HOB_3"] = 3.4
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_HOB_3"] = 10

    ## Heat pump ##
    # Installed capacity [MW]
    tech_infos["P_max_HP"] = 2
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP"] = 0.2
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP"] = 0.9
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP"] = 0.5

    ## Heat pump 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_2"] = 2
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_2"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_2"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_2"] = 0.5

    ## Heat pump 3 ##
    # Installed capacity [MW]
    tech_infos["P_max_HP_3"] = 2
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_3"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_3"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_3"] = 0.5
    tech_infos["cost_fuel_HP_3"] = 1.0

    ## Cogeneration ##

    # Installed capacity [MW]
    tech_infos["P_max_CHP"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_CHP"] = 0.0
    # Efficiency [-]
    tech_infos["eta_CHP_th"] = 0.65
    # Power-to-heat ratio [-]
    tech_infos["cb_CHP"] = 0.3
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_CHP"] = 0.2
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_CHP"] = 3.9
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_CHP"] = 20
    tech_infos["CHP_electricity_price"] = 1.0

    ## Cogeneration 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_CHP_2"] = 0
    # Technical minimum [MW]
    tech_infos["Technical_minimum_CHP_2"] = 0.4
    # Efficiency [-]
    tech_infos["eta_CHP_th_2"] = 0.65
    # Power-to-heat ratio [-]
    tech_infos["cb_CHP_2"] = 0.3
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_CHP_2"] = 0.2
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_CHP_2"] = 3.9
    # Fuel cost [EUR/MWh]
    tech_infos["cost_fuel_CHP_2"] = 15
    tech_infos["CHP_electricity_price_2"] = 1.0

    ## Absorption Heat pump ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_abs"] = 9
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_abs"] = 0.1
    # Efficiency [-]
    tech_infos["eta_HP_abs"] = 0.9
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_abs"] = 1
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_abs"] = 0.1

    ## Waste heat - heat exchangers ##

    # Installed capacity [MW]
    tech_infos["P_HEX_capacity"] = 3
    # Technical minimum [MW]
    tech_infos["P_min_HEX"] = 0
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HEX"] = 0.25

    ## Waste cooling - heat exchangers ##

    # Installed capacity [MW]
    tech_infos["P_HEX_capacity_cool"] = 2
    # Technical minimum [MW]
    tech_infos["P_min_HEX_cool"] = 0
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HEX_cool"] = 0.25

    ## Waste heat - heat pumps - temperature group 1 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_1"] = 1
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_1"] = 0.0
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_1"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_1"] = 0.7

    ## Waste heat - heat pumps - temperature group 2 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_2"] = 1
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_2"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_2"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_2"] = 1.5

    ## Waste heat - heat pumps - temperature group 3 ##

    # Installed capacity [MW]
    tech_infos["P_max_HP_waste_heat_3"] = 1
    # Technical minimum [MW]
    tech_infos["Technical_minimum_HP_waste_heat_3"] = 0.1
    # Ramp-up-down speed [MW/h]
    tech_infos["Percentage_ramp_up_down_HP_waste_heat_3"] = 0.95
    # Variable cost [EUR/MWh]
    tech_infos["cost_var_HP_waste_heat_3"] = 1.5

    ## Thermal energy storage ##

    # Thermal energy storage size [MWh]
    tech_infos["TES_size"] = 1
    # Minimum percentage of state of charge of thermal energy storage [-]
    tech_infos["SOC_min"] = 0.0
    # Thermal energy storage state of charge at the start/end of the year [-]
    tech_infos["TES_start_end"] = 0.0
    # Thermal storage charge/discharge capacity [MW]
    tech_infos["TES_charge_discharge_time"] = 5
    tech_infos["TES_loss"] = 0.1 / (24 * 7)

    # Setting stuff to 0!!!
    tech_infos["TES_size"] = 0.0
    tech_infos["P_max_HP_waste_heat_3"] = 0.0
    tech_infos["P_max_HP_waste_heat_2"] = 0.0
    tech_infos["P_max_HP_waste_heat_1"] = 0.0
    tech_infos["P_HEX_capacity_cool"] = 0.0
    tech_infos["P_HEX_capacity"] = 0.0
    tech_infos["P_max_HP_abs"] = 0.0
    tech_infos["P_max_CHP_2"] = 0.0
    tech_infos["P_max_CHP"] = 0.0
    tech_infos["P_max_HP_3"] = 0.0
    tech_infos["P_max_HP_2"] = 0.0
    tech_infos["P_max_HP"] = 0.0
    tech_infos["P_max_HOB_3"] = 0.0
    tech_infos["P_max_HOB_2"] = 0.0
    tech_infos["P_max_HOB"] = 0.0

    return tech_infos
