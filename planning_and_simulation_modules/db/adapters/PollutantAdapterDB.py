class PollutantAdapterDB:

    def __init__(self):
        self.adapter_db = {
            "CO2": "CO2",
            "NOx": "N2O"
        }

        self.adapter_DPM = {
            "CO2": "CO2",
            "N2O": "NOx"
        }

    def to_db(self, source):
        return self.adapter_db.get(source)

    def to_DPM(self, source):
        return self.adapter_DPM.get(source)