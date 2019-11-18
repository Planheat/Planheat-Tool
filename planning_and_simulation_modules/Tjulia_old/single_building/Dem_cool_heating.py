
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
import csv
import pandas as pd

from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import os.path


def SingleBuilding():
    print("sei dentro al single building eh")
    csvout ="C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\output_SingleBuilding.csv"
    cinput = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\test1_hourly.csv"
    y = 8760
    x = 0
    out = open(csvout, 'w')
    with open(cinput, 'r') as f:
        for line in f:
            if not line == []:
                out.write(line)
            if x == y:
                return
            x = x + 1
    out.close()

def buildDHW():
    print("sei nel cooling")
    with open(
            'C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\output_SingleBuilding.csv')as inputFile:
        csvReader = csv.reader(inputFile, delimiter=';')
        data = [(linea[1], linea[9]) for linea in csvReader]
    csv.register_dialect('myDialect', delimiter='\t', quoting=csv.QUOTE_NONE)
    myfile = open('C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\output_DHW.csv', 'w')
    with myfile:
        writer = csv.writer(myfile, dialect='myDialect')
        writer.writerows(data)

    myfile.close()

def buildCool():
    print("sei nel DHW")
    with open(
            'C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\output_SingleBuilding.csv')as inputFile:
        csvReader = csv.reader(inputFile, delimiter=';')
        data = [(linea[1], linea[8]) for linea in csvReader]
        # print("buildCool, data", data)

    csv.register_dialect('myDialect', delimiter='\t', quoting=csv.QUOTE_NONE)
    myfile2 = open(
        'C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\output_cool.csv',
        'w')
    with myfile2:
        writer = csv.writer(myfile2, dialect='myDialect')
        writer.writerows(data)

    myfile2.close()

def buildHeating():
    print("sei nel Heating")
    with open('C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\output_SingleBuilding.csv')as inputFile:
        csvReader = csv.reader(inputFile, delimiter=';')
        data = [(linea[1], linea[7]) for linea in csvReader]
        # print("buildCool, data", data)

    csv.register_dialect('myDialect', delimiter='\t', quoting=csv.QUOTE_NONE)
    Heatfile = open('C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\output_heating.csv','w')
    with Heatfile:
        writer = csv.writer(Heatfile, dialect='myDialect')
        writer.writerows(data)

    Heatfile.close()


def generafile_old(cinput="", coutput=""):
    # Only for testing
    if cinput == "":
        cinput = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem\\test1_hourly.csv"
    if coutput == "":
        coutput = "C:\\Users\\qgis1\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\planning_module\\fileDem"

    if not os.path.isfile(cinput):
        print("Dem_cool_heating.py, generafile(): file di input non trovato. cinput:", cinput)
        return

    j = 0
    N = 8760
    buildings = []
    fp = open(cinput)
    for i, line in enumerate(fp):
        if i == 1:
            building_id = line.split(";")[1]
            buildings.append(building_id)
            break
    fp.close()
    csvout_H = coutput + "\\DEM_time_" + building_id + ".csv"
    csvout_C = coutput + "\\DEM_cool_time_" + building_id + ".csv"
    csvout_DHW = coutput + "\\DEM_DHW_time_" + building_id + ".csv"
    out_H = open(csvout_H, 'w')
    out_C = open(csvout_C, 'w')
    out_DHW = open(csvout_DHW, 'w')
    # copy and transforming data from hourly profiles (kW in MW)
    with open(cinput) as fp:
        for i, line in enumerate(fp):
            if i>(j*N) and i<=(j+1)*N:
                s = line.split(";")
                # out_H.write("0.0" + "\n")
                # out_C.write("0.0" + "\n")
                # out_DHW.write("0.0" + "\n")
                out_H.write(str(float(s[5].replace(",", "."))/1000) + "\n")
                out_C.write(str(float(s[6].replace(",", "."))/1000) + "\n")
                out_DHW.write(str(float(s[7].replace(",", "."))/1000) + "\n")
            else:
                if not i == 0:
                    out_H.close()
                    out_C.close()
                    out_DHW.close()
                    j = j + 1
                    s = line.split(";")
                    csvout_H = coutput + "\\DEM_time_" + s[1] + ".csv"
                    csvout_C = coutput + "\\DEM_cool_time_" + s[1] + ".csv"
                    csvout_DHW = coutput + "\\DEM_DHW_time_" + s[1] + ".csv"
                    buildings.append(s[1])
                    out_H = open(csvout_H, 'w')
                    out_C = open(csvout_C, 'w')
                    out_DHW = open(csvout_DHW, 'w')
                    # out_H.write("0.0" + "\n")
                    # out_C.write("0.0" + "\n")
                    # out_DHW.write("0.0" + "\n")
                    out_H.write(str(float(s[5].replace(",", "."))/1000) + "\n")
                    out_C.write(str(float(s[6].replace(",", "."))/1000) + "\n")
                    out_DHW.write(str(float(s[7].replace(",", "."))/1000) + "\n")

    out_H.close()
    out_C.close()
    out_DHW.close()
    j = j + 1
    return [j, buildings]


def gen_dem_time_district_old(network, cinput="", coutput=""):
    if not os.path.isfile(cinput):
        print("Dem_cool_heating.py, gen_dem_time_district(): file di input non trovato. cinput:", cinput)
        return
    building_id = [building.attribute("BuildingID") for building in network.get_connected_buildings()]
    csvout = coutput + "\\DEM_time_.csv"
    dem_time = [0.0 for i in range(8760)]
    with open(cinput) as fp:
        for i, line in enumerate(fp):
            s = line.split(";")
            if s[1] in building_id:
                if network.n_type == "DHN":
                    dem_time[(i-1) % 8760] += float(s[7].replace(",", ".")) + float(s[5].replace(",", "."))
                else:
                    dem_time[(i-1) % 8760] += float(s[6].replace(",", "."))
    out = open(csvout, 'w')
    for dem in dem_time:
        out.write(str(dem) + "\n")
    out.close()

def generafile(cinput="", coutput=""):
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
        df_building = df_building.reset_index(drop=True).fillna(0)
        (df_building[Heating].apply(lambda x: float(x)/1000))\
            .to_csv(coutput + "\\DEM_time_" + b + ".csv", sep=";", index=False)
        (df_building[Cooling].apply(lambda x: float(x)/1000))\
            .to_csv(coutput + "\\DEM_cool_time_" + b + ".csv", sep=";", index=False)
        (df_building[DHW].apply(lambda x: float(x)/1000))\
            .to_csv(coutput + "\\DEM_DHW_time_" + b + ".csv", sep=";", index=False)
        buildings.append(b)

    return [len(buildings), buildings]

def gen_dem_time_district(cinput="", coutput="", energy="Heating"):
    print("Generating aggregated file ...")
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
    try:
        os.makedirs(coutput, exist_ok=True)
    except:
        pass
    if not coutput.endswith(".csv"):
        coutput += "\\DEM_time.csv"
    
    df = pd.read_csv(cinput, sep=';', decimal=',')
    df.drop(columns=[ProjectID, Season], inplace=True)
    agg_df = df.groupby(by=[DayOfYear, HourOfDay], as_index=False).agg({energy:sum})[energy]
    agg_df.to_csv(coutput, sep=";", index=False)

    print("End generating aggregated file")

    return True