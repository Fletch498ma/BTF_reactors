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

#local imports
from analysis import *
from viciValve import ViciValve
from dataservice import SensorReader

#phidgets import
from Phidget22.Devices.HumiditySensor import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.TemperatureSensor import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.ErrorCode import *
from Phidget22.Phidget import *

class PhidgetSensorReader(SensorReader):
    def __init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SensorReader.__init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.serialNumber = commConfig.serialNumber
        self.hubPort = commConfig.hubPort
        self.channel = commConfig.channel
        self.isHubPort = commConfig.isHubPort
        self.sensorType = commConfig.sensorType
        self.eol = "\n"
        self.delimiterPattern = "\\S+"
        self.delimiter = " "
    
    def setSensor(self):
        try:
            self.device.setSensorType(self.sensorType)
        except AttributeError:
            #self.device.setThermocoupleType(self.sensorType)
            pass
        
    def initSensor(self,device,attach,detach):
        self.device = device
        self.device.setOnAttachHandler(attach)
        self.device.setOnDetachHandler(detach)
        self.device.setDeviceSerialNumber(self.serialNumber)
        if self.isHubPort:
            self.device.setIsHubPortDevice(True)
        self.device.setHubPort(self.hubPort)
        self.device.setChannel(self.channel)
        self.device.openWaitForAttachment(5000)
        if self.sensorType:
            self.setSensor()
        print(f"\nPhidget Device {device.getDeviceName()} {device.getDeviceID()} is open\n")
        return(self.device)
    
    def stopSensor(self):
        pass
    def getReadings(self,getValue):
        readings = []
        now=datetime.now()
        ts = str((int(time())/self.rateSec)*self.rateSec)
        day = now.strftime("%d/%m/%Y")
        t = now.strftime("%H:%M:%S")
        while len(readings) < self.avg:
            value = getValue()
            read = [ts,day,t,value]
            readings.append(read)
            sleep(1)
        readings = [x for x in readings if x != None]
        return readings
    
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(rowType)]
#        readingsTyped=[]
#        for r in readings:
#            try:
#                typed=[t(c) for t,c in zip(list(zip(*rowType))[1],r)]
#                readingsTyped.append(typed)
#            except ValueError:
#                print("Conversion error in line:",repr(r))
#            readings = readingsTyped
#            
        if not readings: 
            return None
        else:
            strings = readings[0] #readings[0] = time stamp from getReadings()
            avg = list(pandas.DataFrame(readings,columns=list(zip(*self.rowType))[0]).mean()) #unzip first position in rowType which is variable title (for example 'CH4' or 'CO2') and use as header in dataframe. Dump readings tuple into column of data frame and average whole column 
            output = []
            numCol = 0
            for col in range(0,len(strings)):
                if type(strings[col]) == str:
                    output.append(strings[col])
                else:
                    output.append(avg[numCol])
                    numCol = numCol + 1
            
            return output

    def toRow(self, reading):
        pass
    
    def resetSensor(self):
        print("Reseting Sensor: " + self.sensorName)
        return readlineR(self.serialP,self.eol)
    
class PhidgetThermocouple(PhidgetSensorReader):
    def __init__(self,commConfig,sensorName,TempCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        PhidgetSensorReader.__init__(self,commConfig,sensorName,TempCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.TempCache = TempCache
    
    #sensor handler methods
    def onThermocouple_TemperatureChange(self, Temp):
        print("Temperature: " + str(Temp))

    def onThermocouple_Attach(self):
        print("Thermocouple Sensor Attached!")

    def onThermocouple_Detach(self):
        print("Thermocouple Sensor Detached!")

    def initSensor(self):
        self.TemperatureSensor0 = TemperatureSensor()
        self.openDevice = PhidgetSensorReader.initSensor(self,self.TemperatureSensor0,PhidgetThermocouple.onThermocouple_Attach,PhidgetThermocouple.onThermocouple_Detach)
        
    def stopSensor(self):
        self.TemperatureSensor0.close()
    
    def standOutput(self):
        self.TemperatureSensor0.setOnTemperatureChangeHandler(onThermocouple_TemperatureChange)
        
    def getReadings(self):
        readings = PhidgetSensorReader.getReadings(self,self.openDevice.getTemperature)
        return readings
    
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)] #check 
        if not readings: 
            return None
        else:
            strings = readings[0] #readings[0] = time stamp from getReadings()
            avg1 = list(pandas.DataFrame(readings,columns=list(zip(*self.rowType))[0]).mean()) #unzip first position in rowType which is variable title (for example 'CH4' or 'CO2') and use as header in dataframe. Dump readings tuple into column of data frame and average whole column 
            avg = [round(num,4) for num in avg1]
            output = []
            numCol = 0
            for col in range(0,len(strings)):
                if type(strings[col]) == str:
                    output.append(strings[col])
                else:
                    output.append(avg[numCol])
                    numCol = numCol + 1
            print(f"Thermocouple reading: {output}")
            self.TempCache = self.TempCache.append(pandas.Series(output,index=self.TempCache.columns),ignore_index=True)
            return output, self.TempCache
        
    def toRow(self, reading):
#        gets = [0,1,2,3]
#        
#        row = SerialSensorReader.toRow(self,reading)
#        print("toRow:",len(row),":",repr(row))
#        if len(row) != 4:
#            return None
#        row = [row[i] for i in gets]    
#        print("aftercut:",len(row),":",row)
        return reading
    
    def analyseData(self):
        col = np.array(['Temperature (C)'])
        data = np.array([Analysis(self.DataCache,col[i]).basicStats() for i in range(0,len(col))])
        cache = np.array([self.DataCache.TimeIndex.iloc[0],self.DataCache.Date.iloc[0],self.DataCache.Time.iloc[0],data[0,0],data[0,1]])
        return cache
    
    def resetSensor(self):
        pass

class PhidgetpHSensor_1130(PhidgetSensorReader):
    def __init__(self,commConfig,sensorName,pHCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        PhidgetSensorReader.__init__(self,commConfig,sensorName,pHCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.pHCache = pHCache
    
    #sensor handler methods
    def onpHSensor_SensorChange(self, pH):
        print("pH: " + str(pH))

    def onpHSensor_Attach(self):
        print("pH Sensor Attached!")

    def onpHSensor_Detach(self):
        print("pH Sensor Detached!")

    def initSensor(self):
        self.VoltageInput0 = VoltageInput()
        self.openDevice = PhidgetSensorReader.initSensor(self,self.VoltageInput0,PhidgetpHSensor_1130.onpHSensor_Attach,PhidgetpHSensor_1130.onpHSensor_Detach)
        
    def stopSensor(self):
        self.VoltageInput0.close()
    
    def standOutput(self):
        self.VoltageInput0.setOnSensorChangeHandler(onpHSensor_SensorChange)
        
    def getReadings(self):
        readings = PhidgetSensorReader.getReadings(self,self.openDevice.getVoltage)
        return readings
    
    def processData(self,value):
        pH = 7 - ((2.5 - value)/(0.257179+(0.000941468*45)))
        return pH
    
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)] #check 
        if not readings: 
            return None
        else:
            strings = readings[0] #readings[0] = time stamp from getReadings()
            avg1 = list(pandas.DataFrame(readings,columns=list(zip(*self.rowType))[0]).mean()) #unzip first position in rowType which is variable title (for example 'CH4' or 'CO2') and use as header in dataframe. Dump readings tuple into column of data frame and average whole column 
            avg = [round(num,4) for num in avg1]
            output = []
            numCol = 0
            for col in range(0,len(strings)):
                if type(strings[col]) == str:
                    output.append(strings[col])
                else:
                    output.append(avg[numCol])
                    numCol = numCol + 1
            
            output[3] = self.processData(output[3])
            print(f"pH reading: {output}")
            self.pHCache = self.pHCache.append(pandas.Series(output,index=self.pHCache.columns),ignore_index=True)
            return output, self.pHCache
        
    def toRow(self, reading):
#        gets = [0,1,2,3]
#        
#        row = SerialSensorReader.toRow(self,reading)
#        print("toRow:",len(row),":",repr(row))
#        if len(row) != 4:
#            return None
#        row = [row[i] for i in gets]    
#        print("aftercut:",len(row),":",row)
        return reading
    
    def analyseData(self):
        col = np.array(['pH'])
        data = np.array([Analysis(self.DataCache,col[i]).basicStats() for i in range(0,len(col))])
        cache = np.array([self.DataCache.TimeIndex.iloc[0],self.DataCache.Date.iloc[0],self.DataCache.Time.iloc[0],data[0,0],data[0,1]])
        return cache
    
    def resetSensor(self):
        pass

class PhidgetPressureSensor_1136(PhidgetSensorReader):
    def __init__(self,commConfig,sensorName,PresCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        PhidgetSensorReader.__init__(self,commConfig,sensorName,PresCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.PresCache = PresCache
    
    #sensor handler methods
    def onPressureSensor_SensorChange(self, pressure):
        print("Pressure: " + str(pressure))

    def onPressureSensor_Attach(self):
        print("Pressure Sensor Attached!")

    def onPressureSensor_Detach(self):
        print("Pressure Sensor Detached!")

    def initSensor(self):
        self.VoltageRatioInput0 = VoltageRatioInput()
        self.openDevice = PhidgetSensorReader.initSensor(self,self.VoltageRatioInput0,PhidgetPressureSensor_1136.onPressureSensor_Attach,PhidgetPressureSensor_1136.onPressureSensor_Detach)
        
    def stopSensor(self):
        self.VoltageRatioInput0.close()
    
    def standOutput(self):
        self.VoltageRatioInput0.setOnSensorChangeHandler(onPressureSensor_SensorChange)
        
    def getReadings(self):
        readings = PhidgetSensorReader.getReadings(self,self.openDevice.getSensorValue)
        return readings
    
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)] #check 
        if not readings: 
            return None
        else:
            strings = readings[0] #readings[0] = time stamp from getReadings()
            avg1 = list(pandas.DataFrame(readings,columns=list(zip(*self.rowType))[0]).mean()) #unzip first position in rowType which is variable title (for example 'CH4' or 'CO2') and use as header in dataframe. Dump readings tuple into column of data frame and average whole column 
            avg = [round(num,4) for num in avg1]
            output = []
            numCol = 0
            for col in range(0,len(strings)):
                if type(strings[col]) == str:
                    output.append(strings[col])
                else:
                    output.append(avg[numCol])
                    numCol = numCol + 1
            print(f"Pressure reading: {output}")
            self.PresCache = self.PresCache.append(pandas.Series(output,index=self.PresCache.columns),ignore_index=True)
            return output, self.PresCache
        
    def toRow(self, reading):
#        gets = [0,1,2,3]
#        
#        row = SerialSensorReader.toRow(self,reading)
#        print("toRow:",len(row),":",repr(row))
#        if len(row) != 4:
#            return None
#        row = [row[i] for i in gets]    
#        print("aftercut:",len(row),":",row)
        return reading
    
    def analyseData(self):
        col = np.array(['Differential Pressure(kPa)'])
        data = np.array([Analysis(self.DataCache,col[i]).basicStats() for i in range(0,len(col))])
        cache = np.array([self.DataCache.TimeIndex.iloc[0],self.DataCache.Date.iloc[0],self.DataCache.Time.iloc[0],data[0,0],data[0,1]])
        return cache
    
    def resetSensor(self):
        pass

    
class PhidgetHumiditySensor(PhidgetSensorReader):
    def __init__(self,commConfig,sensorName,Humcache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        PhidgetSensorReader.__init__(self,commConfig,sensorName,Humcache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.Humcache = Humcache
        
    #sensor handler methods
    def onHumiditySensor_HumidityChange(self, humidity):
        print("Humidity: " + str(humidity))

    def onHumiditySensor_Attach(self):
        print("Humidity Sensor Attached!")

    def onHumiditySensor_Detach(self):
        print("Humidity Sensor Detached!")

    def initSensor(self):
        self.humiditySensor = HumiditySensor()
        self.openDevice = PhidgetSensorReader.initSensor(self,self.humiditySensor,PhidgetHumiditySensor.onHumiditySensor_Attach,PhidgetHumiditySensor.onHumiditySensor_Detach)
    
    def stopSensor(self):
        self.humiditySensor.close()
    
    def standOutput(self):
        self.humiditySensor.setOnHumidityChangeHandler(onHumiditySensor_HumidityChange)
        
    def getReadings(self):
        readings = PhidgetSensorReader.getReadings(self,self.openDevice.getHumidity)
        return readings
    
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)] #check 
        if not readings: 
            return None
        else:
            strings = readings[0] #readings[0] = time stamp from getReadings()
            avg1 = list(pandas.DataFrame(readings,columns=list(zip(*self.rowType))[0]).mean()) #unzip first position in rowType which is variable title (for example 'CH4' or 'CO2') and use as header in dataframe. Dump readings tuple into column of data frame and average whole column 
            avg = [round(num,2) for num in avg1]
            output = []
            numCol = 0
            for col in range(0,len(strings)):
                if type(strings[col]) == str:
                    output.append(strings[col])
                else:
                    output.append(avg[numCol])
                    numCol = numCol + 1
            print(f"Humidity reading: {output}")
            self.Humcache = self.Humcache.append(pandas.Series(output,index=self.Humcache.columns),ignore_index=True)
            return output, self.Humcache
        
    def toRow(self, reading):
#        gets = [0,1,2,3]
#        
#        row = SerialSensorReader.toRow(self,reading)
#        print("toRow:",len(row),":",repr(row))
#        if len(row) != 4:
#            return None
#        row = [row[i] for i in gets]    
#        print("aftercut:",len(row),":",row)
        return reading
    
    def analyseData(self):
        col = np.array(['RelativeHumidity(%)'])
        data = np.array([Analysis(self.DataCache,col[i]).basicStats() for i in range(0,len(col))])
        cache = np.array([self.DataCache.TimeIndex.iloc[0],self.DataCache.Date.iloc[0],self.DataCache.Time.iloc[0],data[0,0],data[0,1]])
        return cache
    
    def resetSensor(self):
        pass



if __name__ == "__main__":
    try:
        db = sq.create_engine('sqlite:///:memory:', echo=True)
        sr = IRSensorReader({'port':'/dev/ttyUSB1','timeout':61},"Test1",(),1,db,stdout)
        sr.startCollection()
        sleep(100)
        sr.stop()
    except KeyboardInterrupt:
        print("Exiting")
    sr.stop()

#todo
#add database query
#fix it so that avgRow only deals with one averaged collection of readings per time interval
#getReadings returns all readings with a timestamp for each?
#then we only return the readings for one time interval?
#todo create metadatatable with sensor id, type, and name.
