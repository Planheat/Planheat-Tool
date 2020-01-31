import sys
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton, QLabel)

TIME_LIMIT = 100

"""
class External(QThread):
    countChanged = pyqtSignal(int)

    def run(self):
        count = 0
        while count < TIME_LIMIT:
            count += 1
            time.sleep(1)
            self.countChanged.emit(count)
"""

class Actions(QDialog):
    """
    Simple dialog that consists of a Progress Bar and a Button.
    Clicking on the button results in the start of a timer and
    updates the progress bar.
    """

    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Progress Bar')
        self.progress = QProgressBar(self)
        self.label_top = QLabel(self)
        self.label_top.setGeometry(0, 0, 300, 20)
        self.progress.setGeometry(0, 20, 300, 25)
        self.label_bottom = QLabel(self)
        self.label_bottom.setGeometry(0, 40, 300, 20)
        self.progress.setMaximum(100)
        # self.button = QPushButton('Start', self)
        # self.button.move(0, 30)

    def set_value(self, value):
        self.progress.setValue(value)

    @pyqtSlot(name="_add_progress")
    def add_progress(self, value):
        self.set_value(self.progress.value() + value)

    def set_label_top(self, text):
        if isinstance(text, str):
            self.label_top.setText(text)

    def set_label_bottom(self, text):
        if isinstance(text, str):
            self.label_top.setText(text)

    def get_progress(self):
        return self.progress.value()

    def set_maximum_progress(self, value):
        self.progess.setMaximum(value)

    @pyqtSlot(name="_start")
    def start(self):
        print("progress bar started in thread:", int(QThread.currentThreadId()))
        raise RuntimeError
        self.exec()

    @pyqtSlot(name="_stop")
    def stop(self):
        # self.done(200)
        # self.finished.emit()
        raise RuntimeError
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Actions()
    sys.exit(app.exec_())





