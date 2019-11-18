# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 11:17:45 2018

@author: SALFE
"""
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsMessageLog
from qgis.gui import QgsMessageBar
from qgis.core import Qgis
from PyQt5.QtWidgets import QMessageBox
from .EnergySource import EnergySource
from .Technology import Technology

class Solution(QtWidgets.QTreeWidgetItem):
            
    def doRemoveEnergySourceItem(self,itemToRemove):
        key = itemToRemove.eParent + "+" + itemToRemove.eType + "+" + itemToRemove.eName
        if (key in self.sEnergySources):
            self.sEnergySources.remove(key)
            return True
        else:
            return False
        
    def doAddNewEnergySourceItem(self, itemToAdd):
        present = False
        if (itemToAdd.doGetKey() in self.sEnergySources):
            present = True
        if (not present):
            self.sEnergySources.append(itemToAdd.doGetKey())
        return present
        
    def doCheckIfEnergySourceIsAlreadyPresent(self, ekey):   
       if (ekey in self.sEnergySources):
           return True
       else:
           return False
        
    def doCheckIfTechnologyIsAlreadyPresent(self, ekey, tkey):
        if (ekey in self.sEnergySources): 
            for c in range(self.childCount()):
                for e in range (self.child(c).childCount()):				 
                    if (self.child(c).child(e).doCheckIfTechnologyIsAlreadyPresent(tkey) == tkey):
                        return True
                    else:				
                        return False

    def doGetEnergySourceItem(self,ekey):
        if (ekey in self.sEnergySources): 
            for c in range(self.childCount()):
                for e in range (self.child(c).childCount()):
                    if (self.child(c).child(e).doGetKey() == ekey):
                        return self.child(c).child(e)
	
                      
    def doGetTechnologyItem(self,tkey,ekey): 
          for c in range(self.childCount()):
                for e in range (self.child(c).childCount()):
                      for t in range(self.child(c).child(e).childCount()):
                        if(self.child(c).child(e).child(t).doGetKey() == tkey):
                          return self.child(c).child(e).child(t)

    def doGetRootNodeName(self):
        return self.text(0)
    
    def doResetEnergyDict(self):
        self.sEnergySources.clear()
        
    def __init__(self, parent=None, name="Single Building Solution", icon_path=""):
        super(Solution, self).__init__(parent)
        self.setText(0, name)
        self.setIcon(0,QtGui.QIcon(icon_path))
        self.sEnergySources = []
        self.doResetEnergyDict()


