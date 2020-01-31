from PyQt5 import QtWidgets, uic

from PyQt5.QtCore import pyqtSignal

import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../../ui', 'SimulationDetailsGUI.ui'))


class SimulationDetailsGUI(QtWidgets.QDialog, FORM_CLASS):
    SimulationDetailsGUI_closing_signal = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(SimulationDetailsGUI, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


