# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanHeat 
                             -------------------
        begin                : 2019-04-25
        copyright            : (C) 2019 by PlanHeat consortium
        email                : stefano.barberis@rina.org
        git sha              : $Format:%H$
 ***************************************************************************/


 This script initializes the plugin, making it known to QGIS.
"""
import os
from . import config

# Set up appdata working directory
working_path = os.path.join(os.environ["LOCALAPPDATA"], "QGIS")
if not os.path.exists(working_path):
    os.mkdir(working_path)
working_path = os.path.join(working_path, "QGIS3")
if not os.path.exists(working_path):
    os.mkdir(working_path)
working_path = os.path.join(working_path, config.WORKING_DIRECTORY_NAME)
if not os.path.exists(working_path):
    os.mkdir(working_path)
working_path = os.path.join(working_path, config.TEMP_WORKING_DIRECTORY_NAME)
if not os.path.exists(working_path):
    os.mkdir(working_path)




# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PlanHeat class from file PlanHeat.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .planheat import PlanHeat
    return PlanHeat(iface)
