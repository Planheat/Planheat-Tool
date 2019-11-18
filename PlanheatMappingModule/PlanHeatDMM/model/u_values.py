# -*- coding: utf-8 -*-
"""
   Model Map table u_values 
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 24 Oct. 2017
"""
__docformat__ = "restructuredtext"

class UValues():
    

    """ DB Entity u_values to Python object UValues  """

    def __init__(self):
        
        self.__id             = 0
        self.__country_id     = 0
        self.__period_id      = 0
        self.__residential    = False
        self.__roof_u_value   = 0.0
        self.__wall_u_value   = 0.0
        self.__window_u_value = 0.0
        
    
   
     
    def __str__(self):
        return "id:" + str(self.id) + " country_id:" + str(self.country_id) + " period_id:" + str(self.period_id) + " residential:" + str(self.residential) + \
               " roof_u_value:" + str(self.roof_u_value) + " wall_u_value:" + str(self.wall_u_value) + " window_u_value:" + str(self.window_u_value) 
    
    
    
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