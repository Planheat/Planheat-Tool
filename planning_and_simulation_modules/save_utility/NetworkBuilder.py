from ..Network import Network


class NetworkBuilder:

    def __init__(self):
        self.ID = None  # i need an identifier
        self.default_crs = 'EPSG:4326'
        self.sqrPrecision = 0.02
        self.save_file_path = None
        self.H_dem_attributes = ["MaxHeatDem"]
        self.C_dem_attributes = ["MaxCoolDem"]
        self.optimizer_results = {}
        self.optimized = False
        self.efficiency = 1.0
        self.name = None
        self.n_type = None
        self.buildings_layer = None
        self.streets_layer = None
        self.streets_layer_backup = []
        self.optimized_buildings_layer = None
        self.optimized_streets_layer = None
        self.street_quality_status = False
        self.scenario_type = None
        self.supply_layer = None

    def build(self):
        n = Network(name=self.name, n_type=self.n_type, orig=None, parent=None)
        n.ID = self.ID
        n.save_file_path = self.save_file_path
        n.optimizer_results = {}
        n.optimized = False
        n.efficiency = 1.0
        n.buildings_layer = self.buildings_layer
        n.streets_layer = self.streets_layer
        n.streets_layer_backup = self.streets_layer_backup
        n.optimized_buildings_layer = self.optimized_buildings_layer
        n.optimized_streets_layer = self.optimized_streets_layer
        n.street_quality_status = self.street_quality_status
        n.scenario_type = self.scenario_type
        n.supply_layer = self.supply_layer
        print("NetworkBuilder.build() n.ID, n.save_file_path, n.scenario_type, n.name",
              n.ID, n.save_file_path, n.scenario_type, n.name)
        return n
