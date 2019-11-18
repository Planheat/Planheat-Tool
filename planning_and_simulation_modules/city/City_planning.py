
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'city_dialog.ui'))


class CityPlanning(QtWidgets.QDialog, FORM_CLASS):

    CityDialog_closing_signal = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(CityPlanning, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)

        self.btn_step2.setEnabled(False)
        self.btn_step3.setEnabled(False)

    def closeEvent(self, event):
        self.close_city_dialog()
        event.accept()

    def button2_change(self):
            self.btn_step2.setEnabled(True)

    def button3_change(self):
            self.btn_step3.setEnabled(True)

    def close_city_dialog(self):
        self.CityDialog_closing_signal.emit()
        self.hide()