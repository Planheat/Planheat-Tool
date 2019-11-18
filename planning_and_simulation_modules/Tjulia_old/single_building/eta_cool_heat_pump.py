# -*- coding: utf-8 -*-
"""
Created on Wed May 23 13:17:20 2018

@author: hrvoj
"""
import numpy as np


def eta_cool_heat_pump(input_folder="", output_folder=""):
    # Heat pump 2, group 1 COP #

    # Load meteorological data
    T_source_1 = np.genfromtxt(input_folder + "\\Outside_temperature.csv")
    T_source_1 = T_source_1+273.15

    # Heat sink temperature [°C]
    T_sink_1 = 80+273.15

    # Lorenz efficiency
    eta_Lorentz_1 = 0.65

    eta_HP_1 = eta_Lorentz_1*T_sink_1/(T_sink_1-T_source_1)
    np.savetxt(output_folder + "\\eta_HP_cool.csv", eta_HP_1, delimiter=".")

    # Heat pump 2, group 1 COP #

    #Load meteorological data
    T_source_2 = np.genfromtxt(input_folder + "\\Outside_temperature.csv")
    T_source_2 = T_source_2 + 273.15

    # Heat sink temperature [°C]
    T_sink_2 = 80 + 273.15

    # Lorenz efficiency
    eta_Lorentz_2 = 0.55

    eta_HP_2 = eta_Lorentz_2*(T_sink_2)/(T_sink_2-T_source_2)

    np.savetxt(output_folder + "\\eta_HP_cool_2.csv", eta_HP_2, delimiter=".")


