#=
using PyCall

@pyimport pickle


f = open(raw"D:\projets\PlanHeat\tmp\instances\not_dag_2\flows.pickle", "r")
flows=pickle.load(f)
close(f)

include("local_optimizer.jl")

flows = Dict{Tuple, Float32}((0, 1, 0) => 1,
             (1, 2, 0) => 1,
             (2, 3, 0) => 1,
             (1, 4, 0) => 1,
             (5, 6, 0) => 1,
             (6, 4, 0) => 1,
             (6, 7, 0) => 1,
             (7, 8, 0) => 1,
             (8, 10, 0) => 1,
             (10, 9, 0) => 1,
             (9, 10, 0) => 1,
             (9, 10, 1) => 1,
             (10, 3, 0) => 1)



flow_dag = get_flow_dag(flows)

edges = Set{Tuple}()
for (u, ns) in flow_dag
    for (v, ks) in ns
        for k in ks
            e = (u, v, k)
            push!(edges, e)
        end
    end
end
for e in edges
    re = (e[2], e[1], e[3])
    if re in edges
        println(e)
    end
end
start_node= "27307035"

k = find_cycle(flow_dag)

i_flows = copy(flows)

clean_flow_two_cycles(flows)

break_cycles(flows)

flow_dag = get_flow_dag(flows)

get_nodes(flow_dag)
descendants(flow_dag, "S_0")
descendants(flow_dag, start_node)


costs = Dict(e => 1.0 for e in keys(flows))
G = get_adj_dict(keys(flows))
dijkstra_multisource(G, Set(["S_0"]), start_node, costs)

optimization_graph = get_adj_dict(keys(flows))
=#




#=   ======================================================================== =#
include("FCFP.jl")
import FCFP.FCFPInstance
include("DSSP.jl")
using DSSP
using PyCall
using JSON
using DataStructures

@pyimport pickle

p = raw"D:\projets\PlanHeat\tmp\master_plugin\debug_local_optimizer2/"
f = open(p * "flows.pickle", "r")
flows=pickle.load(f)
close(f)

f = open(p * "costs.pickle", "r")
costs=pickle.load(f)
close(f)

f = open(p * "heat_demand.json", "r")
head_demand=JSON.parse(read(f, String))
close(f)


f = open(p * "production.json", "r")
productions = JSON.parse(read(f, String))
close(f)

include("local_optimizer.jl")
import LocalOptimizer:optimize_locally, MultiDiGraph, get_nodes, get_flow_dag, has_no_parent, add_edge!, get_edges
import LocalOptimizer:descendants, get_sub_graph, break_cycles, clean_flow_two_cycles, validate_move, LocalOptimizerInstance, get_flow_arteries, remove_node!, cascade_union, add_zero_weight_edges_from_nodes, dijkstra_multisource, get_edge_like_path, reroute_artery, lowest_common_ancestor
import LocalOptimizer:check_solution, find_cycle, VertexType, KeyType, EdgeType, MultiEdgeType, AdjencyView
import LocalOptimizer:FlowDictType, replace_arteries, WeightType, out_edges, in_edges, has_one_parent

optimization_graph = MultiDiGraph(keys(flows))
V = get_nodes(optimization_graph)
old_buildings = Set()
capacities = Dict()
fcfp = FCFPInstance(0.0, V, costs, head_demand, productions, capacities, old_buildings)
logger = println




using StatProfilerHTML
Profile.clear()
@profile new_flows = optimize_locally(flows, fcfp, logger)
statprofilehtml()


flows2 = FlowDictType(flows)
loi = LocalOptimizerInstance(flows, fcfp, logger)
initial_cost = sum(loi.fcfp.fixed_costs[e] for (e, f) in loi.flows if f > 0)
check_solution(loi, loi.flows)



start = time()

loi = LocalOptimizerInstance(flows, fcfp, logger)
old_flows = copy(loi.flows)
initial_cost = sum(loi.fcfp.fixed_costs[e] for (e, f) in loi.flows if f > 0)
clean_flow_two_cycles(loi.working_flows)
break_cycles(loi, loi.working_flows)
validate_move(loi)
while replace_arteries(loi)
    a = check_solution(loi, loi.flows)
    if a
        old_flows = copy(loi.flows)
    else
        println("now")
        break
    end
    gain = initial_cost - sum(loi.fcfp.fixed_costs[e] for (e, f) in loi.flows if f > 0)
    loi.logger("Cost gain: $(gain)")
end

check_solution(loi, old_flows)
check_solution(loi, loi.flows)


f = open(p * "previous_correct_flows.pickle", "w")
pickle.dump(old_flows, f)
close(f)


################################################################################
################### Understanding while check is false #########################
################################################################################


flows = loi.flows
flow_dag = get_flow_dag(loi.optimization_graph, loi.flows)
c = find_cycle(flow_dag)
tol = 1e-5
nodes = get_nodes(flow_dag)
for n in nodes
    out_flow = sum(Array{WeightType}([flows[e] for e in out_edges(flow_dag, n)]))
    in_flow = sum(Array{WeightType}([flows[e] for e in in_edges(flow_dag, n)]))
    if n in loi.fcfp.building_nodes
        continue
    elseif n in loi.fcfp.production_nodes
        if out_flow > (loi.fcfp.production[n] + tol)
            println("here")
            break
        end
    else
        if abs(out_flow - in_flow) > tol
            println("or here")
            println(n)
            break
        end
    end
end



n= "intersect_S_2"
abs(sum([loi.flows[e] for e in out_edges(flow_dag, n)]) - sum([loi.flows[e] for e in in_edges(flow_dag, n)]))
v = "6341231519"
minimum(values(loi.fcfp.heat_demand))

ns = [u for u in get_nodes(flow_dag)]
v in ns
loi.flows[(v, n , 0)]

out_flow = sum(Array{WeightType}([flows[e] for e in out_edges(flow_dag, n)]))
in_flow = sum(Array{WeightType}([flows[e] for e in in_edges(flow_dag, n)]))

previous_flow = loi.flows
f = open(p * "flows_sources_move_pr.pickle", "w")
pickle.dump(previous_flow, f)
close(f)


################################################################################
################### Finding the artery that is involved ########################
################################################################################

loi.flows = copy(old_flows)
loi.working_flows = copy(old_flows)

loi.roots
[loi.fcfp.production[r] for r in loi.roots]

flow_dag = get_flow_dag(loi.optimization_graph, loi.flows)
arteries = get_flow_arteries(loi, flow_dag)
roots_descendants = Array{Set{VertexType}, 1}([descendants(flow_dag, r, false) for r in loi.roots])
roots_marginal_capacity = [loi.fcfp.production[r] - sum(get(loi.fcfp.heat_demand, n, 0.0)
                                                        for n in roots_descendants[r_index])
                                                                for (r_index, r) in enumerate(loi.roots)]
a = []
edge_like_path = []
while !isempty(arteries)
    a = dequeue!(arteries)
    # determine sub tree
    end_node = last(a)[2]
    sub_tree_nodes = descendants(flow_dag, end_node, false)
    if isempty(sub_tree_nodes)
       print("empty here")
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
       print("empty here2")
    end
    # Add 0-weight edges in the sub-graph
    modified_costs = add_zero_weight_edges_from_nodes(sub_tree_nodes, loi.costs)
    path, cost = dijkstra_multisource(loi.optimization_graph,
                                     parent_dag_trees_nodes,
                                     end_node,
                                     modified_costs)
    edge_like_path = get_edge_like_path(path, loi.optimization_graph, loi.fcfp.fixed_costs)
    if edge_like_path != a
       print("hey")
       break
    end
end
edge_like_path
a
[loi.flows[e] for e in a]
[has_one_parent(flow_dag, e[2]) for e in a]
flow_dag = get_flow_dag(loi.optimization_graph, loi.working_flows)

potential_cycle_creation = false
if any((n != end_node) && (n in sub_tree_nodes) for n in path)
    potential_cycle_creation = true
end
new_start = first(path)
any(new_start in roots_descendants[d_index] for d_index in current_roots_indexes)
if any(new_start in roots_descendants[d_index] for d_index in current_roots_indexes)
    loi.logger("Moving flow inside current dag")
    reroute_artery(loi, a, edge_like_path, flow_dag, potential_cycle_creation)
else
    loi.logger("Moving flow to another dag")
    new_roots_candidates = Set{VertexType}([loi.roots[r] for r in other_roots_indexes if new_start in roots_descendants[r]])
    current_roots = Set{VertexType}([loi.roots[r] for r in current_roots_indexes])
    move_artery_to_other_dag(loi, a, edge_like_path, flow_dag, current_roots, new_roots_candidates, potential_cycle_creation)
end


###### debug : move_artery_to_other_dag ################################
new_a = edge_like_path
artery_flow = loi.working_flows[first(a)]
for e in a
    loi.working_flows[e] = zero(WeightType)
end
# Find path from old root to old start and remove flow
old_start = first(a)[1]
residual_artery_flow = artery_flow
r = first(current_roots)
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
e = edge_down_path[2]
for e in edge_down_path
    loi.working_flows[e] += artery_flow
end
n = "intersect_S_2"

e2 = edge_down_path[2]
v1 = Float64(loi.flows[e2]) + Float64(artery_flow)
e1 = edge_down_path[1]
e3 = ("intersect_S_2", "intersect_5321182.0", 0)
v2 = Float64(loi.flows[e1]) + Float64(artery_flow) - Float64(loi.flows[e3])
v1 - v2


sum([loi.working_flows[e] for e in out_edges(flow_dag, n)]) - (sum([loi.working_flows[e] for e in in_edges(flow_dag, n)]))
[e for e in in_edges(flow_dag, n)]
# Set new artery flow
for e in new_a
    loi.working_flows[e] += artery_flow  # Adding flow because their may be already a flow on it
end
# Clean flows
clean_flow_two_cycles(loi.working_flows)
if potential_cycle_creation
    break_cycles(loi, loi.working_flows, Set{VertexType}([new_start]))
end







validate_move(loi)

new_a = edge_like_path
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







































































gain = initial_cost - sum(loi.fcfp.fixed_costs[e] for (e, f) in loi.flows if f > 0)

optimization_time = time() - start
loi.logger("Arteries flows rerouting postprocess: gain=$(gain),  time: $(optimization_time)")
if check_solution(loi, loi.flows)
    return loi.flows
else
    loi.logger("Local optimization failed")
    return loi.init_flows
end











replace_arteries(loi)


import LocalOptimizer:replace_arteries, check_solution
check_solution(loi, loi.working_flows)

flow_dag = get_flow_dag(loi.optimization_graph, loi.flows)
arteries = get_flow_arteries(loi, flow_dag)
roots_descendants = Array{Set{VertexType}, 1}([descendants(flow_dag, r, false) for r in loi.roots])
roots_marginal_capacity = [loi.fcfp.production[r] - sum(get(loi.fcfp.heat_demand, n, 0.0)
                                                        for n in roots_descendants[r_index])
                           for (r_index, r) in enumerate(loi.roots)]

new_start = nothing
path = nothing
edge_like_path = nothing
a = nothing
potential_cycle_creation = nothing
using DataStructures

while !isempty(arteries)
    a = dequeue!(arteries)
    # determine sub tree
    end_node = last(a)[2]
    sub_tree_nodes = descendants(flow_dag, end_node, false)
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
            break
        else
            loi.logger("Moving flow to another dag")
            println("NOWWW")
            break
        end
    end
end



edge_like_path

a

check_solution(loi, loi.working_flows)
validate_move(loi)




import LocalOptimizer: move_artery_to_other_dag, WeightType, VertexType, MultiEdgeType
other_roots_indexes = Set{Int64}(1)
new_roots_candidates = Set{VertexType}([loi.roots[r] for r in other_roots_indexes if new_start in roots_descendants[r]])
loi.working_flows = copy(loi.flows)

new_a = edge_like_path
artery_flow = loi.working_flows[first(a)]
for e in a
    loi.working_flows[e] = zero(WeightType)
end
new_start = first(new_a)[1]
# Find path from root to new start
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
    break_cycles(loi, loi.working_flows)
end

check_solution(loi, loi.working_flows)

flows = loi.working_flows
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
            println("$(n) : $(out_flow) > $((loi.fcfp.production[n] + tol))")
        end
    else
        if abs(out_flow - in_flow) > tol
            println("$(n) : $(out_flow) != $(in_flow)")
        end
    end
end
return true

import LocalOptimizer: out_edges, in_edges


previous_flow = loi.flows
f = open(raw"D:\projets\PlanHeat\tmp\instances\not_dag_3\flows_sources_move_pr.pickle", "w")
pickle.dump(previous_flow, f)
close(f)

f = open(raw"D:\projets\PlanHeat\tmp\instances\not_dag_3\flows_sources_move.pickle", "w")
pickle.dump(loi.working_flows, f)
close(f)
=#











[has_one_parent(flow_dag, e[2]) for e in current_artery]

a = dequeue!(arteries)

arteries = PriorityQueue{Array{MultiEdgeType, 1}, WeightType}()
explored_nodes = Set{VertexType}()
r = loi.roots[3]
nodes_stack = Array{VertexType, 1}([r])
while !isempty(nodes_stack)
    n = pop!(nodes_stack)
    if n in explored_nodes
        continue
    end
    push!(explored_nodes, n)
    out_flow_edges = collect(out_edges(flow_dag, n))
    println(n)
    if (length(out_flow_edges) != 1) || (! has_one_parent(flow_dag, n))
        for e in out_flow_edges
            push!(nodes_stack, e[2])
        end
        continue
    end
    println("here")
    println(n)
    break
end

n = "intersect_S_0_2"
out_flow_edges = collect(out_edges(flow_dag, n))
# A new artery is found, explore it in depth
current_artery = [first(in_edges(flow_dag, n)), out_flow_edges[1]]
sub_nodes_stack = [out_flow_edges[1][2]]
while !isempty(sub_nodes_stack)
    sub_node = pop!(sub_nodes_stack)
    push!(explored_nodes, sub_node)
    out_flow_edges = collect(out_edges(flow_dag, sub_node))
    if (length(out_flow_edges) != 1) || (! has_one_parent(flow_dag, n))
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
