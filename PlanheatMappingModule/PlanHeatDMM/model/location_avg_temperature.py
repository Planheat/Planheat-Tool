# -*- coding: utf-8 -*-
"""
   Model Map location_avg_temperature    
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 24 Nov. 2017
"""
__docformat__ = "restructuredtext"

class LocationAvgTemperature():
    
    """ Use mapped location temperature if don't use NOA"""

    def __init__(self):
       
        self.__id            = 0            
        self.__location_id   = 0
        self.__dayofyear     = 0           
        self.__hourofday     = 0            
        self.__season        = ""            
        self.__temperature   = 0.0            

        
     
    def __str__(self):
        return "id:" + str(self.__id) + " location id: " + str(self.__location_id) + " dayofyear: " + str(self.__dayofyear) \
            +  " hourofday:" + str(self.__hourofday) +  " season:" + self.__season + " temperature:" + str(self.__temperature)     
     
                 
   
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
    
    
    @property
    def location_id(self):
        return self.__location_id
    
    @location_id.setter
    def location_id(self, val):
        self.__location_id = val    
        
    
    @property
    def dayofyear(self):
        return self.__dayofyear
    
    @dayofyear.setter
    def dayofyear(self, val):
        self.__dayofyear = val
        
        
    @property
    def hourofday(self):
        return self.__hourofday
    
    @hourofday.setter
    def hourofday(self, val):
        self.__hourofday = val    
            
    
    @property
    def season(self):
        return self.__season
    
    @season.setter
    def season(self, val):
        self.__season = val    
        
    
    @property
    def temperature(self):
        return self.__temperature
    
    @temperature.setter
    def temperature(self, val):
        self.__temperature = float(val.replace(",","."))  if isinstance(val,str) else float(val)    
        
            
        