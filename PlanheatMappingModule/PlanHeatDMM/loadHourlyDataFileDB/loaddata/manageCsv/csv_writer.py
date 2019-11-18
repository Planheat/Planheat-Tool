# -*- coding: utf-8 -*-
"""
   csv write output API  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 21 Jan. 2018
   :copyright: (C) 2018 by Tecnalia

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

import csv
import sys

class CSV_Writer():
    """ API for write output CSV files
     
        write data output files   
    """  

    def __init__(self,filename,headerFiedlNames):
        """
        Constructor
        
        :param log: logger object
        :param filename: Work file name
        :param inputFields: Column header names list for output file 
        
        """       
                
        self.filename = filename
        self.__headerFiedlNames = headerFiedlNames  
        
 
        try:
            with open(self.filename, 'w',encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.__headerFiedlNames, delimiter=';',restval='',extrasaction='ignore', quotechar='"', quoting=csv.QUOTE_NONE, lineterminator='\n')        
                writer.writeheader()
                csvfile.close()      
                print("INFO", "Output CSV file " +  self.filename + " created")
        except:
            print("ERROR", "CSV_Writer Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
           
           
            
    def writeRowsCSV(self, dataList):
        """
        Write list Data Processed to output file 
        
        :param dataList: List of data to write
        
        """  
        try:
            rows = self.__compose_rows(dataList)
            
            if rows:
                with open(self.filename, 'a',encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.__headerFiedlNames, delimiter=';', restval='',extrasaction='ignore', quotechar='"', quoting=csv.QUOTE_NONE, lineterminator='\n')
                    """ CSV API doesn't work correctly with UTF-8, we encode bytes str to utf-8 and add fix_encode_error_char_map for correct the charmap characters it can´t associate    
                    """
                    for row in rows:
                        for k,v in row.items():
                            #v = fix_encode_error_char_map(v)
                            v = v.encode(encoding='UTF-8',errors='ignore').decode(encoding='UTF-8',errors='ignore')
                            row[k] = v
                        try:
                            writer.writerow(row)
                            
                        except UnicodeEncodeError:
                            print("ERROR", " writeRowsCSV UnicodeEncodeError " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                        except :
                            print("ERROR", "writeRowsCSV Exception "+ str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                
                print("INFO", "CSV file populated")            
        except:
            print("ERROR", "CSV_Writer writeRowsCSV Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise        
        
    def __compose_rows(self, dataList):
        
        """
        Create row data to write for DictWriter API 
        
        :param dataList: List of data to write
        
        """  
        rows = []
        
        try:
            if dataList:
                for data in dataList:            
                    row = dict()
                    for headerName in self.__headerFiedlNames: 
                        value       = getattr(data,headerName)
                        key         = headerName
                        if isinstance(value,float):
                            newValue = "{:{}.{}f}".format(float(value),20,4).strip()
                            newValue = newValue.replace(".",",")
                        elif isinstance(value,(int,bool)): 
                            newValue = str(value)
                        else:       
                            newValue = value

                        row.update(zip(key.split(";"),newValue.split(":")))
    
                    rows.append(row)
            return rows         
        except:
            print("ERROR", "CSV_Writer compose_rows:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise                
              
                       
    
        
   
    
    