# -*- coding: utf-8 -*-
"""
   Multimap retrofit dialog  
   :author: Sergio Aparicio Vegas
   :version: 0.1  
   :date: 09 Oct. 2017
"""

__docformat__ = "restructuredtext"  

import os,sys


from PyQt5 import uic
  
from PyQt5 import QtCore,QtWidgets, QtGui
from dialogs.message_box import showErrordialog

FONT_PIXEL_SIZE=12

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'retrofit_multi_map_dialog.ui'))


class RetroFitMultiMapDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Multimap  Retrofit Scenarios Dialog 
     
        Mapping Dialog for match multiple selected rows with one option   
    """  
    
    def __init__(self, planHeatDMM,selectOptions):
        """ Dialog Constructor"""
        
        super(RetroFitMultiMapDialog, self).__init__(None)
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
            self.setFixedSize(250,350)
            
            self.planHeatDMM = planHeatDMM
            
            for item in selectOptions:
                self.listWidget.addItem(item)
                
            self.listWidget.setCurrentRow(0)   
            self.setSystemDependantFontSize() 
                
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","RetroFitMultiMapDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetroFitMultiMapDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                
    
    
        
    def accept(self, *args, **kwargs):
        
        try:
            self.planHeatDMM.data.listSelectedValue = self.listWidget.currentItem().text()
        
            self.planHeatDMM.data.roofSpinBoxSelectedValue   = self.roofSpinBox.value() 
            self.planHeatDMM.data.wallSpinBoxSelectedValue   = self.wallSpinBox.value()
            self.planHeatDMM.data.windowSpinBoxSelectedValue = self.windowSpinBox.value()
        
            return QtWidgets.QDialog.accept(self, *args, **kwargs)    
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","RetroFitMultiMapDialog - accept Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetroFitMultiMapDialog - accept Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
             
        
    
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)         