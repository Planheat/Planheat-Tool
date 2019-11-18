# -*- coding: utf-8 -*-
"""
   Spatial Georeference API
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 20 sep. 2017
"""

__docformat__ = "restructuredtext"


import sys
import os
import json
import osr
import gdal
from config import config as Config
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError,HTTPError
from socket import timeout
from manageLog.log import Log




class SpatialReference():
    """ API for get the spatial geospatial reference for given EPSG  """


    def __init__(self,log,fileName):
        """
        Constructor
        
        :param log: logger object
        :param filename: Work file name
        
        """        
        self.__url =  Config.EPSG_URL
        self.__log=log
        self.fileName = fileName
        self.prjFileName = None
        
        self.spatialReferenceWKT = None
        self.spatialReferenceEPSG = None
        
        self.response = None
        self.jsondata = None
        
        

    def checkSpatialReference(self):
        """ Obtain EPSG and WKT from prj file 
            :returns:Status Result   
        """
        try:
            code = 0
            file_name_no_extension = os.path.splitext(self.fileName)[0]
            
            
            self.prjFileName = file_name_no_extension + ".prj"
            
            
            if os.path.isfile(self.prjFileName):
                fp = open(self.prjFileName, 'r') 
                self.__log.write_log("INFO", "checkSpatialReference read spatial reference file {}.prj".format(file_name_no_extension))
                
                with fp:
                    self.spatialReferenceWKT = fp.read()
                
                    code =  self.osrGetSpatialReference(self.spatialReferenceWKT) 
                    
                    if self.spatialReferenceEPSG is None:
                        code = self.callRestApi()
                    
                    if self.spatialReferenceEPSG is not None:
                        self.__log.write_log("INFO","Spatial reference EPSG:" + self.spatialReferenceEPSG)
                        return 0
                    else:
                        self.__log.write_log("WARNING","Spatial reference EPSG is None Value")
                        self.spatialReferenceEPSG = None 
                        self.spatialReferenceWKT = None
                        return code
                        
            else:
                self.__log.write_log("WARNING","checkSpatialReference read spatial reference file {}.prj not found".format(file_name_no_extension))  
                return -1          
                
        except Exception as e:    
            self.__log.write_log("ERROR", "checkSpatialReference " + str(e))
            return -1    
            
        
 
    def callRestApi(self):
        """ Obtain EPSG from WKT over internet 
            :returns: Status Result   
            :raises HTTPError: Server rejects request
            :raises URLError: Invalid Url
            :raises timeout: Time out Exception
        """
        try:
            query = urlencode({
                    'exact': True,
                    'error': True,
                    'mode': 'wkt',
                    'terms': self.spatialReferenceWKT})
    
            self.response = urlopen(self.__url, query.encode(),20)
            self.jsondata = json.loads(self.response.read().decode())
            
            if self.response.status == Config.HTTP_RESPONSE_OK:
                if self.jsondata.get('codes'):
                    self.spatialReferenceEPSG = self.jsondata ['codes'][0]['code']
                    return 0
                else: 
                    self.__log.write_log("WARNING", "prj2epsg Web Service Message" + str(self.jsondata.get('errors','')))
                    return -2
            else:
                self.__log.write_log("ERROR", "Server Response Status Code:" + str(self.response.status))
                return -3
             
                  
        except (HTTPError, URLError):
            self.__log.write_log("ERROR", "Call prj2epsg service HTTP/URL  Unexpected error " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return -4   
        
        except timeout:
            self.__log.write_log("ERROR", "Call prj2epsg service timeOut Exception Unexpected error " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return -5   

        except:   
            self.__log.write_log("ERROR", "Call prj2epsg service  Unexpected error " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return -6   
           

    
    def osrGetSpatialReference(self, prj_text):
        """ Obtain EPSG from WKT over osr
            :param prj_text str: WKT data
            :returns: Status Result    
        """
        try:
            gdal.UseExceptions() 
            srs = osr.SpatialReference()
            srs.ImportFromESRI([prj_text])
            srs.AutoIdentifyEPSG()
            
            #print ("Shape prj is: {}".format(prj_text))
            #print ("WKT  is: {}".format(srs.ExportToWkt()))
            #print ("WKT  is: {}".format(srs.ExportToPrettyWkt()))
            #print ("Proj4  is: {}".format(srs.ExportToProj4()))
            #print ("srs  is: {}".format(srs.GetAuthorityCode(None)))
           
            self.spatialReferenceEPSG = srs.GetAuthorityCode(None)
            
            gdal.DontUseExceptions()
            if self.spatialReferenceEPSG is None:
                return -2                  
            else:
                return 0
        
        except Exception:
            self.__log.write_log("ERROR", "osrSpatialReference  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return -2       
     
        
    def osrGenerateSpatialReference(self,EPSG ):
        """
            Generate WKT from EPSG over osr
            :param EPSG int: EPSG code
            :returns: Status Result    
        """
        
        try:
            
            gdal.UseExceptions() 
            srs = osr.SpatialReference()
            
            srs.ImportFromEPSG(EPSG)
            
            self.spatialReferenceWKT =  srs.ExportToWkt()
            
            if self.spatialReferenceWKT:
                
                prjOut = open(self.prjFileName, "w")
                prjOut.writelines(self.spatialReferenceWKT)
                prjOut.close()

             
            #print ("WKT  is: {}".format(srs.ExportToWkt()))
            #print ("WKT  is: {}".format(srs.ExportToPrettyWkt()))
            #print ("Proj4  is: {}".format(srs.ExportToProj4()))
            #print ("srs  is: {}".format(srs.GetAuthorityCode(None)))
            
           
            self.spatialReferenceEPSG = srs.GetAuthorityCode(None)
            
            gdal.DontUseExceptions()
            
            if self.spatialReferenceEPSG is None:
                return -2                  
            else:
                return 0
        
        except Exception as e:
            self.__log.write_log("ERROR", "osrSpatialReference  unexpected error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return -2           
          
          
          
# Test Case   
if __name__ == '__main__':
    
    log = Log("D:\\Users\\E17004\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\PlanHeatDMM\\log\\","prueba.log")
    #spatial = SpatialReferenceWeb(log,  'D:/PlanHeatDatos/Resultado_v3_3057.prj')
    #EPSG = spatial.call()
    #print(EPSG)
    spatial = SpatialReference(log,  'D:/PlanHeatDatos/Resultado_v3_3057.prj')
    spatial.osrGenerateSpatialReference(-20)
    
    
    pass