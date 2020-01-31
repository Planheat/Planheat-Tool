import os
import os.path
from .. import master_planning_config as mp_config

class ProjectFolderBuilder:

    def __init__(self):
        pass

    @staticmethod
    def run():
        planning_folder = mp_config.CURRENT_PLANNING_DIRECTORY

        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "Baseline", "Networks"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "Future", "Networks"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "KPIs", "Tjulia",
                                                                  "district", "heating", "Results"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "KPIs", "Tjulia",
                                                                  "district", "heating", "input"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "KPIs", "Tjulia",
                                                                  "district", "cooling", "Results"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "KPIs", "Tjulia",
                                                                  "district", "cooling", "input"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "KPIs", "Tjulia",
                                                                  "single_building", "Results"))
        ProjectFolderBuilder.check_and_create_folder(os.path.join(planning_folder, "District", "KPIs", "Tjulia",
                                                                  "single_building", "input"))

    @staticmethod
    def check_and_create_folder(folder):
        if not os.path.isdir(folder):
            try:
                os.makedirs(folder, exist_ok=True)
            except:
                pass
