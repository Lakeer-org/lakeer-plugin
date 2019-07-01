# -*- coding: utf-8 -*-
"""
/***************************************************************************
 lakeer_plugin
                                 A QGIS plugin
 lakeer plugin to import/export data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-03-06
        copyright            : (C) 2019 by lakeer
        email                : amar.kamthe@soft-corner.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load lakeer_plugin class from file lakeer_plugin.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    # import pip
    # pip.main(['install', 'geomet==0.2.0.post2'])
    # pip.main(['install', 'pymongo==3.8.0'])
    from .lakeer import lakeer_plugin
    return lakeer_plugin(iface)
