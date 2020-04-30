#=
district_cooling:
- Julia version: 
- Author: qgis1
- Date: 2019-03-28
=#
module district_cooling
    using JuMP
    using Cbc

    using CSV
    using DelimitedFiles
    csv_sep = ','

    function district_cooling_simulation(input_folder, output_folder, tech_infos, network_id, print_function = print)
        m = Model(with_optimizer(Cbc.Optimizer, logLevel=1, seconds=600))

        ####### Load distributions #########

        DEM=readdlm(string(input_folder, "\\DEM_time.csv"), csv_sep)
        #DEM=DEM[4381:6570]

        Electricity_price=readdlm(string(input_folder, "\\Electricity_price_time.csv"), csv_sep)
        #Electricity_price=Electricity_price[4381:6570]

        Heat_exchanger_specific=readdlm(string(input_folder, "\\Heat_exchanger_specific_time.csv"), csv_sep)
        #Heat_exchanger_specific=Heat_exchanger_specific[4381:6570]

        Heat_exchanger_specific_cool=readdlm(string(input_folder, "\\Heat_exchanger_specific_time_cool.csv"), csv_sep)
        #Heat_exchanger_specific_cool=Heat_exchanger_specific_cool[4381:6570]

        eta_HP = readdlm(string(input_folder, "\\eta_HP_1.csv"), csv_sep)
        #eta_HP = eta_HP[4381:6570]
        eta_HP_2 = readdlm(string(input_folder, "\\eta_HP_2.csv"), csv_sep)
        #eta_HP_2 = eta_HP_2[4381:6570]
        eta_HP_3 = readdlm(string(input_folder, "\\eta_HP_3.csv"), csv_sep)
        #eta_HP_3 = eta_HP_3[4381:6570]

        eta_HP_waste_heat_1=readdlm(string(input_folder, "\\COP_heat_pump_temperature_group_1.csv"), csv_sep)
        #eta_HP_waste_heat_1=eta_HP_waste_heat_1[4381:6570]
        eta_HP_waste_heat_2=readdlm(string(input_folder, "\\COP_heat_pump_temperature_group_2.csv"), csv_sep)
        #eta_HP_waste_heat_2=eta_HP_waste_heat_2[4381:6570]
        eta_HP_waste_heat_3=readdlm(string(input_folder, "\\COP_heat_pump_temperature_group_3.csv"), csv_sep)
        #eta_HP_waste_heat_3=eta_HP_waste_heat_3[4381:6570]

        Available_waste_heat_heat_pump_1=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_1.csv"), csv_sep)
        #Available_waste_heat_heat_pump_1=Available_waste_heat_heat_pump_1[4381:6570]
        Available_waste_heat_heat_pump_2=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_2.csv"), csv_sep)
        #Available_waste_heat_heat_pump_2=Available_waste_heat_heat_pump_2[4381:6570]
        Available_waste_heat_heat_pump_3=readdlm(string(input_folder, "\\Waste_heat_heat_pump_available_temperature_group_3.csv"), csv_sep)
        #Available_waste_heat_heat_pump_3=Available_waste_heat_heat_pump_3[4381:6570]

        ####### Technology input data ########

        ## Heat only boiler ##

        # Installed capacity [MW]
        P_max_HOB = tech_infos["P_max_HOB"] #2
        # Technical minimum [MW]
        Tecnical_minimum_HOB= tech_infos["Tecnical_minimum_HOB"] #0.2
        P_min_HOB = Tecnical_minimum_HOB*P_max_HOB
        # Efficiency [-]
        eta_HOB = tech_infos["eta_HOB"] #0.8
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB= tech_infos["Percentage_ramp_up_down_HOB"] #0.5
        ramp_up_down_HOB = P_max_HOB*Percentage_ramp_up_down_HOB
        # Variable cost [EUR/MWh]
        cost_var_HOB = tech_infos["cost_var_HOB"] #5.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB = tech_infos["cost_fuel_HOB"] #10

        ## Heat only boiler 2 ##

        # Installed capacity [MW]
        P_max_HOB_2 = tech_infos["P_max_HOB_2"] #2
        # Technical minimum [MW]
        Tecnical_minimum_HOB_2= tech_infos["Tecnical_minimum_HOB_2"] #0.3
        P_min_HOB_2 = Tecnical_minimum_HOB_2*P_max_HOB_2
        # Efficiency [-]
        eta_HOB_2 = tech_infos["eta_HOB_2"] #0.8
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB_2= tech_infos["Percentage_ramp_up_down_HOB_2"] #0.5
        ramp_up_down_HOB_2 = P_max_HOB_2*Percentage_ramp_up_down_HOB_2
        # Variable cost [EUR/MWh]
        cost_var_HOB_2 = tech_infos["cost_var_HOB_2"] #5.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB_2 = tech_infos["cost_fuel_HOB_2"] #12.5

        ## Heat only boiler 3 ##

        # Installed capacity [MW]
        P_max_HOB_3 = tech_infos["P_max_HOB_3"] #2
        # Technical minimum [MW]
        Tecnical_minimum_HOB_3= tech_infos["Tecnical_minimum_HOB_3"] #0.2
        P_min_HOB_3 = Tecnical_minimum_HOB_3*P_max_HOB_3
        # Efficiency [-]
        eta_HOB_3 = tech_infos["eta_HOB_3"] #0.8
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HOB_3= tech_infos["Percentage_ramp_up_down_HOB_3"] #0.6
        ramp_up_down_HOB_3 = P_max_HOB_3*Percentage_ramp_up_down_HOB_3
        # Variable cost [EUR/MWh]
        cost_var_HOB_3 = tech_infos["cost_var_HOB_3"] #3.4
        # Fuel cost [EUR/MWh]
        cost_fuel_HOB_3 = tech_infos["cost_fuel_HOB_3"] #20

        ## Heat pump ##

        # Installed capacity [MW]
        P_max_HP = tech_infos["P_max_HP"] #2
        # Technical minimum [MW]
        Technical_minimum_HP= tech_infos["Technical_minimum_HP"] #0.2
        P_min_HP = Technical_minimum_HP*P_max_HP
        # Efficiency [-]
        eta_HP = eta_HP
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP= tech_infos["Percentage_ramp_up_down_HP"] #0.9
        ramp_up_down_HP = Percentage_ramp_up_down_HP*P_max_HP
        # Variable cost [EUR/MWh]
        cost_var_HP = tech_infos["cost_var_HP"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP = Electricity_price

        ## Heat pump 2 ##

        # Installed capacity [MW]
        P_max_HP_2 = tech_infos["P_max_HP_2"] #2
        # Technical minimum [MW]
        Technical_minimum_HP_2= tech_infos["Technical_minimum_HP_2"] #0.1
        P_min_HP_2 = Technical_minimum_HP_2*P_max_HP_2
        # Efficiency [-]
        eta_HP_2 = eta_HP_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_2= tech_infos["Percentage_ramp_up_down_HP_2"] #0.95
        ramp_up_down_HP_2 = Percentage_ramp_up_down_HP_2*P_max_HP_2
        # Variable cost [EUR/MWh]
        cost_var_HP_2 = tech_infos["cost_var_HP_2"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_2 = Electricity_price

        ## Heat pump 3 ##

        # Installed capacity [MW]
        P_max_HP_3 = tech_infos["P_max_HP_3"] #2
        # Technical minimum [MW]
        Technical_minimum_HP_3= tech_infos["Technical_minimum_HP_3"] #0.1
        P_min_HP_3 = Technical_minimum_HP_3*P_max_HP_3
        # Efficiency [-]
        eta_HP_3 = eta_HP_3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_3= tech_infos["Percentage_ramp_up_down_HP_3"] #0.95
        ramp_up_down_HP_3 = Percentage_ramp_up_down_HP_3*P_max_HP_3
        # Variable cost [EUR/MWh]
        cost_var_HP_3 = tech_infos["cost_var_HP_3"] #0.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_3 = Electricity_price

        ## Cogeneration ##

        # Installed capacity [MW]
        P_max_CHP = tech_infos["P_max_CHP"] #0
        # Technical minimum [MW]
        Technical_minimum_CHP= tech_infos["Technical_minimum_CHP"] #0.0
        P_min_CHP = Technical_minimum_CHP*P_max_CHP
        # Efficiency [-]
        eta_CHP_th = tech_infos["eta_CHP_th"] #0.65
        # Power-to-heat ratio [-]
        cb_CHP = tech_infos["cb_CHP"] #0.3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_CHP= tech_infos["Percentage_ramp_up_down_CHP"] #1
        ramp_up_down_CHP = Percentage_ramp_up_down_CHP*P_max_CHP
        # Variable cost [EUR/MWh]
        cost_var_CHP = tech_infos["cost_var_CHP"] #3.9
        # Fuel cost [EUR/MWh]
        cost_fuel_CHP = tech_infos["cost_fuel_CHP"] #20
        # Price paid to CHP for electrcity production
        CHP_electricity_price=Electricity_price

        ## Cogeneration 2 ##

        # Installed capacity [MW]
        P_max_CHP_2 = tech_infos["P_max_CHP_2"] #0
        # Technical minimum [MW]
        Technical_minimum_CHP_2= tech_infos["Technical_minimum_CHP_2"] #0.4
        P_min_CHP_2 = Technical_minimum_CHP_2*P_max_CHP_2
        # Efficiency [-]
        eta_CHP_th_2 = tech_infos["eta_CHP_th_2"] #0.65
        # Power-to-heat ratio [-]
        cb_CHP_2 = tech_infos["cb_CHP_2"] #0.3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_CHP_2= tech_infos["Percentage_ramp_up_down_CHP_2"] #0.2
        ramp_up_down_CHP_2 = Percentage_ramp_up_down_CHP_2*P_max_CHP_2
        # Variable cost [EUR/MWh]
        cost_var_CHP_2 = tech_infos["cost_var_CHP_2"] #3.9
        # Fuel cost [EUR/MWh]
        cost_fuel_CHP_2 = tech_infos["cost_fuel_CHP_2"] #15
        # Price paid to CHP for electrcity production
        CHP_electricity_price_2=Electricity_price

        ## Absorption Heat pump ##

        # Installed capacity [MW]
        P_max_HP_abs = tech_infos["P_max_HP_abs"] #9
        # Technical minimum [MW]
        Technical_minimum_HP_abs= tech_infos["Technical_minimum_HP_abs"] #0.1
        P_min_HP_abs = Technical_minimum_HP_abs*P_max_HP_abs
        # Efficiency [-]
        eta_HP_abs = tech_infos["eta_HP_abs"] #0.9
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_abs= tech_infos["Percentage_ramp_up_down_HP_abs"] #1
        ramp_up_down_HP_abs = Percentage_ramp_up_down_HP_abs*P_max_HP_abs
        # Variable cost [EUR/MWh]
        cost_var_HP_abs = tech_infos["cost_var_HP_abs"] #0.1

        ## Waste heat - heat exchangers ##

        # Installed capacity [MW]
        P_HEX_capacity = tech_infos["P_HEX_capacity"] #3
        P_max_HEX=P_HEX_capacity*Heat_exchanger_specific
        # Technical minimum [MW]
        P_min_HEX= tech_infos["P_min_HEX"] #0
        # Variable cost [EUR/MWh]
        cost_var_HEX = tech_infos["cost_var_HEX"] #0.25

        ## Waste cooling - heat exchangers ##

        # Installed capacity [MW]
        P_HEX_capacity_cool = tech_infos["P_HEX_capacity_cool"] #2
        P_max_HEX_cool=P_HEX_capacity_cool*Heat_exchanger_specific_cool
        # Technical minimum [MW]
        P_min_HEX_cool= tech_infos["P_min_HEX_cool"] #0
        # Variable cost [EUR/MWh]
        cost_var_HEX_cool = tech_infos["cost_var_HEX_cool"] #0.25

        ## Waste heat - heat pumps - temperature group 1 ##

        # Installed capacity [MW]
        P_max_HP_waste_heat_1 = tech_infos["P_max_HP_waste_heat_1"] #1
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_1 = tech_infos["Technical_minimum_HP_waste_heat_1"] #0.0
        P_min_HP_waste_heat_1 = Technical_minimum_HP_waste_heat_1*P_max_HP_waste_heat_1
        # Efficiency [-]
        eta_HP_waste_heat_1 = eta_HP_waste_heat_1
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_1= tech_infos["Percentage_ramp_up_down_HP_waste_heat_1"] #0.95
        ramp_up_down_HP_waste_heat_1 = Percentage_ramp_up_down_HP_waste_heat_1*P_max_HP_waste_heat_1
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_1 = tech_infos["cost_var_HP_waste_heat_1"] #0.7
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_1 = Electricity_price

        ## Waste heat - heat pumps - temperature group 2 ##

        # Installed capacity [MW]
        P_max_HP_waste_heat_2 = tech_infos["P_max_HP_waste_heat_2"] #1
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_2 = tech_infos["Technical_minimum_HP_waste_heat_2"] #0.1
        P_min_HP_waste_heat_2 = Technical_minimum_HP_waste_heat_2*P_max_HP_waste_heat_2
        # Efficiency [-]
        eta_HP_waste_heat_2 = eta_HP_waste_heat_2
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_2= tech_infos["Percentage_ramp_up_down_HP_waste_heat_2"] #0.95
        ramp_up_down_HP_waste_heat_2 = Percentage_ramp_up_down_HP_waste_heat_2*P_max_HP_waste_heat_2
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_2 = tech_infos["cost_var_HP_waste_heat_2"] #1.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_2 = Electricity_price

        ## Waste heat - heat pumps - temperature group 3 ##

        # Installed capacity [MW]
        P_max_HP_waste_heat_3 = tech_infos["P_max_HP_waste_heat_3"] #1
        # Technical minimum [MW]
        Technical_minimum_HP_waste_heat_3 = tech_infos["Technical_minimum_HP_waste_heat_3"] #0.1
        P_min_HP_waste_heat_3 = Technical_minimum_HP_waste_heat_3*P_max_HP_waste_heat_3
        # Efficiency [-]
        eta_HP_waste_heat_3 = eta_HP_waste_heat_3
        # Ramp-up-down speed [MW/h]
        Percentage_ramp_up_down_HP_waste_heat_3= tech_infos["Percentage_ramp_up_down_HP_waste_heat_3"] #0.95
        ramp_up_down_HP_waste_heat_3 = Percentage_ramp_up_down_HP_waste_heat_3*P_max_HP_waste_heat_3
        # Variable cost [EUR/MWh]
        cost_var_HP_waste_heat_3 = tech_infos["cost_var_HP_waste_heat_3"] #1.5
        # Fuel cost [EUR/MWh]
        # Choose between fixed electricity price or electricity market price
        cost_fuel_HP_waste_heat_3 = Electricity_price

        ## Thermal energy storage ##

        # Thermal energy storage size [MWh]
        TES_size = tech_infos["TES_size"] #200
        # Minimum percentage of state of charge of thermal energy storage [-]
        SOC_min = tech_infos["SOC_min"] #0.05
        # Thermal energy storage state of charge at the start/end of the year [-]
        TES_start_end = tech_infos["TES_start_end"] #0.05
        # Thermal storage charge/discharge capacity [MW]
        TES_charge_discharge_time = tech_infos["TES_charge_discharge_time"] #5
        TES_in_out_max = TES_size/TES_charge_discharge_time
        TES_loss = tech_infos["TES_loss"] #0.1/(24*7)

        ######## Constraints and variables ########

        ### Variables ###

        # Technologies' operation
        @variable(m, P_max_HOB >= HOB[1:length(DEM)] >= 0)
        @variable(m, P_max_HOB_2 >= HOB_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HOB_3 >= HOB_3[1:length(DEM)] >= 0)

        @variable(m, P_max_HP >= HP[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_2 >= HP_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_3 >= HP_3[1:length(DEM)] >= 0)

        @variable(m, P_max_CHP >= CHP[1:length(DEM)] >= 0)
        @variable(m, P_max_CHP_2 >= CHP_2[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_abs >= HP_abs[1:length(DEM)] >= 0)

        @variable(m, HEX[1:length(DEM)] >= 0)

        @variable(m, HEX_cool[1:length(DEM)] >= 0)

        @variable(m, P_max_HP_waste_heat_1 >= HP_waste_heat_1[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_2 >= HP_waste_heat_2[1:length(DEM)] >= 0)
        @variable(m, P_max_HP_waste_heat_3 >= HP_waste_heat_3[1:length(DEM)] >= 0)

        @variable(m, TES_in_out_max >=TES[1:length(DEM)]>= -TES_in_out_max)
        @variable(m, TES_size >= SOC[1:length(DEM)] >= TES_size*SOC_min)

        #@variable(m, maximum(DEM) >= Error[1:length(DEM)] >= 0)
        @variable(m, 0 >= Error[1:length(DEM)] >= 0)

        # Binary variables, on/off

        @variable(m, OnOffHOB[1:length(DEM)], Bin)
        @variable(m, OnOffHOB_2[1:length(DEM)], Bin)
        @variable(m, OnOffHOB_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP[1:length(DEM)], Bin)
        @variable(m, OnOffHP_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP_abs[1:length(DEM)], Bin)

        @variable(m, OnOffCHP[1:length(DEM)], Bin)
        @variable(m, OnOffCHP_2[1:length(DEM)], Bin)

        @variable(m, OnOffHP_waste_heat_1[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_2[1:length(DEM)], Bin)
        @variable(m, OnOffHP_waste_heat_3[1:length(DEM)], Bin)

        @variable(m, OnOffHP_waste_heat_seasonal[1:length(DEM)], Bin)

        ### Constraints ###

        # Supply + TES = DEM
        @constraint(m, HP+HP_2+HP_3+HEX_cool+HP_abs+HP_waste_heat_1+HP_waste_heat_2+HP_waste_heat_3 - TES + Error .== DEM)

        @constraint(m, HP_abs.==(HOB+HOB_2+HOB_3+CHP+CHP_2+HEX)*eta_HP_abs)

        # Thermal storage constraints
        t=2:(length(DEM)-1)
        @constraint(m, SOC[t]-SOC[t .- 1]-TES[t]+SOC[t]*TES_loss .== 0)
        @constraint(m, SOC[length(DEM)-1]+TES[length(DEM)] == TES_size*TES_start_end)
        @constraint(m, SOC[1]-TES[1] == TES_size*TES_start_end)
        @constraint(m, SOC[length(DEM)] == TES_size*TES_start_end)

        # Waste heat constraints - can't utilize more than available
        @constraint(m, HEX .<=P_max_HEX)
        @constraint(m, HEX_cool .<=P_max_HEX_cool)

        @constraint(m, HP_waste_heat_1 .<= Available_waste_heat_heat_pump_1)
        @constraint(m, HP_waste_heat_2 .<= Available_waste_heat_heat_pump_2)
        @constraint(m, HP_waste_heat_3 .<= Available_waste_heat_heat_pump_3)

        # OnOff constraints - technical minimum
        @constraint(m, OnOffHOB*P_min_HOB-HOB.<=0)
        @constraint(m, -OnOffHOB*P_max_HOB+HOB.<=0)
        @constraint(m, OnOffHOB_2*P_min_HOB_2-HOB_2.<=0)
        @constraint(m, -OnOffHOB_2*P_max_HOB_2+HOB_2.<=0)
        @constraint(m, OnOffHOB_3*P_min_HOB_3-HOB_3.<=0)
        @constraint(m, -OnOffHOB_3*P_max_HOB_3+HOB_3.<=0)

        @constraint(m, OnOffHP*P_min_HP-HP.<=0)
        @constraint(m, -OnOffHP*P_max_HP+HP.<=0)
        @constraint(m, OnOffHP_2*P_min_HP_2-HP_2.<=0)
        @constraint(m, -OnOffHP_2*P_max_HP_2+HP_2.<=0)
        @constraint(m, OnOffHP_3*P_min_HP_3-HP_3.<=0)
        @constraint(m, -OnOffHP_3*P_max_HP_3+HP_3.<=0)

        @constraint(m, OnOffHP_abs*P_min_HP_abs-HP_abs.<=0)
        @constraint(m, -OnOffHP_abs*P_max_HP_abs+HP_abs.<=0)

        @constraint(m, OnOffCHP*P_min_CHP-CHP.<=0)
        @constraint(m, -OnOffCHP*P_max_CHP+CHP.<=0)
        @constraint(m, OnOffCHP_2*P_min_CHP_2-CHP_2.<=0)
        @constraint(m, -OnOffCHP_2*P_max_CHP_2+CHP_2.<=0)

        @constraint(m, OnOffHP_waste_heat_1*P_min_HP_waste_heat_1-HP_waste_heat_1.<=0)
        @constraint(m, -OnOffHP_waste_heat_1*P_max_HP_waste_heat_1+HP_waste_heat_1.<=0)
        @constraint(m, OnOffHP_waste_heat_2*P_min_HP_waste_heat_2-HP_waste_heat_2.<=0)
        @constraint(m, -OnOffHP_waste_heat_2*P_max_HP_waste_heat_2+HP_waste_heat_2.<=0)
        @constraint(m, OnOffHP_waste_heat_3*P_min_HP_waste_heat_3-HP_waste_heat_3.<=0)
        @constraint(m, -OnOffHP_waste_heat_3*P_max_HP_waste_heat_3+HP_waste_heat_3.<=0)

        # Ramp-up-down constraint for each technology

        i=2:(length(DEM)-1)

        @constraint(m, HOB[i .- 1]-HOB[i].<=ramp_up_down_HOB*OnOffHOB[i]+(1 .- OnOffHOB[i])*P_min_HOB)
        @constraint(m, HOB[i]-HOB[i .- 1].<=ramp_up_down_HOB*OnOffHOB[i .- 1]+(1 .- OnOffHOB[i .- 1])*P_min_HOB)
        @constraint(m, HOB_2[i .- 1]-HOB_2[i].<=ramp_up_down_HOB_2*OnOffHOB_2[i]+(1 .- OnOffHOB_2[i])*P_min_HOB_2)
        @constraint(m, HOB_2[i]-HOB_2[i .- 1].<=ramp_up_down_HOB_2*OnOffHOB_2[i .- 1]+(1 .- OnOffHOB_2[i .- 1])*P_min_HOB_2)
        @constraint(m, HOB_3[i .- 1]-HOB_3[i].<=ramp_up_down_HOB_3*OnOffHOB_3[i]+(1 .- OnOffHOB_3[i])*P_min_HOB_3)
        @constraint(m, HOB_3[i]-HOB_3[i .- 1].<=ramp_up_down_HOB_3*OnOffHOB_3[i .- 1]+(1 .- OnOffHOB_3[i .- 1])*P_min_HOB_3)

        @constraint(m, HP[i .- 1]-HP[i].<=ramp_up_down_HP*OnOffHP[i]+(1 .- OnOffHP[i])*P_min_HP)
        @constraint(m, HP[i]-HP[i .- 1].<=ramp_up_down_HP*OnOffHP[i .- 1]+(1 .- OnOffHP[i .- 1])*P_min_HP)
        @constraint(m, HP_2[i .- 1]-HP_2[i].<=ramp_up_down_HP_2*OnOffHP_2[i]+(1 .- OnOffHP_2[i])*P_min_HP_2)
        @constraint(m, HP_2[i]-HP_2[i .- 1].<=ramp_up_down_HP_2*OnOffHP_2[i .- 1]+(1 .- OnOffHP_2[i .- 1])*P_min_HP_2)
        @constraint(m, HP_3[i .- 1]-HP_3[i].<=ramp_up_down_HP_3*OnOffHP_3[i]+(1 .- OnOffHP_3[i])*P_min_HP_3)
        @constraint(m, HP_3[i]-HP_3[i .- 1].<=ramp_up_down_HP_3*OnOffHP_3[i .- 1]+(1 .- OnOffHP_3[i .- 1])*P_min_HP_3)

        @constraint(m, HP_abs[i .- 1]-HP_abs[i].<=ramp_up_down_HP_abs*OnOffHP_abs[i]+(1 .- OnOffHP_abs[i])*P_min_HP_abs)
        @constraint(m, HP_abs[i]-HP_abs[i .- 1].<=ramp_up_down_HP_abs*OnOffHP_abs[i .- 1]+(1 .- OnOffHP_abs[i .- 1])*P_min_HP_abs)

        @constraint(m, CHP[i .- 1]-CHP[i].<=ramp_up_down_CHP*OnOffCHP[i]+(1 .- OnOffCHP[i])*P_min_CHP)
        @constraint(m, CHP[i]-CHP[i .- 1].<=ramp_up_down_CHP*OnOffCHP[i .- 1]+(1 .- OnOffCHP[i .- 1])*P_min_CHP)
        @constraint(m, CHP_2[i .- 1]-CHP_2[i].<=ramp_up_down_CHP_2*OnOffCHP_2[i]+(1 .- OnOffCHP_2[i])*P_min_CHP_2)
        @constraint(m, CHP_2[i]-CHP_2[i .- 1].<=ramp_up_down_CHP_2*OnOffCHP_2[i .- 1]+(1 .- OnOffCHP_2[i .- 1])*P_min_CHP_2)

        @constraint(m, HP_waste_heat_1[i .- 1]-HP_waste_heat_1[i].<=ramp_up_down_HP_waste_heat_1*OnOffHP_waste_heat_1[i]+(1 .- OnOffHP_waste_heat_1[i])*P_min_HP_waste_heat_1)
        @constraint(m, HP_waste_heat_1[i]-HP_waste_heat_1[i .- 1].<=ramp_up_down_HP_waste_heat_1*OnOffHP_waste_heat_1[i .- 1]+(1 .- OnOffHP_waste_heat_1[i .- 1])*P_min_HP_waste_heat_1)
        @constraint(m, HP_waste_heat_2[i .- 1]-HP_waste_heat_1[i].<=ramp_up_down_HP_waste_heat_2*OnOffHP_waste_heat_2[i]+(1 .- OnOffHP_waste_heat_2[i])*P_min_HP_waste_heat_2)
        @constraint(m, HP_waste_heat_2[i]-HP_waste_heat_2[i .- 1].<=ramp_up_down_HP_waste_heat_2*OnOffHP_waste_heat_2[i .- 1]+(1 .- OnOffHP_waste_heat_2[i .- 1])*P_min_HP_waste_heat_2)
        @constraint(m, HP_waste_heat_3[i .- 1]-HP_waste_heat_3[i].<=ramp_up_down_HP_waste_heat_3*OnOffHP_waste_heat_3[i]+(1 .- OnOffHP_waste_heat_3[i])*P_min_HP_waste_heat_3)
        @constraint(m, HP_waste_heat_3[i]-HP_waste_heat_3[i .- 1].<=ramp_up_down_HP_waste_heat_3*OnOffHP_waste_heat_3[i .- 1]+(1 .- OnOffHP_waste_heat_3[i .- 1])*P_min_HP_waste_heat_3)

        ###### Objective function ######

        # Minimize total running costs

        @objective(m,Min, sum(Error)*1e10
                          + sum(HOB)*(cost_var_HOB .+ cost_fuel_HOB/eta_HOB)
                          + sum(HOB_2)*(cost_var_HOB_2 .+ cost_fuel_HOB_2/eta_HOB_2)
                          + sum(HOB_3)*(cost_var_HOB_3 .+ cost_fuel_HOB_3/eta_HOB_3)
                          + sum(HP.*(cost_var_HP .+ cost_fuel_HP./eta_HP))
                          + sum(HP_2.*(cost_var_HP_2 .+ cost_fuel_HP_2./eta_HP_2))
                          + sum(HP_3.*(cost_var_HP_3 .+ cost_fuel_HP_3./eta_HP_3))
                          + sum(HP_abs)*cost_var_HP_abs
                          + sum(CHP)*(cost_var_CHP .+ cost_fuel_CHP/eta_CHP_th)
                          + sum(CHP_2)*(cost_var_CHP_2 .+ cost_fuel_CHP_2/eta_CHP_th_2)
                          + sum(HEX)*cost_var_HEX+sum(HEX_cool)*cost_var_HEX_cool
                          + sum(HP_waste_heat_1.*(cost_var_HP_waste_heat_1 .+ cost_fuel_HP_waste_heat_1./eta_HP_waste_heat_1))
                          + sum(HP_waste_heat_2.*(cost_var_HP_waste_heat_2 .+ cost_fuel_HP_waste_heat_2./eta_HP_waste_heat_2))
                          + sum(HP_waste_heat_3.*(cost_var_HP_waste_heat_3 .+ cost_fuel_HP_waste_heat_3./eta_HP_waste_heat_3))
                          - sum(CHP*cb_CHP.*CHP_electricity_price)
                          - sum(CHP_2*cb_CHP_2.*CHP_electricity_price_2))


        optimize!(m)
        status = termination_status(m)
        if primal_status(m) == MOI.NO_SOLUTION
            print_function("No solution found.")
            return
        end

        ##### Result visualization ####

        Result_HOB=value.(HOB)
        Result_HOB_2=value.(HOB_2)
        Result_HOB_3=value.(HOB_3)

        Result_HP=value.(HP)
        Result_HP_2=value.(HP_2)
        Result_HP_3=value.(HP_3)

        Result_HP_abs=value.(HP_abs)

        Result_CHP=value.(CHP)
        Result_CHP_2=value.(CHP_2)

        Result_HEX=value.(HEX)
        Result_HEX_cool=value.(HEX_cool)

        Result_HP_waste_heat_1=value.(HP_waste_heat_1)
        Result_HP_waste_heat_2=value.(HP_waste_heat_2)
        Result_HP_waste_heat_3=value.(HP_waste_heat_3)

        Result_SOC=value.(SOC)

        Result_Error=value.(Error)


        ## Export results ##

        writedlm(string(output_folder, "\\Result_HOB_", network_id, ".csv"), Result_HOB, csv_sep)
        writedlm(string(output_folder, "\\Result_HOB_2_", network_id, ".csv"), Result_HOB_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HOB_3_", network_id, ".csv"), Result_HOB_3, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_", network_id, ".csv"), Result_HP, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_2_", network_id, ".csv"), Result_HP_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_3_", network_id, ".csv"), Result_HP_3, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_abs_", network_id, ".csv"), Result_HP_abs, csv_sep)

        writedlm(string(output_folder, "\\Result_CHP_", network_id, ".csv"), Result_CHP, csv_sep)
        writedlm(string(output_folder, "\\Result_CHP_2_", network_id, ".csv"), Result_CHP_2, csv_sep)

        writedlm(string(output_folder , "\\Result_HEX_", network_id, ".csv"), Result_HEX, csv_sep)

        writedlm(string(output_folder, "\\Result_HEX_cool_", network_id, ".csv"), Result_HEX_cool, csv_sep)

        writedlm(string(output_folder, "\\Result_HP_waste_heat_1_", network_id, ".csv"), Result_HP_waste_heat_1, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_waste_heat_2_", network_id, ".csv"), Result_HP_waste_heat_2, csv_sep)
        writedlm(string(output_folder, "\\Result_HP_waste_heat_3_", network_id, ".csv"), Result_HP_waste_heat_3, csv_sep)

        writedlm(string(output_folder, "\\Result_DEM_", network_id, ".csv"), DEM, csv_sep)

        writedlm(string(output_folder, "\\Result_SOC_", network_id, ".csv"), Result_SOC, csv_sep)

        writedlm(string(output_folder, "\\Result_Error_", network_id, ".csv"), Result_Error, csv_sep)

    end
    export district_cooling_simulation
end

