# -*- coding: utf-8 -*-
"""
   Model Map Algorithm - User  protection level
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 10 Oct. 2017
"""
__docformat__ = "restructuredtext"


class ProtectionLevelMap():
    
    """ Protection Degree mapped among the user and the process value """

    def __init__(self):
        
        self.__DMM_protection_level   = 0
        self.__description = ""
        self.__user_definition_protection   = "" 
        
     
    def __str__(self):
        return "DMM_protection_level " + str(self.DMM_protection_level) + " description " + self.description + " user_definition_protection" +self.user_definition_protection  
        
    @property
    def DMM_protection_level(self):
        return self.__DMM_protection_level
    
    @DMM_protection_level.setter
    def DMM_protection_level(self, val):
        self.__DMM_protection_level = val
        
        
    @property
    def user_definition_protection(self):
        return self.__user_definition_protection
    
    @user_definition_protection.setter
    def user_definition_protection(self, val):
        self.__user_definition_protection = val        
       
  
    @property
    def description(self):
        return self.__description
    
    @description.setter
    def description(self, val):
        self.__description = val        
