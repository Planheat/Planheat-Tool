# -*- coding: utf-8 -*-
"""
   Model Map table alternative_consumption_distribution   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 25 Oct. 2017
"""
__docformat__ = "restructuredtext"


class AlternativeConsumptionDistribution():
    """ DB Entity alternative_consumption_distribution to Python object AlternativeConsumptionDistribution  """


    def __init__(self):
        
        self.__id                   = 0
        self.__country_id           = 0
        self.__residential          = False
        self.__space_heating_perc   = 0.0
        self.__water_heating_perc   = 0.0
        self.__other_perc           = 0.0
   
    
     
    def __str__(self):
        return "id:" + str(self.id) + " country_id:" + str(self.country_id) + " residential:" + str(self.residential) + " space_heating_perc:" + \
               str(self.space_heating_perc)  + " water_heating_perc:" + str(self.water_heating_perc)  + " other_perc :" + str(self.other_perc )     
    
    
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
    def residential(self):
        return self.__residential
    
    @residential.setter
    def residential(self, val):
        self.__residential = bool(val)          
        
   
    @property
    def space_heating_perc(self):
        return self.__space_heating_perc
    
    @space_heating_perc.setter
    def space_heating_perc(self, val):
        self.__space_heating_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
                             
    
    @property
    def water_heating_perc(self):
        return self.__water_heating_perc
    
    @water_heating_perc.setter
    def water_heating_perc(self, val):
        self.__water_heating_perc = float(val.replace(",","."))  if isinstance(val,str) else float(val)          
