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
from PyQt5.QtCore import Qt
from PyQt5 import QtCore,QtWidgets,QtGui
from PyQt5.Qt import  QTableWidgetItem, QEvent,QWidget, QFrame
from dialogs.message_box import showErrordialog, showQuestiondialog
from model.user_field_shape_map import UserFieldShapeMap 


FONT_PIXEL_SIZE=12

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'user_field_shape_dialog.ui'))


class UserFieldShapeDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Building use Mapping Dialog 
     
        Mapping Dialog for match municipality building use with  use of plugin   
        
        Refresh all records: Delete all changed not saved and back to the last saved point
        
        Delete record: Delete the selected record, equivalent to select a None Value
        
        Delete All records: Delete all records, equivalent to choice a None Value for all records   
    """  
    
    def __init__(self, planHeatDMM,shpDMMFieldsMapTemp):
        """ Dialog Constructor"""
        
        super(UserFieldShapeDialog, self).__init__(None)
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
            self.shpDMMFieldsMapTemp = shpDMMFieldsMapTemp
            
            self.shapeFieldTable.cellClicked.connect(self.clickCell)
            self.shapeFieldTable.verticalHeader().sectionClicked.connect(self.clickRow)
            self.shapeFieldTable.horizontalHeader().sectionClicked.connect(self.clickAllRows)
            self.shapeFieldTable.installEventFilter(self)
            
            self.setHeaders()
             
            self.addRecordsTable()
            
            self.setSystemDependantFontSize()
           
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
        
        
        
    def setHeaders(self):
        """ Set Headers to table widget"""
        
        self.shapeFieldTable.setColumnCount(2)
        horHeaders = [ "Add Field", "Shape Field Name "]
        self.shapeFieldTable.setHorizontalHeaderLabels(horHeaders)
        self.shapeFieldTable.setRowCount(0)
        self.shapeFieldTable.setColumnWidth(0,80)
        self.shapeFieldTable.setColumnWidth(1,300)
        
        self.shapeFieldTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.shapeFieldTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        
    
    def addRecordsTable(self):
        """ Add Records to the Table Widget"""
        try:
            
            for x, fieldName in enumerate([shapeField[0] for shapeField in self.planHeatDMM.data.originShapeFields]):
                
                addUserFieldCheckBox = QtWidgets.QCheckBox()
                addUserFieldCheckBox.setChecked(False)
                addUserFieldCheckBox.setObjectName(str(x))
    
                cell_widget = QWidget()
                
                lay_out = QtWidgets.QHBoxLayout(cell_widget)
                lay_out.addWidget(addUserFieldCheckBox)
                lay_out.setAlignment(Qt.AlignCenter)
                lay_out.setContentsMargins(0,0,0,0)
                cell_widget.setLayout(lay_out)
        
                #cell_widget.mousePressEvent=self.presiona
                for data in self.planHeatDMM.data.userFieldShapeMap:
                    if data.key == fieldName:
                        addUserFieldCheckBox.setChecked(True)
                         
                rowPosition = self.shapeFieldTable.rowCount()
                self.shapeFieldTable.insertRow(rowPosition)
                self.shapeFieldTable.setCellWidget(rowPosition,0,cell_widget)
                self.shapeFieldTable.setItem(rowPosition , 1, QTableWidgetItem(fieldName))
                
                for data in self.shpDMMFieldsMapTemp:
                    if fieldName == data.user_definition_field and data.calculateModel in (self.planHeatDMM.data.calculateMethod,"Both"):
                        self.shapeFieldTable.item(rowPosition,1).setForeground(QtGui.QColor(0,0,240))
    
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - addRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - addRecordTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
          
            
        
    
    def accept(self, *args, **kwargs):
        
        """ Save mapping data, from widget to list"""
        
        try:
            self.planHeatDMM.data.userFieldShapeMap = []
            boolChecked = False
                 
            for x in range(0,self.shapeFieldTable.rowCount(),1):
                data = UserFieldShapeMap()
                
                for y in range(0,self.shapeFieldTable.columnCount(),1):
                    
                    if y == 0:
                        cell = self.shapeFieldTable.cellWidget(x,y)
                        check = cell.children()
                        # Get the checkbox not the object layout [0] 
                        boolChecked = check[1].isChecked()
                       
                    elif y == 1:
                        item = self.shapeFieldTable.item(x,y)
                        data.key = ""  if item is None else item.text()
                        
                            
                if boolChecked:
                    for shapeField in  self.planHeatDMM.data.originShapeFields:
                        if shapeField[0] == data.key:  
                            data.dataFormat = shapeField[1]  
                            data.length     = shapeField[2]
                            data.precision  = shapeField[3]
                            data.position   = x
                            break
                    
                    self.planHeatDMM.data.userFieldShapeMap.append(data)        
            
                 
            return QtWidgets.QDialog.accept(self, *args, **kwargs)     
        
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - accept Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - accept Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
            
    
    
    def clickCell(self,rowNum,columnNum):
        try:
            cell = self.shapeFieldTable.cellWidget(rowNum,0)
            check = cell.children()[1]
            check.toggle()
            # Get the checkbox not the object layout [0] 
            
           
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - clickCell Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - clickCell Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
            
    
    
    def clickRow(self,rowNum):
        try:    
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - clickRow Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - clickRow Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
            
    def selectedRows(self):
        try:
            modelIndex = self.shapeFieldTable.selectionModel().selectedRows()

            for index in modelIndex:
                cell = self.shapeFieldTable.cellWidget(index.row(),0)
                check = cell.children()[1]
                check.toggle()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - selectedRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - selectedRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
    
    
    def clickAllRows(self):
        try:
            
            self.shapeFieldTable.selectAll()
            self.selectedRows()
                
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - clickAllRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - clickAllRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
            
  
        
    def eventFilter(self, widget, event):
        """ Manage lost focus event on QTablewidget, avoiding deselect rows """
        try:
            if event.type() == QEvent.FocusOut:return True     
            return QtWidgets.QDialog.eventFilter(self, widget, event)    
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","UserFieldShapeDialog - eventFilter Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"UserFieldShapeDialog - eventFilter Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
        
        
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font) 