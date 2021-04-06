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
import math

#relative package import
from ConfigurationFiles import configReactorFlow as Flow
from ConfigurationFiles import configReactorDim as Mater
from ConfigurationFiles import configReactorDim as Dimen
#from DataTrimming import startEnd

Day0 = '2020-05-28'
Day0Epoch = int(datetime.datetime(2020,5,5,0,0).strftime('%s')) #date for reactor start converted to seconds since epoch
ReacTable = ['R1Outlet','R2Outlet','R3Outlet','R4Outlet','R1Inlet','R2Inlet','R3Inlet','R4Inlet']
FileDir = {"Reactor1":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor1/master.csv',
                 "Reactor2":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor2/master.csv',
                 "Reactor3":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor3/master.csv',
                 "Reactor4":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor4/master.csv'}
Reactors = ['Reactor1','Reactor2','Reactor3','Reactor4']

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
    Hum_in = np.array(ReactorData['Inlet RelativeHumidity(%)'])
    Hum_in_STD = np.array(ReactorData['STD-InletHumidity'])
    Hum_out = np.array(ReactorData['Outlet RelativeHumidity(%)'])
    Hum_out_STD = np.array(ReactorData['STD-OutletHumidity'])
    Pres_in = np.array(ReactorData['Inlet Pressure (kPa)'])
    Pres_in_STD = np.array(ReactorData['STD-InletPressure'])
    Pres_out = np.array(ReactorData['Outlet Pressure (kPa)'])
    Pres_out_STD = np.array(ReactorData['STD-OutletPressure'])
    pH = np.array(ReactorData['pH'])
    
    #Humidity = np.array(ReactorData['RelativeHumidity(%)'])
    #Humidity_STD = np.array(ReactorData['STD-Humidity'])
    
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
    Vempty = 517#pi*((Dimen.dfBedDim.iloc[1,i+1]/2)**2)*Dimen.dfBedDim.iloc[0,i+1] # Reactor empty bed volume (cm^3) = pi*h*(d/2)^2 
    Vbed = Dimen.dfBedDim.iloc[2,i+1]*Mater.dfMater.iloc[0,4]/(Mater.dfMater.iloc[0,5]*1000) # (cm^3) Reactor bed solid volume based on total bed weight, individual packing bead weight and volume
    Bedpor = 1 - Vbed/Vempty # porosity of reactor bed packing (interstial space in void)
    # empty bed residence time calculation
    EBRT = Vempty/RFlow # units: min
    print(EBRT)
    # calculate molecular weight of gas mixture based on inlet composition from sensor data: used weighted average for calculation 
    #MW_mix = (yInCH4*Flow.MWCH4/100) + (yInCO2*Flow.MWCO2/100) + (yInO2*Flow.MWO2/100) + ((100-yInCH4-yInCO2-yInO2)*Flow.MWN2/100)
    # calculating EC using flow rate data in configReactorFlow and imported gas concentration data above 
    EC_CH4 = (CH4_in - CH4_out)*Flow.P*Flow.MWCH4*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    ECmol_CH4 = EC_CH4/Flow.MWCH4 # units: mol / m3-hour
    
    PC_CO2 = (CO2_out-CO2_in)*Flow.P*Flow.MWCO2*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    PCmol_CO2 = PC_CO2/Flow.MWCO2 # units: mol / m3-hour
    
    EC_O2 = (O2_in - O2_out)*Flow.P*Flow.MWO2*60*1000/(100*Flow.R*Temper*EBRT) # units: g / m3-hour
    ECmol_O2 = EC_O2/Flow.MWO2 # units: mol / m3-hour
    
    CO2_Recovery = (CO2_out - CO2_in)*100/CH4_in #Note: %v/v = mol/mol fraction under the assumptions of ideal gas law and the combustion of 1 mol CH4 yields 1 mol CO2 so no conversions are neccesary
    
    O2_C_Ratio = (O2_in-O2_out)/(CH4_in-CH4_out)
    
    PresDrop = Pres_in - Pres_out

    fig, RecPlot = plt.subplots(4, figsize=(7, 7))
    #fig, graphR2 = plt.subplots(3, sharex=True,figsize=(7, 7))
    #fig, graphR3 = plt.subplots(3, sharex=True,figsize=(7, 7))
    #fig, graphR4 = plt.subplots(3, sharex=True,figsize=(7, 7))
    #RecPlot = [graphR1,graphR2,graphR3,graphR4]
    
    color = ['blue','red','green','purple']
    axCH4 = RecPlot[0]
    #l1=axCH4.scatter(Day,EC_CH4,facecolors='none',edgecolors='blue')
    l2=axCH4.scatter(Day,ECmol_CH4,c=color[0])
    axCH4.set_title(Reactors[i])
    axCH4.set_ylabel(r'$CH_4\ Removal$' + '\n' + r'$\left(\frac{mol}{m^3 -hour}\right)$',fontsize = 14,verticalalignment='center',rotation='horizontal')
    axCH4.yaxis.set_label_coords(-0.08,0.5)
    CH4err = np.power(CH4_in_STD**2 + CH4_out_STD**2,0.5)
    axCH4.grid(True)
    
    axCO2 = RecPlot[1]
    #l3=axCO2.scatter(xInvalIR,yInCO2,facecolors='none',edgecolors='red')
    l4=axCO2.scatter(Day,PCmol_CO2,c=color[1])
    axCO2.set_ylabel(r'$CO_2\ Production$' + '\n' + r'$\left(\frac{mol}{m^3 -hour}\right)$',fontsize = 14,verticalalignment='center',rotation='horizontal')
    CO2err = np.power(CO2_out_STD**2 + CO2_in_STD**2,0.5)
    axCO2.yaxis.set_label_coords(-0.08,0.5)
    axCO2.grid(True)
    #ax2.set_ylim(0,1+amax(CO2_Recov))
    #axs[0].set_xlim(0,)
    #ax1.set_ylim(0,amax(yGraph)+0.01*amax(yGraph))
    
    axO2 = RecPlot[2]
    #l5=axO2.scatter(xInO2,yInO2,facecolors='none',edgecolors='green')
    l6=axO2.scatter(Day,ECmol_O2,c=color[2])
    axO2.set_xlabel('Days',fontsize='x-large')
    #axO2.set_yticklabels(fontsize='12')
    axO2.set_ylabel(r'$O_2\ Removal$' + '\n' + r'$\left(\frac{mol}{m^3 -hour}\right)$',fontsize = 14,verticalalignment='center',rotation='horizontal')
    O2err = np.power(O2_out_STD**2 + O2_in_STD**2,0.5)
    axO2.yaxis.set_label_coords(-0.08,0.5)
    axO2.grid(True)
    
    axPres = RecPlot[3]
    axPres.scatter(Day,PresDrop,c=color[3])
    axPres.set_xlabel('Days',fontsize='x-large')
    #axO2.set_yticklabels(fontsize='12')
    axPres.set_ylabel('Pressure drop' + '\n' + '(kPa)',fontsize = 14,verticalalignment='center',rotation='horizontal')
    Preserr = np.power(Pres_out_STD**2 + Pres_in_STD**2,0.5)
    axPres.yaxis.set_label_coords(-0.08,0.5)
    axPres.grid(True)
    
    #error bars
    axCH4.errorbar(Day, ECmol_CH4, yerr = CH4_out_STD, fmt = 'none', ecolor='gray', lw=2, capsize=5, capthick=2)
    axCO2.errorbar(Day, PCmol_CO2, yerr = CO2_out_STD, fmt ='none',ecolor='gray', lw=2, capsize=5, capthick=2,)
    axO2.errorbar(Day, ECmol_O2, yerr = O2_out_STD, fmt ='none',ecolor='gray', lw=2, capsize=5, capthick=2,) 
    axPres.errorbar(Day, PresDrop, yerr = Pres_out_STD, fmt ='none',ecolor='gray', lw=2, capsize=5, capthick=2,)
    
    # Labels to use in the legend for each line
    #line_labels = ["Inlet CH4","Outlet CH4","Inlet CO2","Outlet CO2","Inlet O2","Outlet O2"]

    # Create the legend
#     fig.legend([l1,l2,l3,l4,l5,l6],     # The line objects
#                labels=line_labels,   # The labels for each line
#                loc="center right",
# #                bbox_to_anchor=(0.5, -0.05),
#                 fancybox=True, 
#                 shadow=True,
#                 #ncol=6,  # Position of legend
#                borderaxespad=0.1,    # Small spacing around legend box
#                title="Legend"  # Title for the legend
#                )
#     plt.subplots_adjust(right=0.85)
    #RecPlot[i][2].set_title(Reactors[i])


#    fig2, RecPlot2 = plt.subplots(4, figsize=(7, 7))
#    
#    color = ['blue','red','green','purple']
#    axCH4 = RecPlot2[0]
#    #l1=axCH4.scatter(Day,EC_CH4,facecolors='none',edgecolors='blue')
#    l2=axCH4.scatter(Day,EC_CH4,c=color[0])
#    axCH4.set_title(Reactors[i])
#    axCH4.set_ylabel(r'$CH_4\ EC$' + '\n' + r'$\left(\frac{g}{m^3 -hour}\right)$',fontsize = 12,verticalalignment='center',rotation='horizontal')
#    axCH4.yaxis.set_label_coords(-0.08,0.5)
#    #CH4err = np.power(CH4_in_STD**2 + CH4_out_STD**2,0.5)
#    axCH4.grid(True)
#    
#    axCO2 = RecPlot2[1]
#    #l3=axCO2.scatter(xInvalIR,yInCO2,facecolors='none',edgecolors='red')
#    l4=axCO2.scatter(Day,CO2_Recovery,c=color[1])
#    axCO2.set_ylabel('CO2 Recovery(%)',fontsize = 12,verticalalignment='center',rotation='horizontal')
#    #CO2err = np.power(CO2_out_STD**2 + CO2_in_STD**2,0.5)
#    axCO2.yaxis.set_label_coords(-0.08,0.5)
#    axCO2.grid(True)
#    #ax2.set_ylim(0,1+amax(CO2_Recov))
#    #axs[0].set_xlim(0,)
#    #ax1.set_ylim(0,amax(yGraph)+0.01*amax(yGraph))
#    
#    axO2 = RecPlot2[2]
#    #l5=axO2.scatter(xInO2,yInO2,facecolors='none',edgecolors='green')
#    l6=axO2.scatter(Day,O2_C_Ratio,c=color[2])
#    axO2.set_xlabel('Days',fontsize='x-large')
#    #axO2.set_yticklabels(fontsize='12')
#    axO2.set_ylabel(r'O_2 to CH_4' + '\n' + r'Ratio',fontsize = 12,verticalalignment='center',rotation='horizontal')
#    #O2err = np.power(O2_out_STD**2 + O2_in_STD**2,0.5)
#    axO2.yaxis.set_label_coords(-0.08,0.5)
#    axO2.grid(True)
#    
#    axPres = RecPlot2[3]
#    axPres.scatter(Day,PresDrop,c=color[3])
#    axPres.set_xlabel('Days',fontsize='x-large')
#    #axO2.set_yticklabels(fontsize='12')
#    axPres.set_ylabel('Pressure drop' + '\n' + '(kPa)',fontsize = 12,verticalalignment='center',rotation='horizontal')
#    Preserr = np.power(Pres_out_STD**2 + Pres_in_STD**2,0.5)
#    axPres.yaxis.set_label_coords(-0.08,0.5)
#    axPres.grid(True)
    
    #error bars
#    axCH4.errorbar(Day, ECmol_CH4, yerr = CH4_out_STD, fmt = 'none', ecolor='gray', lw=2, capsize=5, capthick=2)
#    axCO2.errorbar(Day, PCmol_CO2, yerr = CO2_out_STD, fmt ='none',ecolor='gray', lw=2, capsize=5, capthick=2,)
#    axO2.errorbar(Day, ECmol_O2, yerr = O2_out_STD, fmt ='none',ecolor='gray', lw=2, capsize=5, capthick=2,) 
#    axPres.errorbar(Day, PresDrop, yerr = Pres_out_STD, fmt ='none',ecolor='gray', lw=2, capsize=5, capthick=2,)
    
    # Labels to use in the legend for each line
    #line_labels = ["Inlet CH4","Outlet CH4","Inlet CO2","Outlet CO2","Inlet O2","Outlet O2"]

    # Create the legend
#     fig.legend([l1,l2,l3,l4,l5,l6],     # The line objects
#                labels=line_labels,   # The labels for each line
#                loc="center right",
# #                bbox_to_anchor=(0.5, -0.05),
#                 fancybox=True, 
#                 shadow=True,
#                 #ncol=6,  # Position of legend
#                borderaxespad=0.1,    # Small spacing around legend box
#                title="Legend"  # Title for the legend
#                )
#     plt.subplots_adjust(right=0.85)
    #RecPlot[i][2].set_title(Reactors[i])
fig.tight_layout()
#fig2.tight_layout()
plt.show()

