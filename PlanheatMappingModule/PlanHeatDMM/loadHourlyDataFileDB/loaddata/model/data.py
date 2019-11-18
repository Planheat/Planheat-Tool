# -*- coding: utf-8 -*-
"""
   data input API  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 19 Jan. 2018
   :copyright: (C) 2017 by Tecnalia

 ***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License or      * 
 *   any later version.                                                    *
 *                                                                         *
 ***************************************************************************
"""

__docformat__ = "restructuredtext"


class Data():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''


        self.__ProjectID          = ""
        self.__BuildingID         = ""
        self.__Period             = ""
        self.__Use                = ""
        self.__DayOfYear          = 0
        self.__HourOfDay          = 0
        self.__Season             = ""
        self.__Heating            = 0.0
        self.__Cooling            = 0.0
        self.__DHW                = 0.0
        
        
        
    def __str__(self):      
        
        text = "ProjectID:" + str(self.__ProjectID) + " BuildingID:" + str(self.__BuildingID) +  " Period:" + str(self.__Period) + \
                +  " Use:" + str(self.__Use) +  " DayOfYear:" +  str(self.__DayOfYear) + " HourOfDay:" + str(self.__HourOfDay) \
                + " Season:" + self.Season  +  " Heating:" + str(self.Heating) + " cooling:" + str(self.Cooling) \
                + " DHW:" + str(self.DHW)  
    
        return text 
    
    
    
    @property
    def ProjectID(self):
        return self.__ProjectID
    
    @ProjectID.setter
    def ProjectID(self, val):
        self.__ProjectID = val
        
        
    @property
    def BuildingID(self):
        return self.__BuildingID
    
    @BuildingID.setter
    def BuildingID(self, val):
        self.__BuildingID = val    
        
        
    @property
    def Period(self):
        return self.__Period
    
    @Period.setter
    def Period(self, val):
        self.__Period = val     
        
        
    @property
    def Use(self):
        return self.__Use
    
    @Use.setter
    def Use(self, val):
        self.__Use = val         
    
    
    @property
    def DayOfYear(self):
        return self.__DayOfYear
    
    @DayOfYear.setter
    def DayOfYear(self, val):
        self.__DayOfYear = val       
    
        
    @property
    def Season(self):
        return self.__Season
    
    @Season.setter
    def Season(self, val):
        self.__Season = val   
        
        
    @property
    def HourOfDay(self):
        return self.__HourOfDay
    
    @HourOfDay.setter
    def HourOfDay(self, val):
        self.__HourOfDay = val      
        
   
    @property
    def Heating(self):
        return self.__Heating
    
    @Heating.setter
    def Heating(self, val):
        self.__Heating =  float(val.replace(",","."))  if isinstance(val,str) else float(val)                 
               
        
    @property
    def Cooling(self):
        return self.__Cooling
    
    @Cooling.setter
    def Cooling(self, val):
        self.__Cooling =  float(val.replace(",","."))  if isinstance(val,str) else float(val)                      
           
     
    @property
    def DHW(self):
        return self.__DHW
    
    @DHW.setter
    def DHW(self, val):
        self.__DHW =  float(val.replace(",","."))  if isinstance(val,str) else float(val)           
       
        