## -*- coding: utf-8 -*-
#"""
#Created on Mon Mar 19 12:48:11 2018
#
#@author: SALFE
#"""
#
#import os
#import sys
#import json
#from PyQt5 import uic
#from PyQt5 import QtCore
#from PyQt5 import QtGui
#from PyQt5 import QtWidgets
#from PyQt5 import Qt
#from PyQt5.QtCore import pyqtSlot
#from PyQt5.QtGui import *
#from PyQt5.QtCore import *
#from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QMessageBox
#from qgis.core import QgsMessageLog
#
#FORM_CLASS, _ = uic.loadUiType(os.path.join(
#    os.path.dirname(__file__), 'mapping_module_page2.ui'), resource_suffix='')
#
##9be5ff
##ffb8b9
#styleCooling  = "background-color: #9be5ff"
#styleHeating  = "background-color: #ffb8b9"
#
#class WizardPage2(QtWidgets.QWizardPage, FORM_CLASS):
#
#    def doPrepareTableWidgetSummary(self):
#        self.tableWidgetOverallResultsHeatingDHW.setHorizontalHeaderLabels("Tot. heat extracted - HP [MWh/y];Tot. electricity consumed - HP [MWh/y]; % on total useful energy demand".split(";"))          
#        self.tableWidgetOverallResultsCOOLING.setHorizontalHeaderLabels("Tot. heat extracted - HP [MWh/y];Tot. electricity consumed - HP [MWh/y]; % on total useful energy demand".split(";"))          
#    
#    def doRegisterFieldForNextPage(self):
#        self.lineEditOverallHEATING_DHW.hide()
#        self.lineEditOverallCOOLING.hide()
#        self.registerField("overall_results_heating_dhw",self.lineEditOverallHEATING_DHW)    
#        self.registerField("overall_results_cooling",self.lineEditOverallCOOLING) 
#
#
#        self.lineEditFinalResultsHEATING_DHW.hide()
#        self.lineEditFinalResultsCOOLING.hide()
#        self.registerField("final_results_heating_dhw",self.lineEditFinalResultsHEATING_DHW)    
#        self.registerField("final_results_cooling",self.lineEditFinalResultsCOOLING)       
#        
#    def doFillControlsWithResults(self):
#        #final results will be processed later
#        self.lineEditFinalResultsHEATING_DHW.setText(self.prevPageFinalResultsHEATING_DHW)
#        self.lineEditFinalResultsCOOLING.setText(self.prevPageFinalResultsCOOLING)        
#        #heat
#        resHeat = {}
#        resEnCons = {}
#        resPercUsefEnergy = {}
#        
#        self.lineEditOverallHEATING_DHW.setText(self.prevPageResultsHEATING_DHW)
#        if (self.prevPageResultsHEATING_DHW != ""):
#            self.tableWidgetOverallResultsHeatingDHW.clearContents()
#            items = self.prevPageResultsHEATING_DHW.split("+")
#            if (len (items) > 0):
#                for item in items:
#                    values = item.split("#")
#                    if (len (values) == 4):
#                        resHeat[values[0]] = float(values[1])     
#                        resEnCons[values[0]] = float(values[2]  )
#                        resPercUsefEnergy[values[0]] = float(values[3])
#                    else:
#                        QMessageBox.about(self, 'info!', 'Sorry! Wrong results format. ' + str(len (values)))
#                verticalHeaders = ""
#                for energyName in resHeat:
#                    verticalHeaders = verticalHeaders + energyName + ";"
#                verticalHeaders = verticalHeaders[:-1]
#                self.tableWidgetOverallResultsHeatingDHW.setRowCount(len(resHeat))
#                self.tableWidgetOverallResultsHeatingDHW.setVerticalHeaderLabels(verticalHeaders.split(";"))
#                rowCont = 0
#                for energy in resHeat:
#                    self.tableWidgetOverallResultsHeatingDHW.setItem(rowCont,0, QTableWidgetItem("{0:.4f}".format(resHeat[energy])))
#                    self.tableWidgetOverallResultsHeatingDHW.setItem(rowCont,1, QTableWidgetItem("{0:.4f}".format(resEnCons[energy])))
#                    self.tableWidgetOverallResultsHeatingDHW.setItem(rowCont,2, QTableWidgetItem("{0:.4f}".format(resPercUsefEnergy[energy])))
#                    rowCont += 1
#                self.tableWidgetOverallResultsHeatingDHW.resizeColumnsToContents()
#            else:
#                QMessageBox.about(self, 'info!', 'Sorry! Wrong results format for heat+dhw.' + str(len (items)))
#      
#        resHeat.clear()
#        resEnCons.clear()
#        resPercUsefEnergy.clear()
#        self.lineEditOverallCOOLING.setText(self.prevPageResultsCOOLING)
#        if (self.prevPageResultsCOOLING != ""):
#            self.tableWidgetOverallResultsCOOLING.clearContents()
#            items = self.prevPageResultsCOOLING.split("+")
#            if (len (items) > 0):
#                for item in items:
#                    values = item.split("#")
#                    if (len (values) == 4):
#                        resHeat[values[0]] = float(values[1])     
#                        resEnCons[values[0]] = float(values[2] ) 
#                        resPercUsefEnergy[values[0]] = float(values[3])
#                    else:
#                        QMessageBox.about(self, 'info!', 'Sorry! Wrong results format. ' + str(len (values)) )
#                verticalHeaders = ""
#                for energyName in resHeat:
#                    verticalHeaders = verticalHeaders + energyName + ";"
#                verticalHeaders = verticalHeaders[:-1]
#                self.tableWidgetOverallResultsCOOLING.setRowCount(len(resHeat))
#                self.tableWidgetOverallResultsCOOLING.setVerticalHeaderLabels(verticalHeaders.split(";"))
#                rowCont = 0
#                for energy in resHeat:
#                    self.tableWidgetOverallResultsCOOLING.setItem(rowCont,0, QTableWidgetItem("{0:.4f}".format(resHeat[energy])))
#                    self.tableWidgetOverallResultsCOOLING.setItem(rowCont,1, QTableWidgetItem("{0:.4f}".format(resEnCons[energy])))
#                    self.tableWidgetOverallResultsCOOLING.setItem(rowCont,2, QTableWidgetItem("{0:.4f}".format(resPercUsefEnergy[energy])))
#                    rowCont += 1
#                self.tableWidgetOverallResultsCOOLING.resizeColumnsToContents()
#            else:
#                QMessageBox.about(self, 'info!', 'Sorry! Wrong results format for cooling.' + str(len (items)))
#                 
#    def __init__(self, parent=None):
#        super(WizardPage2, self).__init__(parent)
#        self.setupUi(self)
#        self.doPrepareTableWidgetSummary()
#        self.prevPageResultsHEATING_DHW = ""
#        self.prevPageResultsCOOLING = ""
#        self.prevPageFinalResultsHEATING_DHW = ""
#        self.prevPageFinalResultsCOOLING = ""
#        self.doRegisterFieldForNextPage()
#        
#    def initializePage(self):
#        self.prevPageResultsHEATING_DHW = self.field("resultsPage1_HEATING_DHW")
#        self.prevPageResultsCOOLING = self.field("resultsPage1_COOLING")  
#        self.prevPageFinalResultsHEATING_DHW = self.field("finalresultsHEATING_DHW")
#        self.prevPageFinalResultsCOOLING = self.field("finalresultsCOOLING")          
#        self.doFillControlsWithResults()          
#                    
