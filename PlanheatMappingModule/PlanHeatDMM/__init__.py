# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanHeatDMM
                                 A QGIS plugin
 PlanHeatDMM
                             -------------------
        begin                : 2017-10-03
        copyright            : (C) 2017 by Sergio Aparicio Vegas
        email                : sapariciovegas@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/
"""


try:
    import sys
    import os
    try:
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    except:
        pass    
    # Add the path for avoid the problems with relative imports vs absolute imports
    sys.path.append(os.path.dirname(__file__))
    import site
    import importlib
    importlib.reload(site)
except ImportError:
    pass

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PlanHeatDMM class from file PlanHeatDMM.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .PlanHeatDMM import PlanHeatDMM
    return PlanHeatDMM(iface)
