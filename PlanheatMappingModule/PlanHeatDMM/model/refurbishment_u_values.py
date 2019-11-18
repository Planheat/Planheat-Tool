# -*- coding: utf-8 -*-
"""
   Model Map table refurbishment_u_values 
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 13 Dec. 2017
"""
__docformat__ = "restructuredtext"

class RefurbishmentUValues():
    

    """ DB Entity refurbishment_u_values to Python object RefurbishmentUValues  """

    def __init__(self):
        
        self.__id                       = 0
        self.__country_id               = 0
        self.__refurbishment_level_id   = 0
        self.__refurbishment_level      = ""
        self.__residential              = False
        self.__roof_u_value             = 0.0
        self.__wall_u_value             = 0.0
        self.__window_u_value           = 0.0
        
    
   
     
    def __str__(self):
        return "id:" + str(self.id) + " country_id:" + str(self.country_id) + " refurbishment_level_id:" + str(self.refurbishment_level_id) \
             + " refurbishment_level:" + str(self.refurbishment_level) + " residential:" + str(self.residential) + " roof_u_value:" + str(self.roof_u_value) \
             + " wall_u_value:" + str(self.wall_u_value) + " window_u_value:" + str(self.window_u_value) 
    
    
    
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
    def residential(self):
        return self.__residential
    
    @residential.setter
    def residential(self, val):
        self.__residential = bool(val)       
    
    
    @property
    def roof_u_value(self):
        return self.__roof_u_value
    
    @roof_u_value.setter
    def roof_u_value(self, val):
        self.__roof_u_value = float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
                             
    
    @property
    def wall_u_value(self):
        return self.__wall_u_value
    
    @wall_u_value.setter
    def wall_u_value(self, val):
        self.__wall_u_value = float(val.replace(",","."))  if isinstance(val,str) else float(val)          
        
               
    @property
    def window_u_value(self):
        return self.__window_u_value
    
    @window_u_value.setter
    def window_u_value(self, val):
        self.__window_u_value = float(val.replace(",","."))  if isinstance(val,str) else float(val)               