# -*- coding: utf-8 -*-
"""
   Model Map table air_lekeage_distribution   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 23 Oct. 2017
"""
__docformat__ = "restructuredtext"

class AirLekeageDistribution():
    """ DB Entity air_lekeage_distribution to Python object AirLekeageDistribution  """

    def __init__(self):
        
        self.__id           = 0
        self.__country_id   = 0
        self.__period_id    = 0
        self.__air_lekeage  = 0.0
        
    
    
    def __str__(self):
        return "id:" + str(self.id) + " country_id:" + str(self.country_id) + " period_id:" + str(self.period_id) + " air_lekeage:" + str(self.air_lekeage)
    
    
    
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
    def air_lekeage(self):
        return self.__air_lekeage
    
    @air_lekeage.setter
    def air_lekeage(self, val):
        self.__air_lekeage = float(val.replace(",","."))  if isinstance(val,str) else float(val)             
            
                             
            

