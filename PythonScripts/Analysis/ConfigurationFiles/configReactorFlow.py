'''
Created on 13/03/2020

@author: Fletcher Gilbertson
'''
import pandas as pd

# Gas parameters - need proper reference, for now EngineeringToolBox
# all gas parameters are based on pure gas at 1 atm and temperature from internal thermistor or sensor 
MWCH4 = 16.04
MWCO2 = 44.01
MWO2 = 32.0
MWN2 = 28.01

# system parameters
P = 1 #atm pressure of reactor inlet stream
R = 0.08206 #L-atm/gmol-K universal gas constant

dFlow = {'Date':['16/03/2020','10/06/2020'],
       'R1 Flow In (ml/min)':[9.4282,10],
       'R1 In STD':[0.0535,0.0535],
       'R2 Flow In (ml/min)':[8.4290,20],
       'R2 In STD':[0.1599,0.0535,],
       'R3 Flow In (ml/min)':[11.2904,20],
       'R3 In STD':[0.2263,0.0535],
       'R4 Flow In (ml/min)':[13.0727,20],
       'R4 In STD':[0.3305,0.0535],
       'R1 Flow Out (ml/min)':[10.3853,10],
       'R1 Out STD':[0.160,10.0535],
       'R2 Flow Out (ml/min)':[9.6044,20],
       'R2 Out STD':[0.4148,0.0535],
       'R3 Flow Out (ml/min)':[10.8223,20],
       'R3 Out STD':[0.4730,0.0535],
       'R4 Flow Out (ml/min)':[14.9861,20],
       'R4 Out STD':[1.4631,0.0535]}

dfFlow = pd.DataFrame(dFlow,columns=['Date','R1 Flow In (ml/min)','R1 In STD','R2 Flow In (ml/min)','R2 In STD','R3 Flow In (ml/min)','R3 In STD','R4 Flow In (ml/min)','R4 In STD','R1 Flow Out (ml/min)','R1 Out STD','R2 Flow Out (ml/min)','R2 Out STD','R3 Flow Out (ml/min)','R3 Out STD','R4 Flow Out (ml/min)','R4 Out STD'])