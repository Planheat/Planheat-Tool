import traceback

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QThread
from PyQt5.QtWidgets import QProgressBar, QDialog

from .SimulationDetailsGUI import SimulationDetailsGUI


class SimulationDetailsWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, iface):
        self.iface = iface
        super().__init__()

    def run(self):
        try:
            print("Thread started:", int(QThread.currentThread().currentThreadId()))
            self.gui = SimulationDetailsGUI(parent=self.iface.mainWindow())
            r = self.gui.open()
            self.gui.deleteLater()
            print("THREAD FINISHED")
            self.finished.emit()
        except:
            traceback.print_exc()
            print("THREAD ERROR")
            self.gui.deleteLater()
            self.finished.emit()

    @pyqtSlot(int, str, str)
    def update_state(self, progress=None, label_text=None, text_browser=None):
        if self.gui is None:
            return
        if label_text is not None:
            self.gui.label_description.setText(label_text)

class Actions(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Progress Bar')
        #self.button = QPushButton("Click")
        #self.button.setGeometry(0, 40, 300, 25)
        #self.button.clicked.connect(self.push_button)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(0, 20, 300, 25)
        self.progress.setMaximum(100)