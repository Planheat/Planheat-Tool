import os, shutil
import unittest
from nose.plugins.attrib import attr
from nose.tools import assert_in, assert_false, assert_not_in
import logging
import geopandas as gpd
from ...optimizer.DHCOptimizer import DHCOptimizer
from ...optimizer import config


@attr('automatic_design')
class TestAutomaticDesign(unittest.TestCase):

    def setUp(self):
        file_dir = os.path.dirname(__file__)
        self.results_dir = os.path.join(file_dir, "results/")
        self.data_dir = os.path.join(file_dir, "../../data/Antwerp_01/")
        if not os.path.exists(self.results_dir):
            os.mkdir(self.results_dir)

    def tearDown(self):
        shutil.rmtree(self.results_dir)


    def test_run_FCFCCP(self):
        district_shape = os.path.join(self.data_dir, "antwerp_01_shape.shp")

        # buildings
        buildings_path = os.path.join(self.data_dir, "antwerp_01_buildings.shp")
        marked_buildings = {'5321187.0', '5321165.0', '5321099.0', '5326321.0', '5321218.0', '5321219.0', '3737065.0',
                            '5326308.0', '3736531.0', '5326263.0', '5321207.0', '3737043.0', '3736950.0', '3737006.0',
                            '5321186.0', '5321152.0', '3736521.0', '3736965.0', '5321145.0', '3736949.0'}
        excluded_streets = {('4425526631', '5868786923'), ('5344904184', '276785748'), ('4935695474', '4935695470'),
                            ('4425526631', '4379660337'), ('221471611', '221470334'), ('195585963', '205458506'),
                            ('4241948344', '1904622108'), ('205466281', '276785748'), ('1904589710', '220727141'),
                            ('370626895', '370800156'), ('4425526639', '4379647009'), ('220734940', '206137275'),
                            ('4241948344', '4376546422'), ('220706669', '4878471829'), ('237768189', '205465493'),
                            ('655344485', '655344484'), ('370626895', '370628404'), ('197762183', '27307067'),
                            ('196191118', '195585878'), ('4241948312', '4379647009'), ('220729562', '220731035'),
                            ('220739268', '203379815'), ('217754032', '217754302'), ('217746618', '217746617'),
                            ('260791188', '195752799'), ('4246205430', '220724162'), ('26522010', '27307038')}

        supply_gdf = gpd.read_file(os.path.join(self.data_dir, "../Waste_heat_city_3.shp"))
        supply_gdf.to_crs(config.CRS, inplace=True)
        prod_mapping = {'<20': 10.0, '20 tot 200': 110.0, '250 tot 500': 375.0, '>200': 350.0, '>500': 700.0}
        supply_gdf["GWh_year"] = list(map(lambda x: prod_mapping[x], supply_gdf["GWh_year"]))
        supply_gdf["GWh_year"] = supply_gdf["GWh_year"] / (365 * 24) * 1000
        supply_gdf.rename(columns={"GWh_year": config.SUPPLY_POWER_CAPACITY_KEY}, inplace=True)

        dhc_opt = DHCOptimizer(DHCOptimizer.FCFCCP, district=district_shape,
                               buildings_file_path=buildings_path,
                               marked_buildings=marked_buildings,
                               excluded_streets=excluded_streets,
                               network_objective=46.99,
                               potential_supply=supply_gdf)

        dhc_opt.result_dir = self.results_dir

        dhc_opt.logger = logging.getLogger()
        dhc_opt.logger.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s')
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        dhc_opt.logger.addHandler(stream_handler)

        dhc_opt.run()

        g = dhc_opt.network_optimizer.optimization_graph

        for b in marked_buildings:
            assert_not_in(b, g.nodes, "A marked building is not in the solution graph")

        for e in excluded_streets:
            assert_false(g.has_edge(e[0], e[1]), "An excluded street is in the optimization graph")




