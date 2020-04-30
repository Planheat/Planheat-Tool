from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QComboBox, QLabel, QPushButton, QMessageBox, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

from .city.src.FileManager import FileManager

from datetime import datetime

import traceback


import os
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui', 'load_save_dialog.ui'))


class LoadInterface(QtWidgets.QDockWidget, FORM_CLASS):
    effectiveSave = pyqtSignal(str)
    effectiveLoad = pyqtSignal(str)

    def __init__(self, work_folder=None, parent=None):
        """Constructor."""
        super(LoadInterface, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        save_folder_name: str = "Save"
        self.save_folder_path = os.path.abspath(os.path.join(work_folder, save_folder_name))
        print("loading LoadInterface:", os.path.join(work_folder, save_folder_name))
        if not os.path.isdir(work_folder):
            print("LoadInterface.__init__(): work_folder does not exist:", work_folder)
            return
        if not os.path.isdir(os.path.abspath(os.path.join(work_folder, save_folder_name))):
            print("LoadInterface.__init__(): creating:", os.path.abspath(os.path.join(work_folder, save_folder_name)))
            os.makedirs(os.path.abspath(os.path.join(work_folder, save_folder_name)), exist_ok=True)
        self.save_file_extension: str = ".json"
        self.file_manager = FileManager(work_folder=os.path.abspath(os.path.join(work_folder, save_folder_name)))
        self.update_combo_box()
        load_file: QComboBox = self.loadFile
        load_file.currentTextChanged.connect(self.on_combo_box_change)
        self.cancel.clicked.connect(self.cancel_clicked_event_handler)
        self.save.clicked.connect(self.save_clicked_event_handler)
        self.load.clicked.connect(self.load_clicked_event_handler)
        self.delete_2.clicked.connect(self.delete_clicked_event_handler)
        self.invalidFileNameWarning.hide()
        self.progressBar.hide()
        self.fileName.textChanged.connect(self.check_file_name)
        self.load: QPushButton = self.load
        self.save: QPushButton = self.save
        self.caller: str = None
        self.add_buttons_icon()

    def cancel_clicked_event_handler(self):
        self.close()

    def ok_clicked_event_handler(self):
        self.data_emitter.emit(self.get_state())
        self.cancel.clicked.emit()

    def update_combo_box(self):
        try:
            self.file_manager.import_and_fill_combo_box(self.loadFile, ".json")
            self.update_label()
        except Exception as e:
            print("LoadInterface.update_combo_box(): exception", e)

    def update_label(self):
        try:
            load_file: QComboBox = self.loadFile
            file_name: str = load_file.currentText()
            file_path: str = self.file_manager.get_path_from_file_name(file_name,
                                                                       -5,
                                                                       [self.file_manager.work_folder])
            if file_path is None:
                print("LoadInterface.update_label(): file path is None")
                return
            if not os.path.isfile(file_path):
                print("LoadInterface.update_label(): file path is not a file")
                return
            info = os.stat(file_path)
            label_created_on: QLabel = self.labelCreatedOn
            label_last_edit_on: QLabel = self.labelLastEditOn
            label_folder: QLabel = self.labelFolder
            label_created_on.setText("Created on: " + str(datetime.fromtimestamp(int(info.st_ctime))))
            label_last_edit_on.setText("Last edit: " + str(datetime.fromtimestamp(int(info.st_mtime))))
            location: str = str(file_path)
            mx: int = 68
            label_folder.setText("Location: " + location if len(location) < mx
                                 else (location[0:29] + " ... " + location[-34:]))
        except Exception:
            traceback.print_exc()

    def on_combo_box_change(self, value: str):
        self.update_label()

    def save_clicked_event_handler(self):
        filename: QLabel = self.fileName
        if self.file_manager.check_file_name(filename.text()):
            self.autosave(file_name=filename.text())

    def autosave(self, file_name="Autosave"):
        if not os.path.isfile(os.path.join(self.file_manager.work_folder, file_name + ".json")):
            self.effectiveSave.emit(file_name)
            self.close()
        else:
            index = 2
            while True:
                new_file_name = file_name + "_" + str(index)
                if not os.path.isfile(os.path.join(self.file_manager.work_folder, new_file_name + ".json")):
                    break
                index += 1
            self.effectiveSave.emit(new_file_name)


    def load_clicked_event_handler(self):
        load_file: QComboBox = self.loadFile
        file_path = self.file_manager.get_path_from_file_name(load_file.currentText(), -5,
                                                              search_folders=[self.file_manager.work_folder])
        if file_path is not None and os.path.isfile(file_path):
            self.effectiveLoad.emit(load_file.currentText() + ".json")
            self.hide()

    def check_file_name(self, file_name: str):
        warning: QLabel = self.invalidFileNameWarning
        if not self.file_manager.check_file_name(file_name):
            warning.show()
        else:
            warning.hide()

    def show_dialog(self, caller: str):
        self.caller = caller
        self.update_combo_box()
        self.show()

    def progress_bar_update(self, value: int, maximum: int, show: bool):
        progress_bar: QProgressBar = self.progressBar
        if show:
            progress_bar.show()
        else:
            progress_bar.hide()
        if value >= maximum or value <= 0:
            progress_bar.hide()
            return
        progress_bar.setValue(value)
        progress_bar.setMaximum(maximum)
        progress_bar.setMinimum(0)

    def delete_clicked_event_handler(self):
        try:
            load_file: QComboBox = self.loadFile
            if load_file.currentText() is None or load_file.currentText() == "":
                return
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Warning)
            main_text = "You are about to delete thi saved data:\n" + load_file.currentText() + "\nThis action " \
                                                                                                "cannot be restored."
            main_text = main_text + "\nAre you sure to continue?"
            msgBox.setText(main_text)
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Ok)
            response = msgBox.exec()
            print("LoadInterface.delete_clicked_event_handler(). response:", response)
            if response == QMessageBox.Cancel:
                return
            file = self.file_manager.get_path_from_file_name(load_file.currentText(), -5,
                                                             search_folders=[self.file_manager.work_folder])
            FileManager.delete_file(file)
            zip_file_path = os.path.join(os.path.dirname(file), "data", load_file.currentText() + ".zip")
            if os.path.isfile(zip_file_path):
                FileManager.delete_file(zip_file_path)
            self.update_combo_box()
        except Exception:
            traceback.print_exc()

    def add_buttons_icon(self):
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons", "garbage.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.delete_2.setIcon(icon)
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons", "import.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.load.setIcon(icon)
        icon = QIcon()
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons", "save.png")
        icon.addPixmap(QPixmap(icon_path), QIcon.Normal, QIcon.Off)
        self.save.setIcon(icon)
