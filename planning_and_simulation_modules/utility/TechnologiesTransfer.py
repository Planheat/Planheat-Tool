from PyQt5.QtWidgets import QTreeWidget


class TechnologiesTransfer:

    def __init__(self, widget_input: QTreeWidget):
        if widget_input is None:
            print("TechologiesTransfer.__init__(): some inputs are None")
        self.widget_input = widget_input
        self.widget_output = None

    def tree_widget_transfer(self, widget_output: QTreeWidget):
        self.widget_output = widget_output
        if self.widget_input is None or self.widget_output is None:
            print("TechologiesTransfer.transfer(): some inputs are None. Transfer aborted")
            return

        self.widget_output.clear()
        for i in range(self.widget_input.topLevelItemCount()):
            self.widget_output.insertTopLevelItem(i, self.widget_input.topLevelItem(i).clone())
