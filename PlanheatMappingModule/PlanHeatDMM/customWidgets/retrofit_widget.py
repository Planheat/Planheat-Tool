# -*- coding: utf-8 -*-
"""
   Retrofit scenarios page for tab  
   :author: Sergio Aparicio Vegas
   :version: 0.2  
   :date: 27 Nov. 2017
"""


__docformat__ = "restructuredtext"  

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import  QTableWidgetItem, QEvent
from dialogs.message_box import showErrordialog, showQuestiondialog
from dialogs.retrofit_multi_map_dialog import RetroFitMultiMapDialog
from dialogs.retrofit_multi_copy_tab_dialog import RetroFitMultiCopyTabDialog
from customWidgets.custom_widgets import QTableRetrofitWidget, QSpinBoxRetrofitWidget, QComboBoxRetrofitWidget
from model.refurbishment_tab_data import  RowRefurbishTableData


FONT_PIXEL_SIZE=12

class Ui_Form(object):
    
    def setupUi(self, Form):
        
        Form.setObjectName("Form")
        #Form.resize(530, 405)
        self.retrofitScenarioTable = QTableRetrofitWidget(Form)
        self.retrofitScenarioTable.setGeometry(QtCore.QRect(65, 15, 530, 305))
        self.retrofitScenarioTable.setObjectName("retrofitScenarioTable")
        self.retrofitScenarioTable.setColumnCount(0)
        self.retrofitScenarioTable.setRowCount(0)
        self.refreshToolButton = QtWidgets.QToolButton(Form)
        self.refreshToolButton.setGeometry(QtCore.QRect(15, 30, 36, 36))
        self.refreshToolButton.setIconSize(QtCore.QSize(24, 24))
        self.refreshToolButton.setObjectName("refreshToolButton")
        self.deleteToolButton = QtWidgets.QToolButton(Form)
        self.deleteToolButton.setGeometry(QtCore.QRect(15, 90, 36, 36))
        self.deleteToolButton.setIconSize(QtCore.QSize(24, 24))
        self.deleteToolButton.setObjectName("deleteToolButton")
        self.multiMapToolButton = QtWidgets.QToolButton(Form)
        self.multiMapToolButton.setEnabled(False)
        self.multiMapToolButton.setGeometry(QtCore.QRect(15, 150, 36, 36))
        self.multiMapToolButton.setIconSize(QtCore.QSize(24, 24))
        self.multiMapToolButton.setObjectName("multiMapToolButton")
        self.applyAllTabsToolButton = QtWidgets.QToolButton(Form)
        self.applyAllTabsToolButton.setGeometry(QtCore.QRect(15, 210, 36, 36))
        self.applyAllTabsToolButton.setIconSize(QtCore.QSize(24, 24))
        self.applyAllTabsToolButton.setObjectName("applyAllTabsToolButton")
        self.deleteAllToolButton = QtWidgets.QToolButton(Form)
        self.deleteAllToolButton.setGeometry(QtCore.QRect(15, 270, 36, 36))
        self.deleteAllToolButton.setIconSize(QtCore.QSize(24, 24))
        self.deleteAllToolButton.setObjectName("deleteAllToolButton")
        
     
        self.setSystemDependantFontSize()


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.deleteAllToolButton.setToolTip(_translate("Form", "Reset all records"))
        self.deleteAllToolButton.setText(_translate("Form", "x"))
        self.deleteToolButton.setToolTip(_translate("Form", "Reset records"))
        self.deleteToolButton.setText(_translate("Form", "-"))
        self.applyAllTabsToolButton.setToolTip(_translate("Form", "Apply this tab values to selected tabs"))
        self.applyAllTabsToolButton.setText(_translate("Form", "*"))
        self.multiMapToolButton.setToolTip(_translate("Form", "Multi map selection"))
        self.multiMapToolButton.setText(_translate("Form", "^"))
        self.refreshToolButton.setToolTip(_translate("Form", "Refresh all records"))
        self.refreshToolButton.setText(_translate("Form", "+"))


    def setHeaders(self):
        self.retrofitScenarioTable.setColumnCount(5)
        horHeaders = ["PlanHeat Period ","Refurbishment Level   ","Roof" , "Wall", "Window"]
        self.retrofitScenarioTable.setHorizontalHeaderLabels(horHeaders)
        self.retrofitScenarioTable.setRowCount(0)
        self.retrofitScenarioTable.resizeColumnToContents(0)
        self.retrofitScenarioTable.resizeColumnToContents(1)
        self.retrofitScenarioTable.setColumnWidth(2,70)
        self.retrofitScenarioTable.setColumnWidth(3,70)
        self.retrofitScenarioTable.setColumnWidth(4,70)
        self.retrofitScenarioTable.resizeRowsToContents()
        self.retrofitScenarioTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.retrofitScenarioTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        

class RetrofitScenarioWidget(QtWidgets.QWidget, Ui_Form):
    
    
    
    def __init__(self, name, planHeatDMM, tabData, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        try:
            
            self.name = name
            self.planHeatDMM    = planHeatDMM
            self.tabData        = tabData
            
            self.setObjectName(name) 
            self.checkTabObject = self.parent()
            
            self.__log = self.planHeatDMM.resources.log
            self.setupUi(self)     
           
            self.multiChange = []  
            
            self.refurbishmentLevelList = [refurbishmentLevel.level for refurbishmentLevel in self.planHeatDMM.data.refurbishment_levels]
            
            self.periodsDict = {}
            for period in  self.planHeatDMM.data.periods:
                self.periodsDict[period.period_text]=period.id
            
            
            
            
            self.refreshToolButton.setIcon(planHeatDMM.resources.icon_refresh_icon)
            self.deleteToolButton.setIcon(planHeatDMM.resources.icon_del_icon)
            self.deleteAllToolButton.setIcon(planHeatDMM.resources.icon_trash_icon)
            self.multiMapToolButton.setIcon(planHeatDMM.resources.icon_multi_map_icon)
            self.applyAllTabsToolButton.setIcon(planHeatDMM.resources.icon_apply_all_icon) 
            self.retrofitScenarioTable.setMouseTracking(True)
            
            self.refreshToolButton.clicked.connect(self.refreshRecordsTable)
            self.deleteToolButton.clicked.connect(self.deleteRecordTable)
            self.deleteAllToolButton.clicked.connect(self.deleteAllRecordsTable)
            self.multiMapToolButton.clicked.connect(self.multiMapDialog)
            self.applyAllTabsToolButton.clicked.connect(self.multiCopyTabsDialog)
            self.retrofitScenarioTable.cellClicked.connect(self.clickCell)
            self.retrofitScenarioTable.pressed.connect(self.pressedCell)
            self.retrofitScenarioTable.verticalHeader().sectionClicked.connect(self.clickRow)
            self.retrofitScenarioTable.horizontalHeader().sectionClicked.connect(self.clickAllRows)
            
            self.setHeaders() 
            
            self.addRecordsTable()
            
            
        except:
            self.__log.write_log("ERROR", "CheckableTabWidget Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"CheckableTabWidget",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            self.planHeatDMM.dlg.statusMessageLabel.setText("Error: " + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))

          
    def addRecordsTable(self):
        try:

            
            for period in self.planHeatDMM.data.periods:
                combo = QComboBoxRetrofitWidget(self)
                options = [refurbishmentLevelPeriod.refurbishment_level for refurbishmentLevelPeriod in self.planHeatDMM.data.refurbishment_level_periods[period.id]]
                combo.addItems(options)
              
                spinRoof   = QSpinBoxRetrofitWidget(self.planHeatDMM)
                spinWall   = QSpinBoxRetrofitWidget(self.planHeatDMM)
                spinWindow = QSpinBoxRetrofitWidget(self.planHeatDMM)
                
                spinRoof.setObjectName("spinRoof")
                spinWall.setObjectName("spinWall")
                spinWindow.setObjectName("spinWindow")
                
                spinRoof.installEventFilter(self)
                spinWall.installEventFilter(self)
                spinWindow.installEventFilter(self)
                
                
                if self.tabData.rows:
                    for data in self.tabData.rows:
                        if data.row_period_text ==  period.period_text:
                            combo.setCurrentText(data.row_refurbishment_level)
                            spinRoof.setValue(data.row_roof_percentage)
                            spinWall.setValue(data.row_wall_percentage)
                            spinWindow.setValue(data.row_window_percentage)
                            break    
             
                rowPosition = self.retrofitScenarioTable.rowCount()
                self.retrofitScenarioTable.insertRow(rowPosition)     
                self.retrofitScenarioTable.setItem(rowPosition , 0, QTableWidgetItem(period.period_text))
                self.retrofitScenarioTable.setCellWidget(rowPosition,1,combo)
                self.retrofitScenarioTable.setCellWidget(rowPosition,2,spinRoof)
                self.retrofitScenarioTable.setCellWidget(rowPosition,3,spinWall)
                self.retrofitScenarioTable.setCellWidget(rowPosition,4,spinWindow)

            
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - addRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - addRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
              
    
    def deleteRecordTable(self):
        """ Reset selected record from widget"""
        
        try:
            modelIndex = self.retrofitScenarioTable.selectionModel().selectedRows()
            self.multiChange = [index.row() for index in modelIndex]
            for rowPosition in self.multiChange:
                self.resetRow(rowPosition)
            
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - deleteRecordTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - deleteRecordTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                 

    def deleteAllRecordsTable(self):
        """ Reset All records from widget
    
        """
        try:
            records = self.retrofitScenarioTable.rowCount()
            if records > 0 :
                message = "{} rows reset, are you sure?".format(records)
                if showQuestiondialog(self,"Reset All Records",message) == QtWidgets.QMessageBox.Yes:
                    for rowPosition in range(self.retrofitScenarioTable.rowCount()):
                        self.resetRow(rowPosition)
                     
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - deleteAllRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - deleteAllRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    def refreshRecordsTable(self):
        """ Refresh all records from the last saving operation , or initial state """
        
        try:
                message = "Discard, not saved changes, are you sure?"
                if showQuestiondialog(self,"Discard Changes",message) == QtWidgets.QMessageBox.Yes:
                    while (self.retrofitScenarioTable.rowCount() > 0):
                        self.retrofitScenarioTable.removeRow(0)
                    self.addRecordsTable()
                    
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - refreshRecordsTable Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - refreshRecordsTable Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
        
    def clickCell(self,rowNum,columnNum):
        """ Clicked cell for select complete row - slot """
        
        try:
            self.selectedRows()
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - clickCell Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - clickCell Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
            
    
    
    def pressedCell(self):
        """ Mouse left button pressed for select rows  """
        try:
            self.selectedRows()
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","RetrofitScenarioWidget - pressedCell Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - pressedCell Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
    
        
    def clickRow(self,rowNum):
        """ Click row from table - Slot """
        try:    
            self.selectedRows()
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - clickRow Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - clickRow Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
    
    def clickAllRows(self):
        """ Click header from table (select all) - Slot """
        try:
            
            self.retrofitScenarioTable.selectAll()
            self.selectedRows()
                
        except:
            self.planHeatDMM.resources.log.write_log("ERROR","BuildingUseMapDialog - clickAllRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"BuildingUseMapDialog - clickAllRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    
    
            
    def selectedRows(self):
        """ Retrieve selected rows - multiple selection"""
        
        try:
            modelIndex = self.retrofitScenarioTable.selectionModel().selectedRows()
            if modelIndex:
                self.multiMapToolButton.setEnabled(True)
            else:
                self.multiMapToolButton.setEnabled(False)    
                self.multiChange = []    
                
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - selectedRows Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - selectedRows Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))        
    
    
            
    @QtCore.pyqtSlot()            
    def multiMapDialog(self):     
        """ Choose values to apply selected rows - Dialog"""
        try:
           
            modelIndex = self.retrofitScenarioTable.selectionModel().selectedRows();
            self.multiChange = [index.row() for index in modelIndex]
            
            dialog = RetroFitMultiMapDialog(self.planHeatDMM,self.refurbishmentLevelList)   
        
            dialog.show()
            dialogResult = dialog.exec_()
            
            if dialogResult == QtWidgets.QDialog.Accepted:
                for rowPosition in self.multiChange:
                    
                    item = self.retrofitScenarioTable.item(rowPosition,0)
                    combo = self.retrofitScenarioTable.cellWidget(rowPosition,1)
                    roofSpinBox = self.retrofitScenarioTable.cellWidget(rowPosition,2)
                    wallSpinBox = self.retrofitScenarioTable.cellWidget(rowPosition,3)
                    windowSpinBox = self.retrofitScenarioTable.cellWidget(rowPosition,4)
                    
                    period_text = item.text()
                    
                    result = self.validateSelectedData(period_text,self.planHeatDMM.data.listSelectedValue)
                    
                    if result:
                        combo.setCurrentText(self.planHeatDMM.data.listSelectedValue)
                        roofSpinBox.setValue(self.planHeatDMM.data.roofSpinBoxSelectedValue)
                        wallSpinBox.setValue(self.planHeatDMM.data.wallSpinBoxSelectedValue)
                        windowSpinBox.setValue(self.planHeatDMM.data.windowSpinBoxSelectedValue)
                    else:
                        self.resetRow(rowPosition)    
                   
            
            self.planHeatDMM.data.listSelectedValue = None
            self.planHeatDMM.data.roofSpinBoxSelectedValue = None      
            self.planHeatDMM.data.wallSpinBoxSelectedValue = None
            self.planHeatDMM.data.windowSpinBoxSelectedValue = None
           
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - multiMapDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - multiMapDialog Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
     
     
    def  validateSelectedData(self,period_text,selectedValue):
        """ Validate refurbishment level from period """
        try: 
            period = self.periodsDict[period_text]

            refurbishmentPeriodLevels = [level.refurbishment_level for level in self.planHeatDMM.data.refurbishment_level_periods[period]]
            
            if selectedValue in refurbishmentPeriodLevels:
                return True
            else:
                return False
        
        except KeyError:
            return False
        
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - validateSelectedData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - validateSelectedData Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            return False
           
        
        
    def multiCopyTabsDialog (self):
        """ Copy tab data to selected tabs """ 
        
        try:
           
            tabList = []
            tabDict = {}
            
            currentTabText = self.checkTabObject.tabText(self.checkTabObject.currentIndex())
            for tab_index in range(self.checkTabObject.count()):
                text = self.checkTabObject.tabText(tab_index)
                if currentTabText != text: 
                    tabDict[text] = tab_index
                    tabList.append(text)
            
            dialog = RetroFitMultiCopyTabDialog(self.planHeatDMM,tabList)   
        
            dialog.show()
            dialogResult = dialog.exec_()
            
            if dialogResult == QtWidgets.QDialog.Accepted:
              
                tableDataListSource = self.retrieveTabData()
                
                for name in self.planHeatDMM.data.listSelectedValues:
                    self.applyTabData(tableDataListSource, self.checkTabObject.widget(tabDict[name]))
                  
                self.planHeatDMM.data.listSelectedValues = []
            
           
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - multiCopyTabsDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - multiCopyTabsDialog Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
     
     
             
    def retrieveTabData(self):
        
        """ retrieve and return tab data rows """
         
        try:
            tableDataList = []
                 
            for x in range(0,self.retrofitScenarioTable.rowCount(),1):
                data = RowRefurbishTableData()
                data.row_index = x
                
                for y in range(0,self.retrofitScenarioTable.columnCount(),1):
                    if y == 0:
                        item = self.retrofitScenarioTable.item(x,y)
                        data.row_period_text = "None"  if item is None else item.text()
                        for period in self.planHeatDMM.data.periods:
                            if period.period_text == data.row_period_text: 
                                data.row_period_id = period.id
                                break 
                    elif y == 1:
                        cell = self.retrofitScenarioTable.cellWidget(x,y)
                        data.row_refurbishment_level = ""  if cell is None else cell.currentText()
                    elif y == 2:
                        cell = self.retrofitScenarioTable.cellWidget(x,y)
                        data.row_roof_percentage = 0  if cell is None else cell.value()
                    elif y == 3:
                        cell = self.retrofitScenarioTable.cellWidget(x,y)
                        data.row_wall_percentage = 0  if cell is None else cell.value()
                    elif y == 4:
                        cell = self.retrofitScenarioTable.cellWidget(x,y)
                        data.row_window_percentage = 0  if cell is None else cell.value()
                        
                tableDataList.append(data)        
            
            return tableDataList
          
        
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - retrieveData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - retrieveData Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
                   
    
    def applyTabData(self,tableDataListSource,tabObjectDestination):
        
        """ Apply source tab data to destination tab data """
         
        try:
        
            retrofitScenarioTableDestination = tabObjectDestination.retrofitScenarioTable
            
            for x in range(0,retrofitScenarioTableDestination.rowCount(),1):
                
                for y in range(0,retrofitScenarioTableDestination.columnCount(),1):
                    if y == 0:
                        item = retrofitScenarioTableDestination.item(x,y)
                        item.setText(tableDataListSource[x].row_period_text)
                    elif y == 1:
                        cell = retrofitScenarioTableDestination.cellWidget(x,y)
                        cell.setCurrentText(tableDataListSource[x].row_refurbishment_level)
                    elif y == 2:
                        cell = retrofitScenarioTableDestination.cellWidget(x,y)
                        cell.setValue(tableDataListSource[x].row_roof_percentage)
                    elif y == 3:
                        cell = retrofitScenarioTableDestination.cellWidget(x,y)
                        cell.setValue(tableDataListSource[x].row_wall_percentage)
                    elif y == 4:
                        cell = retrofitScenarioTableDestination.cellWidget(x,y)
                        cell.setValue(tableDataListSource[x].row_window_percentage)
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - applyTabData Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - applyTabData Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))                       
                        
    
    def resetRow(self,rowPosition):
        try:
            combo = self.retrofitScenarioTable.cellWidget(rowPosition,1)
            roofSpinBox = self.retrofitScenarioTable.cellWidget(rowPosition,2)
            wallSpinBox = self.retrofitScenarioTable.cellWidget(rowPosition,3)
            windowSpinBox = self.retrofitScenarioTable.cellWidget(rowPosition,4)
            combo.setCurrentText("None")
            roofSpinBox.setValue(100)
            wallSpinBox.setValue(100)
            windowSpinBox.setValue(100)   
             
        except:
            self.__log.write_log("ERROR","RetrofitScenarioWidget - resetRow Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - resetRow Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            
    
    
    def eventFilter(self, widget, event):
        """ Manage Event filter for keypress Enter in Toolbuttons """
        try:
            
            if widget.objectName()  in ("spinRoof","spinWall","spinWindow") and event.type() == QEvent.KeyPress:
                event.ignore()
                return True
            else:         
                return QtWidgets.QWidget.eventFilter(self, widget, event)
        except:
            showErrordialog(self.planHeatDMM.dlg,"RetrofitScenarioWidget - eventFilter Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))      
        
            
                                               
    def setSystemDependantFontSize(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)  
        for label in self.dialoglabels:
            label.setFont(font)        