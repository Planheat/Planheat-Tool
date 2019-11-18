import os

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

import os.path


# Import pandas to manage data into DataFrames
import pandas

# Import PyQt5
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QInputDialog, QLineEdit, QTreeWidgetItemIterator

# Import qgis main libraries
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

# Import the custom tree widget items
from .building.Building import *
from .building.DPM import *
from .technology.Technology import *
from .Network import Network

from .layer_utils import load_file_as_layer, load_open_street_maps

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'district.ui'))


class District_widget(QtWidgets.QDockWidget, FORM_CLASS):
    district_closing_signal = pyqtSignal()
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(District_widget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.btnSimulation.setEnabled(False)

    def onCloseDistrictPlanningPlugin(self):
        print("Closing District Planning")
        self.show()

    def onCloseDistrictSimulationPlugin(self):
        print("Closing District Simulation")
        self.show()

    def closeEvent(self, event):
        self.closedistrict()
        event.accept()

    def closedistrict(self):
        self.hide()
        self.district_closing_signal.emit()

    def button_change(self):
            self.btnSimulation.setEnabled(True)