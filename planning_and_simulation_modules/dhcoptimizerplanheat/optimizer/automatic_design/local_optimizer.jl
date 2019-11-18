if !isdefined(:FCFP)
    include("FCFP.jl")
end


"""
The ``LocalOptimizer`` module define methods to optimize locally a Fixed
Cost Flow Problem (FCFP) from an intial solution. It consists mainly by
rerouting main flow arteries. A flow artery is defined as a sequence of
edges where the flow is constant (for now strictly more than one edge).
The optimizer tries to find a path replacing the artery but with a smallest
cost. To do that it computes the shortest path between some nodes that are
already visited by the flow (e.g. parent nodes of the artery) and the nodes
that the artery is sustaining. If such a path is found, the artery will be
removed from the flow graph and replaced by the found path.

For now, the hypothesis of the optimizer are the following:
    * The flow graph is a set of DAG (directed acyclic graphs)
    * Edges have no capacity
    * The initial solution is feasible

"""
module LocalOptimizer



    #include("DSSP.jl")
    include("graph_utils.jl")
    import FCFP.FCFPInstance
    using DataStructures

    # TODO: catch errors (is not a DAG etc), and except with returning the initial flows

    mutable struct LocalOptimizerInstance
        init_flows::FlowDictType
        working_flows::FlowDictType
        flows::FlowDictType
        optimization_graph::MultiDiGraph
        fcfp::FCFPInstance
        costs::Dict{EdgeType, WeightType}
        roots::Array{VertexType, 1}
        treated_arteries::Set
        logger
    end

    function _init_loi(flows::Dict, fcfp::FCFPInstance, logger)
        optimization_graph = MultiDiGraph(keys(flows))
        i_flows = FlowDictType(flows)
        flow_dag = get_flow_dag(optimization_graph, i_flows)
        roots = [n for n in get_nodes(flow_dag) if has_no_parent(flow_dag, n)]
        treated_arteries = Set()
        costs = Dict{EdgeType, WeightType}()
        sizehint!(costs, length(fcfp.fixed_costs))
        for (u, v, _) in keys(fcfp.fixed_costs)
            costs[(u, v)] = minimum([fcfp.fixed_costs[(u, v, k)] for k=optimization_graph.succ[u][v]])
        end
        return LocalOptimizerInstance(i_flows, FlowDictType(flows), FlowDictType(flows),
                                        optimization_graph, fcfp, costs,
                                        roots, treated_arteries, logger)
    end

    LocalOptimizerInstance(flows::Dict, fcfp::FCFPInstance, logger) = _init_loi(flows, fcfp, logger)


    function validate_move(loi::LocalOptimizerInstance)
        loi.flows = copy(loi.working_flows)
    end

    function optimize_locally(flows::Dict, fcfp::FCFPInstance, logger=println) :: Dict
        start = time()
        loi = LocalOptimizerInstance(flows, fcfp, logger)
        initial_cost = sum(loi.fcfp.fixed_costs[e] for (e, f) in loi.flows if f > 0)
        clean_flow_two_cycles(loi.working_flows)
        break_cycles(loi, loi.working_flows)
        validate_move(loi)
        while replace_arteries(loi)
            gain = initial_cost - sum(loi.fcfp.fixed_costs[e] for (e, f) in loi.flows if f > 0)
            loi.logger("Cost gain: $(gain)")
        end
        gain = initial_cost - sum(loi.fcfp.fixed_costs[e] for (e, f) in loi.flows if f > 0)
        optimization_time = time() - start
        loi.logger("Arteries flows rerouting postprocess: gain=$(gain),  time: $(optimization_time)")
        if check_solution(loi, loi.flows)
            return loi.flows
        else
            loi.logger("Local optimization failed")
            return loi.init_flows
        end
    end

    function replace_arteries(loi::LocalOptimizerInstance) :: Bool
        flow_dag = get_flow_dag(loi.optimization_graph, loi.flows)
        arteries = get_flow_arteries(loi, flow_dag)
        roots_descendants = Array{Set{VertexType}, 1}([descendants(flow_dag, r, false) for r in loi.roots])
        roots_marginal_capacity = [loi.fcfp.production[r] - sum(get(loi.fcfp.heat_demand, n, 0.0)
                                                                for n in roots_descendants[r_index])
                                   for (r_index, r) in enumerate(loi.roots)]
        while !isempty(arteries)
            a = dequeue!(arteries)
            # determine sub tree
            end_node = last(a)[2]
            sub_tree_nodes = descendants(flow_dag, end_node, false)
            if isempty(sub_tree_nodes)
                continue
            end
            sub_tree_demand = sum(get(loi.fcfp.heat_demand, n, 0.0) for n in sub_tree_nodes)
            # determine parent sub tree
            start_node = first(a)[1]
            current_roots_indexes = Set{Int64}()
            other_roots_indexes = Set{Int64}()
            for (d_index, d) in enumerate(roots_descendants)
                if (start_node in d)
                    push!(current_roots_indexes, d_index)
                elseif (roots_marginal_capacity[d_index] >= sub_tree_demand)
                    push!(other_roots_indexes, d_index)
                end
            end
            concerned_sub_trees_indexes = union(current_roots_indexes, other_roots_indexes)
            parent_dag_trees_nodes = cascade_union([roots_descendants[d_index] for d_index in concerned_sub_trees_indexes])
            parent_dag_trees_nodes = setdiff(parent_dag_trees_nodes, union(sub_tree_nodes,
                                                                           Set(e[2] for e in a)))
            if isempty(parent_dag_trees_nodes)
                continue
            end
            # Add 0-weight edges in the sub-graph
            modified_costs = add_zero_weight_edges_from_nodes(sub_tree_nodes, loi.costs)
            path, cost = dijkstra_multisource(loi.optimization_graph,
                                              parent_dag_trees_nodes,
                                              end_node,
                                              modified_costs)
            edge_like_path = get_edge_like_path(path, loi.optimization_graph, loi.fcfp.fixed_costs)
            if edge_like_path != a
                potential_cycle_creation = false
                if any((n != end_node) && (n in sub_tree_nodes) for n in path)
                    potential_cycle_creation = true
                end
                new_start = first(path)
                if any(new_start in roots_descendants[d_index] for d_index in current_roots_indexes)
                    loi.logger("Moving flow inside current dag")
                    reroute_artery(loi, a, edge_like_path, flow_dag, potential_cycle_creation)
                else
                    loi.logger("Moving flow to another dag")
                    new_roots_candidates = Set{VertexType}([loi.roots[r] for r in other_roots_indexes if new_start in roots_descendants[r]])
                    current_roots = Set{VertexType}([loi.roots[r] for r in current_roots_indexes])
                    move_artery_to_other_dag(loi, a, edge_like_path, flow_dag, current_roots, new_roots_candidates, potential_cycle_creation)
                end
                validate_move(loi)
                return true
            else
                push!(loi.treated_arteries, a)
            end
        end
        return false
    end

    function reroute_artery(loi::LocalOptimizerInstance, a::Array{MultiEdgeType, 1},
                            new_a::Array{MultiEdgeType, 1}, flow_dag::MultiDiGraph, potential_cycle_creation=false)
        artery_flow = loi.working_flows[first(a)]
        for e in a
            loi.working_flows[e] = zero(WeightType)
        end
        new_start = first(new_a)[1]
        start_node = first(a)[1]
        if new_start != start_node
            lca = lowest_common_ancestor(flow_dag, start_node, new_start)
            if lca === nothing
                throw(ErrorException("Unable to find common ancestor"))
            end
            # 1: Browse back the flow to not show flow in this direction
            if lca != start_node
                back_path, _ = dijkstra_multisource(flow_dag, Set{VertexType}([lca]), start_node, loi.costs)
                edge_back_path = get_edge_like_path(back_path, flow_dag, loi.fcfp.fixed_costs)
                for e in edge_back_path
                    if artery_flow <= loi.working_flows[e]
                        loi.working_flows[e] -= artery_flow
                    else
                        potential_cycle_creation = true
                        loi.working_flows[(e[2], e[1], e[3])] = artery_flow - loi.working_flows[e]
                        loi.working_flows[e] = zero(WeightType)
                    end
                end
            end
            # 2: Browse down the flow to the start of the new artery
            if lca != new_start
                (down_path, _) = dijkstra_multisource(flow_dag, Set{VertexType}([lca]), new_start, loi.costs)
                edge_down_path = get_edge_like_path(down_path, flow_dag, loi.fcfp.fixed_costs)
                for e in edge_down_path
                    loi.working_flows[e] += artery_flow
                end
            end
        end
        for e in new_a
            loi.working_flows[e] += artery_flow  # Adding flow because their may be already a flow on it
        end
        clean_flow_two_cycles(loi.working_flows)
        if potential_cycle_creation
            break_cycles(loi, loi.working_flows, Set{VertexType}([new_start]))
        end
    end

    function move_artery_to_other_dag(loi::LocalOptimizerInstance,
                                      a::Array{MultiEdgeType, 1},
                                      new_a::Array{MultiEdgeType, 1},
                                      flow_dag::MultiDiGraph,
                                      current_roots:: Set{VertexType},
                                      new_roots_candidates::Set{VertexType},
                                      potential_cycle_creation=false)
        artery_flow = loi.working_flows[first(a)]
        for e in a
            loi.working_flows[e] = zero(WeightType)
        end
        # Find path from old root to old start and remove flow
        old_start = first(a)[1]
        residual_artery_flow = artery_flow
        for r in current_roots  # Removing artery flow taking into account multiple roots
            root_flow = sum(loi.working_flows[e] for e in out_edges(flow_dag, r))
            flow_to_remove = min(root_flow, residual_artery_flow)
            (back_path, _) = dijkstra_multisource(flow_dag, Set{VertexType}([r]), old_start, loi.costs)
            edge_back_path = get_edge_like_path(back_path, flow_dag, loi.fcfp.fixed_costs)
            for e in edge_back_path
                loi.working_flows[e] -= flow_to_remove
            end
            residual_artery_flow -= flow_to_remove
            if residual_artery_flow <= 0.0
                break
            end
        end
        # Find path from new root to new start and add flow
        new_start = first(new_a)[1]
        (down_path, _) = dijkstra_multisource(flow_dag, new_roots_candidates, new_start, loi.costs)
        edge_down_path = get_edge_like_path(down_path, flow_dag, loi.fcfp.fixed_costs)
        for e in edge_down_path
            loi.working_flows[e] += artery_flow
        end
        # Set new artery flow
        for e in new_a
            loi.working_flows[e] += artery_flow  # Adding flow because their may be already a flow on it
        end
        # Clean flows
        clean_flow_two_cycles(loi.working_flows)
        if potential_cycle_creation
            break_cycles(loi, loi.working_flows, Set{VertexType}([new_start]))
        end
    end

    function get_edge_like_path(path::Array, graph::MultiDiGraph, costs::Dict) :: Array{MultiEdgeType, 1}
        edge_like_path = Array{MultiEdgeType, 1}()
        for i in 1:(length(path) - 1)
            u, v = path[i], path[i + 1]
            min_edge = (u, v, first(graph.succ[u][v]))
            min_weight = costs[min_edge]
            for k in graph.succ[u][v]
                if costs[(u, v, k)] < min_weight
                    min_edge = (u, v, k)
                    min_weight = costs[min_edge]
                end
            end
            push!(edge_like_path, min_edge)
        end
        return edge_like_path
    end


    function add_zero_weight_edges_from_nodes(nodes::Set{VertexType}, costs::Dict) :: Dict
        modified_costs = copy(costs)
        for (u, v) in keys(costs)
            if (u in nodes) && (v in nodes)
                modified_costs[(u, v)] = zero(WeightType)
                modified_costs[(v, u)] = zero(WeightType)
            end
        end
        return modified_costs
    end

    function remove_zero_weight_edges(graph, added_edges, costs)
        remove_edges!(graph, added_edges)
        for e in added_edges
            delete!(costs, e)
        end
    end


    function cascade_union(sets::Array{Set{T}, 1}) :: Set{T} where {T<:Any}
        u = Set{T}()
        for s in sets
            u = union(u, s)
        end
        return u
    end

    function get_flow_arteries(loi::LocalOptimizerInstance, flow_dag::MultiDiGraph) :: PriorityQueue{Array{MultiEdgeType, 1}, WeightType}
        arteries = PriorityQueue{Array{MultiEdgeType, 1}, WeightType}()
        explored_nodes = Set{VertexType}()
        for r in loi.roots
            nodes_stack = Array{VertexType, 1}([r])
            while !isempty(nodes_stack)
                n = pop!(nodes_stack)
                if n in explored_nodes
                    continue
                end
                push!(explored_nodes, n)
                out_flow_edges = collect(out_edges(flow_dag, n))
                if (length(out_flow_edges) != 1) || (! has_one_parent(flow_dag, n))
                    for e in out_flow_edges
                        push!(nodes_stack, e[2])
                    end
                    continue
                end
                # A new artery is found, explore it in depth
                current_artery = [first(in_edges(flow_dag, n)), out_flow_edges[1]]
                sub_nodes_stack = [out_flow_edges[1][2]]
                while !isempty(sub_nodes_stack)
                    sub_node = pop!(sub_nodes_stack)
                    push!(explored_nodes, sub_node)
                    out_flow_edges = collect(out_edges(flow_dag, sub_node))
                    if (length(out_flow_edges) != 1) || (! has_one_parent(flow_dag, sub_node))
                        # End of the artery
                        artery_cost = - sum(loi.fcfp.fixed_costs[e] for e in current_artery)
                        if current_artery in loi.treated_arteries
                            artery_cost += 1e5
                        end
                        arteries[current_artery] = artery_cost
                        for e in out_flow_edges
                            push!(nodes_stack, e[2])
                        end
                        break
                    else
                        push!(current_artery, out_flow_edges[1])
                        push!(sub_nodes_stack, out_flow_edges[1][2])
                    end
                end
            end
        end
        return arteries
    end

    function sort_arteries(loi::LocalOptimizerInstance, arteries) :: Array
        failed_arteries = []
        new_arteries = []
        for a in arteries
            if a in loi.treated_arteries
                push!(failed_arteries, a)
            else
                push!(new_arteries, a)
            end
        end
        failed_lengths = [sum(loi.fcfp.fixed_costs[e] for e in a) for a in failed_arteries]
        sorted_failed_arteries = [x for (_, x) in sort(collect(zip(failed_lengths, failed_arteries)), rev=true)]
        new_lengths = [sum(loi.fcfp.fixed_costs[e] for e in a) for a in new_arteries]
        sorted_new_arteries = [x for (_, x) in sort(collect(zip(new_lengths, new_arteries)), rev=true)]
        return vcat(sorted_new_arteries, sorted_failed_arteries)
    end

    function get_flow_dag(optimization_graph::MultiDiGraph, flows::FlowDictType) :: MultiDiGraph
        edges_to_keep = [e for (e, f) in flows if f > 0]
        return get_edge_sub_graph(optimization_graph, edges_to_keep)
    end



    """
    Remove the sub-optimal flow 2-cycles allowed with the flow conservation.
    Flows dictionary is modified inplace.
    """
    function clean_flow_two_cycles(flows::FlowDictType)
        for (e, flow) in flows
            if flow > 0
                reversed_e = (e[2], e[1], e[3])
                if (reversed_e in keys(flows)) && (flows[reversed_e] > 0)
                    reversed_flow = flows[reversed_e]
                    cycle_flow = min(flow, reversed_flow)
                    flows[e] -= cycle_flow
                    flows[reversed_e] -= cycle_flow
                end
            end
        end
    end


    """
    Break cycles in a given flow dict by subtracting the minimal flow.
    """
    function break_cycles(loi::LocalOptimizerInstance, flows::FlowDictType,
                          start_nodes=nothing::Union{Void, Set{VertexType}})
        while true
            flow_dag = get_flow_dag(loi.optimization_graph, flows)
            cycle = find_cycle(flow_dag, start_nodes)
            if cycle !== nothing
                min_flow, min_flow_edge = minimum([(flows[e], e) for e=cycle])
                loi.logger("Breaking cycle :$(min_flow)")
                for e in cycle
                    flows[e] -= min_flow
                end
                flows[min_flow_edge] = zero(FlowType)
            else
                break
            end
        end
    end


    """
    Check that solution is correct with respect to the constraint of the FCFP.
    """
    function check_solution(loi::LocalOptimizerInstance, flows::FlowDictType) :: Bool
        # Check that flow graph is a DAG
        flow_dag = get_flow_dag(loi.optimization_graph, flows)
        c = find_cycle(flow_dag)
        if c !== nothing
            return false
        end
        # Check flow conservation
        tol = 1e-5
        nodes = get_nodes(flow_dag)
        for n in nodes
            out_flow = sum(Array{WeightType}([flows[e] for e in out_edges(flow_dag, n)]))
            in_flow = sum(Array{WeightType}([flows[e] for e in in_edges(flow_dag, n)]))
            if n in loi.fcfp.building_nodes
                continue
            elseif n in loi.fcfp.production_nodes
                if out_flow > (loi.fcfp.production[n] + tol)
                    return false
                end
            else
                if abs(out_flow - in_flow) > tol
                    return false
                end
            end
        end
        return true
    end

    export optimize_locally
end
