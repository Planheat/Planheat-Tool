# -*- coding: utf-8 -*-
"""
   Model Map table complete_scheduled
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 18 sept. 2017
"""
__docformat__ = "restructuredtext"


class CompleteScheduled():
    
    """ DB Entity complete_scheduled to Python object CompleteScheduled  """

    __slots__ = ('_CompleteScheduled__id','_CompleteScheduled__dayOfYear','_CompleteScheduled__hourOfDay','_CompleteScheduled__season','_CompleteScheduled__avg_temp','_CompleteScheduled__building_use_id','_CompleteScheduled__id','_CompleteScheduled__building_use','_CompleteScheduled__heating','_CompleteScheduled__cooling','_CompleteScheduled__lighting','_CompleteScheduled__occupancy','_CompleteScheduled__equipment','_CompleteScheduled__DHW','_CompleteScheduled__DHW_total_annual')
    
     
    
    def __init__(self):
        '''
        Constructor
        '''
        self.__id                 = 0
        self.__dayOfYear          = 0
        self.__hourOfDay          = 0
        self.__season             = ""
        self.__avg_temp           = 0.0
        self.__building_use_id    = 0
        self.__building_use       = ""
        self.__heating            = 0.0
        self.__cooling            = 0.0
        self.__lighting           = 0.0
        self.__occupancy          = 0.0
        self.__equipment          = 0.0
        self.__DHW                = 0.0
        
        self.__DHW_total_annual   = 0.0
             
   
   
    def __str__(self):      
        
        text = "id:" + str(self.__id) + " dayOfYear:" +  str(self.__dayOfYear) + " hourOfDay:" + str(self.__hourOfDay) \
                + " building_use_id : " +  str(self.__building_use_id)  \
                + " heating:" + str(self.heating) + " cooling:" + str(self.cooling)  + " DHW:" + str(self.DHW)
    
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
    def avg_temp(self):
        return self.__avg_temp
    
    @avg_temp.setter
    def avg_temp(self, val):
        self.__avg_temp = float(val.replace(",","."))  if isinstance(val,str) else float(val)                    
        
   
    @property
    def building_use_id(self):
        return self.__building_use_id
    
    @building_use_id.setter
    def building_use_id(self, val):
        self.__building_use_id = val        
        
        
    @property
    def building_use(self):
        return self.__building_use
    
    @building_use.setter
    def building_use(self, val):
        self.__building_use = val        
               
        
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
    def lighting(self):
        return self.__lighting
    
    @lighting.setter
    def lighting(self, val):
        self.__lighting =  float(val.replace(",","."))  if isinstance(val,str) else float(val)                         
           
     
    @property
    def occupancy(self):
        return self.__occupancy
    
    @occupancy.setter
    def occupancy(self, val):
        self.__occupancy =  float(val.replace(",","."))  if isinstance(val,str) else float(val)                        
        

    @property
    def equipment(self):
        return self.__equipment
    
    @equipment.setter
    def equipment(self, val):
        self.__equipment =  float(val.replace(",","."))  if isinstance(val,str) else float(val)            
        
    
    @property
    def DHW(self):
        return self.__DHW
    
    @DHW.setter
    def DHW(self, val):
        self.__DHW =  float(val.replace(",","."))  if isinstance(val,str) else float(val)               
    
    @property
    def DHW_total_annual(self):
        return self.__DHW_total_annual
    
    @DHW_total_annual.setter
    def DHW_total_annual(self, val):
        self.__DHW_total_annual =  val