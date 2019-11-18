# -*- coding: utf-8 -*-
"""
Created on Fri Mar  9 10:16:45 2018

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
    os.path.dirname(__file__), 'addTechnology.ui'), resource_suffix='')

styleInNormal  = "color: green; background-color: #cbffcf "
styleReadOnly  = "color: green; background-color: #ffff7f"

class AddTechnologySourceDlg(QtWidgets.QDialog, FORM_CLASS):
    
    dataUpdated = pyqtSignal(str,str,str,str,float,float,float,float,float,float,float,float,float,float,bool,str)
    
    def doParamsConfirmed(self):
        if ((self.lineEditTechnologyName.text() != "") and (self.lineEditTechnologyName.text() != "no name")):
            if (self.ParametersAreValidForBoth): 
                self.doCopyDHWtoHEATING()
                self.dataUpdated.emit(self.parentKey, self.techKey, \
                                  self.lineEditTechnologyName.text(), \
                                  self.solutionType, \
                                  float(self.doubleSpinBoxEfficiencyDHW.value()), \
                                  float(self.doubleSpinBoxPercEndUsersDHW.value()), \
                                  float(self.doubleSpinBoxCHPUtilizationFactorDHW.value()), \
                                  float(self.doubleSpinBoxEfficiencyHEATING.value()), \
                                  float(self.doubleSpinBoxPercEndUsersHEATING.value()), \
                                  float(self.doubleSpinBoxCHPUtilizationFactorHEATING.value()), \
                                  float(self.doubleSpinBoxGridEfficiencyDHW.value()), \
                                  float(self.doubleSpinBoxGridEfficiencyHEATING.value()),  \
                                  float(self.lineEditUsefulDemand.text()),  \
                                  float(self.lineEditTechnologyConsumption.text()), \
                                  self.ParametersAreValidForBoth, \
                                  self.doGetHeatSupplyTypeAsString())
                self.close()
                
            else:
                self.dataUpdated.emit(self.parentKey, self.techKey, \
                                  self.lineEditTechnologyName.text(), \
                                  self.solutionType, \
                                  float(self.doubleSpinBoxEfficiencyDHW.value()), \
                                  float(self.doubleSpinBoxPercEndUsersDHW.value()), \
                                  float(self.doubleSpinBoxCHPUtilizationFactorDHW.value()), \
                                  float(self.doubleSpinBoxEfficiencyHEATING.value()), \
                                  float(self.doubleSpinBoxPercEndUsersHEATING.value()), \
                                  float(self.doubleSpinBoxCHPUtilizationFactorHEATING.value()), \
                                  float(self.doubleSpinBoxGridEfficiencyDHW.value()), \
                                  float(self.doubleSpinBoxGridEfficiencyHEATING.value()),  \
                                  float(self.lineEditUsefulDemand.text()),  \
                                  float(self.lineEditTechnologyConsumption.text()), \
                                  self.ParametersAreValidForBoth, \
                                  self.doGetHeatSupplyTypeAsString())

                self.close()
        else:
            QMessageBox.about(self, 'info!', "Please enter a technology name!")
           

    def doSetEnergyConsumption(self,enCons):
        self.lineEditEnergyConsumption.setText("{0:.1f}".format(float(enCons)))    
    
    def doGetEnergyConsumption(self):
        return self.lineEditEnergyConsumption.text()      
    
    def doSetTechnologyConsumption(self,enCons):
        self.lineEditTechnologyConsumption.setText("{0:.1f}".format(float(enCons)))    
    
    def doGetTechnologyConsumption(self):
        return self.lineEditTechnologyConsumption.text()   
    
    def doSetHeatExtracted(self,htExtracted):
        self.lineEditHeatExtracted.setText("{0:.1f}".format(float(htExtracted)))    
    
    def doGetHeatExtracted(self):
        return self.lineEditHeatExtracted.text()   
    
    def doSetUsefulDemand(self,demand):
        self.lineEditUsefulDemand.setText("{0:.1f}".format(float(demand)))    
    
    def doGetUsefulDemand(self):
        return self.lineEditUsefulDemand.text()    
    
    def doSetTechName(self,name):
        self.lineEditTechnologyName.setText(self.techName)    
    
    def doGetTechName(self):
        return self.lineEditTechnologyName.text()
    
    def doSetGridEfficiencyDHW(self,value):
        self.doubleSpinBoxGridEfficiencyDHW.setValue(float(value))
        
    def doSetGridEfficiencyHEATING(self,value):
        self.doubleSpinBoxGridEfficiencyHEATING.setValue(float(value))
    
    def doSetCHPFactorDHW(self,value):
        self.doubleSpinBoxCHPUtilizationFactorDHW.setValue(float(value))
    
    def doSetCHPFactorHEATING(self,value):
        self.doubleSpinBoxCHPUtilizationFactorHEATING.setValue(float(value)) 
    
    def doSetEfficiencyDHW(self,value):
        self.doubleSpinBoxEfficiencyDHW.setValue(float(value))
    
    def doSetEfficiencyHEATING(self,value):
        self.doubleSpinBoxEfficiencyHEATING.setValue(float(value))         
    
    def doSetPercEndUsersDHW(self,value):
        self.doubleSpinBoxPercEndUsersDHW.setValue(float(value))
    
    def doSetPercEndUsersHEATING(self,value):
        self.doubleSpinBoxPercEndUsersHEATING.setValue(float(value))  
        
    def doGetGridEfficiencyDHW(self):
        return float(self.doubleSpinBoxGridEfficiencyDHW.value())
        
    def doGetEfficiencyHEATING(self):
        return float(self.doubleSpinBoxGridEfficiencyHEATING.value())
    
    def doGetCHPFactorDHW(self,value):
        return float(self.doubleSpinBoxCHPUtilizationFactorDHW.value())
    
    def doGetCHPFactorHEATING(self):
        return float(self.doubleSpinBoxCHPUtilizationFactorHEATING.value() )
    
    def doGetEfficiencyDHW(self):
        return float(self.doubleSpinBoxEfficiencyDHW.value())
    
    def doGetEfficicencyHEATING(self):
        return float(self.doubleSpinBoxEfficiencyHEATING.value())        
    
    def doGetPercEndUsersDHW(self):
        return float(self.doubleSpinBoxPercEndUsersDHW.value())
    
    def doGetPercEndUsersHEATING(self):
        return float(self.doubleSpinBoxPercEndUsersHEATING.value())
 
    def doCopyDHWtoHEATING(self):
        val = float(self.doubleSpinBoxGridEfficiencyDHW.value())
        self.doubleSpinBoxGridEfficiencyHEATING.setValue(val) 
        val = float(self.doubleSpinBoxCHPUtilizationFactorDHW.value())
        self.doubleSpinBoxCHPUtilizationFactorHEATING.setValue(val) 
        val = float(self.doubleSpinBoxEfficiencyDHW.value())
        self.doubleSpinBoxEfficiencyHEATING.setValue(val) 
        val = float(self.doubleSpinBoxPercEndUsersDHW.value())
        self.doubleSpinBoxPercEndUsersHEATING.setValue(val) 
   
    def doPrepareControls(self):
        if ((self.techName == "no name") or (self.techName == "")):        
            self.lineEditTechnologyName.setStyleSheet(styleInNormal) 
            self.lineEditTechnologyName.setReadOnly(False)            
        else:
            self.lineEditTechnologyName.setStyleSheet(styleInNormal) 
            self.lineEditTechnologyName.setReadOnly(False)   
            
        self.lineEditTechnologyName.setText(self.techName)
        self.lineEditUsefulDemand.setReadOnly(True)
        self.lineEditTechnologyConsumption.setReadOnly(True)   
        self.lineEditHeatExtracted.setReadOnly(True)           
        self.lineEditEnergyConsumption.setReadOnly(True)  
        
        self.lineEditUsefulDemand.setStyleSheet(styleReadOnly)  
        self.lineEditTechnologyConsumption.setStyleSheet(styleReadOnly)
        self.lineEditHeatExtracted.setStyleSheet(styleReadOnly)        
        self.lineEditEnergyConsumption.setStyleSheet(styleReadOnly)         
        
        self.doSetUsefulDemand(0)
        self.doSetEnergyConsumption(0) 
        self.doSetTechnologyConsumption(0)
        self.doSetHeatExtracted(0)
        
        if (((self.solutionType == "Single Building Solution") or (self.solutionType == "District Heating Network")) and (self.enType != "COOLING")) :
            if(self.enType == "DHW"):
                self.tabWidget.setTabEnabled(1,False)
                self.tabWidget.setCurrentIndex(0)  
                if (self.solutionType != ("District Heating Network")):
                    self.doubleSpinBoxGridEfficiencyDHW.hide()
                    self.labelGridEfficiencyDHW.hide() 
                else:
                    self.doubleSpinBoxGridEfficiencyDHW.setStyleSheet(styleInNormal)  
                    self.doubleSpinBoxGridEfficiencyDHW.show()
                    self.labelGridEfficiencyDHW.show() 
                    
                if (self.techName != "Comb. Heat & Pow"):
                    self.doubleSpinBoxCHPUtilizationFactorDHW.hide()
                    self.labelCHPUtFactorDHW.hide()
                else:
                    self.doubleSpinBoxCHPUtilizationFactorDHW.setStyleSheet(styleInNormal)
                    self.doubleSpinBoxCHPUtilizationFactorDHW.show()
                    self.labelCHPUtFactorDHW.show()
                     
                self.doubleSpinBoxEfficiencyDHW.setValue(100) 
                self.doubleSpinBoxPercEndUsersDHW.setValue(50)  
                self.doubleSpinBoxEfficiencyDHW.setStyleSheet(styleInNormal) 
                self.doubleSpinBoxPercEndUsersDHW.setStyleSheet(styleInNormal)
                self.groupBoxHeatSupply.hide()
                self.radioButtonValidForAll.hide()
                self.radioButtonSeparated.hide()  
                self.ParametersAreValidForBoth = False
            else:
                if(self.enType == "HEATING"):
                    self.tabWidget.setTabEnabled(0,False)
                    self.tabWidget.setCurrentIndex(1) 
                    if (self.solutionType != "District Heating Network"):
                        self.doubleSpinBoxGridEfficiencyHEATING.hide()
                        self.labelGridEfficiencyHEATING.hide() 
                    else:
                        self.doubleSpinBoxGridEfficiencyHEATING.setStyleSheet(styleInNormal)                      
                        self.doubleSpinBoxGridEfficiencyHEATING.show()
                        self.labelGridEfficiencyHEATING.show() 
                    
                    if (self.techName != "Comb. Heat & Pow"):
                        self.doubleSpinBoxCHPUtilizationFactorHEATING.hide()
                        self.labelCHPUtFactorHEATING.hide() 
                    else:
                        self.doubleSpinBoxCHPUtilizationFactorHEATING.setStyleSheet(styleInNormal)
                        self.doubleSpinBoxCHPUtilizationFactorHEATING.show()
                        self.labelCHPUtFactorHEATING.show() 
                         
                    self.doubleSpinBoxEfficiencyHEATING.setValue(100) 
                    self.doubleSpinBoxPercEndUsersHEATING.setValue(50)  
                    self.doubleSpinBoxEfficiencyHEATING.setStyleSheet(styleInNormal) 
                    self.doubleSpinBoxPercEndUsersHEATING.setStyleSheet(styleInNormal)
                    self.radioButtonValidForAll.hide()
                    self.groupBoxHeatSupply.show()
                    self.radioButtonSeparated.hide()
                    self.ParametersAreValidForBoth = False
                    
                else:
                    if(self.enType == "HEATING+DHW"):
                        self.tabWidget.setTabEnabled(0,True)
                        self.tabWidget.setTabEnabled(1,False)
                        self.tabWidget.setCurrentIndex(0) 

                        
                        if (self.solutionType != "District Heating Network"):
                            self.doubleSpinBoxGridEfficiencyHEATING.hide()
                            self.doubleSpinBoxGridEfficiencyDHW.hide()
                            self.labelGridEfficiencyDHW.hide() 
                            self.labelGridEfficiencyHEATING.hide() 
                        else:
                            self.doubleSpinBoxGridEfficiencyHEATING.setStyleSheet(styleInNormal) 
                            self.doubleSpinBoxGridEfficiencyDHW.setStyleSheet(styleInNormal)                             
                            self.doubleSpinBoxGridEfficiencyHEATING.show()
                            self.doubleSpinBoxGridEfficiencyDHW.show()
                            self.labelGridEfficiencyDHW.show() 
                            self.labelGridEfficiencyHEATING.show()                             
                            
                        if (self.techName != "Comb. Heat & Pow"):

                            self.doubleSpinBoxCHPUtilizationFactorHEATING.hide()
                            self.doubleSpinBoxCHPUtilizationFactorDHW.hide()                            
                            self.labelCHPUtFactorDHW.hide()
                            self.labelCHPUtFactorHEATING.hide()                              
                        else:

                            self.doubleSpinBoxCHPUtilizationFactorHEATING.show()
                            self.doubleSpinBoxCHPUtilizationFactorDHW.show() 
                            self.doubleSpinBoxCHPUtilizationFactorHEATING.setStyleSheet(styleInNormal)
                            self.doubleSpinBoxCHPUtilizationFactorDHW.setStyleSheet(styleInNormal)
                            self.labelCHPUtFactorDHW.show()
                            self.labelCHPUtFactorHEATING.show()      
                            
                        self.doubleSpinBoxEfficiencyHEATING.setValue(100) 
                        self.doubleSpinBoxPercEndUsersHEATING.setValue(50)  
                        self.doubleSpinBoxEfficiencyHEATING.setStyleSheet(styleInNormal) 
                        self.doubleSpinBoxPercEndUsersHEATING.setStyleSheet(styleInNormal)
                        self.doubleSpinBoxEfficiencyDHW.setValue(100) 
                        self.doubleSpinBoxPercEndUsersDHW.setValue(50)  
                        self.doubleSpinBoxEfficiencyDHW.setStyleSheet(styleInNormal) 
                        self.doubleSpinBoxPercEndUsersDHW.setStyleSheet(styleInNormal)
                                  
        else:
            self.tabWidget.setTabEnabled(1,False)
            self.tabWidget.setTabEnabled(0,True)
            self.tabWidget.setCurrentIndex(0)                             
            self.tabWidget.setTabText(0,"Technology parameters") 
            

            self.doubleSpinBoxCHPUtilizationFactorHEATING.hide()
            self.doubleSpinBoxCHPUtilizationFactorDHW.hide()              
            self.labelCHPUtFactorDHW.hide()
            self.labelCHPUtFactorHEATING.hide()  
            self.radioButtonValidForAll.hide()
            self.radioButtonSeparated.hide()
            self.groupBoxHeatSupply.hide()   
            self.doubleSpinBoxGridEfficiencyHEATING.hide()  
            self.labelGridEfficiencyHEATING.hide()             
            if (self.solutionType != "District Cooling Network"):
                self.doubleSpinBoxGridEfficiencyDHW.hide() 
                self.labelGridEfficiencyDHW.hide() 
            else:
                self.doubleSpinBoxGridEfficiencyDHW.setStyleSheet(styleInNormal)                
                self.doubleSpinBoxGridEfficiencyDHW.show()                
                self.labelGridEfficiencyDHW.show()
                
            self.doubleSpinBoxEfficiencyDHW.setValue(100) 
            self.doubleSpinBoxPercEndUsersDHW.setValue(50)  
            self.doubleSpinBoxEfficiencyDHW.setStyleSheet(styleInNormal) 
            self.doubleSpinBoxPercEndUsersDHW.setStyleSheet(styleInNormal) 
            self.ParametersAreValidForBoth = True
                           
    def doGetTechKey(self):
        return self.techKey
    
    def doGetParentKey(self):
        return self.parentKey    
    
    def doSetUpSignalsConnections(self):
        self.pushButtonConfirm.clicked.connect(self.doParamsConfirmed)
        self.radioButtonValidForAll.toggled.connect(lambda:self.doCheckParamsValiditybtnstate(self.radioButtonValidForAll))
        self.radioButtonSeparated.toggled.connect(lambda:self.doCheckParamsValiditybtnstate(self.radioButtonSeparated))   
        self.radioButtonLessThan40.toggled.connect(lambda:self.doCheckHeatSupplyTypebtnstate(self.radioButtonLessThan40))
        self.radioButtonBetween40And70.toggled.connect(lambda:self.doCheckHeatSupplyTypebtnstate(self.radioButtonBetween40And70)) 
        self.radioButtonGreaterThan70.toggled.connect(lambda:self.doCheckHeatSupplyTypebtnstate(self.radioButtonGreaterThan70))         

     
    def  doCheckParamsValiditybtnstate (self,btn):
      if btn.text() == "Parameters valid for DHW and HEATING both":
         if btn.isChecked() == True:
             self.tabWidget.setTabEnabled(1,False)
             self.ParametersAreValidForBoth = True
         else:
             self.tabWidget.setTabEnabled(1,True)
             self.ParametersAreValidForBoth = False             
				
      if btn.text() == "Parameters valid for DHW only":
         if btn.isChecked() == True:
            self.tabWidget.setTabEnabled(1,True)
            self.ParametersAreValidForBoth = False 
         else:
            self.tabWidget.setTabEnabled(1,False)
            self.ParametersAreValidForBoth = True 


    def  doCheckHeatSupplyTypebtnstate (self,btn):
        if (btn.text() == "heat supply < 40°C"):
            self.HeatSupplyType = "heat supply < 40°C" 
        else:
            if (btn.text() == "heat supply 40 -70 °C" ):
                self.HeatSupplyType = "heat supply 40 -70 °C" 
            else:
                if (btn.text() == "heat supply >70°C"):
                    self.HeatSupplyType = "heat supply >70°C"
                else:
                    QMessageBox.about(self, 'info!', "Error attempting to manage heat supply type. Type: " + btn.text() + "    Checked: " + str (btn.isChecked()) )
                    

    def doSetHeatSupplyType(self,supplytype):
        self.HeatSupplyType = supplytype
        if (supplytype == "heat supply < 40°C"):
            self.radioButtonLessThan40.setChecked(True)
            self.radioButtonBetween40And70.setChecked(False) 
            self.radioButtonGreaterThan70.setChecked(False)            
        else:
            if (supplytype == "heat supply 40 -70 °C"): 
                self.radioButtonLessThan40.setChecked(False)
                self.radioButtonBetween40And70.setChecked(True) 
                self.radioButtonGreaterThan70.setChecked(False)
            else:
                if (supplytype == "heat supply >70°C"): 
                    self.radioButtonLessThan40.setChecked(False)
                    self.radioButtonBetween40And70.setChecked(False) 
                    self.radioButtonGreaterThan70.setChecked(True)
                else:
                    QMessageBox.about(self, 'info!', "Error attempting to set heat supply type.")
                
    def doGetHeatSupplyTypeAsString(self):    
        return self.HeatSupplyType 
    
    def doGetParametersAreValidForBoth(self):
        return self.ParametersAreValidForBoth

    def doSetParametersAreValidForBoth(self,val): 
        if ((val == True) or (val == "True")):
            self.ParametersAreValidForBoth = True
            self.radioButtonValidForAll.setChecked(True)
            self.radioButtonSeparated.setChecked(False)
        else:
            self.ParametersAreValidForBoth = False
            self.radioButtonValidForAll.setChecked(False)
            self.radioButtonSeparated.setChecked(True)            
            
    def __init__(self,energyType, techName, solType, tkey,pkey,parent=None):
        super(AddTechnologySourceDlg, self).__init__(parent)
        self.setupUi(self)
        self.techName = techName
        self.enType = energyType
        self.solutionType = solType
        self.techKey = tkey
        self.parentKey = pkey  
        self.HeatSupplyType = "heat supply 40 -70 °C" #
        self.ParametersAreValidForBoth = True
        self.doCopyDHWtoHEATING()
        self.doPrepareControls()
        self.doSetUpSignalsConnections()