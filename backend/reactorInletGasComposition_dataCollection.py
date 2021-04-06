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
import math
from statistics import *
import datetime 

#phidget imports
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.VoltageOutput import *
from Phidget22.Devices.TemperatureSensor import *

#local imports
from util import ek2RowTypes,ek3RowTypes,createDF
from analysis import Analysis
from viciValveThread import *
from controlDevices import Alicat
from alicat import FlowController
from dataservice import SensorReader,SerialSensorReader
from dataservice import IRSensorReader, IR_nonThreadCommands, EC_nonThreadCommands, ECSensorReader
from dataPhidget import PhidgetHumiditySensor, PhidgetPressureSensor_1136
#In configuration file have sensors and associate log filenames
#Have list of active sensors and directories for reading files.
#After reading a sensor file move it to a backup directory
CFGFILE="/home/pi/BTF_reactors/backend/backend.cfg"
CFGFILE_EK2="/home/pi/BTF_reactors/log/ir_ek2/config.cfg"
CFGFILE_EK3="/home/pi/BTF_reactors/log/ec_ek3/config.cfg"
CFGFILE_PRES="/home/pi/BTF_reactors/log/phidgets/diffpressure_1136/config.cfg"
CFGFILE_HUM="/home/pi/BTF_reactors/log/phidgets/humidity_HUM1000/config.cfg"

logdir={'ir_ek2':'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/ir_ek2',
        'ec_ek3':'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/ec_ek3',
        'pressure':'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/diffpressure_1136',
        'humidity':'/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/humidity_HUM1000',
        }

session_id="gas sensor check"

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
    'SMC_Valve_Port4Manifold':Address( 607325, 0, 4, False,None),
    'SMC_Valve_Port5Manifold':Address( 607325, 0, 5, False,None),
    'SMC_Valve_Port6Manifold':Address( 607325, 0, 6, False,None),
    'SMC_Valve_Port2Manifold':Address( 607325, 0, 7, False,None),
#    None:Address( 607325, 0, 8, False ),
#    None:Address( 607325, 0, 9, False ),
#    None:Address( 607325, 0, 10, False ),
#    None:Address( 607325, 0, 11, False ),
#    None:Address( 607325, 0, 12, False ),
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

def cfgLog(cfgFile,parser):
    
    if path.exists(cfgFile):
        cfg=ConfigParser()
        cfg.read(cfgFile)
    else:
        print ("ConfigFile not found.")
    
    # in case multiple sections/values need to be parsed 
    for name in parser:
        cfg.set(parser[name][0],parser[name][1],str(parser[name][2]))
    
    # Over-writing configuration file to 'cfgFile'
    with open(cfgFile,'w') as parsed:
        cfg.write(parsed)
    
def gettimestamp(timeformat=False):
    #the default time stamp format (False) is the time in seconds since epoch
    if timeformat:
        now = time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime())
    else:
        now = time.time()
    return(now)

def dataMerge(data,path,rowType):
    dataf = createDF(rowType)
    dataf = dataf.append(pandas.Series(data,index=dataf.columns),ignore_index = True)
    dataf.to_csv(path,mode='a',header=False,index=False)
    
    return dataf

def mklogfile(sensorname,rowType,parm,phidget_present=False):
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
    if phidget_present:
        if parm == 'zero':
            logpath = path.join(logdir,f"phidgets/{sensorname}/Zero/{gettimestamp(timeformat=True)}.csv")#path.join(logdir,f"{reactor}/{sensorname}/{stream}/{gettimestamp()}.csv")
        elif parm == 'spanCH4':
            logpath = path.join(logdir,f"phidgets/{sensorname}/SpanCH4/{gettimestamp(timeformat=True)}.csv")#path.join(logdir,f"{reactor}/{sensorname}/{stream}/{gettimestamp()}.csv")
        elif parm == 'spanCO2':
            logpath = path.join(logdir,f"phidgets/{sensorname}/SpanCO2/{gettimestamp(timeformat=True)}.csv")#path.join(logdir,f"{reactor}/{sensorname}/{stream}/{gettimestamp()}.csv")
  
    else:
        if parm == 'zero':
            logpath = path.join(logdir,f"{sensorname}/Zero/{gettimestamp(timeformat=True)}.csv")#path.join(logdir,f"{reactor}/{sensorname}/{stream}/{gettimestamp()}.csv")
        elif parm == 'spanCH4':
            logpath = path.join(logdir,f"{sensorname}/SpanCH4/{gettimestamp(timeformat=True)}.csv")#path.join(logdir,f"{reactor}/{sensorname}/{stream}/{gettimestamp()}.csv")
        elif parm == 'spanCO2':
            logpath = path.join(logdir,f"{sensorname}/SpanCO2/{gettimestamp(timeformat=True)}.csv")#path.join(logdir,f"{reactor}/{sensorname}/{stream}/{gettimestamp()}.csv")
       
    with open(logpath,'w+') as log:
        w = csv.writer(log)
        w.writerow(list(list(zip(*(("TimeIndex",str),("Date",str),("Time",str))+rowType)))[0])
        return logpath 

def ir_querie(commd,val=None):
    cfg = ConfigParser()
    cfg.read(CFGFILE)
    
    commConfig = {'port':cfg.get('ir_ek2','port'),'timeout':cfg.getint('global','timeout'),'bytesize':8,'parity':'N'}
    
    if val:
        _rowType = (("TimeIndex",float),("Date",str),("Time",str),("Dummy"),str)
        _cache = None
    else:
        try:
            _rowType = ek2RowTypes[commd]
            _cache = createDF(_rowType)
        except KeyError:
            _rowType = (("TimeIndex",float),("Date",str),("Time",str),("Dummy"),str)
            _cache = None
    try:
        ir = IR_nonThreadCommands(commConfig=commConfig,sensorName='ir_ek2',IRcache=_cache,threadName=commd,
                                    eventType=commd + '_event',event=None,rowType=_rowType,
                                    rateSec=1,timer=0,avg=10,db=None,log=None)
        ir._connect()
    except:
        print('connection issue')
    
    result = ir.call(commd)
    if val:
        result = result(val)
    else:
        result = result()
    
    ir._disconnect()
    print(result)
    return result

def ec_querie(commd,val=None):
    cfg = ConfigParser()
    cfg.read(CFGFILE)
    
    commConfig = {'port':cfg.get('ec_ek3','port'),'timeout':cfg.getint('global','timeout'),'bytesize':8,'parity':'N'}
    
    if val:
        _rowType = (("TimeIndex",float),("Date",str),("Time",str),("Dummy"),str)
        _cache = None
    else:
        try:
            _rowType = ek3RowTypes[commd]
            _cache = createDF(_rowType)
        except KeyError:
            _rowType = (("TimeIndex",float),("Date",str),("Time",str),("Dummy"),str)
            _cache = None
    try:
        ec = EC_nonThreadCommands(commConfig=commConfig,sensorName='ec_ek3',ECcache=_cache,threadName=commd,
                                    eventType=commd + '_event',event=None,rowType=_rowType,
                                    rateSec=1,timer=0,avg=10,db=None,log=None)
        ec._connect()
    except:
        print('connection issue')
    
    result = ec.call(commd)
    if val:
        result = result(val)
    else:
        result = result()
    
    ec._disconnect()
    print(result)
    return result

def main(e):
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
    print(datetime.datetime.now())
    #parameters for checking sensors
    
    #TODO: figure out how to create storage dictionary using nested for loops
    storage = {'N2':['C','flow','N2','zero',0.1,{'ir_ek2':[None,None],'ec_ek3':[None,None],'humidity':[None,None],'pressure':[None,None],'alicat':[None,None]}],
                '3%CO2 in Air':['A','flow',255,'spanCO2',5,{'ir_ek2':[None,None],'ec_ek3':[None,None],'humidity':[None,None],'pressure':[None,None],'alicat':[None,None]}],
                '2%CH4 in N2':['B','flow',255,'spanCH4',50,{'ir_ek2':[None,None],'ec_ek3':[None,None],'humidity':[None,None],'pressure':[None,None],'alicat':[None,None]}]
                }
#    parameters =  ['zero','spanCH4','spanCO2']
#    data = {'ir_ek2':[None,None,None],'ec_ek3':[None,None,None],'humidity':[None,None,None],'pressure':[None,None,None],'alicat':[None,None,None]}#[None,None] position 0 = outlet and position 1 = inlet
#    cacheData = {'ir_ek2':[None,None,None],'ec_ek3':[None,None,None],'humidity':[None,None,None],'pressure':[None,None,None],'alicat':[None,None,None]}
#    
    dmaster = {'TimeIndex':[],
               'Date':[],
               'Time':[],
               'CH4(%v/v)':[],
               'CO2(%v/v)':[],
               'O2(%v/v)':[],
               'RelativeHumidity(%)':[],
               'Pressure(kPa)':[],
               }
    dfmaster = pandas.DataFrame(dmaster,columns=['TimeIndex','Date','Time','CH4%(v/v)','CO2(%v/v)','O2(%v/v)','RelativeHumidity(%)','Pressure(kPa)'])
    
    
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
           'Bulb(V)':[],
           'Zero':[],
           'Span':[]
           }
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
    
    dAlicat = {'TimeIndex':[],
                'Date':[],
                'Time':[],
                'Gas':[],
                'Setpoint':[],
                'Mass Flow':[],
                'Pressure':[],
                'Control Point':[]
               }
    
    dfAlicatData = pandas.DataFrame(dAlicat,columns=['TimeIndex','Date','Time','Gas','Setpoint','Mass Flow','Pressure','Control Point'])
    
    #get old zero and span data from config file and store in variable 
    #ZeroOld in non-volatile memory
    #alpha
    #Temp_cal temperature of calibration gas in non-volatile memory (will have to set to 20C for first measurement b/c calibration temp not stored on microcontroller)
    
    def interpretCoef(coef):
        x = str(int(coef))
        bbb = int(x[0:2])
        c = int(x[3])
        coefNum = round(bbb * 10 ** -c,c+4)
        
        return coefNum
    
    #get calibration parms from IR and EC sensors
    calibrationTCH4 = ir_querie('calibration A')[1]
    a_coef_CH4 = interpretCoef(calibrationTCH4['A coefficient 2(bbbc x 10^-c)'])
    n_coef_CH4 = interpretCoef(calibrationTCH4['N coefficient 2(bbbc x 10^-c)'])
    
    calibrationTCO2 = ir_querie('calibration B')[1]
    a_coef_CO2 = interpretCoef(calibrationTCO2['A coefficient 2(bbbc x 10^-c)'])
    n_coef_CO2 = interpretCoef(calibrationTCO2['N coefficient 2(bbbc x 10^-c)'])
    
    for gas,parms in storage.items():
        
        if gas == 'N2':
            port=cfg.get('alicat','port')
            timer=800
            mfc1=storage['3%CO2 in Air']
            mfc2=storage['2%CH4 in N2']
            flow_controller_1 = FlowController(port=port,address=mfc1[0])
            flow_controller_2 = FlowController(port=port,address=mfc2[0])
        elif gas == '3%CO2 in Air':
            port=cfg.get('alicat','port')
            timer=4000
            mfc1=storage['N2']
            mfc2=storage['2%CH4 in N2']
            flow_controller_1 = FlowController(port=port,address=mfc1[0])
            flow_controller_2 = FlowController(port=port,address=mfc2[0])
        elif gas == '2%CH4 in N2':
            port=cfg.get('alicat','port')
            timer=1200
            mfc1=storage['3%CO2 in Air']
            mfc2=storage['N2']
            flow_controller_1 = FlowController(port=port,address=mfc1[0])
            flow_controller_2 = FlowController(port=port,address=mfc2[0])
        
        flow_controller_1.hold()
        flow_controller_2.hold()
        
        flow_controller_1.close()
        flow_controller_2.close()
        
        curSensor = 'alicat'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = {'port':cfg.get(curSensor,'port'),'address':parms[0],'control_point':parms[1],'gas':parms[2]}
            rowType = (('gas',str),('setpoint',int),('mass_flow',int),('pressure',int),('temperature',float))
            logFile = mklogfile(curSensor,rowType,parms[3])
            sensors[curSensor] = Alicat(commConfig=commConfig,sensorName=curSensor,AlicatCache=dfAlicatData,threadName=curSensor,eventType='wait_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=None,log=logFile)
            sensors[curSensor].mass_flow = parms[4]
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
        
        curSensor = 'ir_ek2'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                    'bytesize':8,'parity':'N'}
            rowType = (('Ref(pk-pkV)',int),('ChA(pk-pkV)',int),('ChB(pk-pkV)',int),('ChA(ppm)',int),('ChB(ppm)',int),('temperature',float),('Bulb(V)',int))
            logFile = mklogfile(curSensor,rowType,parms[3])
            sensors[curSensor] = IRSensorReader(commConfig=commConfig,sensorName=curSensor,IRcache=dfIRData,threadName=curSensor,eventType='wait_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=None,log=logFile)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
            
        curSensor = 'ec_ek3'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = {'port':cfg.get(curSensor,'port'),'timeout':cfg.getint('global','timeout'),
                    'bytesize':8,'parity':'N'}
            rowType = (('Bias(mV)',int),('Concentration(ppm*100)',int),('OutputCurrent(nA)',int),('EC_SpanConcentration(ppm*100)',int),('SpanCurrent(nA)',int),('temperature',float)) #,('CurrentRange(nA)',str),('Range',str))
            logFile = mklogfile(curSensor,rowType,parms[3])
            sensors[curSensor] = ECSensorReader(commConfig=commConfig,sensorName=curSensor,ECcache=dfECData,threadName=curSensor,eventType='wait_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=None,log=logFile)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
            
        curSensor = 'humidity'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = addressMap['HumiditySensor']
            rowType = (('RelativeHumidity(%)',float),)
            logFile = mklogfile('humidity_HUM1000',rowType,parms[3],phidget_present=True)
            sensors[curSensor] = PhidgetHumiditySensor(commConfig=commConfig,sensorName=curSensor,Humcache=dfHumData,threadName=curSensor,eventType='wait_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=None,log=logFile)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
        
        curSensor = 'pressure'
        print(sensors_present.get(curSensor))
        if sensors_present.get(curSensor):
            commConfig = addressMap['DifPressureSensor_Max2kPa']
            rowType = (('Differential Pressure(kPa)',float),)
            logFile = mklogfile('diffpressure_1136',rowType,parms[3],phidget_present=True)
            sensors[curSensor] = PhidgetPressureSensor_1136(commConfig=commConfig,sensorName=curSensor,PresCache=dfPresData,threadName=curSensor,eventType='wait_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=timer,db=None,log=logFile)
            sensors[curSensor].delimiterPattern = "\\S+"
            sensors[curSensor].delimiter = " "
        
            
        try:
            for name,sensor in sensors.items():
                sensor.startCollection() #starting teach sensor connection in separate threads
            e.set()
        except KeyboardInterrupt:
            print("Exiting")
                    
        for name,sensor in sensors.items():
            output = sensor.stop()
            if name == 'alicat':
                if gas == 'N2':
                    ir_querie('set zero A')
                    time.sleep(12) #manual suggest giving 10sec for board to take an average of zero measurement before storing in non-volatile memory of ek2
                    ir_querie('set zero B')
                    time.sleep(12)
                    ec_querie('set EC zero')
                    time.sleep(12)
                
                elif gas == '3%CO2 in Air':
                    ir_querie('set span B')
                    time.sleep(12)
                    ec_querie('set EC span concentration',val=20.4)#%v/v
                    ec_querie('set EC span')
                    time.sleep(12)
                    
                elif gas == '2%CH4 in N2':
                    ir_querie('set span A')
                    time.sleep(12)
                
            for _ in parms[5][name]:
                parms[5][name][1] = output[1] #raw non-processed data 
                
            if gas == 'N2':
                #store old averaged zero/span values in master document for ir_ek2 and ec_ek3
                if name == 'ir_ek2':
                    IRdata = parms[5][name][1]
                    IRdata.insert(6,'Zero ChA',IRdata['ChA(pk-pkV)']/IRdata['Ref(pk-pkV)'])
                    IRdata.insert(7,'Zero ChB',IRdata['ChB(pk-pkV)']/IRdata['Ref(pk-pkV)'])
                    ZeroCH4 = mean(IRdata['Zero ChA'][int(len(IRdata['Zero ChA'])*0.5):int(len(IRdata['Zero ChA'])*0.9)])
                    ZeroCH4_std = stdev(IRdata['Zero ChA'][int(len(IRdata['Zero ChA'])*0.5):int(len(IRdata['Zero ChA'])*0.9)])
                    ZeroCO2 = mean(IRdata['Zero ChB'][int(len(IRdata['Zero ChB'])*0.5):int(len(IRdata['Zero ChB'])*0.9)])
                    ZeroCO2_std = stdev(IRdata['Zero ChB'][int(len(IRdata['Zero ChB'])*0.5):int(len(IRdata['Zero ChB'])*0.9)])
                    Temp_calZero = mean(IRdata['Temperature (C)'][int(len(IRdata['Temperature (C)'])*0.5):int(len(IRdata['Temperature (C)'])*0.9)])
                    Temp_calZero_std = stdev(IRdata['Temperature (C)'][int(len(IRdata['Temperature (C)'])*0.5):int(len(IRdata['Temperature (C)'])*0.9)])

                    ZeroCH4_EK2memory = list(ir_querie('zero A')[1]['Zero (Act/Ref)'])[0]
                    ZeroCO2_EK2memory = list(ir_querie('zero B')[1]['Zero (Act/Ref)'])[0]
                    TempZero_EK2memory = list(ir_querie('calibration A')[1]['Temperature (C)'])[0]
                    
                    parser={'zeroA':['a parameters','zero',ZeroCH4],'zeroAstd':['a parameters','zerostd',ZeroCH4_std],
                            'tempZero':['a parameters','temp',Temp_calZero],'tempZeroAstd':['a parameters','tempAstd',Temp_calZero_std],
                            'zeroAmem':['a parameterslocal','zero',ZeroCH4_EK2memory],'tempZeroAmem':['a parameterslocal','temp',TempZero_EK2memory],
                            'zeroB':['b parameters','zero',ZeroCO2],'zeroBstd':['b parameters','zerostd',ZeroCO2_std],
                            'tempZeroBstd':['b parameters','temp',Temp_calZero],'tempBstd':['b parameters','tempstd',Temp_calZero_std],
                            'zeroBmem':['b parameterslocal','zero',ZeroCO2_EK2memory],'tempZeroBmem':['b parameterslocal','temp',TempZero_EK2memory]
                            }
                    cfgLog(CFGFILE_EK2,parser)
                    
    #                    IRdata.insert(6,'ChA Compensated Noramlised Ratio (Old Zero)',(IRdata['ChA(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroOld))*(1+_alpha(IRdata['Temperature (C)'])*(IRdata['Temperature (C)'] - Temp_cal)))
    #                    IRdata.insert(7,'ChB Compensated Noramlised Ratio (Old Zero)',(IRdata['ChB(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroOld))*(1+_alpha(IRdata['Temperature (C)'])*(IRdata['Temperature (C)'] - Temp_cal)))
    #                    IRdata.insert(10,'ChA Compensated Noramlised Ratio (Local Zero)',(IRdata['ChA(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroOld))*(1+alpha*(Temp - Temp_cal)))
    #                    IRdata.insert(11,'ChB Compensated Noramlised Ratio (Local Zero)',(IRdata['ChB(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroOld))*(1+alpha*(Temp - Temp_cal)))
    #                    
                    #average data points when zero reading is stable
                elif name == 'ec_ek3':
                    ECdata = parms[5][name][1]
                    
                    ZeroO2 = mean(ECdata['OutputCurrent(nA)'][int(len(ECdata['OutputCurrent(nA)'])*0.5):int(len(ECdata['OutputCurrent(nA)']))])
                    ZeroO2_std = stdev(ECdata['OutputCurrent(nA)'][int(len(ECdata['OutputCurrent(nA)'])*0.5):int(len(ECdata['OutputCurrent(nA)']))])
                    TempO2_zero = mean(ECdata['Temperature (C)'][int(len(ECdata['Temperature (C)'])*0.5):int(len(ECdata['Temperature (C)']))])
                    TempO2_zero_std = stdev(ECdata['Temperature (C)'][int(len(ECdata['Temperature (C)'])*0.5):int(len(ECdata['Temperature (C)']))])
                    
                    parser={'zeroO2':['parameters','zero',ZeroO2],
                            'zeroO2std':['parameters','zerostd',ZeroO2_std],
                            'tempZero':['parameters','tempzero',TempO2_zero],
                            'tempZerostd':['parameters','tempzerostd',TempO2_zero_std]
                            }
                    cfgLog(CFGFILE_EK3,parser)
                    
                elif name == 'pressure':
                    PRESdata = parms[5][name][1]
                    
                    Zero_Pres = mean(PRESdata['Differential Pressure(kPa)'][int(len(PRESdata['Differential Pressure(kPa)'])*0.2):int(len(PRESdata['Differential Pressure(kPa)'])*0.8)])
                    Zero_Pres_std = stdev(PRESdata['Differential Pressure(kPa)'][int(len(PRESdata['Differential Pressure(kPa)'])*0.2):int(len(PRESdata['Differential Pressure(kPa)'])*0.8)])
                      
                    parser={'zeropres':['ek2 ek3 zero pressure','pressure',Zero_Pres],
                            'zeropresstd':['ek2 ek3 zero pressure','std',Zero_Pres_std]
                            }
                    cfgLog(CFGFILE_PRES,parser)
                    
                elif name == 'humidity':
                    HUMdata = parms[5][name][1]
                    
                    Zero_Hum = mean(HUMdata['RelativeHumidity(%)'][int(len(HUMdata['RelativeHumidity(%)'])*0.8):int(len(HUMdata['RelativeHumidity(%)']))])
                    Zero_Hum_std = stdev(HUMdata['RelativeHumidity(%)'][int(len(HUMdata['RelativeHumidity(%)'])*0.8):int(len(HUMdata['RelativeHumidity(%)']))])
                    
                    parser={'zerohum':['ek2 ek3 zero humidity','humidity',Zero_Hum],
                            'zerohumstd':['ek2 ek3 zero humidity','std',Zero_Hum_std]
                            }
                    cfgLog(CFGFILE_HUM,parser)
            
            #TODO: change round() to int() and cfgLog with prasers updated
            elif gas == '3%CO2 in Air':
                if name == 'ir_ek2':
                    IRdata = parms[5][name][1]
                    C_CO2stand = 3 #%v/v
                    IRdata.insert(6,'Span ChB',(1-IRdata['ChB(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroCO2))/(1-math.exp(-a_coef_CO2 * C_CO2stand ** n_coef_CO2)))
                    SpanCO2 = mean(IRdata['Span ChB'][int(len(IRdata['Span ChB'])*0.8):int(len(IRdata['Span ChB']))])
                    SpanCO2_std = stdev(IRdata['Span ChB'][int(len(IRdata['Span ChB'])*0.8):int(len(IRdata['Span ChB']))])
                    Temp_calSpanCO2 = mean(IRdata['Temperature (C)'][int(len(IRdata['Temperature (C)'])*0.8):int(len(IRdata['Temperature (C)']))])
                    Temp_calSpanCO2_std = stdev(IRdata['Temperature (C)'][int(len(IRdata['Temperature (C)'])*0.8):int(len(IRdata['Temperature (C)']))])
                    
                    SpanCO2_EK2memory = list(ir_querie('span B')[1]['Span (Act/Ref*Zero)'])[0]
                    
                    parser={'spanB':['b parameters','span',SpanCO2],
                            'spanBstd':['b parameters','spanstd',SpanCO2_std],
                            'spanBmem':['b parameterslocal','span',SpanCO2_EK2memory],
                            'tempB':['b parameters','tempspan',Temp_calSpanCO2],
                            'tempBstd':['b parameters','tempspanstd',Temp_calSpanCO2_std]
                            }
                    cfgLog(CFGFILE_EK2,parser)
    #                    IRdata.insert(6,'ChB Compensated Noramlised Absorbance (Old Zero)',1-((IRdata['ChB(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroOld))*(1+alpha*(IRdata['Temperature (C)'] - Temp_cal))))
    #                    IRdata.insert(7,'ChB Compensated Span (Old Zero)',(IRdata['ChB Compensated Noramlised Absorbance (Old Zero)']/(1-exp(-a_coef * (3 ** c_coef))))+(beta*((IRdata['Temperature (C)'] - Temp_cal)/Temp_cal))) #2 is CH4 calibration gas concentration in %v/

                elif name == 'ec_ek3':
                    ECdata = parms[5][name][1]
                    C_O2stand = 20.4 #%v/v
                    
                    SpanO2 = mean(ECdata['OutputCurrent(nA)'][int(len(ECdata['OutputCurrent(nA)'])*0.2):int(len(ECdata['OutputCurrent(nA)']))])
                    SpanO2_std = stdev(ECdata['OutputCurrent(nA)'][int(len(ECdata['OutputCurrent(nA)'])*0.2):int(len(ECdata['OutputCurrent(nA)']))])
                    TempO2_span = mean(ECdata['Temperature (C)'][int(len(ECdata['Temperature (C)'])*0.2):int(len(ECdata['Temperature (C)']))])
                    TempO2_span_std = stdev(ECdata['Temperature (C)'][int(len(ECdata['Temperature (C)'])*0.2):int(len(ECdata['Temperature (C)'])*0.8)])
                    
                    parser={'spanO2':['parameters','span',SpanO2],
                            'spanO2std':['parameters','spanstd',SpanO2_std],
                            'tempspan':['parameters','tempspan',TempO2_span],
                            'tempspanstd':['parameters','tempspanstd',TempO2_span_std]
                            }
                    cfgLog(CFGFILE_EK3,parser)
                    
                elif name == 'pressure':
                    PRESdata= parms[5][name][1]
                    
                    SpanCO2_Pres = mean(PRESdata['Differential Pressure(kPa)'][int(len(PRESdata['Differential Pressure(kPa)'])*0.2):int(len(PRESdata['Differential Pressure(kPa)'])*0.8)])
                    SpanCO2_Pres_std = stdev(PRESdata['Differential Pressure(kPa)'][int(len(PRESdata['Differential Pressure(kPa)'])*0.2):int(len(PRESdata['Differential Pressure(kPa)'])*0.8)])
                    
                    parser={'spanPres':['ek2 co2 span pressure','pressure',SpanCO2_Pres],
                            'spanPresstd':['ek2 co2 span pressure','std',SpanCO2_Pres_std],
                            'rangePresEK3':['ek3 max range pressure','pressure',SpanCO2_Pres],
                            'rangePresstdEK3':['ek3 max range pressure','std',SpanCO2_Pres_std]
                        }
                    cfgLog(CFGFILE_PRES,parser)

                elif name == 'humidity':
                    HUMdata = parms[5][name][1]
                    
                    SpanCO2_Hum = mean(HUMdata['RelativeHumidity(%)'][int(len(HUMdata['RelativeHumidity(%)'])*0.8):int(len(HUMdata['RelativeHumidity(%)']))])
                    SpanCO2_Hum_std = stdev(HUMdata['RelativeHumidity(%)'][int(len(HUMdata['RelativeHumidity(%)'])*0.8):int(len(HUMdata['RelativeHumidity(%)']))])
                    
                    parser={'spanHum':['ek2 co2 span humidity','humidity',SpanCO2_Hum],
                            'spanHumstd':['ek2 co2 span humidity','std',SpanCO2_Hum_std],
                            'rangeHumEK3':['ek3 max range humidity','humidity',SpanCO2_Hum],
                            'rangeHumstdEK3':['ek3 max range humidity','std',SpanCO2_Hum_std]
                        }
                    cfgLog(CFGFILE_HUM,parser)

            elif gas == '2%CH4 in N2':
                if name =='ir_ek2':
                    IRdata = parms[5][name][1]
                    C_CH4stand = 2 #%v/v
                    IRdata.insert(6,'Span ChA',(1-IRdata['ChA(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroCH4))/(1-math.exp(-a_coef_CH4 * C_CH4stand ** n_coef_CH4)))
                    SpanCH4 = mean(IRdata['Span ChA'][int(len(IRdata['Span ChA'])*0.8):int(len(IRdata['Span ChA']))])
                    SpanCH4_std = stdev(IRdata['Span ChA'][int(len(IRdata['Span ChA'])*0.8):int(len(IRdata['Span ChA']))])
                    Temp_calSpanCH4 =  mean(IRdata['Temperature (C)'][int(len(IRdata['Temperature (C)'])*0.8):int(len(IRdata['Temperature (C)']))])
                    Temp_calSpanCH4_std = stdev(IRdata['Temperature (C)'][int(len(IRdata['Temperature (C)'])*0.8):int(len(IRdata['Temperature (C)']))])
                    
                    SpanCH4_EK2memory = list(ir_querie('span A')[1]['Span (Act/Ref*Zero)'])[0]
                    
                    parser={'spanA':['a parameters','span',SpanCH4],
                            'spanAstd':['a parameters','spanstd',SpanCH4_std],
                            'spanAmem':['a parameterslocal','span',SpanCH4_EK2memory],
                            'tempA':['a parameters','tempspan',Temp_calSpanCH4],
                            'tempAstd':['a parameters','tempspanstd',Temp_calSpanCH4_std]
                            }
                    cfgLog(CFGFILE_EK2,parser)
                    
    #                    IRdata.insert(6,'ChA Compensated Noramlised Absorbance (Old Zero)',1-((IRdata['ChA(pk-pkV)']/(IRdata['Ref(pk-pkV)']*ZeroOld))*(1+alpha*(IRdata['Temperature (C)'] - Temp_cal))))
    #                    IRdata.insert(7,'ChA Compensated Span (Old Zero)',(IRdata['ChA Compensated Noramlised Absorbance (Old Zero)']/(1-exp(-a_coef * (2 ** c_coef))))+(beta*((IRdata['Temperature (C)'] - Temp_cal)/Temp_cal))) #3 is CO2 calibration gas concentration in %v/v
     
                elif name == 'pressure':
                    PRESdata= parms[5][name][1]
                    
                    SpanCH4_Pres = mean(PRESdata['Differential Pressure(kPa)'][int(len(PRESdata['Differential Pressure(kPa)'])*0.2):int(len(PRESdata['Differential Pressure(kPa)'])*0.8)])
                    SpanCH4_Pres_std = stdev(PRESdata['Differential Pressure(kPa)'][int(len(PRESdata['Differential Pressure(kPa)'])*0.2):int(len(PRESdata['Differential Pressure(kPa)'])*0.8)])
                    
                    parser={'spanPres':['ek2 ch4 span pressure','pressure',SpanCH4_Pres],
                            'spanPresstd':['ek2 ch4 span pressure','std',SpanCH4_Pres_std]
                        }
                    cfgLog(CFGFILE_PRES,parser)

                elif name == 'humidity':
                    HUMdata = parms[5][name][1]
                    
                    SpanCH4_Hum = mean(HUMdata['RelativeHumidity(%)'][int(len(HUMdata['RelativeHumidity(%)'])*0.8):int(len(HUMdata['RelativeHumidity(%)']))])
                    SpanCH4_Hum_std = stdev(HUMdata['RelativeHumidity(%)'][int(len(HUMdata['RelativeHumidity(%)'])*0.8):int(len(HUMdata['RelativeHumidity(%)']))])
                    
                    parser={'spanHum':['ek2 ch4 span humidity','humidity',SpanCH4_Hum],
                            'spanHumstd':['ek2 ch4 span humidity','std',SpanCH4_Hum_std]  
                        }
                    cfgLog(CFGFILE_HUM,parser)
        
        flow_controller_1 = FlowController(port=port,address=mfc1[0])
        flow_controller_2 = FlowController(port=port,address=mfc2[0])
        #cancel holding valve shut 
        flow_controller_1.cancel_hold()
        flow_controller_2.cancel_hold()
        #flow controller ports
        flow_controller_1.close()
        flow_controller_2.close()
    
    now = datetime.datetime.now()
    Date = now.strftime("%d/%m/%Y")
    Time = now.strftime("%H:%M:%S")
    timeStamp = [time.time(),Date,Time]
    
    dataZeroIR = np.array(timeStamp+[ZeroCH4,ZeroCH4_std,ZeroCO2,ZeroCO2_std,Temp_calZero,Temp_calZero_std,
                                     Zero_Pres,Zero_Pres_std,Zero_Hum,Zero_Hum_std,
                                     ZeroCH4_EK2memory,ZeroCO2_EK2memory,TempZero_EK2memory])
    rowZeroIR = (('TimeIndex',float),('Date',str),('Time',str),('Zero CH4',float),('Zero CH4 STD',float),('Zero CO2',float),('Zero CO2 STD',float),
                ('Temperature (C)',float),('Temp STD',float),('Pressure (kPa)',float),('Pressure STD',float),('Humidity (%)',float),
                ('Humidity STD',float),('Zero CH4 EK2',float),('Zero CO2 EK2',float),('Temperature (C) EK2',float))
    zeroIRdir = '/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/ir_ek2/Zero/OldParameters.csv'
    
    dataZeroEC = np.array(timeStamp+[ZeroO2,ZeroO2_std,Temp_calZero,Temp_calZero_std,
                                     Zero_Pres,Zero_Pres_std,Zero_Hum,Zero_Hum_std])
                                
    rowZeroEC = (('TimeIndex',float),('Date',str),('Time',str),('Zero O2',float),('Zero O2 STD',float),
                ('Temperature (C)',float),('Temp STD',float),('Pressure (kPa)',float),('Pressure STD',float),('Humidity (%)',float),
                ('Humidity STD',float))
    zeroECdir = '/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/ec_ek3/Zero/OldParameters.csv'
    
    dataSpanCO2 = np.array(timeStamp+[SpanCO2,SpanCO2_std,SpanCO2_EK2memory,Temp_calSpanCO2,Temp_calSpanCO2_std,
                                        SpanCO2_Pres,SpanCO2_Pres_std,SpanCO2_Hum,SpanCO2_Hum_std])
    rowSpanCO2 = (('TimeIndex',float),('Date',str),('Time',str),('Span CO2',float),('Span CO2 STD',float),('Span CO2 EK2',float),
                  ('Temperature (C)',float),('Temp STD',float),('Pressure (kPa)',float),('Pressure STD',float),('Humidity (%)',float),('Humidity STD',float))
    SpanCO2dir = '/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/ir_ek2/SpanCO2/OldParameters.csv'
    
    dataSpanCH4 = np.array(timeStamp+[SpanCH4,SpanCH4_std,SpanCH4_EK2memory,Temp_calSpanCH4,Temp_calSpanCH4_std,
                                        SpanCH4_Pres,SpanCH4_Pres_std,SpanCH4_Hum,SpanCH4_Hum_std])
    rowSpanCH4 = (('TimeIndex',float),('Date',str),('Time',str),('Span CH4',float),('Span CH4 STD',float),('Span CH4 EK2',float),
                  ('Temperature (C)',float),('Temp STD',float),('Pressure (kPa)',float),('Pressure STD',float),('Humidity (%)',float),('Humidity STD',float))
    SpanCH4dir = '/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/ir_ek2/SpanCH4/OldParameters.csv'
    
    dataSpanO2 = np.array(timeStamp+[SpanO2,SpanO2_std,TempO2_span,TempO2_span_std,
                                        SpanCO2_Pres,SpanCO2_Pres_std,SpanCO2_Hum,SpanCO2_Hum_std])
    rowSpanO2 = (('TimeIndex',float),('Date',str),('Time',str),('Span O2',float),('Span O2 STD',float),
                  ('Temperature (C)',float),('Temp STD',float),('Pressure (kPa)',float),('Pressure STD',float),('Humidity (%)',float),('Humidity STD',float))
    SpanO2dir = '/media/pi/One Touch/Seagate/raspberrypi/Biotrickling_filter_data/log2021/ec_ek3/SpanO2/OldParameters.csv'
    
    data_processed = {'Zero IR':dataMerge(dataZeroIR,zeroIRdir,rowZeroIR),'Zero EC':dataMerge(dataZeroEC,zeroECdir,rowZeroEC),'Span CO2':dataMerge(dataSpanCO2,SpanCO2dir,rowSpanCO2),'Span CH4':dataMerge(dataSpanCH4,SpanCH4dir,rowSpanCH4),'Span O2':dataMerge(dataSpanO2,SpanO2dir,rowSpanO2)}

    return data_processed

if __name__ == "__main__":
#    commConfig = {'port':'/dev/ttyUSB1','timeout':10000,'bytesize':8,'parity':'N'}
#    test = IR_nonThreadCommands(commConfig=commConfig,sensorName='ir_ek2',IRcache=None,threadName='test',
#                                eventType='test_event',event=None,rowType=ek2RowTypes['pcb'],
#                                rateSec=1,timer=0,avg=10,db=None,log=None)
#    baseRow = (("TimeIndex",float),("Date",str),("Time",str),)
    while True:
        ir_querie('span A')
        ir_querie('span B')

#    ec_querie('pcb')
#    ec_querie('set EC span concentration',val=2)
#    ec_querie('measure')
    
#    ir_querie('lamp')
#    ir_querie('calibration A')
#    ir_querie('calibration B')
#    ir_querie('set A concentration range 1',val=60000)
#    ir_querie('calibration A')
#    ir_querie('set A concentration range 1',val=1000)
    #test = ir_querie('calibration A')
    
#    def start():
#        test._connect()
#    
#    def _pcb():
#        pcb = test.pcb()
#        print(pcb)
#    
#    def _calbA():
#        test.rowType = baseRow + ek2RowTypes['calibration A']
#        calbTableA = test.calbTA()
#        print('\n') 
#        print(calbTableA)
#    
#    def _calbB():
#        test.rowType = baseRow + ek2RowTypes['calibration B']
#        calbTableB = test.calbTB()
#        print('\n') 
#        print(calbTableB) 
#    
#    def _setAConcR():
#        _calbA()
#        test.setAConcR1(60000)
#        _calbA()
#        test.setAConcR1(1000000)
#    
#    def _setBConcR():
#        _calbB()
#        test.setBConcR1(60000)
#        _calbB()
#        test.setBConcR1(3000)
#    
#    def _setBbetapos1():
#        _calbB()
#        test.setBbetapos1(-0.000005)
#        _calbB()
#        
#    def _setAncoeff1():
#        _calbA()
#        test.setACoef_n1(0.00614)
#        _calbA()
#      
#    def _setAacoeff1():
#        _calbA()
#        test.setACoef_a1(0.00999)
#        _calbA()
#        
#    start()
#    _pcb()
#    _calbA()
#    _setAacoeff1()
#    
#    test.rowType = baseRow + ek2RowTypes['zero A']
#    _zeroA = test.zeroA()
#    print('\n') 
#    print(_zeroA)
#    
#    test.rowType = baseRow + ek2RowTypes['zero B']
#    _zeroB = test.zeroB()
#    print('\n') 
#    print(_zeroB)
#    
#    test.rowType = baseRow + ek2RowTypes['span A']
#    _spanA = test.spanA()
#    print('\n') 
#    print(_spanA)
#    
#    test.rowType = baseRow + ek2RowTypes['span B']
#    _spanB = test.spanB()
#    print('\n') 
#    print(_spanB)
#    
    
