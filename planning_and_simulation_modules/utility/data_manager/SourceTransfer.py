from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class SourceTransfer:

    def __init__(self, widget_input: QTableWidget):
        if widget_input is None:
            print("SourceTransfer.__init__(): some inputs are None")
        self.widget_input = widget_input

    def transfer_sources_table(self, target_table: QTableWidget):
        if target_table is None or self.widget_input is None:
            return
        target_table.clear()
        target_table.setRowCount(self.widget_input.rowCount())
        target_table.setColumnCount(self.widget_input.columnCount())

        for i in range(self.widget_input.rowCount()):
            try:
                target_table.setVerticalHeaderItem(i, self.widget_input.verticalHeaderItem(i).clone())
            except AttributeError:
                target_table.setVerticalHeaderItem(i, QTableWidgetItem())

        for i in range(self.widget_input.columnCount()):
            try:
                print("SourceTransfer.transfer_sources_table(), self.widget_input.horizontalHeaderItem(i):",
                      self.widget_input.horizontalHeaderItem(i))
                print("SourceTransfer.transfer_sources_table(), self.widget_input.horizontalHeaderItem(i):",
                      self.widget_input.horizontalHeaderItem(i).text())
                target_table.setHorizontalHeaderItem(i, self.widget_input.horizontalHeaderItem(i).clone())

            except AttributeError:
                target_table.setHorizontalHeaderItem(i, QTableWidgetItem())

        for i in range(self.widget_input.rowCount()):
            for j in range(self.widget_input.columnCount()):
                try:
                    target_table.setItem(i, j, self.widget_input.item(i, j).clone())
                except AttributeError:
                    target_table.setItem(i, j, QTableWidgetItem())
