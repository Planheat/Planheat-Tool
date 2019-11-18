from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtCore, QtGui, QtWidgets

import sys


class ImgWidget(QLabel):
      def __init__(self, parent=None):
        super(ImgWidget, self).__init__(parent)
        imgPath = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_and_simulation_modules\\city\\naturalGas.png"
        pic= QPixmap(imgPath)
        self.setPixmap(pic)

        #imgPath = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_and_simulation_modules\\city\\naturalGas.png"



