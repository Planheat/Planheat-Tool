from planheatclient import PlanHeatClient
from ..config.SourcesTableFactors import SourcesTableFactors
from .adapters.SourceAdapterDB import SourceAdapterDB
from .adapters.PollutantAdapterDB import PollutantAdapterDB

class DatabaseService:
    URL = "https://planheat.artelys.com"
    resources_emission_factor = "resources-emission-factor"

    def __init__(self):
        pass

    def set_sources_table_factors_params(self, source_table_factors: SourcesTableFactors):
        default_data = source_table_factors.table_data
        source_adapter = SourceAdapterDB()
        pollutant_adapter = PollutantAdapterDB()

        db_api = PlanHeatClient(self.URL)
        d = db_api.geo_query(self.resources_emission_factor)
        r = d.send()

        for feature in r["features"]:
            p = feature["properties"]
            try:
                resource = source_adapter.to_DPM(p["Resource"])
                pollutant = pollutant_adapter.to_DPM(p["Pollutant name"])
                default_data[resource][pollutant] = p["Emission factor"]
            except KeyError:
                pass
