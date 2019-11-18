import os.path
from PyQt5.QtWidgets import QMessageBox
import configparser


def plugin_init_files_check(folder, init_config_file='config\\init_config.ini'):
    if not os.path.exists(folder):
        QMessageBox.warning(None, "Error", "Directory " + folder + " does not exist. Input of files aborted.")
        return False
    path = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(os.path.dirname(path), init_config_file)
    if not os.path.exists(config_file_path):
        QMessageBox.warning(None, "Error", "Tried to open file: " + config_file_path + ". File does not exist. Import aborted.")
        return False
    config = configparser.ConfigParser()
    try:
        config.read(config_file_path)
    except:
        QMessageBox.error(None, "Error", "Could not open the configuration file.")
        return False
    return_boolean = True
    if not os.listdir(folder):
        return_boolean = False
    missing_files = "The following files could not be found in folder: " + folder + ":"
    for section in config.sections():
        for key in config[section]:
            file_found_flag = False
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file == config[section][key]:
                        file_found_flag = True
                        break
                if file_found_flag:
                    break
            if not file_found_flag:
                return_boolean = False
                missing_files = missing_files + "\n - " + config[section][key]
    if not return_boolean:
        QMessageBox.warning(None, "Warning", missing_files)
    return return_boolean


def is_file_in_init_config(file, init_config_file='config\\init_config.ini'):
    path = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(os.path.dirname(path), init_config_file)
    if not os.path.exists(config_file_path):
        QMessageBox.warning(None, "Error", "Tried to open file: " + config_file_path + ". File does not exist. Import aborted.")
        return False
    config = configparser.ConfigParser()
    try:
        config.read(config_file_path)
    except:
        QMessageBox.error(None, "Error", "Could not open the configuration file.")
        return False
    for section in config.sections():
        for key in config[section]:
            if file == config[section][key]:
                return True
    return False
