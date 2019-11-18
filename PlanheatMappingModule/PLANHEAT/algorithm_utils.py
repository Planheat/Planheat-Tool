import csv
import time
import math

import numpy as np
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QColor
from qgis.core import QgsMessageLog
from osgeo import ogr
from .algorithms import dasymap_calculator, weighted_distribution_calculator
from .cache_utils import read_as_array, clear_raster_cache, get_country, set_country
from .database_utils import get_algorithms, get_tree_by_id, get_node_file_by_id, get_node_map_selection_by_id, get_node_attribute_by_id, get_node_by_id
from .io_utils import get_base_raster, create_file_and_layer, open_file_as_raster, rasterize_base_map, \
    load_file_as_layer, get_feature_list, clear_io_cache, reproject_shape_file, load_planning_module_data, buffer, calculate_shape_area_and_rasterize, is_shape_file_polygons, \
    get_temp_folder_name, copy_and_add_id_column, extract_masked_shapefile, get_crs, remove_files_with_name_like,get_parent_node_description,save_array_as_tif
from .layer_utils import read_table_data, move_active_vector_layer_to_top
from .node_utils import get_node_data, is_checked, is_input_file_node, is_algorithm_node
from .enums import AlgorithmEnum
from calendar import monthrange

from .client_api_utils import get_map, clear_api_cache, get_crop_yield

result_table = []
progress = None


def clear_all_caches():
    clear_raster_cache()
    result_table.clear()
    clear_io_cache()
    clear_api_cache()


def set_progress(prog):
    global progress
    progress = prog


def run_algorithm(node, algorithm, group_name=None, original_call=True, only_checked=False):
    global progress
    progress.setValue(progress.value() + 1)
    progress.show()
    print('Algorithm: ', algorithm)
    QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
    try:
        if group_name is None:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            group_name = timestr + " - " + get_node_data(node).description
        algorithms = get_algorithms()
        if algorithm != AlgorithmEnum.SUM and algorithm != AlgorithmEnum.NONE:
            if (not get_node_data(node).parameters or 1 not in get_node_data(node).parameters or get_node_data(node).parameters[1].value == '-1'):
                print('empty parameters')
                return
            if get_node_data(node).parameters and (1 not in get_node_data(node).parameters or get_node_data(node).parameters[1].value == '-1'):
                print('skip')
                return

        algorithm_id = algorithms[algorithm].algorithm_id
        if algorithm_id == AlgorithmEnum.NONE:
            return _calculate_none(node, group_name, only_checked=only_checked)
        if algorithm_id == AlgorithmEnum.SUM:
            return _calculate_sum(node, group_name, original_call, only_checked=only_checked)
        if algorithm_id == AlgorithmEnum.DASYMAP:
            return _calculate_dasymap(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.W_DIST or algorithm_id == AlgorithmEnum.W_DIST2:
            return _calculate_weighted_distribution(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.SPREAD:
            return _calculate_spread(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.SOLAR:
            return _calculate_solar(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.PROVIDED:
            return _calculate_provided(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.BIO_FORESTERY:
            return _calculate_bio_forestry(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.CEREALS or algorithm_id == AlgorithmEnum.GRAIN_MAIZE or algorithm_id == AlgorithmEnum.WHEAT or algorithm_id == AlgorithmEnum.BARLEY or algorithm_id == AlgorithmEnum.RAPE_SEEDS:
            return _calculate_bio_agriculture_adv(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.BASIC_AGRICULTURE:
            return _calculate_bio_agriculture_basic(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.SEWER_SYSTEM:
            return _calculate_sewer_system_heat(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.RIVERS_HEAT:
            return _calculate_from_rivers_heat(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.RIVERS_COLD:
            return _calculate_from_rivers_cold(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.RIVERS_FREE_COLD:
            return _calculate_from_rivers_free_cold(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.LAKES_HEAT:
            return _calculate_from_lakes_heat(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.LAKES_COLD:
            return _calculate_from_lakes_cold(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.SHALLOW_GEOTHERMAL:
            return _calculate_from_shallow_geothermal(node, group_name, original_call)
        if algorithm_id == AlgorithmEnum.DEEP_GEOTHERMAL:
            return _calculate_provided(node, group_name, original_call)
    except TypeError as e:
        QMessageBox.critical(None, "Error", "Node " + node.text(0) + " gives an error. \nPlease check that you filled the fields correctly. \n\nThe first field is mandatory.")
        print(e)


def _calculate_sum(node, group_name, original_call, only_checked=False):
    base_raster = get_base_raster(node)
    result = np.zeros_like(read_as_array(base_raster))
    nb_checked_child = 0
    for pos in range(0, node.childCount()):
        child_node = node.child(pos)
        if is_checked(child_node) or not only_checked:
            result = _process_node_and_subnodes_sum(child_node, group_name, result, only_checked=only_checked)
    if original_call and nb_checked_child > 0:
        create_file_and_layer("Sum", group_name, node, result, result_table, base_raster)
    return result


def _process_node_and_subnodes_sum(node, group_name, result, only_checked=False):
    node_data = get_node_data(node)

    if is_algorithm_node(node):
        alg_result = run_algorithm(node, node_data.algorithm_id, group_name, True, only_checked=only_checked)
        if alg_result is not None:
            alg_result[np.isnan(alg_result)] = 0
            result = np.add(result, alg_result)
    return result


def _calculate_none(node, group_name, only_checked=False):
    base_raster = get_base_raster(node)
    result = np.zeros_like(read_as_array(base_raster))
    for pos in range(0, node.childCount()):
        child_node = node.child(pos)
        if is_checked(child_node) or not only_checked:
            result = _process_node_and_subnodes_no_algortihm(child_node, group_name, only_checked=only_checked)
    return result


def _calculate_provided(node, group_name, original_call):
    node_data = get_node_data(node)
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    buffer_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_file)

    provided_map_file = get_node_input_file_by_id(parameters[1].value)
    provided_map = open_file_as_raster(provided_map_file, base_raster, attribute=get_node_attribute_by_id(parameters[1].value), buffer_extent=buffer_file)
    result = read_as_array(provided_map)
    result[result <= -9999] = np.NaN
    efficiency_factor = float(parameters[6].value) / 100
    result = result * efficiency_factor * buffer_mask
    result = result * get_spatial_constraints(buffer_raster, parameters, 2)
    if original_call:
        is_shape, output_shp = extract_masked_shapefile(buffer_file,get_parent_node_description(node) + node_data.description+"_inputdata_"+str(round(time.time() * 1000))+".shp",provided_map_file, base_raster)
        if is_shape:
            min_val, max_val = create_file_and_layer("", group_name, node, result, result_table, base_raster, load_layer=False)
            load_file_as_layer(output_shp, node_data.description, group_name, min_val=min_val, max_val=max_val, attribute = get_node_attribute_by_id(parameters[1].value))
        else:
             create_file_and_layer("", group_name, node, result, result_table, base_raster)

    return result


def _process_node_and_subnodes_no_algortihm(node, group_name, only_checked=False):
    node_data = get_node_data(node)
    if is_algorithm_node(node):
        return run_algorithm(node, node_data.algorithm_id, group_name, True, only_checked=only_checked)

    if is_input_file_node(node):
        node_map = open_file_as_raster(node_data.file, get_base_raster(node))
        return read_as_array(node_map)


def _calculate_dasymap(node, group_name, original_call):
    t = time.time()
    result, base_map = _do_dasymap(get_tree_by_id(get_node_data(node).tree_id), get_node_data(node).parameters)
    print("d :" + str(time.time() - t))
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, like_raster=base_map)
    return result


def _do_dasymap(tree, parameters):
    zone_map_file = get_node_input_file_by_id(parameters[1].value)
    class_map_file = get_node_input_file_by_id(parameters[2].value)
    class_weight_file = get_node_input_file_by_id(parameters[3].value)
    zone_value_file = get_node_input_file_by_id(parameters[4].value)
    base_map = rasterize_base_map(tree)
    zone_map = open_file_as_raster(zone_map_file, base_map, attribute=get_node_attribute_by_id(parameters[1].value))
    class_map = open_file_as_raster(class_map_file, base_map, attribute=get_node_attribute_by_id(parameters[2].value))

    width = zone_map.RasterXSize
    height = zone_map.RasterYSize
    if class_map.RasterXSize != width or class_map.RasterYSize != height:
        QgsMessageLog.logMessage("landuse layer {}x{} regions layer {}x{}".format(width, height, class_map.RasterXSize, class_map.RasterYSize), level=QgsMessageLog.WARNING)
        raise RuntimeError("Provided layers differ in size")

    if zone_map.RasterCount != 1 or class_map.RasterCount != 1:
        raise RuntimeError("Provided layers should only contain one raster band")

    zone_map_data = read_as_array(zone_map)
    class_map_data = read_as_array(class_map)
    class_weight_data = read_table_data(class_weight_file, parameters[3].id_field, parameters[3].data_field)
    zone_value_data = read_table_data(zone_value_file, parameters[4].id_field, parameters[4].data_field)

    result = dasymap_calculator.calculate(np.NaN, class_map_data, class_weight_data, zone_map_data, zone_value_data)

    return result, base_map


def run_algorithm_for_node(node, algorithm_id):
    clear_all_caches()
    tree = get_tree_by_id(get_node_data(node).tree_id)
    get_feature_list(tree.file, tree.attribute_name)
    run_algorithm(node, algorithm_id)
    move_active_vector_layer_to_top()


def run_all(root_tree, prog, only_checked=False):
    global progress
    progress = prog

    clear_all_caches()
    node = root_tree.invisibleRootItem()
    if node.child(0):
        tree = get_tree_by_id(get_node_data(node.child(0)).tree_id)
        result_csv = get_temp_folder_name() + r"/planheat_result_" + str(tree.type) + ".csv"
        print('####',result_csv)
        f = open(result_csv, "w+")
        f.close()
        tree_description = tree.description
        names = get_feature_list(tree.file, tree.attribute_name)
        headers = ["Class", "Description", "Selected"] + names
        result_table.append(headers)
        _clear_files_from_algorithm_nodes(node)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        group_name = timestr + " - All"

        if valid_structure(node):
            for pos in range(0, node.childCount()):
                child_node = node.child(pos)
                run_algorithm(child_node, get_node_data(child_node).algorithm_id, group_name, only_checked=only_checked)
        print(result_table)
        with open(result_csv, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='\t')
            for line in result_table:
                writer.writerow(line)

        layer = load_file_as_layer(result_csv, "Result Table", group_name)
        move_active_vector_layer_to_top()
        return True
    else:
        QMessageBox.information(None, "Error", "Please load a project first.")
        return False


def _clear_files_from_algorithm_nodes(node):
    for pos in range(0, node.childCount()):
        child_node = node.child(pos)
        if is_algorithm_node(child_node):
            get_node_data(child_node).file = None
            _clear_files_from_algorithm_nodes(child_node)


def valid_structure(node):
    for pos in range(0, node.childCount()):
        child_node = node.child(pos)
        if is_algorithm_node(child_node):
            if count_selected_children(child_node) > 1 and get_node_data(child_node).algorithm_id == 1:
                QMessageBox.information(None, "Error", "Can not have a node with multiple children that has no algorithm.")
                return False
            else:
                if not valid_structure(child_node):
                    return False
        if is_input_file_node(child_node):
            if get_node_data(child_node).map_selection == 'From file' and get_node_data(child_node).file is None:
                QMessageBox.information(None, "Error", "Can not have a selected node without file: " + node.text(0) + " - " + child_node.text(0))
                return False
    return True


def count_selected_children(node):
    result = 0
    for i in range(node.childCount()):
        child = node.child(i)
        if is_checked(child) and is_input_file_node(child):
            result += 1
    return result


def _calculate_weighted_distribution(node, group_name, original_call):
    t = time.time()
    result, base_map, area_array = _do_weighted_distribution(node)
    print("w :" + str(time.time() - t))
    if original_call:
        t = time.time()
        create_file_and_layer("", group_name, node, result, result_table, like_raster=base_map, save_result=False)
        result = np.where(area_array > 0, result, 0)
        create_file_and_layer("", group_name, node, result, result_table, like_raster=base_map, load_layer=False)
        print("f :" + str(time.time() - t))
    return result


def _do_weighted_distribution(node):
    node_data = get_node_data(node)
    parameters = node_data.parameters
    regions_file = get_tree_by_id(get_node_data(node).tree_id).area_file
    base_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_shapefile=regions_file)
    base_map_data = read_as_array(base_raster)
    area_file = get_tree_by_id(get_node_data(node).tree_id).file
    weights_file = get_node_input_file_by_id(parameters[1].value)
    regions_layer = open_file_as_raster(regions_file, base_raster)
    area_layer = open_file_as_raster(area_file, base_raster)
    # print('####',get_node_attribute_by_id(parameters[1].value))
    # weights_layer = open_file_as_raster(weights_file, base_raster, attribute=get_node_attribute_by_id(parameters[1].value), add=True)
    weights_data = get_combined_source_map(base_raster, None, base_raster, node, parameters)

    width = weights_data.shape[1]
    height = weights_data.shape[0]
    if regions_layer.RasterXSize != width or regions_layer.RasterYSize != height:
        QgsMessageLog.logMessage("weights layer {}x{} regions layer {}x{}".format(width, height, regions_layer.RasterXSize, regions_layer.RasterYSize))
        raise RuntimeError("Provided layers differ in size")

    regions_data = read_as_array(regions_layer)
    area_data = read_as_array(area_layer)
    # region_dist_data = read_table_data(region_dist_file, parameters[3].id_field, parameters[3].data_field)
    region_dist_data = np.array([0, load_planning_module_data(node)])
    if parameters[2].value and parameters[2].value != '-1' and parameters[2].value != -1:
        urban_heat_island_file = get_node_input_file_by_id(parameters[2].value)
        urban_heat_island_layer = open_file_as_raster(urban_heat_island_file, base_raster)
        urban_heat_island_data = read_as_array(urban_heat_island_layer) * regions_data
        # redistribute weights map with heat island map. keep same sum
        urban_heat_island_data[urban_heat_island_data <= 0] = np.NaN
        urban_heat_island_data = np.where(weights_data > 0, urban_heat_island_data, np.NaN)
        urban_heat_island_data = urban_heat_island_data / np.nansum(urban_heat_island_data)
        weights_data = np.where(weights_data > -9999, weights_data, np.NaN)
        original_sum = np.nansum(weights_data)
        weights_data = weights_data * urban_heat_island_data
        weights_data = weights_data / np.nansum(weights_data)
        weights_data = weights_data * original_sum
    save_array_as_tif("c:/temp/osm.tif", weights_data, base_raster)

    result = weighted_distribution_calculator.compute_weighted_distribution(np.NaN, weights_data, regions_data, region_dist_data)

    return result, base_raster, area_data


def _calculate_spread(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    raster = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), get_base_raster(node))

    input_array = read_as_array(raster)
    total_sum = np.nansum(input_array)
    factor = float(parameters[2].value) / total_sum

    result = input_array * factor
    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("Spread", group_name, node, result, result_table, raster)
    return result, raster


def _calculate_bio_forestry(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    parameters[1].id_field = "-1"
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    tree = get_tree_by_id(get_node_data(node).tree_id)
    buffer_raster = rasterize_base_map(tree, buffer_file)
    set_progress_if_zero()
    source_combined = get_combined_source_map(base_raster, buffer_file, buffer_raster, node, parameters)
    source_combined[source_combined <= -9999] = np.NaN
    multiply_raster = open_file_as_raster(get_node_input_file_by_id(parameters[2].value), base_raster, attribute=get_node_attribute_by_id(parameters[2].value))

    multiply_array = read_as_array(multiply_raster)  # (mwh/ton)

    efficiency_factor = float(parameters[6].value) / 100
    # source_combined is avg m2/cell
    result = source_combined * multiply_array * buffer_mask * efficiency_factor / 10000 * tree.resolution * tree.resolution

    result = result * get_spatial_constraints(buffer_raster, parameters, 3)

    result[result <= -9999] = np.NaN
    result[result == 0] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, base_raster, value_color=QColor('#119600'))
    return result


def _get_buffer_mask_area_file(node):
    buffer_mask, buffer_shape, buffer_extent, area_file = _get_buffer_mask_for_node_data(get_node_data(node))
    return buffer_mask, buffer_shape, buffer_extent

def _get_buffer_mask_tree_file(node):
    buffer_mask, buffer_shape, buffer_extent, area_file = _get_buffer_mask_for_tree_data(get_node_data(node))
    return buffer_mask, buffer_shape, buffer_extent


def _get_buffer_mask_for_node_data(node_data):
    tree = get_tree_by_id(node_data.tree_id)
    buffer_size = tree.buffer_size
    if node_data.buffer is not None:
        buffer_size = int(node_data.buffer)
    buffer_shape, buffer_extent = buffer(tree.area_file, buffer_size * 1000)
    buffer_mask = read_as_array(rasterize_base_map(tree, buffer_shape))
    print(np.sum(buffer_mask))
    buffer_mask[buffer_mask > 0] = 1
    buffer_mask[buffer_mask < 0] = 0

    return buffer_mask, buffer_shape, buffer_extent, tree.area_file

def _get_buffer_mask_for_tree_data(node_data):
    tree = get_tree_by_id(node_data.tree_id)
    buffer_size = tree.buffer_size
    if node_data.buffer is not None:
        buffer_size = int(node_data.buffer)
    buffer_shape, buffer_extent = buffer(tree.file, buffer_size * 1000)
    buffer_mask = read_as_array(rasterize_base_map(tree, buffer_shape))
    buffer_mask[buffer_mask > 0] = 1
    buffer_mask[buffer_mask < 0] = 0

    return buffer_mask, buffer_shape, buffer_extent, tree.file


def get_buffer_extent_and_crs(node):
    return get_buffer_extent_and_crs_for_node_data(get_node_data(node))


def get_buffer_extent_and_crs_for_node_data(node_data):
    _, buffer_file, buffer_extent, area_file = _get_buffer_mask_for_node_data(node_data)
    crs = get_crs(area_file)
    return buffer_extent, crs, area_file

def get_buffer_extent_and_crs_for_tree_data(node_data):
    _, buffer_file, buffer_extent, area_file = _get_buffer_mask_for_tree_data(node_data)
    crs = get_crs(area_file)
    return buffer_extent, crs, area_file


def _calculate_solar(node, group_name, original_call):
    get_node_data(node).buffer = 0
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    parameters[1].id_field = "calculate feature areas"
    set_progress_if_zero()
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    tree = get_tree_by_id(get_node_data(node).tree_id)
    buffer_raster = rasterize_base_map(tree, buffer_file)
    source_combined = get_combined_source_map(buffer_raster, buffer_file, buffer_raster, node, parameters)
    technical_suitability_factor = float(parameters[2].value) / 100
    pvgis_dataset = open_file_as_raster(get_node_input_file_by_id(parameters[3].value), buffer_raster, attribute=get_node_attribute_by_id(parameters[3].value))
    efficiency_factor = float(parameters[6].value) / 100

    pvgis_array = read_as_array(pvgis_dataset)
    pvgis_array[pvgis_array <= -9999] = np.NaN
    result = source_combined * technical_suitability_factor * efficiency_factor * pvgis_array * buffer_mask

    result = result * get_spatial_constraints(buffer_raster, parameters, 5)

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster)
    return result


def spread_values_over_raster_with_same_id(base_raster, parameters, source_combined):
    print("spread values")
    folder_name = get_temp_folder_name()
    output_file = folder_name + "//" + str(round(time.time() * 1000)) + "-copy_with_id.shp"
    copy_and_add_id_column(get_node_input_file_by_id(parameters[1].value), output_file)
    # spread centroid points over the raster area of the shapes
    source_ids = open_file_as_raster(output_file, base_raster, attribute='ID_GEN')
    source_id_array = read_as_array(source_ids)
    source_combined = spread_values_over_areas_with_same_id(source_id_array, source_combined)
    source_combined = source_combined
    remove_files_with_name_like(output_file)
    return source_combined


def _calculate_bio_agriculture_adv(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    parameters[1].id_field = "calculate feature areas"
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    tree = get_tree_by_id(get_node_data(node).tree_id)
    buffer_raster = rasterize_base_map(tree, buffer_file)
    set_progress_if_zero()
    source_combined = get_combined_source_map(base_raster, buffer_file, buffer_raster, node, parameters, buffer_extent=buffer_file)
    straw_yield = calculate_straw_yield(float(parameters[2].value))
    technical_suitability_factor = float(parameters[3].value) / 100

    energy_production_factor = float(parameters[4].value) * 1000
    source_combined[source_combined <= -9999] = np.NaN
    efficiency_factor = float(parameters[6].value) / 100

    result = source_combined * straw_yield * technical_suitability_factor * energy_production_factor * buffer_mask * efficiency_factor / 10000 * tree.resolution * tree.resolution

    result = result * get_spatial_constraints(buffer_raster, parameters, 5)

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster, value_color=QColor('#f4d942'))
    return result


def _calculate_bio_agriculture_basic(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    parameters[1].id_field = "-1"
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    tree = get_tree_by_id(get_node_data(node).tree_id)
    buffer_raster = rasterize_base_map(tree, buffer_file)
    set_progress_if_zero()
    source_combined = get_combined_source_map(base_raster, buffer_file, buffer_raster, node, parameters)
    source_combined = source_combined.astype(np.float32)
    source_combined[source_combined != 1] = np.NaN
    energy_production_factor = float(parameters[2].value)
    technical_suitability_factor = float(parameters[3].value) / 100
    efficiency_factor = float(parameters[6].value) / 100

    result = source_combined * energy_production_factor * technical_suitability_factor * buffer_mask * efficiency_factor / 10000 * tree.resolution * tree.resolution

    result = result * get_spatial_constraints(buffer_raster, parameters, 4)

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster, value_color=QColor('#f4d942'))
    return result


def _calculate_sewer_system_heat(node, group_name, original_call):
    get_node_data(node).buffer = 0
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    tree = get_tree_by_id(get_node_data(node).tree_id)
    buffer_raster = rasterize_base_map(tree, buffer_file)
    set_progress_if_zero()
    source_combined = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), buffer_raster).ReadAsArray()
    source_combined = source_combined.astype(np.float32)

    area = tree.resolution * tree.resolution / 10000
    population_density = source_combined
    # Eheat = 2 x (A x PD) x 200 / 24 / 1000 x 4200 x tmonth / (3.6 *10^3) [kWh]
    efficiency_factor = float(parameters[6].value) / 100
    monthly_temperatures = parameters[99].value.split(';')
    result = 0.
    spatial_constraints = get_spatial_constraints(buffer_raster, parameters, 2)
    for i in range(1, 13):
        month_temp = float(monthly_temperatures[i - 1])
        month_result = 2 * area * population_density * 200 / 24 / 1000 * 4200 * 24 * monthrange(2018, i)[1] / 3600 / 1000
        result += month_result
        create_file_and_layer("" + str(i) + "_t" + str(month_temp), group_name, node, result * efficiency_factor * buffer_mask * spatial_constraints, result_table,
                              buffer_raster, load_layer=False, save_result=False)
    result = result * efficiency_factor * buffer_mask
    result = result * spatial_constraints

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, base_raster)
    return result


def _calculate_from_rivers_heat(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    buffer_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_file)
    set_progress_if_zero()
    if parameters[2].value is None or parameters[2].value == '':
        source_combined = get_combined_source_map(base_raster, buffer_file, buffer_raster, node, parameters, buffer_extent=buffer_file)
    else:
        source_map = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), buffer_raster, add=True, buffer_extent=buffer_file)
        source_combined = read_as_array(source_map)
        # save_array_as_tif("c:/temp/a.tif", source_combined, base_raster)
        source_combined = source_combined * float(parameters[2].value)
    source_combined = source_combined.astype(np.float32)

    Kmax = 6
    Tmin = 2
    # Eheat = K x Q x 4200 x tmonth / (3.6 *10^3) [kWh]

    efficiency_factor = float(parameters[6].value) / 100
    monthly_temperatures = parameters[99].value.split(';')
    result = 0.
    spatial_constraints = get_spatial_constraints(buffer_raster, parameters, 3)
    for i in range(1, 13):
        month_temp = float(monthly_temperatures[i - 1])
        K = month_temp - Tmin
        if K > Kmax:
            K = Kmax
        month_result = K * source_combined * 4200 * 24 * monthrange(2018, i)[1] / 3600 / 1000
        result += month_result
        create_file_and_layer("" + str(i) + "_t" + str(month_temp), group_name, node, result * efficiency_factor * buffer_mask * spatial_constraints, result_table,
                              buffer_raster, load_layer=False, save_result=False)
    result = result * efficiency_factor * buffer_mask

    result = result * spatial_constraints

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster)
    return result


def _calculate_from_rivers_cold(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    buffer_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_file)
    set_progress_if_zero()
    if parameters[2].value is None or parameters[2].value == '':
        source_combined = get_combined_source_map(base_raster, buffer_file, buffer_raster, node, parameters, buffer_extent=buffer_file)
    else:
        source_map = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), buffer_raster, add=True, buffer_extent=buffer_file)
        source_combined = read_as_array(source_map)
        source_combined = source_combined * float(parameters[2].value)
    source_combined = source_combined.astype(np.float32)

    Kmax = 2
    Tmaxout = 25
    # Ecooling = K x Q x 4200 x tmonth / (3.6 *10^3) [kWh]

    efficiency_factor = float(parameters[6].value) / 100
    monthly_temperatures = parameters[99].value.split(';')
    result = 0.
    spatial_constraints = get_spatial_constraints(buffer_raster, parameters, 3)
    for i in range(1, 13):
        month_temp = float(monthly_temperatures[i - 1])
        K = Tmaxout - month_temp
        if K > Kmax:
            K = Kmax
        if month_temp > Tmaxout:
            K = 0
        K = K * -1

        month_result = K * source_combined * 4200 * 24 * monthrange(2018, i)[1] / 3600 / 1000
        result += month_result
        create_file_and_layer("" + str(i) + "_t" + str(month_temp), group_name, node, result * efficiency_factor * buffer_mask * spatial_constraints, result_table,
                              buffer_raster, load_layer=False, save_result=False)

    result = result * efficiency_factor * buffer_mask * spatial_constraints

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster)
    return result


def _calculate_from_rivers_free_cold(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    buffer_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_file)
    set_progress_if_zero()
    if parameters[2].value is None or parameters[2].value == '':
        source_combined = get_combined_source_map(base_raster, buffer_file, buffer_raster, node, parameters, buffer_extent=buffer_file)
    else:
        source_map = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), buffer_raster, add=True, buffer_extent=buffer_file)
        source_combined = read_as_array(source_map)
        source_combined = source_combined * float(parameters[2].value)
    source_combined = source_combined.astype(np.float32)

    Kmax = 2
    Tmaxin = 18
    Tmaxout = 21
    # Ecooling = K x Q x 4200 x tmonth / (3.6 *10^3) [kWh]

    efficiency_factor = float(parameters[6].value) / 100
    monthly_temperatures = parameters[99].value.split(';')
    result = 0.
    spatial_constraints = get_spatial_constraints(buffer_raster, parameters, 3)
    for i in range(1, 13):
        month_temp = float(monthly_temperatures[i - 1])
        K = Tmaxout - month_temp
        if K > Kmax:
            K = Kmax
        if month_temp > Tmaxout:
            K = 0
        if month_temp < Tmaxin:
            K = 0

        K = K * -1

        month_result = K * source_combined * 4200 * 24 * monthrange(2018, i)[1] / 3600 / 1000
        result += month_result
        create_file_and_layer("" + str(i) + "_t" + str(month_temp), group_name, node, result * efficiency_factor * buffer_mask * spatial_constraints, result_table,
                              buffer_raster, load_layer=False, save_result=False)

    result = result * efficiency_factor * buffer_mask * spatial_constraints

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster)
    return result


def _calculate_from_lakes_heat(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    buffer_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_file)
    set_progress_if_zero()

    area_raster, _ = calculate_shape_area_and_rasterize(node, get_node_input_file_by_id(parameters[1].value), base_raster, buffer_file)
    area_raster_array = read_as_array(area_raster)
    area_raster_array = spread_values_over_raster_with_same_id(base_raster, parameters, area_raster_array)
    area_raster_array = np.where(area_raster_array <= 0, 0, area_raster_array)
    if parameters[3].value is None or parameters[3].value == '':
        source_value_raster = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), buffer_raster, attribute=parameters[1].id_field)
        source_value = read_as_array(source_value_raster)
    else:
        source_value = float(parameters[3].value)
    source_combined = source_value * area_raster_array

    source_combined = source_combined.astype(np.float32)

    Kmax = 6
    Tmin = 2

    # Q = A x d / h
    # Eheat = K x Q x 4200 x tmonth / (3.6 *10^3) [kWh]
    season_hours = float(parameters[2].value)
    Q = source_combined / season_hours
    efficiency_factor = float(parameters[6].value) / 100
    monthly_temperatures = parameters[99].value.split(';')
    result = 0.
    spatial_constraints = get_spatial_constraints(buffer_raster, parameters, 4)
    for i in range(1, 13):
        month_temp = float(monthly_temperatures[i - 1])
        K = month_temp - Tmin
        if K > Kmax:
            K = Kmax

        month_result = K * Q * 4200 * 24 * monthrange(2018, i)[1] / 3600 / 1000
        result += month_result
        create_file_and_layer("" + str(i) + "_t" + str(month_temp), group_name, node, result * efficiency_factor * buffer_mask * spatial_constraints, result_table,
                              buffer_raster, load_layer=False, save_result=False)

    result = result * efficiency_factor * buffer_mask * spatial_constraints

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster)
    return result


def _calculate_from_lakes_cold(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_tree_file(node)
    buffer_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_file)
    set_progress_if_zero()

    area_raster, _ = calculate_shape_area_and_rasterize(node, get_node_input_file_by_id(parameters[1].value), base_raster, buffer_file)
    area_raster_array = read_as_array(area_raster)
    area_raster_array = spread_values_over_raster_with_same_id(base_raster, parameters, area_raster_array)
    area_raster_array = np.where(area_raster_array <= 0, 0, area_raster_array)

    if parameters[3].value is None or parameters[3].value == '':
        source_value_raster = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), buffer_raster, attribute=parameters[1].id_field)
        source_value = read_as_array(source_value_raster)
    else:
        source_value = float(parameters[3].value)

    source_combined = source_value * area_raster_array
    source_combined = source_combined.astype(np.float32)

    Kmax = 2
    Tmaxout = 25
    # Q = A x d / h
    # Eheat = K x Q x 4200 x tmonth / (3.6 *10^3) [kWh]
    season_hours = float(parameters[2].value)
    Q = source_combined / season_hours
    efficiency_factor = float(parameters[6].value) / 100
    monthly_temperatures = parameters[99].value.split(';')
    result = 0.
    spatial_constraints = get_spatial_constraints(buffer_raster, parameters, 4)
    for i in range(1, 13):
        month_temp = float(monthly_temperatures[i - 1])
        K = Tmaxout - month_temp
        if K > Kmax:
            K = Kmax
        if month_temp > Tmaxout:
            K = 0

        K = K

        month_result = K * Q * 4200 * 24 * monthrange(2018, i)[1] / 3600 / 1000
        result += month_result
        create_file_and_layer("" + str(i) + "_t" + str(month_temp), group_name, node, result * efficiency_factor * buffer_mask * spatial_constraints, result_table,
                              buffer_raster, load_layer=False, save_result=False)

    result = result * efficiency_factor * buffer_mask * spatial_constraints

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster)
    return result


def _calculate_from_shallow_geothermal(node, group_name, original_call):
    parameters = get_node_data(node).parameters
    base_raster = get_base_raster(node)
    buffer_mask, buffer_file, buffer_extent = _get_buffer_mask_area_file(node)
    buffer_raster = rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id), buffer_file)
    set_progress_if_zero()

    area_raster, _ = calculate_shape_area_and_rasterize(node, get_node_input_file_by_id(parameters[1].value), base_raster, buffer_file)
    area_raster_array = read_as_array(area_raster)
    area_raster_array = spread_values_over_raster_with_same_id(base_raster, parameters, area_raster_array)
    area_raster_array = np.where(area_raster_array <= 0, 0, area_raster_array)

    source_value = float(parameters[2].value)

    source_combined = source_value * area_raster_array
    source_combined = source_combined.astype(np.float32)

    efficiency_factor = float(parameters[6].value) / 100

    result = source_combined * efficiency_factor * buffer_mask * get_spatial_constraints(buffer_raster, parameters, 3)

    result[result <= -9999] = np.NaN
    if original_call:
        create_file_and_layer("", group_name, node, result, result_table, buffer_raster)
    return result


def get_spatial_constraints(buffer_raster, parameters, parameter_nr):
    if parameters[parameter_nr].value and parameters[parameter_nr].value != -1 and get_node_input_file_by_id(parameters[parameter_nr].value):
        mask_map = open_file_as_raster(get_node_input_file_by_id(parameters[parameter_nr].value), buffer_raster)
        mask_array = 1 - read_as_array(mask_map)
        return mask_array
    return 1


def get_combined_source_map(base_raster, buffer_file, buffer_raster, node, parameters, buffer_extent=None):
    if parameters[1].id_field == "calculate feature areas" or get_node_attribute_by_id(parameters[1].value) == "calculate feature areas":
        source_map, source_shape_file = calculate_shape_area_and_rasterize(node, get_node_input_file_by_id(parameters[1].value), base_raster, buffer_file)
        source_value_array = read_as_array(source_map)
        # spread centroid points over the raster area of the shapes
        source_id_raster = open_file_as_raster(source_shape_file, buffer_raster, attribute='ID_GEN')
        source_id_array = read_as_array(source_id_raster)
        tree = get_tree_by_id(get_node_data(node).tree_id)
        source_combined = spread_values_over_areas_with_same_id(source_id_array, source_value_array, base_raster)
        source_combined = np.where(source_combined != -9999, source_combined / (tree.resolution * tree.resolution), source_combined)
    else:
        #print(get_node_attribute_by_id(parameters[1].value))
        source_map = open_file_as_raster(get_node_input_file_by_id(parameters[1].value), buffer_raster, attribute=get_node_attribute_by_id(parameters[1].value), add=True,
                                         buffer_extent=buffer_file)
        source_combined = read_as_array(source_map)
        if is_shape_file_polygons(get_node_input_file_by_id(parameters[1].value)):
            source_combined = spread_values_over_raster_with_same_id(base_raster, parameters, source_combined)
    return source_combined


def set_progress_if_zero():
    global progress
    if progress.value() == 0:
        progress.setValue(1)
        progress.show()
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)


def spread_values_over_areas_with_same_id(source_id_array, source_point_value_array, like_raster=None):
    output = np.zeros_like(source_id_array)
    id_list, counts = np.unique(source_id_array[source_id_array > 0], return_counts=True)
    id_dict = dict(zip(id_list, counts))
    for id, count in id_dict.items():
        if count > 1:
            output[source_id_array == id] = np.sum(source_point_value_array[source_id_array == id]) / count
    source_combined = np.where(output > 0, output, source_point_value_array)
    source_combined = np.where(source_combined == 0, -9999, source_combined)
    source_combined = source_combined
    return source_combined


def get_crop_and_straw_yield_value(node, algorithm):
    crop_yield = get_crop_yield_value(node, algorithm)
    straw_yield = calculate_straw_yield(crop_yield)
    return crop_yield, straw_yield


def calculate_straw_yield(crop_yield):
    straw_yield = (crop_yield * 0.769) - (0.129 * math.atan((crop_yield - 6.7) / 1.5))
    return straw_yield


def get_crop_yield_value(node, algorithm):
    country = get_country_from_cache(node)
    #print(country)
    crop_yield, success = get_crop_yield(country, algorithm.algorithm_id)
    if success:
        #print(crop_yield)
        return crop_yield
    else:
        from .database_utils import get_crop_yield_old
        return get_crop_yield_old(country, algorithm.algorithm_id)


def get_node_input_file_by_id(node_id):
    map_selection = get_node_map_selection_by_id(node_id)
    if map_selection:
        db_node = get_node_by_id(node_id)
        buffer_extent, crs, area_file = get_buffer_extent_and_crs_for_node_data(db_node)
        result, success = get_map(map_selection, buffer_extent, crs, area_file)
        if success:
            return result
        else:
            return None
    return get_node_file_by_id(node_id)

def get_node_input_file_by_id_with_tree_area(node_id):
    map_selection = get_node_map_selection_by_id(node_id)
    if map_selection:
        db_node = get_node_by_id(node_id)
        buffer_extent, crs, area_file = get_buffer_extent_and_crs_for_tree_data(db_node)
        result, success = get_map(map_selection, buffer_extent, crs, area_file)
        if success:
            return result
        else:
            return None
    return get_node_file_by_id(node_id)


def get_country_from_cache(node):
    if get_country() is None:
        set_country(_get_country_for_region(node))
    return get_country()


def _get_country_for_region(node):
    region_shape_file = get_tree_by_id(get_node_data(node).tree_id).file
    region = ogr.Open(region_shape_file)
    region_layer = region.GetLayer()
    folder_name = get_temp_folder_name()
    db_node = get_node_by_id(get_node_data(node).node_id)
    buffer_extent, crs, _ = get_buffer_extent_and_crs_for_node_data(db_node)
    countries_file, _ = get_map("map-with-eu-countries", buffer_extent, crs)
    countries_reprojected = folder_name + "/countries_reprojected.shp"
    reproject_shape_file(countries_file, countries_reprojected, region_layer.GetSpatialRef())
    countries = ogr.Open(countries_reprojected)
    countries_layer = countries.GetLayer()
    for country in countries_layer:
        #print(country)
        country_geom = country.GetGeometryRef()
        region_layer.ResetReading()
        for feature in region_layer:
            feature_geom = feature.GetGeometryRef()
            f_area = feature_geom.GetArea()
            if country_geom.Intersects(feature_geom) and country_geom.Contains(feature_geom):
                return country.GetField('NUTS_ID')
            elif country_geom.Intersects(feature_geom):
                inters_geom = country_geom.Intersection(feature_geom)
                if (inters_geom.GetArea() / f_area) > 0.5:
                    return country.GetField('NUTS_ID')
    print("find country fail")
