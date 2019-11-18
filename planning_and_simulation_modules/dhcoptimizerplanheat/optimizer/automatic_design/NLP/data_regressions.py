#-----------------------------------------------------------
# Sources of data available in "Sources regressions" folder
#-----------------------------------------------------------

def CP(T):
	''' calculate Cp in function of Temperature '''
	assert 0 <= T <= 120, "T should be between 0 and 120"
	tab_CP =    [[0,    4.2199], [10,    4.1955], [20,    4.1844], [30,    4.1801], 
				[40,    4.1796], [50,    4.1815], [60,    4.1851], [70,    4.1902], 
				[80,    4.1969], [90,    4.2053], [100,   4.2157], [110,   4.2283], 
				[120,   4.2435]] # [Temp (°C), kJ.kg^(-1).K^(-1)]
	return 1e3*( (1-T%10/10)*tab_CP[T//10][1] + (T%10/10)*tab_CP[T//10+1][1])
	
def RHO(T):
	''' calculate \rho in function of Temperature '''
	assert 0 <= T <= 120, "T should be between 0 and 120"
	tab_rho =   [[0,    0.99984], [10,  0.99970], [20,  0.99820], [30,  0.99564],
				[40,    0.99221], [50,  0.98804], [60,  0.98320], [70,  0.97776],
				[80,    0.97179], [90,  0.96531], [100, 0.95835], [110, 0.95095],
				[120,   0.94311]] # [Temp (°C), g.cm^(-3)]
	return 1e3*( (1-T%10/10)*tab_rho[T//10][1] + (T%10/10)*tab_rho[T//10+1][1])

def CONSTRUCTION_COST(RECALCUL=False):
	''' return the linear regression coefficients for 
	the construction cost in function of the inner diameter'''
	tab_construction_cost = [[20, 226, 83, 165, 308, 391],
							[25, 231, 83, 165, 313, 396],
							[32, 257, 83, 165, 340, 422],
							[40, 272, 83, 165, 355, 437],
							[50, 293, 107, 202, 400, 495],
							[65, 335, 107, 202, 442, 537],
							[80, 376, 124, 240, 500, 616],
							[100, 504, 140, 256, 645, 760],
							[125, 640, 157, 273, 798, 913],
							[150, 791, 165, 310, 956, 1101],
							[200, 960, 182, 351, 1141, 1311],
							[250, 1363, 207, 393, 1569, 1755]]
							#[Nominal diameter, Piping costs (€/m), 
							#Trench costs in open field (€/m), Trench costs in street (€/m),
							#Total costs in open field (€/m), Total costs in street (€/m)]

	tab_InDiam=[[20, 21.6], [25, 28.5], [32, 37.2], [40, 43.1],
				[50, 54.5], [65, 70.3], [80, 82.5], [100, 107.1],
				[125, 132.5], [150, 160.3], [200, 210.1], [250, 263.0]]
				#[Nominal diameter, inner diameter (mm)]

	if RECALCUL:
		y = np.array([tab_construction_cost[i][5] for i in range(len(tab_construction_cost))])
		x = np.array([tab_InDiam[i][1] for i in range(len(tab_construction_cost))])

		A = np.vstack([x, np.ones(len(x))]).T
		m, c = np.linalg.lstsq(A, y, rcond=None)[0]
		plt.plot(x, y, x, [m*x[i]+c for i in range(len(x))])
		plt.show()
		print(m, c)

	else:
		m, c = 5.591470447050876, 197.03389414629245
		return m, c

def HEAT_LOSS_COST(T, RECALCUL = False):
	''' return the linear regression coefficients for 
	the heating loss (W/m) in function of the inner diameter 
	for 3 values of (T_supply +T_return)/2'''

	tab_heat_loss = [[25, 10.600, 8.244, 5.889],
					[32, 11.514, 8.955, 6.396],
					[40, 12.944, 10.068, 7.191],
					[50, 14.337, 11.151, 7.965],
					[65, 16.114, 12.533, 8.952],
					[80, 16.904, 13.147, 9.391],
					[100, 17.483, 13.598, 9.713],
					[125, 20.050, 15.595, 11.139],
					[150, 22.807, 17.739, 12.671],
					[200, 24.090, 18.737, 13.384]]
					#[Nominal diameter, 
					#Heat Loss (W/m) for T=100°C,
					#Heat Loss (W/m) for T=80°C,
					#Heat Loss (W/m) for T=60°C]

	tab_InDiam=[[20, 21.6], [25, 28.5], [32, 37.2], [40, 43.1],
				[50, 54.5], [65, 70.3], [80, 82.5], [100, 107.1],
				[125, 132.5], [150, 160.3], [200, 210.1], [250, 263.0]]
				#[Nominal diameter, inner diameter (mm)]

	if RECALCUL:
		y100 = np.array([tab_heat_loss[i][1] for i in range(len(tab_heat_loss))])
		y80 = np.array([tab_heat_loss[i][2] for i in range(len(tab_heat_loss))])
		y60 = np.array([tab_heat_loss[i][3] for i in range(len(tab_heat_loss))])
		x = np.array([tab_InDiam[i][1] for i in range(len(tab_heat_loss))])

		A = np.vstack([x, np.ones(len(x))]).T
		m100, c100 = np.linalg.lstsq(A, y100, rcond=None)[0]
		m80, c80 = np.linalg.lstsq(A, y80, rcond=None)[0]
		m60, c60 = np.linalg.lstsq(A, y60, rcond=None)[0]
		plt.plot(x, y100, x, y80, x, y60, \
			x, [m100*x[i]+c100 for i in range(len(x))], \
			x, [m80*x[i]+c80 for i in range(len(x))], \
			x, [m60*x[i]+c60 for i in range(len(x))])
		plt.show()

		m = (m100-m60)/(100-60)*(T-80) + m80
		c = (c100-c60)/(100-60)*(T-80) + c80

		print(m, c)

	else:
		# T = 100
		m100, c100 = 0.0966460611210018, 9.555686531714919
		# T = 80
		m80, c80 = 0.07517363167858998, 7.43189292738721
		# T = 60
		m60, c60 = 0.05369852278231223, 5.308296959576654

		m = (m100-m60)/(100-60)*(T-80) + m80
		c = (c100-c60)/(100-60)*(T-80) + c80
		
		return m, c

def MAX_VELOCITY(RECALCUL = False):
	tab_velocity = [[20, 0.6], [25, 1.0], [32, 1.1], [40, 1.2],
					[50, 1.4], [65, 1.6], [80, 1.8], [100, 1.9],
					[125, 2.0], [150, 2.5], [200, 3.3], [250, 3.9],
					[300, 4.3], [350, 4.6], [400, 5.0]]
					#[Nominal diameter, max velocity (m/s)]

	tab_InDiam=[[20, 21.6], [25, 28.5], [32, 37.2], [40, 43.1],
				[50, 54.5], [65, 70.3], [80, 82.5], [100, 107.1],
				[125, 132.5], [150, 160.3], [200, 210.1], [250, 263.0],
				[300, 312.7], [350, 344.4],	[400, 393.8]]
				#[Nominal diameter, inner diameter (mm)]

	if RECALCUL:
		y = np.array([tab_velocity[i][1] for i in range(len(tab_velocity))])
		x = np.array([tab_InDiam[i][1] for i in range(len(tab_velocity))])

		A = np.vstack([x, np.ones(len(x))]).T
		m, c = np.linalg.lstsq(A, y, rcond=None)[0]
		plt.plot(x, y, x, [m*x[i]+c for i in range(len(x))])
		plt.show()
		print(m, c)
	else:
		m, c = 0.011478535235426074, 0.6826763141040272
		return m, c

if __name__ =="__main__":
	import matplotlib.pyplot as plt 
	import numpy as np 
	CONSTRUCTION_COST(True)
	HEAT_LOSS_COST(90, True)
	MAX_VELOCITY(True)