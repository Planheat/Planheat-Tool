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
    os.path.dirname(__file__), 'retrofit_multi_copy_tab_dialog.ui'))


class RetroFitMultiCopyTabDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Retrofit Copy Tab Dialog 
     
        Copy selected tab data to the others tabs   
    """  
    
    def __init__(self, planHeatDMM,selectOptions):
        """ Dialog Constructor"""
        
        super(RetroFitMultiCopyTabDialog, self).__init__(None)
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
            self.setFixedSize(250,300)
            
            self.planHeatDMM = planHeatDMM
            self.__log = self.planHeatDMM.resources.log 
            
            self.planHeatDMM.data.listSelectedValues = []
            
            for item in selectOptions:
                self.listWidget.addItem(item)
                
            #self.listWidget.setCurrentRow(0)   
            
            self.selectAllCheckBox.stateChanged.connect(self.selectDeselectAll)
            self.setSystemDependantFontSize() 
                
            
        except:
            self.__log.write_log("ERROR","RetroFitMultiCopyTabDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetroFitMultiCopyTabDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
    
    
    def selectDeselectAll(self):
        try:
            if  self.selectAllCheckBox.isChecked():
                self.listWidget.selectAll()
                self.listWidget.setEnabled(False)
            
            else:
                self.listWidget.clearSelection()
                self.listWidget.setEnabled(True)
        except:
            self.__log.write_log("ERROR","RetroFitMultiCopyTabDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetroFitMultiCopyTabDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise  
        
               
        
    def accept(self, *args, **kwargs):
       
        for index in self.listWidget.selectedIndexes():
            self.planHeatDMM.data.listSelectedValues.append(str(index.data()))
        
        
        return QtWidgets.QDialog.accept(self, *args, **kwargs)
    
        
        
    
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font) 