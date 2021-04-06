import sys
import time
import traceback
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *
from Phidget22.Devices.Log import *
from Phidget22.LogLevel import *
from Phidget22.Phidget import *
from Phidget22.Net import *

NUM_CHANNELS = 22
INVALID_VALUE = 1e300

class Address:
    def __init__(self, serialNumber, hubPort, channel, isHubPort, signalType):
            self.serialNumber = serialNumber
            self.hubPort = hubPort
            self.channel = channel
            self.isHubPort = isHubPort
            self.signalType = signalType
    
    #Here we've created an array to map which sensors correspond to a custom index so we can more easily keep track of which sensor is which
    #TODO all serialNumbers, hubPorts, channels, etc should be stored in config files like serial port names fand accessed using configparser 
    def addressMap(self):
            addressMap = {
                'SMC_Valve_ToGasSensors':Address( 607325, 0, 0, False ),
                'SMC_Valve_Port1Manifold':Address( 607325, 0, 1, False ),
                'SMC_Valve_ToGasSensors':Address( 607325, 0, 2, False ),
                'SMC_Valve_Port3Manifold':Address( 607325, 0, 3, False ),
                'SMC_Valve_Port4Manifold':Address( 607325, 0, 4, False ),
                'SMC_Valve_Port5Manifold':Address( 607325, 0, 5, False ),
                'SMC_Valve_Port6Manifold':Address( 607325, 0, 6, False ),
                'SMC_Valve_Port2Manifold':Address( 607325, 0, 7, False ),
            #    None:Address( 607325, 0, 8, False ),
            #    None:Address( 607325, 0, 9, False ),
            #    None:Address( 607325, 0, 10, False ),
            #    None:Address( 607325, 0, 11, False ),
            #    None:Address( 607325, 0, 12, False ),
            #    None:Address( 607325, 0, 13, False ),
            #    None:Address( 607325, 0, 14, False ),
            #    None:Address( 607325, 0, 15, False ),
                'DifPressureSensor_Max2kPa':Address( -1, 1, 0, True ),
                'HumditySensor':Address( -1, 2, 0, True ),
            #    None:Address( 607325, 4, 0, True ),
            #    None:Address( 607325, 5, 0, True ),
                'pH_Reactor1':Address( 611075, 0, 0, False ),
                'pH_Reactor2':Address( 611075, 0, 1, False ),
                'pH_Reactor3':Address( 611075, 0, 2, False ),
                'pH_Reactor4':Address( 611075, 0, 3, False ),
                'K-Type_Incubator':Address( 611075, 1, 0, False ),
                'K-Type_Reactor2':Address( 611075, 1, 1, False ),
                'K-Type_Reactor3':Address( 611075, 1, 2, False ),
                'K-Type_Reactor4':Address( 611075, 1, 3, False ),
                'SMC_Valve_?1':Address( 611075, 2, 0, False ),
                'SMC_Valve_?2':Address( 611075, 2, 1, False ),
                'SMC_Valve_?3':Address( 611075, 2, 2, False ),
                'SMC_Valve_?4':Address( 611075, 2, 3, False ),
            }
            
            return addressMap

try:
    ch = [VoltageInput() for i in range (0, NUM_CHANNELS)]
        
except RuntimeError as e:
    print("Runtime Exception %s" % e.details)
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    exit(1)

def VoltageInputAttached(self,sensorType):
    try:
        attached = self
        print("\nAttach Event Detected Channel %d" % ch[i].channelIndex)
        attached.setSensorType(VoltageSensorType.SENSOR_TYPE_1142)

    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        exit(1)
    
def VoltageInputDetached(self):
    detached = self
    try:
        print("\nDetach Event Detected Channel %d" % ch[i].channelIndex)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        exit(1)

def tryToPrint():
    #Check if all channels have gathered new data yet
    for i in range (0, NUM_CHANNELS):
        if (not ch[i].isReady):
            return

    #If all channels have new data, print the values on-screen
    print("Values:")
    for i in range (0, NUM_CHANNELS):
        ch[i].isReady = 0
        if (i % 8 == 0):
            sys.stdout.write("\n")
        if (ch[i].value != INVALID_VALUE):
            sys.stdout.write("%7s" % (str(ch[i].value)) + " |")
        else:
            sys.stdout.write("  SAT   |")
    
    sys.stdout.write("\n\n")
    sys.stdout.flush()
        
def ErrorEvent(self, eCode, description):
    #indicate the latest measurement is not in range
    if (eCode == ErrorEventCode.EEPHIDGET_SATURATION 
        or eCode == ErrorEventCode.EEPHIDGET_OUTOFRANGE):
        self.value = INVALID_VALUE
        self.isReady = 1

        tryToPrint();

    else:
        print("Error: %s (%d)\n", description, eCode);

def SensorChangeHandler(self, sensorValue, sensorUnit):
    self.value = sensorValue
    self.isReady = True

    tryToPrint()

try:
    for i in range (0, NUM_CHANNELS):
        ch[i].setOnAttachHandler(VoltageInputAttached)
        ch[i].setOnDetachHandler(VoltageInputDetached)
        ch[i].setOnErrorHandler(ErrorEvent)
        
        #Set the properties used to address the channel from the values in the 
        #addressMap table
        ch[i].setDeviceSerialNumber(addressMap[i].serialNumber)
        ch[i].setHubPort(addressMap[i].hubPort)
        ch[i].setChannel(addressMap[i].channel)
        ch[i].setIsHubPortDevice(addressMap[i].isHubPort)
        
        ch[i].setOnSensorChangeHandler(SensorChangeHandler)

        #In Python it is possible to add attributes to instances
        #of a class to keep additional information with the channel
        ch[i].channelIndex = i
        ch[i].isReady = False

        print("Waiting for the Phidget VoltageInput Object %d to be attached..."  % ch[i].channelIndex)
        ch[i].openWaitForAttachment(5000)
        
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    exit(1)

print("Gathering data for 10 seconds...")
time.sleep(10)

try:
    for i in range (0, NUM_CHANNELS):
        ch[i].close()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    exit(1) 
print("Closed VoltageInput devices")
exit(0)
