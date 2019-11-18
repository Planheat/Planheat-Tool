import os
import os.path
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtCore import Qt
from .qt_utils import copy_table
from.TabConnector import TabConnector


class StepConnector:
    def __init__(self, step01, step2):
        self.step01 = step01
        self.step2 = step2

    def data_transfer_step01_step2(self):
        TabConnector.copy_tables([[self.step01.table_sd_HeDHW, self.step2.table_sd_target],
                                  [self.step01.table_sd_cool, self.step2.table_sd_cool_targ],
                                  [self.step01.tb_HeDHW_source, self.step2.table_HeDHW_source_targ],
                                  [self.step01.table_cool_source, self.step2.table_cool_source]])