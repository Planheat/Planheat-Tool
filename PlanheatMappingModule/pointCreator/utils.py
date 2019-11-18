from enum import IntEnum
import sqlite3
import os

directory = os.path.dirname(os.path.realpath(__file__))
db_file = os.path.join(directory, "../PLANHEAT/database/planheat.db")


class DataTypes(IntEnum):
    INDUSTRIAL = 0
    GENERIC = 1
    UNCONVENTIONAL = 2


class IndustrialQuestion(IntEnum):
    CO2 = 0
    CONSUMPTION = 1
    FLOOR_SURFACE = 2


class UnconventionalQuestion(IntEnum):
    SUBWAY = 1
    CAR_PARKS = 2
    DATA_CENTERS = 3
    DATA_CENTERS_UNKNOWN = 4
    SUPERMARKET_COOLING = 5
    SUPERMARKET_COOLING_UNKNOWN = 6
    REFRIGERATED_STORAGE_FACILITIES = 7
    REFRIGERATED_STORAGE_FACILITIES_UNKNOWN = 8
    WASTE_WATER_PLANT_EFFLUENT = 9
    WASTE_WATER_PLANT_EFFLUENT_LOAD = 10
    WASTE_WATER_PLANT_EFFLUENT_UNKNOWN = 11
    WASTE_WATER_PLANT_EFFLUENT_UNKNOWN_LOAD = 12
    LNG_TERMINAL = 13


class FuelTypes(IntEnum):
    COAL = 1
    NG = 2
    OIL = 3
    MIX = 4
    UNKNOWN = 10


class TemperatureLevels(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    UNKNOWN = 3


class Sector(object):
    def __init__(self, sector_type, description, fuel_type, mwh_per_m2_per_year, heat_recovery, temperature):
        self.sector_type = sector_type
        self.description = description
        self.fuel_type = fuel_type
        self.mwh_per_m2_per_year = mwh_per_m2_per_year
        self.heat_recovery = heat_recovery
        self.temperature = temperature


class UnconventionalSource(object):
    def __init__(self, source_id, description, formula, parameter1, parameter2, parameter3, parameter4, parameter5, label1, label2, label3, label4, label5, tool_tip0, tool_tip1, tool_tip2,
                 tool_tip3, tool_tip4, tool_tip5, unit1, unit2, unit3, unit4, unit5, enabled1, enabled2, enabled3, enabled4, enabled5, monthly_values, monthly_label,
                 monthly_factors):
        self.source_id = source_id
        self.description = description
        self.formula = formula
        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.parameter3 = parameter3
        self.parameter4 = parameter4
        self.parameter5 = parameter5
        self.label1 = label1
        self.label2 = label2
        self.label3 = label3
        self.label4 = label4
        self.label5 = label5
        self.tool_tip0 = tool_tip0
        self.tool_tip1 = tool_tip1
        self.tool_tip2 = tool_tip2
        self.tool_tip3 = tool_tip3
        self.tool_tip4 = tool_tip4
        self.tool_tip5 = tool_tip5
        self.unit1 = unit1
        self.unit2 = unit2
        self.unit3 = unit3
        self.unit4 = unit4
        self.unit5 = unit5
        self.enabled1 = enabled1
        self.enabled2 = enabled2
        self.enabled3 = enabled3
        self.enabled4 = enabled4
        self.enabled5 = enabled5
        self.monthly_values = monthly_values.split(';') if monthly_values else monthly_values
        self.monthly_label = monthly_label
        self.monthly_factors = monthly_factors.split(';') if monthly_factors else monthly_factors


def get_sector_list(sector_type):
    if sector_type:
        db = sqlite3.connect(db_file)
        db.row_factory = sqlite3.Row
        c = db.cursor()
        c.execute("SELECT * FROM SECTORS WHERE TYPE = ?", (int(sector_type),))
        result = []
        for row in c.fetchall():
            temperature = None
            fuel_type = None
            fuel_type_id = _get_int_value(row["fuel_type"])
            if fuel_type_id:
                fuel_type = FuelTypes(fuel_type_id)
            temperature_id = _get_int_value(row["temperature"])
            if temperature_id:
                temperature = TemperatureLevels(temperature_id)
            sector = Sector(_get_int_value(row["type"]), row["description"], fuel_type, row["mwh_per_m2_per_year"],
                            _get_int_value(row['heat_recovery']), temperature)
            result.append(sector)
        c.close()
        db.close()
        return result


def get_unconventional_list(source_id=None):
    db = sqlite3.connect(db_file)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    if source_id:
        c.execute("SELECT * FROM UNCONVENTIONAL_SOURCES WHERE ID = ?", (int(source_id),))
    else:
        c.execute("SELECT * FROM UNCONVENTIONAL_SOURCES")
    result = []
    for row in c.fetchall():
        sector = UnconventionalSource(_get_int_value(row["id"]), row["description"], row['formula'],
                                      _get_float_value(row['parameter_1']),
                                      _get_float_value(row['parameter_2']),
                                      _get_float_value(row['parameter_3']),
                                      _get_float_value(row['parameter_4']),
                                      _get_float_value(row['parameter_5']),
                                      row['label_1'],
                                      row['label_2'],
                                      row['label_3'],
                                      row['label_4'],
                                      row['label_5'],
                                      get_tooltip(row['tooltip_0']),
                                      get_tooltip(row['tooltip_1']),
                                      get_tooltip(row['tooltip_2']),
                                      get_tooltip(row['tooltip_3']),
                                      get_tooltip(row['tooltip_4']),
                                      get_tooltip(row['tooltip_5']),
                                      row['unit_1'],
                                      row['unit_2'],
                                      row['unit_3'],
                                      row['unit_4'],
                                      row['unit_5'],
                                      row['enabled_1'],
                                      row['enabled_2'],
                                      row['enabled_3'],
                                      row['enabled_4'],
                                      row['enabled_5'],
                                      row['monthly_values'],
                                      row['monthly_label'],
                                      row['monthly_factors']
                                      )
        result.append(sector)
    c.close()
    db.close()
    return result


def get_tooltip(input):
    if input:
        return "<span>" + input + "</span>"
    return input


def get_co2_factor(fuel_id):
    if fuel_id:
        db = sqlite3.connect(db_file)
        db.row_factory = sqlite3.Row
        c = db.cursor()
        c.execute("SELECT * FROM FUEL_TYPES WHERE ID = ?", (int(fuel_id),))
        row = c.fetchone()
        result = float(row["factor"])
        c.close()
        db.close()
        return result


def _get_int_value(text_val):
    if text_val is None or text_val == '':
        return None
    return int(text_val)


def _get_float_value(text_val):
    if text_val is None or text_val == '':
        return None
    return float(text_val)
