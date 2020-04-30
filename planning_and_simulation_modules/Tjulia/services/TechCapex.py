from PyQt5.QtWidgets import QTreeWidgetItem


class TechCapex:

    def __init__(self):
        pass

    @staticmethod
    def tech_compare(tech1: QTreeWidgetItem, tech2: QTreeWidgetItem, data: dict):
        try:
            name1 = tech1.text(0)
            name2 = tech2.text(0)
            if not name1 == name2:
                return False
            for compare_column in data[name2]["compare"]:
                if not tech2.text(compare_column) == tech1.text(compare_column):
                    return False
            return True
        except Exception:
            return False