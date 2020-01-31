import os
import os.path
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTableWidget, QListWidget, QTableWidgetItem
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from ..city.src.FileManager import FileManager
from ..layer_utils import load_file_as_layer
from .ZipManager import ZipManager
import traceback


class LoadScenario(QObject):
    progressBarUpdate = pyqtSignal(int, int, bool)

    def __init__(self, folder=None, version=None):
        QObject.__init__(self)
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
        self.file_loaded_name = None

    def fill_tre_widget_item(self, widget, name=None, TreeWidgetItem=QTreeWidgetItem):
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
                for i in range(len(user_role_data)):
                    if user_role_data[i] is not None or not user_role_data[i] == "":
                        new_tree_item.setData(i, QtCore.Qt.UserRole, QtCore.QVariant(user_role_data[i]))
            self.dig_dict_item_to_build_tree_widget(new_tree_item, data_dict[key], level+1)
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
                for i in range(len(user_role_data)):
                    if user_role_data[i] is not None or not user_role_data[i] == "":
                        new_tree_item.setData(i, QtCore.Qt.UserRole, QtCore.QVariant(user_role_data[i]))
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
                widget.item(i).setData(QtCore.Qt.UserRole, QtCore.QVariant(user_role_data[i]))

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
        widget.setRowCount(self.data[name]["rowCount"])
        widget.setColumnCount(self.data[name]["columnCount"])
        try:
            horizontal_header = self.data[name]["horizontalHeader"]
        except KeyError:
            horizontal_header = None
        if horizontal_header is not None:
            widget.setHorizontalHeaderLabels(horizontal_header)
        else:
            widget.horizontalHeader().hide()
        try:
            vertical_header = self.data[name]["verticalHeader"]
        except KeyError:
            vertical_header = None
        if vertical_header is not None:
            widget.setVerticalHeaderLabels(vertical_header)
        else:
            widget.verticalHeader().hide()
        i_limit = True
        j_limit = True
        i, j = [0, 0]
        while i_limit:
            try:
                data_dict = self.data[name][str(i)]
            except KeyError:
                i_limit = False
            while j_limit and i_limit:
                try:
                    widget.setItem(i, j, QTableWidgetItem(data_dict[str(j)]))
                    j += 1
                except KeyError:
                    j_limit = False
            i += 1
            j_limit = True
            j = 0
        self.make_horizontal_header_bold(widget)

    def make_horizontal_header_bold(self, widget):
        for i in range(widget.columnCount()):
            item = widget.horizontalHeaderItem(i)
            # font = QFont(widget.horizontalHeaderItem(i).font())
            font = widget.horizontalHeaderItem(i).font()
            font.setBold(True)
            item.setFont(font)

    def load(self, file):
        self.data = self.file_manager.load(file)
        self.file_loaded_name = file

    def load_layer_from_shapefile(self, file_path, layer_name=None):
        if file_path is None:
            return None
        if layer_name is None:
            layer_name = self.file_manager.get_filename_from_path(file_path)
            layer = load_file_as_layer(file_path, layer_name)
            layer.triggerRepaint()
            return layer
        return None

    def set_check_state(self, check_box, state):
        if state is None:
            return
        if check_box is None:
            return
        if state:
            check_box.setCheckState(QtCore.Qt.Checked)
        else:
            check_box.setCheckState(QtCore.Qt.Unchecked)

    def set_enabled_state(self, btn, state):
        if state is None:
            return
        if btn is None:
            return
        btn.setEnabled(state)

    def get_data(self, key, dict_data=None, default=None):
        if dict_data is None:
            dict_data = self.data
        try:
            return dict_data[str(key)]
        except KeyError:
            return default

    def fill_double_spin_box(self, double_spin_box, value):
        if value is None:
            return
        if double_spin_box is None:
            return
        try:
            value = float(value)
        except ValueError:
            return
        double_spin_box.setValue(value)

    def set_radioButton_state(self, radioButton, state):
        if state is None:
            return
        if radioButton is None:
            return
        radioButton.setChecked(state)

    def get_object_from_zip(self, source):
        try:
            zip_file_path = os.path.join(self.file_manager.work_folder, "data", self.file_loaded_name[0:-5] + ".zip")
            result_object = {}
            if os.path.isfile(zip_file_path):
                # print("LoadScenario.get_object_from_zip(). parameters (before)", zip_file_path,
                #       self.zip_manager.OBJECT,
                #       self.get_data("zipPath." + source, self.data),
                #       result_object)
                result_object = self.zip_manager.extract(zip_file_path,
                                                         self.zip_manager.OBJECT,
                                                         self.get_data("zipPath." + source, self.data),
                                                         result_object)
                # print("LoadScenario.get_object_from_zip(). parameters (after)", zip_file_path,
                #       self.zip_manager.OBJECT,
                #       self.get_data("zipPath." + source, self.data),
                #       result_object)
                return result_object
            return {}
        except Exception:
            traceback.print_exc()
            return None

    def extract_folder_from_zip(self, zip_file_path, rel_folder_path, destination_path):
        return self.zip_manager.extract(zip_file_path, self.zip_manager.FOLDER, rel_folder_path, destination_path,
                                        trunc_base_path=2)

    def version_check(self, version_to_check):
        if version_to_check is None or self.version is None:
            return False
        else:
            if not version_to_check == self.version:
                return False
        return True
