import logging
import os
import math
import networkx as nx
import geonetworkx as gnx
from .. import config
from ...exception_utils import DHCOptimizerException

class MDNetworkOptimizer:
    """This objects implements methods for solving the Steiner Tree Problem. It takes as input an optimization graph and
    optionally an existing network graph."""

    def __init__(self, optimization_graph=None):
        self.logger = logging.getLogger(__name__)
        self.optimization_graph = optimization_graph
        self.old_network_graph = None
        # Output:
        self.solution_graph = None

    def check_is_ready(self):
        """Check that all inputs have been set and the optimization phase is ready to be run."""
        self.logger.info("Checking optimization inputs have been set for manual design.")
        if self.optimization_graph is None:
            raise RuntimeError("The optimization graph needs to be defined in order to optimize the network.")

    def check_infeasibility(self):
        """Check that the input data is consistent, otherwise the problem is infeasible and the optimization phase must
        not be run."""
        self.logger.info("Checking infeasibility for manual design.")
        ccs = list(nx.connected_components(self.optimization_graph.to_undirected(as_view=True)))
        nb_connected_components = len(ccs)
        if nb_connected_components > 1:
            raise DHCOptimizerException("The given optimization graph has several connected"
                                        " components (%d)" % nb_connected_components)

    def optimize(self):
        """Main method to run each step one by one."""
        self.check_is_ready()
        self.check_infeasibility()
        solution_graph, obj_val = self.find_shortest_network_with_ADH((self.old_network_graph is not None))
        self.solution_graph = gnx.GeoMultiGraph(solution_graph, crs=self.optimization_graph.crs)

    def find_shortest_network_with_ADH(self, extension):
        """Solves the Steiner tree problem in a graph.
        The resolution is based on the minimum average distance heuristic (ADH).

        extension = True if the resulting network should contain an already
        existing network

        1. Initialization of the forest F (= set of trees) with terminal nodes

        2. Loop : while there is more than one tree in F:
            - For each node n in G, sort the trees in F by increasing distance from
              (distance of the shortest path) and compute the minimum of the average
              distance function : val
            - Choose the node n0 that minimizes val
            - In F, select the 2 closest trees T1 and T2 from n0, join them through
              the shortest paths with n0 : T'
            - Update F by removing T1 et T2 and adding T' instead 

        3. The last tree is our Steiner tree 
           Remove non-terminals of degree 1
        """

        self.logger.info("Solving with the Minimum Average Distance Heuristic:")
        self.logger.info("extension mode activated: %s" % str(extension))
        self.logger.info("Steiner preprocessing start")
        G, terminal_nodes, link = self.preprocessing_steiner(extension)
        intersect_terminal_nodes = set()
        for tn in terminal_nodes:
            if G.node[tn].get(config.NODE_TYPE_KEY, None) == config.BUILDING_NODE_TYPE:
                intersect_terminal_nodes.add(list(G.neighbors(tn))[0])
                G.remove_node(tn)
        terminal_nodes = intersect_terminal_nodes
        self.logger.info("Steiner preprocessing end")

        # Research of the shortest paths
        self.logger.info("Heuristic run start")
        dictpathlength = dict(nx.shortest_path_length(G, weight=config.EDGE_COST_KEY))
        
        # 1. 
        forest = []
        for node in terminal_nodes:
            temp = nx.Graph()
            temp.add_node(node)
            forest.append(temp)
        nb_terminals = len(terminal_nodes)
        nb_trees = nb_terminals

        # little check
        if nb_trees == 0:
            raise ValueError("There isn't building to connect")

        # creation of a dictionnary {node:{tree:distance,...},...} which contains the minimal distance of a node to a tree
        path_length_node_to_tree = {}
        for node in G.nodes():
            path_length_node_to_tree[node] = {}
            for i_tree in range(len(forest)):
                # for the moment, it's easy: there is only one node in each tree
                node_tree = list(forest[i_tree].nodes())[0]
                path_length_node_to_tree[node][i_tree] = (node_tree,dictpathlength[node][node_tree])

        # trees which can be used
        set_trees = set(range(len(forest)))

        # 2. Loop 
        while nb_trees > 1:
            function_min = math.inf
            for node in G.nodes():
                # we want to find the two trees with the shortest distance to node
                # first_least = [index_of_tree, the_node_of_the_tree_to_connect, minimal_distance]
                first_least, second_least = [None, None, math.inf], [None, None, math.inf]
                for i_tree in set_trees:
                    # minimal distance between node to tree[i_tree]
                    v, length = path_length_node_to_tree[node][i_tree]
                    # update of the two closest tree from node
                    if length < first_least[2]:
                        first_least, second_least = [i_tree, v, length], first_least
                    elif length < second_least[2]:
                        second_least = [i_tree, v, length]
                
                val_function = (second_least[2]+first_least[2])/2
                # update the minimum of f on the nodes, with the corresponding closest trees and the connections
                if val_function < function_min:
                    function_min = val_function
                    central_node = node
                    [i_tree1, connection1, _], [i_tree2, connection2, _] = first_least, second_least

            # fusion
            newtree = nx.union(forest[i_tree1], forest[i_tree2])
            if central_node != connection1:
                path1 = nx.shortest_path(G, source=central_node, target=connection1, weight='cost')
                newtree.add_edges_from([(path1[k], path1[k+1]) for k in range(len(path1) - 1)])
            else:
                path1 = [connection1]
            if central_node != connection2:
                path2 = nx.shortest_path(G, source=central_node, target=connection2, weight='cost')
                newtree.add_edges_from([(path2[k], path2[k+1]) for k in range(len(path2) - 1)])
            else:
                path2 = [connection2]

            # update of the dictionnary path_length_node_to_tree
            for node in G.nodes():   
                # first, find the minimal distance between node and newtree             
                v1, dist1 = path_length_node_to_tree[node][i_tree1]
                v2, dist2 = path_length_node_to_tree[node][i_tree2]
                v3, dist3 = None, math.inf
                for node1 in path1:
                    if dictpathlength[node][node1] < dist3:
                        v3, dist3 = node1, dictpathlength[node][node1]
                for node2 in path2:
                    if dictpathlength[node][node2] < dist3:
                        v3, dist3 = node2, dictpathlength[node][node2]
                # then, compute the distance and the node of the tree to connect
                if dist1 == min(dist1,dist2,dist3):
                    path_length_node_to_tree[node][len(forest)] = (v1, dist1)
                elif dist2 == min(dist1,dist2,dist3):
                    path_length_node_to_tree[node][len(forest)] = (v2, dist2)
                else:
                    path_length_node_to_tree[node][len(forest)] = (v3, dist3)

            # update of the forest
            forest.append(newtree)
            forest[i_tree1] = None
            forest[i_tree2] = None
            # update of the usable trees
            set_trees.add(len(forest)-1)
            set_trees.remove(i_tree1)
            set_trees.remove(i_tree2)
            nb_trees -= 1
            if nb_trees % 10 == 0:
                self.logger.info('%.1f %% of terminal points connected' %
                             ((nb_terminals - nb_trees) / (nb_terminals - 1) * 100))

        # 3. 
        solution_steiner = forest[list(set_trees)[0]]
        for node in solution_steiner.nodes:
            if node not in terminal_nodes and solution_steiner.degree(node) < 2:
                solution_steiner.remove_node(node)
        self.logger.info("Heuristic run end")

        self.logger.info("Steiner postprocessing start")
        sol_tree = self.postprocessing_steiner(extension, solution_steiner, link)
        self.logger.info("Steiner postprocessing end")

        # return a directed graph with attributes
        length = 0
        edges_to_keep = []
        for u, v, k in self.optimization_graph.edges:
            if sol_tree.has_edge(u, v) or sol_tree.has_edge(v, u):
                edges_to_keep.append((u, v, k))
                length += self.optimization_graph.edges[u, v, k]['cost']
            if self.optimization_graph.node[u][config.NODE_TYPE_KEY] == config.BUILDING_NODE_TYPE \
            or self.optimization_graph.node[v][config.NODE_TYPE_KEY] == config.BUILDING_NODE_TYPE:
                edges_to_keep.append((u, v, k))
                length += self.optimization_graph.edges[u, v, k]['cost']

        solution_graph = nx.MultiGraph(self.optimization_graph.edge_subgraph(edges_to_keep))
        return solution_graph, length/2

    def preprocessing_steiner(self, extension):
        """Pre-process the optimization graph before the optimization phase to simplify an existing network as a single
        node."""
        G = nx.Graph(self.optimization_graph)
        terminal_nodes = [node for node, data in G.nodes(data=True)
                          if data.get(config.NODE_TYPE_KEY, None) == config.BUILDING_NODE_TYPE]
        link = {}
        if not extension:
            return G, terminal_nodes, link
        old_Graph = self.old_network_graph
        H = nx.Graph(G.subgraph([n for n in G.nodes if n not in old_Graph.nodes]))
        H_connected_components = list(nx.connected_components(H))
        old_junctions = [n for n, d in old_Graph.nodes(data=True) if d['nodetype'] == 'junction']
        # Remove the old buildings from the terminal nodes list
        for node in [n for n in terminal_nodes if n in old_Graph.nodes]:
            terminal_nodes.remove(node)
        # Building the Graph on which we will use the heuristic
        for node in old_junctions:
            neighbors = [n for n in G.neighbors(node) if n in H.nodes]
            for cc in H_connected_components:
                sub_neighbors = [n for n in neighbors if n in cc]
                if len(sub_neighbors) == 0:
                    continue
                dist, closest_neighbor = min([[G.edges[node, n]['cost'], n] for n in sub_neighbors], key=lambda t: t[0])
                if closest_neighbor not in link:
                    link[closest_neighbor] = [node, dist]
                    continue
                if dist < link[closest_neighbor][1]:
                    link[closest_neighbor] = [node, dist]
        # Add a node corresponding to the old Graph and connected with the selected neighbors
        terminal_nodes.append('OldNetworkNode')
        for n in link:
            H.add_edge('OldNetworkNode', n, cost=link[n][1])
        G = H.copy()
        return G, terminal_nodes, link

    def postprocessing_steiner(self, extension: bool, solution_steiner: nx.Graph, link: dict):
        """
        Reset the initial optimization graph structure by re-adding the existing network.

        :param extension: Boolean to indicate if there is an existing network in the problem.
        :param solution_steiner: Solution graph obtained after the optimization phase.
        :param link: Dictionary of links between the existing network and the street graph.
        :return: The modified solution graph.
        """
        sol_tree = solution_steiner
        if not extension:
            return sol_tree
        connections_to_old = [n for n in sol_tree.neighbors('OldNetworkNode')]
        sol_tree.remove_node('OldNetworkNode')
        for node in connections_to_old:
            sol_tree.add_edge(node, link[node][0])
        old_Graph = nx.Graph(self.old_network_graph)
        sol_tree.add_edges_from(old_Graph.edges)
        return sol_tree


if __name__ == "__main__":
    results_dir = "../../optimizer/manual_design/results/"
    import geonetworkx as gnx
    optimization_graph = gnx.read_gpickle(os.path.join(results_dir, "optimization_graph.gpickle"))
    old_network_graph = gnx.read_gpickle(os.path.join(results_dir, "old_network_graph.gpickle"))
    self = MDNetworkOptimizer(optimization_graph, None)  # old_network_graph)

    self.logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    stream_handler.setFormatter(formatter)
    self.logger.addHandler(stream_handler)
    extension = True

    self.optimize()
