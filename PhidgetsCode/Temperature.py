import sys
import datetime
import traceback
import math
import csv
import datetime

from Phidget22.Devices.TemperatureSensor import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *

#counter variable
attachcount = 0

def onTemperatureAttachHandler(self):
    global attachcount
    ph = self
    port = ph.getHubPort()
    if (port == 0):
        ph.setDataInterval(100) #10 samples/s
        ph.setTemperatureChangeTrigger(0) #report every sample regardless of if there's a change or not
        ph.setThermocoupleType(ThermocoupleType.THERMOCOUPLE_TYPE_K)
    if(port ==1):
        ph.setDataInterval(500) #2 samples/s
        ph.setTemperatureChangeTrigger(0) #report every sample regardless of if there's a change or not
    
    attachcount+=1
    
def onVoltageAttachHandler(self):
    global attachcount
    ph = self
	
    ph.setDataInterval(100) #10 samples/s
    ph.setVoltageChangeTrigger(0) #report every sample regardless of if there's a change or not
    
    attachcount+=1


def onDetachHandler(self):
    global attachcount
    attachcount-=1

def onErrorHandler(self, errorCode, errorString):

    sys.stderr.write("[Phidget Error Event] -> " + errorString + " (" + str(errorCode) + ")\n")

def onTemperatureChangeHandler(self, temperature):
    if(attachcount!=3): #let's only start logging once all 3 devices are attached.  for no particular reason, just because
        return
    sys.stdout.write(".") #provide some feedback that samples are being recorded
    sys.stdout.flush()
    port = self.getHubPort()
    
    #check which of our 2 temperature sensors has had a data event
    if(port == 0): #thermocouple
        self.log.writerow(['Thermocouple',str(temperature),str(self.sampleCount),datetime.datetime.now().isoformat()])
        self.sampleCount+=1
    if(port == 1):#ambient
        self.log.writerow(['Ambient',str(temperature),str(self.sampleCount),datetime.datetime.now().isoformat()])
        self.sampleCount+=1
        

def onVoltageChangeHandler(self, voltage):
    if(attachcount!=3): #let's only start logging once all 3 devices are attached (for no particular reason, just because)
        return
    sys.stdout.write(".") #provide some feedback that samples are being recorded
    sys.stdout.flush()
    #we are only using a single voltage input so we won't need to check which device fired this evernt, it can only be the one
    luminosity = math.exp(0.02448*(voltage*200)-0.8263) #calculate lux value from voltage output according to equation from 1143 user guide
    self.log.writerow(['Light',str(luminosity),str(self.sampleCount),datetime.datetime.now().isoformat()])
    self.sampleCount+=1


def main():
    try:
        try: #out three devices
            thermocouple = TemperatureSensor()
            ambient = TemperatureSensor()
            analogLight = VoltageInput()
        except PhidgetException as e:
            sys.stderr.write("Runtime Error -> Creating Devices: \n\t")
            sys.stderr.write("Desc: " + e.details + "\n")
        
        
        #file we want to log to
        file = open("phidgetLog.csv", "w", newline='')
        filewriter = csv.writer(file, delimiter=',')
        #add header to file
        filewriter.writerow(["Device","Value","Sample Number","Time Stamp"])
        #set this file as the file to log to for all devices
        thermocouple.log = filewriter
        ambient.log = filewriter
        analogLight.log = filewriter
        #add counters to each device
        thermocouple.sampleCount = 0
        ambient.sampleCount = 0
        analogLight.sampleCount = 0
        
        #register handlers for each device
        thermocouple.setOnAttachHandler(onTemperatureAttachHandler)
        thermocouple.setOnDetachHandler(onDetachHandler)
        thermocouple.setOnErrorHandler(onErrorHandler)
        thermocouple.setOnTemperatureChangeHandler(onTemperatureChangeHandler)
        
        ambient.setOnAttachHandler(onTemperatureAttachHandler)
        ambient.setOnDetachHandler(onDetachHandler)
        ambient.setOnErrorHandler(onErrorHandler)
        ambient.setOnTemperatureChangeHandler(onTemperatureChangeHandler)
                
        analogLight.setOnAttachHandler(onVoltageAttachHandler)
        analogLight.setOnDetachHandler(onDetachHandler)
        analogLight.setOnErrorHandler(onErrorHandler)
        analogLight.setOnVoltageChangeHandler(onVoltageChangeHandler)
        
        #set parameters for each device so the open call knows where to looks
        #****note that the serial number used here is for the VINT hub used in our testing.  yours will be different so you should change this.
        thermocouple.setDeviceSerialNumber(371089)
        ambient.setDeviceSerialNumber(371089)
        analogLight.setDeviceSerialNumber(371089)
        
        thermocouple.setHubPort(0)
        ambient.setHubPort(1)
        analogLight.setHubPort(2)
        
        analogLight.setIsHubPortDevice(1)

        #open each device
        try:
            thermocouple.openWaitForAttachment(5000)
            ambient.openWaitForAttachment(5000)
            analogLight.openWaitForAttachment(5000)
        except PhidgetException as e:
            sys.stderr.write("Runtime Error -> Opening Devices: \n\t")
            sys.stderr.write("Desc: " + e.details + "\n")
        
        #wait for data to come in or user to terminate
        input("Press ENTER to end program.\n")
        
        #ensure everything gets written out
        file.flush()
        
        #unregister handlers
        thermocouple.setOnTemperatureChangeHandler(None)
        ambient.setOnTemperatureChangeHandler(None)
        analogLight.setOnVoltageChangeHandler(None)

        #deallocate memory
        thermocouple.close()
        ambient.close()
        analogLight.close()
        return 0

    except PhidgetException as e:
        sys.stderr.write("\nExiting with error(s)...")
        return 1
main()

