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


data = pd.read_csv('/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/sump/ir_ek2_2021-1-5.csv')
x_values = np.arange(len(data['Date']))
y_CH4 = data['ChA(ppm)']
y_CO2 = data['ChB(ppm)']

O2data = pd.read_csv('/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/sump/ec_ek3_2021-1-5.csv')
x_O2 = np.arange(len(O2data['Date']))
y_O2 = O2data['Concentration(ppm*100)']/100

HumidityData = pd.read_csv('/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/sump/humidity_2021-1-5.csv')
x_Hum = np.arange(len(HumidityData['Date']))
y_Hum = HumidityData['RelativeHumidity(%)']

PressureData = pd.read_csv('/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/sump/diffPressure_2021-1-5.csv')
x_Pres = np.arange(len(PressureData['Date']))
y_Pres = PressureData['Pressure (kPa)']

pHData = pd.read_csv('/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/sump/pH_2021-1-5.csv')
x_pH = np.arange(len(pHData['Date']))
y_pH = pHData['pH']

TempData = pd.read_csv('/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/sump/SumpTemperature_2021-1-5.csv')
x_Temp = np.arange(len(TempData['Date']))
y_Temp = TempData['Temperature (C)']


fig, axs = plt.subplots(5, 1,figsize=(15,15))
axs[0].scatter(x_values,y_CH4,s=2,c='blue')
axs[0].scatter(x_values,y_CO2,s=2,c='red')
#axs[0].set_xlim(0,)
axs[0].set_xlabel('Time')
axs[0].set_ylabel('CH4 and CO2 (ppm)')
axs[0].grid(True)

axs[1].scatter(x_O2,y_O2,s=2)
axs[1].set_xlabel('Time')
axs[1].set_ylabel('O2 (ppm)')
#axs[1].set_ylim(0,12)
axs[1].grid(True)

axs[2].scatter(x_Hum,y_Hum,s=2)
axs[2].set_xlabel('Time')
axs[2].set_ylabel('Relative Humidity (%)')
#axs[1].set_ylim(0,12)
axs[2].grid(True)

axs[4].scatter(x_Pres,y_Pres,s=2)
axs[4].set_xlabel('Time')
axs[4].set_ylabel('Pressure (kPa)')
#axs[1].set_ylim(0,12)
axs[4].grid(True)

axs[3].scatter(x_pH,y_pH,s=2,c='green')
axs[3].scatter(x_Temp,y_Temp,s=2,c='orange')
#axs[0].set_xlim(0,)
axs[3].set_xlabel('Time')
axs[3].set_ylabel('pH and Temp')
axs[3].grid(True)
#fig.tight_layout()
plt.show()
