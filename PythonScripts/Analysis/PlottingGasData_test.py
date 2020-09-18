'''
Created on 15/03/2020

@author: Fletcher Gilbertson 
'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cmath import pi
from numpy import amax

#relative package import
from ConfigurationFiles import configReactorFlow as Flow
from ConfigurationFiles import configReactorDim as Mater
from ConfigurationFiles import configReactorDim as Dimen
from DataTrimming import startEnd

Day0 = '2020-05-28'
ReacTable = ['R1Outlet','R2Outlet','R3Outlet','R4Outlet','R1Inlet','R2Inlet','R3Inlet','R4Inlet']
FileDir = ['/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_',
           '/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal']
Reactors = ['R1','R2','R3','R4']
fig, axs = plt.subplots(nrows=4, ncols=2,figsize=(7, 7))

for i in range(0,4):
    # importing data files containing gas concentration and defining variables for plottting
    OutletFileIR = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_'+ReacTable[i]+'.csv')
    xOutvalIR = np.arange(len(OutletFileIR['Date']))
    yOutCH4 = OutletFileIR['CH4 (%v/v)']
    yOutCO2 = OutletFileIR['CO2 (%v/v)']
    Temper = OutletFileIR['Temperature (C)']+273.15 #Kelvin
    
    InletFileIR = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_'+ReacTable[i+4]+'.csv')
    xInvalIR = np.arange(len(InletFileIR['Date']))
    yInCH4 = InletFileIR['CH4 (%v/v)']
    yInCO2 = InletFileIR['CO2 (%v/v)']
    
    OutletFileO2 = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal'+ReacTable[i]+'.csv')
    xOutO2_ = OutletFileO2['Date']
    yOutO2_ = OutletFileO2['O2 (%v/v)']
    O2OutSplice =StartEnd(Day0,xOutO2_,yOutO2_,end='2020-06-10')
    xOutO2 = O2OutSplice[0]
    yOutO2 = O2OutSplice[1]
    print(type(xOutO2))
    
    InletFileO2 = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal'+ReacTable[i+4]+'.csv')
    xIn = InletFileO2['Date']
    yIn = InletFileO2['O2 (%v/v)']
    O2InSplice =startEnd(Day0,xIn,yIn,end='2020-05-31')
    xInO2 = O2InSplice[0]
    yInO2 = O2InSplice[1]
    #xInO2 = np.arange(len(InletFileO2['Date']))
    
    
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