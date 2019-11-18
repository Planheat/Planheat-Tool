# -*- coding: utf-8 -*-
"""
/***************************************************************************
 pointCreator
                                 A QGIS plugin
 ***************************************************************************/
"""

from PyQt5.QtCore import *
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsPointXY, QgsGeometry, QgsVectorFileWriter
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from .dialog_popup import DialogPopup
from .utils import DataTypes, IndustrialQuestion, UnconventionalQuestion, FuelTypes, get_sector_list, get_co2_factor, get_unconventional_list
from calendar import monthrange
import os

from .. import master_mapping_config

layer = None
active = False


class PointCreator:
    def select(self):
        def end_selection():
            canvas.setMapTool(self.previous_map_tool)
            self.myMapTool.canvasClicked.disconnect()
            global active
            active = False
            self.actions[2].setChecked(False)

        def mouse_click(current_pos, clicked_button):
            global layer
            if clicked_button == Qt.LeftButton:
                active_layer = self.iface.activeLayer()
                if isinstance(active_layer, QgsVectorLayer) and active_layer.dataProvider().fields().indexFromName(
                        'VALUE_MWH') >= 0 and active_layer.dataProvider().fields().indexFromName('TYPE') >= 0:
                    point_type = list(active_layer.uniqueValues(1, 1))[0]
                    question_type = list(active_layer.uniqueValues(3, 1))[0]
                else:
                    point_type = None
                    question_type = None
                result, point_type, type_desc, question, question_desc, field1, field2, field3, field4, field5, month_factors, month_values, month_results = open_dialog(point_type,
                                                                                                                                                                         question_type)
                if result:
                    create_or_open_layer(self, active_layer, point_type)
                    feature = QgsFeature(layer.fields())
                    feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(current_pos)))
                    dp = layer.dataProvider()
                    feature.setAttribute(dp.fields().indexFromName('VALUE_MWH'), result)
                    feature.setAttribute(dp.fields().indexFromName('TYPE'), point_type)
                    feature.setAttribute(dp.fields().indexFromName('TYPE_LBL'), type_desc)
                    feature.setAttribute(dp.fields().indexFromName('QUESTION'), question)
                    feature.setAttribute(dp.fields().indexFromName('QUEST_LBL'), question_desc)
                    feature.setAttribute(dp.fields().indexFromName('FIELD1'), field1)
                    feature.setAttribute(dp.fields().indexFromName('FIELD2'), field2)
                    feature.setAttribute(dp.fields().indexFromName('FIELD3'), field3)
                    feature.setAttribute(dp.fields().indexFromName('FIELD4'), field4)
                    feature.setAttribute(dp.fields().indexFromName('FIELD5'), field5)
                    feature.setAttribute(dp.fields().indexFromName('M_FACT'), month_factors)
                    feature.setAttribute(dp.fields().indexFromName('M_INPUT'), month_values)
                    feature.setAttribute(dp.fields().indexFromName('M_VAL_KWH'), month_results)
                    layer.startEditing()
                    layer.addFeature(feature)
                    layer.commitChanges()
            if clicked_button == Qt.RightButton:
                canvas.refresh()
                end_selection()

        global active
        canvas = self.iface.mapCanvas()

        if active:
            end_selection()
        else:
            active = True
            self.actions[2].setChecked(True)
            self.previous_map_tool = canvas.mapTool()
            self.myMapTool = QgsMapToolEmitPoint(canvas)
            self.myMapTool.canvasClicked.connect(mouse_click)
            canvas.setMapTool(self.myMapTool)


def create_or_open_layer(interface, active_layer, point_type):
    global layer
    layer = None
    crs_str = ""
    crs = None
    if interface.dockwidget:
        base_file = interface.dockwidget.baseMapFile.text()
        crs_str = "crs_str=" + QgsVectorLayer(base_file).sourceCrs().toWkt() + "&"
        crs = QgsVectorLayer(base_file).sourceCrs()
    if interface.iface.activeLayer() and interface.iface.activeLayer().name() != "OSM" and crs_str == "":
        crs_str = "crs_str=" + interface.iface.activeLayer().crs().toWkt() + "&"
        crs = interface.iface.activeLayer().crs()
    if crs_str == "":
        crs_str = "crs_str=" + QgsProject.instance().defaultCrsForNewLayers().toWkt() + "&"
        crs = QgsProject.instance().defaultCrsForNewLayers()
    if len(crs_str) <= 5:
        crs_str = ''
        QMessageBox.critical(None, "Warning", "Could not set CRS system to new layer. Please change CRS manually.")
    if isinstance(active_layer, QgsVectorLayer) and \
        active_layer.dataProvider().fields().indexFromName('VALUE_MWH') >= 0 and \
        active_layer.dataProvider().fields().indexFromName('TYPE') >= 0 and \
        active_layer.dataProvider().fields().indexFromName('QUESTION') >= 0 and \
        point_type in active_layer.uniqueValues(1, 1):
        layer = active_layer
    else:
        filename = create_file_for_dialog_action()
        if filename:
            layer = QgsVectorLayer("Point?" + crs_str +
                                   "field=VALUE_MWH:double"
                                   "&field=TYPE:integer"
                                   "&field=TYPE_LBL:string"
                                   "&field=QUESTION:integer"
                                   "&field=QUEST_LBL:string"
                                   "&field=FIELD1:string"
                                   "&field=FIELD2:string"
                                   "&field=FIELD3:string"
                                   "&field=FIELD4:string"
                                   "&field=FIELD5:string"
                                   "&field=M_FACT:string"
                                   "&field=M_INPUT:string"
                                   "&field=M_VAL_KWH:string"
                                   , DataTypes(point_type).name + " layer", "memory")

            layer.updateFields()
            layer.updateExtents()
            error = QgsVectorFileWriter.writeAsVectorFormat(layer, filename, "UTF-8", crs, "ESRI Shapefile")

            if error != QgsVectorFileWriter.NoError:
                print("saving file failed", error)
            layer = QgsVectorLayer(filename, DataTypes(point_type).name + " layer")
    QgsProject.instance().addMapLayer(layer)


def open_dialog(point_type, question_type):
    dialog = DialogPopup()
    dialog.okButton.clicked.connect(lambda: ok(dialog))
    dialog.cancelButton.clicked.connect(lambda: cancel(dialog))
    dialog.typeSelect.currentIndexChanged.connect(lambda: update_type_selection(dialog, dialog.typeSelect.currentData()))
    dialog.questionSelect.currentIndexChanged.connect(lambda: update_question_selection(dialog, dialog.questionSelect.currentData()))
    dialog.questionSelect_2.currentIndexChanged.connect(lambda: update_question_unconventional_selection(dialog, dialog.questionSelect_2.currentData()))
    dialog.field1Select.currentIndexChanged.connect(lambda: sector_changed(dialog))
    dialog.field2Text.textChanged.connect(lambda: calculate_result(dialog))
    dialog.field3Select.currentIndexChanged.connect(lambda: fuel_changed(dialog))
    dialog.field4Text.textChanged.connect(lambda: calculate_result(dialog))
    dialog.field5Text.textChanged.connect(lambda: toggle_ok_button(dialog))
    dialog.resultText.textChanged.connect(lambda: toggle_ok_button(dialog))
    dialog.field1Text_2.textChanged.connect(lambda: calculate_result_unconventional(dialog))
    dialog.field2Text_2.textChanged.connect(lambda: calculate_result_unconventional(dialog))
    dialog.field3Text_2.textChanged.connect(lambda: calculate_result_unconventional(dialog))
    dialog.field4Text_2.textChanged.connect(lambda: calculate_result_unconventional(dialog))
    dialog.field5Text_2.textChanged.connect(lambda: calculate_result_unconventional(dialog))
    for i in range(1, 13):
        getattr(dialog, "monthCheckBox_" + str(i)).stateChanged.connect(lambda: calculate_result_unconventional(dialog))
        getattr(dialog, "month_" + str(i)).textChanged.connect(lambda: calculate_result_unconventional(dialog))
    dialog.closingPlugin.connect(lambda: cancel(dialog))
    dialog.okButton.setEnabled(False)
    dialog.month_results.setVisible(False)
    set_size_policy(dialog.field1Label)
    set_size_policy(dialog.field2Label)
    set_size_policy(dialog.field3Label)
    set_size_policy(dialog.field4Label)
    set_size_policy(dialog.field5Label)
    fill_datatype_select(dialog)
    fill_question_select(dialog)
    fill_question_unconventional_select(dialog)
    fill_fuel_select(dialog)
    fill_sector_select(dialog)
    dialog.typeSelect.setEnabled(True)
    if point_type is not None and point_type > -1:
        index = dialog.typeSelect.findData(DataTypes(point_type))
        if index != -1:
            dialog.typeSelect.setCurrentIndex(index)
            dialog.typeSelect.setEnabled(False)
    if question_type is not None and question_type > -1:
        print(question_type,point_type)
        if point_type == 2:
            index = dialog.questionSelect_2.findData(question_type)
            if index != -1:
                dialog.questionSelect_2.setCurrentIndex(index)
        elif point_type == 0:
            index = dialog.questionSelect.findData(IndustrialQuestion(question_type))
            if index != -1:
                dialog.questionSelect.setCurrentIndex(index)

    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.adjustSize()
    dialog.exec_()
    if dialog.typeSelect.currentData() == DataTypes.UNCONVENTIONAL:
        return dialog.resultText.text(), dialog.typeSelect.currentData().value, dialog.typeSelect.currentText(), dialog.questionSelect_2.currentData(), dialog.questionSelect_2.currentText(), dialog.field1Text_2.text(), \
               dialog.field2Text_2.text(), dialog.field3Text_2.text(), dialog.field4Text_2.text(), dialog.field5Text_2.text(), \
               get_monthly_factors_as_string(dialog), get_month_fields_as_string(dialog), dialog.month_results.text()

    return dialog.resultText.text(), dialog.typeSelect.currentData().value, dialog.typeSelect.currentText(), dialog.questionSelect.currentData().value, \
           dialog.questionSelect.currentText(), dialog.field1Select.currentData().description, \
           dialog.field2Text.text(), dialog.field3Select.currentData().value, dialog.field4Text.text(), dialog.field5Text.text(), None, None, None


def get_monthly_factors_as_string(dialog):
    result = []
    if dialog.monthLabel_1.text():
        for i in range(1, 13):
            status = getattr(dialog, "monthCheckBox_" + str(i)).isChecked()
            if status:
                result.append('1')
            else:
                result.append('0')
    return ';'.join(result)


def get_month_fields_as_string(dialog):
    result = []
    if dialog.month_1.text():
        for i in range(1, 13):
            result.append(getattr(dialog, "month_" + str(i)).text())
    return ';'.join(result)


def sector_changed(dialog):
    sector = dialog.field1Select.currentData()
    if sector:
        dialog.field4Text.setText(str(sector.heat_recovery))
        if dialog.questionSelect.currentData() == IndustrialQuestion.FLOOR_SURFACE:
            sector = dialog.field1Select.currentData()
            dialog.field5Text.setText("{0:.4f}".format(sector.mwh_per_m2_per_year))
        if dialog.questionSelect.currentData() == IndustrialQuestion.CO2:
            dialog.field3Select.setCurrentIndex(-1)
            sector = dialog.field1Select.currentData()
            index = dialog.field3Select.findData(sector.fuel_type)
            if index != -1:
                dialog.field3Select.setCurrentIndex(index)


def fuel_changed(dialog):
    if dialog.questionSelect.currentData() == IndustrialQuestion.CO2:
        conversion_factor = get_co2_factor(dialog.field3Select.currentData())
        if conversion_factor:
            dialog.field5Text.setText("{0:.4f}".format(conversion_factor))


def calculate_result(dialog):
    selection_type = dialog.typeSelect.currentData()
    if selection_type == DataTypes.INDUSTRIAL:
        sector = dialog.field1Select.currentData()
        if dialog.questionSelect.currentData() == IndustrialQuestion.CO2:
            if is_float(dialog.field2Text.text()) and is_float(dialog.field5Text.text()) and is_float(dialog.field4Text.text()):
                result = float(dialog.field2Text.text()) * float(dialog.field5Text.text()) * (1.0 - (float(dialog.field4Text.text()) / 100))
                dialog.resultText.setText("{0:.4f}".format(result))
        if dialog.questionSelect.currentData() == IndustrialQuestion.CONSUMPTION:
            if is_float(dialog.field2Text.text()) and is_float(dialog.field4Text.text()):
                result = float(dialog.field2Text.text()) * (1.0 - (float(dialog.field4Text.text()) / 100))
                dialog.resultText.setText("{0:.4f}".format(result))
        if dialog.questionSelect.currentData() == IndustrialQuestion.FLOOR_SURFACE:
            if is_float(dialog.field2Text.text()) and is_float(dialog.field4Text.text()):
                result = float(dialog.field2Text.text()) * float(dialog.field5Text.text()) * (1.0 - (float(dialog.field4Text.text()) / 100))
                dialog.resultText.setText("{0:.4f}".format(result))
    if selection_type == DataTypes.GENERIC:
        if is_float(dialog.resultText.text()):
            result = float(dialog.resultText.text())
            dialog.resultText.setText("{0:.4f}".format(result))


# calculate results per month and write them and the sum of them into the corresponding fields.
def calculate_result_unconventional(dialog):
    source_id = dialog.questionSelect_2.currentData()
    result = 0.
    month_results = []
    if is_float(dialog.field1Text_2.text()):
        if source_id == UnconventionalQuestion.SUBWAY:
            if is_float(dialog.field2Text_2.text()) and dialog.monthCheckBox_1.isVisible():
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    # Eheat = Tdiff x Q x 1.2 x tmonth / (3.6 *10^3) [kWh]                                  tmonth = 24h * number of days in month
                    month_result = float(dialog.field2Text_2.text()) * float(dialog.field1Text_2.text()) * 1.2 * 24 * monthrange(2018, i)[1] / 3600 * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.CAR_PARKS:
            dialog.field2Text_2.setText(str(float(dialog.field1Text_2.text()) * 3 / 1000 * 3600))
            if is_float(dialog.field2Text_2.text()) and is_float(dialog.field3Text_2.text()):
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    # Eheat = Tdiff x Q x 1.2 x tmonth / (3.6 *10^3) [kWh]
                    month_result = float(dialog.field3Text_2.text()) * float(dialog.field2Text_2.text()) * 1.2 * 24 * monthrange(2018, i)[1] / 3600 * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.DATA_CENTERS:
            for i in range(1, 13):
                if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                    month_factor = 1
                else:
                    month_factor = 0
                # Eheat = ED x 0.9 /12 [kWh/mnth]   (per month = /365 * days in month)
                month_result = float(dialog.field1Text_2.text()) * 0.9 / 365 * monthrange(2018, i)[1] * month_factor
                month_results.append(month_result)
                result += month_result
        if source_id == UnconventionalQuestion.DATA_CENTERS_UNKNOWN:
            if is_float(dialog.field2Text_2.text()) and is_float(dialog.field3Text_2.text()) and is_float(dialog.field4Text_2.text()) and is_float(dialog.field5Text_2.text()):
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    # Eheat = A x PD x FSU x LL x ( 1 + 1 /COP ) x tmonth   [kWh]            PD in W, FSU in %, LL in %
                    month_result = float(dialog.field1Text_2.text()) * float(dialog.field2Text_2.text()) / 1000 * float(dialog.field3Text_2.text()) / 100 * float(
                        dialog.field4Text_2.text()) / 100 * (1 + 1 / float(dialog.field5Text_2.text())) * 24 * monthrange(2018, i)[1] * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.SUPERMARKET_COOLING:
            for i in range(1, 13):
                if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                    month_factor = 1
                else:
                    month_factor = 0
                # Eheat = ED x 0.65 x 3 / 12 [kWh/mnth]  (per month = /365 * days in month)
                month_result = float(dialog.field1Text_2.text()) * 0.65 * 3 / 365 * monthrange(2018, i)[1] * month_factor
                month_results.append(month_result)
                result += month_result
        if source_id == UnconventionalQuestion.SUPERMARKET_COOLING_UNKNOWN:
            if is_float(dialog.field2Text_2.text()) and is_float(dialog.field3Text_2.text()):
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    # Eheat = A x PC / 8760 x (COP + 1) x tmonth   [kWh]        (24h * 365 = 8760h)
                    month_result = float(dialog.field1Text_2.text()) * float(dialog.field2Text_2.text()) / 8760 * (float(dialog.field3Text_2.text()) + 1) * 24 * \
                                   monthrange(2018, i)[
                                       1] * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.REFRIGERATED_STORAGE_FACILITIES:
            if is_float(dialog.field2Text_2.text()):
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    # Eheat = ED x 0.9 x COP / 12 [kWh/mnth]     (per month = /365 * days in month)
                    month_result = float(dialog.field1Text_2.text()) * 0.9 * float(dialog.field2Text_2.text()) / 365 * monthrange(2018, i)[1] * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.REFRIGERATED_STORAGE_FACILITIES_UNKNOWN:
            if is_float(dialog.field2Text_2.text()) and is_float(dialog.field3Text_2.text()):
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    # Eheat = A x 3 x PC / 8760 x (COP + 1) x tmonth   [kWh]
                    month_result = float(dialog.field1Text_2.text()) * 3 * float(dialog.field2Text_2.text()) / 8760 * (float(dialog.field3Text_2.text()) + 1) * 24 * \
                                   monthrange(2018, i)[
                                       1] * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.WASTE_WATER_PLANT_EFFLUENT:
            if is_float(dialog.field2Text_2.text()) and is_float(dialog.month_1.text()):
                Q = float(dialog.field1Text_2.text()) * 200 / 24 / 1000 * 0.67
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    if is_float(getattr(dialog, "month_" + str(i)).text()):
                        water_temp = to_float(getattr(dialog, "month_" + str(i)).text())

                        # Eheat = ρ x Q x C x (Tsew – Tcool) x tmonth / (3.6 *10^3) [kWh]
                        month_result = (water_temp - float(dialog.field2Text_2.text())) * Q * 4200 / 3600 * 24 * monthrange(2018, i)[1] * month_factor
                        month_results.append(month_result)
                        result += month_result
        if source_id == UnconventionalQuestion.WASTE_WATER_PLANT_EFFLUENT_LOAD:
            if is_float(dialog.field2Text_2.text()) and is_float(dialog.month_1.text()):
                Q = float(dialog.field1Text_2.text()) * 200 / 24 / 1000
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    if is_float(getattr(dialog, "month_" + str(i)).text()):
                        water_temp = to_float(getattr(dialog, "month_" + str(i)).text())

                        # Eheat = ρ x Q x C x (Tsew – Tcool) x tmonth / (3.6 *10^3) [kWh]
                        month_result = (water_temp - float(dialog.field2Text_2.text())) * Q * 4200 / 3600 * 24 * monthrange(2018, i)[1] * month_factor
                        month_results.append(month_result)
                        result += month_result
        if source_id == UnconventionalQuestion.WASTE_WATER_PLANT_EFFLUENT_UNKNOWN:
            if is_float(dialog.field2Text_2.text()):
                Q = float(dialog.field1Text_2.text()) * 200 / 24 / 1000 * 0.67
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    water_temp = float(dialog.field2Text_2.text())

                    # Eheat = ρ x Q x C x (Tsew – Tcool) x tmonth / (3.6 *10^3) [kWh]
                    month_result = water_temp * Q * 4200 / 3600 * 24 * monthrange(2018, i)[1] * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.WASTE_WATER_PLANT_EFFLUENT_UNKNOWN_LOAD:
            if is_float(dialog.field2Text_2.text()):
                Q = float(dialog.field1Text_2.text()) * 200 / 24 / 1000
                for i in range(1, 13):
                    if getattr(dialog, "monthCheckBox_" + str(i)).isChecked():
                        month_factor = 1
                    else:
                        month_factor = 0
                    water_temp = float(dialog.field2Text_2.text())

                    # Eheat = ρ x Q x C x (Tsew – Tcool) x tmonth / (3.6 *10^3) [kWh]
                    month_result = water_temp * Q * 4200 / 3600 * 24 * monthrange(2018, i)[1] * month_factor
                    month_results.append(month_result)
                    result += month_result
        if source_id == UnconventionalQuestion.LNG_TERMINAL:
            result = float(dialog.field1Text_2.text()) * 1000 * 1000
    if result < 0:
        result = 0
    dialog.resultText.setText("{0:.4f}".format(result / 1000))
    dialog.month_results.setText(';'.join(format(x, "10.4f") for x in month_results))


def to_float(str):
    try:
        return float(str)
    except ValueError:
        return 0.


def toggle_ok_button(dialog):
    if dialog.resultText.text():
        dialog.okButton.setEnabled(True)
    else:
        dialog.okButton.setEnabled(False)


def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def ok(dialog):
    dialog.closingPlugin.disconnect()

    dialog.close()


def create_file_for_dialog_action():
    qfd = QFileDialog()
    title = 'Create new file'
    #path = "c:/TEMP/"
    path = os.path.join(master_mapping_config.CURRENT_MAPPING_DIRECTORY,
                        "pointCreator")
    os.makedirs(path, exist_ok=True)
    #file_path = QFileDialog.getSaveFileName(qfd, title, path, "shapefile (*.shp)")[0]
    path = os.path.join(path, "point_"+str(len(list(os.listdir(path)))))
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, "point.shp")
    print(file_path)
    if file_path:
        return file_path
    return None


def cancel(dialog):
    dialog.closingPlugin.disconnect()
    dialog.resultText.setText(None)
    dialog.close()


def update_type_selection(dialog, selection_type):
    if selection_type == DataTypes.INDUSTRIAL.value:
        dialog.groupUnconventional.setVisible(False)
        dialog.questionSelect.setVisible(True)
        dialog.groupIndustrial.setVisible(True)
        dialog.resultText.setEnabled(False)
        dialog.typeLabel.setToolTip("<span>Allows manually adding industrial excess heat sources to the map. \
            The wizard enables the calculation of the thermal supply according to three different calculation methods that each are taking into account different levels of  data availability. \
            After this preprocessing step, the created shapefile has to be added to the source 'Additional industries' in the Potential supply list of the Supply Mapping Module of the \
            PLANHEAT tool. This will ensure inclusion in the further PLANHEAT calculations. \
            <br>DISCLAIMER!! The calculated availability of excess heat is only indicative and is by no means a guarantee on the feasibility of excess heat delivery.</span>")
        update_question_selection(dialog, IndustrialQuestion.CO2)
    elif selection_type == DataTypes.UNCONVENTIONAL.value:
        dialog.groupIndustrial.setVisible(False)
        dialog.groupUnconventional.setVisible(True)
        dialog.resultText.setEnabled(False)
        dialog.typeLabel.setToolTip("<span>Creates a shapefile with unconventional sources represented as points for the following categories: subway networks, indoor car parks, data centres, supermarkets, refrigerated storage facilities, waste water treatment plants and LNG terminals. \
        Different calculation methods are available according to the data availability and they can be combined within the development of one shapefile. \
        However, the user should not mix sources of different categories in one shapefile, because after this preprocessing step, the created shapefile has to be added to the corresponding source in the Potential supply list of the Supply Mapping Module of the PLANHEAT tool. \
        This will ensure inclusion in the further PLANHEAT calculations.</span>")
        update_question_unconventional_selection(dialog, UnconventionalQuestion.SUBWAY)
    else:
        dialog.groupIndustrial.setVisible(False)
        dialog.groupUnconventional.setVisible(False)
        dialog.resultText.setEnabled(True)

        dialog.typeLabel.setToolTip("<span>Creates a shapefile with generic excess heat/cooling sources represented as points. In this case, the user already knows the thermal supply of the source.\
                   After this preprocessing step, the created shapefile has to be added to the source 'Generic heating/cooling source' in the Potential supply list of the Supply Mapping Module of the PLANHEAT tool. This will ensure inclusion in the further PLANHEAT calculations.\
                   </span>")


def update_question_unconventional_selection(dialog, source_id):
    source_list = get_unconventional_list(source_id)
    for i in range(1, 6):
        set_visibility_for_field_group(dialog, i, False)
        clear_value_of__text_field(dialog, i, )
    dialog.monthGroup.setVisible(False)
    dialog.monthGroupTemp.setVisible(False)
    for item in source_list:
        dialog.sourceLabel_2.setToolTip(item.tool_tip0)
        if item.label1 or item.parameter1:
            set_visibility_for_field_group(dialog, 1, True)
            dialog.field1Label_2.setText(item.label1)
            dialog.field1Text_2.setText(xstr(item.parameter1))
            print(item.tool_tip1)
            dialog.field1Label_2.setToolTip(item.tool_tip1)
            dialog.field1UnitLabel_2.setText(item.unit1)
            if item.enabled1 == 0:
                dialog.field1Text_2.setEnabled(False)
            else:
                dialog.field1Text_2.setEnabled(True)
        if item.label2 or item.parameter2:
            set_visibility_for_field_group(dialog, 2, True)
            dialog.field2Label_2.setText(item.label2)
            dialog.field2Text_2.setText(xstr(item.parameter2))
            dialog.field2Label_2.setToolTip(item.tool_tip2)
            dialog.field2UnitLabel_2.setText(item.unit2)
            if item.enabled2 == 0:
                dialog.field2Text_2.setEnabled(False)
            else:
                dialog.field2Text_2.setEnabled(True)
        if item.label3 or item.parameter3:
            set_visibility_for_field_group(dialog, 3, True)
            dialog.field3Label_2.setText(item.label3)
            dialog.field3Text_2.setText(xstr(item.parameter3))
            dialog.field3Label_2.setToolTip(item.tool_tip3)
            dialog.field3UnitLabel_2.setText(item.unit3)
            if item.enabled3 == 0:
                dialog.field3Text_2.setEnabled(False)
            else:
                dialog.field3Text_2.setEnabled(True)
        if item.label4 or item.parameter4:
            set_visibility_for_field_group(dialog, 4, True)
            dialog.field4Label_2.setText(item.label4)
            dialog.field4Text_2.setText(xstr(item.parameter4))
            dialog.field4Label_2.setToolTip(item.tool_tip4)
            dialog.field4UnitLabel_2.setText(item.unit4)
            if item.enabled4 == 0:
                dialog.field4Text_2.setEnabled(False)
            else:
                dialog.field4Text_2.setEnabled(True)
        if item.label5 or item.parameter5:
            set_visibility_for_field_group(dialog, 5, True)
            dialog.field5Label_2.setText(item.label5)
            dialog.field5Text_2.setText(xstr(item.parameter5))
            dialog.field5Label_2.setToolTip(item.tool_tip5)
            dialog.field5UnitLabel_2.setText(item.unit5)
            if item.enabled5 == 0:
                dialog.field5Text_2.setEnabled(False)
            else:
                dialog.field5Text_2.setEnabled(True)
        if item.monthly_label:
            dialog.monthGroup.setVisible(True)
            dialog.monthLabel_2.setText(item.monthly_label)
            for i in range(1, 13):
                factor = int(item.monthly_factors[i - 1])
                if factor == 1:
                    getattr(dialog, "monthCheckBox_" + str(i)).setChecked(True)
                else:
                    getattr(dialog, "monthCheckBox_" + str(i)).setChecked(False)
        if item.monthly_values:
            dialog.monthGroupTemp.setVisible(True)
            dialog.monthLabel_2.setToolTip("<span>" + item.tool_tip3 + "</span>")
            for i in range(1, 13):
                getattr(dialog, "month_" + str(i)).setText(str(item.monthly_values[i - 1]))
    dialog.adjustSize()
    calculate_result_unconventional(dialog)


def set_visibility_for_field_group(dialog, i, value):
    getattr(dialog, "field" + str(i) + "Label_2").setVisible(value)
    getattr(dialog, "field" + str(i) + "Text_2").setVisible(value)
    getattr(dialog, "field" + str(i) + "UnitLabel_2").setVisible(value)


def clear_value_of__text_field(dialog, i):
    getattr(dialog, "field" + str(i) + "Text_2").setText('')


def xstr(s):
    if s is None:
        return ''
    return str(s)


def update_question_selection(dialog, selection_type):
    for i in range(1, 5):
        getattr(dialog, "field" + str(i) + "Label").setVisible(True)
    dialog.field1Select.setVisible(True)
    dialog.field2Text.setVisible(True)
    dialog.field2UnitLabel.setVisible(True)
    dialog.field3Select.setVisible(True)
    dialog.field4Text.setVisible(True)
    dialog.field5Text.setVisible(False)
    dialog.field5Label.setVisible(False)
    dialog.field5UnitLabel.setVisible(False)
    dialog.field1Label.setToolTip("<span>Drop-down list to select the industrial sector that best fits the features of the industrial facility</span>")
    if selection_type == IndustrialQuestion.CO2:
        dialog.field2Label.setText("CO2 emission:")
        dialog.field2Label.setToolTip(
            "<span>CO2 emissions of the industry in one year; insert only values referring to CO2 emissions and not to other greenhouse gases (GHG) converted into equivalent-CO2</span>")
        dialog.field2UnitLabel.setText("tCO2/y")
        dialog.field5Label.setVisible(True)
        dialog.field5Text.setVisible(True)
        dialog.field5UnitLabel.setVisible(True)
        dialog.field3Label.setToolTip(
            "<span>Drop-down list to select the type of fuel used by the industry; if this information is not available, standard fuels for each industrial sector are used</span>")
        dialog.field4Label.setToolTip(
            "<span>Percentage of the produced heat that is used and recovered within the industry; if this information is not available, standard values for each industrial sector are used</span>")
        dialog.field5Label.setText("CO2 emission factor:")
        dialog.field5Label.setToolTip(
            "<span>CO2 emission factor of the fuel used in the industry expressed as MWh of heat per unit of CO2 emission; default values from IPCC are used</span>")
        dialog.sourceLabel.setToolTip(
            "<span>Calculates the available excess heat starting from the CO2 emissions of the industry based on the emission factor of the used fuel and on typical heat recovery factors for each industrial sector.</span>")
    elif selection_type == IndustrialQuestion.CONSUMPTION:
        dialog.field2Label.setText("Fuel consumption:")
        dialog.field2Label.setToolTip(
            "<span>Consumption of fuel of the industry per year, expressed in MWh of primary energy (i.e. product of the mass of fuel and its heating value)</span>")
        dialog.field2UnitLabel.setText("MWh/y")
        dialog.field3Label.setVisible(False)
        dialog.field3Select.setVisible(False)
        dialog.sourceLabel.setToolTip(
            "<span>Calculates the available excess heat starting from the fuel consumption of the industry based on typical heat recovery factors for each industrial sector</span>")
    elif selection_type == IndustrialQuestion.FLOOR_SURFACE:
        dialog.field2Label.setText("Footprint area")
        dialog.field2Label.setToolTip("<span>Footprint  area of the industrial buildings (derived from satellite images / aerial photographs / kadaster data)</span>")
        dialog.field2UnitLabel.setText("m2")
        dialog.field3Label.setVisible(False)
        dialog.field3Select.setVisible(False)
        dialog.field5Label.setVisible(True)
        dialog.field5Text.setVisible(True)
        dialog.field5Label.setText("Specific fuel consumption:")
        dialog.typeLabel.setToolTip(
            "<span>Fuel consumption in terms of MWh of primary energy per unit of footprint area; default values are used for each industrial sector</span>")
        dialog.field5UnitLabel.setVisible(True)
        dialog.field5UnitLabel.setText("MWh/m2/y")
        dialog.sourceLabel.setToolTip(
            "<span>Calculates the available excess heat starting from the footprint area of the industrial buildings based on the typical fuel consumption per unit of area for each industrial sector and on typical heat recovery factors for each industrial sector.</span>")
    fill_sector_select(dialog)
    calculate_result(dialog)


def fill_datatype_select(dialog):
    dialog.typeSelect.clear()
    name = ""
    for data_type in DataTypes:
        if data_type == DataTypes.INDUSTRIAL:
            name = "Add industrial excess heat source"
        elif data_type == DataTypes.GENERIC:
            name = "Add generic waste heat/cooling source"
        elif data_type == DataTypes.UNCONVENTIONAL:
            name = "Add unconvential residual heat/cooling source"
        dialog.typeSelect.addItem(name, data_type)


def fill_question_select(dialog):
    dialog.questionSelect.clear()
    name = ""
    for data_type in IndustrialQuestion:
        if data_type == IndustrialQuestion.CO2:
            name = "Calculation based on CO2 emissions"
        elif data_type == IndustrialQuestion.CONSUMPTION:
            name = "Calculation based on fuel consumption"
        elif data_type == IndustrialQuestion.FLOOR_SURFACE:
            name = "Calculation based on footprint area"
        dialog.questionSelect.addItem(name, data_type)


def fill_question_unconventional_select(dialog):
    dialog.questionSelect_2.clear()
    name = ""
    source_list = get_unconventional_list()
    for item in source_list:
        dialog.questionSelect_2.addItem(item.description, item.source_id)


def fill_fuel_select(dialog):
    dialog.field3Select.clear()
    for fuel_type in FuelTypes:
        dialog.field3Select.addItem(fuel_type.name, fuel_type)


def fill_sector_select(dialog):
    dialog.field1Select.clear()
    sector_type = 1
    if dialog.questionSelect.currentData() == IndustrialQuestion.CO2:
        sector_type = 2
    sectors = get_sector_list(sector_type)
    for sector in sectors:
        dialog.field1Select.addItem(sector.description, sector)
    dialog.adjustSize()


def set_size_policy(field):
    pol = field.sizePolicy()
    pol.setRetainSizeWhenHidden(True)
    field.setSizePolicy(pol)
