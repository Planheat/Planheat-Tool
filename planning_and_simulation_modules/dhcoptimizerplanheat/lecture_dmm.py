import pandas as pd 
import matplotlib.pyplot as plt


class DMM_data:

	ProjectID = "ProjectID"
	BuildingID = "BuildingID"
	Heating = "Heating"
	Cooling = "Cooling"
	DHW = "DHW"
	HourOfDay = "HourOfDay"
	DayOfYear = "DayOfYear"
	Season = "Season"
	SumEner = "SumEner"
	Year = "Year"

	def __init__(self, path):
		self.df = pd.read_csv(path, delimiter=";", decimal=",")
		self.df.drop(columns=[self.ProjectID], inplace=True)
	
		self.df_per_buildings = {}
		for building, df_building in self.df.groupby(self.BuildingID):
			self.df_per_buildings[building] = df_building.reset_index(drop=True).fillna(0)
	
		self.by = {	self.HourOfDay: 	[self.DayOfYear, self.HourOfDay],
					self.DayOfYear: 	[self.DayOfYear],
					self.Season:		[self.Season],
					self.Year:			[self.Year]							}

	def get_profiles(self, energies = [Heating], agg = [HourOfDay], subset = None, factor_unit=1):
		assert type(energies) == list, "energies has to be a list"
		assert agg in self.by, "agg should be in {0}".format(set(self.by.keys()))
		if subset is None:
			df_per_buildings = self.df_per_buildings
		else:
			df_per_buildings = {k: self.df_per_buildings.get(k, None) for k in subset}	
		subset = subset if subset is not None else list(self.df_per_buildings.keys())
		profiles = pd.DataFrame() if agg != self.Year else {}
		for building in subset:
			profile = df_per_buildings[building].copy(deep=True)
			if profile is not None:
				profile[self.SumEner] = list(map(lambda *x: sum(x)*factor_unit, *[profile[e] for e in energies]))
				if agg == self.Year:
					profiles[building] =  max(profile[self.SumEner])
				else:
					profiles[building] = profile.groupby(by=self.by[agg], as_index=False).agg({self.SumEner:max})[self.SumEner]
		return profiles

	def get_consumption_peak(self, energies = [Heating], subset=None, index=False, factor_unit=1):
		if subset is None:
			df = self.df.copy(deep=True)
		else:
			df = self.df[self.df[self.BuildingID].isin(subset)].copy(deep=True)
		df.fillna(0, inplace=True)
		df[self.SumEner] = list(map(lambda *x: sum(x)*factor_unit, *[df[e] for e in energies]))
		df_agg = df.groupby(by=[self.DayOfYear, self.HourOfDay], as_index=False).agg({self.SumEner:sum})
		df_agg.set_index([self.DayOfYear, self.HourOfDay], inplace=True)
		df_agg = df_agg[self.SumEner]

		Dmax, Hmax = df_agg.idxmax()
		df_max = df[(df[self.DayOfYear]==Dmax) & (df[self.HourOfDay]==Hmax)]
		df_max.set_index([self.BuildingID], inplace=True)
		df_max = df_max[self.SumEner]
		if index:
			return df_max, (Dmax, Hmax)
		else:
			return df_max

if __name__ == "__main__":

	# ------------------------------------------------------------------

	data = DMM_data(path="data/DMM_result_hourly.csv")

	# ------------------------------------------------------------------
	
	#max_consumption = data.get_profiles(energies=[DMM_data.Heating, DMM_data.DHW],
	#										subset=list(data.df[DMM_data.BuildingID].iloc[:50].values), 
	#										agg="Year")

	# -------------------------------------------------------------------

	peak = data.get_consumption_peak(	energies=[DMM_data.Heating, DMM_data.DHW], 
										subset=list(data.df[DMM_data.BuildingID].iloc[:100000].values))
	print(peak)
	print(peak["3736699.0"])
	#plt.show()


		