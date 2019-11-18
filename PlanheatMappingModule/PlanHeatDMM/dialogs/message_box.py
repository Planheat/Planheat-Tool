# -*- coding: utf-8 -*-
'''
Created on 09 Oct. 2017

@author: Sergio Aparicio
'''
import sys
from PyQt5.QtWidgets import QMessageBox, QInputDialog


def showSpatialReferenceInputDialog(planHeatDMM, code):
    try:
        if code == -1:
            value, ok = QInputDialog.getInt(None,'EPSG Input Dialog', 'File Prj not found.\nIf you want to create it, and continue with the process, please enter EPSG code:',0,0)
        else:
            value, ok = QInputDialog.getInt(None,'EPSG Input Dialog', 'Is not possible to find EPSG code in prj file.\nIf you want to modify it with the correct Geospatial Reference and continue with the process, please enter EPSG code:',0,0)
                 
        if ok:
            return value
        else:
            return None    
            
    except Exception:
        planHeatDMM.resources.log.write_log("ERROR","message_box - showSpatialReferenceInputDialog Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])) 
        showErrordialog(planHeatDMM.dlg,"message_box - showSpatialReferenceInputDialog Unexpected error:",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
        

def showErrordialog(parent,title,messageText,aditionalText=None,detailedText=None):
    try:
        if parent is None:
            msg = QMessageBox()
        else:
            msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
    
        msg.setWindowTitle(title)
        msg.setText(messageText)
        if detailedText is not None:
            msg.setInformativeText(aditionalText)
        if detailedText is not None:
            msg.setDetailedText(detailedText)
    
        #msg.buttonClicked.connect(msgbtn)
    
        msg.exec_()
        
    except Exception as e:
        print(str(e))     
        
        
def showWarningdialog(parent,title,messageText,aditionalText=None,detailedText=None):
    if parent is None:
        msg = QMessageBox()
    else:
        msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setStandardButtons(QMessageBox.Ok)

    msg.setWindowTitle(title)
    msg.setText(messageText)
    if detailedText is not None:
        msg.setInformativeText(aditionalText)
    if detailedText is not None:
        msg.setDetailedText(detailedText)

    #msg.buttonClicked.connect(msgbtn)

    msg.exec_()   
            
    
def showInfodialog(parent,title,messageText,aditionalText=None,detailedText=None):
    if parent is None:
        msg = QMessageBox()
    else:
        msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setStandardButtons(QMessageBox.Ok)

    msg.setWindowTitle(title)
    msg.setText(messageText)
    if detailedText is not None:
        msg.setInformativeText(aditionalText)
    if detailedText is not None:
        msg.setDetailedText(detailedText)

    #msg.buttonClicked.connect(msgbtn)

    msg.exec_()    
    
    
def showQuestiondialog(parent,title,messageText,aditionalText=None,detailedText=None):
    if parent is None:
        msg = QMessageBox()
    else:
        msg = QMessageBox(parent)
            
    msg.setIcon(QMessageBox.Question)
    msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)

    msg.setWindowTitle(title)
    msg.setText(messageText)
    if detailedText is not None:
        msg.setInformativeText(aditionalText)
    if detailedText is not None:
        msg.setDetailedText(detailedText)

    #msg.buttonClicked.connect(msgbtn)

    retval = msg.exec_()   
    
    return retval
        

def msgbtn(i):
    print ("Button pressed is:",i.text())    
