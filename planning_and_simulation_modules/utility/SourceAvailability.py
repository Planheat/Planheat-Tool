# import some modules used in the example
from qgis.core import *
from PyQt5 import QtCore
from ..layer_utils import raster_shapefile_intersection_integral
from .safe_dict_get import get_data
from .. import master_planning_config as config
import os.path
import pandas
import traceback


class SourceAvailability(QtCore.QObject):

    txt = ""
    day_per_month = {}
    h8760 = 8760
    h24 = 24
    pbar_Download = None
    dialog_source = None
    cancel = False
    cancel_button = None

    def __init__(self):
        QtCore.QObject.__init__(self)

    def get_empty_source_availability_dict(self):
        sources_availability = {}
        for source in self.dialog_source.sources:
            sources_availability[source] = [0.0 for i in range(self.h8760)]
        return sources_availability

    def start_end_month(self, month):
        if month is None:
            return [1, 0]
        try:
            month = int(month)
        except ValueError:
            return [1, 0]
        if month < 1 or month > 12:
            return [1, 0]
        total_max = 0
        for i in range(month):
            for month_length in self.day_per_month.keys():
                if i+1 in self.day_per_month[month_length]:
                    total_min = total_max
                    total_max = total_max + month_length*self.h24
        # the interval is of kind [), first hour of year is 0
        return [total_min, total_max]

    def span_integral(self, sources_availability, source, integral, suffix, coeff=1.0):
        if suffix == "":
            # print("integral", integral)
            integral = (integral/self.h8760)/coeff
            for i in range(len(sources_availability[source])):
                sources_availability[source][i] += integral
        else:
            try:
                suffix = int(suffix)
            except ValueError:
                print("Step0, span_integral, suffix is not an int: suffix", suffix)
                return sources_availability
            for month_length in self.day_per_month.keys():
                print("month_length", month_length)
                if int(suffix) in self.day_per_month[month_length]:
                    integral = integral/(month_length*self.h24)
                    start, end = self.start_end_month(suffix)
                    for i in range(start, end):
                        sources_availability[source][i] += integral
                    break
            else:
                print("SourceAvailability.py, span_integral, strange things are happening. suffix: ", suffix)
        return sources_availability

    def get_source_availability_from_rasters(self, layer=None, sources_availability=None):
        points = None
        if sources_availability is None:
            sources_availability = self.get_empty_source_availability_dict()
        # layer is the layer shapefile to intersect with the rasters files
        u = 0
        for mapped_source in self.dialog_source.mapped_sources:
            # if source has monthly values and is a shapefile, ignore it
            if self.dialog_source.monthly_temperature[mapped_source] and self.dialog_source.is_shapefile[mapped_source]:
                continue
            print("Calculating source availability for: ", mapped_source)
            if self.dialog_source.monthly_temperature[mapped_source]:
                suffixs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
            else:
                suffixs = [""]
            for suffix in suffixs:
                print("SourceAvailability.py, get_source_availability_from_rasters. mapped_source, month:",
                      mapped_source, suffix)
                self.pbar_Download.setValue(self.pbar_Download.value() + 1)
                for key in QgsProject.instance().mapLayers().keys():
                    raster_layer = QgsProject.instance().mapLayers()[key]
                    # print("Checking:", self.dialog_source.file_name_mapping[mapped_source], "in", raster_layer.name())
                    if self.dialog_source.file_name_mapping[mapped_source]+suffix in raster_layer.name():
                        # print("FOUND!")
                        # print("Intersection of ", key, layer.name())
                        integral, points = raster_shapefile_intersection_integral(layer, raster_layer, points)
                        print("integral", integral)
                        sources_availability = self.span_integral(sources_availability,
                                                                  self.dialog_source.MM_to_DPM_sources_dict[mapped_source],
                                                                  integral[0], suffix)
                        # sources_availability[self.dialog_source.MM_to_DPM_sources_dict[mapped_source]] += integral[0]
                        # print("sources_availability", sources_availability)
                        break
        return sources_availability

    def get_source_availability_from_csv(self, sources_availability=None):
        if sources_availability is None:
            sources_availability = self.get_empty_source_availability_dict()

        # Read config excel sources file
        config_sources_file = os.path.join(os.path.dirname(__file__), "../", "config", "sources", "Csv_SMM.xlsm")
        try:
            config_sources_data_frame = pandas.read_excel(config_sources_file)
        except Exception:
            print("Source availability: errors with file:", config_sources_file)
            return sources_availability

        # Read the SMM csv sources availability
        supply_csv = os.path.join(config.CURRENT_MAPPING_DIRECTORY, "SMM", "planheat_result_2.csv")
        try:
            data_frame = pandas.read_csv(supply_csv, sep="\t")
        except Exception:
            print("Source availability: errors with file:", supply_csv)
            return sources_availability

        # compute availability
        for i, row in data_frame.iterrows():
            smm_source = row["Class"] + row["Description"]
            for j, source in config_sources_data_frame.iterrows():
                try:
                    config_source = source["Class"]+source["Description"]
                    if smm_source == config_source:
                        dpm_source = source["planning_module_related_source"]
                        inside_availability = self.sum_row(row, 3)
                        sources_availability = self.span_integral(sources_availability,
                                                                  dpm_source, inside_availability, "", coeff=1000.0)
                        break
                except Exception:
                    continue
        return sources_availability

    def sum_row(self, row, start=0, ends=None):
        if ends is None:
            ends = len(row)
        total = 0.0
        try:
            for i in range(start, ends):
                if row[i] == row[i]:
                    total += row[i]
        except Exception:
            print("SourceAvailability.sum_row error at index", i)
            return total
        return total

    def update_source_availability_from_shapefile(self, sources_availability, mapped_source, layer, attribute):
        self.pbar_Download.setValue(self.pbar_Download.value() + 12)
        for feature in layer.getFeatures():
            try:
                values = [float(x) for x in feature.atribute(attribute).replace(" ", "").split(";")]
            except ValueError:
                continue
            if not len(values) == 12:
                continue
            for i in range(len(values)):
                print("SourceAvailability.py, update_source_availability_from_shapefile. mapped_source, feature, month:",
                      mapped_source, feature.id(), i)
                start, end = self.start_end_month(i+1)
                if start < 0:
                    continue
                try:
                    contribution = values[i]/(end-start)
                except ZeroDivisionError:
                    contribution = 0.0
                for j in range(start, end):
                    sources_availability[self.dialog_source.MM_to_DPM_sources_dict[mapped_source]] += contribution
        return sources_availability

    def find_layer(self, mapped_source):
        for key in QgsProject.instance().mapLayers().keys():
            layer = QgsProject.instance().mapLayers()[key]
            look_for = self.dialog_source.file_name_mapping[mapped_source]
            if look_for[0:-1] + "_inputdata" in layer.name():
                try:
                    g = layer.geometryType()
                except AttributeError:
                    g = -1
                if g == 0:
                    return layer
        return None

    def get_sources_availability_from_shapefiles(self, sources_availability=None):
        if sources_availability is None:
            sources_availability = self.get_empty_source_availability_dict()
        # self.mapped_sources[12]: "Excess heat mapped_sources-Data centers (Medium)-",
        # self.mapped_sources[13]: "Excess heat mapped_sources-Supermarkets (Medium)-",
        # self.mapped_sources[14]: "Excess heat mapped_sources-Refrigerated storage facilities (Medium)-",
        # self.mapped_sources[15]: "Excess heat mapped_sources-Indoor carparkings (Low)-",
        # self.mapped_sources[16]: "Excess heat mapped_sources-Subway networks (Low)-",
        group1 = [self.dialog_source.mapped_sources[12], self.dialog_source.mapped_sources[13],
                  self.dialog_source.mapped_sources[14], self.dialog_source.mapped_sources[15],
                  self.dialog_source.mapped_sources[16], self.dialog_source.mapped_sources[18]]
        for mapped_source in self.dialog_source.mapped_sources:
            if self.dialog_source.is_shapefile[mapped_source] and self.dialog_source.monthly_temperature[mapped_source]:
                if mapped_source in group1:
                    layer = self.find_layer(mapped_source)
                    if layer is not None:
                        sources_availability = self.update_source_availability_from_shapefile(sources_availability,
                                                                                              mapped_source, layer, 12)
        return sources_availability

    def fill_layers_combobox(self, a):
        self.comboLayer.clear()
        combo_list = []
        for key in QgsProject.instance().mapLayers().keys():
            if type(QgsProject.instance().mapLayers()[key]) == type(QgsVectorLayer()):
                if QgsProject.instance().mapLayers()[key].geometryType() == 2:
                    if not QgsProject.instance().mapLayers()[key].name() in combo_list:
                        combo_list.append(QgsProject.instance().mapLayers()[key].name())
        self.comboLayer.insertItems(0, combo_list)
        # Master integration
        for i in range(self.comboLayer.count()):
            name = self.comboLayer.itemText(i)
            if mp_config.BUILDING_SHAPE.lower().startswith(name.lower()):
                self.comboLayer.setCurrentText(name)

    def source_availability(self):
        # txt = self.txt
        # layers = QgsProject.instance().mapLayersByName(txt)
        # if len(layers) > 0:
        self.pbar_Download.setMinimum(0)
        self.pbar_Download.setValue(0)
        max_val = 0
        for mapped_source in self.dialog_source.mapped_sources:
            if self.dialog_source.monthly_temperature[mapped_source]:
                max_val += 12
            else:
                max_val += 1
        self.pbar_Download.setMaximum(max_val)
        self.pbar_Download.show()

        # sources_availability = self.get_source_availability_from_rasters(layers[0])
        sources_availability = self.get_source_availability_from_csv()

        sources_availability = self.get_sources_availability_from_shapefiles(sources_availability)

        self.pbar_Download.setValue(self.pbar_Download.maximum())
        self.pbar_Download.hide()
        # self.cancel.hide()

        return sources_availability


    def sources_temperature(self):
        for mapped_source in self.dialog_source.mapped_sources:
            pass



