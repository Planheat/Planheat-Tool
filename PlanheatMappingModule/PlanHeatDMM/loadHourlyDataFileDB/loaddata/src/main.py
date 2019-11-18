# -*- coding: utf-8 -*-
"""
   main - Load hourly demand from datafile to sqlite3 database
   :author: Sergio Aparicio Vegas
   :version: 1.0
   :date: 22 Jan. 2018
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

import sys

from manageDB.db import DB
from manageCsv.csv_reader import CSV_Reader
from manageCsv.csv_writer import CSV_Writer

BATCH_SIZE = 10000
HEADER = ["ProjectID","DayOfYear","HourOfDay","Heating","Cooling","DHW"]


def showTotalizedData(header,dataList):
    
    try:
        HEADER ="{}\t{}\t{}\t{}\t{}\t{}".format(HEADER[0],HEADER[1],HEADER[2],HEADER[3],HEADER[4],HEADER[5])         
        print(header)
        for data in dataList:
            totalHeating = "{:{}.{}f}".format(float(data.Heating),20,4).strip()
            totalCooling = "{:{}.{}f}".format(float(data.Cooling),20,4).strip()
            totalDHW     = "{:{}.{}f}".format(float(data.DHW),20,4).strip()
            
            row = "{}\t{}\t{}\t{}\t{}\t{}".format(data.ProjectID,data.DayOfYear,data.HourOfDay,totalHeating,totalCooling,totalDHW)
            print (row)
    
    except:
        print("ERROR", "showTotalizedData" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                    
                        
       
def saveDataToFile(filename, header,dataList):
    try:
        csvwrite = CSV_Writer(filename,header)
        csvwrite.writeRowsCSV(dataList)
    except:
        print("ERROR", "saveDataToFile" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        raise    
    

def loadData(args):    
    database = None
    
    try:
        batch_size = BATCH_SIZE
        database = DB()
        database.connectDB(args.db)
        
        if not args.mantain:
            print("INFO Truncate table data")
            database.truncate_table("hourly_csv")
        else:    
            print("INFO Mantain table data")
        
        
        if  args.inputfile is not None: 
            print("INFO Create CSV Object - BATCH SIZE",batch_size )
            csvread = CSV_Reader(args.inputfile,batch_size)
            
            print("INFO Open CSV file")
            dataList = csvread.csv_open()
            
            print("INFO Process CSV file")
            x=0
            records = 0
             
            while dataList:
                x+=1
                dataList = csvread.csv_batch_read()
                
                if dataList:
                    print("INFO Read Batch:",x, end=' ')
                    records += len(dataList)
                    print("Insert data to table, record:",records )
                    database.insertData2DataBase(dataList)
            
            #print("INFO Close CSV file")
            dataList = csvread.csv_close()
                
            
        #for data in dataList:
        #    print(data)
        
        if not args.total or args.outputfile:
            
            aggregateList = database.retrieveTotalizedData()
            if not args.total and aggregateList:
                showTotalizedData(HEADER,aggregateList)
            if args.outputfile and aggregateList:
                saveDataToFile(args.outputfile, HEADER, aggregateList)    
            
            
        print("INFO Finish loadData")
            
    except:
        print("ERROR", "main Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
    finally:
        
        if database is not None: 
            database.closeDB()
    

    
    