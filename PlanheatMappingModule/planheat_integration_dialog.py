# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanheatIntegrationDialog
                                 A QGIS plugin
 planheat integration
                             -------------------
        begin                : 2017-12-06
        git sha              : $Format:%H$
        copyright            : (C) 2017 by v
        email                : v
 ***************************************************************************/

"""

import os

from PyQt5 import uic,QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QCoreApplication, Qt

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'planheat integration_dialog_base.ui'))


class PlanheatIntegrationDialog(QtWidgets.QDialog, FORM_CLASS):
    closingPlugin = pyqtSignal()
    def __init__(self, parent=None):
        """Constructor."""
        super(PlanheatIntegrationDialog, self).__init__(parent)
        self.setupUi(self)

        file_dir_path = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(file_dir_path, "ui", "icon.png")
        self.setWindowIcon(QtGui.QIcon(icon_path))

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

#needed to be able to reopen the plugin after close with esc key.
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.closingPlugin.emit()
            super(PlanheatIntegrationDialog, self).keyPressEvent(event)
