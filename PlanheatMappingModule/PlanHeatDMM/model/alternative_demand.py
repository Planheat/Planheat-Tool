# -*- coding: utf-8 -*-
"""
   Model Map table alternative_demand_database   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 14 Sep. 2017
"""
__docformat__ = "restructuredtext"

import sys
class AlternativeDemand():
    
    """ DB Entity alternative_demand_database to Python object AlternativeDemand  """

    def __init__(self,log, param):
        '''
        Constructor
        '''
        try:
            self.__log = log
            self.__param = param
            self.__id         = int(param[0])
            self.__id_country = int(param[1])
            self.__residential_kwhm2  = float(param[2].replace(",","."))  if isinstance(param[2],( str)) else float(param[2])
            self.__service_kwhm2      = float(param[3].replace(",","."))  if isinstance(param[3],( str)) else float(param[3])
        except:
            self.__log.write_log("ERROR", "AlternativeDemand __init__ Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
             
   
    def __str__(self):      
        return "id:" + str(self.id) + " id country:" + str(self.id_country) + " residential_kwhm2:" + str(self.residential_kwhm2) + " service_kwhm2:" + str(self.service_kwhm2) 
        
   
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, val):
        self.__id = val
 
    
    @property
    def id_country(self):
        return self.__id_country
    
    @id_country.setter
    def id_country(self, val):
        self.__id_country = val
    
    
    @property
    def country(self):
        return self.__country
    
    @country.setter
    def country(self, val):
        self.__country = val       
    
        
    @property
    def residential_kwhm2(self):
        return self.__residential_kwhm2
    
    @residential_kwhm2.setter
    def residential_kwhm2(self, val):
        self.__residential_kwhm2 = float(val.replace(",","."))  if isinstance(val,(str)) else float(val)
    
        
    @property
    def service_kwhm2(self):
        return self.__service_kwhm2
    
    @service_kwhm2.setter
    def service_kwhm2(self, val):
        self.__service_kwhm2 = float(val.replace(",","."))  if isinstance(val,(str)) else float(val)            
                    
        
