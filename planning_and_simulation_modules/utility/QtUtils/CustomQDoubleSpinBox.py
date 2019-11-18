from PyQt5.QtWidgets import QDoubleSpinBox


class CustomQDoubleSpinBox(QDoubleSpinBox):

    def __init__(self):
        super(QDoubleSpinBox, self).__init__()

    def textFromValue(self, value):
        text = QDoubleSpinBox.textFromValue(value)
        return text.replace(QLocale().decimalPoint(), QLatin1Char('.'))

    def valueFromText(self, text):
        return QDoubleSpinBox(QString(text).replace(QLatin1Char('.'), QLocale().decimalPoint()))

    self.doubleSpinBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))

