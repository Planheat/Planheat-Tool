# -*- coding: utf-8 -*-
"""
   Model Map table alternative_other_distribution   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 25 Oct. 2017
"""
__docformat__ = "restructuredtext"

class AlternativeOtherDistribution():
    """ DB Entity alternative_other_distribution to Python object AlternativeOtherDistribution  """
    '''
    classdocs
    '''

    def __init__(self):
        
        self.__id                 = 0
        self.__residential        = False
        self.__base_electric_perc = 0.0
        self.__space_cooling_perc = 0.0
        
    
   
     
    def __str__(self):
        return "id:" + str(self.id) + " residential:" + str(self.residential) + \
               " base_electric_perc:" + str(self.base_electric_perc) + " space_cooling_perc:" + str(self.space_cooling_perc) 
    
    
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
        
    @property
    def residential(self):
        return self.__residential
    
    @residential.setter
    def residential(self, val):
        self.__residential = bool(val)       
    
    
    @property
    def base_electric_perc(self):
        return self.__base_electric_perc
    
    @base_electric_perc.setter
    def base_electric_perc(self, val):
        self.__base_electric_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
                             
    
    @property
    def space_cooling_perc(self):
        return self.__space_cooling_perc
    
    @space_cooling_perc.setter
    def space_cooling_perc(self, val):
        self.__space_cooling_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)          
        
               
        