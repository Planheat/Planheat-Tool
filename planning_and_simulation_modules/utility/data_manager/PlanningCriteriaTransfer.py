from PyQt5.QtWidgets import QTableWidget, QListWidget


class PlanningCriteriaTransfer:

    def __init__(self, en: QListWidget, env: QListWidget, eco: QListWidget, so: QListWidget):
        self.en = en
        self.env = env
        self.eco = eco
        self.so = so
        self.en_table = None
        self.env_table = None
        self.eco_table = None
        self.so_table = None

    def set_target_tables(self, en_table: QTableWidget, env_table: QTableWidget, eco_table: QTableWidget,
                          so_table: QTableWidget):
        self.en_table = en_table
        self.env_table = env_table
        self.eco_table = eco_table
        self.so_table = so_table

    def push_districtSim_table_update(self, check_criterion_is_selected):
        if not self.check_all_exist():
            return
        criterion_to_rows = {"EN1": [1, 2, 3, 4, 5, 6, 7],
                             "EN2": [8, 9, 10, 11, 12, 13, 14],
                             "EN3": [15, 16, 17, 18, 19, 20, 21],
                             "EN4": [22, 23, 24, 25, 26],
                             "EN5": [27, 28, 29, 30, 31],
                             "EN6": [32, 33, 34, 35, 36],
                             "EN7": [37, 38, 39, 40, 41],
                             "EN9": [42, 43],
                             "EN11": [44, 45, 46],
                             "EN12": [47, 48, 49],
                             "EN13a": [50, 51, 52, 53],
                             "EN13b": [54, 55, 56],
                             "EN14a": [57, 58, 59],
                             "EN14b": [60, 61],
                             "EN15": [62, 63, 64],
                             "ENV1": [1, 2, 3, 4, 5, 6],
                             "ENV2": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                             "ENV3": [25, 26, 27],
                             "ECO1": [1, 2, 3, 4],
                             "ECO2": [5, 6, 7],
                             "ECO3": [8],
                             "ECO4": [9],
                             "SO1": [1, 2, 3],
                             "SO2": [4, 5, 6],
                             "SO3": [7, 8, 9]
                             }
        for table in [self.en_table, self.env_table, self.eco_table, self.so_table]:
            for i in range(1, table.rowCount()):
                table.hideRow(i)
        for widgets in [[self.en_table, self.en], [self.env_table, self.env],
                        [self.eco_table, self.eco], [self.so_table, self.so]]:
            for criteria in criterion_to_rows.keys():
                if check_criterion_is_selected(widgets[1], criteria):
                    for row in criterion_to_rows[criteria]:
                        widgets[0].showRow(row)

    def check_all_exist(self):
        if self.en is None or self.env is None or self.eco is None or self.so is None:
            return False
        if self.en_table is None:
            return False
        if self.env_table is None:
            return False
        if self.eco_table is None:
            return False
        if self.so_table is None:
            return False
        return True
