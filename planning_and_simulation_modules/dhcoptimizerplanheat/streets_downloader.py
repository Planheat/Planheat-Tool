from PyQt5.QtCore import pyqtSignal, QVariant
from qgis.core import QgsVectorLayer, QgsField, QgsVectorFileWriter, QgsCategorizedSymbolRenderer
import processing, os, time
import osmnx as ox
import geopandas as gpd
import networkx as nx
import geonetworkx as gnx
from .ui import uiconf
from .optimizer import config
from .ui.ui_utils import set_marked_field
from .. import master_planning_config as mp_config


class streetsDownloader():

    def __init__(self):
        """Constructor."""
        self.street_layer = None
        self.geo_graph = None

    def download_streets_from_osm(self):
        print("Downloading streets ...")
        start_time = time.time()
        # Download street from OSM :
        streets_folder = os.path.join(  mp_config.CURRENT_PLANNING_DIRECTORY, mp_config.DISTRICT_FOLDER,
                                        mp_config.STREETS_FOLDER)
        os.makedirs(streets_folder, exist_ok=True)
        buildings_folder = os.path.join(mp_config.CURRENT_PLANNING_DIRECTORY, mp_config.DISTRICT_FOLDER,
                                        mp_config.BUILDING_SHAPE)
        polygon_shape = gpd.read_file(os.path.join(buildings_folder, mp_config.BUILDING_SHAPE+".shp"))
        polygon_shape.to_crs(config.CRS, inplace=True)
        self.street_graph = ox.graph_from_polygon(polygon_shape['geometry'][0], network_type='all')
        stringify_mapping = {n: str(n) for n in self.street_graph.nodes if not isinstance(n, str)}
        nx.relabel_nodes(self.street_graph, stringify_mapping, copy=False)
        
        # construction geo_graph
        self.geo_graph = self.street_graph.to_undirected()
        nx.set_node_attributes(self.geo_graph, name=config.NODE_TYPE_KEY, values=config.STREET_NODE_TYPE)
        self.geo_graph = gnx.read_geograph_with_coordinates_attributes(self.geo_graph, x_key='x', y_key='y',
                                                      edges_geometry_key="geometry", crs=gnx.WGS84_CRS)
        self.geo_graph = gnx.GeoMultiGraph(self.geo_graph)
        gnx.fill_edges_missing_geometry_attributes(self.geo_graph)
        gnx.order_well_lines(self.geo_graph)
        gnx.fill_length_attribute(self.geo_graph, config.EDGE_LENGTH_KEY, only_missing=False)

        # construction street layer
        gdf_edges = ox.save_load.graph_to_gdfs(self.street_graph, nodes=False)
        ox.save_load.save_gdf_shapefile(gdf_edges, filename=streets_folder)
        self.street_layer = QgsVectorLayer(os.path.join(streets_folder, mp_config.STREETS_FOLDER+".shp"),
                                           "all_streets_0", "ogr")
        self.street_layer.renderer().symbol().setColor(uiconf.included_streets_color)
        self.street_layer.renderer().symbol().setWidth(uiconf.street_width)
        self.street_layer.setOpacity(uiconf.streets_opacity)
        set_marked_field(self.street_layer, config.EXCLUDED_BUILDING_KEY, 0)
        
        print("End downloading streets in {0}s".format(time.time() - start_time))
        return self.street_layer