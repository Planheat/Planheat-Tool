module NLP
    using JuMP
    using Ipopt
    using Base

    function find_optimal_physical_parameters(GraphParam, ConfParam, output_file, type_energy, print_function = print)
        """
        Solves a nonlinear optimization of the network's physical parameters
        Hypothesis: temperature of the fluid in the supply and return networks
        is assumed to be constant

        INPUT:
        - GraphParam, ConfParam, output_dir

        OUTPUT:
        - Diameter (dict): pipe(u,v) -> diameter of the pipe in meters
        - AnnualCost (scalar): equivalent annual cost of the network
        """


        ########################################################################
        # Parameters
        ########################################################################
        LENGTH = GraphParam["LENGTH"]
        ELEVATION = GraphParam["ELEVATION"]
        OUTFLOW = GraphParam["OUTFLOW"]
        SUPPLY_MAX_INFLOW =  GraphParam["SUPPLY_MAX_INFLOW"]
        LB_DIAM = GraphParam["LB_DIAM"]
        MAX_CAPACITY = GraphParam["MAX_CAPACITY"]

        # DIAMETER RANGE
        MIN_DIAMETER = ConfParam["MIN_DIAMETER"]
        MAX_DIAMETER = ConfParam["MAX_DIAMETER"]

        # PRESSURE RANGE
        MIN_PRESSURE = ConfParam["MIN_PRESSURE"]
        MAX_PRESSURE = ConfParam["MAX_PRESSURE"]

        # THERM PARAM
        if type_energy == "Heating"
            SUPPLY_HC_TEMPERATURE = ConfParam["SUPPLY_HEAT_TEMPERATURE"]
            RETURN_HC_TEMPERATURE = ConfParam["RETURN_HEAT_TEMPERATURE"]
            HC_PERIOD = ConfParam["HEATING_PERIOD"]
            HC_COST = ConfParam["HEAT_COST"]
        elseif type_energy == "Cooling"
            SUPPLY_HC_TEMPERATURE = ConfParam["SUPPLY_COOL_TEMPERATURE"]
            RETURN_HC_TEMPERATURE = ConfParam["RETURN_COOL_TEMPERATURE"]
            HC_PERIOD = ConfParam["COOLING_PERIOD"]
            HC_COST = ConfParam["COOL_COST"]
        end
        GROUND_TEMPERATURE = ConfParam["GROUND_TEMPERATURE"]

        # ECO PARAM
        ELECTRICITY_COST = ConfParam["ELECTRICITY_COST"]
        INTEREST_RATE = ConfParam["INTEREST_RATE"]
        LIFETIME = ConfParam["LIFETIME"]
        DEPRECIATION_MAINTENANCE_RATE = ConfParam["DEPRECIATION_MAINTENANCE_RATE"]
        EFFECT_COEF = INTEREST_RATE / (1 - (1 + INTEREST_RATE)^(-LIFETIME)) + DEPRECIATION_MAINTENANCE_RATE

        # PUMPING PARAM
        PUMPING_EFFICIENCY = ConfParam["PUMPING_EFFICIENCY"]

        # PHYSICAL PARAM
        CP = ConfParam["CP"]
        RHO = ConfParam["RHO"]
        ROUGHNESS = ConfParam["ROUGHNESS"]
        FRICTION_COEF = (2 * log(ROUGHNESS / (3.71 * (MIN_DIAMETER + MAX_DIAMETER)/2 * 1e-2)) / log(10))^(-2)  #Fanning factor

        # REGRESSIONS
        A_MAX_VELOCITY = ConfParam["A_MAX_VELOCITY"]
        B_MAX_VELOCITY = ConfParam["B_MAX_VELOCITY"]

        A_LINEAR_COST = ConfParam["A_LINEAR_COST"]
        B_LINEAR_COST = ConfParam["B_LINEAR_COST"]

        if type_energy == "Heating"
            A_TRANSIT_COEF = ConfParam["A_HEAT_TRANSIT_COEF"]
            B_TRANSIT_COEF = ConfParam["B_HEAT_TRANSIT_COEF"]
        elseif type_energy == "Cooling"
            A_TRANSIT_COEF = ConfParam["A_COOL_TRANSIT_COEF"]
            B_TRANSIT_COEF = ConfParam["B_COOL_TRANSIT_COEF"]
        end

        # CONVERSION
        W_TO_MW = 1e-6
        DAY_TO_HOUR = 24
        BAR_TO_PA = 1e5
        CM_TO_M = 1e-2
        CM_TO_MM = 10
        G = 9.81 # gravitation constant (m/s2)

        # Sets of edges and nodes
        PIPE = keys(LENGTH)
        NODE = [n for n=Set(vcat([p[1] for p in PIPE], [p[2] for p in PIPE]))]
        SUPPLY_NODE = keys(SUPPLY_MAX_INFLOW)
        BUILDING_NODE = keys(OUTFLOW)

        # Set the bounds for mass flows at each node
        LOWER_BOUND_IO = Dict(n => 0.0 for n in NODE)
        UPPER_BOUND_IO = Dict(n => 0.0 for n in NODE)
        for n in BUILDING_NODE
            LOWER_BOUND_IO[n] = - OUTFLOW[n]
            UPPER_BOUND_IO[n] = - OUTFLOW[n]
        end
        for n in SUPPLY_NODE
            LOWER_BOUND_IO[n] = 0.0
            UPPER_BOUND_IO[n] = SUPPLY_MAX_INFLOW[n]
        end

        #print_function("1")
        ########################################################################
        # Optimization
        ########################################################################

        m = Model(with_optimizer(Ipopt.Optimizer, output_file = output_file,
                                        mu_strategy = "adaptive",  # more successfull
                                        tol = 1e-3, # tolerance hasn't to be very high
                                        max_cpu_time=1.0*ConfParam["MAXTIME"])) # time limit

        ############################ Variables #################################
        @variable(m, MIN_DIAMETER <= varDiameter[PIPE] <= MAX_DIAMETER) # Pipe diameters (cm)
        @variable(m, varVelocity[PIPE]) # Velocity in pipes (m/s), 
        # Positive flow (oriented edges) p = (n1, n2) <=> the flow is going from n1 to n2 
        @variable(m, varMassFlow[PIPE]) # Flow in pipes (kg/s)
        @variable(m, MIN_PRESSURE <= varPressure[PIPE] <= MAX_PRESSURE) # Pressure in pipe (bars)
        @variable(m, varPressureFriction[NODE]) # The pressure drop due to friction
        @variable(m, varConstBernoulli) # variable that plays the role of the constant in the Bernoulli equation


        ############################ Constraints ##############################
        for p in PIPE
            
            # MassFlow = rho * section * velecity where section = pi*r^2
            @NLconstraint(m, 4*varMassFlow[p] == RHO * pi * (varDiameter[p] * CM_TO_M)^2 * varVelocity[p])

            # Max Velocity
            @constraint(m, varVelocity[p] <= A_MAX_VELOCITY * varDiameter[p] * CM_TO_MM + B_MAX_VELOCITY)
            @constraint(m, -varVelocity[p] <= A_MAX_VELOCITY * varDiameter[p] * CM_TO_MM + B_MAX_VELOCITY)
            
            # Pressure loss in pipes (just due to friction)
            @NLconstraint(m, (varPressureFriction[p[1]]-varPressureFriction[p[2]]) * BAR_TO_PA == 0.5 * RHO * 
                LENGTH[p] * varVelocity[p] * abs(varVelocity[p]) * FRICTION_COEF / (varDiameter[p]*CM_TO_M))
        
            # Bernoulli's equation
            @NLconstraint(m, varPressure[p]*BAR_TO_PA + 1/2*RHO*varVelocity[p]^2 + RHO*G*(ELEVATION[p[1]]+ELEVATION[p[2]])/2 == 
                varConstBernoulli + (varPressureFriction[p[1]]+varPressureFriction[p[2]])/2*BAR_TO_PA)

            # Diameter to respect
            @constraint(m, varDiameter[p] >= get(LB_DIAM, p, 0))
            @constraint(m, varDiameter[p] >= get(LB_DIAM, (p[2],p[1]), 0))
            if p in keys(MAX_CAPACITY)
                if !isinf(MAX_CAPACITY[p]) && MAX_CAPACITY[p] >= MIN_DIAMETER
                    # need to be at least equals to MIN_DIAMETER, we put 1 cm more than real value
                    @constraint(m, varDiameter[p] <= get(LB_DIAM, p, Inf)+1)
                    @constraint(m, varDiameter[p] <= get(LB_DIAM, (p[2],p[1]), Inf)+1)
                end
            end
        end

        # Flow conservation
        for n in NODE
            @constraint(m, sum(varMassFlow[p] for p=PIPE if p[1]==n) - sum(varMassFlow[p] for p=PIPE if p[2]==n) >= LOWER_BOUND_IO[n])
            @constraint(m, sum(varMassFlow[p] for p=PIPE if p[1]==n) - sum(varMassFlow[p] for p=PIPE if p[2]==n) <= UPPER_BOUND_IO[n])
        end

        ############################## Objective ###############################

         @objective(m, Min, (A_LINEAR_COST * CM_TO_MM * EFFECT_COEF + # Construction cost
            2 * A_TRANSIT_COEF * CM_TO_MM * W_TO_MW * (HC_PERIOD * DAY_TO_HOUR) * HC_COST ) * # Heat loss cost
            sum(varDiameter[p] * LENGTH[p] for p=PIPE) 

            # Pumping cost (the problem become much longer with pumping cost)
            + sum(SUPPLY_MAX_INFLOW[n] * sum(varPressure[p] for p=PIPE if n in p) for n=SUPPLY_NODE) *
            BAR_TO_PA / RHO * W_TO_MW / PUMPING_EFFICIENCY * (HC_PERIOD * DAY_TO_HOUR) * ELECTRICITY_COST)

        ########################################################################
        # Solve and collect the solution
        ########################################################################  
        optimize!(m)
        status = termination_status(m)

        NLP_Output = Dict()
        #print_function("2")
        if status == MOI.OPTIMAL
            NLP_Output["Diameter"] = Dict(p => value(varDiameter[p]) for p=PIPE)
            NLP_Output["Velocity"] = Dict(p => value(varVelocity[p]) for p=PIPE)
            NLP_Output["MassFlow"] = Dict(p => value(varMassFlow[p]) for p=PIPE)
            NLP_Output["Pressure"] = Dict(p => value(varPressure[p]) for p=PIPE)
            NLP_Output["PressureFriction"] = Dict(n => value(varPressureFriction[n]) for n=NODE)
            NLP_Output["TotalCost"] = getobjectivevalue(m)

            NLP_Output["ConstructionCost"] = Dict(p => (A_LINEAR_COST * value(varDiameter[p]) * CM_TO_MM + B_LINEAR_COST) * LENGTH[p] * EFFECT_COEF for p=PIPE)
            if type_energy == "Heating"
                NLP_Output["HeatLossCost"] = Dict(p => 2 * (A_TRANSIT_COEF * value(varDiameter[p]) * CM_TO_MM + B_TRANSIT_COEF) * LENGTH[p] * 
                                    W_TO_MW * (HC_PERIOD * DAY_TO_HOUR) * HC_COST for p=PIPE)
            elseif type_energy == "Cooling"
                NLP_Output["CoolLossCost"] = Dict(p => 2 *(A_TRANSIT_COEF * value(varDiameter[p]) * CM_TO_MM + B_TRANSIT_COEF) * LENGTH[p] * 
                                    W_TO_MW * (HC_PERIOD * DAY_TO_HOUR) * HC_COST for p=PIPE)
            end
            NLP_Output["PumpingCost"] = Dict(n => value(sum(varPressure[p] for p=PIPE if n in p) - 1) * BAR_TO_PA * 
                SUPPLY_MAX_INFLOW[n] / RHO * W_TO_MW / PUMPING_EFFICIENCY * (HC_PERIOD * DAY_TO_HOUR) * ELECTRICITY_COST for n=SUPPLY_NODE)

        end
        status_str = "Unkown"
        if status == MOI.OPTIMAL
            status_str = "Optimal"
        elseif status == MOI.INFEASIBLE
            status_str = "Infeasible"
        end
        return NLP_Output, status_str
    end

    export find_optimal_physical_parameters
end


