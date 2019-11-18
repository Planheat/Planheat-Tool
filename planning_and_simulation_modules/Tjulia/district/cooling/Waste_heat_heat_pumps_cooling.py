# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 16:57:33 2018

@author: hrvoj
"""

import numpy as np

def generate_file_Waste_heat_pump_cooling(list_val, input_folder, output_folder):
    #Waste heat heat pump group 1
    if list_val is None:
        return

    Waste_heat_source_1 = np.genfromtxt(input_folder + "\\Available_waste_heat_heat_pump_source_group_1.csv")
    COP_1 = np.genfromtxt(input_folder + "\\COP_heat_pump_temperature_group_1.csv")
    eta_1 = list_val[5]
    Waste_heat_heat_pump_available_temperature_group_1 = Waste_heat_source_1 * (COP_1 / (COP_1 - 1)) * eta_1
    np.savetxt(output_folder + "\\Waste_heat_heat_pump_available_temperature_group_1.csv",
               Waste_heat_heat_pump_available_temperature_group_1, delimiter=".")

    # Waste heat heat pump group 2

    Waste_heat_source_2 = np.genfromtxt(input_folder + "\\Available_waste_heat_heat_pump_source_group_2.csv")
    COP_2 = np.genfromtxt(input_folder + "\\COP_heat_pump_temperature_group_2.csv")
    eta_2 = list_val[5]
    Waste_heat_heat_pump_available_temperature_group_2 = Waste_heat_source_2 * (COP_2 / (COP_2 - 1)) * eta_2
    np.savetxt(output_folder + "\\Waste_heat_heat_pump_available_temperature_group_2.csv",
               Waste_heat_heat_pump_available_temperature_group_2, delimiter=".")

    # Waste heat heat pump group 3
    Waste_heat_source_3 = np.genfromtxt(input_folder + "\\Available_waste_heat_heat_pump_source_group_3.csv")
    COP_3 = np.genfromtxt(input_folder + "\\COP_heat_pump_temperature_group_3.csv")
    eta_3 = list_val[5]
    Waste_heat_heat_pump_available_temperature_group_3 = Waste_heat_source_3 * (COP_3 / (COP_3 - 1)) * eta_3
    np.savetxt(output_folder + "\\Waste_heat_heat_pump_available_temperature_group_3.csv",
               Waste_heat_heat_pump_available_temperature_group_3, delimiter=".")
