# -*- coding: utf-8 -*-

import os
import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from qgis.gui import QgsDockWidget
sys.path.append(os.path.dirname(__file__))
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dhcoptimizer_planheat_dock_panel_base.ui'), resource_suffix='')

FONT_PIXEL_SIZE = 12

class DHCOptimizerPlanheatDock(QgsDockWidget , FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(DHCOptimizerPlanheatDock, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "gearing.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.compute_button.setIcon(icon)
        self.pipe_size_calculation_button.setIcon(icon)
        self.only_preprocess_button.setIcon(icon)
        self.set_system_dependant_font_size()

    def set_system_dependant_font_size(self):
        font = self.font()
        font.setPixelSize(FONT_PIXEL_SIZE)
        self.setFont(font)
        self.dialoglabels = self.findChildren(QtWidgets.QLabel)
        for label in self.dialoglabels:
            label.setFont(font)