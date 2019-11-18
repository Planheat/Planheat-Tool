# -*- coding: utf-8 -*-
"""
   Model Map table SHAPE input file to Process CSV file
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 09 Oct. 2017
"""
__docformat__ = "restructuredtext"


import sys

class ShpCsvInputFields():
    
    """ DB Entity shp_map_csv_input_fields to Python object ShpCsvInputFields  """

    def __init__(self):
        self.__id    = 0
        self.__calculateModel        = None
        self.__fieldState            = None
        self.__fieldName             = None
        self.__format                = None
        self.__length                = None
        self.__precision             = None
        self.__user_format_match     = None
        self.__user_definition_field = ""
        
        
   
    def __str__(self):
        try:
            
            return "id:" + str(self.id) + " - fieldState:" + self.fieldState + " - fieldName:" + self.fieldName + " user_definition_field:" + self.user_definition_field    
        except:
            print("ERROR", "ShpCsvInputFields __str__ Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                    
        
    
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
   
   
    @property
    def fieldState(self):
        return self.__fieldState
    
    @fieldState.setter
    def fieldState(self, val):
        self.__fieldState = val
    
    def setFieldState(self, val):
        self.__fieldState = val       
        
        
            
    @property
    def calculateModel(self):
        return self.__calculateModel
    
    @calculateModel.setter
    def calculateModel(self, val):
        self.__calculateModel = val
        
        
    @property
    def fieldName(self):
        return self.__fieldName
    
    @fieldName.setter
    def fieldName(self, val):
        self.__fieldName = val        
           
   
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
        
        
    @property
    def user_format_match(self):
        return self.__user_format_match
    
    @user_format_match.setter
    def user_format_match(self, val):
        self.__user_format_match = bool(val)                  
        
    
    @property
    def user_definition_field(self):
        return self.__user_definition_field
    
    @user_definition_field.setter
    def user_definition_field(self, val):
        self.__user_definition_field = val     

