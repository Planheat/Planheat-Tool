# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 09:01:58 2018

@author: SALFE
"""
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog, Qgis

class Technology(QtWidgets.QTreeWidgetItem):

    
    # calcolo Useful Demand in the separated case
    def doComputeBaselineUsefulDemand(self,DHW,HEATING):
      self.eDHW = float(DHW/100)
      self.eHEATING = float(HEATING/100)
  
      
      self.BaselineUsefulDemand = (self.finalEnergyConsumption *self.eDHW*self.tEfficiencyDHW_COOLER/100*self.tPercInTermsOfNumDevicesDHW_COOLER/100* self.tGridEfficiencyDHW_COOLER * self.tCHPDHW) + (self.finalEnergyConsumption *self.eHEATING *self.tEfficiencyHEATING/100*self.tPercInTermsOfNumDevicesHEATING/100* self.tGridEfficiencyHEATING* self.tCHPHEATING )     
      # print("Tecnology.py, doComputeBaselineUsefulDemand().", "Returns self.BaselineUsefulDemand")
      # self.print_attributes()
      return self.BaselineUsefulDemand
     
# USEFUL DEMAND in any service type          
    def doComputeBaselineUsefulDemandDHW(self):
        self.BaselineUsefulDemandDHW = self.finalEnergyConsumption * self.tEfficiencyDHW_COOLER/100 * self.tPercInTermsOfNumDevicesDHW_COOLER/100 * self.tCHPDHW * self.tGridEfficiencyDHW_COOLER
        # print("Tecnology.py, doComputeBaselineUsefulDemandDHW().", "Returns self.BaselineUsefulDemandDHW")
        # self.print_attributes()
        return self.BaselineUsefulDemandDHW
    
    def doComputeBaselineUsefulDemandHEATING(self):
        self.BaselineUsefulDemandHEATING = self.finalEnergyConsumption * self.tEfficiencyHEATING/100 * self.tPercInTermsOfNumDevicesHEATING/100 * self.tCHPHEATING * self.tGridEfficiencyHEATING
        #QgsMessageLog.logMessage("Usefuldemand:" + str(self.BaselineUsefulDemandHEATING), tag = 'doComputeBaselineUsefulDemandHEATING', level=Qgis.Info)   
        # print("Tecnology.py, doComputeBaselineUsefulDemandHEATING().", "Returns self.BaselineUsefulDemandHEATING")
        # self.print_attributes()
        return self.BaselineUsefulDemandHEATING
        
    def doComputeBaselineUsefulDemandCOOLER(self):
        self.BaselineUsefulDemandCOOLER = self.finalEnergyConsumption * self.tEfficiencyDHW_COOLER/100 * self.tPercInTermsOfNumDevicesDHW_COOLER/100 * self.tCHPDHW * self.tGridEfficiencyDHW_COOLER     
        # print("Tecnology.py, doComputeBaselineUsefulDemandCOOLER().", "Returns self.BaselineUsefulDemandCOOLER")
        # self.print_attributes()
        return self.BaselineUsefulDemandCOOLER
 
    
    # FINAL ENERGY CONSUMPTION FOR TECHNOLOGY
    def doComputeFinalEnergyDHW_COOLER(self):
        factorDHW = float(self.tPercInTermsOfNumDevicesDHW_COOLER)/100   
        if (factorDHW !=0):
            self.energyConsumptionDHW_COOLER = (self.finalEnergyConsumption)*factorDHW
            # print("Tecnology.py, doComputeFinalEnergyDHW_COOLER().", "Returns self.energyConsumptionDHW_COOLER")
            # self.print_attributes()
            return self.energyConsumptionDHW_COOLER


    def doComputeFinalEnergyHEATING(self):
        factorHEATING = float(self.tPercInTermsOfNumDevicesHEATING)/100  
        if (factorHEATING !=0):
            self.energyConsumptionHEATING = (self.finalEnergyConsumption)*factorHEATING
            # print("Tecnology.py, doComputeFinalEnergyHEATING().", "Returns self.energyConsumptionHEATING")
            # self.print_attributes()
            return self.energyConsumptionHEATING
        
        
    def doComputeFinalEnergyHEATING_DHW(self,DHW,HEATING):
        self.eDHW = float(DHW/100)
        self.eHEATING = float(HEATING/100)
 
        self.energyConsumptionHEATING_DHW = (self.eDHW*self.finalEnergyConsumption*self.tPercInTermsOfNumDevicesDHW_COOLER/100) + (self.eHEATING* self.finalEnergyConsumption*self.tPercInTermsOfNumDevicesHEATING/100)
        
       # QgsMessageLog.logMessage("Final:" + str(self.energyConsumptionHEATING_DHW), tag = 'Technology', level=Qgis.Info)   
        
        # print("Tecnology.py, doComputeFinalEnergyHEATING_DHW().", "Returns self.energyConsumptionHEATING_DHW")
        # self.print_attributes()
        return self.energyConsumptionHEATING_DHW
          
    ################################################################################################################################
    # ADDITIONAL FINAL ENERGY CONSUMPTION FOR HEAT PUMPS
    
    def doComputeHeatExtractedByHeatPumpsDHW(self):
        factorDHW = float(self.tEfficiencyDHW_COOLER)/100
        demand = self.BaselineUsefulDemandDHW         
        if ((factorDHW * demand) != 0):
            self.HeatExtractedDHW = ((factorDHW -1) /factorDHW) * demand
            # print("Tecnology.py, doComputeHeatExtractedByHeatPumpsDHW().", "Returns self.HeatExtractedDHW")
            # self.print_attributes()
            return self.HeatExtractedDHW
      
    def doComputeHeatExtractedByHeatPumpsCooler(self): 
        factorCOOLER = float(self.tEfficiencyDHW_COOLER)/100  
        demandCOOLER = self.BaselineUsefulDemandCOOLER
        if ((factorCOOLER * demandCOOLER) != 0):
            self.HeatExtractedCooler = ((factorCOOLER -1)/factorCOOLER) * demandCOOLER
            #QgsMessageLog.logMessage("Additional final energy consumption COOLING case:" + str(self.HeatExtractedByHP),tag = "doComputeHeatExtractedByHeatPumps", level=QgsMessageLog.INFO)         
            # print("Tecnology.py, doComputeHeatExtractedByHeatPumpsCooler().", "Returns self.HeatExtractedCooler")
            # self.print_attributes()
            return self.HeatExtractedCooler
        
        
    def doComputeHeatExtractedByHeatPumpsHEATING(self):
        factorHEATING = float(self.tEfficiencyHEATING)/100
        demand = self.BaselineUsefulDemandHEATING        
        if ((factorHEATING * demand) != 0):
            self.HeatExtractedHEATING = ((factorHEATING -1) /factorHEATING) * demand 
            #QgsMessageLog.logMessage("Additional final energy consumption COOLING case:" + str(self.HeatExtractedHEATING),tag = "doComputeHeatExtractedByHeatPumpsHEATING", level=Qgis.Info)                    
            # print("Tecnology.py, doComputeHeatExtractedByHeatPumpsHEATING().", "Returns self.HeatExtractedHEATING")
            # self.print_attributes()
            return self.HeatExtractedHEATING

    def doComputeHeatExtractedByHeatPumpsHEATING_DHW(self):
      if self.ParamsValidForDHWAndHEATING == False:
        factorDHW = float(self.tEfficiencyDHW_COOLER)/100
        factorHEATING = float(self.tEfficiencyHEATING)/100
        factor = factorDHW + factorHEATING 
        demand = self.BaselineUsefulDemand
        #♠QgsMessageLog.logMessage("Demand:" + str(demand),tag = "doComputeHeatExtractedByHeatPumpsHEATING", level=Qgis.Info)  
        #QgsMessageLog.logMessage("factor:" + str(factor),tag = "doComputeHeatExtractedByHeatPumpsHEATING", level=Qgis.Info)                    
        if ((factor * demand) != 0):
            self.HeatExtractedHEATING_DHW = ((factor -1) /factor) * demand
            # print("Tecnology.py, doComputeHeatExtractedByHeatPumpsHEATING_DHW().", "Returns self.HeatExtractedHEATING_DHW")
            # self.print_attributes()
            return self.HeatExtractedHEATING_DHW   
      else:
        factorDHW = float(self.tEfficiencyDHW_COOLER)/100
        factor = factorDHW
        demand = self.BaselineUsefulDemand
        #QgsMessageLog.logMessage("Demand:" + str(demand),tag = "doComputeHeatExtractedByHeatPumpsHEATING", level=Qgis.Info)  
        #QgsMessageLog.logMessage("factor:" + str(factor),tag = "doComputeHeatExtractedByHeatPumpsHEATING", level=Qgis.Info)                    
        if ((factor * demand) != 0):
            self.HeatExtractedHEATING_DHW = ((factor -1) /factor) * demand
            # print("Tecnology.py, doComputeHeatExtractedByHeatPumpsHEATING_DHW().", "Returns self.HeatExtractedHEATING_DHW")
            # self.print_attributes()
            return self.HeatExtractedHEATING_DHW          
      
  
    def doGetElectricityConsumptionDHW_COOLER(self,):
        return self.energyConsumptionDHW_COOLER
    
    def doGetElectricityConsumptionHEATING(self):
        return self.energyConsumptionHEATING
   
    def doGetElectricityConsumptionHEATING_DHW(self):
        return self.energyConsumptionHEATING_DHW
    
    def doGetHeatExtractedDHW(self):
        return self.HeatExtractedDHW
    
    def doSetHeatExtractedDHW(self,htExtr):
        self.HeatExtractedDHW = htExtr
    
    def doSetHeatExtractedCooler(self,htExtrCooler):
        self.HeatExtractedCooler = htExtrCooler
        
    def doGetHeatExtractedCooler(self):
        return self.HeatExtractedCooler
    
    def doSetHeatExtractedHEATING(self,htExtr):
        self.HeatExtractedHEATING = htExtr
        
    def doGetHeatExtractedHEATING(self):
        return self.HeatExtractedHEATING
    
    def doSetHeatExtractedHEATING_DHW(self,htExtr):
        self.HeatExtractedHEATING_DHW = htExtr
        
    def doGetHeatExtractedHEATING_DHW(self):
        return self.HeatExtractedHEATING_DHW
    
    def doSetElectricityConsumptionDHW_COOLER(self,electrCons):
        self.energyConsumptionDHW_COOLER  = electrCons
        
    def doSetElectricityConsumptionHEATING(self,electrCons):
        self.energyConsumptionHEATING  = electrCons
        
    def doSetElectricityConsumptionHEATING_DHW(self,electrCons):
        self.energyConsumptionHEATING_DHW = electrCons
    
    def doGetUsefulDemand(self):
        return self.BaselineUsefulDemand
    
    def doSetUsefulDemand(self,usefDmd):
        self.BaselineUsefulDemand = usefDmd
    
    def doSetUsefulDemandDHW(self,usefDmdDHW):
        self.BaselineUsefulDemandDHW = usefDmdDHW
        
    def doSetUsefulDemandHEATING(self,usefDmdHEATING):
        self.BaselineUsefulDemandHEATING = usefDmdHEATING        
    
    def doGetUsefulDemandDHW(self):
        return self.BaselineUsefulDemandDHW 
        
    def doGetUsefulDemandHEATING(self):
        return self.BaselineUsefulDemandHEATING  

    def doSetUsefulDemandCOOLER(self,usefDmdCOOLER):
        self.BaselineUsefulDemandCOOLER = usefDmdCOOLER 
        
    def doGetUsefulDemandCOOLER(self):
        return self.BaselineUsefulDemandCOOLER     
    
    def doSetGridEfficiencyDHW_COOLER(self,gridEfficiency):
        if ((self.tGrandFather != "Single Building Solution") and (float(gridEfficiency) <= 1) and (float(gridEfficiency) >= 0)):
            self.tGridEfficiencyDHW_COOLER = float(gridEfficiency)
            return True
        else:
            if (self.tGrandFather == "Single Building Solution"):
                self.tGridEfficiencyDHW_COOLER = 1
                return True
            else:
                return False
            
    def doGetGridEfficiencyDHW_COOLER(self):
        return self.tGridEfficiencyDHW_COOLER
           
    def doSetCHPDHW(self,CHP):
        self.tCHPDHW = float(CHP)
    
    def doGetCHPDHW(self):
        return self.tCHPDHW
        
    def doSetPercInTermsOfNumDevicesDHW_COOLER(self,percInTermsOfNumDevices):
        self.tPercInTermsOfNumDevicesDHW_COOLER = float(percInTermsOfNumDevices)
        
    def doGetPercInTermsOfNumDevicesDHW_COOLER(self):
        return self.tPercInTermsOfNumDevicesDHW_COOLER
        
    def doSetEfficiencyDHW_COOLER(self,efficiency):
        self.tEfficiencyDHW_COOLER = float(efficiency)
        
    def doGetEfficiencyDHW_COOLER(self):
        return self.tEfficiencyDHW_COOLER

    def doSetFinalEnergyConsumption(self,finEnCons):
        self.finalEnergyConsumption = finEnCons    

    def doGetFinalEnergyConsumption(self):
        return self.finalEnergyConsumption 

    def doSetGridEfficiencyHEATING(self,gridEfficiency):
        if ((self.tGrandFather != "Single Building Solution") and (float(gridEfficiency) <= 1) and (float(gridEfficiency) >= 0)):
            self.tGridEfficiencyHEATING = float(gridEfficiency)
            return True
        else:
            if (self.tGrandFather == "Single Building Solution"):
                self.tGridEfficiencyHEATING = 1
                return True
            else:
                return False

    def doGetGridEfficiencyHEATING(self):
        return self.tGridEfficiencyHEATING
            
    def doSetCHPHEATING(self,CHP):
        self.tCHPHEATING = float(CHP)
            
    def doGetCHPHEATING(self):
        return self.tCHPHEATING
    
    def doSetPercInTermsOfNumDevicesHEATING(self,percInTermsOfNumDevices):
        self.tPercInTermsOfNumDevicesHEATING = float(percInTermsOfNumDevices)
    
    def doGetPercInTermsOfNumDevicesHEATING(self):
        return self.tPercInTermsOfNumDevicesHEATING
        
    def doSetEfficiencyHEATING(self,efficiency):
        self.tEfficiencyHEATING = float(efficiency)
    
    def doGetEfficiencyHEATING(self):
        return self.tEfficiencyHEATING     
        
    def doSetName (self,name):
        self.tName = name
        
    def doGetName(self):
        return self.tName
    
    def doSetFather(self,parent):    
        self.Parent = parent
        
    def doGetFather(self):    
        return self.Parent
    
    def doSetGrandFather(self,grandfather):    
        self.tGrandFather = grandfather       
    
    def doGetGrandFather(self):    
        return self.tGrandFather  
  
    def doGetNodeType(self):
        return self.ntype

    def doGetNodeName(self):
        return self.text(0)
    
    def doGetNodeParentName(self):
        return self.tParent  
    
    def doSetKey(self,key):
        self.tKey = key
    
    def doGetKey(self):
        return self.tKey
    
    def doSetPKey(self,key):
        self.pKey = key
    
    def doGetPKey(self):
        return self.pKey 

    def doSetHeatSupplyType(self, stype):
        self.HeatSupplyType = stype
        
    def doGetHeatSupplyType(self):
        return self.HeatSupplyType

    def doSetParamsValidForDHWAndHEATING(self, validity):
        self.ParamsValidForDHWAndHEATING = validity
        
    def doGetParamsValidForDHWAndHEATING(self):
        return self.ParamsValidForDHWAndHEATING     

    def doGetTechHEATING(self):
        return self.eHEATING

    def doGetTechDHW(self):
        return self.eDHW
      
    def doSetTechHEATING(self,HEATING):
        self.eHEATING = HEATING

    def doSetTechDHW(self,DHW):
        self.eDHW  = DHW
      
    def doSetPercOnUsefulDemand(self,percentage):
      self.PercOnUsefulDemand = percentage
      
    def doGetPercOnUsefulDemand(self):
      return self.PercOnUsefulDemand
      

    def doGetPercentages(self): 
        if (self.tParent == 'DHW' or self.tParent == 'HEATING+DHW' or self.tParent == 'COOLING'):            
            #QgsMessageLog.logMessage("parent name" + "" + str(self.tParent),tag = "Technology", level=QgsMessageLog.INFO)   
            # HEATING+DHW
            return "(" + str(self.tEfficiencyDHW_COOLER) + " % -" + str(self.tPercInTermsOfNumDevicesDHW_COOLER) + "%)"
        else:
            # caso HEATING
            #QgsMessageLog.logMessage("parent name" + "" + str(self.tParent),tag = "Technology", level=QgsMessageLog.INFO)   
            return "(" + str(self.tEfficiencyHEATING) + " % - " + str(self.tPercInTermsOfNumDevicesHEATING) + " %)"        
    
    def doTechnologyToJSON(self):
        dynamic_part = "{" + '"tName":'+ '"' + str (self.tName) + '"' + "," + '"tEfficiencyDHW_COOLER":' + str(self.tEfficiencyDHW_COOLER) + "," + '"tPercInTermsOfNumDevicesDHW_COOLER":' + str(self.tPercInTermsOfNumDevicesDHW_COOLER) + "," + '"tCHPDHW":'+ str(self.tCHPDHW)  + "," +'"tCHPHEATING":'+ str(self.tCHPHEATING)  + "," +  '"tGridEfficiencyDHW_COOLER":' + str(self.tGridEfficiencyDHW_COOLER)  + ","  + '"tEfficiencyHEATING":'+ str(self.tEfficiencyHEATING)  + "," + '"tPercInTermsOfNumDevicesHEATING":' + str(self.tPercInTermsOfNumDevicesHEATING)  + ","  +  '"tGridEfficiencyHEATING":'+ str(self.tGridEfficiencyHEATING)  + ","  + '"finalEnergyConsumption":' + str(self.finalEnergyConsumption)  + ","  + '"BaselineUsefulDemandHEATING_DHW":' + str(self.BaselineUsefulDemand)  + ","  + '"BaselineUsefulDemandCOOLER":' +  str(self.BaselineUsefulDemandCOOLER)  + ","  + '"BaselineUsefulDemandDHW":' + str(self.BaselineUsefulDemandDHW)  +  ","  + '"BaselineUsefulDemandHEATING":'+ str(self.BaselineUsefulDemandHEATING) + "," + '"Final energy consumption DHW_COOLER":' + str(self.energyConsumptionDHW_COOLER) + "," + '"Final energy consumption HEATING":' + str(self.energyConsumptionHEATING) + ","  + '"final energy consumption HEATING+DHW":' + str(self.energyConsumptionHEATING_DHW) + "," + '"Heat extracted HP DHW":' + str(self.HeatExtractedDHW) +  ","  + '"Heat extracted HP COOLER":' + str(self.HeatExtractedCooler)  + ","  + '"Heat extracted HP HEATING":' + str(self.HeatExtractedHEATING) +  "," + '"Heat extracted HP HEATING_DHW":' + str(self.HeatExtractedHEATING_DHW) + "," + '"tGrandFather":' + '"' + str(self.tGrandFather) + '"' + "," + '"tParent":' + '"' + str(self.tParent) + '"' + "," + '"iconp":' + '"'+ str(self.iconp) + '"' +  "," + '"tKey":' + '"' + str(self.tKey) + '"' + "," + '"pKey":' + '"' + str(self.pKey) + '"' + "," + '"ntype":' + '"'+ str(self.ntype)  + '"' + "," + '"HeatSupplyType":' + '"' + str(self.HeatSupplyType) + '"' + "," + '"ParamsValidForDHWAndHEATING":' + '"' + str(self.ParamsValidForDHWAndHEATING) + '"' + "}"                                              
        
        return "{" + '"tName":'+ '"' + str (self.tName) + '"' + "," + '"tEfficiencyDHW_COOLER":' + str(self.tEfficiencyDHW_COOLER) + "," + '"tPercInTermsOfNumDevicesDHW_COOLER":' + str(self.tPercInTermsOfNumDevicesDHW_COOLER) + "," + '"tCHPDHW":'+ str(self.tCHPDHW)  + "," +'"tCHPHEATING":'+ str(self.tCHPHEATING)  + "," +  '"tGridEfficiencyDHW_COOLER":' + str(self.tGridEfficiencyDHW_COOLER)  + ","  + '"tEfficiencyHEATING":'+ str(self.tEfficiencyHEATING)  + "," + '"tPercInTermsOfNumDevicesHEATING":' + str(self.tPercInTermsOfNumDevicesHEATING)  + ","  +  '"tGridEfficiencyHEATING":'+ str(self.tGridEfficiencyHEATING)  + ","  + '"finalEnergyConsumption":' + str(self.finalEnergyConsumption)  + ","  + '"BaselineUsefulDemandHEATING_DHW":' + str(self.BaselineUsefulDemand)  + ","  + '"BaselineUsefulDemandCOOLER":' +  str(self.BaselineUsefulDemandCOOLER)  + ","  + '"BaselineUsefulDemandDHW":' + str(self.BaselineUsefulDemandDHW)  +  ","  + '"BaselineUsefulDemandHEATING":'+ str(self.BaselineUsefulDemandHEATING) + "," + '"Final energy consumption DHW_COOLER":' + str(self.energyConsumptionDHW_COOLER) + "," + '"Final energy consumption HEATING":' + str(self.energyConsumptionHEATING) + ","  + '"final energy consumption HEATING+DHW":' + str(self.energyConsumptionHEATING_DHW) + "," + '"Heat extracted HP DHW":' + str(self.HeatExtractedDHW) +  ","  + '"Heat extracted HP COOLER":' + str(self.HeatExtractedCooler)  + ","  + '"Heat extracted HP HEATING":' + str(self.HeatExtractedHEATING) +  "," + '"Heat extracted HP HEATING_DHW":' + str(self.HeatExtractedHEATING_DHW) + "," + '"tGrandFather":' + '"' + str(self.tGrandFather) + '"' + "," + '"tParent":' + '"' + str(self.tParent) + '"' + "," + '"iconp":' + '"'+ str(self.iconp) + '"' +  "," + '"tKey":' + '"' + str(self.tKey) + '"' + "," + '"pKey":' + '"' + str(self.pKey) + '"' + "," + '"ntype":' + '"'+ str(self.ntype)  + '"' + "," + '"HeatSupplyType":' + '"' + str(self.HeatSupplyType) + '"' + "," + '"ParamsValidForDHWAndHEATING":' + '"' + str(self.ParamsValidForDHWAndHEATING) + '"' + "}"                                              

    def print_attributes(self):
        try:
            print("Tecnology.py, print_attributes().")
            print("METADATA")
            print("self.doGetName():", self.doGetName())
            print("self.doGetNodeName():", self.doGetNodeName())
            print("self.doGetNodeType():", self.doGetNodeType())
            print("DATA")
            print("self.tEfficiencyDHW_COOLER:", self.tEfficiencyDHW_COOLER)
            print("self.tEfficiencyHEATING:", self.tEfficiencyHEATING)
            print("self.tPercInTermsOfNumDevicesDHW_COOLER:", self.tPercInTermsOfNumDevicesDHW_COOLER)
            print("self.tPercInTermsOfNumDevicesHEATING:", self.tPercInTermsOfNumDevicesHEATING)
            print("self.tCHPDHW:", self.tCHPDHW)
            print("self.tCHPHEATING:", self.tCHPHEATING)
            print("self.tGridEfficiencyDHW_COOLER:", self.tGridEfficiencyDHW_COOLER)
            print("self.tGridEfficiencyHEATING:", self.tGridEfficiencyHEATING)
            print("self.eDHW:", self.eDHW)
            print("self.eHEATING:", self.eHEATING)
            print("self.finalEnergyConsumption:", self.finalEnergyConsumption)
            print("self.BaselineUsefulDemandDHW:", self.BaselineUsefulDemandDHW)
            print("self.BaselineUsefulDemandHEATING:", self.BaselineUsefulDemandHEATING)
            print("self.BaselineUsefulDemandCOOLER:", self.BaselineUsefulDemandCOOLER)
            print("self.BaselineUsefulDemand:", self.BaselineUsefulDemand)
            print("self.energyConsumptionHEATING:", self.energyConsumptionHEATING)
            print("self.energyConsumptionDHW_COOLER:", self.energyConsumptionDHW_COOLER)
            print("self.energyConsumptionHEATING_DHW:", self.energyConsumptionHEATING_DHW)
            print("self.HeatExtractedDHW:", self.HeatExtractedDHW)
            print("self.HeatExtractedCooler:", self.HeatExtractedCooler)
            print("self.HeatExtractedHEATING:", self.HeatExtractedHEATING)
            print("self.HeatExtractedHEATING_DHW:", self.HeatExtractedHEATING_DHW)
            print("self.doTechnologyToJSON():", self.doTechnologyToJSON())
            print("\n")
        except:
            print("Technology.py, print_attributes(). Tentar non nuoce. Di solito...")

    def __init__(self, parent="", grandfather="Single Building Solution", tparent="", name="", tkey="", icon_path=""):
        super(Technology, self).__init__(parent)   
        self.tName = name
        self.Parent = parent
        # manage the efficiency for DHW and COOLER
        self.tEfficiencyDHW_COOLER = 100
        # manage the efficiency for HEATING
        self.tEfficiencyHEATING = 100
        # ... see before
        self.tPercInTermsOfNumDevicesDHW_COOLER = 50
        self.tPercInTermsOfNumDevicesHEATING = 50

        # manage the CHP for both HEATING and DHW
        self.tCHPDHW = 1
        self.tCHPHEATING = 1

        # manage the grid efficiency        
        self.tGridEfficiencyDHW_COOLER = 1 
        self.tGridEfficiencyHEATING = 1
        
        # the share percentages
        self.eDHW = 50
        self.eHEATING = 50
        
        # final energy consumption
        self.finalEnergyConsumption = 0
        # useful demand
        self.BaselineUsefulDemandDHW = 0
        self.BaselineUsefulDemandHEATING = 0
        self.BaselineUsefulDemandCOOLER = 0  
        self.BaselineUsefulDemand = 0    
        
        # final energy consumption per technology
        self.energyConsumptionHEATING=0
        self.energyConsumptionDHW_COOLER=0
        self.energyConsumptionHEATING_DHW=0
        # heat extracted
        self.HeatExtractedDHW=0
        self.HeatExtractedCooler=0
        self.HeatExtractedHEATING  =0
        self.HeatExtractedHEATING_DHW=0
        
        self.iconp = icon_path 
        self.tGrandFather = grandfather
        self.tParent = tparent
        self.setIcon(0,QtGui.QIcon(icon_path)) 
        self.setText(0, name) 
        self.tKey = tkey
        self.pKey = ""
        self.ntype = "TechnologyNode"
        self.HeatSupplyType = "heat supply 40 -70 °C"
        self.ParamsValidForDHWAndHEATING = True
        self.PercOnUsefulDemand = 0