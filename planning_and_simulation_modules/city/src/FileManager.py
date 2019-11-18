import os
import os.path
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit
import json
import shutil

from ... import master_planning_config


class FileManager:

    def __init__(self, work_folder=None):
        self.city_plugin_folder = os.path.abspath(os.path.join(os.path.realpath(__file__), "../"))
        self.work_folder = work_folder

    def import_and_fill_combo_box(self, combo_box, file_extension, folder=None):
        if folder is None:
            folder = self.work_folder
        combo_box.clear()
        combo_box_file_list = []
        if folder is not None:
            for filename in os.listdir(folder):
                if filename.endswith(file_extension):
                    combo_box_file_list.append(filename[0:-5])
        combo_box.addItems(combo_box_file_list)

    def import_and_fill_combo_box_from_DMM_planheat_mapping_wizard(self, combo_box, sector=None):
        if sector is None:
            print("FileManager.py, import_and_fill_combo_box_from_DMM_planheat_mapping_wizard().",
                  "sector is None")
            return
        if not (sector == "R" or sector == "T"):
            print("FileManager.py, import_and_fill_combo_box_from_DMM_planheat_mapping_wizard().",
                  "Undefined sector.")
            return
        if sector == "R":
            sector = "_R.json"
            sector_x = "_T.json"
        if sector == "T":
            sector = "_T.json"
            sector_x = "_R.json"
        combo_box.clear()
        DMM_wizard_folder = self.get_planheat_mapping_wizard_defaul_folder()
        project_wizard_folder = self.get_planheat_mapping_wizard_project_folder()
        combo_box_file_list = []
        black_list = []
        if project_wizard_folder is not None:
            pass
        if DMM_wizard_folder is not None:
            for filename in os.listdir(DMM_wizard_folder):
                check = False
                if filename.endswith(sector):
                    combo_box_file_list.append(filename[0:-7])
                    check = True
                if filename.endswith(sector_x):
                    check = True
                if not os.path.isfile(filename):
                    check = True
                if not check:
                    black_list.append(filename)
        if len(black_list) > 0:
            message = "Here the list of files that will be erased from your disk:"
            for file in black_list:
                message = message + "\n" + str(file)
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            main_text = "These files should not be here! They are going to be eliminated. Check these folders:"
            if DMM_wizard_folder is not None:
                main_text = main_text + "\n- " + str(DMM_wizard_folder)
            if project_wizard_folder is not None:
                main_text = main_text + "\n- " + str(project_wizard_folder)
            main_text = main_text + "\nand then continue."
            msgBox.setText(main_text)
            msgBox.setInformativeText(message)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec()
            self.delete_files_from_mapping_default_folders(black_list)
        combo_box.addItems(combo_box_file_list)

    def delete_files_from_mapping_default_folders(self, black_list=None):
        if black_list is None:
            return
        DMM_wizard_folder = self.get_planheat_mapping_wizard_defaul_folder()
        project_wizard_folder = self.get_planheat_mapping_wizard_project_folder()
        if DMM_wizard_folder is not None:
            for filename in os.listdir(DMM_wizard_folder):
                if filename in black_list:
                    try:
                        os.remove(os.path.join(DMM_wizard_folder, filename))
                    except:
                        print("FileManager.py, import_and_fill_combo_box_from_DMM_planheat_mapping_wizard().",
                              "Failed to delete file:", filename)
        if project_wizard_folder is not None:
            for filename in os.listdir(project_wizard_folder):
                if filename in black_list:
                    try:
                        os.remove(os.path.join(project_wizard_folder, filename))
                    except:
                        print("FileManager.py, import_and_fill_combo_box_from_DMM_planheat_mapping_wizard().",
                              "Failed to delete file:", filename)

    def get_planheat_mapping_wizard_defaul_folder_old(self):
        DMM_wizard_folder = os.path.abspath(os.path.join(self.city_plugin_folder, "../../../", "PlanheatMappingModule",
                                                         "PLANHEAT",
                                                         "planheatmappingwizard"))
        if not os.path.isdir(DMM_wizard_folder):
            print("FileManager.py, import_and_fill_combo_box_from_DMM_planheat_mapping_wizard().",
                  "Cannot find the Mapping Module plugin")
            DMM_wizard_folder = None
        else:
            DMM_wizard_folder = os.path.join(DMM_wizard_folder, "save_utils", "DefaultSaveFolder")
            if not os.path.isdir(DMM_wizard_folder):
                print("FileManager.py, import_and_fill_combo_box_from_DMM_planheat_mapping_wizard().",
                      "Cannot find the default save directory")
                DMM_wizard_folder = None
        return DMM_wizard_folder

    def get_planheat_mapping_wizard_defaul_folder(self):
        CMM_wizard_folder = os.path.join(master_planning_config.CURRENT_MAPPING_DIRECTORY, 
                                        master_planning_config.CMM_BASELINE_FOLDER, 
                                        master_planning_config.CMM_WIZARD_FOLDER)
        if not os.path.isdir(CMM_wizard_folder):
            CMM_wizard_folder = None
        return CMM_wizard_folder

    def get_planheat_mapping_wizard_project_folder(self):
        return self.work_folder

    def get_path_from_file_name(self, file, end_char=-7, search_folders=None):
        if search_folders is None:
            project_folder = self.get_planheat_mapping_wizard_project_folder()
            mapping_folder = self.get_planheat_mapping_wizard_defaul_folder()
            folders = [project_folder, mapping_folder]
        else:
            folders = search_folders
        for folder in folders:
            if folder is not None:
                for filename in os.listdir(folder):
                    if file == filename[0:end_char]:
                        return os.path.join(folder, filename)
        return None

    def load_json(self, file_path):
        try:
            with open(file_path) as f:
                data = json.load(f)
            return data
        except:
            print("FileManager.py, load_json(). Error loading file!")
            return {}

    def load(self, file):
        input_file = os.path.join(self.work_folder, file)
        if not os.path.isfile(input_file):
            print("SaveScenario.py, load(). Couldn't load", file, "File does not exist.")
            return
        return self.load_json(input_file)

    def get_filename_from_path(self, file_path):
        return os.path.split(file_path)[1]

    def check_file_name(self, text):
        if text == "":
            return False
        if "/" in text:
            return False
        if "\\" in text:
            return False
        if "?" in text:
            return False
        if "!" in text:
            return False
        if "%" in text:
            return False
        if "*" in text:
            return False
        if ":" in text:
            return False
        if "|" in text:
            return False
        if "\"" in text:
            return False
        if "<" in text:
            return False
        if ">" in text:
            return False
        if "." in text:
            return False
        if " " in text:
            return False
        return True

    def get_file_name_from_user(self, parent):
        valid = False
        space = "                                       "
        text = None
        while not valid:
            text, ok_pressed = QInputDialog.getText(None, "Enter file name",
                                                    "Enter file name to store plugin data" + space,
                                                    QLineEdit.Normal, "")
            try:
                if ok_pressed:
                    if not self.check_file_name(text):
                        message = "File names must not contain any of the following symbols: \n/\\?%*:|\"><. or whitespaces"
                        msgBox = QMessageBox()
                        msgBox.setText("Invalid file name.")
                        msgBox.setInformativeText(message)
                        msgBox.setStandardButtons(QMessageBox.Ok)
                        msgBox.setDefaultButton(QMessageBox.Ok)
                        msgBox.exec()
                        valid = False
                    else:
                        valid = True
                else:
                    valid = True
                    text = None
            except:
                valid = False
        return text

    def create_work_folder(self):
        if not os.path.isdir(self.work_folder):
            os.makedirs(self.work_folder, exist_ok=True)

    def remove_shapefiles(self, file):
        folder1 = os.path.join(self.work_folder, "Baseline", file)
        folder2 = os.path.join(self.work_folder, "Future", file)
        folder3 = os.path.join(self.work_folder, "Tools", file)
        self.remove_all_shape_file_from_name(folder1, "buildings")
        self.remove_all_shape_file_from_name(folder1, "streets")
        self.remove_all_shape_file_from_name(folder2, "buildings")
        self.remove_all_shape_file_from_name(folder3, "shape")
        self.remove_folder(folder1)
        self.remove_folder(folder2)
        self.remove_folder(folder3)

    def remove_all_shape_file_from_name(self, folder, name):
        try:
            os.remove(os.path.join(folder, name + ".shp"))
        except Exception as e:
            print("FileManager.py, remove_all_shape_file_from_name. Immpossible to delete file:", e)
        try:
            os.remove(os.path.join(folder, name + ".dbf"))
        except Exception as e:
            print("FileManager.py, remove_all_shape_file_from_name. Immpossible to delete file:", e)
        try:
            os.remove(os.path.join(folder, name + ".prj"))
        except Exception as e:
            print("FileManager.py, remove_all_shape_file_from_name. Immpossible to delete file:", e)
        try:
            os.remove(os.path.join(folder, name + ".qpj"))
        except Exception as e:
            print("FileManager.py, remove_all_shape_file_from_name. Immpossible to delete file:", e)
        try:
            os.remove(os.path.join(folder, name + ".shx"))
        except Exception as e:
            print("FileManager.py, remove_all_shape_file_from_name. Immpossible to delete file:", e)
        try:
            os.remove(os.path.join(folder, name + ".cpg"))
        except Exception as e:
            print("FileManager.py, remove_all_shape_file_from_name. Immpossible to delete file:", e)

    def remove_file_from_file_path(self, file_path):
        try:
            os.remove(os.path.join(file_path))
        except Exception as e:
            print("FileManager.py, remove_all_shape_file_from_name. Immpossible to delete file:", file_path, e)

    def remove_folder(self, folder):
        try:
            shutil.rmtree(folder)
        except Exception as e:
            print("FileManager.py, remove_folder. Immpossible to delete folder:", folder, e)

    def purge_unused_network_folder_and_shapefiles(self):
        network_to_save = []
        for filename in os.listdir(self.work_folder):
            if filename.endswith(".json"):
                data = self.load(filename)
                for n in data["networks"]["baseline"]["DHN"]:
                    network_to_save.append(n)
                for n in data["networks"]["baseline"]["DCN"]:
                    network_to_save.append(n)
                for n in data["networks"]["future"]["DHN"]:
                    network_to_save.append(n)
                for n in data["networks"]["future"]["DCN"]:
                    network_to_save.append(n)
        d = os.path.join(self.work_folder, "Baseline", "Networks", "DHN")
        if os.path.isdir(d):
            for existing_network in [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]:
                if existing_network not in network_to_save:
                    shutil.rmtree(os.path.join(d, existing_network))
        d = os.path.join(self.work_folder, "Baseline", "Networks", "DCN")
        if os.path.isdir(d):
            for existing_network in [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]:
                if existing_network not in network_to_save:
                    shutil.rmtree(os.path.join(d, existing_network))
        d = os.path.join(self.work_folder, "Future", "Networks", "DHN")
        if os.path.isdir(d):
            for existing_network in [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]:
                if existing_network not in network_to_save:
                    shutil.rmtree(os.path.join(d, existing_network))
        d = os.path.join(self.work_folder, "Future", "Networks", "DCN")
        if os.path.isdir(d):
            for existing_network in [o for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]:
                if existing_network not in network_to_save:
                    shutil.rmtree(os.path.join(d, existing_network))

    def move_folder(self, root_src_dir, root_target_dir):
        if not os.path.isdir(root_src_dir):
            print("FileManager.py, move_folder():", root_src_dir, "does not exist and it cannot be moved")
            return
        shutil.move(root_src_dir, root_target_dir)

    def copy_folder(self, source, target):
        if not os.path.isdir(source):
            print("FileManager.py, copy_folder():", source, "does not exist and it cannot be copied")
            return
        shutil.copytree(source, target)














