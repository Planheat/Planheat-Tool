import logging
import math
import osmnx as ox
import pandas as pd
import geopandas as gpd
import networkx as nx
from networkx.classes.filters import no_filter
import geonetworkx as gnx
from . import config
#from . import tools
from requests.exceptions import ConnectionError
from ..exception_utils import DHCOptimizerException


class GraphBuilder:
    """
    This object defines a set of methods to create an optimization graph from different inputs. Lower classes in
    inheritance chain defines specifically the steps needed to create the optimization graph depending on the considered
    problem.
    """

    def __init__(self, **kwargs):
        self.data_transfer = kwargs.get('data_transfer')
        self.logger = logging.getLogger(__name__)
        # Study area
        self.district = kwargs.get('district', None)

        # Streets
        self.streets_are_imported = False
        self.initial_street_graph = None
        self.street_graph = None
        self.excluded_streets = kwargs.get('excluded_streets', set())

        # Buildings
        self.buildings_file_path = kwargs.get('buildings_file_path', None)
        self.buildings_gdf = None
        self.building_merged_graph = None
        self.marked_buildings = kwargs.get('marked_buildings', set())  # ids of the buildings to exclude in automatic
        # mode / consider exclusivelty in manual mode

        # Existing network
        self.old_street_graph = None
        self.old_network_graph = None
        self.old_network_streets = kwargs.get('old_network_streets', set())
        self.old_network_buildings = kwargs.get('old_network_buildings', set())

        # Output
        self.optimization_graph = None

    def check_is_ready(self):
        """Check that all the necessary inputs have been set. If not, an error is raised. This function is called from
        subclasses where additional check can be done."""
        self.logger.info("Checking inputs have been set.")
        if self.district is None:
            raise RuntimeError("No district area have been set.")
        if self.buildings_file_path is None:
            raise RuntimeError("No buildings file path have been set.")

    def generate_graph(self):
        raise NotImplemented("Method must be called from sub class")

    def import_street_graph_from_open_street_map(self):
        """Import from OpenStreetMap the graph of the streets contained in the polygon defined by the district shapefile
        """
        print("graph_building_base.py, import_street_graph_from_open_street_map(). Running...")
        if self.data_transfer.ready_check():
            print("graph_building_base.py, import_street_graph_from_open_street_map(). data_transfer received and run!")
            self.street_graph = self.data_transfer.geo_graph
            self.streets_are_imported = True
        else:
            if not self.streets_are_imported:
                polygon_shape = gpd.read_file(self.district)
                polygon_shape.to_crs(config.CRS)
                self.logger.info("Getting OSM data from polygon")
                try:
                    graph = ox.graph_from_polygon(polygon_shape['geometry'][0], network_type='all')
                except ConnectionError:
                    raise DHCOptimizerException("Internet connection error: unable to reach the OSM overpass API,"
                                                " check your internet connection.")
                self.logger.info("Street graph generation start")
                graph = graph.to_undirected()
                stringify_mapping = {n: str(n) for n in graph.nodes if not isinstance(n, str)}
                nx.relabel_nodes(graph, stringify_mapping, copy=False)
                nx.set_node_attributes(graph, name=config.NODE_TYPE_KEY, values=config.STREET_NODE_TYPE)
                geo_graph = gnx.read_geograph_with_coordinates_attributes(graph, x_key='x', y_key='y',
                                                              edges_geometry_key="geometry", crs=gnx.WGS84_CRS)
                geo_graph = gnx.GeoMultiGraph(geo_graph)
                gnx.fill_edges_missing_geometry_attributes(geo_graph)
                gnx.order_well_lines(geo_graph)
                gnx.fill_length_attribute(geo_graph, config.EDGE_LENGTH_KEY, only_missing=False)
                self.street_graph = geo_graph
                self.streets_are_imported = True
                self.logger.info("Street graph generation end")

    def remove_streets_to_exclude(self):
        """Remove all excluded streets from the street graph."""
        self.logger.info("Streets exclusion start")
        for (u, v) in self.excluded_streets:
            if self.street_graph.has_edge(u, v):
                self.street_graph.remove_edge(u, v)
            if self.street_graph.has_edge(v, u):
                self.street_graph.remove_edge(v, u)
        self.street_graph.remove_nodes_from(list(nx.isolates(self.street_graph)))
        self.logger.info("Streets exclusion end")

    def load_buildings(self):
        if self.buildings_gdf is None:
            self.logger.info("Loading buildings start")
            # read file
            buildings_gdf = gpd.read_file(self.buildings_file_path)
            buildings_gdf.to_crs(config.CRS, inplace=True)
            # Trim columns
            buildings_gdf = buildings_gdf[[config.BUILDING_ID_KEY, config.BUILDING_CONSUMPTION_KEY, config.GPD_GEO_KEY,
                                           config.EXCLUDED_BUILDING_KEY, 
                                           config.BUILDING_USE_KEY, 
                                           config.BUILDING_GROSS_FOOTPRINT_AREA_KEY]]
            # set the index on building id key
            buildings_gdf.set_index(config.BUILDING_ID_KEY, inplace=True, drop=False)
            # filter on excluded buildings
            buildings_gdf = buildings_gdf[buildings_gdf[config.EXCLUDED_BUILDING_KEY] != 1]
            # Set consumptions units in MW
            buildings_gdf[config.BUILDING_CONSUMPTION_KEY] *= config.BUILDING_CONSUMPTION_FACTOR_UNIT
            # Replace polygons with points using polygons centroids
            buildings_gdf[config.GPD_GEO_KEY] = list(map(lambda p: p.centroid, buildings_gdf[config.GPD_GEO_KEY]))
            # Set node type attribute
            buildings_gdf[config.NODE_TYPE_KEY] = [config.BUILDING_NODE_TYPE for b in buildings_gdf.index]
            self.buildings_gdf = buildings_gdf
            self.logger.info("Loading buildings end")
        return self.buildings_gdf

    def add_buildings(self, graph, node_filter=no_filter, edge_filter=no_filter, buildings_filter=None):
        self.logger.info("Add buildings start")
        buildings_gdf = self.load_buildings()
        if buildings_filter is not None:
            buildings_gdf = buildings_gdf[[buildings_filter(b) for b in buildings_gdf[config.BUILDING_ID_KEY]]]
        # Do the merge operation
        intersection_nodes_attr = {config.NODE_TYPE_KEY: config.STREET_NODE_TYPE}
        self.building_merged_graph = gnx.spatial_points_merge(graph, buildings_gdf,
                                                              node_filter=node_filter, edge_filter=edge_filter, inplace=False,
                                                              intersection_nodes_attr=intersection_nodes_attr)
        self.building_merged_graph.name = "building_merged_graph"
        self.logger.info("Add buildings end")

    def generate_old_network_graph(self):
        """Generates the old network graph from the street graph by following theses steps :
            - Remove streets that are not concerned by the old networkX
            - Import buildings with the shapefile and project the buildings of the old network on streets
            - Remove useless parts of streets"""
        self.logger.info("Generating old network start")
        edges_to_keep = [(e[0], e[1], 0) for e in self.old_network_streets]  # TODO: parse real key of edges here
        self.old_street_graph = self.street_graph.edge_subgraph(edges_to_keep)
        self.add_existing_buildings()
        self.recompose_old_network_graph()
        self.logger.info("Generating old network end")

    def add_existing_buildings(self):
        self.logger.info("Add existing buildings start")
        buildings_gdf = self.load_buildings()
        buildings_gdf = buildings_gdf[[b in self.old_network_buildings for b in buildings_gdf[config.BUILDING_ID_KEY]]]
        # Do the merge operation
        intersection_nodes_attr = {config.NODE_TYPE_KEY: config.STREET_NODE_TYPE}
        self.old_network_graph = gnx.spatial_points_merge(self.old_street_graph, buildings_gdf, inplace=False,
                                                          intersection_nodes_attr=intersection_nodes_attr)
        self.logger.info("Add existing buildings end")

    def recompose_old_network_graph(self):
        """Creates the old network graph from its buildings and the list of concerned streets.

        What has to be done if we want to refine the existing network modelling tool:
            * Decide how to deal with cycles in the existing graph (keep them, try to remove them using a criteria)
            * Find a way to store the connections between the street graph and the existing graph
            * Modify the street graph : remove the existing network edges, add the residual connections
            * Show the modification to the user : export street graph as shapefile, re-read it from QGIS

        """
        pass
        # TODO : decide what ho to deal with these problems (see previous code in git for inspiration)

    def read_shp_old_network(self, path):
        nodes_df = pd.read_csv(path + '/data_nodes.csv', sep=';', index_col=0)
        edges_gdf = gpd.read_file(path + '/edges/edges.shp')
        edges_gdf.to_crs(config.CRS, inplace=True)
        self.old_network_graph = nx.MultiGraph()
        for i, row in edges_gdf.iterrows():
            self.old_network_graph.add_edge(row['u'], row['v'], row['key'], cost=row['cost'], geometry=row['geometry'],
                u=row['u'], v=row['v'])
            if edges_gdf.isnull().loc[i, 'originedge']:
                continue
            self.old_network_graph.edges[row['u'], row['v'], row['key']]['originedge'] = row['originedge']
        dict_attr_nodes = {}
        for n in self.old_network_graph.nodes:
            dict_attr_nodes[n] = {}
            for col in nodes_df.columns:
                if nodes_df.isnull().loc[n, col]:
                    continue
                dict_attr_nodes[n][col] = nodes_df.loc[n, col]
        nx.set_node_attributes(self.old_network_graph, dict_attr_nodes)
        self.old_network_graph.graph['crs'] = edges_gdf.crs
        self.old_network_graph.graph['name'] = 'old_network_graph'

        # identify old buildings and old streets
        self.old_network_buildings = set([n for n in self.old_network_graph.nodes
                                          if self.old_network_graph.nodes[n][config.NODE_TYPE_KEY] == config.BUILDING_NODE_TYPE])
        self.marked_buildings = self.marked_buildings.union(self.old_network_buildings)
        self.old_network_streets = set([eval(self.old_network_graph.edges[u, v, k]['originedge'])[:2]
                                        for u, v, k in self.old_network_graph.edges
                                        if self.old_network_graph.edges[u, v, k]['originedge'] != ''])
        reversed_old_streets = {(e[1], e[0]) for e in self.old_network_streets
                                if (e[1], e[0]) in self.street_graph.edges()}
        self.old_network_streets = self.old_network_streets.union(reversed_old_streets)


    def remove_extremity_junctions(self, graph):
        while True:
            nodes_to_remove = [n for n in graph.nodes if n in self.street_graph.nodes
                               and len(list(graph.neighbors(n))) == 1]
            if len(nodes_to_remove) == 0:
                break
            graph.remove_nodes_from(nodes_to_remove)
        return graph


    def fill_edges_cost_attributes(self, graph):
        '''add the cost of the edge which is the length if there is no reduced cost on this street'''
        for e in graph.edges:
            if config.ORIGINAL_EDGE_KEY in graph.edges[e]:
                original_edge = graph.edges[e][config.ORIGINAL_EDGE_KEY]
            else:
                original_edge = e
            if len(original_edge) == 2:
                original_edge = (original_edge[0], original_edge[1], 0)
            leastcost_coef = self.street_graph.edges.get(original_edge,{}).get(config.LEASTCOST_COEF_KEY,0)
            graph.edges[e][config.EDGE_COST_KEY] = (1-leastcost_coef/100)*graph.edges[e][config.EDGE_LENGTH_KEY]
            graph.edges[e][config.LEASTCOST_COEF_KEY] = leastcost_coef