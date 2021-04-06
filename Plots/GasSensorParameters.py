import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
import pandas as pd

# Fixing random state for reproducibility
x_values = []
y_values = []


zeroECdata = pd.read_csv('/home/pi/BTF_reactors/log/ec_ek3/Zero/OldParameters.csv')

TimeIndex = zeroECdata['TimeIndex']
Date = zeroECdata['Date']
ZeroO2 = zeroECdata['Zero O2']
ZeroO2STD = zeroECdata['Zero O2 STD']
Temp = zeroECdata['Temperature (C)']
TempSTD = zeroECdata['Temp STD']
Pres = zeroECdata['Pressure (kPa)']
PresSTD = zeroECdata['Pressure STD']
Hum = zeroECdata['Humidity (%)']
HumSTD = zeroECdata['Humidity STD']

#zeroGasData = pd.read_csv('/home/pi/BTF_reactors/log/ec_ek3/SpanCH4/2021-01-10_08-04-15.csv')
#zeroAlicat = pd.read_csv('/home/pi/BTF_reactors/log/alicat/SpanCH4/2021-01-10_08-04-15.csv')
#zeroPres = pd.read_csv('/home/pi/BTF_reactors/log/phidgets/diffpressure_1136/Zero/2021-01-10_08-04-15.csv')

reactor2 = pd.read_csv('/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor1/master.csv')

time = reactor2['TimeIndex']
CH4IN = reactor2['Inlet CH4(%v/v)']
CH4Out = reactor2['Outlet CH4(%v/v)']
RHIN = reactor2['Inlet RelativeHumidity(%)']
RHOUT = reactor2['Outlet RelativeHumidity(%)']

fig2 = plt.scatter(time,RHIN,c='red')
fig3 = plt.scatter(time,CH4IN)

#TimeIndex2 = zeroGasData['TimeIndex']
#O2Conc = zeroGasData['Concentration(ppm*100)']
#O2Current = zeroGasData['OutputCurrent(nA)']
#TimeIndex = zeroPres['TimeIndex']
#AlicatPres = zeroAlicat['pressure']
#PhidgetPres = zeroPres['Differential Pressure(kPa)']
#
#fig, axs = plt.subplots(2, 1,figsize=(15,15))
#axs[0].scatter(TimeIndex,PhidgetPres,c='blue')
##axs[0].set_xlabel('Date')
#axs[0].set_ylabel('Phidget Pressure (kPa)')
#
#axs[1].scatter(TimeIndex,AlicatPres,c='purple')
#axs[1].set_ylabel('Pressure (kPa)')

#axs[2].scatter(Date,Temp,c='red')
#axs[2].set_ylabel('Temperature (C)')
#
#axs[3].scatter(Date,Hum,c='orange')
#axs[3].set_xlabel('Date')
#axs[3].set_ylabel('Humidity (%)')

#date_form = DateFormatter("%m-%d")
#axs[3].xaxis.set_major_formatter(date_form)
plt.show()

#TimeIndex,Date,Time,Bias(mV),Concentration(ppm*100),OutputCurrent(nA),EC_SpanConcentration(ppm*100),SpanCurrent(nA),temperature