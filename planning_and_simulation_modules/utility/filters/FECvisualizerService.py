from PyQt5.QtWidgets import QTableWidget, QComboBox, QLabel, QTableWidgetItem, QHeaderView
from .FECfilterService import FECfilterService


class FECvisualizerService:

    def __init__(self, output_table: QTableWidget, fec_filter_combo_box: QComboBox, description_filter_label: QLabel,
                 mode="future"):
        self.fec_filter_combo_box = fec_filter_combo_box
        self.description_filter_label = description_filter_label
        self.output_table = output_table
        self.KPIs = {}

        self.filter = FECfilterService(self.fec_filter_combo_box, self.description_filter_label, mode=mode)

        self.fec_filter_combo_box.currentTextChanged.connect(self.combo_box_text_changed)

    def combo_box_text_changed(self, new_text):
        self.filter.update_label(new_text)
        self.update_table()

    def update_table(self):
        self.output_table.clearContents()
        new_data = self.filter.get_filtered_table(self.KPIs)
        self.output_table.setRowCount(len(new_data.keys()))
        for row, key in enumerate(new_data.keys()):
            self.output_table.setItem(row, 0, QTableWidgetItem(key))
            self.output_table.setItem(row, 1, QTableWidgetItem(str(new_data[key]["R"])))
            self.output_table.setItem(row, 2, QTableWidgetItem(str(new_data[key]["T"])))
            self.output_table.setItem(row, 3, QTableWidgetItem(str(new_data[key]["TOT"])))
        self.format_table()

    def format_table(self):
        header = self.output_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

    def set_KPIs(self, KPIs):
        self.KPIs = KPIs

    def get_fec(self):
        return [FECfilterService.get_from_key(self.KPIs, "EN_2.1_s" + str(i)) for i in range(23)]

    def get_fec_fut(self):
        return [FECfilterService.get_from_key(self.KPIs, "EN_2.3_s" + str(i)) for i in range(23)]

    def get_sources(self):
        return FECfilterService.get_from_key(self.KPIs, "sources")
