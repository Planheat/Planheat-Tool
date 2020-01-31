from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtCore import QThread, QObject

from .TreeItemManagerWorker import TreeItemManagerWorker


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
        Hide or show the buildings in the QtreeWidget checking if they are connected to at least one network
        :return:
        """
        for i in range(self.buildings_tree.topLevelItemCount()):
            building = self.buildings_tree.topLevelItem(i)
            for network_list in self.network_lists:
                for network in network_list:
                    if building.building_id in [feature.attribute("BuildingID") for feature in
                                                network.get_connected_buildings()]:
                        building.setHidden(True)
                        building.clear_technologies()
                        break
                else:
                    continue
                break
            else:
                building.setHidden(False)

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

