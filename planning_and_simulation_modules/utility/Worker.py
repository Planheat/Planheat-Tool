from PyQt5.QtCore import QObject, QThread, pyqtSignal
from QtCore import pyqtSlot


class Worker(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    def __init__(self, message):
        super(Worker, self).__init__()
        self.message = message
        self.main_thread = None
    def process(self):
        i = 0
        cicle = 10000
        j = 0
        while j < 5:
            i = i + 1
            if i % cicle == 0:
                j = float(i/cicle)
                print(self.message, j)
        print(self.message, int(QThread.currentThread().currentThreadId()), "\n")
        self.message = self.message + " done"
        self.finished.emit()

worker1 = Worker("Worker 1:")
worker1.main_thread = QThread.currentThread()
thread1 = QThread()
worker1.moveToThread(thread1)
thread1.started.connect(worker1.process)
worker1.finished.connect(thread1.quit)
# worker1.finished.connect(worker1.deleteLater)
thread1.finished.connect(thread1.deleteLater)
worker2 = Worker("Worker 2:")
worker2.main_thread = QThread.currentThread()
thread2 = QThread()
worker2.moveToThread(thread2)
thread2.started.connect(worker2.process)
worker2.finished.connect(thread2.quit)
# worker2.finished.connect(worker2.deleteLater)
thread2.finished.connect(thread2.deleteLater)
print("Main app:", int(QThread.currentThread().currentThreadId()))

thread2.start()
thread1.start()


print("Threads started!")
print("Threads started!")

