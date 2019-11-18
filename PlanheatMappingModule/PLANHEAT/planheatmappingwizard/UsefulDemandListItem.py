# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 09:02:32 2018

@author: SALFE
"""
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from qgis.core import QgsMessageLog

class UsefulDemandListItem(QtWidgets.QWidget):
    def __init__ (self,parent = None):
        # initialize the class as inheritated from QtQidget
        super(UsefulDemandListItem, self).__init__(parent)
        # declare a treeWidgetItem (questa è la sintassi giusta per definire un albero di widget in pyQt5)  
        self.textQVBoxLayout = QtWidgets.QVBoxLayout()
        self.textUpQLabel    = QtWidgets.QLabel()
        self.textDownQLabel  = QtWidgets.QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout  = QtWidgets.QHBoxLayout()
        self.iconQLabel      = QtWidgets.QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        self.textUpQLabel.setStyleSheet('''
            color: rgb(0, 0, 255);
        ''')
        self.textDownQLabel.setStyleSheet('''
            color: rgb(255, 0, 0);
        ''')

    def setTextUp (self, text):
        self.textUpQLabel.setText(text)

    def setTextDown (self, text):
        self.textDownQLabel.setText(text)

    def setIcon (self, itemtype):
        if (itemtype == "COOLING"):
            self.iconQLabel.setPixmap(QtGui.QPixmap(":/images/temperature_hot.png"))
        else:
            self.iconQLabel.setPixmap(QtGui.QPixmap(":/images/temperature_cold.png"))
            