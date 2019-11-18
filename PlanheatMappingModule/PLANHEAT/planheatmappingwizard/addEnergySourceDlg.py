# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 11:23:19 2018

@author: SALFE
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
    os.path.dirname(__file__), 'addEnergySource.ui'), resource_suffix='')

styleInNormal  = "color: green; background-color: #cbffcf "
styleReadOnly  = "color: green; background-color: #ffff7f"

class AddEnergySourceDlg(QtWidgets.QDialog, FORM_CLASS):
    
    dataUpdated = pyqtSignal(str,str,str,float)
    
    def doParamsConfirmed(self):
        if ((self.lineEditEnergyName.text() != "") and (self.lineEditEnergyName.text() != "no name")):
            self.dataUpdated.emit(self.srcType, self.parentType,self.lineEditEnergyName.text(), float(self.doubleSpinBoxFinalEnergyConsumption.value()))
            self.close()
        else:
            QMessageBox.about(self, 'info!', "Please enter a source energy name!")
    
    def doPrepareControls(self):
        if ((self.srcName == "no name") or (self.srcName == "")):        
            self.lineEditEnergyName.setStyleSheet(styleInNormal) 
            self.lineEditEnergyName.setReadOnly(False)            
        else:
            self.lineEditEnergyName.setStyleSheet(styleReadOnly) 
            self.lineEditEnergyName.setReadOnly(True)            
        self.lineEditEnergyName.setText(self.srcName)
        if(self.srcType == "DHW"):
            self.doubleSpinBoxFinalEnergyConsumption.setValue(50)
            self.doubleSpinBoxFinalEnergyConsumption.setStyleSheet(styleInNormal)
            self.doubleSpinBoxFinalEnergyConsumption.setReadOnly(False) 
                   
        else:
            if(self.srcType == "HEATING"):
                self.doubleSpinBoxFinalEnergyConsumption.setValue(50)
                self.doubleSpinBoxFinalEnergyConsumption.setStyleSheet(styleInNormal)
                self.doubleSpinBoxFinalEnergyConsumption.setReadOnly(False)

            else:
                if(self.srcType == "HEATING+DHW"):
                    self.doubleSpinBoxFinalEnergyConsumption.setValue(50)
                    self.doubleSpinBoxFinalEnergyConsumption.setStyleSheet(styleInNormal)
                    self.doubleSpinBoxFinalEnergyConsumption.setReadOnly(False)
                  
                else:
                    if(self.srcType == "COOLING"):    
                        self.doubleSpinBoxFinalEnergyConsumption.setValue(50)
                        self.doubleSpinBoxFinalEnergyConsumption.setStyleSheet(styleInNormal)
                        self.doubleSpinBoxFinalEnergyConsumption.setReadOnly(False)  
 
            
    def doSetTotalEnergyConsumption(self,value):
        self.doubleSpinBoxFinalEnergyConsumption.setValue(value)

    def doSetTotalEnergyConsumptionValueChanged(self,value): 
        self.doubleSpinBoxFinalEnergyConsumption.setValue(100-value)     
       
    def doSetUpSignalsConnections(self):
        self.pushButtonConfirmParams.clicked.connect(self.doParamsConfirmed)
        self.doubleSpinBoxFinalEnergyConsumption.valueChanged.connect(self.doSetTotalEnergyConsumption)

            
    def __init__(self,parentType, srcName, srcType, parent=None):
        super(AddEnergySourceDlg, self).__init__(parent)
        self.setupUi(self)
        self.srcName = srcName
        self.srcType = srcType
        self.parentType = parentType
        self.doPrepareControls()
        self.doSetUpSignalsConnections()