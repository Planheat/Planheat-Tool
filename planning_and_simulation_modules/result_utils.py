import pip
import matplotlib

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QCheckBox, QHBoxLayout

matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import QSizePolicy, QMessageBox
from PyQt5.QtCore import QItemSelectionModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

FIRST = True


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=2, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot([], [], None)

    def plot(self, sectorTable, districtTable, data):
        global FIRST
        if sectorTable and sectorTable.selectedItems():
            labels = []
            selected_rows = []
            for row in sectorTable.selectedItems():
                selected_rows.append(row.text())
            selected_districts = districtTable.selectedItems()
            if len(selected_districts) > 20:
                if FIRST:
                    QMessageBox.information(None, "Warning", "Too many districts selected. Only showing the first 20 districts in graph.")
                    FIRST = False
                selected_districts = selected_districts[:20]
            for row in selected_districts:
                if row.text() not in labels:
                    labels.append(row.text())
            if labels and selected_rows:
                self.figure.clf()
                ax = self.figure.add_subplot(111)
                leftover_rows = (data.loc[selected_rows])
                tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
                tableau20 = [(r / 255, g / 255, b / 255) for r, g, b in tableau20]

                if leftover_rows[labels] is not None:
                    plt = leftover_rows[labels].T.plot.barh(ax=ax, stacked=True, legend=True, width=0.8, color=tableau20)
                font_p = FontProperties()
                font_p.set_size('small')
                ax.legend(leftover_rows["Class"] + " - " + leftover_rows["Description"], loc=2, bbox_to_anchor=(1.01, 1), prop=font_p)
                self.figure.tight_layout(rect=[0, 0, 0.75, 1])
                self.draw()


def fill_sector_table(data, table, plot):
    table.setSortingEnabled(False)
    smodel = table.selectionModel()
    for c, field in enumerate(data.index):
        if str(field) != '':
            widget_item = QTableWidgetItem(str(field))
            if data.iloc[c]['Selected'] == "Yes" and not(str(field).startswith('Deep')or str(field).startswith('Advanced')or str(field).startswith('Forest')or str(field).startswith('Surface')):
                widget_item.setSelected(True)
                model_index = table.model().createIndex(c, 0)
                smodel.select(model_index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            table.setItem(c, 1, widget_item)
    table.setSortingEnabled(True)


def fill_district_table(data, table, plot):
    table.setSortingEnabled(False)
    for c, field in enumerate(data.columns.values.tolist()[3:]):
        if str(field) != '':
            widget_item = QTableWidgetItem(str(field))
            table.setItem(c, 1, widget_item)
    table.setSortingEnabled(True)
