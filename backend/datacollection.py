#!/usr/bin/env python

#system imports
from threading import Event
from queue import Queue
from configparser import ConfigParser
from os import path,mkdir,makedirs
import os
import csv
import time
import sqlalchemy
import serial
from sys import stdout
import pandas
import numpy as np

#phidget imports
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.VoltageOutput import *
from Phidget22.Devices.TemperatureSensor import *

#local imports
from analysis import Analysis
from viciValveThread import *
from dataservice import SensorReader,SerialSensorReader
from dataservice import IRSensorReader, ECSensorReader
from dataPhidget import PhidgetHumiditySensor, PhidgetPressureSensor_1136, PhidgetThermocouple, PhidgetpHSensor_1130
#In configuration file have sensors and associate log filenames
#Have list of active sensors and directories for reading files.
#After reading a sensor file move it to a backup directory
CFGFILE="/home/pi/BTF_reactors/backend/backend.cfg"

logdir="logs"
session_id="testing2"

#state machine variables
polling=True
STDOUT = False # controls where the data goes, either to terminal stdout or to log files 

class Address(object):
    """Class used to identify connected phidget devices."""
    
    def __init__(self, serialNumber, hubPort, channel, isHubPort, sensorType):
        self.serialNumber = serialNumber
        self.hubPort = hubPort
        self.channel = channel
        self.isHubPort = isHubPort
        self.sensorType = sensorType
      

addressMap = {
    'SMC_Valve_ToGasSensors':Address( 607325, 0, 0, False,None),
    'SMC_Valve_Port1Manifold':Address( 607325, 0, 1, False,None),
    'SMC_Valve_ViciCommon':Address( 607325, 0, 2, False,None),
    'SMC_Valve_Port3Manifold':Address( 607325, 0, 3, False,None),
    'ElectroChemCell_Outlet':Address( 607325, 0, 4, False,None),
    'SMC_Valve_Port5Manifold':Address( 607325, 0, 5, False,None),
    'ElectroChemCell_Inlet_Manifold':Address( 607325, 0, 6, False,None),
    'SMC_Valve_Port2Manifold':Address( 607325, 0, 7, False,None),
#    None:Address( 607325, 0, 8, False ),
#    None:Address( 607325, 0, 9, False ),
#    None:Address( 607325, 0, 10, False ),
#    None:Address( 607325, 0, 11, False ),
    'ElectroChemCell_Inlet':Address( 607325, 0, 12, False,None),
    'SMC_Valve_R3SumpOutlet':Address( 607325, 0, 13, False,None),
    'SMC_Valve_R4SumpOutlet':Address( 607325, 0, 14, False,None),
    'SMC_Valve_R2SumpOutlet':Address( 607325, 0, 15, False,None),
    'DifPressureSensor_Max2kPa':Address( 607325, 1, 0, True,VoltageRatioSensorType.SENSOR_TYPE_1136),
    'HumiditySensor':Address( 607325 , 2, 0, False,None),
#    None:Address( 607325, 4, 0, True ),
#    None:Address( 607325, 5, 0, True ),
    'pH_Reactor1':Address( 611075, 0, 0, False,VoltageSensorType.SENSOR_TYPE_1130_PH),
    'pH_Reactor2':Address( 611075, 0, 1, False,VoltageSensorType.SENSOR_TYPE_1130_PH),
    'pH_Reactor3':Address( 611075, 0, 2, False,VoltageSensorType.SENSOR_TYPE_1130_PH),
    'pH_Reactor4':Address( 611075, 0, 3, False,VoltageSensorType.SENSOR_TYPE_1130_PH),
    'dP_Reactor1':Address( 611075, 0, 7, False,VoltageRatioSensorType.SENSOR_TYPE_1136),
    'dP_Reactor2':Address( 611075, 0, 6, False,VoltageRatioSensorType.SENSOR_TYPE_1136),
    'dP_Reactor3':Address( 611075, 0, 5, False,VoltageRatioSensorType.SENSOR_TYPE_1136),
    'dP_Reactor4':Address( 611075, 0, 4, False,VoltageRatioSensorType.SENSOR_TYPE_1136),
    'K-Type_Incubator':Address( 611075, 1, 0, False,None),
    'K-Type_Reactor2':Address( 611075, 1, 1, False,None),
    'K-Type_Reactor3':Address( 611075, 1, 2, False,None),
    'K-Type_Reactor4':Address( 611075, 1, 3, False,None),
    'SMC_Valve_?1':Address( 611075, 5, 0, False,None),
    'SMC_Valve_?2':Address( 611075, 5, 1, False,None),
    'SMC_Valve_?3':Address( 611075, 5, 2, False,None),
    'SMC_Valve_?4':Address( 611075, 5, 3, False,None),
}

        
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
    
def mklogfile(reactor,sensorname,rowType,stream=None):
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
    if stream:
        logpath = path.join(logdir,f"{reactor}/{stream}/{sensorname}/{gettimestamp(timeformat=True)}_{sensorname}.csv")#path.join(logdir,f"{sensorname}_{gettimestamp(timeformat=True)}.csv")
    else:
        logpath = path.join(logdir,f"{reactor}/{sensorname}/{gettimestamp(timeformat=True)}_{sensorname}.csv")
    with open(logpath,'w+') as log:
        w = csv.writer(log)
        w.writerow(list(list(zip(*rowType))[0]))
        return log 
    
def dataMerge(data,path,dataf,timer):
    #data merging
    merge = [round(float(data['ir_ek2'][0][0]),2),data['ir_ek2'][0][1],data['ir_ek2'][0][2], #TimeIndex,Date,Time
             round(float(data['ir_ek2'][1][3]),4),round(float(data['ir_ek2'][1][4]),4),round(float(data['ir_ek2'][0][3]),4),round(float(data['ir_ek2'][0][4]),4),
             round(float(data['ir_ek2'][1][5]),4),round(float(data['ir_ek2'][1][6]),4),round(float(data['ir_ek2'][0][5]),4),round(float(data['ir_ek2'][0][6]),4),
             round(float(data['ec_ek3'][1][3]),4),round(float(data['ec_ek3'][1][4]),4),round(float(data['ec_ek3'][0][3]),4),round(float(data['ec_ek3'][0][4]),4),
             round(float(data['ir_ek2'][0][7]),1), #Temperature on EK2 board
             round(float(data['humidity'][1][3]),1),round(float(data['humidity'][1][4]),1),round(float(data['humidity'][0][3]),1),round(float(data['humidity'][0][4]),1),
             round(float(data['gas_pressure'][1][3]),4),round(float(data['gas_pressure'][1][4]),4),round(float(data['gas_pressure'][0][3]),4),round(float(data['gas_pressure'][0][4]),4),
             round(float(data['ph'][1][3]),3),round(float(data['ph'][1][4]),3),#round(float(data['ph'][0][3]),3),round(float(data['ph'][0][4]),3),
             round(float(data['ktype'][1][3]),2),round(float(data['ktype'][1][4]),2),#,round(float(data['ktype'][0][3]),2),round(float(data['ktype'][0][4]),2)]
             round(float(data['pressure_drop'][1][3]),4),round(float(data['pressure_drop'][1][4]),4)
             ]
             
    dataf = dataf.append(pandas.Series(merge,index=dataf.columns),ignore_index = True)
    #write df to csv if timer 
    if timer > 1000: #only write to final csv log if running valves for more than 20 min ~ 1000sec
        dataf.to_csv(path,mode='a',header=False,index=False)
    return dataf

def main(reactor,inlet_time,outlet_time,thermocouple,pH,pressure_drop,e):
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
    #print(sensors_present)
    db = sqlalchemy.create_engine("sqlite:///%s"%session_id,echo=True)
    sensors = {}
    ReactorTable = {"Reactor1":np.array([1,5]),"Reactor2":np.array([2,6]),"Reactor3":np.array([3,7]),"Reactor4":np.array([4,8])} 
    masterDir = {"Reactor1":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor1/master.csv',
                 "Reactor2":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor2/master.csv',
                 "Reactor3":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor3/master.csv',
                 "Reactor4":'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/Reactor4/master.csv'}
    
    cacheData = {'ir_ek2':[None,None],'ec_ek3':[None,None],'humidity':[None,None],'gas_pressure':[None,None],'ktype':[None,None],'ph':[None,None],'pressure_drop':[None,None]}
    data = {'ir_ek2':[None,None],'ec_ek3':[None,None],'humidity':[None,None],'gas_pressure':[None,None],'ktype':[None,None],'ph':[None,None],'pressure_drop':[None,None]}#[None,None] position 0 = outlet and position 1 = inlet
    
    dmaster = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'Inlet CH4(%v/v)':[],
                'STD-InCH4':[],
                'Outlet CH4(%v/v)':[],
                'STD-OutCH4':[],
                'Inlet CO2(%v/v)':[],
                'STD-InCO2':[],
                'Outlet CO2(%v/v)':[],
                'STD-OutCO2':[],
                'Inlet O2(%v/v)':[],
                'STD-InO2':[],
                'Outlet O2(%v/v)':[],
                'STD-OutO2':[],
                'Temperature (C)':[],
                'Inlet RelativeHumidity(%)':[],
                'STD-InletHumidity':[],
                'Outlet RelativeHumidity(%)':[],
                'STD-OutletHumidity':[],
                'Inlet Pressure (kPa)':[],
                'STD-InletPressure':[],
                'Outlet Pressure (kPa)':[],
                'STD-OutletPressure':[],
                'pH':[],
                'STD-pH':[],
                'Sump Temperature (C)':[],
                'STD-Sump Temp':[],
                'Pressure Drop (kPa)':[],
                'STD-Pressure Drop':[]
               }
    dfmaster = pandas.DataFrame(dmaster,columns=['TimeIndex','Date','Time','Inlet CH4(%v/v)','STD-InCH4','Outlet CH4(%v/v)','STD-OutCH4',
                                                 'Inlet CO2(%v/v)','STD-InCO2','Outlet CO2(%v/v)','STD-OutCO2',
                                                 'Inlet O2(%v/v)','STD-InO2','Outlet O2(%v/v)','STD-OutO2',
                                                 'Temperature (C)','Inlet RelativeHumidity(%)','STD-InletHumidity',
                                                 'Outlet RelativeHumidity(%)','STD-OutletHumidity','Inlet Pressure (kPa)','STD-InletPressure',
                                                 'Outlet Pressure (kPa)','STD-OutletPressure','pH','STD-pH','Sump Temperature (C)','STD-Sump Temp',
                                                 'Pressure Drop (kPa)','STD-Pressure Drop'])
    
    
    #cache dataframe acting as in-house python database to store data locally before analysis or averaging.
    #this dataframe structure is sent to dataservice which then stores data and returns analysed data in a depreciated dictionary labeled 'data'={}
    #'data' dictionary stores data locally before being dumped in a master csv.
    dIR = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'Ref(pk-pkV)':[],
                'ChA(pk-pkV)':[],
                'ChB(pk-pkV)':[],
                'ChA(ppm)':[],
                'ChB(ppm)':[],
                'Temperature (C)':[],
                'Bulb(V)':[]}
    dfIRData = pandas.DataFrame(dIR,columns=['TimeIndex','Date','Time','Ref(pk-pkV)','ChA(pk-pkV)','ChB(pk-pkV)','ChA(ppm)','ChB(ppm)','Temperature (C)','Bulb(V)'])
    
    dEC = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'Bias(mV)':[],
                'Concentration(ppm*100)':[],
                'OutputCurrent(nA)':[],
                'EC_SpanConcentration(ppm*100)':[],
                'SpanCurrent(nA)':[],
                'Temperature (C)':[]}
    dfECData = pandas.DataFrame(dEC,columns=['TimeIndex','Date','Time','Bias(mV)','Concentration(ppm*100)','OutputCurrent(nA)','EC_SpanConcentration(ppm*100)','SpanCurrent(nA)','Temperature (C)'])
    
    dHum = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'RelativeHumidity(%)':[]}
    dfHumData = pandas.DataFrame(dHum,columns=['TimeIndex','Date','Time','RelativeHumidity(%)'])
    
    dPres = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'Differential Pressure(kPa)':[]}
    dfPresData = pandas.DataFrame(dPres,columns=['TimeIndex','Date','Time','Differential Pressure(kPa)'])
    
    dTemp = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'Temperature (C)':[]}
    dfTempData = pandas.DataFrame(dTemp,columns=['TimeIndex','Date','Time','Temperature (C)'])
    
    dpH = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'pH':[]}
    dfpHData = pandas.DataFrame(dpH,columns=['TimeIndex','Date','Time','pH'])
    
    
    for i in range(0,2):
        x = None
        position = ReactorTable[reactor][i]
        if position <= 4:
            stream = 'Outlet'
        else:
            stream = 'Inlet'
        irLogFile={}
        ecLogFile={}
        phLogFile={}
        if i == 0:
            timer=outlet_time
        else:
            timer=inlet_time
        
        #valve move
        curSensor = 'valve'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = {'port':cfg.get('valve','port'),'timeout':cfg.getint('global','timeout'),'bytesize':8,'parity':'N'}
            try:
                v = ViciValve(commConfig=commConfig,sensorName='valve',position=position,wait=15)
            except KeyboardInterrupt:
                print("Exiting")
            v.startValve()
            v.stop()
        
        curSensor = 'ir_ek2'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                    'bytesize':8,'parity':'N'}
            rowType = (('Ref(pk-pkV)',int),('ChA(pk-pkV)',int),('ChB(pk-pkV)',int),('ChA(ppm)',int),('ChB(ppm)',int),('temperature',float),('Bulb(V)',int))
            logFile = mklogfile(reactor,curSensor,(("TimeIndex",float),("Date",str),("Time",str),) + rowType ,stream=stream)#'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/ir_ek2_2021-2-28.csv'
            sensors[curSensor] = IRSensorReader(commConfig=commConfig,sensorName=curSensor,IRcache=dfIRData,threadName=curSensor,eventType='continuous_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=x,log=logFile.name)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
            
        curSensor = 'ec_ek3'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                    'bytesize':8,'parity':'N'}
            rowType = (('Bias(mV)',int),('Concentration(ppm*100)',int),('OutputCurrent(nA)',int),('EC_SpanConcentration(ppm*100)',int),('SpanCurrent(nA)',int),('temperature',float)) #,('CurrentRange(nA)',str),('Range',str))
            logFile = mklogfile(reactor,curSensor,(("TimeIndex",float),("Date",str),("Time",str),) + rowType ,stream=stream)#'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/ec_ek3_2021-2-28.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
            sensors[curSensor] = ECSensorReader(commConfig=commConfig,sensorName=curSensor,ECcache=dfECData,threadName=curSensor,eventType='continuous_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=x,log=logFile.name)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
            
        curSensor = 'humidity'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = addressMap['HumiditySensor']
            rowType = (('RelativeHumidity(%)',float),)
            logFile = mklogfile(reactor,curSensor,(("TimeIndex",float),("Date",str),("Time",str),) + rowType ,stream=stream)#'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/humidity_2021-2-28.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
            sensors[curSensor] = PhidgetHumiditySensor(commConfig=commConfig,sensorName=curSensor,Humcache=dfHumData,threadName=curSensor,eventType='continuous_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=x,log=logFile.name)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
        
        curSensor = 'gas_pressure'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = addressMap['DifPressureSensor_Max2kPa']
            rowType = (('Differential Pressure(kPa)',float),)
            logFile = mklogfile(reactor,curSensor,(("TimeIndex",float),("Date",str),("Time",str),) + rowType ,stream=stream)#'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/gas_Pressure_2021-2-28.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
            sensors[curSensor] = PhidgetPressureSensor_1136(commConfig=commConfig,sensorName=curSensor,PresCache=dfPresData,threadName=curSensor,eventType='continuous_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=x,log=logFile.name)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
        
        curSensor = 'pressure_drop'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = addressMap[pressure_drop]
            rowType = (('Differential Pressure(kPa)',float),)
            logFile = mklogfile(reactor,curSensor,(("TimeIndex",float),("Date",str),("Time",str),) + rowType )#'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/pressure_drop_2021-2-28.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
            sensors[curSensor] = PhidgetPressureSensor_1136(commConfig=commConfig,sensorName=curSensor,PresCache=dfPresData,threadName=curSensor,eventType='continuous_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=x,log=logFile.name)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
            
        curSensor = 'ph'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = addressMap[pH]
            rowType = (('pH',float),)
            logFile = mklogfile(reactor,curSensor,(("TimeIndex",float),("Date",str),("Time",str),) + rowType )#'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/pH_2021-2-28.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
            sensors[curSensor] = PhidgetpHSensor_1130(commConfig=commConfig,sensorName=curSensor,pHCache=dfpHData,threadName=curSensor,eventType='continuous_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=x,log=logFile.name)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
            
        curSensor = 'ktype'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = addressMap[thermocouple]
            rowType = (('Temperature (C)',float),)
            logFile = mklogfile(reactor,curSensor,(("TimeIndex",float),("Date",str),("Time",str),) + rowType )#'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/RawData/SumpTemperature_2021-2-28.csv'#mklogfile(curSensor,rowType)#'/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
            sensors[curSensor] = PhidgetThermocouple(commConfig=commConfig,sensorName=curSensor,TempCache=dfTempData,threadName=curSensor,eventType='continuous_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=x,log=logFile.name)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
           
        try:
            for name,sensor in sensors.items():
                sensor.startCollection() #starting teach sensor connection in separate threads
        except KeyboardInterrupt:
            print("Exiting")
        
        for name,sensor in sensors.items():
            output = sensor.stop()
            data[name][i] = output[0] #averaged and analysed data with header
            cacheData[name][i] = output[1] #raw data frame 
            print(data)
    
    merged = dataMerge(data,masterDir[reactor],dfmaster,timer)
    return merged

if __name__ == "__main__":
    #while polling:
    #check what reactor stream is open and when opened (timestamp), if current timestamp - open timestamp > 3600 call valve switch
    #check if log directory is greater than 2 weeks old, 
    logfilecheck()
    #if yes make new log directory
        #check calibration of sensors by running standards 
        #reset zero and span responses, record previous voltage values for drift analysis
        #run calibration sequence and extrapolate new coefficients, again store old values for analysis later
    #if no keep using same directory and search files within for right reactor stream
    valvSchedule = ["Reactor1","Reactor2","Reactor3","Reactor4"]
    thermocouple = ['K-Type_Incubator','K-Type_Reactor2','K-Type_Reactor3','K-Type_Reactor4']
    pH = ['pH_Reactor1','pH_Reactor2','pH_Reactor3','pH_Reactor4']
    
    # system whide checks (check sensor span and zeros, set inlet reactor gas concentrations)
    while polling:
        for v in range(0,len(valvSchedule)):
            e = Queue()
            #before reactor data is taken system checks should be done (pressure sensor blank)
            data = main(valvSchedule[v],thermocouple[v],pH[v],e)
            #bed removal vs. sump removal run
            print(data)
            