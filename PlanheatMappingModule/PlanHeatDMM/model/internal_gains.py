# -*- coding: utf-8 -*-
"""
   Model Map table internal_gains
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 30 Oct. 2017
"""
__docformat__ = "restructuredtext"


class InternalGain():
    
    """ DB Entity internal_gains to Python object InternalGain  """


    def __init__(self):
        '''
        Constructor
        '''
        self.__id                       = 0
        self.__building_use_id          = 0
        self.__equipment_internal_gains = 0.0
        self.__occupancy_internal_gains = 0.0
        self.__lighting_power = 0.0
                  
   
   
    def __str__(self):
        return "id:" + str(self.__id) + " building_use_id:" + str(self.__building_use_id) + " equipment_internal_gains base:" + str(self.__equipment_internal_gains) \
            + " occupancy_internal_gains:" + str(self.__occupancy_internal_gains) + "  lighting_power:" + str(self.__lighting_power)
    
    
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
    def equipment_internal_gains(self):
        return self.__equipment_internal_gains
    
    @equipment_internal_gains.setter
    def equipment_internal_gains(self, val):
        self.__equipment_internal_gains = float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
        
        
    @property
    def occupancy_internal_gains(self):
        return self.__occupancy_internal_gains
    
    @occupancy_internal_gains.setter
    def occupancy_internal_gains(self, val):
        self.__occupancy_internal_gains = float(val.replace(",","."))  if isinstance(val,str) else float(val)                       
        
        
    @property
    def lighting_power(self):
        return self.__lighting_power
    
    @lighting_power.setter
    def lighting_power(self, val):
        self.__lighting_power = float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
