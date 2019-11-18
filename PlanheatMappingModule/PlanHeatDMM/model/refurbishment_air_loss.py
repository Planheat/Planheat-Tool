# -*- coding: utf-8 -*-
"""
   Map Dynamic table for air loss depending by period and refurbishment level     
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 14 Dec. 2017
"""
__docformat__ = "restructuredtext"

class RefurbishmentAirLoss():
    """ Map Dynamic table to object for air loss depending by period and refurbishment level  """

    def __init__(self):
        self.id                       = 0
        self.__country_id             = 0
        self.__period_id              = 0
        self.__refurbishment_level_id = 0
        self.__refurbishment_level    = ""
        self.__air_lekeage            = 0.0
        
    
    
    def __str__(self):
        return "id:" + str(self.id) + " country_id:" + str(self.country_id) + " period_id:" + str(self.period_id) + \
               " refurbishment_level_id:" + str(self.refurbishment_level_id) + " refurbishment_level:" + str(self.refurbishment_level) + \
               " air_lekeage:" + str(self.air_lekeage)
    
    
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
       
    @property
    def country_id(self):
        return self.__country_id
    
    @country_id.setter
    def country_id(self, val):
        self.__country_id = val
        
        
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
        
        
    @property
    def air_lekeage(self):
        return self.__air_lekeage
    
    @air_lekeage.setter
    def air_lekeage(self, val):
        self.__air_lekeage = float(val.replace(",","."))  if isinstance(val,str) else float(val)             
            
                             
            

