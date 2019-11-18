# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanHeatDialog
 This file defines the Planheat tool main dialog.
                             -------------------
        begin                : 2019-04-25
        git sha              : $Format:%H$
        copyright            : (C) 2019 by PlanHeat consortium
        email                : stefano.barberis@rina.org
 ***************************************************************************/
"""

import os

from PyQt5 import uic
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'planheat_dialog_base.ui'), resource_suffix='',
    import_from="planheat.ui",
    from_imports=True)


class PlanHeatDialog(QtWidgets.QDialog, FORM_CLASS):
    closeMapping = pyqtSignal()
    closePlanning = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(PlanHeatDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        file_dir_path = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(file_dir_path, "icon.png")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setWindowTitle('PLANHEAT')
