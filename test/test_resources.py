# coding=utf-8
"""Resources test.
"""

__author__ = 'stefano.barberis@rina.org'
__date__ = '2019-04-25'
__copyright__ = 'Copyright 2019, PlanHeat consortium'

import unittest

from PyQt5.QtGui import QIcon



class PlanHeatDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Test we can click OK."""
        path = ':/plugins/planheat/ui/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

if __name__ == "__main__":
    suite = unittest.makeSuite(PlanHeatResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)



