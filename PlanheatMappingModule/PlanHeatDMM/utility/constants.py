# -*- coding: utf-8 -*-
"""
   Application Constants, Defualt Values
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 14 Sep. 2017
"""

__docformat__ = "restructuredtext"


SCENARIO_NAME    = "PlanHeat"
SCENARIO_VERSION = 15

CONFIG_FILE_PATH="/config/"
CONFIG_FILE_NAME="PlanHeat.cfg"


TEMP_DIR_PATH="temp"
LOG_DIR_PATH ="log"


LOG_LEVELS={"CRITICAL":50,
            "ERROR":40,
            "WARNING":30,
            "INFO":20,
            "DEBUG":10,
            "NOTSET":0}

DB_PARAMS = {"databaseName" : "PlanHeat.db",
             "path" : "/db/"
             }

LOG_PARAMS = {"logName" : "PlanHeat",
              "logExt" : "log",
              "loggingLevel": LOG_LEVELS["INFO"],   
              "path" : "/log/"}

JAR_FILE_PARAMS= {"jarFileName" : "llamada.jar", "path" : "/java/"}

JAVA_MAIN_CLASS="tecnalia.geoprocess.PerformProcess"

INTERMEDIATE_FILE_CSV="xmlResultado.csv" 

USE_NOA_DATA="Y"

NOA_URL = "http://snf-652558.vm.okeanos.grnet.gr/planheat/proxy.php?action=getCHEntities"

EPSG_URL = "http://prj2epsg.org/search.json"

 
#NOA HTTP API Rest Response Codes  
HTTP_RESPONSE_OK=200
NOA_TIMEOUT=30 #30 Seconds

HOURS_PER_YEAR=8760
RAW_FILES_TTL = 86400     # 1 days seconds
DAYS_REMOVE_OLD_LOGS=3

DECIMAL_POINT_IS_COMMA="Y"
LIDAR_FILE_EXT="asc"

# SHAPE Constants
SHAPE_TYPE_FILE={"0":'NULL',"1":'POINT',"3":'POLYLINE',"5":'POLYGON',"8":'MULTIPOINT',"11":'POINTZ',"13":'POLYLINEZ',"15":'POLYGONZ',"18":'MULTIPOINTZ',"21":'POINTM', \
                 "23":'POLYLINEM',"25":'POLYGONM',"28":'MULTIPOINTM',"31":'MULTIPATCH'}


PROCESS_THREAD_PRIORITY=7   # use the same priority as the creating thread. This is the default.

PROCESS_WAIT_TO_KILL=5 # Seconds Waiting for terminate the Thread

USE_PERSIST_SCENARIO = "Y"
LAUNCH_JAVA_PROCESS = "Y"
OPTIONS_FILE = "N"
