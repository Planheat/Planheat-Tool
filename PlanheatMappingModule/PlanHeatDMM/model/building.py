# -*- coding: utf-8 -*-
"""
   Model Map building CSV   
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 15 sept. 2017
"""
__docformat__ = "restructuredtext"

import sys


class Building():
    """ Building data use for process and output files """

    __slots__ = ('_Building__log','Regstatus', 'Regprocess', '_Building__projectID', '_Building__areaID', '_Building__countryID', '_Building__country', '_Building__reference', '_Building__centroid', '_Building__totalHeight', '_Building__numberOfFloors', '_Building__footPrintArea', '_Building__grossFloorArea', '_Building__roofArea', '_Building__totalEnvelopeArea', '_Building__exteriorEnvelopeArea', '_Building__adjoiningEnvelopeArea', '_Building__northExteriorEnvelopeArea', '_Building__southExteriorEnvelopeArea', '_Building__westExteriorEnvelopeArea', '_Building__eastExteriorEnvelopeArea', '_Building__yearOfConstruction', '_Building__use', '_Building__protectionDegree', '_Building__refurbished', '_Building__windowPercentage', '_Building__parcelID', '_Building__volume', '_Building__districtCentroid', '_Building__longitude', '_Building__latitude', '_Building__shpGeometryData', '_Building__shpRecordData', '_Building__period_id', '_Building__period_text', '_Building__north_opaque_facade_area', '_Building__south_opaque_facade_area', '_Building__east_opaque_facade_area', '_Building__west_opaque_facade_area', '_Building__opaqueFacadeArea', '_Building__north_window_area', '_Building__south_window_area', '_Building__east_window_area', '_Building__west_window_area', '_Building__windowArea', '_Building__useId', '_Building__useMap', '_Building__nonOffice', '_Building__floor_height', '_Building__protectionLevel', '_Building__hourlyBaselineDemandList', '_Building__hourlyFutureDemandList', '_Building__equipment_intenal_gains', '_Building__occupancy_internal_gains', '_Building__light_intenal_gains', '_Building__ACH', '_Building__AU_value', '_Building__roof_u_value', '_Building__wall_u_value', '_Building__window_u_value', '_Building__annualHeatingDemand', '_Building__annualCoolingDemand', '_Building__annualDHWDemand', '_Building__annualHeatingDemandSquareMeter', '_Building__annualCoolingDemandSquareMeter', '_Building__annualDHWDemandSquareMeter', '_Building__maximumHeatingDemand', '_Building__maximumCoolingDemand', '_Building__maximumDHWWaterDemand', '_Building__future_refurbishment', '_Building__future_refurbishment_level', '_Building__future_refurbishment_selected_roof_perc', '_Building__future_refurbishment_selected_wall_perc', '_Building__future_refurbishment_selected_window_perc', '_Building__future_refurbishment_selected_air_loss_perc', '_Building__economic_impact', '_Building__environment_impact', '_Building__future_AU_value', '_Building__future_ACH', '_Building__future_roof_u_value', '_Building__future_wall_u_value', '_Building__future_window_u_value', '_Building__future_annualHeatingDemand', '_Building__future_annualCoolingDemand', '_Building__future_annualDHWDemand', '_Building__future_annualHeatingDemandSquareMeter', '_Building__future_annualCoolingDemandSquareMeter', '_Building__future_annualDHWDemandSquareMeter', '_Building__future_maximumHeatingDemand', '_Building__future_maximumCoolingDemand', '_Building__future_maximumDHWWaterDemand')
    
    def __init__(self,log,projectName,areaName,country_id,param):
        '''
        Constructor
        '''
        
        try:
            
            # Common data 
            self.__log = log
            
            self.Regstatus  = True
            self.Regprocess = True
            
            self.__projectID                = projectName
            self.__areaID                   = areaName
            self.__countryID                = country_id
            self.__country                  = ""
            
             
            self.__reference                = param.Reference
            self.__centroid                 = param.Centroid
            self.__totalHeight              = param.TotalHeight
            
            self.__numberOfFloors           = param.NumberOfFloors
            self.__footPrintArea            = param.FootPrintArea
            self.__grossFloorArea           = param.GrossFloorArea
            self.__roofArea                 = param.RoofArea
            self.__totalEnvelopeArea        = param.TotalEnvelopeArea
            self.__exteriorEnvelopeArea     = param.ExteriorEnvelopeArea
            self.__adjoiningEnvelopeArea    = param.AdjoiningEnvelopeArea
            self.__northExteriorEnvelopeArea= param.NorthExteriorEnvelopeArea
            self.__southExteriorEnvelopeArea= param.SouthExteriorEnvelopeArea
            self.__westExteriorEnvelopeArea = param.WestExteriorEnvelopeArea
            self.__eastExteriorEnvelopeArea = param.EastExteriorEnvelopeArea
            self.__yearOfConstruction       = param.YearOfConstruction
            self.__use                      = param.Use
            self.__protectionDegree         = param.ProtectionDegree
            self.__refurbished              = param.Refurbished
            self.__windowPercentage         = param.WindowPercentage
            self.__parcelID                 = param.ParcelID
            self.__volume                   = param.Volume
            
            self.__districtCentroid         = param.DistrictCentroid
            
            """
            self.__reference                = param['Reference']
            self.__centroid                 = param.get('Centroid')
            self.__totalHeight              = param['TotalHeight']
            
            self.__numberOfFloors           = param.get('NumberOfFloors')
            self.__footPrintArea            = param.get('FootPrintArea')
            self.__grossFloorArea           = param.get('GrossFloorArea')
            self.__roofArea                 = param.get('RoofArea')
            self.__totalEnvelopeArea        = param.get('TotalEnvelopeArea')
            self.__exteriorEnvelopeArea     = param.get('ExteriorEnvelopeArea')
            self.__adjoiningEnvelopeArea    = param.get('AdjoiningEnvelopeArea',0.0)
            self.__northExteriorEnvelopeArea= param.get('NorthExteriorEnvelopeArea',0.0)
            self.__southExteriorEnvelopeArea= param.get('SouthExteriorEnvelopeArea',0.0)
            self.__westExteriorEnvelopeArea = param.get('WestExteriorEnvelopeArea',0.0)
            self.__eastExteriorEnvelopeArea = param.get('EastExteriorEnvelopeArea',0.0)
            self.__yearOfConstruction       = param.get('YearOfConstruction')
            self.__use                      = param.get('Use')
            self.__protectionDegree         = param.get('ProtectionDegree')
            self.__refurbished              = param.get('Refurbished','')
            self.__windowPercentage         = param.get('WindowPercentage','')
            self.__parcelID                 = param.get('ParcelID','')
            self.__volume                   = param.get('Volume')
            
            self.__districtCentroid         = param['DistrictCentroid']
            """
            
            
            #Centroid
            self.__longitude                = 0.0
            self.__latitude                 = 0.0
            
            # SHAPE
            self.__shpGeometryData     = None
            self.__shpRecordData       = None 
            
            
            #CSV COMPLETE  OUT Fields           
            
            self.__period_id            = None
            self.__period_text          = None
            
            self.__north_opaque_facade_area    = 0.0
            self.__south_opaque_facade_area    = 0.0
            self.__east_opaque_facade_area     = 0.0
            self.__west_opaque_facade_area     = 0.0
            self.__opaqueFacadeArea            = 0.0
            self.__north_window_area    = 0.0
            self.__south_window_area    = 0.0
            self.__east_window_area     = 0.0
            self.__west_window_area     = 0.0
            self.__windowArea           = 0.0
            
            self.__useId                = 0
            self.__useMap               = ""
            self.__nonOffice            = None
            self.__floor_height           = 0.0
            self.__protectionLevel      = 0
            
          
            #List hourly data demand
            self.__hourlyBaselineDemandList = []
            self.__hourlyFutureDemandList   = []

            
            # Baseline Calculated
            self.__equipment_intenal_gains  = 0.0
            self.__occupancy_internal_gains = 0.0
            self.__light_intenal_gains      = 0.0
            self.__ACH                  = 0.0 
            self.__AU_value             = 0.0
            self.__roof_u_value         = 0.0
            self.__wall_u_value         = 0.0
            self.__window_u_value       = 0.0
            
            
            self.__annualHeatingDemand  = 0.0
            self.__annualCoolingDemand  = 0.0
            self.__annualDHWDemand      = 0.0
            self.__annualHeatingDemandSquareMeter = 0.0
            self.__annualCoolingDemandSquareMeter = 0.0
            self.__annualDHWDemandSquareMeter     = 0.0
            self.__maximumHeatingDemand   = 0.0
            self.__maximumCoolingDemand   = 0.0
            self.__maximumDHWWaterDemand  = 0.0
            
            #Future General Data
            self.__future_refurbishment                       = False
            self.__future_refurbishment_level                 = "None"  
            self.__future_refurbishment_selected_roof_perc    = 0.0
            self.__future_refurbishment_selected_wall_perc    = 0.0
            self.__future_refurbishment_selected_window_perc  = 0.0
            self.__future_refurbishment_selected_air_loss_perc= 0.0
            
            #Future economic and environment impact
            self.__economic_impact          = 0.0
            self.__environment_impact       = 0.0
            
            # Future Calculated 
            self.__future_AU_value             = 0.0
            self.__future_ACH                  = 0.0
            self.__future_roof_u_value         = 0.0
            self.__future_wall_u_value         = 0.0
            self.__future_window_u_value       = 0.0
            
            
            self.__future_annualHeatingDemand = 0.0
            self.__future_annualCoolingDemand = 0.0
            self.__future_annualDHWDemand     = 0.0
            self.__future_annualHeatingDemandSquareMeter = 0.0
            self.__future_annualCoolingDemandSquareMeter = 0.0
            self.__future_annualDHWDemandSquareMeter     = 0.0
            self.__future_maximumHeatingDemand  = 0.0
            self.__future_maximumCoolingDemand  = 0.0
            self.__future_maximumDHWWaterDemand = 0.0
           
            
        except KeyError:
            self.__log.write_log("ERROR", "Building __init__ key not exist: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
            self.Regstatus = False
            
        except AttributeError:
            self.__log.write_log("ERROR", "Building __init__ Attribute not exist: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
            self.Regstatus = False    
        
        except:
            self.__log.write_log("ERROR", "Building __init__ Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.Regstatus= False
        
    def __str__(self):      
        try:
            text = "Project Id:" + str(self.__projectID) + " area Id:" + str(self.__areaID) + " Country Id:" + str(self.__countryID) + " country" + str(self.country)  \
                    + " Building Id:" + str(self.__reference)  + " footPrintArea:" + str(self.__footPrintArea) +   " centroid:" +  str(self.centroid) + \
            " totalHeight:" + str(self.totalHeight) +  " numberOfFloors:" + str(self.numberOfFloors) +  " footPrintArea:" +  str(self.footPrintArea) + \
            " grossFloorArea:" + str(self.grossFloorArea) +  " roofArea:" +       str(self.roofArea) +  " totalEnvelopeArea:" + str(self.totalEnvelopeArea) + \
            " exteriorEnvelopeArea :" + str(self.exteriorEnvelopeArea) + " yearOfConstruction:" +  str(self.yearOfConstruction) + " use:" +  str(self.use)  + \
            " protectionDegree:" +   str(self.protectionDegree) + " volume:" + str(self.volume)  + " districtCentroid:" +   str(self.districtCentroid) + \
            " adjoiningEnvelopeArea:" +    str(self.adjoiningEnvelopeArea) + " northExteriorEnvelopeArea:" + str(self.northExteriorEnvelopeArea) + \
            " southExteriorEnvelopeArea:" + str(self.southExteriorEnvelopeArea) + " westExteriorEnvelopeArea:" + str(self.westExteriorEnvelopeArea) + \
            " eastExteriorEnvelopeArea:" + str(self.eastExteriorEnvelopeArea) + " annualHeatingDemand:" +  str(self.annualHeatingDemand) + \
            " annualHeatingDemandSquareMeter:" +    str(self.annualHeatingDemandSquareMeter) + " annualCoolingDemand:" +    str(self.annualCoolingDemand) + \
            " annualCoolingDemandSquareMeter:" +    str(self.annualCoolingDemandSquareMeter) + " annualDHWDemand:" +    str(self.annualDHWDemand) + \
            " annualDHWDemandSquareMeter:" +    str(self.annualDHWDemandSquareMeter) + " maximumHeatingDemand:" +    str(self.maximumHeatingDemand) + \
            " maximumCoolingDemand:" +    str(self.maximumCoolingDemand) + " maximumDHWWaterDemand:" +    str(self.maximumDHWWaterDemand) 
                    
            return text
        
        except:
            self.__log.write_log("ERROR", "__str__ Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        
    
    
    
         
    @property
    def projectID(self):
        return self.__projectID
    
    @projectID.setter
    def projectID(self, val):
        self.__projectID = val
    
    @property
    def areaID(self):
        return self.__areaID
    
    @areaID.setter
    def areaID(self, val):
        self.__areaID = val
    
    
    @property
    def countryID(self):
        return self.__countryID
    
    @countryID.setter
    def countryID(self, val):
        self.__countryID = val
    
    
    @property
    def country(self):
        return self.__country
    
    @country.setter
    def country(self, val):
        self.__country = val
      
        
    @property
    def reference(self):
        return self.__reference
    
    @reference.setter
    def reference(self, val):
        self.__reference = val    
    
    @property
    def centroid(self):
        return self.__centroid
    
    @centroid.setter
    def centroid (self, val):
        self.__centroid = val     
        
    @property
    def totalHeight(self):
        return self.__totalHeight
    
    @totalHeight.setter
    def totalHeight (self, val):
        self.__totalHeight = val         
        
    @property
    def numberOfFloors(self):
        return self.__numberOfFloors
    
    @numberOfFloors.setter
    def numberOfFloors(self, val):
        self.__numberOfFloors = val     
        
    @property
    def grossFloorArea(self):
        return self.__grossFloorArea
    
    @grossFloorArea.setter
    def grossFloorArea(self, val):
        self.__grossFloorArea = val
 
    @property
    def roofArea(self):
        return self.__roofArea
    
    @roofArea.setter
    def roofArea(self, val):
        self.__roofArea = val  
    
    @property
    def totalEnvelopeArea(self):
        return self.__totalEnvelopeArea
    
    @totalEnvelopeArea.setter
    def totalEnvelopeArea(self, val):
        self.__totalEnvelopeArea = val
    
    
    @property
    def footPrintArea(self):
        return self.__footPrintArea
    
    @footPrintArea.setter
    def footPrintArea(self, val):
        self.__footPrintArea = val
    
    @property
    def exteriorEnvelopeArea(self):
        return self.__exteriorEnvelopeArea
    
    @exteriorEnvelopeArea.setter
    def exteriorEnvelopeArea(self, val):
        self.__exteriorEnvelopeArea = val 
        
        
    @property
    def adjoiningEnvelopeArea(self):
        return self.__adjoiningEnvelopeArea
    
    @adjoiningEnvelopeArea.setter
    def adjoiningEnvelopeArea(self, val):
        self.__adjoiningEnvelopeArea = val        
    
    @property
    def northExteriorEnvelopeArea(self):
        return self.__northExteriorEnvelopeArea
    
    @northExteriorEnvelopeArea.setter
    def northExteriorEnvelopeArea(self, val):
        self.__northExteriorEnvelopeArea = val 
        
        
    @property
    def southExteriorEnvelopeArea(self):
        return self.__southExteriorEnvelopeArea
    
    @southExteriorEnvelopeArea.setter
    def southExteriorEnvelopeArea(self, val):
        self.__southExteriorEnvelopeArea = val
    
    @property
    def westExteriorEnvelopeArea(self):
        return self.__westExteriorEnvelopeArea
    
    @westExteriorEnvelopeArea.setter
    def westExteriorEnvelopeArea(self, val):
        self.__westExteriorEnvelopeArea = val 
    @property
    def eastExteriorEnvelopeArea(self):
        return self.__eastExteriorEnvelopeArea
    
    @eastExteriorEnvelopeArea.setter
    def eastExteriorEnvelopeArea(self, val):
        self.__eastExteriorEnvelopeArea = val     

    
    @property
    def yearOfConstruction(self):
        return self.__yearOfConstruction
    
    @yearOfConstruction.setter
    def yearOfConstruction(self, val):
        self.__yearOfConstruction = val 
 
 
    @property
    def use(self):
        return self.__use
    
    @use.setter
    def use(self, val):
        self.__use = val

    @property
    def protectionDegree(self):
        return self.__protectionDegree
    
    @protectionDegree.setter
    def protectionDegree(self, val):
        self.__protectionDegree = val

  
    @property
    def refurbished(self):
        return self.__refurbished
    
    @refurbished.setter
    def refurbished(self, val):
        self.__refurbished = val


    @property
    def windowPercentage(self):
        return self.__windowPercentage
    
    @windowPercentage.setter
    def windowPercentage(self, val):
        self.__windowPercentage = val
  
  
    @property
    def parcelID(self):
        return self.__parcelID
    
    @parcelID.setter
    def parcelID(self, val):
        self.__parcelID = val
        
        
    @property
    def volume(self):
        return self.__volume
    
    @volume.setter
    def volume(self, val):
        self.__volume = val    
        
        
    @property
    def districtCentroid(self):
        return self.__districtCentroid
    
    @districtCentroid.setter
    def districtCentroid(self, val):
        self.__districtCentroid = val     
        

    @property
    def period_id(self):
        return self.__period_id
    
    @period_id.setter
    def period_id(self, val):
        self.__period_id = val          

    
    @property
    def period_text(self):
        return self.__period_text
    
    @period_text.setter
    def period_text(self, val):
        self.__period_text = val    
    
    
    @property
    def useId(self):
        return self.__useId
    
    @useId.setter
    def useId(self, val):
        self.__useId = val
    
    @property
    def useMap(self):
        return self.__useMap
    
    @useMap.setter
    def useMap(self, val):
        self.__useMap = val

    
    @property
    def nonOffice(self):
        return self.__nonOffice
    
    @nonOffice.setter
    def nonOffice(self, val):
        self.__nonOffice = bool(val)
    
    
    @property
    def floor_height(self):
        return self.__floor_height
    
    @floor_height.setter
    def floor_height(self, val):
        self.__floor_height = val
    
    
    @property
    def north_opaque_facade_area(self):
        return self.__north_opaque_facade_area

    @north_opaque_facade_area.setter
    def north_opaque_facade_area(self, val):
        self.__north_opaque_facade_area = val
        
    
    @property
    def south_opaque_facade_area(self):
        return self.__south_opaque_facade_area

    @south_opaque_facade_area.setter
    def south_opaque_facade_area(self, val):
        self.__south_opaque_facade_area = val  
           

    @property
    def east_opaque_facade_area(self):
        return self.__east_opaque_facade_area

    @east_opaque_facade_area.setter
    def east_opaque_facade_area(self, val):
        self.__east_opaque_facade_area = val   
    
    @property
    def west_opaque_facade_area(self):
        return self.__west_opaque_facade_area

    @west_opaque_facade_area.setter
    def west_opaque_facade_area(self, val):
        self.__west_opaque_facade_area = val   


    @property
    def opaqueFacadeArea(self):
        return self.__opaqueFacadeArea

    @opaqueFacadeArea.setter
    def opaqueFacadeArea(self, val):
        self.__opaqueFacadeArea = val       
    
    
    @property
    def north_window_area(self):
        return self.__north_window_area
    
    @north_window_area.setter
    def north_window_area(self, val):
        self.__north_window_area = val   
        
        
    @property
    def south_window_area(self):
        return self.__south_window_area
    
    @south_window_area.setter
    def south_window_area(self, val):
        self.__south_window_area = val       
    
    
    @property
    def east_window_area(self):
        return self.__east_window_area
    
    @east_window_area.setter
    def east_window_area(self, val):
        self.__east_window_area = val
        
    
    @property
    def west_window_area(self):
        return self.__west_window_area
    
    @west_window_area.setter
    def west_window_area(self, val):
        self.__west_window_area = val
        
        
    @property
    def windowArea(self):
        return self.__windowArea
    
    @windowArea.setter
    def windowArea(self, val):
        self.__windowArea = val   
            


    @property
    def protectionLevel(self):
        return self.__protectionLevel
    
    @protectionLevel.setter
    def protectionLevel(self, val):
        self.__protectionLevel = val          

    
    @property
    def equipment_intenal_gains(self):
        return self.__equipment_intenal_gains
    
    @equipment_intenal_gains.setter
    def equipment_intenal_gains(self, val):
        self.__equipment_intenal_gains = val  
        
        
    @property
    def occupancy_internal_gains(self):
        return self.__occupancy_internal_gains
    
    @occupancy_internal_gains.setter
    def occupancy_internal_gains(self, val):
        self.__occupancy_internal_gains = val
    
    
    @property
    def light_intenal_gains(self):
        return self.__light_intenal_gains
    
    @light_intenal_gains.setter
    def light_intenal_gains(self, val):
        self.__light_intenal_gains = val
        
        
        
    @property
    def ACH(self):
        return self.__ACH
    
    @ACH.setter
    def ACH(self, val):
        self.__ACH = val    
    
        
    @property
    def AU_value(self):
        return self.__AU_value
    
    @AU_value.setter
    def AU_value(self, val):
        self.__AU_value = val    


    @property
    def roof_u_value(self):
        return self.__roof_u_value
    
    @roof_u_value.setter
    def roof_u_value(self, val):
        self.__roof_u_value = val 
        
    
    @property
    def wall_u_value(self):
        return self.__wall_u_value
    
    @wall_u_value.setter
    def wall_u_value(self, val):
        self.__wall_u_value = val     

    
    @property
    def window_u_value(self):
        return self.__window_u_value
    
    @window_u_value.setter
    def window_u_value(self, val):
        self.__window_u_value = val            

     
    @property
    def longitude(self):
        return self.__longitude
    
    @longitude.setter
    def longitude(self, val):
        self.__longitude = val          
    
    @property
    def latitude(self):
        return self.__latitude
    
    @latitude.setter
    def latitude(self, val):
        self.__latitude = val    
    
    @property
    def shpGeometryData(self):
        return self.__shpGeometryData
    
    @shpGeometryData.setter
    def shpGeometryData(self, val):
        self.__shpGeometryData = val    


    @property
    def shpRecordData(self):
        return self.__shpRecordData
    
    @shpRecordData.setter
    def shpRecordData(self, val):
        self.__shpRecordData = val                   
    

    @property
    def hourlyBaselineDemandList(self):
        return self.__hourlyBaselineDemandList
    
    @hourlyBaselineDemandList.setter
    def hourlyBaselineDemandList(self, val):
        self.__hourlyBaselineDemandList = val    
    
    
    @property
    def hourlyFutureDemandList(self):
        return self.__hourlyFutureDemandList
    
    @hourlyFutureDemandList.setter
    def hourlyFutureDemandList(self, val):
        self.__hourlyFutureDemandList = val    
    
    
    #Baseline
    
    @property
    def annualHeatingDemand(self):
        return self.__annualHeatingDemand
    
    @annualHeatingDemand.setter
    def annualHeatingDemand(self, val):
        self.__annualHeatingDemand = val                   
    
    
    @property
    def annualHeatingDemandSquareMeter(self):
        return self.__annualHeatingDemandSquareMeter
    
    @annualHeatingDemandSquareMeter.setter
    def annualHeatingDemandSquareMeter(self, val):
        self.__annualHeatingDemandSquareMeter = val                   
    
   
    @property
    def annualCoolingDemand(self):
        return self.__annualCoolingDemand
    
    @annualCoolingDemand.setter
    def annualCoolingDemand(self, val):
        self.__annualCoolingDemand = val   
    
            
    @property
    def annualCoolingDemandSquareMeter(self):
        return self.__annualCoolingDemandSquareMeter
    
    @annualCoolingDemandSquareMeter.setter
    def annualCoolingDemandSquareMeter(self, val):
        self.__annualCoolingDemandSquareMeter = val          
        
            
    @property
    def annualDHWDemand(self):
        return self.__annualDHWDemand
    
    @annualDHWDemand.setter
    def annualDHWDemand(self, val):
        self.__annualDHWDemand = val          
        
            
    @property
    def annualDHWDemandSquareMeter(self):
        return self.__annualDHWDemandSquareMeter
    
    @annualDHWDemandSquareMeter.setter
    def annualDHWDemandSquareMeter(self, val):
        self.__annualDHWDemandSquareMeter = val          
            
            
    @property
    def maximumHeatingDemand(self):
        return self.__maximumHeatingDemand
    
    @maximumHeatingDemand.setter
    def maximumHeatingDemand(self, val):
        self.__maximumHeatingDemand = val          
                    
    
    @property
    def maximumCoolingDemand(self):
        return self.__maximumCoolingDemand
    
    @maximumCoolingDemand.setter
    def maximumCoolingDemand(self, val):
        self.__maximumCoolingDemand = val          

            
    @property
    def maximumDHWWaterDemand(self):
        return self.__maximumDHWWaterDemand
    
    @maximumDHWWaterDemand.setter
    def maximumDHWWaterDemand(self, val):
        self.__maximumDHWWaterDemand = val          
    
    
    # Future 
        
    @property
    def future_AU_value(self):
        return self.__future_AU_value
    
    @future_AU_value.setter
    def future_AU_value(self, val):
        self.__future_AU_value = val              


    @property
    def future_ACH(self):
        return self.__future_ACH
    
    @future_ACH.setter
    def future_ACH(self, val):
        self.__future_ACH = val 
            
   
    @property
    def future_roof_u_value(self):
        return self.__future_roof_u_value
    
    @future_roof_u_value.setter
    def future_roof_u_value(self, val):
        self.__future_roof_u_value = val
        

    @property
    def future_wall_u_value(self):
        return self.__future_wall_u_value
    
    
    @future_wall_u_value.setter
    def future_wall_u_value(self, val):
        self.__future_wall_u_value = val                  
        
    @property
    def future_window_u_value(self):
        return self.__future_window_u_value
    
    @future_window_u_value.setter
    def future_window_u_value(self, val):
        self.__future_window_u_value = val   
        
        
    @property
    def future_annualHeatingDemand(self):
        return self.__future_annualHeatingDemand
    
    @future_annualHeatingDemand.setter
    def future_annualHeatingDemand(self, val):
        self.__future_annualHeatingDemand = val      
   
        
    @property
    def future_annualCoolingDemand(self):
        return self.__future_annualCoolingDemand
    
    @future_annualCoolingDemand.setter
    def future_annualCoolingDemand(self, val):
        self.__future_annualCoolingDemand = val      
        

    @property
    def future_annualDHWDemand(self):
        return self.__future_annualDHWDemand
    
    @future_annualDHWDemand.setter
    def future_annualDHWDemand(self, val):
        self.__future_annualDHWDemand = val  
        

    @property
    def future_annualHeatingDemandSquareMeter(self):
        return self.__future_annualHeatingDemandSquareMeter
    
    @future_annualHeatingDemandSquareMeter.setter
    def future_annualHeatingDemandSquareMeter(self, val):
        self.__future_annualHeatingDemandSquareMeter = val      
        
        
    @property
    def future_annualCoolingDemandSquareMeter(self):
        return self.__future_annualCoolingDemandSquareMeter
    
    @future_annualCoolingDemandSquareMeter.setter
    def future_annualCoolingDemandSquareMeter(self, val):
        self.__future_annualCoolingDemandSquareMeter = val      
        

    @property
    def future_annualDHWDemandSquareMeter(self):
        return self.__future_annualDHWDemandSquareMeter
    
    @future_annualDHWDemandSquareMeter.setter
    def future_annualDHWDemandSquareMeter(self, val):
        self.__future_annualDHWDemandSquareMeter = val    
        

    @property
    def future_maximumHeatingDemand(self):
        return self.__future_maximumHeatingDemand
    
    @future_maximumHeatingDemand.setter
    def future_maximumHeatingDemand(self, val):
        self.__future_maximumHeatingDemand = val      
        

    @property
    def future_maximumCoolingDemand(self):
        return self.__future_maximumCoolingDemand
    
    @future_maximumCoolingDemand.setter
    def future_maximumCoolingDemand(self, val):
        self.__future_maximumCoolingDemand = val      
        
    
    
    @property
    def future_maximumDHWWaterDemand(self):
        return self.__future_maximumDHWWaterDemand
    
    @future_maximumDHWWaterDemand.setter
    def future_maximumDHWWaterDemand(self, val):
        self.__future_maximumDHWWaterDemand = val    
        
        
    @property
    def future_refurbishment(self):
        return self.__future_refurbishment
    
    @future_refurbishment.setter
    def future_refurbishment(self, val):
        self.__future_refurbishment = val      
        
        
    @property
    def future_refurbishment_level(self):
        return self.__future_refurbishment_level
    
    @future_refurbishment_level.setter
    def future_refurbishment_level(self, val):
        self.__future_refurbishment_level = val
        
    
    @property
    def future_refurbishment_selected_roof_perc(self):
        return self.__future_refurbishment_selected_roof_perc
    
    @future_refurbishment_selected_roof_perc.setter
    def future_refurbishment_selected_roof_perc(self, val):
        self.__future_refurbishment_selected_roof_perc = val
        
                      
    @property
    def future_refurbishment_selected_wall_perc(self):
        return self.__future_refurbishment_selected_wall_perc
    
    @future_refurbishment_selected_wall_perc.setter
    def future_refurbishment_selected_wall_perc(self, val):
        self.__future_refurbishment_selected_wall_perc = val
        
    
    @property
    def future_refurbishment_selected_window_perc(self):
        return self.__future_refurbishment_selected_window_perc
    
    @future_refurbishment_selected_window_perc.setter
    def future_refurbishment_selected_window_perc(self, val):
        self.__future_refurbishment_selected_window_perc = val  



    @property
    def future_refurbishment_selected_air_loss_perc(self):
        return self.__future_refurbishment_selected_air_loss_perc
    
    @future_refurbishment_selected_air_loss_perc.setter
    def future_refurbishment_selected_air_loss_perc(self, val):
        self.__future_refurbishment_selected_air_loss_perc = val



    @property
    def economic_impact(self):
        return self.__economic_impact
    
    @economic_impact.setter
    def economic_impact(self, val):
        self.__economic_impact = val  
     
        
    @property
    def environment_impact(self):
        return self.__environment_impact
    
    @environment_impact.setter
    def environment_impact(self, val):
        self.__environment_impact = val      
    
        
 