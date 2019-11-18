# -*- coding: utf-8 -*-
"""
   NOA Connection API
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 20 sep. 2017
"""

__docformat__ = "restructuredtext"


import sys
import json
import requests
from config import config as Config
from manageLog.log import Log
from myExceptions.exceptions import NOANoDataFoundException 





class Noa():
    """ 
        API NOA Connection
        
        Retrieve hourly average temperature for a latitude and longitude from the district  
    
    """ 


    def __init__(self,log):
        """
        Constructor
        
        :param log: logger object
        
        """     
        self.url =  Config.NOA_URL
        self.__log=log
        self.lng=None
        self.lat=None
        self.response = None
        
 
    def call(self,latitude,longitude):
        
        """
            Call to API Rest from NOA with JSON format
            :param latitude float: Decimal representation for y axis
            :param longitude float:Decimal representation for x axis 
            :returns: list with district year temperature hourly
            :raises ConnectionError: The server rejects the request  or connection is not possible
            :raises Timeout: Time out exception
        """
        
        try:
            dataAvgTemp=[]
            self.lat=latitude
            self.lng=longitude
            
            data = json.dumps({'lng':self.lng,'lat':self.lat})
            self.response = requests.post(self.url,data=data,timeout=Config.NOA_TIMEOUT)
            
            
            if self.response.status_code == Config.HTTP_RESPONSE_OK:  
                #Return Api control
                noaDataResponse = self.response.json()
                status = noaDataResponse.get('status')
                message = noaDataResponse.get('message')
                dataAvgTemp = noaDataResponse.get('data')
                
                if status != Config.HTTP_RESPONSE_OK:
                    raise NOANoDataFoundException("Error code:{:d} message:{} ".format(status,message))
                
                return dataAvgTemp    
            else:    
                raise NOANoDataFoundException("http response code:" + str(self.response.status_code))  
                
        
        except requests.ConnectionError as e:
            message = str(e)  
            self.__log.write_log("ERROR", "call NOA Service Exception ConnectionError " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "call NOA Service " + str(e))
            raise NOANoDataFoundException(message)
            
        except requests.Timeout as e:
            message = str(e)
            self.__log.write_log("ERROR", "call NOA Service Exception Timeout " + str(Config.NOA_TIMEOUT) + " seconds ");
            self.__log.write_log("ERROR", "call NOA Service " + str(e))
            raise NOANoDataFoundException(message)
        
        except NOANoDataFoundException as e:
            message = "{}\nNot found data for lat:{:f} and longitude:{:f}".format(e,self.lat,self.lng)  
            self.__log.write_log("ERROR", "call  NOA Service Error: " + str(e))
            self.__log.write_log("ERROR", "call  NOA Service not found data for lat:" + str(self.lat) + " and longitude: " + str(self.lng))
            raise NOANoDataFoundException(message)
        
        except:   
            message = str(e)
            self.__log.write_log("ERROR", "Call NOA service  Unexpected error " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))   
            raise NOANoDataFoundException(message)
           

    
    def connectionAvailability(self):
        """
            Checking for the rest availability
            :returns: True or False
            :raises ConnectionError: The server rejects the request  or connection is not possible
            :raises Timeout: Time out exception
        """
        
        check = False
        try:
            self.response = requests.post(self.url,timeout=Config.NOA_TIMEOUT)

            if self.response.status_code != Config.HTTP_RESPONSE_OK:
                check = False
                self.__log.write_log("ERROR", "ConnectionAvailability  NOA Error Response Code:" + str(self.response.status_code))
            else:
                self.__log.write_log("INFO", "ConnectionAvailability  NOA Service Connection OK ")    
                check = True     
                
                    
        except requests.ConnectionError as e:
            self.__log.write_log("ERROR", "ConnectionAvailability  Exception ConnectionError")
            self.__log.write_log("ERROR", "ConnectionAvailability " + str(e))
            check = False
            
        except requests.Timeout as e:
            self.__log.write_log("ERROR", "ConnectionAvailability NOA Service Exception Timeout " + str(Config.NOA_TIMEOUT) + " seconds ");
            self.__log.write_log("ERROR", "ConnectionAvailability NOA Service " + str(e))
            check = False    
        
        except:   
            self.__log.write_log("ERROR", "ConnectionAvailability  Unexpected error " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))   
            check = False

        finally:
            return check
          
          
          
# Test Case   
if __name__ == '__main__':
    
    log = Log()
    # Paris 48.861051,2.335792 
    #Oslo 59.8597,10.8675
    #Antwerp 51.221 4.4007
    # Velika-Gorica 45.71079 16.0647

    latitude  = 51.21827574292595
    longitude = 4.40101513153253
    noa = Noa(log)
    noa.connectionAvailability()
    noa.call(latitude,longitude)
    pass