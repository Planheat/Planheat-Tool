# -*- coding: utf-8 -*-
"""
   Model Map table efficiency_impact   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 12 Dec. 2017
"""
__docformat__ = "restructuredtext"

class EfficiencyImpact():
    """ DB Entity efficiency_impact to Python object EfficiencyImpact()  """

    def __init__(self):
        
        self.__id                       = 0
        self.__refurbishment_level_id   = 0
        self.__refurbishment_level      = ""
        self.__roof_economic            = 0.0
        self.__roof_environment         = 0.0
        self.__wall_economic            = 0.0
        self.__wall_environment         = 0.0
        self.__window_economic          = 0.0
        self.__window_environment       = 0.0
        
        
    
    
    def __str__(self):
        return "id:" + str(self.id) + " refurbishment_level_id:" + str(self.refurbishment_level_id) + " refurbishment_level:" + str(self.refurbishment_level) \
             + " roof_economic:" + str(self.roof_economic) + " roof_environment:" + str(self.roof_environment) + " wall_economic:" + str(self.wall_economic) \
             + " wall_environment:" + str(self.wall_environment) + " window_economic:" + str(self.window_economic) + " window_environment:" + str(self.window_environment)
    
    
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
       
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
    def roof_economic(self):
        return self.__roof_economic
    
    @roof_economic.setter
    def roof_economic(self, val):
        self.__roof_economic = float(val.replace(",","."))  if isinstance(val,str) else float(val)  
        
        
    @property
    def roof_environment(self):
        return self.__roof_environment
    
    @roof_environment.setter
    def roof_environment(self, val):
        self.__roof_environment = float(val.replace(",","."))  if isinstance(val,str) else float(val)                    
            
           
    @property
    def wall_economic(self):
        return self.__wall_economic
    
    @wall_economic.setter
    def wall_economic(self, val):
        self.__wall_economic = float(val.replace(",","."))  if isinstance(val,str) else float(val)                               
            
            
    @property
    def wall_environment(self):
        return self.__wall_environment
    
    @wall_environment.setter
    def wall_environment(self, val):
        self.__wall_environment = float(val.replace(",","."))  if isinstance(val,str) else float(val)      
        
                 
    @property
    def window_economic(self):
        return self.__window_economic
    
    @window_economic.setter
    def window_economic(self, val):
        self.__window_economic = float(val.replace(",","."))  if isinstance(val,str) else float(val)
        
    
    @property
    def window_environment(self):
        return self.__window_environment
    
    @window_environment.setter
    def window_environment(self, val):
        self.__window_environment = float(val.replace(",","."))  if isinstance(val,str) else float(val)
