# -*- coding: utf-8 -*-


import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'algorithm_node_popup.ui'))


class AlgorithmNodePopup(QtWidgets.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()
    loadDockwidget = pyqtSignal()

    def __init__(self, parent=None):
        super(AlgorithmNodePopup, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

