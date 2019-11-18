# -*- coding: utf-8 -*-
"""
   API Log for process   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 12 sep. 2017
"""
__docformat__ = "restructuredtext"  


import os
from time import strftime
from manageLog.logger import Logger
from config import config as Config


class Log(object):
    """
        Create-Write Log File 
    """

    def __init__(self,logDateName=None, path=None,fileName=None):
        """
        Log Constructor
        :param path str:None , only filled for test purpose
        :param fileName str: None , only filled for test purpose
        
        """       
        
        if path is None or fileName is None: 
            if logDateName is None:
                strftime('%Y%m%d%H%M%S')
            self.path= Config.PLUGIN_DIR + os.path.sep +  Config.LOG_PARAMS['path'] + os.path.sep 
            self.fileName = Config.LOG_PARAMS["logName"]
            self.fileName = self.fileName +  "_" +  logDateName
            self.fileName = self.fileName +  "." +  Config.LOG_PARAMS["logExt"]
        else:
            self.path = path
            self.fileName = fileName
            
        self.completeFileName = self.path + self.fileName       

        
        self.logger = Logger(self.path,self.fileName,Config.LOG_PARAMS["loggingLevel"])
        self.write_log("INFO", "Log File Created SUCCESS")
        
        
    
    def write_log(self, level, message):
        """
        Send message and level to logger  
        :param level str: level of message
        :param message str: Message for log file
        """     
        self.logger.write_log(level, message)
        self.logger.filehandler.flush()
                
        
        
    def close_log(self):
        """
         Close log file and logger handlers 
        """    
        self.logger.filehandler.close()
        self.logger.logger.removeHandler(self.logger.filehandler)
                
    
        
    
