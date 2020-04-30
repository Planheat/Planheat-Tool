from PyQt5.QtWidgets import QTreeWidgetItem, QTreeWidget
from PyQt5.QtCore import Qt


class QtTreeWidgetPrinter:

    def __init__(self):
        pass

    @staticmethod
    def printer(widget: QTreeWidget):
        for i in range(widget.topLevelItemCount()):
            QtTreeWidgetPrinter.dig_item(widget.topLevelItem(i))

    @staticmethod
    def dig_item(item: QTreeWidgetItem):
        QtTreeWidgetPrinter.child_printer(item)
        for i in range(item.childCount()):
            QtTreeWidgetPrinter.dig_item(item.child(i))

    @staticmethod
    def child_printer(item: QTreeWidgetItem):
        values = []
        user_role_data = []
        for i in range(item.columnCount()):
            values.append(item.text(i))
            user_role_data.append(item.data(i, Qt.UserRole))
        print("values:", values)
        print("user_role_data:", user_role_data)
