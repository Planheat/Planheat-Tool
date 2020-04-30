from ..SourcesTableFactors import SourcesTableFactors
from ...db.DatabaseService import DatabaseService
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
import traceback


class SourcesTableDefaultLoader:

    def __init__(self):
        pass

    @staticmethod
    def load_default(sourcesTable: QTableWidget):
        try:
            db = DatabaseService()
            default_data = SourcesTableFactors()
            db.set_sources_table_factors_params(default_data)
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
                        sourcesTable.hideRow(i)
                        break
        except Exception:
            traceback.print_exc()
