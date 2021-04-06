# This code relies on the module 'threading' to concurrently take measurements from the various sensors 
from threading import Thread 
from os import path
from time import asctime,localtime,sleep,time,mktime,strptime,strftime
from datetime import datetime
from uuid import uuid4
from sys import stdout
import sqlalchemy as sq
import sqlite3
import re
import csv
import pandas
import numpy as np

#phidgets import
from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *
from Phidget22.ErrorCode import *
from Phidget22.Phidget import *


class PhidgetControl(Thread):
    """overriding the threading sub class __init__"""
    def __init__(self,commConfig,sensorName,threadName,eventType,eventList,event):
        self.commConfig = commConfig
        self.threadName = threadName
        self.eventType = eventType
        
        if self.eventType in eventList:
            self.target = eventList[self.eventType][0]
            self.args = eventList[self.eventType][1]
            self.kwargs = eventList[self.eventType][2]
            targetDaemon = eventList[self.eventType][3]
        else: #custom event
            self.target = eventType[0]
            self.args = eventType[1]
            self.kwargs = eventType[2]
            targetDaemon = eventType[3]
            
        Thread.__init__(self,name=threadName,daemon=targetDaemon)
        self.setName(sensorName)
        self.serialNumber = commConfig.serialNumber
        self.hubPort = commConfig.hubPort
        self.channel = commConfig.channel
        self.isHubPort = commConfig.isHubPort 
        self.sensorName = sensorName
        self.end = False

    """overriding the threading sub class run()"""
    def run(self):
        try:
            if self.target:
                self.target(*self.args, **self.kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self.target, self.args, self.kwargs
    
    """Initialized the sensor using initSensor and starts the data collection loop."""
    def startThread(self):
        self.end = False
        self.start()
    
    """ Closes all handles and synchronizes the collection end"""
    def stopThread(self):
        self.join()
        self.disconnect()
        
    """Called by startCollection to initialize the sensor and communcations."""
    def initDevice(self,device,attach,detach):
        self.device = device
        try: 
            self.device.setOnAttachHandler(attach)
            self.device.setOnDetachHandler(detach)
            self.device.setDeviceSerialNumber(self.serialNumber)
            if self.isHubPort:
                self.device.setIsHubPortDevice(True)
            self.device.setHubPort(self.hubPort)
        except PhidgetException as error:
            print("Phidget Exception %i: %s" % (error.code, error.details))
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            exit(1)
        return self.device
    
    def connect(self,channel):
        try:
            self.device.setChannel(channel)
            self.device.openWaitForAttachment(5000)
            print(f"\nPhidget Device {self.device.getDeviceName()} is open\n")
        except PhidgetException as error:
            print("Phidget Exception %i: %s" % (error.code, error.details))
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            exit(1)
    
    # TODO: detach handler doesn't fire always...I'm not sure why????
    """Called by stopThread after collection has ended."""
    def disconnect(self):
        try:
            self.device.close()
        except PhidgetException as error:
            print("Phidget Exception %i: %s" % (error.code, error.details))
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            exit(1)
            
    def resetDevice(self):
        return None
    

class PhidgetSolidStateRelay_REL1101(PhidgetControl):
    def __init__(self,commConfig,sensorName,threadName,eventType,event):
        
        e = event
        eventList = {'open':[PhidgetSolidStateRelay_REL1101._openValve,(self,e,),{},False],
                     'close':[PhidgetSolidStateRelay_REL1101._closeValve,(self,e,),{},False],
                     'openUntil':[PhidgetSolidStateRelay_REL1101._openUntil,(self,e,),{},False],
                     'waitToOpen':[PhidgetSolidStateRelay_REL1101._waitToOpen,(self,e,),{},False]
                     }
        
        PhidgetControl.__init__(self,commConfig,sensorName,threadName,eventType,eventList,event)
        self.state = False
    
    """sensor events"""
    def _openValve(self,e):
        self._setState(True)
        print('valve open')
    
    def _closeValve(self,e):
        self._setState(False)
        print('valve closed')
    
    def _openUntil(self,e):
        pass
    
    def _waitToOpen(self,e):
        pass
    
    """sensor handlers"""
    def onSSR_Attach(self):
        print("16x Solid State Relay Attached!")

    def onSSR_Detach(self):
        print("16x Solid State Relay Detached!")

    def initDevice(self):
        digitalOutput0 = DigitalOutput()
        PhidgetControl.initDevice(self,digitalOutput0,PhidgetSolidStateRelay_REL1101.onSSR_Attach,PhidgetSolidStateRelay_REL1101.onSSR_Detach)
    
    def connect(self,channel):
        PhidgetControl.connect(self,channel)
    
    """utility functions for SMC valves"""
    def _setState(self,state):
        self.state = state
        self.device.setState(self.state)
    
    def _getState(self):
        current_state = self.device.getState()
        
        if not current_state == self.state:
            self._setState(self.state)
            
        if self.state:
            state = 'open'
        else:
            state = 'closed'
        print("Valve State:" + str(state))
    
    def resetDevice(self):
        pass