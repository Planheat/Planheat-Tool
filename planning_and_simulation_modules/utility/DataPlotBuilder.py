import os
import os.path
import traceback
from PyQt5.QtCore import QObject, pyqtSignal, QThread

class DataPlotBuilder(QObject):

    finished = pyqtSignal()
    calulation_done = pyqtSignal(dict)
    started = pyqtSignal()
    error = pyqtSignal(Exception)

    def __init__(self, work_folder):
        super().__init__()
        self.work_folder = work_folder
        self.h8760 = 8760
        self.HOB = "Result_HOB"
        self.HP_WASTE_HEAT = "Result_HP_waste_heat"
        self.CHP = "Result_CHP"
        self.HP = "Result_HP"
        self.ST = "Result_ST"
        self.SOC = "Result_SOC"
        self.DEM = "Result_DEM"
        self.DEM_cool = "Result_DEM_cool"
        self.DEM_DHW = "Result_DEM_DHW"
        self.HEX = "Result_HEX"
        self.EH = "Result_EH"
        self.HP_COOL = "Result_HP_cool"
        self.HP_COOL_ABSOPRTION = "Result_HP_cool_absorption"
        self.HP_absorption = "Result_HP_absorption"

    def run(self):
        try:
            self.started.emit()
            print("DataPlotBuilder.run() starts thread:", int(QThread.currentThread().currentThreadId()))
            PATH = os.path.join(self.work_folder, "single_building", "Results")
            if not os.path.isdir(PATH):
                return
            fileNames = [file for file in os.listdir(PATH) if '.csv' in file]
            data = self.build_data(PATH, self.buildings_file_to_data_key(fileNames))
            print("DataPlotBuilder.run() finished thread:", int(QThread.currentThread().currentThreadId()))
            self.calulation_done.emit(data)
            self.finished.emit()
        except Exception as e:
            traceback.print_exc()
            self.error.emit(e)
            empty_result = {}
            print("DataPlotBuilder.run() finished thread (with ERROS):",
                  int(QThread.currentThread().currentThreadId()))
            self.calulation_done.emit(empty_result)
            self.finished.emit()

    def build_data(self, folder, file_to_data_key):
        data = {}
        for file_name in file_to_data_key.keys():
            if os.path.isfile(os.path.join(folder, file_name)):
                data_key = file_to_data_key[file_name]
                if data_key not in data.keys():
                    data[data_key] = [0.0 for i in range(self.h8760)]
                with open(os.path.join(folder, file_name), "r") as fr:
                    content = fr.readlines()
                    if len(content) < self.h8760:
                        continue
                    for i in range(self.h8760):
                        try:
                            if not float(content[i]) == float(content[i]):
                                content[i] = 0.0
                        except ValueError:
                            content[i] = 0.0
                        data[data_key][i] += float(content[i])
        return data

    def buildings_file_to_data_key(self, files):
        file_to_data_key = {}
        for file in files:
            # prefix = file[0:-14]
            prefix = file[0:-4]
            if prefix.startswith(self.HOB):
                file_to_data_key[file] = self.HOB
            if prefix.startswith(self.HP):
                if prefix.startswith(self.HP_COOL):
                    file_to_data_key[file] = self.HP_COOL
                else:
                    file_to_data_key[file] = self.HP
            if prefix.startswith(self.CHP):
                file_to_data_key[file] = self.CHP
            if prefix.startswith(self.ST):
                file_to_data_key[file] = self.ST
            if prefix.startswith(self.SOC):
                file_to_data_key[file] = self.SOC
            if prefix.startswith(self.DEM):
                if prefix.startswith(self.DEM_cool):
                    file_to_data_key[file] = self.DEM_cool
                else:  # Heating (DEM) and DHW (DEM_DHW) count as DEM
                    file_to_data_key[file] = self.DEM
            if prefix.startswith(self.EH):
                file_to_data_key[file] = self.EH
        print(file_to_data_key)
        return file_to_data_key

