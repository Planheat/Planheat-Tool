# -*- coding: utf-8 -*-
"""
   Main Window for stand Alone application
   :author: Sergio Aparicio Vegas 
   :version: 0.1  
   :date: 04 Oct. 2017
"""

__docformat__ = "restructuredtext"



import sys
import os


from PyQt5.QtWidgets import QApplication, QMainWindow,QPushButton,QSplashScreen
from PyQt5 import QtCore,QtGui
#from dialogs.PlanHeatDMM_dialog import PlanHeatDMMDialog
from PlanHeatDMM_dialog import PlanHeatDMMDialog
from src.pluginControl import initWindowStatus,initWindowbehavior
from src.resources import Resources
from src.data import Data

try:
    sys.path.append(os.path.dirname(__file__))
    for path in  os.environ['PATH'].split(";"):
        sys.path.append(path)
      
    import site
    import importlib
    importlib.reload(site)
except ImportError:
    pass


try:
    import externModules.shapefile
except:    
    from utility.utils import install_and_import, load_dynamic_module 
    load_dynamic_module('shapefile', os.path.dirname(__file__) + os.path.sep +"externModules" + os.path.sep + "shapefile.py")
    #install_and_import('shapefile',os.path.dirname(__file__)+ os.path.sep +"externpackages" + os.path.sep + "pyshp-1.2.12.tar.gz")  #Local

  
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        self.plugin_dir = os.path.dirname(__file__)
        if self.plugin_dir not in sys.path:
            sys.path.append(self.plugin_dir)
            
        
        self.resize(350, 100)
        self.setWindowTitle("Main Window Application Without Qgis")
        self.boton = QPushButton(self)
        self.boton.setText("Launch Planheat DMM")
        self.boton.resize(350, 100)
        self.boton.setDefault(True)
      
        
        self.dlg = None 
        
        self.exists = False
      
        
        
        self.boton.clicked.connect(self.openDialog)
        
        
        
  
    def openDialog(self):
        
        # Only single instance of Plugin
        if self.exists == True: return
        else: self.exists = True
         
        self.resources = Resources(self.plugin_dir)
        self.dlg = PlanHeatDMMDialog(self) 
        self.data = Data(plugin=False)
        
        splash = QSplashScreen(QtGui.QPixmap(self.plugin_dir + os.path.sep + 'resources/PlanHeatPrincipal.png'), QtCore.Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        splash.setEnabled(False)
        splash.show()

        # Run the dialog event loop
        self.run()
        splash.finish(self.dlg)
        self.dlg.show()
        

        result = self.dlg.exec_()
        
        self.exists = False
        
        # See if OK was pressed
        if result:
            # Do something useful here           
            pass
        else:    
            pass
        
    def run(self):
        try:
           
            initWindowStatus(self)
            self.resources.loadAppResources()
            initWindowbehavior(self)
            
        except Exception as e:
            
            print(e)
        
    
        
        
        
  
app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
app.exec_()