# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 10:02:19 2018

@author: SALFE
"""

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from qgis.core import QgsMessageLog,Qgis
from .Technology import Technology


class EnergySource(QtWidgets.QTreeWidgetItem):
    
    def doSetFinalEnergyConsumption(self,finalEnergyConsumption):
        self.eFinalEnergyConsumption = finalEnergyConsumption
        
    def doGetFinalEnergyConsumption(self):
        return self.eFinalEnergyConsumption    
    
    def doSetParent(self,parent):
        self.eParent = parent

    def doSetName(self,name):
        self.eName = name
        
    def doGetName(self):
        return self.eName 

    def doResetTechnologyDict(self):
        self.eTechnologies.clear()

    def doRefreshTechnologiesData(self):
        for t in range(self.childCount()):
            self.child(t).doComputeBaselineUsefulDemand(self.eDHW, self.eHeating)    
        
    def doAddNewTechnology(self,itemToAdd):
        key = itemToAdd.doGetKey()   
        if (key in self.eTechnologies):
            return True          
        else:      
            self.eTechnologies.append(key)
            #QgsMessageLog.logMessage("Technologies list: " + str(self.eTechnologies), tag="doAddNewTechnology", level=Qgis.Info ) 
 
    def doRemoveTechnology(self,itemToRemove):
        key = itemToRemove.doGetKey()
        if (key in self.eTechnologies):
            self.eTechnologies.remove(key)
            return True
        else:
            return False
        
    def doGetTechnologyItem(self,tkey):
        if (tkey in self.eTechnologies):  
            #QgsMessageLog.logMessage("Yes is present: " + str(tkey), tag="doGetTechnologyItem", level=Qgis.Info ) 
            for t in range(self.childCount()):
                if (self.child(t).doGetKey() == tkey):
                    #QgsMessageLog.logMessage("Yes is present: " + str(tkey), tag="doGetTechnologyItem", level=QgsMessageLog.INFO ) 
                    return self.child(t)
                else:
                    return None
        else:
            return None  
    #pluto 
    def doCheckIfTechnologyIsAlreadyPresent(self, tkey):
        if (tkey in self.eTechnologies):
            #QgsMessageLog.logMessage("Key:" + str(self.eTechnologies), tag = 'doCheckIfTechnologyIsAlreadyPresent' , level=Qgis.Info)						     
            return tkey
        else:
            #QgsMessageLog.logMessage("Key:" + str(self.eTechnologies), tag = 'doCheckIfTechnologyIsAlreadyPresent' , level=Qgis.Info)			
            return None
        
    def doSetTechType(self,serviceType):
        self.eType = serviceType
        
    def doGetTechType(self):
        return self.eType 
        
    def doSetHeating(self,heating):
        self.eHeating = heating

    def doGetNodeName(self):
        return self.text(0)
      
    def doSetDHW(self,dhw):
        self.eDHW = dhw
        
    def doGetDHW(self):
        return self.eDHW
    
    def doGetHEATING(self):
        return self.eHeating
    
    def doGetNodeType(self):
        return self.ntype
    
    def doGetNodeParentName(self):
        return self.eParent
    
    def doGetKey(self):
        return self.ekey
    
    def doSetKey(self,key):
        self.ekey = key
    
    def doGetEnergyNodeType(self):
        return self.eEnergyTypeNode
    
    def doEnergySourceToJSON(self):
        static_part = "{" + '"eParent":'+ '"' + str (self.eParent) + '"' + "," + '"eFinalEnergyConsumption":' + str(self.eFinalEnergyConsumption) + "," + '"eName":' + '"' + str(self.eName) + '"' + "," + '"eHeating":' + str(self.eHeating)  + "," + '"eDHW":'+ str(self.eDHW)  + "," + '"eType":' + '"' + str(self.eType)  + '"' + "," + '"icop":' + '"' + str(self.icop)  + '"' + "," + '"ekey":' + '"' +str(self.ekey) + '"' + "," +  '"ntype":'  + '"' + str(self.ntype)  + '"'+ "," + '"Technologies":['         
        for n in range(self.childCount()):
            #QgsMessageLog.logMessage('Technology child' + str(self.child(n)), tag = 'doEnergySourceToJSON', level=Qgis.Info) 
            static_part = static_part  + self.child(n).doTechnologyToJSON() + "," 
            ##QgsMessageLog.logMessage('Technology child' + str(self.child(n)), tag = 'doEnergySourceToJSON', level=Qgis.Info)   
        if (static_part.endswith(",")):                                          
            static_part = static_part[:-1] 
        return static_part + "]}"
    
    # methods get e set for the two counters 
    
    def doSetSumEfficiencyHEATING(self,sumEfficiencyHEATING):
        self.tSumEfficiencyHEATING = sumEfficiencyHEATING
        
    def doGetSumEfficiencyHEATING(self):
        return self.tSumEfficiencyHEATING    
    
    def doSetSumPercInTermsOfNumDevicesHEATING(self,sumPercInTermsOfNumDevicesHEATING):
        self.tSumPercInTermsOfNumDevicesHEATING = sumPercInTermsOfNumDevicesHEATING
        
    def doGetSumPercInTermsOfNumDevicesHEATING(self,sumPercInTermsOfNumDevicesHEATING):
        return self.tSumPercInTermsOfNumDevicesHEATING


    def doSetSumEfficiencyDHW_COOLER(self,sumEfficiencyDHW_COOLER):
        self.tSumEfficiencyDHW_COOLER = sumEfficiencyDHW_COOLER
              
    def doGetSumEfficiencyDHW_COOLER(self):
        return self.tSumEfficiencyDHW_COOLER
    
    def doSetSumPercInTermsOfNumDevicesDHW_COOLER(self,sumPercInTermsOfNumDevicesDHW_COOLER):
        self.tSumPercInTermsOfNumDevicesDHW_COOLER = sumPercInTermsOfNumDevicesDHW_COOLER
        
    def doGetSumPercInTermsOfNumDevicesDHW_COOLER(self):
        return self.tSumPercInTermsOfNumDevicesDHW_COOLER
    
    def doSetSumUsefulDemandPerType(self,SumUsefulDemandPerType):
        self.tSumUsefulDemandPerType = SumUsefulDemandPerType
        
    def doGetSumUsefulDemandPerTypes(self):
        return self.tSumUsefulDemandPerType     

    
    
    def __init__(self, parent=None,eparent="Single Building Solution",name="",finalEnergyConsumption=0,srctype="Heating+DHW", icon_path=""):
        super(EnergySource, self).__init__(parent) 
        self.eEnergyTypeNode = parent
        self.eFinalEnergyConsumption = finalEnergyConsumption
        self.eParent = eparent
        self.eName = name
        self.eHeating = 50
        self.eDHW = 50
        self.tSumEfficiencyHEATING =0
        self.tSumPercInTermsOfNumDevicesHEATING =0        
        self.tSumEfficiencyDHW_COOLER =0
        self.tSumPercInTermsOfNumDevicesDHW_COOLER=0
        self.tSumUsefulDemandPerType=0
        self.eType = srctype
        self.eTechnologies = []
        self.doResetTechnologyDict()
        self.icop =icon_path 
        self.setIcon(0,QtGui.QIcon(icon_path)) 
        self.setText(0, name)
        self.ekey = ""
        self.ntype = "EnergySourceNode"