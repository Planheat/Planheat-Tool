# -*- coding: utf-8 -*-
"""
   csv output API  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 11 sept. 2017
"""
__docformat__ = "restructuredtext"  

import csv
import sys
import copy
from config import config as Config
#from utility.utils import fix_encode_error_char_map

class CSV_Writer():
    """ API for write output CSV files
     
        write data output files   
    """  

    def __init__(self,log, filename, outputFieldsCsv,boolAddShapeFields=False ,userFieldShapeMap=None):
        """
        Constructor
        
        :param log: logger object
        :param filename: Work file name
        :param inputFields: Column header names list for output file 
        
        """       
                
        self.filename = filename
        self.__outputFieldsCsv = copy.deepcopy(outputFieldsCsv)
        self.__headerFiedlNames = None  
        self.__boolAddShapeFields = boolAddShapeFields
        self.__userFieldShapeMap  = userFieldShapeMap
        
 
        try:
            self.__log=log
                
            if self.__outputFieldsCsv is not None: 
                with open(self.filename, 'w',encoding='utf-8') as csvfile:
                    self.__headerFiedlNames = [outputFieldCsv.headerName for outputFieldCsv in self.__outputFieldsCsv]
                    if self.__boolAddShapeFields and self.__userFieldShapeMap:
                        for userFieldShape in self.__userFieldShapeMap:
                            self.__headerFiedlNames.append(userFieldShape.key)
                             
                    writer = csv.DictWriter(csvfile, fieldnames=self.__headerFiedlNames, delimiter=';',restval='',extrasaction='ignore', quotechar='"', quoting=csv.QUOTE_NONE, lineterminator='\n')        
                    writer.writeheader()
                csvfile.close()      
                self.__log.write_log("INFO", "CSV_Writer Constructor  - " +  self.filename + " Created")
            else:
                self.__log.write_log("WARNING", "CSV_Writer not output fields selected to write on file " +  self.filename  )    
        except:
            self.__log.write_log("ERROR", "CSV_Writer Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
           
           
            
    def writeRowsCSV(self, dataList):
        """
        Write list Data Processed to output file 
        
        :param dataList: List of data to write
        
        """
        try:
            if self.__outputFieldsCsv is not None:
                
                rows = self.__compose_rows(dataList)
                if rows:
                    with open(self.filename, 'a',encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=self.__headerFiedlNames, delimiter=';', restval='',extrasaction='ignore', quotechar='"', quoting=csv.QUOTE_NONE, lineterminator='\n')
                        
                        writerow = writer.writerow 
                        
                        for row in rows:
                            """
                             CSV API doesn't work correctly with UTF-8, we encode bytes str to utf-8 and add fix_encode_error_char_map for correct the charmap characters it can´t associate    
                            
                            for k,v in row.items():
                                #v = fix_encode_error_char_map(v)
                                v = v.encode(encoding='UTF-8',errors='ignore').decode(encoding='UTF-8',errors='ignore')
                                row[k] = v
                            """    
                            try:
                                writerow(row)
                                
                            except :
                                self.__log.write_log("ERROR", "writeRowsCSV Exception " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                                
                                
                        #writer.writerows(rows)
                del rows 
                    #csvfile.close()
                    #self.__log.write_log("INFO", "writeRowsCSV  - " + self.filename + " Populated")
        except:
            self.__log.write_log("ERROR", "CSV_Writer writeRowsCSV Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise        
        
    def __compose_rows(self, dataList):
        
        """
        Create row data to write for DictWriter API 
        
        :param dataList: List of data to write
        
        """  
        rows = []
        append = rows.append
        formatValue = self.__formatValue
        
        try:
            if dataList:
                for data in dataList:            
                    if data.Regstatus and data.Regprocess:
                        row = {}
                        for outputField in self.__outputFieldsCsv: 
                            value       = getattr(data,outputField.attributeName)
                            key         = outputField.headerName
                            dataFormat  = outputField.format
                            length      = outputField.length
                            precision   = outputField.precision 
                            
                            newValue    = formatValue(key,value,dataFormat,length,precision)
                            
                            newValue = newValue.encode(encoding='UTF-8',errors='ignore').decode(encoding='UTF-8',errors='ignore')
                            row[key] = newValue
                            #row.update(zip(key.split(";"),newValue.split(":")))
                        
                        if self.__boolAddShapeFields and self.__userFieldShapeMap:
                            for userFieldShape in self.__userFieldShapeMap:
                                value = data.shpRecordData[userFieldShape.position]
                                if isinstance(value, str):
                                    value = value.replace(";", ",")
                                     
                                    
                                row[userFieldShape.key] = value
                            
                        append(row)
            return rows         
        except:
            self.__log.write_log("ERROR", "CSV_Writer compose_rows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise                
              
                       
    
        
    def __formatValue(self,key, value, dataFormat, length, precision):
        """
        Data formatting

        :param key: dict key to transform
        :param value: dict value to transform
        :param dataFormat: type of format
        :param length: max length of data
        :param precision: precision if is a number
        :returns: value transformed into the corresponding format and styling
        """
        
        try:
            
            result = str(value)
            if dataFormat in 'float':
                result = result.replace(",",".")
                result = "{:{}.{}f}".format(float(result),length,precision)
                result = result.strip()
                if Config.DECIMAL_POINT_IS_COMMA in ("Y","y"):
                    result = result.replace(".",",")
            elif dataFormat in 'int':
                result = result.replace(",",".")
                result = "{:{}.0f}".format(float(result),length)
                result = result.strip()
            elif dataFormat in 'str' and length is not None and length > 0:
                result = "{:.{}}".format(result,length)
                result = result.strip()    
            elif dataFormat in 'boolean':
                if result is None or result.lower() == "false" or result == "0":  
                    result = "False"
                else:
                    result = "True"
            elif dataFormat in 'date':
                pass               
            
            return result
        except:
            self.__log.write_log("ERROR", "CSV write formatValue - key " + key + " value " + str(value) + " Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return str(value)
    
    