# -*- coding: utf-8 -*-
"""
/***************************************************************************
 shapeCreator
                                 A QGIS plugin
 ***************************************************************************/
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import QColor
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsPointXY, QgsWkbTypes
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand

# Initialize Qt resources from file resources.py

rubber_band = None
active = False


class ShapeCreator:
    def select(self):
        def end_selection():
            canvas.setMapTool(self.previous_map_tool)
            self.myMapTool.canvasClicked.disconnect()
            global active
            active = False
            global rubber_band
            canvas.scene().removeItem(rubber_band)
            rubber_band = None
            self.actions[1].setChecked(False)

        def draw_band(current_pos, clicked_button):
            canvas.xyCoordinates.connect(draw_band)
            if rubber_band and rubber_band.numberOfVertices():
                rubber_band.removeLastPoint()
                rubber_band.addPoint(current_pos)

        def mouse_click(current_pos, clicked_button):
            global rubber_band
            if clicked_button == Qt.LeftButton and rubber_band is None:
                create_rubber_band()
                rubber_band.addPoint(QgsPointXY(current_pos))

            if clicked_button == Qt.LeftButton and rubber_band:
                rubber_band.addPoint(QgsPointXY(current_pos))

            if clicked_button == Qt.RightButton and rubber_band:
                poly = QgsFeature()
                geometry = rubber_band.asGeometry()
                poly.setGeometry(geometry)
                data_provider.addFeatures([poly])
                layer.updateExtents()
                canvas.refresh()
                QgsProject.instance().addMapLayers([layer])
                end_selection()
            if clicked_button == Qt.RightButton and rubber_band is None and active:
                end_selection()

        def create_rubber_band():
            global rubber_band
            rubber_band = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
            color = QColor(78, 97, 114)
            color.setAlpha(190)
            rubber_band.setColor(color)

        global active
        canvas = self.iface.mapCanvas()

        if active:
            end_selection()
        else:
            active = True
            self.actions[1].setChecked(True)
            global layer
            rubber_band = None
            crs = ""
            if self.dockwidget:
                base_file = self.dockwidget.baseMapFile.text()
                crs = "?crs=" + QgsVectorLayer(base_file).sourceCrs().toWkt()
            elif self.iface.activeLayer() and self.iface.activeLayer().name() != "OSM":
                crs = "?crs=" + self.iface.activeLayer().crs().toWkt()
            else:
                srs = QgsProject.instance().defaultCrsForNewLayers()
                crs = "?crs=" + srs.toWkt()

            layer = QgsVectorLayer("Polygon" + crs, "selection layer", "memory")
            layer.setOpacity(0.5)
            data_provider = layer.dataProvider()
            self.previous_map_tool = canvas.mapTool()
            self.myMapTool = QgsMapToolEmitPoint(canvas)
            self.myMapTool.canvasClicked.connect(mouse_click)
            canvas.setMapTool(self.myMapTool)

