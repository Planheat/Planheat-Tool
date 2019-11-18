
from PyQt5.QtWidgets import *
from PyQt5.QtCore  import *


class Form(QWidget):
    InputDemand = pyqtSignal(float, float, str)
    futureInputDemand = pyqtSignal(float, float, str)

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)


        nameLabel = QLabel("Peak demand:")
        self.nameLine = QLineEdit()

        range = QLabel("range:")
        self.range = QLineEdit()


        self.submitButton = QPushButton("Submit")

        buttonLayout1 = QVBoxLayout()
        buttonLayout1.addWidget(nameLabel)
        buttonLayout1.addWidget(self.nameLine)

        buttonLayout2 = QVBoxLayout()
        buttonLayout2.addWidget(range)
        buttonLayout2.addWidget(self.range)

        buttonLayout1.addWidget(self.submitButton)
        buttonLayout2.addWidget(self.submitButton)

        self.submitButton.clicked.connect(self.submitContact)

        mainLayout = QGridLayout()
        mainLayout.addLayout(buttonLayout1, 0, 1)
        mainLayout.addLayout(buttonLayout2, 0, 2)

        self.setLayout(mainLayout)
        self.setWindowTitle(" Demand")
        self.attribute_column_name = ""



    def submitContact(self):

        demand = self.nameLine.text()
        range = self.range.text()
        try:
            demand2 = float(demand)
            range2 = float(range)
            self.InputDemand.emit(demand2, range2, self.attribute_column_name)
            self.hide()
        except:
            QMessageBox.information(self, "Empty Field", "Please enter a peak demand and range ")








