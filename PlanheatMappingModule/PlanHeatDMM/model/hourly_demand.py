# -*- coding: utf-8 -*-
"""
   Model Map file Hourly - CSV3
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 30 Oct. 2017
"""
__docformat__ = "restructuredtext"


class HourlyDemand():
    """ Data for every hour of year, used for process and output file hourly CSV """

    __slots__ = ('Regstatus','Regprocess','projectID','reference','period','use','dayOfYear','hourOfDay','season','heating','cooling','DHW','equipment_internal_gains','occupancy_internal_gains','light_internal_gains','solar_gains','HDH','CDH','heat_ventilation_losses','cool_ventilation_losses','scheduling_heating','scheduling_cooling','scheduling_DHW','scheduling_lighting','scheduling_equipment','scheduling_occupancy','base_heating','base_cooling')
    
                 
    def __init__(self):
        '''
        Constructor
        '''
        
        self.Regstatus = True
        self.Regprocess = True
        
        self.projectID          = ""
        self.reference          = ""
        
        #All Calculate Model
        self.period             = ""
        self.use                = ""
        self.dayOfYear          = 0
        self.hourOfDay          = 0
        self.season             = ""
        
        #Simplified Calculate Model 
        self.heating            = 0.0
        self.cooling            = 0.0
        self.DHW                = 0.0
        
        #Complete Calculate Model
        self.equipment_internal_gains = 0.0
        self.occupancy_internal_gains = 0.0
        self.light_internal_gains     = 0.0
        self.solar_gains              = 0.0
        
        self.HDH = 0.0
        self.CDH = 0.0
        
        self.heat_ventilation_losses = 0.0
        self.cool_ventilation_losses = 0.0
        
        self.scheduling_heating   = 0.0
        self.scheduling_cooling   = 0.0
        self.scheduling_DHW       = 0.0
        self.scheduling_lighting  = 0.0
        self.scheduling_equipment = 0.0
        self.scheduling_occupancy = 0.0
        self.base_heating = 0.0
        self.base_cooling = 0.0
        

        
        
        
            
    def __str__(self):      
            text = "projectID:" + str(self.projectID) + " building id:" + str(self.reference)  + " period: " + str(self.period) + " use:" + str(self.use)\
                    + " dayOfYear:" + str(self.dayOfYear) + " hourOfDay:" + str(self.hourOfDay) + " season: " + str(self.season) \
                    + " heating:" + str(self.heating) + " cooling:" + str(self.cooling) + " DHW:" + str(self.DHW)   \
                    + " equipment_internal_gains:" + str(self.equipment_internal_gains) + " occupancy_internal_gains:" + str(self.occupancy_internal_gains) \
                    + " light_internal_gains:" + str(self.light_internal_gains) + " solar_gains:" + str(self.solar_gains) \
                    + " HDH:" + str(self.HDH) + " CDH:" + str(self.CDH) \
                    + " heat_ventilation_losses:" + str(self.heat_ventilation_losses) + " cool_ventilation_losses:" + str(self.cool_ventilation_losses) \
                    + " base_heating:" + str(self.base_heating)  + " base_cooling:" + str(self.base_cooling)
                    
                    
            return text
        
        

                
            