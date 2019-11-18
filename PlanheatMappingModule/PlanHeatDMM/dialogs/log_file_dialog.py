# -*- coding: utf-8 -*-
"""
   Matching user fields dialog  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 19 Oct. 2017
"""

__docformat__ = "restructuredtext"  

import os
import sys
from PyQt5 import uic
from PyQt5 import QtCore,QtWidgets, QtGui
from dialogs.message_box import showErrordialog

FONT_PIXEL_SIZE=12    

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'log_file_dialog.ui'))


class LogFileDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Show Log file Dialog """  
    
    def __init__(self, planHeatDMM):
        """Constructor Dialog"""
        
        super(LogFileDialog, self).__init__(None)
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
            self.setFixedSize(800,500)
            
            self.planHeatDMM = planHeatDMM
            
            self.setSystemDependantFontSize()
            self.showLogFile()
            
            
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","LogFileDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"LogFileDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
        
        
    @QtCore.pyqtSlot()    
    def showLogFile(self):
        """ Load log file to the widget """  
        try:
        
            file = QtCore.QFile(self.planHeatDMM.resources.log.completeFileName)
            if not file.open(QtCore.QIODevice.ReadOnly):
                showErrordialog(self.planHeatDMM.dlg,"LogFileDialog", file.errorString())
            else:
                stream = QtCore.QTextStream(file)
                self.logTextEdit.setText(stream.readAll())
                
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","showLogFile - addRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"LogFileDialog - showLogFile Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))


    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)         