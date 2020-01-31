# -*- coding: utf-8 -*-


import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import  QGuiApplication
from PyQt5.QtWidgets import  QWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'supply_algorithm_node_popup.ui'))


class SupplyAlgorithmNodePopup(QtWidgets.QDialog, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(SupplyAlgorithmNodePopup, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def resizeEvent(self, event):

        print('resize')
        self.setWindowModality(Qt.ApplicationModal)

        layout = self.scrollAreaWidgetContents_2.layout()
        layout.setAlignment(Qt.AlignTop)
        self.scrollAreaWidgetContents_2.setLayout(layout)
        self.scrollAreaWidgetContents_2.adjustSize()
        res_min = 9999
        for screen in QGuiApplication.screens():
            res_min = min(screen.geometry().height(), res_min)
        self.scrollArea.adjustSize()
        self.scrollArea.setMinimumHeight(min(self.height() - 200, res_min - 400, self.scrollArea.height()))
        self.scrollArea.adjustSize()

        layout = self.layout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)
        self.adjustSize()

        super().resizeEvent(event)