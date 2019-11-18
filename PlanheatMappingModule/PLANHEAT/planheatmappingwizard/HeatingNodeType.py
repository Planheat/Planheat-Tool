# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 14:39:59 2018

@author: giurt
"""
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog

class HeatingNodeType(QtWidgets.QTreeWidgetItem):
    
    def doGetNodeParentName(self):
        return self.parentName
    
    def doGetNodeName(self):
        return self.text(0)   

    def doGetNodeType(self):
        return self.ntype
    
    def doSetIconPath(self, icon_path):
        self.icop = icon_path
        
    def doGetIconPath(self):
        return self.icop
       
    
    def __init__ (self, parent=None,stype= "", icon_path=""):
        super(HeatingNodeType, self).__init__(parent)
        self.setText(0, stype)
        self.icop = icon_path
        self.sType = stype
        #setIcon takes in input the column where you want to display the icon
        self.setIcon(0,QtGui.QIcon(icon_path)) 
        self.ntype = "HeatingNodeType"
        self.parentName = parent.text(0)

        
        
        
        
        
        
        
        
        
        
        
        
        