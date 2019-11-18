# -*- coding: utf-8 -*-
"""
Created on Wed May 23 13:17:20 2018

@author: hrvoj
"""
import numpy as np
import os.path

def genera_file_etaHP_cool(val_list=None, input_folder="", output_folder=""):
    if val_list is None:
        return

    # Only for testing
    if input_folder == "":
        input_folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\Tjulia\\single_building"
    if output_folder == "":
        output_folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\Tjulia\\single_building\\input"

    ####### Heat pump 1, group 1 COP ########

    #Load meteorological data

    try:
        T_source_1 = np.genfromtxt(input_folder + "\\T_source_HP_cool.csv")
    except OSError:
        T_source_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../", "Outside_temperature.csv")))
    T_source_1=T_source_1+273.15
    # Heat sink temperature [°C]
    T_sink1 = val_list[0]
    T_sink_1 = T_sink1 + 273.15
    #Lorenz efficiency
    eta_Lorentz_1= 0.6
    print("eta_Lorentz_1", type(eta_Lorentz_1), eta_Lorentz_1, "T_sink_1", type(T_sink_1), T_sink_1, "T_source_1",
          type(T_source_1), T_source_1)
    eta_HP_1=eta_Lorentz_1*(T_sink_1)/(T_sink_1-T_source_1)
    np.savetxt(output_folder + "\\eta_HP_cool.csv", eta_HP_1, delimiter=".")


    ####### Heat pump 2, group 1 COP ########
    #Load meteorological data
    try:
        T_source_2 = np.genfromtxt(input_folder + "\\T_source_HP_cool_2.csv")
    except OSError:
        T_source_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../", "Outside_temperature.csv")))
    T_source_2=T_source_2+273.15
    # Heat sink temperature [°C]
    T_sink2 = val_list[2]
    T_sink_2= T_sink2 +273.15
    #Lorenz efficiency
    eta_Lorentz_2= 0.6
    eta_HP_2=eta_Lorentz_2*(T_sink_2)/(T_sink_2-T_source_2)

    np.savetxt(output_folder + "\\eta_HP_cool_2.csv", eta_HP_2, delimiter=".")
