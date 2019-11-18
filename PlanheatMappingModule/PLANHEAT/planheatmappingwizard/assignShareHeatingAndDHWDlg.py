# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 12:28:36 2018

@author: giurt
"""

import os

from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsMessageLog
from PyQt5.QtWidgets import QMessageBox

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'assignShareHeating.ui'), resource_suffix='')

styleInNormal  = "color: green; background-color: #cbffcf "
styleReadOnly  = "color: green; background-color: #ffff7f"

class AssignShareHeatingAndDHWDlg(QtWidgets.QDialog, FORM_CLASS):
    
    dataUpdated = pyqtSignal(str,str,str,float,float)
    
    def doParamsConfirmed(self):
        currentDHW = self.doubleSpinBoxDHW.value()
        currentHeating= self.doubleSpinBoxHEATING.value()
        #check if DHW and HEATING sono diversi da 0
        if (self.doubleSpinBoxDHW.value()!= 0  and self.doubleSpinBoxHEATING.value()!= 0):
            #emit the signal
            self.dataUpdated.emit(self.parentType,self.srcName,self.srcType, float(self.doubleSpinBoxDHW.value()), float(self.doubleSpinBoxHEATING.value()))
            self.close()
        else:
            QMessageBox.about(self, 'info!', "Please enter a source energy name!")
    
    def doPrepareControls(self):
#        if ((self.srcName == "no name") or (self.srcName == "")):        
#            self.lineEditEnergyName.setStyleSheet(styleInNormal) 
#            self.lineEditEnergyName.setReadOnly(False)            
#        else:
#            self.lineEditEnergyName.setStyleSheet(styleReadOnly) 
#            self.lineEditEnergyName.setReadOnly(True)            
#        self.lineEditEnergyName
        if(self.srcType == "DHW"):
            self.doubleSpinBoxDHW.setValue(100) 
            self.doubleSpinBoxHEATING.setValue(0)
            self.doubleSpinBoxDHW.hide()        
            self.doubleSpinBoxHEATING.hide()   
            self.labelDHW.hide()
            self.labelHEATING.hide()                     
        else:
            if(self.srcType == "HEATING"):
                self.doubleSpinBoxDHW.setValue(0) 
                self.doubleSpinBoxHEATING.setValue(100)  
                self.doubleSpinBoxDHW.hide() 
                self.labelDHW.hide()
                self.labelHEATING.hide()
                self.doubleSpinBoxHEATING.hide()      
            else:
                if(self.srcType == "HEATING+DHW"):
                    self.doubleSpinBoxDHW.setValue(50) 
                    self.doubleSpinBoxHEATING.setValue(50)  
                    self.doubleSpinBoxDHW.setStyleSheet(styleInNormal)        
                    self.doubleSpinBoxHEATING.setStyleSheet(styleInNormal)                    
                    self.doubleSpinBoxDHW.setReadOnly(False)
                    self.doubleSpinBoxHEATING.setReadOnly(False)
                    self.doubleSpinBoxDHW.show()        
                    self.doubleSpinBoxHEATING.show()
                    self.labelDHW.show()
                    self.labelHEATING.show()                     
                else:
                    if(self.srcType == "COOLING"):    
                        self.doubleSpinBoxDHW.setValue(0) 
                        self.doubleSpinBoxHEATING.setValue(0)
                        self.doubleSpinBoxDHW.hide()        
                        self.doubleSpinBoxHEATING.hide()
                        self.labelDHW.hide()
                        self.labelHEATING.hide()
    
    def doSetDHW(self,value): 
        self.doubleSpinBoxDHW.setValue(value)   
             
    def doSetHEATING(self,value): 
        self.doubleSpinBoxHEATING.setValue(value)           
        
    def doDHWValueChanged(self,value):
        self.doubleSpinBoxHEATING.setValue(100-value)
    
    def doHeatingValueChanged(self,value):        
        self.doubleSpinBoxDHW.setValue(100-value) 
        
    def doSetUpSignalsConnections(self):
        self.pushButtonConfirmParams.clicked.connect(self.doParamsConfirmed)
        self.doubleSpinBoxDHW.valueChanged.connect(self.doDHWValueChanged)
        self.doubleSpinBoxHEATING.valueChanged.connect(self.doHeatingValueChanged)  
            
    def __init__(self,parentType,srcName,srcType, parent=None):
        #costruttore per la classe derivata da QDialog
        super(AssignShareHeatingAndDHWDlg, self).__init__(parent)
        self.setupUi(self)
        self.srcType = srcType
        self.srcName = srcName
        self.parentType = parentType
        self.doPrepareControls()
        self.doSetUpSignalsConnections()