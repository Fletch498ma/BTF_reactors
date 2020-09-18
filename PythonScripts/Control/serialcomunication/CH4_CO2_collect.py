'''
Created on 8/03/2020

@author: Fletcher Gilbertson
'''
from Gas_dataCollect import Master_control
from time import sleep

valvSchedule = [2,6,3,7,4,8,1,5]
valvTime = 3700
while True:
    for i in range(0,len(valvSchedule)):
#        if i < 3:
#            RunTest = Master_control(valvSchedule[i],7200)
#            RunTest.valve_control()
#            RunTest.IR_dataCollect()
#        else: 
        RunTest = Master_control(valvSchedule[i],valvTime)
        RunTest.valve_control()
        RunTest.IR_dataCollect()
        
