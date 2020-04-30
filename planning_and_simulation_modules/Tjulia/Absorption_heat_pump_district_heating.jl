module Absorption_heat_pump_district_heating

    using JuMP
    using Cbc

    using CSV
    using DelimitedFiles
    csv_sep = ','

    function district_solver(input_folder, output_folder, tech_infos, network_id, print_function = print)
#         example_file = readdlm(string(input_folder, "\\example_file.csv"), csv_sep)
#         write_results_example(output_folder, network_id, example_file)
# 	end
        m = Model(with_optimizer(Cbc.Optimizer, logLevel=1, ratioGap = 1e+1))

        ####### Load distributions #########
        DEM=readdlm(string(input_folder, "\\DEM_time.csv"), csv_sep)

        ST_specific=readdlm(string(input_folder, "\\ST_specific_time.csv"), csv_sep)

        ST_specific_2=readdlm(string(input_folder, "\\ST_specific_time_2.csv"), csv_sep)

        ST_specific_seasonal=readdlm(string(input_folder, "\\ST_specific_time_seasonal.csv"), csv_sep)


        #28/01/2020:  from tech_infos
        #Electricity_price=readdlm(string(input_folder, "\\Electricity_price_time.csv"), csv_sep)

        Heat_exchanger_specific=readdlm(string(input_folder, "\\Heat_exchanger_specific_time.csv"), csv_sep)

        eta_HP = readdlm(string(input_folder, "\\eta_HP_1.csv"), csv_sep)
        eta_HP_2 = readdlm(string(input_folder, "\\eta_HP_2.csv"), csv_sep)
        eta_HP_3 = readdlm(string(input_folder, "\\eta_HP_3.csv"), csv_sep)

        eta_HP_waste_heat_I_1 = readdlm(string(input_folder, "\\eta_HP_I_1.csv"), csv_sep)
        eta_HP_waste_heat_I_2 = readdlm(string(input_folder, "\\eta_HP_I_1.csv"), csv_sep)
        eta_HP_waste_heat_I_3 = readdlm(string(input_folder, "\\eta_HP_I_1.csv"), csv_sep)

        eta_HP_waste_heat_II_1=readdlm(string(input_folder, "\\eta_HP_II_1.csv"), csv_sep)
        eta_HP_waste_heat_II_2=readdlm(string(input_folder, "\\eta_HP_II_2.csv"), csv_sep)
        eta_HP_waste_heat_II_3=readdlm(string(input_folder, "\\eta_HP_II_3.csv"), csv_sep)

        eta_HP_waste_heat_III_1=readdlm(string(input_folder, "\\eta_HP_III_1.csv"), csv_sep)
        eta_HP_waste_heat_III_2=readdlm(string(input_folder, "\\eta_HP_III_2.csv"), csv_sep)
        eta_HP_waste_heat_III_3=readdlm(string(input_folder, "\\eta_HP_III_3.csv"), csv_sep)


        eta_HP_waste_heat_seasonal=readdlm(string(input_folder, "\\COP_heat_pump_temperature_group_seasonal.csv"), csv_sep)
        #eta_HP_waste_heat_seasonal=eta_HP_waste_heat_seasonal[1:4380]

        Available_waste_heat_heat_pump_I_1=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_1.csv"), csv_sep)
        Available_waste_heat_heat_pump_I_2=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_2.csv"), csv_sep)
        Available_waste_heat_heat_pump_I_3=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_3.csv"), csv_sep)

        Available_waste_heat_heat_pump_II_1=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_II_1.csv"), csv_sep)
        Available_waste_heat_heat_pump_II_2=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_II_2.csv"), csv_sep)
        Available_waste_heat_heat_pump_II_3=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_II_3.csv"), csv_sep)

        Available_waste_heat_heat_pump_III_1=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_III_1.csv"), csv_sep)
        Available_waste_heat_heat_pump_III_2=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_III_2.csv"), csv_sep)
        Available_waste_heat_heat_pump_III_3=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_III_3.csv"), csv_sep)

        Available_waste_heat_heat_pump_seasonal=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_seasonal.csv"), csv_sep)
        #Available_waste_heat_heat_pump_seasonal=Available_waste_heat_heat_pump_seasonal[1:4380]

        Available_waste_heat_heat_pump_absorption=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_absorption.csv"), csv_sep)
        #Available_waste_heat_heat_pump_absorption=Available_waste_heat_heat_pump_absorption[1:4380]


        ORC_waste_heat_availability=readdlm(string(input_folder, "\\ORC_waste_heat_availability.csv"), csv_sep)

        ####### Technology input data ########

        ## Heat only boiler ##

        # Installed capacity [MW]
        P_max_HOB = tech_infos["P_max_HOB"] # 90
        # Technical minimum [MW]
        Tecnical_minimum_HOB= tech_infos["Tecnical_minimum_HOB"] # 0.0
        P_min_HOB = Tecnical_minimum_HOB*P_max_HOB
        # Efficiency [-]
        eta_HOB = tech_infos["eta_HOB"] # 0.8
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB= tech_infos["Percentage_ramp_up_down_HOB"] # 0.99
        ramp_up_down_HOB = P_max_HOB*Percentage_ramp_up_down_HOB
        # Variable cost [EUR/MWh]
        cost_var_HOB = tech_infos["cost_var_HOB"] # 5.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB = tech_infos["cost_fuel_HOB"] # 25

        ## Heat only boiler 2 ##

        # Installed capacity [MW]
        P_max_HOB_2 = tech_infos["P_max_HOB_2"] # 0
        # Technical minimum [MW]
        Tecnical_minimum_HOB_2= tech_infos["Tecnical_minimum_HOB_2"] # 0.0
        P_min_HOB_2 = Tecnical_minimum_HOB_2*P_max_HOB_2
        # Efficiency [-]
        eta_HOB_2 = tech_infos["eta_HOB_2"] # 0.8
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB_2= tech_infos["Percentage_ramp_up_down_HOB_2"] # 0.8
        ramp_up_down_HOB_2 = P_max_HOB_2*Percentage_ramp_up_down_HOB_2
        # Variable cost [EUR/MWh]
        cost_var_HOB_2 = tech_infos["cost_var_HOB_2"] # 5.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB_2 = tech_infos["cost_fuel_HOB_2"] # 12.5

        ## Heat only boiler 3 ##

        # Installed capacity [MW]
        P_max_HOB_3 = tech_infos["P_max_HOB_3"] # 0
        # Technical minimum [MW]
        Tecnical_minimum_HOB_3= tech_infos["Tecnical_minimum_HOB_3"] # 0.8
        P_min_HOB_3 = Tecnical_minimum_HOB_3*P_max_HOB_3
        # Efficiency [-]
        eta_HOB_3 = tech_infos["eta_HOB_3"] # 0.8
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB_3= tech_infos["Percentage_ramp_up_down_HOB_3"] # 0.8
        ramp_up_down_HOB_3 = P_max_HOB_3*Percentage_ramp_up_down_HOB_3
        # Variable cost [EUR/MWh]
        cost_var_HOB_3 = tech_infos["cost_var_HOB_3"] # 3.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB_3 = tech_infos["cost_fuel_HOB_3"] # 10

        ## Electrical heater ##

        # Installed capacity [MW]
        P_max_EH = tech_infos["P_max_EH"] # 0
        # Technical minimum [MW]
        Technical_minimum_EH= tech_infos["Technical_minimum_EH"] # 0.1
        P_min_EH = P_max_EH*Technical_minimum_EH
        # Efficiency [-]
        eta_EH = tech_infos["eta_EH"] # 0.98
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_EH= tech_infos["Percentage_ramp_up_down_EH"] # 0.95
        ramp_up_down_EH = Percentage_ramp_up_down_EH*P_max_EH
        # Variable cost [EUR/MWh]
        cost_var_EH = tech_infos["cost_var_EH"] # 0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_EH = tech_infos["cost_fuel_EH"] # Electricity_price

        ## Electrical heater 2 ##

        # Installed capacity [MW]
        P_max_EH_2 = tech_infos["P_max_EH_2"] # 0
        # Technical minimum [MW]
        Technical_minimum_EH_2= tech_infos["Technical_minimum_EH_2"] # 0.15
        P_min_EH_2 = P_max_EH_2*Technical_minimum_EH_2
        # Efficiency [-]
        eta_EH_2 = tech_infos["eta_EH_2"] # 0.98
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_EH_2=tech_infos["Percentage_ramp_up_down_EH_2"] # 0.9
        ramp_up_down_EH_2 = Percentage_ramp_up_down_EH_2*P_max_EH_2
        # Variable cost [EUR/MWh]
        cost_var_EH_2 = tech_infos["cost_var_EH_2"] # 0.7
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_EH_2 = tech_infos["cost_fuel_EH_2"] # Electricity_price

        ## Electrical heater 3 ##

        # Installed capacity [MW]
        P_max_EH_3 = tech_infos["P_max_EH_3"] # 0
        # Technical minimum [MW]
        Technical_minimum_EH_3= tech_infos["Technical_minimum_EH_3"] # 0.1
        P_min_EH_3 = P_max_EH_3*Technical_minimum_EH_3
        # Efficiency [-]
        eta_EH_3 = tech_infos["eta_EH_3"] # 0.98
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_EH_3= tech_infos["Percentage_ramp_up_down_EH_3"] # 0.99
        ramp_up_down_EH_3 = Percentage_ramp_up_down_EH_3*P_max_EH_3
        # Variable cost [EUR/MWh]
        cost_var_EH_3 = tech_infos["cost_var_EH_3"] # 0.8
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_EH_3 = tech_infos["cost_fuel_EH_3"] # Electricity_price

        ## Heat pump ##
        # Installed capacity [MW]
        P_max_HP = tech_infos["P_max_HP"] # 0
        # Technical minimum [MW]
        Technical_minimum_HP= tech_infos["Technical_minimum_HP"] # 0.1
        P_min_HP = Technical_minimum_HP*P_max_HP
        # Efficiency [-]
        eta_HP = eta_HP
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP= tech_infos["Percentage_ramp_up_down_HP"] # 0.95
        ramp_up_down_HP = Percentage_ramp_up_down_HP*P_max_HP
        # Variable cost [EUR/MWh]
        cost_var_HP = tech_infos["cost_var_HP"] # 0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP = tech_infos["cost_fuel_HP"] # Electricity_price

        ## Heat pump 2 ##

        # Installed capacity [MW]
        P_max_HP_2 = tech_infos["P_max_HP_2"] # 0
        # Technical minimum [MW]
        Technical_minimum_HP_2= tech_infos["Technical_minimum_HP_2"] # 0.1
        P_min_HP_2 = Technical_minimum_HP_2*P_max_HP_2
        # Efficiency [-]
        eta_HP_2 = eta_HP_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_2= tech_infos["Percentage_ramp_up_down_HP_2"] # 0.95
        ramp_up_down_HP_2 = Percentage_ramp_up_down_HP_2*P_max_HP_2
        # Variable cost [EUR/MWh]
        cost_var_HP_2 = tech_infos["cost_var_HP_2"] # 0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_2 = tech_infos["cost_fuel_HP_2"] # Electricity_price

        ## Heat pump 3 ##
        # Installed capacity [MW]
        P_max_HP_3 = tech_infos["P_max_HP_3"] # 0
        # Technical minimum [MW]
        Technical_minimum_HP_3= tech_infos["Technical_minimum_HP_3"] # 0.1
        P_min_HP_3 = Technical_minimum_HP_3*P_max_HP_3
        # Efficiency [-]
        eta_HP_3 = eta_HP_3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_3= tech_infos["Percentage_ramp_up_down_HP_3"] # 0.95
        ramp_up_down_HP_3 = Percentage_ramp_up_down_HP_3*P_max_HP_3
        # Variable cost [EUR/MWh]
        cost_var_HP_3 = tech_infos["cost_var_HP_3"] # 0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_3 = tech_infos["cost_fuel_HP_3"] # Electricity_price

        ## Absorption heat pump ##

        # Installed capacity [MW]
        P_max_HP_absorption = tech_infos["P_max_HP_absorption"] # 30
        # Technical minimum [MW]
        Technical_minimum_HP_absorption= tech_infos["Technical_minimum_HP_absorption"] # 0.0
        P_min_HP_absorption = Technical_minimum_HP_absorption*P_max_HP_absorption
        # Efficiency [-]
        eta_HP_absorption = tech_infos["eta_HP_absorption"] # 1.4
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_absorption=tech_infos["Percentage_ramp_up_down_HP_absorption"] # 0.95
        ramp_up_down_HP_absorption = Percentage_ramp_up_down_HP_absorption*P_max_HP_absorption
        # Variable cost [EUR/MWh]
        cost_var_HP_absorption = tech_infos["cost_var_HP_absorption"] # 0.5
        # Fuel cost [EUR/MWh]
        cost_fuel_HP_absorption = tech_infos["cost_fuel_HP_absorption"] # 25

        ## Cogeneration ##

        # Installed capacity [MW]
        P_max_CHP = tech_infos["P_max_CHP"] # 0
        # Technical minimum [MW]
        Technical_minimum_CHP= tech_infos["Technical_minimum_CHP"] # 0.4
        P_min_CHP = Technical_minimum_CHP*P_max_CHP
        # Efficiency [-]
        eta_CHP_th = tech_infos["eta_CHP_th"] # 0.65
        # Power-to-heat ratio [-]
        cb_CHP = tech_infos["cb_CHP"] # 0.3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_CHP= tech_infos["Percentage_ramp_up_down_CHP"] # 0.2
        ramp_up_down_CHP = Percentage_ramp_up_down_CHP*P_max_CHP
        # Variable cost [EUR/MWh]
        cost_var_CHP = tech_infos["cost_var_CHP"] # 3.9
        # Fuel cost [EUR/MWh]
        cost_fuel_CHP = tech_infos["cost_fuel_CHP"] # 20
        # Price paid to CHP for electrcity production
        CHP_electricity_price = tech_infos["CHP_electricity_price"] # Electricity_price

        ## Cogeneration 2 ##

        # Installed capacity [MW]
        P_max_CHP_2 = tech_infos["P_max_CHP_2"] # 0
        # Technical minimum [MW]
        Technical_minimum_CHP_2= tech_infos["Technical_minimum_CHP_2"] # 0.4
        P_min_CHP_2 = Technical_minimum_CHP_2*P_max_CHP_2
        # Efficiency [-]
        eta_CHP_th_2 = tech_infos["eta_CHP_th_2"] # 0.65
        # Power-to-heat ratio [-]
        cb_CHP_2 = tech_infos["cb_CHP_2"] # 0.3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_CHP_2= tech_infos["Percentage_ramp_up_down_CHP_2"] # 0.2
        ramp_up_down_CHP_2 = Percentage_ramp_up_down_CHP_2*P_max_CHP_2
        # Variable cost [EUR/MWh]
        cost_var_CHP_2 = tech_infos["cost_var_CHP_2"] # 3.9
        # Fuel cost [EUR/MWh]
        cost_fuel_CHP_2 = tech_infos["cost_fuel_CHP_2"] # 15
        # Price paid to CHP for electrcity production
        CHP_electricity_price_2 = tech_infos["CHP_electricity_price_2"] # Electricity_price


        ## ORC Cogeneration ##

        # THERMAL installed capacity [MW]
        P_max_CHP_ORC =tech_infos["P_max_CHP_ORC"] #0
        # Technical minimum [MW]
        Technical_minimum_CHP_ORC=tech_infos["Technical_minimum_CHP_ORC"] #0
        P_min_CHP_ORC = Technical_minimum_CHP_ORC*P_max_CHP_ORC
        # Electrical efficiency [-]
        eta_CHP_el = tech_infos["eta_CHP_el"]
        # Power-to-heat ratio [-]
        cb_CHP_ORC =tech_infos["cb_CHP_ORC"]
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_CHP_ORC=tech_infos["Percentage_ramp_up_down_CHP_ORC"]
        ramp_up_down_CHP_ORC = Percentage_ramp_up_down_CHP_ORC*P_max_CHP_ORC
        # Variable cost [EUR/MWh]
        cost_var_CHP_ORC = tech_infos["cost_var_CHP_ORC"]
        # Price paid to CHP for electrcity production
        CHP_ORC_electricity_price = tech_infos["CHP_ORC_electricity_price"] # Electricity_price
        # ORC Thermal availability
        ORC_thermal_availability=(ORC_waste_heat_availability*eta_CHP_el)/cb_CHP_ORC


        ## Solar thermal ##

        # Installed solar thermal collector area [m2]
        A_ST= tech_infos["A_ST"] # 0
        # Variable cost [EUR/MWh]
        cost_var_ST = tech_infos["cost_var_ST"] # 0.5
        # Solar thermal collector prodution [MW]
        P_max_ST=A_ST*ST_specific/1000000

        ## Solar thermal 2 ##

        # Installed solar thermal collector area [m2]
        A_ST_2= tech_infos["A_ST_2"] # 0
        # Variable cost [EUR/MWh]
        cost_var_ST_2 = tech_infos["cost_var_ST_2"] # 0.5
        # Solar thermal collector prodution [MW]
        P_max_ST_2=A_ST_2*ST_specific_2/1000000

        ## Seasonal solar thermal ##
        # Installed solar thermal collector area [m2]
        A_ST_seasonal= tech_infos["A_ST_seasonal"] # 0
        # Variable cost [EUR/MWh]
        cost_var_ST_seasonal = tech_infos["cost_var_ST_seasonal"] # 0.5
        # Solar thermal collector prodution [MW]
        P_max_ST_seasonal=A_ST_seasonal*ST_specific_seasonal/1000000

        ## Waste heat - heat exchangers ##

        # Installed capacity [MW]
        P_HEX_capacity = tech_infos["P_HEX_capacity"] # 0
        P_max_HEX=P_HEX_capacity*Heat_exchanger_specific
        # Technical minimum [MW]
        P_min_HEX= tech_infos["P_min_HEX"] # 0
        # Variable cost [EUR/MWh]
        cost_var_HEX = tech_infos["cost_var_HEX"] # 0.25

        ## Waste heat - heat pumps 1 ##

        # Installed capacity [MW]
        P_max_HP_waste_heat_I_1 = tech_infos["P_max_HP_waste_heat_I_1"] # 0
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_I_1 = tech_infos["Technical_minimum_HP_waste_heat_I_1"] # 0.0
        P_min_HP_waste_heat_I_1 = Technical_minimum_HP_waste_heat_I_1*P_max_HP_waste_heat_I_1
        # Efficiency [-]
        eta_HP_waste_heat_I_1 = eta_HP_waste_heat_I_1
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_I_1= tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_1"] # 0.95
        ramp_up_down_HP_waste_heat_I_1 = Percentage_ramp_up_down_HP_waste_heat_I_1*P_max_HP_waste_heat_I_1
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_I_1 = tech_infos["cost_var_HP_waste_heat_I_1"] # 0.7
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_I_1 = tech_infos["cost_fuel_HP_waste_heat_I_1"] # Electricity_price

        ## Waste heat - heat pumps 2 ##

        # Installed capacity [MW]
        P_max_HP_waste_heat_I_2 = tech_infos["P_max_HP_waste_heat_I_2"] # 0
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_I_2 = tech_infos["Technical_minimum_HP_waste_heat_I_2"] # 0.0
        P_min_HP_waste_heat_I_2 = Technical_minimum_HP_waste_heat_I_2*P_max_HP_waste_heat_I_2
        # Efficiency [-]
        eta_HP_waste_heat_2 = eta_HP_waste_heat_I_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_I_2= tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_2"] # 0.95
        ramp_up_down_HP_waste_heat_I_2 = Percentage_ramp_up_down_HP_waste_heat_I_2*P_max_HP_waste_heat_I_2
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_I_2 = tech_infos["cost_var_HP_waste_heat_I_2"] # 1.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_I_2 = tech_infos["cost_fuel_HP_waste_heat_I_2"] # Electricity_price

        ## Waste heat - heat pumps 3##

        # Installed capacity [MW]
        P_max_HP_waste_heat_I_3 = tech_infos["P_max_HP_waste_heat_I_3"] # 0
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_I_3 = tech_infos["Technical_minimum_HP_waste_heat_I_3"] # 0.0
        P_min_HP_waste_heat_I_3 = Technical_minimum_HP_waste_heat_I_3*P_max_HP_waste_heat_I_3
        # Efficiency [-]
        eta_HP_waste_heat_I_3 = eta_HP_waste_heat_I_3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_I_3= tech_infos["Percentage_ramp_up_down_HP_waste_heat_I_3"] # 0.95
        ramp_up_down_HP_waste_heat_I_3 = Percentage_ramp_up_down_HP_waste_heat_I_3*P_max_HP_waste_heat_I_3
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_I_3 = tech_infos["cost_var_HP_waste_heat_I_3"] # 1.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_I_3 = tech_infos["cost_fuel_HP_waste_heat_I_3"] # Electricity_price

        ## Waste heat - heat pumps - temperature group II ##

        # Heat pump II_1 #

        # Installed capacity [MW]
        P_max_HP_waste_heat_II_1 = tech_infos["P_max_HP_waste_heat_II_1"]
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_II_1 =tech_infos["Technical_minimum_HP_waste_heat_II_1"]
        P_min_HP_waste_heat_II_1 = Technical_minimum_HP_waste_heat_II_1*P_max_HP_waste_heat_II_1
        # Efficiency [-]
        eta_HP_waste_heat_II_1 = eta_HP_waste_heat_II_1
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_II_1=tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_1"]
        ramp_up_down_HP_waste_heat_II_1 = Percentage_ramp_up_down_HP_waste_heat_II_1*P_max_HP_waste_heat_II_1
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_II_1 =tech_infos["cost_var_HP_waste_heat_II_1"]
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_II_1 = tech_infos["cost_fuel_HP_waste_heat_II_1"] # Electricity_price

        # Heat pump II_2 #

        # Installed capacity [MW]
        P_max_HP_waste_heat_II_2 =tech_infos["P_max_HP_waste_heat_II_2"]
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_II_2 =tech_infos["Technical_minimum_HP_waste_heat_II_2"]
        P_min_HP_waste_heat_II_2 = Technical_minimum_HP_waste_heat_II_2*P_max_HP_waste_heat_II_2
        # Efficiency [-]
        eta_HP_waste_heat_II_2 = eta_HP_waste_heat_II_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_II_2=tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_2"]
        ramp_up_down_HP_waste_heat_II_2 = Percentage_ramp_up_down_HP_waste_heat_II_2*P_max_HP_waste_heat_II_2
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_II_2 =tech_infos["cost_var_HP_waste_heat_II_2"]
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_II_2 = tech_infos["cost_fuel_HP_waste_heat_II_2"] # Electricity_price

        # Heat pump II_3 #

        # Installed capacity [MW]
        P_max_HP_waste_heat_II_3 = tech_infos["P_max_HP_waste_heat_II_3"]
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_II_3 =tech_infos["Technical_minimum_HP_waste_heat_II_3"]
        P_min_HP_waste_heat_II_3 = Technical_minimum_HP_waste_heat_II_3*P_max_HP_waste_heat_II_3
        # Efficiency [-]
        eta_HP_waste_heat_II_3 = eta_HP_waste_heat_II_3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_II_3=tech_infos["Percentage_ramp_up_down_HP_waste_heat_II_3"]
        ramp_up_down_HP_waste_heat_II_3 = Percentage_ramp_up_down_HP_waste_heat_II_3*P_max_HP_waste_heat_II_3
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_II_3 = tech_infos["cost_var_HP_waste_heat_II_3"]
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_II_3 = tech_infos["cost_fuel_HP_waste_heat_II_3"] # Electricity_price


        ## Waste heat - heat pumps - temperature group III ##

        # Heat pump III_1 #

        # Installed capacity [MW]
        P_max_HP_waste_heat_III_1 = tech_infos["P_max_HP_waste_heat_III_1"]
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_III_1 =tech_infos["Technical_minimum_HP_waste_heat_III_1"]
        P_min_HP_waste_heat_III_1 = Technical_minimum_HP_waste_heat_III_1*P_max_HP_waste_heat_III_1
        # Efficiency [-]
        eta_HP_waste_heat_III_1 = eta_HP_waste_heat_III_1
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_III_1=tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_1"]
        ramp_up_down_HP_waste_heat_III_1 = Percentage_ramp_up_down_HP_waste_heat_III_1*P_max_HP_waste_heat_III_1
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_III_1 = tech_infos["cost_var_HP_waste_heat_III_1"]
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_III_1 = tech_infos["cost_fuel_HP_waste_heat_III_1"] # Electricity_price

        # Heat pump III_2 #

        # Installed capacity [MW]
        P_max_HP_waste_heat_III_2 = tech_infos["P_max_HP_waste_heat_III_2"]
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_III_2 =tech_infos["Technical_minimum_HP_waste_heat_III_2"]
        P_min_HP_waste_heat_III_2 = Technical_minimum_HP_waste_heat_III_2*P_max_HP_waste_heat_III_2
        # Efficiency [-]
        eta_HP_waste_heat_III_2 = eta_HP_waste_heat_III_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_III_2=tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_2"]
        ramp_up_down_HP_waste_heat_III_2 = Percentage_ramp_up_down_HP_waste_heat_III_2*P_max_HP_waste_heat_III_2
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_III_2 = tech_infos["cost_var_HP_waste_heat_III_2"]
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_III_2 = tech_infos["cost_fuel_HP_waste_heat_III_2"] # Electricity_price

        # Heat pump III_3 #

        # Installed capacity [MW]
        P_max_HP_waste_heat_III_3 = tech_infos["P_max_HP_waste_heat_III_3"]
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_III_3 =tech_infos["Technical_minimum_HP_waste_heat_III_3"]
        P_min_HP_waste_heat_III_3 = Technical_minimum_HP_waste_heat_III_3*P_max_HP_waste_heat_III_3
        # Efficiency [-]
        eta_HP_waste_heat_III_3 = eta_HP_waste_heat_III_3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_III_3=tech_infos["Percentage_ramp_up_down_HP_waste_heat_III_3"]
        ramp_up_down_HP_waste_heat_III_3 = Percentage_ramp_up_down_HP_waste_heat_III_3*P_max_HP_waste_heat_III_3
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_III_3 = tech_infos["cost_var_HP_waste_heat_III_3"]
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_III_3 = tech_infos["cost_fuel_HP_waste_heat_III_3"] # Electricity_price


        ## Seasonal waste heat heat pumps ##

        # Installed capacity [MW]
        P_max_HP_waste_heat_seasonal = tech_infos["P_max_HP_waste_heat_seasonal"] # 0
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_seasonal = tech_infos["Technical_minimum_HP_waste_heat_seasonal"] # 0.0
        P_min_HP_waste_heat_seasonal = Technical_minimum_HP_waste_heat_seasonal*P_max_HP_waste_heat_seasonal
        # Efficiency [-]
        eta_HP_waste_heat_seasonal = eta_HP_waste_heat_seasonal
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_seasonal= tech_infos["Percentage_ramp_up_down_HP_waste_heat_seasonal"] # 0.95
        ramp_up_down_HP_waste_heat_seasonal = Percentage_ramp_up_down_HP_waste_heat_seasonal*P_max_HP_waste_heat_seasonal
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_seasonal = tech_infos["cost_var_HP_waste_heat_seasonal"] # 0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_seasonal = tech_infos["cost_fuel_HP_waste_heat_seasonal"] # Electricity_price

        ## Waste heat absorption heat pump ##

        # Installed capacity [MW]
        P_max_HP_waste_heat_absorption = tech_infos["P_max_HP_waste_heat_absorption"] # 30
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_absorption = tech_infos["Technical_minimum_HP_waste_heat_absorption"] # 0.0
        P_min_HP_waste_heat_absorption = Technical_minimum_HP_waste_heat_absorption*P_max_HP_waste_heat_absorption
        # Efficiency [-]
        eta_HP_waste_heat_absorption = tech_infos["eta_HP_waste_heat_absorption"] # 1.5
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_absorption= tech_infos["Percentage_ramp_up_down_HP_waste_heat_absorption"] # 0.99
        ramp_up_down_HP_waste_heat_absorption = Percentage_ramp_up_down_HP_waste_heat_absorption*P_max_HP_waste_heat_absorption
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_absorption = tech_infos["cost_var_HP_waste_heat_absorption"] # 0.5
        # Fuel cost [EUR/MWh]
        cost_fuel_HP_waste_heat_absorption = tech_infos["cost_fuel_HP_waste_heat_absorption"] # 25

        ## Thermal energy storage ##
        # Thermal energy storage size [MWh]
        TES_size = tech_infos["TES_size"] # 50
        # Minimum percentage of state of charge of thermal energy storage [-]
        SOC_min = tech_infos["SOC_min"] # 0.15
        # Thermal energy storage state of charge at the start/end of the year [-]
        TES_start_end = tech_infos["TES_start_end"] # 0.5
        # Thermal storage charge/discharge capacity [MW]
        TES_charge_discharge_time = tech_infos["TES_charge_discharge_time"] # 5
        TES_in_out_max = TES_size/TES_charge_discharge_time
        TES_loss= tech_infos["TES_loss"] # 0.1/(24*7)

        ## Seasonal thermal energy storage ##

        # Thermal energy storage size [MWh]
        TES_size_seasonal = tech_infos["TES_size_seasonal"] # 0
        # Minimum percentage of state of charge of thermal energy storage [-]
        SOC_min_seasonal = tech_infos["SOC_min_seasonal"] # 0.0
        # Thermal energy storage state of charge at the start/end of the year [-]
        TES_start_end_seasonal = tech_infos["TES_start_end_seasonal"] # 0.0
        # Thermal storage charge/discharge capacity [MW]
        TES_charge_discharge_time_seasonal = tech_infos["TES_charge_discharge_time_seasonal"] # 2000
        TES_in_out_max_seasonal = TES_size_seasonal/TES_charge_discharge_time_seasonal
        TES_loss_seasonal= tech_infos["TES_loss_seasonal"] # 0.01/(24*7)


        ######## Constraints and variables ########

        ### Variables ###

        # Technologies' operation
        @variable(m, P_max_HOB >= HOB[1:length(DEM)] >= 0)
        @variable(m, P_max_HOB_2 >= HOB_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HOB_3 >= HOB_3[1:length(DEM)] >= 0)

        @variable(m, P_max_EH >= EH[1:length(DEM)] >= 0)
        @variable(m, P_max_EH_2 >= EH_2[1:length(DEM)] >= 0)
        @variable(m, P_max_EH_3 >= EH_3[1:length(DEM)] >= 0)

        @variable(m, P_max_HP >= HP[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_2 >= HP_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_3 >= HP_3[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_absorption >= HP_absorption[1:length(DEM)] >= 0)

        @variable(m, P_max_CHP >= CHP[1:length(DEM)] >= 0)
        @variable(m, P_max_CHP_2 >= CHP_2[1:length(DEM)] >= 0)

        @variable(m, P_max_CHP_ORC >= CHP_ORC[1:length(DEM)] >= 0)

        @variable(m, ST[1:length(DEM)] >= 0)
        @variable(m, ST_2[1:length(DEM)] >= 0)
        @variable(m, ST_seasonal[1:length(DEM)] >= 0)

        @variable(m, HEX[1:length(DEM)] >= 0)


        @variable(m, P_max_HP_waste_heat_I_1 >= HP_waste_heat_I_1[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_I_2 >= HP_waste_heat_I_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_I_3 >= HP_waste_heat_I_3[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_waste_heat_II_1 >= HP_waste_heat_II_1[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_II_2 >= HP_waste_heat_II_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_II_3 >= HP_waste_heat_II_3[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_waste_heat_III_1 >= HP_waste_heat_III_1[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_III_2 >= HP_waste_heat_III_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_III_3 >= HP_waste_heat_III_3[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_waste_heat_seasonal >= HP_waste_heat_seasonal[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_waste_heat_absorption >= HP_waste_heat_absorption[1:length(DEM)] >= 0)
        @variable(m, TES_in_out_max >=TES[1:length(DEM)]>= -TES_in_out_max)
        @variable(m, TES_size >= SOC[1:length(DEM)] >= TES_size*SOC_min)

        @variable(m, 0 >=TES_seasonal[1:length(DEM)]>= -TES_in_out_max_seasonal)
        @variable(m, TES_size_seasonal >= SOC_seasonal[1:length(DEM)] >= TES_size*SOC_min_seasonal)

        #@variable(m, maximum(DEM) >= Error[1:length(DEM)] >= 0)
        @variable(m, 0 >= Error[1:length(DEM)] >= 0)

        # Binary variables, on/off

        @variable(m, OnOffHOB[1:length(DEM)], Bin)
        @variable(m, OnOffHOB_2[1:length(DEM)], Bin)
        @variable(m, OnOffHOB_3[1:length(DEM)], Bin)

        @variable(m, OnOffEH[1:length(DEM)], Bin)
        @variable(m, OnOffEH_2[1:length(DEM)], Bin)
        @variable(m, OnOffEH_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP[1:length(DEM)], Bin)
        @variable(m, OnOffHP_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP_absorption[1:length(DEM)], Bin)

        @variable(m, OnOffCHP[1:length(DEM)], Bin)
        @variable(m, OnOffCHP_2[1:length(DEM)], Bin)

        @variable(m, OnOffCHP_ORC[1:length(DEM)], Bin)

        @variable(m, OnOffHP_waste_heat_I_1[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_I_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_I_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP_waste_heat_II_1[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_II_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_II_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP_waste_heat_III_1[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_III_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_III_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP_waste_heat_seasonal[1:length(DEM)], Bin)

        @variable(m, OnOffHP_waste_heat_absorption[1:length(DEM)], Bin)

        ### Constraints ###
        # Supply + TES = DEM
        @constraint(m, HOB+HOB_2+HOB_3+EH+EH_2+EH_3+HP+HP_2+HP_3+HP_absorption+CHP+CHP_2+CHP_ORC+ST+ST_2+HEX+HP_waste_heat_I_1+HP_waste_heat_I_2+HP_waste_heat_I_3+HP_waste_heat_II_1+HP_waste_heat_II_2+HP_waste_heat_II_3+HP_waste_heat_III_1+HP_waste_heat_III_2+HP_waste_heat_III_3+HP_waste_heat_absorption-TES-TES_seasonal + Error .== DEM)

        # Thermal storage constraints
        t=2:(length(DEM)-1)
        @constraint(m, SOC[t]-SOC[t .- 1]-TES[t]+SOC[t]*TES_loss .== 0)
        @constraint(m, SOC[length(DEM)-1]+TES[length(DEM)] == TES_size*TES_start_end)
        @constraint(m, SOC[1]-TES[1] == TES_size*TES_start_end)
        @constraint(m, SOC[length(DEM)] == TES_size*TES_start_end)

        # Seasonal thermal storage constraints
        @constraint(m, SOC_seasonal[t]-SOC_seasonal[t .- 1]-TES_seasonal[t]+SOC_seasonal[t]*TES_loss_seasonal - HP_waste_heat_seasonal[t]-ST_seasonal[t].== 0)
        @constraint(m, SOC_seasonal[length(DEM)-1]+TES_seasonal[length(DEM)]+HP_waste_heat_seasonal[length(DEM)]+ST_seasonal[length(DEM)] == TES_size_seasonal*TES_start_end_seasonal)
        @constraint(m, SOC_seasonal[1]-TES_seasonal[1]+HP_waste_heat_seasonal[1]+ST_seasonal[1] == TES_size_seasonal*TES_start_end_seasonal)
        @constraint(m, SOC_seasonal[length(DEM)] == TES_size_seasonal*TES_start_end_seasonal)

        # Solar thermal collector constraints
        #@constraint(m, ST .== P_max_ST)
        @constraint(m, ST .<= P_max_ST)
        #@constraint(m, ST_2 .== P_max_ST_2)
        @constraint(m, ST_2 .<= P_max_ST_2)

        #@constraint(m, ST_seasonal .== P_max_ST_seasonal)
        @constraint(m, ST_seasonal .<= P_max_ST_seasonal)

        # Waste heat constraints - can't utilize more than available
        @constraint(m, HEX .<=P_max_HEX)

        @constraint(m, HP_waste_heat_I_1 .<= Available_waste_heat_heat_pump_I_1)
        @constraint(m, HP_waste_heat_I_2 .<= Available_waste_heat_heat_pump_I_2)
        @constraint(m, HP_waste_heat_I_3 .<= Available_waste_heat_heat_pump_I_3)

        @constraint(m, HP_waste_heat_II_1 .<= Available_waste_heat_heat_pump_II_1)
        @constraint(m, HP_waste_heat_II_2 .<= Available_waste_heat_heat_pump_II_2)
        @constraint(m, HP_waste_heat_II_3 .<= Available_waste_heat_heat_pump_II_3)

        @constraint(m, HP_waste_heat_III_1 .<= Available_waste_heat_heat_pump_III_1)
        @constraint(m, HP_waste_heat_III_2 .<= Available_waste_heat_heat_pump_III_2)
        @constraint(m, HP_waste_heat_III_3 .<= Available_waste_heat_heat_pump_III_3)

        @constraint(m, HP_waste_heat_seasonal .<= Available_waste_heat_heat_pump_seasonal)

        @constraint(m, HP_waste_heat_absorption .<= Available_waste_heat_heat_pump_absorption)

        @constraint(m, CHP_ORC.<= ORC_thermal_availability)

        # OnOff constraints - technical minimum
        @constraint(m, OnOffHOB*P_min_HOB-HOB.<=0)
        @constraint(m, -OnOffHOB*P_max_HOB+HOB.<=0)
        @constraint(m, OnOffHOB_2*P_min_HOB_2-HOB_2.<=0)
        @constraint(m, -OnOffHOB_2*P_max_HOB_2+HOB_2.<=0)
        @constraint(m, OnOffHOB_3*P_min_HOB_3-HOB_3.<=0)
        @constraint(m, -OnOffHOB_3*P_max_HOB_3+HOB_3.<=0)

        @constraint(m, OnOffEH*P_min_EH-EH.<=0)
        @constraint(m, -OnOffEH*P_max_EH+EH.<=0)
        @constraint(m, OnOffEH_2*P_min_EH_2-EH_2.<=0)
        @constraint(m, -OnOffEH_2*P_max_EH_2+EH_2.<=0)
        @constraint(m, OnOffEH_3*P_min_EH_3-EH_3.<=0)
        @constraint(m, -OnOffEH_3*P_max_EH_3+EH_3.<=0)

        @constraint(m, OnOffHP*P_min_HP-HP.<=0)
        @constraint(m, -OnOffHP*P_max_HP+HP.<=0)
        @constraint(m, OnOffHP_2*P_min_HP_2-HP_2.<=0)
        @constraint(m, -OnOffHP_2*P_max_HP_2+HP_2.<=0)
        @constraint(m, OnOffHP_3*P_min_HP_3-HP_3.<=0)
        @constraint(m, -OnOffHP_3*P_max_HP_3+HP_3.<=0)

        @constraint(m, OnOffHP_absorption*P_min_HP_absorption-HP_absorption.<=0)
        @constraint(m, -OnOffHP_absorption*P_max_HP_absorption+HP_absorption.<=0)

        @constraint(m, OnOffCHP*P_min_CHP-CHP.<=0)
        @constraint(m, -OnOffCHP*P_max_CHP+CHP.<=0)
        @constraint(m, OnOffCHP_2*P_min_CHP_2-CHP_2.<=0)
        @constraint(m, -OnOffCHP_2*P_max_CHP_2+CHP_2.<=0)

        @constraint(m, OnOffCHP_ORC*P_min_CHP_ORC-CHP_ORC.<=0)
        @constraint(m, -OnOffCHP_ORC*P_max_CHP_ORC+CHP_ORC.<=0)


        @constraint(m, OnOffHP_waste_heat_I_1*P_min_HP_waste_heat_I_1-HP_waste_heat_I_1.<=0)
        @constraint(m, -OnOffHP_waste_heat_I_1*P_max_HP_waste_heat_I_1+HP_waste_heat_I_1.<=0)
        @constraint(m, OnOffHP_waste_heat_I_2*P_min_HP_waste_heat_I_2-HP_waste_heat_I_2.<=0)
        @constraint(m, -OnOffHP_waste_heat_I_2*P_max_HP_waste_heat_I_2+HP_waste_heat_I_2.<=0)
        @constraint(m, OnOffHP_waste_heat_I_3*P_min_HP_waste_heat_I_3-HP_waste_heat_I_3.<=0)
        @constraint(m, -OnOffHP_waste_heat_I_3*P_max_HP_waste_heat_I_3+HP_waste_heat_I_3.<=0)

        @constraint(m, OnOffHP_waste_heat_II_1*P_min_HP_waste_heat_II_1-HP_waste_heat_II_1.<=0)
        @constraint(m, -OnOffHP_waste_heat_II_1*P_max_HP_waste_heat_II_1+HP_waste_heat_II_1.<=0)
        @constraint(m, OnOffHP_waste_heat_II_2*P_min_HP_waste_heat_II_2-HP_waste_heat_II_2.<=0)
        @constraint(m, -OnOffHP_waste_heat_II_2*P_max_HP_waste_heat_II_2+HP_waste_heat_II_2.<=0)
        @constraint(m, OnOffHP_waste_heat_II_3*P_min_HP_waste_heat_II_3-HP_waste_heat_II_3.<=0)
        @constraint(m, -OnOffHP_waste_heat_II_3*P_max_HP_waste_heat_II_3+HP_waste_heat_II_3.<=0)

        @constraint(m, OnOffHP_waste_heat_III_1*P_min_HP_waste_heat_III_1-HP_waste_heat_III_1.<=0)
        @constraint(m, -OnOffHP_waste_heat_III_1*P_max_HP_waste_heat_III_1+HP_waste_heat_III_1.<=0)
        @constraint(m, OnOffHP_waste_heat_III_2*P_min_HP_waste_heat_III_2-HP_waste_heat_III_2.<=0)
        @constraint(m, -OnOffHP_waste_heat_III_2*P_max_HP_waste_heat_III_2+HP_waste_heat_III_2.<=0)
        @constraint(m, OnOffHP_waste_heat_III_3*P_min_HP_waste_heat_III_3-HP_waste_heat_III_3.<=0)
        @constraint(m, -OnOffHP_waste_heat_III_3*P_max_HP_waste_heat_III_3+HP_waste_heat_III_3.<=0)

        @constraint(m, OnOffHP_waste_heat_seasonal*P_min_HP_waste_heat_seasonal-HP_waste_heat_seasonal.<=0)
        @constraint(m, -OnOffHP_waste_heat_seasonal*P_max_HP_waste_heat_seasonal+HP_waste_heat_seasonal.<=0)

        @constraint(m, OnOffHP_waste_heat_absorption*P_min_HP_waste_heat_absorption-HP_waste_heat_absorption.<=0)
        @constraint(m, -OnOffHP_waste_heat_absorption*P_max_HP_waste_heat_absorption+HP_waste_heat_absorption.<=0)

        # Ramp-up-down constraint for each technology
        i=2:(length(DEM)-1)

        @constraint(m, HOB[i .- 1]-HOB[i].<=ramp_up_down_HOB*OnOffHOB[i]+(1 .- OnOffHOB[i])*P_min_HOB)
        @constraint(m, HOB[i]-HOB[i .- 1].<=ramp_up_down_HOB*OnOffHOB[i .- 1]+(1 .- OnOffHOB[i .- 1])*P_min_HOB)
        @constraint(m, HOB_2[i .- 1]-HOB_2[i].<=ramp_up_down_HOB_2*OnOffHOB_2[i]+(1 .- OnOffHOB_2[i])*P_min_HOB_2)
        @constraint(m, HOB_2[i]-HOB_2[i .- 1].<=ramp_up_down_HOB_2*OnOffHOB_2[i .- 1]+(1 .- OnOffHOB_2[i .- 1])*P_min_HOB_2)
        @constraint(m, HOB_3[i .- 1]-HOB_3[i].<=ramp_up_down_HOB_3*OnOffHOB_3[i]+(1 .- OnOffHOB_3[i])*P_min_HOB_3)
        @constraint(m, HOB_3[i]-HOB_3[i .- 1].<=ramp_up_down_HOB_3*OnOffHOB_3[i .- 1]+(1 .- OnOffHOB_3[i .- 1])*P_min_HOB_3)

        @constraint(m, EH[i .- 1]-EH[i].<=ramp_up_down_EH*OnOffEH[i]+(1 .- OnOffEH[i])*P_min_EH)
        @constraint(m, EH[i]-EH[i .- 1].<=ramp_up_down_EH*OnOffEH[i .- 1]+(1 .- OnOffEH[i .- 1])*P_min_EH)
        @constraint(m, EH_2[i .- 1]-EH_2[i].<=ramp_up_down_EH_2*OnOffEH_2[i]+(1 .- OnOffEH_2[i])*P_min_EH_2)
        @constraint(m, EH_2[i]-EH_2[i .- 1].<=ramp_up_down_EH_2*OnOffEH_2[i .- 1]+(1 .- OnOffEH_2[i .- 1])*P_min_EH_2)
        @constraint(m, EH_3[i .- 1]-EH_3[i].<=ramp_up_down_EH_3*OnOffEH_3[i]+(1 .- OnOffEH_3[i])*P_min_EH_3)
        @constraint(m, EH_3[i]-EH_3[i .- 1].<=ramp_up_down_EH_3*OnOffEH_3[i .- 1]+(1 .- OnOffEH_3[i .- 1])*P_min_EH_3)
        @constraint(m, HP[i .- 1]-HP[i].<=ramp_up_down_HP*OnOffHP[i]+(1 .- OnOffHP[i])*P_min_HP)
        @constraint(m, HP[i]-HP[i .- 1].<=ramp_up_down_HP*OnOffHP[i .- 1]+(1 .- OnOffHP[i .- 1])*P_min_HP)
        @constraint(m, HP_2[i .- 1]-HP_2[i].<=ramp_up_down_HP_2*OnOffHP_2[i]+(1 .- OnOffHP_2[i])*P_min_HP_2)
        @constraint(m, HP_2[i]-HP_2[i .- 1].<=ramp_up_down_HP_2*OnOffHP_2[i .- 1]+(1 .- OnOffHP_2[i .- 1])*P_min_HP_2)
        @constraint(m, HP_3[i .- 1]-HP_3[i].<=ramp_up_down_HP_3*OnOffHP_3[i]+(1 .- OnOffHP_3[i])*P_min_HP_3)
        @constraint(m, HP_3[i]-HP_3[i .- 1].<=ramp_up_down_HP_3*OnOffHP_3[i .- 1]+(1 .- OnOffHP_3[i .- 1])*P_min_HP_3)

        @constraint(m, HP_absorption[i .- 1]-HP_absorption[i].<=ramp_up_down_HP_absorption*OnOffHP_absorption[i]+(1 .- OnOffHP_absorption[i])*P_min_HP_absorption)
        @constraint(m, HP_absorption[i]-HP_absorption[i .- 1].<=ramp_up_down_HP_absorption*OnOffHP_absorption[i .- 1]+(1 .- OnOffHP_absorption[i .- 1])*P_min_HP_absorption)

        @constraint(m, CHP_ORC[i .- 1]-CHP_ORC[i].<=ramp_up_down_CHP_ORC*OnOffCHP_ORC[i]+(1 .- OnOffCHP_ORC[i])*P_min_CHP_ORC)
        @constraint(m, CHP_ORC[i]-CHP_ORC[i .- 1].<=ramp_up_down_CHP_ORC*OnOffCHP_ORC[i .- 1]+(1 .- OnOffCHP_ORC[i .- 1])*P_min_CHP_ORC)

        @constraint(m, CHP[i .- 1]-CHP[i].<=ramp_up_down_CHP*OnOffCHP[i]+(1 .- OnOffCHP[i])*P_min_CHP)
        @constraint(m, CHP[i]-CHP[i .- 1].<=ramp_up_down_CHP*OnOffCHP[i .- 1]+(1 .- OnOffCHP[i .- 1])*P_min_CHP)
        @constraint(m, CHP_2[i .- 1]-CHP_2[i].<=ramp_up_down_CHP_2*OnOffCHP_2[i]+(1 .- OnOffCHP_2[i])*P_min_CHP_2)
        @constraint(m, CHP_2[i]-CHP_2[i .- 1].<=ramp_up_down_CHP_2*OnOffCHP_2[i .- 1]+(1 .- OnOffCHP_2[i .- 1])*P_min_CHP_2)


        @constraint(m, HP_waste_heat_I_1[i .- 1]-HP_waste_heat_I_1[i].<=ramp_up_down_HP_waste_heat_I_1*OnOffHP_waste_heat_I_1[i]+(1 .- OnOffHP_waste_heat_I_1[i])*P_min_HP_waste_heat_I_1)
        @constraint(m, HP_waste_heat_I_1[i]-HP_waste_heat_I_1[i .- 1].<=ramp_up_down_HP_waste_heat_I_1*OnOffHP_waste_heat_I_1[i .- 1]+(1 .- OnOffHP_waste_heat_I_1[i .- 1])*P_min_HP_waste_heat_I_1)
        @constraint(m, HP_waste_heat_I_2[i .- 1]-HP_waste_heat_I_2[i].<=ramp_up_down_HP_waste_heat_I_2*OnOffHP_waste_heat_I_2[i]+(1 .- OnOffHP_waste_heat_I_2[i])*P_min_HP_waste_heat_I_2)
        @constraint(m, HP_waste_heat_I_2[i]-HP_waste_heat_I_2[i .- 1].<=ramp_up_down_HP_waste_heat_I_2*OnOffHP_waste_heat_I_2[i .- 1]+(1 .- OnOffHP_waste_heat_I_2[i .- 1])*P_min_HP_waste_heat_I_2)
        @constraint(m, HP_waste_heat_I_3[i .- 1]-HP_waste_heat_I_3[i].<=ramp_up_down_HP_waste_heat_I_3*OnOffHP_waste_heat_I_3[i]+(1 .- OnOffHP_waste_heat_I_3[i])*P_min_HP_waste_heat_I_3)
        @constraint(m, HP_waste_heat_I_3[i]-HP_waste_heat_I_3[i .- 1].<=ramp_up_down_HP_waste_heat_I_3*OnOffHP_waste_heat_I_3[i .- 1]+(1 .- OnOffHP_waste_heat_I_3[i .- 1])*P_min_HP_waste_heat_I_3)

        @constraint(m, HP_waste_heat_II_1[i .- 1]-HP_waste_heat_II_1[i].<=ramp_up_down_HP_waste_heat_II_1*OnOffHP_waste_heat_II_1[i]+(1 .- OnOffHP_waste_heat_II_1[i])*P_min_HP_waste_heat_II_1)
        @constraint(m, HP_waste_heat_II_1[i]-HP_waste_heat_II_1[i .- 1].<=ramp_up_down_HP_waste_heat_II_1*OnOffHP_waste_heat_II_1[i .- 1]+(1 .- OnOffHP_waste_heat_II_1[i .- 1])*P_min_HP_waste_heat_II_1)
        @constraint(m, HP_waste_heat_II_2[i .- 1]-HP_waste_heat_II_2[i].<=ramp_up_down_HP_waste_heat_II_2*OnOffHP_waste_heat_II_2[i]+(1 .- OnOffHP_waste_heat_II_2[i])*P_min_HP_waste_heat_II_2)
        @constraint(m, HP_waste_heat_II_2[i]-HP_waste_heat_II_2[i .- 1].<=ramp_up_down_HP_waste_heat_II_2*OnOffHP_waste_heat_II_2[i .- 1]+(1 .- OnOffHP_waste_heat_II_2[i .- 1])*P_min_HP_waste_heat_II_2)
        @constraint(m, HP_waste_heat_II_3[i .- 1]-HP_waste_heat_II_3[i].<=ramp_up_down_HP_waste_heat_II_3*OnOffHP_waste_heat_II_3[i]+(1 .- OnOffHP_waste_heat_II_3[i])*P_min_HP_waste_heat_II_3)
        @constraint(m, HP_waste_heat_II_3[i]-HP_waste_heat_II_3[i .- 1].<=ramp_up_down_HP_waste_heat_II_3*OnOffHP_waste_heat_II_3[i .- 1]+(1 .- OnOffHP_waste_heat_II_3[i .- 1])*P_min_HP_waste_heat_II_3)

        @constraint(m, HP_waste_heat_III_1[i .- 1]-HP_waste_heat_III_1[i].<=ramp_up_down_HP_waste_heat_III_1*OnOffHP_waste_heat_III_1[i]+(1 .- OnOffHP_waste_heat_III_1[i])*P_min_HP_waste_heat_III_1)
        @constraint(m, HP_waste_heat_III_1[i]-HP_waste_heat_III_1[i .- 1].<=ramp_up_down_HP_waste_heat_III_1*OnOffHP_waste_heat_III_1[i .- 1]+(1 .- OnOffHP_waste_heat_III_1[i .- 1])*P_min_HP_waste_heat_III_1)
        @constraint(m, HP_waste_heat_III_2[i .- 1]-HP_waste_heat_III_2[i].<=ramp_up_down_HP_waste_heat_III_2*OnOffHP_waste_heat_III_2[i]+(1 .- OnOffHP_waste_heat_III_2[i])*P_min_HP_waste_heat_III_2)
        @constraint(m, HP_waste_heat_III_2[i]-HP_waste_heat_III_2[i .- 1].<=ramp_up_down_HP_waste_heat_III_2*OnOffHP_waste_heat_III_2[i .- 1]+(1 .- OnOffHP_waste_heat_III_2[i .- 1])*P_min_HP_waste_heat_III_2)
        @constraint(m, HP_waste_heat_III_3[i .- 1]-HP_waste_heat_III_3[i].<=ramp_up_down_HP_waste_heat_III_3*OnOffHP_waste_heat_III_3[i]+(1 .- OnOffHP_waste_heat_III_3[i])*P_min_HP_waste_heat_III_3)
        @constraint(m, HP_waste_heat_III_3[i]-HP_waste_heat_III_3[i .- 1].<=ramp_up_down_HP_waste_heat_III_3*OnOffHP_waste_heat_III_3[i .- 1]+(1 .- OnOffHP_waste_heat_III_3[i .- 1])*P_min_HP_waste_heat_III_3)


        @constraint(m, HP_waste_heat_seasonal[i .- 1]-HP_waste_heat_seasonal[i].<=ramp_up_down_HP_waste_heat_seasonal*OnOffHP_waste_heat_seasonal[i]+(1 .- OnOffHP_waste_heat_seasonal[i])*P_min_HP_waste_heat_seasonal)
        @constraint(m, HP_waste_heat_seasonal[i]-HP_waste_heat_seasonal[i .- 1].<=ramp_up_down_HP_waste_heat_seasonal*OnOffHP_waste_heat_seasonal[i .- 1]+(1 .- OnOffHP_waste_heat_seasonal[i .- 1])*P_min_HP_waste_heat_seasonal)

        @constraint(m, HP_waste_heat_absorption[i .- 1]-HP_waste_heat_absorption[i].<=ramp_up_down_HP_waste_heat_absorption*OnOffHP_waste_heat_absorption[i]+(1 .- OnOffHP_waste_heat_absorption[i])*P_min_HP_waste_heat_absorption)
        @constraint(m, HP_waste_heat_absorption[i]-HP_waste_heat_absorption[i .- 1].<=ramp_up_down_HP_waste_heat_absorption*OnOffHP_waste_heat_absorption[i .- 1]+(1 .- OnOffHP_waste_heat_absorption[i .- 1])*P_min_HP_waste_heat_absorption)

        ###### Objective function ######

        # Minimize total running costs


        @objective(m,Min, sum(Error)*1e2
                          + sum(HOB)*(cost_var_HOB .+ cost_fuel_HOB/eta_HOB)
                          + sum(HOB_2)*(cost_var_HOB_2 .+ cost_fuel_HOB_2/eta_HOB_2)
                          + sum(HOB_3)*(cost_var_HOB_3 .+ cost_fuel_HOB_3/eta_HOB_3)
                          + sum(EH.*(cost_var_EH .+ cost_fuel_EH/eta_EH))
                          + sum(EH_2.*(cost_var_EH_2 .+ cost_fuel_EH_2/eta_EH_2))
                          + sum(EH_3.*(cost_var_EH_3 .+ cost_fuel_EH_3/eta_EH_3))
                          + sum(HP.*(cost_var_HP .+ cost_fuel_HP./eta_HP))
                          + sum(HP_2.*(cost_var_HP_2 .+ cost_fuel_HP_2./eta_HP_2))
                          + sum(HP_3.*(cost_var_HP_3 .+ cost_fuel_HP_3./eta_HP_3))
                          + sum(HP_absorption.*(cost_var_HP_absorption .+ cost_fuel_HP_absorption./eta_HP_absorption))
                          + sum(CHP)*(cost_var_CHP .+ cost_fuel_CHP/eta_CHP_th)
                          + sum(CHP_2)*(cost_var_CHP_2 .+ cost_fuel_CHP_2/eta_CHP_th_2)
                          + sum(CHP_ORC)*(cost_var_CHP_ORC)
                          + sum(ST)*cost_var_ST
                          + sum(ST_2)*cost_var_ST_2
                          + sum(ST_seasonal)*cost_var_ST_seasonal
                          + sum(HEX)*cost_var_HEX
                          + sum(HP_waste_heat_I_1.*(cost_var_HP_waste_heat_I_1 .+ cost_fuel_HP_waste_heat_I_1./eta_HP_waste_heat_I_1))
                          + sum(HP_waste_heat_I_2.*(cost_var_HP_waste_heat_I_2 .+ cost_fuel_HP_waste_heat_I_2./eta_HP_waste_heat_I_2))
                          + sum(HP_waste_heat_I_3.*(cost_var_HP_waste_heat_I_3 .+ cost_fuel_HP_waste_heat_I_3./eta_HP_waste_heat_I_3))
                          + sum(HP_waste_heat_II_1.*(cost_var_HP_waste_heat_II_1 .+ cost_fuel_HP_waste_heat_II_1./eta_HP_waste_heat_II_1))
                          + sum(HP_waste_heat_II_2.*(cost_var_HP_waste_heat_II_2 .+ cost_fuel_HP_waste_heat_II_2./eta_HP_waste_heat_II_2))
                          + sum(HP_waste_heat_II_3.*(cost_var_HP_waste_heat_II_3 .+ cost_fuel_HP_waste_heat_II_3./eta_HP_waste_heat_II_3))
                          + sum(HP_waste_heat_III_1.*(cost_var_HP_waste_heat_III_1 .+ cost_fuel_HP_waste_heat_III_1./eta_HP_waste_heat_III_1))
                          + sum(HP_waste_heat_III_2.*(cost_var_HP_waste_heat_III_2 .+ cost_fuel_HP_waste_heat_III_2./eta_HP_waste_heat_III_2))
                          + sum(HP_waste_heat_III_3.*(cost_var_HP_waste_heat_III_3 .+ cost_fuel_HP_waste_heat_III_3./eta_HP_waste_heat_III_3))
                          + sum(HP_waste_heat_seasonal.*(cost_var_HP_waste_heat_seasonal .+ cost_fuel_HP_waste_heat_seasonal./eta_HP_waste_heat_seasonal))
                          + sum(HP_waste_heat_absorption.*(cost_var_HP_waste_heat_absorption .+ cost_fuel_HP_waste_heat_absorption./eta_HP_waste_heat_absorption))
                          - sum(CHP*cb_CHP.*CHP_electricity_price)
                          - sum(CHP_2*cb_CHP_2.*CHP_electricity_price_2)
                          - sum(CHP_ORC*cb_CHP_ORC.*CHP_ORC_electricity_price))

        print_function("Julia code for district heating: solve(m)...")

        optimize!(m)
        status = termination_status(m)

        print_function(string("Exit with status:", status))
        print_function("Julia code for district heating: END OF SCRIPT!")
        if primal_status(m) == MOI.NO_SOLUTION
            print_function("No solution found.")
            return
        end

        ##### Result visualization ####

        Result_HOB=value.(HOB)
        Result_HOB_2=value.(HOB_2)
        Result_HOB_3=value.(HOB_3)

        Result_EH=value.(EH)
        Result_EH_2=value.(EH_2)
        Result_EH_3=value.(EH_3)

        Result_HP=value.(HP)
        Result_HP_2=value.(HP_2)
        Result_HP_3=value.(HP_3)
        Result_HP_absorption=value.(HP_absorption)

        Result_CHP=value.(CHP)
        Result_CHP_2=value.(CHP_2)


        Result_CHP_ORC=value.(CHP_ORC)

        Result_ST=value.(ST)
        Result_ST_2=value.(ST_2)
        Result_ST_seasonal=value.(ST_seasonal)

        Result_HEX=value.(HEX)

        Result_HP_waste_heat_I_1=value.(HP_waste_heat_I_1)
        Result_HP_waste_heat_I_2=value.(HP_waste_heat_I_2)
        Result_HP_waste_heat_I_3=value.(HP_waste_heat_I_3)

        Result_HP_waste_heat_II_1=value.(HP_waste_heat_II_1)
        Result_HP_waste_heat_II_2=value.(HP_waste_heat_II_2)
        Result_HP_waste_heat_II_3=value.(HP_waste_heat_II_3)

        Result_HP_waste_heat_III_1=value.(HP_waste_heat_III_1)
        Result_HP_waste_heat_III_2=value.(HP_waste_heat_III_2)
        Result_HP_waste_heat_III_3=value.(HP_waste_heat_III_3)

        Result_HP_waste_heat_seasonal=value.(HP_waste_heat_seasonal)
        Result_HP_waste_heat_absorption=value.(HP_waste_heat_absorption)


        Result_SOC=value.(SOC)
        Result_SOC_seasonal=value.(SOC_seasonal)
        Result_Error=value.(Error)

        #load duration for each technology #

        sort_Result_HOB=sort(Result_HOB, rev=true)
        sort_Result_HOB_2=sort(Result_HOB_2, rev=true)
        sort_Result_HOB_3=sort(Result_HOB_3, rev=true)
        sort_Result_EH=sort(Result_EH, rev=true)
        sort_Result_EH_2=sort(Result_EH_2, rev=true)
        sort_Result_EH_3=sort(Result_EH_3, rev=true)
        sort_Result_HP=sort(Result_HP, rev=true)
        sort_Result_HP_2=sort(Result_HP_2, rev=true)
        sort_Result_HP_3=sort(Result_HP_3, rev=true)
        sort_Result_HP_absorption=sort(Result_HP_absorption, rev=true)
        sort_Result_CHP=sort(Result_CHP, rev=true)
        sort_Result_CHP_2=sort(Result_CHP_2, rev=true)
        sort_Result_CHP_ORC=sort(Result_CHP_ORC, rev=true)
        sort_Result_ST=sort(Result_ST, rev=true)
        sort_Result_ST_2=sort(Result_ST_2, rev=true)
        sort_Result_ST_seasonal=sort(Result_ST_seasonal, rev=true)
        sort_Result_HEX=sort(Result_HEX, rev=true)
        sort_Result_HP_waste_heat_I_1=sort(Result_HP_waste_heat_I_1, rev=true)
        sort_Result_HP_waste_heat_I_2=sort(Result_HP_waste_heat_I_2, rev=true)
        sort_Result_HP_waste_heat_I_3=sort(Result_HP_waste_heat_I_3, rev=true)
        sort_Result_HP_waste_heat_seasonal=sort(Result_HP_waste_heat_seasonal, rev=true)
        sort_Result_HP_waste_heat_absorption=sort(Result_HP_waste_heat_absorption, rev=true)
        sort_Result_Error=sort(Result_Error, rev=true)

        sort_Result_HP_waste_heat_II_1=sort(Result_HP_waste_heat_II_1, rev=true)
        sort_Result_HP_waste_heat_II_2=sort(Result_HP_waste_heat_II_2, rev=true)
        sort_Result_HP_waste_heat_II_3=sort(Result_HP_waste_heat_II_3, rev=true)

        sort_Result_HP_waste_heat_III_1=sort(Result_HP_waste_heat_III_1, rev=true)
        sort_Result_HP_waste_heat_III_2=sort(Result_HP_waste_heat_III_2, rev=true)
        sort_Result_HP_waste_heat_III_3=sort(Result_HP_waste_heat_III_3, rev=true)


        ## Export results ##
        writedlm(string(output_folder, "\\Result_HOB_",network_id ,".csv"), Result_HOB, csv_sep)
        writedlm(string(output_folder, "\\Result_HOB_2_",network_id ,".csv"), Result_HOB_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HOB_3_",network_id ,".csv"), Result_HOB_3, csv_sep)

        writedlm(string(output_folder, "\\Result_EH_",network_id ,".csv"), Result_EH, csv_sep)
        writedlm(string(output_folder, "\\Result_EH_2_",network_id ,".csv"), Result_EH_2, csv_sep)
        writedlm(string(output_folder, "\\Result_EH_3_",network_id ,".csv"), Result_EH_3, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_1_",network_id ,".csv"), Result_HP, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_2_",network_id ,".csv"), Result_HP_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_3_",network_id ,".csv"), Result_HP_3, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_absorption_",network_id ,".csv"), Result_HP_absorption, csv_sep)

        writedlm(string(output_folder, "\\Result_CHP_",network_id ,".csv"), Result_CHP, csv_sep)
        writedlm(string(output_folder, "\\Result_CHP_2_",network_id ,".csv"), Result_CHP_2, csv_sep)

        writedlm(string(output_folder, "\\Result_CHP_ORC_",network_id ,".csv"), Result_CHP_ORC, csv_sep)

        writedlm(string(output_folder, "\\Result_ST_",network_id ,".csv"), Result_ST, csv_sep)
        writedlm(string(output_folder, "\\Result_ST_2_",network_id ,".csv"), Result_ST_2, csv_sep)
        writedlm(string(output_folder, "\\Result_ST_seasonal_",network_id ,".csv"), Result_ST_seasonal, csv_sep)

        writedlm(string(output_folder, "\\Result_HEX_",network_id ,".csv"), Result_HEX, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_I_1_",network_id ,".csv"), Result_HP_waste_heat_I_1, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_I_2_",network_id ,".csv"), Result_HP_waste_heat_I_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_I_3_",network_id ,".csv"), Result_HP_waste_heat_I_3, csv_sep)


        writedlm(string(output_folder, "\\Result_HP_II_1_",network_id ,".csv"), Result_HP_waste_heat_II_1, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_II_2_",network_id ,".csv"), Result_HP_waste_heat_II_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_II_3_",network_id ,".csv"), Result_HP_waste_heat_II_3, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_III_1_",network_id ,".csv"), Result_HP_waste_heat_III_1, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_III_2_",network_id ,".csv"), Result_HP_waste_heat_III_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_III_3_",network_id ,".csv"), Result_HP_waste_heat_III_3, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_waste_heat_seasonal_",network_id ,".csv"), Result_HP_waste_heat_seasonal, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_waste_heat_absorption_",network_id ,".csv"), Result_HP_waste_heat_absorption, csv_sep)
        writedlm(string(output_folder, "\\Result_DEM_",network_id ,".csv"), DEM, csv_sep)
        writedlm(string(output_folder, "\\Result_SOC_",network_id ,".csv"), Result_SOC, csv_sep)
        writedlm(string(output_folder, "\\Result_SOC_seasonal_",network_id ,".csv"), Result_SOC_seasonal, csv_sep)
        writedlm(string(output_folder, "\\Result_Error_",network_id ,".csv"), Result_Error, csv_sep)
    end

    export district_solver

    function write_results_example(output_folder, network_id, example_file)
        writedlm(string(output_folder, "\\Result_HOB_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HOB_2_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HOB_3_",network_id ,".csv"), example_file, csv_sep)

        writedlm(string(output_folder, "\\Result_EH_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_EH_2_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_EH_3_",network_id ,".csv"), example_file, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_2_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_3_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_absorption_",network_id ,".csv"), example_file, csv_sep)

        writedlm(string(output_folder, "\\Result_CHP_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_CHP_2_",network_id ,".csv"), example_file, csv_sep)


        writedlm(string(output_folder, "\\Result_CHP_ORC_",network_id ,".csv"), example_file, csv_sep)

        writedlm(string(output_folder, "\\Result_ST_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_ST_2_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_ST_seasonal_",network_id ,".csv"), example_file, csv_sep)

        writedlm(string(output_folder, "\\Result_HEX_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_I_1_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_I_2_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_I_3_",network_id ,".csv"), example_file, csv_sep)


        writedlm(string(output_folder, "\\Result_HP_II_1_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_II_2_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_II_3_",network_id ,".csv"), example_file, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_III_1_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_III_2_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_III_3_",network_id ,".csv"), example_file, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_waste_heat_seasonal_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_waste_heat_absorption_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_DEM_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_SOC_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_SOC_seasonal_",network_id ,".csv"), example_file, csv_sep)
        writedlm(string(output_folder, "\\Result_Error_",network_id ,".csv"), example_file, csv_sep)
    end
end