from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import QThread, QObject

from .TreeItemManagerWorker import TreeItemManagerWorker
from .Building import Building


class TreeItemManager(QObject):

    def __init__(self, iface, buildings_tree: QTreeWidget, networks_tree: QTreeWidget, network_lists: list):
        QObject.__init__(self)
        self.iface = iface
        self.buildings_tree = buildings_tree
        self.networks_tree = networks_tree
        self.network_lists = network_lists
        self.running = False
        self.priority: int = 7

    def update_buildings_visualizzation(self):
        """
        Hide or show the buildings in the QtreeWidget checking if they are connected to at least one HEATING network
        :return:
        """
        for i in range(self.buildings_tree.topLevelItemCount()):
            building: Building = self.buildings_tree.topLevelItem(i)
            for DCN_network in self.network_lists[0]:
                if building.building_id in [feature.attribute("BuildingID") for feature in
                                            DCN_network.get_connected_buildings()]:
                    building.connected_to_DCN = True
                    break
            else:
                building.connected_to_DCN = False
            for DHN_network in self.network_lists[1]:
                if building.building_id in [feature.attribute("BuildingID") for feature in
                                            DHN_network.get_connected_buildings()]:
                    building.connected_to_DHN = True
                    break
            else:
                building.connected_to_DHN = False
            self.update_single_building_visualizzation(building)

    def fast_update_buildings_visualizzation(self):
        """
        This function does not recompute buildings network connection, it just rely on the building attribute
        :return:
        """
        for i in range(self.buildings_tree.topLevelItemCount()):
            building: Building = self.buildings_tree.topLevelItem(i)
            self.update_single_building_visualizzation(building)


    def update_single_building_visualizzation(self, building: Building):
        if building.connected_to_DHN and building.connected_to_DCN:
            building.setHidden(True)
            building.clear_technologies()
        else:
            for i in range(building.childCount()):
                service: QTreeWidgetItem = building.child(i)
                clear_service = False
                if building.connected_to_DHN and (service.text(0) == "Heating" or service.text(0) == "DHW"):
                    service.setHidden(True)
                    clear_service = True
                elif building.connected_to_DCN and service.text(0) == "Cooling":
                    service.setHidden(True)
                    clear_service = True
                else:
                    service.setHidden(False)
                if clear_service:
                    service.takeChildren()

    def update_buildings_status(self, new_status: dict):
        for i in range(self.buildings_tree.topLevelItemCount()):
            building: Building = self.buildings_tree.topLevelItem(i)
            new_single_building_status = new_status.get(building.text(0))
            if new_single_building_status is None:
                continue
            building.connected_to_DHN = new_single_building_status.get("connected_to_DHN", False)
            building.connected_to_DCN = new_single_building_status.get("connected_to_DCN", False)
            building.modified = new_single_building_status.get("modified", False)
        self.fast_update_buildings_visualizzation()

    def get_building_status(self):
        status = {}
        for i in range(self.buildings_tree.topLevelItemCount()):
            building: Building = self.buildings_tree.topLevelItem(i)
            building_id = building.text(0)
            status[building_id] = {}
            status[building_id]["connected_to_DHN"] = building.connected_to_DHN
            status[building_id]["connected_to_DCN"] = building.connected_to_DCN
            status[building_id]["modified"] = building.modified
        return status


    # this method is not used, left just for reference
    def update_buildings_visualizzation_thread(self):
        if self.running:
            return
        print("TreeItemManager.update_buildings_visualizzation() thread:",
              int(QThread.currentThread().currentThreadId()))
        # self.worker = TreeItemManagerWorker(self.buildings_tree, self.networks_tree, self.network_lists)
        self.worker = TreeItemManagerWorker(self.network_lists)
        # thread = QThread(self.iface.mainWindow())
        self.thread = QThread(self.iface.mainWindow())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.started.connect(self.worker.started)
        self.worker.finished.connect(self.worker.finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def worker_finished(self):
        self.running = False
        print("TreeItemManager thread:", int(QThread.currentThread().currentThreadId()), "worker DONE")

    def worker_started(self):
        self.running = True
        print("TreeItemManager thread:", int(QThread.currentThread().currentThreadId()), "worker STARTED")

