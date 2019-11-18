# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PlanheatMappingPlugin_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!
import os
import sys
import csv
import locale
from PyQt5 import uic
from PyQt5 import QtWidgets
from .MappingWizard import MappingWizard
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMessageBox,QFileDialog
from PyQt5 import QtWidgets
from qgis.core import QgsMessageLog, Qgis
from .AddUsefulEnergyDlg import AddUsefulEnergySourceDlg
from .AddUsefulEnergyDlgTertiary import AddUsefulEnergySourceDlgTertiary

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PlanheatMappingPlugin_dialog_base.ui'), resource_suffix='')


class PlanHeatMappingWizardDialog(QtWidgets.QDialog, FORM_CLASS):
    closingPlugin = pyqtSignal()
   
  
    def openUsefulDlg(self):
      if (self.radioButtonResidential_Baseline.isChecked()):
        self.addUsefulDlg = AddUsefulEnergySourceDlg()
        self.addUsefulDlg.show()
      else:
        self.addUsefulDlgTertiary = AddUsefulEnergySourceDlgTertiary()
        self.addUsefulDlgTertiary.show() 
        
        
        
    def openWizard(self):
        if (self.radioButtonResidential.isChecked()):
            self.wizardResidential.show()
        else:
            self.wizardTertiary.show()      
    
    def __init__(self, working_directory=None, parent=None):
        """Constructor."""
        super(PlanHeatMappingWizardDialog, self).__init__(parent)
        self.setupUi(self)
        self.working_directory = working_directory
        self.wizardResidential = MappingWizard("Residential Sector", working_directory=self.working_directory)
        self.wizardTertiary = MappingWizard("Tertiary Sector", working_directory=self.working_directory)
        self.pushButtonOpenCSV_Existing.clicked.connect(self.openUsefulDlg)         
        self.pushButtonOpenMappingModule.clicked.connect(self.openWizard)
        self.addUsefulDlg = None
        self.addUsefulDlgTertiary = None

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

        
        