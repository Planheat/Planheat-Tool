# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanheatIntegration
                                 A QGIS plugin
 planheat integration
                             -------------------
        begin                : 2017-12-06
        copyright            : (C) 2017 by v
        email                : v
        git sha              : $Format:%H$
 ***************************************************************************/
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PlanheatIntegration class from file PlanheatIntegration.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .planheat_integration import PlanheatIntegration
    return PlanheatIntegration(iface)
