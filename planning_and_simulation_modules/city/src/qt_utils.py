from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt


def make_table_not_editable(qt_table):
    for i in range(qt_table.rowCount()):
        for j in range(qt_table.columnCount()):
            if qt_table.item(i, j) is None:
                empty_table_widget_item = QTableWidgetItem("")
                empty_table_widget_item.setFlags(Qt.ItemIsEnabled)
                qt_table.setItem(i, j, empty_table_widget_item)
            else:
                qt_table.item(i, j).setFlags(Qt.ItemIsEnabled)


def copy_table(source, target, ranges=None, mode=""):
    if ranges is None:
        ranges = [[source.rowCount(), source.columnCount()]]
    if "v" in mode:
        for i in range(source.rowCount()):
            vertical_header_item = source.verticalHeaderItem(i)
            try:
                target.setVerticalHeaderItem(i, QTableWidgetItem(vertical_header_item))
            except:
                pass
    if "h" in mode:
        for j in range(source.columnCount()):
            horizontal_header_item = source.horizontalHeaderItem(j)
            try:
                target.setHorizontalHeaderItem(j, QTableWidgetItem(horizontal_header_item))
            except:
                pass
    for r in ranges:
        for i in range(r[0], r[1]):
            for j in range(r[2], r[3]):
                item = source.item(i, j)
                try:
                    target.setItem(i, j, QTableWidgetItem(item))
                except:
                    pass
