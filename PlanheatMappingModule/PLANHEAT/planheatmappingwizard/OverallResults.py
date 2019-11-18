# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 18:23:28 2018

@author: SALFE
"""

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget

class OverallResults (QtWidgets.QWidget):
    
    def doIntertResult(self,val):
        self.results.append(val)
        
    def doGetCount(self):
        return self.results.count()
        
    def doClearResults(self):
        self.results.clear()
        
    def __init__(self,parent=None):
        super(OverallResults, self).__init__(parent)
        self.results = []
        self.hide()