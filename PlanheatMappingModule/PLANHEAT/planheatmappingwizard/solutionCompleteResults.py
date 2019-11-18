# -*- coding: utf-8 -*-
"""
Created on Mon Apr 23 12:20:39 2018

@author: giurt
"""

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsMessageLog
from PyQt5.QtWidgets import QMessageBox


class createRootNodeCompleteResults(QtWidgets.QTreeWidgetItem):
        
    def __init__(self, parent=None, name="Single Building Solution", icon_path=""):
        super(createRootNodeCompleteResults, self).__init__(parent)
        self.setText(0, name)
        self.setIcon(0,QtGui.QIcon(icon_path))


