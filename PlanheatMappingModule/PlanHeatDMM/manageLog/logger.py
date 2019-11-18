# -*- coding: utf-8 -*-
"""
   Logger API   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 11 sep. 2017
"""
__docformat__ = "restructuredtext"  


import logging
import os
#from logging.config import dictConfig

class Logger():
    """ Python Logger API
        
        Control level, formatting and output handlers for logger
    """
  
    def __init__(self, path, filename,logging_level):
        """
        logger Constructor
        :param path str:path of log  file 
        :param fileName str: name of log file
        :param fileName str: Control level 
        """
        
        self.path = path
        self.fileName = path + filename
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        self.logger = logging.getLogger('PLANHEAT') #Create a log with the same name as the script that created it
        self.logger.setLevel('DEBUG')

        #Create handlers and set their logging level
        self.filehandler = logging.FileHandler(self.fileName)
        self.filehandler.setLevel(logging_level) 
        
                #Create custom formats of the logrecord fit for both the logfile and the console
        streamformatter = logging.Formatter(fmt='%(asctime)s %(name)-12s %(levelname)-8s  %(message)s') #We only want to see certain parts of the message

        #Apply formatters to handlers
        self.filehandler.setFormatter(streamformatter)

        #Add handlers to logger
        self.logger.addHandler(self.filehandler)
        
        """  
        logging_config = dict(
            version = 1,
            formatters = {
                'f': {'format':
                      '%(asctime)s %(name)-12s %(levelname)-8s  %(message)s'}
                },
            handlers = {
                'console': {'class': 'logging.StreamHandler',
                      'formatter': 'f',
                      'level': logging.DEBUG},
                'file': {'class': 'logging.FileHandler',
                      'formatter': 'f',
                      'level': logging_level , #logging.DEBUG,
                      'filename': path + filename}
                },
            root = {
                #'handlers': ['console', 'file'],
                'handlers': ['file'],
                'level': logging_level,
                }
            
        )
            
        dictConfig(logging_config)
        self.logger = logging.getLogger('PLANHEAT')
        """
        
    
    def write_log(self, level, message):
        """
         Write Message in Log file 
        :param level str: level of message
        :param message str: Message for log file
        """     
        
        level = level.lower()
        #print(level, message,str(self.logger))
        if level == 'debug':
            self.logger.debug('%s', message)
        elif level == 'error':
            self.logger.error('%s', message)
        elif level == 'critical':
            self.logger.critical('%s', message)
        elif level == 'warning':
            self.logger.warning('%s', message)
        else:
            self.logger.info('%s', message)   
            
        
             

        
        
                  
            