# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PLANHEAT
                                 A QGIS plugin
 PLANHEAT
                             -------------------
        begin                : 2017-07-20
        copyright            : (C) 2017 by VITO
        email                : lorenz.hambsch@vito.be
        git sha              : $Format:%H$
 ***************************************************************************/
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PLANHEAT class from file PLANHEAT.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .PLANHEAT import PLANHEAT
    return PLANHEAT(iface)
