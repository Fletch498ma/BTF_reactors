'''
Created on 10/03/2020

@author: Fletcher Gilbertson 
'''
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Fixing random state for reproducibility
x_values = []
y_values = []


data = pd.read_csv('/home/pi/BTF_reactors/log/ir_ek2_2020-09-12_11-43-14.csv')
x_values = np.arange(len(data['Date']))
y_CH4 = data['ChA(ppm)']
y_CO2 = data['ChB(ppm)']

O2data = pd.read_csv('/home/pi/BTF_reactors/log/ec_ek3_2020-09-12_11-43-14.csv')
x_O2 = np.arange(len(O2data['Date']))
y_O2 = O2data['Concentration(ppm*100)']

fig, axs = plt.subplots(2, 1)
axs[0].scatter(x_values,y_CH4,s=2,c='blue')
axs[0].scatter(x_values,y_CO2,s=2,c='red')
#axs[0].set_xlim(0,)
axs[0].set_xlabel('Time')
axs[0].set_ylabel('CH4 and CO2 (%v/v)')
axs[0].grid(True)

axs[1].scatter(x_O2,y_O2,s=2)
axs[1].set_xlabel('Time')
axs[1].set_ylabel('O2 (%v/v)')
#axs[1].set_ylim(0,12)
axs[1].grid(True)

fig.tight_layout()
plt.show()
