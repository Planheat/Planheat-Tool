include("local_optimizer.jl")
if !isdefined(:FCFP)
    include("FCFP.jl")
end
module DSSP

    using JuMP
    using Clp
    import FCFP.FCFPInstance
    import LocalOptimizer.optimize_locally

    # Debug Data
    #= network_objective = 450
    V = [1,2,3,4,5,6,7]
    E = [(1,2,0), (1,3,0), (1,4,0), (2,3,0), (4,3,0),(2,6,0),(2,7,0),(3,7,0),(4,5,0)]
    production_nodes = [1]
    building_nodes = [5,6,7]
    junctions_nodes = [2,3,4]
    costs = Dict(e => 1 for e=E)
    heat_demand = Dict(v => 200 for v=building_nodes)
    production = Dict(v => 500 for v=production_nodes)
    capacities = Dict{Tuple, Float32}() =#

    function edge_cost_func(e::Tuple, inst::FCFPInstance)
        if e in keys(inst.fixed_costs)
            return inst.fixed_costs[e]
        else
            return inst.fixed_costs[e[2], e[1], e[3]]
        end
    end

    function write_optimization_LP_model(inst::FCFPInstance)
        ### Create model ###
        m = Model(solver = ClpSolver())
        ### Variables
        @variable(m, 0 <= x[inst.all_edges] <= inst.network_objective)
        # Capacities of old pipes
        for e=keys(inst.capacities)
            setupperbound(x[e], inst.capacities[e])
        end
        ### Constraints
        # Source objective flow:
        @constraint(m, sum(x[e] for e=inst.all_edges if e[1] in inst.production_nodes) >= inst.network_objective)
        # Well objective flow:
        @constraint(m, sum(x[e] for e=inst.all_edges if e[2] in inst.building_nodes) >= inst.network_objective)
        # Each node follows the nodal rule, i.e. sum(flow_in) = sum(flow_out)
        for n=inst.building_nodes
            @constraint(m, sum(x[e] for e=inst.all_edges if e[2]==n) <= inst.heat_demand[n])
        end
        for n=inst.old_buildings
            @constraint(m, sum(x[e] for e=inst.all_edges if e[2]==n) >= inst.heat_demand[n]-1e-5)
        end
        for n=inst.production_nodes
            @constraint(m, sum(x[e] for e=inst.all_edges if e[1]==n) <= inst.production[n])
        end
        for n=inst.junctions_nodes
            @constraint(m, sum(x[e] for e=inst.all_edges if e[2]==n) == sum(x[e] for e=inst.all_edges if e[1]==n))
        end
        ### Objective
        @objective(m, Min, sum(x[e] * edge_cost_func(e, inst) for e=inst.all_edges))

        return m, x
    end

    function update_costs(inst::FCFPInstance, current_solution, last_solution, edge_costs, history_costs, tol, schema = "II" )
            nb_modified = 0
            for e=inst.all_edges
                    flow = current_solution[e]
                    if abs(flow - last_solution[e]) > tol
                            nb_modified += 1
                    end
                    if flow > 0
                            new_cost = edge_cost_func(e, inst) / flow
                            edge_costs[e] = new_cost
                            if schema == "I"
                                    history_costs[e] = max(new_cost, history_costs[e])
                            else
                                    history_costs[e] = new_cost
                            end
                    else
                            edge_costs[e] = history_costs[e]
                    end
            end
            return edge_costs, history_costs, nb_modified
    end

    function disrupt_costs(inst::FCFPInstance, edge_costs)
            for e=inst.all_edges
                    edge_costs[e] = max(0, edge_costs[e] + randn() * edge_costs[e]/2)
            end
            return edge_costs
    end

    function optimize_with_DSSP(network_objective, V, costs, heat_demand,
                                production, capacities, old_buildings, print_function = print,
                                postprocess=true, schema="II", maxiter=1000,
                                tol=1e-2)
        simulated_annealing = false
        simulated_annealing_max_iterations = 30
        simulated_annealing_it = 0
        srand(0)
        max_iter_without_improvement = 20
        inst = FCFPInstance(network_objective, V, costs, heat_demand, production, capacities, old_buildings)
        m, x = write_optimization_LP_model(inst)
        edge_costs =  Dict{Tuple , Float32}()
        for e=inst.all_edges
                if e in keys(capacities)
                        edge_costs[e] =  0 + edge_cost_func(e, inst) / capacities[e]
                else
                        edge_costs[e] =  0
                end
        end
        current_solution = Dict(e => 0 for e=inst.all_edges)
        history_costs = copy(edge_costs)
        best_solution = copy(current_solution)
        best_cost = Inf
        print_function("  Iteration  |  Current Obj.  |  Real Obj.  |  Best Obj.  |  Nb modifed Cost  | Solve Status\n")
        print_function(string(repeat("_", 92), "\n"))
        counter = 0
        nb_iter_without_improvement = 0
        while true
                last_solution = copy(current_solution)
                # Set new objective
                @objective(m, Min, sum(x[e] * edge_costs[e] for e=inst.all_edges))
                # Solve current problem
                status = solve(m)
                current_solution = Dict(e => getvalue(x[e]) for e=inst.all_edges)
                current_cost = getobjectivevalue(m)
                # Update costs
                edge_costs, history_costs, nb_modified = update_costs(inst, current_solution, last_solution, edge_costs, history_costs, tol, schema)
                nb_iter_without_improvement += 1
                # Save best solution
                real_current_cost = sum(edge_cost_func(e, inst) for e=inst.all_edges if current_solution[e] > 0)
                if real_current_cost < best_cost
                        best_solution = copy(current_solution)
                        best_cost = real_current_cost
                        nb_iter_without_improvement = 0
                end
                # Print information
                print_function("$(@sprintf("%13d|%16f|%13f|%13f|%19d|%14s", counter, current_cost, real_current_cost, best_cost, nb_modified, status))")
                counter += 1
                # Stopping conditions
                converged = all(abs(current_solution[e] - last_solution[e]) < tol for e=inst.all_edges)
                converged = converged || (nb_iter_without_improvement > max_iter_without_improvement)
                if converged
                        if simulated_annealing && (simulated_annealing_it < simulated_annealing_max_iterations)
                                print_function("=== Disrupting step ===")
                                edge_costs = disrupt_costs(inst, edge_costs)
                                simulated_annealing_it += 1
                                nb_iter_without_improvement = 0
                        else
                                break
                        end
                end
                if counter > maxiter
                        break
                end
        end
        # Post process : local optimization
        if postprocess
                best_solution = optimize_locally(best_solution, inst, print_function)
        end
        # Return final solution
        return best_solution, best_cost
    end

    export optimize_with_DSSP

end
