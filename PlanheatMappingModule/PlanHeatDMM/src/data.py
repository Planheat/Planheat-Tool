# -*- coding: utf-8 -*-
"""
   Plugin Process Data
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 06 Oct. 2017
"""

__docformat__ = "restructuredtext"


from utility import constants as Constants

class Data():
    """ Properties used by the process & interface Data"""


    def __init__(self, plugin=True):
        '''
        Constructor
        '''

        self.processContinue  = True
        self.closeWindow      = False
        self.pluginLaunch     = plugin
        
        self.scenarioName     = Constants.SCENARIO_NAME
        self.scenarioVersion  = Constants.SCENARIO_VERSION 
        
        
        # Check Process Launcher 
        # self.boolProjectName          = False
        self.boolProjectName          = True
        self.boolAreaName             = False
        self.boolCountry              = True
        self.boolInputShapeFile       = False
        # self.boolOutputSaveFile       = False
        self.boolOutputSaveFile       = True
        self.boolDTMDirectory         = False
        self.boolDSMDirectory         = False
        self.boolCalculateMethod      = True
        self.boolHourlyDetailFile     = False
        self.boolRetrofittedScenarios = False
        self.boolOpenGeneratedShape   = False
        self.boolShpDMMFieldsMap      = False
        self.boolBuildingUseMap       = False
        self.boolProtectionLevelMap   = False
        self.boolAddShapeFields       = False
        
        
        self.baselineScenarioYear     = 0
        self.futureScenarioYear       = 0    

        
        # General Input Values 
        self.fileJar  = None
        self.projectName = None
        self.areaName = None
        self.inputShapeFile = None
        self.outputSaveFile = None
        self.DTMDirectory = None
        self.DSMDirectory = None
        self.calculateMethod = None
        self.country = None
        self.country_id = None
        
        self.spatialReferenceEPSG = None
        self.spatialReferenceWKT  = None


        self.old_building_use_user_definition_value = "NULL_VALUE"
        self.old_protection_user_definition_value = "NULL_VALUE"

        
        self.countries = {}
        self.refurbishment_level_periods = {}
        self.calculateMethodList = []
        self.buildingUse = []
        self.periods = []
        self.refurbishment_levels = []
        
        self.shpBuildingRecords = []
        self.originShapeFields = []
        self.protectionLevels = []
        self.shp_map_csv_fields = []

        #Mapped Values
        self.buildingUseMap = []
        self.protectionLevelMap = []
        self.shpDMMFieldsMap = []
        self.inputSHPFieldBuildingUseValues = []
        self.inputSHPFieldProtectionDegreeValues = []
        self.fieldsSHPMappingPosition=[]
        self.buildingUseFloorHeightDict={}
        self.userFieldShapeMap = []
        


        self.listSelectedValue = None
        self.listSelectedValues = list()
        self.roofSpinBoxSelectedValue = None
        self.wallSpinBoxSelectedValue = None
        self.windowSpinBoxSelectedValue = None
        
        
        self.refurbishmentTabDataList = []
        self.refurbishmentSimplifiedData = 0
        
        
        


