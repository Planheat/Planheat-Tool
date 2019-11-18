# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 11:04:32 2018

@author: hrvoj
"""

import csv
import os
import os.path
# Import pandas to manage data into DataFrames
import pandas
import numpy as np



class Transport_sector:

    def cacluation_transport(self,list):


        dr = os.path.dirname(os.path.realpath(__file__))
        output_folder = dr  # "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_and_simulation_modules\\Transport"
        input_folder = dr  # "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_and_simulation_modules\\Transport"

        #Average consumption of gasoline PV [L/100 km]
        cons_avg_gas = list[0]
        #Gasoline lower calorific value [kWh/L]
        cal_value_gas = list[2]
        #Average energy consumption of gasoline PV [kWh/km]
        en_cons_avg_gas = cons_avg_gas*cal_value_gas/100
        #Average CO2 emissions - gasoline cars [gCO2/km]
        CO2_avg_gas = list[1]

        #Average consumption of diesel PV [L/100 km]
        cons_avg_diesel = list[3]
        #Diesel lower calorific value [kWh/L]
        cal_value_diesel=list[4]
        #Average energy consumption of diesel PV [kWh/km]
        en_cons_avg_diesel=cons_avg_diesel*cal_value_diesel/100
        #Average CO2 emissions - diesel cars [gCO2/km]
        CO2_avg_diesel=list[5]

        #Number of personal vehicles
        N_PV=list[6]
        #Gasoline vehicles share
        share_gas= list[7]
        #Diesel vehicles share
        share_diesel= list[14]
        #Number of gasoline personal vehicles
        N_gas=N_PV*share_gas
        #Number of diesel personal vehicles
        N_diesel=N_PV*share_diesel

        #Estimated daily distance per PV [km/day]
        dist_day=list[8]
        #Estimated yearly distance per PV
        dist_year=dist_day*365
        #Total distance - gasoline PV
        total_distance_gas=dist_year*N_gas
        #Total distance - diesel PV
        total_distance_diesel=dist_year*N_diesel

        #Final energy consumption - gasoline [MWh]
        fin_en_gas=en_cons_avg_gas*total_distance_gas
        #Final energy consumption - diesel [MWh]
        fin_en_diesel=en_cons_avg_diesel*total_distance_diesel
        #CO2 emissions [tonnes CO2]
        total_CO2_fossil=(CO2_avg_gas*total_distance_gas+CO2_avg_diesel*total_distance_diesel)/1000000

        "Electrical vehicles"
        #Share of personal electrical vehicles
        EV_share=list[9]
        #Number of EVs
        N_EV=EV_share*N_PV
        #Specific EV energy consumption [Wh/km]
        en_cons_avg_EV = list[10]
        #Specific CO2 emissions of electricity sector [gCO2/kWh]
        power_sector_CO2=list[11]
        #Average battery capacity [kWh]
        bat_capacity=list[12]
        #Average charging/discharging capacity [kW]
        EV_capacity=list[13]
        #Total electricity consumption [MWh]
        fin_en_EV=en_cons_avg_EV*dist_year*N_EV/1000000
        #Total CO2 emissions
        total_CO2_EV=fin_en_EV*1000*power_sector_CO2/1000000

        " input basic distribution data  "

        hours = np.linspace(1, 8760, 8760)
        hours_24 = np.linspace(1, 24, 24)
        #iput ="C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_and_simulation_modules\\Transport\\transport_electrical_vehicles.txt"

        base_distribution = np.genfromtxt(input_folder + "\\transport_electrical_vehicles.txt")



        " weekend and seasonal characteristics input data"
        #weekend conusmption increase/decrease [-]
        weekend= list[15]
        #seasonal consumption increase/decrease [-]
        winter= list[16]
        spring= list[17]
        summer= list[18]
        autumn= list[19]

        " weekly distribution creation"

        week_1=np.tile(base_distribution,5)
        week_2=np.genfromtxt(input_folder + "\\transport_electrical_vehicles_weekend.txt")
        week_2=np.tile(week_2,2)
        week=np.concatenate((week_1,week_2),axis=0)


        " yearly distribution creation"

        year_1=np.tile(week*winter,11)
        year_2=np.tile(week*spring,13)
        year_3=np.tile(week*summer,13)
        year_4=np.tile(week*autumn,13)
        year_5=np.tile(week*winter,2)
        year_6=base_distribution*winter

        year =np.concatenate((year_1,year_2,year_3,year_4,year_5,year_6),axis=0)


        "yearly distribution update with weekly correction"
        year_update=np.concatenate((year_1,year_2,year_3,year_4,year_5),axis=0)
        year_update=np.reshape(year_update,(52,168))
        n=np.genfromtxt(input_folder + "\\transport_electrical_vehicles_weekly.txt")
        #n=np.ones(53)
        year_update=year_update*n[:52][:,np.newaxis]
        year_update=np.reshape(year_update,(8736,1))
        year_6_update=np.reshape(year_6,(24,1))*n[52]
        year_update=np.concatenate([year_update,year_6_update])



        "Hourly distribution of final consumption"
        #Total final energy consumption [MWh]
        Total_final=fin_en_EV

        year_update_sum=np.sum(year_update)

        Total_final_distribution=Total_final*(year_update/year_update_sum)



        np.savetxt(output_folder + "\\Result_Transport_electrical_vehicles.csv", Total_final_distribution, delimiter=".")
