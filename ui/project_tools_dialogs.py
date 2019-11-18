# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Projects tools dialogs
 This file defines the scenario handling Dialogs.
                             -------------------
        begin                : 2019-04-25
        git sha              : $Format:%H$
        copyright            : (C) 2019 by PlanHeat consortium
        email                : stefano.barberis@rina.org
 ***************************************************************************/
"""

import os

from PyQt5 import uic
from PyQt5 import QtWidgets

# === Create tool ===

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'project_create_dialog.ui'), resource_suffix='',
    import_from="planheat.ui",
    from_imports=True)


class ProjectCreateDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ProjectCreateDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


# === Duplicate tool ===

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'project_duplicate_dialog.ui'), resource_suffix='',
    import_from="planheat.ui",
    from_imports=True)


class ProjectDuplicateDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ProjectDuplicateDialog, self).__init__(parent)
        self.setupUi(self)


# === Delete tool ===

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'project_delete_dialog.ui'), resource_suffix='',
    import_from="planheat.ui",
    from_imports=True)


class ProjectDeleteDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ProjectDeleteDialog, self).__init__(parent)
        self.setupUi(self)