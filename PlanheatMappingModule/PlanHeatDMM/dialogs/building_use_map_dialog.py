# -*- coding: utf-8 -*-
"""
   Matching building use dialog  
   :author: Sergio Aparicio Vegas
   :version: 0.1  
   :date: 09 Oct. 2017
"""

__docformat__ = "restructuredtext"  

import os,sys


from PyQt5 import uic
from PyQt5 import QtCore,QtWidgets
from PyQt5 import QtGui
from PyQt5.Qt import  QTableWidgetItem, QEvent
from dialogs.multi_map_dialog import MultiMapDialog
from dialogs.message_box import showErrordialog, showQuestiondialog
from model.building_use_map import BuildingUseMap

FONT_PIXEL_SIZE=12

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'building_use_map_dialog.ui'))


class BuildingUseMapDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Building use Mapping Dialog 
     
        Mapping Dialog for match municipality building use with  use of plugin   
        
        Refresh all records: Delete all changed not saved and back to the last saved point
        
        Delete record: Delete the selected record, equivalent to select a None Value
        
        Delete All records: Delete all records, equivalent to choice a None Value for all records   
    """  
    
    def __init__(self, planHeatDMM):
        """ Dialog Constructor"""
        
        super(BuildingUseMapDialog, self).__init__(None)
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
            self.buildUseMapTable.cellClicked.connect(self.clickCell)
            self.buildUseMapTable.pressed.connect(self.pressedCell)
            self.buildUseMapTable.verticalHeader().sectionClicked.connect(self.clickRow)
            self.buildUseMapTable.horizontalHeader().sectionClicked.connect(self.clickAllRows)
            
            self.buildUseMapTable.installEventFilter(self)
            
            self.setSystemDependantFontSize()
            
            self.setHeaders()
             
            self.addRecordsTable()
           
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
        
        
        
    def setHeaders(self):
        """ Set Headers to table widget"""
        
        self.buildUseMapTable.setColumnCount(2)
        horHeaders = ["Cadaster Use                ", "PlanHeat Use                    "]
        self.buildUseMapTable.setHorizontalHeaderLabels(horHeaders)
        self.buildUseMapTable.setRowCount(0)
        self.buildUseMapTable.resizeColumnsToContents()
        self.buildUseMapTable.resizeRowsToContents()
        self.buildUseMapTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.buildUseMapTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        
    
    def addRecordsTable(self):
        """ Add Records to the Table Widget"""
        
        try:
            
            for user_use in self.planHeatDMM.data.inputSHPFieldBuildingUseValues:
                self.combo = QtWidgets.QComboBox(self)
                self.combo.setMouseTracking(False)
                self.combo.setObjectName("userFieldCombo")
                for data in self.planHeatDMM.data.buildingUse:
                    self.combo.addItem(data.use)
                
                
                l = [x for x in self.planHeatDMM.data.buildingUseMap if x.user_definition_use == user_use and x.DMM_use not in ("","Not evaluate")] 
                if l:
                    self.combo.setCurrentText(l[0].DMM_use)
                
                
                rowPosition = self.buildUseMapTable.rowCount()
                self.buildUseMapTable.insertRow(rowPosition)     
                self.buildUseMapTable.setItem(rowPosition , 0, QTableWidgetItem(user_use))
                self.buildUseMapTable.setCellWidget(rowPosition,1,self.combo)
                     
    

            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - addRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - addRecordTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
          
            
    def deleteRecordTable(self):
        """ Reset selected record from widget"""
        
        try:
            """
            index = self.buildUseMapTable.selectionModel().selectedRows()
            for i in sorted(index,reverse=True): 
                self.buildUseMapTable.removeRow(i.row())
            """    
            modelIndex = self.buildUseMapTable.selectionModel().selectedRows()
            self.multiChange = [index.row() for index in modelIndex]
            for rowPosition in self.multiChange:
                combo = self.buildUseMapTable.cellWidget(rowPosition,1)
                combo.setCurrentText("Not evaluate")            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - deleteRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - deleteRecordTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
            
    def deleteAllRecordsTable(self):
        """ Reset All records from widget
        """
        try:
            records = self.buildUseMapTable.rowCount()
            if records > 0 :
                message = "{} rows reset, are you sure?".format(records)
                if showQuestiondialog(self,"Reset All Records",message) == QtWidgets.QMessageBox.Yes:
                    for rowPosition in range(self.buildUseMapTable.rowCount()):
                        combo = self.buildUseMapTable.cellWidget(rowPosition,1)
                        combo.setCurrentText("Not evaluate")
                    #while (self.buildUseMapTable.rowCount() > 0):
                        #self.buildUseMapTable.removeRow(0)
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - deleteAllRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - deleteAllRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
    def refreshRecordsTable(self):
        """ Refresh all records from the last saving operation , or initial state """
        
        try:
                message = "Discard, not saved changes, are you sure?"
                if showQuestiondialog(self,"Discard Changes",message) == QtWidgets.QMessageBox.Yes:
                    #self.deleteAllRecordsTable(showMessageDialog=False)
                    while (self.buildUseMapTable.rowCount() > 0):
                        self.buildUseMapTable.removeRow(0)
                    self.addRecordsTable()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - refreshRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - refreshRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
    
    def accept(self, *args, **kwargs):
        
        """ Save mapping data, from widget to list"""
        
        try:
            self.planHeatDMM.data.buildingUseMap = []
                 
            for x in range(0,self.buildUseMapTable.rowCount(),1):
                data = BuildingUseMap()
                
                for y in range(0,self.buildUseMapTable.columnCount(),1):
                    
                    if y == 0:
                        item = self.buildUseMapTable.item(x,y)
                        data.user_definition_use = ""  if item is None else item.text()
                       
                    elif y == 1:
                        cell = self.buildUseMapTable.cellWidget(x,y)
                        data.DMM_use = ""  if cell is None else cell.currentText()
                        for building_use in  self.planHeatDMM.data.buildingUse:
                            if building_use.use == data.DMM_use:  
                                data.building_use_id = building_use.id  
                                data.non_office      = building_use.non_office
                                data.floor_height    = building_use.floor_height
                                #print(str(data))
                                break
                    
                self.planHeatDMM.data.buildingUseMap.append(data)        
            
                
            return QtWidgets.QDialog.accept(self, *args, **kwargs)     
        
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - accept Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - accept Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
            
    
    
    def clickCell(self,rowNum,columnNum):
        try:
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - clickCell Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - clickCell Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
            
    
    
    def pressedCell(self):
        try:
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - pressedCell Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - pressedCell Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))       
            
            
    def clickRow(self,rowNum):
        try:    
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - clickRow Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - clickRow Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
            
    def selectedRows(self):
        try:
            modelIndex = self.buildUseMapTable.selectionModel().selectedRows()
            if modelIndex:
                self.multiMapToolButton.setEnabled(True)
                
            else:
                self.multiMapToolButton.setEnabled(False)    
                self.multiChange = []    
                
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - selectedRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - selectedRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
    
    
    def clickAllRows(self):
        try:
            
            self.buildUseMapTable.selectAll()
            self.selectedRows()
                
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - clickAllRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - clickAllRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
            
    @QtCore.pyqtSlot()            
    def multiMapDialog(self):     
        try:
            
            modelIndex = self.buildUseMapTable.selectionModel().selectedRows();
            self.multiChange = [index.row() for index in modelIndex]
            
            uses = [building.use for building in self.planHeatDMM.data.buildingUse]
            dialog = MultiMapDialog(self.planHeatDMM,uses)   
       
            dialog.show()
            dialogResult = dialog.exec_()
            
            if dialogResult == QtWidgets.QDialog.Accepted:
                for rowPosition in self.multiChange:
                    combo = self.buildUseMapTable.cellWidget(rowPosition,1)
                    combo.setCurrentText(self.planHeatDMM.data.listSelectedValue)
                   
            
            self.planHeatDMM.data.listSelectedValue = None   
           
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - multiMapDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - multiMapDialog Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
        
        
        
    def eventFilter(self, widget, event):
        """ Manage lost focus event on QTablewidget, avoiding deselect rows """
        try:
            if event.type() == QEvent.FocusOut:return True     
            return QtWidgets.QDialog.eventFilter(self, widget, event)    
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - eventFilter Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - eventFilter Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
        
        
    def resizeEvent(self, event):
        try:
            #print(event.size().width())
            self.buildUseMapTable.setGeometry(55,20,event.size().width()-70,240)
            #self.buildUseMapTable.resizeColumnsToContents()
            return QtWidgets.QDialog.resizeEvent(self,event)
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - resizeEvent Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - resizeEvent Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
        
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)     