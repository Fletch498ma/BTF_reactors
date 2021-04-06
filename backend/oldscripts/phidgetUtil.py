#system imports
import sys
import datetime
import traceback
import math
import csv
import time

#phidget imports
from Phidget22.Phidget import
from Phidget22.PhidgetException import *
from Phidget22.Devices.Log import *
from Phidget22.LogLevel import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.Devices.VoltageRatioInput import * 
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.VoltageOutput import *

#phidget sensor imports
from Phidget22.Devices.HumiditySensor import *
from Phidget22.Devices.TemperatureSensor import *


class Address(object):
    """Class used to identify connected phidget devices."""
    
    def __init__(self, serialNumber, hubPort, channel, isHubPort, signalType):
        self.serialNumber = serialNumber
        self.hubPort = hubPort
        self.channel = channel
        self.isHubPort = isHubPort
        self.signalType = signalType
      

class PhidgetProtocol(object):
    """Class for identifying phidgets and attachment 
    """
    def __init__(self,device,manual=None):
        #TODO: have a manual addressing option if used for on-off experiments not on rig 
        if manual:
            print('TODO!')
        else:
            self.device = mapDevices(device)

    #Here we've created an array to map which sensors correspond to a custom index so we can more easily keep track of which sensor is which
    #TODO all serialNumbers, hubPorts, channels, etc should be stored in config files like serial port names fand accessed using configparser
    def mapDevices(device):
        addressMap = {
            'SMC_Valve_ToGasSensors':Address( 607325, 0, 0, False,'DigitalOutput'),
            'SMC_Valve_Port1Manifold':Address( 607325, 0, 1, False,'DigitalOutput'),
            'SMC_Valve_ToGasSensors':Address( 607325, 0, 2, False,'DigitalOutput'),
            'SMC_Valve_Port3Manifold':Address( 607325, 0, 3, False,'DigitalOutput'),
            'SMC_Valve_Port4Manifold':Address( 607325, 0, 4, False,'DigitalOutput'),
            'SMC_Valve_Port5Manifold':Address( 607325, 0, 5, False,'DigitalOutput'),
            'SMC_Valve_Port6Manifold':Address( 607325, 0, 6, False,'DigitalOutput'),
            'SMC_Valve_Port2Manifold':Address( 607325, 0, 7, False,'DigitalOutput'),
        #    None:Address( 607325, 0, 8, False ),
        #    None:Address( 607325, 0, 9, False ),
        #    None:Address( 607325, 0, 10, False ),
        #    None:Address( 607325, 0, 11, False ),
        #    None:Address( 607325, 0, 12, False ),
        #    None:Address( 607325, 0, 13, False ),
        #    None:Address( 607325, 0, 14, False ),
        #    None:Address( 607325, 0, 15, False ),
            'DifPressureSensor_Max2kPa':Address( 607325, 1, 0, True,'VoltageRatioInput'),
            'HumditySensor':Address( 607325 , 2, 0, True,'VINT'),
        #    None:Address( 607325, 4, 0, True ),
        #    None:Address( 607325, 5, 0, True ),
            'pH_Reactor1':Address( 611075, 0, 0, False,'VoltageInput'),
            'pH_Reactor2':Address( 611075, 0, 1, False,'VoltageInput'),
            'pH_Reactor3':Address( 611075, 0, 2, False,'VoltageInput'),
            'pH_Reactor4':Address( 611075, 0, 3, False,'VoltageInput'),
            'K-Type_Incubator':Address( 611075, 1, 0, False,'VINT'),
            'K-Type_Reactor2':Address( 611075, 1, 1, False,'VINT'),
            'K-Type_Reactor3':Address( 611075, 1, 2, False,'VINT'),
            'K-Type_Reactor4':Address( 611075, 1, 3, False,'VINT'),
            'SMC_Valve_?1':Address( 611075, 2, 0, False,'DigitalOutput'),
            'SMC_Valve_?2':Address( 611075, 2, 1, False,'DigitalOutput'),
            'SMC_Valve_?3':Address( 611075, 2, 2, False,'DigitalOutput'),
            'SMC_Valve_?4':Address( 611075, 2, 3, False,'DigitalOutput'),
        }
        
        #TODO: not sure if I should make this try:except and raise exception if device not found in addressmap
        if addressMap[device]:
            return addressMap[device]
        else:
            print('no device found in map directory') #ask for input of addressing properties or raise exception
        
    #find the sensor / device type an
    def discover(self):
        pass
    
    
class Events(DeviceClass):
    """Empty event class that inherits from DeviceClass which will be a identified device type from methods in PhidgetsProtocol
    """
    
    def __init__(self,deviceType,address):
        DeviceClass.__init__(self,deviceType,address)
                             
    def attach(self):
        pass

    def detach(self):
        pass
    
    def error(self):
        pass
    
    def _open(self):
        pass
    
    def _close(self):
        pass
    
    def getReading(self):
        pass
    
    def valueChange(self):
        pass
    

class _HumditySensor(object):
    """Humdity sensor class """
    
    def __init__(self,deviceType,address):
        self.deviceType = deviceType
        self.address = address
        self.manual = manual

    #Handlers for various events: attach, detach, etc...
    def onHumiditySensor_HumidityChange(self, humidity):
        print("Humidity: " + str(humidity))

    def onHumiditySensor_Attach(self):
        print("Attach!")

    def onHumiditySensor_Detach(self):
        print("Detach!")
    
    #events to override Event class 
    def attach(self):
        pass
    
    def detach(self):
        pass
    
    def _open(self):
        pass
    
    def _close(self):
        pass
    
    def getReading(self):
        pass
    
    def valueChange(self,initDevice):
        initDevice.setOnHumidityChangeHandler(onHumiditySensor_HumidityChange)
        
        if self.manual:
            try:
                input("Press Enter to Stop\n")
            except (Exception, KeyboardInterrupt):
                pass
        else:
            print('TODO: create another option which logs data from Phidget handler methods')
    
        #Create your Phidget channels
        humiditySensor0 = HumiditySensor()

        #Set addressing parameters to specify which channel to open (if any)

        #Assign any event handlers you need before calling open so that no events are missed.
        humiditySensor0.setOnHumidityChangeHandler(onHumiditySensor0_HumidityChange)
        humiditySensor0.setOnAttachHandler(onHumiditySensor0_Attach)
        humiditySensor0.setOnDetachHandler(onHumiditySensor0_Detach)

        #Open your Phidgets and wait for attachment
        humiditySensor0.openWaitForAttachment(5000)

        #Do stuff with your Phidgets here or in your event handlers.

        

        #Close your Phidgets once the program is done.
        humiditySensor0.close()

    main()
  
