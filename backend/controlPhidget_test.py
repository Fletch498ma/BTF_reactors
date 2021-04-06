from controlPhidgets import PhidgetSolidStateRelay_REL1101
from datacollection import Address, addressMap
from threading import Event
from time import sleep

e = Event()
address1 = addressMap['SMC_Valve_ViciCommon']
address2 = addressMap['SMC_Valve_Port3Manifold']
#address3 =
#address4 =
#address5 =

index = 0
valve = True
while valve:
    index += 1

    relay1 = PhidgetSolidStateRelay_REL1101(commConfig=address1,sensorName='SMC Valve',threadName='SMC Valve_test',eventType='close',event=e)
    relay2 = PhidgetSolidStateRelay_REL1101(commConfig=address2,sensorName='SMC Valve',threadName='SMC Valve_test',eventType='close',event=e)
        
    conn = {'address':[address2,address1],'relay':[relay2,relay1]}

    for i in range(0,2):
        try:  
            conn['relay'][i].initDevice()
            conn['relay'][i].connect(conn['address'][i].channel)
            conn['relay'][i].startThread()
            sleep(2)
            print("waiting...")
        except KeyboardInterrupt:
            print("Exiting")
    
    relay1.stopThread()
    relay2.stopThread()
    
    sleep(1)
    
    if index == 2:
        valve = False