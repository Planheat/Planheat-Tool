from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

def update_KPIs_visualization_tab(table_KPIsEn,energy_criteria,table_KPIsEnv,environmental_criteria,table_KPIsEco,economic_criteria,
                                  table_KPIsSo,social_criteria):

        criterion_to_rows = {"EN1": [1, 2, 3, 4, 5, 6],
                             "EN3": [7, 8, 9, 10, 11],
                             "EN4": [12, 13, 14, 15, 16],
                             "EN5": [17, 18, 19, 20, 21],
                             "EN6": [22, 23, 24, 25, 26],
                             "EN7": [27, 28, 29, 30, 31],
                             "EN13": [32, 33],
                             "EN14": [34, 35],
                             "ENV1": [1, 2, 3, 4, 5, 6, 7, 8],
                             "ECO1": [1, 2, 3, 4],
                             "ECO2": [5, 6, 7],
                             "ECO3": [8],
                             "ECO4": [9],
                             "SO1": [1, 2],
                             "SO2": [3, 4],
                             "SO3": [5, 6]
                             }

        hide_visualization_rows(table_KPIsEn, table_KPIsEnv, table_KPIsEco, table_KPIsSo)

        for widgets in [[table_KPIsEn, energy_criteria], [table_KPIsEnv, environmental_criteria],
                        [table_KPIsEco, economic_criteria], [table_KPIsSo, social_criteria]]:
            for criteria in criterion_to_rows.keys():
                if chech_criterion_is_selected(widgets[1], criteria):
                    for row in criterion_to_rows[criteria]:
                        widgets[0].showRow(row)



def chech_criterion_is_selected(widget, criteria):
    for i in range(widget.count()):
        texts = widget.item(i).text().split(':')
        if not (len(texts) > 0):
             continue
        if criteria in texts[0]:
            return True
    return False

def hide_visualization_rows(table_KPIsEn,table_KPIsEnv,table_KPIsEco, table_KPIsSo):
        for table in [table_KPIsEn,table_KPIsEnv,table_KPIsEco, table_KPIsSo]:
            for i in range(1, table.rowCount()):
                table.hideRow(i)


def tab_not_editable(table,ncol):
        for i in range(table.rowCount()):
                if table.item(i, ncol) is None:
                    empty_table_widget_item = QTableWidgetItem("")
                    empty_table_widget_item.setFlags(Qt.ItemIsEnabled)
                    table.setItem(i, ncol, empty_table_widget_item)
                else:
                    table.item(i, ncol).setFlags(Qt.ItemIsEnabled)

