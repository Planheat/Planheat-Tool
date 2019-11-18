import math
import time
import csv
import os
import glob
import numpy as np
import random
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
from osgeo import gdal, ogr, osr
from osgeo.gdalnumeric import BandWriteArray
from qgis.core import QgsVectorLayer, QgsField, QgsVectorFileWriter

from .cache_utils import put_raster_in_cache, get_raster_from_cache, read_as_array
from .database_utils import get_tree_by_id, get_node_description_by_id
from .layer_utils import load_file_as_layer, get_selection, add_id_attribute_to_layer
from .node_utils import get_node_data, find_parent_node
import tempfile

selection = None
id_list = []
temp_folder = None
gdal.UseExceptions()
ogr.UseExceptions()


def clear_io_cache():
    global selection
    selection = None
    id_list.clear()


def get_temp_folder_name(prefix='PlanHeat-', base_path=None):
    global temp_folder
    if base_path:
        temp_folder = None
    if not temp_folder:
        temp_folder = base_path#tempfile.TemporaryDirectory(suffix='', prefix=prefix, dir=base_path)
    return temp_folder#.name


def get_temp_folder():
    return temp_folder


def get_parent_node_description(node):
    node_data = get_node_data(node)
    parent_node = find_parent_node(node.treeWidget(), node_data.main_node_id)
    if parent_node:
        if get_node_data(parent_node).description == 'Advanced':
            return get_node_data(find_parent_node(node.treeWidget(), get_node_data(parent_node).main_node_id)).description + "-" + get_node_data(parent_node).description + "-"
        return get_node_data(parent_node).description + "-"
    return ""


def create_file_and_layer(algorithm_description, group_name, node, result, result_table, like_raster=None, value_color=None, load_layer=True, save_result=True):
    if result.shape[0] > 0 and result.shape[1] > 0:
        node_data = get_node_data(node)
        tree = get_tree_by_id(node_data.tree_id)
        params = get_node_data(node).parameters
        p_string = ""
        if params and 6 in params:
            p_string = "_e" + params[6].value
        file_name = get_temp_folder_name() + "\\" + get_parent_node_description(node) + node_data.description + "-" + algorithm_description + "_b" + str(
            node_data.buffer) + p_string + "-" + str(round(time.time() * 1000))[-6:] + ".tif"
        if like_raster is None:
            like_raster = rasterize_base_map(tree)
        if node_data.main_node_id:
            class_name = get_node_description_by_id(node_data.main_node_id)
        else:
            class_name = get_node_description_by_id(node_data.node_id)
        if save_result:
            save_array_in_results_table(result_table, result, like_raster, node_data.description, class_name, "Yes" if node.checkState(0) == Qt.Checked else "No")
        save_array_as_tif(file_name, result, like_raster)
        min_val = round(np.nanpercentile(result[np.nonzero(result)], 2), 6)
        max_val = round(np.nanpercentile(result[np.nonzero(result)], 98), 6)
        mean_val = np.round(np.nanmean(result[np.nonzero(result)]), 6)
        if load_layer and node.checkState(0) == Qt.Checked:
            load_file_as_layer(file_name, get_parent_node_description(node) + node_data.description + " result", group_name, min_val=min_val, max_val=max_val, mean_val=mean_val,
                               value_color=value_color,
                               area=float(tree.resolution) * float(tree.resolution))
        if result[np.nonzero(result)].size > 0:
            return np.round(np.nanmin(result[np.nonzero(result)]), 2), np.round(np.nanmax(result[np.nonzero(result)]), 2)


def get_base_raster(node):
    return rasterize_base_map(get_tree_by_id(get_node_data(node).tree_id))


def save_array_as_tif(output_path_name, array_to_save, like_raster):
    driver = gdal.GetDriverByName("GTiff")
    shape = array_to_save.shape
    if array_to_save.shape.__len__() == 1:
        shape1 = 1
    else:
        shape1 = shape[1]
    ds_out = driver.Create(output_path_name, shape1, shape[0], 1, gdal.GDT_Float32, options=['COMPRESS=LZW'])
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(like_raster.GetProjectionRef())
    ds_out.SetProjection(raster_srs.ExportToWkt())

    gt = like_raster.GetGeoTransform()

    ds_out.SetGeoTransform((gt[0], gt[1], 0.0, gt[3], 0.0, gt[5]))
    band_out = ds_out.GetRasterBand(1)
    band_out.SetNoDataValue(np.NaN)
    BandWriteArray(band_out, array_to_save.astype("float32"))
    ds_out = None
    band_out = None
    del driver, ds_out, band_out


def save_array_in_results_table(result_table, input_array, like_raster, description, class_name, selected):
    global selection
    if selection is None:
        selection, file = get_selection()
    values = []
    if selection:
        shape_dataset = rasterize_shape_dataset(selection, like_raster, attribute='ID_GEN')
        selection_array = read_as_array(shape_dataset)
        values = fill_values(selection_array, input_array)
    else:
        base_array = read_as_array(like_raster)
        values = fill_values(base_array, input_array)
    line = [class_name, description, selected] + values
    result_table.append(line)


def fill_values(zone_array, value_array):
    # values2 = []
    # for i in id_list:
    #     values2.append(round(np.nansum(value_array[zone_array == i]), 2))
    # sum of values per id in id_list where input_array[base_array == i] vectorized
    value_array_nonan = np.where(np.isnan(value_array), 0, value_array)
    bincount = np.round(np.bincount(zone_array.astype(int).ravel(), value_array_nonan.ravel()), 2)
    values = bincount[id_list[:len(bincount)]]
    # assert (np.alltrue(np.isclose(values.tolist(), values2)))
    return values.tolist()


def get_feature_list(file_name, tree_name_attribute):
    global selection
    global id_list
    selection_file = None
    id_list.clear()
    id_list.append(0)
    name_list = dict()
    name_list[0] = "Outside"
    result = []
    if selection is None:
        selection, selection_file = get_selection()
    if selection and selection_file:
        source_ds = QgsVectorLayer(selection_file, "sel")
    else: # fallback for no selection layer
        QMessageBox.information(None, "Warning", "No layer selected, this wil result in a single value table.")
        result.append("Outside")
        return result

    add_id_attribute_to_layer(source_ds)
    number = 1
    count = sum(1 for _ in source_ds.getFeatures());
    if count > 1 or len(source_ds.attributeList()) > 1:
        for feature in source_ds.getFeatures():
            id_attribute = feature['ID_GEN']
            if id_attribute:
                id_list.append(id_attribute)
            else:
                id_list.append(number)

            if tree_name_attribute and source_ds.fields().indexFromName(tree_name_attribute) >= 0:
                name_list[id_list[-1]] = feature[tree_name_attribute]
            else:
                name_list[id_list[-1]] = "area " + str(id_list[-1])
            number += 1
    else:
        id_list.append(1)
        name_list[number] = "Selection"

    for id in id_list:
        result.append(name_list[id])
    return result


def open_file_as_raster(input_file, like_raster, attribute=None, add=False, buffer_extent=None, save_shp=False):
    raster = get_raster_from_cache(input_file, attribute, add)
    if raster:
        return raster
    if input_file.endswith(".shp") or input_file.endswith(".gpkg") or input_file.endswith(".json"):
        # input is Vector
        raster = rasterize_shape(input_file, attribute=attribute, like_raster=like_raster, add=add, buffer_extent=buffer_extent, save_shp=save_shp)
        put_raster_in_cache(input_file, attribute, add, raster)
        return raster
    elif input_file.endswith(".tif") or input_file.endswith(".asc"):
        raster = gdal.Open(input_file)
        if not raster:
            raise RuntimeError("Could not open file: " + input_file)
        if raster.GetGeoTransform() != like_raster.GetGeoTransform():
            #print("warp")
            x_min, y_min, x_max, y_max, resolution = _get_raster_bounds(like_raster)
            projection = like_raster.GetProjectionRef()
            error_threshold = 0.125
            resampling = gdal.GRA_NearestNeighbour
            raster = gdal.Warp('', raster, format='MEM', width=like_raster.RasterXSize, height=like_raster.RasterYSize,
                               outputBounds=[x_min, y_min, x_max, y_max], dstSRS=projection, errorThreshold=error_threshold, resampleAlg=resampling)
            put_raster_in_cache(input_file, attribute, add, raster)
            #print(raster)
        return raster

    return None


def _get_raster_bounds(like_raster):
    gt = like_raster.GetGeoTransform()
    x_min = gt[0]
    y_max = gt[3]
    resolution = gt[1]
    y_min = y_max - (resolution * like_raster.RasterYSize)
    x_max = x_min + (resolution * like_raster.RasterXSize)
    return x_min, y_min, x_max, y_max, resolution


def rasterize_shape(input_file, like_raster, attribute=None, add=False, buffer_extent=None, save_shp=False):
    source_ds = ogr.Open(input_file)
    if not source_ds:
        raise RuntimeError("Could not open file: " + input_file)

    source_ds = reproject_shapefile(input_file, like_raster)

    raster = rasterize_shape_dataset(source_ds, like_raster, attribute, add, buffer_extent=buffer_extent, save_shp=save_shp)

    return raster


def reproject_shapefile(input_file, like_raster):
    source_ds = ogr.Open(input_file)
    source_layer = source_ds.GetLayer()
    sourceSR = source_layer.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(like_raster.GetProjectionRef())
    if sourceSR != targetSR:
        folder_name = get_temp_folder_name()
        if not os.path.exists(folder_name + "/temp"):
            os.mkdir(folder_name + "/temp")
        # add a random number to avoid name clashes within a millisecond on a fast computer
        input_file_reprojected = folder_name + "/temp/shp_reprojected_" + str(round(time.time() * 1000)) + "_" + str(random.randint(111111,999999)) + ".shp"
        #print(input_file_reprojected)
        source_ds = None
        reproject_shape_file(input_file, input_file_reprojected, targetSR)
        source_ds = ogr.Open(input_file_reprojected)
    return source_ds


def rasterize_shape_dataset(source_ds, like_raster, attribute=None, add=False, buffer_extent=None, save_shp=False):
    t = time.time()
    source_layer = source_ds.GetLayer()
    raster = gdal.GetDriverByName('MEM').Create("", like_raster.RasterXSize, like_raster.RasterYSize, 1, gdal.GDT_Float32)
    raster.SetGeoTransform(like_raster.GetGeoTransform())
    band = raster.GetRasterBand(1)
    band.SetNoDataValue(like_raster.GetRasterBand(1).GetNoDataValue())
    raster.SetProjection(like_raster.GetProjection())
    del band
    if buffer_extent:
        shp = ogr.Open(buffer_extent)
        layer = shp.GetLayer()
        union_poly = ogr.Geometry(ogr.wkbPolygon)
        layer.ResetReading()
        for feature in layer:
            geom = feature.GetGeometryRef()
            union_poly = union_poly.Union(geom)
        source_layer.SetSpatialFilter(union_poly)
    # Rasterize
    if attribute is not None and _has_feature(source_layer, attribute):
        # if attribute is present, use it as raster value.
        if add is True:
            if source_layer.GetGeomType() == ogr.wkbPolygon or source_layer.GetGeomType() == ogr.wkbMultiPolygon:
                # use centroid or random point on surface if centroid does not fall into shape.
                sql = "select case when ST_Intersects(ST_Centroid(geometry),geometry) " \
                      "then ST_Centroid(geometry) " \
                      "else ST_PointOnSurface(geometry) " \
                      "end as geometry, " + attribute + \
                      " from " + source_layer.GetName()
                source_layer = source_ds.ExecuteSQL(sql, dialect='sqlite')
                print("rasterize select used")
            t = time.time()
            gdal.RasterizeLayer(raster, [1], source_layer, options=["ATTRIBUTE=" + attribute, "MERGE_ALG=ADD"])
            print("rasterize add done :" + str(time.time() - t))
        else:
            gdal.RasterizeLayer(raster, [1], source_layer, options=["ATTRIBUTE=" + attribute])
            print("rasterize attribute used")
    else:
        gdal.RasterizeLayer(raster, [1], source_layer, burn_values=[1])
        print("rasterize 1 used")
    #print("rasterize done :" + str(time.time() - t))
    return raster


def extract_masked_shapefile(mask_shapefile, output_filename, input_shpfile, like_raster):
    source_ds = ogr.Open(input_shpfile)
    if source_ds:
        mask_shp = reproject_shapefile(mask_shapefile, like_raster)
        input_shp = reproject_shapefile(input_shpfile, like_raster)
        layer = mask_shp.GetLayer()
        union_poly = ogr.Geometry(ogr.wkbPolygon)
        layer.ResetReading()
        for feature in layer:
            geom = feature.GetGeometryRef()
            union_poly = union_poly.Union(geom)
        input_layer = input_shp.GetLayer()
        input_layer.SetSpatialFilter(union_poly)
        shp = None
        copy_datasource(input_layer, get_temp_folder_name() + "/" + output_filename)
        return True, get_temp_folder_name() + "/" + output_filename
    return False, None


def copy_datasource(source_layer, output_file):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    out_ds = driver.CreateDataSource(output_file)
    out_layer = out_ds.CopyLayer(source_layer, source_layer.GetName())
    del out_layer, out_ds


def _has_feature(layer, attribute):
    layerDefinition = layer.GetLayerDefn()
    for i in range(layerDefinition.GetFieldCount()):
        if layerDefinition.GetFieldDefn(i).GetName() == attribute:
            return True
    return False


def get_crs(input_file):
    source_ds = ogr.Open(input_file)
    if not source_ds:
        source_ds = gdal.Open(input_file)
        targetSR = osr.SpatialReference()
        targetSR.ImportFromWkt(source_ds.GetProjectionRef())
        crs = targetSR.GetAttrValue('AUTHORITY', 1)
        return crs
    source_layer = source_ds.GetLayer()
    sourceSR = source_layer.GetSpatialRef()
    crs = sourceSR.GetAttrValue('AUTHORITY', 1)
    #print(crs)
    return crs


def rasterize_base_map(tree, buffer_shapefile=None):
    file = tree.file
    if buffer_shapefile:
        file = buffer_shapefile
    print('base map', file)
    raster = get_raster_from_cache(file, None, None)
    if raster:
        print('cache hit ', file)
        return raster
    print('cache miss ', file)

    cell_size = tree.resolution
    source_ds = ogr.Open(tree.area_file)
    if not source_ds:
        raise RuntimeError("Could not open file: " + file)
    source_layer = source_ds.GetLayer()
    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    x_min_rounded, y_max_rounded, n_rows_rounded, n_cols_rounded = _round_extend(x_min, y_min, x_max, y_max, 1000, cell_size, tree.buffer_size)

    raster = gdal.GetDriverByName('MEM').Create("", n_cols_rounded, n_rows_rounded, 1, gdal.GDT_Float32)
    raster.SetGeoTransform((x_min_rounded, cell_size, 0, y_max_rounded, 0, -cell_size))
    band = raster.GetRasterBand(1)
    band.SetNoDataValue(np.NaN)

    raster_srs = osr.SpatialReference()
    raster_srs = source_layer.GetSpatialRef()
    raster.SetProjection(raster_srs.ExportToWkt())
    # Rasterize
    if buffer_shapefile:
        source_ds = ogr.Open(file)
        if not source_ds:
            raise RuntimeError("Could not open file: " + file)
        source_layer = source_ds.GetLayer()

    gdal.RasterizeLayer(raster, [1], source_layer, options=["ATTRIBUTE=ID_GEN"])
    del source_ds, source_layer, band
    put_raster_in_cache(file, None, None, raster)
    return raster


def _round_extend(x_min, y_min, x_max, y_max, rounding_unit, cell_size, buffer):
    buffer_size = buffer * rounding_unit
    assert rounding_unit % 1 == 0
    assert cell_size % 1 == 0
    assert x_min < x_max and y_min < y_max
    x_min_rounded = _round_down(x_min - buffer_size)
    y_min_rounded = _round_down(y_min - buffer_size)
    x_max_rounded = _round_up(x_max + buffer_size)
    y_max_rounded = _round_up(y_max + buffer_size)
    n_rows_rounded = (y_max_rounded - y_min_rounded) / cell_size
    assert (y_max_rounded - y_min_rounded) % cell_size == 0
    n_cols_rounded = (x_max_rounded - x_min_rounded) / cell_size
    assert (x_max_rounded - x_min_rounded) % cell_size == 0

    return x_min_rounded, y_max_rounded, int(n_rows_rounded), int(n_cols_rounded)


def _round_up(x):
    return int(math.ceil(x / 1000.0)) * 1000


def _round_down(x):
    return int(math.floor(x / 1000.0)) * 1000


def is_shape_file_polygons(file_name):
    source_ds = ogr.Open(file_name)
    if source_ds and (source_ds.GetLayer().GetGeomType() == ogr.wkbPolygon or source_ds.GetLayer().GetGeomType() == ogr.wkbMultiPolygon
                      or source_ds.GetLayer().GetGeomType() < 0):
        return True
    return False


def get_shape_attributes_list(file_name):
    source_ds = ogr.Open(file_name)
    if source_ds:
        result_list = []
        layer_def = source_ds.GetLayer().GetLayerDefn()
        for i in range(layer_def.GetFieldCount()):
            field_def = layer_def.GetFieldDefn(i)
            result_list.append(field_def.name)
        return result_list
    return []


def load_planning_module_data(node):
    map_string = ""
    node_data = get_node_data(node)
    parent_node = find_parent_node(node.treeWidget(), node_data.main_node_id)
    parent_node_text = parent_node.text(0)
    if parent_node_text == "Residential":
        map_string += "residential_"
    elif parent_node_text == "Services":
        map_string += "tertiary_"
    base_node_name = find_parent_node(node.treeWidget(), get_node_data(parent_node).main_node_id).text(0)

    node_text = node.text(0)
    if node_text == "Space heating high temperature":
        map_string += "heat_supply_a"
    elif node_text == "Space heating medium temperature":
        map_string += "heat_supply_b"
    elif node_text == "Space heating low temperature":
        map_string += "heat_supply_c"
    elif node_text == "Domestic hot water":
        map_string += "dhw"
    elif node_text == "Space cooling":
        map_string += "cooling"

    planner_result_dict = dict()
    tree = get_tree_by_id(node_data.tree_id)
    directory = os.path.dirname(os.path.realpath(__file__))
    #planner_file = os.path.join(directory, "saves", tree.planner_file)
    planner_file = tree.planner_file
    
    #old_format:
    #with open(planner_file, newline='') as csvfile:
    #    reader = csv.reader(csvfile, delimiter=';')
    #    for row in reader:
    #        if row and len(row) > 1:
    #            if base_node_name == "Demand":
    #                planner_result_dict[row[0]] = float(row[1].replace(',', '.'))
    #            if base_node_name == "Future Demand":
    #                planner_result_dict[row[0]] = float(row[2].replace(',', '.'))
    #        else:
    #            print("error reading planner file: " + map_string)
    
    #new_format:
    mapping_new2old_format = {}
    mapping_new2old_format["tertiary_heating_hot_extracted"] = "tertiary_heat_supply_a"
    mapping_new2old_format["tertiary_heating_medium_extracted"] = "tertiary_heat_supply_b"
    mapping_new2old_format["tertiary_heating_low_extracted"] = "tertiary_heat_supply_c"
    mapping_new2old_format["tertiary_heating_dhw_extracted"] = "tertiary_dhw"
    mapping_new2old_format["tertiary_heating_cooling_extracted"] = "tertiary_cooling"
    mapping_new2old_format["residential_heating_hot_extracted"] = "residential_heat_supply_a"
    mapping_new2old_format["residential_heating_medium_extracted"] = "residential_heat_supply_b"
    mapping_new2old_format["residential_heating_low_extracted"] = "residential_heat_supply_c"
    mapping_new2old_format["residential_heating_dhw_extracted"] = "residential_dhw"
    mapping_new2old_format["residential_heating_cooling_extracted"] = "residential_cooling"

    # need to be initialized at zero
    for k in mapping_new2old_format.values():
        planner_result_dict[k] = 0

    with open(planner_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row and len(row) > 1:
                description, value = row[0], float(row[1])
                unit, timestep = description.split("_")[-3:-1]
                for key in mapping_new2old_format.keys():
                    if description.startswith(key):
                        planner_result_dict[mapping_new2old_format[key]] = value
    return planner_result_dict[map_string]


def buffer(input_shpfile, buffer_size):
    folder_name = get_temp_folder_name()
    input_shpfile.split()
    if not os.path.exists(folder_name + "/temp"):
        os.mkdir(folder_name + "/temp")
    file_name = folder_name + "/temp/buffer_" + str(round(time.time() * 1000)) + "_" + str(buffer_size) + ".shp"
    file = ogr.Open(file_name)
    if file:
        return file_name, file.GetLayer().GetExtent()
    shp = ogr.Open(input_shpfile)
    drv = shp.GetDriver()
    buffer_shp = drv.CopyDataSource(shp, file_name)
    shp.Destroy()
    lyr = buffer_shp.GetLayer(0)
    if lyr.FindFieldIndex('ID_GEN', 0) == -1:
        print("add id field")
        new_field = ogr.FieldDefn("ID_GEN", ogr.OFTInteger)
        lyr.CreateField(new_field)
    for i in range(0, lyr.GetFeatureCount()):
        feat = lyr.GetFeature(i)
        lyr.DeleteFeature(i)
        geom = feat.GetGeometryRef()
        feat.SetGeometry(geom.Buffer(buffer_size))
        feat.SetField("ID_GEN", i+1)
        lyr.CreateFeature(feat)
    file = buffer_shp.GetName()
    extent = lyr.GetExtent()
    buffer_shp.Destroy()
    return file, extent


def calculate_shape_area_and_rasterize(node, input_shape, like_raster, buffer=None):
    tree = get_tree_by_id(get_node_data(node).tree_id)
    tree_ds = ogr.Open(tree.file)
    if buffer:
        tree_ds = ogr.Open(buffer)
    folder_name = get_temp_folder_name()

    input_ds = ogr.Open(input_shape)
    if not os.path.exists(folder_name + "/temp"):
        os.mkdir(folder_name + "/temp")
    output_file = folder_name + "/temp/projection" + str(round(time.time() * 1000)) + ".shp"
    helper_file = folder_name + "/temp/projection_helper" + str(round(time.time() * 1000)) + ".shp"
    subselect_file = folder_name + "/temp/projection_subselect" + str(round(time.time() * 1000)) + ".shp"

    file = tree.file
    if buffer:
        file = buffer

    reproject_shape_file(file, helper_file, input_ds.GetLayer().GetSpatialRef())

    get_subset(input_shape, subselect_file, helper_file)

    reproject_shape_file(subselect_file, output_file, tree_ds.GetLayer().GetSpatialRef())
    remove_files_with_name_like(subselect_file)
    remove_files_with_name_like(helper_file)
    x_min, x_max, y_min, y_max = tree_ds.GetLayer().GetExtent()
    reprojected_ds = ogr.Open(output_file, 1)
    layer = reprojected_ds.GetLayer()

    if tree_ds:
        tree_lyr = tree_ds.GetLayer()
        union_poly = ogr.Geometry(ogr.wkbPolygon)
        tree_lyr.ResetReading()
        for feature in tree_lyr:
            geom = feature.GetGeometryRef()
            union_poly = union_poly.Union(geom)
        layer.SetSpatialFilter(union_poly)
    t = time.time()
    if layer.FindFieldIndex('AREA_GEN', 0) == -1:
        print("add area field")
        new_field = ogr.FieldDefn("AREA_GEN", ogr.OFTReal)
        layer.CreateField(new_field)

    if layer.FindFieldIndex('ID_GEN', 0) == -1:
        print("add id field")
        new_field = ogr.FieldDefn("ID_GEN", ogr.OFTInteger)
        layer.CreateField(new_field)

    number = 1
    for feature in layer:
        geom = feature.GetGeometryRef()
        area = geom.GetArea()
        feature.SetField("AREA_GEN", area)
        feature.SetField("ID_GEN", number)
        layer.SetFeature(feature)
        number += 1
    reprojected_ds = layer = None
    print("area field creation done :" + str(time.time() - t))

    reprojected_ds = ogr.Open(output_file)

    return rasterize_shape_dataset(reprojected_ds, like_raster, attribute="AREA_GEN", add=True), output_file


def remove_files_with_name_like(name):
    for filename in glob.glob(name[:-4] + '.*'):
        os.remove(filename)


def copy_and_add_id_column(input_shape, output_shape):
    output_ds = ogr.GetDriverByName("ESRI Shapefile").CopyDataSource(ogr.Open(input_shape), output_shape)
    layer = output_ds.GetLayer()
    if layer.FindFieldIndex('ID_GEN', 0) == -1:
        number = 1
        new_field = ogr.FieldDefn("ID_GEN", ogr.OFTInteger)
        layer.CreateField(new_field)
        for feature in layer:
            feature.SetField("ID_GEN", number)
            layer.SetFeature(feature)
            number += 1

    reprojected_ds = None

    reprojected_ds = ogr.Open(output_shape)


# returns an intersection of the extent of the mask and the input file.
def get_subset(input_shape, output_shape, mask_shape):
    t = time.time()
    mask_ds = ogr.Open(mask_shape)
    x_min, x_max, y_min, y_max = mask_ds.GetLayer().GetExtent()
    mask_ds = None
    input_ds = ogr.Open(input_shape)
    in_layer = input_ds.GetLayer()
    in_layer.SetSpatialFilterRect(x_min, y_min, x_max, y_max)

    driver = ogr.GetDriverByName("ESRI Shapefile")
    # create the output layer
    output_shapefile = output_shape
    if os.path.exists(output_shapefile):
        driver.DeleteDataSource(output_shapefile)
    out_data_set = driver.CreateDataSource(output_shapefile)
    out_layer = out_data_set.CreateLayer("basemap", in_layer.GetSpatialRef(), geom_type=ogr.wkbMultiPolygon)

    in_layer_defn = in_layer.GetLayerDefn()
    for i in range(0, in_layer_defn.GetFieldCount()):
        field_defn = in_layer_defn.GetFieldDefn(i)
        out_layer.CreateField(field_defn)

    # loop through the input features
    in_feature = in_layer.GetNextFeature()
    while in_feature:
        out_layer.CreateFeature(in_feature)
        in_feature = in_layer.GetNextFeature()

    out_data_set = None
    print("get_subset done :" + str(time.time() - t))


# reproject the input file into the output file with the target projection
def reproject_shape_file(input_filename, output_filename, target_projection):
    t = time.time()
    # get the input layer
    driver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSet = ogr.Open(input_filename)
    inLayer = inDataSet.GetLayer()

    feature = inLayer.GetNextFeature()
    in_geom = feature.GetGeometryRef().GetGeometryType()
    inLayer.ResetReading()

    # create the output layer
    outputShapefile = output_filename
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer("basemap", target_projection, geom_type=in_geom)

    # create the CoordinateTransformation
    in_srs = osr.SpatialReference()
    in_srs = inLayer.GetSpatialRef()
    out_srs = osr.SpatialReference()
    out_srs = target_projection

    coordTrans = osr.CoordinateTransformation(in_srs, out_srs)

    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()
    print(outLayerDefn)
    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        if geom: #skip if geom is none
        # reproject the geometry
            geom.Transform(coordTrans)
            # create a new feature
            outFeature = ogr.Feature(outLayerDefn)
            # set the geometry and attribute
            outFeature.SetGeometry(geom)
            for i in range(0, outLayerDefn.GetFieldCount()):
                outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
            # add the feature to the shapefile
            outLayer.CreateFeature(outFeature)
            # dereference the features and get the next input feature
            outFeature = None
        inFeature = inLayer.GetNextFeature()

    # Save and close the shapefiles
    inDataSet = None
    outDataSet = None
    print("reproject done :" + str(time.time() - t))


def raster_to_shapefile(input_raster_file, output_shp_file):
    print("polygonize")
    src_ds = gdal.Open(input_raster_file)
    srcband = src_ds.GetRasterBand(1)

    dst_layername = "RASTER_VALUES"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(output_shp_file)

    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(src_ds.GetProjectionRef())

    dst_layer = dst_ds.CreateLayer(dst_layername, srs=raster_srs)
    val_field = ogr.FieldDefn('VALUE', ogr.OFTReal)
    dst_layer.CreateField(val_field)

    gdal.FPolygonize(srcband, None, dst_layer, 0, ["8CONNECTED=8"], callback=None)
    dst_ds = None

    shp_file = ogr.Open(output_shp_file, update=1)
    lyr = shp_file.GetLayerByIndex(0)
    lyr.ResetReading()
    # transform value to total area value.
    for feature in lyr:
        if np.isnan(feature.GetFieldAsDouble('VALUE')) or feature.GetFieldAsDouble('VALUE') == 0:
            lyr.DeleteFeature(feature.GetFID())
        else:
            geom = feature.GetGeometryRef()
            area = geom.GetArea()
            factor = area / 2500
            feature.SetField("VALUE", float(feature.GetField('VALUE')) * factor)
            lyr.SetFeature(feature)

    shp_file = None
