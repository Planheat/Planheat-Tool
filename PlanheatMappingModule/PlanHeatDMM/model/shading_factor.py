# -*- coding: utf-8 -*-
"""
   Future Use
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 31 Oct. 2017
"""
__docformat__ = "restructuredtext"


class ShadingFactor():
    """ Defined for future use """


    def __init__(self,defaultValue=0.0):
        
        self.__id                 = 0
        self.__dayOfYear          = 0
        self.__hourOfDay          = 0
        self.__north              = defaultValue
        self.__south              = defaultValue
        self.__east               = defaultValue
        self.__west               = defaultValue
        
        
        

    def __str__(self):
        return "id:" + str(self.id) + " dayOfYear:" + str(self.dayOfYear) + " hourOfDay:" + str(self.hourOfDay) + \
               " north:" + str(self.north) + " south:" + str(self.south) + " east:" + str(self.east) + " west:" + str(self.west)
    
    
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
    def hourOfDay(self):
        return self.__hourOfDay
    
    @hourOfDay.setter
    def hourOfDay(self, val):
        self.__hourOfDay = val
        
        
    @property
    def north(self):
        return self.__north
    
    @north.setter
    def north(self, val):
        self.__north = float(val.replace(",","."))  if isinstance(val,str) else float(val)     
        
    
    @property
    def south(self):
        return self.__south
    
    @south.setter
    def south(self, val):
        self.south = float(val.replace(",","."))  if isinstance(val,str) else float(val)     
    
    
    @property
    def east(self):
        return self.__east
    
    @east.setter
    def east(self, val):
        self.east = float(val.replace(",","."))  if isinstance(val,str) else float(val)
        
    
    @property
    def west(self):
        return self.__west
    
    @west.setter
    def west(self, val):
        self.west = float(val.replace(",","."))  if isinstance(val,str) else float(val)               
    