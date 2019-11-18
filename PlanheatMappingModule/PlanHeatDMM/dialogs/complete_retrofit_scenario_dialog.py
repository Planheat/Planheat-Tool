# -*- coding: utf-8 -*-
"""
   Matching user fields dialog  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 09 Oct. 2017
"""


__docformat__ = "restructuredtext"  

import os
import sys
import datetime


from PyQt5 import uic
from PyQt5 import QtCore,QtWidgets, QtGui
from copy import deepcopy
from dialogs.message_box import showErrordialog
from customWidgets.retrofit_tab import CheckableTabWidget


FONT_PIXEL_SIZE=12    

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'complete_retrofit_scenario_dialog.ui'))


class CompleteRetrofitScenarioDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Shape Fields Mapping Dialog 
     
        Mapping Dialog for match municipality shape fields, with process fields of plugin  
        
        Refresh all records: Delete all changed not saved and back to the last saved point
        
        Delete record: Delete the selected record, equivalent to select a None Value
        
        Delete All records: Delete all records, equivalent to choice a None Value for all records   
          
    """  
    
    def __init__(self, planHeatDMM):
        """ Dialog Constructor"""
        
        super(CompleteRetrofitScenarioDialog, self).__init__(None)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
                
        try:
            
            self.setWindowIcon(QtGui.QIcon(planHeatDMM.plugin_dir + os.path.sep + 'resources/logo.ico'))
            #self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinimizeButtonHint)
            self.setWindowModality(QtCore.Qt.ApplicationModal)
            self.setFixedSize(650,425)
            
            self.planHeatDMM = planHeatDMM
            
            
            
            self.layout = QtWidgets.QVBoxLayout()
            self.setLayout(self.layout)
            
            self.centralLayout = QtWidgets.QVBoxLayout()
            
            refurbishmentTempTabDataList = deepcopy(self.planHeatDMM.data.refurbishmentTabDataList)
            self.checkableTabWidget = CheckableTabWidget(self.planHeatDMM,refurbishmentTempTabDataList,self)
            self.centralLayout.addWidget(self.checkableTabWidget)
            self.layout.addLayout(self.centralLayout)
            self.layout.addWidget(self.buttonBox)
           
            self.layout.addWidget(self.checkableTabWidget)
            
            year = int(datetime.datetime.now().strftime('%Y'))

            if self.planHeatDMM.data.futureScenarioYear > 0:
                year = self.planHeatDMM.data.futureScenarioYear
                
            self.futureScenarioYearSpinBox.setValue(year)
            
            self.setSystemDependantFontSize()
             
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","CompleteRetrofitScenarioDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"CompleteRetrofitScenarioDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
              
        
        
    def accept(self, *args, **kwargs):
        
            
        """ Save mapping data, from widget tabs to tabData"""
        
        try:
            
            self.planHeatDMM.data.refurbishmentTabDataList = []
            
            for tabIndex in range(self.checkableTabWidget.count()):
                tab = self.checkableTabWidget.widget(tabIndex)
                tabData = self.checkableTabWidget.refurbishmentTempTabDataList[tabIndex]
                tabData.rows = tab.retrieveTabData()
               
                self.planHeatDMM.data.refurbishmentTabDataList.append(tabData)
               
            self.planHeatDMM.data.futureScenarioYear = int(self.futureScenarioYearSpinBox.value())
                    
            return QtWidgets.QDialog.accept(self, *args, **kwargs)     
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","CompleteRetrofitScenarioDialog - accept Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"CompleteRetrofitScenarioDialog - accept Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
        return QtWidgets.QDialog.accept(self, *args, **kwargs)    
        
   
 
            
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)         
            
            