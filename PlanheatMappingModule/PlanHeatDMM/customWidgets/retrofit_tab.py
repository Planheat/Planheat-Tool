# -*- coding: utf-8 -*-
"""
   Retrofit scenarios dialog  
   :author: Sergio Aparicio Vegas
   :version: 0.2  
   :date: 27 Nov. 2017
"""


__docformat__ = "restructuredtext"  

import os,sys


from PyQt5 import QtCore,QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from dialogs.message_box import showErrordialog
from model.refurbishment_tab_data import RefurbishmentTabData
from customWidgets.retrofit_widget import RetrofitScenarioWidget


class CheckableTabWidget(QtWidgets.QTabWidget):

    
    
    def __init__(self, planHeatDMM,refurbishmentTempTabDataList,parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        try:
            #self.setDocumentMode(True)
            self.tabBar().setShape(0)
            
            self.setIconSize(QtCore.QSize(24,24))
    
            self.planHeatDMM = planHeatDMM
            self.__log = self.planHeatDMM.resources.log
            self.refurbishmentTempTabDataList = refurbishmentTempTabDataList
            self.checkBoxList = [] 
            
            self.tabDataNames = [tabData.tab_name for tabData in self.refurbishmentTempTabDataList]
                 
            for i, use in enumerate([building_use for building_use in self.planHeatDMM.data.buildingUse if building_use.use.lower() not in ('not evaluate')]):
                #page = QWidget()
                #page.setLayout(QtWidgets.QVBoxLayout())
                self.addTab(i,use.associated_icon_file, use.use)
           
        except:
            self.__log.write_log("ERROR", "CheckableTabWidget Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"CheckableTabWidget",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.planHeatDMM.dlg.statusMessageLabel.setText("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

        
    def addTab(self, position, icon_file, title):
        try:
            
            tabData = None
            
            checkBox = QtWidgets.QCheckBox()
            checkBox.setChecked(True)
            checkBox.stateChanged.connect(lambda:self.__emitStateChanged(checkBox))
            self.checkBoxList.append(checkBox)
                
            if title not in self.tabDataNames:
                tabData = RefurbishmentTabData(position,title,True)
                self.refurbishmentTempTabDataList.append(tabData)
            else:
                for data in self.refurbishmentTempTabDataList:
                        if data.tab_name == title:
                            tabData = data
                            checkBox.setChecked(data.tab_check)
                            break
                
            page = RetrofitScenarioWidget(title, self.planHeatDMM,tabData,self)
                
            if icon_file:
                try:
                    icon  = QtGui.QIcon(self.planHeatDMM.resources.plugin_dir + os.path.sep + "resources" + os.path.sep + icon_file)
                    QtWidgets.QTabWidget.addTab(self, page, icon, title)
                except:
                    QtWidgets.QTabWidget.addTab(self, page, title)
                
            else:   
                QtWidgets.QTabWidget.addTab(self, page, title)
                 
            self.tabBar().setTabButton(self.tabBar().count()-1, QtWidgets.QTabBar.RightSide, checkBox)
              
            
            #self.connect(checkBox, QtCore.SIGNAL('stateChanged(int)'), lambda checkState: self.__emitStateChanged(checkBox, checkState))
        except:
            self.__log.write_log("ERROR", "CheckableTabWidget addTab Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"CheckableTabWidget addTab",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.planHeatDMM.dlg.statusMessageLabel.setText("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
    
    @pyqtSlot()
    def __emitStateChanged(self, checkBox):
        try:
            state = checkBox.isChecked()
            index = self.checkBoxList.index(checkBox)
            self.refurbishmentTempTabDataList[index].tab_check = state
        except:
            self.__log.write_log("ERROR", "CheckableTabWidget emitStateChanged signal Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"CheckableTabWidget emitStateChanged signal",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.planHeatDMM.dlg.statusMessageLabel.setText("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        
        
