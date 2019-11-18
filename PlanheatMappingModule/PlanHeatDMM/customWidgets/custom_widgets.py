# -*- coding: utf-8 -*-
"""
   Customized Widgets  
   :author: Sergio Aparicio Vegas
   :version: 0.1  
   :date: 28 Nov. 2017
"""


__docformat__ = "restructuredtext"  


from PyQt5 import QtWidgets
from PyQt5.Qt import Qt, QEvent


class QSpinBoxRetrofitWidget(QtWidgets.QSpinBox):
    
    def __init__(self, planHeatDMM, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setRange(0,100)
        self.setSingleStep(100)
        self.setValue(100)
        self.setSuffix(" %")
        #self.setFocusPolicy(Qt.ClickFocus)
        self.setFocusPolicy(Qt.StrongFocus)
        
        
class QComboBoxRetrofitWidget(QtWidgets.QComboBox):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setObjectName("userQCombo")
       

    def initUI(self):
        pass

class QTableRetrofitWidget(QtWidgets.QTableWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.setObjectName("userQTable")
       

    def initUI(self):
        pass
 
    
    def event(self, event):
        
        """ Manage lost focus event on QTablewidget, avoiding deselect rows """
        if event.type()== QEvent.FocusOut:return False     
        
        return QtWidgets.QTableWidget.event(self, event)
                       

            
  
        
                
        