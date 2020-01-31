from ..SourcesTableFactors import SourcesTableFactors
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
import traceback


class SourcesTableDefaultLoader:

    def __init__(self):
        pass

    @staticmethod
    def load_default(sourcesTable: QTableWidget):
        try:
            default_data = SourcesTableFactors()
            for i in range(sourcesTable.rowCount()):
                data = default_data.get_params(sourcesTable.verticalHeaderItem(i).text())
                for j, value in enumerate(data):
                    sourcesTable.setItem(i, j, QTableWidgetItem(str(value)))
        except Exception:
            traceback.print_exc()

    @staticmethod
    def hide_default_rows(sourcesTable: QTableWidget):
        try:
            default_data = SourcesTableFactors()
            for row in default_data.get_hidden_rows():
                for i in range(sourcesTable.rowCount()):
                    if sourcesTable.verticalHeaderItem(i).text() == row:
                        if row == "Excess heat - Data centers":
                            print("Excess heat - Data centers !!! Excess heat - Data centers", i)
                        sourcesTable.hideRow(i)
                        break
        except Exception:
            traceback.print_exc()
