# -*- coding: utf-8 -*-

from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox
# Initialize Qt resources from file resources.py
from .resources import *

from .PLANHEAT_dockwidget import PLANHEATDockWidget
from .dialog_utils import node_preferences_action, load_tree_dialog, open_right_click_menu, run_all_nodes, show_result_dialog
from .algorithm_utils import clear_all_caches
from .client_api_utils import APICacheSerializer
from .database_utils import save_tree
from .io_utils import get_temp_folder
from .planheatmappingwizard import PlanheatMappingPlugin as planning_module
from .enums import ProjectTypeEnum
import os.path
import shutil
from planheat.PlanheatMappingModule import master_mapping_config as mm_config


class PLANHEAT:
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

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PLANHEAT_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []

        self.pluginIsActive = False
        self.dockwidget = None

        self.master_dlg = master_dlg

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
        return QCoreApplication.translate('PLANHEAT', message)

    def onClosePlugin(self, tree, base_path):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        self.check_temp_is_saved(tree, base_path)

        clear_all_caches()
        temp_folder = get_temp_folder()
        if temp_folder:
            temp_folder = None
        print("closed")
        # disconnects
        #self.dockwidget.closingPlugin.disconnect(lambda: self.onClosePlugin(tree, base_path))
        self.dockwidget.treeWidget.itemDoubleClicked.disconnect(node_preferences_action)
        self.dockwidget.runButton.clicked.disconnect()
        self.dockwidget.loadButton.clicked.disconnect()
        self.dockwidget.saveButton.clicked.disconnect()
        self.dockwidget.resultButton.clicked.disconnect()
        self.dockwidget.treeWidget.clear()
        self.dockwidget.titleLabel.setText("")
        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

        # serialize the cache
        APICacheSerializer.serialize()

        # Reopen master dialog
        self.master_dlg.show()
        self.master_dlg.closeMapping.emit()
        #self.master_dlg.startButton.setEnabled(True)
        #self.master_dlg.returnButton.setEnabled(True)

    def run(self, type, base_path):
        """Run method that loads and starts the plugin"""
        # deserialize the cache
        APICacheSerializer.deserialize()

        if ProjectTypeEnum.DEMAND_CURRENT == type:
            openCMMB = self.start_planning_module()

            if not openCMMB:
                self.master_dlg.show()
                self.master_dlg.closeMapping.emit()
                return None

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = PLANHEATDockWidget()
                self.dockwidget.sizePolicy().setRetainSizeWhenHidden(True)

            # empty tree
            tree = self.dockwidget.treeWidget
            tree.setExpandsOnDoubleClick(False)
            tree.itemDoubleClicked.connect(node_preferences_action)
            tree.setContextMenuPolicy(Qt.CustomContextMenu)
            tree.customContextMenuRequested.connect(lambda: open_right_click_menu(tree))
            if ProjectTypeEnum.SUPPLY == type:
                self.dockwidget.setWindowTitle("PLANHEAT SUPPLY")
            elif ProjectTypeEnum.DEMAND_CURRENT == type:
                self.dockwidget.setWindowTitle("PLANHEAT CURRENT DEMAND")
            elif ProjectTypeEnum.DEMAND_FUTURE == type:
                self.dockwidget.setWindowTitle("PLANHEAT FUTURE DEMAND")
            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(lambda: self.onClosePlugin(tree, base_path))

            # show the dockwidget
            if ProjectTypeEnum.DEMAND_CURRENT != type or openCMMB:
                self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
                self.dockwidget.show()

            self.dockwidget.runButton.clicked.connect(lambda: run_all_nodes(tree, type.value, only_checked=True))
            self.dockwidget.loadButton.clicked.connect(lambda: load_tree_dialog(self.dockwidget, type, base_path))
            self.dockwidget.saveButton.clicked.connect(lambda: self.save_db_and_outputs(tree, base_path))
            self.dockwidget.resultButton.clicked.connect(lambda: show_result_dialog(type.value))
            if ProjectTypeEnum.DEMAND_CURRENT != type or openCMMB:
                load_tree_dialog(self.dockwidget, type, base_path)
        return self.dockwidget

    def start_planning_module(self):
        planning_run = planning_module.PlanheatMappingPlugin(self.iface)
        planning_dialog = planning_run.run()
        return planning_run.openCMMB

    def save_db_and_outputs(self, tree, base_path):
        print("Saving db and outputs")

        save_tree(tree)

        # uncommit if we want to clean results
        non_temp_folder = os.path.join(base_path, '..')
        #for f in os.listdir(non_temp_folder):
        #    if f != "temp" and os.path.isdir(os.path.join(non_temp_folder, f)):
        #        shutil.rmtree(os.path.join(non_temp_folder, f))
        #    elif os.path.isfile(os.path.join(non_temp_folder, f)):
        #        os.remove(os.path.join(non_temp_folder, f))

        # copyt data from temp
        for file in os.listdir(base_path):
            if os.path.isfile(os.path.join(base_path, file)):
                shutil.copy2(os.path.join(base_path, file), os.path.join(non_temp_folder, file)) 

         # clean temp folder
        for f in os.listdir(base_path):
            if os.path.isfile(os.path.join(base_path, f)):
                try:
                    os.remove(os.path.join(base_path, f))
                except:
                    "Can't delete {0}".format(os.path.join(base_path, f))
        # Saving cache as well
        APICacheSerializer.serialize()

    def check_temp_is_saved(self, tree, base_path):
        unsaved_file = False
        if os.path.exists(base_path):
            for f in os.listdir(base_path):
                tmp_time = os.path.getmtime(os.path.join(base_path, f))
                if os.path.exists(os.path.join(base_path, '..', f)):
                    saved_time = os.path.getmtime(os.path.join(base_path, '..', f))
                    if saved_time < tmp_time:
                        unsaved_file = True
                        break
                elif f != "temp" and not ".aux" in f:
                    unsaved_file = True
                    break
        if unsaved_file:
            msg = QMessageBox(self.dockwidget)    
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
            msg.setWindowTitle("Save calculations")
            msg.setText("Some calculations are unsaved. Would you like to save them")
            retval = msg.exec_()
            if retval == QMessageBox.Yes:
                self.save_db_and_outputs(tree, base_path)