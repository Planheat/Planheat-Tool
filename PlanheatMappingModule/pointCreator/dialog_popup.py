# -*- coding: utf-8 -*-


import os

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import pyqtSignal, Qt

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog_popup.ui'))


class DialogPopup(QtWidgets.QDialog, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(DialogPopup, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.closingPlugin.emit()
            super(DialogPopup, self).keyPressEvent(event)
