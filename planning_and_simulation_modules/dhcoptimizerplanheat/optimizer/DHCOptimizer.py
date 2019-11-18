# general
import logging
import numpy as np
import os
# geometry/geography
import matplotlib

matplotlib.use('Agg')  # to be used when working with QGIS Python version
import fiona
import geopandas as gpd
from shapely.geometry import Point, LineString
# graph/optimization
import osmnx as ox
import networkx as nx
import geonetworkx as gnx
from .automatic_design.ad_graph_building import ADGraphBuilder
from .automatic_design.ad_network_optimization import ADNetworkOptimizer

from .manual_design.md_graph_building import MDGraphBuilder
from .manual_design.md_network_optimization import MDNetworkOptimizer

#import config as config

from . import config as config


class DHCOptimizer:
    """District Heat and Cooling network optimizer.

    Given a polygon shapefile of the considered district, a building shapefile including demands (kW) and a supply
    shapefile including available production (MW), this module designs a minimal cost network.
    """
    FCFCCP = "Fixed Cost Flow With Coverage Constraint Problem"
    STP = "Steiner Tree Problem"

    def __init__(self, mode=FCFCCP, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.result_dir = kwargs.get('result_dir', '')
        self.data_transfer = kwargs.get('data_transfer')
        self.mode = mode
        if mode == DHCOptimizer.FCFCCP:
            self.graph_builder = ADGraphBuilder(**kwargs)
            self.network_optimizer = ADNetworkOptimizer(**kwargs)
        elif mode == DHCOptimizer.STP:
            self.graph_builder = MDGraphBuilder(**kwargs)
            self.network_optimizer = MDNetworkOptimizer()
        else:
            raise ValueError("Unknown design mode: '%s'" % str(mode))

    def run(self):
        self.logger.info("Generating graph")
        self.graph_builder.generate_graph()
        self.graph_builder.finalize_old_network_graph()
        self.logger.info("Running optimization")
        self.network_optimizer.optimization_graph = self.graph_builder.optimization_graph
        self.network_optimizer.old_network_graph = self.graph_builder.old_network_graph
        self.network_optimizer.optimize()
        self.save_solution(self.network_optimizer.solution_graph, remove_buildings_nodes=False)

    def run_NLP(self, only_preprocess=False):
        self.logger.info("Running NLP optimization")
        self.graph_builder.add_elevation_data(self.network_optimizer.solution_graph)
        success = self.network_optimizer.optimize_NLP(only_preprocess)
        self.save_solution(self.network_optimizer.solution_graph, remove_buildings_nodes=False)
        return success

    def get_old_network_graph(self, problem):
        self.graph_builder.import_street_graph_from_open_street_map()
        self.graph_builder.generate_old_network_graph()
        self.save_old_network_graph(problem)

    def save_old_network_graph(self, problem):
        old_network_graph = self.graph_builder.old_network_graph
        old_network_gdf = ox.save_load.graph_to_gdfs(old_network_graph, nodes=False)
        row_to_keep, geometry_to_keep = [], []
        for index, row in old_network_gdf.iterrows():
            geometry = list(row[config.GPD_GEO_KEY].coords)
            reversed_geometry = geometry[::-1]
            if (geometry not in geometry_to_keep) and (reversed_geometry not in geometry_to_keep):
                geometry_to_keep.append(geometry)
                row_to_keep.append(index)
        old_network_gdf = old_network_gdf.iloc[row_to_keep]
        
        old_network_edges_gdf = old_network_gdf.copy(deep=True)
        ox.save_load.save_gdf_shapefile(old_network_edges_gdf, 
                                filename=os.path.join(self.result_dir, "old_network_edges"))

    def save_old_network_with_capacities(self):
        temp_gdf = gpd.read_file(os.path.join(self.result_dir, "tmp/tmp.shp"))
        for index, row in temp_gdf.iterrows():
            u, v = row['u'], row['v']
            capacity = float(row['capacity'])
            self.graph_builder.old_network_graph.edges[(u, v, 0)]['capacity'] = capacity
            self.graph_builder.old_network_graph.edges[(v, u, 0)]['capacity'] = capacity
        old_network_graph = self.graph_builder.old_network_graph.copy()
        old_supply_graph, old_network_edges_graph = self.separate_supply_and_district_edges(old_network_graph)
        old_supply_gdf = ox.save_load.graph_to_gdfs(old_supply_graph, nodes=False)
        ox.save_load.save_gdf_shapefile(old_supply_gdf, filename=os.path.join(self.result_dir, "old_supply"))
        old_network_edges_gdf = ox.save_load.graph_to_gdfs(old_network_edges_graph, nodes=False)
        ox.save_load.save_gdf_shapefile(old_network_edges_gdf, filename=os.path.join(self.result_dir,
                                                                                     "old_network_edges"))

    def save_solution(self, solution_graph: gnx.GeoGraph, remove_buildings_nodes: bool = False):
        """Save the given solution with shapefiles.

        :param solution_graph: The networkX graph of the solution
        :param remove_buildings_nodes: bool. Specify if the building nodes have to be removed for the visualization
        """
        # Save selected buildings with a shapefile :
        self.logger.info("Saving solution start")
        buildings = gpd.read_file(self.graph_builder.buildings_file_path)

        if self.mode == self.FCFCCP:
            selected_buildings = set()
            for b, data in solution_graph.nodes(data=True):
                if data.get(config.NODE_TYPE_KEY, None) == config.BUILDING_NODE_TYPE:
                    selected_buildings.add(data.get(config.BUILDING_ID_KEY))
            building_not_excluded = [b not in self.graph_builder.marked_buildings
                                     for b in buildings[config.BUILDING_ID_KEY]]
            building_index = [(b in selected_buildings) for b in buildings[config.BUILDING_ID_KEY]]
            building_index = np.logical_and(building_index, building_not_excluded)
            unselected_buildings_index = np.logical_and(np.logical_not(building_index), building_not_excluded)
            buildings_sol = buildings[building_index]
            buildings_not_sol = buildings[unselected_buildings_index]
            schema = self.get_empty_df_writing_schema(buildings_sol, "Polygon") if buildings_sol.empty else None
            buildings_sol.to_file(os.path.join(self.result_dir, config.SELECTED_BUILDINGS_FILE), schema=schema)
            schema = self.get_empty_df_writing_schema(buildings_not_sol, "Polygon") if buildings_not_sol.empty else None
            buildings_not_sol.to_file(os.path.join(self.result_dir, config.UNSELECTED_BUILDINGS_FILE), schema=schema)
        # Remove buildings nodes
        if remove_buildings_nodes:
            heat_demand = nx.get_node_attributes(solution_graph, config.BUILDING_CONSUMPTION_KEY)
            buildings_nodes = heat_demand.keys()
            solution_graph.remove_nodes_from(list(buildings_nodes))
        # Set the line width proportional to the flow
        if self.mode == self.FCFCCP:
            # Separate supply edges from the district edges :
            supply_graph, district_graph = self.separate_supply_and_district_edges(solution_graph)
            district_file_path = os.path.join(self.result_dir, config.SOLUTION_DISTRICT_EDGES_FILE)
            gnx.write_edges_to_geofile(district_graph, district_file_path, fiona_cast=True, driver='ESRI Shapefile')
            supply_file_path = os.path.join(self.result_dir, config.SOLUTION_SUPPLY_EDGES_FILE)
            gnx.write_edges_to_geofile(supply_graph, supply_file_path, fiona_cast=True, driver='ESRI Shapefile')
            if self.graph_builder.old_network_graph is not None:
                old_supply_graph, _ = self.separate_supply_and_district_edges(self.graph_builder.old_network_graph)
                old_supply_file_path = os.path.join(self.result_dir, config.SOLUTION_OLD_SUPPLY_EDGES_FILE)
                gnx.write_edges_to_geofile(old_supply_graph, old_supply_file_path, fiona_cast=True, driver='ESRI Shapefile')
        elif self.mode == self.STP:  # TODO
            edge_file_path = os.path.join(self.result_dir, config.SOLUTION_STP_EDGES_FILE)
            gnx.write_edges_to_geofile(solution_graph, edge_file_path, fiona_cast=True, driver='ESRI Shapefile')
        self.logger.info("Saving solution end")

    @staticmethod
    def get_empty_df_writing_schema(df, geom_type):
        """Set a schema property for an empty data_frame. All non-geometry columns are written has strings."""
        properties = dict([(col, 'str') for col, _type in zip(df.columns, df.dtypes) if col != df._geometry_column_name])
        schema = {'geometry': geom_type, 'properties': properties}
        return schema

    @staticmethod
    def separate_supply_and_district_edges(solution_graph):
        """Separate the supply edges from the district edges for a better visualization.
        :param solution_graph: networkx.Graph
        """
        # Remove nodes and edges not involved in supply
        supply_graph = solution_graph.copy()
        solution_graph = solution_graph.copy()
        for u, v in solution_graph.edges():
            u_node_type = supply_graph.nodes[u].get(config.NODE_TYPE_KEY, None)
            v_node_type = supply_graph.nodes[v].get(config.NODE_TYPE_KEY, None)
            if u_node_type != config.SUPPLY_NODE_TYPE and v_node_type != config.SUPPLY_NODE_TYPE:
                supply_graph.remove_edge(u, v)
        supply_graph.remove_nodes_from(list(nx.isolates(supply_graph)))
        supply_graph.name = "supply"
        # Remove supply nodes from the district solution graph
        for n in list(solution_graph.nodes()):
            if solution_graph.nodes[n].get(config.NODE_TYPE_KEY, None) == config.SUPPLY_NODE_TYPE:
                solution_graph.remove_node(n)
        return supply_graph, solution_graph


if __name__ == '__main__':
    mode = DHCOptimizer.STP

    data_dir = "dhcoptimizerplanheat/data/Antwerp_01"
    results_dir = "dhcoptimizerplanheat/optimizer/automatic_design/results/"
    # district area
    district_shape = os.path.join(data_dir, "antwerp_01_shape.shp")
    # buildings
    buildings_path = os.path.join(data_dir, "antwerp_01_buildings.shp")
    marked_buildings = {'5321164.0', '5321068.0', '3737013.0', '3736648.0', '3737055.0', '3736363.0', '5321079.0',
                        '3736261.0', '3736186.0'}
    excluded_streets = {('220725268', '220729562'), ('206137435', '220689674'), ('281482268', '197759325')}
    if mode == DHCOptimizer.FCFCCP:
        # supply
        supply_gdf = gpd.read_file(os.path.join(data_dir, "../Waste_heat_city_3.shp"))
        supply_gdf.to_crs(config.CRS, inplace=True)
        prod_mapping = {'<20': 10.0, '20 tot 200': 110.0, '250 tot 500': 375.0, '>200': 350.0, '>500': 700.0}
        supply_gdf["GWh_year"] = list(map(lambda x: prod_mapping[x], supply_gdf["GWh_year"]))
        supply_gdf["GWh_year"] = supply_gdf["GWh_year"] / (365 * 24) * 1000 * 1000
        supply_gdf.rename(columns={"GWh_year": config.SUPPLY_POWER_CAPACITY_KEY}, inplace=True)
        # demands = nx.get_node_attributes(self.graph_builder.optimization_graph, config.BUILDING_CONSUMPTION_KEY)
        # total_production = sum(demands.values())
        # dhc_opt
        dhc_opt = DHCOptimizer(mode, potential_supply=supply_gdf,
                               district=district_shape,
                               buildings_file_path=buildings_path,
                               marked_buildings=marked_buildings,
                               excluded_streets=excluded_streets,
                               network_objective=46990.0)
    else:
        dhc_opt = DHCOptimizer(mode, district=district_shape,
                               buildings_file_path=buildings_path,
                               marked_buildings=marked_buildings,
                               excluded_streets=excluded_streets)
    self = dhc_opt

    self.logger = logging.getLogger()
    self.logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    self.logger.addHandler(stream_handler)

    self.run()
