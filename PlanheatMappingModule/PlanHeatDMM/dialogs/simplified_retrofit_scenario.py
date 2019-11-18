# -*- coding: utf-8 -*-
"""
   Multimap retrofit dialog  
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
from dialogs.message_box import showErrordialog

FONT_PIXEL_SIZE=12

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'simplified_retrofit_scenario_dialog .ui'))


class SimplifiedRetroFitDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Multimap  Retrofit Scenarios Dialog 
     
        Mapping Dialog for match multiple selected rows with one option   
    """  
    
    def __init__(self, planHeatDMM):
        """ Dialog Constructor"""
        
        super(SimplifiedRetroFitDialog, self).__init__(None)
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
            self.setFixedSize(270,200)
            
            self.planHeatDMM = planHeatDMM
            
            if self.planHeatDMM.data.refurbishmentSimplifiedData:
                self.heatDemandReductionSpinBox.setValue(self.planHeatDMM.data.refurbishmentSimplifiedData)
             
            
            year = int(datetime.datetime.now().strftime('%Y'))

            if self.planHeatDMM.data.futureScenarioYear > 0:
                year = self.planHeatDMM.data.futureScenarioYear
                
            self.futureScenarioYearSpinBox.setValue(year)
                
            self.setSystemDependantFontSize()
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","SimplifiedRetroFitDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"SimplifiedRetroFitDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
    
    
        
    def accept(self, *args, **kwargs):
        try:
        
            self.planHeatDMM.data.refurbishmentSimplifiedData   = self.heatDemandReductionSpinBox.value()
            self.planHeatDMM.data.futureScenarioYear = int(self.futureScenarioYearSpinBox.value())
            
            return QtWidgets.QDialog.accept(self, *args, **kwargs)
        
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","SimplifiedRetroFitDialog - accept Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"SimplifiedRetroFitDialog - accept Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                 
        
    
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)     