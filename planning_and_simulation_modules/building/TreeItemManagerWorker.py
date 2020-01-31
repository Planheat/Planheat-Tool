from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QTreeWidget
import traceback


class TreeItemManagerWorker(QObject):

    finished = pyqtSignal()
    started = pyqtSignal()

    # def __init__(self, buildings_tree: QTreeWidget, networks_tree: QTreeWidget, network_lists: list):
    def __init__(self, network_lists: list):
        QObject.__init__(self)
        #self.buildings_tree = buildings_tree
        #self.networks_tree = networks_tree
        self.network_lists = network_lists

    def run(self):
        try:
            self.started.emit()
            print("TreeItemManagerWorker started in thread:", int(QThread.currentThread().currentThreadId()))
            for network_list in self.network_lists:
                for network in network_list:
                    print("TreeItemManagerWorker network:", network.name)
            self.finished.emit()
        except Exception as e:
            traceback.print_exc()
            self.finished.emit()