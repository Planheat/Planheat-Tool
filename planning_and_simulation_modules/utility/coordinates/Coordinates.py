from numpy import cos, sin, arcsin, sqrt
from math import radians
from ...Tjulia.test.MyLog import MyLog
from qgis.core import QgsCoordinateTransform
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsProject
import traceback


class Coordinates:

    def __init__(self):
        pass

    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """
        :param lon1: longitudine point 1
        :param lat1: latitudine point 1
        :param lon2: longitudine point 1
        :param lat2: latitudine point 2
        :return: approximate distance in m
        """
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * arcsin(sqrt(a))
        km = 6367 * c
        return km*1000

    @staticmethod
    def haversine_line_length(feature):
        try:
            multi_poly_line = feature.geometry().asMultiPolyline()
            total_distance = 0
            for line in multi_poly_line:
                for i in range(len(line)-1):
                    distance = Coordinates.haversine(line[i].x(), line[i].y(), line[i+1].x(), line[i+1].y())
                    total_distance += distance
            return total_distance
        except Exception:
            log = MyLog(None, "Coordinates_EXCEPIONS", keep_file=True)
            log.log("ERROR", traceback.format_exc())
            return 0.0

    @staticmethod
    def convert_to_EPSG4326(qgs_coordinate_reference_system, geom_as_point):
        transform = QgsCoordinateTransform(qgs_coordinate_reference_system,
                                           QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())

        new_point = transform.transform(geom_as_point)
        return [new_point.x(), new_point.y()]

        # l = iface.activeLayer()
        # p = l.getFeature(0).geometry().centroid().asPoint()
        # t = QgsCoordinateTransform(l.crs(), QgsCoordinateReferenceSystem("EPSG:4326"), QgsProject.instance())
        # new_p = t.transform(p)
