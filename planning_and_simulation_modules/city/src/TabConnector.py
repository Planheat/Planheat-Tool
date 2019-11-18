import os
import os.path
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtCore import Qt
from .qt_utils import copy_table


class TabConnector:
    def __init__(self):
        pass

    @staticmethod
    def copy_tables(list_tables):
        for tables in list_tables:
            range_list = [[1, tables[0].rowCount(), 0, tables[0].columnCount()]]
            copy_table(tables[0], tables[1], ranges=range_list, mode="v")
