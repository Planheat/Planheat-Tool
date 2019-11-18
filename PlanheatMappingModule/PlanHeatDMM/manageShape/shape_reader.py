# -*- coding: utf-8 -*-
"""
   Shape Files Read API   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 21 sept. 2017
"""
__docformat__ = "restructuredtext"  

import sys
import externModules.shapefile as shp
from manageLog.log import Log
from myExceptions.exceptions import ShapeFileFormatException
from config import config as Config 




class Shape_Reader():
    """ API for read input SHAPE file
     
        Read file and extract data to necessary format for the process   
    """  


    def __init__(self, log, filename):
        """
        Constructor
        
        :param log: logger object
        :param filename: Work file name
        
        """        
        self.filename = filename
        
        #self.spatialReferenceEPSG    = None
        #self.spatialReferenceWKT = None
        
        self.geometryAndRecordBuilding=list()
        self.geometryAndRecordBuildingIndex={}
        self.recordBuilding=list()
        self.shapesBuilding=list()
        
        self.__log=log
        self.header_record = []
        
        
    def readShapeFile(self,read="all"):    
        """
        Read File and retrieve records and geometry 
        :raises ShapeFileFormatException: Shape file has a wrong structure, not Polygon
        """        
         
        try:
            sf = shp.Reader(self.filename,encoding='utf-8')
            self.__log.write_log("INFO", "readShapeFile " + self.filename)    
            # File with Polygon Geometry
            if sf.shapeType == shp.POLYGON:
                
                self.header_record = sf.fields[1:]
                
                if read.lower() in("records"):
                    self.recordBuilding = sf.records()
                elif read.lower() in("shapes"):
                    self.shapesBuilding = sf.shapes()
                else:
                    self.geometryAndRecordBuilding = sf.shapeRecords() # Read records and Geometry
                
                    
            else:
                raise ShapeFileFormatException("Shape File Geometry " +  Config.SHAPE_TYPE_FILE.get(sf.shapeType) + " Expected:" + str(Config.SHAPE_TYPE_FILE[5]))
             
            
            
        except ShapeFileFormatException as e:
            self.__log.write_log("ERROR", "readShapeFile " + e)
            raise    
            
        except:    
            self.__log.write_log("ERROR", "readShapeFile  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise 
            
    
                       
    def readShapeFileHeaderFields(self):    
        """
        Read File and retrieve headers  
        :raises ShapeFileFormatException: Shape file has a wrong structure, not Polygon
        """        
         

        try:
            
            sf = shp.Reader(self.filename,encoding='utf-8')
            self.__log.write_log("INFO", "readShapeFileHeaderFields " + self.filename)    
            # File with Polygon Geometry
            if sf.shapeType == shp.POLYGON:
                self.header_record = sf.fields[1:]
                
            else:
                raise ShapeFileFormatException("Shape File Geometry " +  Config.SHAPE_TYPE_FILE.get(sf.shapeType) + " Expected:" + str(Config.SHAPE_TYPE_FILE[5]))
            
        except ShapeFileFormatException as e:
            self.__log.write_log("ERROR", "readShapeFileHeaderFields " + e)
            
            raise    
            
        except Exception as e:
            self.__log.write_log("ERROR", "readShapeFileHeaderFields  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise                   
    
    
    def createGeometryIndex(self,position_field_map):
        try: 
            building_id_position = position_field_map['BuildingID']
            for x, shapeRec in enumerate(self.geometryAndRecordBuilding):
                self.geometryAndRecordBuildingIndex[str(shapeRec.record[building_id_position])]=x
            
            if len(self.geometryAndRecordBuilding) != len(self.geometryAndRecordBuildingIndex):
                raise Exception("building identifier contains duplicated values, the value must be unique")
                 
        except Exception as e:
            self.__log.write_log("ERROR", "createGeometryIndex  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise                   
    
# Test Case            
if __name__ == '__main__':
    
    paramsShapeIn = dict()
    
    paramsShapeIn["path"]="D:/Users/E17004/Desktop/amberes/02-PREPROCESADO\PreProcesado_IPF_Edificios/ORIGEN/"
    paramsShapeIn["filename"]="GRB_hist.shp"
    filename =paramsShapeIn["path"] + paramsShapeIn["filename"]  
    
    log = Log()
    inputShpFile =  Shape_Reader(log, filename)
    inputShpFile.readShapeFile()
    inputShpFile.osrSpatialReference('D:/PlanHeatDatos/Resultado_v3_3057.prj')
    pass        