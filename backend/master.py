#system imports
import time

#modue imports
import datacollection
import sumpRemoval_dataCollection
import gasSensorCheck_dataCollection 
from threading import Event
from controlPhidgets import PhidgetSolidStateRelay_REL1101

polling = True

inlet_time=6000 #measurement time (sec) for the inlet of reactor
outlet_time=4000

valvSchedule = ["Reactor1","Reactor2","Reactor3","Reactor4"]
sumpSchedule = ["Reactor2","Reactor3","Reactor4"]
thermocouple = ['K-Type_Incubator','K-Type_Reactor2','K-Type_Reactor3','K-Type_Reactor4']
sumpThermocouple = ['K-Type_Reactor2','K-Type_Reactor3','K-Type_Reactor4']
pH = ['pH_Reactor1','pH_Reactor2','pH_Reactor3','pH_Reactor4']
sumppH = ['pH_Reactor2','pH_Reactor3','pH_Reactor4']
pressure_drop = ['dP_Reactor1','dP_Reactor2','dP_Reactor3','dP_Reactor4']

def pressureSensorCheck():
    pass

def reactorMeasure():
    for v in range(0,len(valvSchedule)):
        e = Event()
        data = datacollection.main(valvSchedule[v],inlet_time,outlet_time,thermocouple[v],pH[v],pressure_drop[v],e)
        print(data)
            
def gasSensorCheck():
    e  = Event()
    address = datacollection.addressMap['SMC_Valve_ViciCommon']
    
    # open valve connecting calibration gas to gas sensors 
    smcValve = PhidgetSolidStateRelay_REL1101(commConfig=address,sensorName='SMC Valve',threadName='SMC Valve_calibration gas',eventType='open',event=e)
    smcValve.initDevice()
    smcValve.connect(address.channel)
    smcValve.startThread()
    
    # open Alicat connections and start gas flow schedule + checks
    gasSensorCheck_dataCollection.main(e)
   
    # stop all open threads
    smcValve.stopThread()

def gasSensorCalibration():
    pass

def sumpRemoval():
    for v in range(0,len(sumpSchedule)):
        e = Event()
        data = sumpRemoval_dataCollection.main(sumpSchedule[v],sumpThermocouple[v],sumppH[v],e)
        print(data)

def main():
    while polling:
        """
            1. system whide checks (check sensor span and zeros, set inlet reactor gas concentrations, blank pressure sensor and take zero diff pressure reading,
               check humidity sensor stability)
            ## When checking sensors store calibration, zero readings in config files for each sensor
            2. measure reactor parameters: gas concentrations, temp, pH, pressure
            3. bed vs. sump removal tests
        """
        #humSensorCheck()
        #pgasSensorCheck()
        #for i in range(0,3):
        #gasSensorCheck()
        reactorMeasure()
        #sumpRemoval()
    
if __name__ == "__main__":
    main()
    
    
