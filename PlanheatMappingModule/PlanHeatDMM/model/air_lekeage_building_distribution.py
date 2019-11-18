# -*- coding: utf-8 -*-
"""
   Model Map table air_lekeage_building_distribution   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 15 Dec. 2017
"""
__docformat__ = "restructuredtext"

class AirLekeageBuildingDistribution():
    """ DB Entity air_lekeage_building_distribution to Python object AirLekeageBuildingDistribution  """

    def __init__(self):
        
        self.__id                  = 0
        self.__walls_perc          = 0.0
        self.__ceiling_perc        = 0.0
        self.__windows_doors_perc  = 0.0
        
    
    
    def __str__(self):
        return "id:" + str(self.id) + " walls_perc:" + str(self.walls_perc) + " period_id:" + str(self.period_id) + " air_lekeage:" + str(self.air_lekeage)
    
    
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
       
    @property
    def walls_perc(self):
        return self.__walls_perc
    
    @walls_perc.setter
    def walls_perc(self, val):
        self.__walls_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)             
        
        
    @property
    def ceiling_perc(self):
        return self.__ceiling_perc
    
    @ceiling_perc.setter
    def ceiling_perc(self, val):
        self.__ceiling_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)             
        
      
    @property
    def windows_doors_perc(self):
        return self.__windows_doors_perc
    
    @windows_doors_perc.setter
    def windows_doors_perc(self, val):
        self.__windows_doors_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)