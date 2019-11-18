# -*- coding: utf-8 -*-
"""
   Process Thread 
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 10 Oct. 2017
"""

__docformat__ = "restructuredtext"


import sys
import os
import time
import subprocess
import gc
import platform



from json import dumps
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import QThread
from collections import OrderedDict
from src.alternative import Alternative
from src.complete import Complete  
from config import config as Config
from utility.utils import showResults, clean_temp_files
from manageCsv.csv_reader import CSV_Reader
from manageCsv.csv_writer import CSV_Writer
from manageShape.shape_writer import Shape_Writer
from model.building import Building
from manageShape.shape_reader import Shape_Reader
from manageDB.db import DB
from myExceptions.exceptions import NotFoundResourceException, JavaProcessException




class Worker(QThread):
    
    """
        Thread that executes the calculations of the process
    """
    
    showMessageDialog = QtCore.pyqtSignal(str,str,str,object,name='showMessageDialog')
    progress_update = QtCore.pyqtSignal(int,object, name= 'progress_update')
    progress_total = QtCore.pyqtSignal(int,object,name='progress_total')
    changeStatusProcessButton = QtCore.pyqtSignal(str,object,object, name='changeStatusProcessButton')
    message_update = QtCore.pyqtSignal(str,object)
    unlock_interface = QtCore.pyqtSignal(object)
    loadShapeGeneratedFile = QtCore.pyqtSignal(str,str,object, name='loadShapeGeneratedFile')

    def __init__(self,planHeatDMM):
        
        QThread.__init__(self)
         
        
        try:
        
            self.clockThread = ClockThread(planHeatDMM)
            if  planHeatDMM.resources.thread_clock is None: 
                planHeatDMM.resources.thread_clock = self.clockThread
            else:    
                self.clockThread = None
            
                
            self.planHeatDMM = planHeatDMM
            
            self.javaLog =  Config.PLUGIN_DIR + os.path.sep + Config.LOG_PARAMS['path'] + os.path.sep + "java_output_" + planHeatDMM.resources.logDateName + "." + Config.LOG_PARAMS["logExt"]    
            self.fileJsonArg=Config.PLUGIN_DIR + os.path.sep + "temp" + os.path.sep + "planheatjavaargs.json"
            self.fileJava=Config.PLUGIN_DIR + os.path.sep + "java" + os.path.sep + "jre1.8.0_151" +  os.path.sep + "bin" +  os.path.sep
            self.fileJar=self.planHeatDMM.data.fileJar
            self.fileLib=self.planHeatDMM.data.fileLib
            self.mainJavaClass=Config.JAVA_MAIN_CLASS
            
            #Input files
            self.csvInFilename = Config.PLUGIN_DIR + os.path.sep + "temp" + os.path.sep + Config.INTERMEDIATE_FILE_CSV
            self.shapeInFilename              = self.planHeatDMM.data.inputShapeFile
            
            #Baseline Demand
             
            self.shapeOutBaselineFilename     = self.planHeatDMM.data.outputSaveFile
            self.csvOutBaselineFilename       = self.planHeatDMM.data.outputSaveFile + ".csv"
            self.csvOutBaselineTotalFilename  = self.planHeatDMM.data.outputSaveFile + "_totalized.csv"
            self.csvOutBaselineHourlyFilename = self.planHeatDMM.data.outputSaveFile + "_hourly.csv"
            #Future Demand
            self.shapeOutFutureFilename     = self.planHeatDMM.data.outputSaveFile + "_future"
            self.csvOutFutureFilename       = self.planHeatDMM.data.outputSaveFile + "_future.csv"
            self.csvOutFutureTotalFilename  = self.planHeatDMM.data.outputSaveFile + "_future_totalized.csv"
            self.csvOutFutureHourlyFilename = self.planHeatDMM.data.outputSaveFile + "_future_hourly.csv"
            self.threadOptionsLog           = self.planHeatDMM.data.outputSaveFile + "_options.txt" 
            
            self.log = self.planHeatDMM.resources.log
            self.database = None
            self.noa = self.planHeatDMM.resources.noa
            self.planHeatDMM.data.closeWindow = False
            self.dbFileName=Config.DB_PARAMS['databaseName']
          
            self.boolRetrofittedScenarios = self.planHeatDMM.data.boolRetrofittedScenarios 
            self.boolHourlyDetailFile     = self.planHeatDMM.data.boolHourlyDetailFile  
            self.boolAddShapeFields = self.planHeatDMM.data.boolAddShapeFields
            self.userFieldShapeMap  = self.planHeatDMM.data.userFieldShapeMap
          
             
            self.inputCsvFile   = None
            self.inputShpFile   = None
            self.outputDetailBaselineCSVFile    = None
            self.outputTotalizedBaselineCSVFile = None
            self.outputHourlyBaselineCSVFile    = None
            self.outputBaselineSHPFile          = None
            self.outputDetailFutureCSVFile      = None
            self.outputTotalizedFutureCSVFile   = None
            self.outputHourlyFutureCSVFile      = None
            self.outputFutureSHPFile            = None
            
            self.projectName = self.planHeatDMM.data.projectName
            self.areaName = self.planHeatDMM.data.areaName
            self.country_id = self.planHeatDMM.data.country_id
             
            self.folderProject = Config.PLUGIN_DIR +  os.path.sep + "temp" + os.path.sep
            self.shpFilename = self.shapeInFilename 
            self.logFileName = self.planHeatDMM.resources.log.completeFileName
            self.lidarDTMFolder = "" if self.planHeatDMM.data.DTMDirectory is None else self.planHeatDMM.data.DTMDirectory +  os.path.sep
            self.lidarDSMFolder = "" if self.planHeatDMM.data.DSMDirectory is None else self.planHeatDMM.data.DSMDirectory +  os.path.sep
            self.referentialSpaceEPSG =  self.planHeatDMM.data.spatialReferenceEPSG
            self.referentialSpaceWKT = self.planHeatDMM.data.spatialReferenceWKT
            self.fieldMapping= None
            
            self.fieldsSHPJavaPosition = self.planHeatDMM.data.fieldsSHPMappingPosition
            self.buildingUseFloorHeightDict = self.planHeatDMM.data.buildingUseFloorHeightDict
            
            
            self.ok = 0
            self.error = 0
            self.total = 0
            
        except:
            self.showMessageDialog.emit("CRITICAL","Thread Constructor", " __init__ Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]),self.planHeatDMM)    
            self.planHeatDMM.log.write_log("ERROR", "Worker Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                 
    
    def run(self):
        try:
            
            self.log.write_log("INFO","Run Thread")
            
            # Delete temporary files
            # Delete temp files
            if Config.LAUNCH_JAVA_PROCESS in ("Y","y"):
                clean_temp_files(self.log)
            
            
            if  self.clockThread is not None: 
                self.clockThread.start( priority = Config.PROCESS_THREAD_PRIORITY)
            
            # Create DB Connection per Thread 
            self.database = DB(self.log)
            if self.database is None:
                raise Exception("Error Creating Database Object")
            else:
                #Database Connection
                self.database.connectDB("DEFERRED")
                
                
            self.message_update.emit("Process Start",self.planHeatDMM)
            self.progress_update.emit(0,self.planHeatDMM)
            
            self.database.truncate_calculate_complete_totalized_table()
        
            self.planHeatDMM.resources.log.write_log("INFO","Execute")
            self.initizalizeLogExecuteOptions(self.threadOptionsLog)
            self.writeLogExecuteOptions(self.threadOptionsLog,"Execute")
            message = "Calculate Method:{}".format(self.planHeatDMM.data.calculateMethod)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)
            message = "Project Name:{}".format(self.planHeatDMM.data.projectName)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)

            message = "Area Under Study:{}".format(self.planHeatDMM.data.areaName)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)

            message = "Country:{}".format(self.planHeatDMM.data.country)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)
            
            message = "Baseline Scenario Year:{}".format(self.planHeatDMM.data.baselineScenarioYear)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)
            
            if self.boolRetrofittedScenarios:
                message = "Future Scenario Year:{}".format(self.planHeatDMM.data.futureScenarioYear)
                self.writeLogExecuteOptions(self.threadOptionsLog,message)
                self.planHeatDMM.resources.log.write_log("INFO",message)


            message = "Input Shape File:{}".format(self.planHeatDMM.data.inputShapeFile)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)

            message = "Output Files:{}".format(self.planHeatDMM.data.outputSaveFile)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)

            message = "Lidar DSM:{}".format(self.planHeatDMM.data.DSMDirectory)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO",message)

            message = "Lidar DTM:{}".format(self.planHeatDMM.data.DTMDirectory)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO", message)
            
            message = "Database file:{}".format(self.dbFileName)
            self.writeLogExecuteOptions(self.threadOptionsLog,message)
            self.planHeatDMM.resources.log.write_log("INFO", message)

            
            result = self.process()

       
            if result: 
                
                if self.planHeatDMM.data.processContinue:
                    if self.error == 0:   
                        self.changeStatusProcessButton.emit("Process Ok, see log file",self.planHeatDMM.resources.icon_ok_icon, self.planHeatDMM)
                        self.showMessageDialog.emit("OK","Ok", "Process finished Ok",self.planHeatDMM)  
                    else:
                        self.changeStatusProcessButton.emit("Process Warning, see log file",self.planHeatDMM.resources.icon_warn_icon, self.planHeatDMM)
                        self.showMessageDialog.emit("WARN","Warning", "Warning - The Process finished with records in error, check log file for further information",self.planHeatDMM)  
                      
                    
                    
                    if self.ok > 0 and self.planHeatDMM.data.pluginLaunch == True and self.planHeatDMM.data.boolOpenGeneratedShape == True:
                        try:
                            layerName = os.path.splitext(os.path.basename(self.shapeOutFilename))[0]
                        except:
                            layerName = self.projectName    
                        
                        self.loadShapeGeneratedFile.emit(self.shapeOutBaselineFilename + ".shp", layerName  ,self.planHeatDMM)
                        
                        if self.boolRetrofittedScenarios == True:
                            self.loadShapeGeneratedFile.emit(self.shapeOutFutureFilename + ".shp", layerName + "_future_scenario" ,self.planHeatDMM)
                
            else:    
                if self.planHeatDMM.data.closeWindow == False and self.planHeatDMM.data.processContinue == False: 
                    self.changeStatusProcessButton.emit("Process canceled, see log file",self.planHeatDMM.resources.icon_error_icon, self.planHeatDMM)
                    self.message_update.emit("Process canceled by the user",self.planHeatDMM)
                    self.showMessageDialog.emit("CRITICAL","Canceled", "Process canceled by the user",self.planHeatDMM)
                    
                elif self.planHeatDMM.data.closeWindow == False and self.planHeatDMM.data.processContinue == True:
                    self.changeStatusProcessButton.emit("Process Error, see log file",self.planHeatDMM.resources.icon_error_icon, self.planHeatDMM)
                    self.message_update.emit("Process error",self.planHeatDMM)
                        
                else:      
                    self.changeStatusProcessButton.emit("Close Window requested by the User",self.planHeatDMM.resources.icon_error_icon, self.planHeatDMM)
                    self.message_update.emit("Close Window requested by the User",self.planHeatDMM)
                    
                
            
            self.unlock_interface.emit(self.planHeatDMM)
              
            
            # Sleep time for finish de unlock interface signal
            self.planHeatDMM.resources.log.write_log("INFO", "Finish Process")
            time.sleep(1)   
            
            if self.database is not None:
                self.database.closeDB()
                self.database = None       
                
            self.log.write_log("INFO","Finish Thread")
            if self.clockThread is not None and self.clockThread.isRunning():
                self.clockThread.exit()
            
        except:
            self.log.write_log("ERROR", "Run Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
            if self.clockThread is not None and self.clockThread.isRunning():
                self.clockThread.exit()
            if self.database is not None:
                self.database.closeDB()
                self.database = None           
                
            self.unlock_interface.emit(self.planHeatDMM)    
            self.showMessageDialog.emit("CRITICAL","ERROR", "Run Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]),self.planHeatDMM)    
            
   
   
            
    def kill_process(self):
        self.processContinue = False    
    
    
 
    def process(self):
        try:
            
            if self.planHeatDMM.data.calculateMethod.lower() == "simplified": 
                self.sendMessage("INFO", "Simplified - Proccess Start")          
                method_object = Alternative(self.log,self.database,self.country_id, self.boolRetrofittedScenarios,self.planHeatDMM)
                method_object.initialize()
                self.sendMessage("INFO", "Simplified - Create Objet")
            else:
                self.sendMessage("INFO", "Complete -  Proccess Start")
                method_object = Complete(self.log,self.database,self.noa,self.country_id, self.boolRetrofittedScenarios, self.planHeatDMM)
                method_object.initialize()
                self.sendMessage("INFO", "Complete - Create Objet")
    
            # Create the SHP  Handler
            if self.planHeatDMM.data.processContinue == True:
                self.inputShpFile =  Shape_Reader(self.log,self.shapeInFilename)
                self.sendMessage("INFO", "Create  SHP Input  Handler")
                
            else:
                self.sendMessage("INFO", "Process Cancel Request By User - Create  SHP Input Handler Ok")
                return False
    
            # Create the CSV IN  Handler
            if self.planHeatDMM.data.processContinue == True:
                self.inputCsvFile =  CSV_Reader(self.log, self.csvInFilename,method_object.inputFields)
                self.sendMessage("INFO", "Create CSV Input Handler Ok")
            else:
                self.sendMessage("INFO", "Process Cancel Request By User - Create CSV Input Handler")
                return False    
            
           
            # Create Baseline Detail Output CSV
            if self.planHeatDMM.data.processContinue == True:
                self.outputDetailBaselineCSVFile =  CSV_Writer(self.log,self.csvOutBaselineFilename,method_object.outputBaselineDetailFieldsCsv,self.boolAddShapeFields ,self.userFieldShapeMap)
                self.sendMessage("INFO", "Create Baseline CSV - Detail Output Handler Ok")
            else:
                self.sendMessage("INFO","Process Cancel Request By User - Create Baseline CSV Detail Output Handler")
                return False    
            
            # Create Future Detail Output CSV
            if self.boolRetrofittedScenarios == True:
                if self.planHeatDMM.data.processContinue == True:
                    self.outputDetailFutureCSVFile =  CSV_Writer(self.log,self.csvOutFutureFilename,method_object.outputFutureDetailFieldsCsv,self.boolAddShapeFields ,self.userFieldShapeMap)
                    self.sendMessage("INFO", "Create Future CSV Detail Output Handler Ok")
                else:
                    self.sendMessage("INFO", "Process Cancel Request By User - Create Future CSV Detail Output Handler")   
                    return False    
            
            # Create Baseline Totalized Output CSV
            if self.planHeatDMM.data.processContinue == True:
                self.outputTotalizedBaselineCSVFile =  CSV_Writer(self.log,self.csvOutBaselineTotalFilename,method_object.outputBaselineTotalizedFieldsCsv)
                self.sendMessage("INFO", "Create Baseline CSV - Totalized Output Handler Ok")
            else:
                self.sendMessage("INFO","Process Cancel Request By User - Create Baseline CSV - Totalized Output Handler")
                return False
            
            # Create Future Totalized Output CSV
            if self.boolRetrofittedScenarios == True:            
                if self.planHeatDMM.data.processContinue == True:
                    self.outputTotalizedFutureCSVFile =  CSV_Writer(self.log,self.csvOutFutureTotalFilename,method_object.outputFutureTotalizedFieldsCsv)
                    self.sendMessage("INFO", "Create Future CSV - Totalized Output Handler Ok")
                else:
                    self.sendMessage("INFO","Process Cancel Request By User - Create Future CSV - Totalized Output Handler")
                    return False    

            # Create Baseline Hourly Output CSV
            if self.boolHourlyDetailFile  == True:
                if self.planHeatDMM.data.processContinue == True:
                    self.outputHourlyBaselineCSVFile =  CSV_Writer(self.log,self.csvOutBaselineHourlyFilename,method_object.outputBaselineHourlyFieldsCsv)
                    self.sendMessage("INFO", "Create Baseline CSV - Hourly Output Handler Ok")
                else:
                    self.log.write_log("INFO", "Process Cancel Request By User - Create CSV Hourly Output Handler")    
                    return False    


            # Create Future Hourly Output CSV
            if self.boolHourlyDetailFile  == True and self.boolRetrofittedScenarios == True:
                if self.planHeatDMM.data.processContinue == True:
                    self.outputHourlyFutureCSVFile =  CSV_Writer(self.log,self.csvOutFutureHourlyFilename,method_object.outputFutureHourlyFieldsCsv)
                    self.sendMessage("INFO", "Create Future CSV - Hourly Output Handler Ok")
                else:
                    self.log.write_log("INFO", "Process Cancel Request By User - Create CSV Hourly Output Handler")    
                    return False    
    
            #Read Input Shape  file
            self.sendMessage("INFO","Reading Input Shape File")
            if self.planHeatDMM.data.processContinue == True:
                self.inputShpFile.readShapeFile()
                self.inputShpFile.createGeometryIndex(self.fieldsSHPJavaPosition)
                self.sendMessage("INFO","Read Input Shape File  Ok")
            else:
                self.sendMessage("INFO","Process Cancel Request By User - Read Input Shape File")
                return False
            
            
            # Create Baseline SHP Output
            if self.planHeatDMM.data.processContinue == True:
                self.outputBaselineSHPFile =  Shape_Writer(self.log,self.shapeOutBaselineFilename,method_object.outputBaselineDetailFieldsShape,self.boolAddShapeFields ,self.userFieldShapeMap, self.referentialSpaceWKT)
                self.sendMessage("INFO","Create Baseline - Shape File Output Handler")
            else:
                self.sendMessage("INFO","Process Cancel Request By User - Create Shape File Output Handler")
                return False 
            
            # Create future SHP Output
            if self.boolRetrofittedScenarios == True:
                if self.planHeatDMM.data.processContinue == True:
                    self.outputFutureSHPFile =  Shape_Writer(self.log,self.shapeOutFutureFilename,method_object.outputFutureDetailFieldsShape,self.boolAddShapeFields ,self.userFieldShapeMap, self.referentialSpaceWKT)
                    self.sendMessage("INFO","Create future - Shape File Output Handler")
                else:
                    self.sendMessage("INFO","Process Cancel Request By User - Create Shape File Output Handler")
                    return False               
              
            # Create JSON file for Java Callback
            if self.planHeatDMM.data.processContinue == True:
                self.jsonArgs4Java(self.log, self.fileJsonArg,self.folderProject,self.shpFilename,self.logFileName,self.lidarDTMFolder,\
                              self.lidarDSMFolder, self.referentialSpaceEPSG, self.fieldsSHPJavaPosition,self.buildingUseFloorHeightDict)
                self.sendMessage("INFO","Create JSON File for Java Process Ok")
            else:
                self.sendMessage("INFO","Process Cancel Request By User - Create JSON File for Java Process")
                return False           
    
            # CALL TO JAVA PROCESS
            if self.planHeatDMM.data.processContinue == True:
                if Config.LAUNCH_JAVA_PROCESS in ("Y","y"):
                    self.sendMessage("INFO","Call to Java Process")
                    self.message_update.emit("Running Java Process...",self.planHeatDMM)
                    self.javaLaunchProcess(self.log,self.javaLog, self.fileJava, self.fileJar,self.fileLib, self.mainJavaClass, self.fileJsonArg)
                    self.planHeatDMM.resources.javaProcessObject = None
                    self.sendMessage("INFO","Finish Java Process Ok")
            else:
                self.sendMessage("INFO","Process Cancel Request By User - Call to Java Process")
                return False           
    
    
            #Read CSV in file
            if self.planHeatDMM.data.processContinue == True:
                self.sendMessage("INFO","Reading java CSV")
                data = self.inputCsvFile.csv_read()
                self.sendMessage("INFO","Finish CSV Read Ok")
            else:
                self.sendMessage("INFO","Process Cancel Request By User - Reading CSV file")
                return False           
    
            self.progress_total.emit(len(data),self.planHeatDMM)
            
            building_list = []
           
            self.sendMessage("INFO","Data Calculate Processing Start")
            
            # Process Data     
            for i, row in enumerate(data):
                if self.planHeatDMM.data.processContinue == True:
                    building = Building(self.log,self.projectName,self.areaName,self.country_id,row)
                    self.message_update.emit("Processing data calculation - Building {}/{}".format(i+1,len(data)),self.planHeatDMM)
                    self.assignBuildingShapeGeometryAndRecord(self.inputShpFile,building)
                    self.progress_update.emit(i+1,self.planHeatDMM)
                    building = method_object.calculateConsumption(building)
                    building_list.append(building)
                    if self.boolHourlyDetailFile and building.Regstatus and building.Regprocess:
                        #write rows on CSV file with baseline Hourly per building   
                        self.outputHourlyBaselineCSVFile.writeRowsCSV(building.hourlyBaselineDemandList)
                        #write rows on CSV file with Future Hourly per building 
                        if self.boolRetrofittedScenarios:
                            self.outputHourlyFutureCSVFile.writeRowsCSV(building.hourlyFutureDemandList)
                    building.hourlyBaselineDemandList = []
                    building.hourlyFutureDemandList   = []
                else:
                    self.sendMessage("INFO","Process Cancel Request By User - Data Calculate Processing")
                    return False  
                
            self.progress_update.emit(len(data),self.planHeatDMM)
            self.sendMessage("INFO", "Processing data calculation - Building {}/{}".format(len(data),len(data)))

            self.sendMessage("INFO", "Free memory reources - CSV input file and Geometry index") 
            self.freeMemoryResources(self.inputCsvFile,self.inputShpFile.geometryAndRecordBuildingIndex)

            
            #Retrieve totals for selected calculation method
            if self.planHeatDMM.data.processContinue == True:
                self.sendMessage("INFO", "Calculate Totalized Data.")
                method_object.calculateTotalizedConsumptionDemand()
                self.sendMessage("INFO", "Calculate Totalized Data Ok")
            else:
                self.log.write_log("INFO", "Process Cancel Request By User - Calculate Totalized Data")    
                return False     
            
            #Write Baseline Detail CSV file
            if self.planHeatDMM.data.processContinue == True:
                self.sendMessage("INFO", "Writing Output CSV - Baseline Detail file")
                self.outputDetailBaselineCSVFile.writeRowsCSV(building_list)
                self.sendMessage("INFO", "Writing Output CSV - Baseline Detail file Ok")
            else:
                self.sendMessage("INFO", "Process Cancel Request By User - Writing CSV file")
                return False           
                
            #Write Future Detail CSV file
            if self.boolRetrofittedScenarios == True:  
                if self.planHeatDMM.data.processContinue == True:
                    self.sendMessage("INFO", "Writing Output CSV - Future Detail file")
                    self.outputDetailFutureCSVFile.writeRowsCSV(building_list)
                    self.sendMessage("INFO", "Writing Output CSV - Future Detail file Ok")    
                else:
                    self.sendMessage("INFO", "Process Cancel Request By User - Writing CSV file")
                    return False           
                
                
           
            
            #Write Baseline Totalized CSV file
            if self.planHeatDMM.data.processContinue == True:
                self.sendMessage("INFO", "Writing Output CSV - Baseline Totalized file")
                self.outputTotalizedBaselineCSVFile.writeRowsCSV(method_object.baselineTotalizedDemandList)
                self.sendMessage("INFO", "Writing Output CSV - Baseline Totalized file Ok")
            else:
                self.sendMessage("INFO", "Process Cancel Request By User - Writing CSV file")
                return False           
            
            
            #Write Future Totalized CSV file
            if self.boolRetrofittedScenarios == True:  
                if self.planHeatDMM.data.processContinue == True:
                    self.sendMessage("INFO", "Writing Output CSV - Future Totalized file")
                    self.outputTotalizedFutureCSVFile.writeRowsCSV(method_object.futureTotalizedDemandList)
                    self.sendMessage("INFO", "Writing Output CSV - Future Totalized file Ok")
                else:
                    self.sendMessage("INFO", "Process Cancel Request By User - Writing CSV file")
                    return False   
            
            
            self.sendMessage("INFO", "Free memory resources output CSV files")    
            self.freeMemoryResources(self.outputDetailBaselineCSVFile,self.outputDetailFutureCSVFile,\
                                     self.outputHourlyBaselineCSVFile,self.outputHourlyFutureCSVFile,\
                                     self.outputTotalizedBaselineCSVFile, self.outputTotalizedFutureCSVFile,callGC=False)
            self.sendMessage("INFO", "Free memory resources method object data")
            self.freeMemoryResources(method_object)
                
                
            #Populate SHP file - Baseline   
            if self.planHeatDMM.data.processContinue == True:
                self.sendMessage("INFO", "Populate Baseline Output Shape file")
                self.outputBaselineSHPFile.populateAll(building_list)
                self.sendMessage("INFO", "Populate Baseline Output Shape file Ok")
            else:
                self.sendMessage("INFO", "Process Cancel Request By User - populate Qgis Files")
                return False           
                 
            # Save QGIS files  - Baseline   
            if self.planHeatDMM.data.processContinue == True: 
                self.sendMessage("INFO", "Saving Output Baseline Qgis files")    
                self.outputBaselineSHPFile.saveQgisFiles()
                self.sendMessage("INFO", "Saving Output Baseline Qgis files Ok")    
            else:
                self.sendMessage("INFO", "Process Cancel Request By User - Writing Qgis files")    
                return False   
            
            self.sendMessage("INFO", "Free memory resources baseline shape file")
            self.freeMemoryResources(self.outputBaselineSHPFile)
            
            if self.boolRetrofittedScenarios == True:   
                #Populate SHP file - Future   
                if self.planHeatDMM.data.processContinue == True:
                    self.sendMessage("INFO", "Populate Future Output Shape file")
                    self.outputFutureSHPFile.populateAll(building_list)
                    self.sendMessage("INFO", "Populate Future Output Shape file Ok")
                else:
                    self.sendMessage("INFO", "Process Cancel Request By User - populate Qgis Files")
                    return False           
                     
                # Save QGIS files - Future     
                if self.planHeatDMM.data.processContinue == True: 
                    self.sendMessage("INFO", "Saving Output Future Qgis files")    
                    self.outputFutureSHPFile.saveQgisFiles()
                    self.sendMessage("INFO", "Saving Output Future Qgis files Ok")    
                else:
                    self.sendMessage("INFO", "Process Cancel Request By User - Writing Qgis files")    
                    return False   
                
            self.sendMessage("INFO", "Free memory resources future shape file")    
            self.freeMemoryResources(self.outputFutureSHPFile, callGC=False)
            
            
            self.sendMessage("INFO", "Free memory resources building list data") 
            self.freeMemoryResources(building_list)            
                
            self.total, self.ok, self.error, self.skip =  showResults(building_list)
            result = "Processed:{} buildings - Ok:{} - Error:{} - Skipped:{}".format(self.total,self.ok, self.error,self.skip)
            self.sendMessage("INFO", result)
            
            
            self.log.write_log("INFO", "Simplified Proccess End")
            return True
            
            self.exec_()    
        
        except Exception as e:
            self.log.write_log("ERROR ", "Thread process - Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.showMessageDialog.emit("CRITICAL","ERROR", "process Unexpected error:" + str(e),self.planHeatDMM)   
            return False    
        
        
    def freeMemoryResources(self,*args,callGC=True,**kwargs):
        try:
            for arg in args:
                #print("free", asizeof.asizeof(arg),str(arg))
                del arg
                
            if callGC:    
                gc.collect()  
            
        except:
            self.log.write_log("ERROR ","freeMemoryResources Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
   
    
    def assignBuildingShapeGeometryAndRecord(self,shpReader,building):
        try:
            position = shpReader.geometryAndRecordBuildingIndex[str(building.reference)]    
            building.shpGeometryData = shpReader.geometryAndRecordBuilding[position].shape
            building.shpRecordData   = shpReader.geometryAndRecordBuilding[position].record
            
        except KeyError:
            self.log.write_log("ERROR ","assignBuildingShapeGeometryAndRecord Not Exists building reference in shapefile id:" + str(building.reference))
            building.Regstatus = False
                    
        except:
            self.log.write_log("ERROR ","assignBuildingShapeGeometryAndRecord Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            building.Regstatus = False


    
    def sendMessage(self,level,message):
        try:
            self.log.write_log(level, message)
            self.message_update.emit(message,self.planHeatDMM)
            
        except Exception as e:
            self.log.write_log("ERROR ", "process Unexpected error:" + str(e))
            self.showMessageDialog.emit("ERROR", "process Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]),self.planHeatDMM)   
    
    
    
    def jsonArgs4Java(self,log,fileArg,folderProject,shpFilename,logFileName,lidarDTMFolder,lidarDSMFolder,referentialSpace,fieldMapping,buildingUseFloorHeightDict):
        try:
            with open(fileArg, "w") as jsonFile:
                
                jsonPythonJava = OrderedDict()
    
                jsonPythonJava["fieldMapping"]=fieldMapping
                jsonPythonJava["logFileName"] = logFileName
                jsonPythonJava["lidarDTMFolder"] = lidarDTMFolder
                jsonPythonJava["lidarDSMFolder"] = lidarDSMFolder
                jsonPythonJava["shpFilename"] = shpFilename
                jsonPythonJava["referentialSpace"] = referentialSpace
                jsonPythonJava["folderProject"] = folderProject
                jsonPythonJava["floorHeight"]   = buildingUseFloorHeightDict
    
                
                jsonFile.write(dumps(jsonPythonJava))
                
                
                log.write_log("INFO", "Write JSON Args File")
                
        except:
            log.write_log("ERROR", "jsonArgs4Java  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
            raise
    
        
    def javaLaunchProcess(self,log,javaLog, fileJava, fileJar,fileLib, mainJavaClass,fileJsonArg):
        
        try:        
            
            javaConsoleOutput = ""
            run_process = ""
            if os.path.isfile(fileJar):
                
                if platform.system() == 'Windows':
                    #Add command Windows, to do not visible CMD
                    try:
                        run_test_process = fileJava + 'java -version '
                        CREATE_NO_WINDOW = 0x08000000
                        java_process = subprocess.Popen(run_test_process,shell=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags = CREATE_NO_WINDOW)
                        WindowMode =  CREATE_NO_WINDOW
                    except Exception as e: 
                        print("excepcion " + str(e))    
                        WindowMode = subprocess.SW_HIDE
                        #run_process = fileJava + 'java -cp "' + fileJar + ';' + fileLib + '" '  + mainJavaClass + ' '  +  fileJsonArg
                else:
                    WindowMode=0
                
                foutput = open(javaLog, "w")    
                run_process = fileJava + 'java -XX:+UseG1GC -Xms1g -Xmx4g -cp "' + fileJar + ';' + fileLib + '" '  + mainJavaClass + ' '  +  fileJsonArg   
                #self.planHeatDMM.resources.javaProcessObject = subprocess.run(run_process,check=True,shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)   
                #java_process = subprocess.Popen(run_process,shell=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags = WindowMode)
                java_process = subprocess.Popen(run_process,shell=False,stdout=foutput,stderr=foutput,creationflags = WindowMode)
                self.planHeatDMM.resources.javaProcessObject = java_process
                log.write_log("INFO","Java execute command  " + str(java_process.args))
                returnCode = java_process.wait()
                foutput.close()
                
                if returnCode and self.planHeatDMM.data.processContinue is not False:
                    #Process Error
                    raise JavaProcessException("Error on Java Process , exit status code:{:d}".format(returnCode)) 
                
            else:
                raise NotFoundResourceException("jar file not found at location " + fileJar)     
        
        except JavaProcessException:
            log.write_log("ERROR","Execute error  " + run_process)
            log.write_log("ERROR", "javaLaunchProcess JavaProcessException JAVA error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise        
        except subprocess.CalledProcessError as e:
            javaConsoleOutput =  str(e.stdout, 'utf-8', errors='ignore')
            
            log.write_log("ERROR","Java Console Output  " + javaConsoleOutput) 
            log.write_log("ERROR","Execute error  " + run_process)
            log.write_log("ERROR", "javaLaunchProcess CalledProcessError JAVA error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        except OSError as e:
            javaConsoleOutput =  str(e)
            log.write_log("ERROR","Java Console Output  " + javaConsoleOutput) 
            log.write_log("ERROR","Execute error  " + run_process)
            log.write_log("ERROR", "javaLaunchProcess OSError JAVA error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        except Exception as e:
            log.write_log("ERROR", "javaLaunchProcess launching new process JAVA Unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
               

    def initizalizeLogExecuteOptions(self,file_handler):
        try:
            if Config.OPTIONS_FILE.lower() == "y":
                with open(file_handler, "w") as optionsFile:
                    pass
                
        except Exception as e:
            self.log.write_log("ERROR", "initizalizeLogExecuteOptions Unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
    
    
    
    def writeLogExecuteOptions(self,file_handler, message):
        try:
            if Config.OPTIONS_FILE.lower() == "y":
                with open(file_handler, "a") as optionsFile:
                    optionsFile.write(message + "\n")
          
        except Exception as e:
            self.log.write_log("ERROR", "writeLogExecuteOptions Unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                
       
                
class ClockThread(QThread):
    """ Interface Clock for worker thread """
    
    clock_refresh = QtCore.pyqtSignal(int,object,name='clock_refresh')
    
    def __init__(self,planHeatDMM):
        
        QThread.__init__(self)
        try:
            self.planHeatDMM = planHeatDMM
            self.timeStart = None
            self.timer = None
        except Exception as e:
            self.planHeatDMM.resources.log.write_log("ERROR", "ClockThread Unexpected error:" + str(e))
            
    def run(self):
        try:
            
            self.timer = QtCore.QTimer()
            self.timeStart = time.time()
            self.timer.timeout.connect(lambda:self.timeClock())
            self.timer.setInterval(1000)
            self.timer.start()
            
            self.exec_()
            
        except Exception as e:
            self.planHeatDMM.resources.log.write_log("ERROR", "ClockThread Unexpected error:" + str(e))
                
    def timeClock(self):
        try: 
            value = int(time.time() - self.timeStart)
            self.clock_refresh.emit(value,self.planHeatDMM)
        except Exception:
                pass
    

