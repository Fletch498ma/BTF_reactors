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

#local imports
from analysis import *
from util import ek2RowTypes,ek3RowTypes,createDF

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

class SensorReader(Thread):
    """serPort is a pyserial serial port object
    rowType is a tuple of columnName,type pairs. Implicitly the first entry is "time",int and so avgRow is required to return a type of (int,) + rowType. Valid types are float,int,str,bytes. For strings using a db without arbitrary length strings use bytes.
    rateSec is the data polling rate the maximum rate that will be returned.
    log is a file handle where data will be logged to.
    db is an sqlalchemy database engine connection. See: http://docs.sqlalchemy.org/en/rel_0_5/sqlexpression.html and http://docs.sqlalchemy.org/en/rel_0_8/core/connections.html
    """
    
    """overriding the threading sub class __init__"""
    def __init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType = (),rateSec=10,avg=10,timer=100,db=None,log=None):
        
        e = event
        events = {'continuous_event':[SensorReader._continuous,(self,e,),{},True],
              'trigger_event':[SensorReader._trigger,(self,e,),{},False],
              'single_event':[SensorReader._single,(self,e,),{},False],
              'wait_event':[SensorReader._wait,(self,e,),{},False],
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
        self.rowType = (("TimeIndex",float),("Date",str),("Time",str),) + rowType 
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
                readingsStr = ["%s"%repr(reading) for reading in readings]
                rows = [self.toRow(reading) for reading in readings] 
                #ADD typecheck here and reset if there is a problem
                avgRows = self.avgRows(rows)
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
                    with open(self.log,'a+',newline='') as log:
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
#                        metadata = sq.MetaData(bind=self.db)
#                        print(repr(metadata.tables[self.sensorName]))
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
        return self.DataCache
    
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
        
        #print(self.DataCache)
        print(f"\n=======================\n{self.sensorName}\nRun time: {round(time() - start,0)}sec\nTimer Setpoint: {self.timer}sec\n=======================")
        return self.DataCache
    
    def _wait(self,e):
        start = time()
        end = start + self.timer
        while(not self.end):
            if localtime().tm_sec%self.rateSec == 0:
                e.wait()
                strt = time()
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
        return self.DataCache

    """Initialized the sensor using initSensor and starts the data collection loop."""
    def startCollection(self):
        self.initDB()
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
        cols.append(sq.Column('id',self.toDBType(int),primary_key = True))
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
class SerialSensorReader(SensorReader):
    def __init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SensorReader.__init__(self,commConfig,sensorName,DataCache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
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
            #print(line)
        readings = [x for x in readings if x != None]
        return readings
        
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)]
        readingsTyped=[]
        for r in readings:
            try:
                typed=[t(c) for t,c in zip(list(zip(*rowType))[1],r)]
                readingsTyped.append(typed)
            except ValueError:
                print("Conversion error in line:",repr(r))
            readings = readingsTyped
            
        if not readings: 
            return None
        else:
            strings = readings[0:3] #readings[0] = time stamp from getReadings()
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

class  IRSensorReader(SerialSensorReader):
    def __init__(self,commConfig,sensorName,IRcache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SerialSensorReader.__init__(self,commConfig,sensorName,IRcache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.eol = '\n\r'
        self.IRcache = IRcache   
        
    """this needs to be modified to fit the output of the IR sensors serial output, however, the final returned reading needs to be a tuple so avgRows is compatiable """
    def getReadings(self):
        self.serialP.read(self.serialP.in_waiting)
        self.serialP.write(b'[EK2 SEN MEA]')
        sleep(0.1)
        self.serialP.read(self.serialP.in_waiting)
        readings = SerialSensorReader.getReadings(self)
        #print(f"getReadings run time: {time()-strt}\n")
        return readings
   
    def getParameter(self,command):
        self.serialP.read(self.serialP.in_waiting)
        self.serialP.write(command)
        sleep(0.1)
        readings = []
        now=datetime.now()
        ts = str((int(time())/self.rateSec)*self.rateSec)
        day = now.strftime("%d/%m/%Y")
        t = now.strftime("%H:%M:%S")
        line = readlineR(self.serialP,self.eol)
        line = line.lstrip('[')
        line = line.rstrip(']\n\r')
        readings.append(self.delimiter.join([ts,day,t,line]))
        readings = [x for x in readings if x != None]
        return readings
    
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)] #check 
        readingsTyped=[]
        for r in readings: #make sure sensor reading values are all the same type, indicated by the rowType[1]
            indx = 0
            typed = []
            for t,c in zip(list(zip(*self.rowType))[1],r):
                indx += 1
                if indx == 4 or indx == 5 or indx == 6 or indx == 10: #columns with hexadecimal base
                    try:
                        typed.append(t(c,16))
                    except ValueError:
                        print("Conversion error in line:",repr(r))
                else: #all other columns with no keyword arguments 
                    try:
                        typed.append(t(c))
                    except ValueError:
                        print("Conversion error in line:",repr(r))
            readingsTyped.append(typed)
        readings = readingsTyped
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
            print(f"IR-EK2 reading: {output}")
            self.IRcache = self.IRcache.append(pandas.Series(output,index=self.IRcache.columns),ignore_index=True)
            self.reading = output
        
            return output, self.IRcache
    
    def toRow(self, reading):
        gets = [0,1,2,5,6,7,8,9,10,11]
        
        row = SerialSensorReader.toRow(self,reading)
        #print("toRow:",len(row),":",repr(row))
        if len(row) != 12:
            return None
        row = [row[i] for i in gets]    
        #print("aftercut:",len(row),":",row)
        return row
    
    def analyseData(self):
        col = np.array(['ChA(ppm)','ChB(ppm)','Temperature (C)'])
        data = np.array([Analysis(self.DataCache,col[i]).basicStats() for i in range(0,len(col))])
        cache = np.array([self.DataCache.TimeIndex.iloc[0],self.DataCache.Date.iloc[0],self.DataCache.Time.iloc[0],data[0,0]/10000,data[0,1]/10000,data[1,0]/10000,data[1,1]/10000,data[2,0]])
        return cache
    
    def resetSensor(self):
        pass
        #SerialSensorReader.resetSensor(self)
        #seenOP = False
        #while not seenOP:
            #self.serialP.reset_input_buffer()
            #self.serialP.reset_output_buffer()
            #self.serialP.write(b'[EK2 SEN SET]\r\n')
            #line = readlineR(self.serialP,self.eol)
            #print(repr(line))
            #if line.strip() == "[ACK]" or "[NAK]":
                #while self.serialP.in_waiting > 0:
                    #self.serialP.read(self.serialP.in_waiting)
                    #sleep(0.1)
                #else:   
                    #seenOP = True
                    #print("End Reset")
                    #break   
            #else: 
                #continue

class IR_nonThread(IRSensorReader):
    def __init__(self,commConfig,sensorName,IRcache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        IRSensorReader.__init__(self,commConfig,sensorName,IRcache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.setupMode = True
        self.log = log
        
    def _input_command(self,commd,var,sign):
        #weird conversion to change int value into string the serial command protocol for EK2 will accept
        if var is not None:
            if type(var) is int:
                decimal = -1
                varOG = var
                leadZero = ['000000','00000','0000','000','00','0','']
                if var == 0:
                    var = b'0000000'
                else:
                    for _ in range(0,10):
                        if var >= 1:
                            decimal += 1
                            var = var/10
                        else:
                            break
                    var = bytes(leadZero[decimal] + str(varOG),'utf-8')

            elif sign:
                power = 0
                if var < 0:
                    var = var*-1
                    sign = '-'
                else:
                    sign = '+'
                for _ in range(0,20):
                    if var < 100:
                        power += 1
                        var = var*10
                    else:
                        power = power - 2 #because EK2 serial protocol is formated w/o decimal places
                        break
                var = bytes(sign + str(int(var)) + str(power),'utf-8') #TEST:use .encode and see if it works instead of bytes()
                
            else:
                power = 0
                for _ in range(0,20):
                    if var < 100:
                        power += 1
                        var = var*10
                    else:
                        power = power - 2 #because EK2 serial protocol is formated w/o decimal places
                        break
                var = bytes(str(int(var)) + str(power),'utf-8') #TEST:use .encode and see if it works instead of bytes()
        else:
            var = b'none'
            
        command_list = {
            #range values are 7x (aaaaaaa) digit with units ppm
            "set A concentration range 1":b"[EK2 CAA RA1 " + var + b"]",
            "set A concentration range 2":b"[EK2 CAA RA2 " + var + b"]",
            "set A concentration range 3":b"[EK2 CAA RA3 " + var + b"]",
            "set B concentration range 1":b"[EK2 CAB RA1 " + var + b"]",
            "set B concentration range 2":b"[EK2 CAB RA2 " + var + b"]",
            "set B concentration range 3":b"[EK2 CAB RA3 " + var + b"]",
            #a coefficients represented as var ='aaab' where real_var = aaa x 10^-b
            "set A a coefficient 1":b"[EK2 CAA A1 " + var + b"]",
            "set A a coefficient 2":b"[EK2 CAA A2 " + var + b"]",
            "set A a coefficient 3":b"[EK2 CAA A3 " + var + b"]",
            "set B a coefficient 1":b"[EK2 CAB A1 " + var + b"]",
            "set B a coefficient 2":b"[EK2 CAB A2 " + var + b"]",
            "set B a coefficient 3":b"[EK2 CAB A3 " + var + b"]",
            #n coefficients
            "set A n coefficient 1":b"[EK2 CAA N1 " + var + b"]",
            "set A n coefficient 2":b"[EK2 CAA N2 " + var + b"]",
            "set A n coefficient 3":b"[EK2 CAA N3 " + var + b"]",
            "set B n coefficient 1":b"[EK2 CAB N1 " + var + b"]",
            "set B n coefficient 2":b"[EK2 CAB N2 " + var + b"]",
            "set B n coefficient 3":b"[EK2 CAB N3 " + var + b"]",
            #set alpha and beta coefficients var = 'saaab' fomrat
            "set A alphapos":b"[EK2 CAA ALPHA " + var + b"]",
            "set B alphapos":b"[EK2 CAB ALPHA " + var + b"]",
            "set A alphaneg":b"[EK2 CAA ALPHAN " + var + b"]",
            "set B alphaneg":b"[EK2 CAB ALPHAN " + var + b"]",
            "set A betapos 1":b"[EK2 CAA BETA1 " + var + b"]",
            "set A betapos 2":b"[EK2 CAA BETA2 " + var + b"]",
            "set A betapos 3":b"[EK2 CAA BETA3 " + var + b"]",
            "set B betapos 1":b"[EK2 CAB BETA1 " + var + b"]",
            "set B betapos 2":b"[EK2 CAB BETA2 " + var + b"]",
            "set B betapos 3":b"[EK2 CAB BETA3 " + var + b"]"  ,
            "set A betaneg 1":b"[EK2 CAA BETA1N " + var + b"]",
            "set A betaneg 2":b"[EK2 CAA BETA2N " + var + b"]",
            "set A betaneg 3":b"[EK2 CAA BETA3N " + var + b"]",
            "set B betaneg 1":b"[EK2 CAB BETA1N " + var + b"]",
            "set B betaneg 2":b"[EK2 CAB BETA2N " + var + b"]",
            "set B betaneg 3":b"[EK2 CAB BETA3N " + var + b"]"
        }
        
        return command_list[commd]
    
    _read_commands = {
        "pcb":b"[WHO]",
        "setup":b"[EK2 SEN SET]",
        "measure":b"[EK2 SEN MEA]",
        "lamp":b"[EK2 LMP ENQ]",
        "calibration A":b"[EK2 CAA ENQ]",
        "calibration B":b"[EK2 CAB ENQ]",
        "zero A":b"[EK2 CAA ZERO ENQ]",
        "zero B":b"[EK2 CAB ZERO ENQ]",
        "span A":b"[EK2 CAA SPAN ENQ]",
        "span B":b"[EK2 CAB SPAN ENQ]"
        }
    
    _set_commands = {
        "set zero A":b"[EK2 CAA ZERO]",
        "set zero B":b"[EK2 CAB ZERO]",
        "set span A":b"[EK2 CAA SPAN]",
        "set span B":b"[EK2 CAB SPAN]"
        }
    
    def _connect(self):
        SerialSensorReader.initSensor(self)
        
    def _disconnect(self):
        SerialSensorReader.stopSensor(self)
    
    def _setup(self):
        self.serialP.read(self.serialP.in_waiting)
        sleep(1.5)
        setup = self._read_commands['setup']
        while self.serialP.in_waiting:
            self.serialP.read(self.serialP.in_waiting) #manually clear input buffer by reading
            self.serialP.reset_input_buffer()
            self.serialP.reset_output_buffer()
            self.serialP.write(setup)
            sleep(0.1)
            self.serialP.read(self.serialP.in_waiting)
            sleep(1.3)
            
        self.setupMode = True
        
    def _command(self,commd,value,sign):
        self._setup()
        
        reading = None
        if not value:
            #read commands and store info
            try:
               command = self._read_commands[commd]
               reading = self._write_read(command,createDF(self.rowType),self.rowType)
            except KeyError:
                pass
            #set parameters in on-board controller (no input)
            try:
                command = self._set_commands[commd]
                self._write_set(command)
            except KeyError:
                pass
        #set parameters in on-board controller with inputs
        else:
            print(value)
            command = self._input_command(commd,value,sign)
            print(command)
            self._write(command)
        if reading:
            return reading
        
    def toRow(self,reading):
        row = SerialSensorReader.toRow(self,reading)
        readings = row

        try:
            typed=[t(c) for t,c in zip(list(zip(*self.rowType))[1],row)]
            #readingsTyped.append(typed)
        except ValueError:
            print("Conversion error in line:",repr(row))
        readings = typed
        
        return readings
    
    def flush(self):
        self.serialP.reset_input_buffer()
        self.serialP.reset_output_buffer()
        
    def _write_set(self,command):
        
        self.serialP.write(self._read_commands["measure"])
        sleep(0.1)
        self.serialP.read(self.serialP.in_waiting)
        sleep(1)
        
        while self.serialP.in_waiting:
            self.serialP.read(self.serialP.in_waiting)
        self.serialP.write(command)
        sleep(10)
        
    def _write(self,command):
        self.serialP.write(command)
        #return readlineR(self.serialP,self.eol)
        
    def _write_read(self,command,cache,rowType,retries=2):
        indx = 0
        retry = True
        def inner_loop():
            self.serialP.write(command)
            sleep(0.1)
            readings = []
            now=datetime.now()
            ts = str((int(time())/self.rateSec)*self.rateSec)
            day = now.strftime("%d/%m/%Y")
            t = now.strftime("%H:%M:%S")
            line = readlineR(self.serialP,self.eol)
            line = line.lstrip('[')
            line = line.rstrip(']\n\r')
            readings.append(self.delimiter.join([ts,day,t,line]))
            readings = self.toRow(readings[0])
            return readings
                
        for _ in range(retries+1):
            indx += 1
            if retry == False:
                break
            print(f'\nattempt {indx}...')
            readings = inner_loop()
            for r in readings:
                if r == 'NAK':
                    retry = True
                    self.flush()
                    break
                else:
                    retry = False

        cache = cache.append(pandas.Series(readings,index=cache.columns),ignore_index=True)
        #print(readings,cache)
        return readings, cache

     
    def logAppendRow(self,logEntry):
        if self.log:
            #print(logEntry)
            with open(self.log,'a+',newline='') as log:
                writer = csv.writer(log)
                writer.writerow(logEntry)
    
    def resetSensor(self):
        pass
    
class IR_nonThreadCommands(IR_nonThread):
    def __init__(self,commConfig,sensorName,IRcache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        IR_nonThread.__init__(self,commConfig,sensorName,IRcache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
    
    def _connect(self):
        IR_nonThread._connect(self)
        
    def _disconnect(self):
        IR_nonThread._disconnect(self)
                                 
    def _run(self,command,value=None,sign=False):
        results = IR_nonThread._command(self,command,value=value,sign=sign)
        return results
        
    def pcb(self):
        read = self._run('pcb')
        return read
    
    def measure(self):
        read = self._run('measure')
        return read
        
    def lamp(self):
        read = self._run('lamp')
        return read
        
    def calbTA(self):
        read = self._run('calibration A')
        return read
        
    def calbTB(self):
        read = self._run('calibration B')
        return read
        
    def zeroA(self):
        read = self._run('zero A')
        return read
        
    def zeroB(self):
        read = self._run('zero B')
        return read
        
    def spanA(self):
        read = self._run('span A')
        return read
        
    def spanB(self):
        read = self._run('span B')
        return read
        
    def setZeroA(self):
        self._run('set zero A')
        
    def setZeroB(self):
        self._run('set zero B')
        
    def setSpanA(self):
        self._run('set span A')
        
    def setSpanB(self):
        self._run('set span B')
        
    def setAConcR1(self,val):
        self._run('set A concentration range 1',value=val)
    
    def setAConcR2(self,val):
        self._run('set A concentration range 2',value=val)
        
    def setAConcR3(self,val):
        self._run('set A concentration range 3',value=val)
        
    def setBConcR1(self,val):
        self._run('set B concentration range 1',value=val)
    
    def setBConcR2(self,val):
        self._run('set B concentration range 2',value=val)
        
    def setBConcR3(self,val):
        self._run('set B concentration range 3',value=val)
        
    def setACoef_a1(self,val):
        self._run("set A a coefficient 1",value=val)
        
    def setACoef_a2(self,val):
        self._run("set A a coefficient 2",value=val)
    
    def setACoef_a3(self,val):
        self._run("set A a coefficient 3",value=val)
        
    def setBCoef_a1(self,val):
        self._run("set B a coefficient 1",value=val)
        
    def setBCoef_a2(self,val):
        self._run("set B a coefficient 2",value=val)
    
    def setBCoef_a3(self,val):
        self._run("set B a coefficient 3",value=val)
    
    def setACoef_n1(self,val):
        self._run("set A n coefficient 1",value=val)
        
    def setACoef_n2(self,val):
        self._run("set A n coefficient 2",value=val)
    
    def setACoef_n3(self,val):
        self._run("set A n coefficient 3",value=val)
        
    def setBCoef_n1(self,val):
        self._run("set B n coefficient 1",value=val)
        
    def setBCoef_n2(self,val):
        self._run("set B n coefficient 2",value=val)
    
    def setBCoef_n3(self,val):
        self._run("set B n coefficient 3",value=val)
    
    def setAalphapos(self,val):
        self._run("set A alphapos",value=val,sign=True)
        
    def setBalphapos(self,val):
        self._run("set B alphapos",value=val,sign=True)
        
    def setAalphaneg(self,val):
        self._run("set A alphaneg",value=val,sign=True)
        
    def setBalphaneg(self,val):
        self._run("set B alphaneg",value=val,sign=True)
        
    def setAbetapos1(self,val):
        self._run("set A betapos 1",value=val,sign=True)
        
    def setAbetapos2(self,val):
        self._run("set A betapos 2",value=val,sign=True)
        
    def setAbetapos3(self,val):
        self._run("set A betapos 3",value=val,sign=True)
        
    def setBbetapos1(self,val):
        self._run("set B betapos 1",value=val,sign=True)
        
    def setBbetapos2(self,val):
        self._run("set B betapos 2",value=val,sign=True)
        
    def setBbetapos3(self,val):
        self._run("set B betapos 3",value=val,sign=True)
       
    def setAbetaneg1(self,val):
        self._run("set A betaneg 1",value=val,sign=True)
        
    def setAbetaneg2(self,val):
        self._run("set A betaneg 2",value=val,sign=True)
        
    def setAbetaneg3(self,val):
        self._run("set A betaneg 3",value=val,sign=True)
        
    def setBbetaneg1(self,val):
        self._run("set B betaneg 1",value=val,sign=True)
        
    def setBbetaneg2(self,val):
        self._run("set B betaneg 2",value=val,sign=True)
        
    def setBbetaneg3(self,val):
        self._run("set B betaneg 3",value=val,sign=True)
        
    def call(self,commd,val=None):
        
        funcCall = {'pcb':self.pcb,
                    'measure':self.measure,
                    'lamp':self.lamp,
                    'calibration A':self.calbTA,
                    'calibration B':self.calbTB,
                    'zero A':self.zeroA,
                    'zero B':self.zeroB,
                    'span A':self.spanA,
                    'span B':self.spanB,
                    'set zero A':self.setZeroA,
                    'set zero B':self.setZeroB,
                    'set span A':self.setSpanA,
                    'set span B':self.setSpanB,
                    'set A concentration range 1':self.setAConcR1,
                    'set A concentration range 2':self.setAConcR2,
                    'set A concentration range 3':self.setAConcR3,
                    'set B concentration range 1':self.setBConcR1,
                    'set B concentration range 2':self.setBConcR2,
                    'set B concentration range 3':self.setBConcR3,
                    'set A a coefficient 1':self.setACoef_a1,
                    'set A a coefficient 2':self.setACoef_a2,
                    'set A a coefficient 3':self.setACoef_a3,
                    'set B a coefficient 1':self.setBCoef_a1,
                    'set B a coefficient 2':self.setBCoef_a2,
                    'set B a coefficient 3':self.setBCoef_a3,
                    'set A n coefficient 1':self.setACoef_n1,
                    'set A n coefficient 2':self.setACoef_n2,
                    'set A n coefficient 3':self.setACoef_n3,
                    'set B n coefficient 1':self.setBCoef_n1,
                    'set B n coefficient 2':self.setBCoef_n2,
                    'set B n coefficient 3':self.setBCoef_n3,
                    'set A alphapos':self.setAalphapos,
                    'set A alphaneg':self.setAalphaneg,
                    'set B alphapos':self.setBalphapos,
                    'set B alphaneg':self.setBalphaneg,
                    'set A betapos 1':self.setAbetapos1,
                    'set A betapos 2':self.setAbetapos2,
                    'set A betapos 3':self.setAbetapos3,
                    'set B betapos 1':self.setBbetapos1,
                    'set B betapos 2':self.setBbetapos2,
                    'set B betapos 3':self.setBbetapos3,
                    'set A betaneg 1':self.setAbetaneg1,
                    'set A betaneg 2':self.setAbetaneg2,
                    'set A betaneg 3':self.setAbetaneg3,
                    'set B betaneg 1':self.setBbetaneg1,
                    'set B betaneg 2':self.setBbetaneg2,
                    'set B betaneg 3':self.setBbetaneg3,
            }
        
        return funcCall[commd]
            
class  ECSensorReader(SerialSensorReader):
    def __init__(self,commConfig,sensorName,ECcache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SerialSensorReader.__init__(self,commConfig,sensorName,ECcache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.eol = '\n\r'
        self.ECcache = ECcache
        
    """modified for the EC sensor based on commands in ECEK3 manual. Different from IREK2 because sensor data is output only when prompted with a command, while IREK2 will continually send data lines if in 'measurement' mode"""
    def getReadings(self):
        strt = time()
        readings = []
        now=datetime.now()
        ts = str((int(time())/self.rateSec)*self.rateSec)
        day = now.strftime("%d/%m/%Y")
        t = now.strftime("%H:%M:%S")
        while len(readings) < 10:
            self.serialP.read(self.serialP.in_waiting)
            self.serialP.write(b'[EK3 ECM ENQ]')
            sleep(0.1)
            line = readlineR(self.serialP,self.eol)
            line = line.strip()
            line = line.lstrip('[')
            line = line.rstrip(']')
            readings.append(self.delimiter.join([ts,day,t,line]))
            sleep(1)
            #print(line)
        readings = [x for x in readings if x != None]
        #print(f"getReadings run time: {time()-strt}")
        return readings 
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)] #check 
        readingsTyped=[]
        for r in readings: #make sure sensor reading values are all the same type, indicated by the rowType[1]
            indx = 0
            typed = []
            for t,c in zip(list(zip(*self.rowType))[1],r):
                indx += 1
                if indx == 4 or indx == 5 or indx == 6 or indx == 7 or indx == 8: #columns with hexadecimal base
                    try:
                        typed.append(t(c,16))
                    except ValueError:
                        print("Conversion error in line:",repr(r))
                else: #all other columns with no keyword arguments 
                    try:
                        typed.append(t(c))
                    except ValueError: 
                        print("Conversion error in line:",repr(r))
            readingsTyped.append(typed)
        readings = readingsTyped  
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
            print(f"EC-EK3 reading: {output}")
            self.ECcache = self.ECcache.append(pandas.Series(output,index=self.ECcache.columns),ignore_index=True)
            #print(self.ECcache)
            return output, self.ECcache
            
    def toRow(self, reading):
        gets = [0,1,2,5,6,7,8,9,10]
        row = SerialSensorReader.toRow(self,reading)
        #print("toRow:",len(row),":",repr(row))
        if len(row) != 13:
            return None
        row = [row[i] for i in gets]    
        #print("aftercut:",len(row),":",row)
        return row
    
    def analyseData(self):
        col = np.array(['Concentration(ppm*100)','Temperature (C)'])
        data = np.array([Analysis(self.DataCache,col[i]).basicStats() for i in range(0,len(col))])
        cache = np.array([self.DataCache.TimeIndex.iloc[0],self.DataCache.Date.iloc[0],self.DataCache.Time.iloc[0],data[0,0]/1000000,data[0,1]/1000000,data[1,0]])
        return cache
    
    def resetSensor(self):
        #SerialSensorReader.resetSensor(self)
        pass

class EC_nonThread(ECSensorReader):
    def __init__(self,commConfig,sensorName,ECcache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        ECSensorReader.__init__(self,commConfig,sensorName,ECcache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
        self.setupMode = True
        self.log = log
        
    def _input_command(self,commd,var):
        var = hex(int(var * 1000000))
        var = var.lstrip('0x')
        length = len(var) - 1
        leadZero = ['0000000','000000','00000','0000','000','00','0','']
        
        var = bytes(leadZero[length] + str(var),'utf-8')

        command_list = {
            #set span concentration must be converted by following equation _(%v/v) * 10,000 (ppm/%v/v) * 100 * Hexadecimal/Decimal
            "set EC span concentration":b"[EK3 CAE SCG " + var + b"]"
            
        }
        
        return command_list[commd]
    
    _read_commands = {
        "pcb":b"[WHO]",
        "measure":b"[EK3 ECM ENQ]"
        }
    
    _set_commands = {
        "set EC zero":b"[EK3 CAE ZERO]",
        "set Pellistor zero":b"[EK3 CAP ZERO]",
        "set EC span":b"[EK3 CAE SPAN]",
        "set Pellistor span":b"[EK3 CAP SPAN]"
        }
    
    def _connect(self):
        SerialSensorReader.initSensor(self)
        
    def _disconnect(self):
        SerialSensorReader.stopSensor(self)
    
    def _setup(self):
        while self.serialP.in_waiting:
            self.serialP.read(self.serialP.in_waiting) #manually clear input buffer by reading
            self.serialP.reset_input_buffer()
            self.serialP.reset_output_buffer()
            sleep(1)
        
        self.setupMode = True
        
    def _command(self,commd,value):
        self._setup()
        
        reading = None
        if not value:
            #read commands and store info
            try:
               command = self._read_commands[commd]
               reading = self._write_read(command,createDF(self.rowType),self.rowType)
            except KeyError:
                pass
            #set parameters in on-board controller (no input)
            try:
                command = self._set_commands[commd]
                self._write(command)
            except KeyError:
                pass
        #set parameters in on-board controller with inputs
        else:
            command = self._input_command(commd,value)
            self._write(command)
        if reading:
            return reading
        
    def toRow(self,reading):
        row = SerialSensorReader.toRow(self,reading)
        readings = row

        try:
            typed=[t(c) for t,c in zip(list(zip(*self.rowType))[1],row)]
            #readingsTyped.append(typed)
        except ValueError:
            print("Conversion error in line:",repr(row))
        readings = typed
        
        return readings
    
    def _write(self,command):
        self.serialP.write(command)
        sleep(0.1)
        readlineR(self.serialP,self.eol)
        
    def _write_read(self,command,cache,rowType,retries=2):
        retry = True
        indx = 0
        def inner_loop():
            self.serialP.write(command)
            sleep(0.1)
            readings = []
            now=datetime.now()
            ts = str((int(time())/self.rateSec)*self.rateSec)
            day = now.strftime("%d/%m/%Y")
            t = now.strftime("%H:%M:%S")
            line = readlineR(self.serialP,self.eol)
            line = line.lstrip('[')
            line = line.rstrip(']\n\r')
            readings.append(self.delimiter.join([ts,day,t,line]))
            readings = self.toRow(readings[0])
            return readings
                
        for _ in range(retries+1):
            indx += 1
            if retry == False:
                break
            print(f'\nattempt {indx}...')
            readings = inner_loop()
            for r in readings:
                if r == 'NAK':
                    retry == True
                    self.flush()
                    break
                else:
                    retry = False
              
        cache = cache.append(pandas.Series(readings,index=cache.columns),ignore_index=True)
        return readings, cache
     
    def logAppendRow(self,logEntry):
        if self.log:
            #print(logEntry)
            with open(self.log,'a+',newline='') as log:
                writer = csv.writer(log)
                writer.writerow(logEntry)
    
    def resetSensor(self):
        pass
    
class EC_nonThreadCommands(EC_nonThread):
    def __init__(self,commConfig,sensorName,ECcache,threadName,eventType,event,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        EC_nonThread.__init__(self,commConfig,sensorName,ECcache,threadName,eventType,event,rowType,rateSec,avg,timer,db,log)
    
    def _connect(self):
        EC_nonThread._connect(self)
        
    def _disconnect(self):
        EC_nonThread._disconnect(self)
                                 
    def _run(self,command,value=None):
        results = EC_nonThread._command(self,command,value=value)
        return results
        
    def pcb(self):
        read = self._run('pcb')
        return read
    
    def measure(self):
        read = self._run('measure')
        return read
        
    def setECspanRange(self,val):
        self._run('set EC span concentration',value=val)
        
    def setECzero(self):
        self._run('set EC zero')
        
    def setPellzero(self):
        self._run('set Pellistor zero')
        
    def setECspan(self):
        self._run('set EC span')
        
    def setPellspan(self):
        self._run('set Pellistor span')
        
    def call(self,commd,val=None):
        
        funcCall = {'pcb':self.pcb,
                    'measure':self.measure,
                    'set EC span concentration':self.setECspanRange,
                    'set EC zero':self.setECzero,
                    'set EC span':self.setECspan,
                    'set Pellistor zero':self.setPellzero,
                    'set Pellistor span':self.setPellspan
            }
        
        return funcCall[commd]

if __name__ == "__main__":
    print('test')
#    try:
#        db = sq.create_engine('sqlite:///:memory:', echo=True)
#        sr = IRSensorReader({'port':'/dev/ttyUSB1','timeout':61},"Test1",(),1,db,stdout)
#        sr.startCollection()
#        sleep(100)
#        sr.stop()
#    except KeyboardInterrupt:
#        print("Exiting")
#    sr.stop()

#todo
#add database query
#fix it so that avgRow only deals with one averaged collection of readings per time interval
#getReadings returns all readings with a timestamp for each?
#then we only return the readings for one time interval?
#todo create metadatatable with sensor id, type, and name.
