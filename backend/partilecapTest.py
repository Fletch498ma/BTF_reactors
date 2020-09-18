#!/usr/bin/env python
from configparser import ConfigParser
from os import path,mkdir,makedirs
import time
import sqlalchemy
from sys import stdout
from dataservice import SerialSensorReader
from dataservice import IRSensorReader
#In configuration file have sensors and associate log filenames
#Have list of active sensors and directories for reading files.
#After reading a sensor file move it to a backup directory
CFGFILE="/home/pi/BTF_reactors/backend/backend.cfg"

logdir="logs"
session_id="testing"

STDOUT = True

def gettimestamp():
    return(time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime()))
def mklogfile(sensorname):
    if STDOUT:
        return(stdout)
    logpath = path.join(logdir,sensorname+gettimestamp()+".csv")
    return(open(logpath,'w+'))

#global logdir
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
session_id = cfg.get("global","session_id")
sensors_present = {}
sensors_present.setdefault(False)
for name,x in cfg.items("sensors_present"):
    sensors_present[name]=x in ('true','True')
db = sqlalchemy.create_engine("sqlite:///%s"%session_id,echo=True)
sensors = {}

print("tsst")
curSensor = 'IRgas'
if sensors_present.get(curSensor):
    commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
            'bytesize':8,'parity':'N'}
    logFile = mklogfile(curSensor)
    rowType = (('Ref(pk-pkV',str),('ChA(pk-pkV)',str),('ChB(pk-pkV)',str),('ChA(ppm)',int),('ChB(ppm)',int),('temperature',float),('bulb(V)',str))
    sensors[curSensor] = IRSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=60,db=db,log=logFile)
    sensors[curSensor].delimiterPattern = "[^,]+"#"[\d.-e]+"
    sensors[curSensor].delimiter = ","

try:
    print(sensors)
    for name,sensor in sensors.items():
        sensor.startCollection() #starting the each sensor connection in separate threads 
    time.sleep(10)
except KeyboardInterrupt:
    print("Exiting")    
for name,sensor in sensors.items():
    sensor.stop()

