import json
import os
import os.path
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTableWidget, QListWidget
from PyQt5 import QtCore


class SaveScenario:

    folder = ""
    data = {}

    def __init__(self, folder=None):
        self.data = {}
        if folder is None:
            self.folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")
        else:
            try:
                os.path.exists(folder)
                self.folder = folder
            except TypeError:
                self.folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DefaultSaveFolder")

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

    def save(self, file, exist_ok=True):
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
        i = 0
        output_file = os.path.join(self.folder, file)
        while exists and exist_ok:
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

        return output_file

    def load(self, file):
        input_file = os.path.join(self.folder, file)
        if not os.path.isfile(input_file):
            print("SaveScenario.py, load(). Couldn't load", file, "File does not exist.")
            return
        with open(input_file) as json_file:
            self.data = json.load(json_file)

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

    def fill_tre_widget_item(self, widget, name=None):
        if name is None:
            name = widget.objectName()
        if name not in [key for key in self.data.keys()]:
            print("SaveScenario.py, fill_tre_widget_item(). Error: widget item not found.")
            return
        if not self.data[name]["widgetType"] == "QTreeWidget":
            print("SaveScenario.py, fill_tre_widget_item(). Error: widget is not QTreeWidget.")
            return
        widget.clear()
        level = 0
        item = 0
        look_for = True
        data_dict = self.data[name]
        while look_for:
            key = str(level) + "_" + str(item)
            try:
                data = data_dict[key]["data"]
            except KeyError:
                look_for = False
                continue
            try:
                user_role_data = data_dict[key]["Qt.UserRole"]
            except KeyError:
                user_role_data = None
            new_tree_item = QTreeWidgetItem(widget, data)
            if user_role_data is not None:
                for item_user_role_data in user_role_data:
                    if item_user_role_data is not None or not item_user_role_data == "":
                        new_tree_item.setData(QtCore.Qt.UserRole, QtCore.QVariant(item_user_role_data))
            self.dig_dict_item_to_build_tree_widget(new_tree_item, data_dict[key], level)
            item += 1

    def dig_dict_item_to_build_tree_widget(self, old_tree_item, data_dict, level):
        item = 0
        look_for = True
        while look_for:
            key = str(level) + "_" + str(item)
            try:
                data = data_dict[key]["data"]
            except KeyError:
                look_for = False
                continue
            try:
                user_role_data = data_dict[key]["Qt.UserRole"]
            except KeyError:
                user_role_data = None
            new_tree_item = QTreeWidgetItem(old_tree_item, data)
            if user_role_data is not None:
                for item_user_role_data in user_role_data:
                    if item_user_role_data is not None or not item_user_role_data == "":
                        new_tree_item.setData(QtCore.Qt.UserRole, QtCore.QVariant(item_user_role_data))
            self.dig_dict_item_to_build_tree_widget(new_tree_item, data_dict[key], level+1)
            item += 1

    def fill_list_widget_item(self, widget, name=None):
        if name is None:
            name = widget.objectName()
        if name not in [key for key in self.data.keys()]:
            print("SaveScenario.py, fill_list_widget_item(). Error: widget item not found.")
            return
        if not self.data[name]["widgetType"] == "QListWidget":
            print("SaveScenario.py, fill_list_widget_item(). Error: widget is not QTreeWidget.")
            return
        widget.clear()
        try:
            widget.addItems(self.data[name]["data"])
        except KeyError:
            print("SaveScenario.py, fill_list_widget_item(). Data not found.")
        try:
            user_role_data = self.data[name]["Qt.UserRole"]
        except KeyError:
            user_role_data = None
        if user_role_data is not None:
            for i in range(widget.count()):
                widget.item(i).setData(QtCore.Qt.UserRole, QtCore.QVariant(user_role_data(i)))

    def fill_table_widget_item(self, widget, name=None):
        if name is None:
            name = widget.objectName()
        if name not in [key for key in self.data.keys()]:
            print("SaveScenario.py, fill_table_widget_item(). Error: widget item not found.")
            return
        if not self.data[name]["widgetType"] == "QTableWidget":
            print("SaveScenario.py, fill_table_widget_item(). Error: widget is not QTreeWidget.")
            return
        widget.clear()

