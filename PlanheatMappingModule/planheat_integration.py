# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanheatIntegration
                                 A QGIS plugin
 planheat integration
                              -------------------
        begin                : 2017-12-06
        git sha              : $Format:%H$
        copyright            : (C) 2017 by v
        email                : v
 ***************************************************************************/

"""
import subprocess
import site
import os
import importlib, sys
from osgeo import gdal

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .planheat_integration_dialog import PlanheatIntegrationDialog

from .PLANHEAT import PLANHEAT as cmm
from .PlanHeatDMM import PlanHeatDMM as dmm

from qgis.core import QgsProject, QgsRasterLayer, QgsFillSymbol, QgsVectorLayer
from qgis.utils import iface

from .PLANHEAT.enums import ProjectTypeEnum
from .shapeCreator.shapeCreator import ShapeCreator
from .pointCreator.pointCreator import PointCreator
from . import master_mapping_config


class PlanheatIntegration:
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
        # Save reference to master dlg
        self.master_dlg = master_dlg
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PlanheatMappingModule_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PlanheatIntegrationDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Planheat Mapping Module')
        self.pluginIsActive = False
        self.dockwidget = None


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
        return QCoreApplication.translate('PlanheatMappingModule', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        checkable=False):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param checkable: boolean if button is checkable (activate/deactivate).
        :type checkable: boolean

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PlanheatMappingModule/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Planheat Mapping Module'),
            callback=self.run,
            parent=self.iface.mainWindow())

        #icon_path_sc = ':/plugins/PlanheatMappingModule/shapeCreator/icon.png'
        file_dir_path = os.path.dirname(os.path.realpath(__file__))
        icon_path_sc = os.path.join(file_dir_path, "shapeCreator", "icon.png")
        self.add_action(
            icon_path_sc,
            text='&Create shape',
            callback=self.runShapeCreator,
            checkable=True,
            parent=self.iface.mainWindow())

        #icon_path_pc = ':/plugins/PlanheatMappingModule/pointCreator/icon.png'
        file_dir_path = os.path.dirname(os.path.realpath(__file__))
        icon_path_pc = os.path.join(file_dir_path, "pointCreator", "icon.png")
        self.add_action(
            icon_path_pc,
            text='&Create point',
            callback=self.runPointCreator,
            checkable=True,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Planheat Mapping Module'),
                action)
            self.iface.removeToolBarIcon(action)

    def runShapeCreator(self):
        ShapeCreator.select(self)

    def runPointCreator(self):
        PointCreator.select(self)

    def run(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True
            self.dlg.closingPlugin.connect(lambda: self.onClosePlugin(master_dlg=False))
            self.dlg.startButton.clicked.connect(self.onStart)
            self.dlg.returnButton.clicked.connect(lambda: self.onClosePlugin(master_dlg=True))
            self.dlg.infoCmmWidget.setVisible(False)
            self.dlg.infoDmmWidget.setVisible(False)
            self.dlg.infoSupplyWidget.setVisible(False)
            self.dlg.cmm_image.setVisible(False)
            self.dlg.dmm_image.setVisible(False)
            self.dlg.smm_image.setVisible(False)
            self.dlg.startButton.setEnabled(False)
            self.dlg.returnButton.setEnabled(True)
            self.dlg.buttonGroup.setExclusive(False)
            self.dlg.currentRadio.setChecked(False)
            self.dlg.futureRadio.setChecked(False)
            self.dlg.districtRadio.setChecked(False)
            self.dlg.supplyRadio.setChecked(False)
            self.dlg.buttonGroup.setExclusive(True)
            self.dlg.currentRadio.clicked.connect(self.radio_selection_changed)
            self.dlg.futureRadio.clicked.connect(self.radio_selection_changed)
            self.dlg.districtRadio.clicked.connect(self.radio_selection_changed)
            self.dlg.supplyRadio.clicked.connect(self.radio_selection_changed)
            #self.dlg.show()

    def radio_selection_changed(self):
        self.dlg.infoCmmWidget.setVisible(False)
        self.dlg.infoDmmWidget.setVisible(False)
        self.dlg.infoSupplyWidget.setVisible(False)
        self.dlg.cmm_image.setVisible(False)
        self.dlg.dmm_image.setVisible(False)
        self.dlg.smm_image.setVisible(False)
        if self.dlg.currentRadio.isChecked() or self.dlg.futureRadio.isChecked():
            self.dlg.infoCmmWidget.setVisible(True)
            self.dlg.cmm_image.setVisible(True)
        elif self.dlg.districtRadio.isChecked():
            self.dlg.infoDmmWidget.setVisible(True)
            self.dlg.dmm_image.setVisible(True)
        elif self.dlg.supplyRadio.isChecked():
            self.dlg.infoSupplyWidget.setVisible(True)
            self.dlg.smm_image.setVisible(True)
        self.dlg.startButton.setEnabled(True)
        self.dlg.returnButton.setEnabled(True)

    def onClosePlugin(self, master_dlg=True):
        # disconnects

        self.dlg.closingPlugin.disconnect()
        self.dlg.startButton.clicked.disconnect()
        self.dlg.returnButton.clicked.disconnect()
        self.dlg.close()
        self.pluginIsActive = False
        if master_dlg:
            self.master_dlg.show()
            self.master_dlg.closeMapping.emit()

    def onStart_old(self):
        # print(os.path.dirname(__file__))
        # base_path = "c:/TEMP/"
        base_path = master_mapping_config.CURRENT_MAPPING_DIRECTORY
        self.dlg.startButton.setEnabled(False)
        self.dlg.returnButton.setEnabled(False)
        if self.dlg.currentRadio.isChecked():
            self.open_cmm_current_demand(base_path)
        elif self.dlg.futureRadio.isChecked():
            self.open_cmm_future_demand(base_path)
        elif self.dlg.districtRadio.isChecked():
            self.open_dmm()
        elif self.dlg.supplyRadio.isChecked():
            self.open_cmm_supply(base_path)
        #self.dlg.close()
        self.dlg.startButton.setEnabled(True)
        self.dlg.returnButton.setEnabled(True)

    def onStart(self, mode):
        # mode in ["CMMB", "CMMF", "SMM", "DMM"]
        # print(os.path.dirname(__file__))
        # base_path = "c:/TEMP/"
        base_path = master_mapping_config.CURRENT_MAPPING_DIRECTORY
        self.dlg.startButton.setEnabled(False)
        self.dlg.returnButton.setEnabled(False)
        if mode == master_mapping_config.CMM_BASELINE_FOLDER:
            self.open_cmm_current_demand(base_path)
        elif mode == master_mapping_config.CMM_FUTURE_FOLDER:
            self.open_cmm_future_demand(base_path)
        elif mode == master_mapping_config.DMM_FOLDER:
            self.open_dmm()
        elif mode == master_mapping_config.SMM_FOLDER:
            self.open_cmm_supply(base_path)

    def open_cmm_current_demand(self, base_path):
        cmmrun = cmm.PLANHEAT(self.iface, self.master_dlg)
        self.dlg.hide()

        dockwidget = cmmrun.run(ProjectTypeEnum.DEMAND_CURRENT, os.path.join(base_path, 
                                                                master_mapping_config.CMM_BASELINE_FOLDER,
                                                                "temp_folder"))
        self.dockwidget = dockwidget
        self.dlg.currentRadio.setEnabled(False)
        if dockwidget is not None:
            dockwidget.closingPlugin.connect(lambda: self.enable_button(self.dlg.currentRadio))

    def open_cmm_future_demand(self, base_path):
        cmmrun = cmm.PLANHEAT(self.iface, self.master_dlg)
        self.dlg.hide()

        dockwidget = cmmrun.run(ProjectTypeEnum.DEMAND_FUTURE, os.path.join(base_path, 
                                                                master_mapping_config.CMM_FUTURE_FOLDER,
                                                                "temp_folder"))
        self.dockwidget = dockwidget
        self.dlg.futureRadio.setEnabled(False)
        if dockwidget is not None:
            dockwidget.closingPlugin.connect(lambda: self.enable_button(self.dlg.futureRadio))

    def open_cmm_supply(self, base_path):
        cmmrun = cmm.PLANHEAT(self.iface, self.master_dlg)
        self.dlg.hide()

        dockwidget = cmmrun.run(ProjectTypeEnum.SUPPLY, os.path.join(base_path, 
                                                                    master_mapping_config.SMM_FOLDER, 
                                                                    "temp_folder"))
        self.dockwidget = dockwidget
        self.dlg.supplyRadio.setEnabled(False)
        if dockwidget:
            dockwidget.closingPlugin.connect(lambda: self.enable_button(self.dlg.supplyRadio))

    def enable_button(self, button):
        button.setEnabled(True)
        self.dockwidget = None

    def open_dmm(self):
        dmmrun = dmm.PlanHeatDMM(self.iface, self.master_dlg)
        dmmrun.run()

    def load_open_street_maps(self):
        if not QgsProject.instance().mapLayersByName("OSM"):
            canvas = self.iface.mapCanvas()
            canvas.setSelectionColor(QColor(255, 255, 0, 80))
            canvas.zoomToFullExtent()
            QTimer.singleShot(10, load_osm)
        else:
            layer = self.iface.activeLayer()
            layer.selectAll()
            self.iface.mapCanvas().zoomToSelected()
            layer.removeSelection()


def load_osm():
    lyr = QgsRasterLayer("type=xyz&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png", "OSM", "wms")
    QgsProject.instance().addMapLayer(lyr, False)
    QgsProject.instance().layerTreeRoot().insertLayer(-1, lyr)
