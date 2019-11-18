from PyQt5.QtGui import QColor

#=== Layers names and groups ===
study_group_prefix = "Study "

# Data layers
input_layers_group_prefix = "Data "
buildings_layer_prefix = "all_buildings_"
streets_layer_prefix = "all_streets_"
supply_layer_prefix = "potential_supply_"


# Solution layers
output_layers_group_prefix = "Solution "
selected_edges_layer_prefix = "selected_edges_"
selected_buildings_layer_prefix = "selected_buildings_"
unselected_buildings_layer_prefix = "unselected_buildings_"
solution_supply_layer_prefix = "solution_supply_"
old_network_edges_layer_prefix = "old_network_edges_"
pressure_layer_prefix = "pressure_in_pipes_"
diameter_layer_prefix = "diameter_pipes_"
flow_layer_prefix = "flow_in_pipes_"

#=== Colors definition ===
# Buildings status styles
buildings_opacity = 0.5
included_buildings_color = QColor.fromRgb(3, 82, 193)
excluded_buildings_color = QColor.fromRgb(204, 110, 56)
old_network_buildings_color = QColor.fromRgb(0, 100, 0)  # green

# Streets status styles
streets_opacity = 0.5
street_width = 0.6
included_streets_color = QColor.fromRgb(3, 82, 193)
excluded_streets_color = QColor.fromRgb(204, 110, 56)
leastcost_streets_color = QColor.fromRgb(0, 250, 0)
old_network_streets_color = QColor.fromRgb(0, 100, 0)
old_network_edges_color = QColor.fromRgb(0, 100, 0)
old_network_edges_border_color = "0, 100, 0"
old_network_edges_opacity = 0.8

# Solution styles
selected_buildings_color = QColor.fromRgb(0, 109, 234)  # blue
selected_buildings_opacity = 0.8
unselected_buildings_color = QColor.fromRgb(255, 255, 191)  # light yellow
unselected_buildings_opacity = 0.8
solution_flow_color = QColor.fromRgb(255, 30, 0)  # orange
solution_flow_border_color = "255, 30, 0"
solution_flow_opacity = 0.8
solution_diameter_color = QColor.fromRgb(30, 150, 0) 
solution_diameter_border_color = "30, 150, 0"
solution_diameter_opacity = 0.8
solution_pressure_color = QColor.fromRgb(0, 30, 255) 
solution_pressure_border_color = "0, 30, 255"
solution_pressure_opacity = 0.8