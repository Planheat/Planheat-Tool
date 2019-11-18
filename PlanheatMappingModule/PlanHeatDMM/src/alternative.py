# -*- coding: utf-8 -*-
"""
   Simplified Calculation Algorithm
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 15 sep. 2017
"""

__docformat__ = "restructuredtext"

import sys
from model.alternative_demand import AlternativeDemand
from model.alternative_built_surface import AlternativeBuiltSurface
from model.alternative_other_distribution import AlternativeOtherDistribution
from model.alternative_consumption_distribution import AlternativeConsumptionDistribution
from model.totalized_demand import TotalizedDemand
from model.hourly_demand import HourlyDemand
from myExceptions.exceptions import  NoDataFoundException, DataValueNoneException, ZeroValueException, WrongValueException




class Alternative():
    """
     Alternative Object for simplified calculation method 
    """

    def __init__(self, log, database,country_id,boolRetrofittedScenarios,planHeatDMM):

        '''
        Constructor
        '''
        self.name = "Simplified"
        self.__log = log
        self.__db = database
        self.__planHeatDMM = planHeatDMM
        self.__boolRetrofittedScenarios = boolRetrofittedScenarios
        
        self.__refurbishmentSimplifiedData = self.__planHeatDMM.data.refurbishmentSimplifiedData
        
        
        
        self.scheduledResidentialList = list()
        self.scheduledNonResidentialList = list()
        
        self.country_demand = None
        self.builtSurface = None
        self.peakConsumption = None
        self.otherDistributionResidential = None
        self.otherDistributionNonResidential = None
        self.consumptionDistributionResidential = None
        self.consumptionDistributionNonResidential = None
        
        self.country = None
        self.country_name = None
        self.countryID  = country_id
        
        self.baselineTotalizedDemand = None
        self.futureTotalizedDemand   = None
        
        self.baselineTotalizedDemandList = []
        self.futureTotalizedDemandList = []

    def initialize(self):
        try:
            
            self.baselineTotalizedDemand = TotalizedDemand()
            self.futureTotalizedDemand   = TotalizedDemand()
            
            self.baselineTotalizedDemand.scenario = 'Baseline'
            self.futureTotalizedDemand.scenario   = 'Future'
                      
            self.inputFields              = self.retrieveCSVInterimFields("Alternative")
            
            #Baseline Fields
            self.outputBaselineDetailFieldsCsv    = self.retrieveOutputFields("Baseline", "Detail", "Csv","Alternative")
            self.outputBaselineTotalizedFieldsCsv = self.retrieveOutputFields("Baseline", "Totalized", "Csv","Alternative")
            self.outputBaselineHourlyFieldsCsv    = self.retrieveOutputFields("Baseline", "Hourly", "Csv","Alternative")
            self.outputBaselineDetailFieldsShape  = self.retrieveOutputFields("Baseline", "Detail", "Shp","Alternative")
            
            
            #Future Fields 
            self.outputFutureDetailFieldsCsv    = self.retrieveOutputFields("Future", "Detail", "Csv","Alternative")
            self.outputFutureTotalizedFieldsCsv = self.retrieveOutputFields("Future", "Totalized", "Csv","Alternative")
            self.outputFutureHourlyFieldsCsv    = self.retrieveOutputFields("Future", "Hourly", "Csv","Alternative")
            self.outputFutureDetailFieldsShape  = self.retrieveOutputFields("Future", "Detail", "Shp","Alternative")
            
            
            self.country_demand = self.retrieveAlternativeDemandByCountryId(self.countryID)
            self.country = self.retrieveCountryById(self.countryID)
            self.country_name = self.country.country
            
            
            
            #Retrieve scheduled list - Residential & Service     
            self.scheduledResidentialList    = self.retrieveAlternativeScheduled(residential=True)
            self.scheduledNonResidentialList = self.retrieveAlternativeScheduled(residential=False)
                    
            #Retrieve Other distribution data - Residential & Service
            self.otherDistributionResidential      = self.retrieveAlternativeOtherDistribution(residential=True)
            self.otherDistributionNonResidential   = self.retrieveAlternativeOtherDistribution(residential=False)
            
            #Retrieve Built data - Residential & Service
            self.builtSurface = self.retrieveAlternativeBuiltSurfaceByCountryId(self.countryID)
                     
            #Retrieve consumptions Distribution  list - Residential & Service
            self.consumptionDistributionResidential     = self.retrieveAlternativeConsumptionDistribution(self.countryID, residential=True)
            self.consumptionDistributionNonResidential  = self.retrieveAlternativeConsumptionDistribution(self.countryID,residential=False)

            
        except:
            self.__log.write_log("ERROR", "Simplified initialize Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise

            

    def calculateConsumption(self,building):
        try:
            if building.Regstatus:
                building.country = self.country_name 
                                      
                if not self.country or not self.country_demand or not self.builtSurface \
                   or not self.otherDistributionResidential or not self.otherDistributionNonResidential \
                   or not self.consumptionDistributionResidential or not self.consumptionDistributionNonResidential:
                    
                    noneMessage = ""
                    if not self.country: noneMessage = noneMessage + " - country is None or False"
                    if not self.country_demand: noneMessage = noneMessage + " - country_demand is None or False"
                    if not self.builtSurface: noneMessage = noneMessage + " - builtSurface is None or False"
                    if not self.otherDistributionResidential: noneMessage = noneMessage + " - otherDistributionResidential is None or False"
                    if not self.otherDistributionNonResidential: noneMessage = noneMessage + " - otherDistributionNonResidential is None or False"
                    if not self.consumptionDistributionResidential: noneMessage = noneMessage + " - consumptionDistributionResidential is None or False" 
                    if not self.consumptionDistributionNonResidential: noneMessage = noneMessage + " - consumptionDistributionNonResidential is None or False"
                    
                    raise DataValueNoneException("calculateConsumption value fields None " + noneMessage)
                
                else:
                    
                    self.calculateConsumptionDemand(building)
                  
                        
            return building
        
        except:
            self.__log.write_log("ERROR", "calculateConsumption Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            building.Regstatus = False
            return building
            
    
    
    def calculateConsumptionDemand(self,building):
        try:
            
            
            annualHeatingDemand = 0.0
            annualCoolingDemand = 0.0 
            annualDHWDemand     = 0.0
            annualHeatingDemandSqm = 0.0
            annualCoolingDemandSqm = 0.0 
            annualDHWDemandSqm     = 0.0  
            
            future_annualHeatingDemand = 0.0
            future_annualCoolingDemand = 0.0 
            future_annualDHWDemand     = 0.0
            future_annualHeatingDemandSqm = 0.0
            future_annualCoolingDemandSqm = 0.0 
            future_annualDHWDemandSqm     = 0.0  
            
            
            maximumHeatingDemand  = 0.0
            maximumCoolingDemand  = 0.0
            maximumDHWWaterDemand = 0.0
            
            future_maximumHeatingDemand  = 0.0
            future_maximumCoolingDemand  = 0.0
            future_maximumDHWWaterDemand = 0.0
            
            
            dataList = []
            dataFutureList = []
            
            if building.totalHeight < 3.0: 
                raise WrongValueException((" building_id:{} with totalHeight :{:f} meters , must be greater than 3.0").format(building.reference,building.totalHeight))
            elif building.numberOfFloors <= 0.0:
                raise ZeroValueException((" building_id:{} with numberOfFloors:{:f} ").format(building.reference,building.numberOfFloors))
            elif building.grossFloorArea <= 0.0:
                raise ZeroValueException((" building_id:{} with grossFloorArea:{:f} square meters").format(building.reference,building.grossFloorArea))
            
            schedResdidentialIter = iter(self.scheduledResidentialList)
            schedNonResdidentialIter = iter(self.scheduledNonResidentialList)
            
            residential_base_heating_demand = (self.builtSurface.residential_perc / 100.0) * self.country_demand.residential_kwhm2 * ( self.consumptionDistributionResidential.space_heating_perc / 100.0)  
            service_base_heating_demand =  (self.builtSurface.service_perc / 100.0) * self.country_demand.service_kwhm2 *  ( self.consumptionDistributionNonResidential.space_heating_perc / 100.0)
            
            residential_base_cooling_demand = (self.builtSurface.residential_perc / 100.0) * self.country_demand.residential_kwhm2 * ( (self.consumptionDistributionResidential.other_perc / 100.0) *  (self.otherDistributionResidential.space_cooling_perc / 100.0))
            service_base_cooling_demand =  (self.builtSurface.service_perc / 100.0) * self.country_demand.service_kwhm2 *   ( (self.consumptionDistributionNonResidential.other_perc / 100)  *  (self.otherDistributionNonResidential.space_cooling_perc / 100.0))
            
            residential_base_DHW_demand = (self.builtSurface.residential_perc / 100.0) * self.country_demand.residential_kwhm2 * ( self.consumptionDistributionResidential.water_heating_perc / 100.0)  
            service_base_DHW_demand =  (self.builtSurface.service_perc / 100.0) * self.country_demand.service_kwhm2 *  ( self.consumptionDistributionNonResidential.water_heating_perc / 100.0)

            try:
                while True:
                      
                    schedResdidential= next(schedResdidentialIter)
                    schedNonResdidential = next(schedNonResdidentialIter)
                    
                    #Baseline Calculation Algorithm
                    heating_demand = (residential_base_heating_demand * schedResdidential.heating_nuf + service_base_heating_demand * schedNonResdidential.heating_nuf) * building.grossFloorArea
                    cooling_demand = (residential_base_cooling_demand * schedResdidential.cooling_nuf + service_base_cooling_demand * schedNonResdidential.cooling_nuf) * building.grossFloorArea
                    DHW_demand     = (residential_base_DHW_demand     * schedResdidential.DHW_nuf     + service_base_DHW_demand     * schedNonResdidential.DHW_nuf)     * building.grossFloorArea

                  
                    if maximumHeatingDemand < heating_demand:
                        maximumHeatingDemand = heating_demand
                    
                    if maximumCoolingDemand < cooling_demand:
                        maximumCoolingDemand = cooling_demand
                    
                    if maximumDHWWaterDemand < DHW_demand:
                        maximumDHWWaterDemand = DHW_demand
                    
                        
                    annualHeatingDemand += heating_demand
                    annualCoolingDemand += cooling_demand 
                    annualDHWDemand     += DHW_demand
                    
                    #Future Calculation Algorithm
                    future_heatingDemand = heating_demand - ( heating_demand * (self.__refurbishmentSimplifiedData / 100.0)) #Percentage reduction
                    future_coolingDemand = cooling_demand 
                    future_DHWDemand     = DHW_demand    
                    
                    if future_maximumHeatingDemand < future_heatingDemand:
                        future_maximumHeatingDemand = future_heatingDemand
                    
                    if future_maximumCoolingDemand < future_coolingDemand:
                        future_maximumCoolingDemand = future_coolingDemand
                    
                    if future_maximumDHWWaterDemand < future_DHWDemand:
                        future_maximumDHWWaterDemand = future_DHWDemand
                    
                    future_annualHeatingDemand += future_heatingDemand
                    future_annualCoolingDemand += future_coolingDemand
                    future_annualDHWDemand     += future_DHWDemand
                      
                    #Baseline hourly data
                    data = HourlyDemand()

                    data.projectID  = building.projectID
                    data.reference  = building.reference
                    
                    data.dayOfYear = schedResdidential.dayOfYear
                    data.hourOfDay = schedResdidential.hourOfDay
                    data.season = schedResdidential.season
                    data.heating = heating_demand
                    data.cooling = cooling_demand
                    data.DHW     = DHW_demand
                    
                    dataList.append(data)
                    
                    if self.__boolRetrofittedScenarios:                
                        #Future hourly data
                        dataFuture = HourlyDemand()
                        
                        dataFuture.projectID  = building.projectID
                        dataFuture.reference  = building.reference
                        
                        dataFuture.dayOfYear = schedResdidential.dayOfYear
                        dataFuture.hourOfDay = schedResdidential.hourOfDay
                        dataFuture.season    = schedResdidential.season
                        dataFuture.heating = future_heatingDemand
                        dataFuture.cooling = future_coolingDemand
                        dataFuture.DHW     = future_DHWDemand
                        
                        
                        dataFutureList.append(dataFuture)
                          
                #print("heating_demand:",heating_demand," cooling_demand:",cooling_demand," DHW demand:", DHW_demand)
                    
                    
            except StopIteration:
                pass #End of while
            
            
            annualHeatingDemandSqm = annualHeatingDemand / building.grossFloorArea 
            annualCoolingDemandSqm = annualCoolingDemand / building.grossFloorArea
            annualDHWDemandSqm     = annualDHWDemand     / building.grossFloorArea
            
            building.annualHeatingDemand = annualHeatingDemand
            building.annualCoolingDemand = annualCoolingDemand
            building.annualDHWDemand     = annualDHWDemand
            
            building.annualCoolingDemandSquareMeter = annualCoolingDemandSqm
            building.annualHeatingDemandSquareMeter = annualHeatingDemandSqm
            building.annualDHWDemandSquareMeter     = annualDHWDemandSqm
            
            building.maximumHeatingDemand  = maximumHeatingDemand
            building.maximumCoolingDemand  = maximumCoolingDemand 
            building.maximumDHWWaterDemand = maximumDHWWaterDemand
            
            
            future_annualHeatingDemandSqm = future_annualHeatingDemand / building.grossFloorArea 
            future_annualCoolingDemandSqm = future_annualCoolingDemand / building.grossFloorArea
            future_annualDHWDemandSqm     = future_annualDHWDemand     / building.grossFloorArea
            
            building.future_annualHeatingDemand = future_annualHeatingDemand 
            building.future_annualCoolingDemand = future_annualCoolingDemand  
            building.future_annualDHWDemand     = future_annualDHWDemand
            
            building.future_annualHeatingDemandSquareMeter = future_annualHeatingDemandSqm
            building.future_annualCoolingDemandSquareMeter = future_annualCoolingDemandSqm 
            building.future_annualDHWDemandSquareMeter     = future_annualDHWDemandSqm  
            
            building.future_maximumHeatingDemand  = future_maximumHeatingDemand
            building.future_maximumCoolingDemand  = future_maximumCoolingDemand
            building.future_maximumDHWWaterDemand = future_maximumDHWWaterDemand
            
            
            building.hourlyBaselineDemandList = dataList
            building.hourlyFutureDemandList   = dataFutureList
            
            self.baselineTotalizedDemand.numberOfBuildings   += 1
            self.baselineTotalizedDemand.totalGrossFloorArea += building.grossFloorArea
            self.baselineTotalizedDemand.annualUsefulHeatingDemand            += annualHeatingDemand
            self.baselineTotalizedDemand.annualUsefulCoolingDemand            += annualCoolingDemand
            self.baselineTotalizedDemand.annualUsefulDHWDemand                += annualDHWDemand
           
            self.futureTotalizedDemand.numberOfBuildings   += 1
            self.futureTotalizedDemand.totalGrossFloorArea += building.grossFloorArea            
            self.futureTotalizedDemand.annualUsefulHeatingDemand            += future_annualHeatingDemand
            self.futureTotalizedDemand.annualUsefulCoolingDemand            += future_annualCoolingDemand
            self.futureTotalizedDemand.annualUsefulDHWDemand                += future_annualDHWDemand
            
            
            #print ("building", building)
            
        except WrongValueException as e:
            self.__log.write_log("ERROR", "calculateConsumption WrongValueException " + str(e))
            self.__log.write_log("ERROR", "calculateConsumption Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        
            
        except ZeroValueException as e:
            self.__log.write_log("ERROR", "calculateConsumptionDemand ZeroValueException " + str(e))
            self.__log.write_log("ERROR", "calculateConsumptionDemand Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
                
        except:
            self.__log.write_log("ERROR", "calculateConsumptionDemand building id:" + str(building.reference))
            self.__log.write_log("ERROR", "calculateConsumptionDemand Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
            
        
 
 
    def calculateTotalizedConsumptionDemand(self):
        
        self.baselineTotalizedDemand.annualUsefulHeatingDemandSquareMeter = self.baselineTotalizedDemand.annualUsefulHeatingDemand / self.baselineTotalizedDemand.totalGrossFloorArea if self.baselineTotalizedDemand.totalGrossFloorArea > 0.0 else 0.0
        self.baselineTotalizedDemand.annualUsefulCoolingDemandSquareMeter = self.baselineTotalizedDemand.annualUsefulCoolingDemand / self.baselineTotalizedDemand.totalGrossFloorArea if self.baselineTotalizedDemand.totalGrossFloorArea > 0.0 else 0.0
        self.baselineTotalizedDemand.annualUsefulDHWDemandSquareMeter     = self.baselineTotalizedDemand.annualUsefulDHWDemand     / self.baselineTotalizedDemand.totalGrossFloorArea if self.baselineTotalizedDemand.totalGrossFloorArea > 0.0 else 0.0
        
        self.baselineTotalizedDemandList.append(self.baselineTotalizedDemand)

        self.futureTotalizedDemand.annualUsefulHeatingDemandSquareMeter = self.futureTotalizedDemand.annualUsefulHeatingDemand / self.futureTotalizedDemand.totalGrossFloorArea if self.futureTotalizedDemand.totalGrossFloorArea > 0.0 else 0.0
        self.futureTotalizedDemand.annualUsefulCoolingDemandSquareMeter = self.futureTotalizedDemand.annualUsefulCoolingDemand / self.futureTotalizedDemand.totalGrossFloorArea if self.futureTotalizedDemand.totalGrossFloorArea > 0.0 else 0.0
        self.futureTotalizedDemand.annualUsefulDHWDemandSquareMeter     = self.futureTotalizedDemand.annualUsefulDHWDemand     / self.futureTotalizedDemand.totalGrossFloorArea if self.futureTotalizedDemand.totalGrossFloorArea > 0.0 else 0.0
            
        self.futureTotalizedDemandList.append(self.futureTotalizedDemand )


    """ DB access Methods for Alternative Calculate Algorithm """
    
    def retrieveAlternativeScheduled(self,residential):
        try:
            
            dataList =  self.__db.retrieveAlternativeScheduledResidential(residential)
            #self.totalHdhCalculated = functools.reduce((lambda x,y : x + y ),[scheduled_demand.hdhHour  for scheduled_demand in dataList])
            return dataList  
        except:
            self.__log.write_log("ERROR", "Simplified retrieveAlternativeScheduledResidential Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
        

    def retrieveCountryById(self,id_country):
        try:
            
            return self.__db.retrieveCountryById(id_country)
        
        except:
            self.__log.write_log("ERROR", "Simplified retrieveCountryById Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
               
    
    def retrieveAlternativeDemandByCountry(self,country):
        try:

            statement = """SELECT alternative.id,alternative.id_country,
                                  alternative.residential_kwhm2,alternative.service_kwhm2
                           FROM alternative_demand_database as alternative inner join
                           country as country ON alternative.id_country =  country.id AND
                           UPPER(country.country) = UPPER(:country) AND country.active = 1;"""

            bindvars = {'country':country.country}

            data = self.__db.executeStatement(statement,bindvars)

            if data:
                country_demand = AlternativeDemand(self.__log,data)
                return country_demand
            else:
                raise NoDataFoundException("No record found on table alternative_demand_database")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveAlternativeDemandByCountry " + e)
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveAlternativeDemandByCountry Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise

    def retrieveAlternativeDemandByCountryId(self,id_country):
        try:

            statement = """SELECT alternative.id,alternative.id_country,
                                  alternative.residential_kwhm2,alternative.service_kwhm2
                           FROM alternative_demand_database as alternative 
                           WHERE alternative.active = 1 AND alternative.id_country = :id_country;"""

            bindvars = {'id_country':id_country}

            data = self.__db.executeStatement(statement,bindvars)

            if data:
                country_demand = AlternativeDemand(self.__log,data)
                return country_demand
            else:
                raise NoDataFoundException("No record found on table alternative_demand_database")

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveAlternativeDemandByCountryId " + e)
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveAlternativeDemandByCountryId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise
    
    
    def retrieveAlternativeBuiltSurfaceByCountryId(self,country_id):
        try:
            
            
            statement = """SELECT surface.id, surface.country_id, surface.residential_perc, surface.service_perc 
                           FROM alternative_built_surface as surface 
                           WHERE surface.country_id = :country_id;"""
            
            bindvars = {'country_id':country_id}

            data = self.__db.executeStatement(statement,bindvars)
            
            
            if data:
                built_surface = AlternativeBuiltSurface()
                built_surface.id               = int(data[0])
                built_surface.country_id       = int(data[1])
                built_surface.residential_perc = data[2]
                built_surface.service_perc     = data[3]
                
                return built_surface
            
            else:
                raise NoDataFoundException("No record found on table alternative_built_surface")
            
        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveAlternativeBuiltSurfaceByCountryId " + e)
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveAlternativeBuiltSurfaceByCountryId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
  
    def retrieveAlternativeOtherDistribution(self,residential=True):
        try:
                
            statement = """SELECT other.id, other.residential, other.base_electric_perc, other.space_cooling_perc
                           FROM alternative_other_distribution as other
                           WHERE other.residential = :residential;"""
            
            bindvars = {'residential':int(residential)}

            data = self.__db.executeStatement(statement,bindvars)
            
            
            if data:
                otherDistribution = AlternativeOtherDistribution()
                otherDistribution.id                 = int(data[0])
                otherDistribution.residential        = int(data[1])
                otherDistribution.base_electric_perc = data[2]
                otherDistribution.space_cooling_perc = data[3]

                return otherDistribution
            
            else:
                raise NoDataFoundException("No record found on table alternative_other_distribution")
            
        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveAlternativeOtherDistribution " + e)
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars)) 
            raise

        except:
            self.__log.write_log("ERROR", "retrieveAlternativeOtherDistribution Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
  
     
    def retrieveAlternativeConsumptionDistribution(self,country_id,residential=True):
        try:
                
            statement = """SELECT consumption.id, consumption.country_id, consumption.residential,consumption.space_heating_perc,
                           consumption.water_heating_perc, consumption.other_perc 
                           FROM alternative_consumption_distribution as consumption 
                           WHERE consumption.country_id = :country_id and residential = :residential;"""
            
            bindvars = {'country_id':country_id, 'residential':int(residential)}

            data = self.__db.executeStatement(statement,bindvars)
            
            
            if data:
                consumptionDistribution = AlternativeConsumptionDistribution()
                consumptionDistribution.id                  = int(data[0])
                consumptionDistribution.country_id          = int(data[1])
                consumptionDistribution.residential         = data[2]
                consumptionDistribution.space_heating_perc  = data[3]
                consumptionDistribution.water_heating_perc  = data[4]
                consumptionDistribution.other_perc          = data[5]
                
                return consumptionDistribution
            
            else:
                raise NoDataFoundException("No record found on table alternative_consumption_distribution")
            
        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveAlternativeConsumptionDistribution " + e)
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars)) 
            raise

        except:
            self.__log.write_log("ERROR", "retrieveAlternativeConsumptionDistribution Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
  
  
        
        
    def retrieveCSVInterimFields(self, method):
        try:
            return self.__db.retrieveCSVInterimFields(method)
        
        except:
            self.__log.write_log("ERROR", "Alternative retrieveCSVInterimFields Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise     


  
    def retrieveOutputFields(self,scenario,fileType,fileCategory,calculateModel):
        try:
            return self.__db.retrieveOutputFields(scenario, fileType,fileCategory,calculateModel)
        
        except:
            self.__log.write_log("ERROR", "Alternative retrieveOutputFields Error  scenario:"+ scenario + " fileType:" + fileType +  "  fileCategory:" + fileCategory + " CalculateModel:" + calculateModel)
            self.__log.write_log("ERROR", "Alternative retrieveOutputFields Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise                
        

# Test Case   
if __name__ == '__main__':
    from manageLog.log import Log
    from manageDB.db import DB
    from model.building import Building
    

    log = Log("D:\\Users\\E17004\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\PlanHeatDMM\\log\\","prueba.log")
    database = DB(log)
    database.connectDB()
    param = {'Regstatus':True,'Reference':3737318,'TotalHeight':0,'GrossFloorArea':833.42,'DistrictCentroid':"0.0#0.0"}
                    
    
    building = Building(log,"prueba","prueba",1,param)
    simplified = Alternative(log,database,None)
    simplified.calculateConsumption(building)
    
    
    pass