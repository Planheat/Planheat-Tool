# -*- coding: utf-8 -*-
"""
Created on Thu May 24 14:25:27 2018

@author: giurt
"""

import os
import csv
from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsMessageLog
from PyQt5.QtWidgets import QMessageBox

from ... import master_mapping_config

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'addUsefulEnergyDlg.ui'), resource_suffix='')

styleInNormal  = "color: green; background-color: #cbffcf "
styleReadOnly  = "color: green; background-color: #ffff7f"

class AddUsefulEnergySourceDlg(QtWidgets.QDialog, FORM_CLASS):
  
  
    def doSetHighHeating(self,value):
      self.doubleSpinBox_HEATING_HIGH.setValue(float(value))

    def doGetHighHeating(self):
      return self.doubleSpinBox_HEATING_HIGH.value()     
      
    def doSetMediumHeating(self,value):
      self.doubleSpinBox_HEATING_MEDIUM.setValue(float(value))
            
    def doGetMediumHeating(self):
      return self.doubleSpinBox_HEATING_MEDIUM.value()
        
    def doSetLowHeating(self,value):
      self.doubleSpinBox_HEATING_LOW.setValue(float(value))
      
    def doGetLowHeating(self):
      return self.doubleSpinBox_HEATING_LOW.value()
    
    def doSetUsefulDHW(self,value):
      self.doubleSpinBox_DHW.setValue(float(value))
    
    def doGetUsefulDHW(self):
      return self.doubleSpinBox_DHW.value()
    
    
    def doSetUsefulCOOLING(self,value):
      self.doubleSpinBox_COOLING.setValue(float(value))   
    
    def doGetUsefulCOOLING(self):
      return self.doubleSpinBox_COOLING.value()
       
    def doSetDoubleSpinBoxValues(self):
      self.doubleSpinBox_HEATING_HIGH.setMaximum(10000000000000000000)
      self.doubleSpinBox_HEATING_HIGH.setStyleSheet(styleInNormal) 
      self.doubleSpinBox_HEATING_MEDIUM.setMaximum(10000000000000000000)
      self.doubleSpinBox_HEATING_MEDIUM.setStyleSheet(styleInNormal) 
      self.doubleSpinBox_HEATING_LOW.setMaximum(10000000000000000000)
      self.doubleSpinBox_HEATING_LOW.setStyleSheet(styleInNormal) 
      self.doubleSpinBox_DHW.setMaximum(10000000000000000000)
      self.doubleSpinBox_DHW.setStyleSheet(styleInNormal) 
      self.doubleSpinBox_COOLING.setMaximum(10000000000000000000)
      self.doubleSpinBox_COOLING.setStyleSheet(styleInNormal) 
      
    def doConnectActions(self):
      self.pushButtonOK.clicked.connect(self.doParamsConfirmed)
  
  
    def doParamsConfirmed(self):
      #directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
      #planner_save_location = os.path.join(directory, "saves")
      #fileName = os.path.join(planner_save_location,"results.csv")

      folder = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                            master_mapping_config.INPUT_FOLDER)
      os.makedirs(folder, exist_ok=True)
      tertiary_results = []
      result_file_name = master_mapping_config.CMM_WIZARD_RESULT_FILE_NAME
      if result_file_name in os.listdir(folder):
        with open(os.path.join(folder, result_file_name), newline='') as csvfile:
          reader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
          for row in reader:
            if row and row[0].startswith("tertiary_"):
              tertiary_results.append(row)

      print(tertiary_results)
      fileName = os.path.join(folder, result_file_name)

      keyHOT = "High Temperature"
      keyMEDIUM = "Medium Temperature"
      keyLOW = "Low Temperature"
      keyDHW = "DHW"
      keyCOOLING =  "COOLING"
      resHeatHot={}
      resHeatMedium={}
      resHeatLow={}
      resDHW={}
      resCOOLING={}
      
      resHeatHot[keyHOT] = float(self.doGetHighHeating())
      resHeatMedium[keyMEDIUM] = float(self.doGetMediumHeating())
      resHeatLow[keyLOW] = float(self.doGetLowHeating())
      resDHW[keyDHW] = float(self.doGetUsefulDHW())
      resCOOLING[keyCOOLING] = float(self.doGetUsefulCOOLING())
                
      # here open the file csv and save values on it    
      f = open(fileName, "w", newline= '')
      
      with f as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)    
        
        
        for energy in resHeatHot.keys():
          spamwriter.writerow(['residential_heating_hot_extracted_MWh_y_' + ""] + [(resHeatHot[energy])])
          
        for energy in resHeatMedium.keys():
          spamwriter.writerow(['residential_heating_medium_extracted_MWh_y_' + ""] + [(resHeatMedium[energy])])
          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeatMedium[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
     
        for energy in resHeatLow.keys():
          spamwriter.writerow(['residential_heating_low_extracted_MWh_y_' + ""] + [(resHeatLow[energy])])
          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeatLow[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)

        for energy in resDHW.keys():
          spamwriter.writerow(['residential_heating_dhw_extracted_MWh_y_' + ""] + [(resDHW[energy])])
          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resDHW[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
                         
        for energy in resCOOLING.keys():
          spamwriter.writerow(['residential_heating_cooling_extracted_MWh_y_' + ""] + [(resCOOLING[energy])])

        for energy in tertiary_results:
          spamwriter.writerow(energy)

      
      
        QMessageBox.about(self,'Info!', 'The file results.csv has been created!')
      
      self.close()
      
  
    def __init__(self,parent=None):
        super(AddUsefulEnergySourceDlg, self).__init__(parent)
        
        # link the ui files to the code
        self.setupUi(self)
        # ... slots
        self.doConnectActions()
        self.doSetDoubleSpinBoxValues()
      
  
  
