# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanheatMappingPlugin
                                 A QGIS plugin
 A mapping plugin
                              -------------------
        begin                : 2018-03-07
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Salvatore Ferraro - RINA
        email                : salvatore.ferraro@rina.org
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .PlanheatMappingPlugin_dialog import PlanHeatMappingWizardDialog
import os.path

from ... import master_mapping_config as mm_config

class PlanheatMappingPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface, working_directory=None):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.working_directory = working_directory
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PlanheatMappingPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = None
        self.is_running = False
        self.openCMMB = False


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
        return QCoreApplication.translate('PlanheatMappingPlugin', message)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg = PlanHeatMappingWizardDialog(working_directory=self.working_directory)
        self.dlg.closingPlugin.connect(lambda: self.onClosePlanningModule(CMMB_dlg=False))
        self.dlg.CMMButton.clicked.connect(lambda: self.onClosePlanningModule(CMMB_dlg=True))

        self.dlg.show()
        # Run the dialog event loop
        self.is_running = True
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def onClosePlanningModule(self, CMMB_dlg=False):
        if not self.is_running:
            return
        # check if results.csv is made or not
        results_path = os.path.join(mm_config.CURRENT_MAPPING_DIRECTORY,
                                    mm_config.INPUT_FOLDER,
                                    mm_config.CMM_WIZARD_RESULT_FILE_NAME)
        if not os.path.exists(results_path):
            msg = QMessageBox(self.dlg)    
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setWindowTitle("Usefull energy demand not done ")
            msg.setText("You haven't load baseline data, which is required in the city mapping."+
                        " Would you like to continue ?")
            retval = msg.exec_()
            if retval == QMessageBox.No:
                return
        self.is_running = False
        self.dlg.close()
        if CMMB_dlg:
            self.openCMMB = True