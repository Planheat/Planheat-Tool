from PyQt5.QtCore import QObject, QThread, pyqtSignal
import requests
import traceback


class PvgisApiWorker(QObject):

    started: pyqtSignal = pyqtSignal()
    finished: pyqtSignal = pyqtSignal(dict)

    def __init__(self, url: str, dr: str):
        super(PvgisApiWorker, self).__init__()
        self.url = url
        self.dr = dr

    def process(self):
        print("PvgisApiWorker DONE!!!")
        self.finished.emit({})

