# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 08:55:39 2018

@author: SALFE
"""

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from qgis.core import QgsMessageLog
from .EnergySource import EnergySource

class EnergySourceType(QtWidgets.QTreeWidgetItem):
            
    def doGetNodeParentName(self):
        return self.parentName
    
    def doGetNodeName(self):
        return self.text(0)   
    
    def doGetNodeType(self):
        return self.ntype
 
    def doSetDHW(self,DHW):
        self.eDHW = DHW
        
    def doGetDHW(self):
        return self.eDHW
    
    def doSetHEATING(self,HEATING):
        self.eHEATING= HEATING
    
    def doGetHEATING(self):
        return self.eHEATING
    
    def doEnergySourceTypeToJSON(self):
        static_part = "{" + '"parentName":'+ '"' + str (self.parentName) + '"' + "," + '"sType":' + '"' + str(self.sType) + '"' + "," + '"icop":' + '"' + str(self.icop)  + '"' + "," +  '"ntype":'  + '"'  + str(self.ntype)  + '"' + "," + '"EnergySources":['
        for n in range(self.childCount()):
            static_part = static_part  + self.child(n).doEnergySourceToJSON() + ","
        if (static_part.endswith(",")):                                          
            static_part = static_part[:-1]                                           
        return static_part + "]}"   


    def doGetPercentages(self):
        if (self.sType == 'HEATING+DHW'):            
            #QgsMessageLog.logMessage("parent name" + "" + str(self.tParent),tag = "Technology", level=QgsMessageLog.INFO)   
            # HEATING+DHW
            return "(" + str(self.eDHW) + " % -" + str(self.eHEATING) + "%)"
        else:
            return None

      
    def __init__(self, parent=None, stype="DHW", icon_path=""):
        super(EnergySourceType, self).__init__(parent)
        self.setText(0, stype)
        self.icop = icon_path
        self.sType = stype
        self.eDHW = 50
        self.eHEATING = 50
        self.setIcon(0,QtGui.QIcon(icon_path)) 
        
        self.ntype = "EnergySourceTypeNode"
        self.parentName = parent.text(0)
