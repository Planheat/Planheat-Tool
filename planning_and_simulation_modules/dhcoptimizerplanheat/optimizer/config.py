# == CRS settings == #
CRS = {'init': 'epsg:4326'}

# == KEYS == #
# geopandas geometry key
GPD_GEO_KEY = "geometry"

# graph keys
NODE_TYPE_KEY = "nodetype"
EDGE_COST_KEY = "cost"
EDGE_LENGTH_KEY = "length"
SOLUTION_POWER_FLOW_KEY = "flow"
NODE_ELEVATION_KEY = "z"
ORIGINAL_EDGE_KEY = "original_edge"
PIPE_DIAMETER_KEY = "diameter"
VELOCITY_KEY = "velocity"
AVERAGE_PRESSURE_KEY = "Apressure"
CONSTRUCTION_COST_KEY = "ConstC"
HEAT_LOSS_COST_KEY = "HLC"
COOL_LOSS_COST_KEY = "CLC"
PUMPING_COST_KEY = "PumpC"

# supply keys
SUPPLY_POWER_CAPACITY_KEY = "capacity_MW"
SUPPLY_NODE_TYPE = "production"
SUPPLY_NODE_NAME_PREFIX = "S_"
OLD_SUPPLY_NODE_NAME_PREFIX = "OldS_"
SUPPLY_FIXED_COST = 1000.0  # meters

# buildings keys
BUILDING_CONSUMPTION_KEY = "MaxHeatDem"
BUILDING_NODE_TYPE = "building"
BUILDING_ID_KEY = "BuildingID"
BUILDING_NODE_NAME_PREFIX = "B_"
EXCLUDED_BUILDING_KEY = "IsExcluded"
BUILDING_CONSUMPTION_FACTOR_UNIT = 1e-3  # buildings consumptions are in GW and the plugin is working in MW

BUILDING_ID_KEY = "BuildingID"
BUILDING_USE_KEY = "Use"
BUILDING_ROOF_AREA_KEY = "RoofArea"
BUILDING_GROSS_FOOTPRINT_AREA_KEY = "GrossFA"
BUILDING_FLOORS_KEY = "NumberFloo"
CONNECTED_BUILDING_KEY = "Connected"
BUILDING_SURFACE_KEY = "Surface"
BUILDING_MAX_HEAT_DEM_KEY = "MaxHeatDem"
BUILDING_MAX_COOL_DEM_KEY = 'MaxCoolDem'
BUILDING_AVERAGE_HEAT_DEM_KEY = "AHeatDem"
BUILDING_AVERAGE_COOL_DEM_KEY = 'ACoolDem'
BUILDING_PEAK_HEAT_DEM_KEY = "PeakHeatDe"
BUILDING_PEAK_COOL_DEM_KEY = 'PeakCoolDe'
DAY_KEY = "DayOfYear"
HOUR_KEY = "HourOfDay"

# Streets keys
STREET_NODE_TYPE = "junction"
STREET_NODE_PEAK_DEMAND = "JunPeakDem"

# Least cost coefficient (%)
LEASTCOST_COEF = 30
LEASTCOST_COEF_KEY = 'LSTCcoef'

# Imaginary edges:
IM_PREFIX = "IM_"


# Output files :
SELECTED_BUILDINGS_FILE = "result_buildings.shp"
UNSELECTED_BUILDINGS_FILE = "result_unselected_buildings.shp"
SOLUTION_DISTRICT_EDGES_FILE = "solution_edges.shp"
SOLUTION_SUPPLY_EDGES_FILE = "solution_supply.shp"
SOLUTION_OLD_SUPPLY_EDGES_FILE = "solution_old_supply.shp"

SOLUTION_STP_EDGES_FILE = "solution_edges_stp.shp"

# == PLUGIN KEYS == #
STATUS_KEY = "Status"
EXCLUDED_KEY = "Excluded"
EXCLUDED_STATUS_VALUE = 0
INCLUDED_KEY = "Included"
INCLUDED_STATUS_VALUE = 1
EXISTING_KEY = "Already connected"
EXISTING_STATUS_VALUE = 2
LEASTCOST_KEY = "Least Cost"
LEASTCOST_STATUS_VALUE = 3
SUPPLY_NAME_KEY = "name"

COVERAGE_OBJECTIVE_DEFAULT = 50  # %

POSTPROCESS = True
