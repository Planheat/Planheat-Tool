# -*- coding: utf-8 -*-
"""
   Model Map table alternative_built_surface   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 25 Oct. 2017
"""
__docformat__ = "restructuredtext"


class AlternativeBuiltSurface():
    """ DB Entity alternative_built_surface to Python object AlternativeBuiltSurface  """

    def __init__(self):
        
        self.__id               = 0
        self.__country_id       = 0
        self.__residential_perc = 0.0
        self.__service_perc     = 0.0
        
    
   
     
    def __str__(self):
        return "id:" + str(self.id) + " country_id:" + str(self.country_id) + " residential_perc:" + str(self.period_id) + " service_perc:" + str(self.residential)
    
    
    
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
    def residential_perc(self):
        return self.__residential_perc
    
    @residential_perc.setter
    def residential_perc(self, val):
        self.__residential_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
                             
    
    @property
    def service_perc(self):
        return self.__service_perc
    
    @service_perc.setter
    def service_perc(self, val):
        self.__service_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)          
