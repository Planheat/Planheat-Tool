import matplotlib
matplotlib.use("Agg")
# general
import time
import os
import logging
from copy import deepcopy
# geometry/geography
import geopandas as gpd
import srtm
# graph
import networkx as nx
import geonetworkx as gnx
from networkx.classes.filters import no_filter
from .. import config
#from .. import tools
from ..graph_building_base import GraphBuilder


class ADGraphBuilder(GraphBuilder):
    """Graph builder for the DHC optimizer. It creates an optimization graph for the Fixed Cost Flow Problem with
    Coverage Constraints (FCFPCC).
    It creates the optimization graph by projecting buildings and supplies on streets, then defining a cost structure on
    edges."""

    def __init__(self, **kwargs):
        super(ADGraphBuilder, self).__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        # Supply information :
        self.potential_supply = kwargs.get('potential_supply', None)
        self.old_supply = None
        self.supply_merged_graph = None

    def check_is_ready(self):
        self.logger.info("Checking inputs have been set for the automatic design.")
        super(ADGraphBuilder, self).check_is_ready()
        if self.potential_supply is None and self.old_supply is None:
            raise RuntimeError("No supply has been set.")

    def edge_filter_base(self, graph, e1, e2, e3=0):
        original_edge = graph.edges[e1, e2, e3].get(config.ORIGINAL_EDGE_KEY, (e1,e2))
        oe1, oe2 = original_edge[0], original_edge[1]
        if (oe1,oe2) in self.old_street_graph.edges() or (oe2,oe1) in self.old_street_graph.edges():
            return True
        return False

    def generate_graph(self):
        
        self.check_is_ready()
        self.logger.info("Start optimization graph building...")
        graph_generation_start = time.time()
        self.import_street_graph_from_open_street_map()
        if self.initial_street_graph is None:
            self.initial_street_graph = self.street_graph.copy()
        self.street_graph = self.initial_street_graph.copy()
        self.remove_streets_to_exclude()

        self.add_supply(self.street_graph)

        if self.old_street_graph is not None:
            # first, only with old buildings
            buildings_filter = lambda b: b in self.old_network_buildings
            edge_filter = lambda e1, e2, e3: self.edge_filter_base(self.supply_merged_graph, e1, e2, e3) 
            self.add_buildings(self.supply_merged_graph, node_filter=no_filter, edge_filter = edge_filter, buildings_filter=buildings_filter)

            # then whith the rest of the buildings
            buildings_filter = lambda b: b not in self.marked_buildings and b not in self.old_network_buildings
            node_filter = lambda n: n not in self.old_network_buildings and n not in [config.OLD_SUPPLY_NODE_NAME_PREFIX + str(s) for s in self.old_supply.index]
            self.add_buildings(self.building_merged_graph, node_filter=node_filter, buildings_filter=buildings_filter)
        else:
            buildings_filter = lambda b: b not in self.marked_buildings
            self.add_buildings(self.supply_merged_graph, node_filter=no_filter, buildings_filter=buildings_filter)
        self.finalize_optimization_graph()
        self.logger.info("Optimization graph building time: %.2fs" % (time.time() - graph_generation_start))

    def add_supply(self, street_graph):
        self.logger.info("Start merging supply points...")
        supply_merging_start = time.time()
        
        potential_supply = deepcopy(self.potential_supply)
        potential_supply.index = [config.SUPPLY_NODE_NAME_PREFIX + str(s) for s in potential_supply.index]
        potential_supply[config.NODE_TYPE_KEY] = [config.SUPPLY_NODE_TYPE for s in potential_supply.index]
        old_supply = deepcopy(self.old_supply)
        old_supply.index = [config.OLD_SUPPLY_NODE_NAME_PREFIX + str(s) for s in old_supply.index]
        old_supply[config.NODE_TYPE_KEY] = [config.SUPPLY_NODE_TYPE for s in old_supply.index]
        if self.old_street_graph is not None and not self.modify_old_network:
            edge_filter = lambda e1, e2, e3: not self.edge_filter_base(street_graph, e1, e2, e3) 
        else:
            edge_filter = no_filter
        self.supply_merged_graph = gnx.spatial_points_merge(street_graph, potential_supply, edge_filter=edge_filter, inplace=False)
        
        # we need to add the old supply to the optmization graph and to the old_network_graph
        if self.old_street_graph is not None:
            edge_filter = lambda e1, e2, e3: self.edge_filter_base(self.supply_merged_graph, e1, e2, e3) 
        else:
            edge_filter = no_filter
        gnx.spatial_points_merge(self.supply_merged_graph, old_supply, edge_filter=edge_filter, inplace=True)
        
        self.logger.info("\tMerging supply points time: %.2fs" % (time.time() - supply_merging_start))

    def remove_old_network_streets(self):
        """Remove all old network streets from the street graph."""
        self.logger.info("Old network streets exclusion start")
        street_graph_wo_old_streets = deepcopy(self.street_graph)
        for (u, v) in self.old_network_streets:
            if street_graph_wo_old_streets.has_edge(u, v):
                street_graph_wo_old_streets.remove_edge(u, v)
            if street_graph_wo_old_streets.has_edge(v, u):
                street_graph_wo_old_streets.remove_edge(v, u)
        street_graph_wo_old_streets.remove_nodes_from(list(nx.isolates(street_graph_wo_old_streets)))
        self.logger.info("Old network streets exclusion end")

        return street_graph_wo_old_streets

    def finalize_optimization_graph(self):
        self.logger.info("Start finalization of the optimization graph...")
        finalization_start = time.time()
        # Set graph to directed
        self.optimization_graph = self.building_merged_graph.to_directed(as_view=False)
        # Remove streets to supply edges
        for s, data in self.optimization_graph.nodes(data=True):
            if config.NODE_TYPE_KEY in data and data[config.NODE_TYPE_KEY] == config.SUPPLY_NODE_TYPE:
                edges_to_remove = [e for e in self.optimization_graph.in_edges(s) \
                            if self.optimization_graph.nodes[e[0]].get(config.NODE_TYPE_KEY) != config.SUPPLY_NODE_TYPE] 
                self.optimization_graph.remove_edges_from(edges_to_remove)
        # Set cost on supply edges:
        for s, data in self.optimization_graph.nodes(data=True):
            if config.NODE_TYPE_KEY in data and data[config.NODE_TYPE_KEY] == config.SUPPLY_NODE_TYPE:
                out_edges = self.optimization_graph.out_edges(s, keys=True)
                for e in out_edges:
                    self.optimization_graph.edges[e][config.EDGE_COST_KEY] = config.SUPPLY_FIXED_COST

        # Remove buildings to streets edges
        for b, data in self.optimization_graph.nodes(data=True):
            if config.NODE_TYPE_KEY in data and data[config.NODE_TYPE_KEY] == config.BUILDING_NODE_TYPE:
                edges_to_remove = list(self.optimization_graph.out_edges(b))
                self.optimization_graph.remove_edges_from(edges_to_remove)
        # Fill geometry attribute
        gnx.fill_edges_missing_geometry_attributes(self.optimization_graph)
        # Set length
        gnx.fill_length_attribute(self.optimization_graph, attribute_name=config.EDGE_LENGTH_KEY, only_missing=True)
        # Fill cost
        self.fill_edges_cost_attributes(self.optimization_graph)
        # Fill elevation data
        self.add_elevation_data(self.optimization_graph) 

        self.optimization_graph.graph["name"] = "optimization_graph"
        # self.remove_steep_edges()
        # gnx.export_graph_as_shape_file(self.optimization_graph, r"D:\projets\PlanHeat\PlanHeatGnxWork\tmp",
        #  fiona_cast=True)
        self.logger.info("\tGraph finalization time: %.2fs" % (time.time() - finalization_start))

    def add_elevation_data(self, graph):
        self.logger.info("Start adding elevation data to the graph...")
        add_elevation_start = time.time()
        elevation_data = srtm.get_data()
        nb_nodes = len(graph.nodes)
        # Add the Elevation attribute
        for i, n in enumerate(graph.nodes):
            data = graph.nodes[n]
            graph.nodes[n][config.NODE_ELEVATION_KEY] = elevation_data.get_elevation(data['geometry'].y, data['geometry'].x)
        self.logger.info("End adding elevation data to the graph")

    def remove_steep_edges(self, slope_tolerance = 10):
        self.logger.info("Start removing too steep edges...")
        edges_to_remove = [(u, v, k) for u, v, k in self.optimization_graph.edges \
                if 100*abs(self.optimization_graph.nodes[v][config.NODE_ELEVATION_KEY] \
                - self.optimization_graph.nodes[u][config.NODE_ELEVATION_KEY]) \
                > slope_tolerance * self.optimization_graph.edges[u, v, k][config.EDGE_COST_KEY]]
        self.optimization_graph.remove_edges_from(edges_to_remove)
        isolates = nx.isolates(self.optimization_graph)
        self.optimization_graph.remove_nodes_from(isolates)
        print('Optimization graph has', len(self.optimization_graph.nodes))
        self.logger.info("Ended removing too steep edges")

    def finalize_old_network_graph(self):
        '''fill the missing informations'''
        if self.old_network_graph is None :
            return
        self.logger.info("Start finalization of the old network graph...")
        finalization_start = time.time()

        edges_to_keep = set()
        for e in self.optimization_graph.edges(keys=True):
            if self.optimization_graph.nodes[e[1]].get(config.NODE_TYPE_KEY) == config.BUILDING_NODE_TYPE:
                if e[1] in self.old_network_buildings:
                    edges_to_keep.add(e)
            elif self.optimization_graph.nodes[e[0]].get(config.NODE_TYPE_KEY) == config.SUPPLY_NODE_TYPE:
                if e[0] in [config.OLD_SUPPLY_NODE_NAME_PREFIX + str(s) for s in self.old_supply.index]:
                    edges_to_keep.add(e)
            else:
                original_edge = self.optimization_graph.edges[e].get(config.ORIGINAL_EDGE_KEY, e)
                if (original_edge[0], original_edge[1]) in self.old_network_streets \
                    or (original_edge[1], original_edge[0]) in self.old_network_streets:
                    edges_to_keep.add(e)
        self.old_network_graph = self.optimization_graph.edge_subgraph(edges_to_keep).copy()


# noinspection PyPep8
if __name__ == "__main__":
    data_dir = "data/Antwerp_01"
    results_dir = "optimizer/automatic_design/results/"
    # district area
    district_shape = os.path.join(data_dir, "antwerp_01_shape.shp")
    # supply
    supply_gdf = gpd.read_file(os.path.join(data_dir, "../Waste_heat_city_3.shp"))
    supply_gdf.to_crs(config.CRS, inplace=True)
    prod_mapping = {'<20': 10.0, '20 tot 200': 110.0, '250 tot 500': 375.0, '>200': 350.0, '>500': 700.0}
    supply_gdf["GWh_year"] = list(map(lambda x: prod_mapping[x], supply_gdf["GWh_year"]))
    supply_gdf["GWh_year"] = supply_gdf["GWh_year"] / (365 * 24) * 1000
    supply_gdf.rename(columns={"GWh_year": config.SUPPLY_POWER_CAPACITY_KEY}, inplace=True)
    # buildings
    buildings_path = os.path.join(data_dir, "antwerp_01_buildings.shp")
    # Set graph builder
    self = ADGraphBuilder()

    self.logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    self.logger.addHandler(stream_handler)

    self.district = district_shape
    self.potential_supply = supply_gdf
    self.buildings_file_path = buildings_path
    self.marked_buildings = {'B_231', 'B_1336', 'B_1519', 'B_827', 'B_802', 'B_1546', 'B_1583', 'B_672', 'B_414'}
    self.excluded_streets = {('220725268', '220729562'), ('206137435', '220689674'), ('281482268', '197759325')}
    # Run
    self.generate_graph()
    # Save results
    # gnx.export_graph_as_shape_file(self.optimization_graph, results_dir, fiona_cast=True)
    nx.write_gpickle(self.optimization_graph, os.path.join(results_dir, "optimization_graph.gpickle"))
