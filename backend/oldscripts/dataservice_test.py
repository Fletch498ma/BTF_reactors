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
#TODO the delimter patterns are odd in that they reject empty comma separated values


def valvecheck():
    """Function doc """
    v = ViciValve()
    v.connect()
    v.setup()
    position = v.interpretPosition()
    return position

class SensorReader(Thread):
    """serPort is a pyserial serial port object
    rowType is a tuple of columnName,type pairs. Implicitly the first entry is "time",int and so avgRow is required to return a type of (int,) + rowType. Valid types are float,int,str,bytes. For strings using a db without arbitrary length strings use bytes.
    rateSec is the data polling rate the maximum rate that will be returned.
    log is a file handle where data will be logged to.
    db is an sqlalchemy database engine connection. See: http://docs.sqlalchemy.org/en/rel_0_5/sqlexpression.html and http://docs.sqlalchemy.org/en/rel_0_8/core/connections.html
    """
    
    """overriding the threading sub class __init__"""
    def __init__(self,commConfig,sensorName,DataCache,rowType = (),rateSec=10,avg=10,timer=100,db=None,log=None):
        Thread.__init__(self) 
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
    
        print(self.DataCache)
        print(f"\n=======================\n{self.sensorName}\nRun time: {round(time() - start,0)}sec\nTimer Setpoint: {self.timer}sec\n=======================")
         
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
        return outputCache
#        if self.log:
#            self.log.flush()
    
    def analyseData(self):
        pass
    
    def collectData(self):
        post = self.analyseData()
        return post
    
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

class PhidgetSensorReader(SensorReader):
    def __init__(self,commConfig,sensorName,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SensorReader.__init__(self,commConfig,sensorName,rowType,rateSec,timer,db,log)
        self.eol = "\n"
        self.delimiterPattern = "\\S+"
        self.delimiter = " "
    def initSensor(self):
        pass
    def stopSensor(self):
        pass
    def getReadings(self):
        readlineR(self.serialP,self.eol)
        readings = []
        ts = str((int(time())/self.rateSec)*self.rateSec)
        while len(readings) < self.avg:
            line = readlineR(self.serialP,self.eol)
            line = line.lstrip('[')
            line = line.rstrip(']\n\r')
            readings.append(self.delimiter.join([ts, line]))
            sleep(1)
        readings = [x for x in readings if x != None]
        return readings

    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(rowType)]
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


    
#might want to make this a threadsafe interrupt driven reader
class SerialSensorReader(SensorReader):
    def __init__(self,commConfig,sensorName,DataCache,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SensorReader.__init__(self,commConfig,sensorName,DataCache,rowType,rateSec,avg,timer,db,log)
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
        readlineR(self.serialP,self.eol)
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
        readings = [r for r in readings if r != None and len(r) == len(rowType)]
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
    def __init__(self,commConfig,sensorName,IRcache,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SerialSensorReader.__init__(self,commConfig,sensorName,IRcache,rowType,rateSec,avg,timer,db,log)
        self.eol = '\n\r'
        self.IRcache = IRcache
        
    """this needs to be modified to fit the output of the IR sensors serial output, however, the final returned reading needs to be a tuple so avgRows is compatiable """
    def getReadings(self):
        strt = time()
        self.serialP.read(self.serialP.in_waiting)
        self.serialP.write(b'[EK2 SEN MEA]')
        sleep(0.1)
        self.serialP.read(self.serialP.in_waiting)
        readings = SerialSensorReader.getReadings(self)
        #print(f"getReadings run time: {time()-strt}\n")
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
            #print(self.IRcache)
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

class  ECSensorReader(SerialSensorReader):
    def __init__(self,commConfig,sensorName,ECcache,rowType=(),rateSec=10,avg=10,timer=100,db=None,log=None):
        SerialSensorReader.__init__(self,commConfig,sensorName,ECcache,rowType,rateSec,avg,timer,db,log)
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

class  pHSensorReader(PhidgetSensorReader):
    def __init__(self,commConfig,sensorName,rowType=(),rateSec=10,avg=10,db=None,log=None):
        SerialSensorReader.__init__(self,commConfig,sensorName,rowType,rateSec,db,log)
        self.eol = '\n\r'
    """this needs to be modified to fit the output of the IR sensors serial output, however, the final returned reading needs to be a tuple so avgRows is compatiable """
    def getReadings(self):
        strt = time()
        self.serialP.read(self.serialP.in_waiting)
        self.serialP.write(b'[EK2 SEN MEA]')
        sleep(0.1)
        self.serialP.read(self.serialP.in_waiting)
        readings = SerialSensorReader.getReadings(self)
        print(f"getReadings run time: {time()-strt}\n")
        return readings 
    def avgRows(self, readings):
        readings = [r for r in readings if r != None and len(r) == len(self.rowType)] #check 
        readingsTyped=[]
        for r in readings: #make sure sensor reading values are all the same type, indicated by the rowType[1]
            indx = 0
            typed = []
            for t,c in zip(list(zip(*self.rowType))[3],r):
                indx += 1
                if indx == 2 or indx == 3 or indx == 4 or indx == 8: #columns with hexadecimal base
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
            avg = list(pandas.DataFrame(readings,columns=list(zip(*self.rowType))[0]).mean()) #unzip first position in rowType which is variable title (for example 'CH4' or 'CO2') and use as header in dataframe. Dump readings tuple into column of data frame and average whole column 
            output = []
            numCol = 0
            for col in range(0,len(strings)):
                if type(strings[col]) == str:
                    output.append(strings[col])
                else:
                    output.append(avg[numCol])
                    numCol = numCol + 1
            output = [round(num,2) for num in output]
            print(f"\nIR-EK2 reading: {output}\n")
            return output
    
    def toRow(self, reading):
        gets = [0,3,4,5,6,7,8,9]
        
        row = SerialSensorReader.toRow(self,reading)
        #print("toRow:",len(row),":",repr(row))
        if len(row) != 10:
            return None
        row = [row[i] for i in gets]    
        #print("aftercut:",len(row),":",row)
        return row
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
#Since time is the primary key, I need a sensor ID to identify each sensor. 
#That can be the sensorname, but in that case the calling program, which will be giving out pointers
#will have to be aware of sensor ids. That makes sense since why should a data management program worry about metadata
#The sensor id can be unique and another table should be the one managing the type and name of the sensor.
#Since I'll likely be reading redundant data I'll need to not update if the primary key, time, is already in the table.
class FileSensorReader(SensorReader):
    def __init__(self):
        pass
    def initSensor(self):
        pass
    def stopSensor(self):
        pass
    def getReadings(self):
        pass
    def toRow(self,reading):
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
