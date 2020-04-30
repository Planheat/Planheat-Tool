# general
import logging
import os
import sys
import time
import configparser
import math
import scipy.optimize as opt
from scipy.spatial import ConvexHull
from copy import deepcopy
from itertools import combinations
# graph
import networkx as nx
import geonetworkx as gnx
# data
import pandas as pd
# optimization
import julia
# config
from .. import config
from ...exception_utils import DHCOptimizerException
from .NLP.data_regressions import *
from PyQt5.QtWidgets import QMessageBox
from ....python_julia_interface import JuliaQgisInterface


class ADNetworkOptimizer:
    """Network optimizer in automatic design mode.
    Given a 'networkx' network having costs, capacities, demand and production attributes, the optimize method trying to
    find the minimal fixed cost network supplying the given objective.
    """

    def __init__(self, optimization_graph=None, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.optimization_graph = optimization_graph
        self.network_objective = kwargs.get('network_objective', None)
        self.solution_graph = None
        self.connected = False
        self.connected_buildings = None
        self.old_capacity = {}
        self.conf = {}
        os.makedirs(os.path.join(os.environ["LOCALAPPDATA"], "QGIS\\QGIS3\\planheat_data\\tmp"), exist_ok=True)
        self.solver_log_file =  os.path.join(os.environ["LOCALAPPDATA"], "QGIS\\QGIS3\\planheat_data\\tmp\\output.log")
        self.energy = None
        self.consumption_file_path = os.path.join(os.path.dirname(__file__),'NLP','consumption_data.csv')
        self.conf_path = os.path.join(os.path.dirname(__file__),'NLP','conf.ini')

    def check_is_ready(self):
        """Check that all necessary inputs have been set."""
        self.logger.info("Checking optimization inputs for automatic design.")
        if self.optimization_graph is None:
            raise RuntimeError("The optimization graph needs to be defined in order to optimize the network.")
        if self.network_objective is None:
            raise RuntimeError("A network objective has to be set (in MW).")

    def check_infeasibility(self, graph, objective):
        self.logger.info("Checking infeasibility for automatic design.")
        ccs = list(nx.connected_components(graph.to_undirected()))
        productions = nx.get_node_attributes(graph, config.SUPPLY_POWER_CAPACITY_KEY)
        heat_demand = nx.get_node_attributes(graph, config.BUILDING_CONSUMPTION_KEY)
        total_residual_connections = 0.0
        # print([e for e in graph.edges()])
        for cc in ccs:
            #print('!!', cc)
            residual_production = sum(productions[n] for n in cc if n in productions)
            residual_consumption = sum(heat_demand[n] for n in cc if n in heat_demand)
            residual_maximum_connection = min(residual_production, residual_consumption)
            total_residual_connections += residual_maximum_connection
        if total_residual_connections < objective - 1e-8:
            raise DHCOptimizerException("Problem is inconsistent: total production capacity is lower than coverage"
                                        " objective (taking into account connected components): "
                                        "reachable consumption is %f"
                                        " and total objective is %f" % (total_residual_connections,
                                                                         objective))

    def optimize(self):
        """Run the optimization with the selected method
        :return: flows : dict. Flow on each edge.
        :return: obj_val: float. Solution cost.
        """

        self.logger.info("Solving with Dynamic Slope Scaling Procedure in Julia :")
        optimization_start = time.time()

        # 1. Preprocess for old network graph
        if self.old_network_graph is not None:

            # DSSP on old network
            old_network_obj = sum(list(nx.get_node_attributes(self.old_network_graph, config.BUILDING_CONSUMPTION_KEY).values()))-1e-5
            try:
                self.check_infeasibility(self.old_network_graph, old_network_obj)
            except DHCOptimizerException as e:
                e.data = "Invalid existing network: " + e.data
                raise e

            flows, obj_val = self.optimize_with_dssp_julia(self.old_network_graph, old_network_obj, set())
            self.logger.info("Optimization phase time: %.2fs" % (time.time() - optimization_start))
            solution_old_graph = self.build_solution_graph(self.old_network_graph, flows)

            if self.modify_old_network:

                # Add max capacity on old edges
                self.old_capacity = deepcopy(flows)
                old_buildings = list(nx.get_node_attributes(self.old_network_graph, config.BUILDING_CONSUMPTION_KEY).values())
                for key in flows:
                    if (key[1],key[0],0) not in self.old_capacity and key[1] not in old_buildings:
                        self.old_capacity[(key[1],key[0],0)] = self.old_capacity[key]

                # Add Imaginary edges
                for edge in self.old_capacity:
                    if self.optimization_graph.has_edge(*edge):

                        # add nodes
                        if not self.optimization_graph.has_node(config.IM_PREFIX+edge[0]):
                            self.optimization_graph.add_node(config.IM_PREFIX+edge[0])
                            self.optimization_graph.nodes[config.IM_PREFIX+edge[0]][config.GPD_GEO_KEY] = \
                                    self.optimization_graph.nodes[edge[0]][config.GPD_GEO_KEY]
                        if not self.optimization_graph.has_node(config.IM_PREFIX+edge[1]):
                            self.optimization_graph.add_node(config.IM_PREFIX+edge[1])
                            self.optimization_graph.nodes[config.IM_PREFIX+edge[1]][config.GPD_GEO_KEY] = \
                                    self.optimization_graph.nodes[edge[1]][config.GPD_GEO_KEY]
                        # add edges
                        if not self.optimization_graph.has_edge(edge[0],config.IM_PREFIX+edge[0]):
                            self.optimization_graph.add_edge(edge[0],config.IM_PREFIX+edge[0])
                        if not self.optimization_graph.has_edge(config.IM_PREFIX+edge[0],config.IM_PREFIX+edge[1]):
                            self.optimization_graph.add_edge(config.IM_PREFIX+edge[0],config.IM_PREFIX+edge[1])
                        if not self.optimization_graph.has_edge(config.IM_PREFIX+edge[1],edge[1]):
                            self.optimization_graph.add_edge(config.IM_PREFIX+edge[1],edge[1])

                        # put cost
                        self.optimization_graph.edges[(config.IM_PREFIX+edge[0],config.IM_PREFIX+edge[1],0)][config.EDGE_COST_KEY] = \
                                    self.optimization_graph.edges[(edge[0],edge[1],0)][config.EDGE_COST_KEY]
                        self.optimization_graph.edges[(edge[0],edge[1],0)][config.EDGE_COST_KEY] = 1e-5
                        self.optimization_graph.edges[(edge[0],config.IM_PREFIX+edge[0],0)][config.EDGE_COST_KEY] = 1e-5
                        self.optimization_graph.edges[(config.IM_PREFIX+edge[1],edge[1],0)][config.EDGE_COST_KEY] = 1e-5

            else:
                # if we don't modify the old network, we have to change the capacity of the supplies
                already_consummed = {}
                for edge in solution_old_graph.edges():
                    if solution_old_graph.nodes[edge[0]].get(config.NODE_TYPE_KEY) == config.SUPPLY_NODE_TYPE:
                        already_consummed[edge[0]] = already_consummed.get(edge[0], 0) + \
                                solution_old_graph.edges[edge][config.SOLUTION_POWER_FLOW_KEY]
                for source in already_consummed:
                    if already_consummed[source] <= self.optimization_graph.nodes[source][config.SUPPLY_POWER_CAPACITY_KEY]:
                        self.optimization_graph.nodes[source][config.SUPPLY_POWER_CAPACITY_KEY] -= already_consummed[source]
                        self.network_objective -= already_consummed[source]
                    else:
                        self.network_objective -= self.optimization_graph.nodes[source][config.SUPPLY_POWER_CAPACITY_KEY]
                        self.optimization_graph.nodes[source][config.SUPPLY_POWER_CAPACITY_KEY] = 0

                # Remove edges from old network
                edges_to_remove = set()
                for e in self.optimization_graph.edges():
                    if self.old_network_graph.has_edge(*e) or self.old_network_graph.has_edge(e[1],e[0]):
                        edges_to_remove.add(e)
                self.optimization_graph.remove_edges_from(edges_to_remove)

                # Remove isolated buildings of optimization graph
                isolated_to_remove = set()
                for e in self.old_network_graph.edges():
                    if e[0] in self.old_network_graph.nodes() and \
                    self.optimization_graph.nodes[e[1]].get(config.NODE_TYPE_KEY) == config.BUILDING_NODE_TYPE:
                        isolated_to_remove.add(e)
                self.optimization_graph.remove_edges_from(isolated_to_remove)

                # Remove buildings from old network
                for n, data in self.old_network_graph.nodes(data=True):
                    if data.get(config.NODE_TYPE_KEY) == config.BUILDING_NODE_TYPE:
                        self.optimization_graph.remove_node(n)

                # Re-link sources
                sources = set()
                for n, data in self.optimization_graph.nodes(data=True):
                    if data.get(config.NODE_TYPE_KEY) == config.SUPPLY_NODE_TYPE:
                        sources.add(n)
                source_graph = self.optimization_graph.subgraph(sources).copy()
                self.optimization_graph.remove_nodes_from(sources)
                gnx.remove_isolates(self.optimization_graph)
                node_filter = lambda n: self.optimization_graph.nodes.get(n,{}).get(config.NODE_TYPE_KEY) != config.BUILDING_NODE_TYPE
                gnx.spatial_points_merge(self.optimization_graph, source_graph.nodes_to_gdf(), node_filter=node_filter, inplace=True)

            # fill missing information
            gnx.fill_edges_missing_geometry_attributes(self.optimization_graph)
            gnx.fill_length_attribute(self.optimization_graph, config.EDGE_LENGTH_KEY, only_missing=True)
            gnx.fill_length_attribute(self.optimization_graph, config.EDGE_COST_KEY, only_missing=True)
            for e in self.optimization_graph.edges(keys=True):
                self.optimization_graph.edges[e][config.LEASTCOST_COEF_KEY] = \
                    self.optimization_graph.edges[e].get(config.LEASTCOST_COEF_KEY,0)



        # 2. Process the DSSP on optimization graph
        self.check_is_ready()
        self.check_infeasibility(self.optimization_graph, self.network_objective)

        if self.old_network_graph is not None and self.modify_old_network:
            old_buildings = set(nx.get_node_attributes(self.old_network_graph, config.BUILDING_CONSUMPTION_KEY).keys())
        else:
            old_buildings = set()
        flows, obj_val = self.optimize_with_dssp_julia(self.optimization_graph, self.network_objective, old_buildings,postprocess= (not self.modify_old_network))
        self.logger.info("Optimization phase time: %.2fs" % (time.time() - optimization_start))
        self.solution_graph = self.build_solution_graph(self.optimization_graph, flows, self.connected)

        # 3. Postprocess for old network graph
        if self.old_network_graph is not None:
            
            if self.modify_old_network:
                # Put the right supply capacity and cost
                for edge in self.old_capacity:
                    if self.solution_graph.has_edge(edge[0],edge[1]):
                        self.solution_graph.edges[(edge[0],edge[1])][config.EDGE_COST_KEY] = \
                        self.optimization_graph.edges[(config.IM_PREFIX+edge[0],config.IM_PREFIX+edge[1],0)][config.EDGE_COST_KEY]
                
                # Remove imaginary edges
                imaginary_nodes_to_remove = set()
                nodes_to_relabel = {}
                for edge in self.solution_graph.edges():
                    if str(edge[0]).startswith(config.IM_PREFIX) and str(edge[1]).startswith(config.IM_PREFIX):
                        real_edge = edge[0][len(config.IM_PREFIX):],edge[1][len(config.IM_PREFIX):]
                        self.old_capacity[(real_edge[0], real_edge[1], 0)] = pd.np.inf
                        self.old_capacity[(real_edge[1], real_edge[0], 0)] = pd.np.inf
                        if not self.solution_graph.has_edge(*real_edge):
                            for i in range(2):
                                nodes_to_relabel[edge[i]] = real_edge[i]
                        else:
                            self.solution_graph.edges[real_edge[0],real_edge[1]][config.SOLUTION_POWER_FLOW_KEY] += \
                            self.solution_graph.edges[edge].get(config.SOLUTION_POWER_FLOW_KEY,0)
                            imaginary_nodes_to_remove.add(edge[0])
                            imaginary_nodes_to_remove.add(edge[1])
                    elif str(edge[0]).startswith(config.IM_PREFIX):
                        imaginary_nodes_to_remove.add(edge[0])
                    elif str(edge[1]).startswith(config.IM_PREFIX):
                        imaginary_nodes_to_remove.add(edge[1])

                nx.relabel_nodes(self.solution_graph, nodes_to_relabel, copy=False)
                self.solution_graph.remove_nodes_from(list(imaginary_nodes_to_remove))
                for node in nodes_to_relabel.values():
                    if self.solution_graph.has_edge(node, node):
                        self.solution_graph.remove_edge(node, node)

            else:
                for source in nx.get_node_attributes(self.solution_graph, config.SUPPLY_POWER_CAPACITY_KEY):
                    self.solution_graph.nodes[source][config.SUPPLY_POWER_CAPACITY_KEY] += already_consummed.get(source,0)
                    self.optimization_graph.nodes[source][config.SUPPLY_POWER_CAPACITY_KEY] += already_consummed.get(source,0)

        return flows, obj_val

    def optimize_NLP(self, only_preprocess=False):
        ''' solve the NLP problem of the optimal size of the pipes knowing the route i.e. the selected streets
        1. Load parameters
        2. Preprocess to satisfy the heat demand at any time of the year
        3. Solve the problem with Ipopt or Knitro on the graph
        4. Add velocity, pressure and costs information on solution graph's edges if the status of the optimizer is "Optimal" '''

        self.logger.info("Start pipe size optimization")

        # 1. Load parameters
        self.load_conf()


        consumption_data, capacity_data = self.get_consumption_and_capacities_from_csv(self.solution_graph, self.consumption_file_path)
        
        # 2. Preprocess NLP
        if self.old_network_graph is not None and self.modify_old_network:
            max_capacity = self.old_capacity
        else:
            max_capacity = {}
        lb_flow = self.preprocess(self.solution_graph, consumption_data, capacity_data, max_capacity)
        # Conversion MW flow to diameter
        lb_diam = {}
        a_vel, b_vel = self.conf["A_MAX_VELOCITY"], self.conf["B_MAX_VELOCITY"]
        for edge in lb_flow:
            mass_flow = self.convert_power_to_mass_flow(lb_flow[edge])

            # mass flow = v * pi*(D/2)**2 = (A*D+B) * pi*(D/2)**2 (in mm)
            f = lambda x : x**3 *a_vel + x**2*b_vel - 4*mass_flow/math.pi/self.conf["RHO"]*1e6
            a, b = 0, 500
            while b-a>0.1:
                c = (a+b)/2        
                if f(a)*f(c) <= 0 : b = c        
                else: a = c
            lb_diam[edge] = a/10 # (in cm)

        if only_preprocess:
            self.fill_edges_with_NLP({'Diameter': lb_diam})
            self.logger.info("Pipe size optimization completed")
            return True

        # 3.
        peak_consumption = self.get_annual_peak_consumption(consumption_data)
        NLP_Output, status = self.optimize_pipe_size(self.solution_graph, lb_diam, peak_consumption, max_capacity)

        if status == "Optimal": # "Optimal", "Unbounded", "Infeasible", "UserLimit", "Error" or "NotSolved"
            self.logger.info("Pipe size optimization completed")
            self.logger.info("Collecting the NLP solution" )
            self.fill_edges_with_NLP(NLP_Output)
            return True
        else:
            self.logger.warning("NLP optimization exits with status: %s" % str(status))
            self.fill_edges_with_NLP({'Diameter': lb_diam})
            return False

    def build_solution_graph(self, graph, flows, connecting_graph=False):
        """Create the solution with the optimization results. Keep only the edges with non negative flow."""
        self.logger.info("Building solution graph")
        self.clean_flow_cycles(flows)
        edges_to_keep = [e for e, flow in flows.items() if flow > 0]
        solution_graph_mdg = graph.edge_subgraph(edges_to_keep)

        if connecting_graph:
            # We add the edges to connect
            edges_to_keep = edges_to_keep + self.connecting_graph(solution_graph_mdg)
            # We rebuild the graph
            solution_graph_mdg = graph.edge_subgraph(edges_to_keep)

        # We add the flow attribute
        for e in edges_to_keep:
            solution_graph_mdg.edges[(e[0], e[1], 0)][config.SOLUTION_POWER_FLOW_KEY] = flows[e]

        # We convert it in GeoDiGraph
        solution_graph_mdg.crs = self.optimization_graph.crs
        solution_graph = gnx.GeoDiGraph(solution_graph_mdg, crs=solution_graph_mdg.crs)

        gnx.remove_isolates(solution_graph)
        solution_graph.name = "solution_graph"

        return solution_graph


    def preprocess(self, solution_graph, consumption_data, capacity_data, max_capacity={}):
        ''' calculate the lower bound for flow. 
        1. Simplify the graph until having no end nodes
        2. If there is no crossing nodes, the preprocess is ended.
        3.  1) we calculate for each edge the surplus and the need 
            2) we deduced the lower bounds'''

        self.logger.info('start preprocess')

        lb_flow = {}

        # Graph copy to directed graph
        G = nx.DiGraph(nx.Graph(solution_graph))

        # check dimensions
        assert len(consumption_data) == len(capacity_data), "Dimension of consumption_data and capacity_data much match"

        start_time = time.time()

        # 1. simplify the graph and calculate the lower bounds
        end_nodes = set([x for x in G.nodes() \
            if len(set(G.predecessors(x)).union(set(G.successors(x))))==1\
            and G.node[x].get(config.NODE_TYPE_KEY,config.SUPPLY_NODE_TYPE) != config.SUPPLY_NODE_TYPE])
        finished = self.calculate_consumption_predecessors_nodes(G, consumption_data, capacity_data, lb_flow, end_nodes)
        if finished:
            return lb_flow
        
        # 3.
        source_nodes = set([n for n in G.nodes() if G.node[n].get(config.NODE_TYPE_KEY,None) == config.SUPPLY_NODE_TYPE])
        needs_data, surplus_data = {}, {}
        for node in source_nodes:
            for edge in G.out_edges(node):
                self.find_needs(G, edge, needs_data, consumption_data, source_nodes, max_capacity)
        
        for edge in G.edges():
            self.find_surplus(G, edge, surplus_data, consumption_data, capacity_data, set(), max_capacity)

        for edge in set(surplus_data.keys()).intersection(set(needs_data.keys())):
            if type(surplus_data[edge]) != int and type(needs_data[edge]) != int:
                lb_flow[edge] = max(lb_flow.get(edge,0), max(pd.concat([surplus_data[edge],needs_data[edge]], axis=1).min(axis=1)))
                lb_flow[(edge[1], edge[0], *edge[2:])] = max( lb_flow.get((edge[1], edge[0], *edge[2:]),0), lb_flow[edge] )


        self.logger.info('end preprocess in ' + str(time.time() - start_time) + ' s')


        return lb_flow

    def connecting_graph(self, solution_graph, weight='cost', ignore_sources=False):
        """Return the list of edges to add to have a connected graph
        1. find the groups of sources isolated from each others
        2. calculate for each group of sources the convex hull
        3. find the smallest path between each pair of groups
            The key idea is to add to the graph edges of weight 0 between all nodes on the convex hull
            and then run a dijkstra between one random node of group1 to one random node of group2.
            To have the "real" path, we just have to remove 0-weigth edges
        4. Do a minimum spanning tree with the aggregated graph (nodes are the different groups and edges are the path found just before)
        """
        debut = time.time()
        self.logger.info('start connecting graph')

        # we need an undirected graph
        undirected_solution_graph = solution_graph.to_undirected()

        if self.old_network_graph is not None and self.modify_old_network:
            undirected_solution_graph = nx.compose(nx.MultiGraph(self.old_network_graph), undirected_solution_graph)

        # if already connected
        if nx.is_connected(undirected_solution_graph) == True:
            self.logger.info("the solution graph is already connected")
            return []

        # Computing the minimum sources in each component and all junction nodes in the solution graph
        nodetype = nx.get_node_attributes(undirected_solution_graph, config.NODE_TYPE_KEY)
        list_sources = [node for node in nodetype if nodetype[node] == config.SUPPLY_NODE_TYPE]

        # 1. Search of all connected subgraphs
        if not ignore_sources:
            reduced_list_sources = []
            while len(list_sources) > 0:
                source, is_isolated = list_sources.pop(0), True
                for i in range(len(list_sources)):
                    is_isolated = is_isolated and not (nx.has_path(undirected_solution_graph, source, list_sources[i]))
                if is_isolated:
                    reduced_list_sources.append(source)
        else:
            reduced_list_sources = [list(n)[0] for n in nx.connected_components(undirected_solution_graph)]

        # 2. Creation of all convex hulls for each source in reduced_list_sources
        hulls = {}
        for source in reduced_list_sources:
            coord_compo = {}
            nodes_connecting_source = nx.node_connected_component(undirected_solution_graph, source)
            for node in nodes_connecting_source:
                xy = tuple(self.optimization_graph.get_node_coordinates(node))
                coord_compo[xy] = node
            if len(coord_compo) > 2:
                convexhull = ConvexHull(list(coord_compo.keys())).points
            else:
                convexhull = list(coord_compo.keys())
            hulls[source] = [coord_compo[tuple(coord)] for coord in convexhull]

        # 3. Create list of possible list_edges_to_add
        list_edges_to_add = {}  # list of {(S1, S2):(length_of_SP, edges_to_add)}

        for S1, S2 in combinations(reduced_list_sources, 2):

            # change weight of edges
            for i in range(len(hulls[S1])-1):
                u,v = hulls[S1][i], hulls[S1][i+1]
                self.optimization_graph.add_edge(u,v,key=-1,weight=0)
            self.optimization_graph.add_edge(hulls[S1][-1],hulls[S1][0],key=-1,weight=0)
            for i in range(len(hulls[S2])-1):
                u,v = hulls[S2][i], hulls[S2][i+1]
                self.optimization_graph.add_edge(u,v,key=-1,weight=0)
            self.optimization_graph.add_edge(hulls[S2][-1],hulls[S2][0],key=-1,weight=0)

            # find the shortest path
            source, target = hulls[S1][0], hulls[S2][0]  # it's a choice to take 0, but no matter
            try:
                length, path = nx.single_source_dijkstra(self.optimization_graph, source, target=target, weight=weight)
            except nx.NetworkXNoPath:
                self.logger.info("Source " + str(S1) + " and source " + str(S2) + " can't be connected")
                return []
            list_weights = nx.get_edge_attributes(self.optimization_graph, weight)

            # edges to add to connect S1 and S2
            edges_to_add = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                # if the edge between (u,v) is not artificial, we add it
                if list_weights.get((u, v, -1), None) != 0 and list_weights.get((u, v, 0), None) is not None:
                    edges_to_add.append((u, v, 0))
                if list_weights.get((v, u, -1), None) != 0 and list_weights.get((v, u, 0), None) is not None:
                    edges_to_add.append((v, u, 0))
            list_edges_to_add[(S1, S2)] = (length, edges_to_add)

            # change weight of edges
            for i in range(len(hulls[S1])-1):
                u,v = hulls[S1][i], hulls[S1][i+1]
                self.optimization_graph.remove_edge(u,v,key=-1)
            self.optimization_graph.remove_edge(hulls[S1][-1],hulls[S1][0],key=-1)
            for i in range(len(hulls[S2])-1):
                u,v = hulls[S2][i], hulls[S2][i+1]
                self.optimization_graph.remove_edge(u,v,key=-1)
            self.optimization_graph.remove_edge(hulls[S2][-1],hulls[S2][0],key=-1)


        # 4. choice of best edges to add (Kruskal)
        G = nx.Graph()
        for (S1, S2) in list_edges_to_add:
            (length, _) = list_edges_to_add[(S1, S2)]
            if not G.has_node(S1):
                G.add_node(S1)
            if not G.has_node(S2):
                G.add_node(S2)
            G.add_edge(S1, S2, weight=length)

        reduced_list_edges_to_add = set()
        T = nx.minimum_spanning_tree(G)
        for u, v in T.edges:
            if (u, v) in list_edges_to_add:
                reduced_list_edges_to_add = reduced_list_edges_to_add.union(set(list_edges_to_add[(u, v)][1]))
            if (v, u) in list_edges_to_add:
                reduced_list_edges_to_add = reduced_list_edges_to_add.union(set(list_edges_to_add[(v, u)][1]))

        self.logger.info('end connecting graph in ' + str(time.time() - debut) + ' s')
        return list(reduced_list_edges_to_add)

    @staticmethod
    def clean_flow_cycles(flows: dict):
        """Remove the sub-optimal flow cycles allowed with the flow conservation. Flows dictionnary is modified
         inplace."""
        for e, flow in flows.items():
            if flow > 0:
                reversed_e = (e[1], e[0], *e[2:])
                if reversed_e in flows and flows[reversed_e] > 0:
                    reversed_flow = flows[reversed_e]
                    cycle_flow = min(flow, reversed_flow)
                    flows[e] -= cycle_flow
                    flows[reversed_e] -= cycle_flow

    # -------------- NLP methods 
    def load_conf(self):
        """ loads the parameters defined in the config.ini in self.conf to prepare the NLP optimization"""
        conf = configparser.ConfigParser()
        conf.read(self.conf_path)
        params = self.conf
        for s in conf.sections():
            for p in conf[s]:
                params[p.upper()] = eval(conf.get(s,p))
        self.conf = params
        if self.energy == "Heating":
            T = self.conf['SUPPLY_HEAT_TEMPERATURE']
        if self.energy == "Cooling":
            T = self.conf['SUPPLY_COOL_TEMPERATURE']
        
        # piecewise linear functions
        self.conf['CP'] = CP(T)
        self.conf['RHO'] = RHO(T)

        # REGRESSIONS
        if self.energy == "Heating":
            self.conf['A_HEAT_TRANSIT_COEF'], self.conf['B_HEAT_TRANSIT_COEF'] = \
                HEAT_LOSS_COST((self.conf['SUPPLY_HEAT_TEMPERATURE']+self.conf['RETURN_HEAT_TEMPERATURE'])/2)
        if self.energy == "Cooling":
            self.conf['A_COOL_TRANSIT_COEF'], self.conf['B_COOL_TRANSIT_COEF'] = \
                HEAT_LOSS_COST((self.conf['SUPPLY_COOL_TEMPERATURE']+self.conf['RETURN_COOL_TEMPERATURE'])/2)
        self.conf['A_LINEAR_COST'], self.conf['B_LINEAR_COST'] = CONSTRUCTION_COST()
        self.conf['A_MAX_VELOCITY'], self.conf['B_MAX_VELOCITY'] = MAX_VELOCITY()

    def convert_power_to_mass_flow(self, power_mw):
        if self.energy == "Heating":
            mass_flow = (power_mw * 1e6) / (self.conf['CP']\
                * (self.conf['SUPPLY_HEAT_TEMPERATURE'] - self.conf['RETURN_HEAT_TEMPERATURE']))
        if self.energy == "Cooling":
            mass_flow = (power_mw * 1e6) / (self.conf['CP']\
                * (self.conf['RETURN_COOL_TEMPERATURE'] - self.conf['SUPPLY_COOL_TEMPERATURE']))
        return mass_flow

    def convert_mass_flow_to_power(self, mass_flow):
        if self.energy == "Heating":
            power_mw = mass_flow * 1e-6 * self.conf['CP'] * \
                (self.conf['SUPPLY_HEAT_TEMPERATURE'] - self.conf['RETURN_HEAT_TEMPERATURE'])
        if self.energy == "Cooling":
            power_mw = mass_flow * 1e-6 * self.conf['CP'] * \
                (self.conf['RETURN_COOL_TEMPERATURE'] - self.conf['SUPPLY_COOL_TEMPERATURE'])
        return power_mw

    def get_params(self, network_frame, peak_consumption):
        lengths = nx.get_edge_attributes(network_frame, config.EDGE_LENGTH_KEY)
        Length, Outflow, Supply_Max_Inflow = {}, {}, {}
        sources = set(n for n,d in network_frame.nodes(data = True) if \
                        config.NODE_TYPE_KEY in d and d[config.NODE_TYPE_KEY] == config.SUPPLY_NODE_TYPE)
        connected_buildings = set(n for n,d in network_frame.nodes(data =True) if \
                                        config.NODE_TYPE_KEY in d and d[config.NODE_TYPE_KEY] == config.BUILDING_NODE_TYPE)
        # IMPORTANT : edges between a source and a junction must have the form (source, junction)
        # edges between a building and junction must have the form (junction, building)
        for key in lengths:
            u, v = key[0], key[1]
            if (v,u) not in Length:
                if v in sources: Length[(v,u)] = max(lengths[key],1e-5) # we don't want a length of zero
                else: Length[(u,v)] = max(lengths[key],1e-5)
        for s in sources:
            Supply_Max_Inflow[s] = self.convert_power_to_mass_flow(network_frame.nodes[s][config.SUPPLY_POWER_CAPACITY_KEY])
        for b in connected_buildings:
            if self.energy == "Heating":
                Outflow[b] = self.convert_power_to_mass_flow(peak_consumption[b])
            if self.energy == "Cooling":
                Outflow[b] = self.convert_power_to_mass_flow(peak_consumption[b])
        GraphParam = {}
        GraphParam["LENGTH"] = Length
        GraphParam["ELEVATION"] = nx.get_node_attributes(network_frame, config.NODE_ELEVATION_KEY)
        GraphParam["OUTFLOW"] = Outflow
        GraphParam["SUPPLY_MAX_INFLOW"] = Supply_Max_Inflow
        return GraphParam

    def get_consumption_and_capacities_from_csv(self, graph, csv_file):
        consumption_data, capacity_data = pd.DataFrame(), pd.DataFrame()
        csv_data = pd.read_csv(csv_file, sep=";",decimal=',')
        L = len(csv_data)
        for n, data in graph.nodes(data=True):
            if data.get(config.NODE_TYPE_KEY,None) == config.BUILDING_NODE_TYPE:
                consumption_data[n] = data[config.BUILDING_CONSUMPTION_KEY]/max(csv_data[data[config.BUILDING_USE_KEY]])*csv_data[data[config.BUILDING_USE_KEY]]
            if data.get(config.NODE_TYPE_KEY,None) == config.SUPPLY_NODE_TYPE:
                capacity_data[n] = pd.Series([data[config.SUPPLY_POWER_CAPACITY_KEY]]*L)

        return consumption_data.dropna(), capacity_data.dropna()

    def get_annual_peak_consumption(self, consumption_data):
        index_tot_consumption = pd.concat([consumption_data[n] for n in consumption_data], axis=1).sum(axis=1).idxmax(axis=0)
        return {n:consumption_data[n].loc[index_tot_consumption] for n in consumption_data}

    def fill_edges_with_NLP(self, NLP_Output):
        Diameter = NLP_Output.get("Diameter", {})
        Velocity = NLP_Output.get("Velocity", {})
        Pressure = NLP_Output.get("Pressure", {})
        MassFlow = NLP_Output.get("MassFlow", {})
        PressureFriction = NLP_Output.get("PressureFriction", {})
        #print(PressureFriction)
        ConstructionCost = NLP_Output.get("ConstructionCost", {})
        if self.energy == "Heating":
            HeatLossCost = NLP_Output.get("HeatLossCost", {})
        if self.energy == "Cooling":
            CoolLossCost = NLP_Output.get("CoolLossCost", {})
        PumpingCost = NLP_Output.get("PumpingCost", {})

        for u,v in self.solution_graph.edges:
            if self.solution_graph.edges[u, v][config.EDGE_LENGTH_KEY] > 0:
                # fill diameter
                if (u, v) in Diameter: 
                    self.solution_graph.edges[u, v][config.PIPE_DIAMETER_KEY] = round(Diameter[(u, v)]*10)/10
                elif (v, u) in Diameter:
                    self.solution_graph.edges[u, v][config.PIPE_DIAMETER_KEY] = round(Diameter[(v, u)]*10)/10
                else:
                    self.solution_graph.edges[u, v][config.PIPE_DIAMETER_KEY] = 0

                # fill velocity
                if (u, v) in Velocity: 
                    self.solution_graph.edges[u, v][config.VELOCITY_KEY] = Velocity[(u, v)]
                elif (v, u) in Velocity:
                    self.solution_graph.edges[u, v][config.VELOCITY_KEY] = -Velocity[(v, u)]
                else:
                    self.solution_graph.edges[u, v][config.VELOCITY_KEY] = 0

                # fill construction and heat/cool loss costs
                if (u, v) in ConstructionCost: 
                    self.solution_graph.edges[u, v][config.CONSTRUCTION_COST_KEY] = ConstructionCost[(u, v)]
                elif (v, u) in ConstructionCost: 
                    self.solution_graph.edges[u, v][config.CONSTRUCTION_COST_KEY] = ConstructionCost[(v, u)]
                else: 
                    self.solution_graph.edges[u, v][config.CONSTRUCTION_COST_KEY] = 0
                if self.energy == "Heating":
                    if (u, v) in HeatLossCost: 
                        self.solution_graph.edges[u, v][config.HEAT_LOSS_COST_KEY] = HeatLossCost[(u, v)]
                    elif (v, u) in HeatLossCost: 
                        self.solution_graph.edges[u, v][config.HEAT_LOSS_COST_KEY] = HeatLossCost[(v, u)]
                    else:
                        self.solution_graph.edges[u, v][config.HEAT_LOSS_COST_KEY] = 0
                if self.energy == "Cooling":
                    if (u, v) in CoolLossCost:
                        self.solution_graph.edges[u, v][config.COOL_LOSS_COST_KEY] = CoolLossCost[(u, v)]
                    elif (v, u) in CoolLossCost:
                        self.solution_graph.edges[u, v][config.COOL_LOSS_COST_KEY] = CoolLossCost[(v, u)]
                    else:
                        self.solution_graph.edges[u, v][config.COOL_LOSS_COST_KEY] = 0

                # fill average pressure
                if (u, v) in Pressure:
                    self.solution_graph.edges[u, v][config.AVERAGE_PRESSURE_KEY] = Pressure[(u, v)]
                elif (v, u) in Pressure:
                    self.solution_graph.edges[u, v][config.AVERAGE_PRESSURE_KEY] = Pressure[(v, u)]
                else:
                    self.solution_graph.edges[u, v][config.AVERAGE_PRESSURE_KEY] = 0

                # fill pumping costs
                if u in PumpingCost: 
                    self.solution_graph.edges[u, v][config.PUMPING_COST_KEY] = PumpingCost[u]
                elif v in PumpingCost:
                    self.solution_graph.edges[u, v][config.PUMPING_COST_KEY] = PumpingCost[v]
                else:
                    self.solution_graph.edges[u, v][config.PUMPING_COST_KEY] = 0

                # actualize flow values
                if (u, v) in MassFlow:
                    self.solution_graph.edges[u, v][config.SOLUTION_POWER_FLOW_KEY] = \
                        self.convert_mass_flow_to_power(MassFlow[(u, v)])
                elif (v, u) in MassFlow:
                    self.solution_graph.edges[u, v][config.SOLUTION_POWER_FLOW_KEY] = \
                        -self.convert_mass_flow_to_power(MassFlow[(v, u)])
                else:
                    self.solution_graph.edges[u, v][config.SOLUTION_POWER_FLOW_KEY] = 0

    # -------------- Preprocess NLP methods 
    def calculate_consumption_predecessors_nodes(self, G, consumption_data, capacity_data, lb_flow, end_nodes):
        ''' simplify all the simple final branches until having no end nodes. '''
        #draw_graph(G, pos)

        # terminal case
        if len(end_nodes) == 0:
            for n in G.nodes():
                if G.node[n].get(config.NODE_TYPE_KEY,None) != config.SUPPLY_NODE_TYPE:
                    return False
            return True
        else:
            pre_end_nodes = set()

            # calculate all the terminal branches {pre_end_nodes: {end_node1, end_node2}}
            for n in end_nodes:
                p = list(set(G.predecessors(n)).union(set(G.successors(n))))[0]

                # update consumption data
                consumption_data[p] = consumption_data.get(p,0) + consumption_data.get(n,0)
                    
                # the flow lb is the max over the time of the consumption
                lb_flow[(p,n)] = max(consumption_data.get(n,[0]))

                # remove the terminal node
                G.remove_node(n)

                # compute pre_end_nodes = next end nodes
                if len(set(G.predecessors(p)).union(set(G.successors(p))))==1:
                    if G.node[p].get(config.NODE_TYPE_KEY) != config.SUPPLY_NODE_TYPE:
                        pre_end_nodes.add(p)

            # continue to simplify the graph
            self.calculate_consumption_predecessors_nodes(G, consumption_data, capacity_data, lb_flow, pre_end_nodes)

    def find_needs(self, G, edge, needs_data, consumption_data, forbidden_nodes, max_capacity={}):
        forbidden_nodes.add(edge[0])
        if edge not in needs_data:
            successors = set(G.successors(edge[1]))
            reduced_successors = successors.difference(forbidden_nodes)
            val = consumption_data.get(edge[1],0)
            if len(reduced_successors) > 0:
                for s in reduced_successors:
                    val = val + self.find_needs(G, (edge[1],s), needs_data, consumption_data, deepcopy(forbidden_nodes), max_capacity)
            if type(val) != int:
                needs_data[edge] = pd.concat([val, pd.Series([max_capacity.get((*edge,0), pd.np.inf)]*len(val))],axis=1).min(axis=1)
            else:
                needs_data[edge] = val
        return needs_data[edge]

    def find_surplus(self, G, edge, surplus_data, consumption_data, capacity_data, forbidden_nodes, max_capacity={}):
        forbidden_nodes.add(edge[1])
        if edge not in surplus_data:
            predecessors = set(G.predecessors(edge[0]))
            reduced_predecessors = predecessors.difference(forbidden_nodes)
            if G.node[edge[0]].get(config.NODE_TYPE_KEY,None) == config.SUPPLY_NODE_TYPE:
                val = capacity_data[edge[0]]
            else:
                val = - consumption_data.get(edge[0],0)
            if len(reduced_predecessors) > 0:
                for p in reduced_predecessors:
                    val = val + self.find_surplus(G, (p,edge[0]), surplus_data, consumption_data, capacity_data, deepcopy(forbidden_nodes), max_capacity)
            if type(val) != int:
                surplus_data[edge] = pd.concat([val, pd.Series([max_capacity.get((*edge,0), pd.np.inf)]*len(val))],axis=1).min(axis=1)
            else:
                surplus_data[edge] = val
        return surplus_data[edge]

    # ============================================= Optimization methods ===============================================

    def optimize_with_dssp_julia(self, graph, network_objective, old_buildings, postprocess=True):
        """Solve the Fixed Charge Network Flow Problem using the Dynamic Slope Scaling Procedure from Dukwon Kim,
        Panos M. Pardalos in "A solution approach to the fixed charge network flow problem using a dynamic slope scaling
        procedure" (1998). The model and the procedure is defined in the Julia language in the file 'DSSP.jl'. We use
        here the python library PyJulia to call julia and to wrap input and output variables.
        :return: tuple containing :
            flows : dict. Values of the flow on each edge.
            obj_val : float. Value of the optimization objective, i.e. the total cost of the network.
        """
        # === Start data initialization
        data_init_start = time.time()
        # === Start the algorithm
        all_nodes = set(graph.nodes())
        costs = nx.get_edge_attributes(graph, config.EDGE_COST_KEY)
        heat_demand = nx.get_node_attributes(graph, config.BUILDING_CONSUMPTION_KEY)
        production = nx.get_node_attributes(graph, config.SUPPLY_POWER_CAPACITY_KEY)
        capacities = {}
        #print(costs)
        #print(heat_demand)
        #print(production)
        if self.old_network_graph is not None and self.modify_old_network:
            for e,c in self.old_capacity.items():
                if e in graph.edges(keys=True):
                    capacities[e] = c+1e-5
                elif (e[1],e[0],e[2]) in graph.edges(keys=True):
                    capacities[(e[1],e[0],e[2])] = c+1e-5

        self.logger.info("\tData initialization time: %.2fs" % (time.time() - data_init_start))
        # === Set up instance of julia :
        self.logger.info("Setting up julia call...")
        julia_instantiate_start = time.time()
        optimizer_directory = os.path.dirname(os.path.realpath(__file__))
        with JuliaQgisInterface() as j:
            j.include(os.path.join(optimizer_directory, "DSSP.jl"))
            j.using("Main.DSSP: optimize_with_DSSP")
            assert (hasattr(j, "optimize_with_DSSP"))
            self.logger.info("\tJulia instantiating time: %.2fs" % (time.time() - julia_instantiate_start))
            dssp_start = time.time()
            #print("old_buildings", old_buildings)
            best_solution, best_cost = j.optimize_with_DSSP(network_objective, all_nodes, costs, heat_demand,
                                                            production,
                                                            capacities,
                                                            old_buildings,
                                                            self.logger.info,
                                                            postprocess)
            self.logger.info("\tDSSP run time: %.2fs" % (time.time() - dssp_start))
        return best_solution, best_cost

    def optimize_pipe_size(self, network_frame, lb_diam, peak_consumption, max_capacity={}):
        """Optimize the diameter layout of the network's main line based on connected building's
        consumption during the peak. Non linear and nonconvex problem to be solved with Artelys KNITRO
        or open-source solver Ipopt.
        Techno-economic optimization: we minimize annualised costs of construction, heat loss and pumping.
        The model and the procedure is defined in the Julia language in the file 'NLP_variable_flows.jl'"""

        # Start data initialization
        GraphParam = self.get_params(network_frame, peak_consumption)
        GraphParam['LB_DIAM'] = lb_diam

        # In case of old network
        if len(max_capacity) > 0:
            GraphParam['MAX_CAPACITY'] = {}
            for e, val in max_capacity.items():
                GraphParam['MAX_CAPACITY'][(e[0],e[1])] = val
        else:
            GraphParam['MAX_CAPACITY'] = {}
        
        # Start the algorithm
        # Use NLP module
        optimizer_directory = os.path.dirname(os.path.realpath(__file__))
        with JuliaQgisInterface() as j:
            j.include(os.path.join(optimizer_directory, "NLP", "NLP_variable_flows.jl"))
            j.using("Main.NLP: find_optimal_physical_parameters")
            assert (hasattr(j, "find_optimal_physical_parameters"))
            nlp_start = time.time()
            NLP_Output, status = j.find_optimal_physical_parameters(GraphParam,
                                                                    self.conf,
                                                                    self.solver_log_file,
                                                                    self.energy,
                                                                    self.logger.info)
            nlp_end = time.time()
            self.logger.info("nlp time: %s" % str(nlp_end - nlp_start))
        return NLP_Output, status

if __name__ == "__main__":
    results_dir = "optimizer/automatic_design/results/"
    # Load optimization graph
    optimization_graph = nx.read_gpickle(os.path.join(results_dir, "optimization_graph.gpickle"))
    supplies = nx.get_node_attributes(optimization_graph, config.SUPPLY_POWER_CAPACITY_KEY)
    for s in supplies:
        optimization_graph.nodes[s][config.SUPPLY_POWER_CAPACITY_KEY] *= 1000
    self = ADNetworkOptimizer(optimization_graph)

    self.logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    self.logger.addHandler(stream_handler)

    consumptions = nx.get_node_attributes(optimization_graph, config.BUILDING_CONSUMPTION_KEY)
    total_consumption = sum(consumptions.values())
    self.network_objective = total_consumption * 0.8
    assert (sum(
        nx.get_node_attributes(optimization_graph, config.SUPPLY_POWER_CAPACITY_KEY).values()) > self.network_objective)
    self.optimize()
    # gnx.export_graph_as_shape_file(self.solution_graph, results_dir, fiona_cast=True)
