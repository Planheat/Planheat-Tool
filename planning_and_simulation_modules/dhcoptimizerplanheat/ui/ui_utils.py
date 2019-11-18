# -*- coding: utf-8 -*-
from qgis.core import QgsProject, QgsField
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QVariant


def node_has_child_name(node, child_name):
    for c in node.children():
        if child_name == c.name():
            return True
    return False


def add_group(group_name, parent_group=None):
    root = QgsProject.instance().layerTreeRoot()
    if parent_group is not None:
        node = root.findGroup(parent_group)
        if node is None:
            raise ValueError("Unable to find parent group named: '%s'" % str(parent_group))
    else:
        node = root
    if not node_has_child_name(node, group_name):
        node.addGroup(group_name)


def add_layer_to_group(layer, group_name, add_to_layer_list=True):
    if layer is None:
        return
    if add_to_layer_list:
        QgsProject.instance().addMapLayer(layer, False)
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(group_name)
    if group is None:
        group = root.insertGroup(0, group_name)
    group.addLayer(layer)

def hide_group(group_name):
    root = QgsProject.instance().layerTreeRoot()
    group = root.findGroup(group_name)
    group.setItemVisibilityChecked(False)
    group.setExpanded(False)

def hide_layers(layers_prefix_to_hide: list):
    layers = QgsProject.instance().mapLayers()
    for layer in layers:
        for layer_prefix in layers_prefix_to_hide:
            if layer_prefix in layer:
                ltl = QgsProject.instance().layerTreeRoot().findLayer(layers[layer].id())
                ltl.setItemVisibilityChecked(False)


def remove_layers(layers_prefix_to_remove: list):
    layers = QgsProject.instance().mapLayers()
    for layer in layers:
        for layer_prefix in layers_prefix_to_remove:
            if layer_prefix in layer:
                QgsProject.instance().removeMapLayer(layers[layer])


def has_layer(layer_prefix_to_find: list):
    layers = QgsProject.instance().mapLayers()
    for layer in layers:
        if layer_prefix_to_find in layer:
            return True
    return False


def browse_and_set_file_path(lineEdit, **kwargs):
    file_path = QFileDialog.getOpenFileName(**kwargs)
    lineEdit.clear()
    if isinstance(file_path, tuple):
        file_path = file_path[0]
    lineEdit.insert(file_path)


def browse_and_set_directory_path(lineEdit):
    file_path = QFileDialog.getExistingDirectory()
    lineEdit.clear()
    if isinstance(file_path, tuple):
        file_path = file_path[0]
    lineEdit.insert(file_path)


def set_marked_field(layer, AttributeName, value):
    if AttributeName not in layer.fields().names():
        print(AttributeName + ' not in the attributes at the beginning')
        layer.startEditing()
        layer.addAttribute(QgsField(AttributeName, QVariant.Int))
        layer.commitChanges()
    print('Initialized ' + AttributeName + ': ', AttributeName in layer.fields().names())
    # Set all AttributeName attributes to value :
    layer.startEditing()
    index = layer.fields().indexFromName(AttributeName)
    for f in layer.getFeatures():
        layer.changeAttributeValue(f.id(), index, value)
    layer.commitChanges()

def refresh_layers(iface):
    for layer in iface.mapCanvas().layers():
        layer.triggerRepaint()