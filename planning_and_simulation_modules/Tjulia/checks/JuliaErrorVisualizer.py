from PyQt5.QtWidgets import QMessageBox


class JuliaErrorVisualizer:

    def __init__(self, report):
        self.report = report
        self.NO_ERRORS_REPORT = "Julia output files: no error found."

    def visualize(self):
        msgBox = QMessageBox()
        s = "\n"
        i = 0
        for error in self.report.keys():
            s = s + "ERROR IN FILE \"" + str(error) + "\": " + str(self.report[error]) + "\n"
            i = i + 1
            if i > 20:
                s = s + "\n... and other " + str(len(list(self.report.keys())) - i) + " errors."
                break
        if len(list(self.report.keys())) == 0:
            print(self.NO_ERRORS_REPORT)
        else:
            msgBox.setText("Problems found!")
            msgBox.setInformativeText("List of problems: " + s)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            ret = msgBox.exec()

    def set_report(self, report):
        self.report = report
