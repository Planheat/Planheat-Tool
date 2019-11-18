# -*- coding: utf-8 -*-
"""
   Model Map table alternative_scheduled   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 18 sept. 2017
"""
__docformat__ = "restructuredtext"


class AlternativeScheduled():
    """ DB Entity alternative_scheduled to Python object AlternativeScheduled  """
    
    

    def __init__(self):
        '''
        Constructor
        '''
        self.__id                 = 0
        self.__dayOfYear          = 0
        self.__hourOfDay          = 0
        self.__season             = ""
        self.__heating            = 0.0
        self.__cooling            = 0.0
        self.__DHW                = 0.0
        
        
        self.__heating_nuf    = 0.0
        self.__cooling_nuf    = 0.0
        self.__DHW_nuf        = 0.0
        
             
   
    def __str__(self):      
        
        text = "id:" + str(self.__id) + " dayOfYear:" +  str(self.__dayOfYear) + " hourOfDay:" + str(self.__hourOfDay) \
                + " season:" + self.season  +  " heating:" + str(self.heating) + " cooling:" + str(self.cooling) \
                + " DHW:" + str(self.DHW) + " heating_nuf:" + str(self.heating_nuf) + " cooling_nuf:" + str(self.cooling_nuf) + " cooling_nuf:" + str(self.DHW_nuf) 
    
        return text 
   
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
    
    
    @property
    def dayOfYear(self):
        return self.__dayOfYear
    
    @dayOfYear.setter
    def dayOfYear(self, val):
        self.__dayOfYear = val       
        
    @property
    def season(self):
        return self.__season
    
    @season.setter
    def season(self, val):
        self.__season = val   
        
        
    @property
    def hourOfDay(self):
        return self.__hourOfDay
    
    @hourOfDay.setter
    def hourOfDay(self, val):
        self.__hourOfDay = val      
        
   
    @property
    def heating(self):
        return self.__heating
    
    @heating.setter
    def heating(self, val):
        self.__heating =  float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
               
        
    @property
    def cooling(self):
        return self.__cooling
    
    @cooling.setter
    def cooling(self, val):
        self.__cooling =  float(val.replace(",","."))  if isinstance(val,str) else float(val)                      
           
     
    @property
    def DHW(self):
        return self.__DHW
    
    @DHW.setter
    def DHW(self, val):
        self.__DHW =  float(val.replace(",","."))  if isinstance(val,str) else float(val)               
    
        
    @property
    def heating_nuf(self):
        return self.__heating_nuf
    
    @heating_nuf.setter
    def heating_nuf(self, val):
        self.__heating_nuf =  val                  
    
    
    @property
    def cooling_nuf(self):
        return self.__cooling_nuf
    
    @cooling_nuf.setter
    def cooling_nuf(self, val):
        self.__cooling_nuf =  val                  
    
      
    @property
    def DHW_nuf(self):
        return self.__DHW_nuf
    
    @DHW_nuf.setter
    def DHW_nuf(self, val):
        self.__DHW_nuf =  val                  
            
      
        

        