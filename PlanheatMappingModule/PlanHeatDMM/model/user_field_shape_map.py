# -*- coding: utf-8 -*-
"""
   Model Map user field shape 
   :author: Sergio Aparicio Vegas 
   :version: 1.0  
   :date: 22 Feb. 2018
"""
__docformat__ = "restructuredtext"


class UserFieldShapeMap():
    """ DB Entity air_lekeage_building_distribution to Python object AirLekeageBuildingDistribution  """

    def __init__(self):
        
        self.__key         = None
        self.__dataFormat  = None  
        self.__length      = None  
        self.__precision   = None
        self.__position    = 0  
    
    
    def __str__(self):
        return "key:" + str(self.__key) + " dataFormat:" + str(self.__dataFormat) + " length:" + str(self.__length)\
             + "precision:" + str(self.__precision) + " position:" + str(self.__position)
    
    
    
    @property
    def key(self):
        return self.__key
    
    @key.setter
    def key(self, val):
        self.__key = val
   
       
    @property
    def dataFormat(self):
        return self.__dataFormat
    
    @dataFormat.setter
    def dataFormat(self, val):
        self.__dataFormat = val
        
        
    @property
    def length(self):
        return self.__length
    
    @length.setter
    def length(self, val):
        self.__length = val
      
      
    @property
    def precision(self):
        return self.__precision
    
    @precision.setter
    def precision(self, val):
        self.__precision = val
        
    
    @property
    def position(self):
        return self.__position
    
    @position.setter
    def position(self, val):
        self.__position = val
            