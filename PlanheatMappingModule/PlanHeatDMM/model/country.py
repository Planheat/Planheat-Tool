# -*- coding: utf-8 -*-
"""
   Model Map table country
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 14 sept. 2017
"""
__docformat__ = "restructuredtext"



class Country():
    
    """ DB Entity country to Python object Country  """
            
    def __init__(self):
        self.__id    = 0
        self.__country   = ""
        self.__heating_base   = 0.0
        self.__cooling_base   = 0.0
    
             
    def __str__(self):
        return "id:" + str(self.__id) + " id country:" + str(self.__country) + " heating base:" + str(self.__heating_base)  + " cooling base:" + str(self.__cooling_base) 
    
       
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
 
    
    @property
    def country(self):
        return self.__country
    
    @country.setter
    def country(self, val):
        self.__country = val    
 
        
    @property
    def heating_base(self):
        return self.__heating_base
    
    @heating_base.setter
    def heating_base(self, val):
        self.__heating_base = float(val.replace(",",".") if isinstance(val,str) else float(val))        

   
    @property
    def cooling_base(self):
        return self.__cooling_base
    
    @cooling_base.setter
    def cooling_base(self, val):
        self.__cooling_base = float(val.replace(",",".") if isinstance(val,str) else float(val))             
         
        