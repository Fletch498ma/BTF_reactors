# This code relies on the module 'threading' to concurrently take measurements from the various sensors 

from threading import Thread, Event
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
from sys import stdout

#universal library: mcc 
from uldaq import get_daq_device_inventory, DaqDevice, InterfaceType, AOutFlag

#local imports
from analysis import *

#device imports
from alicat import FlowController

#phidgets import
from Phidget22.Devices.HumiditySensor import *
from Phidget22.Phidget import *

def readlineR(ser,delim):
    line = ""
    start = time()
    waiting = True
    while(waiting):
        if ser.in_waiting: 
            c = str(ser.read(1),'utf-8')
            line = line + c
            waiting = not line.endswith(delim)
            start = time()
        else:
            sleep(1.0/ser.baudrate)
            waiting = time()-start < ser.timeout
            if not waiting: line = None
    return line

def clearBuffer(ser):
    start = time()
    waiting = True
    while(waiting):
        if ser.in_waiting>0: 
            waiting = time()-start < ser.timeout
            ser.read(ser.in_waiting)
            sleep(1)
        else:
            waiting = False

#def valvecheck():
#    """Function doc """
#    v = ViciValve()
#    v.connect()
#    v.setup()
#    position = v.interpretPosition()
#    return position

class DeviceController(Thread):
    """serPort is a pyserial serial port object
    rowType is a tuple of columnName,type pairs. Implicitly the first entry is "time",int and so avgRow is required to return a type of (int,) + rowType. Valid types are float,int,str,bytes. For strings using a db without arbitrary length strings use bytes.
    rateSec is the data polling rate the maximum rate that will be returned.
    log is a file handle where data will be logged to.
    db is an sqlalchemy database engine connection. See: http://docs.sqlalchemy.org/en/rel_0_5/sqlexpression.html and http://docs.sqlalchemy.org/en/rel_0_8/core/connections.html
    """
    
    """overriding the threading sub class __init__"""
    def __init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType = (),rateSec=10,avg=10,timer=100,db=None,log=None):
        
        e = event
        events = {'continuous_event':[DeviceController._continuous,(self,e,),{},True],
              'trigger_event':[DeviceController._trigger,(self,e,),{},False],
              'single_event':[DeviceController._single,(self,e,),{},False],
              'wait_event':[DeviceController._wait,(self,e,),{},False],
            }
        
        if eventType in events:
            self.target = events[eventType][0]
            self.args = events[eventType][1]
            self.kwargs = events[eventType][2]
            targetDaemon = events[eventType][3]
        else: #custom event
            self.target = eventType[0]
            self.args = eventType[1]
            self.kwargs = eventType[2]
            targetDaemon = eventType[3]
            
        Thread.__init__(self,name=threadName,daemon=targetDaemon)
        self.setName(sensorName)
        self.commConfig = commConfig 
        self.rateSec = rateSec
        self.avg = avg
        self.db = db
        self.sensorName = sensorName
        self.rowType = (("TimeIndex",float),("Date",str),("Time",str),) + rowType #(("Time",float),) + rowType
        self.log = log#.name
        #log.close()
        self.end = False
        self.timer = timer
        self.DataCache = DataCache
        
    """overriding the threading sub class run()"""
    def run(self):
        try:
            if self.target:
                self.target(*self.args, **self.kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self.target, self.args, self.kwargs
    
    """event which continuously monitors data from reactors, callable by run() when event envoked. No Event flags are used, TODO: maybe make it dameaon thread?"""
    def _continuous(self,e):
        start = time()
        end = start + self.timer
        while(not self.end):
            if localtime().tm_sec%self.rateSec == 0:
                strt = time()
                readings = self.getReadings()
                #rows = [self.toRow(reading) for reading in readings] 
                #ADD typecheck here and reset if there is a problem
                avgRows = self.avgRows(readings)
                now = datetime.now()
                Date = now.strftime("%d/%m/%Y")
                Time = now.strftime("%H:%M:%S")
                timeStamp = [time(),Date,Time]
                logEntry = timeStamp + avgRows[0][3:]
                self.data = logEntry
                #logEntry = ",".join(
                        #["%s"%repr(avgRows)]) + "\n" 
                if self.log:
                    with open(self.log,'a+',newline='') as log:#self.log: #not sure if this will work????
                        writer = csv.writer(log)
                        writer.writerow(logEntry)
                if self.db:
                    indx = 0
                    for row in avgRows:
                        indx +=1
                        dbentry = list(zip(avgRows,list(zip(*self.rowType))[0])) #unzip rowType tuple column header (string) and rezip with values in avgRows
                        self.dbTable.insert().values(dbentry[indx-1])
                wait = self.rateSec - time()%self.rateSec
                sleep(wait)
                #print(f"\ndata pol run time: {time()-strt}\n")
            sleep(.1)
            self.DataCache = avgRows[1]
            #keep track of time 
            if strt >= end :
                self.end = True
    
        #print(self.DataCache)
        print(f"\n=======================\n{self.sensorName}\nRun time: {round(time() - start,0)}sec\nTimer Setpoint: {self.timer}sec\n=======================")
        
    def _trigger(self,e):
        readings = self.getReadings()
        readingsStr = ["%s"%repr(reading) for reading in readings]
        rows = [self.toRow(reading) for reading in readings] 
        #ADD typecheck here and reset if there is a problem
        avgRows = self.avgRows(rows)
        now = datetime.now()
        Date = now.strftime("%d/%m/%Y")
        Time = now.strftime("%H:%M:%S")
        timeStamp = [time(),Date,Time]
        logEntry = timeStamp + avgRows[0][3:]
        #logEntry = ",".join(
                #["%s"%repr(avgRows)]) + "\n" 
        if self.log:
            #print(logEntry)
            with open(self.log,'a+',newline='') as log:#self.log: #not sure if this will work????
                writer = csv.writer(log)
                writer.writerow(logEntry)
            #self.log.write(logEntry)
            #self.log.flush()
        if self.db:
            indx = 0
            for row in avgRows:
                indx +=1
                dbentry = list(zip(avgRows,list(zip(*self.rowType))[0])) #unzip rowType tuple column header (string) and rezip with values in avgRows
                self.dbTable.insert().values(dbentry[indx-1])
        self.DataCache = avgRows[1]
        
        e.set()
        return avgRows[1]
    
    def _single(self,e):
        readings = self.getReadings()
        readingsStr = ["%s"%repr(reading) for reading in readings]
        rows = [self.toRow(reading) for reading in readings] 
        #ADD typecheck here and reset if there is a problem
        avgRows = self.avgRows(rows)
        now = datetime.now()
        Date = now.strftime("%d/%m/%Y")
        Time = now.strftime("%H:%M:%S")
        timeStamp = [time(),Date,Time]
        logEntry = timeStamp + avgRows[0][3:]
        #logEntry = ",".join(
                #["%s"%repr(avgRows)]) + "\n" 
        if self.log:
            #print(logEntry)
            with open(self.log,'a+',newline='') as log:#self.log: #not sure if this will work????
                writer = csv.writer(log)
                writer.writerow(logEntry)
            #self.log.write(logEntry)
            #self.log.flush()
        if self.db:
            indx = 0
            for row in avgRows:
                indx +=1
                dbentry = list(zip(avgRows,list(zip(*self.rowType))[0])) #unzip rowType tuple column header (string) and rezip with values in avgRows
                self.dbTable.insert().values(dbentry[indx-1])
        self.DataCache = avgRows[1]
             
    def _wait(self,e):
        start = time()
        end = start + self.timer
        e.wait()
        while(not self.end):
            if localtime().tm_sec%self.rateSec == 0:
                strt = time()
                readings = self.getReadings()
                #rows = [self.toRow(reading) for reading in readings] 
                #ADD typecheck here and reset if there is a problem
                avgRows = self.avgRows(readings)
                now = datetime.now()
                Date = now.strftime("%d/%m/%Y")
                Time = now.strftime("%H:%M:%S")
                timeStamp = [time(),Date,Time]
                logEntry = timeStamp + avgRows[0][3:]
                self.data = logEntry
                #logEntry = ",".join(
                        #["%s"%repr(avgRows)]) + "\n" 
                if self.log:
                    #print(logEntry)
                    with open(self.log,'a+',newline='') as log:#self.log: #not sure if this will work????
                        writer = csv.writer(log)
                        writer.writerow(logEntry)
                    #self.log.write(logEntry)
                    #self.log.flush()
                if self.db:
                    indx = 0
                    for row in avgRows:
                        indx +=1
                        dbentry = list(zip(avgRows,list(zip(*self.rowType))[0])) #unzip rowType tuple column header (string) and rezip with values in avgRows
                        self.dbTable.insert().values(dbentry[indx-1])
                wait = self.rateSec - time()%self.rateSec
                sleep(wait)
                #print(f"\ndata pol run time: {time()-strt}\n")
            sleep(.1)
            self.DataCache = avgRows[1]
            #keep track of time 
            if strt >= end :
                self.end = True
    
        #print(self.DataCache)
        print(f"\n=======================\n{self.sensorName}\nRun time: {round(time() - start,0)}sec\nTimer Setpoint: {self.timer}sec\n=======================")
    
    def _analogTest(self,e):
        start = time()
        end = start + self.timer
        e.wait()
        
        
    """Initialized the sensor using initSensor and starts the data collection loop."""
    def startCollection(self):
        #self.initDB()
        self.end = False
        self.initSensor()
        self.start()
    
    """ Closes all handles and synchronizes the collection end"""
    def stop(self):
        self.join()
        self.stopSensor()
        outputCache = self.collectData()
        print(self.DataCache)
        return outputCache, self.DataCache
#        if self.log:
#            self.log.flush()
        
    def analyseData(self):
        pass
    
    def collectData(self):
        post = self.analyseData()
        return post
    
    def graphliveData(self,data):
        pass
    
    def toDBType(self,ty):
        if ty == int:
            return sq.Integer
        if ty == float:
            return sq.Float
        if ty == str:
            return sq.String
        if ty == bytes or ty == bytearray:
            return sq.Binary
        raise ValueError("Does not map to a database type.")
    def initDB(self):
        if not self.db: return
        cols = []
        cols.append(sq.Column('time',self.toDBType(int),primary_key = True))
        for name,ty in self.rowType[1:]:
            cols.append(sq.Column(name,self.toDBType(ty)))
        metadata = sq.MetaData(bind=self.db)
        
        self.dbTable = sq.Table(self.sensorName,metadata,*cols)
        self.dbTable.create()
        print(repr(metadata.tables[self.sensorName]))

    """Called by startCollection to initialize the sensor and communcations."""
    def initSensor(self):
        pass
    """Called by stop after collection has ended."""
    def stopSensor(self):
        pass
    """Returns raw readings gather from sensor. Later on will be converted to rows by a call to toRow. Must return a list of readings. This function should be responsible for synchronizing with the sensor. The rate value really just indicates how frequently to call this function and attempt at retriving a value."""
    def getReadings(self):
        return [asctime(localtime())]
    """Must return a tuple following the type of rowType in __init__"""
    def avgRows(self, rows):
        if len(rows) > 0:
            return [rows[0]]
        else:
            return None
    """Takes the raw sensor output and converts it to a row. A collection of these will be sent to avgRows."""
    def toRow(self,reading):
        row = strptime(reading)
        return (int(mktime(row)),)
    def resetSensor(self):
        return None
    
#might want to make this a threadsafe interrupt driven reader
class SerialDeviceController(DeviceController):
    def __init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        DeviceController.__init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.eol = "\n"
        self.delimiterPattern = "\\S+"
        self.delimiter = " "
    def initSensor(self):
        from serial import Serial
        self.serialP = Serial(**self.commConfig)
        if self.serialP.is_open:
            chkport = "true"
        else:
            ckcport = "false"
        print("\nSerial port " +self.commConfig["port"] + " is open: " +chkport+"\n")
        self.resetSensor()
    def stopSensor(self):
        self.serialP.close()
    def getReadings(self):
        readlineR(self.serialP,self.eol)#manually clearing buffer, probably should use method
        readings = []
        now=datetime.now()
        ts = str((int(time())/self.rateSec)*self.rateSec)
        day = now.strftime("%d/%m/%Y")
        t = now.strftime("%H:%M:%S")
        while len(readings) < self.avg:
            line = readlineR(self.serialP,self.eol)
            line = line.lstrip('[')
            line = line.rstrip(']\n\r')
            readings.append(self.delimiter.join([ts,day,t,line]))
            sleep(1)
        readings = [x for x in readings if x != None]
        return readings

    def avgRows(self, readings):
        pass
    
    def toRow(self, reading):
        # code used to parase the raw sensor output, isolating parameter strings without having to index string characters directly!!!!!!
        # \\S+ means all non white space characters. This includes words and punctuation. Note: re module can analyze byte strings b''. 
        # re.findall will find all the non-white space characters in the string and dump each found character group into a list element = row
        # .strip() just removes leading and tailing white spaces and carriage returns, in the case of gas sensors it removes leading \r and tailing = \n
        row = re.findall(self.delimiterPattern,reading.strip())
        row = [x.strip() for x in row]
        return row
    def resetSensor(self):
        print("Reseting Sensor: " + self.sensorName)
        return readlineR(self.serialP,self.eol)

class Alicat(SerialDeviceController):
    #TODO: add address, control_point to commConfig 
    def __init__(self,commConfig,sensorName,AlicatCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SerialDeviceController.__init__(self,commConfig,sensorName,AlicatCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.port = self.commConfig['port']
        self.address = self.commConfig['address']
        self.point = self.commConfig['control_point']
        self.gas = self.commConfig['gas']
        self.mass_flow = 0
        self.AlicatCache = AlicatCache
        
    def initSensor(self):
        self.flowcontroller = FlowController(port=self.port,address=self.address)
        print("\nSerial port " +self.port + " is open: true\n")
        self.resetSensor()
        self.setParameter(gas=self.gas,mass_flow=self.mass_flow)
        #self.flowcontroller.set_control_point(self.point)
        
    def stopSensor(self):
        self.resetSensor()
        self.flowcontroller.close()
    
    def setParameter(self,gas='Air',mass_flow=0.0,pressure=14.79,volumetric_flow=0.0):
        self.flowcontroller.set_gas(gas)
        try:
            point = self.flowcontroller._get_control_point()
            if point == 'flow':
                self.flowcontroller.set_flow_rate(mass_flow)
            else:
                self.flowcontroller.set_pressure(pressure)
        except ValueError:
            self.flowcontroller.set_flow_rate(mass_flow)
            #self.flowcontroller.set_pressure(pressure)
            
    def getReadings(self):
        readings = []
        now=datetime.now()
        ts = str((int(time())/self.rateSec)*self.rateSec)
        day = now.strftime("%d/%m/%Y")
        t = now.strftime("%H:%M:%S")
        while len(readings) < self.avg:
            line = self.flowcontroller.get()
            line = [line['gas'],line['setpoint'],line['mass_flow'],line['pressure'],line['temperature']]
            line = [ts,day,t] + line 
            readings.append(line)
            sleep(1)
        readings = [x for x in readings if x != None]
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
            print(f"Alicat reading: {output}")
            self.AlicatCache = self.AlicatCache.append(pandas.Series(output,index=self.AlicatCache.columns),ignore_index=True)
            return output, self.AlicatCache
    
    def analyseData(self):
        pass
    
    def resetSensor(self):
        self.setParameter()
        self.flowcontroller.cancel_hold()

class mDAQ(SerialDeviceController):
    #TODO: add address, control_point to commConfig 
    def __init__(self,commConfig,sensorName,DAQCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SerialDeviceController.__init__(self,commConfig,sensorName,DAQCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.DAQCache = DAQCache
        self.interface_type = InterfaceType.USB
        self.output_channel = commConfig['channel']
        self.daq_device = None
        self.ao_device = None
        self.descriptor = None
        self.ouput_range = None
        
    def initSensor(self):
        try:
            # Get descriptors for all of the available DAQ devices.
            devices = get_daq_device_inventory(self.interface_type)
            number_of_devices = len(devices)

            # Verify at least one DAQ device is detected.
            if number_of_devices == 0:
                raise Exception('Error: No DAQ device is detected')

            print('Found', number_of_devices, 'DAQ device(s):')
            for i in range(number_of_devices):
                print('    ', devices[i].product_name, ' (', devices[i].unique_id, ')', sep='')

            # Create a DaqDevice object from the first descriptor.
            self.daq_device = DaqDevice(devices[0])
            self.ao_device = daq_device.get_ao_device()

            # Verify the specified DAQ device supports analog output.
            if ao_device is None:
                raise Exception('Error: The DAQ device does not support analog output')

            self.descriptor = daq_device.get_descriptor()
            print('\nConnecting to', self.descriptor.dev_string, '- please wait...')
            # Establish a connection to the device.
            self.daq_device.connect()

            ao_info = ao_device.get_info()
            self.output_range = ao_info.get_ranges()[0]  # Select the first supported range.
            
            print('\n', self.descriptor.dev_string, 'ready')
            print('    Function demonstrated: AoDevice.a_out')
            print('    Channel:', self.output_channel)
            print('    Range:', self.output_range.name)
            
            self.resetSensor()
            
        except Exception as e:
            print('\n', e)
        
    def stopSensor(self):
        try:
            if self.daq_device:
                # Disconnect from the DAQ device.
                if self.daq_device.is_connected():
                    self.daq_device.disconnect()
                # Release the DAQ device resource.
                self.daq_device.release()
                
        except Exception as e:
            print('\n', e)
    
    def resetSensor(self):
        system('clear')
        print('Active DAQ device: ', self.descriptor.dev_string, ' (',
              self.descriptor.unique_id, ')\n', sep='')
        
    def getReadings(self):
        #get previous voltage reading from csv files 
#        if self.log:
#            with open(self.log,newline='') as log:#self.log: #not sure if this will work????
#                writer = csv.reader(log)
        if self.log:
            df = pandas.read_csv(self.log)
            voltages = df['voltage']
        
        return voltages.iloc[-1]
                
    def setParameters(self,out_val):
        #store out_val in raspberry pi memory, not sure how to access DAQ voltage values using uldaq library
        Date = now.strftime("%d/%m/%Y")
        Time = now.strftime("%H:%M:%S")
        logEntry = [time(),Date,Time,out_val]
                
        if self.log:
            with open(self.log,'a+',newline='') as log:
                writer = csv.writer(log)
                writer.writerow(logEntry)
            
        try:
            self.ao_device.a_out(self.output_channel, self.output_range, AOutFlag.DEFAULT, float(out_val))
        except (ValueError, NameError, SyntaxError):
            pass

class GilsonMinipuls(SerialDeviceController):
    _control_commands = {"device model":b"%",
                          "reset":b"$", #restarts pump and returns to start up values (10rpm and off)
                          "start":b"KG",
                          "stop":b"KH",
                          "prime":b"K&", #sets rpms to max (60rpm) 
                          "counter clockwise":b"K<",
                          "clockwise":b"K>",
                          "faster":b"K+", #increases rpms by smallest unit (either 0.01 or 0.1 rpm depending on range)
                          "slower":b"K-"
                         }
    
    _read_commands = {"read display":b"R",
                    }
    
    def _input_command(self,commd,value):
        value  = bytes(value,'utf-8')
        
        _set_commands = {"set speed":b"S" + value
                        }
        
        return _set_commands[commd]
    
    def __init__(self,commConfig,sensorName,GilsonCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SerialDeviceController.__init__(self,commConfig,sensorName,GilsonCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.GilsonCache = GilsonCache
        self.eol  = "\r"
        
    def resetSensor(self):
        pass
    
    def _connect(self):
        SerialDeviceController.initSensor(self)
        
    def _disconnect(self):
        SerialDeviceController.stopSensor(self)
    
    def _command(self,commd,value):
        
        reading = None
        if not value:
            #read commands 
            try:
               command = self._read_commands[commd]
               reading = self._write(command)
            except KeyError:
                pass
            #commands to control pump (K type command)
            try:
                command = self._control_commands[commd]
                reading = self._write(command)
            except KeyError:
                pass
        #set parameters on pump
        else:
            command = self._input_command(commd,value)
            reading = self._write(command)
        if reading:
            return reading
    
    def _write(self,command):
        while self.serialP.in_waiting:
            self.serialP.read(self.serialP.in_waiting)
        self.serialP.write(command + bytes(self.eol,'utf-8'))
        self.serialP.write(b'')
        sleep(0.1)
        
        return readlineR(self.serialP,self.eol)
   
    def setSpeed(self,rpm):
        self._flush()
        output = self._command("set speed",str(rpm*100))
        print(output)
        
    def start(self):
        self._flush()
        output = self._command("start",value=None)
        print(output)
    
    def stop(self):
        self._flush()
        output = self._command("stop",value=None)
        print(output)
    
    def forward(self):
        self._flush()
        output = self._command("clockwise",value=None)
        print(output)
        
    def backward(self):
        self._flush()
        output = self._command("counter clockwise",value=None)
        print(output)
        
    def getFlow(self):
        self._flush()
        output = self._command("read display",value=None)
        return output
    
    def _reset(self):
        output = self._command("reset",value=None)
        print(output)
        sleep(5)
    
    def _flush(self):
        self.serialP.read(self.serialP.in_waiting)
        sleep(0.1)
        self.serialP.reset_input_buffer()
        self.serialP.reset_output_buffer()
        
    
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
