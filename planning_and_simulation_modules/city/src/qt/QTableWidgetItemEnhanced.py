from PyQt5.QtWidgets import QTableWidgetItem


class QTableWidgetItemEnhanced(QTableWidgetItem):

    def __init__(self, item: QTableWidgetItem | str):
        if item is None:
            QTableWidgetItem.__init__()
        else:
            QTableWidgetItem.__init__(item)

    def auto_add_percent_symbol(self):
        pass

    def add_percent_symbol(self):
        if self.auto_add_percent_symbol:
            atext = self.text() + " %"
            self.setText(atext)