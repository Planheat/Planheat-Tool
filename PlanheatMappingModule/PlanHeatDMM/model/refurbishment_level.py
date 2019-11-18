# -*- coding: utf-8 -*-
"""
   Model Map refurbishment_level table   
   :author: Sergio Aparicio Vegas 
   :version: 0.2  
   :date: 29 Nov 2017
"""
__docformat__ = "restructuredtext"

class RefurbishmentLevel():
    
    """ Refurbishment level options """

    def __init__(self):
        self.__id = 0
        self.__level      = ""
     
    def __str__(self):
        return "id:" + str(self.__id) + " level:" + self.__level    
     
                 
   
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
    
    @property
    def level(self):
        return self.__level
    
    @level.setter
    def level(self, val):
        self.__level = val         
             
        
        