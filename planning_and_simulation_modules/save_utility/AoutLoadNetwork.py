from ..Network import Network
from ..utility.data_manager.DataTransfer import DataTransfer
from ..dhcoptimizerplanheat.dhcoptimizer_planheat import DHCOptimizerPlanheat
import os.path
import os
import traceback

#QGIS stuff
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.core import QgsProject


class AutoLoadNetwork:

    def __init__(self, work_folder):
        self.work_folder = work_folder

    def load(self, network: Network, data_transfer: DataTransfer):
        try:
            self.router_optimizer(network, data_transfer)
        except Exception:
            traceback.print_exc()

    def router_optimizer(self, network: Network, data_transfer: DataTransfer):
        root = QgsProject.instance().layerTreeRoot()
        network_node = root.findGroup(network.get_group_name())
        result_node = network_node.findGroup("Router Optimizer RESULTS")
        if result_node is not None:
                network_node.removeChildNode(result_node)

        if network.scenario_type == "baseline":
            scenario_type = "Baseline"
        else:
            scenario_type = "Future"

        folder = os.path.join(self.work_folder, scenario_type, "Networks", network.n_type, network.get_ID())
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            data_transfer.automatic_upload_network = False
        elif os.path.isfile(os.path.join(folder, network.name + ".zip")):
            data_transfer.automatic_upload_network = True
        else:
            data_transfer.automatic_upload_network = False
        network.save_file_path = os.path.join(folder, network.name + ".zip")

        data_transfer.network = network
        data_transfer.study_id += 1
        data_transfer.step1_mode = True  # do not shows dialog

        dhcoptimizerplanheat = DHCOptimizerPlanheat(iface,
                                                    working_directory=folder,
                                                    data_transfer=data_transfer)
        dhcoptimizerplanheat.dialog_menu.radioButton_1_auto.setChecked(True)
        dhcoptimizerplanheat.dialog_menu.radioButton_2_manual.setChecked(False)

        dhcoptimizerplanheat.run()

        canvas = iface.mapCanvas()
        root = QgsProject.instance().layerTreeRoot()
        for layer in root.findLayers():
            if layer.name().startswith("all_streets_{0}".format(data_transfer.study_id)):
                proj = QgsProject.instance()
                ex = layer.layer().extent()

                if layer.layer().crs().authid() != proj.crs().authid():
                    print("Layer has not the same CRS as proj",
                          layer.layer().crs().authid(), proj.crs().authid())
                    tr = QgsCoordinateTransform(layer.layer().crs(), proj.crs(), proj)
                    ex = tr.transform(ex)
                canvas.setExtent(ex)
                canvas.refresh()

        dhcoptimizerplanheat.dock.closed.emit()
        dhcoptimizerplanheat.manual_dock.closed.emit()
        AutoLoadNetwork.dhcoptimizerplanheat_closed(dhcoptimizerplanheat)

    @staticmethod
    def dhcoptimizerplanheat_closed(dhcoptimizerplanheat: DHCOptimizerPlanheat):
        root = QgsProject.instance().layerTreeRoot()
        network_group_name = dhcoptimizerplanheat.data_transfer.network.get_group_name()
        network_node = root.findGroup(network_group_name)
        if network_node is None:
            print("AutoLoadNetwork.py, dhcoptimizerplanheat_closed(). ERROR: network node not found")
        old = dhcoptimizerplanheat.data_transfer.tree_group
        try:
            new = old.clone()
        except RuntimeError:
            root = QgsProject.instance().layerTreeRoot()
            old = root.findGroup(dhcoptimizerplanheat.data_transfer.tree_group_name)
            new = old.clone()
        network_node.addChildNode(new)
        network_node.removeChildNode(old)
        new.setName("Router Optimizer RESULTS")


