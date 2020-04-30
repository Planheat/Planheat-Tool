
from planheatclient import PlanHeatClient
import requests
URL = PlanHeatClient("https://planheat.artelys.com")


def recive_country():
    try:
        URL.data_query("final-energy-consumption").filter("Fuel","Natural Gas")\
            .filter("Category", "Heating").filter("Country", "Italy").filter("Sector", "Residential").send()
        res = URL.data_query("default-population").send()
        resultsCountry = (res["Country"])
        return resultsCountry
    except requests.exceptions.ConnectionError:
        RaiseConnectionError()

def recive_primary_energy_factor(country):
    try:
        name = country
        results = URL.data_query("primary-energy-factor").filter("Country", name).send()
        return(results)
    except requests.exceptions.ConnectionError:
        RaiseConnectionError()

def em_factorOIl():
    try:
        results = URL.data_query("resources-emission-factor").filter("Resource", "Oil").send()
        return(results)
    except requests.exceptions.ConnectionError:
        RaiseConnectionError()

def find_em_factorCoal():
    try:
        results = URL.data_query("resources-emission-factor").filter("Resource", "Coal").send()
        return(results)
    except requests.exceptions.ConnectionError:
        RaiseConnectionError()

def find_em_factorBiomass():
    try:
        results = URL.data_query("resources-emission-factor").filter("Resource", "Biomass").send()
        return(results)
    except requests.exceptions.ConnectionError:
        RaiseConnectionError()

def electricity_em_fact(country):
    try:
        name = country
        results = URL.data_query("electricity-emission-factor").filter("Country", name).send()
        return(results)
    except requests.exceptions.ConnectionError:
        RaiseConnectionError()

def RaiseConnectionError():
    try:
        requests.get("http://google.com//")
        raise Exception("PlanHeatClient connection error: you can't access to PlanHeatClient, "
                        "please check your proxy or your firewall.")
    except requests.exceptions.ConnectionError:
        raise Exception("PlanHeatClient connection error: please check your Internet connection.")


def test():
    URL = PlanHeatClient("https://planheat.artelys.com")
    d = URL.geo_query("resources-emission-factor")
    r = d.send()
    for f in r["features"]:
        for k in f:
            print(f[k])

    for country in r["Country"]:
        URL = PlanHeatClient("https://planheat.artelys.com")
        d = URL.data_query("primary-energy-factor").filter("Country", country)
        r = d.send()
        print(r)



    d.filter("Country", "Italy")
    r = d.send()

