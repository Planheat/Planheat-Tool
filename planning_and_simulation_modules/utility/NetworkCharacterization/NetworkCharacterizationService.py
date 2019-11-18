from ..CharacterizationUIutils import CharacterizationUIutils
import os.path
from PyQt5.QtGui import QIcon, QPixmap


class NetworkCharacterizationService:

    def __init__(self, ui):
        ui.network_input_reset.clicked.connect(lambda: CharacterizationUIutils.reset_network_input(ui))
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../",
                                 "icons", "reload.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        ui.network_input_reset.setIcon(icon)
