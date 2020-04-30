import os
import os.path
from PyQt5.QtWidgets import QTableWidgetItem, QComboBox
from PyQt5.QtGui import QColor, QPixmap, QIcon, QBrush
from PyQt5.QtCore import Qt
from .qt_utils import make_table_not_editable
from ..config import tableConfig


class ImportManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.precision = 1.0

    def load_DMM_output_to_table(self, file, heating_dhw, cooling, fec_table, summary_table_H_DHW,
                                 summary_table_C):
        precision = self.precision
        file_path = self.file_manager.get_path_from_file_name(file)
        if file_path is None:
            return
        input_dict = self.file_manager.load_json(file_path)
        self.fill_table_from_tree_dict(input_dict, heating_dhw, cooling, precision)
        try:
            self.fill_summary_table(input_dict["fec_baseline"], fec_table)
        except:
            pass
        try:
            self.fill_total_table([input_dict["summary"]["lineEditTotal_HEATING_SBS"],
                              input_dict["summary"]["lineEditTotal_HEATING_DHN"]],
                              summary_table_H_DHW, precision)
        except:
            pass
        try:
            self.fill_total_table([input_dict["summary"]["lineEditCOOLING_SBS"],
                              input_dict["summary"]["lineEditCOOLING_DCN"]],
                              summary_table_C, precision)
        except:
            pass

    def fill_total_table(self, input_list, table, precision):
        table.clearContents()
        table.setItem(1, 0, QTableWidgetItem(str(input_list[0][0])))
        table.setItem(1, 1, QTableWidgetItem(str(input_list[0][1]) + " %"))
        table.setItem(2, 0, QTableWidgetItem(str(input_list[1][0])))
        table.setItem(2, 1, QTableWidgetItem(str(input_list[1][1]) + " %"))
        table.setItem(3, 0, QTableWidgetItem(str(round(input_list[0][0] + input_list[1][0], 2))))
        total_percent = QTableWidgetItem(str(round(input_list[0][1] + input_list[1][1], 2)) + " %")
        if input_list[0][1] + input_list[1][1] < 100.0 + precision and input_list[0][1] + input_list[1][
                                                                       1] > 100.0 - precision:
            total_percent.setForeground(QColor(0, 255, 0))
            icon = QIcon()
            icon_path = os.path.join(self.file_manager.city_plugin_folder, "../", "images",
                                     "green_check.png")
            icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
            total_percent.setIcon(icon)
        else:
            total_percent.setForeground(QColor(255, 0, 0))
            icon = QIcon()
            icon_path = os.path.join(self.file_manager.city_plugin_folder, "../", "images",
                                     "red_cross.png")
            icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
            total_percent.setIcon(icon)
        table.setItem(3, 1, total_percent)
        make_table_not_editable(table)

    def fill_table_from_tree_dict(self, input_dict, heating_dhw,  cooling, precision):
        heating_dhw.clearContents()

        cooling.clearContents()
        table_heating = self.get_table_form(input_dict["treeWidgetHEATING_DHW"])
        table_cooling = self.get_table_form(input_dict["treeWidgetCOOLING"])

        self.fill_table(heating_dhw, table_heating, [4], 5, tableConfig.data_rows)

        self.fill_table(cooling, table_cooling, [2], 3, tableConfig.data_rows_cool)

        self.validate_import_tables([heating_dhw, cooling], 1, precision)

    def validate_import_tables(self, qt_tables, col, precision):
        ncol=col
        for qt_table in qt_tables:
            for i in range(qt_table.rowCount()):
                if qt_table.verticalHeaderItem(i).text() == "Total":
                    try:
                        total_share = float(qt_table.item(i, ncol).text()[0:-2])
                    except (ValueError, AttributeError):
                        if qt_table.item(i, 1) is None:
                            total_share = None
                        else:
                            total_share = 100.0 + precision + 1.0
                    if total_share is not None:
                        if total_share > 100.0 + precision or total_share < 100.0 - precision:
                            qt_table.item(i, 1).setForeground(QColor(255, 0, 0))
                            icon = QIcon()
                            icon_path = os.path.join(self.file_manager.city_plugin_folder, "../", "images",
                                                     "red_cross.png")
                            icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
                            qt_table.item(i, 1).setIcon(icon)
                        else:
                            qt_table.item(i, 1).setForeground(QColor(0, 255, 0))
                            icon = QIcon()
                            icon_path = os.path.join(self.file_manager.city_plugin_folder, "../", "images",
                                                     "green_check.png")
                            icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
                            qt_table.item(i, ncol).setIcon(icon)

    def fill_table(self, qt_table, input_list, columns, share, data_rows):
        last_bold = ""
        last = ""
        empty_table_widget_item = QTableWidgetItem()
        empty_table_widget_item.setFlags(Qt.ItemIsEnabled)
        colored_empty_table_item = QTableWidgetItem()
        colored_empty_table_item.setBackground(QBrush(QColor(232, 232, 232)))
        colored_empty_table_item.setFlags(Qt.ItemIsEnabled)
        for i in range(qt_table.rowCount()):
            vertical_header_item = qt_table.verticalHeaderItem(i)
            if vertical_header_item is not None:
                if vertical_header_item.font().bold():
                    last_bold = vertical_header_item.text()
                    if i not in data_rows and i > 0 and not i > data_rows[-1]:
                        item = colored_empty_table_item.clone()
                    else:
                        item = empty_table_widget_item.clone()
                    qt_table.setItem(i, 0, item)
                    qt_table.setItem(i, 1, item.clone())
                    qt_table.setItem(i, 2, item.clone())
                    qt_table.setItem(i, 3, item.clone())
                    continue
                else:
                    last = vertical_header_item.text()
                    tot_dem = 0
                    tot_share = 0
                    for element in input_list:
                        if element[0].upper() == last_bold.upper() and element[1].upper() == last.upper():
                            try:
                                for column in columns:
                                    tot_dem += float(element[column])
                                    tot_share += float(element[share])
                            except ValueError:
                                pass
                    if not tot_dem == 0:
                        qt_table.setItem(i, 0, QTableWidgetItem(str(round(tot_dem, 2))))
                        qt_table.setItem(i, 1, QTableWidgetItem(str(round(tot_share, 2)) + " %"))
                    else:
                        qt_table.setItem(i, 0, empty_table_widget_item.clone())
                        qt_table.setItem(i, 1, empty_table_widget_item.clone())

        total = 0
        total_share = 0
        for i in range(qt_table.rowCount()):
            try:
                total += float(qt_table.item(i, 0).text())
            except (ValueError, AttributeError):
                pass
            try:
                total_share += float(qt_table.item(i, 1).text()[0:-2])
            except (ValueError, AttributeError):
                pass
            if qt_table.verticalHeaderItem(i).text() == "Total":
                qt_table.setItem(i, 0, QTableWidgetItem(str(round(total, 2))))
                qt_table.setItem(i, 1, QTableWidgetItem(str(round(total_share, 2)) + " %"))
        make_table_not_editable(qt_table)

        # for i in range(qt_table.rowCount()):
        #     if not qt_table.verticalHeaderItem(i).font().bold():
        #         try:
        #             value = float(qt_table.item(i, 0).text())
        #             if not total == 0:
        #                 qt_table.setItem(i, 1, QTableWidgetItem(str(round((value/total)*100, 2)) + " %"))
        #         except (ValueError, AttributeError):
        #             pass

    def get_table_form(self, input_dict):
        i = 0
        table_output = []
        while True:
            try:
                source = input_dict["0_" + str(i)]["data"][0]
                row = input_dict["0_" + str(i)]
            except KeyError:
                break
            j = 0
            while True:
                try:
                    tech = row["1_" + str(j)]["data"][0]
                    dem = row["1_" + str(j)]["data"][1]
                    dem2 = row["1_" + str(j)]["data"][2]
                    tot = row["1_" + str(j)]["data"][3]
                    share = row["1_" + str(j)]["data"][4]
                    table_output.append([source, tech, dem, dem2, tot, share])
                except KeyError:
                    break
                j += 1
            i += 1
        return table_output

    def upload_fec_baseline(self, file):
        if isinstance(file, QComboBox):
            file = file.currentText()
        file_path = self.file_manager.get_path_from_file_name(file)
        if file_path is None:
            return
        input_dict = self.file_manager.load_json(file_path)
        try:
            dict_to_return = input_dict["fec_baseline"]
        except:
            dict_to_return = None
        return dict_to_return

    def fill_summary_table(self, input_dict, table):
        table.clearContents()
        for i in range(table.rowCount()):
            try:
                value = input_dict[table.verticalHeaderItem(i).text()]
            except KeyError:
                continue
            table.setItem(i, 0, QTableWidgetItem(str(round(value, 2))))
        make_table_not_editable(table)
