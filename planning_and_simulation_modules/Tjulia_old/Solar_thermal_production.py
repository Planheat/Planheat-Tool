# -*- coding: utf-8 -*-
"""
Created on Wed May 23 13:17:20 2018

@author: hrvoj
"""
import numpy as np
import matplotlib.pyplot as plt



def generate_solar_thermal_forJulia(list_val, input_folder="", output_folder=""):

    ####### Solar thermal production calculation ########
    if list_val is None:
        list_val = [0, 1, 2, 70, 0.7, 3.1, 0.0005]

    # Only for testing
    if input_folder == "":
        input_folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\Tjulia\\single_building"
    if output_folder == "":
        output_folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\Tjulia\\single_building\\input"

    #Load meteorological data
    G_s=np.genfromtxt(input_folder + "\\Global_solar_irradiation.csv")
    G_s=G_s+0.00000001
    T_out=np.genfromtxt(input_folder + "\\Outside_temperature.csv")

    G_s_2=np.genfromtxt(input_folder + "\\Global_solar_irradiation_2.csv")
    G_s_2=G_s_2+0.00000001

    G_s_seasonal=np.genfromtxt(input_folder + "\\Global_solar_irradiation_seasonal.csv")
    G_s_seasonal=G_s_seasonal+0.00000001

    ## Input data for Solar thermal 1

    # Mean collector fluid temperature [°C]
    T_ST_mean = list_val[3]  # 70
    # Solar thermal collector optical efficiency [-]
    eta_ST_opt = list_val[4]  # 0.7
    # First order solar thermal collector loss coefficient
    a1_ST = list_val[5]  # 3.1
    # Second order solar thermal collector loss coefficient
    a2_ST = list_val[6]  # 0.0005

    eta_ST = eta_ST_opt-(a1_ST*(T_ST_mean-T_out))/G_s-a2_ST*(T_ST_mean-T_out)*(T_ST_mean-T_out)/G_s
    eta_ST[eta_ST < 0] = 0
    eta_ST[eta_ST > 1] = 0

    ST_specific=eta_ST*G_s
    plt.figure(1)
    plt.plot(ST_specific)

    np.savetxt(output_folder + "\\ST_specific_time.csv", ST_specific, delimiter=".")


    ## Input data for Solar thermal 2

    # Mean collector fluid temperature [°C]
    T_ST_mean_2 = list_val[3]  # 70
    # Solar thermal collector optical efficiency [-]
    eta_ST_opt_2 = list_val[4]  # 0.6
    # First order solar thermal collector loss coefficient
    a1_ST_2 = list_val[5]  # 3.1
    # Second order solar thermal collector loss coefficient
    a2_ST_2 = list_val[6]  # 0.0007
    eta_ST_2 = eta_ST_opt_2-(a1_ST_2*(T_ST_mean_2-T_out))/G_s_2-a2_ST_2*(T_ST_mean_2-T_out)*(T_ST_mean_2-T_out)/G_s_2

    eta_ST_2[eta_ST_2 < 0] = 0
    eta_ST_2[eta_ST_2 > 1] = 0
    ST_specific_2 = eta_ST_2*G_s_2

    # plt.figure(2)
    # plt.plot(ST_specific_2)
    # plt.savefig(output_folder, 'ST_specific.png')
    # np.savetxt(output_folder + "\\ST_specific_time_2.csv", ST_specific_2, delimiter=".")


    ## Input data for seasonal Solar thermal

    # Mean collector fluid temperature [°C]
    T_ST_mean_seasonal = list_val[3]  # 70
    # Solar thermal collector optical efficiency [-]
    eta_ST_opt_seasonal = list_val[4]  # 0.6
    # First order solar thermal collector loss coefficient
    a1_ST_seasonal = list_val[5]  # 3.1
    # Second order solar thermal collector loss coefficient
    a2_ST_seasonal = list_val[6]  # 0.0005

    eta_ST_seasonal=eta_ST_opt_seasonal-(a1_ST_seasonal*(T_ST_mean_seasonal-T_out))/G_s_seasonal-a2_ST_seasonal*(T_ST_mean_seasonal-T_out)*(T_ST_mean_seasonal-T_out)/G_s_seasonal

    eta_ST_seasonal[eta_ST_seasonal<0] = 0
    eta_ST_seasonal[eta_ST_seasonal>1] = 0
    ST_specific_seasonal = eta_ST_seasonal*G_s_seasonal

    np.savetxt(output_folder + "\\ST_specific_time_seasonal.csv", ST_specific_seasonal, delimiter=".")

