# -*- coding: utf-8 -*-
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dhcoptimizer_planheat_dialog_base.ui'))


class DHCOptimizerPlanheatDialog(QtWidgets.QDialog, FORM_CLASS):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(DHCOptimizerPlanheatDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closed.emit()
