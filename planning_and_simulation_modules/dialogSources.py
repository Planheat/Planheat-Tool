

from PyQt5.QtWidgets import (QWidget, QPushButton,
    QHBoxLayout, QVBoxLayout,QListView)

from PyQt5 import QtCore, QtGui


class CheckSourceDialog(QWidget):

    def __init__(self, checked=False, parent=None):
        super(CheckSourceDialog, self).__init__(parent)
        self.sources = ['Biomass Forestry',  # [0]
                        'Deep geothermal',  # [1]
                        'Geothermal - Shallow - Ground heat extraction',  # [2]
                        'Geothermal - Shallow - Ground cold extraction',  # [3]
                        'Solar thermal',  # [4]
                        'Solar thermal',  # [5]
                        'Excess heat Industry',  # [6]
                        'Excess heat - Data centers',  # [7]
                        'Excess heat - Data centers',  # [8]
                        'Excess heat - Supermarkets',  # [9]
                        'Excess heat - Refrigerated storage facilities',  # [10]
                        'Excess heat - Indoor carparkings',  # [11]
                        'Excess heat - Subway networks',  # [12]
                        'Urban waste water treatment plant', # [13]
                        'Water - Waste water - Sewer system',  # [14]
                        'Water - Surface water - Rivers cold extraction heat pump',  # [15]
                        'Water - Surface water - Rivers cold extraction from free cooling',  # [16]
                        'Water - Surface water - Lakes heat extraction with heat pump',  # [17]
                        'Water - Surface water - Lakes cold extraction with heat pump',  # [18]
                        'Excess cooling - LNG terminals',  # [19]
                        'Generic heating/cooling source',  # [20]
                        'Water - Surface water - Rivers heat extraction heat pump'  # [21]
                        ]

        self.mapped_sources = [
            'Geothermal - Deep - Potential till 1km',  # [0]
            'Geothermal - Deep - Additional 1-2km',  # [1]
            'Geothermal - Deep - Additional 2-3km',  # [2]
            'Geothermal - Deep - Additional 3-4km',  # [3]
            'Geothermal - Deep - Additional 4-5km',  # [4]
            'Geothermal - Deep - Additional 5-7km',  # [5]
            'Geothermal - Shallow - Ground heat extraction',  # [6]
            'Geothermal - Shallow - Ground cold extraction',  # [7]
            'Solar thermal - Rooftops',  # [8]
            'Solar thermal - Other areas',  # [9]
            'Excess heat - Industry - Large industries',  # [10] ?
            'Excess heat - Industry - Additional industries',  # [11] ?
            'Excess heat - Data centers',  # [12]
            'Excess heat - Supermarkets',  # [13]
            'Excess heat - Refrigerated storage facilities',  # [14]
            'Excess heat - Indoor carparkings',  # [15]
            'Excess heat - Subway networks',  # [16]
            'Water - Waste water - Large UWWTPs',  # [17]
            'Water - Waste water - Additional UWWTPs',  # [18]
            'Water - Waste water - Sewer system',  # [19]
            'Water - Surface water - Rivers cold extraction heat pump',  # [20] -
            'Water - Surface water - Rivers cold extraction from free cooling',  # [21] Not found in MM
            'Water - Surface water - Lakes heat extraction with heat pump',  # [22] -
            'Water - Surface water - Lakes cold extraction with heat pump',  # [23] -
            'Excess cooling - LNG terminals',  # [24]
            'Generic heating/cooling source',  # [25]
            'Biomass - Forestry - Broad-leaved forest',  # [26]
            'Biomass - Forestry - Coniferous forest',  # [27]
            'Biomass - Forestry - Mixed forest',  # [28]
            'Water - Surface water - Rivers heat extraction heat pump'  # [29]
            ]

        self.supply_csv_sources = {"Agriculture (High) Basic": self.sources[20], "Agriculture (High)": self.sources[20],
                                   "Forestry (High)": self.sources[0], "Biomass": self.sources[0],
                                   "Industry (High)": self.sources[6], "Excess heat sources": self.sources[6],
                                   "Excess cooling sources": self.sources[19], "Waste water": self.sources[14],
                                   "Surface water (Low)": self.sources[15], "Water": self.sources[14],
                                   "Deep geothermal (High)": self.sources[1],
                                   "Shallow geothermal (Low)": self.sources[2],
                                   "Geothermal": self.sources[2], "Solar thermal (High)": self.sources[4],
                                   "Generic heating or cooling source": self.sources[20]
                                   }

        self.MM_to_DPM_sources_dict = {self.mapped_sources[0]: self.sources[1],
                                        self.mapped_sources[1]: self.sources[1],
                                        self.mapped_sources[2]: self.sources[1],
                                        self.mapped_sources[3]: self.sources[1],
                                        self.mapped_sources[4]: self.sources[1],
                                        self.mapped_sources[5]: self.sources[1],
                                        self.mapped_sources[6]: self.sources[2],
                                        self.mapped_sources[7]: self.sources[3],
                                        self.mapped_sources[8]: self.sources[4],
                                        self.mapped_sources[9]: self.sources[5],
                                        self.mapped_sources[10]: self.sources[6],
                                        self.mapped_sources[11]: self.sources[7],
                                        self.mapped_sources[12]: self.sources[8],
                                        self.mapped_sources[13]: self.sources[9],
                                        self.mapped_sources[14]: self.sources[10],
                                        self.mapped_sources[15]: self.sources[11],
                                        self.mapped_sources[16]: self.sources[12],
                                        self.mapped_sources[17]: self.sources[13],
                                        self.mapped_sources[18]: self.sources[13],
                                        self.mapped_sources[19]: self.sources[14],
                                        self.mapped_sources[20]: self.sources[15],
                                        self.mapped_sources[21]: self.sources[16],
                                        self.mapped_sources[22]: self.sources[17],
                                        self.mapped_sources[23]: self.sources[18],
                                        self.mapped_sources[24]: self.sources[19],
                                        self.mapped_sources[25]: self.sources[20],
                                        self.mapped_sources[26]: self.sources[0],
                                        self.mapped_sources[27]: self.sources[0],
                                        self.mapped_sources[28]: self.sources[0],
                                        self.mapped_sources[29]: self.sources[21]
                                        }

        self.DPM_to_MM_sources_dict = {}
        for source in self.sources:
            sources_list =[]
            for key in self.MM_to_DPM_sources_dict.keys():
                if self.MM_to_DPM_sources_dict[key] == source:
                    sources_list.append(key)
            self.DPM_to_MM_sources_dict[source] = sources_list


        self.sources_for_absorption ={self.MM_to_DPM_sources_dict[self.mapped_sources[6]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[10]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[12]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[13]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[17]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[18]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[25]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[22]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[14]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[19]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[15]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[20]],
                                      self.MM_to_DPM_sources_dict[self.mapped_sources[16]]
                                      }
        self.sources_lowT = {self.MM_to_DPM_sources_dict[self.mapped_sources[6]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[7]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[15]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[16]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[19]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[24]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[26]]
                             }

        self.sources_mediumT = {self.MM_to_DPM_sources_dict[self.mapped_sources[12]],
                                self.MM_to_DPM_sources_dict[self.mapped_sources[13]],
                                self.MM_to_DPM_sources_dict[self.mapped_sources[14]]
                                }

        self.sources_highT = {self.MM_to_DPM_sources_dict[self.mapped_sources[0]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[1]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[2]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[3]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[4]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[5]],
                            self.MM_to_DPM_sources_dict[self.mapped_sources[27]]
                             }

        self.monthly_temperature = {self.mapped_sources[0]: False,
                                    self.mapped_sources[1]: False,
                                    self.mapped_sources[2]: False,
                                    self.mapped_sources[3]: False,
                                    self.mapped_sources[4]: False,
                                    self.mapped_sources[5]: False,
                                    self.mapped_sources[6]: False,
                                    self.mapped_sources[7]: False,
                                    self.mapped_sources[8]: False,
                                    self.mapped_sources[9]: False,
                                    self.mapped_sources[10]: False,
                                    self.mapped_sources[11]: False,
                                    self.mapped_sources[12]: True,
                                    self.mapped_sources[13]: True,
                                    self.mapped_sources[14]: True,
                                    self.mapped_sources[15]: True,
                                    self.mapped_sources[16]: True,
                                    self.mapped_sources[17]: True,
                                    self.mapped_sources[18]: True,
                                    self.mapped_sources[19]: True,
                                    self.mapped_sources[20]: True,
                                    self.mapped_sources[21]: True,
                                    self.mapped_sources[22]: True,
                                    self.mapped_sources[23]: True,
                                    self.mapped_sources[24]: False,
                                    self.mapped_sources[25]: False,
                                    self.mapped_sources[26]: False,
                                    self.mapped_sources[27]: False,
                                    self.mapped_sources[28]: False,
                                    self.mapped_sources[29]: True
                                    }

        self.is_shapefile = {self.mapped_sources[0]: False,
                                    self.mapped_sources[1]: False,
                                    self.mapped_sources[2]: False,
                                    self.mapped_sources[3]: False,
                                    self.mapped_sources[4]: False,
                                    self.mapped_sources[5]: False,
                                    self.mapped_sources[6]: False,
                                    self.mapped_sources[7]: False,
                                    self.mapped_sources[8]: False,
                                    self.mapped_sources[9]: False,
                                    self.mapped_sources[10]: True,
                                    self.mapped_sources[11]: True,
                                    self.mapped_sources[12]: True,
                                    self.mapped_sources[13]: True,
                                    self.mapped_sources[14]: True,
                                    self.mapped_sources[15]: True,
                                    self.mapped_sources[16]: True,
                                    self.mapped_sources[17]: True,
                                    self.mapped_sources[18]: True,
                                    self.mapped_sources[19]: False,
                                    self.mapped_sources[20]: False,
                                    self.mapped_sources[21]: False,
                                    self.mapped_sources[22]: False,
                                    self.mapped_sources[23]: False,
                                    self.mapped_sources[24]: True,
                                    self.mapped_sources[25]: True,
                                    self.mapped_sources[26]: False,
                                    self.mapped_sources[27]: False,
                                    self.mapped_sources[28]: False,
                                    self.mapped_sources[29]: False
                                    }

        self.file_name_mapping = {self.mapped_sources[0]: "Deep geothermal (High)-Potential till 1 km-",
                                  self.mapped_sources[1]: "Deep geothermal (High)-Additional 1-2 km-",
                                  self.mapped_sources[2]: "Deep geothermal (High)-Additional 2-3 km-",
                                  self.mapped_sources[3]: "Deep geothermal (High)-Additional 3-4 km-",
                                  self.mapped_sources[4]: "Deep geothermal (High)-Additional 4-5 km-",
                                  self.mapped_sources[5]: "Deep geothermal (High)-Additional 5-7 km-",
                                  self.mapped_sources[6]: "Shallow geothermal (Low)-Ground heat extraction-",
                                  self.mapped_sources[7]: "Shallow geothermal (Low)-Ground cold extraction-",
                                  self.mapped_sources[8]: "Solar thermal (High)-Rooftops-",
                                  self.mapped_sources[9]: "Solar thermal (High)-Other areas-",
                                  self.mapped_sources[10]: "Industry (High)-Large industries-",
                                  self.mapped_sources[11]: "Industry (High)-Additional industries-",
                                  self.mapped_sources[12]: "Excess heat mapped_sources-Data centers (Medium)-",
                                  self.mapped_sources[13]: "Excess heat mapped_sources-Supermarkets (Medium)-",
                                  self.mapped_sources[14]: "Excess heat mapped_sources-Refrigerated storage facilities (Medium)-",
                                  self.mapped_sources[15]: "Excess heat mapped_sources-Indoor carparkings (Low)-",
                                  self.mapped_sources[16]: "Excess heat mapped_sources-Subway networks (Low)-",
                                  self.mapped_sources[17]: "Waste water-Effluent of UWWTPs (Low)-",
                                  self.mapped_sources[18]: "Waste water-Additional UWWTPs (Low)-",
                                  self.mapped_sources[19]: "Waste water-Sewer system (Low)-",
                                  self.mapped_sources[20]: "Surface water (Low)-Rivers cold extraction with heat pump-",
                                  self.mapped_sources[21]: "Surface water (Low)-Rivers cold extraction from free cooling-",
                                  self.mapped_sources[22]: "Surface water (Low)-Lakes heat extraction with heat pump-",
                                  self.mapped_sources[23]: "Surface water (Low)-Lakes cold extraction with heat pump-",
                                  self.mapped_sources[24]: "Excess cooling mapped_sources-LNG terminals (Low)-",
                                  self.mapped_sources[25]: "",
                                  self.mapped_sources[26]: "Forestry (High)-Broad-leaved forest-",
                                  self.mapped_sources[27]: "Forestry (High)-Coniferous-",
                                  self.mapped_sources[28]: "Forestry (High)-Mixed-",
                                  self.mapped_sources[29]: "Surface water (Low)-Rivers heat extraction with heat pump-"
                                  }

        self.source_temperature = {}

        self.source_buffer = {}

        self.source_efficiency = {}

        for key in self.mapped_sources:
            if "High" in self.file_name_mapping[key]:
                self.source_temperature[key] = 80
            else:
                if "Low" in self.file_name_mapping[key]:
                    self.source_temperature[key] = 15
                else:
                    if "Medium" in self.file_name_mapping[key]:
                        self.source_temperature[key] = 50
                    else:
                        self.source_temperature[key] = -274
            self.source_buffer[key] = -274
            self.source_efficiency[key] = 100

        self.sources_rens = [self.MM_to_DPM_sources_dict[self.mapped_sources[0]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[1]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[2]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[3]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[4]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[5]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[6]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[7]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[8]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[9]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[26]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[27]],
                             self.MM_to_DPM_sources_dict[self.mapped_sources[28]]]

        self.sources_fecWH = [self.MM_to_DPM_sources_dict[self.mapped_sources[10]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[11]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[12]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[13]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[14]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[15]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[16]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[17]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[18]],
                              self.MM_to_DPM_sources_dict[self.mapped_sources[19]]]

        self.sources_pecCF = [self.MM_to_DPM_sources_dict[self.mapped_sources[24]]]

        self.sources_pecIS = self.sources

        self.tech_source = ""


        self.model = QtGui.QStandardItemModel()
        self.listView =QListView()
        self.okButton = QPushButton("Ok")

    def vis_interfaccia(self, t):
        checked = False
        t = str(t)

        if t =="Absorption Heat Pump":
            sources = self.sources_for_absorption
        if t == "Waste Heat Compression Heat Pump Hight T" or "Seasonal Waste Heat Compression Heat Pump":
            sources = self.sources_highT
        if t == "Waste Heat Compression Heat Pump Medium T":
            sources = self.sources_mediumT
        if t =="Waste Heat Compression Heat Pump Low T":
            sources= self.sources_lowT

        for string in sources:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            check = \
                (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)

        self.listView.setModel(self.model)

        hbox =QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.listView)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setGeometry(600, 600, 500, 280)


        self.setWindowTitle("sources")
        """if self.icon:
            self.setWindowIcon(self.icon)"""
        #self.hide()
