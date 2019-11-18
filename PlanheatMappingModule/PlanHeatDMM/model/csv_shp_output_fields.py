# -*- coding: utf-8 -*-
"""
   Model Map table csv_shp_output_fields
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 28 sept. 2017
"""
__docformat__ = "restructuredtext"

class CsvShpOutputFields():
    
    """ DB Entity csv_shp_output_fields to Python object CsvShpOutputFields  """

    def __init__(self):
        self.__id               = 0
        self.__scenario         = None
        self.__fileCategory     = None
        self.__fileType         = None
        self.__calculateModel   = None
        self.__headerName       = None
        self.__attributeName    = None
        self.__format           = None
        self.__length           = None
        self.__precision        = None
        
             
   
    def __str__(self):
        return "id:" + str(self.id) + " - scenario:" + self.scenario  +   " - fileCategory:" + self.fileCategory +  " - fileType:" + self.fileType + " - calculateModel:" + self.calculateModel \
                + " - headerName:" + self.headerName + " - attributeName:" + self.attributeName \
                + " - format:" + self.format + " - length:" + str(self.length) + " - precison:" + str(self.precision)    
    
    
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
   
    @property
    def scenario(self):
        return self.__scenario
    
    @scenario.setter
    def scenario(self, val):
        self.__scenario = val
        
   
    @property
    def fileCategory(self):
        return self.__fileCategory
    
    @fileCategory.setter
    def fileCategory(self, val):
        self.__fileCategory = val
        
            
    @property
    def fileType(self):
        return self.__fileType
    
    @fileType.setter
    def fileType(self, val):
        self.__fileType = val
        
            
    @property
    def calculateModel(self):
        return self.__calculateModel
    
    @calculateModel.setter
    def calculateModel(self, val):
        self.__fileType = val
        
        
    @property
    def headerName(self):
        return self.__headerName
    
    @headerName.setter
    def headerName(self, val):
        self.__headerName = val        
           
        
    @property
    def attributeName(self):
        return self.__attributeName
    
    @attributeName.setter
    def attributeName(self, val):
        self.__attributeName = val       
  
    
    @property
    def format(self):
        return self.__format
    
    @format.setter
    def format(self, val):
        self.__format = val    

    
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