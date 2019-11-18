# -*- coding: utf-8 -*-
"""
   Control behavior of the plugin interface
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 14 Sep. 2017
"""



__docformat__ = "restructuredtext"



import sys
import os
import ntpath
import pickle
import datetime
import shutil
#import sched
#import time


from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtGui,QtCore,QtWidgets 
from PyQt5.Qt import  QTableWidgetItem
from PyQt5.QtCore import QThread
 
from copy import deepcopy
from src.worker import Worker
from manageShape.shape_reader import Shape_Reader
from config import config as Config
from restApi.noa_rest import Noa
from restApi.spatial_reference import SpatialReference
from manageDB.db import DB
from manageLog.log import Log
from model.refurbishment_tab_data import RefurbishmentTabData, RowRefurbishTableData
from model.building_use_map import BuildingUseMap
from model.protection_level_map import ProtectionLevelMap
from model.user_field_shape_map import UserFieldShapeMap
from utility.utils import clean_old_log_files,check_work_folders, check_LIDAR_files, check_no_other_files,timeit
from dialogs.message_box import showErrordialog, showInfodialog,showWarningdialog, showQuestiondialog,showSpatialReferenceInputDialog
from dialogs.field_user_map_dialog import FieldUserMapDialog
from dialogs.building_use_map_dialog import BuildingUseMapDialog
from dialogs.protection_level_map_dialog import ProtectionLevelMapDialog
from dialogs.complete_retrofit_scenario_dialog import CompleteRetrofitScenarioDialog
from dialogs.simplified_retrofit_scenario import SimplifiedRetroFitDialog 
from dialogs.log_file_dialog import LogFileDialog
from myExceptions.exceptions import NotFoundResourceException, LoadScenarioException
from planheat.PlanheatMappingModule import master_mapping_config

try:
    from qgis.core import *
    from qgis.gui import *
except ImportError:
    pass    


def initWindowStatus(planHeatDMM):
    """
            Initial application state,load Resources and external connections
            :param planHeatDMM : Application Object
            
    """
    try:
        
        database = None
        log = None
        noa = None
        fileJar = None
        
        Config.reload_cfg_file()
        
        
        planHeatDMM.dlg.openShapeFileCheckBox.setChecked(False)
        planHeatDMM.dlg.statusMessageLabel.setText("Initializaton Application...")
        
        check_work_folders()
        
        log = Log(planHeatDMM.resources.logDateName)
        if log is None:
            raise Exception("Error Creating Log file")
        else:
            planHeatDMM.resources.log = log 
        
        
        # Delete old log files > n days
        clean_old_log_files(log)
        
        #Create Database Object
        
        database = DB(log)
        if database is None:
            raise Exception("Error Creating Database Object")
        else:
            #Database Connection
            database.connectDB()
            database.maintenanceDataBase("REINDEX")
            planHeatDMM.resources.database = database 
            
        fileJar = Config.PLUGIN_DIR + os.path.sep + Config.JAR_FILE_PARAMS['path'] + os.path.sep +  Config.JAR_FILE_PARAMS['jarFileName']    
        if os.path.isfile(fileJar): 
            planHeatDMM.data.fileJar = fileJar
            planHeatDMM.data.fileLib = Config.PLUGIN_DIR + os.path.sep + Config.JAR_FILE_PARAMS['path'] + os.path.sep + "lib" + os.path.sep + "*" 
            
        else:
            raise NotFoundResourceException("jar file not found at location " + fileJar)     
                
        
        if Config.USE_NOA_DATA in ("Y","y"):
            #Create NOA Rest API Object
            noa = Noa(log)
    
            #Check NOA connectivity
            
            if not noa.connectionAvailability():
                raise Exception("NOA Service - Connection not available")
            else:
                planHeatDMM.resources.noa = noa
        else:
            planHeatDMM.resources.noa = None
            log.write_log("INFO","Not use NOA WS")
                
        # Load from Database configuration Tables 
        planHeatDMM.data.buildingUse = planHeatDMM.resources.database.retrieveBuildingUseAll()
        planHeatDMM.data.periods = planHeatDMM.resources.database.retrievePeriodsAll()
        planHeatDMM.data.refurbishment_levels = planHeatDMM.resources.database.retrieveRefurbishmentLevelsAll()
        planHeatDMM.data.refurbishment_level_periods = planHeatDMM.resources.database.retrieveRefurbishmentLevelsPeriodsAll(planHeatDMM.data.periods)
        planHeatDMM.data.shp_map_csv_fields = planHeatDMM.resources.database.retrieveSHPInputFields()
        planHeatDMM.data.protectionLevels = planHeatDMM.resources.database.retrieveProtectionLevels()
        planHeatDMM.data.countries = planHeatDMM.resources.database.retrieveCountryAll()
        
        planHeatDMM.data.refurbishmentTabDataList = createDefaultRefurbishmentTabData(planHeatDMM)
        
        
        
       
        for i, data  in enumerate(planHeatDMM.data.countries.values()):
            planHeatDMM.dlg.countryComboBox.addItem(data.country)
            if Config.COUNTRY_DEFAULT is not None and str(Config.COUNTRY_DEFAULT).lower() == data.country.lower():
                planHeatDMM.data.country_id = data.id
                planHeatDMM.data.country = data.country
                planHeatDMM.dlg.countryComboBox.setCurrentIndex(i)
                
        
        if  Config.COUNTRY_DEFAULT is None or planHeatDMM.data.country_id is None:
            planHeatDMM.dlg.countryComboBox.setCurrentIndex(0)
            data = list(planHeatDMM.data.countries.values())
            planHeatDMM.data.country_id = data[0].id
            planHeatDMM.data.country = data[0].country
                
                
                
        planHeatDMM.data.calculateMethodList = ["Simplified","Complete"]
        for method in planHeatDMM.data.calculateMethodList: 
            planHeatDMM.dlg.methodComboBox.addItem(method)

        planHeatDMM.data.calculateMethod = planHeatDMM.data.calculateMethodList[0]
        
        planHeatDMM.dlg.statusMessageLabel.setText("Application ready...")

    except Exception:
        planHeatDMM.dlg.setEnabled(False)
        
        log.write_log("ERROR", "initWindowStatus Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowStatus",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        planHeatDMM.dlg.statusMessageLabel.setText("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

        if database is not None:
            log.write_log("INFO","close Database")
            database.closeDB()
            planHeatDMM.resources.database = None

        if log is not None:
            log.write_log("INFO","close log file")
            log.close_log()
            planHeatDMM.resources.log = None
        raise    
            


def initWindowbehavior(planHeatDMM):
    """
            Initial windows state, prepare GUI for use it 
            Widgets functionalities,signals and slots 
            :param planHeatDMM : Application Object
            
    """
    try:
        planHeatDMM.dlg.setEnabled(True)
        
       
        if planHeatDMM.data.pluginLaunch == True and 'qgis.core' in sys.modules and 'qgis.gui' in sys.modules:
            planHeatDMM.dlg.openShapeFileCheckBox.setVisible(True)
            planHeatDMM.dlg.openShapeFileCheckBox.setEnabled(True)
        
        else:
            planHeatDMM.dlg.openShapeFileCheckBox.setVisible(False)
        
        planHeatDMM.dlg.loadScenario.setLayoutDirection(QtCore.Qt.RightToLeft)
        planHeatDMM.dlg.loadScenario.setIconSize(QtCore.QSize(20,20))
        planHeatDMM.dlg.loadScenario.setIcon(planHeatDMM.resources.icon_load_icon)
        
            
        if Config.USE_PERSIST_SCENARIO in ("Y","y"):
            planHeatDMM.dlg.loadScenario.setVisible(True)
        else:         
            planHeatDMM.dlg.loadScenario.setVisible(False)
        
        year = int(datetime.datetime.now().strftime('%Y'))
        planHeatDMM.dlg.baselineScenarioYearSpinBox.setValue(year) 
        planHeatDMM.data.calculateMethod =  planHeatDMM.dlg.methodComboBox.currentText()
        planHeatDMM.data.country =  planHeatDMM.dlg.countryComboBox.currentText()

        planHeatDMM.data.outputSaveFile = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                                       master_mapping_config.DMM_FOLDER,
                                                       master_mapping_config.DMM_PREFIX + ".shp")
        planHeatDMM.dlg.saveFileLineEdit.setText(planHeatDMM.data.outputSaveFile)
        planHeatDMM.dlg.projectLineEdit.setText(planHeatDMM.data.projectName)
        
        
        planHeatDMM.dlg.DTMLabelState.setVisible(False)
        planHeatDMM.dlg.DSMLabelState.setVisible(False)
        planHeatDMM.dlg.fieldUserMatchLabel.setVisible(False)
        planHeatDMM.dlg.buildingUseMatchLabel.setVisible(False)
        planHeatDMM.dlg.protectionMatchLabel.setVisible(False)
        planHeatDMM.dlg.retrofittedScenariosToolbutton.setVisible(True)
        planHeatDMM.dlg.retrofittedScenariosToolbutton.setEnabled(False)
                
        planHeatDMM.dlg.lidarCheckBox.setChecked(False)
        planHeatDMM.dlg.DTMLineEdit.setEnabled(False)
        planHeatDMM.dlg.DSMLineEdit.setEnabled(False)
        planHeatDMM.dlg.DTMToolButton.setEnabled(False)
        planHeatDMM.dlg.DSMToolButton.setEnabled(False)
        planHeatDMM.dlg.DTMToolButton.setEnabled(False)
        planHeatDMM.dlg.DSMToolButton.setEnabled(False)
        
        planHeatDMM.dlg.fieldUserTable.setEnabled(False)
        planHeatDMM.dlg.fieldAddToolButton.setEnabled(False)
        
        
        planHeatDMM.dlg.buildingUseTable.setEnabled(False)
        planHeatDMM.dlg.buildUseAddToolButton.setEnabled(False)
        
        planHeatDMM.dlg.protectionLevelTable.setEnabled(False)
        planHeatDMM.dlg.protectionAddToolButton.setEnabled(False)
        
        planHeatDMM.dlg.processButton.setEnabled(False)
        
        #○ Load Icons to labels  and buttons      
        #planHeatDMM.dlg.projectNameLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.dlg.projectNameLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
        planHeatDMM.dlg.saveFileLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
        planHeatDMM.dlg.areaLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.dlg.countryLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
        planHeatDMM.dlg.loadFileLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        #planHeatDMM.dlg.saveFileLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.dlg.saveFileLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
        planHeatDMM.dlg.DTMLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.dlg.DSMLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.dlg.methodLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
        planHeatDMM.dlg.fieldUserMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)

        planHeatDMM.dlg.fieldAddToolButton.setIcon(planHeatDMM.resources.icon_pencil)
        planHeatDMM.dlg.buildUseAddToolButton.setIcon(planHeatDMM.resources.icon_pencil)
        planHeatDMM.dlg.protectionAddToolButton.setIcon(planHeatDMM.resources.icon_pencil)
        planHeatDMM.dlg.retrofittedScenariosToolbutton.setIcon(planHeatDMM.resources.icon_retrofitted_icon)
        
        
        
        
        # Show state Lables
        planHeatDMM.dlg.projectNameLabelState.setVisible(True)
        planHeatDMM.dlg.areaLabelState.setVisible(True)
        planHeatDMM.dlg.countryLabelState.setVisible(True) 
        planHeatDMM.dlg.loadFileLabelState.setVisible(True)
        planHeatDMM.dlg.saveFileLabelState.setVisible(True)
        planHeatDMM.dlg.methodLabelState.setVisible(True)


        # Window Action Signals
        planHeatDMM.dlg.closeButton.clicked.connect(lambda:closeButtonDialog(planHeatDMM))
        
        # planHeatDMM.dlg.projectLineEdit.textChanged.connect(lambda:projectLineEditTextChanged(planHeatDMM))
        planHeatDMM.dlg.areaLineEdit.textChanged.connect(lambda:areaLineEditTextChanged(planHeatDMM))
        
        
        planHeatDMM.dlg.loadFileToolButton.clicked.connect(lambda:openLoadFileDialog(planHeatDMM))
        planHeatDMM.dlg.loadFileLineEdit.textChanged.connect(lambda:loadFileTextChanged(planHeatDMM))
        
        planHeatDMM.dlg.saveFileToolButton.clicked.connect(lambda:openSaveFileDialog(planHeatDMM))
        planHeatDMM.dlg.saveFileLineEdit.textChanged.connect(lambda:saveFileTextChanged(planHeatDMM))
        
        planHeatDMM.dlg.lidarCheckBox.stateChanged.connect(lambda:lidarCheckBoxStateChanged(planHeatDMM))
        planHeatDMM.dlg.detailFileCheckBox.stateChanged.connect(lambda:checkBoxDetailFileChanged(planHeatDMM))
        planHeatDMM.dlg.retrofittedScenariosCheckBox.stateChanged.connect(lambda:checkBoxRetrofittedScenariosChanged(planHeatDMM))
        planHeatDMM.dlg.openShapeFileCheckBox.stateChanged.connect(lambda:openShapeFileCheckBoxStateChanged(planHeatDMM))
        
        planHeatDMM.dlg.DTMToolButton.clicked.connect(lambda:openLoadFileDialogDTM(planHeatDMM))
        planHeatDMM.dlg.DTMLineEdit.textChanged.connect(lambda:DTMFileTextChanged(planHeatDMM))
        planHeatDMM.dlg.DSMToolButton.clicked.connect(lambda:openLoadFileDialogDSM(planHeatDMM))
        planHeatDMM.dlg.DSMLineEdit.textChanged.connect(lambda:DSMFileTextChanged(planHeatDMM))
        
        
        planHeatDMM.dlg.methodComboBox.currentIndexChanged.connect(lambda:methodSelectChanged(planHeatDMM))
        planHeatDMM.dlg.countryComboBox.currentIndexChanged.connect(lambda:countrySelectChanged(planHeatDMM))
        
        planHeatDMM.dlg.retrofittedScenariosToolbutton.clicked.connect(lambda:openRetrofittedScenarioDialog(planHeatDMM))
        
        planHeatDMM.dlg.fieldAddToolButton.clicked.connect(lambda:openFieldUserMapDialog(planHeatDMM))
        planHeatDMM.dlg.buildUseAddToolButton.clicked.connect(lambda:openBuildingUseMapDialog(planHeatDMM))
        planHeatDMM.dlg.protectionAddToolButton.clicked.connect(lambda:openProtectionLevelMapDialog(planHeatDMM))
        
        planHeatDMM.dlg.processButton.clicked.connect(lambda:launchProcess(planHeatDMM))
        planHeatDMM.dlg.statusProcessButton.clicked.connect(lambda:stopProcess(planHeatDMM))
        planHeatDMM.dlg.statusProcessButton.clicked.connect(lambda:showLogProcessFile(planHeatDMM))
        
        planHeatDMM.dlg.loadScenario.clicked.connect(lambda:loadScenario(planHeatDMM))
        

    except Exception:
        planHeatDMM.dlg.setEnabled(False)
        planHeatDMM.resources.log.write_log("ERROR", "initWindowbehavior Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        planHeatDMM.dlg.statusMessageLabel.setText("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

 
        
def closeButtonDialog(planHeatDMM):
    """
        Close Main application Window
        :param planHeatDMM : Application Object
            
    """
    planHeatDMM.dlg.close()
    planHeatDMM.master_dlg.show()
    planHeatDMM.master_dlg.closeMapping.emit()
    
    
def closeWindow(planHeatDMM):    
    """
        Previous actions to closing application 
        close button and X slot
        :param planHeatDMM : Application Object
        :returns:True or False
            
    """
    try:
        message = "Do you want to close the window?"
        if showQuestiondialog(planHeatDMM.dlg,"Close DMM Planheat Plugin",message) == QtWidgets.QMessageBox.Yes:
            stopProcess(planHeatDMM, False)
            
                
            if planHeatDMM.resources.javaProcessObject is not None:
                planHeatDMM.resources.javaProcessObject.kill()
                QThread.currentThread().msleep(300)    

            if planHeatDMM.resources.thread_clock is not None and planHeatDMM.resources.thread_clock.isRunning():
                planHeatDMM.resources.thread_clock.exit()
                QThread.currentThread().msleep(300)
                
            if planHeatDMM.resources.thread is not None and planHeatDMM.resources.thread.isRunning():
                planHeatDMM.resources.thread.exit()
                
            #showInfodialog(planHeatDMM.dlg,"see you","Thanks, for using DMM Planheat Plugin")    
            QThread.currentThread().msleep(300)    
            return True        
        else:
            return False
        
    except Exception:
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior closeWindow",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        planHeatDMM.resources.log.write_log("ERROR", "initWindowbehavior closeWindow Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        
            

def openLoadFileDialog(planHeatDMM):
    """
        load opendialog for select shape file  
        load shape file button slot
        :param planHeatDMM : Application Object
        
            
    """
    
    try:
        
        fname, _ = QFileDialog.getOpenFileName(planHeatDMM.dlg, 'Open Shape File...',Config.PLUGIN_DIR,"shape files *.shp")
        
        if fname is not None and fname != "":
            if controlEPSG(planHeatDMM,fname) == True:
                planHeatDMM.dlg.loadFileLineEdit.setText(fname)
                    
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openLoadFileDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openLoadFileDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
  
    
def controlEPSG(planHeatDMM,fname):
    """
        Check EPSG code for selected shape file  
        :param planHeatDMM : Application Object
        
            
    """
    try:
        sp = SpatialReference(planHeatDMM.resources.log,fname)
        retCode = sp.checkSpatialReference()
        if retCode == 0:
            planHeatDMM.data.spatialReferenceEPSG = sp.spatialReferenceEPSG
            planHeatDMM.data.spatialReferenceWKT = sp.spatialReferenceWKT
            return True
        else:    
            EPSG_code = showSpatialReferenceInputDialog(planHeatDMM, retCode)
            if EPSG_code is not None:
                retCode = sp.osrGenerateSpatialReference(EPSG_code)
                if  retCode == 0:  
                    planHeatDMM.data.spatialReferenceEPSG = sp.spatialReferenceEPSG
                    planHeatDMM.data.spatialReferenceWKT = sp.spatialReferenceWKT
                    return True
                else:
                    showErrordialog(planHeatDMM.dlg,"Open Shape File","EPSG code is not valid, you must provide a correct value")
                    return False     
                    
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - controlEPSG Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - controlEPSG",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        return False
    
        
    
def openSaveFileDialog(planHeatDMM): 
    """
        load savedialog for select output files  
        save csv and shape file button slot
        :param planHeatDMM : Application Object
            
    """
    
    try:
        fname, _ = QFileDialog.getSaveFileName(planHeatDMM.dlg, 'Save File As...', Config.PLUGIN_DIR)
        
        if fname is not None and fname != "":
            planHeatDMM.dlg.saveFileLineEdit.setText(fname)
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openSaveFileDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openLoadFileDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))


def projectLineEditTextChanged(planHeatDMM):
    """
        Control input data in project name widget   
        project name widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        # planHeatDMM.data.projectName = planHeatDMM.dlg.projectLineEdit.text()
        
        if planHeatDMM.data.projectName is not None and planHeatDMM.data.projectName != "":
            planHeatDMM.dlg.projectNameLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
            planHeatDMM.data.boolProjectName = True
        
        else:
            planHeatDMM.dlg.projectNameLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            planHeatDMM.data.boolProjectName = False      
        
        checkProcessLauncher(planHeatDMM)
           
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - projectLineEditTextChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - projectLineEditTextChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        


def areaLineEditTextChanged(planHeatDMM):
    """
        Control input data in area under study widget   
        area under study widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        planHeatDMM.data.areaName = planHeatDMM.dlg.areaLineEdit.text()
        
        if planHeatDMM.data.areaName is not None and planHeatDMM.data.areaName != "":
            planHeatDMM.dlg.areaLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
            planHeatDMM.data.boolAreaName = True
        else:
            planHeatDMM.dlg.areaLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            planHeatDMM.data.boolAreaName = False      
         
        checkProcessLauncher(planHeatDMM)
           
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - areaLineEditTextChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - areaLineEditTextChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
        
    
def loadFileTextChanged(planHeatDMM):
    """
        Control input data in area under study widget   
        area under study widget slot
        :param planHeatDMM : Application Object
            
    """
    
    try:
        
        planHeatDMM.dlg.buildingUseTable.setColumnCount(0)
        planHeatDMM.dlg.buildingUseTable.setRowCount(0) 
        planHeatDMM.dlg.fieldUserTable.setColumnCount(0)
        planHeatDMM.dlg.fieldUserTable.setRowCount(0)
        planHeatDMM.dlg.protectionLevelTable.setColumnCount(0)
        planHeatDMM.dlg.protectionLevelTable.setRowCount(0)
        
        planHeatDMM.dlg.fieldUserTable.setEnabled(False)
        planHeatDMM.dlg.buildingUseTable.setEnabled(False)
        planHeatDMM.dlg.protectionLevelTable.setEnabled(False)
         
        planHeatDMM.dlg.fieldAddToolButton.setEnabled(False)
        planHeatDMM.dlg.buildUseAddToolButton.setEnabled(False)
        planHeatDMM.dlg.protectionAddToolButton.setEnabled(False)
        
        planHeatDMM.dlg.fieldUserMatchLabel.setVisible(False)
        planHeatDMM.dlg.buildingUseMatchLabel.setVisible(False)
        planHeatDMM.dlg.protectionMatchLabel.setVisible(False)
        
        planHeatDMM.dlg.fieldUserMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.data.boolShpDMMFieldsMap = False  
        planHeatDMM.data.shpDMMFieldsMap = []
        
        planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.data.boolBuildingUseMap     = False
        planHeatDMM.data.old_building_use_user_definition_value = "NULL_VALUE" 
        planHeatDMM.data.buildingUseMap = []
        
        planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        planHeatDMM.data.boolProtectionLevelMap = False
        planHeatDMM.data.old_protection_user_definition_value = "NULL_VALUE"
        planHeatDMM.data.protectionLevelMap = []
        
        fname = planHeatDMM.dlg.loadFileLineEdit.text()
        if os.path.isfile(fname) and fname.endswith(".shp"):
            # Copy the input file in the shape file
            dmm_folder = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                      master_mapping_config.DMM_FOLDER)
            # Only if the file is not already in the project directory
            if os.path.normpath(os.path.dirname(fname)) != os.path.normpath(dmm_folder):
                dmm_standard_file_name = os.path.join(dmm_folder, master_mapping_config.DMM_INPUT_SHAPE_FILE_NAME)
                remove_shapefile(dmm_standard_file_name)
                copy_shapefile(fname, dmm_standard_file_name)
                fname = dmm_standard_file_name + ".shp"
                planHeatDMM.dlg.loadFileLineEdit.setText(fname)
            # Process the input
            retrieveShapeHeaderFields(planHeatDMM, fname)
            planHeatDMM.data.shpBuildingRecords = readShapeFileData(planHeatDMM, fname).recordBuilding
            planHeatDMM.data.inputShapeFile = fname
            planHeatDMM.data.boolInputShapeFile = True
            planHeatDMM.dlg.loadFileLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
            planHeatDMM.dlg.fieldUserMatchLabel.setEnabled(True)
            planHeatDMM.dlg.fieldUserMatchLabel.setVisible(True)
            planHeatDMM.dlg.fieldAddToolButton.setEnabled(True)
            planHeatDMM.dlg.fieldUserTable.setEnabled(True)
        
        else:
            planHeatDMM.data.inputShapefile = None 
            planHeatDMM.data.boolInputShapeFile = False
            planHeatDMM.dlg.loadFileLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            planHeatDMM.dlg.fieldUserMatchLabel.setEnabled(False)
            planHeatDMM.dlg.fieldUserMatchLabel.setVisible(False)
            planHeatDMM.dlg.fieldAddToolButton.setEnabled(False)
            planHeatDMM.dlg.fieldUserTable.setEnabled(False)

        checkProcessLauncher(planHeatDMM)

    except:
        planHeatDMM.dlg.loadFileLineEdit.setText("")
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - loadFileTextChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - loadFileTextChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        

def remove_shapefile(shapefile_path):
    """Delete a shapefile with all the inluded files (shp, dbf, shx, etc)."""
    file_name = os.path.splitext(shapefile_path)[0]
    for extension in master_mapping_config.SHAPE_FILE_EXTENSIONS:
        file_path = file_name + extension
        if os.path.isfile(file_path):
            os.remove(file_path)

def copy_shapefile(shapefile_path, destination_name):
    """Copy a shapefile with all the inluded files (shp, dbf, shx, etc). The destination name must be file name."""
    file_name = os.path.splitext(shapefile_path)[0]
    for extension in master_mapping_config.SHAPE_FILE_EXTENSIONS:
        file_path = file_name + extension
        if os.path.isfile(file_path):
            shutil.copy(file_path, destination_name + extension)

def retrieveShapeHeaderFields(planHeatDMM,fname):
    try:
        shpRead = Shape_Reader(planHeatDMM.resources.log, fname)
        shpRead.readShapeFileHeaderFields()
        planHeatDMM.data.originShapeFields = shpRead.header_record
        
        
    except:
        
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - retrieveShapeHeaderFields Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - retrieveShapeHeaderFields",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    

def shapeFileFieldsValues(planHeatDMM,records, fieldPosition):
    """
        sort shape field values for field user dialog  
        :param planHeatDMM : Application Object
            
    """
    try:
        listValues = []
                
        for record in records:
            if str(record[fieldPosition]).lower() not in map(str.lower, listValues):
                listValues.append(str(record[fieldPosition]))
				
        #print(listValues)    
        return sorted(listValues)    
                    
    except:
        
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - shapeFileFieldsValues Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - shapeFileFieldsValues",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        return listValues        
                

def saveFileTextChanged(planHeatDMM):
    """
        Control input data in save file text  
        load file text widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        fname = planHeatDMM.dlg.saveFileLineEdit.text()
        directory = ntpath.dirname(fname)
        if os.path.isdir(directory):
            planHeatDMM.data.outputSaveFile = os.path.splitext(fname)[0]
            planHeatDMM.data.boolOutputSaveFile = True
            planHeatDMM.dlg.saveFileLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
        else:
            planHeatDMM.data.outputSaveFile = None 
            planHeatDMM.data.boolOutputSaveFile = False
            planHeatDMM.dlg.saveFileLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)      
        
        checkProcessLauncher(planHeatDMM)
           
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - loadFileTextChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - loadFileTextChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                

        
def lidarCheckBoxStateChanged(planHeatDMM):
    """
       lidar checkbox control   
       lidar checkbox widget slot
       :param planHeatDMM : Application Object
            
    """
     
    try:
        if  planHeatDMM.dlg.lidarCheckBox.isChecked():
            planHeatDMM.dlg.DTMLineEdit.setEnabled(True)
            planHeatDMM.dlg.DSMLineEdit.setEnabled(True)
            planHeatDMM.dlg.DTMToolButton.setEnabled(True)
            planHeatDMM.dlg.DSMToolButton.setEnabled(True)
            planHeatDMM.dlg.DTMLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            planHeatDMM.dlg.DSMLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            planHeatDMM.dlg.DTMLabelState.setVisible(True)
            planHeatDMM.dlg.DSMLabelState.setVisible(True)
            
            
            
            #if the Lidar is checked the totalheigh is optional 
            [x.setFieldState("Optional") for x in planHeatDMM.data.shp_map_csv_fields if x.fieldName.lower() == "totalheight"]
            [x.setFieldState("Optional") for x in planHeatDMM.data.shp_map_csv_fields if x.fieldName.lower() == "numberoffloors"]
            
            checkMandatoryFieldFilledData(planHeatDMM)
            
            checkProcessLauncher(planHeatDMM)
            
            
        else:
            planHeatDMM.dlg.DTMLineEdit.setText(None)
            planHeatDMM.dlg.DSMLineEdit.setText(None)
            planHeatDMM.dlg.DTMLineEdit.setEnabled(False)
            planHeatDMM.dlg.DSMLineEdit.setEnabled(False)
            planHeatDMM.dlg.DTMToolButton.setEnabled(False)
            planHeatDMM.dlg.DSMToolButton.setEnabled(False)
            planHeatDMM.dlg.DTMLabelState.setVisible(False)
            planHeatDMM.dlg.DSMLabelState.setVisible(False)
            
            if planHeatDMM.data.shpDMMFieldsMap and "numberoffloors".lower() not in map(str.lower,[data.fieldName for data  in planHeatDMM.data.shpDMMFieldsMap]): 
                [x.setFieldState("Mandatory") for x in planHeatDMM.data.shp_map_csv_fields if x.fieldName.lower() == "totalheight"]

            checkMandatoryFieldFilledData(planHeatDMM)
            
            checkProcessLauncher(planHeatDMM)
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - lidarCheckBoxStateChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - loadFileTextChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
                
                

def checkBoxDetailFileChanged(planHeatDMM):
    """
        Control hourly data file yes or no   
         hourly file checkbox widget slot
        :param planHeatDMM : Application Object
            
    """ 
    try:
        if  planHeatDMM.dlg.detailFileCheckBox.isChecked():
            planHeatDMM.data.boolHourlyDetailFile = True
        else:
            planHeatDMM.data.boolHourlyDetailFile = False
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - CheckBoxHourlyFileChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - CheckBoxHourlyFileChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
                                


def checkBoxRetrofittedScenariosChanged(planHeatDMM):
    """
         Show or hide retrofitted scenarios toolbutton   
         Retrofitted Scenarios checkbox widget slot
        :param planHeatDMM : Application Object
            
    """ 
    try:
        if  planHeatDMM.dlg.retrofittedScenariosCheckBox.isChecked():
            planHeatDMM.data.boolRetrofittedScenarios = True
            planHeatDMM.dlg.retrofittedScenariosToolbutton.setEnabled(True)
                 
        else:
            planHeatDMM.data.boolRetrofittedScenarios = False
            planHeatDMM.dlg.retrofittedScenariosToolbutton.setEnabled(False)
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - checkBoxRetrofittedScenariosChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - checkBoxRetrofittedScenariosChanged ",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
                                


def openShapeFileCheckBoxStateChanged(planHeatDMM):
    """
        Open the generated shape file after the process   
        shapefile checkbox  widget slot
        :param planHeatDMM : Application Object
            
    """
    
    try:
        if  planHeatDMM.dlg.openShapeFileCheckBox.isChecked():
            planHeatDMM.data.boolOpenGeneratedShape = True
        else:
            planHeatDMM.data.boolOpenGeneratedShape = False
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openShapeFileCheckBoxStateChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openShapeFileCheckBoxStateChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                
                
                
def openLoadFileDialogDTM(planHeatDMM):
    """
        Open file dialog for select DTM files, if lidar checkbox is checked
        file dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    
    try:
    
        fname = str(QFileDialog.getExistingDirectory(planHeatDMM.dlg, "Select DTM files Directory"))
        if fname is not None and fname != "":
            planHeatDMM.dlg.DTMLineEdit.setText(fname)
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openLoadFileDialogDTM Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openLoadFileDialogDTM",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
                

def openLoadFileDialogDSM(planHeatDMM):
    """
        Open file dialog for select DSM files, if lidar checkbox is checked
        file dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
    
        fname = str(QFileDialog.getExistingDirectory(planHeatDMM.dlg, "Select DSM files Directory"))
        if fname is not None and fname != "":
            planHeatDMM.dlg.DSMLineEdit.setText(fname)
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openLoadFileDialogDSM Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openLoadFileDialogDSM",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
    
                
def DTMFileTextChanged(planHeatDMM):
    """
        DTM file text widget change 
        text widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        dirname = planHeatDMM.dlg.DTMLineEdit.text()
        if os.path.isdir(dirname) and check_LIDAR_files(dirname) and check_no_other_files(dirname):
            planHeatDMM.data.DTMDirectory = dirname
            planHeatDMM.data.boolDTMDirectory = True
            planHeatDMM.dlg.DTMLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
            
        else:
            
            planHeatDMM.data.DTMDirectory = None 
            planHeatDMM.data.boolDTMDirectory = False
            planHeatDMM.dlg.DTMLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            if os.path.isdir(dirname) and not check_LIDAR_files(dirname):
                showErrordialog(planHeatDMM.dlg,"LIDAR DTM folder","DTM folder must contain .asc files")
            elif os.path.isdir(dirname) and not check_no_other_files(dirname):
                showErrordialog(planHeatDMM.dlg,"LIDAR DTM folder","DTM folder can only contain .asc files")      
            planHeatDMM.dlg.DTMLineEdit.setText("")
            
        checkProcessLauncher(planHeatDMM)
           
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - DTMFileTextChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - DTMFileTextChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        


def DSMFileTextChanged(planHeatDMM):
    """
        DSM file text widget change 
        text widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        dirname = planHeatDMM.dlg.DSMLineEdit.text()
        if os.path.isdir(dirname) and check_LIDAR_files(dirname) and check_no_other_files(dirname):
            planHeatDMM.data.DSMDirectory = dirname
            planHeatDMM.data.boolDSMDirectory = True
            planHeatDMM.dlg.DSMLabelState.setPixmap(planHeatDMM.resources.pixmap_right_icon)
        else:
            planHeatDMM.data.DSMDirectory = None
            planHeatDMM.data.boolDSMDirectory = False
            planHeatDMM.dlg.DSMLabelState.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)      
            if os.path.isdir(dirname) and not check_LIDAR_files(dirname):
                showErrordialog(planHeatDMM.dlg,"LIDAR DSM folder","DSM folder must contain .asc files")
            elif os.path.isdir(dirname) and not check_no_other_files(dirname):
                showErrordialog(planHeatDMM.dlg,"LIDAR DSM folder","DSM folder can only contain .asc files")
            planHeatDMM.dlg.DSMLineEdit.setText("")    
                   
        
        checkProcessLauncher(planHeatDMM)
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - DSMFileTextChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - DSMFileTextChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        

         

def openRetrofittedScenarioDialog(planHeatDMM):
    """
        Open Refurbishmnet scenario dialog 
        protect level dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        if planHeatDMM.data.calculateMethod and planHeatDMM.data.calculateMethod.lower() == "simplified":
            dialog = SimplifiedRetroFitDialog(planHeatDMM)
        else:
            dialog = CompleteRetrofitScenarioDialog(planHeatDMM)    
       
        dialog.show()
        dialog.exec_()
    
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openRetrofittedScenarioDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openRetrofittedScenarioDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
     
   
         
def openProtectionLevelMapDialog(planHeatDMM):
    """
        Open protection level file match dialog 
        protect level dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        dialog = ProtectionLevelMapDialog(planHeatDMM)   
       
        dialog.show()
        dialog.exec_()
        loadProtectionLevelMapTable(planHeatDMM)
        checkProcessLauncher(planHeatDMM)
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openProtectionLevelMapDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openProtectionLevelMapDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        


def loadProtectionLevelMapTable(planHeatDMM):         
    """
        load building use match data to main window table 
        building use  dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        checkProtectionLevelMapFilledData(planHeatDMM)
        dlg = planHeatDMM.dlg
        if planHeatDMM.data.protectionLevelMap:
            dlg.protectionLevelTable.setColumnCount(2)
            horHeaders = ["Cadaster Protection Level                             ", "Application Protection Level"]
            dlg.protectionLevelTable.setHorizontalHeaderLabels(horHeaders)
            dlg.protectionLevelTable.setRowCount(0)
            dlg.protectionLevelTable.resizeColumnsToContents()
            dlg.protectionLevelTable.resizeRowsToContents()
            for data in planHeatDMM.data.protectionLevelMap:
                rowPosition = dlg.protectionLevelTable.rowCount()
                dlg.protectionLevelTable.insertRow(rowPosition) 
                dlg.protectionLevelTable.setItem(rowPosition , 0, QTableWidgetItem(str(data.user_definition_protection)))    
                dlg.protectionLevelTable.setItem(rowPosition , 1, QTableWidgetItem(str(data.DMM_protection_level)))    
                  
        else:
            dlg.protectionLevelTable.setColumnCount(0)
            dlg.protectionLevelTable.setRowCount(0)   
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - loadProtectionLevelMapTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - loadProtectionLevelMapTable",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
        
       

def openBuildingUseMapDialog(planHeatDMM):
    """
        Open building use match dialog 
        building use  dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        dialog = BuildingUseMapDialog(planHeatDMM)   
       
        dialog.show()
        dialog.exec_()
        loadBuildingUseMapTable(planHeatDMM)
        checkProcessLauncher(planHeatDMM)
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openBuildingUseMapDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openBuildingUseMapDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
        
        
def loadBuildingUseMapTable(planHeatDMM):  
    """
        load building use match data to main window table 
        building use  dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:      
        checkBuildingUseMapFilledData(planHeatDMM)
        dlg = planHeatDMM.dlg
        planHeatDMM.data.buildingUseFloorHeightDict={}

        if planHeatDMM.data.buildingUseMap:
            dlg.buildingUseTable.setColumnCount(2)
            horHeaders = ["Cadaster Use               ", "Application Use                 "]
            dlg.buildingUseTable.setHorizontalHeaderLabels(horHeaders)
            dlg.buildingUseTable.setRowCount(0)
            dlg.buildingUseTable.resizeColumnsToContents()
            dlg.buildingUseTable.resizeRowsToContents()
            
            for data in planHeatDMM.data.buildingUseMap:
                planHeatDMM.data.buildingUseFloorHeightDict[data.user_definition_use] = data.floor_height
                
                rowPosition = dlg.buildingUseTable.rowCount()
                dlg.buildingUseTable.insertRow(rowPosition)
                dlg.buildingUseTable.setItem(rowPosition , 0, QTableWidgetItem(data.user_definition_use)) 
                dlg.buildingUseTable.setItem(rowPosition , 1, QTableWidgetItem(data.DMM_use))
        else:
            dlg.buildingUseTable.setColumnCount(0)
            dlg.buildingUseTable.setRowCount(0)    
            
        
          
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - loadBuildingUseMapDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - loadBuildingUseMapDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
    
def openFieldUserMapDialog(planHeatDMM):
    """
        Open user field match dialog 
        field user map  dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        dialog = FieldUserMapDialog(planHeatDMM)   
       
        dialog.show()
        dialog.exec_()
        
        loadFieldUserMapTable(planHeatDMM)
        checkProcessLauncher(planHeatDMM)
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - openFieldUserMapDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - openFieldUserMapDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    

def loadFieldUserMapTable(planHeatDMM):   
    """
        load field use match data to main window table 
        building use  dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:    
        dlg = planHeatDMM.dlg
        if planHeatDMM.data.shpDMMFieldsMap:
            
            #shpRead = readShapeFileData(planHeatDMM, planHeatDMM.data.inputShapeFile)

            planHeatDMM.data.fieldsSHPMappingPosition = assignmentPositionFieldMap(planHeatDMM,planHeatDMM.data.shpDMMFieldsMap)
            #planHeatDMM.resources.log.write_log("INFO", "Shape file Mapping Fields")         
            
            if "BuildingUse" not in [field.fieldName for field in  planHeatDMM.data.shpDMMFieldsMap]:
                planHeatDMM.data.old_building_use_user_definition_value  = "NULL_VALUE"
                planHeatDMM.dlg.buildingUseTable.setColumnCount(0)
                planHeatDMM.dlg.buildingUseTable.setRowCount(0) 
                planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
                planHeatDMM.dlg.buildingUseTable.setEnabled(False)
                planHeatDMM.dlg.buildUseAddToolButton.setEnabled(False)
                planHeatDMM.dlg.buildingUseMatchLabel.setVisible(False)
                planHeatDMM.data.buildingUseMap = []
                planHeatDMM.data.boolBuildingUseMap = True
                for originShapeField in planHeatDMM.data.shp_map_csv_fields:
                    if "BuildingUse" == originShapeField.fieldName and originShapeField.fieldState.lower() == "optional":     
                        planHeatDMM.data.boolBuildingUseMap = False
                        break
                    
                        
                
                
            if "ProtectionDegree" not in [field.fieldName for field in  planHeatDMM.data.shpDMMFieldsMap]:
                planHeatDMM.data.old_protection_user_definition_value    = "NULL_VALUE"
                planHeatDMM.dlg.protectionLevelTable.setColumnCount(0)
                planHeatDMM.dlg.protectionLevelTable.setRowCount(0) 
                planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
                planHeatDMM.dlg.protectionLevelTable.setEnabled(False)
                planHeatDMM.dlg.protectionAddToolButton.setEnabled(False)
                planHeatDMM.dlg.protectionMatchLabel.setVisible(False)
                planHeatDMM.data.protectionLevelMap = []
                planHeatDMM.data.boolProtectionLevelMap = True
                for originShapeField in planHeatDMM.data.shp_map_csv_fields:
                    if "ProtectionDegree" == originShapeField.fieldName and originShapeField.fieldState.lower() == "mandatory":     
                        planHeatDMM.data.boolProtectionLevelMap = False
                        break
                       
            
            dlg.fieldUserTable.setColumnCount(3)
            horHeaders = ["Application Column Header     ","Cadaster Column Header    ", " Field State      " ]
            dlg.fieldUserTable.setHorizontalHeaderLabels(horHeaders)
            dlg.fieldUserTable.setRowCount(0)
            dlg.fieldUserTable.resizeColumnsToContents()
            dlg.fieldUserTable.resizeRowsToContents()
            for data in planHeatDMM.data.shpDMMFieldsMap:
                rowPosition = dlg.fieldUserTable.rowCount()
                dlg.fieldUserTable.insertRow(rowPosition) 
                dlg.fieldUserTable.setItem(rowPosition , 0, QTableWidgetItem(str(data.fieldName)))    
                dlg.fieldUserTable.setItem(rowPosition , 1, QTableWidgetItem(data.user_definition_field))
                dlg.fieldUserTable.setItem(rowPosition , 2, QTableWidgetItem(data.fieldState))  
                
                if data.fieldName == 'BuildingUse':
                    
                    planHeatDMM.dlg.buildingUseTable.setEnabled(True)
                    planHeatDMM.dlg.buildUseAddToolButton.setEnabled(True)
                    planHeatDMM.dlg.buildingUseMatchLabel.setVisible(True)
                    
                    if data.user_definition_field != planHeatDMM.data.old_building_use_user_definition_value:
                        planHeatDMM.data.old_building_use_user_definition_value = data.user_definition_field
                        
                        planHeatDMM.data.inputSHPFieldBuildingUseValues = retrieveInputSHPFieldMapping(planHeatDMM,planHeatDMM.data.shpBuildingRecords,planHeatDMM.data.fieldsSHPMappingPosition[data.fieldName])
                        """ 
                        shpRead = Shape_Reader(planHeatDMM.resources.log, planHeatDMM.data.inputShapeFile)
                        shpRead.readShapeFile()
                        
                        planHeatDMM.data.inputSHPFieldBuildingUseValues = shapeFileFieldsValues(planHeatDMM,shpRead.geometryAndRecordBuilding,position_field_map[data.fieldName])
                        """
                        
                        planHeatDMM.dlg.buildingUseTable.setColumnCount(0)
                        planHeatDMM.dlg.buildingUseTable.setRowCount(0) 
                        planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
                        planHeatDMM.data.boolBuildingUseMap = False
                        planHeatDMM.data.buildingUseMap = []
    
            
                elif data.fieldName == 'ProtectionDegree':
                    
                    planHeatDMM.dlg.protectionLevelTable.setEnabled(True)
                    planHeatDMM.dlg.protectionAddToolButton.setEnabled(True)
                    planHeatDMM.dlg.protectionMatchLabel.setVisible(True)
                        
                    if data.user_definition_field != planHeatDMM.data.old_protection_user_definition_value:
                        
                        planHeatDMM.data.old_protection_user_definition_value = data.user_definition_field
                        
                        """
                        shpRead = Shape_Reader(planHeatDMM.resources.log, planHeatDMM.data.inputShapeFile)
                        shpRead.readShapeFileHeaderFields()
                        shpRead.readShapeFile()
                        
                        planHeatDMM.data.inputSHPFieldProtectionDegreeValues = shapeFileFieldsValues(planHeatDMM,shpRead.geometryAndRecordBuilding,position_field_map[data.fieldName])
                        """
                        
                        planHeatDMM.data.inputSHPFieldProtectionDegreeValues = retrieveInputSHPFieldMapping(planHeatDMM,planHeatDMM.data.shpBuildingRecords,planHeatDMM.data.fieldsSHPMappingPosition[data.fieldName])
                        
                        planHeatDMM.dlg.protectionLevelTable.setColumnCount(0)
                        planHeatDMM.dlg.protectionLevelTable.setRowCount(0) 
                        planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
                        planHeatDMM.data.boolProtectionLevelMap = False
                        planHeatDMM.data.protectionLevelMap = []
                
            checkMandatoryFieldFilledData(planHeatDMM)
                
                  
        else:
            dlg.fieldUserTable.setColumnCount(0)
            dlg.fieldUserTable.setRowCount(0)
            planHeatDMM.dlg.fieldUserMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            
                    
            planHeatDMM.dlg.buildingUseTable.setColumnCount(0)
            planHeatDMM.dlg.buildingUseTable.setRowCount(0) 
            planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            planHeatDMM.dlg.buildingUseTable.setEnabled(False)
            planHeatDMM.dlg.buildUseAddToolButton.setEnabled(False)
            planHeatDMM.dlg.buildingUseMatchLabel.setVisible(False)
            planHeatDMM.data.boolBuildingUseMap = False
            planHeatDMM.data.buildingUseMap = []
    
            
            planHeatDMM.dlg.protectionLevelTable.setColumnCount(0)
            planHeatDMM.dlg.protectionLevelTable.setRowCount(0) 
            planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
            planHeatDMM.dlg.protectionLevelTable.setEnabled(False)
            planHeatDMM.dlg.protectionAddToolButton.setEnabled(False)
            planHeatDMM.dlg.protectionMatchLabel.setVisible(False)
            planHeatDMM.data.boolProtectionLevelMap = False
            planHeatDMM.data.protectionLevelMap = []
            
        
        
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - loadFieldUserMapTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - loadFieldUserMapTable",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        


def assignmentPositionFieldMap(planHeatDMM,shpDMMFieldsMap):
    try:
        # MAPPING FIELDS SHP TO CSV 4 JAVA
        position_field_map = {}
        for data in shpDMMFieldsMap:
            for x, item in enumerate(planHeatDMM.data.originShapeFields):
                if data.user_definition_field == item[0]:
                    position_field_map[data.fieldName]=x
                    break
        return position_field_map        
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - assignment_position_field_map Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - assignment_position_field_map",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        raise        
        

def readShapeFileData(planHeatDMM, filename):
    try:
        shpRead = Shape_Reader(planHeatDMM.resources.log, filename)
        shpRead.readShapeFile(read="records")
        return shpRead 
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - readShapeFileData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - readShapeFileData",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        raise        
 
    
def retrieveInputSHPFieldMapping(planHeatDMM,buildingRecords,position):
    try:
        
        return shapeFileFieldsValues(planHeatDMM,buildingRecords,position)
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - retrieveInputSHPFieldMapping Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - retrieveInputSHPFieldMapping",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        raise      
    

    
def methodSelectChanged(planHeatDMM):
    """
        Calculation Method 
        methodComboBox widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        text = planHeatDMM.dlg.methodComboBox.currentText()
        planHeatDMM.data.calculateMethod = text
        
        planHeatDMM.dlg.fieldUserTable.setColumnCount(0)
        planHeatDMM.dlg.fieldUserTable.setRowCount(0)   
        planHeatDMM.dlg.fieldUserMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        
        
        planHeatDMM.dlg.buildingUseTable.setColumnCount(0)
        planHeatDMM.dlg.buildingUseTable.setRowCount(0) 
        planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        
        planHeatDMM.dlg.protectionLevelTable.setColumnCount(0)
        planHeatDMM.dlg.protectionLevelTable.setRowCount(0) 
        planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
        
        planHeatDMM.data.boolShpDMMFieldsMap = False
        planHeatDMM.data.shpDMMFieldsMap = []
                
        planHeatDMM.data.boolBuildingUseMap     = False
        planHeatDMM.data.buildingUseMap = []
        
        planHeatDMM.data.boolProtectionLevelMap = False
        planHeatDMM.data.protectionLevelMap = []
        
        planHeatDMM.dlg.buildingUseTable.setEnabled(False)
        planHeatDMM.dlg.buildUseAddToolButton.setEnabled(False)
        planHeatDMM.dlg.buildingUseMatchLabel.setVisible(False)

        planHeatDMM.dlg.protectionLevelTable.setEnabled(False)
        planHeatDMM.dlg.protectionAddToolButton.setEnabled(False)
        planHeatDMM.dlg.protectionMatchLabel.setVisible(False)

        planHeatDMM.data.refurbishmentTabDataList = createDefaultRefurbishmentTabData(planHeatDMM)
        planHeatDMM.data.refurbishmentSimplifiedData = 0
        
        
        if text.lower() == "simplified":
            
            planHeatDMM.dlg.buildingUseTable.setEnabled(False)
            planHeatDMM.dlg.buildUseAddToolButton.setEnabled(False)
            planHeatDMM.dlg.buildingUseMatchLabel.setVisible(False)
            
            planHeatDMM.dlg.protectionLevelTable.setEnabled(False)
            planHeatDMM.dlg.protectionAddToolButton.setEnabled(False)
            planHeatDMM.dlg.protectionMatchLabel.setVisible(False)
            
         
        checkProcessLauncher(planHeatDMM)    
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - methodSelectChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - methodSelectChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        


def countrySelectChanged(planHeatDMM):
    """
        Country selection
        countryComboBox widget slot
        :param planHeatDMM : Application Object
            
    """
    
    try:
        text = planHeatDMM.dlg.countryComboBox.currentText()
        
        for data in planHeatDMM.data.countries.values():
            if data.country == text: 
                planHeatDMM.data.country = data.country
                planHeatDMM.data.country_id = data.id
                break
        
        checkProcessLauncher(planHeatDMM)
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - methodSelectChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - methodSelectChanged",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        



def checkBuildingUseMapFilledData(planHeatDMM):
    """
        Control building use, mapped data
        :param planHeatDMM : Application Object
            
    """  
    try:
         
        AllFields = [x.use for x in planHeatDMM.data.buildingUse if x.use.lower() not in ("not evaluate")]
        mappedFields    = [x.DMM_use for x in planHeatDMM.data.buildingUseMap if x.DMM_use.lower() not in ("not evaluate")]
        
        
        if len(mappedFields) == len(planHeatDMM.data.inputSHPFieldBuildingUseValues):
            planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_right_icon)
            planHeatDMM.data.boolBuildingUseMap = True
        else:    
            if mappedFields:
                for field in AllFields:
                    
                    if field not in (mappedFields):
                        planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_warning_icon)
                        planHeatDMM.data.boolBuildingUseMap = True
                        break
                else:    
                    planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_right_icon)
                    planHeatDMM.data.boolBuildingUseMap = True
            else:
                planHeatDMM.dlg.buildingUseMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
                planHeatDMM.data.boolBuildingUseMap = False        
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - checkBuildingUseMapFilledData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - checkBuildingUseMapFilledData",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))       


def checkProtectionLevelMapFilledData(planHeatDMM):
    """
        Control protection level, mapped data
        :param planHeatDMM : Application Object
            
    """  
    try:
         
        AllFields = [x.protectionLevel for x in planHeatDMM.data.protectionLevels]
        mappedFields    = [x.DMM_protection_level for x in planHeatDMM.data.protectionLevelMap]
        
        if len(mappedFields) == len(planHeatDMM.data.inputSHPFieldProtectionDegreeValues):
            planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_right_icon)
            planHeatDMM.data.boolProtectionLevelMap = True
        else:   
            if mappedFields:
                for field in AllFields:
                    
                    if field not in (mappedFields):
                        planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_warning_icon)
                        planHeatDMM.data.boolProtectionLevelMap = True
                        break
                else:    
                    planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_right_icon)
                    planHeatDMM.data.boolProtectionLevelMap = True
            else:
                planHeatDMM.dlg.protectionMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)      
                planHeatDMM.data.boolProtectionLevelMap = False  
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - checkProtectionLevelMapFilledData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - checkProtectionLevelMapFilledData",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))       



def checkMandatoryFieldFilledData(planHeatDMM):
    """
        Check mandatory fields mapped
        :param planHeatDMM : Application Object
            
    """
    try:
         
        #mandatoryFields = [x.fieldName for x in planHeatDMM.data.shp_map_csv_fields if x.fieldState.lower() == "mandatory" and ( x.calculateModel == planHeatDMM.data.calculateMethod or x.calculateModel == "Both")]
        mandatoryFields = [x.fieldName for x in planHeatDMM.data.shp_map_csv_fields if x.fieldState.lower() == "mandatory" and ( x.calculateModel == planHeatDMM.data.calculateMethod or x.calculateModel == "Both")]
        mappedFields    = [x.fieldName for x in planHeatDMM.data.shpDMMFieldsMap]
        
             
        for mandatory in mandatoryFields:
            
            if mandatory not in (mappedFields):
                planHeatDMM.dlg.fieldUserMatchLabel.setPixmap(planHeatDMM.resources.pixmap_wrong_icon)
                planHeatDMM.data.boolShpDMMFieldsMap = False 
                break
        else:    
            planHeatDMM.dlg.fieldUserMatchLabel.setPixmap(planHeatDMM.resources.pixmap_right_icon)
            planHeatDMM.data.boolShpDMMFieldsMap = True  
            
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - checkMandatoryFieldFilledData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - checkMandatoryFieldFilledData",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
        

def checkProcessLauncher(planHeatDMM):
    """
        Check all required fields are correctly filled
        :param planHeatDMM : Application Object
            
    """
    if planHeatDMM.data.calculateMethod.lower() == "simplified":
        
        if planHeatDMM.data.boolProjectName and planHeatDMM.data.boolAreaName and  planHeatDMM.data.boolCountry  \
           and planHeatDMM.data.boolInputShapeFile  and planHeatDMM.data.boolOutputSaveFile and planHeatDMM.data.boolCalculateMethod  \
           and planHeatDMM.data.boolShpDMMFieldsMap:
            
            if  planHeatDMM.dlg.lidarCheckBox.isChecked():
                if planHeatDMM.data.boolDTMDirectory and planHeatDMM.data.boolDSMDirectory:          
                    planHeatDMM.dlg.processButton.setEnabled(True)
                else:
                    planHeatDMM.dlg.processButton.setEnabled(False)
                        
            else:
                planHeatDMM.dlg.processButton.setEnabled(True)
        else:
            planHeatDMM.dlg.processButton.setEnabled(False)
        
    else:
        
        if planHeatDMM.data.boolProjectName and planHeatDMM.data.boolAreaName and  planHeatDMM.data.boolCountry \
           and planHeatDMM.data.boolInputShapeFile    and planHeatDMM.data.boolOutputSaveFile and planHeatDMM.data.boolCalculateMethod \
           and planHeatDMM.data.boolShpDMMFieldsMap and planHeatDMM.data.boolBuildingUseMap and planHeatDMM.data.boolProtectionLevelMap:
            
            if  planHeatDMM.dlg.lidarCheckBox.isChecked():
                if planHeatDMM.data.boolDTMDirectory and planHeatDMM.data.boolDSMDirectory:          
                    planHeatDMM.dlg.processButton.setEnabled(True)
                else:
                    planHeatDMM.dlg.processButton.setEnabled(False) 
                       
            else:
                planHeatDMM.dlg.processButton.setEnabled(True)
        else:
            planHeatDMM.dlg.processButton.setEnabled(False)    
        
             
    
"""
    FOR FUTURE USE
def launchProcessClick(planHeatDMM):
    
        Process button clicked
        :param planHeatDMM : Application Object
            
    
    try:
        
        scheduler = sched.scheduler(time.time, time.sleep)
        planHeatDMM.resources.log.write_log("INFO","initWindowbehavior - launchProcessClick scheduled seconds:" + "5" )
        scheduler.enter(30, 1, launchProcess, (planHeatDMM,))
        scheduler.run(blocking=True)
        #launchProcess(planHeatDMM)
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - launchProcessClick Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - launchProcessClick",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
                    

"""

def setCurrentProjetPaths(planHeatDMM):
    current_dmm_path = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                    master_mapping_config.DMM_FOLDER)
    planHeatDMM.data.inputShapeFile = os.path.join(current_dmm_path,
                                                   master_mapping_config.DMM_INPUT_SHAPE_FILE_NAME + ".shp")
    planHeatDMM.data.outputSaveFile = os.path.join(current_dmm_path,
                                                   master_mapping_config.DMM_PREFIX)

def launchProcess(planHeatDMM):
    """
        Create process thread and manage interface
        :param planHeatDMM : Application Object
            
    """
    
    try:
        FieldUserMapDialog.addAllFieldsStatic(planHeatDMM)

        if not planHeatDMM.dlg.detailFileCheckBox.isChecked() \
        or not planHeatDMM.dlg.retrofittedScenariosCheckBox.isChecked():
            msg = QMessageBox(planHeatDMM.dlg)    
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setText("Both 'hourly demand' and 'retrofitted Scenarios' options must be activated for the planning module."
                            +" Do you still want to lanch process ?")
            msg.setWindowTitle("Unchecked options")
            response = msg.exec_()

            if response == QMessageBox.No:
                return
        
        planHeatDMM.dlg.processButton.setEnabled(False)

        setCurrentProjetPaths(planHeatDMM)
        """
        Cambio de cursor cuando corre el proceso
        """
        #&planHeatDMM.dlg.setEnabled(False)
        planHeatDMM.data.processContinue = True
        planHeatDMM.resources.thread_clock = None
        planHeatDMM.resources.thread = Worker(planHeatDMM)
       
        planHeatDMM.resources.thread.progress_update.connect(updateProgressBar)
        planHeatDMM.resources.thread.progress_total.connect(totalProgressBar)
        planHeatDMM.resources.thread.message_update.connect(updateMessageLabel)
        planHeatDMM.resources.thread.unlock_interface.connect(unlock_interface)
        planHeatDMM.resources.thread_clock.clock_refresh.connect(clock_refresh)
        planHeatDMM.resources.thread.showMessageDialog.connect(showMessageDialog)
        planHeatDMM.resources.thread.loadShapeGeneratedFile.connect(loadShapeGeneratedFile)
        planHeatDMM.resources.thread.changeStatusProcessButton.connect(changeStatusProcessButton)
        
        temp = planHeatDMM.data.shpBuildingRecords[:]
        planHeatDMM.data.shpBuildingRecords = []
        
        planHeatDMM.data.baselineScenarioYear = int(planHeatDMM.dlg.baselineScenarioYearSpinBox.value())

        if Config.USE_PERSIST_SCENARIO in ("Y","y"):
            with open(planHeatDMM.data.outputSaveFile + ".scn", "wb") as scenarioFile:
                pickle.dump(planHeatDMM.data, scenarioFile, protocol=pickle.HIGHEST_PROTOCOL)     
                planHeatDMM.resources.log.write_log("INFO", "Save current scenario")
        
        
        planHeatDMM.data.shpBuildingRecords = temp
        
        lock_interface(planHeatDMM)
        planHeatDMM.resources.thread.setTerminationEnabled(True)
        planHeatDMM.resources.thread.start( priority = Config.PROCESS_THREAD_PRIORITY)
        
                    
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - launchProcess Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - launchProcess",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
        
        
def stopProcess(planHeatDMM, ask=True):
    """
        Stop thread process 
        :param planHeatDMM : Application Object
        :param ask : Show message Dialog True/False
    """
    
    
    try:
        if  planHeatDMM.resources.thread is not None and planHeatDMM.resources.thread.isRunning():
            message = "Really, do you want to stop the process?"
            if ask:
                if showQuestiondialog(planHeatDMM.dlg,"Stop Process",message) == QtWidgets.QMessageBox.Yes:
                    planHeatDMM.data.processContinue = False
                    planHeatDMM.dlg.statusMessageLabel.setText("Process cancel request by user")
            else:
                planHeatDMM.data.processContinue = False
       
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - stopProcess Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - stopProcess",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))            

def showLogProcessFile(planHeatDMM):
    """
        Open log file file dialog 
        Process log file dialog widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        if  planHeatDMM.resources.thread is not None and not planHeatDMM.resources.thread.isRunning():
            dialog = LogFileDialog(planHeatDMM)   
            dialog.show()
            dialog.exec_()
                
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - showLogProcessFile Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - showLogProcessFile",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))            
        
    
def totalProgressBar(value,planHeatDMM):
    """
        Set Maximun value to current process to progress bar
        ProgressBar widget slot
        :param planHeatDMM : Application Object
            
    """
    planHeatDMM.dlg.statusProgressBar.setMaximum(value)
    
    
def updateProgressBar(value,planHeatDMM):
    """
        Refresh progressbar value 
        ProgressBar widget slot
        :param planHeatDMM : Application Object
            
    """
    planHeatDMM.dlg.statusProgressBar.setValue(value)
    
    
def updateMessageLabel(message,planHeatDMM):    
    """
        Set message to status bar 
        statusbar label widget slot
        :param planHeatDMM : Application Object
            
    """
    planHeatDMM.dlg.statusMessageLabel.setText(message)
    
    
def clock_refresh(value,planHeatDMM):    
    """
        Refresh clock label 
        clock label widget slot
        :param planHeatDMM : Application Object
            
    """
    try:
        hour = int(value / 3600)
        minute = int((value % 3600) / 60)
        second = int((value % 3600) % 60)
        clock_text = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
        planHeatDMM.dlg.statusTimeLabel.setText(clock_text)
   
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - clock_refresh Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
                    
                    
def lock_interface(planHeatDMM):
    """
        Lock interface when process is running 
        :param planHeatDMM : Application Object
            
    """
    try:
        planHeatDMM.dlg.setCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        planHeatDMM.dlg.projectLineEdit.setEnabled(False)
        planHeatDMM.dlg.areaLineEdit.setEnabled(False)
        planHeatDMM.dlg.loadFileToolButton.setEnabled(False)
        planHeatDMM.dlg.saveFileToolButton.setEnabled(False)
        planHeatDMM.dlg.loadFileLineEdit.setEnabled(False)
        planHeatDMM.dlg.saveFileLineEdit.setEnabled(False)
        planHeatDMM.dlg.countryComboBox.setEnabled(False)
        planHeatDMM.dlg.baselineScenarioYearSpinBox.setEnabled(False)
        planHeatDMM.dlg.lidarCheckBox.setEnabled(False)
        planHeatDMM.dlg.detailFileCheckBox.setEnabled(False)
        planHeatDMM.dlg.retrofittedScenariosCheckBox.setEnabled(False)
        planHeatDMM.dlg.retrofittedScenariosToolbutton.setEnabled(False)
        planHeatDMM.dlg.openShapeFileCheckBox.setEnabled(False)
        planHeatDMM.dlg.DTMToolButton.setEnabled(False)
        planHeatDMM.dlg.DSMToolButton.setEnabled(False)
        planHeatDMM.dlg.DTMLineEdit.setEnabled(False)
        planHeatDMM.dlg.DSMLineEdit.setEnabled(False)
        planHeatDMM.dlg.methodComboBox.setEnabled(False)
        planHeatDMM.dlg.fieldAddToolButton.setEnabled(False)
        planHeatDMM.dlg.fieldUserTable.setEnabled(False)
        planHeatDMM.dlg.buildingUseTable.setEnabled(False)
        planHeatDMM.dlg.buildUseAddToolButton.setEnabled(False)
        planHeatDMM.dlg.protectionLevelTable.setEnabled(False)
        planHeatDMM.dlg.protectionAddToolButton.setEnabled(False)
        planHeatDMM.dlg.processButton.setEnabled(False)
        planHeatDMM.dlg.loadScenario.setEnabled(False)
        planHeatDMM.dlg.statusTimeLabel.setEnabled(True)
        
        planHeatDMM.dlg.statusProcessButton.setIcon(planHeatDMM.resources.icon_halt_icon)
        planHeatDMM.dlg.statusProcessButton.setToolTip("Stop Process")
        planHeatDMM.dlg.statusProcessButton.setEnabled(True)
        planHeatDMM.dlg.statusProcessButton.setVisible(True)
        planHeatDMM.dlg.statusProgressBar.setVisible(True)
        planHeatDMM.dlg.statusProcessButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        
        
        
        
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - lock_interface Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - lock_interface",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))            
    
        
def unlock_interface(planHeatDMM):
    """
        Unkock interface when process is finished 
        :param planHeatDMM : Application Object
            
    """

    try:
        # planHeatDMM.dlg.projectLineEdit.setEnabled(True)
        planHeatDMM.dlg.areaLineEdit.setEnabled(True)
        planHeatDMM.dlg.loadFileToolButton.setEnabled(True)
        # planHeatDMM.dlg.saveFileToolButton.setEnabled(True)
        planHeatDMM.dlg.lidarCheckBox.setEnabled(True)
        planHeatDMM.dlg.loadFileLineEdit.setEnabled(True)
        # planHeatDMM.dlg.saveFileLineEdit.setEnabled(True)
            
        planHeatDMM.dlg.methodComboBox.setEnabled(True)
        planHeatDMM.dlg.fieldAddToolButton.setEnabled(True)
        planHeatDMM.dlg.fieldUserTable.setEnabled(True)
        planHeatDMM.dlg.processButton.setEnabled(True)
        planHeatDMM.dlg.countryComboBox.setEnabled(True)
        planHeatDMM.dlg.baselineScenarioYearSpinBox.setEnabled(True)
        planHeatDMM.dlg.detailFileCheckBox.setEnabled(True)
        #planHeatDMM.dlg.loadScenario.setEnabled(True)
        
        if planHeatDMM.data.pluginLaunch == True and 'qgis.core' in sys.modules and 'qgis.gui' in sys.modules: 
            planHeatDMM.dlg.openShapeFileCheckBox.setEnabled(True)
        
        planHeatDMM.dlg.retrofittedScenariosCheckBox.setEnabled(True)
        
        if planHeatDMM.dlg.retrofittedScenariosCheckBox.isChecked():  
            planHeatDMM.dlg.retrofittedScenariosToolbutton.setEnabled(True)
            
        
        
        if  planHeatDMM.dlg.lidarCheckBox.isChecked():  
            planHeatDMM.dlg.DTMToolButton.setEnabled(True)
            planHeatDMM.dlg.DSMToolButton.setEnabled(True)
            planHeatDMM.dlg.DTMLineEdit.setEnabled(True)
            planHeatDMM.dlg.DSMLineEdit.setEnabled(True)
        
            
            
        if  planHeatDMM.dlg.methodComboBox.currentText().lower() != "simplified":
            
            planHeatDMM.dlg.buildingUseTable.setEnabled(True)
            planHeatDMM.dlg.buildUseAddToolButton.setEnabled(True)
            planHeatDMM.dlg.protectionLevelTable.setEnabled(True)
            planHeatDMM.dlg.protectionAddToolButton.setEnabled(True)
            
        planHeatDMM.dlg.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        
        planHeatDMM.dlg.update()
    
    except:
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - unlock_interface Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - unlock_interface",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))            



def showMessageDialog(typeDialog, title,message,planHeatDMM):   
    """
        Show application error dialog to user
        :param typeDialog : type of message dialog
        :param title : Title of message
        :param message : Error message
        :param planHeatDMM : Application Object
            
    """
    
    try:
        parent = planHeatDMM.dlg
         
        if typeDialog == "CRITICAL":
            showErrordialog(parent,title,message)
        elif typeDialog =="OK":
            showInfodialog(parent,title,message)
        elif typeDialog =="WARN":
            showWarningdialog(parent,title,message)
        elif typeDialog =="QUESTION":
            showQuestiondialog(parent,title,message)    
        else:
            showErrordialog(parent,title,message)        
                
    except:
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - showMessageDialog",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))     
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - showMessageDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
                    
       
def changeStatusProcessButton(message,icon, planHeatDMM):   
    """
        Update Status Process Button 
        :param message : Tooltip message
        :param icon :    show icon
        :param planHeatDMM : Application Object
    """
    
    try:
        if icon:
            planHeatDMM.dlg.statusProcessButton.setIcon(icon)
        if message:    
            planHeatDMM.dlg.statusProcessButton.setToolTip(message)
    except:
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - changeStatusProcessButton",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))     
        planHeatDMM.resources.log.write_log("ERROR","initWindowbehavior - changeStatusProcessButton Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
                    


def loadShapeGeneratedFile(shapeFileName, layerName,planHeatDMM):
    """
        Load generated file to Qgis interface layer
        :param planHeatDMM : Application Object
            
    """

    try:
        planHeatDMM.resources.log.write_log("INFO", "Try to Load Shape File to Canvas:" + shapeFileName)
        layer = QgsVectorLayer(shapeFileName, layerName, "ogr")
        QgsProject().instance().addMapLayer(layer)
        planHeatDMM.resources.log.write_log("INFO", "Load Shape File to Canvas:" + shapeFileName)
        
        
    except Exception as e:          
        planHeatDMM.resources.log.write_log("ERROR", "initWindowbehavior - loadShapeGeneratedFile  Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowbehavior - loadShapeGeneratedFile",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    


def createDefaultRefurbishmentTabData(planHeatDMM):
    try:
        planHeatDMM.data.refurbishmentTabDataList = []
        for i, use in enumerate([building_use for building_use in planHeatDMM.data.buildingUse if building_use.use.lower() not in ('not evaluate')]):
            tabData = RefurbishmentTabData(i,use.use,True)
            for x, period in enumerate(planHeatDMM.data.periods):
                rowData = RowRefurbishTableData() 
                rowData.row_index = x
                rowData.row_period_id   = period.id
                rowData.row_period_text = period.period_text
                rowData.row_refurbishment_level = "None"
                rowData.row_roof_percentage     = 100
                rowData.row_wall_percentage     = 100
                rowData.row_window_percentage   = 100
                
                tabData.rows.append(rowData)
                
            
            planHeatDMM.data.refurbishmentTabDataList.append(tabData)
            
        return planHeatDMM.data.refurbishmentTabDataList
         
    except Exception as e:          
        planHeatDMM.resources.log.write_log("ERROR", "initWindowStatus - createDefaultRefurbishmentTabData  Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowStatus - createDefaultRefurbishmentTabData",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        return planHeatDMM.refurbishmentTabDataList    
     
            
       
def loadScenario(planHeatDMM, file_path=None):
    try:
        
        planHeatDMM.dlg.statusMessageLabel.setText("Loading Scenario...")
        if file_path is None:
            fname, _ = QFileDialog.getOpenFileName(planHeatDMM.dlg, 'Open Scenario File...',Config.PLUGIN_DIR,"scenario files *.scn")
        else:
            fname = file_path
        if fname is not None and fname != "":
            
            with open(fname, "rb") as fichero:
                load_data = pickle.load(fichero)
                
                if  planHeatDMM.data.scenarioName != load_data.scenarioName:
                    raise LoadScenarioException("Saved scenario name: {} different from application scenario name: {}".format(load_data.scenarioName,planHeatDMM.data.scenarioName))
                
                if  planHeatDMM.data.scenarioVersion != load_data.scenarioVersion:
                    raise LoadScenarioException("Saved scenario version number: {:d} different from application scenario version number: {:d}".format(load_data.scenarioVersion,planHeatDMM.data.scenarioVersion))
                
                
                countries = [data.country for data in planHeatDMM.data.countries.values()]
                if not load_data.country in countries:
                    raise LoadScenarioException("Saved Scenario, has a wrong value location:" + str(load_data.country))
                
                
                if not load_data.calculateMethod in planHeatDMM.data.calculateMethodList:
                    raise LoadScenarioException("Saved Scenario, has a wrong value method:" + str(load_data.calculateMethod))
                
                if load_data.DTMDirectory and load_data.DSMDirectory:
                    if os.path.isdir(load_data.DTMDirectory) and check_LIDAR_files(load_data.DTMDirectory) and check_no_other_files(load_data.DTMDirectory):
                        pass
                    else:
                        raise LoadScenarioException("Saved Scenario, has a wrong value DTM Directory:" + str(load_data.DTMDirectory))
                        
                    if os.path.isdir(load_data.DSMDirectory) and check_LIDAR_files(load_data.DSMDirectory) and check_no_other_files(load_data.DSMDirectory):
                        pass
                    else:
                        raise LoadScenarioException("Saved Scenario, has a wrong value DSM Directory:" + str(load_data.DSMDirectory))
              
              
                fname = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                     master_mapping_config.DMM_FOLDER,
                                     master_mapping_config.DMM_INPUT_SHAPE_FILE_NAME + ".shp")
                if os.path.isfile(fname) and fname.endswith(".shp"):
                    if not controlEPSG(planHeatDMM,fname):
                        raise LoadScenarioException("Saved Scenario shape file, EPSG code is not valid, you must provide a correct value")
                    
                    retrieveShapeHeaderFields(planHeatDMM,fname)
                    
                    fileFields     = set([shp_file_field[0] for shp_file_field in planHeatDMM.data.originShapeFields])
                    selectedFields = set([shp_csv_input_field.user_definition_field  for shp_csv_input_field in load_data.shpDMMFieldsMap])
                    selectedUserShapeFields = set([userFieldShapeMap.key  for userFieldShapeMap in load_data.userFieldShapeMap]) 
                    planHeatDMM.data.fieldsSHPMappingPosition = assignmentPositionFieldMap(planHeatDMM,load_data.shpDMMFieldsMap)
                    
                    if selectedFields.issubset(fileFields) and selectedUserShapeFields.issubset(fileFields):
                       
                        if load_data.calculateMethod == "Complete":
                            #######################################################################################
                            # Load fields in MainWindow tables and check values for types of use and protection levels
                            #######################################################################################
                            #shpRead = readShapeFileData(planHeatDMM, fname)
                            planHeatDMM.data.shpBuildingRecords = readShapeFileData(planHeatDMM, fname).recordBuilding
                            
                            if  planHeatDMM.data.fieldsSHPMappingPosition.get("BuildingUse",False):  
                                planHeatDMM.data.inputSHPFieldBuildingUseValues      = retrieveInputSHPFieldMapping(planHeatDMM,planHeatDMM.data.shpBuildingRecords,planHeatDMM.data.fieldsSHPMappingPosition["BuildingUse"])
                                buildingUseShapeSet        = set(planHeatDMM.data.inputSHPFieldBuildingUseValues)
                                buildingUseSelectedSet     = set([data.user_definition_use for data in load_data.buildingUseMap])
                                
                                
                                # Building uses
                                if buildingUseSelectedSet.issubset(buildingUseShapeSet):
                                    difference = buildingUseShapeSet.difference(buildingUseSelectedSet)
                                    if difference: 
                                        for use  in difference:
                                            build_use = BuildingUseMap()
                                            build_use.DMM_use   = "Not Evaluate"
                                            build_use.user_definition_use = use  
                                            load_data.buildingUseMap.append(build_use)
                                        else:
                                            showInfodialog(planHeatDMM.dlg,"Load Scenario","Shape file has new building use not mapped on the scenario, have been mapped as not evaluate")    
                                else:    
                                    raise LoadScenarioException("Saved Scenario shape file, Building use selected not exist on the file")
                            
                            
                           
                            if  planHeatDMM.data.fieldsSHPMappingPosition.get("ProtectionDegree",False):  
                                planHeatDMM.data.inputSHPFieldProtectionDegreeValues = retrieveInputSHPFieldMapping(planHeatDMM,planHeatDMM.data.shpBuildingRecords,planHeatDMM.data.fieldsSHPMappingPosition["ProtectionDegree"])
                                protectionLevelShapeSet    = set(planHeatDMM.data.inputSHPFieldProtectionDegreeValues)
                                protectionLevelSelectedSet = set([data.user_definition_protection for data in load_data.protectionLevelMap])
                                #Protection Levels
                                if protectionLevelSelectedSet.issubset(protectionLevelShapeSet):
                                    difference = protectionLevelShapeSet.difference(protectionLevelSelectedSet)
                                    if difference:
                                        for protection  in difference:
                                            protection_level = ProtectionLevelMap()
                                            protection_level.DMM_protection_level = 0
                                            protection_level.user_definition_protection = protection 
                                            load_data.protectionLevelMap.append(protection_level)
                                        else:
                                            showInfodialog(planHeatDMM.dlg,"Load Scenario","Shape file has new protection not mapped on the scenario, have been mapped as 0")
                                else:    
                                    raise LoadScenarioException("Saved Scenario shape file, Protection level selected not exist on the file")
                                    
                                    
                            
                            planHeatDMM.dlg.methodComboBox.setCurrentText(load_data.calculateMethod)    
                            planHeatDMM.dlg.loadFileLineEdit.setText(fname)
                            
                        else:  #Simplified 
                            planHeatDMM.dlg.methodComboBox.setCurrentText(load_data.calculateMethod)
                            planHeatDMM.dlg.loadFileLineEdit.setText(fname) 
                    else:
                        if not selectedFields.issubset(fileFields):
                            raise LoadScenarioException("Saved Scenario shape file, has selected shape field that not exist on the file")
                        else:
                            raise LoadScenarioException("Saved Scenario shape file, has selected user shape field that not exist on the file")
                    
                else:
                    raise LoadScenarioException("Saved Scenario, not exist shape file: " + str(fname))    
                    
               
                copyData(planHeatDMM.data,load_data)    
                
                #planHeatDMM.data = deepcopy(load_data)
                
                planHeatDMM.dlg.countryComboBox.setCurrentText(planHeatDMM.data.country)                
                planHeatDMM.dlg.DTMLineEdit.setText(planHeatDMM.data.DTMDirectory)
                planHeatDMM.dlg.DSMLineEdit.setText(planHeatDMM.data.DSMDirectory)
                loadFieldUserMapTable(planHeatDMM)
                loadBuildingUseMapTable(planHeatDMM)
                loadProtectionLevelMapTable(planHeatDMM)

                
                
                if  planHeatDMM.data.pluginLaunch == False:
                    planHeatDMM.data.boolOpenGeneratedShape = False

                planHeatDMM.dlg.openShapeFileCheckBox.setChecked(planHeatDMM.data.boolOpenGeneratedShape)
                
                planHeatDMM.dlg.projectLineEdit.setText(planHeatDMM.data.projectName)
                planHeatDMM.dlg.areaLineEdit.setText(planHeatDMM.data.areaName)
                planHeatDMM.data.outputSaveFile = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                                               master_mapping_config.DMM_FOLDER,
                                                               master_mapping_config.DMM_PREFIX)
                planHeatDMM.dlg.saveFileLineEdit.setText(planHeatDMM.data.outputSaveFile)
                
                planHeatDMM.dlg.detailFileCheckBox.setChecked(planHeatDMM.data.boolHourlyDetailFile)
                planHeatDMM.dlg.retrofittedScenariosCheckBox.setChecked(planHeatDMM.data.boolRetrofittedScenarios)
                
                
                
                if planHeatDMM.data.DTMDirectory:
                    planHeatDMM.dlg.lidarCheckBox.setChecked(True)
                else:
                    planHeatDMM.dlg.lidarCheckBox.setChecked(False)
                    
                checkProcessLauncher(planHeatDMM)    
                
                planHeatDMM.resources.log.write_log("INFO", "Load saved scenario")
                   
          
    
    
    except LoadScenarioException as e:
        planHeatDMM.resources.log.write_log("ERROR", "initWindowbehavior - loadScenario  LoadScenarioException:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowStatus - LoadScenarioException",str(sys.exc_info()[1]))
    except pickle.PickleError:
        planHeatDMM.resources.log.write_log("ERROR", "initWindowbehavior - loadScenario  Pickle error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowStatus - loadScenario PickleError",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      

    except Exception as e:          
        planHeatDMM.resources.log.write_log("ERROR", "initWindowbehavior - loadScenario  Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        showErrordialog(planHeatDMM.dlg,"initWindowStatus - loadScenario",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
    finally:
        planHeatDMM.dlg.statusMessageLabel.setText("Application ready...")      
              
            
            
def copyData(dataDest,dataSource):
    
    dataDest.processContinue  = dataSource.processContinue
    dataDest.closeWindow      = dataSource.closeWindow 
    #dataDest.pluginLaunch     = dataSource.pluginLaunch
    
    # Check Process Launcher 
    dataDest.boolProjectName          = dataSource.boolAreaName
    dataDest.boolAreaName             = dataSource.boolProjectName
    dataDest.boolCountry              = dataSource.boolCountry
    dataDest.boolInputShapeFile       = dataSource.boolInputShapeFile
    dataDest.boolOutputSaveFile       = dataSource.boolOutputSaveFile
    dataDest.boolDTMDirectory         = dataSource.boolDTMDirectory
    dataDest.boolDSMDirectory         = dataSource.boolDSMDirectory
    dataDest.boolCalculateMethod      = dataSource.boolCalculateMethod
    dataDest.boolHourlyDetailFile     = dataSource.boolHourlyDetailFile
    dataDest.boolRetrofittedScenarios = dataSource.boolRetrofittedScenarios
    dataDest.boolOpenGeneratedShape   = dataSource.boolOpenGeneratedShape
    dataDest.boolShpDMMFieldsMap      = dataSource.boolShpDMMFieldsMap
    dataDest.boolBuildingUseMap       = dataSource.boolBuildingUseMap
    dataDest.boolProtectionLevelMap   = dataSource.boolProtectionLevelMap
    dataDest.boolAddShapeFields       = dataSource.boolAddShapeFields
    
    #dataDest.fileJar         = dataSource.fileJar
    dataDest.projectName            = dataSource.projectName
    dataDest.areaName               = dataSource.areaName
    dataDest.inputShapeFile         = dataSource.inputShapeFile
    dataDest.outputSaveFile         = dataSource.outputSaveFile
    dataDest.DTMDirectory           = dataSource.DTMDirectory
    dataDest.DSMDirectory           = dataSource.DSMDirectory
    dataDest.calculateMethod        = dataSource.calculateMethod
    dataDest.country                = dataSource.country
    dataDest.country_id             = dataSource.country_id
    dataDest.baselineScenarioYear   = dataSource.baselineScenarioYear
    dataDest.futureScenarioYear     = dataSource.futureScenarioYear
    
    
    #dataDest.spatialReferenceEPSG = dataSource.spatialReferenceEPSG
    #dataDest.spatialReferenceWKT  = dataSource.spatialReferenceWKT
    
    dataDest.old_building_use_user_definition_value = dataSource.old_building_use_user_definition_value
    dataDest.old_protection_user_definition_value   = dataSource.old_protection_user_definition_value
    
    
    dataDest.buildingUseMap                      = deepcopy(dataSource.buildingUseMap)
    dataDest.protectionLevelMap                  = deepcopy(dataSource.protectionLevelMap)
    dataDest.shpDMMFieldsMap                     = deepcopy(dataSource.shpDMMFieldsMap)
    dataDest.userFieldShapeMap                   = deepcopy(dataSource.userFieldShapeMap)
    dataDest.shp_map_csv_fields                  = deepcopy(dataSource.shp_map_csv_fields)   
    #dataDest.inputSHPFieldBuildingUseValues      = deepcopy(dataSource.inputSHPFieldBuildingUseValues)
    #dataDest.inputSHPFieldProtectionDegreeValues = deepcopy(dataSource.inputSHPFieldProtectionDegreeValues)
    #Not necessary auto calculated at loadFieldUserMapTable
    #dataDest.fieldsSHPMappingPosition=deepcopy(dataSource.fieldsSHPMappingPosition)
    
    
    dataDest.refurbishmentTabDataList = deepcopy(dataSource.refurbishmentTabDataList)
    dataDest.refurbishmentSimplifiedData = dataSource.refurbishmentSimplifiedData
