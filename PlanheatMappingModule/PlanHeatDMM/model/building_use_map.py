# -*- coding: utf-8 -*-
"""
   Model Map Algorithm - User  building_use   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 10 Oct. 2017
"""
__docformat__ = "restructuredtext"

class BuildingUseMap():
    
    """ Use mapped  among the user and the process value """

    def __init__(self):
        self.__building_use_id = 0
        self.__DMM_use   = ""
        self.__user_definition_use   = "" 
        self.__non_office = True
        self.__floor_height = 0.0
        
     
    def __str__(self):
        return "building_use_id:" + str(self.building_use_id) + " DMM_use " + self.DMM_use + " user_definition_use " + self.user_definition_use \
                +" non_office:" + str(self.non_office) + " floor_height:" + str(self.floor_height)     
     
                 
   
    @property
    def building_use_id(self):
        return self.__building_use_id
    
    @building_use_id.setter
    def building_use_id(self, val):
        self.__building_use_id = val
   
       
    @property
    def DMM_use(self):
        return self.__DMM_use
    
    @DMM_use.setter
    def DMM_use(self, val):
        self.__DMM_use = val
        
        
    @property
    def user_definition_use(self):
        return self.__user_definition_use
    
    
    @user_definition_use.setter
    def user_definition_use(self, val):
        self.__user_definition_use = val
        
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