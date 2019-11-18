"""This file defines methods to serialize DMM dialog inputs. There are two ways to serialize the DMM:
        * Incrementally: only strore the simple inputs
        * Fully: reset all the outputs using the native serialization method from the DMM
"""
import os
import pickle
from .src.pluginControl import loadScenario
from .. import master_mapping_config as config


class SimpleSerializedElement:
    """Represent a simple Qt element with its value getter and setter. Getter should be called without argument.
    Setter should be called with only one argument."""
    def __init__(self, elt_str, getter_str, setter_str):
        self.elt_str = elt_str
        self.getter_str = getter_str
        self.setter_str = setter_str
        self.value = None

    def store_value(self, dlg):
        elt = getattr(dlg, self.elt_str)
        self.value = getattr(elt, self.getter_str)()

    def deserialize_value(self, dlg):
        """Deserialize the value into the given dialog. If the element doesn't exists anymore in the dialog, nothing is
         done."""
        if self.elt_str in dir(dlg):
            elt = getattr(dlg, self.elt_str)
            if self.setter_str in dir(elt):
                getattr(elt, self.setter_str)(self.get_value())

    def get_value(self):
        return self.value


class SimpleProjectPathSerializedElement(SimpleSerializedElement):
    """Represent a simple Qt element that stores a project path. As the path is machine-dependant, this object
    implements methods for deserializing."""
    def __init__(self, elt_str, getter_str, setter_str):
        super(SimpleProjectPathSerializedElement, self).__init__(elt_str, getter_str, setter_str)

    @staticmethod
    def get_base_path():
        return os.path.join(config.CURRENT_MAPPING_DIRECTORY, config.DMM_FOLDER)

    def store_value(self, dlg):
        super(SimpleProjectPathSerializedElement, self).store_value(dlg)
        if os.path.isfile(self.value):
            self.value = os.path.relpath(self.value, self.get_base_path())

    def get_value(self):
        val = os.path.join(self.get_base_path(), self.value)
        if os.path.isfile(val):
            return val
        else:
            return ""


class DMMSerializer:
    """This object store all inputs from the DMM"""

    def __init__(self, dlg):
        self.elements = [SimpleSerializedElement("areaLineEdit", "text", "setText"),
                         SimpleSerializedElement("countryComboBox", "currentText", "setCurrentText"),
                         SimpleSerializedElement("baselineScenarioYearSpinBox", "value", "setValue"),
                         SimpleProjectPathSerializedElement("loadFileLineEdit", "text", "setText"),
                         SimpleSerializedElement("lidarCheckBox", "isChecked", "setChecked"),
                         SimpleSerializedElement("DTMLineEdit", "text", "setText"),
                         SimpleSerializedElement("DSMLineEdit", "text", "setText"),
                         SimpleSerializedElement("methodComboBox", "currentText", "setCurrentText"),
                         SimpleSerializedElement("detailFileCheckBox", "isChecked", "setChecked"),
                         SimpleSerializedElement("retrofittedScenariosCheckBox", "isChecked", "setChecked")]
        for e in self.elements:
            e.store_value(dlg)

    @staticmethod
    def get_incremental_serialization_file_path():
        """Return the pickle file path (including current project directory)."""
        return os.path.join(config.CURRENT_MAPPING_DIRECTORY,
                            config.DMM_FOLDER,
                            config.INCREMENTAL_SERIALIZED_DMM_PICKLE_FILE)

    @staticmethod
    def get_full_serialization_file_path():
        """Return the DMM full serialization file. Using the serialization native method from the DMM."""
        return os.path.join(config.CURRENT_MAPPING_DIRECTORY,
                            config.DMM_FOLDER,
                            config.SERIALIZED_DMM_FILE)
    @staticmethod
    def serialize(dlg):
        """Writes a pickle file with a dialog data."""
        dmm_serializer = DMMSerializer(dlg)
        with open(DMMSerializer.get_incremental_serialization_file_path(), "wb") as f:
            pickle.dump(dmm_serializer, f)

    @staticmethod
    def deserialize(dmm_module):
        """Serialize in an incremental way or in a full way."""
        full_serialization_file_path = DMMSerializer.get_full_serialization_file_path()
        is_incremental_serialization = not os.path.exists(full_serialization_file_path)
        if is_incremental_serialization:
            print("Deserializing DMM incrementally.")
            DMMSerializer.deserialize_incrementally(dmm_module.dlg)
        else:
            print("Deserializing DMM fully.")
            loadScenario(dmm_module, full_serialization_file_path)

    @staticmethod
    def deserialize_incrementally(dlg):
        """Open the current project file and fill the dialog given as input."""
        # Check for existence of the file
        file_path = DMMSerializer.get_incremental_serialization_file_path()
        if not os.path.exists(file_path):
            return
        # Read the serialized file
        with open(file_path, 'rb') as f:
            dmm_serializer = pickle.load(f)
        # Incremental serialization:
        # Set all the elements
        for e in dmm_serializer.elements:
            e.deserialize_value(dlg)

    @staticmethod
    def set_simple_element_with_setter(dlg, elt_str, setter_str, value):
        """Sets a simple element value with a given setting method (given as string)."""
        if setter_str in dir(dlg):
            elt = getattr(dlg, elt_str)  # Get the element
            if setter_str in dir(elt):
                getattr(elt, setter_str)(value)  # Set the value
