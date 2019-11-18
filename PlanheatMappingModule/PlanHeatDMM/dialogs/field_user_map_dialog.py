# -*- coding: utf-8 -*-
"""
   Matching user fields dialog  
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 09 Oct. 2017
"""

__docformat__ = "restructuredtext"  

import os,sys


from PyQt5 import uic
  
from PyQt5 import QtCore,QtWidgets, QtGui
from PyQt5.Qt import  QTableWidgetItem, QEvent,QGuiApplication

from dialogs.message_box import showErrordialog, showQuestiondialog
from dialogs.user_field_shape_dialog import UserFieldShapeDialog
from model.shp_map_csv_input_fields import ShpCsvInputFields
from model.user_field_shape_map import UserFieldShapeMap 

FONT_PIXEL_SIZE=12    

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'field_user_map_dialog.ui'))


class FieldUserMapDialog(QtWidgets.QDialog, FORM_CLASS):
    
    """ Shape Fields Mapping Dialog 
     
        Mapping Dialog for match municipality shape fields, with process fields of plugin  
        
        Refresh all records: Delete all changed not saved and back to the last saved point
        
        Delete record: Delete the selected record, equivalent to select a None Value
        
        Delete All records: Delete all records, equivalent to choice a None Value for all records   
          
    """  
    
    def __init__(self, planHeatDMM):
        """ Dialog Constructor"""
        
        super(FieldUserMapDialog, self).__init__(None)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        try:
            
            palette = QGuiApplication.palette()
            self.brush = palette.windowText()
            
            self.shapeFormat ={'N':'Number','C':'String', 'D':'Date','L':'Boolean','F':'Float' }
            self.previousValueList = []
            self.setWindowIcon(QtGui.QIcon(planHeatDMM.plugin_dir + os.path.sep + 'resources/logo.ico'))
            #self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowMinimizeButtonHint)
            self.setWindowModality(QtCore.Qt.ApplicationModal)
            self.setFixedSize(600,380)
            
            self.planHeatDMM = planHeatDMM
            
            
            self.refreshToolButton.setIcon(planHeatDMM.resources.icon_refresh_icon)
            self.deleteToolButton.setIcon(planHeatDMM.resources.icon_del_icon)
            self.deleteAllToolButton.setIcon(planHeatDMM.resources.icon_trash_icon)
            self.addFieldsToolButton.setIcon(planHeatDMM.resources.icon_add_icon)
            
            
            self.refreshToolButton.clicked.connect(self.refreshRecordsTable)
            self.deleteToolButton.clicked.connect(self.deleteRecordTable)
            self.deleteAllToolButton.clicked.connect(self.deleteAllRecordsTable)
            self.fieldUserMapTable.horizontalHeader().sectionClicked.connect(self.clickAllRows)    
            self.userSHPFieldMapCheckBox.stateChanged.connect(self.shapeFieldCheckBoxStateChanged)
            self.addFieldsToolButton.clicked.connect(self.openShapeUserFieldDialog)
            self.addAllFieldsButton.clicked.connect(self.addAllFields)
            
            self.addFieldsToolButton.setVisible(self.planHeatDMM.data.boolAddShapeFields)  
            self.userSHPFieldMapCheckBox.setChecked(self.planHeatDMM.data.boolAddShapeFields) 
          
            
            
            self.fieldUserMapTable.installEventFilter(self)
            
            self.setSystemDependantFontSize()
            self.setHeaders()
             
            self.addRecordsTable()
            
            
           
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - Constructor Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - Constructor Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            raise    
        
        
        
    def setHeaders(self):
        """ Set Headers to table widget"""
          
        self.fieldUserMapTable.setColumnCount(3)
        horHeaders = ["PlanHeat Column Header     ","Cadaster Column Header    ", " Field State      " ]
        self.fieldUserMapTable.setHorizontalHeaderLabels(horHeaders)
        self.fieldUserMapTable.setRowCount(0)
        self.fieldUserMapTable.resizeColumnsToContents()
        self.fieldUserMapTable.resizeRowsToContents()
        self.fieldUserMapTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.fieldUserMapTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
    
         
        
    def addRecordsTable(self):
        """ Add Records to the Table Widget"""
        
        try:
            self.previousValueList = ["None"]* len(self.planHeatDMM.data.shp_map_csv_fields) 
            for data in self.planHeatDMM.data.shp_map_csv_fields:
                if data.calculateModel in (self.planHeatDMM.data.calculateMethod,"Both"):
                      
                    self.combo = QtWidgets.QComboBox()
                    
                    
                    self.combo.addItem(str("None"))
                    for shapeField in self.planHeatDMM.data.originShapeFields:
                        self.combo.addItem(str(shapeField[0]))
                    
                    if data.user_format_match == True:
                        self.combo.currentTextChanged.connect(self.checkFieldDataFormat)
                    
                          
                    rowPosition = self.fieldUserMapTable.rowCount()
                    self.fieldUserMapTable.insertRow(rowPosition)
                    
                    self.combo.setObjectName(str(rowPosition))
                    self.combo.currentTextChanged.connect(self.checkHeightMandatoryField)   
                    
                    self.fieldUserMapTable.setItem(rowPosition , 0, QTableWidgetItem(data.fieldName))
                    self.fieldUserMapTable.setCellWidget(rowPosition,1,self.combo)
                    self.fieldUserMapTable.setItem(rowPosition , 2, QTableWidgetItem(data.fieldState))
                    
                    l = [x for x in self.planHeatDMM.data.shpDMMFieldsMap if x.fieldName == data.fieldName and x.user_definition_field.lower not in ("","none")] 
                    if l:
                        self.combo.setCurrentText(l[0].user_definition_field)
                        self.previousValueList[rowPosition]=l[0].user_definition_field
                        
                    
                    if data.fieldState.lower() in ('mandatory'): 
                        self.fieldUserMapTable.item(rowPosition,2).setForeground(QtGui.QColor(255,0,0))
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - addRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - addRecordTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
           
            
    def deleteRecordTable(self):
        """ Reset selected record from widget"""
        try:
    
            
            modelIndex = self.fieldUserMapTable.selectionModel().selectedRows()
            self.multiChange = [index.row() for index in modelIndex]
            for rowPosition in self.multiChange:
                combo = self.fieldUserMapTable.cellWidget(rowPosition,1)
                combo.setCurrentText("None")
                            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - deleteRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - deleteRecordTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
            
    def deleteAllRecordsTable(self):
        """ Reset All records from widget
        
        """
        try:
            records = self.fieldUserMapTable.rowCount()
            if records > 0 :
                message = "{} rows reset, are you sure?".format(records)
                if showQuestiondialog(self,"Reset All Records",message) == QtWidgets.QMessageBox.Yes:
                    for rowPosition in range(self.fieldUserMapTable.rowCount()):
                        combo = self.fieldUserMapTable.cellWidget(rowPosition,1)
                        combo.setCurrentText("None")
                    #while (self.fieldUserMapTable.rowCount() > 0):
                        #self.fieldUserMapTable.removeRow(0)
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - deleteAllRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - deleteAllRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
    
    def refreshRecordsTable(self):
        """ Refresh all records from the last saving operation , or initial state """
        try:
                message = "Discard, not saved changes, are you sure?"
                if showQuestiondialog(self,"Discard Changes",message) == QtWidgets.QMessageBox.Yes:
                    #self.deleteAllRecordsTable(showMessageDialog=False)
                    while (self.fieldUserMapTable.rowCount() > 0):
                        self.fieldUserMapTable.removeRow(0)
                    self.addRecordsTable()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - refreshRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - refreshRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
            
    
    
    def clickAllRows(self):
        try:
            
            self.fieldUserMapTable.selectAll()
                            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - clickAllRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - clickAllRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
     
            
    
    
    
    def accept(self, *args, **kwargs):
        """ Save mapping data, from widget to list"""
        try:
            self.planHeatDMM.data.shpDMMFieldsMap = []
            
            self.planHeatDMM.data.shpDMMFieldsMap = self.retrieveDataCSVInputFieldData()     
            shpDMMFieldsMapList = self.retrieveDataCSVInputFieldData(True)
            
            # UPDATE Mandatory Fields
            for shpDMMFieldsMap in shpDMMFieldsMapList:   
                for shp_map_csv_field in self.planHeatDMM.data.shp_map_csv_fields:
                    if shpDMMFieldsMap.fieldName == shp_map_csv_field.fieldName:
                        shp_map_csv_field.fieldState = shpDMMFieldsMap.fieldState                  
                
            return QtWidgets.QDialog.accept(self, *args, **kwargs)     
        
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - accept Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - accept Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                


    def retrieveDataCSVInputFieldData(self, complete=False):
        try:
            
            dataList = []
            for x in range(0,self.fieldUserMapTable.rowCount(),1):
                    data = ShpCsvInputFields()
                    
                    for y in range(0,self.fieldUserMapTable.columnCount(),1):
                     
                        if y == 0:
                            item = self.fieldUserMapTable.item(x,y)
                            data.fieldName = ""  if item is None else item.text()
                        elif y == 1:
                            cell = self.fieldUserMapTable.cellWidget(x,y)
                            data.user_definition_field = ""  if cell is None else cell.currentText()
                            
                        elif y == 2:
                            item = self.fieldUserMapTable.item(x,y)
                            data.fieldState = ""  if item is None else item.text()
                            
                    for csv_field in  self.planHeatDMM.data.shp_map_csv_fields:
                        if csv_field.fieldName == data.fieldName:  
                            data.calculateModel = csv_field.calculateModel  
                            break
                            
                       
                    if data.user_definition_field.lower() != 'none' or complete is True:       
                        dataList.append(data)
                        
            return dataList                    

        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - retrieveDataCSVInputFieldData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - retrieveDataCSVInputFieldData Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
                 


    def checkFieldDataFormat(self,text):
        """ Control of the data format between the field defined by the end user and the needs for the application process """
        
        try:
            DMM_definition_field = None
            shapeField = None
            cell = None
            previousValue = "None"
            
            if text.lower() not in ('none'): 
                dataList = [shapeField for shapeField in self.planHeatDMM.data.originShapeFields if str(shapeField[0]) == text]
                if dataList: shapeField = dataList[0] 
                
                #Select row table position for type control field
                rowPosition = int(self.sender().objectName())
                item = self.fieldUserMapTable.item(rowPosition,0)
                DMM_definition_field_text = "" if item is None else item.text()
                cell = self.fieldUserMapTable.cellWidget(rowPosition,1)
                previousValue=self.previousValueList[rowPosition]
                dataList = [data for data in self.planHeatDMM.data.shp_map_csv_fields if data.fieldName ==  DMM_definition_field_text ]   
                if dataList: DMM_definition_field = dataList[0]
             
                    
                if  DMM_definition_field and shapeField:
                    if  DMM_definition_field.format ==  'F':DMM_definition_field.format = 'N'
                    if  shapeField[1] ==  'F':shapeField[1] = 'N'
                    if  DMM_definition_field.format !=  shapeField[1]:
                        showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - checkFieldDataFormat:", "Cadaster Column type:{} is not compatible with PlanHeat definition format required for application:{}".format(self.shapeFormat[shapeField[1]],self.shapeFormat[DMM_definition_field.format]))
                        cell.setCurrentText(previousValue)
                    else:
                        self.previousValueList[rowPosition] = text
                else:
                    self.previousValueList[rowPosition] = text        
                        
                
                 
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - checkFieldDataFormat Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - checkFieldDataFormat Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
 
 
    def checkHeightMandatoryField(self,text):
        try:
            
            shpDMMFieldsMapTemp = self.retrieveDataCSVInputFieldData(complete=True)
         
            #Select row table position for type control field
            rowPosition = int(self.sender().objectName())
            item = self.fieldUserMapTable.item(rowPosition,0)
            
            if not item:return
            
            if  self.planHeatDMM.dlg.lidarCheckBox.isChecked():
                self.changeFieldState("numberoffloors","Optional",self.findFieldPosition("numberoffloors",shpDMMFieldsMapTemp))
                self.changeFieldState("totalheight","Optional",self.findFieldPosition("totalheight",shpDMMFieldsMapTemp))
         
            else:
                if item.text().lower() == "totalheight" and text.lower() not in ("none",""):
                    self.changeFieldState("numberoffloors","Optional",self.findFieldPosition("numberoffloors",shpDMMFieldsMapTemp))
                    self.changeFieldState("totalheight","Mandatory",rowPosition)
                    
                    
                elif item.text().lower() == "totalheight" and text.lower() in ("none",""):
                    self.changeFieldState("totalheight","Mandatory",rowPosition)
                    
                    for position , fieldMap in enumerate(shpDMMFieldsMapTemp):
                        if fieldMap.fieldName.lower() == "numberoffloors" and fieldMap.user_definition_field.lower() not in ("none",""):   
                            self.changeFieldState("totalheight","Optional",rowPosition)
                            self.changeFieldState("numberoffloors","Mandatory",position)
                            break
                        elif fieldMap.fieldName.lower() == "numberoffloors" and fieldMap.user_definition_field.lower() in ("none",""):
                            self.changeFieldState("numberoffloors","Optional",position)
                            break
                            
                elif item.text().lower() == "numberoffloors" and text.lower() not in ("none",""):
                    self.changeFieldState("numberoffloors","Mandatory",rowPosition)
                    
                    for position , fieldMap in enumerate(shpDMMFieldsMapTemp):
                        if fieldMap.fieldName.lower() == "totalheight" and fieldMap.user_definition_field.lower() not in ("none",""):   
                            self.changeFieldState("numberoffloors","Optional",rowPosition)
                            self.changeFieldState("totalheight","Mandatory",position)
                            break
                        elif fieldMap.fieldName.lower() == "totalheight" and fieldMap.user_definition_field.lower() in ("none",""):
                            self.changeFieldState("totalheight","Optional",position)
                            break
                elif item.text().lower() == "numberoffloors" and text.lower() in ("none",""):
                    self.changeFieldState("numberoffloors","Optional",rowPosition)
                    for position , fieldMap in enumerate(shpDMMFieldsMapTemp):
                        if fieldMap.fieldName.lower() == "totalheight":    
                            self.changeFieldState("totalheight","Mandatory",position)
                            break
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - checkHeightMandatoryfield Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - checkHeightMandatoryfield Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
 
 
 
 
    def changeFieldState(self,fieldName, state,position):
        try:
            if position != -1:
                if state.lower() == "mandatory":
                    self.fieldUserMapTable.item(position,2).setText(state)
                    #self.fieldUserMapTable.setItem(position , 2, QTableWidgetItem(state))
                    self.fieldUserMapTable.item(position,2).setForeground(QtGui.QColor(255,0,0))
                else:
                    #self.fieldUserMapTable.setItem(position , 2, QTableWidgetItem(state))
                    self.fieldUserMapTable.item(position,2).setText(state)
                    self.fieldUserMapTable.item(position,2).setForeground(self.brush)
                    #self.fieldUserMapTable.item(position,2).setForeground(QtGui.QColor(0,0,0))
    
                self.fieldUserMapTable.setUpdatesEnabled(True)    
                self.fieldUserMapTable.repaint()       
                self.fieldUserMapTable.update()              
                    
            
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - changeFieldState Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - changeFieldState Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
    
    
    def findFieldPosition(self,fieldName,shpDMMFieldsMapList):
        try:
            position = -1
            for rowPosition, field in enumerate(shpDMMFieldsMapList):
                if field.fieldName.lower() == fieldName.lower():
                    position = rowPosition
                    break
                
            return position
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - findFieldPosition Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - findFieldPosition Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
    

    
    def shapeFieldCheckBoxStateChanged(self,state):
        try:
            
            self.planHeatDMM.data.boolAddShapeFields = bool(state)
            if state:
                self.addFieldsToolButton.setVisible(True)
            else:
                self.addFieldsToolButton.setVisible(False)    
 
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - shapeFieldCheckBoxStateChanged Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - shapeFieldCheckBoxStateChanged Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
 
    
    def openShapeUserFieldDialog(self):
        
        try:
            
            shpDMMFieldsMapTemp = self.retrieveDataCSVInputFieldData()
            dialog = UserFieldShapeDialog(self.planHeatDMM,shpDMMFieldsMapTemp)   
       
            dialog.show()
            dialog.exec_()
        
                
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","FieldUserMapDialog - openShapeUserFieldDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"FieldUserMapDialog - openShapeUserFieldDialog Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                
 
    @staticmethod
    def addAllFieldsStatic(planHeatDMM):
        planHeatDMM.data.userFieldShapeMap = []
        origin_fields = [data[0] for data in planHeatDMM.data.originShapeFields]
        outputsFields = planHeatDMM.resources.database.retrieveOutputFields("Baseline", "Detail", "Shp","Alternative")
        outputsFieldsName = [data.headerName for data in outputsFields]
        for shapeField in planHeatDMM.data.originShapeFields:
            if shapeField[0] not in outputsFieldsName:
                data = UserFieldShapeMap()
                data.key        = shapeField[0]
                data.dataFormat = shapeField[1]
                data.length     = shapeField[2]
                data.precision  = shapeField[3]
                data.position   = origin_fields.index(data.key)
                planHeatDMM.data.userFieldShapeMap.append(data)

        planHeatDMM.data.boolAddShapeFields = True

    def addAllFields(self):
        self.addAllFieldsStatic(self.planHeatDMM)
 
 
    def eventFilter(self, widget, event):
        """ Manage lost focus event on QTablewidget, avoiding deselect rows """
        if event.type() == QEvent.FocusOut:return True     
        return QtWidgets.QDialog.eventFilter(self, widget, event)  
    
    
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)         