'''
Created on 15/03/2020

@author: Fletcher Gilbertson 
'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cmath import pi
from numpy import amax
import datetime

#relative package import
from ConfigurationFiles import configReactorFlow as Flow
from ConfigurationFiles import configReactorDim as Mater
from ConfigurationFiles import configReactorDim as Dimen
#from DataTrimming import startEnd

Day0 = '2020-05-28'
Day0Epoch = int(datetime.datetime(2020,5,5,0,0).strftime('%s')) #date for reactor start converted to seconds since epoch
ReacTable = ['R1Outlet','R2Outlet','R3Outlet','R4Outlet','R1Inlet','R2Inlet','R3Inlet','R4Inlet']
FileDir = {'Reactor1':'/home/pi/BTF_reactors/log/Reactor1/master.csv','Reactor2':'/home/pi/BTF_reactors/log/Reactor2/master.csv','Reactor3':'/home/pi/BTF_reactors/log/Reactor3/master.csv','Reactor4':'/home/pi/BTF_reactors/log/Reactor4/master.csv'}
Reactors = ['Reactor1','Reactor2','Reactor3','Reactor4']
fig, axs = plt.subplots(nrows=4, ncols=2,figsize=(7, 7))

for i in range(0,4):
    # importing data files containing gas concentration and defining variables for plottting
    ReactorData = pd.read_csv(FileDir[Reactors[i]])
    TimeIndex = np.array(ReactorData['TimeIndex']) #time stamp when measurement taken representing seconds since epoch
    Day = (TimeIndex - Day0Epoch)/86400 #Day of each reading since reactor start
    
    CH4_in = np.array(ReactorData['Inlet CH4(%v/v)'])
    CH4_in_STD = np.array(ReactorData['STD-InCH4'])
    CH4_out = np.array(ReactorData['Outlet CH4(%v/v)'])
    CH4_out_STD = np.array(ReactorData['STD-OutCH4'])
    CO2_in = np.array(ReactorData['Inlet CO2(%v/v)'])
    CO2_in_STD = np.array(ReactorData['STD-InCO2'])
    CO2_out = np.array(ReactorData['Outlet CO2(%v/v)'])
    CO2_out_STD = np.array(ReactorData['STD-OutCO2'])
    O2_in = np.array(ReactorData['Inlet O2(%v/v)'])
    O2_in_STD = np.array(ReactorData['STD-InO2'])
    O2_out = np.array(ReactorData['Outlet O2 (%v/v)'])
    O2_out_STD = np.array(ReactorData['STD-OutO2'])
    Temper = 318.15 #K or 45C    
    
    # calling reactor inlet flow rates in config file
    if i == 0:
        RFlow = Flow.dfFlow.iloc[2,1] #R1 flow
    elif i == 1:
        RFlow = Flow.dfFlow.iloc[2,3] #R2 flow
    elif i == 2:
        RFlow = Flow.dfFlow.iloc[2,5] #R3 flow
    elif i == 3:
        RFlow = Flow.dfFlow.iloc[2,7] #R4 flow

    # calculating biotrickling bed parameters: glass bead bed
    Vempty = pi*((Dimen.dfBedDim.iloc[1,i+1]/2)**2)*Dimen.dfBedDim.iloc[0,i+1] # Reactor empty bed volume (cm^3) = pi*h*(d/2)^2 
    Vbed = Dimen.dfBedDim.iloc[2,i+1]*Mater.dfMater.iloc[0,4]/(Mater.dfMater.iloc[0,5]*1000) # (cm^3) Reactor bed solid volume based on total bed weight, individual packing bead weight and volume
    Bedpor = 1 - Vbed/Vempty # porosity of reactor bed packing (interstial space in void)
    # empty bed residence time calculation
    EBRT = Vempty/RFlow # units: min
    
    # calculate molecular weight of gas mixture based on inlet composition from sensor data: used weighted average for calculation 
    #MW_mix = (yInCH4*Flow.MWCH4/100) + (yInCO2*Flow.MWCO2/100) + (yInO2*Flow.MWO2/100) + ((100-yInCH4-yInCO2-yInO2)*Flow.MWN2/100)
    # calculating EC using flow rate data in configReactorFlow and imported gas concentration data above 
    EC_CH4 = (CH4_in - CH4_out)*Flow.P*Flow.MWCH4*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    ECmol_CH4 = EC_CH4*1000/Flow.MWCH4 # units: mmol / m3-hour
    
    PC_CO2 = (CO2_out-CO2_in)*Flow.P*Flow.MWCO2*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    PCmol_CO2 = PC_CO2*1000/Flow.MWCO2 # units: mmol / m3-hour
    
    EC_O2 = (O2_in - O2_out)*Flow.P*Flow.MWO2*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    ECmol_O2 = EC_O2*1000/Flow.MWO2 # units: mmol / m3-hour
    
    CO2_Recov = (CO2_in - CO2_out)*100/CH4_in #Note: %v/v = mol/mol fraction under the assumptions of ideal gas law and the combustion of 1 mol CH4 yields 1 mol CO2 so no conversions are neccesary
    
    color = ['blue','red','green']
    yGraph = ECmol_CH4
    ax1 = axs[i,0]
    #ax1.scatter(xOutvalIR,yGraph,c=color[0])
    ax1.scatter(Day,ECmol_CH4,c=color[0])
    #ax1.scatter(xOutvalIR,yInCH4-yOutCH4,c=color[0])
    ax2 = axs[i,0].twinx()
    #axs[i,0].scatter(xInvalIR,yInCH4,c=color[0])
    #ax2.scatter(xOutvalIR,CO2_Recov,c=color[1])
    ax2.scatter(Day,PCmol_CO2,c=color[1])
    #ax2.scatter(xOutvalIR,yOutCO2-yInCO2,c=color[1])
    ax2.set_ylabel('PC (mmol/m3-hour)')
    #ax2.set_ylim(0,1+amax(CO2_Recov))
    #axs[i,0].scatter(xInvalIR,yInCO2,c=color[1])
    #axs[0].set_xlim(0,)
    ax1.set_xlabel('Day')
    ax1.set_ylabel('EC (mmol/m3-hour)')
    #ax1.set_ylim(0,amax(yGraph)+0.01*amax(yGraph))
    ax1.grid(True)
    ax1.set_title(Reactors[i])
    
    axs[i,1].scatter(Day,ECmol_O2,c=color[2])
    #axs[i,1].scatter(xOutO2,yInO2-yOutO2,c=color[2])
    #axs[i,1].scatter(xInO2,yInO2,c=color[2])
    axs[i,1].set_xlabel('Day')
    axs[i,1].set_ylabel('EC (mmol/m3-hour)')
    axs[i,1].grid(True)
    axs[i,1].set_title(Reactors[i])
    
fig.tight_layout()
plt.show()