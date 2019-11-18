# -*- coding: utf-8 -*-
"""
   Plugin Process Resources
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 06 Oct. 2017
"""

__docformat__ = "restructuredtext"

import os
import sys
import time
import datetime

from PyQt5 import QtGui
from dialogs.message_box import showErrordialog 

class Resources():
    
    """ Resources used by the process & interface Objects """


    def __init__(self,directory):
        '''
        Constructor
        '''
        self.logDateName =  datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.processName =  datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        self.plugin_dir = directory 
        self.log = None
        self.database = None
        self.noa = None
        self.thread = None
        self.thread_clock = None
        self.javaProcessObject = None
        

        
        self.pixmap_wrong_icon   = None
        self.pixmap_right_icon   = None 
        self.pixmap_warning_icon = None
        self.pixmap_wrong_way_icon = None
        self.pixmap_halt_icon = None
        self.pixmap_warn_icon = None
        
        self.icon_pencil = None
        self.icon_add_icon = None
        self.icon_del_icon = None
        self.icon_trash_icon = None
        self.icon_refresh_icon = None
        self.icon_halt_icon = None
        
    def loadAppResources(self):
        """ load interface graphical resources """
        try:
            self.pixmap_wrong_icon      = QtGui.QPixmap(self.plugin_dir + os.path.sep + 'resources/wrong24.png')
            self.pixmap_warning_icon    = QtGui.QPixmap(self.plugin_dir + os.path.sep + 'resources/warning24.png')
            self.pixmap_right_icon      = QtGui.QPixmap(self.plugin_dir+ os.path.sep + 'resources/right24.png')
            self.pixmap_wrong_way_icon  = QtGui.QPixmap(self.plugin_dir + os.path.sep + 'resources/wrong_way_32.png')
            self.pixmap_halt_icon       = QtGui.QPixmap(self.plugin_dir + os.path.sep + 'resources/halt_32.png')
            self.pixmap_warn_icon       = QtGui.QPixmap(self.plugin_dir+ os.path.sep + 'resources/warning_32.png')
            
           
            self.icon_pencil            = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/pencil.png')
            self.icon_add_icon          = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/add_32.png')
            self.icon_del_icon          = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/delete_32.png')
            self.icon_trash_icon        = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/trash_32.png')
            self.icon_refresh_icon      = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/refresh_32.png')
            self.icon_halt_icon         = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/halt_32.png')
            self.icon_ok_icon           = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/ok_32.png')
            self.icon_error_icon        = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/error_32.png')
            self.icon_warn_icon         = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/warning_32.png')
            self.icon_multi_map_icon    = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/multi_map_32.png')
            self.icon_retrofitted_icon  = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/building_repair_32.png')
            self.icon_apply_all_icon    = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/apply_all_32.png')
            self.icon_load_icon         = QtGui.QIcon(self.plugin_dir + os.path.sep + 'resources/load_32.png')
            
            

            
        except:
            self.log.write_log("ERROR","loadAppResources Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
            showErrordialog(None,"loadAppResources",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
    
    def releaseResources(self,planHeatDMM):
        """ Release application resources """
        try:
            if planHeatDMM.resources.thread is not None:
                if planHeatDMM.resources.thread.isRunning():
                    planHeatDMM.data.processContinue = False
                    self.log.write_log("INFO","releaseResources close thread request")
                    time.sleep(2.0)
                
                if not planHeatDMM.resources.thread.isFinished():
                    planHeatDMM.resources.thread.terminate()
                    self.log.write_log("INFO","releaseResources kill thread")
                
            if planHeatDMM.resources.database is not None:
                planHeatDMM.resources.database.maintenanceDataBase("VACUUM")
                planHeatDMM.resources.log.write_log("INFO","close Database")
                planHeatDMM.resources.database.closeDB()
                planHeatDMM.resources.database = None
        
            if planHeatDMM.resources.log is not None:
                planHeatDMM.resources.log.write_log("INFO","close log file")
                planHeatDMM.resources.log.close_log()
                planHeatDMM.resources.log = None
                    
        except:
            showErrordialog(planHeatDMM.dlg,"releaseResources",str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))    
            self.log.write_log("ERROR","releaseResources Unexpected error:" + str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1]))
                
    
        


