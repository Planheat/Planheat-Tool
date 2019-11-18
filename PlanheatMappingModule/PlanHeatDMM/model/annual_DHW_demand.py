# -*- coding: utf-8 -*-
"""
   Model Map table annual_DHW_demand   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 26 Oct. 2017
"""
__docformat__ = "restructuredtext"

class AnnualDHWDemand():
    """ DB Entity annual_DHW_demand to Python object AnnualDHWDemand  """

    def __init__(self):
        
        self.__id                = 0
        self.__building_use_id   = 0
        self.__DHW_demand_kwhm2  = 0.0
        
   
    
    def __str__(self):
        return "id:" + str(self.id) + " building_use_id:" + str(self.building_use_id) + " DHW_demand_kwhm2:" + str(self.DHW_demand_kwhm2) + " air_lekeage:" + str(self.air_lekeage)
    
    
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
        
        
    @property
    def building_use_id(self):
        return self.__building_use_id
    
    @building_use_id.setter
    def building_use_id(self, val):
        self.__building_use_id = val    
     
        
    @property
    def DHW_demand_kwhm2(self):
        return self.__DHW_demand_kwhm2
    
    @DHW_demand_kwhm2.setter
    def DHW_demand_kwhm2(self, val):
        self.__DHW_demand_kwhm2 = float(val.replace(",","."))  if isinstance(val,(str)) else float(val)      
