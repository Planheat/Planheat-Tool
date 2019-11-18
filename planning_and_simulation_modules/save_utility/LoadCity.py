from .LoadScenario import LoadScenario
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject
import os
import os.path


class LoadCity(LoadScenario):
    Cstep01 = None
    Cstep2 = None
    Cstep3 = None
    Cstepsim = None

    def __init__(self, folder=None):
        LoadScenario.__init__(self, folder)


    def refresh_file_selection_combo_box(self,):
        self.file_manager.import_and_fill_combo_box(self.Cstep01.comboBox, ".json")


    def run(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        main_text = "Load and override data?"
        msgBox.setText(main_text)
        msgBox.setInformativeText("All the unsaved data wil be lost. Continue?")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        r = msgBox.exec()
        if r == QMessageBox.Ok:

                self.load(self.Cstep01.comboBox.currentText() + ".json")
                self.load_step01()
                self.load_step2()
                self.load_step3()
                self.load_sim()



    def saved_done(self):
        self.refresh_file_selection_combo_box()


    def load_step01(self):
        self.fill_table_widget_item(self.Cstep01.table_sd_HeDHW, name="step1heat")
        self.fill_table_widget_item(self.Cstep01.tb_HeDHW_source,name="step1source")
        self.fill_table_widget_item(self.Cstep01.table_fec_baseline)
        self.set_radioButton_state(self.Cstep01.radioButton, self.get_data("residenziario"))
        self.set_radioButton_state(self.Cstep01.radioButton_2, self.get_data("terziario"))

        #self.fill_table_widget_item(self.Cstep01.table_sd_heating)

        self.fill_table_widget_item(self.Cstep01.table_sd_cool, name="step1Cool")
        self.fill_table_widget_item(self.Cstep01.table_cool_source, name="step1CoolSource")
        self.fill_table_widget_item(self.Cstep01.table_KPIsEn, name="step1En")


        self.fill_double_spin_box(self.Cstep01.weight_plan, self.get_data("weight_plan"))
        self.fill_list_widget_item(self.Cstep01.energy_criteria)
        self.fill_list_widget_item(self.Cstep01.environmental_criteria)
        self.fill_list_widget_item(self.Cstep01.economic_criteria)
        self.fill_list_widget_item(self.Cstep01.social_criteria)

        self.fill_table_widget_item(self.Cstep01.tableWidget, name="heatH")
        self.fill_table_widget_item(self.Cstep01.tableWidget_HeatingM, name="heatM")
        self.fill_table_widget_item(self.Cstep01.tableWidget_heatinhH, name="heat")
        self.fill_table_widget_item(self.Cstep01.tableWidget_dhw, name="heatDhw")
        self.fill_table_widget_item(self.Cstep01.tableWidget_cool, name="heatCool")

    def load_step2(self):
        self.fill_table_widget_item(self.Cstep2.table_HeDHW_source_targ)
        self.fill_table_widget_item(self.Cstep2.table_sd_target)
        self.fill_table_widget_item(self.Cstep2.table_sd_cool_targ)
        self.fill_table_widget_item(self.Cstep2.table_cool_source)
        self.fill_table_widget_item(self.Cstep2.table_dhw_source_targ)
        self.fill_table_widget_item(self.Cstep2.table_cool)
        self.fill_double_spin_box(self.Cstep2.demoFactor_dhw, self.get_data("ued_demograic_factor"))
        self.fill_double_spin_box(self.Cstep2.envelope_dhw, self.get_data("ued_corrective_factor"))
        self.fill_double_spin_box(self.Cstep2.demoFact_cool, self.get_data("ued_demograic_factor_cool"))
        self.fill_double_spin_box(self.Cstep2.envelope_cool, self.get_data("ued_corrective_factor_cool"))
        self.fill_double_spin_box(self.Cstep2.increase_cool, self.get_data("ued_icrease_factor_cool"))

        self.Cstep2.calculate_dhw.clicked.emit()
        self.Cstep2.btn_calculate_cool.clicked.emit()
        self.Cstep2.btn_ued.clicked.emit()
        self.Cstep2.pushButton.clicked.emit()
        self.Cstep2.btn_ued_cool.clicked.emit()

    def load_step3(self):

        self.fill_table_widget_item(self.Cstep3.sbs_hdhw_Source)
        self.fill_table_widget_item(self.Cstep3.sbs_cool_source)
        self.fill_table_widget_item(self.Cstep3.dist_hdhw_source)
        self.fill_table_widget_item(self.Cstep3.dist_cool_source)


    def load_sim(self):
        self.fill_table_widget_item(self.citySim.sim_sbs_hdhw_Source)
        self.fill_table_widget_item(self.citySim.sim_sbs_cool_source)
        self.fill_table_widget_item(self.citySim.dist_heat_source)
        self.fill_table_widget_item(self.citySim.dist_cool_net)
        self.fill_table_widget_item(self.citySim.table_source)
        self.fill_table_widget_item(self.citySim.table_sutil)
        self.fill_table_widget_item(self.citySim.tableWidget_10)
        self.fill_table_widget_item(self.citySim.table_sutil)
        self.fill_table_widget_item(self.citySim.table_source)

        self.fill_double_spin_box(self.citySim.sbs_heat, self.get_data("share_heating"))
        self.fill_double_spin_box(self.citySim.sbs_dhw, self.get_data("share"))
        self.fill_double_spin_box(self.citySim.sbs_heat_h, self.get_data("heating_hours"))
        self.fill_double_spin_box(self.citySim.sbs_dhw_h, self.get_data("dhw_hours"))
        self.fill_double_spin_box(self.citySim.sbs_cool_h, self.get_data("cool_hours"))
        self.fill_double_spin_box(self.citySim.period, self.get_data("period"))
        self.fill_double_spin_box(self.citySim.rate, self.get_data("rate"))

        self.fill_double_spin_box(self.citySim.spinBox_9, self.get_data("gross_area"))
        self.fill_double_spin_box(self.citySim.share_heat, self.get_data("share_heat"))
        self.fill_double_spin_box(self.citySim.share, self.get_data("share"))
        self.fill_double_spin_box(self.citySim.eff, self.get_data("eff"))
        self.fill_double_spin_box(self.citySim.btn_eff, self.get_data("btn_eff"))
        self.fill_double_spin_box(self.citySim.leng, self.get_data("leng"))
        self.fill_double_spin_box(self.citySim.btn_len, self.get_data("btn_len"))

        self.citySim.btn_fec.clicked.emit()
        self.citySim.btn_fec_afec.clicked.emit()
        self.citySim.DHCN_heating_fec.clicked.emit()
        self.citySim.DHCN_net_losses.clicked.emit()
        self.citySim.fec_cool_dist.clicked.emit()
        self.citySim.dh_loss_dist.clicked.emit()
        self.citySim.btn_KPIsFuture.clicked.emit()