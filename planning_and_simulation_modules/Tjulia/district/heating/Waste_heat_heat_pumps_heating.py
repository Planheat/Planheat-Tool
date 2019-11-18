import numpy as np
import os
import os.path


def generate_file_Waste_heat_pump_heating(list_val, input_folder, output_folder):
        print("generate_file_Waste_heat_pump_heating(), input_folder:", input_folder)
        print("generate_file_Waste_heat_pump_heating(), output_folder:", output_folder)

        if list_val is None:
                list_val = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        if not len(list_val) == 10:
                list_val = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        Waste_heat_source_1=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../","Available_waste_heat_heat_pump_source_group_I_1.csv")))
        COP_1=np.genfromtxt(input_folder + "\\eta_HP_I_1.csv")
        eta_1=list_val[0]
        Waste_heat_heat_pump_available_temperature_group_1=Waste_heat_source_1*(COP_1/(COP_1-1))*eta_1
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_1.csv", Waste_heat_heat_pump_available_temperature_group_1, delimiter=".")

        #Waste heat heat pump group 2

        Waste_heat_source_2=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_I_2.csv")))
        COP_2=np.genfromtxt(input_folder + "\\eta_HP_I_2.csv")
        eta_2=list_val[1]
        Waste_heat_heat_pump_available_temperature_group_2=Waste_heat_source_2*(COP_2/(COP_2-1))*eta_2
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_2.csv", Waste_heat_heat_pump_available_temperature_group_2, delimiter=".")

        #################################################

        #Waste heat heat pump group 3
        Waste_heat_source_3=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_I_3.csv")))
        COP_3=np.genfromtxt(input_folder + "\\eta_HP_I_3.csv")
        eta_3=list_val[2]
        Waste_heat_heat_pump_available_temperature_group_3=Waste_heat_source_3*(COP_3/(COP_3-1))*eta_3
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_3.csv", Waste_heat_heat_pump_available_temperature_group_3, delimiter=".")

        # Temperature group II
        # Heat pump 1
        Waste_heat_source_II_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../","Available_waste_heat_heat_pump_source_group_II_1.csv")))
        COP_II_1 = np.genfromtxt(input_folder + "\\eta_HP_II_1.csv")
        eta_II_1 = list_val[3]
        Waste_heat_heat_pump_available_temperature_group_II_1 = Waste_heat_source_II_1 * (
                        COP_II_1 / (COP_II_1 - 1)) * eta_II_1

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_II_1.csv",
                   Waste_heat_heat_pump_available_temperature_group_II_1, delimiter=".")

        # Heat pump 2
        Waste_heat_source_II_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_II_2.csv")))
        COP_II_2 = np.genfromtxt(input_folder + "\\eta_HP_II_2.csv")
        eta_II_2 = list_val[4]
        Waste_heat_heat_pump_available_temperature_group_II_2 = Waste_heat_source_II_2 * (
                        COP_II_2 / (COP_II_2 - 1)) * eta_II_2

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_II_2.csv",
                   Waste_heat_heat_pump_available_temperature_group_II_2, delimiter=".")

        # Heat pump 3

        Waste_heat_source_II_3 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_II_3.csv")))

        COP_II_3 = np.genfromtxt(input_folder + "\\eta_HP_II_3.csv")

        eta_II_3 = list_val[5]

        Waste_heat_heat_pump_available_temperature_group_II_3 = Waste_heat_source_II_3 * (
                        COP_II_3 / (COP_II_3 - 1)) * eta_II_3

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_II_3.csv",
                   Waste_heat_heat_pump_available_temperature_group_II_3, delimiter=".")

        ####################################################

        # Temperature group III

        # Heat pump 1

        Waste_heat_source_III_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_III_1.csv")))

        COP_III_1 = np.genfromtxt(input_folder + "\\eta_HP_III_1.csv")

        eta_III_1 = list_val[6]

        Waste_heat_heat_pump_available_temperature_group_III_1 = Waste_heat_source_III_1 * (
                        COP_III_1 / (COP_III_1 - 1)) * eta_III_1

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_III_1.csv",
                   Waste_heat_heat_pump_available_temperature_group_III_1, delimiter=".")

        # Heat pump 2

        Waste_heat_source_III_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_III_2.csv")))

        COP_III_2 = np.genfromtxt(input_folder + "\\eta_HP_III_2.csv")

        eta_III_2 = list_val[7]

        Waste_heat_heat_pump_available_temperature_group_III_2 = Waste_heat_source_III_2 * (
                        COP_III_2 / (COP_III_2 - 1)) * eta_III_2

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_III_2.csv",
                   Waste_heat_heat_pump_available_temperature_group_III_2, delimiter=".")

        # Heat pump 3

        Waste_heat_source_III_3 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_III_3.csv")))
        COP_III_3 = np.genfromtxt(input_folder + "\\eta_HP_III_3.csv")
        eta_III_3 = list_val[8]
        Waste_heat_heat_pump_available_temperature_group_III_3 = Waste_heat_source_III_3 * (
                        COP_III_3 / (COP_III_3 - 1)) * eta_III_3

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_III_3.csv",
                   Waste_heat_heat_pump_available_temperature_group_III_3, delimiter=".")

        ####################################################

        #Waste heat heat pump group seasonal

        Waste_heat_source_seasonal=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_seasonal.csv")))
        COP_seasonal=np.genfromtxt(input_folder + "\\eta_HP_seasonal.csv")
        eta_seasonal= list_val[9]
        Waste_heat_heat_pump_available_temperature_group_seasonal=Waste_heat_source_seasonal*(COP_seasonal/(COP_seasonal-1))*eta_seasonal
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_seasonal.csv", Waste_heat_heat_pump_available_temperature_group_seasonal, delimiter=".")

        #Waste heat heat pump absorption

        Waste_heat_source_absorption=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_absorption.csv")))
        COP_absorption=10 #list_val[10]
        try:
                division = (COP_absorption/(COP_absorption-1))
        except ZeroDivisionError:
                division = 1
        Waste_heat_heat_pump_available_absorption=Waste_heat_source_absorption*division
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_absorption.csv", Waste_heat_heat_pump_available_absorption, delimiter=".")

