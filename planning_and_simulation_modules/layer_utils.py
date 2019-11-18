import time

import numpy as np
from PyQt5.QtCore import QTimer, QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from osgeo import gdal, ogr
from qgis.core import QgsProject, QgsRasterLayer, QgsSingleBandPseudoColorRenderer, QgsFillSymbol, QgsVectorLayer, QgsVectorFileWriter, QgsColorRampShader, \
    QgsRasterShader, QgsField, QgsMapLayer, QgsRasterBandStats, QgsPointXY
from qgis.utils import iface
import processing
import os.path


def load_file_from_dialog_as_layer(dialog):
    file_name = dialog.fileNameText.text()
    if not file_name or file_name == "None":
        QMessageBox.information(None, "Error", "No file specified.")
    else:
        layer_name = dialog.descriptionText.text()
        load_file_as_layer(file_name, layer_name)


def load_file_as_layer(file_name, layer_name, group_name=None, min_val=None, max_val=None, mean_val=None, value_color=None, area=None):
    """
    :param file_name: string, full path to the layer to be loaded
    :param layer_name: string, layer name to be displayed
    :param group_name: string, group name of the group the layer should be added to
    :param min_val: float, if None will be evaluated (for raster files)
    :param max_val: float, if None will be evaluated (for raster files)
    :param mean_val: float, if None will be evaluated (for raster files). If at least one variable among mean, max and
                    min is not present, create_legend() will do nothing.
    :param value_color: QColor, e.g. q = QColor('#FFFF7F50'). If None, create_legend() will define a 3 range interval
                        colormap
    :param area: float, the area of the pixel:
                QgsRasterLayer.rasterUnitsPerPixelX()*QgsRasterLayer.rasterUnitsPerPixelY(). If None will be evaluated
    :return: QgsRasterLayer or QgsVectorLayer, depends on the input file defined by file_name
    """
    layers = QgsProject.instance().mapLayersByName("OSM")
    if len(layers) > 0:
        iface.setActiveLayer(layers[0])
    shape_file = False
    if file_name[-3:] == "shp":
        shape_file = True
    else:
        layer = QgsRasterLayer(file_name, layer_name)
    type = None
    if not shape_file and layer.isValid():
        type = "r"
        # get QgsRasterDataProvider to access raster data
        provider = layer.dataProvider()
        # QgsRasterBandStats contains generic info on the cells values
        stats = provider.bandStatistics(1, QgsRasterBandStats.All, provider.extent(), 0)
        if not min_val:
            min_val = stats.minimumValue
        if not max_val:
            max_val = stats.maximumValue
        if not mean_val:
            mean_val = stats.mean
        # getting the dimension of the raster pixel
        if not area:
            xsize = layer.rasterUnitsPerPixelX()
            ysize = layer.rasterUnitsPerPixelY()
            area = abs(float(xsize*ysize))
        # generate legend with min/max values
        create_legend(layer, max_val, min_val, mean_val, value_color, area)
    else:
        layer = QgsVectorLayer(file_name, layer_name)
        # add_id_attribute_to_layer(layer)
        if layer.isValid():
            type = "s"
            renderer = layer.renderer()
            if renderer and layer.geometryType() == 2:  # make fill of shapes invisible
                my_symbol = QgsFillSymbol.createSimple({'color': '#00ff00ff'})
                renderer.setSymbol(my_symbol)
                layer.triggerRepaint()
        else:
            # QMessageBox.information(None, "Error", "file " + file_name + " could not be loaded")
            validity = False
    if group_name is None:
        QgsProject.instance().addMapLayer(layer)
    else:
        QgsProject.instance().addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(group_name)
        if group is None:
            group = root.insertGroup(0, group_name)
        group.addLayer(layer)
    return layer


def add_layer_to_group(layer, group_name, add_to_layer_list=True):
    if layer is None:
        print("layer_utils.add_layer_to_group(layer, group_name, add_to_layer_list=True): Import failed: layer is None")
        return
    try:
        if not layer.isValid():
            print("layer_utils.add_layer_to_group(layer, group_name, add_to_layer_list=True): Import failed: layer invalid")
            return
    except:
        print("layer_utils.add_layer_to_group(layer, group_name, add_to_layer_list=True): Import failed", type(layer), layer)
        return

    if add_to_layer_list:
        QgsProject.instance().addMapLayer(layer, False)

    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(group_name)
    if group is None:
        group = root.insertGroup(0, group_name)
    group.addLayer(layer)


def get_only_new_features(new_layer, old_layer, attr):
    f = []
    for f_add in new_layer.selectedFeatures():
        found = False
        for f_curr in old_layer.getFeatures():
            if f_curr.attribute(attr) == "" or f_curr.attribute(attr) is None:
                pass
            else:
                if f_add.attribute(attr) == f_curr.attribute(attr):
                    found = True
                    break
        if not found:
            f.append(f_add)
    return f


def create_legend(layer, max_val, min_val, mean_val, value_color=None, area=None):
    if max_val is not None and min_val is not None and mean_val is not None:
        shader = QgsRasterShader()
        color_ramp = QgsColorRampShader()
        color_ramp.setColorRampType("INTERPOLATED")
        items = []
        item = QgsColorRampShader.ColorRampItem(0, QColor('#000005ae'), '0')
        items.append(item)
        area_lbl = ''
        if area:
            area_lbl = '/' + str(int(round(area, 0))) + "m²"
        if value_color:
            item = QgsColorRampShader.ColorRampItem(mean_val, value_color, str(mean_val) + " MWh/year" + area_lbl)
            items.append(item)
        else:
            if min_val == 0:
                min_val_text = "> 0"
            else:
                min_val_text = str(min_val)
            item = QgsColorRampShader.ColorRampItem(min_val + 0.00001, QColor('#0005ae'), min_val_text + " MWh/year" + area_lbl)
            items.append(item)
            item = QgsColorRampShader.ColorRampItem(min_val + round((max_val - min_val) / 2, 0), QColor('#fda000'),
                                                    str(min_val + round((max_val - min_val) / 2, 0)) + " MWh/year" + area_lbl)
            items.append(item)
            item = QgsColorRampShader.ColorRampItem(max_val, QColor('#ff0000'), str(max_val) + " MWh/year" + area_lbl)
            items.append(item)
        color_ramp.setColorRampItemList(items)
        shader.setRasterShaderFunction(color_ramp)
        ps = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
        layer.setRenderer(ps)


def add_id_attribute_to_layer(layer):
    if layer.fields().indexFromName('ID_GEN') == -1:

        number = 1
        layer.startEditing()
        layer.addAttribute(QgsField('ID_GEN', QVariant.Int))
        layer.commitChanges()
        layer.updateFields()
        idx = layer.fields().indexFromName('ID_GEN')
        layer.startEditing()

        for feature in layer.getFeatures():
            feature.setAttribute(idx, number)
            layer.updateFeature(feature)
            number += 1
            if number % 1000 == 0:
                print("x")
        layer.commitChanges()
    if layer.fields().indexFromName('ID_GEN') == -1:
        print("failed")


def load_mem_as_layer(layer, layer_name, group_name=None, min_val=None, max_val=None):
    if layer.type() == QgsMapLayer.LayerType.RasterLayer:
        create_legend(layer, max_val, min_val)
    else:
        renderer = layer.renderer()
        if renderer and layer.geometryType() == 2:  # make fill of shapes invisible
            symbol = QgsFillSymbol.createSimple({'color': '#00ff00ff'})
            renderer.setSymbol(symbol)
            layer.triggerRepaint()

    if group_name is None:
        QgsProject.instance().addMapLayer(layer)
    else:
        QgsProject.instance().addMapLayer(layer, False)
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(group_name)
        if group is None:
            group = root.insertGroup(0, group_name)
        group.addLayer(layer)
    return layer


def read_table_data(file_path, id_column, column_name):
    shape_data_set = gdal.OpenEx(file_path, gdal.OF_READONLY | gdal.OF_VECTOR)
    if shape_data_set is None:
        raise RuntimeError('Failed to open weights data: {} ({})'.format(file_path, gdal.GetLastErrorMsg()))

    layer = shape_data_set.GetLayer(0)
    layer_def = layer.GetLayerDefn()

    id_field = layer_def.GetFieldIndex(id_column)
    if id_field is None:
        raise RuntimeError('No {} column in data file: {}'.format(id_column, file_path))

    value_field = layer_def.GetFieldIndex(column_name)
    if value_field is None:
        raise RuntimeError('No {} column in data file: {}'.format(column_name, file_path))

    values = {}
    layer.ResetReading()
    feature = layer.GetNextFeature()
    while feature is not None:
        id = feature.GetFieldAsInteger(id_field)
        value = feature.GetFieldAsDouble(value_field)
        values[id] = value
        feature = layer.GetNextFeature()

    max_id = max(values.keys(), key=int)

    weights = np.zeros(max_id + 1)
    for id, value in values.items():
        weights[id] = value

    return weights


def load_open_street_maps():
    print("Downloading OSM map ...")
    if not QgsProject.instance().mapLayersByName("OSM"):
        canvas = iface.mapCanvas()
        canvas.setSelectionColor(QColor(255, 255, 0, 80))
        canvas.zoomToFullExtent()
        QTimer.singleShot(10, load_osm)
    else:
        layer = iface.activeLayer()
        if layer is not None:
            try:
                layer.selectAll()
                iface.mapCanvas().zoomToSelected()
                layer.removeSelection()
            except:
                pass
    print("End downloading OSM map")

def load_osm():
    lyr = QgsRasterLayer("type=xyz&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png", "OSM", "wms")
    QgsProject.instance().addMapLayer(lyr, False)
    QgsProject.instance().layerTreeRoot().insertLayer(-1, lyr)

def get_selection():
    layer = iface.activeLayer()
    if isinstance(layer, QgsVectorLayer):
        selected_features = layer.selectedFeatures()
        if selected_features:
            file_name = "C:/TEMP/" + layer.name() + str(round(time.time() * 1000)) + "-selection.shp"
            QgsVectorFileWriter.writeAsVectorFormat(layer, file_name, "utf-8", layer.crs(), "ESRI Shapefile", 1)
        else:
            file_name = "C:/TEMP/" + layer.name() + str(round(time.time() * 1000)) + "-selection.shp"
            QgsVectorFileWriter.writeAsVectorFormat(layer, file_name, "utf-8", layer.crs(), "ESRI Shapefile")
        result = ogr.Open(file_name)
        return result, file_name

    return None, None

def move_active_vector_layer_to_top():
    layer = iface.activeLayer()
    if isinstance(layer, QgsVectorLayer):
        root = QgsProject.instance().layerTreeRoot()
        my_layer = root.findLayer(layer)
        clone = my_layer.clone()
        parent = my_layer.parent()
        parent.insertChildNode(0, clone)
        parent.removeChildNode(my_layer)


def raster_shapefile_intersection_integral(vector_layer, raster_layer, points):
    if vector_layer is None:
        print("raster_shapefile_intersection_integral: vector_layer is None")
        return [{0: 0, 1: 0, 2: 0}, None]
    elif not vector_layer.isValid():
        print("raster_shapefile_intersection_integral: vector_layer is not a valid layer")
        return [{0: 0, 1: 0, 2: 0}, None]
    if vector_layer is None:
        print("raster_shapefile_intersection_integral: raster_layer is None")
        return [{0: 0, 1: 0, 2: 0}, None]
    elif not vector_layer.isValid():
        print("raster_shapefile_intersection_integral: raster_layer is not a valid layer")
        return [{0: 0, 1: 0, 2: 0}, None]
    if isinstance(raster_layer, QgsVectorLayer):
        print("raster_shapefile_intersection_integral: raster_layer is a QgsVectorLayer...")
        return [{0: 0, 1: 0, 2: 0}, None]


    if not vector_layer.geometryType() == 2:
        print("raster_shapefile_intersection_integral: vector_layer.geometryType() it's not polygons:",
              vector_layer.geometryType())
        return [{0: 0, 1: 0, 2: 0}, None]
    if not vector_layer.crs().authid() == raster_layer.crs().authid():
        parameter = {'INPUT': vector_layer, 'TARGET_CRS': raster_layer.crs().authid(),
                     'OUTPUT': 'memory:'}
        p = processing.run('qgis:reprojectlayer', parameter)
        vector_layer = p['OUTPUT']
    output = {}
    provider = raster_layer.dataProvider()
    x_min = provider.extent().xMinimum()
    y_min = provider.extent().yMinimum()
    dx = raster_layer.rasterUnitsPerPixelX()
    dy = raster_layer.rasterUnitsPerPixelY()
    new_points = []
    block = provider.block(1, provider.extent(), provider.xSize(), provider.ySize())
    for band in range(raster_layer.bandCount()):
        output[band] = 0.0
        for feature in vector_layer.getFeatures():
            if points is None:
                for x in range(provider.xSize()):
                    for y in range(provider.ySize()):
                        pixel = QgsPointXY(x_min+x*dx, y_min+y*dy)
                        if feature.geometry().contains(pixel):
                            new_points.append([x, y])
                            increment = block.value(x, y)
                            if not np.isnan(increment):
                                output[band] = output[band] + increment
            else:
                for point in points:
                    increment = block.value(point[0], point[1])
                    if not np.isnan(increment):
                        output[band] = output[band] + increment
        if points is None:
            points = new_points
    return [output, points]

def save_layer_to_shapefile(layer, file_path):

    if not os.path.isdir(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    try:
        QgsVectorFileWriter.writeAsVectorFormat(layer, file_path, "utf-8", layer.crs(), "ESRI Shapefile")

        return file_path
    except:
        print("layer_utils.py, save_layer_to_shapefile: failed to save layer. layer, file_path:", layer, file_path)
        return None


def read_layer_attribute_by_id(layer, feature_id, attribute):
    try:
        return layer.getFeature(int(feature_id)).attribute(attribute)
    except:
        return None





