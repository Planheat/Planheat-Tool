# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:11:28 2018

@author: SALFE
"""

import os
import re
import json
import csv
from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsMessageLog,Qgis
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QMessageBox,QTreeWidgetItem
from .solutionCompleteResults import createRootNodeCompleteResults
from .HeatingNodeType import HeatingNodeType
from .Technology import Technology

# Softeco updates 14/05/2019
from .save_utils.SaveScenario import SaveScenario

from ... import master_mapping_config


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'baseline_useful_demand_details.ui'), resource_suffix='')

styleInNormal  = "color: green; background-color: #cbffcf "
styleReadOnly  = "color: green; background-color: #ffff7f"

  
class BaselineUsefulDemandResults(QtWidgets.QDialog, FORM_CLASS):

    # Softeco updates 05/2019
    def doGenerateOutputJson(self):
        #if self.working_directory is not None:
        #    folder = os.path.join(self.working_directory, "Mapping_wizard", "Saves")
        #    try:
        #        os.makedirs(folder, exist_ok=True)
        #    except:
        #        print("usefulDemandDetails.py, doGenerateOutputJson(). Error, impossibile create folder!")
        #        folder = None
        #else:
        #    folder = None
        folder = os.path.join(  master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                master_mapping_config.CMM_BASELINE_FOLDER,
                                master_mapping_config.CMM_WIZARD_FOLDER)
        save = SaveScenario(folder=folder)
        save.add_tree_widget_to_saved_data(self.treeWidgetHEATING_DHW)
        save.add_tree_widget_to_saved_data(self.treeWidgetCOOLING)

        save.add_tree_widget_to_saved_data(self.lineEditTotal_HEATING_SBS_DHN)           
        save.add_tree_widget_to_saved_data(self.lineEditTotal_HEATING_SBS)
        save.add_tree_widget_to_saved_data(self.lineEditTotal_HEATING_DHN) 
        save.add_tree_widget_to_saved_data(self.lineEditTotal_COOLING_SBS_DCN)

        valid = False
        space = "                                       "
        while not valid:
            #text, ok_pressed = QInputDialog.getText(self, "Enter file name",
            #                                        "Enter file name to store results data" + space,
            #                                        QLineEdit.Normal, "")

            text, ok_pressed = "CMM_wizard", True


            try:
                if ok_pressed:
                    if not self.check_file_name(text):
                        message = "File names must not contain any of the following symbols: \n/\\?%*:|\"><. or whitespaces"
                        msgBox = QMessageBox()
                        msgBox.setText("Invalid file name.")
                        msgBox.setInformativeText(message)
                        msgBox.setStandardButtons(QMessageBox.Ok)
                        msgBox.setDefaultButton(QMessageBox.Ok)
                        msgBox.exec()
                    else:
                        valid = True
                else:
                    message = "You can any time click the Export button to save data in the project folder."
                    msgBox = QMessageBox()
                    msgBox.setText("Info:")
                    msgBox.setInformativeText(message)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.setDefaultButton(QMessageBox.Ok)
                    msgBox.exec()
                    valid = True
                    text = None
            except:
                pass
        if text is None:
            return
        if self.sector == "Residential Sector":
            file_name = text + "_R.json"
        elif self.sector == "Tertiary Sector":
            file_name = text + "_T.json"
        else:
            message = "Sector not defined in planheatmappingwizard/usefulDemandDetails.py(). Check source code."
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("ERROR: File not created!")
            msgBox.setInformativeText(message)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec()
            print(self.sector)
            return
        save.save(file_name, exist_ok=False)
        message = "Export success!\nFile {0} created".format(file_name)
        msgBox = QMessageBox()
        msgBox.setText("Info:")
        msgBox.setInformativeText(message)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec()
        self.pushButtonExport.setEnabled(False)
        self.pushButtonExport_2.setEnabled(False)
        self.pushButtonExport.setToolTip("Export already executed.")
        self.pushButtonExport_2.setToolTip("Export already executed.")


    # Softeco updates 05/2019
    def check_file_name(self, text):
        if text == "":
            return False
        if "/" in text:
            return False
        if "\\" in text:
            return False
        if "?" in text:
            return False
        if "!" in text:
            return False
        if "%" in text:
            return False
        if "*" in text:
            return False
        if ":" in text:
            return False
        if "|" in text:
            return False
        if "\"" in text:
            return False
        if "<" in text:
            return False
        if ">" in text:
            return False
        if "." in text:
            return False
        if " " in text:
            return False
        return True

    def doClear(self):
        self.treeWidgetHEATING_DHW.clear()  
        self.treeWidgetCOOLING.clear()  
        self.doPrepareTreeViewSolutions()

    def doAddRootNodeToTreeCompleteResults(self,treeView,name):
        icon_path=''
        if (name == 'Electricity'):  
            icon_path = ':/images/lightbulb.png'
        elif (name == 'Natural gas'):   
            icon_path = ':/images/naturalGas.png'    
        elif (name == 'Biomass'):
            icon_path = ':/images/biomass.png'
        elif (name == 'Waste heat'):  
            icon_path = ':/images/wasteHeat.png'
        elif (name == 'Geothermal'):  
            icon_path = ':/images/geotermal.png'
        elif (name == 'Heating oil'):  
            icon_path = ':/images/heatingOil.png'
        elif (name == 'Coal'): 
            icon_path = ':/images/coal.png'
        elif (name == 'Solar'):
            icon_path = ':/images/solar.png'
        else:
            QMessageBox.about(self, 'Info', 'Sorry! Failed to add the element!')
        rootnodeResults = createRootNodeCompleteResults (treeView, name,icon_path)
        return rootnodeResults 
    
    
########## Functions that are needed to add the elements to the tree
    def doAddChildToCompleteResultsTree(self, parent, stype="",icon=""):
        treeItem = HeatingNodeType(parent,stype,icon)
        if (parent != None):
            parent.addChild(treeItem) 
            return treeItem
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed to append a tree item.')           
    
    
    def doPrepareTreeViewSolutions(self):   
        # prepare the tree for the HEATING+DHW case....
        self.treeWidgetHEATING_DHW.setRootIsDecorated(True)
        self.treeWidgetHEATING_DHW.setColumnCount(5)
        self.treeWidgetHEATING_DHW.setHeaderLabels(("Energy source;HEATING useful demand;DHW useful demand ; Total useful demand ;Share of useful energy demand [%]").split(";"))
        self.treeWidgetHEATING_DHW.expandAll()  
        self.treeWidgetHEATING_DHW.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        # and do the same in the case of COOLING
        
        self.treeWidgetCOOLING.setRootIsDecorated(True)
        self.treeWidgetCOOLING.setColumnCount(2)
        self.treeWidgetCOOLING.setHeaderLabels(("Energy source; Total useful demand COOLER ;Share of useful energy demand [%]").split(";"))
        self.treeWidgetCOOLING.expandAll()  
        self.treeWidgetCOOLING.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        # create the root nodes in case of HEATING_DHW
        self.rootElectricity = self.doAddRootNodeToTreeCompleteResults (self.treeWidgetHEATING_DHW, 'Electricity')
        self.rootGas = self.doAddRootNodeToTreeCompleteResults(self.treeWidgetHEATING_DHW, 'Natural gas')
        self.rootBiomass = self.doAddRootNodeToTreeCompleteResults (self.treeWidgetHEATING_DHW, 'Biomass')
        self.rootWaste = self.doAddRootNodeToTreeCompleteResults (self.treeWidgetHEATING_DHW, 'Waste heat')
        self.rootGeothermal = self.doAddRootNodeToTreeCompleteResults (self.treeWidgetHEATING_DHW, 'Geothermal')
        self.rootHeatingOil = self.doAddRootNodeToTreeCompleteResults(self.treeWidgetHEATING_DHW, 'Heating oil')
        self.rootCoal = self.doAddRootNodeToTreeCompleteResults(self.treeWidgetHEATING_DHW, 'Coal')
        self.rootSolar = self.doAddRootNodeToTreeCompleteResults (self.treeWidgetHEATING_DHW, 'Solar')
        
        # create the root nodes in case of HEATING_DHW
        self.rootElectricityCOOLING = self.doAddRootNodeToTreeCompleteResults (self.treeWidgetCOOLING, 'Electricity')
        self.rootGasCOOLING = self.doAddRootNodeToTreeCompleteResults(self.treeWidgetCOOLING, 'Natural gas')
        self.rootWasteCOOLING = self.doAddRootNodeToTreeCompleteResults(self.treeWidgetCOOLING, 'Waste heat')
        self.rootGeothermalCOOLING = self.doAddRootNodeToTreeCompleteResults(self.treeWidgetCOOLING, 'Geothermal')
        
    def doConvertFloatToString(self,fval):
        return "{0:.1f}".format(float(fval))

    def doUpdateBaselineBox(self, total_HEATING_DHW_SBS, total_HEATING_DHW_DHN, total_COOLER_SBS, total_COOLER_DCN):
        # compute the penetration factors associated with SBS and DHN , SBS and DCN 
        shareSBS_HEATING=0
        shareDHN_HEATING=0
        shareSBS_COOLING=0
        shareDCN_COOLING=0
        #compute the total useful demand SBS and DHN
        total_SBS_DHN= total_HEATING_DHW_SBS + total_HEATING_DHW_DHN
        total_SBS_DCN = total_COOLER_SBS + total_COOLER_DCN
             
        # compute the penetration factors
        if (total_SBS_DHN !=0 and total_SBS_DCN!=0):
          shareSBS_HEATING = int((float(total_HEATING_DHW_SBS)/float(total_SBS_DHN))*100)
          shareDHN_HEATING = int((float(total_HEATING_DHW_DHN)/float(total_SBS_DHN))*100)
          self.lineEditTotal_HEATING_SBS_DHN.setText(self.doConvertFloatToString(total_SBS_DHN) + "" + "|" + str(shareSBS_HEATING + shareDHN_HEATING) + '%')           
          self.lineEditTotal_HEATING_SBS.setText(self.doConvertFloatToString(total_HEATING_DHW_SBS) + "" + "|" + str(shareSBS_HEATING) + '%')
          self.lineEditTotal_HEATING_DHN.setText(self.doConvertFloatToString(total_HEATING_DHW_DHN) + "" + "|" + str(shareDHN_HEATING) + '%') 
          
          shareSBS_COOLING = int((float(total_COOLER_SBS)/float(total_SBS_DCN))*100)
          shareDCN_COOLING = int((float(total_COOLER_DCN)/float(total_SBS_DCN ))*100)
          self.lineEditTotal_COOLING_SBS_DCN.setText(self.doConvertFloatToString(total_SBS_DCN) + "" + "|" + str(shareSBS_COOLING + shareDCN_COOLING) + '%')  
          self.lineEditCOOLING_SBS.setText(self.doConvertFloatToString(total_COOLER_SBS) + "" + "|" + str(shareSBS_COOLING) + '%')
          self.lineEditCOOLING_DCN.setText(self.doConvertFloatToString(total_COOLER_DCN) + "" + "|" + str(shareDCN_COOLING) + '%')        
        else:
          shareSBS_COOLING=0
          shareDCN_COOLING=0
          shareSBS_HEATING = int((float(total_HEATING_DHW_SBS)/float(total_SBS_DHN))*100) if float(total_SBS_DHN) != 0 else 0
          shareDHN_HEATING = int((float(total_HEATING_DHW_DHN)/float(total_SBS_DHN))*100) if float(total_SBS_DHN) != 0 else 0
          self.lineEditTotal_HEATING_SBS_DHN.setText(self.doConvertFloatToString(total_SBS_DHN) + "" + "|" + str(shareSBS_HEATING + shareDHN_HEATING) + '%')           
          self.lineEditTotal_HEATING_SBS.setText(self.doConvertFloatToString(total_HEATING_DHW_SBS) + "" + "|" + str(shareSBS_HEATING) + '%')
          self.lineEditTotal_HEATING_DHN.setText(self.doConvertFloatToString(total_HEATING_DHW_DHN) + "" + "|" + str(shareDHN_HEATING) + '%') 
          self.lineEditTotal_COOLING_SBS_DCN.setText(self.doConvertFloatToString(total_SBS_DCN) + "" + "|" + str(shareSBS_COOLING + shareDCN_COOLING) + '%')  
          self.lineEditCOOLING_SBS.setText(self.doConvertFloatToString(total_COOLER_SBS) + "" + "|" + str(shareSBS_COOLING) + '%')
          self.lineEditCOOLING_DCN.setText(self.doConvertFloatToString(total_COOLER_DCN) + "" + "|" + str(shareDCN_COOLING) + '%')                
          
          
    def doUpdateTree_HEAT(self,dictResults):
        # save the value into a global variable
        self.dictResults = dictResults
        #QgsMessageLog.logMessage('Dictionary:' + str(dictResults), tag = 'doUpdateTree_HEAT', level= Qgis.Info)  
        for key, value in self.dictResults.items():
            #QgsMessageLog.logMessage('Dictionary value:' + str(value), tag = 'doUpdateTree_HEAT', level= Qgis.Info)  
            targetTree = QtWidgets.QTreeWidgetItem(value)
            targetTree.setTextAlignment(QtCore.Qt.AlignHCenter, QtCore.Qt.AlignVCenter)
            if 'COOLING' not in key:            
                if 'Electricity' in key:
                    self.rootElectricity.addChild(targetTree)
                elif 'Gas' in key:
                    self.rootGas.addChild(targetTree)
                elif 'Biomass' in key:
                    self.rootBiomass.addChild(targetTree)    
                elif 'Coal' in key:
                    self.rootCoal.addChild(targetTree)
                elif 'Geothermal' in key:
                    self.rootGeothermal.addChild(targetTree)
                elif 'Heating oil' in key:
                    self.rootHeatingOil.addChild(targetTree)
                elif 'Solar' in key:
                    self.rootSolar.addChild(targetTree)
                elif 'Waste' in key:
                    self.rootWaste.addChild(targetTree)             
                
                
    def doUpdateTree_COOLING(self,dictResultsCOOLING):
       # QgsMessageLog.logMessage('Dictionary:' + str(dictResultsCOOLING), tag = 'doUpdateTree_COOLING', level= Qgis.Info)  
       # save the results 
        self.dictResults_COOLING = dictResultsCOOLING
        for key,value in dictResultsCOOLING.items():
            #QgsMessageLog.logMessage('Dictionary value:' + str(value), tag = 'doUpdateTree_COOLING', level= Qgis.Info)  
            targetTree = QtWidgets.QTreeWidgetItem(value)
            targetTree.setTextAlignment(QtCore.Qt.AlignHCenter, QtCore.Qt.AlignVCenter)
            if 'Electricity' in key:
                self.rootElectricityCOOLING.addChild(targetTree)
            elif 'Gas' in key:
                self.rootGasCOOLING.addChild(targetTree)
            elif 'Geothermal' in key:
                self.rootGeothermalCOOLING.addChild(targetTree)
            elif 'Waste':
                self.rootWasteCOOLING.addChild(targetTree)
                
                
    def doFillTable_HEATING_DHW(self,dictResultsTABLE_HEAT):
        headerCount = self.tableWidgetHEATING_DHW.columnCount()
        rowCount = self.tableWidgetHEATING_DHW.rowCount()
        indexColumn=0
        indexColumn1=0
        indexColumn2=0
        totalFinal_HP=0
        totalFinal=0
        v =0
        v1=0
        items=[]

        self.dictResultsTABLE_HEAT = dictResultsTABLE_HEAT

        QgsMessageLog.logMessage('Dict results' + "" + str(self.dictResultsTABLE_HEAT), tag = "doFillTable_HEATING_DHW", level= Qgis.Info)
        
        for key,value in self.dictResultsTABLE_HEAT.items():
            a,b = key.split("+")
            items = b.split(" ")
            
            if 'HP' in key and not 'CHP' in key:    
              v= value[0]
              v1 = value[1] 
              totalFinal_HP += float(v)
              for x in range(0, headerCount, 1):
                headerText = self.tableWidgetHEATING_DHW.horizontalHeaderItem(x).text()  
                for z in range(0, rowCount, 1):
                  verticalHeaderText = self.tableWidgetHEATING_DHW.verticalHeaderItem(z).text()
                  if items[1] in headerText.strip() and items[0] == verticalHeaderText.strip():
                    if (v1 !=0): 
                      indexColumn= x
                      rowPosition= z
                      newItem_ADDITIONAL = QtWidgets.QTableWidgetItem()
                      newItem_ADDITIONAL.setText(str(v1))                  
                      if (newItem_ADDITIONAL != None):                              
                        self.tableWidgetHEATING_DHW.setItem(rowPosition,indexColumn,newItem_ADDITIONAL)
                  
              for y in range(0, headerCount, 1):
                headerText = self.tableWidgetHEATING_DHW.horizontalHeaderItem(y).text()  
                for k in range(0, rowCount, 1):
                  verticalHeaderText = self.tableWidgetHEATING_DHW.verticalHeaderItem(k).text()
                  if a == headerText.strip() and items[0] == verticalHeaderText.strip():                
                    if (v !=0):    
                        indexColumn1= y
                        rowPosition= k
                        newItemTotal_TOTAL = QtWidgets.QTableWidgetItem()
                        newItemTotal_TOTAL.setText(str(totalFinal_HP))
                        if (newItemTotal_TOTAL !=None):      
                          self.tableWidgetHEATING_DHW.setItem(rowPosition,indexColumn1,newItemTotal_TOTAL)

            else:           
              if (value !=0):
                totalFinal += float(value)
                for y in range(0, headerCount, 1):
                  headerText = self.tableWidgetHEATING_DHW.horizontalHeaderItem(y).text()  
                  for k in range(0, rowCount, 1):
                    verticalHeaderText = self.tableWidgetHEATING_DHW.verticalHeaderItem(k).text()
                    if a == headerText.strip()and b == verticalHeaderText.strip():  
                        indexColumn2= y
                        rowPosition= k
                        newItem_TOTAL_FINAL_NO_HP = QtWidgets.QTableWidgetItem()
                        newItem_TOTAL_FINAL_NO_HP.setText(str(totalFinal))
                        if (newItem_TOTAL_FINAL_NO_HP  !=None):      
                          self.tableWidgetHEATING_DHW.setItem(rowPosition,indexColumn2,newItem_TOTAL_FINAL_NO_HP)
                
   
    def doFillTable_COOLING(self,dictResultsTABLE_COOLING):
        headerCount = self.tableWidgetCOOLING.columnCount()
        rowCount = self.tableWidgetCOOLING.rowCount()
        indexColumn=0
        rowPosition=0
        v =0
        v1=0
        items=[]
        totalAdditional=0
        totalFinal_COOLING=0
  
        self.dictResultsTABLE_COOLING = dictResultsTABLE_COOLING
        
        for key,value in self.dictResultsTABLE_COOLING.items():
            a,b = key.split("+")
            items = b.split(" ")
  
            if 'HP' in key and not 'CHP' in key:    
              v= value[0]
              v1 = value[1]   
              totalAdditional += float(v1)
              totalFinal_COOLING += float(v) 
              for x in range(0, headerCount, 1):
                headerText = self.tableWidgetCOOLING.horizontalHeaderItem(x).text()  
                for z in range(0, rowCount, 1):
                  verticalHeaderText = self.tableWidgetCOOLING.verticalHeaderItem(z).text()
                  if items[1] in headerText.strip() and items[0] == verticalHeaderText.strip():
                    if (v1 !=0):   
                      indexColumn= x
                      rowPosition= z
                      newItem_ADDITIONAL = QtWidgets.QTableWidgetItem()
                      newItem_ADDITIONAL.setText(str(v1))
                      if (newItem_ADDITIONAL!= None):                              
                        self.tableWidgetCOOLING.setItem(rowPosition,indexColumn,newItem_ADDITIONAL)
                        
                
                QgsMessageLog.logMessage('Total final:' + str(totalFinal_COOLING), tag= 'doFillTable_COOLING', level = Qgis.Info)
                for y in range(0, headerCount, 1):
                  headerText = self.tableWidgetCOOLING.horizontalHeaderItem(y).text()  
                  for k in range(0, rowCount, 1):
                    verticalHeaderText = self.tableWidgetCOOLING.verticalHeaderItem(k).text() 
                    if a == headerText.strip() and items[0] == verticalHeaderText.strip():
                      QgsMessageLog.logMessage('header vertical' + verticalHeaderText.strip(), tag= 'doFillTable_COOLING', level = Qgis.Info)
                      if (v !=0):
                        indexColumn= y
                        rowPosition= k
                        newItemTotal_TOTAL=QtWidgets.QTableWidgetItem()
                        newItemTotal_TOTAL.setText(str(totalFinal_COOLING))
                        if (newItemTotal_TOTAL !=None):     
                          self.tableWidgetCOOLING.setItem(rowPosition,indexColumn,newItemTotal_TOTAL)                                         
  
            else:               
              if (value !=0):
                totalFinal_COOLING += float(value)
                QgsMessageLog.logMessage('Total no HP' + str(totalFinal_COOLING), tag = 'doFillTable_COOLING', level = Qgis.Info )
                for y in range(0, headerCount, 1):
                  headerText = self.tableWidgetCOOLING.horizontalHeaderItem(y).text()  
                  for k in range(0, rowCount, 1):
                    verticalHeaderText = self.tableWidgetCOOLING.verticalHeaderItem(k).text()
                    if a == headerText.strip() and b == verticalHeaderText.strip():     
                        indexColumn2= y
                        rowPosition= k
                        newItem_FINAL_NO_HP = QtWidgets.QTableWidgetItem()
                        newItem_FINAL_NO_HP.setText(str(totalFinal_COOLING))                       
                        if (newItem_FINAL_NO_HP != None):      
                          self.tableWidgetCOOLING.setItem(rowPosition,indexColumn2,newItem_FINAL_NO_HP) 



    def doSumColumnValues(self):
        table = None
        table_COOLING = None
        val =0 
        val_COOLING=0
        # first calculate the sum of the tableWidgetHEATING_DHW column
        val = sum([float(item.text()) for item in self.tableWidgetHEATING_DHW.selectedItems()])
        table = QtWidgets.QTableWidgetItem()
        table.setText(str(val))
        column= self.tableWidgetHEATING_DHW.currentColumn()
        self.tableWidgetHEATING_DHW.setItem(9,column, table) 
        
        val_COOLING = sum([float(item.text()) for item in self.tableWidgetCOOLING.selectedItems()])
        table_COOLING = QtWidgets.QTableWidgetItem()
        table_COOLING.setText(str(val_COOLING))
        column= self.tableWidgetCOOLING.currentColumn()
        self.tableWidgetCOOLING.setItem(9,column, table_COOLING)         

    def doCancelTableTotal(self):
        table = None
        table_COOLING = None
      
        for item in self.tableWidgetHEATING_DHW.selectedItems():
          table = QtWidgets.QTableWidgetItem()
          table.setText(" ")
          column = self.tableWidgetHEATING_DHW.currentColumn()
          self.tableWidgetHEATING_DHW.setItem(9,column, table_COOLING) 
        
        for item in self.tableWidgetCOOLING.selectedItems():
          table_COOLING = QtWidgets.QTableWidgetItem()
          table_COOLING.setText(" ")
          column = self.tableWidgetCOOLING.currentColumn()
          self.tableWidgetCOOLING.setItem(9,column, table_COOLING) 


    #EXPORT THE BASELINE
    def doExportBaselineUsefulOnCsv(self):
      
      # adding the values associated with the groupbox before saving on the csv
      #self.dictResults.update({'total_SBS_DHN_HEATING': str(self.lineEditTotal_HEATING_SBS_DHN.text()), 'SBS_HEATING': str(self.lineEditTotal_HEATING_SBS.text()) , 'DHN_HEATING':str(self.lineEditTotal_HEATING_DHN.text())})
      #self.dictResults_COOLING.update({'total_SBS_DHN_COOLING': str(self.lineEditTotal_COOLING_SBS_DCN.text()), 'SBS_COOLING': str(self.lineEditCOOLING_SBS.text()), 'DCN_COOLING': str(self.lineEditCOOLING_DCN.text())})
      
      #QgsMessageLog.logMessage("dictResults_Updated" + "" + str(self.dictResults), tag = "doExportBaselineFinalOnCsv", level = Qgis.Info)
      #QgsMessageLog.logMessage("dictResults_Updated" + "" + str(self.dictResults_COOLING), tag = "doExportBaselineFinalOnCsv", level = Qgis.Info)
      
      with open(r'C:\Users\giurt\Desktop\ExportedBaselineUsefulHEATING_DHW.csv','w',newline='') as csv_file:
        wr = csv.writer(csv_file)
        if self.dictResults != {}:    
          for key,value in self.dictResults.items():
            wr.writerow([key,value])           
        else:
          return True
          
        
      
      with open(r'C:\Users\giurt\Desktop\ExportedBaselineUsefulCOOLING.csv','w', newline ='') as csv_file:
        wr = csv.writer(csv_file)
        if self.dictResults_COOLING != {}:
          for key,value in self.dictResults_COOLING.items():
            wr.writerow([key,value]) 
        else:
          return True
          
                  
      
    # EXPORT THE FINAL  
    def writeFinalOnCsv(self,dictToBeExportedHEATING,dictToBeExportedCOOLING):
      with open(r'C:\Users\giurt\Desktop\ExportedBaselineFinalHEATING_DHW.csv','w') as csv_file:
        wr = csv.writer(csv_file)
        QgsMessageLog.logMessage("list of values" + "" + str(dictToBeExportedHEATING), tag = "writeFinalOnCsv", level = Qgis.Info)
        if dictToBeExportedHEATING != {}:
          for key,value in dictToBeExportedHEATING.items():
            wr.writerow([key,value])  
            
            
      with open(r'C:\Users\giurt\Desktop\ExportedBaselineFinalCOOLING.csv','w') as csv_file:
        wr = csv.writer(csv_file)
        QgsMessageLog.logMessage("list of values" + "" + str(dictToBeExportedCOOLING), tag = "writeFinalOnCsv", level = Qgis.Info)
        if dictToBeExportedCOOLING != {}:
          for key,value in dictToBeExportedCOOLING.items():
            wr.writerow([key,value])   

    
    def doExportBaselineFinalOnCsv(self):
      # dictResultsHEATING_DHW={}
      # dictResultsCOOLING={}
      # for row in range(self.tableWidgetHEATING_DHW.rowCount()):
      #   rowdata = []
      #   for column in range(self.tableWidgetHEATING_DHW.columnCount()):
      #     item = self.tableWidgetHEATING_DHW.item(row,column)
      #     if item is not None:
      #       rowdata.append(item.text())
      #       dictResultsHEATING_DHW[self.tableWidgetHEATING_DHW.verticalHeaderItem(row).text()] = rowdata
      #       QgsMessageLog.logMessage("dict:" + "" + str( dictResultsHEATING_DHW), tag = "doExportBaselineFinalOnCsv", level = Qgis.Info)
      #
      # for row in range(self.tableWidgetCOOLING.rowCount()):
      #   rowdataCOOLING = []
      #   for column in range(self.tableWidgetCOOLING.columnCount()):
      #     item = self.tableWidgetCOOLING.item(row,column)
      #     if item is not None:
      #       rowdataCOOLING.append(item.text())
      #       dictResultsCOOLING[self.tableWidgetCOOLING.verticalHeaderItem(row).text()] = rowdataCOOLING
      #       QgsMessageLog.logMessage("dict:" + "" + str(dictResultsCOOLING), tag = "doExportBaselineFinalOnCsv", level = Qgis.Info)
      #
      #
      #
      #
      # self.writeFinalOnCsv(dictResultsHEATING_DHW,dictResultsCOOLING)
      #
      # # copy the baseline useful
      # self.doExportBaselineUsefulOnCsv()
        self.doGenerateOutputJson()
#      
    

    # EXPORT BASELINE useful demand assessment
    def doExportBaselineUsefulTotal(self):
      
      
      
      str(self.lineEditTotal_HEATING_SBS_DHN.text())

               
    def doPrepareFinalEnergyTableWidgets(self):
        # set the columns of table widgets
        self.tableWidgetHEATING_DHW.setColumnCount(10)
        self.tableWidgetCOOLING.setColumnCount(10)
        self.tableWidgetHEATING_DHW.setRowCount(10)
        self.tableWidgetCOOLING.setRowCount(10)
        
        #set the vertical header labels
        self.tableWidgetHEATING_DHW.setHorizontalHeaderLabels("Gas; Heating oil;Coal/Peat;Waste heat; Geothermal;Air source;Electricity; Biomass; Solar thermal; Other".split(";"))
        self.tableWidgetCOOLING.setHorizontalHeaderLabels("Gas; Heating oil;Coal/Peat;Waste heat; Geothermal;Air source;Electricity; Biomass; Solar thermal; Other".split(";"))
        self.tableWidgetHEATING_DHW.setVerticalHeaderLabels("HP; GAHP; Heater; Boiler; Comb. Heat & Pow;Heat Exchanger;Thermal collectors;ETC;Other;Total".split(";"))
        self.tableWidgetCOOLING.setVerticalHeaderLabels("HP; GAHP; Heater; Boiler; Comb. Heat & Pow;Heat Exchanger;Thermal collectors;ETC;Other;Total".split(";"))

    def __init__(self, working_directory=None, sector=None, parent=None):
        super(BaselineUsefulDemandResults, self).__init__(parent)
        self.setupUi(self)
        self.working_directory = working_directory
        self.sector = sector
        self.setWindowTitle("Baseline assessment for both final energy demand [MWh/y] and useful energy demand [MWh/y]")
        self.doPrepareTreeViewSolutions()
        self.doPrepareFinalEnergyTableWidgets() 
        self.pushButtonCalculator.clicked.connect(self.doSumColumnValues)
        self.pushButtonCancel.clicked.connect(self.doCancelTableTotal)
        self.pushButtonExport.clicked.connect(self.doExportBaselineFinalOnCsv)
        self.pushButtonExport_2.clicked.connect(self.doExportBaselineFinalOnCsv)
        self.totalFinal=0
        self.dictResultsTABLE_HEAT={}
        self.dictResultsTABLE_COOLING={}
        self.dictResults={}
        self.dictResults_COOLING={}


  
    
    