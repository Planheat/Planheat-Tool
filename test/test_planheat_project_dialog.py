# coding=utf-8
"""Dialog test.
"""

__author__ = 'stefano.barberis@rina.org'
__date__ = '2019-04-25'
__copyright__ = 'Copyright 2019, PlanHeat consortium'

import unittest

from PyQt5.QtGui import QDialogButtonBox, QDialog

from ui.planheat_dialog import PlanHeatDialog

from utilities import get_qgis_app
QGIS_APP = get_qgis_app()


class PlanHeatDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = PlanHeatDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""

        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)

    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)

if __name__ == "__main__":
    suite = unittest.makeSuite(PlanHeatDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

