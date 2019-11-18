# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 14:55:34 2018

@author: SALFE
"""
import os
import sys
import json
import csv
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import *
#from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import Qt
#from PyQt5.QtCore import pyqtSlot,QStringList,QString
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog, Qgis
from .Solution import Solution
from .EnergySourceType import EnergySourceType
from .EnergySource import EnergySource
from .addEnergySourceDlg import AddEnergySourceDlg
from .addTechnologyDlg import AddTechnologySourceDlg
from .assignShareHeatingAndDHWDlg import AssignShareHeatingAndDHWDlg
from .Technology import Technology
from .usefulDemandDetails import BaselineUsefulDemandResults
from .HeatingNodeType import HeatingNodeType
from .genericResult import genericResult

from ... import master_mapping_config



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'mapping_module_page1.ui'), resource_suffix='')



class WizardPage1(QtWidgets.QWizardPage, FORM_CLASS):
     
    def doManageGetEnergyDlgResults(self,node,srcType,parentName,srcName,CONSUMPTION):
        if not self.selectedItem is None:
            #get the share DHW e HEATING
            DHW= self.selectedItem.doGetDHW()
            HEATING = self.selectedItem.doGetHEATING()
        
            key = parentName + "+" + srcType + "+" + srcName        
            if (not node.doCheckIfEnergySourceIsAlreadyPresent(key)):
                newEnergyItem = self.doAddTreeEnergySourceChild(self.selectedItem, parentName, srcName, CONSUMPTION, DHW, HEATING, srcType,"")          
                if (newEnergyItem != None):
                    node.doAddNewEnergySourceItem(newEnergyItem)
                else:
                    QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to create an energy source object.') 
            else:
                energyItem = node.doGetEnergySourceItem(key)
                if (energyItem != None):
                    #•qui lo commento perché DHW e HEATING sono attributi della classe EnergySourceTypeNode
#                    energyItem.doSetDHW(DHW)
#                    energyItem.doSetHeating(HEATING)
                    energyItem.doSetName(srcName)
                    energyItem.doSetFinalEnergyConsumption(CONSUMPTION)
                    #pluto
                    for t in range (energyItem.childCount()):
                        energyItem.child(t).doSetFinalEnergyConsumption(float(CONSUMPTION))
                else:
                    QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to update energy source.') 
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to add energy source.')            
    
    @pyqtSlot(str,str,str,float)
    def get_dlg_resultsSBS(self,srcType,parentName,srcName,CONSUMPTION):
        self.doManageGetEnergyDlgResults(self.rootNodeSBS,srcType,parentName,srcName,CONSUMPTION)
     
    @pyqtSlot(str,str,str,float)
    def get_dlg_resultsDCN(self,srcType,parentName,srcName,CONSUMPTION):
        self.doManageGetEnergyDlgResults(self.rootNodeDCN,srcType,parentName,srcName,CONSUMPTION)
         
    @pyqtSlot(str,str,str,float)
    def get_dlg_resultsDHN(self,srcType,parentName,srcName,CONSUMPTION):
        self.doManageGetEnergyDlgResults(self.rootNodeDHN,srcType,parentName,srcName,CONSUMPTION)
    
    ########################################################################################################
    ################################ MODIFICATA DA ME 
    ########################################################################################################        
    # the purpose is to: send the data updated to a slot that save the data into the energy source node
    def doAssignShareDlgTriggered(self,parentName,srcName,srcType):
        if not self.selectedItem is None:
            if (self.selectedItem.doGetNodeParentName() == "Single Building Solution"):
                if(self.rootNodeSBS_HEATING_DHW.doGetNodeName() == "HEATING+DHW" ):
                    #QgsMessageLog.logMessage("srcType" + "" + str(srcType), tag = "doAssignShareDlgTriggered", level=QgsMessageLog.INFO )     
                    #QgsMessageLog.logMessage("parentName" + "" + str(parentName), tag = "doAssignShareDlgTriggered", level=QgsMessageLog.INFO )     
                    self.assignShareld = AssignShareHeatingAndDHWDlg(parentName,srcName,srcType)
                    self.assignShareld.dataUpdated.connect(self.getShareDlgResultsSBS)
                    self.assignShareld.show()           
            elif (self.selectedItem.doGetNodeParentName()== "District Heating Network"):
                if(self.rootNodeDHN_HEATING_DHW.doGetNodeName()== "HEATING+DHW" ):
                    self.assignShareld = AssignShareHeatingAndDHWDlg(parentName,srcName,srcType)
                    self.assignShareld.dataUpdated.connect(self.getShareDlgResultsDHN)
                    self.assignShareld.show()
        else:        
            QMessageBox.warning(self, 'The item is a null object!', 'Please select another item!', QMessageBox.Ok, QMessageBox.Default)
       
    ########################################################################################################
    ################################ MODIFICATA DA ME 
    ########################################################################################################            
    def doManageGetShareDlgResults(self,node,scrName,srcType,DHW,HEATING):     
        #define the key to parse the tree
       # key = str(self.rootNodeSBS_HEATING_DHW.doGetNodeParentName()) + "" + "+"+  srcType        
        if (self.rootNodeSBS_HEATING_DHW.doGetNodeParentName() == "Single Building Solution") :
            energySourceTypeItem = self.rootNodeSBS_HEATING_DHW.doGetNodeType()
          #  QgsMessageLog.logMessage("The node type is:" + "" +str(energySourceTypeItem),tag = "doManageGetShareDlgResults", level=QgsMessageLog.INFO)   
            if(energySourceTypeItem != None):
                #QgsMessageLog.logMessage("DHW is:" + "" +str(DHW),tag = "doManageGetShareDlgResults", level=QgsMessageLog.INFO)
                #QgsMessageLog.logMessage("HEATING is:" + "" +str(HEATING),tag = "doManageGetShareDlgResults", level=QgsMessageLog.INFO) 
                self.rootNodeSBS_HEATING_DHW.doSetDHW(DHW)
                self.rootNodeSBS_HEATING_DHW.doSetHEATING(HEATING)
                self.rootNodeSBS_HEATING_DHW.setText(1, self.rootNodeSBS_HEATING_DHW.doGetPercentages())
            else:
                QMessageBox.about(self, 'info!', 'Null object!' )
                
        if (self.rootNodeDHN_HEATING_DHW.doGetNodeParentName() == "District Heating Network") :
            energySourceTypeItem = self.rootNodeDHN_HEATING_DHW.doGetNodeType()
            #QgsMessageLog.logMessage("The node type is:" + "" +str(energySourceTypeItem),tag = "doManageGetShareDlgResults", level=QgsMessageLog.INFO)   
            if(energySourceTypeItem != None):
                #QgsMessageLog.logMessage("DHW is:" + "" +str(DHW),tag = "doManageGetShareDlgResults", level=QgsMessageLog.INFO)
                #QgsMessageLog.logMessage("HEATING is:" + "" +str(HEATING),tag = "doManageGetShareDlgResults", level=QgsMessageLog.INFO) 
                self.rootNodeDHN_HEATING_DHW.doSetDHW(DHW)
                self.rootNodeDHN_HEATING_DHW.doSetHEATING(HEATING)
                self.rootNodeDHN_HEATING_DHW.setText(1, self.rootNodeDHN_HEATING_DHW.doGetPercentages())
            else:
                QMessageBox.about(self, 'info!', 'Null object!' )
        
    @pyqtSlot(str,str,str,float,float)
    def getShareDlgResultsSBS(self,node,scrName,srcType,DHW,HEATING):
        self.doManageGetShareDlgResults(self.rootNodeSBS,scrName,srcType,DHW,HEATING)
     
    @pyqtSlot(str,str,str,float,float)
    def getShareDlgResultsDHN(self,node,scrName,srcType,DHW,HEATING):
        self.doManageGetShareDlgResults(self.rootNodeDHN,scrName,srcType,DHW,HEATING)


#    def doRefreshEnergySourceTriggered(self):
#        if not self.selectedItem is None:              
#            for i in range(self.selectedItem.childCount()):
#                if (self.selectedItem.doGetEnergyNodeType().doGetNodeName() != "COOLING"):
#                    #QgsMessageLog.logMessage("DHW:" + "" + str(self.rootNodeSBS_HEATING_DHW.doGetDHW()), tag = "WizardPage1", level=QgsMessageLog.INFO) 
#                    return self.selectedItem.child(i).doComputeBaselineUsefulDemand(self.selectedItem.doGetDHW(),self.selectedItem.doGetHEATING()) 
#                else:
#                    return self.selectedItem.child(i).doComputeBaselineUsefulDemandCooler()
#            QMessageBox.about(self, 'info!', '(' + str(self.selectedItem.childCount()) + ') item(s) updated.')                
#        else:
#            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to refresh data.') 
#            

    def doManageEditEnergySourceTriggered(self, node, key):
        if (node.doCheckIfEnergySourceIsAlreadyPresent(key)):
            self.addEnergydld = AddEnergySourceDlg(self.selectedItem.eParent,self.selectedItem.eName,self.selectedItem.eType)
            self.addEnergydld.doSetTotalEnergyConsumption(self.selectedItem.eFinalEnergyConsumption)
            self.addEnergydld.show()    
            if (node.doGetRootNodeName() == "Single Building Solution"):
                self.addEnergydld.dataUpdated.connect(self.get_dlg_resultsSBS)
            else:
                if (node.doGetRootNodeName() == "District Heating Network"):
                    self.addEnergydld.dataUpdated.connect(self.get_dlg_resultsDHN)
                else:
                    if (node.doGetRootNodeName() == "District Cooling Network"):
                        self.addEnergydld.dataUpdated.connect(self.get_dlg_resultsDCN)
                    else:
                        QMessageBox.about(self, 'info!', '????    ' + node.doGetRootNodeName())               
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to edit energy source. Item not found.')  
                    
    def doEditEnergySourceTriggered(self):
        if not self.selectedItem is None:
            key = self.selectedItem.eParent + "+" + self.selectedItem.eType + "+" + self.selectedItem.eName
            if (self.selectedItem.eParent == self.rootNodeSBS.doGetRootNodeName()):
                self.doManageEditEnergySourceTriggered(self.rootNodeSBS, key) 
            else:
                if (self.selectedItem.eParent == self.rootNodeDCN.doGetRootNodeName()):
                    self.doManageEditEnergySourceTriggered(self.rootNodeDCN, key) 
                else:
                    if (self.selectedItem.eParent == self.rootNodeDHN.doGetRootNodeName()):
                        self.doManageEditEnergySourceTriggered(self.rootNodeDHN, key)
                    else:
                        return            
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to edit energy source.') 
     
    def doDeleteEnergySourceTriggered(self):
        if not self.selectedItem is None:
            key = self.selectedItem.eParent + "+" + self.selectedItem.eType + "+" + self.selectedItem.eName
            if (self.selectedItem.eParent == self.rootNodeSBS.doGetRootNodeName()):
                if (self.rootNodeSBS.doCheckIfEnergySourceIsAlreadyPresent(key)): 
                    self.rootNodeSBS.doRemoveEnergySourceItem(self.selectedItem)
                else:
                    QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove energy source. Item not found.')
            else:
                if (self.selectedItem.eParent == self.rootNodeDCN.doGetRootNodeName()):
                    if (self.rootNodeDCN.doCheckIfEnergySourceIsAlreadyPresent(key)): 
                        self.rootNodeDCN.doRemoveEnergySourceItem(self.selectedItem)
                    else:
                        QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove energy source. Item not found.') 
                else:
                    if (self.selectedItem.eParent == self.rootNodeDHN.doGetRootNodeName()):
                        if (self.rootNodeDHN.doCheckIfEnergySourceIsAlreadyPresent(key)): 
                            self.rootNodeDHN.doRemoveEnergySourceItem(self.selectedItem)
                        else:
                            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove energy source. Item not found.')  
                    else:
                        return
            pp = self.selectedItem.parent()
            pp.removeChild(self.selectedItem)
            self.selectedItem = None
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove energy source.')  
    
    def doAddEnergySourceTriggered(self,parentName,srcName,srcType):
        #QMessageBox.about(self, 'info!', 'parentName: ' + parentName + " srcName: " + srcName + " srcType: " + srcType)
        key = parentName + "+" + srcType + "+" + srcName
        if(parentName == self.rootNodeSBS.doGetRootNodeName()):
            if (self.rootNodeSBS.doCheckIfEnergySourceIsAlreadyPresent(key)):
                QMessageBox.about(self, 'info!', 'Sorry! A source with the same name already exist.')
            else:
                self.addEnergydld = AddEnergySourceDlg(parentName, srcName, srcType)
                self.addEnergydld.dataUpdated.connect(self.get_dlg_resultsSBS)
                self.addEnergydld.show()
        else: 
            if (parentName == self.rootNodeDCN.doGetRootNodeName()):
                if (self.rootNodeDCN.doCheckIfEnergySourceIsAlreadyPresent(key)):
                    QMessageBox.about(self, 'info!', 'Sorry! A source with the same name already exist.' )
                else:
                    self.addEnergydld = AddEnergySourceDlg(parentName,srcName,srcType)
                    self.addEnergydld.dataUpdated.connect(self.get_dlg_resultsDCN)
                    self.addEnergydld.show() 
            else:
                if (parentName == self.rootNodeDHN.doGetRootNodeName()):
                    if (self.rootNodeDHN.doCheckIfEnergySourceIsAlreadyPresent(key)):
                        QMessageBox.about(self, 'info!', 'Sorry! A source with the same name already exist.')
                    else:
                        self.addEnergydld = AddEnergySourceDlg(parentName,srcName,srcType)
                        self.addEnergydld.dataUpdated.connect(self.get_dlg_resultsDHN)
                        self.addEnergydld.show()
                else:
                    QMessageBox.about(self, 'info!', 'parent: ' + parentName + " - root node name: " + self.rootNodeSBS.doGetRootNodeName() )
 


    def doManageGetTechnologyDlgResults(self, node, pkey, tkey, tname, solution, \
                                                DHWEfficiency, DHWPErc, DHWCHP, \
                                                HEATINGEfficiency, HEATINGPErc, HEATINGCHP, \
                                                DHWGridEff, HEATINGGridEff, \
                                                UsefulDemand, ElectrCons, ParamsValidityType, HeatSupplyType):

      if not self.selectedItem is None:          
        energyItem = node.doGetEnergySourceItem(pkey)
        #QgsMessageLog.logMessage("energyItem:" + "" + str(energyItem), tag = 'doManageGetTechnologyDlgResults', level=Qgis.Info)      
        if (energyItem != None):
          #♣node.doGetTechnologyItem(tkey,pkey)
          a = node.doGetTechnologyItem(tkey,pkey)
          #QgsMessageLog.logMessage("Technology key:" + "" + str(a), tag = 'doManageGetTechnologyDlgResults', level=Qgis.Info)      
          if(node.doGetTechnologyItem(tkey,pkey) == None):
            newTechItem = self.doAddTreeTechnologyChild(self.selectedItem,tname, solution, pkey, \
                                                            DHWEfficiency,DHWPErc,DHWCHP,\
                                                            HEATINGEfficiency,HEATINGPErc,HEATINGCHP, \
                                                            DHWGridEff, HEATINGGridEff, ParamsValidityType, HeatSupplyType)            
                
            if (newTechItem != None):
              self.selectedItem.doAddNewTechnology(newTechItem)
              #add the check also about DHW
              self.selectedItem.tSumEfficiencyDHW_COOLER += newTechItem.doGetEfficiencyDHW_COOLER()
              self.selectedItem.tSumPercInTermsOfNumDevicesDHW_COOLER += newTechItem.doGetPercInTermsOfNumDevicesDHW_COOLER()
              # ... idem for the check about HEATING
              self.selectedItem.tSumEfficiencyHEATING += newTechItem.doGetEfficiencyHEATING()
              # e poi quella relativa al numero di users\devices
              self.selectedItem.tSumPercInTermsOfNumDevicesHEATING += newTechItem.doGetPercInTermsOfNumDevicesHEATING() 
              # inside the if add the check about both HEATING and DHW
              if (self.selectedItem.tSumPercInTermsOfNumDevicesDHW_COOLER > 100 or self.selectedItem.tSumPercInTermsOfNumDevicesHEATING> 100):
                self.selectedItem.tSumPercInTermsOfNumDevicesDHW_COOLER =0
                self.selectedItem.tSumEfficiencyDHW_COOLER =0
                self.selectedItem.tSumEfficiencyHEATING=0
                self.selectedItem.tSumPercInTermsOfNumDevicesHEATING=0                    
                reply = QMessageBox.critical(self, r'The sum of % devices\users is equal to 100', r'Please change the % in terms of devices/users!', QMessageBox.Ok, QMessageBox.Default)
                if (reply == QMessageBox.Yes):
                  return True
                else:
                  return False

            else:
                QMessageBox.about(self, 'Info', 'Sorry! Failed to attempt creating technology!')
                                
          else:           
              techItem =  node.doGetTechnologyItem(tkey,pkey)
              #QMessageBox.about(self, 'info!', 'aggiorna la tech')    
              if (techItem != None):
                #♠QMessageBox.about(self, 'info!', 'aggiorna la tech') 
                techItem.doSetFinalEnergyConsumption(energyItem.doGetFinalEnergyConsumption())
                techItem.doSetGridEfficiencyDHW_COOLER(DHWGridEff)
                techItem.doSetCHPDHW(DHWCHP)
                techItem.doSetPercInTermsOfNumDevicesDHW_COOLER(DHWPErc)
                techItem.doSetEfficiencyDHW_COOLER(DHWEfficiency)
                techItem.doSetGridEfficiencyHEATING(HEATINGGridEff)
                techItem.doSetCHPHEATING(HEATINGCHP)
                techItem.doSetPercInTermsOfNumDevicesHEATING(HEATINGPErc)
                techItem.doSetEfficiencyHEATING(HEATINGEfficiency) 
                techItem.doSetParamsValidForDHWAndHEATING(ParamsValidityType)
                techItem.doSetHeatSupplyType(HeatSupplyType)
                techItem.doSetName(tname)
                techItem.setText(1, techItem.doGetPercentages())  
                 #QgsMessageLog.logMessage("Percentages:" + "" + str(techItem.doGetPercentages()), tag = 'doManageGetTechnologyDlgResults', level=Qgis.Info)                                 
              else:
                  QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to update a technology object.')

    @pyqtSlot(str,str,str,str,float,float,float,float,float,float,float,float,float,float,bool,str)
    def get_dlg_Tech_resultsSBS(self, pkey, tkey, tname, solution, \
                                DHWEfficiency, DHWPErc, DHWCHP,\
                                HEATINGEfficiency, HEATINGPErc, HEATINGCHP, \
                                DHWGridEff, HEATINGGridEff, \
                                UsefulDemand, ElectrCons,ParamsValidityType,HeatSupplyType):

        self.doManageGetTechnologyDlgResults(self.rootNodeSBS, pkey, tkey, tname, solution, \
                                DHWEfficiency, DHWPErc, DHWCHP,\
                                HEATINGEfficiency, HEATINGPErc, HEATINGCHP, \
                                DHWGridEff, HEATINGGridEff, \
                                UsefulDemand, ElectrCons,ParamsValidityType,HeatSupplyType)
   

    @pyqtSlot(str,str,str,str,float,float,float,float,float,float,float,float,float,float,bool,str)
    def get_dlg_Tech_resultsDCN(self, pkey, tkey,tname,solution, \
                                DHWEfficiency,DHWPErc,DHWCHP,\
                                HEATINGEfficiency,HEATINGPErc,HEATINGCHP, \
                                DHWGridEff, HEATINGGridEff, \
                                UsefulDemand, ElectrCons,ParamsValidityType,HeatSupplyType):
        self.doManageGetTechnologyDlgResults(self.rootNodeDCN, pkey, tkey, tname, solution, \
                                DHWEfficiency, DHWPErc, DHWCHP,\
                                HEATINGEfficiency, HEATINGPErc, HEATINGCHP, \
                                DHWGridEff, HEATINGGridEff, \
                                UsefulDemand, ElectrCons,ParamsValidityType,HeatSupplyType)
 

    @pyqtSlot(str,str,str,str,float,float,float,float,float,float,float,float,float,float,bool,str)
    def get_dlg_Tech_resultsDHN(self,pkey, tkey,tname,solution, \
                                DHWEfficiency,DHWPErc,DHWCHP,\
                                HEATINGEfficiency,HEATINGPErc,HEATINGCHP, \
                                DHWGridEff, HEATINGGridEff, \
                                UsefulDemand, ElectrCons,ParamsValidityType,HeatSupplyType):
        self.doManageGetTechnologyDlgResults(self.rootNodeDHN, pkey, tkey, tname, solution, \
                                DHWEfficiency, DHWPErc, DHWCHP,\
                                HEATINGEfficiency, HEATINGPErc, HEATINGCHP, \
                                DHWGridEff, HEATINGGridEff, \
                                UsefulDemand, ElectrCons,ParamsValidityType,HeatSupplyType)
    
    def doManageEditTechnologyTriggered(self, node, key, pkey):
            energyItem = node.doGetEnergySourceItem(pkey)
            if (energyItem != None):
                #QMessageBox.about(self,'Info!','Service type is' + str(energyItem.doGetTechType()))
                if(energyItem.doGetTechType()== 'DHW'):
                    self.addTechld = AddTechnologySourceDlg(energyItem.doGetTechType(), self.selectedItem.doGetNodeName(),self.selectedItem.doGetGrandFather(),key,pkey)
                    self.addTechld.doSetTechName(self.selectedItem.doGetNodeName())
                    self.addTechld.doSetEnergyConsumption(self.selectedItem.doGetFinalEnergyConsumption()) 
                    self.addTechld.doSetTechnologyConsumption(self.selectedItem.doGetElectricityConsumptionDHW_COOLER())
                    self.addTechld.doSetHeatExtracted(self.selectedItem.doGetHeatExtractedDHW())                        
                    self.addTechld.doSetUsefulDemand(self.selectedItem.doGetUsefulDemandDHW()) 
                    self.addTechld.doSetPercEndUsersDHW(self.selectedItem.doGetPercInTermsOfNumDevicesDHW_COOLER())
                    self.addTechld.doSetGridEfficiencyDHW(self.selectedItem.doGetGridEfficiencyDHW_COOLER())
                    self.addTechld.doSetEfficiencyDHW(self.selectedItem.doGetEfficiencyDHW_COOLER())
                    self.addTechld.doSetCHPFactorDHW(self.selectedItem.doGetCHPDHW())
                    self.addTechld.doSetHeatSupplyType(self.selectedItem.doGetHeatSupplyType())
                    self.addTechld.show()
                    
                elif(energyItem.doGetTechType()== 'HEATING'):
                    self.addTechld = AddTechnologySourceDlg(energyItem.doGetTechType(), self.selectedItem.doGetNodeName(),self.selectedItem.doGetGrandFather(),key,pkey)
                    self.addTechld.doSetTechName(self.selectedItem.doGetNodeName())
                    self.addTechld.doSetEnergyConsumption(self.selectedItem.doGetFinalEnergyConsumption()) 
                    self.addTechld.doSetTechnologyConsumption(self.selectedItem.doGetElectricityConsumptionHEATING())
                    self.addTechld.doSetHeatExtracted(self.selectedItem.doGetHeatExtractedHEATING())                        
                    self.addTechld.doSetUsefulDemand(self.selectedItem.doGetUsefulDemandHEATING()) 
                    self.addTechld.doSetPercEndUsersHEATING(self.selectedItem.doGetPercInTermsOfNumDevicesHEATING())
                    self.addTechld.doSetCHPFactorHEATING(self.selectedItem.doGetCHPHEATING())
                    self.addTechld.doSetEfficiencyHEATING(self.selectedItem.doGetEfficiencyHEATING()) 
                    self.addTechld.doSetHeatSupplyType(self.selectedItem.doGetHeatSupplyType())
                    self.addTechld.show()
                    
                elif (energyItem.doGetTechType()== 'HEATING+DHW'):
                    self.addTechld = AddTechnologySourceDlg(energyItem.doGetTechType(), self.selectedItem.doGetNodeName(),self.selectedItem.doGetGrandFather(),key,pkey)
                    self.addTechld.doSetTechName(self.selectedItem.doGetNodeName())
                    self.addTechld.doSetEnergyConsumption(self.selectedItem.doGetFinalEnergyConsumption()) 
                    self.addTechld.doSetTechnologyConsumption(self.selectedItem.doGetElectricityConsumptionHEATING_DHW())
                    self.addTechld.doSetHeatExtracted(self.selectedItem.doGetHeatExtractedHEATING_DHW())                        
                    self.addTechld.doSetUsefulDemand(self.selectedItem.doGetUsefulDemand()) 
                    self.addTechld.doSetPercEndUsersDHW(self.selectedItem.doGetPercInTermsOfNumDevicesDHW_COOLER())
                    self.addTechld.doSetGridEfficiencyDHW(self.selectedItem.doGetGridEfficiencyDHW_COOLER())
                    self.addTechld.doSetEfficiencyDHW(self.selectedItem.doGetEfficiencyDHW_COOLER())
                    self.addTechld.doSetCHPFactorDHW(self.selectedItem.doGetCHPDHW())                    
                    self.addTechld.doSetPercEndUsersHEATING(self.selectedItem.doGetPercInTermsOfNumDevicesHEATING())
                    self.addTechld.doSetCHPFactorHEATING(self.selectedItem.doGetCHPHEATING())
                    self.addTechld.doSetEfficiencyHEATING(self.selectedItem.doGetEfficiencyHEATING()) 
                    self.addTechld.doSetParametersAreValidForBoth(self.selectedItem.doGetParamsValidForDHWAndHEATING()) 
                    self.addTechld.doSetHeatSupplyType(self.selectedItem.doGetHeatSupplyType())
                    self.addTechld.show()
                    
                else:
                    self.addTechld_Cooler = AddTechnologySourceDlg(energyItem.doGetTechType(), self.selectedItem.doGetNodeName(),self.selectedItem.doGetGrandFather(),key,pkey)
                    self.addTechld_Cooler.doSetTechName(self.selectedItem.doGetNodeName())
                    self.addTechld_Cooler.doSetEnergyConsumption(self.selectedItem.doGetFinalEnergyConsumption())  
                    self.addTechld_Cooler.doSetTechnologyConsumption(self.selectedItem.doGetElectricityConsumptionDHW_COOLER())
                    self.addTechld_Cooler.doSetHeatExtracted(self.selectedItem.doGetHeatExtractedCooler())                        
                    self.addTechld_Cooler.doSetUsefulDemand(self.selectedItem.doGetUsefulDemandCOOLER()) 
                    self.addTechld_Cooler.doSetGridEfficiencyDHW(self.selectedItem.doGetGridEfficiencyDHW_COOLER())
                    self.addTechld_Cooler.doSetPercEndUsersDHW(self.selectedItem.doGetPercInTermsOfNumDevicesDHW_COOLER())
                    self.addTechld_Cooler.doSetEfficiencyDHW(self.selectedItem.doGetEfficiencyDHW_COOLER())
                    self.addTechld_Cooler.show()
                    
                    
                if (node.doGetRootNodeName() == "Single Building Solution"):
                    self.addTechld.dataUpdated.connect(self.get_dlg_Tech_resultsSBS)
                else:
                    if (node.doGetRootNodeName() == "District Heating Network"):
                        self.addTechld.dataUpdated.connect(self.get_dlg_Tech_resultsDHN) 
                    else:
                        if (node.doGetRootNodeName() == "District Cooling Network"):
                            self.addTechld_Cooler.dataUpdated.connect(self.get_dlg_Tech_resultsDCN)
                        else:
                            QMessageBox.about(self, 'info!', 'Error! Unknown item name: ' + node.doGetRootNodeName())
           
            else:
                QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to edit technology. Item not found.')
   
            
    def doEditTechnologyTriggered(self):
        if not self.selectedItem is None:
            key = self.selectedItem.doGetKey()
            pKey = self.selectedItem.doGetPKey()
            if (self.selectedItem.doGetGrandFather() == self.rootNodeSBS.doGetRootNodeName()):
                self.doManageEditTechnologyTriggered(self.rootNodeSBS,key,pKey)
            else:
                if (self.selectedItem.doGetGrandFather()  == self.rootNodeDCN.doGetRootNodeName()):
                    self.doManageEditTechnologyTriggered(self.rootNodeDCN,key,pKey)
                else:
                    if (self.selectedItem.doGetGrandFather()  == self.rootNodeDHN.doGetRootNodeName()):
                        self.doManageEditTechnologyTriggered(self.rootNodeDHN,key,pKey)
                    else:
                        return     
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to edit technology.') 

    def doDeleteTechnologyTriggered(self):
        if not self.selectedItem is None:
            key = self.selectedItem.doGetKey()
            pKey = self.selectedItem.doGetPKey()
            if (self.selectedItem.doGetGrandFather() == self.rootNodeSBS.doGetRootNodeName()):
              energyItem = self.rootNodeSBS.doGetEnergySourceItem(pKey)
              if (energyItem != None):
                techItem = self.rootNodeSBS.doGetTechnologyItem(key,pKey)
                if (techItem != None):
                  energyItem.doRemoveTechnology(techItem)
                  pp = self.selectedItem.parent()
                  pp.removeChild(self.selectedItem)
                else:
                    QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove technology. Item not found.')
            else:
                if (self.selectedItem.doGetGrandFather() == self.rootNodeDCN.doGetRootNodeName()):
                  energyItem = self.rootNodeDCN.doGetEnergySourceItem(pKey)
                  if (energyItem != None):
                    techItem = energyItem.doGetTechnologyItem(key)
                    if (techItem != None):
                      energyItem.doRemoveTechnology(techItem)
                      pp = self.selectedItem.parent()
                      pp.removeChild(self.selectedItem)
                    else:
                        QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove technology. Item not found.')
                else:
                    if (self.selectedItem.doGetGrandFather() == self.rootNodeDHN.doGetRootNodeName()):
                      energyItem = self.rootNodeDHN.doGetEnergySourceItem(pKey)
                      if (energyItem != None):
                        techItem = self.rootNodeDHN.doGetTechnologyItem(key,pKey)
                        if (techItem != None):
                          energyItem.doRemoveTechnology(techItem)
                          pp = self.selectedItem.parent()
                          pp.removeChild(self.selectedItem)
                        else:
                          QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove technology. Item not found.')
                      else:
                            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove technology. Item not found.')
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to remove technology.') 
            
        
    def doAddTechnologyTriggered(self,eType,parentName,techName,grandFather,parentkey):
        key = parentkey + "+" + techName
        #QMessageBox.about(self, 'info!', 'key' + str(key))
        if(grandFather == self.rootNodeSBS.doGetRootNodeName()):
          energyItem = self.rootNodeSBS.doGetEnergySourceItem(parentkey)
          #QgsMessageLog.logMessage("Energy source item" + str(energyItem), tag = 'doAddTechnologyTriggered' , level=Qgis.Info)	
          if (energyItem != None):
            techItem = self.rootNodeSBS.doGetTechnologyItem(key,parentkey)
            if (techItem !=None):
                QMessageBox.about(self, 'info!', 'Sorry! A technology with the same name already exist.')
            else:
               # QMessageBox.about(self, 'info!', 'Add a new tech')
                self.addTechld = AddTechnologySourceDlg(eType,techName,grandFather,key,parentkey)
                self.addTechld.dataUpdated.connect(self.get_dlg_Tech_resultsSBS)      
                self.addTechld.show()          
        if (grandFather == self.rootNodeDCN.doGetRootNodeName()):    
          energyItem = self.rootNodeDCN.doGetEnergySourceItem(parentkey)
          if (energyItem != None):
            techItem = self.rootNodeDCN.doGetTechnologyItem(key,parentkey)
            if (techItem !=None):
                QMessageBox.about(self, 'info!', 'Sorry! A technology with the same name already exist.')
            else:
                self.addTechld_Cooler = AddTechnologySourceDlg(eType,techName,grandFather,key,parentkey)
                self.addTechld_Cooler.dataUpdated.connect(self.get_dlg_Tech_resultsDCN)
                self.addTechld_Cooler.show()
        if (grandFather == self.rootNodeDHN.doGetRootNodeName()):
          energyItem = self.rootNodeDHN.doGetEnergySourceItem(parentkey)
          if (energyItem != None):
            techItem = self.rootNodeDHN.doGetTechnologyItem(key,parentkey)
            if (techItem !=None):
                QMessageBox.about(self, 'info!', 'Sorry! A technology with the same name already exist.')
            else:
                self.addTechld = AddTechnologySourceDlg(eType,techName,grandFather,key,parentkey)
                self.addTechld.dataUpdated.connect(self.get_dlg_Tech_resultsDHN)
                self.addTechld.show()
                                 
    #papering
    def doDisplayTreeResults(self):                 
        demandToBePrintedHOT =  self.listOfElements[1]
        demandToBePrintedMEDIUM =  self.listOfElements[2]
        demandToBePrintedLOW =  self.listOfElements[3]
        demandToBePrintedDHW =  self.doConvertFloatToString(self.listOfElements[4])
        demandToBePrintedCOOLING =  self.doConvertFloatToString(self.doConvertFloatToString((self.totalUsefulEnergyDemandCOOLER_DHN+ self.totalUsefulEnergyDemandCOOLER_SBS)))
        
      
        if (len(self.listOfElements)>0):
            self.rootDHW.setText(2, demandToBePrintedDHW)
            self.rootCOOLING.setText(2, demandToBePrintedCOOLING) 
            self.rootHEATING_MEDIUM.setText(1,"heat supply 40 -70 °C")
            self.rootHEATING_MEDIUM.setText(2,self.doConvertFloatToString((demandToBePrintedMEDIUM)))
            self.rootHEATING_HOT.setText(1,"heat supply >70°C")
            self.rootHEATING_HOT.setText(2,self.doConvertFloatToString((demandToBePrintedHOT)))
            self.rootHEATING_LOW.setText(1,"heat supply < 40°C")
            self.rootHEATING_LOW.setText(2,self.doConvertFloatToString((demandToBePrintedLOW)))               
        else:
            QMessageBox.about(self, 'Info!','Sorry! The list of elements to be printed is empty')
        
         

    def doClearCompleteResults(self):
        self.dictResultsHEAT_COOLING_TREE.clear()
        self.dictResultsCOOLING_TABLE.clear()
        self.dictResultsHEAT_TABLE.clear()
        self.dictResults.clear()
        self.dictResultsCOOLING.clear()
        
        
    def doClearTreeResults(self):
        #QMessageBox.about(self, 'Info', 'OK qui ci entro')
        self.dictResultsHOT.clear()
        self.dictResultsMEDIUM.clear()
        self.dictResultsLOW.clear()
        self.dictResultsDHW.clear()
        self.totalUsefulEnergyDemandCOOLER_SBS=0
        self.totalUsefulEnergyDemandCOOLER_DHN=0
        self.totalUsefulEnergyDemand_HEATING_DHW_SBS=0
        self.totalUsefulEnergyDemand_HEATING_DHW_DHN=0        
        
    def doSummaryResultsSourceTriggered(self):   
        #♣QMessageBox.about(self, 'Info', str(self.selectedItem.doGetGrandFather().doGetEnergyNodeType()))
        usefulCOOLER_SBS=0
        usefulCOOLER_DCN =0
        usefulHEATING_DHW =0
        usefulDHW=0
        usefulHEATING =0
        usefulHEATING_DHW=0
        
        if not self.selectedItem is None:              
            for i in range(self.selectedItem.childCount()):
                if (self.selectedItem.doGetEnergyNodeType().doGetNodeName() != "COOLING"): 
                    if (self.selectedItem.doGetNodeParentName() == 'Single Building Solution'):
                        if (self.selectedItem.doGetTechType() !='HEATING+DHW'):
                            usefulHEATING = self.selectedItem.child(i).doComputeBaselineUsefulDemandHEATING()
                            usefulDHW  = self.selectedItem.child(i).doComputeBaselineUsefulDemandDHW()
                            self.selectedItem.child(i).doComputeFinalEnergyDHW_COOLER()                            
                            self.selectedItem.child(i).doComputeFinalEnergyHEATING()
                            useful = usefulHEATING+usefulDHW                            
                            self.totalUsefulEnergyDemand_HEATING_DHW_SBS += float(useful)
                            #QgsMessageLog.logMessage("Sum :" + "" + str(self.totalUsefulEnergyDemand_HEATING_DHW_SBS),tag = "doSummaryResultsSourceTriggered", level=Qgis.Info )
                            
                            if (self.selectedItem.child(i).doGetName() != "Comb. Heat & Pow (CHP)"):
                                if ("HP" in self.selectedItem.child(i).doGetName()):
                                  self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsHEATING() 
                                  self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsDHW()                                          
                        else:
                            usefulHEATING_DHW = self.selectedItem.child(i).doComputeBaselineUsefulDemand(self.selectedItem.doGetDHW(),self.selectedItem.doGetHEATING())
                            self.totalUsefulEnergyDemand_HEATING_DHW_SBS += float(usefulHEATING_DHW)
                            self.selectedItem.child(i).doComputeFinalEnergyHEATING_DHW(self.selectedItem.doGetDHW(),self.selectedItem.doGetHEATING())                         
                            if (self.selectedItem.child(i).doGetName() != "Comb. Heat & Pow (CHP)"):
                                if ("HP" in self.selectedItem.child(i).doGetName()):
                                    #QgsMessageLog.logMessage("Technology name:" + "" + str(self.selectedItem.child(i).doGetName()),tag = "doComputeBaselineUsefulDemand", level=QgsMessageLog.INFO )
                                    self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsHEATING_DHW()     
                    elif (self.selectedItem.doGetNodeParentName() == 'District Heating Network'):
                      if (self.selectedItem.doGetTechType() !='HEATING+DHW'):
                        usefulHEATING = self.selectedItem.child(i).doComputeBaselineUsefulDemandHEATING()
                        usefulDHW  = self.selectedItem.child(i).doComputeBaselineUsefulDemandDHW()
                        self.selectedItem.child(i).doComputeFinalEnergyDHW_COOLER()                            
                        self.selectedItem.child(i).doComputeFinalEnergyHEATING()
                        useful = usefulHEATING+usefulDHW                                                  
                        self.totalUsefulEnergyDemand_HEATING_DHW_DHN += float(useful)  
                        #compute the heat extracted for heat pumps
                        self.selectedItem.child(i).doComputeFinalEnergyDHW_COOLER()
                        self.selectedItem.child(i).doComputeFinalEnergyHEATING()
                        if (self.selectedItem.child(i).doGetName() != "Comb. Heat & Pow (CHP)"):
                            if ("HP" in self.selectedItem.child(i).doGetName()):
                                #QgsMessageLog.logMessage("Technology name:" + "" + str(self.selectedItem.child(i).doGetName()),tag = "doComputeBaselineUsefulDemand", level=QgsMessageLog.INFO )
                                self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsHEATING
                                self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsDHW()   
                      else:
                            usefulHEATING_DHW = self.selectedItem.child(i).doComputeBaselineUsefulDemand(self.selectedItem.doGetDHW(),self.selectedItem.doGetHEATING())
                            self.totalUsefulEnergyDemand_HEATING_DHW_DHN += float(usefulHEATING_DHW)
                            self.selectedItem.child(i).doComputeFinalEnergyHEATING_DHW(self.selectedItem.doGetDHW(),self.selectedItem.doGetHEATING())                         
                            if (self.selectedItem.child(i).doGetName() != "Comb. Heat & Pow (CHP)"):
                                if ("HP" in self.selectedItem.child(i).doGetName()):
                                    self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsHEATING_DHW()
                else:
                    if (self.selectedItem.doGetNodeParentName() == 'Single Building Solution'):
                        usefulCOOLER_SBS = self.selectedItem.child(i).doComputeBaselineUsefulDemandCOOLER()
                        self.totalUsefulEnergyDemandCOOLER_SBS += float(usefulCOOLER_SBS)
                        #QgsMessageLog.logMessage("sum COOLING:" + "" + str(self.totalUsefulEnergyDemandCOOLER_SBS),tag = "doSummaryResultsSourceTriggered", level=Qgis.InfO)   
                        self.selectedItem.child(i).doComputeFinalEnergyDHW_COOLER()
                        if (self.selectedItem.child(i).doGetName() != "Comb. Heat & Pow (CHP)"):
                            if ("HP" in self.selectedItem.child(i).doGetName()):
                                self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsCooler()        
                    elif(self.selectedItem.doGetNodeParentName() == 'District Cooling Network'):
                        usefulCOOLER_DCN = self.selectedItem.child(i).doComputeBaselineUsefulDemandCOOLER()
                        self.totalUsefulEnergyDemandCOOLER_DHN += float(usefulCOOLER_DCN)
                        #QgsMessageLog.logMessage("sum COOLING DCN:" + "" + str(self.totalUsefulEnergyDemandCOOLER_DHN),tag = "doSummaryResultsSourceTriggered", level=Qgis.Info)   
                        self.selectedItem.child(i).doComputeFinalEnergyDHW_COOLER()
                        if (self.selectedItem.child(i).doGetName() != "Comb. Heat & Pow (CHP)"):
                            if ("HP" in self.selectedItem.child(i).doGetName()):
                                self.selectedItem.child(i).doComputeHeatExtractedByHeatPumpsCooler()   
              
              
                #self.pushButtonUpdateAllResults.setEnabled(True)
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to refresh data.') 
   
                   
    def doComputeDemandTechnology(self,parent): 
        counterUsefulDemandTotHOT =0 
        counterUsefulDemandTotMEDIUM =0
        counterUsefulDemandTotLOW =0
        counterUsefulDemandDHW =0

        for e in range(parent.childCount()):
            energySourceName = parent.child(e)
            if(parent.childCount()!=0):
                for t in range (parent.child(e).childCount()):
                    if (parent.child(e).childCount()!= 0):
                        techItem = parent.child(e).child(t) 
                        if not techItem is None:
                            key = str(techItem.doGetGrandFather()) + "+" + energySourceName.doGetTechType() + "+" + str(techItem.doGetName()) + "+" + str(techItem.doGetHeatSupplyType())
                            #key = str(techItem.doGetHeatSupplyType())
                            usefulDemand = techItem.doGetUsefulDemand()   
                            usefulDemandHEATING = techItem.doGetUsefulDemandHEATING()   
                            usefulDemandDHW = techItem.doGetUsefulDemandDHW()   
                            QgsMessageLog.logMessage("useful" + "" + str(usefulDemand), tag = "doComputeDemandTechnology", level=Qgis.Info) 
                            #QgsMessageLog.logMessage("DHW useful" + "" + str(usefulDemandDHW), tag = "doComputeDemandTechnology", level=Qgis.Info) 
           
                            # get the corresponding heating supply type
                            self.heatingSupplyType = techItem.doGetHeatSupplyType()
                             
                             
                            if (self.heatingSupplyType == "heat supply >70°C"):
                                self.dictResultsHOT[key]= float(usefulDemand*(energySourceName.doGetHEATING()/100) + usefulDemandHEATING)  
                                QgsMessageLog.logMessage("Dictionary HOT" + "" + str(self.dictResultsHOT), tag = "doComputeDemandTechnology", level=Qgis.Info) 
                                QgsMessageLog.logMessage("heating" + "" + str(energySourceName.doGetHEATING()), tag = "doComputeDemandTechnology", level=Qgis.Info) 
                            elif(self.heatingSupplyType == "heat supply 40 -70 °C"):
                                self.dictResultsMEDIUM[key]= float(usefulDemand*(energySourceName.doGetHEATING()/100) + usefulDemandHEATING)
                                #QgsMessageLog.logMessage("Dictionary MEDIUM" + "" + str(self.dictResultsMEDIUM), tag = "doComputeDemandTechnology", level=Qgis.Info) 
                            elif(self.heatingSupplyType == "heat supply < 40°C"):
                                self.dictResultsLOW[key]= float(usefulDemand*(energySourceName.doGetHEATING()/100) + usefulDemandHEATING)
                           
                            self.dictResultsDHW[key] = float(usefulDemand*(energySourceName.doGetDHW()/100) + usefulDemandDHW)
                            #QgsMessageLog.logMessage("Dictionary DHW" + "" + str(self.dictResultsDHW), tag = "doComputeDemandTechnology", level=Qgis.Info) 
        
        
    
        for key, value in self.dictResultsHOT.items():
            counterUsefulDemandTotHOT += float(value)
            
        for key, value in self.dictResultsMEDIUM.items():
            counterUsefulDemandTotMEDIUM += float(value)
            
        for key, value in self.dictResultsLOW.items():
            counterUsefulDemandTotLOW  += float(value)
            
        for key, value in self.dictResultsDHW.items():
            counterUsefulDemandDHW += float(value)
         

        self.listOfElements =[self.heatingSupplyType,counterUsefulDemandTotHOT,counterUsefulDemandTotMEDIUM,counterUsefulDemandTotLOW,counterUsefulDemandDHW]
             
        #QgsMessageLog.logMessage("List of elements" + "" + str(self.listOfElements), tag = "doComputeDemandTechnology", level=Qgis.Info)      
        self.doDisplayTreeResults()        

    
    def doConvertFloatToString(self,fval):
        return "{0:.1f}".format(float(fval))
      

    def doShowUsefulCompleteResults(self, show=True): 

        # clear the results
        self.doClearCompleteResults()
        # update the useful demand
        self.doUpdateUsefulDemand()
        # instance an object from the class BaselineUsefulDemandResults
        self.details = BaselineUsefulDemandResults(working_directory=self.working_directory, sector=self.sector)
        #QMessageBox.about(self,'Info!','Results list' + str(self.shareUsefulDemand_COOLING))    
        self.details.doUpdateBaselineBox(self.totalUsefulEnergyDemand_HEATING_DHW_SBS, self.totalUsefulEnergyDemand_HEATING_DHW_DHN, self.totalUsefulEnergyDemandCOOLER_SBS, self.totalUsefulEnergyDemandCOOLER_DHN) 
        self.details.doUpdateTree_HEAT(self.dictResults)
        self.details.doUpdateTree_COOLING(self.dictResultsCOOLING)
        self.details.doFillTable_HEATING_DHW(self.dictResultsHEAT_TABLE)
        self.details.doFillTable_COOLING(self.dictResultsCOOLING_TABLE)

        if not show:
            # Softeco updates 05/2019
            self.details.doGenerateOutputJson()
        if show:
            self.details.show()



        

    
    def doOpenMenu(self, point):
        self.selectedItem = self.treeWidgetSolutionsAndSources.itemAt(point)
        if (self.selectedItem == None):
            return
        parent = self.selectedItem.parent()
        if not parent:
            return
        menu = QtWidgets.QMenu()
        if (self.selectedItem.doGetNodeType() == 'EnergySourceTypeNode'):
            if (self.selectedItem.doGetNodeName() == "DHW"):
                #definisce l'azione
                addEnergySourceAction = QtWidgets.QAction(QtGui.QIcon(":/images/add.png"),"Add new energy source",self)
                addEnergySourceAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"no name",self.selectedItem.doGetNodeName()))
                menu.addAction(addEnergySourceAction)
                menu.addSeparator()  
                # add the default natural sources
                addNGLiquidGasAction = QtWidgets.QAction("Natural gas", self)
                addNGLiquidGasAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Gas",self.selectedItem.doGetNodeName()))
                menu.addAction(addNGLiquidGasAction)
                menu.addSeparator()  
                addElectricityAction = QtWidgets.QAction("Electricity", self)
                addElectricityAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Electricity",self.selectedItem.doGetNodeName()))
                menu.addAction(addElectricityAction)
                menu.addSeparator()                             
                addHeatingOilAction = QtWidgets.QAction("Heating oil", self)
                addHeatingOilAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Heating oil",self.selectedItem.doGetNodeName()))
                menu.addAction(addHeatingOilAction)
                menu.addSeparator() 
                addBiomassAction = QtWidgets.QAction("Biomass", self)
                addBiomassAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Biomass",self.selectedItem.doGetNodeName()))
                menu.addAction(addBiomassAction)
                menu.addSeparator() 
                addWasteHeatAction = QtWidgets.QAction("Waste heat", self)
                addWasteHeatAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Waste heat",self.selectedItem.doGetNodeName()))   
                menu.addAction(addWasteHeatAction)
                menu.addSeparator()
                addGeothermalAction = QtWidgets.QAction("Geothermal", self)
                addGeothermalAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Geothermal",self.selectedItem.doGetNodeName()))
                menu.addAction(addGeothermalAction)
                menu.addSeparator()                             
                addSolarThermalAction = QtWidgets.QAction("Solar thermal", self)
                addSolarThermalAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Solar thermal",self.selectedItem.doGetNodeName()))
                menu.addAction(addSolarThermalAction)
                menu.addSeparator()                              
                addCoalPeatAction = QtWidgets.QAction("Coal/Peat", self)
                addCoalPeatAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Coal/Peat",self.selectedItem.doGetNodeName()))
                menu.addAction(addCoalPeatAction)
                menu.addSeparator()                  
                    
            else:
                if (self.selectedItem.doGetNodeName() == "HEATING"):
                    addEnergySourceAction = QtWidgets.QAction(QtGui.QIcon(":/images/add.png"),"Add new energy source")
                    addEnergySourceAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"no name",self.selectedItem.doGetNodeName()))
                    menu.addAction(addEnergySourceAction)
                    menu.addSeparator()
                    # MODIFICATA DA ME 
                    #Idea: add all of the default sources to the context menu
                    #Create the actions and connect to the signals
                    addNGLiquidGasAction = QtWidgets.QAction("Natural gas", self)
                    addNGLiquidGasAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Gas",self.selectedItem.doGetNodeName()))
                    menu.addAction(addNGLiquidGasAction)
                    menu.addSeparator()  
                    addElectricityAction = QtWidgets.QAction("Electricity", self)
                    addElectricityAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Electricity",self.selectedItem.doGetNodeName()))
                    menu.addAction(addElectricityAction)
                    menu.addSeparator()                             
                    addHeatingOilAction = QtWidgets.QAction("Heating oil", self)
                    addHeatingOilAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Heating oil",self.selectedItem.doGetNodeName()))
                    menu.addAction(addHeatingOilAction)
                    menu.addSeparator() 
                    addBiomassAction = QtWidgets.QAction("Biomass", self)
                    addBiomassAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Biomass",self.selectedItem.doGetNodeName()))
                    menu.addAction(addBiomassAction)
                    menu.addSeparator() 
                    addWasteHeatAction = QtWidgets.QAction("Waste heat", self)
                    addWasteHeatAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Waste heat",self.selectedItem.doGetNodeName()))
                    menu.addAction(addWasteHeatAction)
                    menu.addSeparator()
                    addGeothermalAction = QtWidgets.QAction("Geothermal", self)
                    addGeothermalAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Geothermal",self.selectedItem.doGetNodeName()))
                    menu.addAction(addGeothermalAction)
                    menu.addSeparator()                             
                    addSolarThermalAction = QtWidgets.QAction("Solar thermal", self)
                    addSolarThermalAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Solar thermal",self.selectedItem.doGetNodeName()))
                    menu.addAction(addSolarThermalAction)
                    menu.addSeparator()                              
                    addCoalPeatAction = QtWidgets.QAction("Coal/Peat", self)
                    addCoalPeatAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Coal/Peat",self.selectedItem.doGetNodeName()))
                    menu.addAction(addCoalPeatAction)
                    menu.addSeparator()    
                else:
                    if (self.selectedItem.doGetNodeName() == "COOLING"):
                        addEnergySourceAction = QtWidgets.QAction(QtGui.QIcon(":/images/add.png"),"Add new energy source",self)
                        addEnergySourceAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"no name",self.selectedItem.doGetNodeName()))
                        menu.addAction(addEnergySourceAction)
                        menu.addSeparator() 
                        addElectricityAction = QtWidgets.QAction("Electricity", self)
                        addElectricityAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Electricity",self.selectedItem.doGetNodeName()))
                        menu.addAction(addElectricityAction)
                        menu.addSeparator() 
                        addNGLiquidGasAction = QtWidgets.QAction("Natural gas", self)
                        addNGLiquidGasAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Gas",self.selectedItem.doGetNodeName()))
                        menu.addAction(addNGLiquidGasAction)
                        menu.addSeparator()        
                        addGeothermalAction = QtWidgets.QAction("Geothermal", self)
                        addGeothermalAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Geothermal",self.selectedItem.doGetNodeName()))
                        menu.addAction(addGeothermalAction)
                        menu.addSeparator()    
                        addWasteHeatAction = QtWidgets.QAction("Waste heat", self)
                        addWasteHeatAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Waste heat",self.selectedItem.doGetNodeName()))
                        menu.addAction(addWasteHeatAction)
                    else:
                        if (self.selectedItem.doGetNodeName() == "HEATING+DHW"):    
                            addEnergySourceAction = QtWidgets.QAction(QtGui.QIcon(":/images/add.png"),"Add new energy source",self)
                            addEnergySourceAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"no name",self.selectedItem.doGetNodeName()))
                            menu.addAction(addEnergySourceAction)
                            menu.addSeparator() 
                            #MODIFICATA DA ME!!!!!!! aggiunta un nuovo item del context menu che permette all'utente di selezionare lo share di DHW e HEATING
                            addShareHeatingAndDHWAction = QtWidgets.QAction(QtGui.QIcon(":/images/add.png"),"Assign share HEATING and DHW",self)
                            addShareHeatingAndDHWAction.triggered.connect(lambda: self.doAssignShareDlgTriggered(self.selectedItem.doGetNodeParentName(),"no name",self.selectedItem.doGetNodeName()))
                            menu.addAction(addShareHeatingAndDHWAction)
                            menu.addSeparator()                            
                            #MODIFICATA DA ME
                            addNGLiquidGasAction = QtWidgets.QAction("Natural gas", self)
                            addNGLiquidGasAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Gas",self.selectedItem.doGetNodeName()))
                            menu.addAction(addNGLiquidGasAction)
                            menu.addSeparator()  
                            addElectricityAction = QtWidgets.QAction("Electricity", self)
                            addElectricityAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Electricity",self.selectedItem.doGetNodeName()))
                            menu.addAction(addElectricityAction)
                            menu.addSeparator()                             
                            addHeatingOilAction = QtWidgets.QAction("Heating oil", self)
                            addHeatingOilAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Heating oil",self.selectedItem.doGetNodeName()))
                            menu.addAction(addHeatingOilAction)
                            menu.addSeparator() 
                            addBiomassAction = QtWidgets.QAction("Biomass", self)
                            addBiomassAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Biomass",self.selectedItem.doGetNodeName()))
                            menu.addAction(addBiomassAction)
                            menu.addSeparator() 
                            addWasteHeatAction = QtWidgets.QAction("Waste heat", self)
                            addWasteHeatAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Waste heat",self.selectedItem.doGetNodeName()))
                            menu.addAction(addWasteHeatAction)
                            menu.addSeparator()
                            addGeothermalAction = QtWidgets.QAction("Geothermal", self)
                            addGeothermalAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Geothermal",self.selectedItem.doGetNodeName()))
                            menu.addAction(addGeothermalAction)
                            menu.addSeparator()                             
                            addSolarThermalAction = QtWidgets.QAction("Solar thermal", self)
                            addSolarThermalAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Solar thermal",self.selectedItem.doGetNodeName()))
                            menu.addAction(addSolarThermalAction)
                            menu.addSeparator()                              
                            addCoalPeatAction = QtWidgets.QAction("Coal/Peat", self)
                            addCoalPeatAction.triggered.connect(lambda: self.doAddEnergySourceTriggered(self.selectedItem.doGetNodeParentName(),"Coal/Peat",self.selectedItem.doGetNodeName()))
                            menu.addAction(addCoalPeatAction)
                            menu.addSeparator()    
        else:
            if (self.selectedItem.doGetNodeType() == 'EnergySourceNode'):
                deleteEnergySourceAction = QtWidgets.QAction(QtGui.QIcon(":/images/delete.png"),"Remove",self)
                deleteEnergySourceAction.triggered.connect(self.doDeleteEnergySourceTriggered)
                menu.addAction(deleteEnergySourceAction)
                menu.addSeparator()  
                editEnergySourceAction = QtWidgets.QAction(QtGui.QIcon(":/images/edit.png"),"Edit source",self)
                editEnergySourceAction.triggered.connect(self.doEditEnergySourceTriggered)              
                menu.addAction(editEnergySourceAction) 
                computeTechnologyAction = QtWidgets.QAction(QtGui.QIcon(":/images/calculator.png"),"Calculate partial results",self)
                computeTechnologyAction.triggered.connect(self.doSummaryResultsSourceTriggered)
                menu.addAction(computeTechnologyAction)               
                menu.addSeparator()
                addTechAction = QtWidgets.QAction(QtGui.QIcon(":/images/add.png"),"Add new technology",self)
                addTechAction.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"no name",self.selectedItem.doGetNodeParentName(), self.selectedItem.doGetKey()))
                menu.addAction(addTechAction)
                menu.addSeparator()                 
                if (self.selectedItem.eType != "COOLING"):
                    addBoiler = QtWidgets.QAction("Boiler", self)
                    addBoiler.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"Boiler",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addBoiler)
                    menu.addSeparator() 
                    addCHP = QtWidgets.QAction("Comb. Heat & Pow", self)
                    addCHP.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"Comb. Heat & Pow",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addCHP)
                    menu.addSeparator() 
                    addHeatExchanger = QtWidgets.QAction("Heat Exchanger", self)
                    addHeatExchanger.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"Heat Exchanger",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHeatExchanger)
                    menu.addSeparator() 
                    addHeater = QtWidgets.QAction("Heater", self)
                    addHeater.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"Heater",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHeater)
                    menu.addSeparator() 
                    addHPAir = QtWidgets.QAction("HP Air", self)
                    addHPAir.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"HP Air",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHPAir)
                    menu.addSeparator() 
                    addHeatPumpWasteHeat = QtWidgets.QAction("HP Waste heat", self)
                    addHeatPumpWasteHeat.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"HP Waste heat",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHeatPumpWasteHeat)
                    menu.addSeparator()  
                    addHeatPumpGeothermal = QtWidgets.QAction("HP Geothermal", self)
                    addHeatPumpGeothermal.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"HP Geothermal",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHeatPumpGeothermal)
                    menu.addSeparator() 
                    addAbsorptionHeatPump = QtWidgets.QAction("GAHP Air", self)
                    addAbsorptionHeatPump.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"GAHP Air",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addAbsorptionHeatPump)
                    menu.addSeparator() 
                    addAbsorptionHeatPumpWaste = QtWidgets.QAction("GAHP Waste heat", self)
                    addAbsorptionHeatPumpWaste.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"GAHP Waste heat",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addAbsorptionHeatPumpWaste)
                    menu.addSeparator() 
                    addAbsorptionHeatPumpGeothermal = QtWidgets.QAction("GAHP Geothermal", self)
                    addAbsorptionHeatPumpGeothermal.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"GAHP Geothermal",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addAbsorptionHeatPumpGeothermal)
                    menu.addSeparator() 
                    addSolarThermalAction = QtWidgets.QAction("Thermal collectors",self)
                    addSolarThermalAction.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"Thermal collectors",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addSolarThermalAction)
                    menu.addSeparator()  
                    addTubeSolarAction = QtWidgets.QAction("Solar tube (ETC)",self)
                    addTubeSolarAction.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"Solar tube (ETC)",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addTubeSolarAction)
                    menu.addSeparator() 
                else:
                    addHeatExchanger = QtWidgets.QAction("Heat Exchanger", self)
                    addHeatExchanger.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"Heat Exchanger",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))	
                    menu.addAction(addHeatExchanger)
                    menu.addSeparator() 
                    addHPAir = QtWidgets.QAction("HP Air", self)
                    addHPAir.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"HP Air",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHPAir)
                    menu.addSeparator() 
                    addHeatPumpWasteHeat = QtWidgets.QAction("HP Waste Heat", self)
                    addHeatPumpWasteHeat.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"HP Waste heat",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHeatPumpWasteHeat)
                    menu.addSeparator()  
                    addHeatPumpGeothermal = QtWidgets.QAction("HP Geothermal", self)
                    addHeatPumpGeothermal.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"HP Geothermal",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addHeatPumpGeothermal)
                    menu.addSeparator() 
                    addAbsorptionHeatPump = QtWidgets.QAction("GAHP Air", self)
                    addAbsorptionHeatPump.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"GAHP Air",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addAbsorptionHeatPump)
                    menu.addSeparator() 
                    addAbsorptionHeatPumpWaste = QtWidgets.QAction("GAHP Waste heat", self)
                    addAbsorptionHeatPumpWaste.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"GAHP Waste heat",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addAbsorptionHeatPumpWaste)
                    menu.addSeparator() 
                    addAbsorptionHeatPumpGeothermal = QtWidgets.QAction("GAHP Geothermal", self)
                    addAbsorptionHeatPumpGeothermal.triggered.connect(lambda: self.doAddTechnologyTriggered(self.selectedItem.doGetTechType(),self.selectedItem.doGetNodeName(),"GAHP Geothermal",self.selectedItem.doGetNodeParentName(),self.selectedItem.doGetKey()))
                    menu.addAction(addAbsorptionHeatPumpGeothermal)
                    menu.addSeparator() 
            else:
                if (self.selectedItem.doGetNodeType() == 'TechnologyNode'):
                    deleteTechnologyAction = QtWidgets.QAction(QtGui.QIcon(":/images/delete.png"),"Remove",self)
                    deleteTechnologyAction.triggered.connect(self.doDeleteTechnologyTriggered)
                    menu.addAction(deleteTechnologyAction)
                    menu.addSeparator()  
                    editTechnologyAction = QtWidgets.QAction(QtGui.QIcon(":/images/edit.png"),"Edit technology",self)
                    editTechnologyAction.triggered.connect(self.doEditTechnologyTriggered)
                    menu.addAction(editTechnologyAction)  
                    menu.addSeparator()  
                else:
                    QMessageBox.about(self, 'info!', self.selectedItem.text(0) + " - " + parent.text(0) )
        menu.exec(self.treeWidgetSolutionsAndSources.viewport().mapToGlobal(point))
        
    def doCheckAllNodes(self):
        return ((self.rootNodeSBS != None) and (self.rootNodeSBS_DHW != None) and (self.rootNodeSBS_HEATING != None) and (self.rootNodeSBS_HEATING_DHW != None) and (self.rootNodeSBS_COOLING != None) and (self.rootNodeDHN != None) and (self.rootNodeDHN_DHW != None) and (self.rootNodeDHN_HEATING != None) and (self.rootNodeDHN_HEATING_DHW != None) and (self.rootNodeDCN != None) and (self.rootNodeDCN_COOLING != None))   
    
    def doClearOverallResultsForOutput(self):
        self.detailedResults["HEAT"].clear()
        self.detailedResults["COOLING"].clear()
    
    def doPrepareTreeViewSolutions(self):
        self.jscenario = ""
        headerTitle = "Solutions" + ";"
       # self.dictResults = {}
#        self.dictResultsDHW = {}
#        self.dictResultsHEATING = {}
#        self.dictResultsCOOLING = {}
        
        
#        self.detailedResults = {}
#        self.detailedResults["HEAT"] = {}
#        self.detailedResults["COOLING"] = {}
        
        self.usefulDemandHeatDHW = {}
        self.consumedEnergyHPHeatDHW = {}
        self.extractedHeatHPHeatDHW = {}  
        self.usefulDemandCOOLING = {}             
        self.consumedEnergyHPCOOLING = {} 
        self.extractedHeatHPCOOLING = {}           
        self.treeWidgetSolutionsAndSources.setRootIsDecorated(True)
        self.treeWidgetSolutionsAndSources.setColumnCount(2)
        #self.treeWidgetSolutionsAndSources.setHeaderLabels(("Solutions;Share in terms of nr. of devices/end users").split(";"))
        # MODIFICA FATTA DA ME
        self.treeWidgetSolutionsAndSources.setHeaderLabels(headerTitle.split(";"))
        self.treeWidgetSolutionsAndSources.expandAll()  
        self.treeWidgetSolutionsAndSources.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
        self.rootNodeSBS = self.doAddTreeRoot('Single Building Solution')
        self.rootNodeSBS_DHW = self.doAddTreeEnergySourceTypeChild(self.rootNodeSBS,"DHW",':/images/hot_water.png')
        self.rootNodeSBS_HEATING = self.doAddTreeEnergySourceTypeChild(self.rootNodeSBS,"HEATING",':/images/heating.png')
        self.rootNodeSBS_HEATING_DHW = self.doAddTreeEnergySourceTypeChild(self.rootNodeSBS,"HEATING+DHW",':/images/heatingDHW.png')
        self.rootNodeSBS_COOLING = self.doAddTreeEnergySourceTypeChild(self.rootNodeSBS,"COOLING",':/images/cooler.png')        
        
        self.rootNodeDHN = self.doAddTreeRoot('District Heating Network')
        self.rootNodeDHN_DHW = self.doAddTreeEnergySourceTypeChild(self.rootNodeDHN,"DHW",':/images/hot_water.png')
        self.rootNodeDHN_HEATING = self.doAddTreeEnergySourceTypeChild(self.rootNodeDHN,"HEATING",':/images/heating.png')
        self.rootNodeDHN_HEATING_DHW = self.doAddTreeEnergySourceTypeChild(self.rootNodeDHN,"HEATING+DHW",':/images/heatingDHW.png')         
        
        self.rootNodeDCN = self.doAddTreeRoot('District Cooling Network')
        self.rootNodeDCN_COOLING = self.doAddTreeEnergySourceTypeChild(self.rootNodeDCN,"COOLING",':/images/cooler.png')  
        
    #pippo    
    # Purpose of the function: perepare the treeView for the results inside the mapping module
    def doTreeViewResults(self):
        headerTitle = "Baseline scenario - Useful energy demand [MWh/y]"
        self.treeViewResults.setRootIsDecorated(True)  
        self.treeViewResults.setColumnCount(3)
        self.treeViewResults.setHeaderLabel(headerTitle)
        self.treeViewResults.setHeaderLabels(("Type of service;Temperature levels;Useful demand - (Single Building Solutions & District Heating and Cooling network)").split(";"))
        self.treeViewResults.expandAll()
    
        
        self.rootHEATING = self.doAddTreeViewResultsRoot('HEATING')
        self.rootDHW = self.doAddTreeViewResultsRoot('DHW')
        self.rootCOOLING = self.doAddTreeViewResultsRoot('COOLING')
        
        # add the children of HEATING node
        self.rootHEATING_HOT = self.doAddTreeViewHEATINGChild(self.rootHEATING, 'HIGH',':/images/highVector.png')
        self.rootHEATING_MEDIUM = self.doAddTreeViewHEATINGChild(self.rootHEATING, 'MEDIUM', ':/images/mediumVector.png')
        self.rootHEATING_LOW = self.doAddTreeViewHEATINGChild(self.rootHEATING, 'LOW', ':/images/lowVector.png')
        
        #add the child to the treeWidget
          
        
    # purpose of the function: this slot needs to populate the tree    
    def doPopulateTreeViewCalcs(self):
        if (self.doCheckAllNodes()):  
            # do calculations for the heating type node
            self.doComputeDemandTechnology(self.rootNodeSBS_DHW)
            self.doComputeDemandTechnology(self.rootNodeSBS_HEATING) 
            self.doComputeDemandTechnology(self.rootNodeSBS_COOLING)
            self.doComputeDemandTechnology(self.rootNodeSBS_HEATING_DHW)
            self.doComputeDemandTechnology(self.rootNodeDHN_DHW)
            self.doComputeDemandTechnology(self.rootNodeDHN_HEATING)
            self.doComputeDemandTechnology(self.rootNodeDHN_HEATING_DHW)
            self.doComputeDemandTechnology(self.rootNodeDCN_COOLING)
            #enable the other buttons
            self.pushButtonShowDetails.setEnabled(True)
            self.pushButtonExportResults.setEnabled(True)   
            #pluto
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed attempting to refresh calculations')   
        
        
    
    def doInitData(self):
        self.dictResultsHOT={}
        self.dictResultsMEDIUM={}
        self.dictResultsLOW={}
        self.dictResults={}
        self.dictResultsDHW ={}
        self.dictResultSBS={}
        self.dictResultDHN={}
        self.dictResultDCN={}
        self.dictResultsCOOLING={}
        self.dictResultsHEAT_COOLING_TREE={}
        self.dictResultsCOOLING_TREE={}
        self.dictResultsHEAT_TABLE={}
        self.dictResultsCOOLING_TABLE={}       
        self.shareUsefulDemandHEAT =0
        self.shareUsefulDemand_COOLING=0
        self.totalUsefulEnergyDemand =0
        self.totalUsefulEnergyDemand_HEATING_DHW_SBS =0
        self.totalUsefulEnergyDemand_DHW_SBS=0
        self.totalUsefulEnergyDemand_HEATING_SBS=0
        self.totalUsefulEnergyDemand_DHW_DHN=0
        self.totalUsefulEnergyDemand_HEATING_DHN=0
        self.totalUsefulEnergyDemand_HEATING_DHW_DHN=0
        self.totalUsefulEnergyDemandCOOLER_DHN=0
        self.totalUsefulEnergyDemandCOOLER_SBS=0
        self.totalUsefulEnergyDemandCOOLER=0
        self.totalFinalEnergyConsumptionPerSource =0
        self.totalFinalEnergyConsumptionPerSourceCooler=0
        self.totScenarios=0
        self.percentage_COOLER =0
        self.percentage_HEAT=0
        self.heatingSupplyType="heat supply 40 -70 °C"
        self.listOfElements=[]
        self.resultsRESIDENTIAL_SECTOR_COOLING=''
        self.resultsRESIDENTIAL_SECTOR_HEATING_DHW=''
        self.resultsTERTIARY_SECTOR_COOLING=''
        self.resultsTERTIARY_SECTOR_HEATING_DHW=''
        
        
    
    
    def doUpdateUsefulDemand(self):
      treeCompleteResult= genericResult()
      treeCompleteResultHP = genericResult()
      treeCompleteResultHP_WASTE_HEAT = genericResult()
      treeCompleteResultHP_GEO = genericResult()
      treeCompleteResultBoiler = genericResult()
      treeCompleteResultGAHP = genericResult()
      treeCompleteResultGAHP_WASTE_HEAT = genericResult()
      treeCompleteResultGAHP_GEO = genericResult()
      treeCompleteResultHEAT_EXCHANGER = genericResult()
      treeCompleteResultCHP = genericResult()
      treeCompleteResultOther = genericResult()
      treeCompleteResultHEAT_EXCHANGER_COOLER = genericResult()
      treeCompleteResultGAHP_COOLER = genericResult()
      treeCompleteResultGAHP_COOLER_WASTE_HEAT = genericResult()
      treeCompleteResultGAHP_COOLER_GEO = genericResult()
      treeCompleteResultHP_COOLER= genericResult()
      treeCompleteResultHP_COOLER_WASTE_HEAT = genericResult()
      treeCompleteResultHP_COOLER_GEO = genericResult()
      
      if (self.doCheckAllNodes()):  
       
            # clear results
            self.doClearCompleteResults()
            
            # do calculations for the heating type node
            self.doUpdateSingleNodeDemand(self.rootNodeSBS_DHW)
            self.doUpdateSingleNodeDemand(self.rootNodeSBS_HEATING)
            self.doUpdateSingleNodeDemand(self.rootNodeSBS_HEATING_DHW)
            self.doUpdateSingleNodeDemand(self.rootNodeSBS_COOLING)
            self.doUpdateSingleNodeDemand(self.rootNodeDHN_DHW)          
            self.doUpdateSingleNodeDemand(self.rootNodeDHN_HEATING)
            self.doUpdateSingleNodeDemand(self.rootNodeDHN_HEATING_DHW)
            self.doUpdateSingleNodeDemand(self.rootNodeDCN_COOLING)         
            #pluto
            
  
            # after updating all results dictionary
            for key,value in self.dictResultsHEAT_COOLING_TREE.items():
              subKey = value.doGetNodeName()
              parentKey = value.doGetFather().doGetNodeName()
              grandFatherKey = value.doGetFather().doGetTechType()
              #QgsMessageLog.logMessage("Type of service" + "" + str(parentKey),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                    
              if 'COOLING' not in grandFatherKey:
                if grandFatherKey == 'HEATING' or grandFatherKey == 'DHW':
                  #QMessageBox.about(self, 'Info','HEATING OR DHW')
                  if 'Heater' in key:
                    treeCompleteResult.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                    treeCompleteResult.DHWusefulDemand += value.doGetUsefulDemandDHW()
                    treeCompleteResult.usefulDemand += value.doGetUsefulDemand()
                    treeCompleteResult.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                    treeCompleteResult.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()
                    treeCompleteResult.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                    self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResult.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResult.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResult.usefulDemand),self.doConvertFloatToString(treeCompleteResult.percOnTotUsefulDemand)]
                    self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResult.electricityConsumedDHW_COOLER + treeCompleteResult.electricityConsumedHEATING)        
                    #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                    
                  elif 'HP Air' in key:
                     treeCompleteResultHP.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultHP.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultHP.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHP.heatExtractedDHW += value.doGetHeatExtractedDHW()
                     treeCompleteResultHP.heatExtractedHEATING += value.doGetHeatExtractedHEATING()
                     treeCompleteResultHP.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultHP.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()
                     treeCompleteResultHP.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHP.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHP.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHP.usefulDemand),self.doConvertFloatToString(treeCompleteResultHP.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultHP.electricityConsumedDHW_COOLER + treeCompleteResultHP.electricityConsumedHEATING) ,int(treeCompleteResultHP.heatExtractedDHW + treeCompleteResultHP.heatExtractedHEATING)]
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                     
                  elif 'HP Waste heat' in key:
                     treeCompleteResultHP_WASTE_HEAT.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultHP_WASTE_HEAT.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultHP_WASTE_HEAT.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHP_WASTE_HEAT.heatExtractedDHW += value.doGetHeatExtractedDHW()
                     treeCompleteResultHP_WASTE_HEAT.heatExtractedHEATING += value.doGetHeatExtractedHEATING()
                     treeCompleteResultHP_WASTE_HEAT.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultHP_WASTE_HEAT.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()
                     treeCompleteResultHP_WASTE_HEAT.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.usefulDemand),self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultHP_WASTE_HEAT.electricityConsumedDHW_COOLER + treeCompleteResultHP_WASTE_HEAT.electricityConsumedHEATING), int(treeCompleteResultHP_WASTE_HEAT.heatExtractedDHW  + treeCompleteResultHP_WASTE_HEAT.heatExtractedHEATING)]       
                     
                  elif 'HP Geothermal' in key:
                     treeCompleteResultHP_GEO.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultHP_GEO.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultHP_GEO.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHP_GEO.heatExtractedDHW += value.doGetHeatExtractedDHW()
                     treeCompleteResultHP_GEO.heatExtractedHEATING += value.doGetHeatExtractedHEATING()
                     treeCompleteResultHP_GEO.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultHP_GEO.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()
                     treeCompleteResultHP_GEO.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHP_GEO.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHP_GEO.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHP_GEO.usefulDemand),self.doConvertFloatToString(treeCompleteResultHP_GEO.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultHP_GEO.electricityConsumedDHW_COOLER + treeCompleteResultHP_GEO.electricityConsumedHEATING), int(treeCompleteResultHP_GEO.heatExtractedDHW +  treeCompleteResultHP_GEO.heatExtractedHEATING)]
                                
                  elif 'Boiler' in key:
                     treeCompleteResultBoiler.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultBoiler.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultBoiler.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultBoiler.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultBoiler.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()
                     treeCompleteResultBoiler.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultBoiler.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultBoiler.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultBoiler.usefulDemand),self.doConvertFloatToString(treeCompleteResultBoiler.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultBoiler.electricityConsumedDHW_COOLER + treeCompleteResultBoiler.electricityConsumedHEATING)        
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
    
                  elif 'GAHP Air' in key:
                     treeCompleteResultGAHP.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultGAHP.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultGAHP.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultGAHP.heatExtractedDHW += value.doGetHeatExtractedDHW()
                     treeCompleteResultGAHP.heatExtractedHEATING += value.doGetHeatExtractedHEATING()
                     treeCompleteResultGAHP.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultGAHP.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                     
                     treeCompleteResultGAHP.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultGAHP.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultGAHP.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP.usefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultGAHP.electricityConsumedDHW_COOLER + treeCompleteResultGAHP.electricityConsumedHEATING)                             
                     
                    #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                  
                  elif 'GAHP Waste heat' in key:
                     treeCompleteResultGAHP_WASTE_HEAT.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultGAHP_WASTE_HEAT.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultGAHP_WASTE_HEAT.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultGAHP_WASTE_HEAT.heatExtractedDHW += value.doGetHeatExtractedDHW()
                     treeCompleteResultGAHP_WASTE_HEAT.heatExtractedHEATING += value.doGetHeatExtractedHEATING()
                     treeCompleteResultGAHP_WASTE_HEAT.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultGAHP_WASTE_HEAT.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                     
                     treeCompleteResultGAHP_WASTE_HEAT.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.usefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultGAHP_WASTE_HEAT.electricityConsumedDHW_COOLER + treeCompleteResultGAHP_WASTE_HEAT.electricityConsumedHEATING), int(treeCompleteResultGAHP_WASTE_HEAT.heatExtractedDHW + treeCompleteResultGAHP_WASTE_HEAT.heatExtractedHEATING)]                             
                     
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                  
                  
                  elif 'GAHP Geothermal' in key:
                     treeCompleteResultGAHP_GEO.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultGAHP_GEO.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultGAHP_GEO.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultGAHP_GEO.heatExtractedDHW += value.doGetHeatExtractedDHW()
                     treeCompleteResultGAHP_GEO.heatExtractedHEATING += value.doGetHeatExtractedHEATING()
                     treeCompleteResultGAHP_GEO.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultGAHP_GEO.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                     
                     treeCompleteResultGAHP_GEO.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultGAHP_GEO.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultGAHP_GEO.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_GEO.usefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_GEO.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultGAHP_GEO.electricityConsumedDHW_COOLER + treeCompleteResultGAHP_GEO.electricityConsumedHEATING), int(treeCompleteResultGAHP_GEO.heatExtractedDHW + treeCompleteResultGAHP_GEO.heatExtractedHEATING)]
                     
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
        
            
    
                  elif 'Heat Exchanger' in key:
                     treeCompleteResultHEAT_EXCHANGER.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultHEAT_EXCHANGER.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultHEAT_EXCHANGER.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHEAT_EXCHANGER.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultHEAT_EXCHANGER.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                     
                     treeCompleteResultHEAT_EXCHANGER.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.usefulDemand),self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultHEAT_EXCHANGER.electricityConsumedDHW_COOLER + treeCompleteResultHEAT_EXCHANGER.electricityConsumedHEATING)                             
                     
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
    
                  elif 'Comb. Heat & Pow' in key:
                     treeCompleteResultCHP.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultCHP.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultCHP.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultCHP.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultCHP.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                      
                     treeCompleteResultCHP.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultCHP.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultCHP.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultCHP.usefulDemand),self.doConvertFloatToString(treeCompleteResultCHP.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultCHP.electricityConsumedDHW_COOLER + treeCompleteResultCHP.electricityConsumedHEATING)                             
                                          
                     
                    #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                     
                  elif 'Other' in key:
                    treeCompleteResultOther.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                    treeCompleteResultOther.DHWusefulDemand += value.doGetUsefulDemandDHW()
                    treeCompleteResultOther.usefulDemand += value.doGetUsefulDemand()
                    treeCompleteResultOther.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                    treeCompleteResultOther.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                       
                    treeCompleteResultOther.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                    self.dictResults[parentKey + "+"  + subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultOther.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultOther.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultOther.usefulDemand),self.doConvertFloatToString(treeCompleteResultOther.percOnTotUsefulDemand)]
                    self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultOther.electricityConsumedDHW_COOLER + treeCompleteResultOther.electricityConsumedHEATING)                             
                    #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                else:
                  if 'Heater' in key:
                    #QgsMessageLog.logMessage("heating:" + "" + str(value.doGetTechHEATING()),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)   
                    treeCompleteResult.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                    treeCompleteResult.DHWusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechDHW()))
                    treeCompleteResult.usefulDemand += value.doGetUsefulDemand()
                    treeCompleteResult.electricityConsumed += value.doGetElectricityConsumptionHEATING_DHW()
                    treeCompleteResult.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                    self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResult.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResult.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResult.usefulDemand),self.doConvertFloatToString(treeCompleteResult.percOnTotUsefulDemand)]
                    self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResult.electricityConsumed)                            
                    #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                  
                  elif 'HP Air' in key:
                     treeCompleteResultHP.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                     treeCompleteResultHP.DHWusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechDHW()))
                     treeCompleteResultHP.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHP.heatExtracted += value.doGetHeatExtractedHEATING_DHW()
                     treeCompleteResultHP.electricityConsumed  += value.doGetElectricityConsumptionHEATING_DHW()
                     treeCompleteResultHP.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHP.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHP.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHP.usefulDemand),self.doConvertFloatToString(treeCompleteResultHP.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultHP.electricityConsumed), int(treeCompleteResultHP.heatExtracted)]
                     
                  elif 'HP Waste heat' in key:
                     treeCompleteResultHP_WASTE_HEAT.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                     treeCompleteResultHP_WASTE_HEAT.DHWusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechDHW()))
                     treeCompleteResultHP_WASTE_HEAT.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHP_WASTE_HEAT.heatExtracted += value.doGetHeatExtractedHEATING_DHW()
                     treeCompleteResultHP_WASTE_HEAT.electricityConsumed += value.doGetElectricityConsumptionHEATING_DHW()
                     treeCompleteResultHP_WASTE_HEAT.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.usefulDemand),self.doConvertFloatToString(treeCompleteResultHP_WASTE_HEAT.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultHP_WASTE_HEAT.electricityConsumed), int(treeCompleteResultHP_WASTE_HEAT.heatExtracted)]
                     
                  elif 'HP Geothermal' in key:
                     treeCompleteResultHP_GEO.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                     treeCompleteResultHP_GEO.DHWusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechDHW()))
                     treeCompleteResultHP_GEO.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHP_GEO.heatExtracted += value.doGetHeatExtractedHEATING_DHW()
                     treeCompleteResultHP_GEO.electricityConsumed += value.doGetElectricityConsumptionHEATING_DHW()
                     treeCompleteResultHP_GEO.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHP_GEO.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHP_GEO.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHP_GEO.usefulDemand),self.doConvertFloatToString(treeCompleteResultHP_GEO.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultHP_GEO.electricityConsumed), int(treeCompleteResultHP_GEO.heatExtracted)]    
          
                  elif 'Boiler' in key:
                     treeCompleteResultBoiler.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                     treeCompleteResultBoiler.DHWusefulDemand += float(value.doGetUsefulDemand()*(value.doGetTechDHW()))
                     treeCompleteResultBoiler.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultBoiler.electricityConsumed += value.doGetElectricityConsumptionHEATING_DHW()
                     treeCompleteResultBoiler.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultBoiler.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultBoiler.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultBoiler.usefulDemand),self.doConvertFloatToString(treeCompleteResultBoiler.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultBoiler.electricityConsumed)  
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
    
                  elif 'GAHP Air' in key:
                     treeCompleteResultGAHP.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultGAHP.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultGAHP.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultGAHP.heatExtracted += value.doGetHeatExtractedHEATING_DHW()
                     treeCompleteResultGAHP.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultGAHP.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                     
                     treeCompleteResultGAHP.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultGAHP.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultGAHP.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP.usefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultGAHP.electricityConsumed), int(treeCompleteResultGAHP.heatExtracted )]
                     
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                  
                  elif 'GAHP Waste heat' in key:
                     treeCompleteResultGAHP_WASTE_HEAT.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultGAHP_WASTE_HEAT.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultGAHP_WASTE_HEAT.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultGAHP_WASTE_HEAT.heatExtracted += value.doGetHeatExtractedHEATING_DHW()
                     treeCompleteResultGAHP_WASTE_HEAT.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultGAHP_WASTE_HEAT.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                     
                     treeCompleteResultGAHP_WASTE_HEAT.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.usefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_WASTE_HEAT.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultGAHP_WASTE_HEAT.electricityConsumed) , int(treeCompleteResultGAHP_WASTE_HEAT.heatExtracted )]
                     
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                                   
                  elif 'GAHP Geothermal' in key:
                     treeCompleteResultGAHP_GEO.HEATINGusefulDemand += value.doGetUsefulDemandHEATING()
                     treeCompleteResultGAHP_GEO.DHWusefulDemand += value.doGetUsefulDemandDHW()
                     treeCompleteResultGAHP_GEO.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultGAHP_GEO.heatExtracted += value.doGetHeatExtractedHEATING_DHW()
                     treeCompleteResultGAHP_GEO.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                     treeCompleteResultGAHP_GEO.electricityConsumedHEATING += value.doGetElectricityConsumptionHEATING()                     
                     treeCompleteResultGAHP_GEO.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultGAHP_GEO.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultGAHP_GEO.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_GEO.usefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_GEO.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = [int(treeCompleteResultGAHP_GEO.electricityConsumed), int(treeCompleteResultGAHP_GEO.heatExtracted)]                             
                     
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
        
                  elif 'Heat Exchanger' in key:
                     treeCompleteResultHEAT_EXCHANGER.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                     treeCompleteResultHEAT_EXCHANGER.DHWusefulDemand += float(value.doGetUsefulDemand()*(value.doGetTechDHW()))
                     treeCompleteResultHEAT_EXCHANGER.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultHEAT_EXCHANGER.electricityConsumed += value.doGetElectricityConsumptionHEATING_DHW()
                     treeCompleteResultHEAT_EXCHANGER.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+ " + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.usefulDemand),self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultHEAT_EXCHANGER.electricityConsumed)  
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
    
                  elif 'Comb. Heat & Pow' in key:
                     treeCompleteResultCHP.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                     treeCompleteResultCHP.DHWusefulDemand += float(value.doGetUsefulDemand()*(value.doGetTechDHW()))
                     treeCompleteResultCHP.usefulDemand += value.doGetUsefulDemand()
                     treeCompleteResultCHP.electricityConsumed += value.doGetElectricityConsumptionHEATING_DHW()
                     treeCompleteResultCHP.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                     self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultCHP.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultCHP.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultCHP.usefulDemand),self.doConvertFloatToString(treeCompleteResultCHP.percOnTotUsefulDemand)]
                     self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultCHP.electricityConsumed)  
                     #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                  
                  
                  elif 'Other' in key:
                    treeCompleteResultOther.HEATINGusefulDemand += float(value.doGetUsefulDemand()* (value.doGetTechHEATING()))
                    treeCompleteResultOther.DHWusefulDemand += float(value.doGetUsefulDemand()*(value.doGetTechDHW()))
                    treeCompleteResultOther.usefulDemand += value.doGetUsefulDemand()
                    treeCompleteResultOther.electricityConsumed += value.doGetElectricityConsumptionHEATING_DHW()
                    treeCompleteResultOther.percOnTotUsefulDemand += value.doGetPercOnUsefulDemand()
                    self.dictResults[parentKey + "+" + subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultOther.HEATINGusefulDemand), self.doConvertFloatToString(treeCompleteResultOther.DHWusefulDemand),self.doConvertFloatToString(treeCompleteResultOther.usefulDemand),self.doConvertFloatToString(treeCompleteResultOther.percOnTotUsefulDemand)]
                    self.dictResultsHEAT_TABLE[parentKey + "+" + subKey] = int(treeCompleteResultOther.electricityConsumed)  
                    #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResults),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)                              
              else:
                  if 'GAHP Air' in key:
                      treeCompleteResultGAHP_COOLER.COOLERusefulDemand += float(value.doGetUsefulDemandCOOLER())
                      treeCompleteResultGAHP_COOLER.percOnTotUsefulDemand += float(value.doGetPercOnUsefulDemand())
                      treeCompleteResultGAHP_COOLER.heatExtracted += float(value.doGetHeatExtractedCooler())
                      treeCompleteResultGAHP_COOLER.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                      self.dictResultsCOOLING[parentKey + "+ "+ subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultGAHP_COOLER.COOLERusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_COOLER.percOnTotUsefulDemand)]
                      self.dictResultsCOOLING_TABLE [parentKey + "+" + subKey] = [int(treeCompleteResultGAHP_COOLER.electricityConsumedDHW_COOLER), int(treeCompleteResultGAHP_COOLER.heatExtracted)] 
                      
                  elif 'GAHP Waste heat' in key:
                      treeCompleteResultGAHP_COOLER_WASTE_HEAT.COOLERusefulDemand += float(value.doGetUsefulDemandCOOLER())
                      treeCompleteResultGAHP_COOLER_WASTE_HEAT.percOnTotUsefulDemand += float(value.doGetPercOnUsefulDemand())
                      treeCompleteResultGAHP_COOLER_WASTE_HEAT.heatExtracted += float(value.doGetHeatExtractedCooler())
                      treeCompleteResultGAHP_COOLER_WASTE_HEAT.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                      self.dictResultsCOOLING[parentKey + "+ "+ subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultGAHP_COOLER_WASTE_HEAT.COOLERusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_COOLER_WASTE_HEAT.percOnTotUsefulDemand)]
                      self.dictResultsCOOLING_TABLE [parentKey + "+" + subKey] = [int(treeCompleteResultGAHP_COOLER_WASTE_HEAT.electricityConsumedDHW_COOLER),int(treeCompleteResultGAHP_COOLER_WASTE_HEAT.heatExtracted)]
                  
                  elif 'GAHP Geothermal' in key:
                      treeCompleteResultGAHP_COOLER_GEO.COOLERusefulDemand += float(value.doGetUsefulDemandCOOLER())
                      treeCompleteResultGAHP_COOLER_GEO.percOnTotUsefulDemand += float(value.doGetPercOnUsefulDemand())
                      treeCompleteResultGAHP_COOLER_GEO.heatExtracted += float(value.doGetHeatExtractedCooler())
                      treeCompleteResultGAHP_COOLER_GEO .electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                      self.dictResultsCOOLING[parentKey + "+ "+ subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultGAHP_COOLER_GEO .COOLERusefulDemand),self.doConvertFloatToString(treeCompleteResultGAHP_COOLER_GEO .percOnTotUsefulDemand)]
                      self.dictResultsCOOLING_TABLE [parentKey + "+" + subKey] = [int(treeCompleteResultGAHP_COOLER_GEO .electricityConsumedDHW_COOLER), int(treeCompleteResultGAHP_COOLER_GEO.heatExtracted)] 
                                           
                  elif 'HP Air' in key:
                       treeCompleteResultHP_COOLER.COOLERusefulDemand += float(value.doGetUsefulDemandCOOLER())
                       treeCompleteResultHP_COOLER.percOnTotUsefulDemand += float(value.doGetPercOnUsefulDemand())
                       treeCompleteResultHP_COOLER.heatExtracted += float(value.doGetHeatExtractedCooler())
                       treeCompleteResultHP_COOLER.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                       self.dictResultsCOOLING[parentKey + "+ "+ subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultHP_COOLER.COOLERusefulDemand),self.doConvertFloatToString(treeCompleteResultHP_COOLER.percOnTotUsefulDemand)]
                       self.dictResultsCOOLING_TABLE [parentKey + "+" + subKey] = [int(treeCompleteResultHP_COOLER.electricityConsumedDHW_COOLER), int(treeCompleteResultHP_COOLER.heatExtracted)]
                     
                  elif 'HP Waste heat' in key:
                        treeCompleteResultHP_COOLER_WASTE_HEAT.COOLERusefulDemand += float(value.doGetUsefulDemandCOOLER())
                        treeCompleteResultHP_COOLER_WASTE_HEAT.percOnTotUsefulDemand += float(value.doGetPercOnUsefulDemand())
                        treeCompleteResultHP_COOLER_WASTE_HEAT.heatExtracted += float(value.doGetHeatExtractedCooler())
                        treeCompleteResultHP_COOLER_WASTE_HEAT.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                        self.dictResultsCOOLING[parentKey + "+ "+ subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultHP_COOLER_WASTE_HEAT.COOLERusefulDemand),self.doConvertFloatToString(treeCompleteResultHP_COOLER_WASTE_HEAT.percOnTotUsefulDemand)]
                        self.dictResultsCOOLING_TABLE [parentKey + "+" + subKey] = [int(treeCompleteResultHP_COOLER_WASTE_HEAT.electricityConsumedDHW_COOLER), int(treeCompleteResultHP_COOLER_WASTE_HEAT.heatExtracted)]
                     
                  elif 'HP Geothermal' in key:
                        treeCompleteResultHP_COOLER_GEO.COOLERusefulDemand += float(value.doGetUsefulDemandCOOLER())
                        treeCompleteResultHP_COOLER_GEO.percOnTotUsefulDemand += float(value.doGetPercOnUsefulDemand())
                        treeCompleteResultHP_COOLER_GEO.heatExtracted += float(value.doGetHeatExtractedCooler())
                        treeCompleteResultHP_COOLER_GEO.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                        self.dictResultsCOOLING[parentKey + "+ "+ subKey] = [str(subKey),self.doConvertFloatToString(treeCompleteResultHP_COOLER_GEO.COOLERusefulDemand),self.doConvertFloatToString(treeCompleteResultHP_COOLER_GEO.percOnTotUsefulDemand)]
                        self.dictResultsCOOLING_TABLE [parentKey + "+" + subKey] = [int(treeCompleteResultHP_COOLER_GEO.electricityConsumedDHW_COOLER), int(treeCompleteResultHP_COOLER_GEO.heatExtracted)]
                     
                 
                  elif 'Heat Exchanger' in key:
                       treeCompleteResultHEAT_EXCHANGER_COOLER.COOLERusefulDemand += float(value.doGetUsefulDemandCOOLER())
                       treeCompleteResultHEAT_EXCHANGER_COOLER.percOnTotUsefulDemand += float(value.doGetPercOnUsefulDemand())
                       treeCompleteResultHEAT_EXCHANGER_COOLER.electricityConsumedDHW_COOLER += value.doGetElectricityConsumptionDHW_COOLER()
                       self.dictResultsCOOLING[parentKey + "+ "+ subKey] = [str(subKey), self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER_COOLER.COOLERusefulDemand),self.doConvertFloatToString(treeCompleteResultHEAT_EXCHANGER_COOLER.percOnTotUsefulDemand)]
                       self.dictResultsCOOLING_TABLE [parentKey + "+" + subKey] = int(treeCompleteResultHEAT_EXCHANGER_COOLER.electricityConsumedDHW_COOLER)
                       #QgsMessageLog.logMessage("dict:" + "" + str(self.dictResultsCOOLING),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
  
        

    def doUpdateSingleNodeDemand(self,parent):
        usefulDemand = 0
      
        for e in range(parent.childCount()):
            for t in range(parent.child(e).childCount()):
                if (parent.child(e).child(t) != None):
                    techItem = parent.child(e).child(t)
                    energySourceName = parent.child(e)
                    techName = techItem.doGetNodeName()
                    key = str(techItem.doGetGrandFather()) + "+" + str(energySourceName.doGetTechType()) + "+" + str(energySourceName.doGetName()) + "+" +techName
                    # istanzio un risultato generico
                    if 'COOLING' not in parent.doGetNodeName():
                      if parent.doGetNodeName() != 'HEATING+DHW':
                        usefulDemand = techItem.doGetUsefulDemandHEATING() + techItem.doGetUsefulDemandDHW()
                        #finalEnergy = techItem.doGetElectricityConsumptionHEATING() + techItem.doGetElectricityConsumptionDHW_COOLER()
                        self.shareUsefulDemandHEAT = (usefulDemand/(self.totalUsefulEnergyDemand_HEATING_DHW_SBS + self.totalUsefulEnergyDemand_HEATING_DHW_DHN))*100
                        techItem.PercOnUsefulDemand = self.shareUsefulDemandHEAT
                        QgsMessageLog.logMessage("share:" + "" + str(self.shareUsefulDemandHEAT),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                        
                        self.percentage_HEAT += float(self.shareUsefulDemandHEAT)                                       
                        self.dictResultsHEAT_COOLING_TREE[key]= techItem
                        #QgsMessageLog.logMessage("Dict HEAT  is:" + "" + str(self.dictResultsHEAT_COOLING_TREE), tag = "doUpdateSingleNodeDemand", level=Qgis.Info) 
                        
                        #[str(techName),self.doConvertFloatToString((float(usefulDemand* (energyItem.doGetDHW()/100)))), self.doConvertFloatToString((float(usefulDemand* (energyItem.doGetHEATING()/100)))), self.doConvertFloatToString(usefulDemand), str(techItem.doGetHeatSupplyType()),self.doConvertFloatToString(self.shareUsefulDemandHEAT) + '%']
                        #self.dictResultsHEAT_TABLE[key] = int(finalEnergy)
                        #♣QgsMessageLog.logMessage("share:" + "" + str(self.dictResultsHEAT_TABLE),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)                                           
                      else:
                         # QgsMessageLog.logMessage("heating+dhw:" + "" + str(techItem.doGetUsefulDemand()),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                          self.shareUsefulDemandHEAT = (techItem.doGetUsefulDemand()/(self.totalUsefulEnergyDemand_HEATING_DHW_SBS + self.totalUsefulEnergyDemand_HEATING_DHW_DHN))*100
                          #QgsMessageLog.logMessage("Dict HEAT  is:" + "" + str(self.shareUsefulDemandHEAT),tag = "doUpdateSingleNodeDemand", level=Qgis.Info) 
                          techItem.PercOnUsefulDemand = self.shareUsefulDemandHEAT                         
                          self.percentage_HEAT += float(self.shareUsefulDemandHEAT)                                       
                          self.dictResultsHEAT_COOLING_TREE[key]= techItem
                          #self.dictResultsHEAT_TABLE[key] = int(techItem.doGetElectricityConsumptionHEATING_DHW())
                        
                          #QgsMessageLog.logMessage("Dict HEAT  is:" + "" + str(self.dictResultsHEAT_COOLING_TREE),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)                         
                    else:
                          # mi servono come variabili di appoggio per sommare le varie percentuali
                          QgsMessageLog.logMessage("Dict COOLING is:" + "" + str(self.dictResultsCOOLING_TREE),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)   
                          self.shareUsefulDemand_COOLING = (techItem.doGetUsefulDemandCOOLER()/(self.totalUsefulEnergyDemandCOOLER_SBS + self.totalUsefulEnergyDemandCOOLER_DHN))*100
                          techItem.PercOnUsefulDemand = self.shareUsefulDemand_COOLING 
                          self.percentage_COOLER += float(self.shareUsefulDemand_COOLING)
                          self.dictResultsHEAT_COOLING_TREE[key] = techItem
                          #self.dictResultsCOOLING_TABLE[key] = int(techItem.doGetElectricityConsumptionDHW_COOLER())
                        
                          #QgsMessageLog.logMessage("Dict COOLING is:" + "" + str(self.dictResultsCOOLING_TREE),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)   
                         # QgsMessageLog.logMessage("Dict FINAL COOLING is:" + "" + str(self.dictResultsCOOLING_TABLE),tag = "doUpdateSingleNodeDemand", level=Qgis.Info)
                else:
                     QMessageBox.about(self,'Info!','Sorry! There is no technology element')
                  

    def doGetSumLists(self,list_Of_Values):
        if(len(list_Of_Values)):
            return 0
        else:
            return list_Of_Values[0] + self.doGetSumLists(list_Of_Values[1:])

    def doConnectActions(self):
        self.treeWidgetSolutionsAndSources.customContextMenuRequested.connect(self.doOpenMenu)
        self.pushButtonSaveTreeToJson.clicked.connect(self.doOpenSaveAsDialog)
        self.pushButtonLoadScenario.clicked.connect(self.doOpenOpenFileDialog)
        self.pushButtonClearTree.clicked.connect(self.doDeleteTree)        
        self.pushButtonUpdateAllResults.clicked.connect(self.doPopulateTreeViewCalcs)
        self.pushButtonShowDetails.clicked.connect(lambda: self.doShowUsefulCompleteResults(show=True))  
        self.pushButtonExportResults.clicked.connect(lambda: self.doShowUsefulCompleteResults(show=False))

            
    def doClearTree(self):
        self.rootNodeSBS.doResetEnergyDict()
        
        for e in range(self.rootNodeSBS_DHW.childCount()):
            self.rootNodeSBS_DHW.removeChild(self.rootNodeSBS_DHW.child(e))
            
        for e in range(self.rootNodeSBS_HEATING.childCount()):          
            self.rootNodeSBS_HEATING.removeChild(self.rootNodeSBS_HEATING.child(e))
            
        for e in range(self.rootNodeSBS_HEATING_DHW.childCount()):          
            self.rootNodeSBS_HEATING_DHW.removeChild(self.rootNodeSBS_HEATING_DHW.child(e))
            
        for e in range(self.rootNodeSBS_COOLING.childCount()):          
            self.rootNodeSBS_COOLING.removeChild(self.rootNodeSBS_COOLING.child(e))   
                        
        self.rootNodeDHN.doResetEnergyDict()
        
        for e in range(self.rootNodeDHN_DHW.childCount()):
            self.rootNodeDHN_DHW.removeChild(self.rootNodeDHN_DHW.child(e))
            
        for e in range(self.rootNodeDHN_HEATING.childCount()):          
            self.rootNodeDHN_HEATING.removeChild(self.rootNodeDHN_HEATING.child(e))
            
        for e in range(self.rootNodeDHN_HEATING_DHW.childCount()):          
            self.rootNodeDHN_HEATING_DHW.removeChild(self.rootNodeDHN_HEATING_DHW.child(e))         
                
        self.rootNodeDCN.doResetEnergyDict()     
        
        for e in range(self.rootNodeDCN_COOLING.childCount()):          
            self.rootNodeDCN_COOLING.removeChild(self.rootNodeDCN_COOLING.child(e))          
        
        self.treeViewResults.clear()
        self.doClearTreeResults()
        
        
    def doFillTreeFromJSON(self):
        if (len(self.jscenario) > 0):
#            self.doClearTree()
            jscen = json.loads(self.jscenario)
            sbs = jscen["Single Building Solution"]  
            for entype in sbs:
                enSources = entype["EnergySources"]
                for energySource in enSources:
                    if (entype["sType"] == "DHW"):
                        eparent = self.doAddTreeEnergySourceChild(self.rootNodeSBS_DHW, "Single Building Solution" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])   
                        self.rootNodeSBS.doAddNewEnergySourceItem(eparent)
                        technologies = energySource ["Technologies"] 
                        for technology in technologies:
                            tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])
                            eparent.doAddNewTechnology(tech)
                    else:
                        if (entype["sType"] == "HEATING"):
                            eparent = self.doAddTreeEnergySourceChild(self.rootNodeSBS_HEATING, "Single Building Solution" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])
                            self.rootNodeSBS.doAddNewEnergySourceItem(eparent)
                            technologies = energySource ["Technologies"] 
                            for technology in technologies:
                                tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])                        
                                eparent.doAddNewTechnology(tech)
                        else:
                            if (entype["sType"] == "HEATING+DHW"):
                                eparent = self.doAddTreeEnergySourceChild(self.rootNodeSBS_HEATING_DHW, "Single Building Solution" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])
                                self.rootNodeSBS.doAddNewEnergySourceItem(eparent)
                                technologies = energySource ["Technologies"] 
                                for technology in technologies:
                                    tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])                            
                                    eparent.doAddNewTechnology(tech)
                            else:
                                if (entype["sType"] == "COOLING"):
                                    eparent = self.doAddTreeEnergySourceChild(self.rootNodeSBS_COOLING, "Single Building Solution" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])
                                    self.rootNodeSBS.doAddNewEnergySourceItem(eparent)
                                    technologies = energySource ["Technologies"] 
                                    for technology in technologies:
                                        tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])        
                                        eparent.doAddNewTechnology(tech)
            dhn = jscen["District Heating Network"]
            for entype in dhn:                            
                enSources = entype["EnergySources"]
                for energySource in enSources:
                    if (entype["sType"] == "DHW"):
                        eparent = self.doAddTreeEnergySourceChild(self.rootNodeDHN_DHW, "District Heating Networkn" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])   
                        self.rootNodeDHN.doAddNewEnergySourceItem(eparent)
                        technologies = energySource ["Technologies"] 
                        for technology in technologies:
                            tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])
                            eparent.doAddNewTechnology(tech)
                    else:
                        if (entype["sType"] == "HEATING"):
                            eparent = self.doAddTreeEnergySourceChild(self.rootNodeDHN_HEATING, "District Heating Network" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])
                            self.rootNodeDHN.doAddNewEnergySourceItem(eparent)
                            technologies = energySource ["Technologies"] 
                            for technology in technologies:
                                tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])                        
                                eparent.doAddNewTechnology(tech)
                        else:
                            if (entype["sType"] == "HEATING+DHW"):
                                eparent = self.doAddTreeEnergySourceChild(self.rootNodeDHN_HEATING_DHW, "District Heating Network" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])
                                self.rootNodeDHN.doAddNewEnergySourceItem(eparent)
                                technologies = energySource ["Technologies"] 
                                for technology in technologies:
                                    tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])                            
                                    eparent.doAddNewTechnology(tech)
            dcn = jscen["District Cooling Network"]                            
            for entype in dcn:                            
                enSources = entype["EnergySources"]
                for energySource in enSources:
                    if (entype["sType"] == "COOLING"):
                        eparent = self.doAddTreeEnergySourceChild(self.rootNodeDCN_COOLING, "District Cooling Network" , energySource["eName"], energySource["eFinalEnergyConsumption"], energySource["eDHW"], energySource["eHeating"], energySource["eType"], energySource["icop"])   
                        self.rootNodeDCN.doAddNewEnergySourceItem(eparent)
                        technologies = energySource ["Technologies"] 
                        for technology in technologies:
                            tech = self.doAddTreeTechnologyChild(eparent, technology["tName"], technology["tGrandFather"], technology["pKey"], technology["tEfficiencyDHW_COOLER"], technology["tPercInTermsOfNumDevicesDHW_COOLER"], technology["tCHPDHW"], technology["tEfficiencyHEATING"], technology["tPercInTermsOfNumDevicesHEATING"], technology["tCHPHEATING"], technology["tGridEfficiencyDHW_COOLER"], technology["tGridEfficiencyHEATING"],technology["ParamsValidForDHWAndHEATING"],technology["HeatSupplyType"])
                            eparent.doAddNewTechnology(tech)
            if (self.doCheckAllNodes()):
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeSBS)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeSBS_HEATING_DHW)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeSBS_DHW)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeSBS_HEATING)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeSBS_COOLING)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeDCN)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeDCN_COOLING)                         
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeDHN)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeDHN_DHW)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeDHN_HEATING)
                self.treeWidgetSolutionsAndSources.expandItem(self.rootNodeDHN_HEATING_DHW)
          
          
# the purpose of the function: clear tree children and the results          
    def doDeleteTree(self):
        self.doClearTreeResults()
        self.doClearCompleteResults()
        self.treeWidgetSolutionsAndSources.clear()
        self.treeViewResults.clear()
        self.doPrepareTreeViewSolutions()
        self.doTreeViewResults()
        self.pushButtonUpdateAllResults.setEnabled(False)
        self.pushButtonShowDetails.setEnabled(False)
        self.pushButtonExportResults.setEnabled(False)
        

                   
    def doOpenSaveAsDialog(self):
        folder = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                master_mapping_config.CMM_BASELINE_FOLDER,
                                master_mapping_config.CMM_WIZARD_FOLDER, "Scenarios")
        #name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save scenario to json')
        os.makedirs(folder, exist_ok = True)
        if self.sector == "Residential Sector":
            name = os.path.join(folder, "scenario_residential.json")
        else:
            name = os.path.join(folder, "scenario_tertiary.json")
        #print("!", name)
        if name is not None:#((len(str(name[0])) > 0)):
            file = open(name, 'w')#str(name[0]),'w')
            text = self.doTreeToJSON()
            file.write(text)
            QMessageBox.about(self, 'info!', 'File ' + str(name) + ' written.' )
            file.close()
        else:
            QMessageBox.about(self, 'info!', 'Invalid filename. Cannot save scenario.' )
            
    def doOpenOpenFileDialog(self): 

        folder = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                master_mapping_config.CMM_BASELINE_FOLDER,
                                master_mapping_config.CMM_WIZARD_FOLDER, "Scenarios")
        
        reply = QMessageBox.question(self, 'Question','Before loading use Clear to remove all already saved information. Loading a new scenario anyway?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            #name = QtWidgets.QFileDialog.getOpenFileName(self, 'Load scenario...')
            if self.sector == "Residential Sector":
                name = os.path.join(folder, "scenario_residential.json")
            else:
                name = os.path.join(folder, "scenario_tertiary.json")
            if os.path.isfile(name):
                file = open(name,'r')
                self.jscenario = file.read()
                file.close()
                self.doFillTreeFromJSON()
                QMessageBox.about(self, 'info!', 'File ' + name + ' loaded.' )
            else:
                #QMessageBox.about(self, 'info!', 'Invalid filename. Cannot load scenario.' )        
                QMessageBox.about(self, 'info!', 'No scenario saved for this project.' )                  
     
                
    def doAddTreeTechnologyChild(self,parent, tname,solution,pkey, \
                                       DHWEfficiency,DHWPErc,DHWCHP,\
                                       HEATINGEfficiency,HEATINGPErc,HEATINGCHP, \
                                       DHWGridEff, HEATINGGridEff, ParamsValidityType, HeatSupplyType):
        icon_path = ":/images/technology.png"
        if ("COOLING" in pkey):
            icon_path = ":/images/ice.png"
        treeItem = Technology(parent, solution, parent.doGetTechType(), tname, pkey, icon_path) 
        if (treeItem != None ):
            treeItem.doSetFinalEnergyConsumption(parent.doGetFinalEnergyConsumption())
            treeItem.doSetGridEfficiencyDHW_COOLER(DHWGridEff)
            treeItem.doSetCHPDHW(DHWCHP)
            treeItem.doSetPercInTermsOfNumDevicesDHW_COOLER(DHWPErc)
            treeItem.doSetEfficiencyDHW_COOLER(DHWEfficiency)
            treeItem.doSetGridEfficiencyHEATING(HEATINGGridEff)
            treeItem.doSetCHPHEATING(HEATINGCHP)
            treeItem.doSetPercInTermsOfNumDevicesHEATING(HEATINGPErc)
            treeItem.doSetEfficiencyHEATING(HEATINGEfficiency)
            treeItem.doSetParamsValidForDHWAndHEATING(ParamsValidityType)
            treeItem.doSetHeatSupplyType(HeatSupplyType)  
            tkey = pkey + "+" + tname 
            #QMessageBox.about(self, 'Info!', 'key' + tkey)
            treeItem.doSetKey(tkey)
            treeItem.doSetPKey(pkey)
            treeItem.setText(1, treeItem.doGetPercentages())   
            if (parent != None):
                parent.addChild(treeItem)
            else:
                QMessageBox.about(self, 'info!', 'Sorry! Failed to append a tree item.')
        return treeItem        
        
        
    def doAddTreeEnergySourceTypeChild(self, parent,stype="",icon=""):
        treeItem = EnergySourceType(parent,stype,icon)
        if (parent != None):
            parent.addChild(treeItem) 
            return treeItem
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed to append a tree item.')    
            
    def doAddTreeEnergySourceChild(self, parent, parentName, srcName, srcEnergyCons, DHW, HEATING, srcType="",icon=""):
        treeItem = EnergySource(parent, parentName, srcName, srcEnergyCons, srcType, icon)
        if (treeItem != None):
            treeItem.doSetFinalEnergyConsumption(srcEnergyCons)
            treeItem.doSetDHW(DHW)
            treeItem.doSetHeating(HEATING)
            #QgsMessageLog.logMessage("Final energy consumption:" + "" + str(srcEnergyCons),tag = "doAddTreeEnergySourceChild", level=QgsMessageLog.INFO) 
            key = parentName + "+" + srcType + "+" + srcName
            treeItem.doSetKey(key)
            if (parent != None):
                parent.addChild(treeItem)
            else:
                QMessageBox.about(self, 'info!', 'Sorry! Failed to append a tree item.') 
        return treeItem
                     
    def doAddTreeRoot(self,name):
        icon_path = ''        
        if (name == "Single Building Solution"):
            icon_path = ':/images/building.png'
        else:
            if (name == "District Heating Network"):
                icon_path = ':/images/networking.png'  
            else:
                icon_path = ':/images/networking_green.png'
        rootnode = Solution(self.treeWidgetSolutionsAndSources, name, icon_path)
        return rootnode
    
########## Functions that are needed to add the elements to the tree
    def doAddTreeViewResultsRoot(self,name):
        if (name == 'HEATING'):
            icon_path = ':/images/heating.png'
        else:
            if (name == 'DHW'):
                icon_path = ':/images/hot_water.png'
            elif (name == 'COOLING') :
                icon_path = ':/images/cooler.png'
            else:
                QMessageBox.about(self, 'Info', 'Sorry! Failed to add the element!')
        rootnodeResults = Solution (self.treeViewResults, name,icon_path )
        return rootnodeResults 

########## Functions that are needed to add the elements to the tree
    def doAddTreeViewHEATINGChild(self, parent, stype="",icon=""):
        treeItem = HeatingNodeType(parent,stype,icon)
        if (parent != None):
            parent.addChild(treeItem) 
            return treeItem
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Failed to append a tree item.')    

        
    def doTreeToJSON(self):
       #d QgsMessageLog.logMessage('ok qui ci entra', tag = 'doTreeToJSON', level=Qgis.Info) 
        if ((self.rootNodeSBS != None) and (self.rootNodeDHN != None) and (self.rootNodeDCN != None)):
            tjson = "{"
            tjson = tjson + '"Single Building Solution":'
            tjson = tjson + "["
            for n in range(self.rootNodeSBS.childCount()):
                tjson = tjson + self.rootNodeSBS.child(n).doEnergySourceTypeToJSON() + ","
                #QgsMessageLog.logMessage('json part:' + str(tjson), tag = 'doTreeToJSON', level=Qgis.Info) 
            if (tjson.endswith(",")):                                          
                tjson = tjson[:-1] 
            tjson = tjson + "]," 
            tjson = tjson + '"District Heating Network":'
            tjson = tjson + "["
            for n in range(self.rootNodeDHN.childCount()):
                tjson = tjson + self.rootNodeDHN.child(n).doEnergySourceTypeToJSON() + ","
            if (tjson.endswith(",")):                                          
                tjson = tjson[:-1] 
            tjson = tjson + "],"                              
            tjson = tjson + '"District Cooling Network":'
            tjson = tjson + "[" 
            for n in range(self.rootNodeDCN.childCount()):
                tjson = tjson + self.rootNodeDCN.child(n).doEnergySourceTypeToJSON() + ","
            if (tjson.endswith(",")):                                          
                tjson = tjson[:-1]                               
            return tjson + "]}" 
        else:
            QMessageBox.about(self, 'info!', 'Sorry! Got an error attempting to write json file.')
                  
    def __init__(self, working_directory=None, sector=None, parent=None):
        super(WizardPage1, self).__init__(parent)
        self.setupUi(self)
        self.working_directory = working_directory
        # qui definisco le variabili globali della class
        self.sector = sector
        self.selectedItem = None
        self.addEnergydld = None
        self.addShareld = None
        self.addTechld = None 
        self.addTechld_Cooler = None
        self.doPrepareTreeViewSolutions()
        self.doTreeViewResults()
        self.doConnectActions()
        self.doInitData()
       # self.doRegisterFieldForNextPage()

        