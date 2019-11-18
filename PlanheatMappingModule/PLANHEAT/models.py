class Tree(object):
    def __init__(self, tree_id, name, description, file, resolution, buffer_size, attribute_name, planner_file, type, area_file):
        self.tree_id = tree_id
        self.name = name
        self.description = description
        self.file = file
        self.resolution = resolution
        self.buffer_size = buffer_size
        self.attribute_name = attribute_name
        self.planner_file = planner_file
        self.type = type
        self.area_file = area_file


class TreeNode(object):
    def __init__(self, node_id, tree_id, main_node_id, selected, description, icon, file, shape_attribute, algorithm_id, algorithm, parameters, map_selection, type,
                 algorithm_selection, buffer):
        self.node_id = node_id
        self.tree_id = tree_id
        self.main_node_id = main_node_id
        self.selected = selected
        self.description = description
        self.icon = icon
        self.file = file
        self.shape_attribute = shape_attribute
        self.set_algorithm(algorithm_id, algorithm)
        self.set_parameters(parameters)
        self.map_selection = map_selection
        self.type = type
        self.algorithm_selection = algorithm_selection
        self.buffer = buffer

    def set_parameters(self, parameters):
        self.parameters = parameters

    def set_algorithm(self, algorithm_id, algorithm):
        self.algorithm_id = algorithm_id
        self.algorithm = algorithm


class Algorithm(object):
    def __init__(self, algorithm_id, description, icon, number_of_parameters, type):
        self.algorithm_id = algorithm_id
        self.description = description
        self.icon = icon
        self.number_of_parameters = number_of_parameters
        self.type = type


class Parameter(object):
    def __init__(self, parameter_id, node_id, parameter_nr, value, id_field, data_field):
        self.parameter_id = parameter_id
        self.node_id = node_id
        self.parameter_nr = parameter_nr
        self.value = value
        self.id_field = id_field
        self.data_field = data_field
