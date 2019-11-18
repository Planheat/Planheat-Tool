from PyQt5.QtWidgets import QTableWidget


class SourceAvailabilityPostCalculation:

    def __init__(self, table: QTableWidget):
        if isinstance(table, QTableWidget):
            self.table = table
        else:
            self.table = None

    def remove_temperature(self, sources_list: list):
        if self.table is None:
            print("SourceAvailabilityPostCalculation, remove_temperature(). self.table is None")
            return
        for i in range(self.table.rowCount()):
            if self.table.item(i, 0).text() in sources_list:
                self.table.item(i, 2).setText("NA")
        return

    def swap_position(self, i, j):
        if self.table is None:
            print("SourceAvailabilityPostCalculation, swap_position(). self.table is None")
            return
        if i >= self.table.rowCount() or j >= self.table.rowCount():
            print("SourceAvailabilityPostCalculation, swap_position(). Not enough rows in self.table:",
                  "self.table.rowCount(), i, j:", self.table.rowCount(), i, j)
            return

        for k in range(self.table.columnCount()):
            item = self.table.item(i, k).clone()
            self.table.setItem(i, k, self.table.item(j, k))
            self.table.setItem(j, k, item)

    def set_new_text(self):
        self.table.item(0, 2).setText("T>70 °C")
        self.table.item(1, 2).setText("15 °C<T<30 °C")
        self.table.item(2, 2).setText("15 °C<T<30 °C")
        self.table.item(3, 2).setText("---")
        self.table.item(4, 2).setText("T>70 °C")
        self.table.item(5, 2).setText("30 °C<T<70 °C")
        self.table.item(6, 2).setText("30 °C<T<70 °C")
        self.table.item(7, 2).setText("30 °C<T<70 °C")
        self.table.item(8, 2).setText("15 °C<T<30 °C")
        self.table.item(9, 2).setText("15 °C<T<30 °C")
        self.table.item(10, 2).setText("15 °C<T<30 °C")
        self.table.item(11, 2).setText("15 °C<T<30 °C")
        self.table.item(12, 2).setText("T<30 °C")
        self.table.item(13, 2).setText("T<30 °C")
        self.table.item(14, 2).setText("T<30 °C")
        self.table.item(15, 2).setText("T<30 °C")
        self.table.item(16, 2).setText("T<15 °C")
        self.table.item(17, 2).setText("---")
        self.table.item(18, 2).setText("---")




