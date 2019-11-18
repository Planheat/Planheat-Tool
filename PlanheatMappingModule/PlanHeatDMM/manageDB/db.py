# -*- coding: utf-8 -*-
"""
   csv output API  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 23 sep. 2017
"""

__docformat__ = "restructuredtext"  

from time import sleep
import sys
import os
import sqlite3


from myExceptions.exceptions import DBNotFoundException, NoDataFoundException
from config import config as Config
from model.country import Country
from model.building_use import BuildingUse
from model.period import Period
from model.shp_map_csv_input_fields import ShpCsvInputFields
from model.protection_level import ProtectionLevel 
from model.complete_scheduled import CompleteScheduled
from model.csv_interim_input_fields import CsvInterimInputFields
from model.csv_shp_output_fields import CsvShpOutputFields
from model.alternative_scheduled import AlternativeScheduled
from model.location_avg_temperature import LocationAvgTemperature
from model.refurbishment_period_level import RefurbishmentLevelPeriod
from model.refurbishment_level import RefurbishmentLevel
from _sqlite3 import DatabaseError





class DB():
    """ API for work with database
     
        Basic operations for work with Sqlite3 embebded database
        
        Common Search, query and sentences for both calculate methods 
         
    """  

    def __init__(self,log):
        """
        Constructor
        :param log: logger object
        
        """
        
        self.__log = log
        self.__dbfile = ""
        self.__db = None
        self.__cursor = None
        self.__statement=""
        self.__bindvars={}

       
    @property
    def dbfile(self):
        return self.__dbfile 
          
    def connectDB(self, isolationValue=None):
        """ 
            Database connection
            :raises DBNotFoundException: db file not found on filesystem path
        """
        
        try:
            
            if self.__db is None:
                self.__dbfile = Config.PLUGIN_DIR + os.path.sep +  Config.DB_PARAMS['path'] + os.path.sep + Config.DB_PARAMS['databaseName']
                if os.path.isfile(self.__dbfile):
                    
                    #self.dbfile = sqlite3.connect(Config.PLUGIN_DIR +  Config.DB_PARAMS['path'] + Config.DB_PARAMS['databaseName'])#Connect to DatabaseFile
                    #self.__db = sqlite3.connect(':memory:') # create a memory database
                    #query = "".join(line for line in self.dbfile.iterdump()) # Query Dump DatabaseFile
                    #self.__db.executescript(query)# Dump file database to the new memory database.
                    #self.dbfile.close()
                    
                    self.__db = sqlite3.connect(self.__dbfile, isolation_level=isolationValue)#Connect to DatabaseFile
                    self.testDB()
                    sleep(0.1)
                    self.__log.write_log("INFO", "DB Init {}  connection OK and Ready".format(Config.DB_PARAMS['databaseName']))
                else:
                    raise DBNotFoundException
 
        except DBNotFoundException:
            self.__log.write_log("ERROR", "connectDB Failure No exists DB " + self.__dbfile)
            raise
                    
        except:
            self.__log.write_log("ERROR", "connectDB Failure Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
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
                self.__log.write_log("ERROR", " closeDB Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
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
                    self.__log.write_log("INFO", "testDB test connection success schema version:" + str(version[0]))
            except:
                self.__log.write_log("ERROR", "testDB test connection failure Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                self.__db = None
                raise    
    
    def maintenanceDataBase(self, operation):    
            """ 
            Maintenance Database Indexes and Space
            """
            try:
                if self.__db is not None:
                    #self.__db.execute("REINDEX")
                    self.__db.execute(operation)
                    self.__log.write_log("INFO", "maintenanceDataBase {} Command executed".format(operation) )
            except:
                self.__log.write_log("ERROR", "maintenanceDataBase {} Command failure".format(operation) + " Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                raise    
            
    
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
            self.__log.write_log("ERROR", "executeStatement Database error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "statement: " + self.__statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(self.__bindvars))
                
            raise
            
        except:
            self.__log.write_log("ERROR", "executeStatement Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "statement: " + self.__statement)
            if self.__bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(self.__bindvars))
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
            self.__log.write_log("ERROR", "executeStatementAll Database error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "statement: " + self.__statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(self.__bindvars))
                
            raise                 
                    
        except:
            self.__log.write_log("ERROR", "executeStatementAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "statement: " + self.__statement)
            if self.__bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(self.__bindvars))
            raise     
   
    
    
    def commit_data(self):
        try:
            self.__db.commit()
        except:
            self.__log.write_log("ERROR", "commit_data Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
            
    
    def rollback_data(self):
        try:
            self.__db.rollback()
        except:
            self.__log.write_log("ERROR", "rollback_data Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
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

        except:
            self.__log.write_log("ERROR", "truncate_table Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "statement: " + self.__statement)
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

        except:
            self.__log.write_log("ERROR", "insert_record_table Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "statement: " + self.__statement)
            if self.__bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(self.__bindvars))
            raise 
        
         

    #SEARCHING METHODS SHARED By both calculate Methods 
    
    def truncate_calculate_complete_totalized_table(self):
        """  Call truncate table function for calculate_complete_totalized_demand table   """
        try:
            table_name = "calculate_complete_totalized_demand"
            
            self.truncate_table(table_name)
            
            self.__log.write_log("INFO", "Truncate calculate_complete_totalized_demand ")
            
            
        except:
            self.__log.write_log("ERROR", "truncate_calculate_complete_totalized_table Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise 
        
        
          
    def retrieveCountryByName(self,name):
        """ 
             Retrieve country object, for named country 
            :param name str: Name of country
            :returns: Mapped table object, country 
            :raises NoDataFoundException: Not found data in table for active country given
        """
        
        try:
            statement = """SELECT  country.id, country.country, 
                           country.heating_base, country.cooling_base
                           FROM country as country 
                           WHERE  active = 1 AND country.country = :name;"""

            bindvars = {'name':name}

            data = self.executeStatement(statement,bindvars)

            if data:
                country_demand = Country()
                country_demand.id = data[0]
                country_demand.country = data[1]
                country_demand.heating_base = data[2]
                country_demand.cooling_base = data[3]
                
                return country_demand
            else:
                raise NoDataFoundException("No record found on table country")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCountryByName " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise
        
        except:
            self.__log.write_log("ERROR", "retrieveCountryByName Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
    
    
    def retrieveCountryAll(self):
        """ 
             Retrieve countries dict 
            :returns: Mapped table Dict, country 
            :raises NoDataFoundException: Not found data in table for active country
        """
        try:
            countries = dict()
            statement = """SELECT  country.id, country.country, 
                           country.heating_base, country.cooling_base
                           FROM country as country 
                           WHERE  active = 1
                           ORDER BY country.country ASC;"""

            
            
            totalRegs, data_table = self.executeStatementAll(statement)
            
            if data_table:
                for data in data_table:
                    try:
                        country = Country()
                        country.id = int(data[0])
                        country.country = data[1]
                        country.heating_base = data[2]
                        country.cooling_base = data[3]
                        
                        countries[country.id] = country
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveCountryAll create Country " + str(e)) 
                else:
                    return countries
            else:    
                raise NoDataFoundException("No record found on table country")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCountryAll " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCountryAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
    
    
    def retrievePeriodsAll(self):
        try:

            dataList = []
            statement = """SELECT period.id, period.start_period, period.end_period,period.period_text
                           FROM period as period
                           WHERE period.active = 1
                           ORDER BY period.start_period, period.end_period; """



            totalRegs, data_table = self.executeStatementAll(statement)

            if data_table:
                for data in data_table:
                    try:
                        period = Period()
                        period.id                = int(data[0])
                        period.start_period      = int(data[1])
                        period.end_period        = int(data[2])
                        period.period_text       = data[3]

                        dataList.append(period)

                    except Exception as e:
                        self.__log.write_log("ERROR", "DB retrieveCompletePeriodsAll create Period" + str(e))
                else:
                    return tuple(dataList)
            else:
                raise NoDataFoundException("No record found on table period" )



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "DB retrieveCompletePeriodsAll " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)

        except:
            self.__log.write_log("ERROR", "DB retrievePeriodsAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
    
    
    def retrieveBuildingUseAll(self):
        """ 
             Retrieve Building uses list 
            :returns: List of all active building_use from mapped table 
            :raises NoDataFoundException: Not found data in table for active country
        """
        try:
            buildingUses = list()
            
            statement = """SELECT  use.id, use.use, use.non_office,use.floor_height, use.description, use.associated_icon_file
                           FROM building_use as use 
                           WHERE  use.active = 1;"""
            
            totalRegs, data_table = self.executeStatementAll(statement)
            
            if data_table:
                for data in data_table:
                    try:
                        buildingUse = BuildingUse()
                        buildingUse.id                   = int(data[0])
                        buildingUse.use                  = data[1]
                        buildingUse.non_office           = data[2]
                        buildingUse.floor_height         = data[3]
                        buildingUse.description          = data[4]
                        buildingUse.associated_icon_file = data[5]
                        
                        buildingUses.append(buildingUse) 
                        
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveBuildingUseAll create BuildingUse " + str(e)) 
                else:
                    return buildingUses
            else:    
                raise NoDataFoundException("No record found on table building_use")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveBuildingUseAll " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "retrieveBuildingUseAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
    
     
     
    def retrieveRefurbishmentLevelsAll(self):
        try:
            
            refurbishmentLevelList = list()
            statement = """SELECT level.id, level.level as refurbishment_level
                           FROM   refurbishment_level level 
                           WHERE  level.active = 1;"""


            totalRegs, data_table = self.executeStatementAll(statement)
            
            if data_table:
                for data in data_table:
                    try:
                        refurbishmentLevel = RefurbishmentLevel()
                        refurbishmentLevel.id    = int(data[0])
                        refurbishmentLevel.level = data[1]
                        
                        refurbishmentLevelList.append(refurbishmentLevel) 
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveRefurbishmentLevelsAll create RefurbishmentLevel " + str(e))
                else:
                    return tuple(refurbishmentLevelList)    

            else:
                raise NoDataFoundException("No record found on table refurbishment_level")



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveRefurbishmentLevelsAll " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "retrieveRefurbishmentLevelsAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    

        
        
        
    def retrieveRefurbishmentLevelsPeriodsAll(self, periods):
        try:

            dataDict = {}

            for period in periods:
                    refurbishmentLevelPeriod = self.retrieveRefurbishmentLevelPeriodId(period.id)
                    if refurbishmentLevelPeriod:
                        dataDict[period.id] = refurbishmentLevelPeriod

            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveRefurbishmentLevelsPeriodsAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise

    
    
    def retrieveRefurbishmentLevelPeriodId(self, period_id):
        try:
            
            refurbishmentLevelPeriodList = list()
            statement = """SELECT period_level.id, period.id as period_id, level.id as refurbishment_level_id, level.level as refurbishment_level
                           FROM   refurbishment_periods_levels period_level INNER JOIN refurbishment_level level ON
                                  period_level.refurbishment_level_id  = level.id INNER JOIN period as period ON  
                                  period_level.period_id = period.id 
                           WHERE period.id = :period_id AND level.active = 1 AND period.active = 1;"""

            bindvars = {'period_id':period_id}


            totalRegs, data_table = self.executeStatementAll(statement,bindvars)
            
            if data_table:
                for data in data_table:
                    try:
                        refurbishmentLevelPeriod = RefurbishmentLevelPeriod()
                        refurbishmentLevelPeriod.id                     = int(data[0])
                        refurbishmentLevelPeriod.period_id              = int(data[1])
                        refurbishmentLevelPeriod.refurbishment_level_id = int(data[2])
                        refurbishmentLevelPeriod.refurbishment_level    = data[3]
                        
                        refurbishmentLevelPeriodList.append(refurbishmentLevelPeriod) 
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveRefurbishmentLevelPeriodId create RefurbishmentLevelPeriod " + str(e))
                else:
                    return tuple(refurbishmentLevelPeriodList)    

            else:
                raise NoDataFoundException("No record found on table refurbishment_periods_levels for period_id:" + str(period_id) )



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveRefurbishmentLevelPeriodId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveRefurbishmentLevelPeriodId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
    
    
    def retrieveSHPInputFields(self):
        
        """ 
             Retrieve database mapping fields among the input shape and plugin process
            :returns:  List of all active process fields
            :raises NoDataFoundException: Not found data in table for mapping users field with process fields
        """
        
        try:
            shpInputFieldsList= []
            statement = """SELECT  id,calculateModel,fieldState,fieldName,
                                   format,length,precision, user_format_match
                           FROM shp_map_csv_input_fields as fields 
                           WHERE  fields.active = 1
                           ORDER BY id;"""
            
            totalRegs, data_table = self.executeStatementAll(statement)
            
            if data_table:
                for data in data_table:
                    try:
                        shpInputFields = ShpCsvInputFields()
                        shpInputFields.id = int(data[0])
                        shpInputFields.calculateModel = data[1]
                        shpInputFields.fieldState = data[2]
                        shpInputFields.fieldName = data[3]
                        shpInputFields.format = data[4]
                        shpInputFields.length = None if data[5] is None else int(data[5]) 
                        shpInputFields.precision = None if data[6] is None else int(data[6])
                        shpInputFields.user_format_match = data[7] 
                        
                        
                        shpInputFieldsList.append(shpInputFields)
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveSHPInputFields create shpInputFields " + str(e)) 
                else:
                    return tuple(shpInputFieldsList)
            else:    
                raise NoDataFoundException("No record found on table shp_map_csv_input_fields")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveSHPInputFields " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "retrieveSHPInputFields Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
    
    
    def retrieveProtectionLevels(self):
        
        """ 
             Retrieve database mapping protection degree
            :returns:  List of all active protection levels
            :raises NoDataFoundException: Not found active data in table protection_level 
        """
        
        
        try:
            protectionLevelsList= []
            statement = """SELECT  pl.id,pl.protection_level, pl.roof, pl.wall, pl.window,pl.description
                           FROM protection_level as pl 
                           WHERE  pl.active = 1
                           ORDER BY id;"""
            
            totalRegs, data_table = self.executeStatementAll(statement)
            
            if data_table:
                for data in data_table:
                    try:
                        protectionLevel = ProtectionLevel()
                        protectionLevel.id              = int(data[0])
                        protectionLevel.protectionLevel = int(data[1])
                        protectionLevel.roof            = data[2]
                        protectionLevel.wall            = data[3]
                        protectionLevel.window          = data[4]
                        protectionLevel.description     = data[5]
                        
                        protectionLevelsList.append(protectionLevel)
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveProtectionLevels create protectionLevel " + str(e)) 
                else:
                    return protectionLevelsList
            else:    
                raise NoDataFoundException("No record found on table protection_level")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveProtectionLevels " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "retrieveProtectionLevels Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
        
        
    def retrieveCountryById(self,id_country):
        """ 
             Retrieve country object, for country id 
            :param name int: id of country
            :returns: Mapped table object, country 
            :raises NoDataFoundException: Not found data in table for active country id given
        """
        try:
            statement = """SELECT  country.id, country.country, 
                           country.heating_base, country.cooling_base
                           FROM country as country 
                           WHERE active = 1 AND  country.id = :id_country;"""

            bindvars = {'id_country':id_country}

            data = self.executeStatement(statement,bindvars)

            if data:
                country_demand = Country()
                country_demand.id = data[0]
                country_demand.country = data[1]
                country_demand.heating_base = data[2]
                country_demand.cooling_base = data[3]
                
                return country_demand
            else:
                raise NoDataFoundException("No record found on table country")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCountryById " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCountryById Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
    
    
    def retrieveCSVInterimFields(self,calculateModel):
        """ 
             Retrieve CSV internal process data fields 
            :param calulateModel str: Complete or Simplified
            :returns: list of fields 
            :raises NoDataFoundException: Not found data in table csv_interim_input_fields
        """
        try:
            
            inputFields_list = []
            statement = """SELECT id, calculateModel, headerName, attributeName, format, length, precision 
                          FROM csv_interim_input_fields 
                          WHERE active = 1 AND calculateModel IN ("Both",:calculateModel)
                          ORDER BY position;
                        """ 
                        
                        

            bindvars={'calculateModel':calculateModel}
            totalRegs, data_table = self.executeStatementAll(statement,bindvars)
            
            if data_table:
                for data in data_table:
                    try:
                        inputFields = CsvInterimInputFields()
                        inputFields.id              = int(data[0])
                        inputFields.calculateModel  = data[1]
                        inputFields.headerName      = data[2]
                        inputFields.attributeName   = data[3]
                        inputFields.format          = data[4]
                        inputFields.length          = None if data[5] is None else int(data[5])         
                        inputFields.precision       = None if data[6] is None else int(data[6])         
              
                        
                        inputFields_list.append(inputFields)
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveCSVInterimFields create CsvInterimInputFields " + str(e)) 
                else:

                    return tuple(inputFields_list)

            
            else:
                raise NoDataFoundException("No record found on table csv_interim_input_fields")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCSVInterimFields " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCSVInterimFields Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        
        
    def retrieveOutputFields(self,scenario,fileType,fileCategory,calculateModel):
        
        """ 
             Retrieve database output fields
            :param fileType: Detail / Hourly / Totalized
            :param fileCategory:CSV / SHAPE
            :param calculateModel: Complete/Simplified
            :returns:  List of all active fields
            :raises NoDataFoundException: Not found data in table csv_shp_output_fields
        """
        
        try:
            
            outputFields_list = []
            statement = """SELECT id,TRIM(scenario), TRIM(fileCategory), TRIM(fileType), TRIM(calculateModel), TRIM(headerName), TRIM(attributeName), 
                                  format, length, precision 
                           FROM  csv_shp_output_fields
                           WHERE active = 1 AND  scenario IN ('Both', :scenario) AND fileType =:fileType AND fileCategory IN ('Both', :fileCategory) AND  calculateModel IN  ("Both",:calculateModel)
                           ORDER BY position ASC;
                        """ 

            bindvars={'scenario':scenario,'fileCategory':fileCategory,'fileType':fileType,'calculateModel':calculateModel}
            
            totalRegs, data_table = self.executeStatementAll(statement,bindvars)
            
            if data_table:
                for data in data_table:
                    try:
                        outputFields = CsvShpOutputFields()
                        outputFields.id              = int(data[0])
                        outputFields.scenario  = data[1]
                        outputFields.Category  = data[2]
                        outputFields.fileType  = data[3]
                        outputFields.calculateModel  = data[4]
                        outputFields.headerName      = data[5]
                        outputFields.attributeName   = data[6]
                        outputFields.format          = "str" if data[7] is None else data[7]
                        outputFields.length          = None if data[8] is None else int(data[8])         
                        outputFields.precision       = None if data[9] is None else int(data[9])         
              
                        
                        outputFields_list.append(outputFields)
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "DB retrieveOutputFields create CsvShpOutputFields " + str(e)) 
                else:

                    return outputFields_list

            
            else:
                raise NoDataFoundException("No record found on table csv_shp_output_fields")

        except NoDataFoundException as e:
            self.__log.write_log("WARNING", " DB retrieveOutputFields " + str(e))
            self.__log.write_log("WARNING", "statement: " + statement)
            if bindvars:
                self.__log.write_log("WARNING", "bindvars: " + str(bindvars))
           

        except:
            self.__log.write_log("ERROR", "DB retrieveOutputFields Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        
        
    
    
    def retrieveCompleteScheduledAll(self,buildingUses,district_temperature):
        """ 
             Retrieve database scheduled for complete calculate method 
            :param buildingUses: Uses of the buildings 
            :param district_temperature: Noa District Temperature
            :returns : Dict with list of Hourly scheduled data for building_use_id 
        """
        try:

            scheduledDict = {}
            
            for buildingUse in buildingUses:
                    scheduled = self.retrieveCompleteScheduledBydUseId(buildingUse.id,district_temperature)
                    if scheduled:
                        scheduledDict[buildingUse.use] = scheduled 
            
      
            return scheduledDict
            
        except:
            self.__log.write_log("ERROR", "DB retrieveCompleteScheduledAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        
        
    
    def retrieveCompleteScheduledBydUseId(self,building_use_id,district_temperature):
        
        """ 
             Retrieve database scheduled for complete calculate method 
            :param building_use_id: Id Use of the building 
            :param district_temperature: Noa District Temperature
            :returns : List of Hourly scheduled data for building_use_id 
            :raises NoDataFoundException: Not found data in table complete_scheduled
        """
        
        try:
            
            SummationDHWFactor      = 0.0 
            scheduled_list = []
            statement = """SELECT scheduled.id,scheduled.dayofyear,scheduled.hourofday,scheduled.season,
                           scheduled.building_use_id, use.use,scheduled.heating,scheduled.cooling,scheduled.lighting,
                           scheduled.equipment, scheduled.occupancy,scheduled.DHW
                           FROM complete_scheduled as scheduled inner join  building_use as use ON use.id = scheduled.building_use_id
                           WHERE use.id = :building_use_id AND use.active = 1
                           ORDER BY scheduled.building_use_id, scheduled.dayofyear, scheduled.hourofday;"""

            bindvars = {'building_use_id':building_use_id}

            

            totalRegs, data_table = self.executeStatementAll(statement,bindvars)
            
            if totalRegs == len(district_temperature): 
                 
                if data_table:
                    for i, data in enumerate(data_table):
                        try:
                            scheduled_demand = CompleteScheduled()
                            scheduled_demand.id             = int(data[0])
                            scheduled_demand.dayOfYear      = int(data[1])
                            scheduled_demand.hourOfDay      = int(data[2])
                            scheduled_demand.season         = data[3]
                            scheduled_demand.avg_temp       = district_temperature[i]
                            scheduled_demand.building_use_id= int(data[4])
                            scheduled_demand.building_use   = data[5]
                            scheduled_demand.heating        = data[6]
                            scheduled_demand.cooling        = data[7]
                            scheduled_demand.lighting       = data[8]
                            scheduled_demand.equipment      = data[9]
                            scheduled_demand.occupancy      = data[10]
                            scheduled_demand.DHW            = data[11]
                            
                            SummationDHWFactor              += scheduled_demand.DHW  
                            
                            
                            scheduled_list.append(scheduled_demand)
                        except Exception as e:
                            self.__log.write_log("ERROR", "DB retrieveCompleteScheduledBydUseId create CompleteScheduled" + str(e)) 
                    else:    
                        
                        for item in scheduled_list:
                            item.DHW_total_annual = SummationDHWFactor
                        
                        return tuple(scheduled_list)
                else:
                    raise NoDataFoundException("No record found on table complete_scheduled  for building_use_id:" + str(building_use_id) )
            else:
                self.__log.write_log("ERROR", "DB retrieveCompleteScheduledBydUseId NOA avg_temp {} not corresponding with complete_scheduled tuples {}".format(len(district_temperature),totalRegs)  )     

                 

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "DB retrieveCompleteScheduledBydUseId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "DB retrieveCompleteScheduledBydUseId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        
   
    
    def retrieveAlternativeScheduledResidential(self,residential):
        """ 
            Retrieve database scheduled for Simplified calculate method  
            :param residential: True or False 
            :returns : List of Hourly scheduled data   
            :raises NoDataFoundException: Not found data in table alternative_scheduled
        """
        
        try:
            scheduled_list = []
            
            SummationHeatingFactor  = 0.0
            SummationCoolingFactor  = 0.0
            SummationDHWFactor      = 0.0   
            
            statement = """SELECT scheduled.id,scheduled.dayofyear,scheduled.hourofday,
                           scheduled.season,scheduled.heating,scheduled.cooling,scheduled.DHW
                           FROM alternative_scheduled as scheduled
                           WHERE residential = :residential 
                           ORDER BY scheduled.dayofyear, scheduled.hourofday;"""
            
            bindvars = {'residential':int(residential)}
            
            totalRegs, data_table = self.executeStatementAll(statement,bindvars)
            
            if data_table:
                for i, data in enumerate(data_table):
                    try:
                        scheduled_demand = AlternativeScheduled()
                        scheduled_demand.id             = int(data[0])
                        scheduled_demand.dayOfYear      = int(data[1])
                        scheduled_demand.hourOfDay      = int(data[2])
                        scheduled_demand.season         = data[3]
                        scheduled_demand.heating        = data[4]
                        scheduled_demand.cooling        = data[5]
                        scheduled_demand.DHW            = data[6]
                        
                        
                        SummationHeatingFactor  += scheduled_demand.heating
                        SummationCoolingFactor  += scheduled_demand.cooling
                        SummationDHWFactor      += scheduled_demand.DHW   
                        
                        scheduled_list.append(scheduled_demand)
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "DB retrieveAlternativeScheduledResidential create AlternativeScheduled" + str(e)) 
                else:
                    
                 
                    #Calculate Normalized Usage Factor NUF
                    for item in scheduled_list:
                        item.heating_nuf = item.heating / SummationHeatingFactor
                        item.cooling_nuf = item.cooling / SummationCoolingFactor
                        item.DHW_nuf     = item.DHW / SummationDHWFactor
                        
                        
                        
                    return scheduled_list
            else:
                raise NoDataFoundException("No record found on table alternative_scheduled ")
        
        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "DB retrieveAlternativeScheduledResidential " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "DB retrieveAlternativeScheduledResidential Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
    
    
    def retrieveAvgLocationTemperature(self,location_id):
        """ 
            Retrieve database scheduled for Simplified calculate method  
            :param location_id: country or city selected for calculation  
            :returns : List of Hourly avg temperature data for given location_id    
            :raises NoDataFoundException: Not found data in table location_avg_temp
        """
        
        try:
            avg_temperature_list = []
            
            statement = """SELECT loc_temperature.id,loc_temperature.dayofyear,loc_temperature.hourofday,
                           loc_temperature.season,loc_temperature.location_id, loc_temperature.temperature
                           FROM location_avg_temperature as loc_temperature
                           WHERE loc_temperature.location_id = :location_id 
                           ORDER BY loc_temperature.dayofyear, loc_temperature.hourofday;"""
            
            bindvars = {'location_id':location_id}
            
            totalRegs, data_table = self.executeStatementAll(statement,bindvars)
            
            if data_table:
                for data in data_table:
                    try:
                        locationAvgTemp = LocationAvgTemperature()
                        locationAvgTemp.id             = int(data[0])
                        locationAvgTemp.dayOfYear      = int(data[1])
                        locationAvgTemp.hourOfDay      = int(data[2])
                        locationAvgTemp.season         = data[3]
                        locationAvgTemp.location_id    = int(data[4])
                        locationAvgTemp.temperature    = data[5]
                     
                        
                        avg_temperature_list.append(locationAvgTemp)
                        
                    except Exception as e:
                        self.__log.write_log("ERROR", "DB retrieveAvgLocationTemperature create LocationAvgTemperature" + str(e)) 
                else:
                    
                        
                    return avg_temperature_list
            else:
                raise NoDataFoundException("No record found on table location_avg_temperature ")
        
        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "DB retrieveAvgLocationTemperature " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "DB retrieveAvgLocationTemperature Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
      
    