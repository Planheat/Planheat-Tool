import os
import os.path
from .JuliaErrorVisualizer import JuliaErrorVisualizer


class JuliaOutputChecker:

    def __init__(self, dr):
        self.work_directory = dr
        self.file_starts_string = "Result_"
        self.file_ends_string = ".csv"
        self.h8760 = 8760
        self.report = {}
        self.REPORT_ERROR_NOT_FLOAT = "CAN'T_CONVERT_TO_FLOAT"
        self.REPORT_ERROR_NOT_A_NUMBER = "CONTENT IS Nan"

    def check(self):
        if not os.path.isdir(self.work_directory):
            return
        for f in os.listdir(self.work_directory):
            file = os.path.join(self.work_directory, f)
            if os.path.isfile(file):
                if str(f).startswith(self.file_starts_string) and str(f).endswith(self.file_ends_string):
                    with open(file, "r") as fr:
                        for i in range(self.h8760):
                            line = fr.readline()
                            try:
                                line = float(line)
                            except:
                                self.add_to_report(f, self.REPORT_ERROR_NOT_FLOAT)
                                break
                            if not line == line:
                                self.add_to_report(f, self.REPORT_ERROR_NOT_A_NUMBER)
                                break

    def visualize(self):
        julia_error_visualizer = JuliaErrorVisualizer(self.report)
        julia_error_visualizer.visualize()

    def add_to_report(self, file, error):
        self.report[str(file)] = error

    def clear_report(self):
        self.report = {}

    def get_report(self):
        return self.report

    def set_folder(self, folder):
        self.work_directory = folder



