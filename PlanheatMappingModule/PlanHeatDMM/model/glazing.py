# -*- coding: utf-8 -*-
"""
   Model Map table glazing
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 24 Oct. 2017
"""
__docformat__ = "restructuredtext"


class Glazing():
    
    """ DB Entity glazing to Python object Glazing  """

    def __init__(self):
        
        self.__id               = 0
        self.__building_use_id  = 0
        self.__percentage       = 0.0
   
     
    def __str__(self):
        return "id:" + str(self.id) + " building_use_id:" + str(self.building_use_id) + " percentage:" + str(self.percentage)
    
    
    
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
    def percentage(self):
        return self.__percentage
    
    @percentage.setter
    def percentage(self, val):
        self.__percentage =  float(val.replace(",","."))  if isinstance(val,str) else float(val)              
        
    