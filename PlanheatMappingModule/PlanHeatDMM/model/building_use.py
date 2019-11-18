# -*- coding: utf-8 -*-
"""
   Model Map table building_use   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 14 Sep. 2017
"""
__docformat__ = "restructuredtext"

class BuildingUse():
    
    """ DB Entity building_use to Python object BuildingUse  """

    def __init__(self):
        self.__id    = 0
        self.__use   = ""
        self.__non_office   = True
        self.__floor_height = 0.0
        self.__description  = ""
        self.__associated_icon_file = ""
             
   
    def __str__(self):
        return "id:" + str(self.id) + " use:" + str(self.use) + " non_office:" + str(self.non_office) + " floor_height:" + str(self.floor_height) + " description:" + str(self.description)     
        
   
    @property
    def id(self):
        return self.__id
    
    
    @id.setter
    def id(self, val):
        self.__id = val
   
       
    @property
    def use(self):
        return self.__use
    
    
    @use.setter
    def use(self, val):
        self.__use = val
        
        
       
    @property
    def non_office(self):
        return self.__non_office
    
    
    @non_office.setter
    def non_office(self, val):
        self.__non_office = bool(val)    
        
    
    @property
    def floor_height(self):
        return self.__floor_height
    
    
    @floor_height.setter
    def floor_height(self, val):
        self.__floor_height = float(val.replace(",","."))  if isinstance(val,str) else float(val)
    
    
    @property
    def description(self):
        return self.__description
    
    
    @description.setter
    def description(self, val):
        self.__description = val
    
    @property
    def associated_icon_file(self):
        return self.__associated_icon_file
    
    
    @associated_icon_file.setter
    def associated_icon_file(self, val):
        self.__associated_icon_file = val    