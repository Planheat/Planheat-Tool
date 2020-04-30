from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import traceback


class NetworkEfficiency:

    def __init__(self, label: QLabel, spin: QDoubleSpinBox, DHN_network_list: list, DCN_network_list: list,
                 tree_widget: QTreeWidget):
        self.label = label
        self.spin = spin
        self.DHN_network_list = DHN_network_list
        self.DCN_network_list = DCN_network_list
        self.tree_widget = tree_widget

    def update_network_efficiency(self):
        updates = []
        for item in self.tree_widget.selectedItems():
            try:
                parent = NetworkEfficiency.get_item_anchestor(item)
                network = self.find_network(parent.data(0, Qt.UserRole))
                network.efficiency = self.spin.value()
                updates.append(network.name)
            except Exception:
                traceback.print_exc()
        self.visualize_succes(updates)

    def visualize_succes(self, updates: list):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Done")
        if len(updates) == 0:
            txt = "No networks have been updated."
        elif len(updates) == 1:
            txt = "Updated efficiency of network: " + updates[0]
            txt += "\nNew value: " + str(self.spin.value())
        else:
            txt = "Updated efficiency of networks:"
            for update in updates:
                txt += "\n\t- " + update
            txt += "\nNew values: " + str(self.spin.value())
        msgBox.setInformativeText(txt)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        ret = msgBox.exec()

    def change_spin_box_value(self, item: QTreeWidgetItem):
        try:
            parent = NetworkEfficiency.get_item_anchestor(item)
            network = self.find_network(parent.data(0, Qt.UserRole))
            new_value = float(network.efficiency)
            self.spin.setValue(new_value)
        except Exception:
            traceback.print_exc()

    @staticmethod
    def get_item_anchestor(item: QTreeWidgetItem):
        if item is None:
            return None
        max_loop = 10
        i = 0
        while i < max_loop:
            i += 1
            if item.parent() is None:
                return item
            else:
                item = item.parent()
        return None

    def find_network(self, network_id: str):
        for network_list in [self.DHN_network_list, self.DCN_network_list]:
            for network in network_list:
                if network.get_ID() == network_id:
                    return network