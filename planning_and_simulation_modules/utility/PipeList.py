from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from .Pipe import Pipe
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QListWidget, QInputDialog, QLineEdit
import traceback


class PipeList:

    check_attribute = "Status"
    check_attribute_value = 2
    storage_attribute = "diameter"
    precision = 0.1

    def __init__(self, layer=None):
        self.layer = layer
        self.pipes = []
        self.widget = None

        self.add_layer_features_to_list(self.layer)

    def check_layer(self):
        if self.layer is None:
            return False
        if self.layer.isValid():
            return True
        else:
            return False

    def set_layer(self, layer):
        if layer is None:
            return
        if layer.isValid():
            self.layer = layer
        else:
            return

    def feature_is_in_list(self, feature):
        for pipe in self.pipes:
            if pipe.feature.id() == feature.id():
                return True
        return False

    def attribute_check(self, pipe):
        return pipe.status == self.check_attribute_value

    def update_list(self, widget=None):
        if widget is None:
            widget = self.widget
        if not isinstance(widget, QListWidget):
            print("PipeList.py, update_list_widget(). Widget is not a QListWidget.")
            return
        if self.check_layer():
            print("PipeList.py, update_list(): self.layer.name() =", self.layer.name())

            for feature in self.layer.getFeatures():
                try:
                    if feature.attribute(self.check_attribute) == self.check_attribute_value:
                        if not self.feature_is_in_list(feature):
                            pipe = Pipe(feature, main_attribute="osmid")
                            pipe.status = feature.attribute(self.check_attribute)
                            self.pipes.append(pipe)
                            self.widget.addItem(pipe)
                except Exception as e:
                    print(traceback.print_tb(e.__traceback__))

            index_to_remove = []
            for i in range(len(self.pipes)):
                # print("PipeList.py, update_list():", self.pipes[i].feature.attribute(self.check_attribute))
                # print(self.pipes[i].feature.attribute(self.check_attribute))
                self.pipes[i].set_status(
                    self.layer.getFeature(self.pipes[i].feature.id()).attribute(self.check_attribute))
                if not self.attribute_check(self.pipes[i]):
                    index_to_remove.append(i)
            for i in range(len(index_to_remove)-1, -1, -1):
                self.delete_pipe(self.pipes[index_to_remove[i]])

            for pipe in self.pipes:

                # get updated diameter, if it fails do nothing
                try:
                    new_diameter = round(float(pipe.feature.attribute(self.storage_attribute)), 2)
                except Exception as e:
                    # print(traceback.print_tb(e.__traceback__))
                    new_diameter = None

                # check if old diameter is more or less the same
                if isinstance(new_diameter, float) and isinstance(pipe.diameter, float):
                    if abs(new_diameter-pipe.diameter) < self.precision:
                        continue
                    else:
                        pipe.set_diameter(new_diameter)

                # set new diameter if old does not exist
                if isinstance(new_diameter, float) and pipe.diameter is None:
                    pipe.set_diameter(new_diameter)

    def get_pipe_from_feature(self, feature):
        for pipe in self.pipes:
            if pipe.feature.id() == feature.id():
                return pipe

    def add_layer_features_to_list(self, layer=None):
        if layer is None:
            layer = self.layer
        if layer is None:
            return
        if not layer.isValid():
            return
        for feature in layer.getFeatures():
            try:
                if feature.attribute(self.check_attribute) == self.check_attribute_value:
                    pipe = Pipe(feature, main_attribute="osmid")
                    pipe.status = feature.attribute(self.check_attribute)
                    self.pipes.append(pipe)
            except Exception as e:
                print(traceback.print_tb(e.__traceback__))

    def update_list_widget(self, widget=None):
        if widget is None:
            widget = self.widget
        if not isinstance(widget, QListWidget):
            print("PipeList.py, update_list_widget(). Widget is not a QListWidget.")
            return
        widget.clear()
        for pipe in self.pipes:
            widget.addItem(pipe)

    def clear_list(self, widget=None):
        if widget is None:
            widget = self.widget
        if not isinstance(widget, QListWidget):
            print("PipeList.py, clear_list(). Widget is not a QListWidget.")
            return
        widget.clear()
        for pipe in self.pipes:
            del pipe

    def check_and_add_layer_storage_attribute(self, layer=None):
        if layer is None:
            layer = self.layer
        if layer is None:
            print("PipeList.py, check_and_add_layer_storage_attribute(). layer is None.")
            return
        if self.storage_attribute not in layer.fields().names():
            try:
                new_fields = QgsFields()
                new_fields.append(QgsField(self.storage_attribute, QVariant.Double, "double", 10, 2,
                                           "QgsField to store pipe diameter in cm"))
                layer.dataProvider().addAttributes(new_fields)
                layer.updateFields()
            except Exception as e:
                print("PipeList.py, check_and_add_layer_storage_attribute()", e)

    def set_pipes_diameter(self, widget=None):
        if not self.check_layer():
            print("PipeList.py, set_pipes_diameter(). self.check_layer() returns False.")
            return
        if not isinstance(widget, QListWidget):
            widget = self.widget
        if not isinstance(widget, QListWidget):
            print("PipeList.py, set_pipes_diameter(). Widget is not a QListWidget.", type(widget), widget)
            return

        if len(widget.selectedItems()) < 1:
            return

        valid = False
        space = "                                       "
        pipe_diameter = None
        while not valid:
            text, ok_pressed = QInputDialog.getText(widget,
                                                    "Specify pipes diameter", "Select the pipe diameter [cm]" + space,
                                                    QLineEdit.Normal, "")
            try:
                pipe_diameter = round(float(text), 2)
                valid = True
            except Exception as e:
                print(traceback.print_tb(e.__traceback__))

        if pipe_diameter is not None:
            self.check_and_add_layer_storage_attribute()
            for pipe in widget.selectedItems():
                pipe.set_diameter(pipe_diameter)
                feature = self.layer.getFeature(pipe.feature.id())
                pr = self.layer.dataProvider()
                pr.changeAttributeValues({feature.id(): {pr.fieldNameMap()[self.storage_attribute]: pipe_diameter}})
                self.layer.updateFeature(feature)
                pipe.auto_set_text()

    def delete_pipe(self, pipe, widget=None):
        if widget is None:
            widget = self.widget
        if not isinstance(widget, QListWidget):
            print("PipeList.py, delete_pipe(). Widget is not a QListWidget.")
            return
        try:
            widget.removeItemWidget(pipe)
            self.pipes.remove(pipe)
            return True
        except Exception as e:
            print(traceback.print_tb(e.__traceback__))
            return False

    def update_pipes(self, layer):
        self.set_layer(layer)
        if not self.check_layer():
            self.check_and_add_layer_storage_attribute(layer)
            self.clear_list()
            self.add_layer_features_to_list()
            self.update_list_widget()
        else:
            self.update_list()
