# -*- coding: utf-8 -*-
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog, QTableWidgetItem, QTextEdit
from PyQt5.QtCore import Qt

# Initialize Qt resources from file resources.py
from .ui.resources import *
# Import the code for the dialog
from .ui.dhcoptimizer_planheat_dialog import DHCOptimizerPlanheatDialog
from .ui.dhcoptimizer_planheat_dock import DHCOptimizerPlanheatDock
from .ui.dhcoptimizer_planheat_dock_manual import DHCOptimizerPlanheatDockManual
import os.path
import sys
import osmnx as ox
from qgis.core import QgsVectorLayer, QgsProject, QgsField, QgsCategorizedSymbolRenderer, QgsRendererCategory, \
    QgsFillSymbol, QgsLineSymbol, QgsDistanceArea, QgsVectorFileWriter, QgsGraduatedSymbolRenderer,\
    QgsPointXY, QgsGeometry, QgsFeature
from .optimizer.DHCOptimizer import DHCOptimizer
from .optimizer import config
from .exception_utils import DHCOptimizerException
from .ui import uiconf, ui_utils
from .optimizer.network_serialization import NetworkSerializer
from ..layer_utils import save_layer_to_shapefile, load_file_as_layer
from shapely.geometry import Point
import geopandas as gpd
import networkx as nx
import logging


class DHCOptimizerPlanheat:
    """QGIS Plugin Implementation."""

    #os.environ["JULIA_HOME"] = os.path.join(os.path.dirname(__file__),"deps/Julia-0.6.2/bin")

    def __init__(self, iface, working_directory=None, data_transfer=None):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.data_transfer = data_transfer
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DHCOptimizerPlanheat_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Set useful paths :
        if working_directory is not None:
            self.working_directory = working_directory
        else:
            self.working_directory = os.path.join(os.environ["LOCALAPPDATA"], "QGIS\\QGIS3\\planheat_data")
            if not os.path.exists(self.working_directory):
                raise RuntimeError("DHC optimizer working directory does not exist in AppData/Local/. Please set a valid"
                            " path as variable.")
        self.result_dir = os.path.join(self.working_directory, "results")
        os.makedirs(self.result_dir, exist_ok=True)
        self.tmp_dir = os.path.join(self.working_directory, "tmp")
        os.makedirs(self.tmp_dir, exist_ok=True)

        # Create empty DHC optimizer object
        self.dhc_opt = None

        # Set layers :
        self.street_layer = None
        self.building_layer = None
        self.supply_layer = None

        # Extension mode:
        self.old_network_edges_layer = None
        self.old_network_supply_layer = None
        self.old_supply_edges_layer = None
        self.temp_layer = None

        # FCFCCP = "Fixed cost flow with coverage constraint problem"
        # STP = "Steiner tree problem"
        # dialog_menu to chose the mode
        # dock for the FCFCCP
        # manual_dock for the STP

        # Create the dialog (after translation) and keep reference
        self.dialog_menu = DHCOptimizerPlanheatDialog()
        self.dock = DHCOptimizerPlanheatDock()
        self.manual_dock = DHCOptimizerPlanheatDockManual()

        # Problem statistics :
        self.nb_streets = 0
        self.nb_buildings = 0
        self.nb_old_supply = 0
        self.nb_leastcost_streets = 0
        self.nb_potential_supply = 0
        self.building_heat_demand = 0
        if self.data_transfer is None:
            self.study_id = 0
        else:
            self.study_id = self.data_transfer.study_id
            print("dhcoptimizer_planheat.py, __init__(), self.study_id :", self.study_id)

        # Declare instance attributes
        self.actions = []
        # self.menu = self.tr(u'&DHCOptimizerPlanheat')
        # TODO: We are going to let the user set this up in a future iteration
        # self.toolbar = self.iface.addToolBar(u'DHCOptimizerPlanheat')
        # self.toolbar.setObjectName(u'DHCOptimizerPlanheat')
        self.connect_buttons()
        self.dock.tabWidget.setTabEnabled(self.dock.tabWidget.indexOf(self.dock.sizing_tab), False)
        self.manual_dock.tabWidget.setTabEnabled(self.manual_dock.tabWidget.indexOf(self.manual_dock.results_tab),
                                                 False)

        # Solution layers :
        self.selected_buildings_layer = None
        self.unselected_buildings_layer = None
        self.selected_edges_layer = None
        self.selected_supply_layer = None


    def connect_buttons(self):
        self.dock.toolButton_districtShapeFile.clicked.connect(
            lambda: ui_utils.browse_and_set_file_path(self.dock.lineEdit_districtShapefile))
        self.dock.toolButton_buildingsShapefile.clicked.connect(
            lambda: ui_utils.browse_and_set_file_path(self.dock.lineEdit_buildingsShapefile))
        # Supply buttons :
        self.dock.locate_sources_button.clicked.connect(lambda: self.locate_sources("potential_supply"))
        self.dock.clear_sources_button.clicked.connect(lambda: self.clear_sources("potential_supply"))
        # Set click action for 'compute' button :
        self.dock.compute_button.clicked.connect(lambda: self.run_computation(self.dock))
        # Streets buttons :
        self.dock.download_street_button.clicked.connect(lambda: self.download_streets_from_osm(self.dock))
        self.dock.exclude_streets_button.clicked.connect(
            lambda: self.update_selected_streets_status(self.dock, config.EXCLUDED_STATUS_VALUE))
        self.dock.include_streets_button.clicked.connect(
            lambda: self.update_selected_streets_status(self.dock, config.INCLUDED_STATUS_VALUE))
        self.dock.leastcost_streets_button.clicked.connect(
            lambda: self.update_selected_streets_status(self.dock, config.LEASTCOST_STATUS_VALUE))
        self.dock.spinBox_leastcost_coef.setValue(config.LEASTCOST_COEF)
        # Buildings buttons :
        self.dock.show_buildings_button.clicked.connect(lambda: self.show_buildings(self.dock))
        self.dock.exclude_buildings_button.clicked.connect(
            lambda: self.update_selected_buildings_status(self.dock, config.EXCLUDED_STATUS_VALUE))
        self.dock.include_buildings_button.clicked.connect(
            lambda: self.update_selected_buildings_status(self.dock, config.INCLUDED_STATUS_VALUE))
        # Objective spin box update :
        self.dock.demandCoverage.valueChanged.connect(self.update_objective_number)
        self.dock.checkBox_connect_all_buildings.clicked.connect(self.update_objective_number)
        # Reset button:
        #self.dock.reset_button.clicked.connect(lambda: self.reset(self.dock))
        ## Pipe size calculation
        self.dock.only_preprocess_button.clicked.connect(lambda: self.pipe_size_calculation(self.dock, only_preprocess=True))
        self.dock.pipe_size_calculation_button.clicked.connect(lambda: self.pipe_size_calculation(self.dock, only_preprocess=False))
        # # Extension mode:
        self.dock.add_old_buildings_button.clicked.connect(lambda: self.add_old_network_buildings(self.dock))
        self.dock.add_old_streets_button.clicked.connect(lambda: self.add_old_network_streets(self.dock))
        #self.dock.locate_old_sources_button.clicked.connect(lambda: self.locate_sources("old_supply"))
        #self.dock.clear_old_sources_button.clicked.connect(lambda: self.clear_sources("old_supply"))
        self.dock.generate_existing_network_button.clicked.connect(lambda: self.show_existing_network(self.dock))
        # self.dock.save_pipe_capacities_button.clicked.connect(lambda: self.save_pipe_capacities())
        self.dock.toolButton_existingNetworkShapefile.clicked.connect(
            lambda: ui_utils.browse_and_set_file_path(self.dock.lineEdit_existingNetworkShapefile,
                                                    filter="Compressed file (*.zip)"))
        self.dock.save_existing_network_button.clicked.connect(lambda: self.save_existing_network(self.dock))
        self.dock.add_existing_network_button.clicked.connect(lambda: self.add_existing_network(self.dock))

        ### For manual dock :
        md_dock = self.manual_dock
        md_dock.toolButton_districtShapeFile.clicked.connect(
            lambda: ui_utils.browse_and_set_file_path(self.manual_dock.lineEdit_districtShapefile))
        md_dock.toolButton_buildingsShapefile.clicked.connect(
            lambda: ui_utils.browse_and_set_file_path(self.manual_dock.lineEdit_buildingsShapefile))
        # Set click action for 'compute' button :
        md_dock.compute_button.clicked.connect(lambda: self.run_computation(md_dock))
        # Streets buttons :
        md_dock.download_street_button.clicked.connect(lambda: self.download_streets_from_osm(md_dock))
        md_dock.exclude_streets_button.clicked.connect(
            lambda: self.update_selected_streets_status(md_dock, config.EXCLUDED_STATUS_VALUE))
        md_dock.include_streets_button.clicked.connect(
            lambda: self.update_selected_streets_status(md_dock, config.INCLUDED_STATUS_VALUE))
        md_dock.leastcost_streets_button.clicked.connect(
            lambda: self.update_selected_streets_status(md_dock, config.LEASTCOST_STATUS_VALUE))
        md_dock.spinBox_leastcost_coef.setValue(config.LEASTCOST_COEF)
        # Buildings buttons :
        md_dock.show_buildings_button.clicked.connect(lambda: self.show_buildings(md_dock))
        md_dock.include_buildings_button.clicked.connect(
            lambda: self.update_selected_buildings_status(md_dock, config.INCLUDED_STATUS_VALUE))
        md_dock.exclude_buildings_button.clicked.connect(
            lambda: self.update_selected_buildings_status(md_dock, config.EXCLUDED_STATUS_VALUE))
        # Reset button:
        md_dock.reset_button.clicked.connect(lambda: self.reset(md_dock))
        # Extension mode :
        md_dock.add_old_buildings_button.clicked.connect(lambda: self.add_old_network_buildings(md_dock))
        md_dock.add_old_streets_button.clicked.connect(lambda: self.add_old_network_streets(md_dock))
        md_dock.generate_existing_network_button.clicked.connect(lambda: self.show_existing_network(md_dock))
        md_dock.toolButton_existingNetworkShapefile.clicked.connect(
            lambda: ui_utils.browse_and_set_file_path(md_dock.lineEdit_existingNetworkShapefile,
                                                  filter="Compressed file (*.zip)"))
        md_dock.save_existing_network_button.clicked.connect(lambda: self.save_existing_network(md_dock))
        md_dock.add_existing_network_button.clicked.connect(lambda: self.add_existing_network(md_dock))
        md_dock.Extension_mGroupBox.setCollapsed(True)
        self.update_extension_mode_status(md_dock)

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
        return QCoreApplication.translate('DHCOptimizerPlanheat', message)

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
            parent=None):
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

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/dhcoptimizer_planheat/ui/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Planheat DHC Optimizer'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&DHCOptimizerPlanheat'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar



    def check_file_exists(self, filepath):
        if not os.path.isfile(filepath):
            self.iface.messageBar().pushMessage("Error", "File not found : ‘%s’" % str(filepath), level=1)
            return False
        return True

    def check_district_shapefile(self, dock):
        district_shape_file = dock.lineEdit_districtShapefile.text()
        if not self.check_file_exists(district_shape_file):
            district_shape_file = self.data_transfer.get_building_layer_file_path()
            if not self.check_file_exists(district_shape_file):
                return False
        return True

    def check_building_shapefile(self, dock):
        building_shape_file = dock.lineEdit_buildingsShapefile.text()
        if not self.check_file_exists(building_shape_file):
            return False
        return True

    def check_inputs(self, dock):
        if not self.check_district_shapefile(dock):
            return False
        if not self.check_building_shapefile(dock):
            return False
        if dock == self.dock:
            try:
                demand_coverage = float(self.dock.demandCoverage.value())
            except:
                demand_coverage = 0
            if demand_coverage > 100 or demand_coverage < 0:
                self.iface.messageBar().pushMessage("Error",
                                                    "Invalid demand coverage objective value : %s " % str(
                                                        demand_coverage),
                                                    level=1)
                return False
            objective, production_is_limiting = self.get_objective_number()
            if objective <= 0.0:
                self.iface.messageBar().pushMessage("Error",
                                                    "Invalid coverage objective : %s " % str(objective),
                                                    level=1)
                return False
        elif dock == self.manual_dock:
            if dock.Extension_mGroupBox.isEnabled():
                if self.dhc_opt.graph_builder.old_network_graph is None:
                    self.show_existing_network(dock)
        return True

    def show_buildings(self, dock):
        print("show buildings")
        # Get text from the text input edit line
        if self.data_transfer.ready_check():
            dock.lineEdit_buildingsShapefile.setText(self.data_transfer.get_building_layer_file_path())
        building_shape_file = dock.lineEdit_buildingsShapefile.text()
        # Check if the file exists
        if not self.check_file_exists(building_shape_file):
            return
        # Set waiting message bar :
        self.iface.messageBar().pushMessage("Loading building shape file", "Please wait...", level=0, duration=0)
        self.iface.mainWindow().repaint()
        # If a building layer already exists, remove it to show the new one
        if self.building_layer is not None and self.building_layer in QgsProject.instance().mapLayers().values():
            QgsProject.instance().removeMapLayer(self.building_layer)
        self.load_building_layer(building_shape_file)
        # Set style of the new layer :
        buildings_color = uiconf.included_buildings_color if dock == self.dock else uiconf.excluded_buildings_color
        buildings_opacity = uiconf.buildings_opacity
        self.building_layer.renderer().symbol().setColor(buildings_color)
        self.building_layer.setOpacity(buildings_opacity)
        # Show the layer
        ui_utils.add_layer_to_group(self.building_layer, self.study_suffix(uiconf.input_layers_group_prefix))
        # Add the "Status" boolean attribute to the layer if it is not already set
        if dock == self.dock:
            ui_utils.set_marked_field(self.building_layer, config.STATUS_KEY, config.INCLUDED_STATUS_VALUE)
        elif dock == self.manual_dock:
            ui_utils.set_marked_field(self.building_layer, config.STATUS_KEY, config.EXCLUDED_STATUS_VALUE)
        # Allow to click the button "exclude selected buildings"
        dock.exclude_buildings_button.setEnabled(True)
        dock.include_buildings_button.setEnabled(True)
        # Set labels
        self.update_buildings_labels(dock)
        # update accessibility to extension mode
        self.update_extension_mode_status(dock)
        # Reset message bar
        self.iface.messageBar().clearWidgets()

    def load_building_layer(self, building_shape_file: str):
        if not self.check_file_exists(building_shape_file):
            return
        self.building_layer = QgsVectorLayer(building_shape_file, self.study_suffix(uiconf.buildings_layer_prefix),
                                             "ogr")
        fields = self.building_layer.fields()   
        field_names = [field.name() for field in fields]
        if config.EXCLUDED_BUILDING_KEY not in field_names:
            ui_utils.set_marked_field(self.building_layer, config.EXCLUDED_BUILDING_KEY, 0)
        self.nb_buildings = self.building_layer.featureCount()

    def study_suffix(self, prefix):
        return prefix + str(self.study_id)


    def update_selected_buildings_status(self, dock, status_value):
        # Get the current selected buildings
        selected_buildings = self.building_layer.selectedFeatures()
        buildings_ids = {f.attribute(config.BUILDING_ID_KEY) for f in selected_buildings}
        # Set excluded buildings set for the optimizer
        graph_builder = self.dhc_opt.graph_builder
        if dock == self.dock:
            if status_value == config.EXCLUDED_STATUS_VALUE:
                graph_builder.marked_buildings = graph_builder.marked_buildings.union(buildings_ids)
            elif status_value == config.INCLUDED_STATUS_VALUE:
                graph_builder.marked_buildings = graph_builder.marked_buildings.difference(buildings_ids)
        elif dock == self.manual_dock:
            if status_value == config.EXCLUDED_STATUS_VALUE:
                graph_builder.marked_buildings = graph_builder.marked_buildings.difference(buildings_ids)
            elif status_value == config.INCLUDED_STATUS_VALUE:
                graph_builder.marked_buildings = graph_builder.marked_buildings.union(buildings_ids)
        if status_value != config.EXISTING_STATUS_VALUE:
            graph_builder.old_network_buildings = graph_builder.old_network_buildings.difference(buildings_ids)
        # Set "Status" attribute to 0 for buildings to exclude, 1 if included
        self.building_layer.startEditing()
        status_index = self.building_layer.fields().indexFromName(config.STATUS_KEY)
        for b in selected_buildings:
            self.building_layer.changeAttributeValue(b.id(), status_index, status_value)
        self.building_layer.commitChanges()
        # Set categorized renderer to show which buildings have been excluded :
        current_renderer = self.building_layer.renderer()
        if not isinstance(current_renderer, QgsCategorizedSymbolRenderer) \
                or current_renderer.classAttribute() != config.STATUS_KEY:
            r = self.get_renderer('fill')
            self.building_layer.setRenderer(r)
        # Remove selection :
        self.building_layer.removeSelection()
        # Update labels :
        self.update_buildings_labels(dock)

    def get_renderer(self, sub_symbol_type):
        r = QgsCategorizedSymbolRenderer()
        r.setClassAttribute(config.STATUS_KEY)
        qrc0 = QgsRendererCategory()
        qrc1 = QgsRendererCategory()
        qrc2 = QgsRendererCategory()
        qrc3 = QgsRendererCategory()
        qrc0.setLabel(config.EXCLUDED_KEY)
        qrc1.setLabel(config.INCLUDED_KEY)
        qrc2.setLabel(config.EXISTING_KEY)
        qrc3.setLabel(config.LEASTCOST_KEY)
        qrc0.setValue(config.EXCLUDED_STATUS_VALUE)
        qrc1.setValue(config.INCLUDED_STATUS_VALUE)
        qrc2.setValue(config.EXISTING_STATUS_VALUE)
        qrc3.setValue(config.LEASTCOST_STATUS_VALUE)
        if sub_symbol_type == 'fill':
            symb0 = QgsFillSymbol()
            symb1 = QgsFillSymbol()
            symb2 = QgsFillSymbol()
            symb3 = QgsFillSymbol()
            symb0.setColor(uiconf.excluded_buildings_color)
            symb1.setColor(uiconf.included_buildings_color)
            symb2.setColor(uiconf.old_network_buildings_color)
        elif sub_symbol_type == 'line':
            symb0 = QgsLineSymbol()
            symb1 = QgsLineSymbol()
            symb2 = QgsLineSymbol()
            symb3 = QgsLineSymbol()
            symb0.setColor(uiconf.excluded_streets_color)
            symb0.setWidth(uiconf.street_width)
            symb1.setColor(uiconf.included_streets_color)
            symb1.setWidth(uiconf.street_width)
            symb2.setColor(uiconf.old_network_streets_color)
            symb2.setWidth(uiconf.street_width)
            symb3.setColor(uiconf.leastcost_streets_color)
            symb3.setWidth(uiconf.street_width)
        else:
            raise RuntimeError('Unknown sub-symbol type for setting up exclusion renderer')
        qrc0.setSymbol(symb0)
        r.setLegendSymbolItem(str(config.EXCLUDED_STATUS_VALUE), symb0)
        qrc1.setSymbol(symb1)
        r.setLegendSymbolItem(str(config.INCLUDED_STATUS_VALUE), symb1)
        qrc2.setSymbol(symb2)
        r.setLegendSymbolItem(str(config.EXISTING_STATUS_VALUE), symb2)
        qrc3.setSymbol(symb3)
        r.setLegendSymbolItem(str(config.LEASTCOST_STATUS_VALUE), symb3)
        r.addCategory(qrc0)
        r.addCategory(qrc1)
        r.addCategory(qrc2)
        r.addCategory(qrc3)
        return r

    def download_streets_from_osm(self, dock):
        print("show streets")
        # Load polygon shapefile name and check if it exists
        if not self.check_district_shapefile(dock):
            return
        self.dhc_opt.graph_builder.district = dock.lineEdit_districtShapefile.text()
        print("dhcoptimizer_planheat.py(), download_streets_from_osm(), dock.lineEdit_districtShapefile.text():",
              dock.lineEdit_districtShapefile.text())
        # Set message bar :
        self.iface.messageBar().pushMessage("Loading OSM data", "Please wait...", level=0, duration=0)
        self.iface.mainWindow().repaint()
        # Download street from OSM :
        if not self.dhc_opt.graph_builder.streets_are_imported:
            try:
                self.dhc_opt.graph_builder.import_street_graph_from_open_street_map()
            except DHCOptimizerException as e:
                e.show_in_message_bar(self.iface)
                return
        street_layer_name = self.study_suffix(uiconf.streets_layer_prefix)
        if ui_utils.has_layer(street_layer_name):
            ui_utils.remove_layers([street_layer_name])
        self.nb_streets = len(self.dhc_opt.graph_builder.street_graph.edges)
        cleaned_graph = self.dhc_opt.graph_builder.street_graph.copy()
        nodes = dict(cleaned_graph.nodes(data=True))
        cleaned_graph.remove_nodes_from(n for n in nodes if 'production' in nodes[n])
        gdf_edges = ox.save_load.graph_to_gdfs(cleaned_graph, nodes=False)
        file_name = os.path.join(self.tmp_dir, street_layer_name)
        ox.save_load.save_gdf_shapefile(gdf_edges, filename=file_name)

        self.street_layer = QgsVectorLayer(os.path.join(self.tmp_dir,
                                                        "%s/%s.shp" % (street_layer_name, street_layer_name)),
                                           street_layer_name,
                                           "ogr")
        # Set style for new layer
        self.street_layer.renderer().symbol().setColor(uiconf.included_streets_color)
        self.street_layer.renderer().symbol().setWidth(uiconf.street_width)
        self.street_layer.setOpacity(uiconf.streets_opacity)
        ui_utils.add_layer_to_group(self.street_layer, self.study_suffix(uiconf.input_layers_group_prefix))

        # Add the "Status" boolean attribute to the layer if it is not already set
        ui_utils.set_marked_field(self.street_layer, config.STATUS_KEY, config.INCLUDED_STATUS_VALUE)
        # Enable 'exclude street' button:
        dock.exclude_streets_button.setEnabled(True)
        dock.include_streets_button.setEnabled(True)
        # Enable 'leastcost street' button:
        dock.leastcost_streets_button.setEnabled(True)
        # Set labels
        self.update_streets_labels(dock)
        # update accessibility to extension mode
        self.update_extension_mode_status(dock)
        # Reset message bar
        self.iface.messageBar().clearWidgets()

    def update_street_graph_edges_least_cost(self, e, val):
        """Set the least cost value on the given edge. If given value is negative, we remove the attribute from the edge.
        TODO: to be exhaustive, we should parse a key attribute to differentiate parallel edges
        """
        graph = self.dhc_opt.graph_builder.street_graph
        for uv in [e, (e[1], e[0], *e[2:])]:
            if graph.has_edge(*uv):
                for k in graph.adj[uv[0]][uv[1]]:
                    if val < 0 and config.LEASTCOST_COEF_KEY in graph.edges[(*uv, k)]:
                        del graph.edges[(*uv, k)][config.LEASTCOST_COEF_KEY]
                    else:
                        graph.edges[(*uv, k)][config.LEASTCOST_COEF_KEY] = val

    def update_selected_streets_status(self, dock, status_value):
        # Get the current selected buildings
        selected_streets = self.street_layer.selectedFeatures()
        selected_edges = {(f['u'], f['v']) for f in selected_streets}
        # Set excluded buildings set for the optimizer
        graph_builder = self.dhc_opt.graph_builder
        if status_value == config.EXCLUDED_STATUS_VALUE:
            for e in selected_edges :
                reversed_e = (e[1], e[0])
                if e in self.dhc_opt.graph_builder.street_graph.edges():
                    graph_builder.excluded_streets.add(e)
                elif reversed_e in self.dhc_opt.graph_builder.street_graph.edges():
                    graph_builder.excluded_streets.add(reversed_e)
                self.update_street_graph_edges_least_cost(e, -1)
        elif status_value == config.INCLUDED_STATUS_VALUE:
            for e in selected_edges:
                reversed_e = (e[1], e[0])
                if e in graph_builder.excluded_streets:
                    graph_builder.excluded_streets.remove(e)
                if reversed_e in graph_builder.excluded_streets:
                    graph_builder.excluded_streets.remove(reversed_e)
                self.update_street_graph_edges_least_cost(e, -1)
        elif status_value == config.LEASTCOST_STATUS_VALUE:
            for e in selected_edges:
                self.update_street_graph_edges_least_cost(e, dock.spinBox_leastcost_coef.value())
            self.nb_leastcost_streets = len([e for e, v in
                                             nx.get_edge_attributes(graph_builder.street_graph,
                                                                    config.LEASTCOST_COEF_KEY).items() if v > 0])
        if status_value != config.EXISTING_STATUS_VALUE:
            graph_builder.old_network_streets = graph_builder.old_network_streets.difference(selected_edges)
            reversed_selected_edges = {(e[1], e[0]) for e in selected_edges}
            graph_builder.old_network_streets = graph_builder.old_network_streets.difference(reversed_selected_edges)
        # Set "Status" attribute to the new status value
        self.street_layer.startEditing()
        status_index = self.street_layer.fields().indexFromName(config.STATUS_KEY)
        for f in selected_streets:
            self.street_layer.changeAttributeValue(f.id(), status_index, status_value)
        self.street_layer.commitChanges()
        # Set categorized renderer to show which buildings have been excluded :
        current_renderer = self.street_layer.renderer()
        if not isinstance(current_renderer,
                          QgsCategorizedSymbolRenderer) or current_renderer.classAttribute() != config.STATUS_KEY:
            r = self.get_renderer('line')
            self.street_layer.setRenderer(r)
        # Remove selection :
        self.street_layer.removeSelection()
        # Update labels :
        self.update_streets_labels(dock)

    def connect_sources_old(self):
        if self.dhc_opt is None:
            self.dhc_opt = DHCOptimizer(mode=DHCOptimizer.FCFCCP, result_dir=self.result_dir,
                                        data_transfer=self.data_transfer)
        self.dhc_opt.logger.info("Generating supplies")
        self.dhc_opt.graph_builder.old_supply = self.generate_supply_gdf('old_supply')
        self.dhc_opt.graph_builder.potential_supply = self.generate_supply_gdf('potential_supply')
        self.dhc_opt.graph_builder.modify_old_network = False
        self.dhc_opt.logger.info("Generating graph")
        self.dhc_opt.graph_builder.generate_graph()
        self.dhc_opt.graph_builder.finalize_old_network_graph()

        ui_utils.refresh_layers(self.iface)

    def connect_sources(self):
        def_layer = "MultiLineString?crs=epsg:4326"
        for f in self.old_network_supply_layer.fields():
            def_layer += "&field={0}:{1}".format(f.name(), f.type())
        def_layer += "&index=yes"
        old_supply_streets = QgsVectorLayer(def_layer, "old_supply_edges_%d" % self.study_id, "memory")
        feature_list_to_add = [] 
        for point in self.old_network_supply_layer.getFeatures():
            P = point.geometry().asPoint()
            nearest_point, nearest_street, vertex_index = self.get_nearest_street_to_point(P)
            if nearest_point is None:
                continue
            new_street = [P, nearest_point]
            geom = QgsGeometry().fromPolylineXY(new_street)
            feature = QgsFeature()
            feature.setFields(self.old_network_supply_layer.fields(), True)

            feature[config.SUPPLY_POWER_CAPACITY_KEY] = point[config.SUPPLY_POWER_CAPACITY_KEY]
            feature["name"] = point["name"]
            feature.setGeometry(geom)
            feature_list_to_add.append(feature)
        
        if len(feature_list_to_add) > 0:
            old_supply_streets.startEditing()
            old_supply_streets.dataProvider().addFeatures(feature_list_to_add)
            old_supply_streets.commitChanges()
            old_supply_streets_symbol = old_supply_streets.renderer().symbol()
            old_supply_streets_symbol = old_supply_streets_symbol.createSimple({"style": "no", "line_style": "dot",
                                                            "color_border": uiconf.old_network_edges_border_color})
            old_supply_streets_symbol.setColor(uiconf.old_network_edges_color)
            old_supply_streets.renderer().setSymbol(old_supply_streets_symbol)
            ui_utils.add_layer_to_group(old_supply_streets,
                                            self.study_suffix(uiconf.input_layers_group_prefix))

    def get_nearest_street_to_point(self, P):
        """
        :param P: the point to look for the nearest street in self.street_layer
        :return: segment_distance: distance between point and the nearest street
        :return: nearest_point: nearest point on the nearest street
        :return: nearest_street: nearest street feature
        :return: vertex_index:  index of the first vertex of the nearest segment
        """
        segment_distance = None
        for street in self.street_layer.getFeatures():
            # no connection to existing connection between buildings and streets
            try:
                if street.attribute('OSM_origin') == 0:
                    continue
            except KeyError:
                pass
            try:
                if not str(street.attribute('Status')) == "2":
                    continue
            except KeyError:
                pass
            try:
                line = street.geometry().asMultiPolyline()
                if len(line) == 0:
                    line = street.geometry().asPolyline()
                    if len(line) == 0:
                        print("No way: failed to get the geometry also as Polyline.", "\n")
                        continue
                    else:
                        line = [line]
                for i in range(len(line[0]) - 1):
                    if segment_distance is None:
                        segment_distance, nearest_point = P.sqrDistToSegment(line[0][i + 1].x(), line[0][i + 1].y(),
                                                                             line[0][i].x(), line[0][i].y(), 1e-16)
                        nearest_street = street
                        vertex_index = i
                    else:
                        d, np = P.sqrDistToSegment(line[0][i + 1].x(), line[0][i + 1].y(),
                                                   line[0][i].x(), line[0][i].y(), 1e-16)
                        if d < segment_distance:
                            segment_distance = d
                            nearest_point = np
                            nearest_street = street
                            vertex_index = i
            except:
                print("Something went terribly wrong analyzing street:", street.attribute("osmid"), "\n")
        if segment_distance is None:
            return [None, None, None]
        else:
            return [nearest_point, nearest_street, vertex_index]

    def locate_sources(self, str):
        if str == 'potential_supply':
            layer = self.supply_layer
            table = self.dock.potential_sources_table
        elif str == 'old_supply':
            layer = self.old_network_supply_layer
            table = self.dock.old_sources_table
        # If supply_layer is none, create it
        if layer is None:
            # TODO : set generic crs here
            layer = QgsVectorLayer("Point?crs=epsg:4326", str + "_%d" % self.study_id, "memory")
            # Show the layer
            ui_utils.add_layer_to_group(layer, self.study_suffix(uiconf.input_layers_group_prefix))
        # Add fields :
        layer.dataProvider().addAttributes([QgsField(config.SUPPLY_NAME_KEY, QVariant.String),
                                            QgsField(config.SUPPLY_POWER_CAPACITY_KEY, QVariant.Double)])
        # Set update table when feature is added:
        if str == 'potential_supply':
            layer.featureAdded.connect(lambda fid: self.validate_potential_sources(layer, table, fid))
        elif str == 'old_supply':
            layer.featureAdded.connect(lambda fid: self.validate_old_sources(layer, table, fid))

        # Set active layer
        self.iface.setActiveLayer(layer)
        # Start editing the layer
        if not layer.isEditable():
            layer.startEditing()
        # Start new point creation tool
        self.iface.actionAddFeature().trigger()

        if str == 'potential_supply':
            self.supply_layer = layer
            self.dock.potential_sources_table = table
        elif str == 'old_supply':
            self.old_network_supply_layer = layer
            self.dock.old_sources_table = table

        # Enable validate and discard button
        if str == 'potential_supply':
            self.dock.clear_sources_button.setEnabled(True)
        elif str == 'old_supply':
            pass#self.dock.clear_old_sources_button.setEnabled(True)
        # TODO : what if layer already exists ?

        return layer

    def validate_potential_sources(self, layer, table, fid):
        # Get all supply sources in the layer and add it to the supply table
        f = layer.getFeature(fid)
        if self.supply_feature_is_not_valid(f):
            if f is not None:
                layer.deleteFeature(f.id())
            self.iface.messageBar().pushMessage("Error",
                                                "Invalid name or production capacity for the selected point.", level=1)
            return False
        self.update_table_from_layer(layer, table)
        self.nb_potential_supply = layer.featureCount()
        self.update_supply_labels()
        return True

    def supply_feature_is_not_valid(self, f):
        check = f is None
        check = check or config.SUPPLY_NAME_KEY not in f.fields().names()
        check = check or f[config.SUPPLY_NAME_KEY] is None
        check = check or str(f[config.SUPPLY_NAME_KEY]) == ""
        check = check or f[config.SUPPLY_POWER_CAPACITY_KEY] is None
        check = check or f[config.SUPPLY_POWER_CAPACITY_KEY] <= 0.0
        return check

    def validate_old_sources(self, layer, table, fid):
        # Get all supply sources in the layer and add it to the supply table
        f = layer.getFeature(fid)
        if self.supply_feature_is_not_valid(f):
            if f is not None:
                layer.deleteFeature(f.id())
            self.iface.messageBar().pushMessage("Error",
                                                "Invalid name or production capacity for the selected point.", level=1)
            return False
        #self.update_table_from_layer(layer, table)
        #self.nb_old_supply = layer.featureCount()
        #self.update_supply_labels()
        return True

    def clear_sources(self, str):
        if str == 'potential_supply':
            layer = self.supply_layer
            table = self.dock.potential_sources_table
        elif str == 'old_supply':
            layer = self.old_network_supply_layer
            table = self.dock.old_sources_table
        if layer is None:
            return
        print('Clear supplies')
        if not layer.isEditable():
            layer.startEditing()
        for f in layer.getFeatures():
            layer.deleteFeature(f.id())
        layer.commitChanges()
        self.update_table_from_layer(layer, table)
        if str == 'potential_supply':
            self.supply_layer = layer
            self.dock.potential_sources_table = table
            self.nb_potential_supply = 0
        elif str == 'old_supply':
            self.old_network_supply_layer = layer
            self.dock.old_sources_table = table
            self.nb_old_supply = 0
        self.update_supply_labels()
        total_potential_heat_production, total_existing_heat_production = self.get_total_heat_production()
        self.dock.checkBox_connect_all_buildings.setEnabled(total_potential_heat_production \
                                                        + total_existing_heat_production >= self.building_heat_demand)
        self.update_objective_number()

    def update_table_from_layer(self, layer, table):
        # Remove all items
        table.setRowCount(0)
        for f in layer.getFeatures():
            nb_rows = table.rowCount()
            table.insertRow(nb_rows)
            table.setItem(nb_rows, 0, QTableWidgetItem(f[config.SUPPLY_NAME_KEY]))
            table.setItem(nb_rows, 1, QTableWidgetItem(str(f[config.SUPPLY_POWER_CAPACITY_KEY])))

    def get_total_building_consumption(self):
        """Return the peak consumption of the considered buildings (MW). If some buildings have been excluded,
        it considers only non-excluded ones."""
        if self.building_layer is None:
            return 0
        else:
            total_demand = 0
            for f in self.building_layer.getFeatures():
                if f[config.STATUS_KEY] != 0:
                    total_demand += f[config.BUILDING_CONSUMPTION_KEY]
            total_demand *= config.BUILDING_CONSUMPTION_FACTOR_UNIT  # MW
        return total_demand

    def generate_supply_gdf(self, str):
        supply_gdf = gpd.GeoDataFrame(columns=[config.GPD_GEO_KEY, config.SUPPLY_NAME_KEY,
                                               config.SUPPLY_POWER_CAPACITY_KEY])
        if str == 'potential_supply':
            layer = self.supply_layer
        elif str == 'old_supply':
            layer = self.old_network_supply_layer
        if layer is not None:
            for f in layer.getFeatures():
                supply_gdf.loc[len(supply_gdf)] = [Point(f.geometry().asPoint()), f[config.SUPPLY_NAME_KEY],
                                                   float(f[config.SUPPLY_POWER_CAPACITY_KEY])]
        return supply_gdf

    def reset(self, dock):
        if dock == self.dock:
            self.dhc_opt = DHCOptimizer(mode=DHCOptimizer.FCFCCP)
        else:
            self.dhc_opt = DHCOptimizer(mode=DHCOptimizer.STP)
        self.dhc_opt.result_dir = self.result_dir

        self.street_layer = None
        self.building_layer = None
        if dock == self.dock:
            self.clear_sources('potential_supply')
            self.clear_sources('old_supply')
        self.supply_layer = None
        self.old_network_supply_layer = None

        self.nb_streets = 0
        self.nb_buildings = 0
        self.building_heat_demand = 0
        self.nb_leastcost_streets = 0
        self.update_objective_number()
        # dock.lineEdit_districtShapefile.clear()
        # dock.lineEdit_buildingsShapefile.clear()
        ui_utils.hide_layers([self.study_suffix(uiconf.buildings_layer_prefix),
                              self.study_suffix(uiconf.streets_layer_prefix)])
        if dock == self.dock:
            self.dock.demandCoverage.setValue(50.0)
            ui_utils.hide_layers([self.study_suffix(uiconf.supply_layer_prefix)])
            self.dock.checkBox_connected_network.setChecked(True)
            self.dock.pipe_size_calculation_button.setEnabled(False)


        ui_utils.hide_group(self.study_suffix(uiconf.study_group_prefix))
        self.selected_edges_layer = None
        self.selected_buildings_layer = None
        self.unselected_buildings_layer = None
        self.selected_supply_layer = None
        self.old_network_edges_layer = None

        self.study_id += 1
        self.init_study_tree()
        dock.exclude_streets_button.setEnabled(False)
        dock.include_streets_button.setEnabled(False)
        dock.exclude_buildings_button.setEnabled(False)
        dock.include_buildings_button.setEnabled(False)
        dock.leastcost_streets_button.setEnabled(False)
        dock.spinBox_leastcost_coef.setValue(config.LEASTCOST_COEF)
        self.update_labels(dock)
        if dock == self.dock:
            self.dock.tabWidget.setTabEnabled(dock.tabWidget.indexOf(dock.sizing_tab), False)
            self.dock.results_mGroupBox.setEnabled(False)
            self.dock.results_mGroupBox.setCollapsed(True)
            self.dock.results_NLP_mGroupBox.setEnabled(False)
            self.dock.results_NLP_mGroupBox.setCollapsed(True)
        if dock == self.manual_dock:
            self.reset_extension_mode_status(dock)

    def run_computation(self, dock):
        try:
            if not self.check_inputs(dock):
                return
            # Set message bar :
            self.iface.messageBar().pushMessage("Computing solution", "Please wait...", level=0, duration=0)
            self.iface.mainWindow().repaint()
            # Change working directory:
            initial_directory = os.getcwd()
            os.chdir(self.working_directory)
            # Get inputs
            district_shape_file = dock.lineEdit_districtShapefile.text()  # "..\\apps\\qgis\\python\\plugins\\dhcoptimizerplanheat\\data\\antwerp.shp"
            building_shape_file = dock.lineEdit_buildingsShapefile.text()  # "..\\apps\\qgis\\python\\plugins\\dhcoptimizerplanheat\\data\\Antwerp_simplified.shp"
            if dock == self.dock:
                try:
                    demand_coverage = float(self.dock.demandCoverage.value())
                except:
                    demand_coverage = 0
                # Commit changes in the supply layer if any
                # if self.supply_layer.isEditable():
                #     self.supply_layer.commitChanges()

            # Compute total building heat demand :
            if self.building_layer is None:
                self.load_building_layer(building_shape_file)
            heat_demand_objective, production_is_limiting = self.get_objective_number()

            # Print for debug :
            print("Computing arguments :")
            print("\tdistrict_shape_file=", district_shape_file)
            print("\tbuilding_shape_file=", building_shape_file)
            if dock == self.dock:
                problem = "FCFCCP"
                method = 'DSSP_Julia'
                print("\tdemand_coverage=", demand_coverage)
                print("\tobjective=", heat_demand_objective)
                print("\texcluded streets=", self.dhc_opt.graph_builder.excluded_streets)
                print("\texcluded buildings=", self.dhc_opt.graph_builder.marked_buildings)
            elif dock == self.manual_dock:
                problem = "STP"
                # ADH = average distance heuristic
                method = "ADH"
                print("\texcluded streets=", self.dhc_opt.graph_builder.excluded_streets)
                print("\tselected buildings=", self.dhc_opt.graph_builder.marked_buildings)

            # Set DHC optimizer parameters :
            self.dhc_opt.graph_builder.district = district_shape_file
            self.dhc_opt.graph_builder.buildings_file_path = building_shape_file
            self.dhc_opt.network_optimizer.method = method
            if dock == self.dock:
                self.dhc_opt.graph_builder.potential_supply = self.generate_supply_gdf('potential_supply')
                self.dhc_opt.graph_builder.old_supply = self.generate_supply_gdf('old_supply')
                self.dhc_opt.network_optimizer.network_objective = heat_demand_objective
                self.dhc_opt.network_optimizer.connected = self.dock.checkBox_connected_network.isChecked()
                self.dhc_opt.graph_builder.modify_old_network = self.dock.modify_existing_network_button.isChecked()
                self.dhc_opt.network_optimizer.modify_old_network = self.dock.modify_existing_network_button.isChecked()
            self.dhc_opt.verbose = 3
            
            self.dhc_opt.run()

            self.show_solution(dock)

            if dock == self.dock:
                self.dock.pipe_size_calculation_button.setEnabled(True)

            # Reset working directory
            os.chdir(initial_directory)
            # Reset message bar
            self.iface.messageBar().clearWidgets()
        except DHCOptimizerException as e:
            e.show_in_message_bar(self.iface)

    def show_solution(self, dock):
        # Get resulting shapefiles
        if dock == self.dock:
            selected_edges_path = os.path.join(self.result_dir, config.SOLUTION_DISTRICT_EDGES_FILE)
        else:
            selected_edges_path = os.path.join(self.result_dir, config.SOLUTION_STP_EDGES_FILE)
        if not os.path.exists(selected_edges_path):
            raise RuntimeError("Impossible to find the solution file at path: '%s'" % str(selected_edges_path))

        if ui_utils.has_layer("selected_edges_%d" % self.study_id):
            ui_utils.remove_layers(["selected_edges_%d" % self.study_id])
        self.selected_edges_layer = QgsVectorLayer(selected_edges_path, "selected_edges_%d" % self.study_id, "ogr")
        # Set styles for new layers
        if dock == self.dock:
            r = QgsGraduatedSymbolRenderer(config.SOLUTION_POWER_FLOW_KEY)
            r.setGraduatedMethod(QgsGraduatedSymbolRenderer.GraduatedSize)
            r.updateClasses(self.selected_edges_layer, QgsGraduatedSymbolRenderer.EqualInterval, 10)
            r.setSymbolSizes(0.26, 1.0)
            s = QgsLineSymbol().createSimple({"color_border": uiconf.solution_flow_border_color})
            s.setColor(uiconf.solution_flow_color)
            r.updateSymbols(s)
            self.selected_edges_layer.setRenderer(r)
        else:
            edge_layer_symbol = self.selected_edges_layer.renderer().symbol()
            self.selected_edges_layer.renderer().setSymbol(
                edge_layer_symbol.createSimple({"color_border": uiconf.solution_flow_border_color}))
            self.selected_edges_layer.renderer().symbol().setColor(uiconf.solution_flow_color)
        self.selected_edges_layer.setOpacity(uiconf.solution_flow_opacity)
        ui_utils.add_layer_to_group(self.selected_edges_layer, self.study_suffix(uiconf.output_layers_group_prefix))

        if dock == self.dock:
            # selected buildings
            if ui_utils.has_layer("selected_buildings_%d" % self.study_id):
                ui_utils.remove_layers(["selected_buildings_%d" % self.study_id])
            self.selected_buildings_layer = QgsVectorLayer(
                os.path.join(self.result_dir, config.SELECTED_BUILDINGS_FILE),
                "selected_buildings_%d" % self.study_id, "ogr")
            self.selected_buildings_layer.renderer().symbol().setColor(uiconf.selected_buildings_color)
            self.selected_buildings_layer.setOpacity(uiconf.selected_buildings_opacity)
            ui_utils.add_layer_to_group(self.selected_buildings_layer,
                                        self.study_suffix(uiconf.output_layers_group_prefix))
            
            # unselected buildings
            if ui_utils.has_layer("unselected_buildings_%d" % self.study_id):
                ui_utils.remove_layers(["unselected_buildings_%d" % self.study_id])
            self.unselected_buildings_layer = QgsVectorLayer(os.path.join(self.result_dir,
                                                                          config.UNSELECTED_BUILDINGS_FILE),
                                                             "unselected_buildings_%d" % self.study_id, "ogr")
            self.unselected_buildings_layer.renderer().symbol().setColor(uiconf.unselected_buildings_color)
            self.unselected_buildings_layer.setOpacity(uiconf.unselected_buildings_opacity)
            ui_utils.add_layer_to_group(self.unselected_buildings_layer,
                                        self.study_suffix(uiconf.output_layers_group_prefix))

            # supply
            if ui_utils.has_layer("solution_supply_%d" % self.study_id):
                ui_utils.remove_layers(["solution_supply_%d" % self.study_id])
            solution_supply_path = os.path.join(self.result_dir, config.SOLUTION_SUPPLY_EDGES_FILE)
            self.selected_supply_layer = QgsVectorLayer(solution_supply_path,
                                                        "solution_supply_%d" % self.study_id, "ogr")
            supply_layer_symbol = self.selected_supply_layer.renderer().symbol()
            supply_layer_symbol = supply_layer_symbol.createSimple({"style": "no", "line_style": "dot",
                                                                    "color_border": uiconf.solution_flow_border_color})
            supply_layer_symbol.setColor(uiconf.solution_flow_color)
            self.selected_supply_layer.renderer().setSymbol(supply_layer_symbol)
            ui_utils.add_layer_to_group(self.selected_supply_layer,
                                        self.study_suffix(uiconf.output_layers_group_prefix))

            # old supply
            if self.dhc_opt.graph_builder.old_network_graph is not None:
                if ui_utils.has_layer("solution_old_supply_%d" % self.study_id):
                    ui_utils.remove_layers(["solution_old_supply_%d" % self.study_id])
                solution_old_supply_path = os.path.join(self.result_dir, config.SOLUTION_OLD_SUPPLY_EDGES_FILE)
                self.selected_old_supply_layer = QgsVectorLayer(solution_old_supply_path,
                                                            "solution_old_supply_%d" % self.study_id, "ogr")          
                old_supply_layer_symbol = self.selected_old_supply_layer.renderer().symbol()
                old_supply_layer_symbol = old_supply_layer_symbol.createSimple({"style": "no", "line_style": "dot",
                                                                        "color_border": uiconf.old_network_edges_border_color})
                old_supply_layer_symbol.setColor(uiconf.old_network_edges_color)
                self.selected_old_supply_layer.renderer().setSymbol(old_supply_layer_symbol)
                ui_utils.add_layer_to_group(self.selected_old_supply_layer,
                                            self.study_suffix(uiconf.output_layers_group_prefix))

            # Hide all the buildings layer
            if "Single" in type(self.building_layer.renderer()).__name__:
                ui_utils.hide_layers([self.study_suffix(uiconf.buildings_layer_prefix)])
            # Hide all the buildings layer a part from old network
            if "Categorized" in type(self.building_layer.renderer()).__name__:
                #self.building_layer.renderer().checkLegendSymbolItem(str(config.EXCLUDED_STATUS_VALUE), False)
                self.building_layer.renderer().checkLegendSymbolItem(str(config.INCLUDED_STATUS_VALUE), False)
                self.building_layer.renderer().checkLegendSymbolItem(str(config.LEASTCOST_STATUS_VALUE), False)

        # Hide all the street layer
        ui_utils.hide_layers([self.study_suffix(uiconf.streets_layer_prefix)])

        # Show results in the result tab
        self.show_solution_in_result_tab(dock)
        ui_utils.refresh_layers(self.iface)

    def show_pipe_size_solution(self, dock, only_preprocess, success):

        # Remove old selected edges layer (rebuilt after)
        ui_utils.remove_layers([self.study_suffix(uiconf.selected_edges_layer_prefix),
        						self.study_suffix(uiconf.solution_supply_layer_prefix)])

        if self.old_network_edges_layer is not None and self.dhc_opt.graph_builder.modify_old_network:
            ui_utils.hide_layers(["old_network_edges_%d" % self.study_id])

        # Get resulting shapefiles
        if dock == self.dock:
            selected_edges_path = os.path.join(self.result_dir, config.SOLUTION_DISTRICT_EDGES_FILE)
        else:
            selected_edges_path = os.path.join(self.result_dir, config.SOLUTION_STP_EDGES_FILE)
        if not os.path.exists(selected_edges_path):
            raise RuntimeError("Impossible to find the solution file at path: '%s'" % str(selected_edges_path))

        # supply layer
        solution_supply_path = os.path.join(self.result_dir, config.SOLUTION_SUPPLY_EDGES_FILE)
        self.selected_supply_layer = QgsVectorLayer(solution_supply_path, "solution_supply_%d" % self.study_id, "ogr")
        supply_layer_symbol = self.selected_supply_layer.renderer().symbol()
        supply_layer_symbol = supply_layer_symbol.createSimple({"style": "no", "line_style": "dot", 
        														"color_border": uiconf.solution_flow_border_color})
        supply_layer_symbol.setColor(uiconf.solution_flow_color)
        self.selected_supply_layer.renderer().setSymbol(supply_layer_symbol)
        ui_utils.add_layer_to_group(self.selected_supply_layer, self.study_suffix(uiconf.output_layers_group_prefix))

        # diameter layer
        if ui_utils.has_layer("diameter_pipes_%d" % self.study_id):
            ui_utils.remove_layers(["diameter_pipes_%d" % self.study_id])
        self.diameter_layer = QgsVectorLayer(selected_edges_path, "diameter_pipes_%d" % self.study_id, "ogr")
        r = QgsGraduatedSymbolRenderer(config.PIPE_DIAMETER_KEY)
        r.setGraduatedMethod(QgsGraduatedSymbolRenderer.GraduatedSize)
        r.updateClasses(self.diameter_layer, QgsGraduatedSymbolRenderer.EqualInterval, 10)
        r.setSymbolSizes(0.26, 1.0)
        s = QgsLineSymbol().createSimple({"color_border": uiconf.solution_diameter_border_color})
        s.setColor(uiconf.solution_diameter_color)
        r.updateSymbols(s)
        self.diameter_layer.setRenderer(r)
        self.diameter_layer.setOpacity(uiconf.solution_diameter_opacity)
        ui_utils.add_layer_to_group(self.diameter_layer, self.study_suffix(uiconf.output_layers_group_prefix))

        if not only_preprocess and success:
            # flow layer
            if ui_utils.has_layer("flow_in_pipes_%d" % self.study_id):
                ui_utils.remove_layers(["flow_in_pipes_%d" % self.study_id])
            self.flow_layer = QgsVectorLayer(selected_edges_path, "flow_in_pipes_%d" % self.study_id, "ogr")
            # Set styles for new layers
            r = QgsGraduatedSymbolRenderer(config.SOLUTION_POWER_FLOW_KEY)
            r.setGraduatedMethod(QgsGraduatedSymbolRenderer.GraduatedSize)
            r.updateClasses(self.flow_layer, QgsGraduatedSymbolRenderer.EqualInterval, 10)
            r.setSymbolSizes(0.26, 1.0)
            s = QgsLineSymbol().createSimple({"color_border": uiconf.solution_flow_border_color})
            s.setColor(uiconf.solution_flow_color)
            r.updateSymbols(s)
            self.flow_layer.setRenderer(r)
            self.flow_layer.setOpacity(uiconf.solution_flow_opacity)
            ui_utils.add_layer_to_group(self.flow_layer, self.study_suffix(uiconf.output_layers_group_prefix))

            # pressure layer
            if ui_utils.has_layer("pressure_in_pipes_%d" % self.study_id):
                ui_utils.remove_layers(["pressure_in_pipes_%d" % self.study_id])
            self.pressure_layer = QgsVectorLayer(selected_edges_path, "pressure_in_pipes_%d" % self.study_id, "ogr")
            r = QgsGraduatedSymbolRenderer(config.AVERAGE_PRESSURE_KEY)
            r.setGraduatedMethod(QgsGraduatedSymbolRenderer.GraduatedSize)
            r.updateClasses(self.pressure_layer, QgsGraduatedSymbolRenderer.EqualInterval, 10)
            r.setSymbolSizes(0.26, 1.0)
            s = QgsLineSymbol().createSimple({"color_border": uiconf.solution_pressure_border_color})
            s.setColor(uiconf.solution_pressure_color)
            r.updateSymbols(s)
            self.pressure_layer.setRenderer(r)
            self.pressure_layer.setOpacity(uiconf.solution_pressure_opacity)
            ui_utils.add_layer_to_group(self.pressure_layer, self.study_suffix(uiconf.output_layers_group_prefix))

            # we don't show them by default
            ui_utils.hide_layers([self.study_suffix(uiconf.pressure_layer_prefix), self.study_suffix(uiconf.flow_layer_prefix)])

            # Show results in the result tab
            self.show_pipe_size_solution_in_result_tab(dock)


    def pipe_size_calculation(self, dock, only_preprocess = False):
        self.iface.messageBar().pushMessage("Pipe size calculation", "Please wait...", level=0, duration=0)
        self.iface.mainWindow().repaint()
        if dock == self.dock:
            if self.dock.radioButton_Heating.isChecked():
                self.dhc_opt.network_optimizer.energy = 'Heating'
            elif self.dock.radioButton_Cooling.isChecked():
                self.dhc_opt.network_optimizer.energy = 'Cooling'
            else: 
                raise ValueError("The user needs to choose either Heating or Cooling")
            self.dhc_opt.network_optimizer.conf["MIN_PRESSURE"] = self.dock.doubleSpinBox_min_P.value()
            self.dhc_opt.network_optimizer.conf["MAX_PRESSURE"] = self.dock.doubleSpinBox_max_P.value()
            self.dhc_opt.network_optimizer.conf["MIN_DIAMETER"] = self.dock.spinBox_min_D.value()
            self.dhc_opt.network_optimizer.conf["MAX_DIAMETER"] = self.dock.spinBox_max_D.value()
            success = self.dhc_opt.run_NLP(only_preprocess)
            self.show_pipe_size_solution(dock, only_preprocess, success)
        self.iface.messageBar().clearWidgets()

    def show_solution_in_result_tab(self, dock):
        if dock == self.dock:
            # Get and print total covered consumption
            total_covered_consumption = float(
                sum(f[config.BUILDING_CONSUMPTION_KEY] for f in self.selected_buildings_layer.getFeatures()))
            self.dock.total_covered_consumption_int_label.setText("%.0f MW" % (total_covered_consumption / 1000))
            # Get and print number of used sources
            nb_sources = self.selected_supply_layer.featureCount()
            self.dock.nb_used_sources_int_label.setText(str(nb_sources))
        # Get and print number of selected buildings:
        if dock == self.dock:
            nb_buildings = self.selected_buildings_layer.featureCount()
        elif dock == self.manual_dock:
            nb_buildings = int(self.manual_dock.nb_buildings_int_label.text())
        dock.nb_selected_buildings_int_label.setText(str(nb_buildings))
        # Get and print the length of the pipes
        total_pipe_length = sum(float(f[config.EDGE_LENGTH_KEY]) for f in self.selected_edges_layer.getFeatures())
        dock.total_pipe_length_int_label.setText("%d meters" % int(total_pipe_length))
        # Get and print the length of the pipes for reduced cost street
        total_leastcost_pipe_length = self.get_total_leastcost_pipe_length()
        dock.total_leastcost_length_int_label.setText("%d meters" % int(total_leastcost_pipe_length))
        # Activate result tab
        if dock == self.dock:
            self.dock.tabWidget.setTabEnabled(self.dock.tabWidget.indexOf(self.dock.sizing_tab), True)
        else:
            dock.tabWidget.setTabEnabled(dock.tabWidget.indexOf(dock.results_tab), True)
        if dock == self.dock:
            self.dock.results_mGroupBox.setEnabled(True)
            self.dock.results_mGroupBox.setCollapsed(False)

    def show_pipe_size_solution_in_result_tab(self, dock):
        dock.min_diameter_int_label.setText("%g cm" % min([float(f[config.PIPE_DIAMETER_KEY]) for f in self.diameter_layer.getFeatures() \
                                                                if f[config.EDGE_LENGTH_KEY] > 0]))
        dock.max_diameter_int_label.setText("%g cm" % max([float(f[config.PIPE_DIAMETER_KEY]) for f in self.diameter_layer.getFeatures() \
                                                                if f[config.EDGE_LENGTH_KEY] > 0]))
        dock.min_pressure_int_label.setText("%g Bar" % min([float(f[config.AVERAGE_PRESSURE_KEY]) for f in self.pressure_layer.getFeatures() \
                                                                if f[config.EDGE_LENGTH_KEY] > 0]))
        dock.max_pressure_int_label.setText("%g Bar" % max([float(f[config.AVERAGE_PRESSURE_KEY]) for f in self.pressure_layer.getFeatures() \
                                                                if f[config.EDGE_LENGTH_KEY] > 0]))

        energy = self.dhc_opt.network_optimizer.energy
        #dock.construction_cost_int_label.setText("%d €" % sum([float(f[config.CONSTRUCTION_COST_KEY]) for f in self.pressure_layer.getFeatures() \
        #                                                        if f[config.EDGE_LENGTH_KEY] > 0]))
        #if energy == "Heating":
        #    dock.hl_cost_int_label.setText("%d €" % sum([float(f[config.HEAT_LOSS_COST_KEY]) for f in self.pressure_layer.getFeatures() \
        #                                                        if f[config.EDGE_LENGTH_KEY] > 0]))
        #if energy == "Cooling":
        #    dock.hl_cost_int_label.setText("%d €" % sum([float(f[config.COOL_LOSS_COST_KEY]) for f in self.pressure_layer.getFeatures() \
        #                                                        if f[config.EDGE_LENGTH_KEY] > 0]))
        #    dock.hl_cost_int_label.setText("Cool Loss Cost:")
        #dock.pumping_cost_int_label.setText("%d €" % sum([float(f[config.PUMPING_COST_KEY]) for f in self.selected_supply_layer.getFeatures() \
        #                                                        if f[config.EDGE_LENGTH_KEY] > 0]))

        dock.min_pressure_int_label.setEnabled(True)
        dock.max_pressure_int_label.setEnabled(True)
        dock.min_diameter_int_label.setEnabled(True)
        dock.max_diameter_int_label.setEnabled(True)
        #dock.construction_cost_int_label.setEnabled(True)
        #dock.hl_cost_int_label.setEnabled(True)
        #dock.pumping_cost_int_label.setEnabled(True)
        dock.min_pressure_label.setEnabled(True)
        dock.max_pressure_label.setEnabled(True)
        dock.min_diameter_label.setEnabled(True)
        dock.max_diameter_label.setEnabled(True)
        #dock.construction_cost_label.setEnabled(True)
        #dock.hl_cost_label.setEnabled(True)
        #dock.pumping_cost_label.setEnabled(True)


        if dock == self.dock:
            self.dock.results_NLP_mGroupBox.setEnabled(True)
            self.dock.results_NLP_mGroupBox.setCollapsed(False)


    def update_objective_number(self):
        if self.dock.checkBox_connect_all_buildings.isChecked():
            self.dock.demandCoverage.setValue(100.0)
            self.dock.demandCoverage.setEnabled(False)
        else:
            self.dock.demandCoverage.setEnabled(True)
        total_objective_number, production_is_limiting = self.get_objective_number()
        self.dock.future_number_label.setText("(%.1f MW)" % total_objective_number)
        if production_is_limiting:  # Set the maximum objective value on the spinbox
            max_objective_val = min(max(0.0, total_objective_number / self.building_heat_demand * 100), 100.0)
            self.dock.demandCoverage.setValue(max_objective_val)

    def get_objective_number(self):
        """Return the objective number and a boolean indicating if the the production is limiting the objective."""
        if self.dock.checkBox_connect_all_buildings.isChecked():
            heat_demand_objective = self.building_heat_demand
        else:
            try:
                demand_coverage_value = float(self.dock.demandCoverage.value())
            except:
                demand_coverage_value = 0
            heat_demand_objective = self.building_heat_demand * demand_coverage_value / 100
        total_potential, total_existing = self.get_total_heat_production()
        total_production = total_potential + total_existing
        if heat_demand_objective <= total_production:
            return heat_demand_objective, False
        else:
            return total_production, True

    def get_total_leastcost_pipe_length(self):
        total_leastcost_pipe_length = 0
        for f in self.selected_edges_layer.getFeatures():
            if float(f[config.LEASTCOST_COEF_KEY]) > 0:
                total_leastcost_pipe_length += float(f[config.EDGE_LENGTH_KEY])
        return total_leastcost_pipe_length

    def update_streets_labels(self, dock):
        nb_excluded = len(self.dhc_opt.graph_builder.excluded_streets)
        dock.nb_streets_int_label.setText(str(self.nb_streets - nb_excluded))
        dock.nb_excluded_streets_int_label.setText(str(nb_excluded))
        dock.nb_leastcost_streets_int_label.setText(str(self.nb_leastcost_streets))


    def update_buildings_labels(self, dock):
        if dock == self.dock:
            nb_excluded = len(self.dhc_opt.graph_builder.marked_buildings)
            self.dock.nb_buildings_int_label.setText(str(self.nb_buildings - nb_excluded))
            self.dock.nb_excluded_buildings_int_label.setText(str(nb_excluded))
            self.building_heat_demand = self.get_total_building_consumption()
            self.dock.buildings_consumption_label.setText("(%.1f MW)" % self.building_heat_demand)
            self.update_objective_number()
        elif dock == self.manual_dock:
            nb_added = len(self.dhc_opt.graph_builder.marked_buildings)
            self.manual_dock.nb_buildings_int_label.setText(str(nb_added))

    def update_supply_labels(self):
        self.dock.nb_potential_supply_int_label.setText(str(self.nb_potential_supply))
        self.dock.nb_old_supply_int_label.setText(str(self.dock.old_sources_table.rowCount()-1)) # self.nb_old_supply
        total_potential_heat_production, total_existing_heat_production = self.get_total_heat_production()
        self.dock.total_energy_supply_int_label.setText("%.0f MW" % total_potential_heat_production)
        self.dock.total_old_supply_future_int_label.setText("%.0f MW" % total_existing_heat_production)
        self.dock.checkBox_connect_all_buildings.setEnabled(total_potential_heat_production \
                                                        + total_existing_heat_production >= self.building_heat_demand)
        self.update_objective_number()
        self.update_future_capacity()

    def update_future_capacity(self):
        for i in range(1, self.dock.old_sources_table.rowCount()):
            try:
                future_capacity = float(self.dock.old_sources_table.cellWidget(i, 2).toPlainText())
            except:
                future_capacity = float(self.dock.old_sources_table.item(i, 1).text())
            supply_name = self.dock.old_sources_table.item(i, 0).text()
            try:
                capacity_index = [f.name() for f in self.old_network_supply_layer.fields()]\
                            .index(config.SUPPLY_POWER_CAPACITY_KEY)
                self.old_network_supply_layer.startEditing()
                for feat in self.old_network_supply_layer.getFeatures():
                    if feat[config.SUPPLY_NAME_KEY] == supply_name:
                        self.old_network_supply_layer.changeAttributeValue(feat.id(), capacity_index, future_capacity)
                try:
                    capacity_index = [f.name() for f in self.old_network_supply_layer.fields()]\
                                .index(config.SUPPLY_POWER_CAPACITY_KEY[:10])
                    self.old_network_supply_layer.renameAttribute(capacity_index, config.SUPPLY_POWER_CAPACITY_KEY)
                except:
                    pass
                self.old_network_supply_layer.commitChanges()
            except:
                pass

    def update_baseline_capacity(self):
        baseline_coverage, baseline_total_demand = 0, 0

        if self.building_layer is not None and self.data_transfer.baseline_scenario is not None:
            old_network_buildings = {b[config.BUILDING_ID_KEY] for b in self.building_layer.getFeatures()\
                                        if b[config.STATUS_KEY] == config.EXISTING_STATUS_VALUE}
            for feature in self.data_transfer.baseline_scenario.getFeatures():
                baseline_total_demand += feature[config.BUILDING_MAX_HEAT_DEM_KEY]\
                                            *config.BUILDING_CONSUMPTION_FACTOR_UNIT
                if feature[config.BUILDING_ID_KEY] in old_network_buildings:
                    baseline_coverage += feature[config.BUILDING_MAX_HEAT_DEM_KEY]\
                                            *config.BUILDING_CONSUMPTION_FACTOR_UNIT

        if baseline_total_demand != 0:
            self.dock.baseline_percent_label.setText(str(int(100*baseline_coverage/baseline_total_demand)))
        self.dock.baseline_number_label.setText("(%.1f MW)" % float(baseline_coverage))


    def get_total_heat_production(self, baseline_total=False):
        total_potential_heat_production, total_existing_heat_production = 0, 0
        total_existing_heat_production_baseline = 0
        if self.supply_layer is not None:
            total_potential_heat_production += sum(
                [float(self.dock.potential_sources_table.item(i, 1).text()) for i in
                 range(self.dock.potential_sources_table.rowCount())])
        for i in range(1, self.dock.old_sources_table.rowCount()):
            try:
                total_existing_heat_production += \
                float(self.dock.old_sources_table.cellWidget(i, 2).toPlainText())
            except:
                pass
        if baseline_total:
            for i in range(1, self.dock.old_sources_table.rowCount()):
                try:
                    total_existing_heat_production_baseline += \
                    float(self.dock.old_sources_table.item(i, 1).text())
                except:
                    pass
        
        if baseline_total:
            return [total_potential_heat_production, 
            total_existing_heat_production, 
            total_existing_heat_production_baseline]
        return total_potential_heat_production, total_existing_heat_production

    def update_labels(self, dock):
        self.update_streets_labels(dock)
        self.update_buildings_labels(dock)
        self.update_supply_labels()

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog menu
        if self.data_transfer is not None and self.data_transfer.step1_mode:
            pass
        else:
            self.dialog_menu.show()
            # Run the dialog event loop
            result = self.dialog_menu.exec_()
            if not result:
                return
            # Create layers tree
        print("dhcoptimizer_planheat.py, run(): starting init_study_tree()")
        self.init_study_tree()
        if self.data_transfer.automatic_upload_network:
            self.set_up_old_supplies(self.data_transfer.network.save_file_path[:-4]+".shp")
        if self.dialog_menu.radioButton_1_auto.isChecked():
            # show the dialog
            if self.data_transfer is not None and self.data_transfer.step1_mode:
                pass
            else:
                self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
            self.dhc_opt = DHCOptimizer(mode=DHCOptimizer.FCFCCP, result_dir=self.result_dir,
                                        data_transfer=self.data_transfer)
            print("dhcoptimizer_planheat.py, run(): forcing buttons for atuomatic mode")
            self.force_button_clicking(self.dock)
        else:
            if self.data_transfer is not None and self.data_transfer.step1_mode:
                pass
            else:
                self.iface.addDockWidget(Qt.RightDockWidgetArea, self.manual_dock)
            self.dhc_opt = DHCOptimizer(mode=DHCOptimizer.STP, result_dir=self.result_dir,
                                        data_transfer=self.data_transfer)
            print("dhcoptimizer_planheat.py, run(): forcing buttons for manual mode")
            self.force_button_clicking(self.manual_dock)
        self.set_up_logger()

    def force_button_clicking(self, dock):
        dock.geography_group.hide()
        dock.Extension_mGroupBox.hide()
        if self.data_transfer.ready_check():
            if dock == self.manual_dock:
                self.data_transfer.dock_type = "manual"
            else:
                self.data_transfer.dock_type = "automatic"
            print("dhcoptimizer_planheat.py, force_button_clicking(): dock.download_street_button.clicked.emit()")
            dock.download_street_button.clicked.emit()
            print("dhcoptimizer_planheat.py, force_button_clicking(): dock.show_buildings_button.clicked.emit()")
            dock.show_buildings_button.clicked.emit()
            dock.download_street_button.setEnabled(False)
            dock.show_buildings_button.setEnabled(False)
            dock.geography_group.setEnabled(False)

            layers = QgsProject.instance().mapLayersByName(
                uiconf.buildings_layer_prefix + str(self.data_transfer.study_id))
            if len(layers) < 1:
                print("dhcoptimizer_planheat.py, force_button_clicking(). WARNING: no layers found!")
            if len(layers) > 1:
                print("dhcoptimizer_planheat.py, force_button_clicking(). WARNING: found more then one layer!")
            if len(layers) > 0:
                layer = layers[0]
                selection = []
                if self.data_transfer.network.buildings_layer is not None:
                    for feature_scenario in layer.getFeatures():
                        print("building in baseline scenario:", feature_scenario.attribute("BuildingID"))
                        for feature_network in self.data_transfer.network.buildings_layer.getFeatures():
                            if feature_scenario.attribute("BuildingID") == feature_network.attribute("BuildingID"):
                                break
                        else:
                            if feature_scenario.id() not in selection:
                                selection.append(feature_scenario.id())
                print("selection", selection)
                layer.modifySelection(selection, [])
                dock.exclude_buildings_button.clicked.emit()

            self.data_transfer.nb_selected_buildings_int_label = dock.nb_selected_buildings_int_label
            self.data_transfer.total_pipe_length_int_label = dock.total_pipe_length_int_label
            self.data_transfer.total_leastcost_length_int_label = dock.total_leastcost_length_int_label

            try:
                self.data_transfer.nb_used_sources_int_label = dock.nb_used_sources_int_label
            except AttributeError:
                pass
            try:
                self.data_transfer.total_covered_consumption_int_label = dock.total_covered_consumption_int_label
            except AttributeError:
                pass

            if dock == self.manual_dock:
                dock.lineEdit_existingNetworkShapefile.setText(self.data_transfer.network.save_file_path)
                print("save_file_path received:", self.data_transfer.network.save_file_path)
                dock.lineEdit_existingNetworkShapefile.setEnabled(False)
                dock.toolButton_existingNetworkShapefile.setEnabled(False)
                dock.save_existing_network_button.setEnabled(False)
                dock.save_existing_network_button.setToolTip("This network will be automatically saved on exit!")
                dock.save_existing_network_button.setToolTipDuration(10000)
                dock.add_existing_network_button.setEnabled(False)
                dock.add_existing_network_button.setToolTip("If present, network was already automatically loaded!")
                dock.add_existing_network_button.setToolTipDuration(10000)
                if self.data_transfer.automatic_upload_network:
                    print("data_transfer.automatic_upload_network was found to be TRUE")
                    dock.add_existing_network_button.clicked.emit()

            if dock == self.dock:
                dock.add_old_buildings_button.setEnabled(False)
                dock.add_old_streets_button.setEnabled(False)
                dock.generate_existing_network_button.setEnabled(False)
                dock.save_existing_network_button.setEnabled(False)
                dock.lineEdit_existingNetworkShapefile.setEnabled(False)
                dock.toolButton_existingNetworkShapefile.setEnabled(False)
                dock.add_existing_network_button.setEnabled(False)
                # dock.geography_group.hide()
                # dock.Extension_mGroupBox.hide()
                if self.data_transfer.automatic_upload_network:
                    dock.lineEdit_existingNetworkShapefile.setText(self.data_transfer.network.save_file_path)
                    dock.add_existing_network_button.clicked.emit()
                dock.Extension_mGroupBox.hide()

    def set_up_logger(self):
        class Printer:
            def write(self, x):
                print(x)

        self.dhc_opt.logger = logging.getLogger()
        self.dhc_opt.logger.setLevel(logging.INFO)

        output_stream = sys.stdout if sys.stdout is not None else Printer()
        stream_handler = logging.StreamHandler(output_stream)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        self.dhc_opt.logger.addHandler(stream_handler)

    # Extension mode
    def update_extension_mode_status(self, dock):
        if dock == self.manual_dock:
            dock.Extension_mGroupBox.setEnabled(self.building_layer is not None and self.street_layer is not None)
        return

    def reset_extension_mode_status(self, dock):
        dock.Extension_mGroupBox.setEnabled(False)
        self.dhc_opt.graph_builder.old_network_buildings = set()
        self.dhc_opt.graph_builder.old_network_streets = set()

    def add_old_network_buildings(self, dock):
        if not dock.Extension_mGroupBox.isEnabled():
            return
        # Get the current selected buildings
        selected_buildings = self.building_layer.selectedFeatures()
        # Set buildings belonging to the old network
        self.dhc_opt.graph_builder.old_network_buildings = self.dhc_opt.graph_builder.old_network_buildings.union(
            {f.attribute(config.BUILDING_ID_KEY) for f in selected_buildings})
        self.dhc_opt.graph_builder.marked_buildings = self.dhc_opt.graph_builder.marked_buildings.union(
            {f.attribute(config.BUILDING_ID_KEY) for f in selected_buildings})
        # Set "Status" attribute to 2 for selected buildings
        self.building_layer.startEditing()
        status_index = self.building_layer.fields().indexFromName(config.STATUS_KEY)
        for b in selected_buildings:
            # Every building belonging to the old network has to be Included
            self.building_layer.changeAttributeValue(b.id(), status_index, config.EXISTING_STATUS_VALUE)
        self.building_layer.commitChanges()
        # Set categorized renderer to show which buildings have been excluded :
        current_renderer = self.building_layer.renderer()
        if not isinstance(current_renderer,
                          QgsCategorizedSymbolRenderer) or current_renderer.classAttribute() != config.STATUS_KEY:
            r = self.get_renderer('fill')
            self.building_layer.setRenderer(r)
        # Remove selection :
        self.building_layer.removeSelection()
        self.update_buildings_labels(dock)

    def add_old_network_streets(self, dock):
        print("dhcoptimizer_planheat.py, add_old_network_streets(): add_old_network_streets fired!, "
              "self.street_layer.name() =", self.street_layer.name())
        if not dock.Extension_mGroupBox.isEnabled():
            return
        # Get the current selected streets
        print("dhcoptimizer_planheat.py, add_old_network_streets(): add_old_network_streets working!")
        selected_streets = self.street_layer.selectedFeatures()
        # Set streets belonging to the old network
        self.dhc_opt.graph_builder.old_network_streets = self.dhc_opt.graph_builder.old_network_streets.union(
            {(f['u'], f['v']) for f in selected_streets})
        # Set "Status" attribute to 2 for selected streets
        self.street_layer.startEditing()
        status_index = self.street_layer.fields().indexFromName(config.STATUS_KEY)
        for b in selected_streets:
            # Every building belonging to the old network has to be Included
            self.street_layer.changeAttributeValue(b.id(), status_index, config.EXISTING_STATUS_VALUE)
        self.street_layer.commitChanges()
        # Set categorized renderer to show which buildings have been excluded :
        current_renderer = self.street_layer.renderer()
        if not isinstance(current_renderer,
                          QgsCategorizedSymbolRenderer) or current_renderer.classAttribute() != config.STATUS_KEY:
            r = self.get_renderer('line')
            self.street_layer.setRenderer(r)
        # Remove selection :
        self.street_layer.removeSelection()

        self.data_transfer.pipes_list.update_pipes(self.street_layer)

    def show_existing_network(self, dock):
        if not dock.Extension_mGroupBox.isEnabled():
            return
        old_network_streets = self.dhc_opt.graph_builder.old_network_streets
        old_network_buildings = self.dhc_opt.graph_builder.old_network_buildings
        if len(old_network_streets) == 0 or len(old_network_buildings) == 0:
            return
        if ui_utils.has_layer("old_network_edges_%d" % self.study_id):
            ui_utils.remove_layers(["old_network_edges_%d" % self.study_id])
        self.dhc_opt.graph_builder.district = dock.lineEdit_districtShapefile.text()
        self.dhc_opt.graph_builder.buildings_file_path = dock.lineEdit_buildingsShapefile.text()
        if dock == self.dock:
            self.dhc_opt.get_old_network_graph(problem='FCFCCP')
        else:
            self.dhc_opt.get_old_network_graph(problem='STP')

        
        # Get the resulting shapefile
        old_network_path = os.path.join(self.result_dir, "old_network_edges/old_network_edges.shp")
        self.old_network_edges_layer = QgsVectorLayer(old_network_path,
                                                          "old_network_edges_%d" % self.study_id, "ogr")
        # Set styles for new layers
        edge_layer_symbol = self.old_network_edges_layer.renderer().symbol()
        new_symbol = edge_layer_symbol.createSimple({"color_border": uiconf.old_network_edges_border_color})
        self.old_network_edges_layer.renderer().setSymbol(new_symbol)
        self.old_network_edges_layer.renderer().symbol().setColor(uiconf.old_network_edges_color)
        self.old_network_edges_layer.setOpacity(uiconf.old_network_edges_opacity)
        ui_utils.add_layer_to_group(self.old_network_edges_layer,
                                    self.study_suffix(uiconf.input_layers_group_prefix))

    def save_pipe_capacities(self):
        if self.temp_layer.isEditable():
            self.temp_layer.commitChanges()
        print(dict(self.dhc_opt.graph_builder.old_network_graph.nodes))
        self.dhc_opt.save_old_network_with_capacities()
        print(dict(self.dhc_opt.graph_builder.old_network_graph.nodes))

        ui_utils.remove_layers(["tmp_%d" % self.study_id])
        self.temp_layer = None

        # Get the resulting shapefile
        old_network_edges_path = os.path.join(self.result_dir, "old_network_edges/old_network_edges.shp")
        self.old_network_edges_layer = QgsVectorLayer(old_network_edges_path,
                                                      "old_network_edges_%d" % self.study_id, "ogr")
        # Set styles for new layers
        edge_layer_symbol = self.old_network_edges_layer.renderer().symbol()
        new_symbol = edge_layer_symbol.createSimple({"color_border": uiconf.old_network_edges_border_color})
        self.old_network_edges_layer.renderer().setSymbol(new_symbol)
        self.old_network_edges_layer.renderer().symbol().setColor(uiconf.old_network_edges_color)
        self.old_network_edges_layer.setOpacity(uiconf.old_network_edges_opacity)
        ui_utils.add_layer_to_group(self.old_network_edges_layer,
                                    self.study_suffix(uiconf.input_layers_group_prefix))

        # Get the resulting shapefile
        old_sypply_edges_path = os.path.join(self.result_dir, "old_supply/old_supply.shp")
        self.old_supply_edges_layer = QgsVectorLayer(old_sypply_edges_path,
                                                     "old_supply_edges_%d" % self.study_id, "ogr")
        # Set styles for new layers
        supply_layer_symbol = self.old_supply_edges_layer.renderer().symbol()
        new_symbol = supply_layer_symbol.createSimple({"style": "no",
                                                       "line_style": "dot",
                                                       "color_border": uiconf.old_network_edges_border_color})
        self.old_supply_edges_layer.renderer().setSymbol(new_symbol)
        self.old_supply_edges_layer.renderer().symbol().setColor(uiconf.old_network_edges_color)
        self.old_supply_edges_layer.setOpacity(uiconf.old_network_edges_opacity)
        ui_utils.add_layer_to_group(self.old_supply_edges_layer,
                                    self.study_suffix(uiconf.input_layers_group_prefix))


    def save_existing_network(self, dock):
        if self.data_transfer is not None:
            path_instance = self.data_transfer.network.save_file_path
        else:
            path_instance = QFileDialog.getSaveFileName(filter="Compressed file (*.zip)")
            if isinstance(path_instance, tuple):
                path_instance = path_instance[0]
        old_network_graph = self.dhc_opt.graph_builder.old_network_graph
        ns = NetworkSerializer(old_network_graph,
                               self.dhc_opt.graph_builder.old_network_streets,
                               self.dhc_opt.graph_builder.old_network_buildings)
        ns.serialize(path_instance, self.tmp_dir)

        old_supply_layer_path = path_instance[:-4]+".shp"
        save_layer_to_shapefile(self.old_network_supply_layer, old_supply_layer_path)
        self.iface.messageBar().pushMessage("Success",
                                            "Existing network saved to '%s'" % str(path_instance),
                                            level=3)

    def add_existing_network(self, dock):
        file_path = dock.lineEdit_existingNetworkShapefile.text()
        # import old_network_graph and update old buildings and old streets
        ns = NetworkSerializer.deserialize(file_path, self.tmp_dir)
        self.dhc_opt.graph_builder.old_network_graph = ns.network
        self.dhc_opt.graph_builder.old_network_streets = ns.old_network_streets
        self.dhc_opt.graph_builder.old_network_buildings = ns.old_network_buildings
        self.read_old_supply_file(file_path[:-4]+".shp")

        if dock == self.dock:
            self.show_existing_network(dock)
        else:
            self.dhc_opt.save_old_network_graph(problem='STP')

            # Get the resulting layer
            old_network_edges_path = os.path.join(self.result_dir, "old_network_edges/old_network_edges.shp")
            self.old_network_edges_layer = QgsVectorLayer(old_network_edges_path,
                                                          "old_network_edges_%d" % self.study_id, "ogr")
            # Set styles for new layers
            edge_layer_symbol = self.old_network_edges_layer.renderer().symbol()
            new_symbol = edge_layer_symbol.createSimple({"color_border": uiconf.old_network_edges_border_color})
            self.old_network_edges_layer.renderer().setSymbol(new_symbol)
            self.old_network_edges_layer.renderer().symbol().setColor(uiconf.old_network_edges_color)
            self.old_network_edges_layer.setOpacity(uiconf.old_network_edges_opacity)
            ui_utils.add_layer_to_group(self.old_network_edges_layer,
                                        self.study_suffix(uiconf.input_layers_group_prefix))

        self.update_buildings_labels(dock)

        # Add the buildings and streets to the Already Connected sublayer, set the old_streets and old_buildings attributes from GraphBuilder
        all_streets = self.street_layer.getFeatures()
        old_streets = [s for s in all_streets if (s['u'], s['v']) in self.dhc_opt.graph_builder.old_network_streets]
        all_buildings = self.building_layer.getFeatures()
        old_network_buildings = self.dhc_opt.graph_builder.old_network_buildings
        old_buildings = [b for b in all_buildings if b.attribute(config.BUILDING_ID_KEY) in old_network_buildings]

        # Set "Status" attribute to 2 for selected streets
        self.street_layer.startEditing()
        status_index = self.street_layer.fields().indexFromName(config.STATUS_KEY)
        for s in old_streets:
            # Every building belonging to the old network has to be Included
            self.street_layer.changeAttributeValue(s.id(), status_index, config.EXISTING_STATUS_VALUE)
        self.street_layer.commitChanges()
        # Set categorized renderer to show which buildings have been excluded :
        current_renderer = self.street_layer.renderer()
        if not isinstance(current_renderer,
                          QgsCategorizedSymbolRenderer) or current_renderer.classAttribute() != config.STATUS_KEY:
            r = self.get_renderer('line')
            self.street_layer.setRenderer(r)

        # Set "Status" attribute to 2 for selected buildings
        self.building_layer.startEditing()
        status_index = self.building_layer.fields().indexFromName(config.STATUS_KEY)
        for b in old_buildings:
            # Every building belonging to the old network has to be Included
            self.building_layer.changeAttributeValue(b.id(), status_index, config.EXISTING_STATUS_VALUE)
        self.building_layer.commitChanges()
        # Set categorized renderer to show which buildings have been excluded :
        current_renderer = self.building_layer.renderer()
        if not isinstance(current_renderer,
                          QgsCategorizedSymbolRenderer) or current_renderer.classAttribute() != config.STATUS_KEY:
            r = self.get_renderer('fill')
            self.building_layer.setRenderer(r)

        if self.data_transfer.baseline_scenario is not None:
            self.update_baseline_capacity()

    def init_study_tree(self):
        study_group_name = self.study_suffix(uiconf.study_group_prefix)
        root = QgsProject.instance().layerTreeRoot()
        if self.data_transfer is not None:
            ui_utils.add_group(study_group_name, self.data_transfer.network.get_group_name())
            node = root.findGroup(study_group_name)
            self.data_transfer.tree_group = node
            self.data_transfer.tree_group_name = study_group_name
        else:
            ui_utils.add_group(study_group_name)
        ui_utils.add_group(self.study_suffix(uiconf.input_layers_group_prefix), study_group_name)
        ui_utils.add_group(self.study_suffix(uiconf.output_layers_group_prefix), study_group_name)

        # put OSM at the end
        root = QgsProject.instance().layerTreeRoot()
        for ch in root.children():
            if ch.name() == "OSM":
                _ch = ch.clone()
                root.insertChildNode(len(root.children()), _ch)
                root.removeChildNode(ch)

    def read_old_supply_file(self, file_name):
        # load file
        # retrieve old supply information
        old_supply_capacity = []
        #for b, data in self.dhc_opt.graph_builder.old_network_graph.nodes(data=True):
        #    if data.get(config.NODE_TYPE_KEY, None) == config.SUPPLY_NODE_TYPE:
        #        old_supply_capacity[b] = (  data.get(config.SUPPLY_NAME_KEY, b), 
        #                                    data.get(config.SUPPLY_POWER_CAPACITY_KEY, 0) )
        for f in self.old_network_supply_layer.getFeatures():
            print("feature")
            old_supply_capacity.append([f[config.SUPPLY_NAME_KEY], f[config.SUPPLY_POWER_CAPACITY_KEY]])

        # update old supplies
        if len(old_supply_capacity) > 0:
            self.dock.oldSupply_mGroupBox.setCollapsed(False)
            self.dock.old_sources_table.setRowCount(0)
            self.dock.old_sources_table.insertRow(0)
            self.dock.old_sources_table.setItem(0, 0, QTableWidgetItem("Name"))
            self.dock.old_sources_table.setItem(0, 1, QTableWidgetItem("Baseline Capacity"))
            self.dock.old_sources_table.setItem(0, 2, QTableWidgetItem("Future Capacity"))

            for s in old_supply_capacity:
                nb_rows = self.dock.old_sources_table.rowCount()
                self.dock.old_sources_table.insertRow(nb_rows)
                self.dock.old_sources_table.setItem(nb_rows, 0, QTableWidgetItem(str(s[0])))
                self.dock.old_sources_table.setItem(nb_rows, 1, QTableWidgetItem(str(s[1])))
                self.dock.old_sources_table.setCellWidget(nb_rows, 2, QTextEdit())
                self.dock.old_sources_table.cellWidget(nb_rows, 2).setText(\
                    str(self.dock.old_sources_table.item(nb_rows, 1).text()))
                self.dock.old_sources_table.cellWidget(nb_rows, 2).textChanged.connect(self.update_supply_labels)

            _, _, total_baseline = self.get_total_heat_production(baseline_total=True)
            self.dock.total_old_supply_baseline_int_label.setText("%.0f MW" % total_baseline)
            self.update_supply_labels()

    def set_up_old_supplies(self, file_path):
        self.old_network_supply_layer = QgsVectorLayer(file_path, "old_supply_%d" % self.study_id, "ogr")
        idx = 0
        for field in self.old_network_supply_layer.fields():
            if field.name() == config.SUPPLY_POWER_CAPACITY_KEY[:10]:
                self.old_network_supply_layer.startEditing()
                self.old_network_supply_layer.renameAttribute(idx, config.SUPPLY_POWER_CAPACITY_KEY)
                self.old_network_supply_layer.commitChanges()
            idx += 1
        ui_utils.add_layer_to_group(self.old_network_supply_layer, self.study_suffix(uiconf.input_layers_group_prefix))
        ui_utils.refresh_layers(self.iface)

    def hide_layers_before_editing_networks(self):
        ui_utils.hide_layers(["all_streets_0", "future_scenario", "baseline_scenario"])