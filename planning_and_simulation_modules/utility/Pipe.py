from PyQt5.QtWidgets import QListWidgetItem
import traceback


class Pipe(QListWidgetItem):
    diam_attribute = "diameter"
    status_attribute = "Status"

    def __init__(self, feature, main_attribute="", parent=None):
        super(Pipe, self).__init__(parent)

        self.diameter = None
        self.feature = feature
        self.status = feature.attribute(self.status_attribute)
        self.main_attribute = main_attribute

        self.auto_set_text()

    def set_status(self, value):
        self.status = value

    def auto_set_text(self):
        bad_luck = True
        if self.diameter is not None:
            try:
                text = self.feature.attribute(self.main_attribute) + "\t| D = {} cm".format(round(self.diameter), 2)
                bad_luck = False
            except Exception as e:
                # print(traceback.print_tb(e.__traceback__))
                pass
        if bad_luck:
            try:
                diameter = float(self.feature.attribute(self.diam_attribute))
                self.diameter = diameter
            except Exception as e:
                # print(traceback.print_tb(e.__traceback__))
                diameter = None
            if diameter is None:
                text = self.feature.attribute(self.main_attribute) + "\t| D = ??? cm"
            else:
                text = self.feature.attribute(self.main_attribute) + "\t| D = {} cm".format(round(diameter), 2)
        self.setText(text)

    def set_diameter(self, diameter):
        try:
            diameter = float(diameter)
        except Exception as e:
            # print(traceback.print_tb(e.__traceback__))
            return None

        # if self.set_feature_diameter(diameter):
        self.diameter = diameter
        self.auto_set_text()
        # return self.feature
        # else:
        return None

    def set_feature_diameter(self, diameter):
        try:
            self.feature.setAttribute(self.feature.fieldNameIndex(self.diam_attribute), diameter)
            return True
        except Exception as e:
            # print(traceback.print_tb(e.__traceback__))
            return False

