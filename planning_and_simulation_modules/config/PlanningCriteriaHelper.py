class PlanningCriteriaHelper:

    def __init__(self):
        self.planningCriteria_en = ['EN1: Reduction of primary energy consumption',  # [0]
                                    'EN2: Reduction of final energy consumption',  # [1]
                                    'EN3: Reduction of useful energy demand',  # [2]
                                    'EN4: Increase share of renewable energy sources',  # [3]
                                    'EN5: Increase utilization of energy from waste heat sources',  # [4]
                                    'EN6: Reduction of energy consumption from conventional fuels',  # [5]
                                    'EN7: Reduction of energy consumption  from Imported Sources',  # [6]
                                    'EN9: Cooling penetration',  # [7]
                                    'EN11: Solar thermal penetration',  # [8]
                                    'EN12: Use of local sources',  # [9]
                                    'EN13a:  DHN thermal losses reduction',  # [10]
                                    'EN13b: DCN thermal losses reduction',  # [11]
                                    'EN14a: DHN heat density reduction',  # [12]
                                    'EN14b: DCN heat density reduction',  # [13]
                                    'EN15: Operating hours increase']  # [14]

        self.planningCriteria_ev = ['ENV1: CO2 reduction',  # [0]
                                    'ENV2: Pollutants emission reduction',  # [1]
                                    'ENV3: Noise pollution reduction']  # [2]

        self.planningCriteria_eco = ['ECO1: Creation of economically feasible H&C scenarios',  # [0]
                                     'ECO2: Operational costs reduction',  # [1]
                                     'ECO3: Levelised cost of heat',  # [2]
                                     'ECO4: CO2 reduction cost']  # [3]

        self.planningCriteria_so = ['SO1: Energy poverty reduction',  # [0]
                                    'SO2: Job increase',  # [1]
                                    'SO3: Security of supply increase']  # [2]

    def insert_text_help(self, p):
        try:
            if p == self.planningCriteria_en[0]:
                help = ("Utilization of sources with a lower primary energy factor \n"
                        "Utilization of more efficient technologies \n "
                        "Increase the use of HPs and CHP \n"
                        "Decrease the utilization of boilers \n"
                        "Increase the renovation rate of buildings envelope \n"
                        "Increase the consumption of local RES \n"
                        "Increase the direct consumption of local Waste Heat through Heat Exchangers \n "
                        "Increase the penetration of solar thermal technology \n"
                        "Increase the efficiency of the distribution of DHCNs \n ")

            elif p == self.planningCriteria_en[1]:
                help = ("Utilization of more efficient technologies \n"
                        "Increase the use of HPs and CHP \n"
                        "Decrease the utilization of boilers \n"
                        "Increase the renovation rate of buildings envelope \n"
                        "Increase the consumption of local RES \n"
                        "Increase the direct consumption of local Waste Heat through Heat Exchangers \n"
                        "Increase the penetration of solar thermal technology \n"
                        "Increase the efficiency of the distribution of DHCNs \n")

            elif p == self.planningCriteria_en[2]:
                help = "Increase the renovation rate of buildings envelope "

            elif p == self.planningCriteria_en[3]:
                help = "Increase the consumption of local RES "

            elif p == self.planningCriteria_en[4]:
                help = "Increase the consumption of local Waste Heat"

            elif p == self.planningCriteria_en[5]:
                help = ("Increase the consumption of local Waste Heat \n",
                        "Increase the consumption of local RES \n",
                        "Increase the penetration of solar thermal technology \n",
                        "Increase the penetration of DHCNs in combination with local source exploitation \n",
                        "Increase consumption of  biomass \n",
                        "Increase the utilization of waste heat and geothermal HPs \n",
                        "Decrease the penetration of cooling from air source HPs \n")
            elif p == self.planningCriteria_en[6]:
                help = "increase the consumption of local sources \n"

            elif p == self.planningCriteria_en[10]:
                help = "Increase the efficiency of the DHNs distribution systems \n"
            elif p == self.planningCriteria_en[11]:
                help = "Increase the efficiency of the DHNs distribution systems \n"

            elif p == self.planningCriteria_en[12]:
                help = "Increase the efficiency of the DHNs distribution systems \n"

            elif p == self.planningCriteria_en[13]:
                help = "Increase the efficiency of the DHNs distribution systems \n"

            elif p == self.planningCriteria_en[14]:
                help = (
                    "Increase the utilization of reliable imported or local sources (in general NG and electricity for imported source and geothermal for local sources) \n"
                    "Increase the utilization of reliable technologies (boilers, CHP, HPs, heat exchangers) \n "
                    "Increase the utilization of thermal storages")

            elif p == self.planningCriteria_ev[0]:
                help = ("Reduction of the utilization of sources/technologies with an high CO2 emission factor \n"
                        "Utilization of local sources \n"
                        "Utilization of RES and waste heat \n"
                        "Utilization of no combustion technologies \n")

            elif p == self.planningCriteria_ev[1]:
                help = ("Reduction of the utilization of sources with an high pollutant (NOx, SOx, PM10) emission factor \n"
                        "Utilization of local sources \n"
                        "Utilization of RES and waste heat \n"
                        "Utilization of no combustion technologies")
            elif p == self.planningCriteria_ev[2]:
                help = ("Reduction of the utilization of sources with an high noise pollution factor \n"
                        "Utilization of no combustion technologies \n"
                        "Direct use of local available heat or cool")

            elif p == self.planningCriteria_eco[0]:
                help = ("Increase the utilization of technologies with low specific cost \n"
                        "Increase the utilization of technologies with low operational costs \n"
                        "Increase the utilization of technologies with low fuel costs \n "
                        "Increase the utilization of technologies supported by local or national grants \n"
                        "Increase the utilization of technologies with high values of YEOHs \n"
                        "Increase the utilization of technologies with high conversion efficiencies \n"
                        "Increase the penetration of DHCNs  Direct use of local available heat or cool")
            elif p == self.planningCriteria_eco[1]:
                help = ("Increase the utilization of technologies with low operational costs \n"
                        "Increase the utilization of technologies with low fuel costs \n"
                        "Increase the utilization of technologies with high values of YEOHs \n"
                        "Increase the utilization of technologies with high conversion efficiencies \n"
                        "Increase the penetration of DHCNs \n"
                        "Direct use of local available heat or cool")

            elif p == self.planningCriteria_eco[2]:
                help = ("Increase the utilization of technologies with low specific cost \n "
                        "Increase the utilization of technologies with low operational costs \n"
                        "Increase the utilization of technologies with low fuel costs \n"
                        "Increase the utilization of technologies supported by local or national grants \n"
                        "Increase the utilization of technologies with high values of YEOHs \n"
                        "Increase the utilization of technologies with high conversion efficiencies \n"
                        "Increase the penetration of DHCNs ")

            elif p == self.planningCriteria_eco[3]:
                help = ("Reduction of the utilization of sources/technologies with an high CO2 emission factor \n"
                        "Utilization of local sources \n "
                        "Utilization of RES and waste heat \n "
                        "Utilization of no combustion technologies \n"
                        "increase the utilization of technologies with low specific cost \n "
                        "Increase the utilization of technologies with low operational costs \n"
                        "Increase the utilization of technologies with low fuel costs \n "
                        "Increase the utilization of technologies supported by local or national grants \n"
                        "Increase the utilization of technologies with high values of YEOHs \n "
                        "Increase the utilization of technologies with high conversion efficiencies \n"
                        "Increase the penetration of DHCNs \n"
                        "Direct use of local available heat or cool")

            elif p == self.planningCriteria_so[0]:
                help = ("Utilization of more efficient technologies \n"
                        "Increase the use of HPs and CHP \n "
                        "Decrease the utilization of boilers \n "
                        "Increase the renovation rate of buildings envelope \n"
                        "Increase the consumption of local RES \n"
                        "Increase the direct consumption of local Waste Heat through Heat Exchangers \n "
                        "Increase the penetration of solar thermal technology \n"
                        "Increase the efficiency of the distribution of DHCNs ")

            elif p == self.planningCriteria_so[1]:
                help = ("Increase the technologies with an high “job factor” \n"
                        "Increase the utilization of local sources exploitation \n"
                        "Increase the penetration of DHCNs")
            elif p == self.planningCriteria_so[2]:
                help = "Increase the utilization of local sources "

            return help
        except:
            return ""
