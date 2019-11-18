# -*- coding: utf-8 -*-
"""
   Model Map table solar_gains 
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 23 Oct. 2017
"""
__docformat__ = "restructuredtext"

class SolarGain():
    
    """ DB Entity solar_gains to Python object SolarGain  """


    __slots__ =  ('_SolarGain__id', '_SolarGain__country_id','_SolarGain__dayOfYear','_SolarGain__hourOfDay','_SolarGain__wwr_north_non_offices','_SolarGain__wwr_south_non_offices','_SolarGain__wwr_west_non_offices','_SolarGain__wwr_east_non_offices','_SolarGain__wwr_north_offices','_SolarGain__wwr_south_offices','_SolarGain__wwr_east_offices','_SolarGain__wwr_west_offices')
    
    def __init__(self):
        
        self.__id           = 0
        self.__country_id   = 0
        self.__dayOfYear    = 0
        self.__hourOfDay    = 0
        self.__wwr_north_non_offices     = 0.0
        self.__wwr_south_non_offices     = 0.0
        self.__wwr_east_non_offices      = 0.0
        self.__wwr_west_non_offices      = 0.0
        self.__wwr_north_offices = 0.0
        self.__wwr_south_offices = 0.0
        self.__wwr_east_offices  = 0.0
        self.__wwr_west_offices  = 0.0
        
    
    def __str__(self):
        return "id:" + str(self.id) + " country_id:" + str(self.country_id) + " dayOfYear:" + str(self.dayOfYear) + " hourOfDay:" + str(self.hourOfDay) + \
               " wwr_north_non_offices:" + str(self.__wwr_north_non_offices) + " wwr_south_non_offices:" + str(self.__wwr_south_non_offices) + \
               " wwr_east_non_offices:" + str(self.__wwr_east_non_offices) + " wwr_west_non_offices:" + str(self.__wwr_west_non_offices) + \
               " wwr_north_offices:" + str(self.__wwr_north_offices) + " wwr_south_offices:" + str(self.__wwr_south_offices) + \
               " wwr_east_offices:" + str(self.__wwr_east_offices) + " wwr_west_offices:" + str(self.__wwr_west_offices)  
    
    
    
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
    def dayOfYear(self):
        return self.__dayOfYear
    
    @dayOfYear.setter
    def dayOfYear(self, val):
        self.__dayOfYear = val
        
        
    @property
    def hourOfDay(self):
        return self.__hourOfDay
    
    @hourOfDay.setter
    def hourOfDay(self, val):
        self.__hourOfDay = val       
            
    
    @property
    def wwr_north_non_offices(self):
        return self.__wwr_north_non_offices
    
    @wwr_north_non_offices.setter
    def wwr_north_non_offices(self, val):
        self.__wwr_north_non_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val)                                   
            
            
    @property
    def wwr_south_non_offices(self):
        return self.__wwr_south_non_offices
    
    @wwr_south_non_offices.setter
    def wwr_south_non_offices(self, val):
        self.__wwr_south_non_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val)                   
        
        
    @property
    def wwr_east_non_offices(self):
        return self.__wwr_east_non_offices
    
    @wwr_east_non_offices.setter
    def wwr_east_non_offices(self, val):
        self.__wwr_east_non_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val) 
        
        
    @property
    def wwr_west_non_offices(self):
        return self.__wwr_west_non_offices
    
    @wwr_west_non_offices.setter
    def wwr_west_non_offices(self, val):
        self.__wwr_west_non_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val)     
        
    
    @property
    def wwr_north_offices(self):
        return self.__wwr_north_offices
    
    @wwr_north_offices.setter
    def wwr_north_offices(self, val):
        self.__wwr_north_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val)                                   
            
            
    @property
    def wwr_south_offices(self):
        return self.__wwr_south_offices
    
    @wwr_south_offices.setter
    def wwr_south_offices(self, val):
        self.__wwr_south_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val)                   
        
        
    @property
    def wwr_east_offices(self):
        return self.__wwr_east_offices
    
    @wwr_east_offices.setter
    def wwr_east_offices(self, val):
        self.__wwr_east_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val) 
        
        
    @property
    def wwr_west_offices(self):
        return self.__wwr_west_offices
    
    @wwr_west_offices.setter
    def wwr_west_offices(self, val):
        self.__wwr_west_offices = float(val.replace(",","."))  if isinstance(val,str) else float(val)


if __name__ == "__main__":
    solar = SolarGain()
    print ("solar",solar)        