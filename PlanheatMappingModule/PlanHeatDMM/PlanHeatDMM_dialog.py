# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanHeatDMMDialog
                                 A QGIS plugin
 PlanHeatDMM
                             -------------------
        begin                : 2017-10-03
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Sergio Aparicio Vegas
        email                : sapariciovegas@gmail.com
 ***************************************************************************/
"""

import os,sys

from PyQt5 import uic
from PyQt5 import QtWidgets,QtGui  
from PyQt5 import QtCore
from PyQt5.Qt import  QEvent
from dialogs.message_box import showErrordialog   
from src.pluginControl import closeWindow, openLoadFileDialog,openSaveFileDialog, openLoadFileDialogDTM, openLoadFileDialogDSM, loadScenario, openRetrofittedScenarioDialog,openFieldUserMapDialog, openBuildingUseMapDialog, openProtectionLevelMapDialog 
from .dmm_serialization import DMMSerializer
FONT_PIXEL_SIZE=12

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanHeatDMM_dialog_base.ui'))


class PlanHeatDMMDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, planHeatDMM, parent=None):
        """Constructor."""
        super(PlanHeatDMMDialog, self).__init__(parent)
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        self.planHeatDMM = planHeatDMM
        
        
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'resources/logo.ico'))
        self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinimizeButtonHint)
        self.setFixedSize(650,680)
        
        self.loadFileToolButton.installEventFilter(self)
        self.saveFileToolButton.installEventFilter(self)
        self.DTMToolButton.installEventFilter(self)
        self.DSMToolButton.installEventFilter(self)
        self.retrofittedScenariosToolbutton.installEventFilter(self)
        self.fieldAddToolButton.installEventFilter(self)
        self.buildUseAddToolButton.installEventFilter(self)
        self.protectionAddToolButton.installEventFilter(self)
        self.loadScenario.installEventFilter(self)
       
        self.statusBar()
        self.setEnabled(False)
        self.setSystemDependantFontSize()
        
    def statusBar(self):
        try:
            self.statusMessageLabel.setEnabled(True)
            self.statusProcessButton.setVisible(False)
            self.statusProgressBar.setVisible(False)
        
        except:
            showErrordialog(self.planHeatDMM.dlg,"statusBar",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
                
        
    def closeEvent(self, event):
        
        if closeWindow(self.planHeatDMM):
            self.planHeatDMM.resources.releaseResources(self.planHeatDMM)
            event.accept() # let the window close
        else:
            event.ignore()

        # Serialize current info
        DMMSerializer.serialize(self)
            
        self.planHeatDMM.master_dlg.show()
    
    def keyPressEvent(self,event):
        try: 
            if event.key()==QtCore.Qt.Key_Return: 
                return None
            else: 
                event.accept() 
                
        except:
            showErrordialog(self.planHeatDMM.dlg,"PlanHeatDMM_dialog_base - keyPressEvent",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            

    def eventFilter(self, widget, event):
        """ Manage Event filter for keypress Enter in Toolbuttons """
        try:
            if event.type() == QEvent.KeyPress and event.key() == QtCore.Qt.Key_Return: 
                #  print(widget.objectName())
                if widget.objectName()  == "loadFileToolButton":openLoadFileDialog(self.planHeatDMM)
                elif widget.objectName()== "saveFileToolButton":openSaveFileDialog(self.planHeatDMM)
                elif widget.objectName()== "DTMToolButton":openLoadFileDialogDTM(self.planHeatDMM)
                elif widget.objectName()== "DSMToolButton":openLoadFileDialogDSM(self.planHeatDMM)
                elif widget.objectName()== "retrofittedScenariosToolbutton":openRetrofittedScenarioDialog(self.planHeatDMM)
                elif widget.objectName()== "fieldAddToolButton":openFieldUserMapDialog(self.planHeatDMM)
                elif widget.objectName()== "buildUseAddToolButton":openBuildingUseMapDialog(self.planHeatDMM)
                elif widget.objectName()== "protectionAddToolButton":openProtectionLevelMapDialog(self.planHeatDMM)
                elif widget.objectName()== "loadScenario":loadScenario(self.planHeatDMM)
            
            return QtWidgets.QDialog.eventFilter(self, widget, event)    
        except:
            showErrordialog(self.planHeatDMM.dlg,"PlanHeatDMM_dialog_base - eventFilter Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
                
    
    
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)

