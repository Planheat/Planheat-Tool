# -*- coding: utf-8 -*-
"""
   Complete Calculation Algorithm
   :author: Sergio Aparicio Vegas
   :version: 0.1
   :date: 24 Oct. 2017
"""

__docformat__ = "restructuredtext"

import sys
import itertools
from utility.utils import timeit
from copy import deepcopy
from config import config as Config
from model.totalized_demand import TotalizedDemand
from model.hourly_demand import HourlyDemand
from model.internal_gains import InternalGain
from model.annual_DHW_demand import AnnualDHWDemand
from model.glazing import Glazing
from model.solar_gains import SolarGain
from model.air_lekeage_distribution import AirLekeageDistribution
from model.u_values import UValues
from model.efficiency_impact import EfficiencyImpact
from model.refurbishment_u_values  import RefurbishmentUValues
from model.refurbishment_air_loss import RefurbishmentAirLoss
from model.air_lekeage_building_distribution import AirLekeageBuildingDistribution
from myExceptions.exceptions import  NoDataFoundException, DataValueNoneException,ZeroValueException, \
                                     NoProcessException,WrongValueException,NOANoDataFoundException



class Complete():
    """
     Complete Object for complete calculation method
    """


    def __init__(self, log, database, noa, country_id,boolRetrofittedScenarios, planHeatDMM):

        """
        Constructor
        """
        self.name = "Complete"
        self.__log = log
        self.__db = database
        self.__noa = noa
        self.__boolRetrofittedScenarios = boolRetrofittedScenarios
        self.__planHeatDMM = planHeatDMM

        self.building_uses = []
        self.building_use_map = {}

        self.protection_levels = []
        self.protection_level_map = {}

        self.refurbishment_levels = []

        #Baseline catalog data
        self.scheduledUseDict = {}
        self.internalGainsDict = {}
        self.annualDHWDemandDict={}
        self.glazingDict = {}
        self.airLekeageDict = {}
        self.UValuesResidentialDict = {}
        self.UValuesNonResidentialDict = {}
        self.solarGainsList = []
        self.periodList = []

        #Future catalog data
        self.airLekeageBuildingObj = None
        self.efficiencyImpactDict={}
        self.refurbishmentUValuesResidentialDict = {}
        self.refurbishmentUValuesNonResidentialDict = {}
        self.refurbishmentAirLossDict = {}
        self.protectionLevelDict = {}
        self.tabDataDict={}

        self.country = None
        self.country_name = None
        self.countryID  = country_id


        self.district_temperature = None
        self.district_geolocation = -1

        self.totalizedDemand = None
        self.baselineTotalizedDemandList = []
        self.futureTotalizedDemandList   = []




    def initialize(self):
        try:

            self.inputFields              = self.retrieveCSVInterimFields("Complete")

            #Baseline Fields
            self.outputBaselineDetailFieldsCsv    = self.retrieveOutputFields("Baseline", "Detail", "Csv","Complete")
            self.outputBaselineTotalizedFieldsCsv = self.retrieveOutputFields("Baseline", "Totalized", "Csv","Complete")
            self.outputBaselineHourlyFieldsCsv    = self.retrieveOutputFields("Baseline", "Hourly", "Csv","Complete")
            self.outputBaselineDetailFieldsShape  = self.retrieveOutputFields("Baseline", "Detail", "Shp","Complete")


            #Future Fields
            self.outputFutureDetailFieldsCsv    = self.retrieveOutputFields("Future", "Detail", "Csv","Complete")
            self.outputFutureTotalizedFieldsCsv = self.retrieveOutputFields("Future", "Totalized", "Csv","Complete")
            self.outputFutureHourlyFieldsCsv    = self.retrieveOutputFields("Future", "Hourly", "Csv","Complete")
            self.outputFutureDetailFieldsShape  = self.retrieveOutputFields("Future", "Detail", "Shp","Complete")


            self.hourlyBaselineDataList = [HourlyDemand() for _ in range(Config.HOURS_PER_YEAR)]
            self.hourlyFutureDataList   = [HourlyDemand() for _ in range(Config.HOURS_PER_YEAR)]


            #Object building_use_map List to Dict
            for useMap in self.__planHeatDMM.data.buildingUseMap:
                self.building_use_map[useMap.user_definition_use] = useMap


            for protection_level_map in deepcopy(self.__planHeatDMM.data.protectionLevelMap):
                    if protection_level_map.DMM_protection_level > 0:
                        protection_level_map.user_definition_protection = protection_level_map.user_definition_protection.lower().strip().replace(';','')
                        self.protection_levels.append(protection_level_map)

            self.building_uses = [building_use for building_use in self.__planHeatDMM.data.buildingUse if building_use.use.lower() not in  ("not evaluate")]

            self.refurbishment_levels = [refurbishmentLevel for refurbishmentLevel in self.__planHeatDMM.data.refurbishment_levels if refurbishmentLevel.level.lower() not in  ("none")]

            self.country = self.retrieveCountryById(self.countryID)
            self.country_name = self.country.country

            #Baseline Retrieve catalog data
            self.internalGainsDict = self.retrieveCompleteInternalGainsAll(self.building_uses)
            self.annualDHWDemandDict=self.retrieveCompleteAnnualDHWDemandAll(self.building_uses)
            self.glazingDict    = self.retrieveCompleteGlazingAll(self.building_uses)
            self.solarGainsList = self.retrieveCompleteSolarGainsByCountryId(self.countryID)
            self.periodList = self.retrieveCompletePeriodsAll()
            self.airLekeageDict =  self.retrieveCompleteAirLekeageAll(self.countryID, self.periodList)
            self.UValuesResidentialDict    = self.retrieveCompleteUValuesAll(self.countryID, self.periodList, residential=True)
            self.UValuesNonResidentialDict = self.retrieveCompleteUValuesAll(self.countryID, self.periodList,residential=False)


            #Future Retrieve catalog data
            self.airLekeageBuildingDistributionObj = self.retrieveAirLekeageBuildingDistribution()
            self.efficiencyImpactDict = self.retrieveEfficiencyImpactAll(self.refurbishment_levels)
            self.refurbishmentUValuesResidentialDict    = self.retrieveRefurbishmentUValuesAll(self.countryID, self.refurbishment_levels, residential=True)
            self.refurbishmentUValuesNonResidentialDict = self.retrieveRefurbishmentUValuesAll(self.countryID, self.refurbishment_levels, residential=False)
            self.refurbishmentAirLossDict = self.generateRefurbishmentAirlossTable(self.countryID, self.airLekeageDict, self.periodList, self.refurbishment_levels)
            self.tabDataDict = self.convertTabDataListToDict(deepcopy(self.__planHeatDMM.data.refurbishmentTabDataList))
            self.protectionLevelDict = self.convertProtectionLevelListToDict(deepcopy(self.__planHeatDMM.data.protectionLevels))

        except:
            self.__log.write_log("ERROR", "Complete initialize Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def calculateConsumption(self,building):
        try:
            if building.Regstatus:

                if self.district_geolocation != building.districtCentroid:

                    if Config.USE_NOA_DATA in ("Y","y"):
                        # call NOA Module
                        self.getLongLatDistrictCentroid(building)
                        self.district_temperature = self.__noa.call(building.latitude,building.longitude)
                        self.__log.write_log("INFO", "Use location temperatures from NOA service")
                        
                    else:
                        self.district_temperature  = self.retrieveAvgLocationTemperature(self.countryID)
                        self.__log.write_log("INFO", "Use location temperatures from database")

                    self.district_geolocation = building.districtCentroid
                    self.scheduledUseDict = self.retrieveCompleteScheduledAll(self.building_uses, self.district_temperature)


                building.country            = self.country_name
                use                         = self.building_use_map[building.use]
                building.useMap             = use.DMM_use
                building.nonOffice          = use.non_office
                building.floor_height       = use.floor_height  
                building.useId              = use.building_use_id
                period                      = self.retrievePeriodFromYearConstruction(building.reference, building.yearOfConstruction)
                building.period_id          = period.id
                building.period_text = period.period_text
                building.protectionLevel    = self.checkProtectionLevel(building.reference, building.protectionDegree)


                if not self.country  or not self.district_temperature or not self.scheduledUseDict or not self.internalGainsDict \
                or not self.glazingDict or not self.periodList or not self.airLekeageDict or not self.UValuesResidentialDict \
                or not  self.UValuesNonResidentialDict or not self.annualDHWDemandDict or not  self.building_uses \
                or not building.period_id or not building.useMap or  building.nonOffice is None:

                    noneMessage = ""
                    if not self.country: noneMessage = noneMessage + " - country is None or False"
                    if not self.district_temperature: noneMessage = noneMessage + " - district_temperature is None or False"
                    if not self.scheduledUseDict: noneMessage = noneMessage + " - scheduledUseDict is None or False"
                    if not self.internalGainsDict: noneMessage = noneMessage + " - internalGainsDict is None or False"
                    if not self.glazingDict: noneMessage = noneMessage + " - glazingDict is None or False"
                    if not self.periodList: noneMessage = noneMessage + " - periodList is None or False"
                    if not self.airLekeageDict: noneMessage = noneMessage + " - airLekeageDict is None or False"
                    if not self.UValuesResidentialDict: noneMessage = noneMessage + " - UValuesResidentialDict is None or False"
                    if not self.UValuesNonResidentialDict: noneMessage = noneMessage + " - UValuesNonResidentialDict is None or False"
                    if not self.annualDHWDemandDict: noneMessage = noneMessage + " - annualDHWDemandDict is None or False"
                    if not self.building_uses: noneMessage = noneMessage + " - building_uses is None or False"
                    if not building.period_id: noneMessage = noneMessage + " - building period_id is None or False"
                    if not building.useMap: noneMessage = noneMessage + " - building useMap is None or False"
                    if not building.nonOffice: noneMessage = noneMessage + " - building nonOffice is None"


                    raise DataValueNoneException("calculateConsumption - baseline scenario - value fields None " + noneMessage)

                elif self.__boolRetrofittedScenarios and \
                    (not self.efficiencyImpactDict  or not self.refurbishmentUValuesResidentialDict or not self.refurbishmentUValuesNonResidentialDict \
                     or not self.refurbishmentAirLossDict or not self.tabDataDict or not self.airLekeageBuildingDistributionObj or not self.protectionLevelDict):
                    noneMessage = ""
                    if not self.efficiencyImpactDict: noneMessage = noneMessage + " - efficiencyImpactDict is None or False"
                    if not self.refurbishmentUValuesResidentialDict: noneMessage = noneMessage + " - refurbishmentUValuesResidentialDict is None or False"
                    if not self.refurbishmentUValuesNonResidentialDict: noneMessage = noneMessage + " - refurbishmentUValuesNonResidentialDict is None or False"
                    if not self.refurbishmentAirLossDict: noneMessage = noneMessage + " - refurbishmentAirLossDict is None or False"
                    if not self.tabDataDict: noneMessage = noneMessage + " - refurbishmentAirLossDict is None or False"
                    if not self.airLekeageBuildingDistributionObj: noneMessage = noneMessage + " - airLekeageBuildingDistributionObj is None or False"
                    if not self.protectionLevelDict: noneMessage = noneMessage + " - airLekeageBuildingDistributionObj is None or False"

                    raise DataValueNoneException("calculateConsumption - future scenario - value fields None " + noneMessage)

                else:

                    if  building.useMap.lower() == 'not evaluate':
                        raise NoProcessException()

                    if building.numberOfFloors <= 0.0:
                        raise ZeroValueException((" building_id:{} with numberOfFloors:{:f}  with totalHeight:{:f} meters").format(building.reference,building.numberOfFloors,building.totalHeight))
                    
                    elif building.totalHeight <=0.0:
                        raise ZeroValueException((" building_id:{} with totalHeight:{:f} meters , must be greater than 0.0").format(building.reference,building.totalHeight))
                    
                    elif building.grossFloorArea <= 0.0:
                        raise ZeroValueException((" building_id:{} with grossFloorArea:{:f} square meters, must be greater than 0.0").format(building.reference,building.grossFloorArea))
                    elif building.volume <= 0.0:
                        raise ZeroValueException((" building_id:{},volume:{:f}, must be greater than 0.0").format(building.reference,building.volume))


                    self.calculateConsumptionDemand(building)

                    #print (building)


            return building


        except NoProcessException as e:
            self.__log.write_log("WARNING", "calculateConsumption Building use {}  not evaluate, for building_id:{}".format(building.use,building.reference))
            building.Regstatus = True
            building.Regprocess = False
            return building
        except KeyError as e:
            self.__log.write_log("ERROR", "calculateConsumption keyError " + str(e))
            building.Regstatus = False
            return building
        except WrongValueException as e:
            self.__log.write_log("ERROR", "calculateConsumption WrongValueException " + str(e))
            #self.__log.write_log("ERROR", "calculateConsumption Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            building.Regstatus = False
            return building

        except ZeroValueException as e:
            self.__log.write_log("ERROR", "calculateConsumption ZeroValueException " + str(e))
            #self.__log.write_log("ERROR", "calculateConsumption Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            building.Regstatus = False
            return building
        
        except NOANoDataFoundException as e:
            raise NOANoDataFoundException(e)
        
        except:
            self.__log.write_log("ERROR", "calculateConsumption building_id:{} Unexpected error:{} {}".format(building.reference,str(sys.exc_info()[0]),str(sys.exc_info()[1])))
            #self.__log.write_log("ERROR", "calculateConsumption Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            building.Regstatus = False
            return building


    def calculateConsumptionDemand(self,building):
        try:
            UValue = None
            futureUValue = None
            boolComputeFutureScenario = False
            cooling_correction_factor = 0
            heatBaseTemp = self.country.heating_base
            coolBaseTemp = self.country.cooling_base

            scheduledList = self.scheduledUseDict[building.useMap]
            internal_gain = self.internalGainsDict[building.useMap]
            glazing_perc = self.glazingDict[building.useMap].percentage
            building.ACH = self.airLekeageDict[building.period_id].air_lekeage
            DHW_demand = self.annualDHWDemandDict[building.useMap].DHW_demand_kwhm2

            if building.useMap.lower() == 'residential':
                UValue       = self.UValuesResidentialDict[building.period_id]
                cooling_correction_factor = 1.0

            else:
                UValue       = self.UValuesNonResidentialDict[building.period_id]
                cooling_correction_factor =  0.3333333333

            building.north_window_area = building.northExteriorEnvelopeArea * glazing_perc /100.0
            building.south_window_area = building.southExteriorEnvelopeArea * glazing_perc /100.0
            building.east_window_area  = building.eastExteriorEnvelopeArea  * glazing_perc /100.0
            building.west_window_area  = building.westExteriorEnvelopeArea  * glazing_perc /100.0

            building.north_opaque_facade_area = building.northExteriorEnvelopeArea - building.north_window_area
            building.south_opaque_facade_area = building.southExteriorEnvelopeArea - building.south_window_area
            building.east_opaque_facade_area  = building.eastExteriorEnvelopeArea  - building.east_window_area
            building.west_opaque_facade_area  = building.westExteriorEnvelopeArea  - building.west_window_area

            #Calculate building Window Area
            building.windowArea = building.north_window_area + building.south_window_area + building.east_window_area + building.west_window_area
            #Calculate building Wall Area
            building.opaqueFacadeArea = building.north_opaque_facade_area + building.south_opaque_facade_area + building.east_opaque_facade_area + building.west_opaque_facade_area

            building.roof_u_value   = UValue.roof_u_value
            building.wall_u_value   = UValue.wall_u_value
            building.window_u_value = UValue.window_u_value
            
           
            # U values aRoof * uRoof + aWall * uWall + aWindow * uWindow
            building.AU_value = (building.roofArea * UValue.roof_u_value) + (building.opaqueFacadeArea * UValue.wall_u_value ) + (UValue.window_u_value * building.windowArea)

            refurbishmentTabRow={}
            if self.__boolRetrofittedScenarios:

                try:
                    protectionLevelObj =  self.protectionLevelDict[ building.protectionLevel]

                    #If building is completely reformed and has the maximum protection level, we check it as not refurbishable
                    if protectionLevelObj.roof == True and protectionLevelObj.wall == True and protectionLevelObj.window == True:
                        boolComputeFutureScenario = False

                except KeyError:
                    self.__log.write_log("ERROR", "calculateConsumptionDemand key not found in protectionLevelDict dict for key:" + str(building.protectionLevel) )
                    raise


                try:
                    tabData = self.tabDataDict[building.useMap]
                    refurbishmentTabRow = tabData.rows[building.period_id]

                except KeyError:
                    self.__log.write_log("ERROR", "calculateConsumptionDemand key not found in tabDataDict dict for tab key:" + str(building.useMap) + " and row key:" + str(building.period_id))
                    raise


                building.future_refurbishment_selected_air_loss_perc = 0.0
                
                if tabData.tab_check  == True and refurbishmentTabRow.row_refurbishment_level.lower() != "none":
                    boolComputeFutureScenario = True

                    building.future_refurbishment                       = tabData.tab_check
                    building.future_refurbishment_level                 = refurbishmentTabRow.row_refurbishment_level


                    if protectionLevelObj.roof == True:
                        building.future_refurbishment_selected_roof_perc = 0
                    else:
                        building.future_refurbishment_selected_roof_perc   = refurbishmentTabRow.row_roof_percentage
                        building.future_refurbishment_selected_air_loss_perc += self.airLekeageBuildingDistributionObj.ceiling_perc *  (building.future_refurbishment_selected_roof_perc / 100.0)


                    if protectionLevelObj.wall == True :
                        building.future_refurbishment_selected_wall_perc  = 0
                    else:
                        building.future_refurbishment_selected_wall_perc    = refurbishmentTabRow.row_wall_percentage
                        building.future_refurbishment_selected_air_loss_perc += self.airLekeageBuildingDistributionObj.walls_perc *  (building.future_refurbishment_selected_wall_perc / 100.0)

                    if protectionLevelObj.window == True:
                        building.future_refurbishment_selected_window_perc  = 0
                        
                    else:
                        building.future_refurbishment_selected_window_perc  = refurbishmentTabRow.row_window_percentage
                        building.future_refurbishment_selected_air_loss_perc += self.airLekeageBuildingDistributionObj.windows_doors_perc *  (building.future_refurbishment_selected_window_perc / 100.0)


                    try:
                        impact = self.efficiencyImpactDict[refurbishmentTabRow.row_refurbishment_level]

                        building.economic_impact   =  impact.roof_economic     * building.footPrintArea    * (building.future_refurbishment_selected_roof_perc   / 100.0) + \
                                                      impact.wall_economic     * building.opaqueFacadeArea * (building.future_refurbishment_selected_wall_perc   / 100.0) + \
                                                      impact.window_economic   * building.windowArea       * (building.future_refurbishment_selected_window_perc / 100.0)

                        building.environment_impact = impact.roof_environment     * building.footPrintArea    * (building.future_refurbishment_selected_roof_perc   / 100.0) + \
                                                      impact.wall_environment     * building.opaqueFacadeArea * (building.future_refurbishment_selected_wall_perc   / 100.0) + \
                                                      impact.window_environment   * building.windowArea       * (building.future_refurbishment_selected_window_perc / 100.0)

                    except KeyError:
                        self.__log.write_log("ERROR", "calculateConsumptionDemand key not found in efficiencyImpactDict dict for key:" + str(refurbishmentTabRow.row_refurbishment_level_id) )
                        raise


                    try:
                        future_ACH = self.refurbishmentAirLossDict[building.period_id][building.future_refurbishment_level].air_lekeage
                        
                        building.future_ACH = building.ACH * ((100.0 - building.future_refurbishment_selected_air_loss_perc)/100.0) + (future_ACH * building.future_refurbishment_selected_air_loss_perc) / 100.0
                         
                    except KeyError:
                        self.__log.write_log("ERROR", "calculateConsumptionDemand key not found in refurbishmentAirLossDict dict for key:" + str(building.period_id) + " and second level key:" + str(building.future_refurbishment_level))
                        raise

                    
                    if building.useMap.lower() == 'residential':
                        futureUValue = self.refurbishmentUValuesResidentialDict[building.future_refurbishment_level]
                    else:
                        futureUValue = self.refurbishmentUValuesNonResidentialDict[building.future_refurbishment_level]
    
                    """
                    building.future_roof_u_value   = futureUValue.roof_u_value
                    building.future_wall_u_value   = futureUValue.wall_u_value
                    building.future_window_u_value = futureUValue.window_u_value
                    """      
                    
                    building.future_roof_u_value  =  UValue.roof_u_value   * ((100.0 -  building.future_refurbishment_selected_roof_perc)/100.0)   + futureUValue.roof_u_value   * (building.future_refurbishment_selected_roof_perc / 100.0 ) 
                    building.future_wall_u_value   = UValue.wall_u_value   * ((100.0 -  building.future_refurbishment_selected_wall_perc)/100.0)   + futureUValue.wall_u_value   * (building.future_refurbishment_selected_wall_perc / 100.0 )
                    building.future_window_u_value = UValue.window_u_value * ((100.0 -  building.future_refurbishment_selected_window_perc)/100.0) + futureUValue.window_u_value * (building.future_refurbishment_selected_window_perc / 100.0 )

                    # Future U values
                    building.future_AU_value = (building.roofArea * UValue.roof_u_value) * ((100.0 -  building.future_refurbishment_selected_roof_perc)/100.0) + (building.roofArea * futureUValue.roof_u_value) * (building.future_refurbishment_selected_roof_perc / 100.0 ) + \
                                               (building.opaqueFacadeArea * UValue.wall_u_value ) * ((100.0 -  building.future_refurbishment_selected_wall_perc)/100.0) + (building.opaqueFacadeArea * futureUValue.wall_u_value ) * (building.future_refurbishment_selected_wall_perc / 100.0 ) +\
                                               (building.windowArea * UValue.window_u_value) * ((100.0 -  building.future_refurbishment_selected_window_perc)/100.0) + (building.windowArea * futureUValue.window_u_value) * (building.future_refurbishment_selected_window_perc /100.0 ) 
                   
                    
                    #print("---------------------------------------------------------------------------------------------------------------------------------")
                    #print("building id",building.reference)
                    #print("futureUValue",futureUValue)
                    #print("future_AU_value",building.future_AU_value)  
                    #print ("cooling Factor",cooling_correction_factor)
                    #print("impact", impact)
                    #print("economic impact",building.economic_impact)
                    #print("environment impact",building.environment_impact)
                    #print("tabData",tabData)
                    #print("tabDataRow",refurbishmentTabRow)
                    #print("Future ACH",building.future_ACH )
                    #print("Protection Level", protectionLevelObj)
                    #print("---------------------------------------------------------------------------------------------------------------------------------")
                    

                else:
                    boolComputeFutureScenario = False

            else:
                boolComputeFutureScenario = False

            self.calculateConsumptionDemandHourly(building,heatBaseTemp,coolBaseTemp,scheduledList,internal_gain,DHW_demand,cooling_correction_factor, boolComputeFutureScenario)

            
            try: 
                self.insert_building_calculate_totalized_demand(building,"Baseline")
                self.insert_building_calculate_totalized_demand(building,"Future")
                self.__db.commit_data()
            except:
                self.__db.rollback_data()
                raise    



        except:
            self.__log.write_log("ERROR", "calculateConsumptionDemand building id:" + str(building.reference))
            self.__log.write_log("ERROR", "calculateConsumptionDemand Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    #@timeit
    def calculateConsumptionDemandHourly(self,building,heatBaseTemp,coolBaseTemp,scheduledList,internal_gain,DHW_demand,cooling_correction_factor, boolComputeFutureScenario):
        try:
            hourlyBaselineDataList = self.hourlyBaselineDataList[:]
            hourlyFutureDataList   = self.hourlyFutureDataList[:]
            #for x in range(8760):
            #    print("Baseline",id(hourlyBaselineDataList[x]), "Future",id(hourlyFutureDataList[x]))
            #hourlyBaselineDataList = [HourlyDemand() for x in range(Config.HOURS_PER_YEAR)]
            #hourlyFutureDataList   = [HourlyDemand() for x in range(Config.HOURS_PER_YEAR)]

            #Baseline Calculate Variables
            HD   = 0.0
            CD   = 0.0
            DHWD = 0.0

            maxHeatDemand = 0.0 #float(sys.float_info.min)
            maxCoolDemand = 0.0
            maxDHWDemand  = 0.0

            future_HD   = 0.0
            future_CD   = 0.0
            future_DHWD = 0.0

            future_maxHeatDemand = 0.0
            future_maxCoolDemand = 0.0
            future_maxDHWDemand  = 0.0
            
            projectID  = building.projectID
            reference  = building.reference
            period     = building.period_text
            use        = building.useMap    
            
            building_north_window_area = building.north_window_area 
            building_south_window_area = building.south_window_area
            building_east_window_area  = building.east_window_area
            building_west_window_area  = building.west_window_area
            
            building_grossFloorArea = building.grossFloorArea
            building_volume =  building.volume
            building_ACH = building.ACH
            building_AU_value = building.AU_value

            building.equipment_intenal_gains  = internal_gain.equipment_internal_gains
            building.occupancy_internal_gains = internal_gain.occupancy_internal_gains
            building.light_intenal_gains      = internal_gain.lighting_power 
             
            equipment_intenal_gains_kw_tmp  = internal_gain.equipment_internal_gains * building_grossFloorArea / 1000.0
            occupancy_internal_gains_kw_tmp = internal_gain.occupancy_internal_gains * building_grossFloorArea / 1000.0
            light_intenal_gains_kw_tmp      = internal_gain.lighting_power           * building_grossFloorArea / 1000.0


            # Calculate Data for Hourly Demand
            for x, hourly in enumerate(hourlyBaselineDataList):

                scheduled = scheduledList[x]
                solarGain = self.solarGainsList[x]

                hourly.projectID  = projectID
                hourly.reference  = reference
                hourly.period     = period
                hourly.use        = use   

                hourly.dayOfYear = scheduled.dayOfYear
                hourly.hourOfDay = scheduled.hourOfDay
                hourly.season    = scheduled.season


                hourly.equipment_internal_gains = equipment_intenal_gains_kw_tmp  * scheduled.equipment
                hourly.occupancy_internal_gains = occupancy_internal_gains_kw_tmp * scheduled.occupancy
                hourly.light_internal_gains     = light_intenal_gains_kw_tmp      * scheduled.lighting


                if building.nonOffice:
                    hourly.solar_gains = (building_north_window_area * solarGain.wwr_north_non_offices + building_south_window_area * solarGain.wwr_south_non_offices \
                    + building_east_window_area  * solarGain.wwr_east_non_offices  + building_west_window_area  * solarGain.wwr_west_non_offices) / 1000.0
                else:
                    hourly.solar_gains = (building_north_window_area * solarGain.wwr_north_offices + building_south_window_area * solarGain.wwr_south_offices \
                    + building_east_window_area  * solarGain.wwr_east_offices  + building_west_window_area * solarGain.wwr_west_offices) / 1000.0


                gains =  hourly.equipment_internal_gains + hourly.occupancy_internal_gains + hourly.light_internal_gains + hourly.solar_gains

                if heatBaseTemp - scheduled.avg_temp < 0:
                    hourly.HDH = 0
                else:
                    hourly.HDH = heatBaseTemp - scheduled.avg_temp 
                          
                hourly.CDH =  scheduled.avg_temp - coolBaseTemp
                
                hourly_heat_ventilation_losses_temp = heatBaseTemp - scheduled.avg_temp

                hourly.heat_ventilation_losses = (0.33 * building_ACH * building_volume * hourly_heat_ventilation_losses_temp) / 1000.0
                hourly.cool_ventilation_losses = (0.33 * building_ACH * building_volume * hourly.CDH) / 1000.0

                hourly_heating_demand = 0.0
                hourly_cooling_demand = 0.0
                hourly_DHW_demand     = 0.0
                
                hourly.base_heating = (hourly.HDH * building_AU_value )/1000.0
                hourly_heating_demand = (hourly.base_heating - gains + hourly.heat_ventilation_losses) * scheduled.heating


                hourly.base_cooling = (hourly.CDH * building_AU_value ) / 1000.0
                hourly_cooling_demand = (hourly.base_cooling + gains + hourly.cool_ventilation_losses) * scheduled.cooling * cooling_correction_factor

                hourly_DHW_demand     =  DHW_demand * building_grossFloorArea * scheduled.DHW /scheduled.DHW_total_annual

                # Avoid demand with negative values
                if hourly_heating_demand <= 0.0 or hourly.season.lower() == "s": hourly_heating_demand = 0.0
                if hourly_cooling_demand <= 0.0 or hourly.season.lower() == "w": hourly_cooling_demand = 0.0


                hourly.heating = hourly_heating_demand
                hourly.cooling = hourly_cooling_demand
                hourly.DHW     = hourly_DHW_demand

                hourly.scheduling_heating   = scheduled.heating
                hourly.scheduling_cooling   = scheduled.cooling
                hourly.scheduling_DHW       = scheduled.DHW
                hourly.scheduling_lighting  = scheduled.lighting
                hourly.scheduling_equipment = scheduled.equipment
                hourly.scheduling_occupancy = scheduled.occupancy

                #  Totalized and Maximun
                HD   += hourly_heating_demand
                CD   += hourly_cooling_demand
                DHWD += hourly_DHW_demand

                if hourly_heating_demand > maxHeatDemand:
                    maxHeatDemand = hourly_heating_demand

                if hourly_cooling_demand > maxCoolDemand:
                    maxCoolDemand = hourly_cooling_demand

                if hourly_DHW_demand > maxDHWDemand:
                    maxDHWDemand = hourly_DHW_demand

                # Future
                hourlyFuture = hourlyFutureDataList[x]
                hourlyFuture.projectID  =  projectID
                hourlyFuture.reference  =  reference
                hourlyFuture.period     =  period
                hourlyFuture.use        =  use
            
                hourlyFuture.dayOfYear = scheduled.dayOfYear
                hourlyFuture.hourOfDay = scheduled.hourOfDay
                hourlyFuture.season    = scheduled.season

                hourlyFuture.equipment_internal_gains = hourly.equipment_internal_gains
                hourlyFuture.occupancy_internal_gains = hourly.occupancy_internal_gains
                hourlyFuture.light_internal_gains     = hourly.light_internal_gains
                hourlyFuture.solar_gains =  hourly.solar_gains
                hourlyFuture.HDH = hourly.HDH
                hourlyFuture.CDH = hourly.CDH
                
                
                
                if boolComputeFutureScenario == False:
                    
                    #Baseline same values
                    hourly.heat_ventilation_losses = (0.33 * building_ACH * building_volume * hourly_heat_ventilation_losses_temp) / 1000.0
                    hourly.cool_ventilation_losses = (0.33 * building_ACH * building_volume * hourlyFuture.CDH) / 1000.0
                
                    hourlyFuture.heat_ventilation_losses = hourly.heat_ventilation_losses
                    hourlyFuture.cool_ventilation_losses = hourly.cool_ventilation_losses
    
                    hourlyFuture.base_heating = hourly.base_heating
                    hourlyFuture.base_cooling = hourly.base_cooling
    
                    hourlyFuture.heating = hourly.heating
                    hourlyFuture.cooling = hourly.cooling
                    hourlyFuture.DHW     = hourly.DHW
    
                    hourlyFuture.scheduling_heating = hourly.scheduling_heating
                    hourlyFuture.scheduling_cooling = hourly.scheduling_cooling
                    hourlyFuture.scheduling_DHW     = hourly.scheduling_DHW
                    future_HD   = HD
                    future_CD   = CD
                    future_DHWD = DHWD
    
                    future_maxHeatDemand = maxHeatDemand
                    future_maxCoolDemand = maxCoolDemand
                    future_maxDHWDemand  = maxDHWDemand
                    
                    building.future_roof_u_value   = building.roof_u_value
                    building.future_wall_u_value   = building.wall_u_value
                    building.future_window_u_value = building.window_u_value
                                              
                    building.future_AU_value = building_AU_value 
                    building.future_ACH      = building_ACH
                    
                else:
                    
                    #Apply Retrofit Scenario
                    future_hourly_heating_demand = 0.0
                    future_hourly_cooling_demand = 0.0
                    
                    
                    hourlyFuture.heat_ventilation_losses = (0.33 * building.future_ACH * building_volume * hourly_heat_ventilation_losses_temp) / 1000.0
                    hourlyFuture.cool_ventilation_losses = (0.33 * building.future_ACH * building_volume * hourlyFuture.CDH) / 1000.0
                    
                    hourlyFuture.base_heating = (hourlyFuture.HDH * building.future_AU_value)/1000.0
                    future_hourly_heating_demand = (hourlyFuture.base_heating - gains + hourlyFuture.heat_ventilation_losses) * scheduled.heating


                    hourlyFuture.base_cooling = (hourlyFuture.CDH * building.future_AU_value) / 1000.0
                    future_hourly_cooling_demand = (hourlyFuture.base_cooling + gains + hourlyFuture.cool_ventilation_losses) * scheduled.cooling * cooling_correction_factor
                    
                    
                    # Avoid demand with negative values
                    if future_hourly_heating_demand <= 0.0 or hourlyFuture.season.lower() == "s": future_hourly_heating_demand = 0.0
                    if future_hourly_cooling_demand <= 0.0 or hourlyFuture.season.lower() == "w": future_hourly_cooling_demand = 0.0

                    hourlyFuture.heating = future_hourly_heating_demand
                    hourlyFuture.cooling = future_hourly_cooling_demand
                
                    hourlyFuture.scheduling_heating   = scheduled.heating
                    hourlyFuture.scheduling_cooling   = scheduled.cooling
                    
                    #  Totalized and Maximun for Future scenario
                    future_HD   += future_hourly_heating_demand
                    future_CD   += future_hourly_cooling_demand
                    
                    if future_hourly_heating_demand > future_maxHeatDemand:
                        future_maxHeatDemand = future_hourly_heating_demand

                    if future_hourly_cooling_demand > future_maxCoolDemand:
                        future_maxCoolDemand = future_hourly_cooling_demand

                    
                    #Baseline DHW Same Values  
                    hourlyFuture.DHW     = hourly.DHW
                    hourlyFuture.scheduling_DHW     = hourly.scheduling_DHW
                    future_DHWD = DHWD
                    future_maxDHWDemand  = maxDHWDemand    


            #Totalized data per building
            
            #Baseline
            building.annualHeatingDemand = HD
            building.annualCoolingDemand = CD
            building.annualDHWDemand     = DHWD
            building.annualHeatingDemandSquareMeter = HD / building_grossFloorArea
            building.annualCoolingDemandSquareMeter = CD / building_grossFloorArea
            building.annualDHWDemandSquareMeter     = DHWD / building_grossFloorArea

            building.maximumHeatingDemand  = maxHeatDemand
            building.maximumCoolingDemand  = maxCoolDemand
            building.maximumDHWWaterDemand = maxDHWDemand

            #Future

            building.future_annualHeatingDemand = future_HD
            building.future_annualCoolingDemand = future_CD
            building.future_annualDHWDemand     = future_DHWD

            building.future_annualHeatingDemandSquareMeter = future_HD / building_grossFloorArea
            building.future_annualCoolingDemandSquareMeter = future_CD / building_grossFloorArea
            building.future_annualDHWDemandSquareMeter     = future_DHWD / building_grossFloorArea

            building.future_maximumHeatingDemand  = future_maxHeatDemand
            building.future_maximumCoolingDemand  = future_maxCoolDemand
            building.future_maximumDHWWaterDemand = future_maxDHWDemand


            building.hourlyBaselineDemandList = hourlyBaselineDataList
            building.hourlyFutureDemandList   = hourlyFutureDataList



        except KeyError:
            self.__log.write_log("ERROR", "calculateConsumptionDemandHourly building id:" + str(building.reference) +  " Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "calculateConsumptionDemandHourly key not found in refurbishment dict for tab key:" + str(building.useMap) + " and row key:" + str(building.period_id))
            raise
        except:
            self.__log.write_log("ERROR", "calculateConsumptionDemandHourly building id:" + str(building.reference))
            self.__log.write_log("ERROR", "calculateConsumptionDemandHourly Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    def calculateTotalizedConsumptionDemand(self):
        try:
            self.baselineTotalizedDemandList = []
            self.futureTotalizedDemandList = []
            
            for data in itertools.product(self.building_uses,self.periodList):
                building_use = data[0]
                period       = data[1]
                
                #Baseline Structure
                baseline_totalized_demand = TotalizedDemand()
                
                baseline_totalized_demand.period_id       = period.id
                baseline_totalized_demand.period_text     = period.period_text
                baseline_totalized_demand.building_use_id = building_use.id
                baseline_totalized_demand.use             = building_use.use
                
                self.baselineTotalizedDemandList.append(baseline_totalized_demand)

                #Future Structure
                future_totalized_demand   = TotalizedDemand()
                
                future_totalized_demand.period_id       = period.id
                future_totalized_demand.period_text     = period.period_text
                future_totalized_demand.building_use_id = building_use.id
                future_totalized_demand.use             = building_use.use

                self.futureTotalizedDemandList.append(future_totalized_demand)

            # Update data with baseline results from database 
            dbList = self.retrieveCompleteTotalizedDemand('Baseline')
            
            for data in self.baselineTotalizedDemandList:
                for totalized in dbList:
                    if data == totalized:
                        data << totalized
                        break
                    
            # Update data with future results from database 
            dbList = self.retrieveCompleteTotalizedDemand('Future')
            
            for data in self.futureTotalizedDemandList:
                for totalized in dbList:
                    if data == totalized:
                        data << totalized
                        break        

            #ADD total section for baseline scenario
            for period in self.periodList:
                total_totalized_demand = TotalizedDemand()
                total_totalized_demand.use = "Total"
                total_totalized_demand.period_id   = period.id
                total_totalized_demand.period_text = period.period_text
                period_data = [data for data in self.baselineTotalizedDemandList if data.period_id == total_totalized_demand.period_id]
                for data in period_data:
                    total_totalized_demand.numberOfBuildings         += data.numberOfBuildings
                    total_totalized_demand.totalGrossFloorArea       += data.totalGrossFloorArea
                    total_totalized_demand.annualUsefulHeatingDemand += data.annualUsefulHeatingDemand
                    total_totalized_demand.annualUsefulCoolingDemand += data.annualUsefulCoolingDemand
                    total_totalized_demand.annualUsefulDHWDemand     += data.annualUsefulDHWDemand
                else:
                    total_totalized_demand.annualUsefulHeatingDemandSquareMeter = total_totalized_demand.annualUsefulHeatingDemand / total_totalized_demand.totalGrossFloorArea if total_totalized_demand.totalGrossFloorArea > 0.0 else 0.0
                    total_totalized_demand.annualUsefulCoolingDemandSquareMeter = total_totalized_demand.annualUsefulCoolingDemand / total_totalized_demand.totalGrossFloorArea if total_totalized_demand.totalGrossFloorArea > 0.0 else 0.0
                    total_totalized_demand.annualUsefulDHWDemandSquareMeter     = total_totalized_demand.annualUsefulDHWDemand     / total_totalized_demand.totalGrossFloorArea if total_totalized_demand.totalGrossFloorArea > 0.0 else 0.0
                    
                self.baselineTotalizedDemandList.append(total_totalized_demand)


            #ADD total section for future scenario
            for period in self.periodList:
                total_totalized_demand = TotalizedDemand()
                total_totalized_demand.use = "Total"
                total_totalized_demand.period_id   = period.id
                total_totalized_demand.period_text = period.period_text
                period_data = [data for data in self.futureTotalizedDemandList if data.period_id == total_totalized_demand.period_id]
                for data in period_data:
                    total_totalized_demand.numberOfBuildings         += data.numberOfBuildings
                    total_totalized_demand.totalGrossFloorArea       += data.totalGrossFloorArea
                    total_totalized_demand.annualUsefulHeatingDemand += data.annualUsefulHeatingDemand
                    total_totalized_demand.annualUsefulCoolingDemand += data.annualUsefulCoolingDemand
                    total_totalized_demand.annualUsefulDHWDemand     += data.annualUsefulDHWDemand
                else:
                    total_totalized_demand.annualUsefulHeatingDemandSquareMeter = total_totalized_demand.annualUsefulHeatingDemand / total_totalized_demand.totalGrossFloorArea if total_totalized_demand.totalGrossFloorArea > 0.0 else 0.0
                    total_totalized_demand.annualUsefulCoolingDemandSquareMeter = total_totalized_demand.annualUsefulCoolingDemand / total_totalized_demand.totalGrossFloorArea if total_totalized_demand.totalGrossFloorArea > 0.0 else 0.0
                    total_totalized_demand.annualUsefulDHWDemandSquareMeter     = total_totalized_demand.annualUsefulDHWDemand     / total_totalized_demand.totalGrossFloorArea if total_totalized_demand.totalGrossFloorArea > 0.0 else 0.0
                self.futureTotalizedDemandList.append(total_totalized_demand)    

        except NoDataFoundException as e:
            self.baselineTotalizedDemandList = []
            self.futureTotalizedDemandList   = []

        except:
            self.__log.write_log("ERROR", "calculateTotalizedConsumptionDemand Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrievePeriodFromYearConstruction(self,reference,yearOfConstruction):
        try:
            retPeriod = None
            for period in self.periodList:
                if period.start_period <= yearOfConstruction <= period.end_period:
                    retPeriod = period
                    break
            #± No period Found
            else:
                raise  NoDataFoundException("No period found for year of construction:" + str(yearOfConstruction))

            return retPeriod


        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrievePeriodFromYearConstruction building id:" + str(reference))
            self.__log.write_log("ERROR", "retrievePeriodFromYearConstruction Unexpected error:" + str(e))
            raise

        except:
            self.__log.write_log("ERROR", "retrievePeriodFromYearConstruction building id:" + str(reference))
            self.__log.write_log("ERROR", "retrievePeriodFromYearConstruction Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    def checkProtectionLevel(self,reference, protectionDegree):
        try:
            protectionLevel = 0
            userProtectionDegree = protectionDegree.lower().strip()
            for protection_level in self.protection_levels:
                if userProtectionDegree == protection_level.user_definition_protection:
                    protectionLevel = protection_level.DMM_protection_level
                    break

            return protectionLevel

        except:
            self.__log.write_log("ERROR", "checkProtectionLevel building id:" + str(reference))
            self.__log.write_log("ERROR", "checkProtectionLevel Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def getLongLatDistrictCentroid(self,building):

        try:
            points = []
            points  = building.districtCentroid.split('#')
            if len(points) < 2:
                self.__log.write_log("ERROR", "getLongLatDistrictCentroid building id:" + str(building.reference))
                self.__log.write_log("ERROR", "getLongLatDistrictCentroid needs 2 points x,y not " + str(len(points)) + " points - " + building.districtCentroid)
                raise
            else:
                building.latitude = float(points[0].replace(",","."))  if isinstance(points[0],str) else float(points[0])
                building.longitude = float(points[1].replace(",","."))  if isinstance(points[1],str) else float(points[1])

        except:
            self.__log.write_log("ERROR", "getLongLatDistrictCentroid building id:" + str(building.reference))
            self.__log.write_log("ERROR", "populate getLongLatDistrictCentroid Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    """ DB access Methods for Alternative Calculate Algorithm """

    def retrieveCompleteScheduledAll(self,building_uses,district_temperature):
        try:

            dataDict =  self.__db.retrieveCompleteScheduledAll(building_uses,district_temperature)

            return dataDict
        except:
            self.__log.write_log("ERROR", "Complete retrieveCompleteScheduled Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    def retrieveCompleteInternalGainsAll(self,buildingUses):
        try:

            dataDict = {}

            for buildingUse in buildingUses:
                    internalGain = self.retrieveCompleteInternalGainByUseId(buildingUse.id)
                    if internalGain:
                        dataDict[buildingUse.use] = internalGain

            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveCompleteInternalGainsAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveCompleteInternalGainByUseId(self,building_use_id):
        try:


            statement = """SELECT internal.id, internal.building_use_id, internal.equipment_internal_gains,
                                  internal.occupancy_internal_gains,internal.lighting_power
                           FROM internal_gains  internal
                           WHERE internal.building_use_id = :building_use_id AND internal.active = 1
                           ORDER BY internal.building_use_id;"""

            bindvars = {'building_use_id':building_use_id}


            data = self.__db.executeStatement(statement,bindvars)


            if data:
                try:
                    internalGain = InternalGain()
                    internalGain.id                       = int(data[0])
                    internalGain.building_use_id          = int(data[1])
                    internalGain.equipment_internal_gains = data[2]
                    internalGain.occupancy_internal_gains = data[3]
                    internalGain.lighting_power           = data[4]

                    return internalGain

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveCompleteInternalGainByUseId create InternalGain" + str(e))


            else:
                raise NoDataFoundException("No record found on table internal_gains for building_use_id:" + str(building_use_id) )



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCompleteInternalGainByUseId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCompleteInternalGainByUseId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveCompleteAnnualDHWDemandAll(self,buildingUses):
        try:

            dataDict = {}

            for buildingUse in buildingUses:
                    annualDHWDemand = self.retrieveCompleteAnnualDHWDemandByUseId(buildingUse.id)
                    if annualDHWDemand:
                        dataDict[buildingUse.use] = annualDHWDemand

            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveCompleteAnnualDHWDemandAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveCompleteAnnualDHWDemandByUseId(self,building_use_id):
        try:


            statement = """SELECT demand.id, demand.building_use_id, demand.DHW_demand_kwhm2
                           FROM annual_DHW_demand  demand
                           WHERE demand.building_use_id = :building_use_id AND demand.active = 1
                           ORDER BY demand.building_use_id;"""

            bindvars = {'building_use_id':building_use_id}


            data = self.__db.executeStatement(statement,bindvars)


            if data:
                try:
                    annualDHWDemand = AnnualDHWDemand()
                    annualDHWDemand.id                       = int(data[0])
                    annualDHWDemand.building_use_id          = int(data[1])
                    annualDHWDemand.DHW_demand_kwhm2         = data[2]


                    return annualDHWDemand

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveCompleteAnnualDHWDemandByUseId create AnnualDHWDemand" + str(e))


            else:
                raise NoDataFoundException("No record found on table annual_DHW_demand for building_use_id:" + str(building_use_id) )



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCompleteAnnualDHWDemandByUseId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCompleteAnnualDHWDemandByUseId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise




    def retrieveCompleteGlazingAll(self,buildingUses):
        try:

            dataDict = {}

            for buildingUse in buildingUses:
                    glazing = self.retrieveCompleteGlazingByUseId(buildingUse.id)
                    if glazing:
                        dataDict[buildingUse.use] = glazing


            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveCompleteGlazingAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveCompleteGlazingByUseId(self,building_use_id):
        try:

            statement = """SELECT glazing.id, glazing.building_use_id, glazing.percentage
                           FROM  glazing  as glazing
                           WHERE glazing.building_use_id = :building_use_id AND glazing.active = 1
                           ORDER BY glazing.building_use_id;"""

            bindvars = {'building_use_id':building_use_id}


            data = self.__db.executeStatement(statement,bindvars)


            if data:
                try:
                    glazing = Glazing()
                    glazing.id                       = int(data[0])
                    glazing.building_use_id          = int(data[1])
                    glazing.percentage               = data[2]

                    return glazing

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveCompleteGlazingByUseId create Glazing " + str(e))


            else:
                raise NoDataFoundException("No record found on table glazing for building_use_id:" + str(building_use_id) )



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCompleteGlazingByUseId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCompleteGlazingByUseId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveEfficiencyImpactAll(self,reburbishment_levels):
        try:

            dataDict = {}

            for refurbishment_level in reburbishment_levels:
                    impact = self.retrieveEfficiencyImpactAllByLevelId(refurbishment_level.id)
                    if impact:
                        dataDict[impact.refurbishment_level] = impact


            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveEfficiencyImpactAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveEfficiencyImpactAllByLevelId(self,refurbishment_level_id):
        try:

            statement = """SELECT impact.id ,impact.refurbishment_level_id,level.level,
                                  impact.roof_economic, impact.roof_environment,
                                  impact.wall_economic,impact.wall_environment,
                                  impact.window_economic,impact.window_environment
                           FROM   efficiency_impact impact INNER JOIN refurbishment_level level ON
                                  impact.refurbishment_level_id = level.id
                           WHERE  impact.refurbishment_level_id = :refurbishment_level_id AND level.active = 1;"""

            bindvars = {'refurbishment_level_id':refurbishment_level_id}


            data = self.__db.executeStatement(statement,bindvars)


            if data:
                try:
                    impact = EfficiencyImpact()
                    impact.id                       = int(data[0])
                    impact.refurbishment_level_id   = int(data[1])
                    impact.refurbishment_level      = data[2]
                    impact.roof_economic            = data[3]
                    impact.roof_environment         = data[4]
                    impact.wall_economic            = data[5]
                    impact.wall_environment         = data[6]
                    impact.window_economic          = data[7]
                    impact.window_environment       = data[8]

                    return impact

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveEfficiencyImpactAllByLevelId create EfficiencyImpact " + str(e))


            else:
                raise NoDataFoundException("No record found on table efficiency_impact for refurbishment_level_id:" + str(refurbishment_level_id))



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveEfficiencyImpactAllByLevelId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveEfficiencyImpactAllByLevelId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    def retrieveCompleteAirLekeageAll(self,country_id,periods):
        try:

            dataDict = {}

            for period in periods:
                    airLeak = self.retrieveCompleteAirLekeageByCountryIdPeriodId(country_id,period.id)
                    if airLeak:
                        dataDict[period.id] = airLeak

            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveCompleteAirLekeageAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise







    def retrieveCompleteAirLekeageByCountryIdPeriodId(self,country_id, period_id):
        try:

            statement = """ SELECT leak.id, leak.country_id, leak.period_id, leak.air_lekeage
                           FROM air_lekeage_distribution leak
                           WHERE leak.country_id = :country_id and  leak.period_id = :period_id;"""

            bindvars = {'country_id':country_id, 'period_id':period_id}


            data = self.__db.executeStatement(statement,bindvars)


            if data:
                try:
                    airLeak = AirLekeageDistribution()
                    airLeak.id          = data[0]
                    airLeak.country_id  = data[1]
                    airLeak.period_id   = data[2]
                    airLeak.air_lekeage = data[3]

                    return airLeak

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveCompleteAirLekeageByCountryIdPeriodId create AirLekeageDistribution " + str(e))


            else:
                raise NoDataFoundException("No record found on table air_lekeage_distribution for country_id:" + str(country_id) + " period_id:" + str(period_id) )



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCompleteAirLekeageByCountryIdPeriodId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCompleteAirLekeageByCountryIdPeriodId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveAirLekeageBuildingDistribution(self):
        try:

            statement = """ SELECT leak.id, leak.walls_perc, leak.ceiling_perc, leak.windows_doors_perc
                           FROM air_lekeage_building_distribution leak;"""


            data = self.__db.executeStatement(statement)


            if data:
                try:
                    airLeakDistribution = AirLekeageBuildingDistribution()
                    airLeakDistribution.id                  = data[0]
                    airLeakDistribution.walls_perc          = data[1]
                    airLeakDistribution.ceiling_perc        = data[2]
                    airLeakDistribution.windows_doors_perc  = data[3]

                    return airLeakDistribution

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveAirLekeageBuildingDistribution create AirLekeageBuildingDistribution " + str(e))


            else:
                raise NoDataFoundException("No record found on table air_lekeage_building_distribution")



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCompleteAirLekeageByCountryIdPeriodId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            raise

        except:
            self.__log.write_log("ERROR", "retrieveAirLekeageBuildingDistribution Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise

    def retrieveCountryById(self,id_country):
        try:

            return self.__db.retrieveCountryById(id_country)

        except:
            self.__log.write_log("ERROR", "Complete retrieveCountryById Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveCompleteSolarGainsByCountryId(self, country_id):
        try:

            dataList = []
            statement = """SELECT solar.id, solar.country_id, solar.dayofyear, solar.hourofday,
                                  solar.wwr_north_non_offices, solar.wwr_south_non_offices,
                                  solar.wwr_east_non_offices, solar.wwr_west_non_offices,
                                  solar.wwr_north_offices, solar.wwr_south_offices,
                                  solar.wwr_east_offices, solar.wwr_west_offices
                           FROM solar_gains as solar
                           WHERE solar.country_id = :country_id
                           ORDER BY solar.dayofyear, solar.hourofday;"""



            bindvars = {'country_id':country_id}

            totalRegs, data_table = self.__db.executeStatementAll(statement,bindvars)



            if data_table:
                for data in data_table:
                    try:
                        solarGain = SolarGain()
                        solarGain.id                        = int(data[0])
                        solarGain.country_id                = int(data[1])
                        solarGain.dayOfYear                 = int(data[2])
                        solarGain.hourOfDay                 = int(data[3])
                        solarGain.wwr_north_non_offices     = data[4]
                        solarGain.wwr_south_non_offices     = data[5]
                        solarGain.wwr_west_non_offices      = data[6]
                        solarGain.wwr_east_non_offices      = data[7]
                        solarGain.wwr_north_offices         = data[8]
                        solarGain.wwr_south_offices         = data[9]
                        solarGain.wwr_east_offices          = data[10]
                        solarGain.wwr_west_offices          = data[11]

                        dataList.append(solarGain)

                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveCompleteSolarGainsByCountryId create SolarGain" + str(e))
                else:
                    return tuple(dataList)
            else:
                raise NoDataFoundException("No record found on table solar_gains" )



        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCompleteSolarGainsByCountryId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)

        except:
            self.__log.write_log("ERROR", "retrieveCompleteSolarGainsByCountryId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise





    def retrieveCompletePeriodsAll(self):

        try:

            return  self.__db.retrievePeriodsAll()
        except:
            self.__log.write_log("ERROR", "retrieveCompletePeriodsAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveCompleteUValuesAll(self,country_id,periods,residential):

        try:

            dataDict = {}

            for period in periods:
                    UValue = self.retrieveCompleteUValuesByCountryIdPeriodId(country_id,period.id,residential)
                    if UValue:
                        dataDict[period.id] = UValue
            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveCompleteUValuesAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveCompleteUValuesByCountryIdPeriodId(self,country_id,period_id,residential):
        try:

            statement = """SELECT u.id, u.country_id, u.period_id, u.residential,
                                  u.roof_u_value, u.wall_u_value, u.window_u_value
                          FROM   u_values u
                          WHERE u.country_id = :country_id AND u.period_id = :period_id AND u.residential = :residential;"""

            bindvars = {'country_id':country_id,'period_id':period_id,'residential':int(residential)}

            data = self.__db.executeStatement(statement,bindvars)

            if data:
                try:
                    uValue = UValues()
                    uValue.id             = data[0]
                    uValue.country_id     = data[1]
                    uValue.period_id      = data[2]
                    uValue.residential    = data[3]
                    uValue.roof_u_value   = data[4]
                    uValue.wall_u_value   = data[5]
                    uValue.window_u_value = data[6]

                    return uValue

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveCompleteUValuesByCountryIdPeriodId create UValues " + str(e))


            else:
                raise NoDataFoundException("No record found on table u_values for country_id:" + str(country_id) + " period_id:" + str(period_id) + " residential:" + str(residential) )

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveCompleteUValuesByCountryIdPeriodId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveCompleteUValuesByCountryIdPeriodId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise





    def retrieveRefurbishmentUValuesAll(self,country_id,refurbishment_levels,residential):

        try:

            dataDict = {}

            for refurbishmentLevel in refurbishment_levels:
                    refurbishmentUValue = self.retrieveRefurbishmentUValuesByCountryIdLevelId(country_id,refurbishmentLevel.id,residential)
                    if refurbishmentUValue:
                        dataDict[refurbishmentLevel.level] = refurbishmentUValue
            return dataDict

        except:
            self.__log.write_log("ERROR", "retrieveRefurbishmentUValuesAll Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def retrieveRefurbishmentUValuesByCountryIdLevelId(self,country_id,refurbishment_level_id,residential):
        try:

            statement = """SELECT  refurbish.id,refurbish.country_id, refurbish.refurbishment_level_id,level.level,
                                   refurbish.residential,refurbish.roof_u_value,refurbish.wall_u_value,refurbish.window_u_value
                           FROM    refurbishment_u_values refurbish INNER JOIN refurbishment_level level ON
                                   refurbish.refurbishment_level_id = level.id
                           WHERE   refurbish.country_id = :country_id AND  refurbish.refurbishment_level_id = :refurbishment_level_id AND 
                                   refurbish.residential = :residential AND level.active = 1;"""

            bindvars = {'country_id':country_id,'refurbishment_level_id':refurbishment_level_id,'residential':int(residential)}

            data = self.__db.executeStatement(statement,bindvars)

            if data:
                try:
                    refurbishmentUValue = RefurbishmentUValues()
                    refurbishmentUValue.id                      = int(data[0])
                    refurbishmentUValue.country_id              = int(data[1])
                    refurbishmentUValue.refurbishment_level_id  = int(data[2])
                    refurbishmentUValue.refurbishment_level     = data[3]
                    refurbishmentUValue.residential             = data[4]
                    refurbishmentUValue.roof_u_value            = data[5]
                    refurbishmentUValue.wall_u_value            = data[6]
                    refurbishmentUValue.window_u_value          = data[7]

                    return refurbishmentUValue

                except Exception as e:
                    self.__log.write_log("ERROR", "retrieveRefurbishmentUValuesByCountryIdLevelId create RefurbishmentUValues " + str(e))


            else:
                raise NoDataFoundException("No record found on table refurbishment_u_values for country_id:" + str(country_id) + " refurbishment_level_id:" + str(refurbishment_level_id) + " residential:" + str(residential) )

        except NoDataFoundException as e:
            self.__log.write_log("ERROR", "retrieveRefurbishmentUValuesByCountryIdLevelId " + str(e))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
            raise

        except:
            self.__log.write_log("ERROR", "retrieveRefurbishmentUValuesByCountryIdLevelId Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def generateRefurbishmentAirlossTable(self,country_id,airLekeageDict, periods, refurbishment_levels):
        try:

            for period in periods:

                airLekeage = airLekeageDict[period.id]
                levelAirLossDict={}

                for refurbishment_level in refurbishment_levels:

                    air_lekeage = 0.0

                    refurbishmentAirLoss = RefurbishmentAirLoss()
                    refurbishmentAirLoss.id                      = 0
                    refurbishmentAirLoss.country_id              = country_id
                    refurbishmentAirLoss.period_id               = period.id
                    refurbishmentAirLoss.refurbishment_level_id  = refurbishment_level.id
                    refurbishmentAirLoss.refurbishment_level     = refurbishment_level.level



                    if refurbishment_level.level.lower() == "low":
                        air_lekeage = 0.6 if airLekeage.air_lekeage < 0.6 or airLekeage.air_lekeage * 0.85 < 0.6 else airLekeage.air_lekeage * 0.85

                    elif refurbishment_level.level.lower() == "medium":
                        valueLow  = 0.6 if airLekeage.air_lekeage < 0.6 or airLekeage.air_lekeage * 0.85 < 0.6 else airLekeage.air_lekeage * 0.85
                        valueHigh = 0.6 if airLekeage.air_lekeage < 0.6 or airLekeage.air_lekeage * 0.6 < 0.6 else airLekeage.air_lekeage * 0.6
                        air_lekeage = 0.6 if (valueLow + valueHigh)/2 < 0.6 else (valueLow + valueHigh)/2

                    elif refurbishment_level.level.lower() == "high":
                        air_lekeage = 0.6 if airLekeage.air_lekeage < 0.6 or airLekeage.air_lekeage * 0.6 < 0.6 else airLekeage.air_lekeage * 0.6
                    else:
                        air_lekeage = airLekeage.air_lekeage

                    refurbishmentAirLoss.air_lekeage = air_lekeage
                    levelAirLossDict[refurbishment_level.level] = refurbishmentAirLoss

                self.refurbishmentAirLossDict[period.id] = levelAirLossDict

            return self.refurbishmentAirLossDict

        except:
            self.__log.write_log("ERROR", "Complete generateRefurbishmentAirlossTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def convertTabDataListToDict(self, refurbishmentTabDataList):
        try:
            tabDataDict = {data.tab_name:data for data in refurbishmentTabDataList}
            for key, value in tabDataDict.items():
                tabRowsDict = {data.row_period_id:data for data in value.rows}
                tabDataDict[key].rows=tabRowsDict

            return tabDataDict

        except:
            self.__log.write_log("ERROR", "Complete convertTabDataListToDict Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



    def convertProtectionLevelListToDict(self, protectionLevelList):
        try:
            protectionLevelDict = {data.protectionLevel:data for data in protectionLevelList}
            return protectionLevelDict

        except:
            self.__log.write_log("ERROR", "Complete convertProtectionLevelListToDict Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise

    def retrieveAvgLocationTemperature(self, location_id):
        try:

            location_temperature_list = self.__db.retrieveAvgLocationTemperature(location_id)


            return tuple([location_temperature.temperature for location_temperature in location_temperature_list])

        except:
            self.__log.write_log("ERROR", "Complete retrieveAvgLocationTemperature Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    def retrieveCompleteTotalizedDemand(self,scenario):
        try:
            totalizedDemandList = list()

            statement = """SELECT  total_demand.scenario, total_demand.building_use_id, use.use, period_id, period.period_text,
                                   COUNT(1)as "Number of buildings",SUM(total_demand.gross_floor_area) as gross_floor_area,
                                   SUM(total_demand.annual_useful_heating_demand) as annual_useful_heating_demand,
                                   SUM(total_demand.annual_useful_cooling_demand) as annual_useful_cooling_demand,
                                   SUM(total_demand.annual_useful_DHW_demand)as annual_useful_DHW_demand,
                                   (SUM(total_demand.annual_useful_heating_demand)/ SUM(total_demand.gross_floor_area))as  annual_useful_heating_demand_m2,
                                   (SUM(total_demand.annual_useful_cooling_demand)/ SUM(total_demand.gross_floor_area))as  annual_useful_cooling_demand_m2,
                                   (SUM(total_demand.annual_useful_DHW_demand)/ SUM(total_demand.gross_floor_area))as  annual_useful_DHW_demand_m2
                            FROM calculate_complete_totalized_demand as total_demand INNER JOIN period as period ON
                                 total_demand.period_id = period.id INNER JOIN building_use use ON total_demand.building_use_id = use.id
                            WHERE total_demand.process_name = :process_name AND total_demand.scenario = :scenario AND use.active = 1  AND period.active = 1
                            GROUP BY total_demand.scenario, total_demand.building_use_id, use.use, total_demand.period_id, period.period_text
                            ORDER BY total_demand.building_use_id, total_demand.period_id;"""


            bindvars = {'process_name':self.__planHeatDMM.resources.processName,'scenario':scenario}

            totalRegs, data_table = self.__db.executeStatementAll(statement,bindvars)

            if data_table:
                for data in data_table:
                    try:
                        totalizedDemand = TotalizedDemand()
                        totalizedDemand.scenario                          = data[0]
                        totalizedDemand.building_use_id                     = int(data[1])
                        totalizedDemand.use                                 = data[2]
                        totalizedDemand.period_id                           = int(data[3])
                        totalizedDemand.period_text                         = data[4]
                        totalizedDemand.numberOfBuildings                   = int(data[5])
                        totalizedDemand.totalGrossFloorArea                 = data[6]
                        totalizedDemand.annualUsefulHeatingDemand           = data[7]
                        totalizedDemand.annualUsefulCoolingDemand           = data[8]
                        totalizedDemand.annualUsefulDHWDemand               = data[9]

                        totalizedDemand.annualUsefulHeatingDemandSquareMeter= data[10]
                        totalizedDemand.annualUsefulCoolingDemandSquareMeter= data[11]
                        totalizedDemand.annualUsefulDHWDemandSquareMeter    = data[12]


                        totalizedDemandList.append(totalizedDemand)


                    except Exception as e:
                        self.__log.write_log("ERROR", "retrieveCompleteTotalizedDemand create TotalizedDemand " + str(e))
                else:
                    return totalizedDemandList
            else:
                raise NoDataFoundException("No record found on table calculate_complete_totalized_demand")

        except NoDataFoundException as e:
            self.__log.write_log("WARNING", "retrieveCompleteTotalizedDemand " + str(e))
            self.__log.write_log("WARNING", "statement: " + statement)
            if bindvars:
                self.__log.write_log("WARNING", "bindvars: " + str(bindvars))
            raise NoDataFoundException

        except:
            self.__log.write_log("ERROR", "retrieveCompleteTotalizedDemand Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.__log.write_log("ERROR", "statement: " + statement)
            if bindvars:
                self.__log.write_log("ERROR", "bindvars: " + str(bindvars))
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
            self.__log.write_log("ERROR", "Alternative retrieveOutputFields Error:" + scenario +  " fileType:" + fileType +  "  fileCategory:" + fileCategory + " CalculateModel:" + calculateModel)
            self.__log.write_log("ERROR", "Alternative retrieveOutputFields Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise


    def insert_building_calculate_totalized_demand(self,building, scenario):
        try:

            statement = """INSERT INTO calculate_complete_totalized_demand
                           (process_name,scenario, building_id, period_id,building_use_id,gross_floor_area,
                            annual_useful_heating_demand,annual_useful_cooling_demand,annual_useful_DHW_demand)
                           VALUES(:process_name,:scenario, :building_id,:period_id,:building_use_id,:gross_floor_area,
                                  :annual_useful_heating_demand,:annual_useful_cooling_demand,:annual_useful_DHW_demand);"""
            #Baseline scenario
            if scenario == "Baseline":
                bindvars = {'process_name':self.__planHeatDMM.resources.processName,'scenario':scenario,'building_id':building.reference,
                            'period_id':building.period_id,'building_use_id':building.useId,'gross_floor_area':building.grossFloorArea,
                            'annual_useful_heating_demand':building.annualHeatingDemand,
                            'annual_useful_cooling_demand':building.annualCoolingDemand,
                            'annual_useful_DHW_demand':building.annualDHWDemand
                           }
            #Future scenario
            else:
                bindvars = {'process_name':self.__planHeatDMM.resources.processName,'scenario':scenario,'building_id':building.reference,
                            'period_id':building.period_id,'building_use_id':building.useId,'gross_floor_area':building.grossFloorArea,
                            'annual_useful_heating_demand':building.future_annualHeatingDemand,
                            'annual_useful_cooling_demand':building.future_annualCoolingDemand,
                            'annual_useful_DHW_demand':building.future_annualDHWDemand
                           }

            self.__db.insert_record_table(statement,bindvars)


        except:
            self.__log.write_log("ERROR", "insert_building_calculate_totalized_demand building_id:{}".format(building.reference))
            self.__log.write_log("ERROR", "insert_building_calculate_totalized_demand Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise



if __name__ == '__main__':
    from model.building_use_map import BuildingUseMap

    buildingUseMapList = []
    building_use_map = {}

    build1 = BuildingUseMap()
    build1.user_definition_use = "hola"
    build1.DMM_use = 'Adios'
    buildingUseMapList.append(build1)
    build2 = BuildingUseMap()
    build2.user_definition_use = "hello"
    build2.DMM_use = 'bye'
    buildingUseMapList.append(build2)
    for useMap in buildingUseMapList:
        building_use_map[useMap.user_definition_use] = useMap.DMM_use

    #print(building_use_map)

