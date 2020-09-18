'''
Created on 15/03/2020

@author: Fletcher Gilbertson 
'''
import matplotlib.pyplot as plt
import pandas as pd
from ConfigurationFiles import configReactorFlow as Flow
from ConfigurationFiles import configReactorDim as Dimen
from math import pi

ReacTable = ['R1Outlet','R2Outlet','R3Outlet','R4Outlet','R1Inlet','R2Inlet','R3Inlet','R4Inlet']
Reactors = ['R1','R2','R3','R4']

for i in range(0,4):
    # importing data files containing gas concentration and defining variables for plottting
    OutletFileIR = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_'+ReacTable[i]+'.csv')
    xraw = pd.to_datetime(OutletFileIR['Date'],format='%Y-%m-%d')
    xOutvalIR = [index for index in range(10,len(xraw))]
    #datetime.datetime.strptime()
    #xOutvalIR = []
    #Day0 = xraw.iloc[0]
    #xOutvalIR.append(0)
    #for p in range(0,len(xraw)):
        #if p == 0:
            #continue
        #daynow = xraw.iloc[p]
        #daybef = xraw.iloc[p-1]
        #daydelta = daynow - daybef
        #xOutvalIR.append(xOutvalIR[p-1]+daydelta.days)
#   rangex =  endx - startx
#   xOutvalIR = np.arange(rangex.days)
    yOutCH4 = OutletFileIR['CH4 (%v/v)'][10:len(OutletFileIR)]
    yOutCO2 = OutletFileIR['CO2 (%v/v)'][10:len(OutletFileIR)]
    Temper = OutletFileIR['Temperature (C)']+273.15 #Kelvin
    print(len(yOutCH4),len(xOutvalIR))
    
    InletFileIR = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_'+ReacTable[i+4]+'.csv')
    xraw = pd.to_datetime(InletFileIR['Date'],format='%Y-%m-%d')
    xInvalIR = [index for index in range(10,len(xraw))]
    #datetime.datetime.strptime()
    #xInvalIR = []
    #Day0 = xraw.iloc[0]
    #xInvalIR.append(0)
    #for p in range(0,len(xraw)):
        #if p == 0:
            #continue
        #daynow = xraw.iloc[p]
        #daybef = xraw.iloc[p-1]
        #daydelta = daynow - daybef
        #xInvalIR.append(xInvalIR[p-1]+daydelta.days)
    yInCH4 = InletFileIR['CH4 (%v/v)'][10:len(InletFileIR)]
    yInCO2 = InletFileIR['CO2 (%v/v)'][10:len(InletFileIR)]
    print(len(yInCH4),len(xInvalIR))
    
    OutletFileO2 = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal'+ReacTable[i]+'.csv')
    xraw = pd.to_datetime(OutletFileO2['Date'],format='%Y-%m-%d')
    xOutO2 = [index for index in range(10,len(xraw))]
    #if i == 0:
        #xraw = xraw[10:len(xraw)]
    #else:
        #xraw = xraw[10:len(xraw)]
    #datetime.datetime.strptime()
    #xOutO2 = []
    #Day0 = xraw.iloc[0]
    #xOutO2.append(0)
    #for p in range(0,len(xraw)):
        #if p == 0:
            #continue
        #daynow = xraw.iloc[p]
        #daybef = xraw.iloc[p-1]
        #daydelta = daynow - daybef
        #xOutO2.append(xOutO2[p-1]+daydelta.days)
    yOutO2 = OutletFileO2['O2 (%v/v)']
    yOutO2 = yOutO2[10:len(yOutO2)]
    #if i == 0:
        #yOutO2 = yOutO2[10:len(yOutO2)]
    #else:
        #yOutO2 = yOutO2[10:len(yOutO2)]
    print(len(yOutO2),len(xOutO2))
    
    InletFileO2 = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal'+ReacTable[i+4]+'.csv')
    xraw = pd.to_datetime(InletFileO2['Date'],format='%Y-%m-%d')
    xInO2 = [index for index in range(10,len(xraw))]
    #if i == 0:
        #xraw = xraw[len(xraw)-14:len(xraw)]
    #else:
        #xraw = xraw[len(xraw)-21:len(xraw)]
    ##datetime.datetime.strptime()
    #xInO2 = []
    #Day0 = xraw.iloc[0]
    #xInO2.append(0)
    #for p in range(0,len(xraw)):
        #if p == 0:
            #continue
        #daynow = xraw.iloc[p]
        #daybef = xraw.iloc[p-1]
        #daydelta = daynow - daybef
        #xInO2.append(xInO2[p-1]+daydelta.days)
    yInO2 = InletFileO2['O2 (%v/v)']
    yInO2 = yInO2[10:len(yInO2)]
    #if i == 0:
        #yInO2 = yInO2[10:len(yInO2)]
    #else:
        #yInO2 = yInO2[10:len(yInO2)]
    print(len(yInO2),len(xInO2))
    
    # calling reactor inlet flow rates in config file
    if i == 0:
        RFlow = Flow.dfFlow.iloc[1,2] #R1 flow
    elif i == 1:
        RFlow = Flow.dfFlow.iloc[1,4] #R2 flow
    elif i == 2:
        RFlow = Flow.dfFlow.iloc[1,6] #R3 flow
    elif i == 3:
        RFlow = Flow.dfFlow.iloc[1,8] #R4 flow

    # calculating biotrickling bed parameters: pumice rock bed
    Vempty = pi*((Dimen.dfBedDim.iloc[1,i+1]/2)**2)*Dimen.dfBedDim.iloc[0,i+1] # Reactor empty bed volume (cm^3) = pi*h*(d/2)^2 
    Vbed = Dimen.dfBedDim.iloc[2,i+1]*Dimen.dfMater.iloc[0,4]/(Dimen.dfMater.iloc[0,5]*1000) # (cm^3) Reactor bed solid volume based on total bed weight, individual packing bead weight and volume
    Bedpor = 1 - Vbed/Vempty # porosity of reactor bed packing (interstial space in void)
    # empty bed residence time calculation
    EBRT = Vempty/RFlow # units: min
    
    # calculate molecular weight of gas mixture based on inlet composition from sensor data: used weighted average for calculation 
    MW_mix = (yInCH4*Flow.MWCH4/100) + (yInCO2*Flow.MWCO2/100) + (yInO2*Flow.MWO2/100) + ((100-yInCH4-yInCO2-yInO2)*Flow.MWN2/100)
    # calculating EC using flow rate data in configReactorFlow and imported gas concentration data above 
    EC_CH4 = (yInCH4 - yOutCH4)*Flow.P*Flow.MWCH4*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    ECmol_CH4 = (yInCH4 - yOutCH4)*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT) # units: mmol / m3-hour
    CO2_Recov = (yOutCO2-yInCO2)*100/yInCH4 #Note: %v/v = mol/mol fraction under the assumptions of ideal gas law and the combustion of 1 mol CH4 yields 1 mol CO2 so no conversions are neccesary
    _yInCH4 = yInCH4*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT) # units: mmol / m3-hour
    _yInCO2 = yInCO2*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT)
    _yInO2 = yInO2*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT)
    _yOutCH4 = yOutCH4*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT) # units: mmol / m3-hour
    _yOutCO2 = yOutCO2*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT)
    _yOutO2 = yOutO2*Flow.P*60*1000*1000/(100*Flow.R*Temper*EBRT)
    
    
    fig, RecPlot = plt.subplots(3, sharex=True,figsize=(7, 7))
    #fig, graphR2 = plt.subplots(3, sharex=True,figsize=(7, 7))
    #fig, graphR3 = plt.subplots(3, sharex=True,figsize=(7, 7))
    #fig, graphR4 = plt.subplots(3, sharex=True,figsize=(7, 7))
    #RecPlot = [graphR1,graphR2,graphR3,graphR4]
    
    color = ['blue','red','green']
    yGraph = ECmol_CH4
    axCH4 = RecPlot[0]
    l1=axCH4.scatter(xInvalIR,yInCH4,facecolors='none',edgecolors='blue')
    l2=axCH4.scatter(xOutvalIR,yOutCH4,c=color[0])
    #ax1.scatter(xOutvalIR,yInCH4-yOutCH4,c=color[0])
    axCO2 = RecPlot[1]
    #axs[i,0].scatter(xInvalIR,yInCH4,c=color[0])
    l3=axCO2.scatter(xInvalIR,yInCO2,facecolors='none',edgecolors='red')
    l4=axCO2.scatter(xOutvalIR,yOutCO2,c=color[1])
    #ax2.scatter(xOutvalIR,yOutCO2-yInCO2,c=color[1])
    #ax2.set_ylabel('CO2 Recovery (%)')
    axCO2.set_ylabel('CO2 (%v/v)')
    axCO2.grid(True)
    #ax2.set_ylim(0,1+amax(CO2_Recov))
    #axs[i,0].scatter(xInvalIR,yInCO2,c=color[1])
    #axs[0].set_xlim(0,)
    #axCH4.set_xlabel('Day')
    #ax1.set_ylabel('EC (mmol/m3-hour)')
    axCH4.set_ylabel('CH4 (%v/v)')
    #ax1.set_ylim(0,amax(yGraph)+0.01*amax(yGraph))
    axCH4.grid(True)
    axCH4.set_title(Reactors[i])
    
    axO2 = RecPlot[2]
    l5=axO2.scatter(xInO2,yInO2,facecolors='none',edgecolors='green')
    l6=axO2.scatter(xOutO2,yOutO2,c=color[2])
    axO2.set_xlabel('Day')
    axO2.set_ylabel('O2 (%v/v)')
    axO2.grid(True)
   
    # Labels to use in the legend for each line
    line_labels = ["Inlet CH4","Outlet CH4","Inlet CO2","Outlet CO2","Inlet O2","Outlet O2"]

    # Create the legend
    #fig.legend([l1,l2,l3,l4,l5,l6],     # The line objects
                #labels=line_labels,   # The labels for each line
                #loc="center right",
 ##                bbox_to_anchor=(0.5, -0.05),
                #fancybox=True, 
                #shadow=True,
                 ##ncol=6,  # Position of legend
                #borderaxespad=0.1,    # Small spacing around legend box
                #title="Legend"  # Title for the legend
                #)
    #plt.subplots_adjust(right=0.85)
    #RecPlot[i][2].set_title(Reactors[i])
    
fig.tight_layout()
plt.show()
