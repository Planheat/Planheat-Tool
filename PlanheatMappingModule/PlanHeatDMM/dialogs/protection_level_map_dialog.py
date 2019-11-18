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
from PyQt5.Qt import  QTableWidgetItem, QEvent
from dialogs.message_box import showErrordialog, showQuestiondialog
from dialogs.multi_map_dialog import MultiMapDialog
from model.protection_level_map import ProtectionLevelMap

FONT_PIXEL_SIZE=12

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'protection_level_map_dialog.ui'))


class ProtectionLevelMapDialog(QtWidgets.QDialog, FORM_CLASS):
    
     
    """ Protection Level  Mapping Dialog 
     
        Mapping Dialog for match municipality protection degree with  protection level of plugin   
    
        Refresh all records: Delete all changed not saved and back to the last saved point
        
        Delete record: Delete the selected record, equivalent to select a None Value
        
        Delete All records: Delete all records, equivalent to choice a None Value for all records   
          
    """  
    
    def __init__(self, planHeatDMM):
        """Dialog Constructor """
        
        
        super(ProtectionLevelMapDialog, self).__init__(None)
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
            #self.setFixedSize(600,350)
            
            self.planHeatDMM = planHeatDMM
            
            self.multiChange=[]
           
            
            self.refreshToolButton.setIcon(planHeatDMM.resources.icon_refresh_icon)
            self.deleteToolButton.setIcon(planHeatDMM.resources.icon_del_icon)
            self.deleteAllToolButton.setIcon(planHeatDMM.resources.icon_trash_icon)
            self.multiMapToolButton.setIcon(planHeatDMM.resources.icon_multi_map_icon)
            
            self.refreshToolButton.clicked.connect(self.refreshRecordsTable)
            self.deleteToolButton.clicked.connect(self.deleteRecordTable)
            self.deleteAllToolButton.clicked.connect(self.deleteAllRecordsTable)
            self.multiMapToolButton.clicked.connect(self.multiMapDialog)
            self.protectionLevelMapTable.cellClicked.connect(self.clickCell)
            self.protectionLevelMapTable.pressed.connect(self.pressedCell)
            self.protectionLevelMapTable.verticalHeader().sectionClicked.connect(self.clickRow)
            self.protectionLevelMapTable.horizontalHeader().sectionClicked.connect(self.clickAllRows)    
            
            self.protectionLevelMapTable.installEventFilter(self)
            
            self.setSystemDependantFontSize()
            self.setHeaders()
            
            self.addRecordsTable()
             
            
           
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
        
        
        
    def setHeaders(self):
        """ Set Headers to table widget"""
        self.protectionLevelMapTable.setColumnCount(2)
        horHeaders = ["Cadaster Protection Level                         ", "PlanHeat Protection Level                            "]
        self.protectionLevelMapTable.setHorizontalHeaderLabels(horHeaders)
        self.protectionLevelMapTable.setRowCount(0)
        self.protectionLevelMapTable.resizeColumnsToContents()
        self.protectionLevelMapTable.resizeRowsToContents()
        self.protectionLevelMapTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.protectionLevelMapTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
    
         
        
    def addRecordsTable(self):
        """ Add Records to the Table Widget"""
        try:
            
            for user_protection in self.planHeatDMM.data.inputSHPFieldProtectionDegreeValues: 
    
                model = QtGui.QStandardItemModel()
                
                for data in self.planHeatDMM.data.protectionLevels:
                    protection_level = QtGui.QStandardItem(str(data.protectionLevel))
                    description = QtGui.QStandardItem(data.description)
                    model.appendRow([protection_level, description])
                    
                  
                view = QtWidgets.QTreeView()
                view.setMouseTracking(False)
                view.header().hide()
                view.setRootIsDecorated(False)
                
                self.comboProtectionLevel = QtWidgets.QComboBox()
                self.comboProtectionLevel.setMouseTracking(False)
                self.comboProtectionLevel.setView(view)
                self.comboProtectionLevel.setModel(model)
                
                #self.comboProtectionLevel = QtWidgets.QComboBox()
                #for data in self.planHeatDMM.data.protectionLevels:
                #    self.comboProtectionLevel.addItem(str(data.protectionLevel))
                
                rowPosition = self.protectionLevelMapTable.rowCount()
                self.protectionLevelMapTable.insertRow(rowPosition)
                
                
                if self.planHeatDMM.data.protectionLevelMap:
                    l = [x for x in self.planHeatDMM.data.protectionLevelMap if x.user_definition_protection == user_protection and x.DMM_protection_level not in ("","Not evaluate")] 
                    if l:
                        self.comboProtectionLevel.setCurrentText(str(l[0].DMM_protection_level))
                    
        
                self.protectionLevelMapTable.setItem(rowPosition,0, QTableWidgetItem(user_protection))            
                self.protectionLevelMapTable.setCellWidget(rowPosition,1,self.comboProtectionLevel)

      
            
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - addRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - addRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
           
            
    def deleteRecordTable(self):
        """ Reset selected record from widget"""
        try:
            """
            index = self.protectionLevelMapTable.selectionModel().selectedRows()
            for i in sorted(index,reverse=True): 
                self.protectionLevelMapTable.removeRow(i.row())
            """
            modelIndex = self.protectionLevelMapTable.selectionModel().selectedRows()
            self.multiChange = [index.row() for index in modelIndex]
            for rowPosition in self.multiChange:
                combo = self.protectionLevelMapTable.cellWidget(rowPosition,1)
                combo.setCurrentText("0")
                             
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - deleteRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - deleteRecordTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
    
    def deleteAllRecordsTable(self):
        """ Reset All records from widget
        """
        try:
            records = self.protectionLevelMapTable.rowCount()
            if records > 0 :
                message = "{} rows reset, are you sure?".format(records)
                if showQuestiondialog(self,"Reset All Records",message) == QtWidgets.QMessageBox.Yes:
                    
                    for rowPosition in range(self.protectionLevelMapTable.rowCount()):
                        combo = self.protectionLevelMapTable.cellWidget(rowPosition,1)
                        combo.setCurrentText("0")
                    #while (self.protectionLevelMapTable.rowCount() > 0):
                        #self.protectionLevelMapTable.removeRow(0)
                  
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - deleteAllRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - deleteAllRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
    def refreshRecordsTable(self):
        """ Refresh all records from the last saving operation , or initial state """
        try:
                message = "Discard, not saved changes, are you sure?"
                if showQuestiondialog(self,"Discard Changes",message) == QtWidgets.QMessageBox.Yes:
                    #self.deleteAllRecordsTable(showMessageDialog=False)
                    while (self.protectionLevelMapTable.rowCount() > 0):
                        self.protectionLevelMapTable.removeRow(0)
                    self.addRecordsTable()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - refreshRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - refreshRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
                                
    
    def accept(self, *args, **kwargs):
        """ Save mapping data, from widget to list"""
        try:
            self.planHeatDMM.data.protectionLevelMap = []
                 
            for x in range(0,self.protectionLevelMapTable.rowCount(),1):
                data = ProtectionLevelMap()
                
                for y in range(0,self.protectionLevelMapTable.columnCount(),1):
                    
                    if y == 0:
                        item = self.protectionLevelMapTable.item(x,y)
                        data.user_definition_protection = ""  if item is None else item.text()
                        
                    elif y == 1:
                        cell = self.protectionLevelMapTable.cellWidget(x,y)
                        data.DMM_protection_level = 0  if cell is None else int(cell.currentText())
                         
                    
                self.planHeatDMM.data.protectionLevelMap.append(data)        
            
                
            return QtWidgets.QDialog.accept(self, *args, **kwargs)     
        
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - accept Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - accept Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                



    def clickCell(self,rowNum,columnNum):
        try:
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - clickCell Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - clickCell Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
            
    
    def pressedCell(self):
        try:
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - pressedCell Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - pressedCell Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))       
            
        
    def clickRow(self,rowNum):
        try:    
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - clickRow Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - clickRow Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
    
    
    def clickAllRows(self):
        try:
            
            self.protectionLevelMapTable.selectAll()
            self.selectedRows()
                
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - clickAllRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - clickAllRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
     
            
    def selectedRows(self):
        try:
            modelIndex = self.protectionLevelMapTable.selectionModel().selectedRows()
            if modelIndex:
                self.multiMapToolButton.setEnabled(True)
            else:
                self.multiMapToolButton.setEnabled(False)    
                self.multiChange = []    
                
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - selectedRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - selectedRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
     
            
    @QtCore.pyqtSlot()            
    def multiMapDialog(self):     
        try:
            modelIndex = self.protectionLevelMapTable.selectionModel().selectedRows();
            self.multiChange = [index.row() for index in modelIndex]
            
            levels = [str(level.protectionLevel) for level in self.planHeatDMM.data.protectionLevels]
            dialog = MultiMapDialog(self.planHeatDMM,levels)   
       
            dialog.show()
            dialogResult = dialog.exec_()
            
            if dialogResult == QtWidgets.QDialog.Accepted:
                for rowPosition in self.multiChange:
                    combo = self.protectionLevelMapTable.cellWidget(rowPosition,1)
                    combo.setCurrentText(self.planHeatDMM.data.listSelectedValue)
                   
            
            self.planHeatDMM.data.listSelectedValue = None   
           
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - multiMapDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - multiMapDialog Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))  
            
    
    def eventFilter(self, widget, event):
        """ Manage lost focus event on QTablewidget, avoiding deselect rows """
        
        try:
            if event.type() == QEvent.FocusOut:return True     
            return QtWidgets.QDialog.eventFilter(self, widget, event)
        
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - eventFilter Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - eventFilter Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
        
    
    def resizeEvent(self, event):
        try:
            #print(event.size().width())
            self.protectionLevelMapTable.setGeometry(55,20,event.size().width()-70,240)
            #self.buildUseMapTable.resizeColumnsToContents()
            return QtWidgets.QDialog.resizeEvent(self,event)
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","ProtectionLevelMapDialog - resizeEvent Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"ProtectionLevelMapDialog - resizeEvent Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
          
    
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)         