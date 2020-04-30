from PyQt5.QtWidgets import QTreeWidget

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import pandas as pd

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ...building.Building import Building

import os.path

def generafile(widget: QTreeWidget, cinput="", coutput=""):
    # Fields csv
    ProjectID   = "ProjectID"
    BuildingID  = "BuildingID"
    Heating     = "Heating"
    Cooling     = "Cooling"
    DHW         = "DHW"
    HourOfDay   = "HourOfDay"
    DayOfYear   = "DayOfYear"
    Season      = "Season"
    
    # To be sure
    if not os.path.exists(cinput):
        print("File {0} doesn't exist".format(cinput))
        return [None, None]
    os.makedirs(coutput, exist_ok=True)
    
    df = pd.read_csv(cinput, sep=';', decimal=',')
    df.drop(columns=[ProjectID, HourOfDay, DayOfYear, Season], inplace=True)
    buildings = []

    # profile per building
    for b, df_building in df.groupby(BuildingID):
        b = str(b)
        for i in range(widget.topLevelItemCount()):
            building: Building = widget.topLevelItem(i)
            if building.building_id == b:
                break
        else:
            continue
        df_building = df_building.reset_index(drop=True).fillna(0)

        if not building.connected_to_DHN:
            conversion_DHN = lambda x: float(x)/1000
        else:
            conversion_DHN = to_zero
        if not building.connected_to_DCN:
            conversion_DCN = lambda x: float(x)/1000
        else:
            conversion_DCN = to_zero

        (df_building[Heating].apply(conversion_DHN))\
            .to_csv(coutput + "\\DEM_time_" + b + ".csv", sep=";", index=False)
        (df_building[DHW].apply(conversion_DHN))\
            .to_csv(coutput + "\\DEM_DHW_time_" + b + ".csv", sep=";", index=False)
        (df_building[Cooling].apply(conversion_DCN))\
            .to_csv(coutput + "\\DEM_cool_time_" + b + ".csv", sep=";", index=False)
        buildings.append(b)

    return [len(buildings), buildings]

def to_zero(x):
    return 0.0


def gen_dem_time_district(cinput="", coutput="", services=[], buildings=[], conversion_factor=1/1000, log=None):

    print("Generating aggregated file ...")
    # Fields csv
    ProjectID   = "ProjectID"
    BuildingID  = "BuildingID"
    Heating     = "Heating"
    Cooling     = "Cooling"
    DHW         = "DHW"
    Total       = "Total"
    HourOfDay   = "HourOfDay"
    DayOfYear   = "DayOfYear"
    Season      = "Season"

    # cinput = "C://Users//qgis1///AppData//Local//QGIS//QGIS3//planheat_data//c36e42a4-4993-4a7a-a771-8c2aa1a0da12//mapping//DMM//DMM_result_hourly.csv"
    df = pd.read_csv(cinput, sep=';', decimal=',')
    df.drop(columns=[ProjectID, Season], inplace=True)
    building_list = df.groupby(by=[BuildingID], as_index=False, sort=False).agg({})
    index = 0
    acceptance_table = []
    while True:
        try:
            acceptance_table.append(str(building_list["BuildingID"][index]) in buildings)
            index += 1
        except KeyError:
            break
    log.log("gen_dem_time_district(): acceptance_table", acceptance_table)
    log.log("gen_dem_time_district(): building_list[\"BuildingID\"]", building_list["BuildingID"])

    columns = {}
    for service in services:
        columns[service] = lambda x: if_sum(x, acceptance_table)
    agg_df = df.groupby(by=[DayOfYear, HourOfDay], as_index=False).agg(columns)
    agg_df[Total] = [0 for i in range(8760)]
    for service in services:
        agg_df[Total] += agg_df[service]*conversion_factor
    agg_df[Total].to_csv(coutput, sep=";", index=False)

    print("End generating aggregated file")

    return True


def if_sum(values, acceptance_table):
    total = 0
    for i, key in enumerate(values.keys()):
        if acceptance_table[i]:
            total += values[key]
    return total
