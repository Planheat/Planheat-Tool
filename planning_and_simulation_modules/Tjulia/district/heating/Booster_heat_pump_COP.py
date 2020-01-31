# -*- coding: utf-8 -*-
"""
Created on Wed May 23 13:17:20 2018

@author: hrvoj
"""
import numpy as np
import os.path


class Booster_COP:

    @staticmethod
    def generate_fileEta_forHeating(list_val, input_folder="", output_folder=""):
        #######  grop 1   heat pump 1  ########

        if input_folder == "":
            input_folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\Tjulia\\district\\heating"
        if output_folder == "":
            output_folder = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\Tjulia\\district\\heating\\Input"
        #Load meteorological data
        # dizionario = "in elaborazione da Daniele che lo rumina"  # dizionario fonte temperatura
        # tech = list_val[1]
        #if tech == self.district_function[9]:
        # if category_julia ==self.district_function[9]:
        #
        #     if list_val[2] in dizionario:
        #         T_source_I_1 = getVal(dizionario)
        #     else:
        #         T_source_I_1=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_I_1 = np.genfromtxt(input_folder + "\\T_source_I_1_HP.csv")
        except OSError:
            T_source_I_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../",
                                                                     "Outside_temperature.csv")))
        print("Booster_heat_pump_COP.generate_fileEta_forHeating() file dato\n",
              input_folder + "\\T_source_I_1_HP.csv",
              os.path.realpath(os.path.join(input_folder, "../../",
                                            "Outside_temperature.csv")),
              T_source_I_1)
        T_source_I_1=T_source_I_1+273.15
        T_sink = list_val[0]
        T_sink_I_1= T_sink + 273.15
        eta_Lorentz_I_1=0.6
        eta_HP_I_1=eta_Lorentz_I_1*(T_sink_I_1)/(T_sink_I_1-T_source_I_1)
        print("Booster_heat_pump_COP.generate_fileEta_forHeating() saved in\n",
              output_folder + "\\eta_HP_I_1.csv")
        np.savetxt(output_folder + "\\eta_HP_I_1.csv", eta_HP_I_1, delimiter=".")

            ####### heat pump 2  ########
            # if list_val[2] in dizionario:
            #     T_source_I_2 = getVal(Temp)
            # else:
            #     T_source_I_2=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_I_2 = np.genfromtxt(input_folder + "\\T_source_I_2_HP.csv")
        except OSError:
            T_source_I_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_I_2=T_source_I_2+273.15
        T_sink2 = list_val[2]
        T_sink_I_2=T_sink2+273.15
        eta_Lorentz_I_2 = 0.6
        eta_HP_I_2=eta_Lorentz_I_2*(T_sink_I_2)/(T_sink_I_2-T_source_I_2)
        np.savetxt(output_folder + "\\eta_HP_I_2.csv", eta_HP_I_2, delimiter=".")

            #######  heat pump 3  ########
        # if list_val[2] in dizionario:
        #     T_source_I_3 = getVal(Temp)
        # else:
        #     T_source_I_3=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_I_3 = np.genfromtxt(input_folder + "\\T_source_I_3_HP.csv")
        except OSError:
            T_source_I_3 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_I_3=T_source_I_3+273.15
        T_sink3 = list_val[4]
        T_sink_I_3=T_sink3 +273.15
        eta_Lorentz_I_3= 0.6
        eta_HP_I_3=eta_Lorentz_I_3*(T_sink_I_3)/(T_sink_I_3-T_source_I_3)
        np.savetxt(output_folder + "\\eta_HP_I_3.csv", eta_HP_I_3, delimiter=".")

        #if tech == self.district_function[10]: #grup 2
            #######heat pump 1  ########
            # if list_val[2] in dizionario:
            #     T_source_II_1 = getVal(Temp)
            # else:
            #     T_source_II_1=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_II_1 = np.genfromtxt(input_folder + "\\T_source_II_1_HP.csv")
        except OSError:
            T_source_II_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_II_1=T_source_II_1+273.15
        T_sink_II1 = list_val[6]
        T_sink_II_1= T_sink_II1 +273.15
        eta_Lorentz_II_1 = 0.6
        eta_HP_II_1=eta_Lorentz_II_1*(T_sink_II_1)/(T_sink_II_1-T_source_II_1)
        np.savetxt(output_folder + "\\eta_HP_II_1.csv", eta_HP_II_1, delimiter=".")

            ###heat pump 2  ########
            # if list_val[2] in dizionario:
            #     T_source_II_2 = getVal(Temp)
            # else:
            #     T_source_II_2=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_II_2 = np.genfromtxt(input_folder + "\\T_source_II_2_HP.csv")
        except OSError:
            T_source_II_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_II_2=T_source_II_2+273.15
        T_sinkII2 = list_val[8]
        T_sink_II_2= T_sinkII2 +273.15
        eta_Lorentz_II_2= 0.6
        eta_HP_II_2=eta_Lorentz_II_2*(T_sink_II_2)/(T_sink_II_2-T_source_II_2)
        np.savetxt(output_folder + "\\eta_HP_II_2.csv", eta_HP_II_2, delimiter=".")

            #### heat pump 3  ########
            # if list_val[2] in dizionario:
            #     T_source_II_3 = getVal(Temp)
            # else:
            #     T_source_II_3=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_II_3 = np.genfromtxt(input_folder + "\\T_source_II_3_HP.csv")
        except OSError:
            T_source_II_3 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_II_3=T_source_II_3+273.15
        Tsink2 = list_val[10]
        T_sink_II_3= Tsink2 +273.015
        eta_Lorentz_II_3= 0.6
        eta_HP_II_3=eta_Lorentz_II_3*(T_sink_II_3)/(T_sink_II_3-T_source_II_3)
        np.savetxt(output_folder + "\\eta_HP_II_3.csv", eta_HP_II_3, delimiter=".")

        # if category_julia == self.district_function[10]:
        #     ####### Temperature group III, heat pump 1  ########
        #     if list_val[2] in dizionario:
        #         T_source_III_1 = getVal(Temp)
        #     else:
        #         T_source_III_1=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_III_1 = np.genfromtxt(input_folder + "\\T_source_III_1_HP.csv")
        except OSError:
            T_source_III_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_III_1=T_source_III_1+273.15
        T_sinkIII3 = list_val[12]
        T_sink_III_1= T_sinkIII3 +273.15
        eta_Lorentz_III_1 = 0.6
        eta_HP_III_1=eta_Lorentz_III_1*(T_sink_III_1)/(T_sink_III_1-T_source_III_1)
        np.savetxt(output_folder + "\\eta_HP_III_1.csv", eta_HP_III_1, delimiter=".")

            # ####### heat pump 2  ########
            # if list_val[2] in dizionario:
            #     T_source_III_2 = getVal(Temp)
            # else:
            #     T_source_III_2=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_III_2 = np.genfromtxt(input_folder + "\\T_source_III_2_HP.csv")
        except OSError:
            T_source_III_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_III_2=T_source_III_2+273.15
        TsinkIII2 = list_val[14]
        T_sink_III_2= TsinkIII2 +273.15
        eta_Lorentz_III_2=0.6
        eta_HP_III_2=eta_Lorentz_III_2*(T_sink_III_2)/(T_sink_III_2-T_source_III_2)
        np.savetxt(output_folder + "\\eta_HP_III_2.csv", eta_HP_III_2, delimiter=".")

            # ####### heat pump 3  ########
            # if list_val[2] in dizionario:
            #     T_source_III_3= getVal(Temp)
            # else:
            #     T_source_III_3=np.genfromtxt(input_folder + "\\Outside_temperature.csv")
        try:
            T_source_III_3 = np.genfromtxt(input_folder + "\\T_source_III_3_HP.csv")
        except OSError:
            T_source_III_3 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_III_3=T_source_III_3+273.15
        TsinkIII3 = list_val[16]
        T_sink_III_3= TsinkIII3 +273.15
        eta_Lorentz_III_3= 0.6
        eta_HP_III_3=eta_Lorentz_III_3*(T_sink_III_3)/(T_sink_III_3-T_source_III_3)
        np.savetxt(output_folder + "\\eta_HP_III_3.csv", eta_HP_III_3, delimiter=".")

        # if category_julia == self.district_function[13]:
            ####### Seasonal  ########

            #Load meteorological data
        T_source_seasonal=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Outside_temperature.csv")))
        T_source_seasonal=T_source_seasonal+273.15

        # Heat sink temperature [°C]
        Tsesonal = list_val[18]
        T_sink_seasonal=Tsesonal+273.15
        #Lorenz efficiency
        eta_Lorentz_seasonal=0.6
        eta_HP_seasonal=eta_Lorentz_seasonal*(T_sink_seasonal)/(T_sink_seasonal-T_source_seasonal)
        np.savetxt(output_folder + "\\eta_HP_seasonal.csv", eta_HP_seasonal, delimiter=".")
