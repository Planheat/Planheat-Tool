# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanHeatDMM
                                 A QGIS plugin
 PlanHeatDMM
                              -------------------
        begin                : 2017-10-03
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Sergio Aparicio Vegas
        email                : sapariciov@hotmail.com
 ***************************************************************************/
"""

import os.path
import sys

try:
    sys.path.append(os.path.dirname(__file__))
    for path in os.environ['PATH'].split(";"):
        sys.path.append(path)
    import site
    import importlib

    importlib.reload(site)

except ImportError:
    pass

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QSplashScreen
from PyQt5 import QtCore, QtGui

# Initialize Qt resources from file resources.py

try:
    import externModules.shapefile
except:
    from utility.utils import load_dynamic_module

    load_dynamic_module('shapefile', os.path.dirname(__file__) + os.path.sep + "externModules" + os.path.sep + "shapefile.py")
    # install_and_import('shapefile','pyshp',"1.2.12")  # Internet

# QCoreApplication.setAttribute(QtCore.Qt.AA_Use96Dpi)


try:
    from config import config as Config
except ImportError:
    from .config import config as Config
    # sys.exit()

from .resources import *
# Import the code for the dialog
from .PlanHeatDMM_dialog import PlanHeatDMMDialog

from src.pluginControl import initWindowStatus, initWindowbehavior
from src.resources import Resources
from src.data import Data

from .. import master_mapping_config
from .dmm_serialization import DMMSerializer


class PlanHeatDMM:
    """QGIS Plugin Implementation."""

    def __init__(self, iface, master_dlg):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        if self.plugin_dir not in sys.path:
            sys.path.append(self.plugin_dir)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PlanHeatDMM_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = None
        self.resources = None
        self.data = None

        self.exists = False

        # Declare instance attributes
        self.actions = []
        self.master_dlg = master_dlg
        self.projectName = master_mapping_config.CURRENT_PROJECT_NAME

        dir_path = os.path.dirname(os.path.realpath(__file__))
        dmm_temp_dir = os.path.join(dir_path, "temp")
        os.makedirs(dmm_temp_dir, exist_ok=True)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DMM PlanHeat', message)

    def run(self):
        """Run method that performs all the real work"""
        try:
            # locale.setlocale(locale.LC_ALL, 'en-GB')
            # Only single instance of Plugin
            if self.exists == True:
                return
            else:
                self.exists = True

            self.dlg = PlanHeatDMMDialog(self)
            self.resources = Resources(self.plugin_dir)
            self.data = Data(plugin=True)

            # Name of project
            self.data.projectName = master_mapping_config.CURRENT_PROJECT_NAME

            # Redirection
            dmm_folder = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                                                    master_mapping_config.DMM_FOLDER)
            os.makedirs(dmm_folder, exist_ok=True)
            self.data.outputSaveFile = os.path.join(dmm_folder, master_mapping_config.DMM_PREFIX)


            splash = QSplashScreen(QtGui.QPixmap(self.plugin_dir + os.path.sep + 'resources/PlanHeatPrincipal.png'), QtCore.Qt.WindowStaysOnTopHint)
            splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
            splash.setEnabled(False)
            splash.show()

            # Run the dialog event loop
            initWindowStatus(self)
            self.resources.loadAppResources()
            initWindowbehavior(self)

            # Deserialize the module
            DMMSerializer.deserialize(self)

            splash.finish(self.dlg)

            # show the dialog
            self.dlg.show()

            # Run the dialog event loop
            result = self.dlg.exec_()

            self.exists = False

            # See if OK was pressed
            if result:
                # Do something useful here -
                pass
            else:
                pass



        except Exception as e:
            self.exists = False
            print(str(e))

