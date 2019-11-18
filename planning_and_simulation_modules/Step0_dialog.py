import os
import os.path
import csv
import pickle
import processing
import geopandas as gpd
import osmnx as ox
from PyQt5 import uic, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QVariant
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtWidgets import QMessageBox
from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsRasterLayer, 
                    QgsFeature, QgsVertexId, QgsMultiPoint, QgsGeometry, QgsCoordinateTransform)
from .Step3_docwidget import Step3_widget
# from dialogs.message_box import showErrordialog
from .dhcoptimizerplanheat.streets_downloader import streetsDownloader
from .layer_utils import load_file_as_layer, load_open_street_maps, save_layer_to_shapefile
from .dialogSources import CheckSourceDialog
from .utility.SourceAvailability import SourceAvailability
from .utility.SourceAvailabilityPostCalculation import SourceAvailabilityPostCalculation
from .utility.data_manager.DataTransfer import DataTransfer
from .city.src.FileManager import FileManager
from . import master_planning_config as mp_config


FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui', 'Step0dockwidget.ui'))


class Step0Dialog(QtWidgets.QDockWidget, FORM_CLASS):

    district_shp_loaded = pyqtSignal()
    buildings_shp_loaded = pyqtSignal()
    buildings_shp_loaded2 = pyqtSignal()
    step0_closing_signal = pyqtSignal()
    file_removed = pyqtSignal()
    send_data_to_step2 = pyqtSignal(dict, dict)
    buildings_shp_loaded_step1signal = pyqtSignal(QgsVectorLayer)
    buildings_shp_loaded_step4signal = pyqtSignal(QgsVectorLayer)
    step0_all_import_complete = pyqtSignal(QgsVectorLayer, DataTransfer)
   # csv_loaded = pyqtSignal(QTableWidget)
    send_tab_sources = pyqtSignal(QTableWidget)

    h8760 = 8760
    h24 = 24
    day_per_month = {28: [2], 30: [11, 4, 6, 9], 31: [1, 3, 5, 7, 8, 10, 12]}




    def __init__(self, iface, parent=None, work_folder=None):
        """Constructor."""
        super(Step0Dialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.work_folder = work_folder

        self.listWidget.hide()

        self.iface = iface
        self.district_shp_loaded.connect(self.fill_district_menu)
        self.buildings_shp_loaded.connect(self.fill_buildings_table)
        self.buildings_shp_loaded2.connect(self.fill_buildings_table_future)
        self.listWidget.itemChanged.connect(self.list_district_select)
        QgsProject.instance().layersAdded.connect(self.fill_layers_combobox)
        QgsProject.instance().layerWasAdded.connect(self.fill_layers_combobox)
        QgsProject.instance().layerRemoved.connect(self.fill_layers_combobox)
        self.btnSourcesAvailability.clicked.connect(self.source_availability)
        #self.pushButton_4.clicked.connect(self.download_streets_from_comboBox_selection)
        self.delete_file.clicked.connect(self.delete_import_file)
        self.ok2.clicked.connect(self.send_tab_to_stap3)
        self.baseline_scenario_layer = None
        self.phases.setTabEnabled(0, False)
        self.phases.setTabEnabled(2, False)
        self.all_import_completed = True

        self.geo_graph = None
        self.data_transfer = DataTransfer()
        self.data_transfer.geo_graph = self.geo_graph
        self.data_transfer.buildings = self.baseline_scenario_layer

        # QgsProject.layerRemoved.connect(self.update_source_combobox)
        # QgsProject.layerWasAdded.connect(self.update_source_combobox)

        self.dialog_source = CheckSourceDialog()

        self.fill_layers_combobox(1)
        self.pbar_Download.hide()
        self.label_3.setEnabled(False)
        self.label_9.setEnabled(False)
        self.layerPath2.setEnabled(False)
        self.layerPath3.setEnabled(False)
        self.load1.setEnabled(False)
        self.load2.setEnabled(False)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "open_file.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.load.setIcon(icon)
        self.load1.setIcon(icon)
        self.load2.setIcon(icon)
        self.load3.setIcon(icon)
        self.load4.setIcon(icon)
        #self.load_streets.setIcon(icon)
        self.pushButton_5.setIcon(icon)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "untitled.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.delete_file.setIcon(icon)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "save_as.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.save_plugin.setIcon(icon)

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons",
                                 "import.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.pushButton_load_all_files.setIcon(icon)

        self.combo_box_layer = None
        self.future_scenario_layer = None

        default_root = mp_config.CURRENT_MAPPING_DIRECTORY
        self.layerPath.setEnabled(False)#setDefaultRoot(default_root)
        self.layerPath.lineEdit().setText(os.path.join(default_root, "DMM", 
                                                    mp_config.DMM_PREFIX+".shp"))
        self.layerPath1.setEnabled(False)#.setDefaultRoot(default_root)
        self.layerPath1.lineEdit().setText(os.path.join(default_root, "DMM", 
                        mp_config.DMM_PREFIX+mp_config.DMM_FUTURE_SUFFIX+".shp"))
        self.layerPath2.setEnabled(False)#.setDefaultRoot(default_root)
        self.layerPath2.lineEdit().setText(os.path.join(default_root, "DMM", 
                                                    mp_config.DMM_PREFIX+".scn"))
        self.layerPath3.setEnabled(False)#.setDefaultRoot(default_root)
        self.layerPath3.lineEdit().setText(os.path.join(default_root, "DMM", 
                mp_config.DMM_PREFIX+mp_config.DMM_FUTURE_SUFFIX+mp_config.DMM_HOURLY_SUFFIX+".csv"))
        #self.layerPath_streets.setDefaultRoot(os.path.expanduser("~"))
        self.folder.setEnabled(False)
        self.btnSmm.setEnabled(False)
        self.folder.setText(os.path.join(default_root, "SMM"))

        self.cancel.hide()
        self.pushButton_2.hide()
        self.pushButton.hide()
        self.pushButton_3.hide()



    def load_all_files_from_folder(self):
        folder = self.folder.text()
        if not os.path.exists(folder):
            QMessageBox.warning(None, "Warning", "Folder " + folder + " does not exist")
            return
        # Counting number of files to be open in the selected folder
        file_counter = 0
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith('.tif') or file.endswith('.shp'):
                    file_counter += 1
        if file_counter==0:
            QMessageBox.information(None, "Warning", "Folder " + folder + " does not contain .tif or .shp files. There's nothing to load, here!")
            return
        # setting progress bar
        self.progressBar.setMaximum(file_counter)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.progressBar.show()
        progress = 0
        # loading all .tif and .shp files. Files already loaded are ignored.
        for root, dirs, files in os.walk(folder):
            for filename in files:
                if filename[-4:] == ".shp":
                    progress = progress + 1
                    file_path = folder + "\\" + filename
                    if not QgsProject.instance().mapLayersByName(filename):
                        load_file_as_layer(file_path, filename, 'Shapefiles from SMM', min_val=None,
                                           max_val=None, mean_val=None, value_color=None, area=None)
                    else:
                        print("File " + file_path + "seems to be already loaded! Skipping file...")
                if filename[-4:] == ".tif":
                    progress = progress + 1
                    file_path = folder + "\\" + filename
                    if not QgsProject.instance().mapLayersByName(filename):
                        load_file_as_layer(file_path, filename, 'Raster layers from SMM',
                                           min_val=None, max_val=None, mean_val=None, value_color=None, area=None)
                    else:
                        print("File " + file_path + "seems to be already loaded! Skipping file...")
                self.progressBar.setValue(progress)
        load_open_street_maps()
        # emit signal to activate and fill (reload) the district list in the district tab of step0
        self.district_shp_loaded.emit()
        self.progressBar.hide()

        self.get_temperature_from_mapping_module(folder)


    def load_folder(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.folder.setText(folder)

    def load_shp_file4(self):
        print("Downloading baseline scenario ...")
        layer_list = QgsProject.instance().mapLayersByName("baseline scenario")
        if len(layer_list)>0:
            self.baseline_scenario_layer = layer_list[0]
        else:
            layerShp = self.layerPath.filePath()
            self.baseline_scenario_layer = load_file_as_layer(layerShp, 'baseline scenario', None, min_val=None,
                               max_val=None, mean_val=None, value_color=None, area=None)
        self.buildings_shp_loaded.emit()
        self.buildings_shp_loaded_step1signal.emit(self.baseline_scenario_layer)
        print("End downloading baseline scenario")


    def load_shp_file3(self):
        print("Downloading future scenario ...")
        Flayer = self.layerPath1.filePath()
        self.future_scenario_layer= load_file_as_layer(Flayer, 'future scenario', None, min_val=None,
                           max_val=None, mean_val=None, value_color=None, area=None)
        self.buildings_shp_loaded2.emit()
        self.buildings_shp_loaded_step4signal.emit(self.future_scenario_layer)
        print("End downloading future scenario ...")

    def fill_district_menu(self):
        layer_list = QgsProject.instance().mapLayersByName("projection_helper.shp")
        if len(layer_list) > 0:
            layer = layer_list[0]
        else:
            layer = None
        if layer is not None:
            #retrieve district code list and update

            self.listWidget.clear()
            district_code_list = []
            features = layer.getFeatures()
            for feature in features:
                district_code_list.append(feature.attribute(2))

            self.listWidget.addItems(district_code_list)
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setFlags(self.listWidget.item(i).flags() | QtCore.Qt.ItemIsUserCheckable)
                self.listWidget.item(i).setCheckState(QtCore.Qt.Unchecked)

    def add_district_selection(self):
        layer_list = QgsProject.instance().mapLayersByName("projection_helper.shp")
        if len(layer_list) > 0:
            layer = layer_list[0]
        else:
            layer = None
        if layer is not None:
            features = layer.selectedFeatures()
            for i in range(self.listWidget.count()):
                for feature in features:
                    if self.listWidget.item(i).text() == feature.attribute(2):
                        self.listWidget.item(i).setCheckState(QtCore.Qt.Checked)

    def override_district_selection(self):
        # uncheck all the district and add the new selection
        for i in range(self.listWidget.count()):
            self.listWidget.item(i).setCheckState(QtCore.Qt.Unchecked)
        self.add_district_selection()

    def reverse_district_selection(self):
        # check the state of each item and change it
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState():
                self.listWidget.item(i).setCheckState(QtCore.Qt.Unchecked)
            else:
                self.listWidget.item(i).setCheckState(QtCore.Qt.Checked)


    def loadScenario(self):
        fname = self.layerPath2.filePath()
        with open(fname, "rb") as fichero:
            load_data = pickle.load(fichero)
            self.pname.setText(load_data.scenarioName)
            self.pname.show()
            self.label_6.show()
            self.areaStudy.setText(str(load_data.scenarioVersion))
            self.areaStudy.show()
            self.label_7.show()
            self.country.setText(load_data.country)
            self.country.show()
            self.label_8.show()

    def fill_buildings_table(self):
        layer_list = QgsProject.instance().mapLayersByName("baseline scenario")
        if len(layer_list) > 0:
            layer = layer_list[0]
        else:
            layer = None
        if layer is not None:
            features = layer.getFeatures()
            building_item_list = []
            fields = ["BuildingID", "AHeatDem", "AHeatDemM2", "ACoolDem", "ACoolDemM2", "ADHWDem",
                            "ADHWDemM2", "MaxDHWDem", "MaxCoolDem", "MaxDHWDem", "Use", "GrossFA"]
            missing_fields = set()
            for feature in features:
                if len(feature.attributes()) > 13:
                    # Field names
                    # BuildingID AHeatDem AHeatDemM2 ACoolDem ACoolDemM2 ADHWDem ADHWDemDM2 MaxHeatDem MaxCoolDem MaxDHWDem USE, GrossFloor area
                    #string_list = [str(feature.attribute(3)), str(feature.attribute(5)), str(feature.attribute(6)),
                    #               str(feature.attribute(7)), str(feature.attribute(8)), str(feature.attribute(9)),
                    #               str(feature.attribute(10)), str(feature.attribute(11)), str(feature.attribute(12)),
                    #               str(feature.attribute(13)), str(feature.attribute(14)), str(feature.attribute(18))]
                    string_list = []
                    for f in fields:
                        try:
                            string_list.append(str(feature[f]))
                        except:
                            missing_fields.add(f)
                            string_list.append('')
                    building_item_list.append(QTreeWidgetItem(string_list))
                    self.pmTree.addTopLevelItems(building_item_list)
            if len(missing_fields) > 0:
                self.iface.messageBar().pushMessage("Field {0} is missing in ths baseline shape file".format(missing_fields), level=1, duration=0)

    def fill_buildings_table_future(self):
        layer_name = "future scenario"
        layer_list2 = QgsProject.instance().mapLayersByName(layer_name)
        flag = True
        if len(layer_list2) > 0:
            layer2 = layer_list2[0]
        else:
            layer2 = None
        if layer2 is not None:
            features2 = layer2.getFeatures()
            building_item_list2 = []
            fields = ["BuildingID", "AHeatDem", "AHeatDemM2", "ACoolDem", "ACoolDemM2", "ADHWDem",
                            "ADHWDemM2", "MaxDHWDem", "MaxCoolDem", "MaxDHWDem", "Use", "GrossFA"]
            missing_fields = set()
            for feature in features2:
                if len(feature.attributes()) > 13:
                    # Field names
                    # BuildingID AHeatDem AHeatDemM2 ACoolDem ACoolDemM2 ADHWDem ADHWDemDM2 MaxHeatDem MaxCoolDem MaxDHWDem USE, GrossFloor area
                    #string_list = [str(feature.attribute(3)), str(feature.attribute(5)), str(feature.attribute(6)),
                    #               str(feature.attribute(7)), str(feature.attribute(8)), str(feature.attribute(9)),
                    #               str(feature.attribute(10)), str(feature.attribute(11)), str(feature.attribute(12)),
                    #               str(feature.attribute(13)), str(feature.attribute(14)), str(feature.attribute(18))]
                    string_list2 = []
                    for f in fields:
                        try:
                            string_list2.append(str(feature[f]))
                        except:
                            missing_fields.add(f)
                            string_list2.append('')
                    building_item_list2.append(QTreeWidgetItem(string_list2))
                    self.pmTree2.addTopLevelItems(building_item_list2)
            if len(missing_fields) > 0:
                self.iface.messageBar().pushMessage("Field {0} is missing in ths future shape file".format(missing_fields), level=1, duration=0)

    def load_csv_file(self):
        self.list_district_select()
      #  self.csv_loaded.emit(self.sources_available)

    # confronta i distretti selezionati e riempe la tabella
    def list_district_select(self):
        lista = self.list_district()
        csvFile = self.layerPath3.filePath()
        if not os.path.exists(csvFile):
            return
        data = []
        self.sources_available.clear()
        self.sources_available.insertRow(0)
        with open(csvFile)as inputFile:
            csvReader = csv.reader(inputFile, delimiter='\t')
            for row in csvReader:
                data.append(row)
            index_list = []
            for i in range(len(lista)):
                if lista[i] in data[0][:]:
                    index_list.append(data[0][:].index(lista[i]))
        self.sources_available.clear()
        totalColumns = self.sources_available.columnCount()
        headerList = lista
        headerList.insert(0, "Source Description")
        headerList.append("Total")
        self.sources_available.setRowCount(0)
        for i in range(totalColumns - 1, -1, -1):
            self.sources_available.removeColumn(i)
        for j in range(len(lista)):
            self.sources_available.insertColumn(j)
        self.sources_available.setHorizontalHeaderLabels(headerList)
        # data[riga][colonna]
        for k in range(len(data) - 1):
            self.sources_available.insertRow(k)
            for z in range(len(lista)):
                if z == 0:

                    self.sources_available.setItem(k, z, QTableWidgetItem(str(data[k + 1][0])))
                else:
                    if z < len(index_list) + 1:
                        self.sources_available.setItem(k, z, QTableWidgetItem(str(data[k + 1][index_list[z - 1]])))
                    else:
                        self.sources_available.setItem(k, z, QTableWidgetItem(self.somma(k)))

    def somma(self, q):
        total = 0

        try:
            column = self.sources_available.columnCount() - 2

            for p in range(column):
                num = float(self.sources_available.item(q, p + 1).text())
                total = total + num
        except:
            pass

        return str(total)

    def list_district(self):
        # return list of selected district
        distretti = []
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState():
                # self.listWidget.item(i).setCheckState(list.addItem())
                distretti.append(self.listWidget.item(i).text())

        return distretti


    def reset_function(self):
        self.pmTree.clear()
        self.pmTree2.clear()

    def closeEvent(self, event):
        self.closeStep0()
        event.accept()

    def closeStep0(self):
        self.hide()
        self.step0_closing_signal.emit()

    def activate_visualization_tabs(self):
        self.listWidget.clear()
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton.setEnabled(False)
        # Districts layer it's expected to be called projection_helper.shp
        layer_list = QgsProject.instance().mapLayersByName("projection_helper.shp")
        if len(layer_list) > 0:
            layer = layer_list[0]
        else:
            layer = None
        if layer is not None and self.baseline_scenario_layer is not None:
            if not layer.crs() == self.baseline_scenario_layer.crs():
                parameter = {'INPUT': layer, 'TARGET_CRS': self.baseline_scenario_layer.crs().authid(),
                             'OUTPUT': 'memory:'}
                p = processing.run('qgis:reprojectlayer', parameter)
                layer = p['OUTPUT']

            # do this only if all_import_completed flag it's true
            if self.all_import_completed:
                # setting progress bar
                self.progressBar.setMaximum(self.baseline_scenario_layer.featureCount())
                self.progressBar.setMinimum(0)
                self.progressBar.setValue(0)
                self.progressBar.show()
                progress = 0
                district_list = []

                # for every buildings check in what district it is placed
                for feature in self.baseline_scenario_layer.getFeatures():
                    self.progressBar.setValue(progress)
                    progress = progress + 1
                    centroid = feature.geometry().centroid()
                    for district in layer.getFeatures():
                        # if building is in a specific district, check that district in listWidget
                        if district.geometry().contains(centroid):
                            # add the district name (which contain the building) to a list
                            if district.id() not in district_list:
                                district_list.append(district.id())
                            break

                area_analyzed = QgsVectorLayer('Polygon?crs=' + layer.crs().authid(), "", "memory")
                area_analyzed.startEditing()
                area_analyzed.dataProvider().addAttributes([f for f in layer.fields()])
                area_analyzed.updateFields()
                area_analyzed.commitChanges()

                # Set message bar :
                self.iface.messageBar().pushMessage("Loading OSM data", "Please wait...", level=0, duration=0)
                self.iface.mainWindow().repaint()

                self.progressBar.setMaximum(len(district_list)+1)
                self.progressBar.setMinimum(0)
                self.progressBar.setValue(0)
                self.progressBar.show()
                progress = 0
                p = streetsDownloader()
                streets = []
                streets_merged = None
                for i in district_list:

                    progress = progress + 1

                    # clear the layer
                    area_analyzed.startEditing()
                    for f in area_analyzed.getFeatures():
                        area_analyzed.deleteFeature(f.id())
                    area_analyzed.commitChanges()

                    # add next district
                    area_analyzed.startEditing()
                    dp = area_analyzed.dataProvider()
                    dp.addFeatures([layer.getFeature(i)])
                    area_analyzed.commitChanges()

                    # if streets_merged is None:
                    streets.append(p.download_streets_from_osm(area_analyzed))

                    # It assumes the widget display districts in the same order of .getFeatures()
                    if self.listWidget.item(i) is not None:
                        self.listWidget.item(i).setCheckState(QtCore.Qt.Checked)
                    self.progressBar.setValue(progress)

                for i in range(len(streets)):
                    if streets_merged is None:
                        streets_merged = streets[i]
                    else:
                        streets_merged.startEditing()
                        dp = streets_merged.dataProvider()
                        dp.addFeatures([s for s in streets[i].getFeatures()])
                        streets_merged.commitChanges()

                streets_merged.startEditing()
                f1 = QgsField('ID', QVariant.Int, 'int', 10)
                f2 = QgsField('OSM_origin', QVariant.Int, 'int', 1, 0, '', QVariant.Invalid)
                f3 = QgsField('diameter', QVariant.Double, 'double', 16, 3, '', QVariant.Invalid)
                streets_merged.dataProvider().addAttributes([f1, f2, f3])
                streets_merged.commitChanges()
                streets_merged.startEditing()
                i = 0
                for f in streets_merged.getFeatures():
                    f.setAttribute(f.fieldNameIndex('ID'), i)
                    f.setAttribute(f.fieldNameIndex('OSM_origin'), 1)
                    streets_merged.updateFeature(f)
                    i = i + 1
                streets_merged.commitChanges()
                progress = progress + 1
                self.progressBar.setValue(progress)
                QgsProject.instance().addMapLayer(streets_merged)
                self.step0_all_import_complete.emit(streets_merged)
                self.progressBar.hide()
        self.phases.setTabEnabled(1, True)
        self.phases.setTabEnabled(2, True)

    def get_temperature_from_mapping_module(self, dr):
        sources_temperature = {}
        # sources_temperature = self.dialog_source.source_temperature
        for mapped_source in self.dialog_source.mapped_sources:
            temperature = self.dialog_source.source_temperature[mapped_source]
            sources_temperature[self.dialog_source.MM_to_DPM_sources_dict[mapped_source]] = [temperature for i in
                                                                                             range(self.h8760)]
            try:
                file_start = self.dialog_source.file_name_mapping[mapped_source]
            except:
                continue
            if self.dialog_source.monthly_temperature[mapped_source]:
                suffixs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            else:
                suffixs = [""]

            for suffix in suffixs:
                f = Step0Dialog.find_file(dr, file_start + str(suffix) + "_", ".tif")
                if f is None:
                    continue
                params = f.split("_")[1:-1]
                for param in params:
                    try:
                        if param.startswith("t"):
                            sources_temperature = self.span_temperature(sources_temperature,
                                                            self.dialog_source.MM_to_DPM_sources_dict[mapped_source],
                                                            suffix, float(param.lstrip("t")))
                        if param.startswith("b"):
                            self.dialog_source.source_buffer[mapped_source] = float(param.lstrip("b"))
                        if param.startswith("e"):
                            self.dialog_source.source_efficiency[mapped_source] = float(param.lstrip("e"))
                    except:
                        print("Step0, get_temperature_from_mapping_module: failed to interpreter param", param,
                              "File:", f)


        return sources_temperature

    def span_temperature(self, sources_temperature, source, suffix, integral):
        if suffix == "":
            for i in range(len(sources_temperature[source])):
                sources_temperature[source][i] = integral
        else:
            try:
                suffix = int(suffix)
            except ValueError:
                return sources_temperature
            for month_length in self.day_per_month.keys():
                if int(suffix) in self.day_per_month[month_length]:
                    start, end = self.start_end_month(suffix)
                    for i in range(start, end):
                        sources_temperature[source][i] = integral
                    break
            else:
                print("Step0Dialog.py, span_integral, strange things are happening. suffix: ", suffix)
        return sources_temperature

    @staticmethod
    def find_file(folder, start, end):
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.endswith(end) and f.startswith(start):
                    return f
        return None

    def start_end_month(self, month):
        if month is None:
            return [1, 0]
        try:
            month = int(month)
        except ValueError:
            return [0, self.h8760]
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

    def update_source_combobox(self):
        pass

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
        txt = self.comboLayer.currentText()
        worker = SourceAvailability()
        worker.txt = txt
        worker.pbar_Download = self.pbar_Download
        worker.cancel_button = self.cancel
        worker.cancel_button.clicked.connect(self.interrupt)
        worker.day_per_month = self.day_per_month
        worker.dialog_source = self.dialog_source

        self.worker = worker

        sources_availability = worker.source_availability()
        if sources_availability is None:
            return
        sources_temperature = self.get_temperature_from_mapping_module(self.folder.text())

        self.sources_available.clear()

        self.sources_available.setColumnCount(3)
        self.sources_available.setRowCount(len(sources_availability))
        self.sources_available.setHorizontalHeaderLabels(["Source", "Availability [MWh/y]", "Temperature [°C]"])
        i = 0
        for key in sources_availability.keys():
            self.sources_available.setItem(i, 0, QTableWidgetItem(str(key)))
            self.sources_available.setItem(i, 1, QTableWidgetItem(str(round(sum(sources_availability[key])/1000.0, 2))))
            self.sources_available.setItem(i, 2, QTableWidgetItem(str(round(sum(sources_temperature[key])/self.h8760, 2))))
            i = i + 1
        self.sources_available.setColumnWidth(0, 320)
        self.sources_available.setColumnWidth(1, 140)
        self.sources_available.setColumnWidth(2, 140)
        # self.sources_available.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        #self.send_tab_to_stap3()
        self.send_data_to_step2.emit(sources_availability, sources_temperature)

        source_availability_post_calculation = SourceAvailabilityPostCalculation(self.sources_available)
        source_availability_post_calculation.remove_temperature([self.dialog_source.sources[1],
                                                                 self.dialog_source.sources[0],
                                                                 self.dialog_source.sources[4],
                                                                 self.dialog_source.sources[20]])
        source_availability_post_calculation.set_new_text()
        source_availability_post_calculation.swap_position(19, 13)


    def send_tab_to_stap3(self):
        self.send_tab_sources.emit(self.sources_available)


    def interrupt(self):
        self.worker.cancel = True

    def download_streets_from_comboBox_selection(self):

        p = streetsDownloader()
        streets_merged = p.download_streets_from_osm()

        self.geo_graph = p.geo_graph
        self.data_transfer.geo_graph = self.geo_graph
        self.data_transfer.buildings = self.baseline_scenario_layer

        streets_merged.startEditing()
        f1 = QgsField('ID', QVariant.Int, 'int', 10)
        f2 = QgsField('OSM_origin', QVariant.Int, 'int', 1, 0, '', QVariant.Invalid)
        f3 = QgsField('diameter', QVariant.Double, 'double', 16, 3, '', QVariant.Invalid)
        streets_merged.dataProvider().addAttributes([f1, f2, f3])
        streets_merged.commitChanges()
        streets_merged.startEditing()
        i = 0
        for f in streets_merged.getFeatures():
            f.setAttribute(f.fieldNameIndex('ID'), i)
            f.setAttribute(f.fieldNameIndex('OSM_origin'), 1)
            streets_merged.updateFeature(f)
            i = i + 1
        streets_merged.commitChanges()

        layers = QgsProject.instance().mapLayersByName(streets_merged.name())
        for layer in layers:
            QgsProject.instance().removeMapLayer(layer.id())
            try:
                del layer
            except:
                print("Step0_dialog.py, download_streets_from_comboBox_selection."
                        +" Unable to remove layer.")
        QgsProject.instance().addMapLayer(streets_merged)
        self.step0_all_import_complete.emit(streets_merged, self.data_transfer)


    def get_layer_streets_old(self):
        file_path = self.layerPath_streets.filePath()
        if not QgsProject.instance().mapLayersByName(os.path.basename(file_path)):
            load_file_as_layer(file_path, os.path.basename(file_path), 'Streets layer', min_val=None,
                            max_val=None, mean_val=None, value_color=None, area=None)
        else:
            print("File " + file_path + "seems to be already loaded! Skipping file...")
        self.download_streets_from_comboBox_selection()

    def get_layer_streets(self):
        layer = self.create_shape_buildings(display=True, save_output=True)
        self.download_streets_from_comboBox_selection()

    def create_shape_buildings(self, to_crs=None, display=False, save_output=False):
        building_layer_path = os.path.join(mp_config.CURRENT_MAPPING_DIRECTORY, mp_config.DMM_FOLDER,
                                           mp_config.DMM_PREFIX+".shp")
        if not os.path.exists(building_layer_path):
            raise Exception("The shape file from the District Mapping doesn't exist. "
                            "Please run the District Mapping Module first.")
        if to_crs is None:
            to_crs = mp_config.WGS84_CRS
        # Read buildings file as geopandas
        buildings_gdf = gpd.read_file(building_layer_path)
        if len(buildings_gdf) == 0:
            raise Exception("The shape file from the District Mapping is empty.")
        # Buffer 0.0 to remove invalid polygons, even if there is a loss
        if any(not p.is_valid for p in buildings_gdf["geometry"]):
            buildings_gdf["geometry"] = buildings_gdf["geometry"].buffer(0.0)
        # Remove the empty polygons
        buildings_gdf = buildings_gdf[buildings_gdf["geometry"].is_empty == False]
        # Project gdf to WGS84
        buildings_gdf.to_crs(mp_config.WGS84_CRS, inplace=True)
        # Project gdf in UTM
        projected_gdf = ox.project_gdf(buildings_gdf)
        # ConveHull of all buildings (unary_union)
        hull = projected_gdf["geometry"].unary_union.convex_hull
        # Buffer around it
        buffer_hull = hull.buffer(mp_config.BUFFER_HULL_FOR_STREETS)
        # Reproject store it in geodataframe
        buffer_hull_gdf = gpd.GeoDataFrame(columns=["geometry"], crs=projected_gdf.crs)
        buffer_hull_gdf.loc[0] = [buffer_hull]
        # Reproject
        buffer_hull_gdf = ox.project_gdf(buffer_hull_gdf, to_crs=to_crs)
        print("Save as shapefile ...")
        output_folder = os.path.join(mp_config.CURRENT_PLANNING_DIRECTORY, mp_config.DISTRICT_FOLDER,
                                     mp_config.BUILDING_SHAPE)
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, mp_config.BUILDING_SHAPE+".shp")
        buffer_hull_gdf.to_file(output_file, driver='ESRI Shapefile')

        if display:
            print("Displaying ...")
            output_layer = QgsProject.instance().addMapLayer(QgsVectorLayer(output_file, "building_shape", "ogr"))
            crs = output_layer.crs()
            crs.createFromId(4326)
            output_layer.setCrs(crs)
            lyr = QgsProject.instance().layerTreeRoot().findLayer(output_layer.id())
            lyr.setItemVisibilityChecked(False)
            self.iface.mapCanvas().refresh()

        return output_layer

    def delete_import_file(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        main_text = "Delete selected file?"
        msgBox.setText(main_text)
        msgBox.setWindowTitle("PlanHeat Planning and Simulation modules")
        msgBox.setInformativeText("Pressing Ok the file will be removed from your drive. Press Cancel to return.")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        r = msgBox.exec()
        if r == QMessageBox.Ok:
            if self.work_folder is None:
                folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "save_utility", "DefaultSaveFolder")
            else:
                folder = self.work_folder
                try:
                    os.path.exists(folder)
                except TypeError:
                    folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "save_utility", "DefaultSaveFolder")
            file_manager = FileManager(work_folder=folder)
            file_manager.create_work_folder()
            file = self.comboBox.currentText()
            file_path = file_manager.get_path_from_file_name(file, end_char=-5, search_folders=[folder])
            file_manager.remove_shapefiles(file)
            file_manager.purge_unused_network_folder_and_shapefiles()
            file_manager.remove_file_from_file_path(file_path)
            self.file_removed.emit()