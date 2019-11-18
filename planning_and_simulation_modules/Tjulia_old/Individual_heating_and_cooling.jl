module individual_heating_and_cooling

    using JuMP
    using Cbc
    using Clp
    using CSV

    function individual_H_and_C(input_folder, output_folder, tech_infos, building_id, print_function = print)

       # m = Model(solver = CbcSolver(logLevel=3, seconds=60))
       # input_folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\Tjulia\\single_building\\input"

        m = Model(solver = CbcSolver(logLevel=1, ratioGap=1e-4))

        #T_start=1
        #T_end=8760

        file_end = string(building_id, ".csv")
        file = string("\\DEM_time_", file_end)
        DEM = readcsv(string(input_folder, file))
        #DEM=DEM[T_start:T_end]

        file = string("\\DEM_DHW_time_", file_end)
        DEM_DHW = readcsv(string(input_folder, file))
        # DEM_DHW=DEM_DHW[1:4000]

        file = string("\\DEM_cool_time_", file_end)
        DEM_cool = readcsv(string(input_folder, file))
        # DEM_cool=DEM_cool[1:4000]

        ST_specific = readcsv(string(input_folder, "\\ST_specific_time.csv"))
        # ST_specific=ST_specific[1:4000]

        Electricity_price = readcsv(string(input_folder, "\\Electricity_price_time.csv"))
        # Electricity_price=Electricity_price[1:4000]

        eta_HP = readcsv(string(input_folder, "\\eta_HP_1.csv"))
        # eta_HP = eta_HP[1:4000]

        eta_HP_2 = readcsv(string(input_folder, "\\eta_HP_2.csv"))
        # eta_HP_2 = eta_HP_2[1:4000]

        eta_HP_cool = readcsv(string(input_folder, "\\eta_HP_cool.csv"))
        # eta_HP_cool = eta_HP_cool[1:4000]

        eta_HP_cool_2 = readcsv(string(input_folder, "\\eta_HP_cool_2.csv"))
        # eta_HP_cool_2 = eta_HP_cool_2[1:4000]


        ####### Technology input data ########
        ## Heat only boiler ##

        # Installed capacity [MW]
        P_max_HOB = tech_infos["P_max_HOB"] #1
        # Efficiency [-]
        eta_HOB = tech_infos["eta_HOB"] #0.8
        # Variable cost [EUR/MWh]
        cost_var_HOB = tech_infos["cost_var_HOB"] #5.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB = tech_infos["cost_fuel_HOB"] #10
        tec_min_HOB = tech_infos["tec_min_HOB"]
        P_min_HOB = tec_min_HOB *P_max_HOB
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB=tech_infos["Percentage_ramp_up_down_HOB"]
        ramp_up_down_HOB = P_max_HOB*Percentage_ramp_up_down_HOB

        ## Heat only boiler 2 ##

        # Installed capacity [MW]
        P_max_HOB_2 = tech_infos["P_max_HOB_2"] #1
        # Efficiency [-]
        eta_HOB_2 = tech_infos["eta_HOB_2"] #0.8
        # Variable cost [EUR/MWh]
        cost_var_HOB_2 = tech_infos["cost_var_HOB_2"] #5.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB_2 = tech_infos["cost_fuel_HOB_2"] #12.5
        tec_min_HOB_2 = tech_infos["tec_min_HOB_2"]
        P_min_HOB_2 = tec_min_HOB_2 *P_max_HOB_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB_2=tech_infos["Percentage_ramp_up_down_HOB_2"]
        ramp_up_down_HOB_2 = P_max_HOB_2*Percentage_ramp_up_down_HOB_2

        ## Electrical heater ##

        # Installed capacity [MW]
        P_max_EH = tech_infos["P_max_EH"] #0
        # Technical minimum [MW]
        Technical_minimum_EH = tech_infos["Technical_minimum_EH"] #0
        P_min_EH = P_max_EH*Technical_minimum_EH
        # Efficiency [-]
        eta_EH = tech_infos["eta_EH"] #0.98
        # Variable cost [EUR/MWh]
        cost_var_EH = tech_infos["cost_var_EH"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_EH = Electricity_price
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_EH=tech_infos["Percentage_ramp_up_down_EH"]
        ramp_up_down_EH = P_max_EH*Percentage_ramp_up_down_EH

        ## Electrical heater 2 ##

        # Installed capacity [MW]
        P_max_EH_2 = tech_infos["P_max_EH_2"] #0
        # Efficiency [-]
        eta_EH_2 = tech_infos["eta_EH_2"] #0.98
        # Variable cost [EUR/MWh]
        cost_var_EH_2 = tech_infos["cost_var_EH_2"] #0.7
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_EH_2 = Electricity_price
        Technical_minimum_EH_2 = tech_infos["Technical_minimum_EH_2"] #0
        P_min_EH_2 = P_max_EH_2*Technical_minimum_EH_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_EH_2=tech_infos["Percentage_ramp_up_down_EH_2"]
        ramp_up_down_EH_2 = P_max_EH_2*Percentage_ramp_up_down_EH_2

        ## Heat pump ##

        # Installed capacity [MW]
        P_max_HP = tech_infos["P_max_HP"] #1
        # Efficiency [-]
        eta_HP = eta_HP
        # Variable cost [EUR/MWh]
        cost_var_HP = tech_infos["cost_var_HP"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP = Electricity_price
        Tecnical_minimum_HP= tech_infos["Technical_minimum_HP"] #0
        P_min_HP = Tecnical_minimum_HP*P_max_HP
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP=tech_infos["Percentage_ramp_up_down_HP"]
        ramp_up_down_HP = P_max_HP*Percentage_ramp_up_down_HP

        ## Heat pump 2 ##

        # Installed capacity [MW]
        P_max_HP_2 = tech_infos["P_max_HP_2"] #1
        # Efficiency [-]
        eta_HP_2 = eta_HP_2
        # Variable cost [EUR/MWh]
        cost_var_HP_2 = tech_infos["cost_var_HP_2"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_2 = Electricity_price
        Tecnical_minimum_HP_2= tech_infos["Technical_minimum_HP_2"] #0
        P_min_HP_2 = Tecnical_minimum_HP_2*P_max_HP_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_2=tech_infos["Percentage_ramp_up_down_HP_2"]
        ramp_up_down_HP_2 = P_max_HP_2*Percentage_ramp_up_down_HP_2

        ## Absorption heat pump ##

        # Installed capacity [MW]
        P_max_HP_absorption = tech_infos["P_max_HP_absorption"] #1
        # Efficiency [-]
        eta_HP_absorption =  tech_infos["eta_HP"]
        # Variable cost [EUR/MWh]
        cost_var_HP_absorption = tech_infos["cost_var_HP_absorption"]
        # Fuel cost [EUR/MWh]
        cost_fuel_HP_absorption = tech_infos["cost_fuel_HP_absorption"]
        # Technical minimum [MW]
        Tecnical_minimum_HP_absorption=tech_infos["Tecnical_minimum_HP_absorption"]
        P_min_HP_absorption = Tecnical_minimum_HP_absorption*P_max_HP_absorption
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_absorption=tech_infos["Percentage_ramp_up_down_HP_absorption"]
        ramp_up_down_HP_absorption = P_max_HP_absorption*Percentage_ramp_up_down_HP_absorption


        ## Cogeneration ##

        # Installed capacity [MW]
        P_max_CHP = tech_infos["P_max_CHP"] #0
        # Efficiency [-]
        eta_CHP_th = tech_infos["eta_CHP_th"] #0.65
        # Power-to-heat ratio [-]
        cb_CHP = tech_infos["cb_CHP"] #0.3
        # Variable cost [EUR/MWh]
        cost_var_CHP = tech_infos["cost_var_CHP"] #3.9
        # Fuel cost [EUR/MWh]
        cost_fuel_CHP = tech_infos["cost_fuel_CHP"] #20
        # Price paid to CHP for electrcity production
        CHP_electricity_price=Electricity_price
        # Technical minimum [MW]
        Tecnical_minimum_CHP= tech_infos["Tecnical_minimum_CHP"]
        P_min_CHP = Tecnical_minimum_CHP*P_max_CHP
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_CHP=tech_infos["Percentage_ramp_up_down_CHP"]
        ramp_up_down_CHP= P_max_CHP*Percentage_ramp_up_down_CHP

        ## Solar thermal ##

        # Installed solar thermal collector area [m2]
        A_ST= tech_infos["A_ST"] #100
        # Variable cost [EUR/MWh]
        cost_var_ST = tech_infos["cost_var_ST"] #0.5
        # Solar thermal collector prodution [MW]
        P_max_ST=A_ST*ST_specific/1000000

        ## Cooling heat pump ##

        # Installed capacity [MW]
        P_max_HP_cool = tech_infos["P_max_HP_cool"] #0.5
        # Efficiency [-]
        eta_HP_cool = eta_HP_cool
        # Variable cost [EUR/MWh]
        cost_var_HP_cool = tech_infos["cost_var_HP_cool"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_cool = Electricity_price
        # Technical minimum [MW]
        Tecnical_minimum_HP_cool=tech_infos["Tecnical_minimum_HP_cool"]
        P_min_HP_cool = Tecnical_minimum_HP_cool*P_max_HP_cool
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_cool=tech_infos["Percentage_ramp_up_down_HP_cool"]
        ramp_up_down_HP_cool = P_max_HP_cool*Percentage_ramp_up_down_HP_cool


        ## Cooling heat pump 2 ##

        # Installed capacity [MW]
        P_max_HP_cool_2 = tech_infos["P_max_HP_cool_2"] #0.5
        # Efficiency [-]
        eta_HP_cool_2 = eta_HP_cool_2
        # Variable cost [EUR/MWh]
        cost_var_HP_cool_2 = tech_infos["cost_var_HP_cool_2"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_cool_2 = Electricity_price
        Tecnical_minimum_HP_cool_2=tech_infos["Tecnical_minimum_HP_cool_2"]
        P_min_HP_cool_2 = Tecnical_minimum_HP_cool_2*P_max_HP_cool_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_cool_2=tech_infos["Percentage_ramp_up_down_HP_cool_2"]
        ramp_up_down_HP_cool_2 = P_max_HP_cool_2*Percentage_ramp_up_down_HP_cool_2


        ## Absorption Cooling heat pump ##

        # Installed capacity [MW]
        P_max_HP_cool_absorption = tech_infos["P_max_HP_cool_absorption"]
        # Efficiency [-]
        eta_HP_cool_absorption = tech_infos["eta_HP_cool_absorption"]
        # Variable cost [EUR/MWh]
        cost_var_HP_cool_absorption = tech_infos["cost_var_HP_cool_absorption"]
        # Fuel cost [EUR/MWh]
        cost_fuel_HP_cool_absorption = tech_infos["cost_fuel_HP_cool_absorption"]
        # Technical minimum [MW]
        Tecnical_minimum_HP_cool_absorption=tech_infos["Tecnical_minimum_HP_cool_absorption"]
        P_min_HP_cool_absorption = Tecnical_minimum_HP_cool_absorption*P_max_HP_cool_absorption
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_cool_absorption=tech_infos["Percentage_ramp_up_down_HP_cool_absorption"]
        ramp_up_down_HP_cool_absorption = P_max_HP_cool_absorption*Percentage_ramp_up_down_HP_cool_absorption

        ## Thermal energy storage ##

        # Thermal energy storage size [MWh]
        TES_size = tech_infos["TES_size"] #0
        # Minimum percentage of state of charge of thermal energy storage [-]
        SOC_min = tech_infos["SOC_min"] #0.15
        # Thermal energy storage state of charge at the start/end of the year [-]
        TES_start_end = tech_infos["TES_start_end"] #0.5
        # Thermal storage charge/discharge capacity [MW]
        TES_charge_discharge_time = tech_infos["TES_charge_discharge_time"] #5
        TES_in_out_max = TES_size/TES_charge_discharge_time
        TES_loss=0.5/(24*7)

        ## Domestic hot water thermal energy storage ##

        # Thermal energy storage size [MWh]
        TES_size_DHW = tech_infos["TES_size_DHW"] #1
        # Minimum percentage of state of charge of thermal energy storage [-]
        SOC_min_DHW = tech_infos["SOC_min_DHW"] #0.0
        # Thermal energy storage state of charge at the start/end of the year [-]
        TES_start_end_DHW = tech_infos["TES_start_end_DHW"] #0.0
        # Thermal storage charge/discharge capacity [MW]
        TES_charge_discharge_time_DHW = tech_infos["TES_charge_discharge_time_DHW"] #5
        TES_in_out_max_DHW = TES_size_DHW/TES_charge_discharge_time_DHW
        TES_loss_DHW=0.5/(24*7)

        ######## Constraints and variables ########
        ### Variables ###

        # Technologies' operation
        @variable(m, P_max_HOB >= HOB[1:length(DEM)] >= 0)
        @variable(m, P_max_HOB_2 >= HOB_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HOB >= HOB_DHW[1:length(DEM)] >= 0)
        @variable(m, P_max_HOB_2 >= HOB_2_DHW[1:length(DEM)] >= 0)

        @variable(m, P_max_EH >= EH[1:length(DEM)] >= 0)
        @variable(m, P_max_EH_2 >= EH_2[1:length(DEM)] >= 0)
        @variable(m, P_max_EH >= EH_DHW[1:length(DEM)] >= 0)
        @variable(m, P_max_EH_2 >= EH_2_DHW[1:length(DEM)] >= 0)

        @variable(m, P_max_HP >= HP[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_2 >= HP_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HP >= HP_DHW[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_2 >= HP_2_DHW[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_absorption >= HP_absorption[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_absorption >= HP_absorption_DHW[1:length(DEM)] >= 0)

        @variable(m, P_max_CHP >= CHP[1:length(DEM)] >= 0)
        @variable(m, P_max_CHP >= CHP_DHW[1:length(DEM)] >= 0)

        @variable(m, ST[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_cool >= HP_cool[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_cool_2 >= HP_cool_2[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_cool_absorption >= HP_cool_absorption[1:length(DEM)] >= 0)

        @variable(m, TES_in_out_max >=TES[1:length(DEM)]>= -TES_in_out_max)
        @variable(m, TES_size >= SOC[1:length(DEM)] >= TES_size*SOC_min)

        @variable(m, TES_in_out_max_DHW >=TES_DHW[1:length(DEM)]>= -TES_in_out_max_DHW)
        @variable(m, TES_size_DHW >= SOC_DHW[1:length(DEM)] >= TES_size_DHW*SOC_min_DHW)



        # Binary variables, on/off

        @variable(m, OnOffHOB[1:length(DEM)], Bin)
        @variable(m, OnOffHOB_2[1:length(DEM)], Bin)
        @variable(m, OnOffEH[1:length(DEM)], Bin)
        @variable(m, OnOffEH_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP[1:length(DEM)], Bin)
        @variable(m, OnOffHP_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_absorption[1:length(DEM)], Bin)
        @variable(m, OnOffCHP[1:length(DEM)], Bin)
        @variable(m, OnOffHP_cool[1:length(DEM)], Bin)
        @variable(m, OnOffHP_cool_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_cool_absorption[1:length(DEM)], Bin)

        ### Constraints ###
        # Supply + TES = DEM



		
		@constraint(m, HOB+HOB_2+EH+EH_2+HP+HP_2+HP_absorption+CHP-TES.== DEM)
		@constraint(m, HOB_DHW+HOB_2_DHW+EH_DHW+EH_2_DHW+HP_DHW+HP_2_DHW+HP_absorption_DHW+CHP_DHW+ST-TES_DHW.== DEM_DHW)

		@constraint(m, HP_cool+HP_cool_2+HP_cool_absorption.== DEM_cool)

        @constraint(m, HOB+HOB_DHW .<= P_max_HOB)
        @constraint(m, HOB_2+HOB_2_DHW .<= P_max_HOB_2)
        @constraint(m, EH+EH_DHW .<= P_max_EH)
        @constraint(m, EH_2+EH_2_DHW .<= P_max_EH_2)
        @constraint(m, HP+HP_DHW .<= P_max_HP)
        @constraint(m, HP_2+HP_2_DHW .<= P_max_HP_2)
        @constraint(m, HP_absorption+HP_absorption_DHW .<= P_max_HP_absorption)

        @constraint(m, CHP+CHP_DHW .<= P_max_CHP)



        # Thermal storage constraints
        t=2:(length(DEM)-1)
        @constraint(m, SOC[t]-SOC[t-1]-TES[t]+SOC[t]*TES_loss .== 0)
        @constraint(m, SOC[length(DEM)-1]+TES[length(DEM)] == TES_size*TES_start_end)
        @constraint(m, SOC[1]-TES[1] == TES_size*TES_start_end)
        @constraint(m, SOC[length(DEM)] == TES_size*TES_start_end)

        # Domestic hot water thermal storage constraints
        @constraint(m, SOC_DHW[t]-SOC_DHW[t-1]-TES_DHW[t]+SOC_DHW[t]*TES_loss_DHW .== 0)
        @constraint(m, SOC_DHW[length(DEM)-1]+TES_DHW[length(DEM)] == TES_size_DHW*TES_start_end_DHW)
        @constraint(m, SOC_DHW[1]-TES_DHW[1] == TES_size_DHW*TES_start_end_DHW)
        @constraint(m, SOC_DHW[length(DEM)] == TES_size_DHW*TES_start_end_DHW)

        # Solar thermal collector constraints - has to utilize all available
        @constraint(m, ST .<= P_max_ST)

        # OnOff constraints - technical minimum
        @constraint(m, OnOffHOB*P_min_HOB-(HOB+HOB_DHW).<=0)
        @constraint(m, -OnOffHOB*P_max_HOB+(HOB+HOB_DHW).<=0)
        @constraint(m, OnOffHOB_2*P_min_HOB_2-(HOB_2+HOB_2_DHW).<=0)
        @constraint(m, -OnOffHOB_2*P_max_HOB_2+(HOB_2+HOB_2_DHW).<=0)

        @constraint(m, OnOffEH*P_min_EH-(EH+EH_DHW).<=0)
        @constraint(m, -OnOffEH*P_max_EH+(EH+EH_DHW).<=0)
        @constraint(m, OnOffEH_2*P_min_EH_2-(EH_2+EH_2_DHW).<=0)
        @constraint(m, -OnOffEH_2*P_max_EH_2+(EH_2+EH_2_DHW).<=0)

        @constraint(m, OnOffHP*P_min_HP-(HP+HP_DHW).<=0)
        @constraint(m, -OnOffHP*P_max_HP+(HP+HP_DHW).<=0)
        @constraint(m, OnOffHP_2*P_min_HP_2-(HP_2+HP_2_DHW).<=0)
        @constraint(m, -OnOffHP_2*P_max_HP_2+(HP_2+HP_2_DHW).<=0)

        @constraint(m, OnOffHP_absorption*P_min_HP_absorption-(HP_absorption+HP_absorption_DHW).<=0)
        @constraint(m, -OnOffHP_absorption*P_max_HP_absorption+(HP_absorption+HP_absorption_DHW).<=0)

        @constraint(m, OnOffCHP*P_min_CHP-(CHP+CHP_DHW).<=0)
        @constraint(m, -OnOffCHP*P_max_CHP+(CHP+CHP_DHW).<=0)

        @constraint(m, OnOffHP_absorption*P_min_HP_absorption-HP_absorption.<=0)
        @constraint(m, -OnOffHP_absorption*P_max_HP_absorption+HP_absorption.<=0)

        @constraint(m, OnOffHP_cool*P_min_HP_cool-HP_cool.<=0)
        @constraint(m, -OnOffHP_cool*P_max_HP_cool+HP_cool.<=0)
        @constraint(m, OnOffHP_cool_2*P_min_HP_cool_2-HP_cool_2.<=0)
        @constraint(m, -OnOffHP_cool_2*P_max_HP_cool_2+HP_cool_2.<=0)

        @constraint(m, OnOffHP_cool_absorption*P_min_HP_cool_absorption-HP_cool_absorption.<=0)
        @constraint(m, -OnOffHP_cool_absorption*P_max_HP_cool_absorption+HP_cool_absorption.<=0)

        # Ramp-up-down constraint for each technology

        i=2:length(DEM-1)

        @constraint(m, (HOB[i-1]+HOB_DHW[i-1])-(HOB[i]+HOB_DHW[i]).<=ramp_up_down_HOB*OnOffHOB[i]+(1-OnOffHOB[i])*P_min_HOB)
        @constraint(m, (HOB[i]+HOB_DHW[i])-(HOB[i-1]+HOB_DHW[i-1]).<=ramp_up_down_HOB*OnOffHOB[i-1]+(1-OnOffHOB[i-1])*P_min_HOB)
        @constraint(m, (HOB_2[i-1]+HOB_2_DHW[i-1])-(HOB_2[i]+HOB_2_DHW[i]).<=ramp_up_down_HOB_2*OnOffHOB_2[i]+(1-OnOffHOB_2[i])*P_min_HOB_2)
        @constraint(m, (HOB_2[i]+HOB_2_DHW[i])-(HOB_2[i-1]+HOB_2_DHW[i-1]).<=ramp_up_down_HOB_2*OnOffHOB_2[i-1]+(1-OnOffHOB_2[i-1])*P_min_HOB_2)

        @constraint(m, (EH[i-1]+EH_DHW[i-1])-(EH[i]+EH_DHW[i]).<=ramp_up_down_EH*OnOffEH[i]+(1-OnOffEH[i])*P_min_EH)
        @constraint(m, (EH[i]+EH_DHW[i])-(EH[i-1]+EH_DHW[i-1]).<=ramp_up_down_EH*OnOffEH[i-1]+(1-OnOffEH[i-1])*P_min_EH)
        @constraint(m, (EH_2[i-1]+EH_2_DHW[i-1])-(EH_2[i]+EH_2_DHW[i]).<=ramp_up_down_EH_2*OnOffEH_2[i]+(1-OnOffEH_2[i])*P_min_EH_2)
        @constraint(m, (EH_2[i]+EH_2_DHW[i])-(EH_2[i-1]+EH_2_DHW[i-1]).<=ramp_up_down_EH_2*OnOffEH_2[i-1]+(1-OnOffEH_2[i-1])*P_min_EH_2)

        @constraint(m, (HP[i-1]+HP_DHW[i-1])-(HP[i]+HP_DHW[i]).<=ramp_up_down_HP*OnOffHP[i]+(1-OnOffHP[i])*P_min_HP)
        @constraint(m, (HP[i]+HP_DHW[i])-(HP[i-1]+HP_DHW[i-1]).<=ramp_up_down_HP*OnOffHP[i-1]+(1-OnOffHP[i-1])*P_min_HP)
        @constraint(m, (HP_2[i-1]+HP_2_DHW[i-1])-(HP_2[i]+HP_2_DHW[i]).<=ramp_up_down_HP_2*OnOffHP_2[i]+(1-OnOffHP_2[i])*P_min_HP_2)
        @constraint(m, (HP_2[i]+HP_2_DHW[i])-(HP_2[i-1]+HP_2_DHW[i-1]).<=ramp_up_down_HP_2*OnOffHP_2[i-1]+(1-OnOffHP_2[i-1])*P_min_HP_2)

        @constraint(m, (HP_absorption[i-1]+HP_absorption_DHW[i-1])-(HP_absorption[i]+HP_absorption_DHW[i]).<=ramp_up_down_HP_absorption*OnOffHP_absorption[i]+(1-OnOffHP_absorption[i])*P_min_HP_absorption)
        @constraint(m, (HP_absorption[i]+HP_absorption_DHW[i])-(HP_absorption[i-1]+HP_absorption_DHW[i-1]).<=ramp_up_down_HP_absorption*OnOffHP_absorption[i-1]+(1-OnOffHP_absorption[i-1])*P_min_HP_absorption)

        @constraint(m, (CHP[i-1]+CHP_DHW[i-1])-(CHP[i]+CHP_DHW[i]).<=ramp_up_down_CHP*OnOffCHP[i]+(1-OnOffCHP[i])*P_min_CHP)
        @constraint(m, (CHP[i]+CHP_DHW[i])-(CHP[i-1]+CHP_DHW[i-1]).<=ramp_up_down_CHP*OnOffCHP[i-1]+(1-OnOffCHP[i-1])*P_min_CHP)

        @constraint(m, HP_cool[i-1]-HP_cool[i].<=ramp_up_down_HP_cool*OnOffHP_cool[i]+(1-OnOffHP_cool[i])*P_min_HP_cool)
        @constraint(m, HP_cool[i]-HP_cool[i-1].<=ramp_up_down_HP_cool*OnOffHP_cool[i-1]+(1-OnOffHP_cool[i-1])*P_min_HP_cool)
        @constraint(m, HP_cool_2[i-1]-HP_cool_2[i].<=ramp_up_down_HP_cool_2*OnOffHP_cool_2[i]+(1-OnOffHP_cool_2[i])*P_min_HP_cool_2)
        @constraint(m, HP_cool_2[i]-HP_cool_2[i-1].<=ramp_up_down_HP_cool_2*OnOffHP_cool_2[i-1]+(1-OnOffHP_cool_2[i-1])*P_min_HP_cool_2)

        @constraint(m, HP_cool_absorption[i-1]-HP_cool_absorption[i].<=ramp_up_down_HP_cool_absorption*OnOffHP_cool_absorption[i]+(1-OnOffHP_cool_absorption[i])*P_min_HP_cool_absorption)
        @constraint(m, HP_cool_absorption[i]-HP_cool_absorption[i-1].<=ramp_up_down_HP_cool_absorption*OnOffHP_cool_absorption[i-1]+(1-OnOffHP_cool_absorption[i-1])*P_min_HP_cool_absorption)


        ###### Objective function ######

        # Minimize total running costs
        @objective(m,Min, sum(HOB)*(cost_var_HOB+cost_fuel_HOB/eta_HOB)+sum(HOB_DHW)*(cost_var_HOB+cost_fuel_HOB/eta_HOB)+sum(HOB_2)*(cost_var_HOB_2+cost_fuel_HOB_2/eta_HOB_2)+sum(HOB_2_DHW)*(cost_var_HOB_2+cost_fuel_HOB_2/eta_HOB_2)+sum(EH.*(cost_var_EH+cost_fuel_EH/eta_EH))+sum(EH_DHW.*(cost_var_EH+cost_fuel_EH/eta_EH))+sum(EH_2.*(cost_var_EH_2+cost_fuel_EH_2/eta_EH_2))+sum(EH_2_DHW.*(cost_var_EH_2+cost_fuel_EH_2/eta_EH_2))+sum(HP.*(cost_var_HP+cost_fuel_HP./eta_HP))+sum(HP_DHW.*(cost_var_HP+cost_fuel_HP./eta_HP))+sum(HP_2.*(cost_var_HP_2+cost_fuel_HP_2./eta_HP_2))+sum(HP_2_DHW.*(cost_var_HP_2+cost_fuel_HP_2./eta_HP_2))+sum(HP_absorption.*(cost_var_HP_absorption+cost_fuel_HP_absorption./eta_HP_absorption))+sum(HP_absorption_DHW.*(cost_var_HP_absorption+cost_fuel_HP_absorption./eta_HP_absorption))+sum(CHP)*(cost_var_CHP+cost_fuel_CHP/eta_CHP_th)+sum(CHP_DHW)*(cost_var_CHP+cost_fuel_CHP/eta_CHP_th)-sum(CHP*cb_CHP.*CHP_electricity_price)-sum(CHP_DHW*cb_CHP.*CHP_electricity_price)+sum(HP_cool.*(cost_var_HP_cool+cost_fuel_HP_cool./eta_HP_cool))+sum(HP_cool_2.*(cost_var_HP_cool_2+cost_fuel_HP_cool_2./eta_HP_cool_2))+sum(HP_cool_absorption.*(cost_var_HP_cool_absorption+cost_fuel_HP_cool_absorption./eta_HP_cool_absorption)))

        status = solve(m)


        ##### Result visualization ####

        println("Objective value: ", getobjectivevalue(m))

        Result_HOB=getvalue(HOB)+getvalue(HOB_DHW)
        Result_HOB_2=getvalue(HOB_2)+getvalue(HOB_2_DHW)

        Result_EH=getvalue(EH)+getvalue(EH_DHW)
        Result_EH_2=getvalue(EH_2)+getvalue(EH_2_DHW)

        Result_HP=getvalue(HP)+getvalue(HP_DHW)
        Result_HP_2=getvalue(HP_2)+getvalue(HP_2_DHW)
        Result_HP_absorption=getvalue(HP_absorption)+getvalue(HP_absorption_DHW)
        Result_CHP=getvalue(CHP)+getvalue(CHP_DHW)
        Result_ST=getvalue(ST)

        Result_SOC=getvalue(SOC)

        Result_SOC_DHW=getvalue(SOC_DHW)

        Result_HP_cool=getvalue(HP_cool)
        Result_HP_cool_2=getvalue(HP_cool_2)
        Result_HP_cool_absorption=getvalue(HP_cool_absorption)

        sort_Result_HOB=sort(Result_HOB, rev=true)
        sort_Result_HOB_2=sort(Result_HOB_2, rev=true)
        sort_Result_EH=sort(Result_EH, rev=true)
        sort_Result_EH_2=sort(Result_EH_2, rev=true)
        sort_Result_HP=sort(Result_HP, rev=true)
        sort_Result_HP_2=sort(Result_HP_2, rev=true)
        sort_Result_HP_absorption=sort(Result_HP_absorption, rev=true)
        sort_Result_CHP=sort(Result_CHP, rev=true)
        sort_Result_ST=sort(Result_ST, rev=true)
        sort_Result_HP_cool=sort(Result_HP_cool, rev=true)
        sort_Result_HP_cool_2=sort(Result_HP_cool_2, rev=true)
        sort_Result_HP_cool_absorption=sort(Result_HP_cool_absorption, rev=true)
        #sort_Result_HP_comb_heat_and_DHW=sort(Result_HP_comb_heat_and_DHW, rev=true)
        #sort_Result_HP_comb_cool=sort(Result_HP_comb_cool, rev=true)
        write_results(Result_HOB, Result_HOB_2, Result_EH, Result_EH_2, Result_HP, Result_HP_2,Result_HP_absorption, Result_CHP, Result_ST, DEM, Result_SOC, Result_HP_cool, Result_HP_cool_2,Result_HP_cool_absorption, output_folder, building_id)
    end


## Export results ##

    function write_results(Result_HOB, Result_HOB_2, Result_EH, Result_EH_2, Result_HP, Result_HP_2,Result_HP_absorption, Result_CHP, Result_ST, DEM, Result_SOC, Result_HP_cool, Result_HP_cool_2,Result_HP_cool_absorption, output_folder, building_id)
        writecsv(string(output_folder, "/Result_HOB_", building_id, ".csv"), Result_HOB)
        writecsv(string(output_folder, "/Result_HOB_2_", building_id, ".csv"), Result_HOB_2)

        writecsv(string(output_folder, "/Result_EH_", building_id, ".csv"), Result_EH)
        writecsv(string(output_folder, "/Result_EH_2_", building_id, ".csv"), Result_EH_2)

        writecsv(string(output_folder, "/Result_HP_", building_id, ".csv"), Result_HP)
        writecsv(string(output_folder, "/Result_HP_2_", building_id, ".csv"), Result_HP_2)

        writecsv(string(output_folder, "/Result_HP_absorption_" ,building_id, ".csv"), Result_HP_absorption)

        writecsv(string(output_folder, "/Result_CHP_", building_id, ".csv"), Result_CHP)

        writecsv(string(output_folder, "/Result_ST_", building_id, ".csv"), Result_ST)

        writecsv(string(output_folder, "/Result_DEM_", building_id, ".csv"), DEM)

        writecsv(string(output_folder, "/Result_SOC_", building_id, ".csv"), Result_SOC)

        writecsv(string(output_folder, "/Result_HP_cool_", building_id, ".csv"), Result_HP_cool)
        writecsv(string(output_folder, "/Result_HP_cool_2_", building_id, ".csv"), Result_HP_cool_2)

        writecsv(string(output_folder, "/Result_HP_cool_absorption" ,building_id, ".csv"), Result_HP_cool_absorption)

       # writecsv(string(output_folder, "/Result_HP_comb_heat_", building_id, ".csv"), Result_HP_comb_heat_and_DHW)
        #writecsv(string(output_folder, "/Result_HP_comb_cool_", building_id, ".csv"), Result_HP_comb_cool)
    end

    export individual_H_and_C

end