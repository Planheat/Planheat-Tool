from .... import master_planning_config
import os.path
import os
import shutil

from .ResultCalculator import ResultCalculator
from ...config import scenarioAttributes


class ResultWriter:

    def __init__(self):
        pass

    @staticmethod
    def export(gui, sim_gui):
        sector = scenarioAttributes.sector
        if sector == "residential":
            file_name = "results_CMM_wizard_R.csv"
        else:
            file_name = "results_CMM_wizard_T.csv"
        folder = os.path.join(master_planning_config.CURRENT_PLANNING_DIRECTORY, master_planning_config.FUTURE_FOLDER)
        mapping_folder = os.path.join(master_planning_config.CURRENT_MAPPING_DIRECTORY, "CMMF", "Wizard")
        file_path = os.path.join(mapping_folder, file_name)
        try:
            os.makedirs(folder, exist_ok=True)
            os.makedirs(mapping_folder, exist_ok=True)
        except:
            print("ERROR - export() aborted, check folders:", folder, mapping_folder)
            return
        result_calculator = ResultCalculator(gui, sim_gui)
        print("Writing results in:", file_path, "for sector:", sector)
        with open(file_path, "w") as file:
            file.write(
                sector + "_heating_hot_extracted_MWh_y_,[ {}]\n".format(result_calculator.get_heating_hot_extracted()))
            file.write(
                sector + "_heating_medium_extracted_MWh_y_,[ {}]\n".format(result_calculator.get_heating_medium_extracted()))
            file.write(
                sector + "_heating_low_extracted_MWh_y_,[ {}]\n".format(result_calculator.get_heating_low_extracted()))
            file.write(
                sector + "_heating_dhw_extracted_MWh_y_,[ {}]\n".format(result_calculator.get_heating_dhw_extracted()))
            file.write(
                sector + "_cooling_extracted_MWh_y_,[{}]\n".format(result_calculator.get_cooling_extracted()))
        ResultWriter.merge(mapping_folder, folder)

    @staticmethod
    def merge(mapping_folder, folder):
        try:
            file1 = os.path.join(mapping_folder, "results_CMM_wizard_R.csv")
            file2 = os.path.join(mapping_folder, "results_CMM_wizard_T.csv")
            if not os.path.isfile(file1) or not os.path.isfile(file2):
                return
            with open(file1, "r") as fp:
                data = fp.read()
            with open(file2, "r") as fp:
                data2 = fp.read()
            data += data2
            file_name = "results_CMM_wizard.csv"
            with open(os.path.join(mapping_folder, file_name), 'w') as fp:
                fp.write(data)
            os.remove(file1)
            os.remove(file2)
            shutil.copyfile(os.path.join(mapping_folder, file_name), os.path.join(folder, file_name))
        except:
            print("ResultWriter.merge() FAILED:", mapping_folder, folder)

