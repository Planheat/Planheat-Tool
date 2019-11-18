# -*- coding: utf-8 -*-
"""
   csv output API  
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

from time import sleep
import sys
import sqlite3
from _sqlite3 import DatabaseError
from model.data import Data


class DB():
    """ API for work with database
     
        Basic operations for work with Sqlite3 embebded database
        
        Common Search, query and sentences for both calculate methods 
         
    """  

    def __init__(self):
        """
        Constructor
        :param log: logger object
        
        """
        
        
        self.__db = None
        self.__cursor = None
        self.__statement=""
        self.__bindvars={}

       
#         
    def connectDB(self,path,  isolationValue=None):
        """ 
            Database connection
            :raises DBNotFoundException: db file not found on filesystem path
        """
        try:
            
            if self.__db is None:
                self.__db = sqlite3.connect(path, isolation_level=isolationValue)#Connect to DatabaseFile
                self.testDB()
                sleep(0.1)
                print("INFO", "DB Init connection OK and Ready")
                    
        except:
            print("ERROR", "connectDB Failure Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__db = None
            raise 
      
        
    def closeDB(self):    
            """ 
            Close Database connection
            """
            try:
                if self.__db is not None:
                    self.__db.close()
            except:
                print("ERROR", " closeDB Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                self.__db = None
                raise    
            
            
    def testDB(self):    
            """ 
            Test Database connection and retrieve the schema version
            """
            try:
                if self.__db is not None:
                    self.__cursor = self.__db.cursor()
                    self.__cursor.execute("PRAGMA synchronous = OFF")
                    self.__cursor.execute("PRAGMA journal_mode = MEMORY")
                    self.__cursor.execute("PRAGMA main.schema_version")
                    version = self.__cursor.fetchone()
                    print("INFO", "testDB test connection success schema version:" + str(version[0]))
            except:
                print("ERROR", "testDB test connection failure Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                self.__db = None
                raise    
    
    def maintenanceDataBase(self, operation):    
            """ 
            Maintenance Database Indexes and Space
            """
            try:
                if self.__db is not None:
                    
                    self.__db.execute(operation)
                    print("INFO", "maintenanceDataBase {} Command executed".format(operation) )
            except:
                print("ERROR", "maintenanceDataBase {} Command failure".format(operation) + " Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                    
    
    def executeStatement(self,statement,bindvars={}):
        
        """ 
            Execute statement with one data retrieved
            :param statement: Execute Statement
            :param bindvars: Bounded variables with the statement
            :returns: Mapped table object    
            :raises DatabaseError: The db operation is erroneous
        """
        
        try:
            data = None
            self.__statement = statement
            self.__bindvars = bindvars          
            
            if self.__bindvars:                    
                self.__cursor.execute(self.__statement,self.__bindvars)
            else:
                self.__cursor.execute(self.__statement)
                
            data = self.__cursor.fetchone()
            
            return data
        
        except DatabaseError:
            print("ERROR", "executeStatement Database error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            print("ERROR", "statement: " + self.__statement)
            if bindvars:
                print("ERROR", "bindvars: " + str(self.__bindvars))
                
            raise
            
        except:
            print("ERROR", "executeStatement Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            print("ERROR", "statement: " + self.__statement)
            if self.__bindvars:
                print("ERROR", "bindvars: " + str(self.__bindvars))
            raise    
     
        
    def executeStatementAll(self,statement,bindvars={}):
        """ 
            Execute statement with all data retrieved
            :param statement: Execute Statement
            :param bindvars: Bounded variables with the statement
            :returns: Mapped table object tuple    
            :raises DatabaseError: The db operation is erroneous
        """
        
        try:
            data = None
            count = 0
            self.__statement = statement
            self.__bindvars = bindvars          
            
            if self.__bindvars:                    
                self.__cursor.execute(self.__statement,self.__bindvars)
            else:
                self.__cursor.execute(self.__statement)
                
            data = self.__cursor.fetchall()
            count  =  len(data)
        
            return count, data
        
        except DatabaseError:
            print("ERROR", "executeStatementAll Database error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            print("ERROR", "statement: " + self.__statement)
            if bindvars:
                print("ERROR", "bindvars: " + str(self.__bindvars))
                
            raise                 
                    
        except:
            print("ERROR", "executeStatementAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            print("ERROR", "statement: " + self.__statement)
            if self.__bindvars:
                print("ERROR", "bindvars: " + str(self.__bindvars))
            raise     
   
    
    
    def commit_data(self):
        try:
            self.__db.commit()
        except:
            print("ERROR", "commit_data Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
            
    
    def rollback_data(self):
        try:
            self.__db.rollback()
        except:
            print("ERROR", "rollback_data Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
            
        
        
    
    def truncate_table(self,table_name):
        """ 
            Simulate ANSI SQL Tuncate Table
            :param table_name: Table Name 
        """
        
        try:
            statement = " DELETE FROM " + table_name + ";"
            self.__statement = statement
            
            self.__cursor.execute(self.__statement)
            self.commit_data()
            self.maintenanceDataBase("VACUUM")

        except:
            print("ERROR", "truncate_table Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            print("ERROR", "statement: " + self.__statement)
            self.rollback_data()
            raise     
    
    
    
    def insert_record_table(self,statement,bindvars={}):
        """ 
            Insert building data for Complete calculate method 
            :param statement: Execute Statement
            :param bindvars: Bounded variables with the statement
        """
        try:
            self.__statement = statement
            self.__bindvars = bindvars
            
            if self.__bindvars:                    
                self.__cursor.execute(self.__statement,self.__bindvars)
            else:
                self.__cursor.execute(self.__statement)
            
            #self.__db.commit()
        except sqlite3.IntegrityError:
            print("ERROR", "insert_record_table Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
            
        except:
            print("ERROR", "insert_record_table Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            print("ERROR", "statement: " + self.__statement)
            if self.__bindvars:
                print("ERROR", "bindvars: " + str(self.__bindvars))
        
    
    
    def insertData2DataBase(self,dataList):
        try:

            
                           
            for data in dataList:           
                if data.Period != "":
                    statement = """INSERT INTO hourly_csv
                               (ProjectID, BuildingID,Period,Use, DayOfYear,HourOfDay,Season,Heating,Cooling,DHW)
                               VALUES(:project_id,:building_id,:period,:use,:day_of_year,:hour_of_day,:season,:heating,:cooling,:dhw);"""    
                               
                    bindvars = {'project_id':data.ProjectID,'building_id':data.BuildingID,'period':data.Period,'use':data.Use,
                                'day_of_year':data.DayOfYear,'hour_of_day':data.HourOfDay,'season':data.Season,
                                'heating':data.Heating, 'cooling': data.Cooling,'dhw':data.DHW}     
                else:
                    statement = """INSERT INTO hourly_csv
                               (ProjectID, BuildingID,DayOfYear,HourOfDay,Season,Heating,Cooling,DHW)
                               VALUES(:project_id,:building_id,:day_of_year,:hour_of_day,:season,:heating,:cooling,:dhw);"""    
                               
                    bindvars = {'project_id':data.ProjectID,'building_id':data.BuildingID,'day_of_year':data.DayOfYear,
                                'hour_of_day':data.HourOfDay,'season':data.Season,'heating':data.Heating, 'cooling': data.Cooling,'dhw':data.DHW} 
                             
                self.insert_record_table(statement,bindvars)
            self.commit_data()              
        except:
            print("ERROR", "insertData2DataBase building_id:{}".format(data.BuildingID))
            print("ERROR", "insertData2DataBase Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.rollback_data() 
            raise    
        
        
    def retrieveTotalizedData(self):
        try:
            dataList=[]
            statement = """SELECT ProjectID,DayOfYear,HourOfDay, ROUND(SUM(IFNULL(Heating,0)),8)Heating,
                           ROUND(SUM(IFNULL(Cooling,0)),8)Cooling,ROUND(SUM(IFNULL(DHW,0)),8)DHW 
                           FROM hourly_csv GROUP BY ProjectID, DayOfYear, HourOfDay ORDER BY ProjectID, DayOfYear, HourOfDay;"""
                           
            _, data_table = self.executeStatementAll(statement)
            
            if data_table:
                for data in data_table:
                    try:
                        aggregateData = Data()
                        aggregateData.ProjectID    = str(data[0])
                        aggregateData.DayOfYear    = data[1]
                        aggregateData.HourOfDay    = data[2]
                        aggregateData.Heating      = data[3]
                        aggregateData.Cooling      = data[4]
                        aggregateData.DHW          = data[5]
                        
                        dataList.append(aggregateData)
                        
                    except Exception as e:
                        print("ERROR", "retrieveTotalizedData create Data " + str(e))
                        raise 
                    
                
                return tuple(dataList)    
                 
            else:
                print("Total District - No data found")
                return None  
                
        except:
            print("ERROR", "retrieveTotalizedData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.rollback_data() 
            raise    
                
         

    