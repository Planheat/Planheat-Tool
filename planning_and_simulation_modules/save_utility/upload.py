import json
import os
import os.path
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTableWidget, QListWidget
from PyQt5 import QtCore

class Upload:


    def upload_file_json(self):
        lista_file=[]
        PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")
        fileNames = os.listdir(PATH)
        #fileNames = [file for file in fileNames if '.json' in file]

        for name in fileNames:
            if name.endswith('.json'):
               lista_file.append(name)

        print(lista_file)

        # with open(lista_file[4]) as json_file:
        #     data = json.load(json_file)
        #     for p in data:
        #         print(p)

