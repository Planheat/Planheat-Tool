# -*- coding: utf-8 -*-
"""
   Model Map file Totalized - CSV2 
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 25 Oct. 2017
"""
__docformat__ = "restructuredtext"


class TotalizedDemand():
    
    """ Totalized Data used for process and output file totalized CSV """


    __slots__ = ('Regstatus','Regprocess','_TotalizedDemand__period_id','_TotalizedDemand__period_text','_TotalizedDemand__building_use_id','_TotalizedDemand__use','_TotalizedDemand__scenario','_TotalizedDemand__numberOfBuildings','_TotalizedDemand__totalGrossFloorArea','_TotalizedDemand__annualUsefulHeatingDemand','_TotalizedDemand__annualUsefulHeatingDemandSquareMeter','_TotalizedDemand__annualUsefulCoolingDemand','_TotalizedDemand__annualUsefulCoolingDemandSquareMeter','_TotalizedDemand__annualUsefulDHWDemand','_TotalizedDemand__annualUsefulDHWDemandSquareMeter')

    def __init__(self):
        '''
        Constructor
        '''
        self.Regstatus = True
        self.Regprocess = True
        
        self.__period_id = 0
        self.__period_text = ""
        self.__building_use_id = 0
        self.__use = ""
        self.__scenario = 'Baseline'
        self.__numberOfBuildings = 0
        self.__totalGrossFloorArea = 0.0
        
        
        self.__annualUsefulHeatingDemand = 0.0
        self.__annualUsefulHeatingDemandSquareMeter = 0.0
        self.__annualUsefulCoolingDemand = 0.0
        self.__annualUsefulCoolingDemandSquareMeter = 0.0
        self.__annualUsefulDHWDemand = 0.0
        self.__annualUsefulDHWDemandSquareMeter = 0.0
            
            
    def __str__(self):      
            text =  "scenario:" + self.scenario + "period_id:" + str(self.period_id) + " period_text:" + str(self.period_text) + " building_use_id:" + str(self.building_use_id) + " use:" + str(self.use) \
                    + " annualUsefulHeatingDemand:" + str(self.annualUsefulHeatingDemand) + " annualUsefulCoolingDemand:" + str(self.annualUsefulCoolingDemand) + " annualUsefulDHWDemand:" + str(self.annualUsefulDHWDemand) \
                    + " annualUsefulHeatingDemandSquareMeter:" + str(self.annualUsefulHeatingDemandSquareMeter)  + " annualUsefulCoolingDemandSquareMeter:" + str(self.annualUsefulCoolingDemandSquareMeter) \
                    + " annualUsefulDHWDemandSquareMeter:" + str(self.annualUsefulDHWDemandSquareMeter)
            return text
    
    
    
    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False
        else:
            return (self.period_id == other.period_id and self.building_use_id == other.building_use_id)
        
        
    def __rshift__(self, other):
        
        if not isinstance(self, other.__class__):
            return other 
            
        other.Regstatus         = self.Regstatus
        other.Regprocess        = self.Regprocess
        other.period_id         = self.period_id
        other.period_text       = self.period_text
        other.building_use_id   = self.building_use_id
        other.use               = self.use
        other.scenario          = self.scenario
        other.numberOfBuildings = self.numberOfBuildings
        other.totalGrossFloorArea                   = self.totalGrossFloorArea
        other.annualUsefulHeatingDemand             = self.annualUsefulHeatingDemand
        other.annualUsefulHeatingDemandSquareMeter  = self.annualUsefulHeatingDemandSquareMeter
        other.annualUsefulCoolingDemand             = self.annualUsefulCoolingDemand
        other.annualUsefulCoolingDemandSquareMeter  = self.annualUsefulCoolingDemandSquareMeter
        other.annualUsefulDHWDemand                 = self.annualUsefulDHWDemand
        other.annualUsefulDHWDemandSquareMeter      = self.annualUsefulDHWDemandSquareMeter
        
        return other
    
    
    def __lshift__(self, other):
        
        if not isinstance(self, other.__class__):
            return other 
            
        self.Regstatus         = other.Regstatus
        self.Regprocess        = other.Regprocess
        self.period_id         = other.period_id
        self.period_text       = other.period_text
        self.building_use_id   = other.building_use_id
        self.use               = other.use
        self.scenario          = other.scenario
        self.numberOfBuildings = other.numberOfBuildings
        self.totalGrossFloorArea                   = other.totalGrossFloorArea
        self.annualUsefulHeatingDemand             = other.annualUsefulHeatingDemand
        self.annualUsefulHeatingDemandSquareMeter  = other.annualUsefulHeatingDemandSquareMeter
        self.annualUsefulCoolingDemand             = other.annualUsefulCoolingDemand
        self.annualUsefulCoolingDemandSquareMeter  = other.annualUsefulCoolingDemandSquareMeter
        self.annualUsefulDHWDemand                 = other.annualUsefulDHWDemand
        self.annualUsefulDHWDemandSquareMeter      = other.annualUsefulDHWDemandSquareMeter
        
        return other
        
    
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
    def building_use_id(self):
        return self.__building_use_id
    
    @building_use_id.setter
    def building_use_id(self, val):
        self.__building_use_id = val        
    
    
    @property
    def use(self):
        return self.__use
    
    @use.setter
    def use(self, val):
        self.__use = val        
    
    
    @property
    def scenario(self):
        return self.__scenario
    
    @scenario.setter
    def scenario(self, val):
        self.__scenario = val    
        
        
    @property
    def numberOfBuildings(self):
        return self.__numberOfBuildings
    
    @numberOfBuildings.setter
    def numberOfBuildings(self, val):
        self.__numberOfBuildings = val        
    
    
    @property
    def totalGrossFloorArea(self):
        return self.__totalGrossFloorArea
    
    @totalGrossFloorArea.setter
    def totalGrossFloorArea(self, val):
        self.__totalGrossFloorArea = float(val.replace(",","."))  if isinstance(val,str) else float(val)                   
         
         
    @property
    def annualUsefulHeatingDemand(self):
        return self.__annualUsefulHeatingDemand
    
    @annualUsefulHeatingDemand.setter
    def annualUsefulHeatingDemand(self, val):
        self.__annualUsefulHeatingDemand = float(val.replace(",","."))  if isinstance(val,str) else float(val)                   
    
    
    @property
    def annualUsefulHeatingDemandSquareMeter(self):
        return self.__annualUsefulHeatingDemandSquareMeter
    
    @annualUsefulHeatingDemandSquareMeter.setter
    def annualUsefulHeatingDemandSquareMeter(self, val):
        self.__annualUsefulHeatingDemandSquareMeter = float(val.replace(",","."))  if isinstance(val,str) else float(val)                   
    
   
    @property
    def annualUsefulCoolingDemand(self):
        return self.__annualUsefulCoolingDemand
    
    @annualUsefulCoolingDemand.setter
    def annualUsefulCoolingDemand(self, val):
        self.__annualUsefulCoolingDemand = float(val.replace(",","."))  if isinstance(val,str) else float(val)   
    
            
    @property
    def annualUsefulCoolingDemandSquareMeter(self):
        return self.__annualUsefulCoolingDemandSquareMeter
    
    @annualUsefulCoolingDemandSquareMeter.setter
    def annualUsefulCoolingDemandSquareMeter(self, val):
        self.__annualUsefulCoolingDemandSquareMeter = float(val.replace(",","."))  if isinstance(val,str) else float(val)          
        
            
    @property
    def annualUsefulDHWDemand(self):
        return self.__annualUsefulDHWDemand
    
    @annualUsefulDHWDemand.setter
    def annualUsefulDHWDemand(self, val):
        self.__annualUsefulDHWDemand = float(val.replace(",","."))  if isinstance(val,str) else float(val)          
        
            
    @property
    def annualUsefulDHWDemandSquareMeter(self):
        return self.__annualUsefulDHWDemandSquareMeter
    
    @annualUsefulDHWDemandSquareMeter.setter
    def annualUsefulDHWDemandSquareMeter(self, val):
        self.__annualUsefulDHWDemandSquareMeter = float(val.replace(",","."))  if isinstance(val,str) else float(val)          
        
                
        
    