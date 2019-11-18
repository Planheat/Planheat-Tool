from ..Network import Network
from qgis.core import QgsFeature, QgsVectorLayer


class PluginTest:

    step0 = None
    step1 = None
    step2 = None
    step3 = None
    step4 = None
    simulation = None

    def __init__(self, step0, step1, step2, step3, step4, simulation):
        self.step0 = step0
        self.step1 = step1
        self.step2 = step2
        self.step3 = step3
        self.step4 = step4
        self.simulation = simulation

    def add_fake_network(self, type, scenario, dim):
        if not scenario == "baseline":
            scenario = "baseline"
            print("PluginTest.py, add_network(). Can only add network to baseline scenario")
        n = Network()
        n.n_type = type
        n.scenario_type = scenario

        layer = self.step1.building_layer
        layer_copy = QgsVectorLayer(layer.source().split("&")[0], layer.name(), layer.providerType())
        new_features = [QgsFeature(f) for f in layer.getFeatures()]
        new_features = new_features[0:dim]
        layer_copy.startEditing()
        layer_copy.dataProvider().addAttributes([f for f in layer.fields()])
        layer_copy.updateFields()
        layer_copy.dataProvider().addFeatures(new_features)
        layer_copy.commitChanges()

        n.buildings_layer = layer

        layer = self.step1.street_layer
        layer_copy = QgsVectorLayer(layer.source().split("&")[0], layer.name(), layer.providerType())
        new_features = [QgsFeature(f) for f in layer.getFeatures()]
        new_features = new_features[0:dim]
        layer_copy.startEditing()
        layer_copy.dataProvider().addAttributes([f for f in layer.fields()])
        layer_copy.updateFields()
        layer_copy.dataProvider().addFeatures(new_features)
        layer_copy.commitChanges()

        n.streets_layer = layer

        n.streets_layer_backup = new_features
