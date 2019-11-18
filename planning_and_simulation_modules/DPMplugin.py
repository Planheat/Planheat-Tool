
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'Flusso_base.ui'))


class DPMDialog(QtWidgets.QDialog, FORM_CLASS):

    DPMDialog_closing_signal = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(DPMDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        self.setupUi(self)
        self.step1btn.setEnabled(False)
        self.step2btn.setEnabled(False)
        self.step3btn.setEnabled(False)
        self.step4btn.setEnabled(False)


    def button1_change(self):
        """if not state:
            self.step1btn.setEnabled(False)
        else:"""
        self.step1btn.setEnabled(True)
        #self.step4btn.setEnabled(True)

    def button2_change(self):
            self.step2btn.setEnabled(True)

    def button3_change(self):
            self.step3btn.setEnabled(True)

    def button4_change(self):
            self.step4btn.setEnabled(True)

    def closeEvent(self, event):
        self.close_dpm_dialog()
        event.accept()

    def close_dpm_dialog(self):
        self.DPMDialog_closing_signal.emit()
        self.hide()

