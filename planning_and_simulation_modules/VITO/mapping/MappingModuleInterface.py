from ... import master_planning_config
import os.path
import traceback


class MappingModuleInterface:

    def __init__(self):
        self.mapping_folder = os.path.join(master_planning_config.CURRENT_MAPPING_DIRECTORY)

    def get_baseline_year(self):
        return MappingModuleInterface.find_number_in_file(self.get_DMM_result_option_path(),
                                                          "Baseline Scenario Year", ":", 1)

    def get_future_year(self):
        return MappingModuleInterface.find_number_in_file(self.get_DMM_result_option_path(),
                                                          "Future Scenario Year", ":", 1)

    def get_DMM_result_option_path(self):
        try:
            return os.path.join(self.mapping_folder, "DMM", "DMM_result_options.txt")
        except Exception:
            return None

    @staticmethod
    def find_number_in_file(file_path, description, separator, position):
        try:
            if not os.path.isfile(file_path):
                return None
        except Exception:
            return None
        with open(file_path, "r") as f:
            line = True
            while line:
                line = f.readline()
                if description in line:
                    try:
                        return int(line.split(separator)[position])
                    except Exception:
                        pass
        return None

