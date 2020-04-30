from PyQt5.QtWidgets import QTreeWidget, QMessageBox
from ...layer_utils import read_layer_attribute_by_id
from ...building.Building import Building
from PyQt5 import QtCore


class TechnologiesTransfer:

    def __init__(self, widget_input: QTreeWidget, n_tree: QTreeWidget=None):
        if widget_input is None:
            print("TechologiesTransfer.__init__(): some inputs are None")
        self.widget_input = widget_input
        self.widget_output: QTreeWidget = None
        self.buildings_transferred = False
        self.n_tree = n_tree

    def tree_widget_transfer(self, widget_output: QTreeWidget):
        self.widget_output = widget_output
        if self.widget_input is None or self.widget_output is None:
            print("TechologiesTransfer.transfer(): some inputs are None. Transfer aborted")
            return
        self.widget_output.clear()
        for i in range(self.widget_input.topLevelItemCount()):
            self.widget_output.insertTopLevelItem(i, self.widget_input.topLevelItem(i).clone())

    def buildings_tree_widget_transfer(self, widget_output: QTreeWidget, baseline_layer, future_layer):
        self.widget_output = widget_output
        if self.widget_input is None or self.widget_output is None or baseline_layer is None or future_layer is None:
            print("TechologiesTransfer.buildings_tree_widget_transfer(): some inputs are None. Transfer aborted")
            return
        if not self.check_if_override():
            return
        if not self.check_if_scenarios_exist():
            return
        dic_building_input_id = {}
        nb_input = self.widget_input.topLevelItemCount()
        for i in range(nb_input):
            building_input = self.widget_input.topLevelItem(i)
            #print("TechnologiesTransfer.buildings_tree_widget_transfer(). building_input:", building_input.text(0))
            building_input_id = read_layer_attribute_by_id(baseline_layer, building_input.text(0), "BuildingID")
            #print("TechnologiesTransfer.buildings_tree_widget_transfer(). building_input_id:", building_input_id)
            dic_building_input_id[building_input_id] = building_input
        for j in range(widget_output.topLevelItemCount()):
            building_target: Building = widget_output.topLevelItem(j)
            building_target_id = read_layer_attribute_by_id(future_layer, building_target.text(0), "BuildingID")
            if building_target_id in dic_building_input_id:
                self.transfer_single_building(dic_building_input_id[building_target_id], building_target)
        self.buildings_transferred = True

    def transfer_single_building(self, building_input, building_target: Building):
        building_target.set_unmodified()
        # I'll tanke only the first 3 childs
        for i in range(3):
            input_service = building_input.child(i)
            target_service = building_target.child(i)
            self.transfer_single_service(input_service, target_service)

    def transfer_single_service(self, input_service, target_service):
        for i in range(target_service.childCount()):
            target_service.removeChild(target_service.child(i))
        for i in range(input_service.childCount()):
            target_service.addChild(input_service.child(i).clone())

    def check_if_scenarios_exist(self):
        if self.widget_output.topLevelItemCount() == 0 or self.widget_input.topLevelItemCount() == 0:
            QMessageBox.warning(None, "Warning", "Baseline and Future scenario buildings shapefiles are not correctly "
                                                 "initialized. Go back to step 0 to fix this.")
            return False
        else:
            return True

    def check_if_override(self):
        if not self.buildings_transferred:
            return True
        msgBox = QMessageBox()
        msgBox.setText("Do you want to transfer baseline characterization data?")
        msgBox.setInformativeText(
            "If you press Ok all the building characterization data in the future scenario assesment will be replaced "
            "with the information coming from the baseline scenario.\nThis can be useful if you want to start again the future scenario characterization."
            "\nIf you want to proceed keeping the already existing data, please click Cancel."
            "\nIf you don't know, click Cancel.")
        msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec()
        if ret == QMessageBox.Ok:
            return True
        else:
            return False

    def update_network_id_user_role_data(self, future_networks):
        print("TechologiesTransfer:")
        for lista in future_networks:
            for n in lista:
                print(n.get_ID(), "-", n.cloned_from)
        for i in range(self.widget_output.topLevelItemCount()):
            future_network_id = self.widget_output.topLevelItem(i).data(0, QtCore.Qt.UserRole)
            print("---")
            print("future_network_id:", future_network_id)
            for j in range(self.widget_input.topLevelItemCount()):
                baseline_network_id = self.widget_input.topLevelItem(j).data(0, QtCore.Qt.UserRole)
                print("baseline_network_id:", baseline_network_id)
                if baseline_network_id == future_network_id:
                    print("FOUND")
                    for future_networks_service in future_networks:
                        for network in future_networks_service:
                            print("network.cloned_from vs baseline_network_id", network.cloned_from, baseline_network_id)
                            if network.cloned_from == baseline_network_id:
                                print("FOUND and start to replace")
                                self.widget_output.topLevelItem(i).setData(0, QtCore.Qt.UserRole,
                                                                           QtCore.QVariant(network.get_ID()))
                                break
                        else:
                            continue
                        break
                    else:
                        continue
                    break

