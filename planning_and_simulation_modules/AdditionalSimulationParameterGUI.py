from PyQt5 import QtWidgets, uic

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox

import os
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'sim_params_dialog.ui'))


class AdditionalSimulationParameterGUI(QtWidgets.QDockWidget, FORM_CLASS):
    data_emitter = pyqtSignal(dict)

    def __init__(self, data=None, description="", parent=None):
        """Constructor."""
        super(AdditionalSimulationParameterGUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.years.setValue(5)
        self.r_factor.setValue(0.11)
        self.demo_factor.setValue(1.00)
        self.FEavailability.setValue(1)

        self.cancel.clicked.connect(self.cancel_clicked_event_handler)
        self.ok.clicked.connect(self.ok_clicked_event_handler)

        self.set_data(data)
        self.set_description(description)

    def get_state(self):
        return {"years": self.years.value(), "r_factor": self.r_factor.value(), "demo_factor": self.demo_factor.value(),
                "FEavailability": self.FEavailability.value()}

    def cancel_clicked_event_handler(self):
        while True:
            try:
                self.data_emitter.disconnect()
            except TypeError:
                break
        self.close()

    def ok_clicked_event_handler(self):
        self.data_emitter.emit(self.get_state())
        self.cancel.clicked.emit()

    def set_data(self, data):
        if not isinstance(data, dict):
            return
        AdditionalSimulationParameterGUI.safe_set_spin_value(self.years, data, "years")
        AdditionalSimulationParameterGUI.safe_set_spin_value(self.r_factor, data, "r_factor")
        AdditionalSimulationParameterGUI.safe_set_spin_value(self.demo_factor, data, "demo_factor")
        AdditionalSimulationParameterGUI.safe_set_spin_value(self.FEavailability, data, "FEavailability")

    def set_description(self, description):
        self.description.setText(description)

    @staticmethod
    def safe_set_spin_value(spin_box, data, key):
        try:
            spin_box.setValue(data[key])
        except KeyError:
            pass
