module FCFP
        export FCFPInstance

        struct FCFPInstance
                network_objective::Real
                all_edges::Array{Tuple}
                production_nodes::Array{}
                building_nodes::Array{}
                junctions_nodes::Array{}
                fixed_costs::Dict{Tuple, Real}
                heat_demand::Dict{}
                production::Dict{}
                capacities::Dict{Tuple, Real}
                old_buildings::Array{}
        end


        """
        Initialize the FCFP instance struct object with given arguments. All edges
        are specified within the `costs` dictionnary.
        """
        function initialize_data(network_objective, V, costs, demands, productions, capacities, old_buildings)
                production_nodes = [p for p=keys(productions)]
                building_nodes = [b for b=keys(demands)]
                junctions_nodes = setdiff(V, union(production_nodes, building_nodes))
                all_edges = collect(keys(costs))
                old_buildings = collect(old_buildings)
                inst = FCFPInstance(network_objective, all_edges, production_nodes, building_nodes, junctions_nodes, costs, demands, productions, capacities, old_buildings)
                return inst
        end

        FCFPInstance(network_objective, V, costs, demands, productions, capacities, old_buildings) = initialize_data(network_objective, V, costs, demands, productions, capacities, old_buildings)
end
