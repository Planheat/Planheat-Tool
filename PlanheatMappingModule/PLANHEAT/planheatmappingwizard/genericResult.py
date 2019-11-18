# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 17:49:41 2018

@author: SALFE
"""

class genericResult ():

    def doGetusefulDemand (self):
        return self.usefulDemand    
    
    def doSetusefulDemand (self,val):
        self.usefulDemand = val
        
    def doGetDHWusefulDemand (self):
        return self.DHWusefulDemand        
    
    def doSetDHWusefulDemand (self,val): 
        self.DHWusefulDemand = val
        
    def doGetHEATINGusefulDemand (self):
        return self.HEATINGusefulDemand        
    
    def doSetHEATINGusefulDemand (self,val): 
        self.HEATINGusefulDemand = val
        
    def doGetCOOLERusefulDemand (self):
        return self.COOLERusefulDemand    
    
    def doSetCOOLERGusefulDemand (self,val): 
        self.COOLERusefulDemand   = val     
        
    def doGettechnologyName (self):
        return str(self.technologyName)        
    
    def doSettechnologyName (self,val): 
        self.technologyName = val
        
    def doGetheatExtractedDHW (self):
        return self.heatExtracted        
    
    def doSetheatExtracted (self,val): 
        self.heatExtracted = val
        
    def doGetheatExtracted (self):
        return self.heatExtracted        
    
    def doSetheatExtractedDHW (self,val): 
        self.heatExtractedDHW = val    
        
    def doSetheatExtractedHEATING (self,val): 
        self.heatExtractedHEATING = val 
        
    def doGetheatExtractedHEATING(self):
        return self.heatExtracted                   
        
    def doGetelectricityConsumed (self):
        return self.electricityConsumed        
    
    def doSetelectricityConsumedDHW_COOLER (self,val): 
        self.electricityConsumedDHW_COOLER= val
        
    def doGetelectricityConsumedDHW_COOLER (self):
        return self.electricityConsumedDHW_COOLER  
          
    def doGetelectricityConsumedHEATING (self):
        return self.electricityConsumedHEATING
      
    def doSetelectricityConsumedHEATING (self,val): 
        self.electricityConsumedHEATING = val
            
    def doSetelectricityConsumed (self,val): 
        self.electricityConsumed = val
        
    def doGetpercOnTotUsefuleDemand (self):
        return self.percOnTotUsefuleDemand        
    
    def doSetpercOnTotUsefuleDemand(self,val):
        self.percOnTotUsefuleDemand = val
        
    def doGetheatingSupplyType (self):
        return str(self.heatingSupplyType)
        
    def doSetheatingSupplyType(self,val):
        self.heatingSupplyType = val        
               
    def __init__(self):
        self.usefulDemand = 0
        self.DHWusefulDemand = 0
        self.HEATINGusefulDemand = 0
        self.COOLERusefulDemand = 0
        self.technologyName = ""
        self.heatExtracted = 0
        self.heatExtractedDHW =0
        self.heatExtractedHEATING=0
        self.electricityConsumed = 0
        self.electricityConsumedDHW_COOLER=0
        self.electricityConsumedHEATING=0
        self.percOnTotUsefulDemand = 0
        self.heatingSupplyType = ""