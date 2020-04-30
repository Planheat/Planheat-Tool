class SourceAdapterDB:

    def __init__(self):
        self.adapter_db = {
            "Biomass Forestry": "Biomass",
            "Natural gas": "Gas",
            "Heating Oil": "Oil",
            "Coal and Peat": "Coal"
        }

        self.adapter_DPM = {
            "Biomass": "Biomass Forestry",
            "Gas": "Natural gas",
            "Oil": "Heating Oil",
            "Coal": "Coal and Peat"
        }

    def to_db(self, source: str):
        return self.adapter_db.get(source, "District heating")

    def to_DPM(self, source: str):
        return self.adapter_DPM.get(source, "Generic heating/cooling source")