import requests
from ...config.pvgis import default_params
from .... import config
from ... import master_planning_config
from PyQt5.QtWidgets import QMessageBox
from ..exceptions.UserInterruptException import UserInterruptException

import os.path

class PvgisApi:

    def __init__(self):
        self.folder = os.path.join(master_planning_config.CURRENT_PLANNING_DIRECTORY, "District", "KPIs", "PVGIS")
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder, exist_ok=True)
        self.pvgis_base_url = "https://re.jrc.ec.europa.eu/api/seriescalc?"
        self.params = {
            "ot": {"lat": default_params.lat,
                   "lon": default_params.lon,
                   "startyear": default_params.startyear,
                   "endyear": default_params.endyear,
                   "outputformat": default_params.outputformat},
            "gsi_1": {"lat": default_params.lat,
                   "lon": default_params.lon,
                   "startyear": default_params.startyear,
                   "endyear": default_params.endyear,
                   "angle": default_params.angle,
                   "aspect": default_params.aspect,
                   "optimalangles": default_params.optimalangles,
                   "outputformat": default_params.outputformat},
            "gsi_2": {"lat": default_params.lat,
                   "lon": default_params.lon,
                   "startyear": default_params.startyear,
                   "endyear": default_params.endyear,
                   "angle": default_params.angle,
                   "aspect": default_params.aspect,
                   "optimalangles": default_params.optimalangles,
                   "outputformat": default_params.outputformat},
            "gsi_s": {"lat": default_params.lat,
                   "lon": default_params.lon,
                   "startyear": default_params.startyear,
                   "endyear": default_params.endyear,
                   "angle": default_params.angle,
                   "aspect": default_params.aspect,
                   "optimalangles": default_params.optimalangles,
                   "outputformat": default_params.outputformat}
            }
        self.key_to_query = {"ot": False, "gsi_1": False, "gsi_2": False, "gsi_s": False}
        self.global_solar_irradiation = ""
        self.outside_temperature = ""
        self.global_solar_irradiation_2 = ""
        self.global_solar_irradiation_seasonal = ""
        self.show_error = True

    def PVGIS_url_gen(self, key: str):
        url_PVGIS = self.pvgis_base_url
        for parameter in self.params[key]:
            url_PVGIS = url_PVGIS + "&" + parameter + "=" + str(self.params[key][parameter])
        return url_PVGIS

    def get_file_suffix(self, key: str):
        suffix = ""
        angle = int(self.params[key].get("angle", 0))
        resto = angle % 5
        angle = angle - resto if resto < 3 else angle + (5 - resto)
        ps = [int(self.params[key]["lat"]), int(self.params[key]["lon"]), self.params[key]["startyear"], angle]
        for parameter in ps:
            suffix = suffix + "_" + str(parameter)
        return suffix

    def query(self, key: str):
        print(self.PVGIS_url_gen(key))
        try:
            r = requests.get(self.PVGIS_url_gen(key))
            if r.status_code == 200:
                return r.json()
            else:
                data = r.json()
                if data["status"] == 400:
                    if self.show_error:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.setWindowTitle("ERROR querying PVGIS servers.")
                        msg.setText(data["message"])
                        self.show_error = False
                        retval = msg.exec_()
                        raise UserInterruptException("User forced interrupt.")
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setWindowTitle("ERROR connecting PVGIS servers.")
            msg.setText("PVGIS server Exception:\n" + str(e) + "\nYou may try to continue but simulation can fail."
                                                               "\n\nContinue?")
            retval = msg.exec_()
            if not retval == QMessageBox.Yes:
                raise UserInterruptException("User forced interrupt.")

    def file_already_exist(self, file_path):
        try:
            return os.path.isfile(file_path)
        except Exception:
            return False

    def write_to_files(self):
        self.outside_temperature = os.path.join(self.folder,
                                                "Outside_temperature" + self.get_file_suffix("ot") + ".csv")
        self.global_solar_irradiation = os.path.join(self.folder,
                                                    "Global_solar_irradiation" + self.get_file_suffix("gsi_1") + ".csv")
        self.global_solar_irradiation_2 = os.path.join(self.folder,
                                                    "Global_solar_irradiation" + self.get_file_suffix("gsi_2") + ".csv")
        self.global_solar_irradiation_seasonal = os.path.join(self.folder,
                                                    "Global_solar_irradiation" + self.get_file_suffix("gsi_s") + ".csv")
        self.write_single_file(self.outside_temperature, "T2m", "ot")
        self.write_single_file(self.global_solar_irradiation, "G(i)", "gsi_1")
        self.write_single_file(self.global_solar_irradiation_2, "G(i)", "gsi_2")
        self.write_single_file(self.global_solar_irradiation_seasonal, "G(i)", "gsi_s")
        return {"ot": self.outside_temperature,
                "gsi_1": self.global_solar_irradiation,
                "gsi_2": self.global_solar_irradiation_2,
                "gsi_s": self.global_solar_irradiation_seasonal
            }

    def write_single_file(self, file_path, key: str, key_param: str):
        if self.key_to_query[key_param] and not self.file_already_exist(file_path):
            data = self.query(key_param)
            with open(file_path, "w") as of:
                for i in range(8760):
                    of.write(str(data["outputs"]["hourly"][i][key]) + "\n")

    def update_common_params(self, lat=default_params.lat, lon=default_params.lon,
                      startyear=default_params.startyear, endyear=default_params.endyear):
        for key in self.params.keys():
            self.params[key]["lat"] = lat
            self.params[key]["lon"] = lon
            self.params[key]["startyear"] = startyear
            self.params[key]["endyear"] = endyear

    def gen_dummy_output(self, files: dict):
        dummy_file = os.path.join(self.folder, "dummy_PVGIS_data.csv")
        if not os.path.isfile(dummy_file):
            with open(dummy_file, "w") as f:
                for i in range(8760):
                    f.write("0\n")
        for key in files:
            try:
                if not os.path.isfile(files[key]):
                    files[key] = dummy_file
            except Exception:
                pass
