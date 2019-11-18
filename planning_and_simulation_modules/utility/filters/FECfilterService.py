from PyQt5.QtWidgets import QComboBox, QLabel
from PyQt5.QtCore import Qt
import random


class FECfilterService:

    FEC = "FEC baseline"  # EN_2.1
    FEC_specific = "FEC baseline (specific)"  # EN_2.2
    FEC_future = "FEC future"  # EN_2.3
    FEC_future_specific = "FEC future (specific)"  # EN_2.4
    FEC_future_variation = "FEC variation"  # EN_2.5
    FEC_future_saving = "FEC saving"  # EN_2.6
    YEOH_Base = "YEOH baseline"  # EN_15.1
    YEOH_Future = "YEOH future"  # EN_15.2
    YEOH_Variation = "YEOH variation"  # EN_15.3

    def __init__(self, fec_filter_combo_box: QComboBox, description_filter_label: QLabel, mode="future"):
        self.fec_filter_combo_box = fec_filter_combo_box
        self.description_filter_label = description_filter_label

        self.fec_filter_combo_box.clear()
        self.fec_filter_combo_box.insertItem(0, "Select filter:")
        self.fec_filter_combo_box.setItemData(0, 0, Qt.UserRole - 1)
        self.fec_filter_combo_box.insertItem(1, self.FEC)
        self.fec_filter_combo_box.insertItem(2, self.FEC_specific)
        self.fec_filter_combo_box.insertItem(3, self.YEOH_Base)

        if mode == "future":
            self.fec_filter_combo_box.insertItem(4, self.FEC_future)
            self.fec_filter_combo_box.insertItem(5, self.FEC_future_specific)
            self.fec_filter_combo_box.insertItem(6, self.FEC_future_variation)
            self.fec_filter_combo_box.insertItem(7, self.FEC_future_saving)
            self.fec_filter_combo_box.insertItem(8, self.YEOH_Future)
            self.fec_filter_combo_box.insertItem(9, self.YEOH_Variation)

    def update_label(self, new_text):
        self.description_filter_label.setText(new_text + ":")

    def get_filtered_table(self, KPIs):
        if self.fec_filter_combo_box.currentText() == self.FEC:
            return self.apply_filter_FEC(KPIs)

        if self.fec_filter_combo_box.currentText() == self.FEC_specific:
            return self.apply_filter_FEC_specific(KPIs)

        if self.fec_filter_combo_box.currentText() == self.FEC_future:
            return self.apply_filter_FEC_future(KPIs)

        if self.fec_filter_combo_box.currentText() == self.FEC_future_specific:
            return self.apply_filter_FEC_future_specific(KPIs)

        if self.fec_filter_combo_box.currentText() == self.FEC_future_variation:
            return self.apply_filter_FEC_variation(KPIs)

        if self.fec_filter_combo_box.currentText() == self.FEC_future_saving:
            return self.apply_filter_FEC_saving(KPIs)

        if self.fec_filter_combo_box.currentText() == self.YEOH_Base:
            return self.apply_filter_YEOH_Base(KPIs)

        if self.fec_filter_combo_box.currentText() == self.YEOH_Future:
            return self.apply_filter_YEOH_Future(KPIs)

        if self.fec_filter_combo_box.currentText() == self.YEOH_Variation:
            return self.apply_filter_YEOH_Variation(KPIs)

        return {}

    def apply_filter_FEC(self, KPIs):
        return self.generic_fec_filter(KPIs, "EN_2.1")

    def apply_filter_FEC_specific(self, KPIs):
        return self.generic_fec_filter(KPIs, "EN_2.2")

    def apply_filter_FEC_future(self, KPIs):
        return self.generic_fec_filter(KPIs, "EN_2.3")

    def apply_filter_FEC_future_specific(self, KPIs):
        return self.generic_fec_filter(KPIs, "EN_2.4")

    def apply_filter_FEC_variation(self, KPIs):
        return self.generic_fec_filter(KPIs, "EN_2.5")

    def apply_filter_FEC_saving(self, KPIs):
        return self.generic_fec_filter(KPIs, "EN_2.6")

    def apply_filter_YEOH_Base(self, KPIs):
        return self.generic_YEOH_filter(KPIs, "EN_15.1")

    def apply_filter_YEOH_Future(self, KPIs):
        return self.generic_YEOH_filter(KPIs, "EN_15.2")

    def apply_filter_YEOH_Variation(self, KPIs):
        return self.generic_YEOH_filter(KPIs, "EN_15.3")

    def generic_fec_filter(self, KPIs, key):
        # Key should be in the form eg. "EN_2.1"
        output_table = {}
        sources_names = FECfilterService.get_from_key(KPIs, "sources")
        if sources_names is None:
            return output_table
        for index, source in enumerate(sources_names):
            output_table[source] = {}
            output_table[source]["R"] = FECfilterService.get_from_key(KPIs, key + "R_s" + str(index))
            output_table[source]["T"] = FECfilterService.get_from_key(KPIs, key + "T_s" + str(index))
            output_table[source]["TOT"] = FECfilterService.get_from_key(KPIs, key + "_s" + str(index))
        return output_table

    def generic_YEOH_filter(self, KPIs, key):
        # Key should be in the form eg. "EN_2.15"
        output_table = {}
        YEOHbase = FECfilterService.get_from_key(KPIs, key)
        print("YEOHbase:", YEOHbase)
        if YEOHbase is None:
            return output_table
        for index, key in enumerate(YEOHbase.keys()):
            output_table[key] = {}
            output_table[key]["R"] = "-"
            output_table[key]["T"] = "-"
            fec_pow = FECfilterService.get_from_key(YEOHbase, key)
            try:
                output_table[key]["TOT"] = round(float((fec_pow[0]) * 1000) / float(fec_pow[1]), 2)
            except (ValueError, IndexError) as e:
                output_table[key]["TOT"] = "Nan"
            except ZeroDivisionError as e:
                output_table[key]["TOT"] = "-"
        return output_table

    @staticmethod
    def get_from_key(dictionary, key):
        try:
            return dictionary[key]
        except KeyError:
            return None


    def example_KPIs(self):
        KPIs = {}

        KPIs["sources"] = ["Heating Oil", "Natural gas", "Electricity", "Deep Geothermal",
                           "Geothermal - Shallow - Ground heat extraction",
                           "Geothermal - Shallow - Ground cold extraction", "Solar thermal", "Excess heat Industry",
                           "Excess heat - Data centers",
                           "Excess heat - Supermarkets", "Excess heat - Refrigerated storage facilities",
                           "Excess heat - Indoor carparkings",
                           "Excess heat - Subway networks", "Urban waste water treatment plant",
                           "Water - Waste water - Sewer system",
                           "Water - Surface water - Rivers cold extraction heat pump",
                           "Water - Surface water - Rivers cold extraction from free cooling HEX", "Water - Surface water - Lakes heat extraction with heat pump",
                           "Water - Surface water - Lakes cold extraction with heat pump", "Water - Surface water - Rivers heat extraction heat pump",
                           "LNG terminals excess cooling", "Biomass Forestry",
                           "generic source"]

        for i in range(23):
            KPIs["EN_2.1_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.1R_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.1T_s" + str(i)] = round(random.random(), 2)

            KPIs["EN_2.2_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.2R_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.2T_s" + str(i)] = round(random.random(), 2)

            KPIs["EN_2.3_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.3R_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.3T_s" + str(i)] = round(random.random(), 2)

            KPIs["EN_2.4_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.4R_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.4T_s" + str(i)] = round(random.random(), 2)

            KPIs["EN_2.5_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.5R_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.5T_s" + str(i)] = round(random.random(), 2)

            KPIs["EN_2.6_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.6R_s" + str(i)] = round(random.random(), 2)
            KPIs["EN_2.6T_s" + str(i)] = round(random.random(), 2)
        return KPIs
