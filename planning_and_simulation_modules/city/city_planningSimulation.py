
import os
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from .src.FileManager import FileManager
from .step01 import CityStep01Dialog
from .step2 import CityStep2Dialog
from .step3 import CityStep3Dialog
from .City_planning import CityPlanning
from .src.StepConnector import StepConnector
from .city_simulation import CitySimulation
from ..save_utility.save_city import SaveCityTab
from ..save_utility.LoadCity import LoadCity

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'city.ui'))


class PlanningAndSimulationCity(QtWidgets.QDialog, FORM_CLASS):
    city_closing_signal = pyqtSignal()

    def __init__(self, iface, first_start=False, work_folder=None, parent=None):
        """Constructor."""
        super(PlanningAndSimulationCity, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface = iface
        self.work_folder = work_folder

        self.city_planning_first_start = first_start
        self.Cstep01_first_start = first_start
        self.Cstep2_first_start = first_start
        self.Cstep3_first_start = first_start
        self.city_first_start = first_start
        self.citySim_first_start = first_start

        self.city = None
        self.city_planning = None
        self.citySim = None
        self.Cstep01 = None
        self.Cstep2 = None
        self.Cstep3 = None
        self.init_city_interfaces()
        self.btnCitySimulation.setEnabled(False)

        #self.save_routine_initialized = False

        self.step_connector = StepConnector(self.Cstep01, self.Cstep2)

        self.Cstep01.refresh_step2.connect(self.step_connector.data_transfer_step01_step2)

    def closeEvent(self, event):
        self.closeCity()
        event.accept()

    def onCloseCityPlanningPlugin(self):
        print("Closing City Planning")
        self.show()

    def onCloseCitySimulationPlugin(self):
        print("Closing City Simulation")
        self.show()

    def init_city_interfaces(self):

        file_dir_path = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(file_dir_path, "..", "icon.png")
        self.setWindowIcon(QIcon(icon_path))

        if self.city_planning_first_start:
            self.city_planning = CityPlanning()
            self.city_planning.CityDialog_closing_signal.connect(self.onCloseCityPlanningPlugin)
            self.city_planning.btn_step01.clicked.connect(self.openCStep01)
            self.city_planning.btn_step2.clicked.connect(self.openCStep2)
            self.city_planning.btn_step3.clicked.connect(self.openCStep3)
            self.city_planning.setWindowIcon(QIcon(icon_path))
            self.city_planning_first_start = False

        if self.Cstep01_first_start:
            self.Cstep01 = CityStep01Dialog(self.iface, work_folder=self.work_folder)
            self.Cstep01.step01_closing_signal.connect(lambda: self.city_planning.show())
            self.Cstep01.hide()
            self.Cstep01.ok.clicked.connect(self.Cstep01.closeStep01)
            self.Cstep01.step01_closing_signal.connect(self.openCity_planning)
            self.Cstep01_first_start = False
            #self.Cstep01.send_sources.connect(self.citySim.load_source_base)
            self.Cstep01.ok.clicked.connect(self.city_planning.button2_change)
            self.Cstep01.setWindowIcon(QIcon(icon_path))

        if self.Cstep2_first_start:
            self.Cstep2 = CityStep2Dialog(self.iface)
            self.Cstep2.step2_closing_signal.connect(lambda: self.city_planning.show())
            self.Cstep2.hide()
            self.Cstep2.ok.clicked.connect(self.Cstep2.closeStep2)
            self.Cstep2.step2_closing_signal.connect(self.openCity_planning)
            self.Cstep2_first_start = False
            self.Cstep2.ok.clicked.connect(self.city_planning.button3_change)
            self.Cstep2.setWindowIcon(QIcon(icon_path))


        if self.Cstep3_first_start:
            self.Cstep3 = CityStep3Dialog(self.iface)
            self.Cstep3.step3_closing_signal.connect(lambda: self.city_planning.show())
            self.Cstep3.hide()
            self.Cstep3.ok.clicked.connect(self.Cstep3.closeStep3)
            self.Cstep3.step3_closing_signal.connect(self.close_step3)
            self.Cstep3_first_start = False
            self.Cstep2.send.connect(self.Cstep3.load_from_step2)
            self.Cstep3.setWindowIcon(QIcon(icon_path))

        if self.citySim_first_start:
            self.citySim = CitySimulation(self.iface)
            self.citySim.simulation_closing_signal.connect(self.onCloseCitySimulationPlugin)
            self.Cstep01.citySim = self.citySim
            self.citySim.hide()
            self.citySim.simulation_closing_signal.connect(self.citySim.closeSimulation)
            self.citySim_first_start = False
            self.Cstep3.send_toSim.connect(self.citySim.load_from_ste3)
            self.Cstep2.send_corrected_ued.connect(self.citySim.calculationKPIs)
            self.citySim.btn_ok.clicked.connect(self.citySim.closeSimulation)
            self.citySim.setWindowIcon(QIcon(icon_path))


        work_folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                               "DefaultSaveFolder"))
        self.save_routine = SaveCityTab(folder=work_folder)
        self.save_routine.Cstep01 = self.Cstep01
        self.save_routine.Cstep2 = self.Cstep2
        self.save_routine.Cstep3 = self.Cstep3
        self.save_routine.citySim = self.citySim
        self.citySim.btn_save.clicked.connect(self.save_routine.save_steps)

        self.load_routine = LoadCity(folder=work_folder)
        self.load_routine.Cstep01 = self.Cstep01
        self.load_routine.Cstep2 = self.Cstep2
        self.load_routine.Cstep3 = self.Cstep3
        self.load_routine.citySim = self.citySim

        self.save_routine.saved_done.connect(self.load_routine.saved_done)

        self.Cstep01.load_city = self.load_routine

    def close_step3(self):
        self.show()
        self.button_change()



    def openCity_planning(self):
        if self.city_planning is not None:
            self.city_planning.show()
        self.hide()

    def openCStep01(self):
        if self.Cstep01 is not None:
            self.Cstep01.show()
        if self.city_planning is not None:
            self.city_planning.hide()

    def openCStep2(self):
        if self.Cstep2 is not None:
            self.Cstep2.show()
        if self.city_planning is not None:
            self.city_planning.hide()

    def openCStep3(self):
        if self.Cstep3 is not None:
            self.Cstep3.show()
        if self.city_planning is not None:
            self.city_planning.hide()

    def openCity_simulation(self):
        if self.citySim is not None:
            self.citySim.show()
        self.hide()

    def closeCity(self):
        self.hide()
        self.city_closing_signal.emit()

    def button_change(self):
        self.btnCitySimulation.setEnabled(True)


