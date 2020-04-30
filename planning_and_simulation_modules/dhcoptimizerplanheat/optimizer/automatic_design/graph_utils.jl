using ResumableFunctions
using DataStructures
import Base.deepcopy

VertexType = String
KeyType = Int64
EdgeType = Tuple{VertexType, VertexType}
MultiEdgeType = Tuple{VertexType, VertexType, KeyType}
AdjencyView = Dict{VertexType, Dict{VertexType, Set{KeyType}}}
WeightType = Float64
FlowType = Float64
FlowDictType = Dict{MultiEdgeType, FlowType}


mutable struct MultiDiGraph
    succ::AdjencyView
    pred::AdjencyView
end

function deepcopy(mdg::MultiDiGraph) :: MultiDiGraph
    return MultiDiGraph(Base.deepcopy(mdg.succ), Base.deepcopy(mdg.pred))
end

function _init_multidigraph(edges) :: MultiDiGraph
    mdg = MultiDiGraph(AdjencyView(), AdjencyView())
    for e in edges
        add_edge!(mdg, e)
    end
    return mdg
end

function fill_adjency_view(adj::AdjencyView, e::MultiEdgeType)
    if e[1] in keys(adj)
        if e[2] in keys(adj[e[1]])
            push!(adj[e[1]][e[2]], e[3])
        else
            adj[e[1]][e[2]] = Set{KeyType}([e[3]])
        end
        if ! (e[2] in keys(adj))
            adj[e[2]] = Dict{VertexType, Set{KeyType}}()
        end
    else
        adj[e[1]] = Dict{VertexType, Set{KeyType}}(e[2] => Set{KeyType}([e[3]]))
    end
end

MultiDiGraph(edges) = _init_multidigraph(edges)

function get_sub_graph(mdg::MultiDiGraph, sub_nodes::Set{VertexType}, from_new=true) :: MultiDiGraph
    if from_new
        sub_graph = MultiDiGraph(AdjencyView(), AdjencyView())
        for e in get_edges(mdg)
            if (e[1] in sub_nodes) && (e[2] in sub_nodes)
                add_edge!(sub_graph, e)
            end
        end
        return sub_graph
    else
        sub_graph = deepcopy(mdg)
        for u in setdiff(get_nodes(mdg), sub_nodes)
            remove_node!(sub_graph, u)
        end
        return sub_graph
    end
end

function get_edge_sub_graph(mdg::MultiDiGraph, edges, from_new=true) :: MultiDiGraph
    if from_new
        sub_graph = MultiDiGraph(AdjencyView(), AdjencyView())
        for e in edges
            add_edge!(sub_graph, e)
        end
        return sub_graph
    else
        sub_graph = deepcopy(mdg)
        for e in get_edges(mdg)
            if !(e in edges)
                remove_edge!(sub_graph, e)
            end
        end
        remove_isolates!(sub_graph)
        return sub_graph
    end
end


"""
Return set of nodes from an adjency dictionary.
"""
function get_nodes(mdg::MultiDiGraph)
    return keys(mdg.succ)
end


#=
Yields all edges in the given graph.
=#
@resumable function get_edges(mdg::MultiDiGraph)
    for (u, ns) in mdg.succ
        for (v, ks) in ns
            for k in ks
                @yield (u, v, k)
            end
        end
    end
end


#=
Yields an outgoing edge to the given node with the given adjency dictionary.
=#
@resumable function out_edges(mdg::MultiDiGraph, u::VertexType) :: Union{MultiEdgeType, Nothing}
    if u in keys(mdg.succ)
        for (v, ks) in mdg.succ[u]
            for k in ks
                @yield (u, v, k)
            end
        end
    end
end


#=
Yields an incoming edge to the given node with the given adjency dictionary.
=#
@resumable function in_edges(mdg::MultiDiGraph, v::VertexType) :: Union{MultiEdgeType, Nothing}
    if v in keys(mdg.pred)
        for (u, ks) in mdg.pred[v]
            for k in ks
                @yield (u, v, k)
            end
        end
    end
end


#=
Yields reachable edges in a DFS way from a start node.
=#
@resumable function edges_dfs(mdg::MultiDiGraph, start_node::VertexType) :: Union{MultiEdgeType, Nothing}
    visited_nodes = Set{VertexType}()
    visited_edges = Set{MultiEdgeType}()
    edges = Dict{VertexType, Any}()
    stack = Array{VertexType, 1}([start_node])
    while ! isempty(stack)
        current_node = last(stack)
        if ! (current_node in visited_nodes)
            edges[current_node] = out_edges(mdg, current_node)
            push!(visited_nodes, current_node)
        end
        edge = edges[current_node]()
        if edge === nothing
            pop!(stack)
        else
            if ! (edge in visited_edges)
                push!(visited_edges, edge)
                push!(stack, edge[2])
                @yield edge
            end
        end
    end
end


"""
Find a cycle with the given adjency dictionary. Return `nothing` if no cycle is
found.
"""
function find_cycle(mdg::MultiDiGraph, start_nodes=nothing::Union{Nothing, Set{VertexType}}) :: Union{Array{MultiEdgeType, 1}, Nothing}
    explored = Set{VertexType}()
    cycle = Array{MultiEdgeType, 1}()
    final_node = nothing
    if start_nodes === nothing
        nodes = get_nodes(mdg)
    else
        nodes = start_nodes
    end
    for start_node in nodes
        if start_node in explored
            # No loop is possible.
            continue
        end
        edges = Array{MultiEdgeType, 1}()
        # All nodes seen in this iteration of edge_dfs
        seen = Set{VertexType}()
        push!(seen, start_node)
        # Nodes in active path.
        active_nodes = Set{VertexType}()
        push!(active_nodes, start_node)
        previous_head = nothing
        for edge in edges_dfs(mdg, start_node)
            # Determine if this edge is a continuation of the active path.
            tail, head = edge[1], edge[2]
            if head in explored
                # Then we've already explored it. No loop is possible.
                continue
            end
            if (previous_head !== nothing) && (tail != previous_head)
                # This edge results from backtracking.
                # Pop until we get a node whose head equals the current tail.
                # So for example, we might have:
                #  (0, 1), (1, 2), (2, 3), (1, 4)
                # which must become:
                #  (0, 1), (1, 4)
                while true
                    if ! isempty(edges)
                        popped_edge = pop!(edges)
                        popped_head = popped_edge[2]
                        filter!(x -> x != popped_head, active_nodes)
                    else
                        edges = Array{MultiEdgeType, 1}()
                        active_nodes = Set{VertexType}([tail])
                        break
                    end
                    if ! isempty(edges)
                        last_head = last(edges)[2]
                        if tail == last_head
                            break
                        end
                    end
                end
            end
            push!(edges, edge)
            if head in active_nodes
                # We have a loop!
                cycle = vcat(cycle, edges)
                final_node = head
                break
            else
                push!(seen, head)
                push!(active_nodes, head)
                previous_head = head
            end
        end
        if ! isempty(cycle)
            break
        else
            for n in seen
                push!(explored, n)
            end
        end
    end
    if isempty(cycle)
        return nothing
    end
    # We now have a list of edges which ends on a cycle.
    # So we need to remove from the beginning edges that are not relevant.
    trimming_i = 1
    for (i, edge) in enumerate(cycle)
        tail, head = edge[1], edge[2]
        if tail == final_node
            trimming_i = i
            break
        end
    end
    return cycle[trimming_i:length(cycle)]
end


"""
Return all nodes reachable from `source` in the given adjency dictionary.
"""
function descendants(mdg::MultiDiGraph, source::VertexType, strict=false) :: Set{VertexType}
    des = Set{VertexType}()
    node_stack = [source]
    while ! isempty(node_stack)
        current_node = pop!(node_stack)
        if ! (current_node in des)
            push!(des, current_node)
            for e in out_edges(mdg, current_node)
                push!(node_stack, e[2])
            end
        end
    end
    if strict
        filter!(x -> x != source, des)
    end
    return des
end


"""
Compute the shortest path from a set of sources to a target node.
"""
function dijkstra_multisource(mdg::MultiDiGraph, sources::Set{VertexType}, target::VertexType, weight::Dict)
    dists = DefaultDict{VertexType, WeightType}(typemax(WeightType))
    visited = DefaultDict{VertexType, Bool}(false)
    parents = Dict{VertexType, VertexType}()
    fringe = PriorityQueue{VertexType, WeightType}()

    for s=sources
        dists[s] = zero(WeightType)
        visited[s] = true
        fringe[s] = zero(WeightType)
    end

    while !isempty(fringe)
        u = dequeue!(fringe)
        d = dists[u]
        if u == target
            break
        end
        if u in keys(mdg.succ)
            for v in keys(mdg.succ[u])
                alt = d + weight[(u, v)]
                if (visited[v]) && alt < dists[u]
                    throw(ErrorException("Contradictory paths found:
                                            negative weights?: alt='$(alt)', dists[v]='$(dists[v])"))
                end
                if (!visited[v]) || (alt < dists[v])
                    visited[v] = true
                    dists[v] = alt
                    parents[v] = u
                    fringe[v] = alt
                end
            end
        end
    end
    if ! visited[target]
        return nothing
    end
    path = [target]
    node = target
    while ! (node in sources)
        node = parents[node]
        push!(path, node)
    end
    return (path[end:-1:1], dists[target])
end


"""
Return the lowest common ancestor of the two given nodes in the given DAG.
Return `nothing` if none is found.
"""
function lowest_common_ancestor(mdg::MultiDiGraph, node1::VertexType, node2::VertexType) :: Union{VertexType, Nothing}
    # First node backtracking
    nodes_stack = [node1]
    ancestors1 = Set{VertexType}([node1])
    while !isempty(nodes_stack)
        current_node = pop!(nodes_stack)
        for e in in_edges(mdg, current_node)
            if e[1] in ancestors1
                continue
            end
            push!(ancestors1, e[1])
            push!(nodes_stack, e[1])
        end
    end
    # Second node backtracking
    ancestors2 = Set{VertexType}([node2])
    nodes_stack = [node2]
    while !isempty(nodes_stack)
        current_node = pop!(nodes_stack)
        if current_node in ancestors1
            return current_node  # lca found
        end
        for e in in_edges(mdg, current_node)
            if e[1] in ancestors2
                continue
            end
            push!(ancestors2, e[1])
            push!(nodes_stack, e[1])
        end
    end
    # no common ancestor found
    return nothing
end


function add_node!(graph::MultiDiGraph, n::VertexType)
    if ! (n in keys(graph.succ))
        graph.succ[n] = Dict{VertexType, Set{KeyType}}()
    end
    if ! (n in keys(graph.pred))
        graph.pred[n] = Dict{VertexType, Set{KeyType}}()
    end
end

function add_edge!(graph::MultiDiGraph, e::MultiEdgeType)
    u, v, k = e
    add_node!(graph, u)
    add_node!(graph, v)
    if v in keys(graph.succ[u])
        push!(graph.succ[u][v], k)
    else
        graph.succ[u][v] = Set{KeyType}([k])
    end
    if u in keys(graph.pred[v])
        push!(graph.pred[v][u], k)
    else
        graph.pred[v][u] = Set{KeyType}([k])
    end
end

function remove_node!(graph::MultiDiGraph, n::VertexType)
    for u in keys(graph.pred[n])
        delete!(graph.succ[u], n)
    end
    for v in keys(graph.succ[n])
        delete!(graph.pred[v], n)
    end
    delete!(graph.succ, n)
    delete!(graph.pred, n)
end


function remove_edge!(graph::MultiDiGraph, e::MultiEdgeType)
    u, v, k = e
    delete!(graph.succ[u][v], k)
    if isempty(graph.succ[u][v])
        delete!(graph.succ[u], v)
    end
    delete!(graph.pred[v][u], k)
    if isempty(graph.pred[v][u])
        delete!(graph.pred[v], u)
    end
end




function has_one_parent(graph::MultiDiGraph, n::VertexType) :: Bool
    parent_found = false
    for (u, ks) in graph.pred[n]
        if parent_found
            return false
        end
        parent_found = true
    end
    return parent_found
end


function has_no_parent(graph::MultiDiGraph, n::VertexType) :: Bool
    return isempty(graph.pred[n])
end


function remove_isolates!(graph::MultiDiGraph)
    nodes_to_remove = Set{VertexType}()
    for (u, ns) in graph.succ
        if isempty(ns) && isempty(graph.pred[u])
            push!(nodes_to_remove, u)
        end
    end
    for n in nodes_to_remove
        remove_node!(graph, n)
    end
end
