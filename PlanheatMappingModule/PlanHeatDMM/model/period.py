# -*- coding: utf-8 -*-
"""
   Model Map table period
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 23 Oct. 2017
"""
__docformat__ = "restructuredtext"


class Period():
    
    """ DB Entity period to Python object Period  """

    def __init__(self):
        
        self.__id            = 0
        self.__start_period  = 0
        self.__end_period    = 0
        self.__period_text   = ""
       
   
     
    def __str__(self):
        return "id:" + str(self.__id) + " start_period:" + str(self.__start_period) + " end_period:" + str(self.__end_period) + " period_text:" + str(self.__period_text)
    
    
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
       
    @property
    def start_period(self):
        return self.__start_period
    
    @start_period.setter
    def start_period(self, val):
        self.__start_period = val
        
        
    @property
    def end_period(self):
        return self.__end_period
    
    @end_period.setter
    def end_period(self, val):
        self.__end_period = val
        
        
    @property
    def period_text(self):
        return self.__period_text
    
    @period_text.setter
    def period_text(self, val):
        self.__period_text = val