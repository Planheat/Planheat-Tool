from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import Qt
from ...config.technologies.building_capex_columns import data
from .TechCapex import TechCapex


class BuildingTechCapex(TechCapex):

    def __init__(self):
        TechCapex.__init__()

    @staticmethod
    def capext(tech: QTreeWidgetItem):
        try:
            name = tech.text(0)
            if name in ["Seasonal Solar Thermal", "Evacuated tube solar collectors", "Flat plate solar collectors"]:
                panel_area = float(tech.data(3, Qt.UserRole))
                return panel_area * float(tech.text(data[name]["costs"])) * float(tech.text(data[name]["eta"]))
            if name in ["Thermal energy storage", "DHW thermal energy storage", "Seasonal thermal energy storage"]:
                return (float(tech.text(data[name]["size"])) / float(tech.text(data[name]["charge"]))) * float(
                    tech.text(data[name]["costs"]))
            return float(tech.text(data[name]["capacity"])) * float(tech.text(data[name]["costs"]))
        except Exception:
            return 0.0

    @staticmethod
    def compare(tech1: QTreeWidgetItem, tech2: QTreeWidgetItem):
        return TechCapex.tech_compare(tech1, tech2, data)