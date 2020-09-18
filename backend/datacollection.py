#!/usr/bin/env python
from configparser import SafeConfigParser
from os import path,mkdir,makedirs
import time
import sqlalchemy
from sys import stdout
from dataservice import SerialSensorReader
from dataservice import MetOneSensorReader
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
def main():
    global logdir
    if path.exists(CFGFILE):
        cfg=SafeConfigParser()
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

    curSensor = 'IRgas'
    if sensors_present.get(curSensor):
        commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                'bytesize':8,'parity':'N'}
        logFile = mklogfile(curSensor)
        rowType = (('reactor_stream',str),('IRgas_date',str),('IRgas_time',str),('CH4(%v/v)',float),('CO2(%v/v)',float),('temperature',float))
        sensors[curSensor] = SerialSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=60,db=db,log=logFile)
        sensors[curSensor].delimiterPattern = "[^,]+"#"[\d.-e]+"
        sensors[curSensor].delimiter = ","
    
    curSensor ='dustrack' 
    if sensors_present.get(curSensor):
        pass
    
    curSensor ='O2gas' 
    if sensors_present.get(curSensor):
        commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),'bytesize':8,'parity':'N'}
        logFile = mklogfile(curSensor)
        rowType = (('bscat_m_1',float),('calibcoef',float),('preassure_mb',float),('temp_K',int),('RH_percent',int),('relay_status',int))
        sensors[curSensor] = SerialSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=60,db=db,log=logFile)
    
    curSensor ='metone' 
    if sensors_present.get('metone'):
        commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout')}
        logFile = mklogfile(curSensor)
        rowType = (('daytime',str),('0_3',int),('0_5',int),('0_7',int),('1_0',int),('2_0',int),
                ('5_0',int),('UNK0',int),('UNK1',int),('UNK2',int))
        sensors[curSensor] = MetOneSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=10,db=db,log=logFile)
        sensors[curSensor].delimiterPattern = "[^,]+"#"[\d.-e]+"
        sensors[curSensor].delimiter = ","

    curSensor ='ucpc' 
    if sensors_present.get('ucpc'):
        commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),'baudrate':115200}
        logFile = mklogfile(curSensor)
        rowType = (('dayucpc',str),('timeucpc',str),('UNK1',int),('CN',float),('ST',int),('LT',float),('CNT',int),('PM',int),('RP',int))
        sensors[curSensor] = SerialSensorReader(commConfig=commConfig,sensorName=curSensor,rowType=rowType,rateSec=60,db=db,log=logFile)
        sensors[curSensor].delimiterPattern = "[^,]+"#"[\d.-e]+"
        sensors[curSensor].delimiter = ","
        sensors[curSensor].eol = "\r"
    if sensors_present.get('vueiss'):
        pass

    try:
        print(sensors)
        for name,sensor in sensors.iteritems():
            sensor.startCollection() #starting the each sensor connection in separate threads 
    except KeyboardInterrupt:
        print("Exiting")    
    for name,sensor in sensors.iteritems():
        sensor.stop()

if __name__ == "__main__":
    main()
