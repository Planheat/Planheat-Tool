import uuid

import os
import os.path
import json

from qgis.core import QgsPointXY, QgsGeometry, QgsProject, QgsFeature, QgsVectorLayer
from qgis.core import *

from .layer_utils import add_layer_to_group, save_layer_to_shapefile
from .utility.easy_progress_bar import Actions

import processing
import copy
import traceback

from shapely.geometry import LineString

from PyQt5.QtCore import pyqtSignal, QObject, QVariant
from PyQt5.QtWidgets import QMessageBox

from .dhcoptimizerplanheat.optimizer import config


class Network(QObject):

    list_to_select_ready = pyqtSignal(str, str, list)

    def __init__(self, name="default", n_type="DHN", orig=None, parent=None):
        super(Network, self).__init__(parent)
        self.ID = uuid.uuid4()  # i need an identifier
        self.default_crs = 'EPSG:4326'
        self.sqrPrecision = 0.02
        self.save_file_path = None
        self.H_dem_attributes = ["MaxHeatDem"]
        self.C_dem_attributes = ["MaxCoolDem"]
        self.optimizer_results = {}

        if orig is None:
            self.optimizer_results = {}
            self.optimized = False
            self.efficiency = 1.0
            self.name = name
            self.n_type = n_type
            self.buildings_layer = None
            self.streets_layer = None
            self.streets_layer_backup = []
            self.optimized_buildings_layer = None
            self.optimized_streets_layer = None
            self.street_quality_status = False
            self.scenario_type = "baseline"
            self.supply_layer = self.create_supply_layer()
        else:
            self.optimized = orig.optimized
            self.efficiency = orig.efficiency
            self.scenario_type = orig.scenario_type
            self.name = orig.name
            self.n_type = orig.n_type
            if orig.buildings_layer is not None:
                self.buildings_layer = self.clone_layer(orig.buildings_layer)
                # QgsVectorLayer(orig.buildings_layer.source(), orig.buildings_layer.name(), orig.buildings_layer.providerType())
            else:
                self.buildings_layer = None
            if orig.streets_layer is not None:
                self.streets_layer = self.clone_layer(orig.streets_layer)
            else:
                self.streets_layer = None
            if orig.supply_layer is not None:
                self.supply_layer = self.clone_layer(orig.supply_layer)
            else:
                self.supply_layer = None
            if orig.optimized_buildings_layer is not None:
                self.optimized_buildings_layer = self.clone_layer(orig.optimized_buildings_layer)
            else:
                self.optimized_buildings_layer = None
            if orig.optimized_streets_layer is not None:
                self.optimized_streets_layer = self.clone_layer(orig.optimized_streets_layer)
            else:
                self.optimized_streets_layer = None
            self.streets_layer_backup = [QgsFeature(f) for f in orig.streets_layer_backup]
            self.street_quality_status = orig.street_quality_status
            for key in orig.optimizer_results.keys():
                self.optimizer_results[key] = copy.deepcopy(orig.optimizer_results[key])

    def get_network_default_saved_file(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "save_utility", "DefaultSaveFolder",
                            self.scenario_type, "Networks", self.n_type, str(self.ID), "network_data.zip")

    def create_supply_layer(self):
        return
        group_name = self.get_group_name()
        generate = self.name
        crs = self.default_crs
        supply_layer = QgsVectorLayer("Point?crs=" + crs, "generation_point" + " - " + generate, "memory")
        # Show the layer
        add_layer_to_group(supply_layer, group_name)
        # Add fields :
        supply_layer.startEditing()
        supply_layer.dataProvider().addAttributes([QgsField("name", QVariant.String), QgsField("capacity_MW",
                                                                                                QVariant.Double)])
        supply_layer.updateFields()
        supply_layer.commitChanges()
        return supply_layer


    @staticmethod
    def clone_layer(layer):
        layer_copy = QgsVectorLayer(layer.source().split("&")[0], layer.name(), layer.providerType())
        new_features = [QgsFeature(f) for f in layer.getFeatures()]
        layer_copy.startEditing()
        layer_copy.dataProvider().addAttributes([f for f in layer.fields()])
        layer_copy.updateFields()
        layer_copy.dataProvider().addFeatures(new_features)
        layer_copy.commitChanges()
        return layer_copy

    def get_building_list(self):
        if self.buildings_layer is not None:
            return [str(f.attribute("BuildingID")) for f in self.buildings_layer.getFeatures()]
        return []

    def get_street_list(self):
        if self.streets_layer is not None:
            return ["Pipe ID: " + str(f.attribute("ID")) + "\t| Diameter: " + str(f.attribute("diameter")) for f in self.streets_layer.getFeatures()]
        return []

    def get_ID(self):
        return str(self.ID)

    def validate_sources(self, fid):
        # Get all supply sources in the layer and add it to the supply table
        f = self.supply_layer.getFeature(fid)
        if f is None or "name" not in f.fields().names() or f["name"] is None or str(f["name"]) == "" or f[
            "capacity_MW"] is None or f["capacity_MW"] <= 0.0:
            if f is not None:
                self.supply_layer.deleteFeature(f.id())
            self.iface.messageBar().pushMessage("Error",
                                                "Invalid name or production capacity for the selected point.", level=1)
        else:
            pass
            # self.nb_supply += 1
            # self.update_table_from_layer()
            # self.update_supply_labels()
        return True

    @staticmethod
    def get_length(feature):
        return feature.geometry().length()

    def select_in_widget(self, selected, deselected, clearAndSelect):
        feature_to_select = []
        for feature in self.streets_layer.getSelectedFeatures():
            feature_to_select.append(feature.attribute("ID"))
        self.list_to_select_ready.emit(self.n_type, self.get_ID(), feature_to_select)

    @staticmethod
    def get_MultiPolyLine_from_feature(feature):
        try:
            line = feature.geometry().asMultiPolyline()
            if len(line) == 0:
                line = feature.geometry().asPolyline()
                if len(line) == 0:
                    print("Network.get_MultiPolyLine_from_feature: no line extracted from feature", "\n")
                    return None
                else:
                    line = [line]
        except:
            print("Network.get_MultiPolyLine_from_feature: failed to extract line from feature", "\n")
            return None
        return line

    @staticmethod
    def feature_to_shapely_linestring(feature):
        line = Network.get_MultiPolyLine_from_feature(feature)
        if line is not None:
            tuple_line = []
            for p in line[0]:
                tuple_line.append((p.x(), p.y()))
            shapely_geometry = LineString(tuple_line)
            return shapely_geometry
        return None

    def pipes_length(self, log=None):
        if log is not None:
            log.log("---   Network.pipes_lenght()   ---")
        total = 0
        if self.streets_layer is None:
            self.search_and_fix_street_layers(log=log)
        if self.streets_layer is None:
            return total
        if log is not None:
            log.log("self.streets_layer: " + str(self.streets_layer.name()))
        parameters = {'INPUT': self.streets_layer,
                      'OUTPUT': 'TEMPORARY_OUTPUT',
                      'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3035')}
        p = processing.run('qgis:reprojectlayer', parameters)

        if log is not None:
            log.log("parameters: " + str(parameters))
        for f in p['OUTPUT'].getFeatures():
            total = total + f.geometry().length()
            if log is not None:
                log.log("id strada - total length: " + str(f.id()) + " - " + str(total))
        print("Netowrok.pipes_length:", total)
        return total

    def get_residential_factor(self):
        if self.optimized_buildings_layer is not None:
            layer = self.optimized_buildings_layer
        else:
            layer = self.buildings_layer
        if layer is None:
            layer = self.search_and_fix_layers()
        residential = 0
        others = 0
        output = -1
        if layer is not None:
            for feature in layer.getFeatures():
                if feature.attribute("Use") == "Residential":
                    residential = residential + feature.attribute("MaxHeatDem") + feature.attribute(
                        "MaxCoolDem") + feature.attribute("MaxDHWDem")
                else:
                    others = others + feature.attribute("MaxHeatDem") + feature.attribute(
                        "MaxCoolDem") + feature.attribute("MaxDHWDem")
            try:
                output = residential/(residential+others)
            except ZeroDivisionError:
                output = -1
        return output

    def save_network(self, dict_data, directory):
        dict_data["default_crs"] = self.default_crs
        dict_data["sqrPrecision"] = self.sqrPrecision
        dict_data["H_dem_attributes"] = self.H_dem_attributes
        dict_data["C_dem_attributes"] = self.C_dem_attributes
        dict_data["efficiency"] = self.efficiency
        dict_data["name"] = self.name
        dict_data["n_type"] = self.n_type
        dict_data["street_quality_status"] = self.street_quality_status
        dict_data["scenario_type"] = self.scenario_type
        dict_data["buildings_layer"] = save_layer_to_shapefile(self.buildings_layer,
                                                               os.path.join(directory,
                                                                            "Networks",
                                                                            self.get_ID(),
                                                                            "buildings_layer.shp"))
        dict_data["streets_layer"] = save_layer_to_shapefile(self.streets_layer,
                                                             os.path.join(directory,
                                                                          "Networks",
                                                                          self.get_ID(),
                                                                          "streets_layer.shp"))
        dict_data["supply_layer"] = save_layer_to_shapefile(self.supply_layer,
                                                            os.path.join(directory,
                                                                         "Networks",
                                                                         self.get_ID(),
                                                                         "supply_layer.shp"))
        dict_data["optimized_buildings_layer"] = save_layer_to_shapefile(self.optimized_buildings_layer,
                                                                         os.path.join(directory,
                                                                                      "Networks",
                                                                                      self.get_ID(),
                                                                                      "optimized_buildings_layer.shp"))
        dict_data["optimized_streets_layer"] = save_layer_to_shapefile(self.optimized_streets_layer,
                                                                       os.path.join(directory,
                                                                                    "Networks",
                                                                                    self.get_ID(),
                                                                                    "optimized_streets_layer.shp"))
        streets_lyr_backup = self.generate_streets_layer_from_features_list(self.streets_layer_backup)
        dict_data["streets_layer_backup"] = save_layer_to_shapefile(streets_lyr_backup,
                                                                    os.path.join(directory,
                                                                                 "Networks",
                                                                                 self.get_ID(),
                                                                                 "streets_layer_backup.shp"))
        dict_data["graph"] = {}
        self.save_graph(dict_data["graph"])

    def generate_streets_layer_from_features_list(self, features):
        try:
            crs = self.streets_layer.crs().authid()
            layer = QgsVectorLayer('LineString?crs=' + crs, "streets backup", "memory")
            layer.startEditing()
            layer.setCrs(self.street_layer.crs())
            layer.dataProvider().addAttributes([f for f in self.streets_layer.fields()])
            layer.updateFields()
            layer.commitChanges()
            layer.startEditing()
            pr = layer.dataProvider()
            pr.addFeatures(features)
            layer.commitChanges()
            return layer
        except:
            print("Network.py, generate_streets_layer_from_features_list. FAILED to create backup_streets layer")
            return None

    def get_group_name(self):
        return self.n_type + " (" + self.scenario_type + "): " + self.name + " - ID:" + self.get_ID()

    def get_supplies_names(self):
        supply_layer = self.supply_layer
        supply_list = []

        if supply_layer is None:
            print("Network.py, get_supplies_names(). supply_layer is None")
            return supply_list
        if not supply_layer.isValid():
            print("Network.py, get_supplies_names(). supply_layer is invalid")
            return supply_list
        for supply_feature in supply_layer.getFeatures():
            supply_list.append([supply_feature.attribute("name"),
                                supply_feature.attribute("capacity_MW")])
        return supply_list

    def remove_group(self):
        root = QgsProject.instance().layerTreeRoot()
        network_node = root.findGroup(self.get_group_name())
        if network_node is not None:
            root.removeChildNode(network_node)

    def get_save_file_path(self):
        return self.save_file_path

    def connect_generation_points_v2(self, supply_layer, streets_layer):
        feature_list_to_add = []
        self.supply_layer = supply_layer
        self.streets_layer = streets_layer
        for point in self.supply_layer.getFeatures():
            P = point.geometry().asPoint()
            nearest_point, nearest_street, vertex_index = self.get_nearest_street_to_point(P)
            if nearest_point is None:
                print("Network.connect_building_to_streets: self.get_nearest_street_to_point(P) returned None!", "\n")
                continue
            try:
                new_street = [P, nearest_point]
                geom = QgsGeometry().fromPolylineXY(new_street)
                feature = QgsFeature()
                # what if the layer has no features?
                fields = self.streets_layer.fields()
                feature.setFields(fields)
                feature.setGeometry(geom)
                feature_list_to_add.append(feature)
            except:
                print("Something went terribly wrong while creating a new feature for the layer",
                      self.streets_layer.name(), "in Network.connect_building_to_streets", "\n")
        try:
            if len(feature_list_to_add) > 0:
                self.streets_layer.startEditing()
                self.streets_layer.dataProvider().addFeatures(feature_list_to_add)
                self.streets_layer.commitChanges()
        except:
            print("Something went terribly wrong while updating the layer",
                  self.streets_layer.name(), "in Network.connect_generation_points")

    def get_connected_buildings(self):
        index = None
        output_list = []
        root = QgsProject.instance().layerTreeRoot()
        network_node = root.findGroup(self.get_group_name())
        if network_node is None:
            return output_list
        for i, id_layer in enumerate(network_node.findLayerIds()):
            if id_layer.startswith("selected_buildings_"):
                index = i
                break
        else:
            for i, id_layer in enumerate(network_node.findLayerIds()):
                if id_layer.startswith("all_buildings_"):
                    index = i
                    break
        layer = network_node.findLayer(network_node.findLayerIds()[index]).layer()
        if index is None or layer is None:
            return output_list
        for building in layer.getFeatures():
            try:
                if building.attribute("Status") == 2:
                    output_list.append(building)
            except:
                print("Network.get_connected_buildings(): error checking status... WHY?")
                pass
        return output_list

    def search_and_fix_street_layers(self, log=None):
        if log is not None:
            log.log("---   Network.search_and_fix_street_layers()   ---")
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(self.get_group_name())
        if log is not None:
            log.log("self.get_group_name()" + str(self.get_group_name()))
        if group is None:
            return
        layers = group.findLayers()
        for layer in layers:
            if layer.name().startswith("old_network_edges_"):
                if log is not None:
                    log.log("self.streets_layer found: " + str(layer.layer().name()))
                self.streets_layer = layer.layer()
                break
        else:
            for layer in layers:
                if layer.name().startswith("selected_edges_"):
                    if log is not None:
                        log.log("self.streets_layer found: " + str(layer.layer().name()))
                    self.streets_layer = layer.layer()

    def search_and_fix_layers(self, ovveride_layer=True):
        print("Network.search_and_fix_layers() fired")
        root = QgsProject.instance().layerTreeRoot()
        print("Network.search_and_fix_layers() looking for group:", self.get_group_name())
        group = root.findGroup(self.get_group_name())
        if group is None:
            print("Network.search_and_fix_layers() group is None")
            return None
        layers = group.findLayers()
        if self.scenario_type == "baseline":
            for layer in layers:
                if layer.name().startswith("all_buildings_"):
                    try:
                        print("Network.search_and_fix_layers() found layer:", layer.layer().name())
                        if ovveride_layer:
                            self.optimized_buildings_layer = layer.layer()
                    except:
                        print("Network.search_and_fix_layers() found a layer, but failed to write it's name")
                        traceback.print_exc()
                    return layer.layer()
            return None
        else:
            for layer in layers:
                if layer.name().startswith("selected_buildings_"):
                    try:
                        print("Network.search_and_fix_layers() found layer:", layer.layer().name())
                        if ovveride_layer:
                            self.optimized_buildings_layer = layer.layer()
                    except:
                        print("Network.search_and_fix_layers() found a layer, but failed to write it's name")
                        traceback.print_exc()
                    return layer.layer()
            return None

    def get_efficiency(self):
        val = 1.0
        try:
            val = float(self.efficiency)
        except:
            pass
        return val

class network_save(Network):
    def __init__(self, network=None):
        Network.__init__(self, name="default", n_type=network, orig=network, parent=None)
        self.ID = network.get_ID()

    def save_network_baseline(self, dr):
        reti= {}
        self.save_network(reti, dr)
        output_file = os.path.join(dr, self.get_ID() + ".json")
        with open(output_file, 'w') as outfile:
            json.dump(reti, outfile, indent=4)

