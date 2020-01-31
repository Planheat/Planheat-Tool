import os
import os.path
from ...result_utils import PlotCanvas


class PlotService:

    HOB = "Result_HOB"
    HP_WASTE_HEAT = "Result_HP_waste_heat"
    CHP = "Result_CHP"
    HP = "Result_HP"
    ST = "Result_ST"
    SOC = "Result_SOC"
    DEM = "Result_DEM"
    HEX = "Result_HEX"
    EH = "Result_EH"
    HP_COOL = "Result_HP_cool"
    HP_COOL_ABSOPRTION = "Result_HP_cool_absorption"
    HP_absorption = "Result_HP_absorption"

    canvas_dpi = 85
    canvas_height = 4
    canvas_width = 8

    def __init__(self, folder, sim_ui):
        self.work_folder = folder

        self.plot = PlotCanvas(sim_ui, width=self.canvas_width, height=self.canvas_height, dpi=self.canvas_dpi)
        sim_ui.gridLayout.addWidget(self.plot)

        self.plot2 = PlotCanvas(sim_ui, width=self.canvas_width, height=self.canvas_height, dpi=self.canvas_dpi)
        sim_ui.gridLayout_2.addWidget(self.plot2)

        self.plot3 = PlotCanvas(sim_ui, width=self.canvas_width, height=self.canvas_height, dpi=self.canvas_dpi)
        sim_ui.gridLayout_3.addWidget(self.plot3)

        self.plot4 = PlotCanvas(sim_ui, width=self.canvas_width, height=self.canvas_height, dpi=self.canvas_dpi)
        sim_ui.gridIndiv.addWidget(self.plot4)

        self.plot5 = PlotCanvas(sim_ui, width=self.canvas_width, height=self.canvas_height, dpi=self.canvas_dpi)
        sim_ui.gridIndiv2.addWidget(self.plot5)

        self.plot6 = PlotCanvas(sim_ui, width=self.canvas_width, height=self.canvas_height, dpi=self.canvas_dpi)
        sim_ui.gridIndiv3.addWidget(self.plot6)

        self.district_min_spinBox = sim_ui.district_min_spinBox
        self.district_max_spinBox = sim_ui.district_max_spinBox
        self.building_min_spinBox = sim_ui.building_min_spinBox
        self.building_max_spinBox = sim_ui.building_max_spinBox

        self.h8760 = 8760

    def plot_district(self, var=None):
        PATH = os.path.join(self.work_folder, "district", "heating", "Results")
        if not os.path.isdir(PATH):
            return
        if self.district_min_spinBox.value() == self.district_max_spinBox.value():
            return
        fileNames = [file for file in os.listdir(PATH) if '.csv' in file]
        data = self.build_data(PATH, self.district_file_to_data_key(fileNames))

        grafici_splitter = {1: [self.DEM], 2: [self.HOB, self.HP, self.EH],
                            3: [self.HP_WASTE_HEAT, self.CHP, self.ST, self.SOC, self.HEX]}

        PlotService.plot_distric_single_graph(self.plot, data, grafici_splitter[1],
                                              {"title": "Demand profile",
                                               "xmin": self.district_min_spinBox.value(),
                                               "xmax": self.district_max_spinBox.value()})
        PlotService.plot_distric_single_graph(self.plot2, data, grafici_splitter[2],
                                              {"title": "Load",
                                               "xmin": self.district_min_spinBox.value(),
                                               "xmax": self.district_max_spinBox.value()})
        PlotService.plot_distric_single_graph(self.plot3, data, grafici_splitter[3],
                                              {"title": "Load",
                                               "xmin": self.district_min_spinBox.value(),
                                               "xmax": self.district_max_spinBox.value()})

    def plot_buildings(self, var=None):
        PATH = os.path.join(self.work_folder, "single_building", "Results")
        if not os.path.isdir(PATH):
            return
        if self.building_min_spinBox.value() == self.building_max_spinBox.value():
            return
        fileNames = [file for file in os.listdir(PATH) if '.csv' in file]
        data = self.build_data(PATH, self.buildings_file_to_data_key(fileNames))

        grafici_splitter = {1: [self.DEM], 2: [self.HOB, self.HP, self.HP_COOL, self.EH],
                            3: [self.CHP, self.ST, self.SOC]}

        PlotService.plot_distric_single_graph(self.plot4, data, grafici_splitter[1],
                                              {"title": "Demand profile",
                                               "xmin": self.building_min_spinBox.value(),
                                               "xmax": self.building_max_spinBox.value()})
        PlotService.plot_distric_single_graph(self.plot5, data, grafici_splitter[2],
                                              {"title": "Load",
                                               "xmin": self.building_min_spinBox.value(),
                                               "xmax": self.building_max_spinBox.value()})
        PlotService.plot_distric_single_graph(self.plot6, data, grafici_splitter[3],
                                              {"title": "Load",
                                               "xmin": self.building_min_spinBox.value(),
                                               "xmax": self.building_max_spinBox.value()})

    def build_data(self, folder, file_to_data_key):
        data = {}
        for file_name in file_to_data_key.keys():
            if os.path.isfile(os.path.join(folder, file_name)):
                data_key = file_to_data_key[file_name]
                if data_key not in data.keys():
                    data[data_key] = [0.0 for i in range(self.h8760)]
                with open(os.path.join(folder, file_name), "r") as fr:
                    content = fr.readlines()
                    if len(content) < self.h8760:
                        continue
                    for i in range(self.h8760):
                        try:
                            if not float(content[i]) == float(content[i]):
                                content[i] = 0.0
                        except ValueError:
                            content[i] = 0.0
                        data[data_key][i] += float(content[i])
        return data

    def district_file_to_data_key(self, files):
        file_to_data_key = {}
        for file in files:
            prefix = file[0:-41]
            if prefix.startswith(self.HOB):
                file_to_data_key[file] = self.HOB
            if prefix.startswith(self.HP):
                if prefix.startswith(self.HP_WASTE_HEAT):
                    file_to_data_key[file] = self.HP_WASTE_HEAT
                else:
                    file_to_data_key[file] = self.HP
            if prefix.startswith(self.CHP):
                file_to_data_key[file] = self.CHP
            if prefix.startswith(self.ST):
                file_to_data_key[file] = self.ST
            if prefix.startswith(self.SOC):
                file_to_data_key[file] = self.SOC
            if prefix.startswith(self.DEM):
                file_to_data_key[file] = self.DEM
            if prefix.startswith(self.HEX):
                file_to_data_key[file] = self.HEX
            if prefix.startswith(self.EH):
                file_to_data_key[file] = self.EH
        return file_to_data_key

    def buildings_file_to_data_key(self, files):
        file_to_data_key = {}
        for file in files:
            prefix = file[0:-14]
            if prefix.startswith(self.HOB):
                file_to_data_key[file] = self.HOB
            if prefix.startswith(self.HP):
                if prefix.startswith(self.HP_COOL):
                    file_to_data_key[file] = self.HP_COOL
                else:
                    file_to_data_key[file] = self.HP
            if prefix.startswith(self.CHP):
                file_to_data_key[file] = self.CHP
            if prefix.startswith(self.ST):
                file_to_data_key[file] = self.ST
            if prefix.startswith(self.SOC):
                file_to_data_key[file] = self.SOC
            if prefix.startswith(self.DEM):
                file_to_data_key[file] = self.DEM
            if prefix.startswith(self.EH):
                file_to_data_key[file] = self.EH
        return file_to_data_key

    @staticmethod
    def plot_distric_single_graph(plot, data, grafici_splitter, props):
        plot.figure.clf()
        ax = plot.figure.add_subplot(111)
        # ax.margins(0, 0.15)
        ax.set_title(props["title"])
        ax.set_xlabel('Hours [h]')
        ax.set_ylabel('Load [MW]')
        legend = [key[7:] for key in grafici_splitter]
        for key in grafici_splitter:
            if not key in data.keys():
                data[key] = [0.0 for i in range(8760)]
            ax.plot(data[key])
        ax.legend(legend, loc="upper right", ncol=1)
        plot.figure.tight_layout()
        ax.set_ylim([0, PlotService.max_max(data, grafici_splitter)])
        ax.set_xlim((props["xmin"], props["xmax"]))
        plot.draw()

    @staticmethod
    def max_max(data, grafici_splitter):
        massimo = 0.0
        for key in grafici_splitter:
            if not key in data.keys():
                continue
            for value in data[key]:
                if value > massimo:
                    massimo = value
        if massimo == 0:
            massimo = 1
        else:
            massimo = massimo * 1.1
        return massimo
