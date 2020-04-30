import numpy as np
import os
import os.path

def fix_out_of_bound_numbers(arr, min_val, max_val):
        for i in range(len(arr)):
                if max_val is not None and arr[i] > max_val:
                        arr[i] = max_val
                if min_val is not None and arr[i] < min_val:
                        arr[i] = min_val


def generate_file_Waste_heat_pump_heating(list_val, input_folder, output_folder):
        print("generate_file_Waste_heat_pump_heating(), input_folder:", input_folder)
        print("generate_file_Waste_heat_pump_heating(), output_folder:", output_folder)


        Waste_heat_source_1=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../","Available_waste_heat_heat_pump_source_group_I_1.csv")))
        COP_1=np.genfromtxt(input_folder + "\\eta_HP_I_1.csv")

        print("Waste_heat_heat_pumps_heating.generate_file_Waste_heat_pump_heating(), COP_1 before", COP_1)
        fix_out_of_bound_numbers(COP_1, None, 10.0)
        print("Waste_heat_heat_pumps_heating.generate_file_Waste_heat_pump_heating(), COP_1 after", COP_1)

        print("Waste_heat_heat_pumps_heating.generate_file_Waste_heat_pump_heating() file file dato dato\n",
              os.path.realpath(
                      os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_I_1.csv")),
              input_folder + "\\eta_HP_I_1.csv",
              Waste_heat_source_1,
              COP_1)
        eta_1=list_val["HP_I_1"]
        Waste_heat_heat_pump_available_temperature_group_1=Waste_heat_source_1*(COP_1/(COP_1-1))*eta_1
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_1.csv", Waste_heat_heat_pump_available_temperature_group_1, delimiter=".")

        #Waste heat heat pump group 2

        Waste_heat_source_2=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_I_2.csv")))
        COP_2=np.genfromtxt(input_folder + "\\eta_HP_I_2.csv")
        fix_out_of_bound_numbers(COP_2, None, 10.0)
        eta_2=list_val["HP_I_2"]
        Waste_heat_heat_pump_available_temperature_group_2=Waste_heat_source_2*(COP_2/(COP_2-1))*eta_2
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_2.csv", Waste_heat_heat_pump_available_temperature_group_2, delimiter=".")

        #################################################

        #Waste heat heat pump group 3
        Waste_heat_source_3=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_I_3.csv")))
        COP_3=np.genfromtxt(input_folder + "\\eta_HP_I_3.csv")
        fix_out_of_bound_numbers(COP_3, None, 10.0)
        eta_3=list_val["HP_I_3"]
        Waste_heat_heat_pump_available_temperature_group_3=Waste_heat_source_3*(COP_3/(COP_3-1))*eta_3
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_3.csv", Waste_heat_heat_pump_available_temperature_group_3, delimiter=".")

        # Temperature group II
        # Heat pump 1
        Waste_heat_source_II_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../","Available_waste_heat_heat_pump_source_group_II_1.csv")))
        COP_II_1 = np.genfromtxt(input_folder + "\\eta_HP_II_1.csv")
        fix_out_of_bound_numbers(COP_II_1, None, 10.0)
        eta_II_1 = list_val["HP_II_1"]
        Waste_heat_heat_pump_available_temperature_group_II_1 = Waste_heat_source_II_1 * (
                        COP_II_1 / (COP_II_1 - 1)) * eta_II_1

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_II_1.csv",
                   Waste_heat_heat_pump_available_temperature_group_II_1, delimiter=".")

        # Heat pump 2
        Waste_heat_source_II_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_II_2.csv")))
        COP_II_2 = np.genfromtxt(input_folder + "\\eta_HP_II_2.csv")
        fix_out_of_bound_numbers(COP_II_2, None, 10.0)
        eta_II_2 = list_val["HP_II_2"]
        Waste_heat_heat_pump_available_temperature_group_II_2 = Waste_heat_source_II_2 * (
                        COP_II_2 / (COP_II_2 - 1)) * eta_II_2

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_II_2.csv",
                   Waste_heat_heat_pump_available_temperature_group_II_2, delimiter=".")

        # Heat pump 3

        Waste_heat_source_II_3 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_II_3.csv")))

        COP_II_3 = np.genfromtxt(input_folder + "\\eta_HP_II_3.csv")
        fix_out_of_bound_numbers(COP_II_3, None, 10.0)
        eta_II_3 = list_val["HP_II_3"]

        Waste_heat_heat_pump_available_temperature_group_II_3 = Waste_heat_source_II_3 * (
                        COP_II_3 / (COP_II_3 - 1)) * eta_II_3

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_II_3.csv",
                   Waste_heat_heat_pump_available_temperature_group_II_3, delimiter=".")

        ####################################################

        # Temperature group III

        # Heat pump 1

        Waste_heat_source_III_1 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_III_1.csv")))

        COP_III_1 = np.genfromtxt(input_folder + "\\eta_HP_III_1.csv")
        fix_out_of_bound_numbers(COP_III_1, None, 10.0)
        eta_III_1 = list_val["HP_III_1"]

        Waste_heat_heat_pump_available_temperature_group_III_1 = Waste_heat_source_III_1 * (
                        COP_III_1 / (COP_III_1 - 1)) * eta_III_1

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_III_1.csv",
                   Waste_heat_heat_pump_available_temperature_group_III_1, delimiter=".")

        # Heat pump 2

        Waste_heat_source_III_2 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_III_2.csv")))

        COP_III_2 = np.genfromtxt(input_folder + "\\eta_HP_III_2.csv")
        fix_out_of_bound_numbers(COP_III_2, None, 10.0)
        eta_III_2 = list_val["HP_III_2"]

        Waste_heat_heat_pump_available_temperature_group_III_2 = Waste_heat_source_III_2 * (
                        COP_III_2 / (COP_III_2 - 1)) * eta_III_2

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_III_2.csv",
                   Waste_heat_heat_pump_available_temperature_group_III_2, delimiter=".")

        # Heat pump 3

        Waste_heat_source_III_3 = np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_III_3.csv")))
        COP_III_3 = np.genfromtxt(input_folder + "\\eta_HP_III_3.csv")
        fix_out_of_bound_numbers(COP_III_3, None, 10.0)
        eta_III_3 = list_val["HP_III_3"]
        Waste_heat_heat_pump_available_temperature_group_III_3 = Waste_heat_source_III_3 * (
                        COP_III_3 / (COP_III_3 - 1)) * eta_III_3

        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_III_3.csv",
                   Waste_heat_heat_pump_available_temperature_group_III_3, delimiter=".")

        ####################################################

        #Waste heat heat pump group seasonal

        Waste_heat_source_seasonal=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_source_group_seasonal.csv")))
        COP_seasonal=np.genfromtxt(input_folder + "\\eta_HP_seasonal.csv")
        eta_seasonal= list_val["HP_waste_heat_seasonal"]
        Waste_heat_heat_pump_available_temperature_group_seasonal=Waste_heat_source_seasonal*(COP_seasonal/(COP_seasonal-1))*eta_seasonal
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_temperature_group_seasonal.csv", Waste_heat_heat_pump_available_temperature_group_seasonal, delimiter=".")

        #Waste heat heat pump absorption

        Waste_heat_source_absorption=np.genfromtxt(os.path.realpath(os.path.join(input_folder, "../../", "Available_waste_heat_heat_pump_absorption.csv")))
        COP_absorption=list_val["COP_absorption"]
        if COP_absorption == 0.0:
                print("Waste_heat_heat_pumps_heating.generate_file_Waste_heat_pump_heating(), COP_absorption is zero!")
                COP_absorption = 1.0
        Waste_heat_heat_pump_available_absorption=Waste_heat_source_absorption/COP_absorption
        np.savetxt(input_folder + "\\Waste_heat_heat_pump_available_absorption.csv", Waste_heat_heat_pump_available_absorption, delimiter=".")

