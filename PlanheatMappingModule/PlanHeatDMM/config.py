# -*- coding: utf-8 -*-
"""
   Load Configuration File
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 27 Sep. 2017
"""

__docformat__ = "restructuredtext"


import os,re
import json
import utility.constants as Constants
from configparser import SafeConfigParser
import planheat.config as master_config


section_names = 'LOG', 'DATABASE','NOA','SHAPE','CSV', 'GENERAL'


class ConfigurationPlugin():
    """ Load configuration File options to the application """
    

    def __init__(self,plugin_dir, file_name):
        """ 
            Constructor
            Load Constants before read cfg file options
            
            :param plugin_dir str: Plugin path
            :param file_name str: Configuration file name
        """
        try:
            self.file_name  = file_name
            
            #Constants Default Values
            self.PLUGIN_DIR =  plugin_dir
            self.RAW_FILES_TTL = Constants.RAW_FILES_TTL
            self.LOG_LEVELS = Constants.LOG_LEVELS
            self.DB_PARAMS = Constants.DB_PARAMS
            self.LOG_PARAMS = Constants.LOG_PARAMS
            self.JAR_FILE_PARAMS = Constants.JAR_FILE_PARAMS
            self.INTERMEDIATE_FILE_CSV = Constants.INTERMEDIATE_FILE_CSV 
            self.USE_NOA_DATA = Constants.USE_NOA_DATA
            self.NOA_URL = Constants.NOA_URL
            self.HTTP_RESPONSE_OK = Constants.HTTP_RESPONSE_OK
            self.RAW_FILES_TTL = Constants.RAW_FILES_TTL
            self.NOA_TIMEOUT = Constants.NOA_TIMEOUT
            self.SHAPE_TYPE_FILE = Constants.SHAPE_TYPE_FILE
            self.DAYS_REMOVE_OLD_LOGS = Constants.DAYS_REMOVE_OLD_LOGS
            self.DECIMAL_POINT_IS_COMMA = Constants.DECIMAL_POINT_IS_COMMA
            self.LIDAR_FILE_EXT = Constants.LIDAR_FILE_EXT
            self.PROCESS_THREAD_PRIORITY = Constants.PROCESS_THREAD_PRIORITY
            self.PROCESS_WAIT_TO_KILL = Constants.PROCESS_WAIT_TO_KILL
            self.COUNTRY_DEFAULT = None
            self.EPSG_URL = Constants.EPSG_URL
            self.JAVA_MAIN_CLASS = Constants.JAVA_MAIN_CLASS
            self.HOURS_PER_YEAR = Constants.HOURS_PER_YEAR
            self.USE_PERSIST_SCENARIO = Constants.USE_PERSIST_SCENARIO
            self.LAUNCH_JAVA_PROCESS = Constants.LAUNCH_JAVA_PROCESS
            self.OPTIONS_FILE = Constants.OPTIONS_FILE
            self.LOG_DIR_PATH = Constants.LOG_DIR_PATH
            self.TEMP_DIR_PATH = Constants.TEMP_DIR_PATH
            
            self.__load_cfg_file()
        
        except:
            raise      
            
        
        
    def reload_cfg_file(self):
        try:
            self.__load_cfg_file()
        except:
            raise     
    
    
    def __load_cfg_file(self):         
        try:
            # Constants from cfg file 
            parser = SafeConfigParser()
            parser.optionxform = str  # make option names case sensitive
            found = parser.read(self.file_name)
            if not found:
                raise ValueError('No config file {} found'.format(self.file_name))
            
            for name in section_names:
                self.__dict__.update(parser.items(name))  # <-- here the magic happens
            
            
            #Change str to a List or Dictionary when correspond    
            for k, v in dict.items(self.__dict__):
                #Integer Number
                if str(v).isdigit() and not re.search("^'*'$",str(v)):
                    self.__dict__[k]=int(str(v).replace("'", ""))
                #float Number    
                elif re.search("^[0-9.]*$",str(v)) and not re.search("^'[0-9.]*'$",str(v)):
                    self.__dict__[k]=float(str(v))
                #list object        
                elif str(v).startswith("[") and str(v).endswith("]"):
                    self.__dict__[k] = list(v[1:len(v)-1].split(","))
                #dictionary object    
                elif str(v).startswith("{") and str(v).endswith("}"):
                    self.__dict__[k] = json.loads(str(v))

        except ValueError as e:
            raise ValueError(e)
        except:
            raise Exception("cfg file,  incorrect format")    
  
  

#Load the cfg file
config = ConfigurationPlugin(os.path.dirname(__file__), os.path.dirname(__file__) + Constants.CONFIG_FILE_PATH + Constants.CONFIG_FILE_NAME)

#WORKING_PATH = os.path.join(os.environ["LOCALAPPDATA"], "QGIS/QGIS3", master_config.WORKING_DIRECTORY_NAME)
#TEMP_WORKING_PATH = os.path.join(WORKING_PATH, master_config.TEMP_WORKING_DIRECTORY_NAME)
#config.TEMP_DIR_PATH = TEMP_WORKING_PATH