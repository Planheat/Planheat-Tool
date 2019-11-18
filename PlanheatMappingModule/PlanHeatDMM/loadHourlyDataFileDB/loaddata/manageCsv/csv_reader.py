# -*- coding: utf-8 -*-
"""
   csv read input API  
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
from copy import deepcopy
from model.data import Data




class CSV_Reader():
    
    """ API for read input CSV file
     
        Read file and convert data to necessary format for the process   
    """  


    def __init__(self,filename, batch_size = 1000, inputFields=None):
        """
        Constructor
        
        :param log: logger object
        :param filename: Work file name
        :param inputFields: Column header names list expected for the process
        
        """        
        self.filename = filename
        self.inputFields = inputFields
        self.headerFiedlNames = None
        self.csvfile = None
        self.reader = None
        self.batch_size = batch_size
        self.data=[]
        
        
    def csv_open(self):
        """
        Read File with header field name format
        :returns: building data text list 
        :raises NumberIncorrectException: column header, column header number, with wrong value 
        """        
        try:
            #self.headerFiedlNames = [inputField.headerName for inputField in self.inputFields]  
            self.csvfile = open(self.filename, 'r',encoding='utf-8')
            reader = csv.DictReader(self.csvfile, delimiter=';', quotechar='"', quoting= csv.QUOTE_NONE, lineterminator='\n')
            #headDict = next(reader)
                
            self.reader = reader
          
            return reader
             
        except:
            print("ERROR", "CSV Read Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.data = None
            raise    
    
    
    def csv_close(self):
        del self.reader
        self.csvfile.close()    
        
        
    def csv_batch_read(self):
        try:
            self.data = []
            for y, row in enumerate(self.reader):
                
                """
                if len(row) != len(self.headerFiedlNames): 
                    raise Exception("CSV Column Row Number Incorrect: " + str(len(row)) + " expected " +  str(len(self.headerFiedlNames)))
                
                """        
                data = Data()
               
                for key, value in row.items():
                    try:
                        
                        if getattr(data, key,None) is not None:
                            setattr(data, key, value)
                        
                    except:
                        print("key:",key, " value:",value)
                        print("ERROR", "CSV csv_batch_read assignment Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                        raise    
                
                #print ("data",data)            
                self.data.append(deepcopy(data))
                if y == self.batch_size-1:break
                
                    
            
            #print("INFO", "csv_read  - file " +  self.filename + " data read")
            return self.data
        except:
            print("ERROR", "CSV csv_batch_read Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.data = None
            raise    
            
            
  