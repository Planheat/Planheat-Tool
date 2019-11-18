# -*- coding: utf-8 -*-
"""
   csv input API  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 12 sept. 2017
"""

__docformat__ = "restructuredtext"  

import csv
import sys
import copy
from collections import namedtuple
from myExceptions.exceptions import NumberIncorrectException



class CSV_Reader():
    
    """ API for read input CSV file
     
        Read file and convert data to necessary format for the process   
    """  


    def __init__(self,log, filename, inputFields):
        """
        Constructor
        
        :param log: logger object
        :param filename: Work file name
        :param inputFields: Column header names list expected for the process
        
        """        
        self.filename = filename
        
        self.__building_data=[]
        self.__log=log
        self.__inputFields = copy.deepcopy(inputFields)
        self.__headerFiedlNames = None
        
        
    def csv_read(self):
        """
        Read File with header field name format
        :returns: building data text list 
        :raises NumberIncorrectException: column header, column header number, with wrong value 
        """        
        try:
            
            formatValue = self.formatValue
            recordTuple = None 
            self.__building_data=[]
            self.__headerFiedlNames = [inputField.headerName for inputField in self.__inputFields]
              
            with open(self.filename, 'r',encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile,fieldnames=self.__headerFiedlNames, delimiter=';', quotechar='"', quoting= csv.QUOTE_NONE, lineterminator='\n')
                headDict = next(reader)
                x = 0
                for value in headDict.values():
                    if value is not None:
                        x += 1
                    
                if x != len(self.__headerFiedlNames):
                    raise NumberIncorrectException("CSV Column Header Number Incorrect expected " +  str(len(self.__headerFiedlNames)))
                
                recordTuple = namedtuple('RecordTuple', headDict.keys())   
                              
                for y, row in enumerate(reader):
                    if len(row) != len(self.__headerFiedlNames): 
                        raise NumberIncorrectException("CSV Column Row Number Incorrect expected " +  str(len(self.__headerFiedlNames)) + " for java output file xmlResultado.csv row number:" + str(y+2)) # Included Header columns row
                
                    for key, value in row.items():
                        if value is not None:
                            value = formatValue(key, value)
                        else:
                            value = ""    
                        row[key] = value
                    
                    self.__building_data.append(self.convert(recordTuple,row))
                    #self.__building_data.append(copy.deepcopy(row))
                del reader        
            
            self.__log.write_log("INFO", "csv_read  - file " +  self.filename + " data read")
            
            return self.__building_data
        
        except NumberIncorrectException as e:
            self.__log.write_log("ERROR",  e)
            self.__building_data = None     
            raise              
        except:
            self.__log.write_log("ERROR", "CSV Read Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__building_data = None
            raise    
    
   
    
    def convert(self,namedTupled,obj):
        """ Fast Conversion Dictionary to Tuple"""
        if isinstance(obj, dict):
            return namedTupled(**obj)     
        else:
            return obj   
    
    """
    #Complete Conversion
    def convert(self,obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self.convert(value)
            return namedtuple('GenericDict', obj.keys())(**obj)
        elif isinstance(obj, list):
            return [self.convert(item) for item in obj]
        else:
            return obj   
    """    
            
    def formatValue(self,key, value):
        
        """
        Data formatting

        :param key: dict key to transform
        :param value: dict value to transform
        :returns: value transformed into the corresponding format
        """
        try:
            result = value
            
            for inputField in self.__inputFields:
                if inputField.headerName == key:
                    if inputField.format == 'float':
                        result = result.replace(",",".")
                        result = "{:{}.{}f}".format(float(result),inputField.length,inputField.precision)
                        result = float(result)
                    elif inputField.format == 'int':   
                        result = result.replace(",",".")
                        result = "{:{}.0f}".format(float(result),inputField.length)
                        result = int(result)
                    elif inputField.format == 'str' and inputField.length is not None and inputField.length > 0:
                        result = "{:.{}}".format(result,inputField.length)
                    elif inputField.format == 'boolean':
                        if result is None or result.lower() == "false" or result == "0":  
                            result = False
                        else:
                            result = True
                    elif inputField.format == 'date':
                        pass           
                    break
            return result
        except:
            self.__log.write_log("ERROR", "CSV Reader formatValue - key " + key + " value " + value + " Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return value
    
    
             