import time

import numpy as np
from PyQt5.QtCore import QTimer, QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox
from osgeo import gdal, ogr
from qgis.core import QgsProject, QgsRasterLayer, QgsSingleBandPseudoColorRenderer, QgsFillSymbol, QgsVectorLayer, QgsVectorFileWriter, QgsColorRampShader, \
    QgsRasterShader, QgsField, QgsMapLayer, QgsGraduatedSymbolRenderer, QgsSymbol, QgsRendererRange
from qgis.utils import iface


def load_file_as_layer(file_name, layer_name, group_name=None, min_val=None, max_val=None, mean_val=None, value_color=None, area=None, attribute=None):
    layer = QgsRasterLayer(file_name, layer_name)
    if layer.isValid():
        # generate legend with min/max values
        create_legend(layer, max_val, min_val, mean_val, value_color, area)
    else:
        layer = QgsVectorLayer(file_name, layer_name)
        # add_id_attribute_to_layer(layer)
        if layer.isValid():
            renderer = layer.renderer()
            print(layer.geometryType())
            if renderer and layer.geometryType() == 2:  # make fill of shapes invisible
                mySymbol1 = QgsFillSymbol.createSimple({'color': '#00ff00ff'})
                renderer.setSymbol(mySymbol1)
                layer.triggerRepaint()
            elif renderer and layer.geometryType() == 0 and min_val and max_val:
                print(layer.geometryType())
                ranges = []
                center = round((max_val - min_val) / 2, 0)
                range_1 = round((center - min_val) / 2, 0)
                range_2 = round(((max_val - center) / 2) + center, 0)
                print(min_val, range_1, center, range_2, max_val)

                symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                symbol.setColor(QColor("#0005ae"))
                myRange = QgsRendererRange(min_val - 0.001, range_1, symbol, str(round(min_val,2)) + " - " + str(range_1) + " (MWh/point)")
                ranges.append(myRange)

                symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                symbol.setColor(QColor("#fda000"))
                myRange = QgsRendererRange(range_1, range_2, symbol, str(range_1) + " - " + str(range_2) + " (MWh/point)")
                ranges.append(myRange)

                symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                symbol.setColor(QColor("#ff0000"))
                myRange = QgsRendererRange(range_2, max_val + 0.001, symbol, str(range_2) + " - " + str(round(max_val,2)) + " (MWh/point)")
                ranges.append(myRange)

                expression = attribute  # field name
                renderer = QgsGraduatedSymbolRenderer(expression, ranges)
                layer.setRenderer(renderer)
        else:
            QMessageBox.information(None, "Error", "file " + file_name + " could not be loaded")

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
            item = QgsColorRampShader.ColorRampItem(mean_val, value_color, str(round(mean_val,2)) + " MWh/year" + area_lbl)
            items.append(item)
        elif not np.isnan(min_val):
            if min_val == 0:
                min_val_text = "> 0"
            else:
                min_val_text = str(round(min_val,2))
            item = QgsColorRampShader.ColorRampItem(min_val + 0.00001, QColor('#0005ae'), min_val_text + " MWh/year" + area_lbl)
            items.append(item)
            item = QgsColorRampShader.ColorRampItem(min_val + 0.00001 + round((max_val - min_val) / 2, 2), QColor('#fda000'),
                                                    str(round(min_val + ((max_val - min_val) / 2), 2)) + " MWh/year" + area_lbl)
            items.append(item)
            item = QgsColorRampShader.ColorRampItem(max_val, QColor('#ff0000'), str(round(max_val,2)) + " MWh/year" + area_lbl)
            items.append(item)
        color_ramp.setColorRampItemList(items)
        shader.setRasterShaderFunction(color_ramp)
        ps = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
        layer.setRenderer(ps)


def add_id_attribute_to_layer(layer):
    if layer.fields().indexFromName('ID_GEN') == -1:
        print("add id field")
        number = 1
        layer.startEditing()
        layer.addAttribute(QgsField('ID_GEN', QVariant.Int))
        layer.commitChanges()
        layer.updateFields()
        idx = layer.fields().indexFromName('ID_GEN')
        layer.startEditing()
        print(layer.fields().indexFromName('ID_GEN'))
        for feature in layer.getFeatures():
            print(number)
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
    if not QgsProject.instance().mapLayersByName("OSM"):
        canvas = iface.mapCanvas()
        canvas.setSelectionColor(QColor(255, 255, 0, 80))
        canvas.zoomToFullExtent()
        QTimer.singleShot(10, load_osm)
    else:
        layer = iface.activeLayer()
        layer.selectAll()
        iface.mapCanvas().zoomToSelected()
        layer.removeSelection()


def load_osm():
    lyr = QgsRasterLayer("type=xyz&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png", "OSM", "wms")
    QgsProject.instance().addMapLayer(lyr, False)
    QgsProject.instance().layerTreeRoot().insertLayer(-1, lyr)


def get_selection():

    layer = iface.activeLayer()
    if isinstance(layer, QgsVectorLayer):
        selected_features = layer.selectedFeatures()
        if selected_features:
            file_name, newlayer = copy_layer(layer)
            error = QgsVectorFileWriter.writeAsVectorFormat(newlayer, file_name, "utf-8", layer.crs(), "ESRI Shapefile", 1)
            print(error)
        else:
            file_name, newlayer = copy_layer(layer)
            error = QgsVectorFileWriter.writeAsVectorFormat(newlayer, file_name, "utf-8", layer.crs(), "ESRI Shapefile")
            print(error)
        layer = newlayer = None
        result = ogr.Open(file_name)
        return result, file_name

    return None, None


def copy_layer(layer):
    from .io_utils import get_temp_folder_name
    file_name = get_temp_folder_name() + r"/" + "layer.shp"
    feats = [feat for feat in layer.getFeatures()]
    newlayer = QgsVectorLayer(layer.source(), layer.name(), layer.providerType())
    mem_layer_data = newlayer.dataProvider()
    attr = layer.dataProvider().fields().toList()
    mem_layer_data.addAttributes(attr)
    newlayer.updateFields()
    mem_layer_data.addFeatures(feats)
    add_id_attribute_to_layer(newlayer)
    return file_name, newlayer


def move_active_vector_layer_to_top():
    layer = iface.activeLayer()
    if isinstance(layer, QgsVectorLayer):
        root = QgsProject.instance().layerTreeRoot()
        my_layer = root.findLayer(layer)
        clone = my_layer.clone()
        parent = my_layer.parent()
        parent.insertChildNode(0, clone)
        parent.removeChildNode(my_layer)
        layer = QgsProject.instance().mapLayersByName(layer.name())[0]
        iface.setActiveLayer(layer)