# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanheatMappingPlugin
                                 A QGIS plugin
 A mapping plugin
                             -------------------
        begin                : 2018-03-07
        copyright            : (C) 2018 by Salvatore Ferraro - RINA
        email                : salvatore.ferraro@rina.org
        git sha              : $Format:%H$
 ***************************************************************************/

"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PlanheatMappingPlugin class from file PlanheatMappingPlugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .PlanheatMappingPlugin import PlanheatMappingPlugin
    return PlanheatMappingPlugin(iface)
