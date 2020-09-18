'''
Created on 15/03/2020

@author: Fletcher Gilbertson 
'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ConfigurationFiles import configReactorFlow as Flow
from ConfigurationFiles import configReactorDim as Mater
from ConfigurationFiles import configReactorDim as Dimen
from cmath import pi
from numpy import amax

ReacTable = ['R1Outlet','R2Outlet','R3Outlet','R4Outlet','R1Inlet','R2Inlet','R3Inlet','R4Inlet']
Reactors = ['R1','R2','R3','R4']
fig, axs = plt.subplots(nrows=4, ncols=2,figsize=(7, 7))

for i in range(0,4):
    days = 14
    # importing data files containing gas concentration and defining variables for plottting
    OutletFileIR = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_'+ReacTable[i]+'.csv')
    fileLength = len(OutletFileIR['Time'])
    xOutvalIR = np.arange(days)
    yOutCH4 = OutletFileIR['CH4 (%v/v)'][fileLength-days:fileLength]
    yOutCO2 = OutletFileIR['CO2 (%v/v)'][fileLength-days:fileLength]
    Temper = OutletFileIR['Temperature (C)']+273.15 #Kelvin
    
    InletFileIR = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_'+ReacTable[i+4]+'.csv')
    fileLength = len(InletFileIR['Time'])
    xInvalIR = np.arange(days)
    yInCH4 = InletFileIR['CH4 (%v/v)'][fileLength-days:fileLength]
    yInCO2 = InletFileIR['CO2 (%v/v)'][fileLength-days:fileLength]
    
    daysO2 = 8
    OutletFileO2 = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal'+ReacTable[i]+'.csv')
    fileLength = len(OutletFileO2['Time'])
    xOutO2 = np.arange(daysO2)
    yOutO2 = OutletFileO2['O2 (%v/v)'][fileLength-daysO2:fileLength]
    
    InletFileO2 = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal'+ReacTable[i+4]+'.csv')
    fileLength = len(InletFileO2['Time'])
    xInO2 = np.arange(daysO2)
    yInO2 = InletFileO2['O2 (%v/v)'][fileLength-daysO2:fileLength]
    
    # calling reactor inlet flow rates in config file
    if i == 0:
        RFlow = Flow.dfFlow.iloc[0,1] #R1 flow
    elif i == 1:
        RFlow = Flow.dfFlow.iloc[0,3] #R2 flow
    elif i == 2:
        RFlow = Flow.dfFlow.iloc[0,5] #R3 flow
    elif i == 3:
        RFlow = Flow.dfFlow.iloc[0,7] #R4 flow

    # calculating biotrickling bed parameters: glass bead bed
    Vempty = pi*((Dimen.dfBedDim.iloc[1,i+1]/2)**2)*Dimen.dfBedDim.iloc[0,i+1] # Reactor empty bed volume (cm^3) = pi*h*(d/2)^2 
    Vbed = Dimen.dfBedDim.iloc[2,i+1]*Mater.dfMater.iloc[0,4]/(Mater.dfMater.iloc[0,5]*1000) # (cm^3) Reactor bed solid volume based on total bed weight, individual packing bead weight and volume
    Bedpor = 1 - Vbed/Vempty # porosity of reactor bed packing (interstial space in void)
    # empty bed residence time calculation
    EBRT = Vempty/RFlow # units: min
    
    # calculate molecular weight of gas mixture based on inlet composition from sensor data: used weighted average for calculation 
    MW_mix = (yInCH4*Flow.MWCH4/100) + (yInCO2*Flow.MWCO2/100) + (yInO2*Flow.MWO2/100) + ((100-yInCH4-yInCO2-yInO2)*Flow.MWN2/100)
    # calculating EC using flow rate data in configReactorFlow and imported gas concentration data above 
    EC_CH4 = (yInCH4 - yOutCH4)*Flow.P*Flow.MWCH4*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    ECmol_CH4 = (yInCH4 - yOutCH4)*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT) # units: mmol / m3-hour
    CO2_Recov = (yOutCO2-yInCO2)*100/yInCH4 #Note: %v/v = mol/mol fraction under the assumptions of ideal gas law and the combustion of 1 mol CH4 yields 1 mol CO2 so no conversions are neccesary
    
    color = ['blue','red','green']
    yGraph = ECmol_CH4
    ax1 = axs[i,0]
    #ax1.scatter(xOutvalIR,yGraph,c=color[0])
    ax1.scatter(xOutvalIR,yOutCH4,c=color[0])
    #ax1.scatter(xOutvalIR,yInCH4-yOutCH4,c=color[0])
    ax2 = axs[i,0].twinx()
    #axs[i,0].scatter(xInvalIR,yInCH4,c=color[0])
    #ax2.scatter(xOutvalIR,CO2_Recov,c=color[1])
    ax2.scatter(xOutvalIR,yOutCO2,c=color[1])
    #ax2.scatter(xOutvalIR,yOutCO2-yInCO2,c=color[1])
    ax2.set_ylabel('CO2 Recovery (%)')
    #ax2.set_ylim(0,1+amax(CO2_Recov))
    #axs[i,0].scatter(xInvalIR,yInCO2,c=color[1])
    #axs[0].set_xlim(0,)
    ax1.set_xlabel('Day')
    ax1.set_ylabel('EC (mmol/m3-hour)')
    #ax1.set_ylim(0,amax(yGraph)+0.01*amax(yGraph))
    ax1.grid(True)
    ax1.set_title(Reactors[i])
    
    axs[i,1].scatter(xOutO2,yOutO2,c=color[2])
    #axs[i,1].scatter(xOutO2,yInO2-yOutO2,c=color[2])
    #axs[i,1].scatter(xInO2,yInO2,c=color[2])
    axs[i,1].set_xlabel('Day')
    axs[i,1].set_ylabel('O2 (%v/v)')
    axs[i,1].grid(True)
    axs[i,1].set_title(Reactors[i])
    
fig.tight_layout()
plt.show()