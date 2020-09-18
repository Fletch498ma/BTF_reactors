#!/usr/bin/env python

#system imports
from configparser import ConfigParser
from os import path,mkdir,makedirs
import os
import csv
import time
import sqlalchemy
import serial
from sys import stdout

#local imports
from viciValve import ViciValve
from dataservice import SerialSensorReader
from dataservice import IRSensorReader, ECSensorReader
#In configuration file have sensors and associate log filenames
#Have list of active sensors and directories for reading files.
#After reading a sensor file move it to a backup directory
CFGFILE="/home/pi/BTF_reactors/backend/backend.cfg"

logdir="logs"
session_id="testing"

global reactor

#state machine variables
polling=True
STDOUT = False # controls where the data goes, either to terminal stdout or to log files 

def logDir():
    if path.exists(CFGFILE):
        cfg=ConfigParser()
        cfg.read(CFGFILE)
    else:
        print ("ConfigFile not found.")
        exit() #exit() = quit which stops the current script 
    logdir = cfg.get("global","logdir")
    if not path.exists(logdir):
        print ("Creating: \'%s\'"%logdir)
        makedirs(logdir)
    return logdir
    
def gettimestamp(timeformat=False):
    #the default time stamp format (False) is the time in seconds since epoch
    if timeformat:
        now = time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime())
    else:
        now = time.time()
    return(now)

#seq = [7,8,5,6,1,2,3,4]
#delta = 3700
#experimentRun= True
#
#def start():
#    global v
#    v = ViciValve()
#    v.connect()
#    v.setup()
#
#def stop():
#    v.reset()
#    
#def sequence(seq,delta):
#    for i in seq:
#        start()
#        v.move(i)
#        v.interpretPosition()
#        stop()
#        time.sleep(delta)
#    
#while experimentRun:
#    sequence(seq,delta)
#    
def valvecheck():
    """Function doc """
    v = ViciValve()
    v.connect()
    v.setup()
    position = v.interpretPosition()
    return position

def logfilecheck():
    """ Function doc """
    pass
    
def mklogfile(sensorname,rowType):
    if STDOUT:
        return(stdout)
    logdir = logDir()
    
    #today = time.strftime("%Y-%m-%d",time.localtime())
    #files = [name for name in os.listdir(logdir) if os.path.isfile(os.path.join(logdir))]
    #check to see if files in directory are named with date 
    #logFile = [file for file in files if file.find(today) != -1] #.find returns -1 if searched string isn't found
        
    #Check if log file exists for reactor/sensorname/stream directory 
        #If yes, logpath is becomes most recent file date thats not full 
            #check if file is full 
    logpath = path.join(logdir,f"{sensorname}_{gettimestamp(timeformat=True)}.csv")#path.join(logdir,f"{reactor}/{sensorname}/{stream}/{gettimestamp()}.csv")
    with open(logpath,'w+') as log:
        w = csv.writer(log)
        w.writerow(list(list(zip(*(("Sensor",str),("Date",str),)+rowType)))[0])
        return log 
    
def main():
    global logdir
    logdir = logDir()
    if path.exists(CFGFILE):
        cfg=ConfigParser()
        cfg.read(CFGFILE)
    session_id = cfg.get("global","session_id")
    sensors_present = {}
    sensors_present.setdefault(False)
    for name,x in cfg.items("sensors_present"):
        sensors_present[name]=x in ('true','True')
    print(sensors_present)
    db = sqlalchemy.create_engine("sqlite:///%s"%session_id,echo=True)
    sensors = {}
    
    curSensor = 'ir_ek2'
    print(sensors_present.get(curSensor))
    if sensors_present.get(curSensor):
        print("working...")
        commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                'bytesize':8,'parity':'N'}
        rowType = (('Ref(pk-pkV)',int),('ChA(pk-pkV)',int),('ChB(pk-pkV)',int),('ChA(ppm)',int),('ChB(ppm)',int),('temperature',float),('Bulb(V)',int))
        logFile = '/home/pi/BTF_reactors/log/ir_ek2_2020-09-12_11-43-14.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasData.csv'
        sensors[curSensor] = IRSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=1,avg=10,db=None,log=logFile)
        sensors[curSensor].delimiterPattern = "\\S+"
        sensors[curSensor].delimiter = " "
    
    curSensor = 'ec_ek3'
    print(sensors_present.get(curSensor))
    if sensors_present.get(curSensor):
        print("working...")
        commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                'bytesize':8,'parity':'N'}
        rowType = (('Bias(mV)',int),('Concentration(ppm*100)',int),('OutputCurrent(nA)',int),('EC_SpanConcentration(ppm*100)',int),('SpanCurrent(nA)',int),('temperature',float)) #,('CurrentRange(nA)',str),('Range',str))
        logFile = '/home/pi/BTF_reactors/log/ec_ek3_2020-09-12_11-43-14.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
        sensors[curSensor] = ECSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=1,avg=10,db=None,log=logFile)
        sensors[curSensor].delimiterPattern = "\\S+"
        sensors[curSensor].delimiter = " "
    
#    curSensor = 'valve'
#    print(sensors_present.get(curSensor))
#    if sensors_present.get(curSensor)
#        commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
#                'bytesize':8,'parity':'N'}
    #curSensor = 'ph'
    #print(sensors_present.get(curSensor))
    #if sensors_present.get(curSensor):
        #print("working...")
        #commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                #'bytesize':8,'parity':'N'}
        #rowType = (('Voltage(V)',int))
        #logFile = mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/pHdata.csv'
        #sensors[curSensor] = pHSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=1,avg=10,db=None,log=logFile)
        #sensors[curSensor].delimiterPattern = "\\S+"
        #sensors[curSensor].delimiter = " "
        
    try:
        for name,sensor in sensors.items():
            sensor.startCollection() #starting teach sensor connection in separate threads 
    except KeyboardInterrupt:
        print("Exiting")
    
    for name,sensor in sensors.items():
        sensor.stop()

if __name__ == "__main__":
    while polling:
        #check what reactor stream is open and when opened (timestamp), if current timestamp - open timestamp > 3600 call valve switch
        #valvecheck()
        #check if log directory is greater than 2 weeks old, 
        logfilecheck()
        #if yes make new log directory
            #check calibration of sensors by running standards 
            #reset zero and span responses, record previous voltage values for drift analysis
            #run calibration sequence and extrapolate new coefficients, again store old values for analysis later
        #if no keep using same directory and search files within for right reactor stream
        main()
