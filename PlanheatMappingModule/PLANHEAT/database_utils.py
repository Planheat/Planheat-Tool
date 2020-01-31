import os
import shutil
import sqlite3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItemIterator

from .models import Parameter, Algorithm, TreeNode, Tree
from .node_utils import add_node, get_node_data
from .enums import AlgorithmEnum

from planheat.PlanheatMappingModule import master_mapping_config as mm_config

# directory = os.path.dirname(os.path.realpath(__file__))
# db_file = os.path.join(directory, "database\\planheat.db")
# print(db_file)

ALIAS = True

def get_algorithm(algorithm_id):
    if algorithm_id is None:
        return None
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM ALGORITHMS WHERE ALGORITHM_ID=? ;", (_get_int_value(algorithm_id),))
    row = c.fetchone()
    algorithm = Algorithm(row["algorithm_id"], row["description"], row["icon"], row["number_of_parameters"], row["type"])
    c.close()
    db.close()
    return algorithm


def get_algorithms():
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM ALGORITHMS ORDER BY ALGORITHM_ID;")
    algorithm_dict = dict()
    for row in c.fetchall():
        algorithm_dict[row["algorithm_id"]] = Algorithm(row["algorithm_id"], row["description"], row["icon"], row["number_of_parameters"], row["type"])
    c.close()
    db.close()
    return algorithm_dict


def get_algorithms_for_type(type):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM ALGORITHMS WHERE TYPE = ? ORDER BY ALGORITHM_ID;", (_get_int_value(type),))
    algorithm_dict = dict()
    for row in c.fetchall():
        algorithm_dict[row["algorithm_id"]] = Algorithm(row["algorithm_id"], row["description"], row["icon"], row["number_of_parameters"], row["type"])
    c.close()
    db.close()
    return algorithm_dict


def get_algorithm_by_id_and_default(algorithm_id):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM ALGORITHMS WHERE ALGORITHM_ID IN (?, ?) ORDER BY ALGORITHM_ID;", (algorithm_id, AlgorithmEnum.PROVIDED), )
    algorithm_dict = dict()
    for row in c.fetchall():
        algorithm_dict[row["algorithm_id"]] = Algorithm(row["algorithm_id"], row["description"], row["icon"], row["number_of_parameters"], row["type"])
    c.close()
    db.close()
    return algorithm_dict


def get_parameters(node_id):
    if node_id is None:
        return None
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM PARAMETERS WHERE NODE_ID=? ORDER BY PARAMETER_NR ASC;", (_get_int_value(node_id),))
    parameter_dict = dict()
    for row in c.fetchall():
        parameter_dict[row["parameter_nr"]] = Parameter(row["parameter_id"], row["node_id"], row["parameter_nr"], row["value"], row["id_field"], row["data_field"])
    c.close()
    db.close()
    return parameter_dict


def get_trees(type, alias = ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM TREES WHERE TYPE = ? ORDER BY TREE_ID ASC", (type,))
    tree_dict = dict()
    for row in c.fetchall():
        tree_dict[row["tree_id"]] = Tree(row["tree_id"], row['name'], alias2path(row["description"], alias), 
                                         alias2path(row["file"], alias), row["resolution"], row["buffer_size"], 
                                         row['attribute_name'], alias2path(row['planner_file'], alias), row['type'],
                                         alias2path(row['area_file'], alias))
    c.close()
    db.close()
    return tree_dict


def get_tree_by_id(tree_id, alias= ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM TREES WHERE TREE_ID = ?", (_get_int_value(tree_id),))
    row = c.fetchone()
    tree = Tree(row["tree_id"], row['name'], alias2path(row["description"], alias), alias2path(row["file"], alias), 
                int(row["resolution"]), int(row["buffer_size"]), row['attribute_name'], alias2path(row['planner_file'], alias),
                row['type'], alias2path(row['area_file'], alias))
    c.close()
    db.close()
    return tree


def copy_tree_into_new(dialog, type, alias=ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()

    c.execute("SELECT * FROM NODES WHERE TREE_ID=? ORDER BY  MIN(MAIN_NODE_ID, NODE_ID) ASC", (_get_int_value(dialog.treeSelect.currentData().tree_id),))
    db_nodes = c.fetchall()
    c.execute("SELECT seq FROM sqlite_sequence WHERE NAME = 'TREES'")
    new_tree_id = c.fetchone()["seq"] + 1
    c.execute("INSERT INTO TREES (TREE_ID, NAME, DESCRIPTION, FILE, RESOLUTION, BUFFER_SIZE, ATTRIBUTE_NAME, PLANNER_FILE, TYPE, AREA_FILE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (
                  new_tree_id, dialog.nameText.text(), path2alias(dialog.descriptionText.text(), alias), 
                  path2alias(dialog.fileNameText.text(), alias), dialog.resolutionText.text(), dialog.bufferText.text(),
                  dialog.nameSelect.currentText(), path2alias(dialog.plannerText.text(), alias), 
                  type, path2alias(dialog.areaFileText.text(), alias)))
    id_map_dict = dict()
    for node in db_nodes:

        main_node_id = None
        if node["main_node_id"]:
            main_node_id = id_map_dict[node["main_node_id"]]
        c.execute(
            "INSERT INTO NODES (TREE_ID,MAIN_NODE_ID,SELECTED,DESCRIPTION,ICON,FILE,SHAPE_ATTRIBUTE,ALGORITHM_ID,MAP_SELECTION,TYPE, ALGORITHM_SELECTION, BUFFER) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (new_tree_id, main_node_id, node["selected"], path2alias(node["description"], alias), node["icon"], 
            path2alias(node["file"], alias), node['shape_attribute'], node["algorithm_id"],
             node["map_selection"], node["type"], node["algorithm_selection"], dialog.bufferText.text()))
        new_node_id = c.lastrowid

        id_map_dict[node["node_id"]] = new_node_id
    for node in db_nodes:
        copy_parameters(c, node["node_id"], id_map_dict)

    db.commit()
    c.close()
    db.close()
    return new_tree_id


def get_next_node_id():
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT seq FROM sqlite_sequence WHERE NAME = 'NODES'")
    next_node_id = c.fetchone()["seq"] + 1
    c.execute("UPDATE sqlite_sequence set seq = ? WHERE NAME = 'NODES'", (next_node_id,))
    db.commit()
    c.close()
    db.close()
    return next_node_id


def copy_parameters(c, old_node_id, id_map_dict):
    c.execute("SELECT * FROM PARAMETERS WHERE NODE_ID = ?", (old_node_id,))
    for row in c.fetchall():
        if row["value"]:
            new_node_id = id_map_dict[old_node_id]
            if is_int(row["value"]) and int(row["value"]) in id_map_dict:
                new_value = id_map_dict[int(row["value"])]
            else:
                new_value = row["value"]
            c.execute("INSERT INTO PARAMETERS (NODE_ID, PARAMETER_NR, VALUE, ID_FIELD, DATA_FIELD) VALUES (?, ?, ?, ?, ?)",
                      (new_node_id, row["parameter_nr"], new_value, row["id_field"], row["data_field"]))


def is_int(str):
    try:
        int(str)
        return True
    except ValueError:
        return False


def save_tree(tree, alias=ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    iterator = QTreeWidgetItemIterator(tree)
    remaining_node_ids = []
    while iterator.value():
        node = iterator.value()
        data = get_node_data(node)

        if data.node_id:
            if does_node_exist(data.node_id):
                c.execute(
                    "UPDATE NODES SET SELECTED = ?, DESCRIPTION = ?, ICON = ?, FILE = ?, SHAPE_ATTRIBUTE = ?, ALGORITHM_ID = ?, MAP_SELECTION = ?, BUFFER = ? WHERE NODE_ID=?",
                    (_get_boolean_value(node.checkState(0)), node.text(0), data.icon, path2alias(data.file, alias), 
                    data.shape_attribute, _get_int_value(data.algorithm_id),
                     data.map_selection, _get_int_value(data.buffer), _get_int_value(data.node_id)))
            else:
                c.execute(
                    "INSERT INTO NODES (NODE_ID,TREE_ID,MAIN_NODE_ID,SELECTED,DESCRIPTION,ICON,FILE,SHAPE_ATTRIBUTE,ALGORITHM_ID,MAP_SELECTION,TYPE, ALGORITHM_SELECTION, BUFFER)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (data.node_id, data.tree_id, data.main_node_id, _get_boolean_value(node.checkState(0)), node.text(0), data.icon, 
                    path2alias(data.file, alias), data.shape_attribute,
                     data.algorithm_id, data.map_selection, data.type, data.algorithm_selection, data.buffer))
        else:
            c.execute(
                "INSERT INTO NODES (TREE_ID,MAIN_NODE_ID,SELECTED,DESCRIPTION,ICON,FILE,SHAPE_ATTRIBUTE,ALGORITHM_ID,MAP_SELECTION,TYPE, ALGORITHM_SELECTION, BUFFER)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (data.tree_id, data.main_node_id, _get_boolean_value(node.checkState(0)), node.text(0), data.icon, 
                path2alias(data.file, alias), data.shape_attribute, data.algorithm_id,
                 data.map_selection, data.type, data.algorithm_selection, data.buffer))
            data.node_id = c.lastrowid

        if data.parameters:
            update_parameters(c, data)
        remaining_node_ids.append(data.node_id)
        iterator += 1
    # remove all nodes that are not in the tree anymore (deleted)
    c.execute("SELECT NODE_ID FROM NODES WHERE TREE_ID = ?", (data.tree_id,))
    db_node_id_rows = c.fetchall()
    for db_node_id_row in db_node_id_rows:
        db_node_id = db_node_id_row["node_id"]
        if db_node_id not in remaining_node_ids:
            c.execute("DELETE FROM PARAMETERS WHERE NODE_ID = ?", (db_node_id,))
            c.execute("DELETE FROM NODES WHERE NODE_ID = ?", (db_node_id,))
    db.commit()
    c.close()
    db.close()


def delete_tree(tree_id):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT NODE_ID FROM NODES WHERE TREE_ID = ?", (tree_id,))
    db_node_id_rows = c.fetchall()
    for db_node_id_row in db_node_id_rows:
        db_node_id = db_node_id_row["node_id"]
        c.execute("DELETE FROM PARAMETERS WHERE NODE_ID = ?", (db_node_id,))
        c.execute("DELETE FROM NODES WHERE NODE_ID = ?", (db_node_id,))
    c.execute("DELETE FROM TREES WHERE TREE_ID = ?", (tree_id,))
    db.commit()
    c.close()


def update_parameters(c, data):
    for parameter in data.parameters.values():
        if parameter.parameter_id:
            c.execute("UPDATE PARAMETERS SET NODE_ID = ?, PARAMETER_NR = ?, VALUE = ?, ID_FIELD = ?, DATA_FIELD = ? WHERE PARAMETER_ID = ?",
                      (data.node_id, parameter.parameter_nr, parameter.value,
                       parameter.id_field, parameter.data_field, parameter.parameter_id))
        else:
            c.execute("INSERT INTO PARAMETERS (NODE_ID, PARAMETER_NR, VALUE, ID_FIELD, DATA_FIELD) VALUES (?, ?, ?, ?, ?)",
                      (data.node_id, parameter.parameter_nr, parameter.value, parameter.id_field, parameter.data_field))
            parameter.parameter_id = c.lastrowid


def initialize_tree_from_db(dockwidget, tree_id, alias = ALIAS):
    correct_city_boundary_path()
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM TREES WHERE TREE_ID=?", (tree_id,))
    tree = c.fetchone()
    dockwidget.titleLabel.setText(tree["name"])
    dockwidget.baseMapFile.setText(alias2path(tree["file"], alias))
    c.execute("SELECT * FROM NODES WHERE TREE_ID=? ORDER BY MIN(MAIN_NODE_ID, NODE_ID) ASC", (tree_id,))
    failed_nodes = []
    for row in c.fetchall():
        node = create_tree_node(row)
        failed_nodes.append(add_node(dockwidget.treeWidget, node))
    c.close()
    db.close()
    for node in failed_nodes:
        if node:
            add_node(dockwidget.treeWidget, node)


def get_node_file_by_id(node_id, alias = ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM NODES WHERE NODE_ID=?", (node_id,))
    result = c.fetchone()
    file = None
    if result:
        file = alias2path(result["file"], alias)
    c.close()
    db.close()
    return file


def get_node_map_selection_by_id(node_id, alias = ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM NODES WHERE NODE_ID=?", (node_id,))
    result = c.fetchone()
    file = None
    if result:
        file = alias2path(result["map_selection"], alias)
    c.close()
    db.close()
    return file


def get_node_attribute_by_id(node_id):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM NODES WHERE NODE_ID=?", (node_id,))
    attribute = c.fetchone()["shape_attribute"]
    c.close()
    db.close()
    return attribute


def get_node_description_by_id(node_id):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM NODES WHERE NODE_ID=?", (node_id,))
    description = c.fetchone()["description"]
    c.close()
    db.close()
    return description


def does_node_exist(node_id):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT 1 FROM NODES WHERE NODE_ID=?", (node_id,))
    result = c.fetchone()
    c.close()
    db.close()
    return result


def create_tree_node(row, alias = ALIAS):
    tree_node = TreeNode(row["node_id"], row["tree_id"], row["main_node_id"], row["selected"], row["description"], row["icon"], 
                         alias2path(row["file"], alias), row["shape_attribute"],
                         row["algorithm_id"], get_algorithm(row["algorithm_id"]), get_parameters(row["node_id"]), row["map_selection"],
                         row["type"], row["algorithm_selection"], row['buffer'])
    return tree_node


def get_crop_yield_old(country, crop_id):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM CROP_YIELDS WHERE COUNTRY=?", (country,))
    if AlgorithmEnum.CEREALS == crop_id:
        crop_yield = c.fetchone()["cereal"]
    elif AlgorithmEnum.GRAIN_MAIZE == crop_id:
        crop_yield = c.fetchone()["grain_maize"]
    elif AlgorithmEnum.WHEAT == crop_id:
        crop_yield = c.fetchone()["wheat"]
    elif AlgorithmEnum.BARLEY == crop_id:
        crop_yield = c.fetchone()["barley"]
    elif AlgorithmEnum.RAPE_SEEDS == crop_id:
        crop_yield = c.fetchone()["rape_seeds"]
    elif AlgorithmEnum.BASIC_AGRICULTURE == crop_id:
        crop_yield = c.fetchone()["basic"]

    c.close()
    db.close()
    return crop_yield


def get_energy_production_factor(crop_id):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM ENERGY_PRODUCTION_FACTOR WHERE CROP_ID=?", (crop_id,))
    factor = c.fetchone()["factor"]
    c.close()
    db.close()
    return float(factor) / 3600


def get_tooltip(algorithm_id, field_nr):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT DESCRIPTION FROM TOOLTIPS WHERE ALGORITHM_ID=? AND FIELD_NR=?", (algorithm_id, field_nr))
    result = c.fetchone()
    if result:
        description = result["description"]
    else:
        description = ''
    c.close()
    db.close()
    description = description.replace('$path', os.path.dirname(__file__))
    description = '<span>' + description + '</span>'
    return description


def get_node_by_id(node_id, alias = ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM NODES WHERE NODE_ID = ?", (_get_int_value(node_id),))
    row = c.fetchone()
    node = TreeNode(row["node_id"], row["tree_id"], row["main_node_id"], row["selected"], row["description"], row["icon"], 
                    alias2path(row["file"], alias), row["shape_attribute"],
                    row["algorithm_id"], get_algorithm(row["algorithm_id"]), get_parameters(row["node_id"]), row["map_selection"],
                    row["type"], row["algorithm_selection"], row['buffer'])
    c.close()
    db.close()
    return node


def _get_boolean_value(boolean_val):
    if boolean_val == Qt.Checked:
        return 1
    return 0


def _get_int_value(text_val):
    if text_val is None or text_val == '':
        return None
    return int(text_val)


# Master integration
def path2alias(path, alias):
    if type(path) == str and os.path.exists(path) and alias:

        # if already in the project folder
        if path.startswith(mm_config.CURRENT_MAPPING_DIRECTORY):
            return path.replace(mm_config.CURRENT_MAPPING_DIRECTORY, 
                        mm_config.ALIAS_MAPPING_DIRECTORY)

        # else, need to copy the file
        else:
            input_folder = os.path.join(mm_config.CURRENT_MAPPING_DIRECTORY, 
                                mm_config.INPUT_FOLDER)
            os.makedirs(input_folder, exist_ok=True)
            new_file_path = os.path.join(input_folder, os.path.basename(path))
            file_to_copy = {path: new_file_path}
            if path.endswith(".shp"):
                for ext in [".cpg", ".dbf", ".prj", ".qpj", ".shx"]:
                    file_to_copy[path[:-4]+ext] = new_file_path[:-4]+ext
            error_occured = False
            for f in file_to_copy:
                try:
                    shutil.copy2(f, file_to_copy[f])
                except IOError:
                    error_occured = True

            return os.path.join(mm_config.ALIAS_MAPPING_DIRECTORY, 
                                mm_config.INPUT_FOLDER, 
                                os.path.basename(path))
    else:
        return path

def alias2path(path, alias):
    if type(path) == str and alias:
        return path.replace(mm_config.ALIAS_MAPPING_DIRECTORY,
                            mm_config.CURRENT_MAPPING_DIRECTORY)
    else:
        return path

def correct_city_boundary_path(alias=ALIAS):
    db = sqlite3.connect(mm_config.CURRENT_DB_CMM_SMM_FILE_PATH)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    c.execute("SELECT * FROM NODES WHERE DESCRIPTION=?", ("city boundary",))
    result = c.fetchone()
    if result:
        file = alias2path(result["file"], alias)
        if not os.path.exists(file):
            tree_id = result["tree_id"]
            c.execute("SELECT * FROM TREES WHERE TREE_ID=?", (tree_id,))
            result = c.fetchone()
            if result:
                new_file = result["file"]
                c.execute("UPDATE NODES SET FILE=? WHERE DESCRIPTION=?", (new_file,"city boundary",))
    db.commit()
    c.close()