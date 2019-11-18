# -*- coding: utf-8 -*-
"""
   Model Map refurbishment_periods_levels table   
   :author: Sergio Aparicio Vegas 
   :version: 0.2  
   :date: 29 Nov 2017
"""
__docformat__ = "restructuredtext"

class RefurbishmentLevelPeriod():
    
    """ Refurbishment level options for each period """

    def __init__(self):
        self.__id = 0
        self.__period_id                = 0
        self.__refurbishment_level_id   = 0 
        self.__refurbishment_level      = ""
     
    def __str__(self):
        return "id:" + str(self.__id) + " period_id " + str(self.__period_id) + " refurbishment_level_id " + str(self.__refurbishment_level_id) +" refurbishment_level:" + self.refurbishment_level    
     
                 
   
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
    
    
    @property
    def period_id(self):
        return self.__period_id
    
    @period_id.setter
    def period_id(self, val):
        self.__period_id = val   
        
        
    @property
    def refurbishment_level_id(self):
        return self.__refurbishment_level_id
    
    @refurbishment_level_id.setter
    def refurbishment_level_id(self, val):
        self.__refurbishment_level_id = val    
             
             
    @property
    def refurbishment_level(self):
        return self.__refurbishment_level
    
    @refurbishment_level.setter
    def refurbishment_level(self, val):
        self.__refurbishment_level = val         
             
        
        