import json
import os
import os.path
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTableWidget, QListWidget
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from ..city.src.FileManager import FileManager
from .ZipManager import ZipManager


class SaveScenario(QtCore.QObject):

    saved_done = pyqtSignal()
    progressBarUpdate = pyqtSignal(int, int, bool)

    def __init__(self, folder=None, version=None):
        super(SaveScenario, self).__init__(parent=None)
        self.folder = ""
        self.data = {}
        self.version = version
        if folder is None:
            self.folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")
        else:
            try:
                os.path.exists(folder)
                self.folder = folder
            except TypeError:
                self.folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")
        self.file_manager = FileManager(work_folder=self.folder)
        self.zip_manager = ZipManager()

    def add_file(self, source_type, source, relative_path: str):
        self.zip_manager.add_file(source_type, source, relative_path)

    @staticmethod
    def make_directory(folder):
        try:
            os.makedirs(folder)
        except (FileExistsError, FileNotFoundError, TypeError) as e:
            if isinstance(e, TypeError) or isinstance(e, FileNotFoundError):
                return False
            else:
                pass
        return True

    def save(self, file):
        if not SaveScenario.make_directory(self.folder):
            print("ERROR! SaveScenario.py, save(). Impossible to create folder:", self.folder)
            return None
        if file is None:
            print("ERROR! SaveScenario.py, save(). output file is None")
            return None
        if not file.split(".")[-1] == "json":
            print("ERROR! SaveScenario.py, save(). output file must be of type .json")
            return None
        exists = True
        print("SaveScenario.save() zipfolde in", os.path.join(self.folder, "data"))
        SaveScenario.make_directory(os.path.join(self.folder, "data"))
        self.zip_manager.write(os.path.join(self.folder, "data", file[0:-5] + ".zip"))
        i = 0
        output_file = os.path.join(self.folder, file)
        while False:#exists:
            i += 1
            output_file = os.path.join(self.folder, file)
            exists = os.path.isfile(output_file)
            if exists:
                try:
                    version = int(file.split(".")[-2].split("_")[-1])
                except ValueError:
                    version = 0
                version += 1
                if version == 1:
                    file = file.split(".")[0] + "_" + str(version) + ".json"
                else:
                    version_string_index = file.rfind("_")
                    file = file[0:version_string_index] + "_" + str(version) + ".json"
            if i > 100:
                print("ERROR! SaveScenario.py, save(). Loop max iteration exceeded")
                return None

        with open(output_file, 'w') as outfile:
            json.dump(self.data, outfile, indent=4)

        self.saved_done.emit()

        return output_file

    def add_tree_widget_to_saved_data(self, widget, name=None):
        if not isinstance(widget, QTreeWidget):
            print("SaveScenario.py, add_tree_widget_to_saved_data(): widget is not a QTreeWidget")
            return
        if name is None:
            name = widget.objectName()
        self.data[name] = {}
        self.data[name]["widgetType"] = "QTreeWidget"
        for i in range(widget.topLevelItemCount()):
            top_level_item = widget.topLevelItem(i)
            item_key = "0_" + str(i)
            self.data[name][item_key] = {}
            self.dig_tree_item(top_level_item, self.data[name][item_key], 0)

    def dig_tree_item(self, item, dict_data, level):
        if not isinstance(item, QTreeWidgetItem):
            print("SaveScenario.py, dig_tree_item(): item is not a QTreeWidgetItem")
            return
        dict_data["data"] = [item.text(i) for i in range(item.columnCount())]
        data_list = SaveScenario.get_user_role_data_from_tree_item(item)
        if data_list is not None:
            dict_data["Qt.UserRole"] = data_list
        if item.childCount() == 0:
            return
        else:
            for i in range(item.childCount()):
                child_item = item.child(i)
                item_key = str(level+1) + "_" + str(i)
                dict_data[item_key] = {}
                self.dig_tree_item(child_item, dict_data[item_key], level+1)

    @staticmethod
    def get_user_role_data_from_tree_item(item):
        output_list = []
        for i in range(item.columnCount()):
            try:
                output_data = str(item.data(i, QtCore.Qt.UserRole))
            except (RuntimeError, MemoryError):
                output_data = ""
            output_list.append(output_data)
        for element in output_list:
            if not element == "":
                return output_list
        return None

    def add_table_widget_to_saved_data(self, widget, name=None):
        if not isinstance(widget, QTableWidget):
            print("SaveScenario.py, add_table_widget_to_saved_data(): widget is not a QTableWidget")
            return
        if name is None:
            name = widget.objectName()
        self.data[name] = {}
        self.data[name]["widgetType"] = "QTableWidget"
        horizontal_header_list = []
        vertical_header_list = []
        for i in range(widget.columnCount()):
            try:
                horizontal_header_list.append(widget.horizontalHeaderItem(i).text())
            except AttributeError:
                horizontal_header_list.append("")
        for j in range(widget.rowCount()):
            try:
                vertical_header_list.append(widget.verticalHeaderItem(j).text())
            except AttributeError:
                vertical_header_list.append("")
        for element in horizontal_header_list:
            if not element == "":
                self.data[name]["horizontalHeader"] = horizontal_header_list
                break
        else:
            self.data[name]["horizontalHeader"] = None
        for element in vertical_header_list:
            if not element == "":
                self.data[name]["verticalHeader"] = vertical_header_list
                break
        else:
            self.data[name]["verticalHeader"] = None
        for i in range(widget.rowCount()):
            self.data[name][i] = {}
            for j in range(widget.columnCount()):
                try:
                    element = widget.item(i, j).text()
                except AttributeError:
                    element = None
                self.data[name][i][j] = element
        self.data[name]["rowCount"] = widget.rowCount()
        self.data[name]["columnCount"] = widget.columnCount()

    def add_list_widget_to_saved_data(self, widget, name=None):
        if not isinstance(widget, QListWidget):
            print("SaveScenario.py, add_list_widget_to_saved_data(): widget is not a QListWidget")
            return
        if name is None:
            name = widget.objectName()
        self.data[name] = {}
        self.data[name]["widgetType"] = "QListWidget"
        self.data[name]["data"] = [widget.item(i).text() for i in range(widget.count())]
        self.data[name]["Qt.UserRole"] = [str(widget.item(i).data(QtCore.Qt.UserRole)) for i in range(widget.count())]



