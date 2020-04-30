from PyQt5.QtWidgets import QTreeWidget
from ...building.Building import Building
from ..test.MyLog import MyLog


class JuliaBuildingChecker:

    def __init__(self):
        pass

    def building_needs_simulation(self, widget: QTreeWidget, building_id: str, log: MyLog = None):
        if log: log.log("--- building_needs_simulation ---")
        for i in range(widget.topLevelItemCount()):
            building: Building = widget.topLevelItem(i)
            if building.building_id == building_id:
                if building.connected_to_DHN and building.connected_to_DCN:
                    if log: log.log("Building", building_id, "is connected to DHC and DCN")
                    return False
                for j in range(building.childCount()):
                    if building.child(j).childCount() > 0:
                        if log: log.log("Building", building_id, "has technologies in", building.child(j).text(0))
                        return True
                if log: log.log("Building", building_id, "has no technologies")
                return False

