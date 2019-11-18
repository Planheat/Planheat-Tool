# -*- coding: utf-8 -*-
"""
/***************************************************************************
 shapeCreator
                                 A QGIS plugin
 shapeCreator
                             -------------------
        begin                : 2017-10-17
        copyright            : (C) 2017 by a
        email                : a
        git sha              : $Format:%H$
 ***************************************************************************/
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load shapeCreator class from file shapeCreator.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .shapeCreator import shapeCreator
    return shapeCreator(iface)
