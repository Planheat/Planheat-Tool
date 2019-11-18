# -*- coding: utf-8 -*-
"""
   Model Map table protection level
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 09 Oct. 2017
"""
__docformat__ = "restructuredtext"


class ProtectionLevel():
    
    """ DB Entity protection_level to Python object ProtectionLevel  """

    def __init__(self):
        self.__id    = 0
        self.__protectionLevel   = None
        self.__description       = None
        self.__roof              = False
        self.__wall              = False
        self.__window            = False
   
    def __str__(self):
        return "id:" + str(self.id) + " - protectionLevel:" + str(self.protectionLevel) + " - description:" + self.description \
             + " roof:" + str(self.roof) + " wall:" + str(self.wall) + " window:" + str(self.window) 
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
   
    @property
    def protectionLevel(self):
        return self.__protectionLevel
    
    @protectionLevel.setter
    def protectionLevel(self, val):
        self.__protectionLevel = val
        
            
    @property
    def description(self):
        return self.__description
    
    @description.setter
    def description(self, val):
        self.__description = val
        
        
    @property
    def roof(self):
        return self.__roof
    
    @roof.setter
    def roof(self, val):
        self.__roof = bool(val)        
    
    
    @property
    def wall(self):
        return self.__wall
    
    @wall.setter
    def wall(self, val):
        self.__wall = bool(val)
    
        
    @property
    def window(self):
        return self.__window
    
    @window.setter
    def window(self, val):
        self.__window = bool(val)            
        