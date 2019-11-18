# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 14:22:52 2018

@author: SALFE
"""

#!/usr/bin/env python
import sys, os
import csv
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty, pyqtSignal
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox,QWizard
from qgis.core import QgsMessageLog, Qgis
from .WizardPage1 import WizardPage1

from ... import master_mapping_config

class MappingWizard(QtWidgets.QWizard):


    def get_final_results(self,who):
        if (who == "Residential Sector"):
            self.resultsRESIDENTIAL_SECTOR_HEATING_DHW = str(self.page1.listOfElements)
            #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(self.resultsRESIDENTIAL_SECTOR_HEATING), tag = 'get_final_results',level=Qgis.Info)
            self.resultsRESIDENTIAL_SECTOR_COOLING = str(self.page1.totalUsefulEnergyDemandCOOLER_SBS) + "+" + str(self.page1.totalUsefulEnergyDemandCOOLER_DHN)
  
        else:
            self.resultsTERTIARY_SECTOR_HEATING_DHW = str(self.page1.listOfElements)
            self.resultsTERTIARY_SECTOR_COOLING = str(self.page1.totalUsefulEnergyDemandCOOLER_SBS) + "+" + str(self.page1.totalUsefulEnergyDemandCOOLER_DHN)
    
    
    
    def doManageFinish(self):
        self.get_final_results(self.who)
        #name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save results to csv')
        folder = os.path.join(  master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                master_mapping_config.CMM_BASELINE_FOLDER, 
                                master_mapping_config.CMM_WIZARD_FOLDER)
        os.makedirs(folder, exist_ok=True)
        if self.who == "Residential Sector":
          name = [os.path.join(folder, "results_CMM_wizard_R.csv")]
        else:
          name = [os.path.join(folder, "results_CMM_wizard_T.csv")]
        lista =[]
        if ((len(str(name[0]))> 0)):
          if sys.version_info >=(3,0,0):          
              f = open(str(name[0]), 'a')
          #else:
              #f = open(str(name[0]), 'wb')
              
              with f as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)            
                  
                resHeat = {}
                resHeatMedium={}
                resHeatLow={}
                resDHW ={}
                
                #residential sector heating
                if (len(self.resultsRESIDENTIAL_SECTOR_HEATING_DHW) != 0):
                    items = self.resultsRESIDENTIAL_SECTOR_HEATING_DHW.split(",")
                    #spamwriter.writerow(items)
                    #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(items), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
                    if (len(items) > 0):
                      for item in items: 
                        if "[" in item:
                          values = str(item) + "]"
                          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning ciclo For',level=Qgis.Info)  
                        elif "]" in item:
                          values = "[" + str(item)
                         # QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning ciclo For',level=Qgis.Info)  
                        else: 
                          values = "[" + str(item) + "]"
                          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning ciclo For',level=Qgis.Info)  
                        
                        lista.append(values)
                     
                      resHeat[values[0]] = lista[1]
                      resHeatMedium[values[0]] = lista[2]
                      resHeatLow[values[0]] = lista[3]
                      resDHW[values[0]] = lista[4]
                             
                      for energy in resHeat.keys():
                        spamwriter.writerow(['residential_heating_hot_extracted_MWh_y_' + ""] + [(resHeat[energy])])
                        #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeat[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)  
                      
                      for energy in resHeatMedium.keys():
                        spamwriter.writerow(['residential_heating_medium_extracted_MWh_y_' + ""] + [(resHeatMedium[energy])])
                        #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeatMedium[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
                   
                      for energy in resHeatLow.keys():
                        spamwriter.writerow(['residential_heating_low_extracted_MWh_y_' + ""] + [(resHeatLow[energy])])
                        #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeatLow[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
    
                      for energy in resDHW.keys():
                        spamwriter.writerow(['residential_heating_dhw_extracted_MWh_y_' + ""] + [(resDHW[energy])])
                        #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resDHW[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
                                       
                    else:
                        QMessageBox.about(self, 'info!', 'Sorry! Wrong results format for heat+dhw.' + str(len (items)))
                
              # residential cooling
                if (self.resultsRESIDENTIAL_SECTOR_COOLING != ""):  
                   items = self.resultsRESIDENTIAL_SECTOR_COOLING.split("+")
                   #☼QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(items), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)  
                   if (len(items) > 0): 
                        values = float(items[0] + items[1])
                        #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)  
                        spamwriter.writerow(['residential_cooling_extracted_MWh_y_' + ""] + ["[" + str(values) + "]"])      
                   else:
                        QMessageBox.about(self, 'info!', 'Sorry! Wrong results format for heat+dhw.' + str(len (items)))                  
              
                resHeat.clear()
                resHeatMedium.clear()
                resHeatLow.clear()
                resDHW.clear()
                                  
                #tertiary sector heating
                if (len(self.resultsTERTIARY_SECTOR_HEATING_DHW) != 0):
                      items = self.resultsTERTIARY_SECTOR_HEATING_DHW.split(",")
                      #spamwriter.writerow(items)
                      QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(items), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
                      if (len(items) > 0):
                        for item in items: 
                          if "[" in item:
                            values = str(item) + "]"
                            #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning ciclo For',level=Qgis.Info)  
                          elif "]" in item:
                            values = "[" + str(item)
                           # QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning ciclo For',level=Qgis.Info)  
                          else: 
                            values = "[" + str(item) + "]"
                            #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning ciclo For',level=Qgis.Info)  
                          
                          lista.append(values)
                       
                        resHeat[values[0]] = lista[1]
                        resHeatMedium[values[0]] = lista[2]
                        resHeatLow[values[0]] = lista[3]
                        resDHW[values[0]] = lista[4]
                               
                        for energy in resHeat.keys():
                          spamwriter.writerow(['tertiary_heating_hot_extracted_MWh_y_' + ""] + [(resHeat[energy])])
                          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeat[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)  
                        
                        for energy in resHeatMedium.keys():
                          spamwriter.writerow(['tertiary_heating_medium_extracted_MWh_y_' + ""] + [(resHeatMedium[energy])])
                          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeatMedium[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
                     
                        for energy in resHeatLow.keys():
                          spamwriter.writerow(['tertiary_heating_low_extracted_MWh_y_' + ""] + [(resHeatLow[energy])])
                          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resHeatLow[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
      
                        for energy in resDHW.keys():
                          spamwriter.writerow(['tertiary_heating_dhw_extracted_MWh_y_' + ""] + [(resDHW[energy])])
                          #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(resDHW[energy]), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)
                             
                     
                      else:
                          QMessageBox.about(self, 'info!', 'Sorry! Wrong results format for heat+dhw.' + str(len (items)))
                  
                # residential cooling
                if (self.resultsTERTIARY_SECTOR_COOLING != ""):  
                     items = self.resultsTERTIARY_SECTOR_COOLING.split("+")                   
                     if (len(items) > 0): 
                        value = float(items[0] + items[1])
                        #QgsMessageLog.logMessage('results HEATING+DHW:' + "" + str(values), tag = 'exportCsvResultsForPlanning',level=Qgis.Info)  
                        spamwriter.writerow(['tertiary_cooling_extracted_MWh_y_' + ""] + ["[" + str(value) + "]"])      
                     else:
                          QMessageBox.about(self, 'info!', 'Sorry! Wrong results format for heat+dhw.' + str(len (items)))                  
                               
          QMessageBox.about(self, 'info!', 'File successfully created.' ) 
          f.close()              
        else:
          QMessageBox.about(self, 'info!', 'Invalid filename. Cannot export data to csv.' )


                                        
    def __init__(self,who, working_directory=None, parent=None):
        super(MappingWizard, self).__init__(parent)
        self.who = who
        self.working_directory = working_directory
        self.page1 = WizardPage1(working_directory=self.working_directory, sector=who)
        self.addPage(self.page1)
        self.setWindowTitle("Mapping module wizard [" + self.who + "]")
        self.setButtonText(self.FinishButton, "Finish")
        self.setButtonText(self.CancelButton, "Cancel")
        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.doManageFinish)
        self.resize(768,640)
        self.resultsRESIDENTIAL_SECTOR_COOLING=''
        self.resultsRESIDENTIAL_SECTOR_HEATING_DHW=''
        self.resultsTERTIARY_SECTOR_COOLING=''
        self.resultsTERTIARY_SECTOR_HEATING_DHW=''
