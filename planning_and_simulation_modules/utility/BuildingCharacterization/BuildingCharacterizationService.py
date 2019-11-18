from ..CharacterizationUIutils import CharacterizationUIutils
import os.path
from PyQt5.QtGui import QIcon, QPixmap


class BuildingCharacterizationService:

    def __init__(self, ui):
        ui.heating_input_reset.clicked.connect(lambda: CharacterizationUIutils.reset_heating_input(ui))
        ui.cooling_input_reset.clicked.connect(lambda: CharacterizationUIutils.reset_cooling_input(ui))
        ui.dhw_input_reset.clicked.connect(lambda: CharacterizationUIutils.reset_dhw_input(ui))

        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../",
                                 "icons", "reload.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        ui.heating_input_reset.setIcon(icon)
        ui.cooling_input_reset.setIcon(icon)
        ui.dhw_input_reset.setIcon(icon)
