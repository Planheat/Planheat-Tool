from PyQt5.QtWidgets import QTreeWidgetItem
from ...config.technologies.network_capex_columns import data
from .TechCapex import TechCapex

class NetworkTechCapex(TechCapex):

    def __init__(self):
        TechCapex.__init__()

    @staticmethod
    def capext(tech: QTreeWidgetItem):
        try:
            name = tech.text(1)
            if name in ["Seasonal Solar Thermal", "Evacuated tube solar collectors", "Flat plate solar collectors"]:
                return 0.001 * float(tech.text(data[name]["area"])) * float(tech.text(data[name]["costs"])) * float(tech.text(data[name]["eta"]))
            if name in ["Thermal energy storage", "DHW thermal energy storage", "Seasonal thermal energy storage"]:
                return (float(tech.text(data[name]["size"])) / float(tech.text(data[name]["charge"]))) * float(
                    tech.text(data[name]["costs"]))
            return float(tech.text(data[name]["capacity"])) * float(tech.text(data[name]["costs"]))
        except Exception:
           return 0.0

    @staticmethod
    def compare(tech1: QTreeWidgetItem, tech2: QTreeWidgetItem):
        return TechCapex.tech_compare(tech1, tech2, data)