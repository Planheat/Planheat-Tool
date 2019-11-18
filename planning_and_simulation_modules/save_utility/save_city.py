import json
import os
import os.path
from .SaveScenario import SaveScenario
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QTableWidget, QListWidget
from PyQt5 import QtCore


class SaveCityTab(SaveScenario):
    Cstep01 = None
    Cstep2 = None
    Cstep3 = None
    Cstepsim = None


    def __init__(self, folder=None):
        if folder is None:
            folder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../", "city",
                                                   "DefaultSaveFolder"))
        SaveScenario.__init__(self, folder)

    def load_saved_file(self):
        self.load("save.json")
        self.load_step01()



    def save_steps(self):
        text = self.file_manager.get_file_name_from_user(self.Cstep2)
        if text is None:
            message = "File name is missing. No files produced."
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setText("Invalid file name.")
            msgBox.setInformativeText(message)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.exec ()
        else:
            self.override_save_plugin_state(text)


    def override_save_plugin_state(self, file):
        self.save_step_01()
        self.save_step_2()
        self.save_step_3()
        self.save_simulation()
        self.save(file + ".json")

    def save_step_01(self):

        self.add_table_widget_to_saved_data(self.Cstep01.table_sd_HeDHW, name="step1heat")
        self.add_table_widget_to_saved_data(self.Cstep01.tb_HeDHW_source, name="step1source")
        self.data["residenziario"] = self.Cstep01.radioButton.isChecked()
        self.data["terziario"] = self.Cstep01.radioButton_2.isChecked()
        self.add_table_widget_to_saved_data(self.Cstep01.table_fec_baseline)
        #self.add_table_widget_to_saved_data(self.Cstep01.table_sd_heating)

        self.add_table_widget_to_saved_data(self.Cstep01.table_sd_cool, name="step1Cool")
        self.add_table_widget_to_saved_data(self.Cstep01.table_cool_source, name="step1CoolSource")
        self.add_table_widget_to_saved_data(self.Cstep01.table_KPIsEn, name="step1En")
        self.add_table_widget_to_saved_data(self.Cstep01.tableWidget, name ="heatH")
        self.data["weight_plan"] = self.Cstep01.weight_plan.value()

        self.add_list_widget_to_saved_data(self.Cstep01.energy_criteria)
        self.add_list_widget_to_saved_data(self.Cstep01.environmental_criteria)
        self.add_list_widget_to_saved_data(self.Cstep01.economic_criteria)
        self.add_list_widget_to_saved_data(self.Cstep01.social_criteria)

        self.add_table_widget_to_saved_data(self.Cstep01.tableWidget_HeatingM, name="heatM")
        self.add_table_widget_to_saved_data(self.Cstep01.tableWidget_heatinhH, name="heat")
        self.add_table_widget_to_saved_data(self.Cstep01.tableWidget_dhw, name="heatDhw")
        self.add_table_widget_to_saved_data(self.Cstep01.tableWidget_cool, name="heatCool")


    def save_step_2(self):

        self.add_table_widget_to_saved_data(self.Cstep2.table_HeDHW_source_targ)
        self.add_table_widget_to_saved_data(self.Cstep2.table_sd_target)
        self.data["ued_demograic_factor"] = self.Cstep2.demoFactor_dhw.value()
        self.data["ued_corrective_factor"] = self.Cstep2.envelope_dhw.value()
        self.add_table_widget_to_saved_data(self.Cstep2.table_sd_cool_targ)
        self.add_table_widget_to_saved_data(self.Cstep2.table_cool_source)
        self.data["ued_demograic_factor_cool"] = self.Cstep2.demoFact_cool.value()
        self.data["ued_corrective_factor_cool"] = self.Cstep2.envelope_cool.value()
        self.data["ued_icrease_factor_cool"] = self.Cstep2.increase_cool.value()
        self.add_table_widget_to_saved_data(self.Cstep2.table_dhw_source_targ)
        self.add_table_widget_to_saved_data(self.Cstep2.total_dhw_source)
        self.add_table_widget_to_saved_data(self.Cstep2.table_cool)
        self.add_table_widget_to_saved_data(self.Cstep2.total_cool_source)

    def save_step_3(self):
        self.add_table_widget_to_saved_data(self.Cstep3.sbs_hdhw_Source)
        self.add_table_widget_to_saved_data(self.Cstep3.sbs_cool_source)
        self.add_table_widget_to_saved_data(self.Cstep3.dist_hdhw_source)
        self.add_table_widget_to_saved_data(self.Cstep3.dist_cool_source)

    def save_simulation(self):
        self.add_table_widget_to_saved_data(self.citySim.sim_sbs_hdhw_Source)
        self.add_table_widget_to_saved_data(self.citySim.sim_sbs_cool_source)
        self.add_table_widget_to_saved_data(self.citySim.dist_heat_source)
        self.add_table_widget_to_saved_data(self.citySim.dist_cool_net)

        self.data["share_heating"] = self.citySim.sbs_heat.value()
        self.data["share"] = self.citySim.sbs_dhw.value()
        self.data["heating_hours"] = self.citySim.sbs_heat_h.value()
        self.data["dhw_hours"] = self.citySim.sbs_dhw_h.value()
        self.data["cool_hours"] = self.citySim.sbs_cool_h.value()
        self.data["period"] = self.citySim.period.value()
        self.data["rate"] = self.citySim.rate.value()
        self.data["share_heat"] = self.citySim.share_heat.value()
        self.data["share"] = self.citySim.share.value()
        self.data["grid_eff"] = self.citySim.eff.value()
        self.data["grid_lenght"] = self.citySim.leng.value()
        self.data["btn_eff"] = self.citySim.btn_eff.value()
        self.data["btn_len"] = self.citySim.btn_len.value()
        self.data["leng"] = self.citySim.leng.value()
        self.data["gross_area"] = self.citySim.spinBox_9.value()
        self.add_table_widget_to_saved_data(self.citySim.table_source)
        self.add_table_widget_to_saved_data(self.citySim.table_sutil)
        self.add_table_widget_to_saved_data(self.citySim.tableWidget_10)
        self.add_table_widget_to_saved_data(self.citySim.table_source)
        self.add_table_widget_to_saved_data(self.citySim.table_sutil)










