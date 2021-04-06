import serial
import time
import datetime
from os import path
from configparser import ConfigParser
from threading import Thread
from serial import *

#global CFGFILE
CFGFILE="/home/pi/BTF_reactors/backend/backend.cfg"

class ValveThread(Thread):
    
    def __init__(self,commConfig,sensorName,position,wait):
        Thread.__init__(self) 
        self.setName(sensorName)
        self.commConfig = commConfig 
        self.sensorName = sensorName
        self.end = False
        self.position = position
        self.wait = wait
    
    def run(self):
        if self.getPosition() == self.position:
            print(f"Valve already in position: {str(self.position)}")
        else:   
            self.move(self.position)
        Reactor = self.interpretPosition()
        print(Reactor)
    
    def startValve(self):
        self.end = False
        self.initSensor()
        self.start()
        
    def stop(self):
        self.end = True
        self.join()
        self.stopSensor()
        
    """Called by startCollection to initialize the sensor and communcations."""
    def initSensor(self):
        pass
    
    """Called by stop after collection has ended."""
    def stopSensor(self):
        pass
        
class ViciValve(ValveThread): 
    
    def __init__(self,commConfig,sensorName,position,wait):
        ValveThread.__init__(self,commConfig,sensorName,position,wait)
        self.eol = '\r'
        self.valve_state = False
        self.num_positions = 8
        
    _move_commands = {
            "c": "CW",
            "cw": "CW",
            "clockwise": "CW",
            "a": "CC",
            "cc": "CC",
            "counterclockwise": "CC",
            "anticlockwise": "CC",
            "f": "GO",
            "fastest": "GO"
        }
    
    def clear(self):
        timeout=10
        start = time.time()
        while self.serialP.in_waiting:
            self.serialP.read(self.serialP.in_waiting)
            if time.time() - start > 0:
                print("timed out") 
                break
         
    
    #readlineR and comand really should be in a separate serial protocol module which ViciVave class should inherit from 
    def readlineR(self):
        timeout = 10
        line = ""
        start = time.time()
        waiting = True
        while(waiting):
            if self.serialP.in_waiting: 
                c = str(self.serialP.read(1),'utf-8')
                line = line + c
                waiting = not line.endswith(self.eol)
                start = time.time()
                line.strip()
            else:
                time.sleep(1.0/self.serialP.baudrate)
                waiting = time.time()-start < timeout
                if not waiting: line = None
        return line
        
    def comand(self,cmd,length):
        com = False
        while not com:
            self.serialP.read(self.serialP.in_waiting)
            self.serialP.write(cmd)
            time.sleep(1)
            line = self.readlineR()
            if len(line) == length:
                com = True
                return line
            else:
                continue
    
#    def setup(self):
#        # Check number of positions and set to self.num_positions if not same
#        
#        self.clear()
#        SNP = str(self.num_positions)
#        NP = self.comand(ser,b'NP\r',6)
#        time.sleep(1)
#        while NP != 'NP = ' + SNP:
#            self.clear()
#            NP = self.comand(ser,b'NP'+SNP+b'\r',6)
#            time.sleep(1)
#        print('Number of valve positions set to ' + str(self.num_positions)+'\n')
##    
#    def connect(self):
#        global ser, valve_port
#        if path.exists(CFGFILE):
#            cfg=ConfigParser()
#            cfg.read(CFGFILE)
#        valve_port = cfg.get("valve","port")
#        while not self.valve_state:
#            try:
#                ser = serial.Serial(valve_port,9600,timeout=10)
#                if ser.is_open:
#                    self.valve_state = True
#                    print('connected to port ' + valve_port)
#            except:
#                time.sleep(1) #delay for 1 second and wait for port to be open
           
    def initSensor(self):
            while not self.valve_state:
                try:
                    self.serialP = serial.Serial(**self.commConfig)
                    if self.serialP.is_open:
                        self.valve_state = True
                except:
                    time.sleep(1) #delay for 1 second and wait for port to be open
            if self.serialP.is_open:
                chkport = "true"
            else:
                ckcport = "false"
            print("\nSerial port " +self.commConfig["port"] + " is open: " +chkport+"\n")
            self.resetSensor()

            # Check number of positions and set to self.num_positions if not same
            self.clear()
            NP = int(self.comand(b'NP\r',7)[5])
            time.sleep(1)
            while NP != self.num_positions:
                self.clear()
                NP = self.comand(b'NP'+bytes(str(self.num_positions),'utf-8')+b'\r',7)
                time.sleep(1)
            print('Number of valve positions set to ' + str(self.num_positions)+'\n')
    
    def resetSensor(self):
        print("Reseting Sensor: " + self.sensorName)
        return self.readlineR()
    
    def stopSensor(self):
        self.serialP.close()
        
    def getPosition(self,label=False):      
        self.clear()
        
        self.serialP.write(b'CP\r')
        time.sleep(1)
        Val_Pos = str(self.serialP.read(self.serialP.in_waiting),'utf-8')
        ValNum = int(Val_Pos[15])
        
        if label:
            print('Valve ' + Val_Pos)
        return ValNum
    
    def interpretPosition(self):
        
        pos = self.getPosition()
        ReacTable = ['Reactor1','Reactor2','Reactor3','Reactor4']
        
        if pos < 5:
            flow = 'Outlet'
            self.reactor = 'R' + str(pos) + ' ' +flow
        else:
            flow = 'Inlet'
            Val_Pos = str(pos - 4)
            self.reactor = 'R' + Val_Pos + flow 
        
        return self.reactor
        
            
    def move (self, position, direction = "f"):
            if direction not in self._move_commands:
                raise "Invalid direction"

            command = self._move_commands[direction]

            # Make sure position is between 1 and NP
            position = ((int(position) - 1) % self.num_positions) + 1
            
            while self.getPosition() != position:
                self.clear()
                self.serialP.write(b''+bytes(command,'utf-8') + b'0'+bytes(str(position),'utf-8') + b'\r')
                time.sleep(2)
            
            print(datetime.datetime.now(tz=None)) # print date and time stap after confirming valve has switched to the desired
            self.getPosition(label=True)
            
    def reset(self):
        if self.serialP.is_open:
            self.serialP.close()
            self.valve_state = False
            print('closing port ' + self.commConfig["port"] + '...\n')

if __name__ == "__main__":
    if path.exists(CFGFILE):
        cfg=ConfigParser()
        cfg.read(CFGFILE)
    commConfig = {'port':cfg.get('valve','port'),'timeout':cfg.getint('global','timeout'),
                'bytesize':8,'parity':'N'}
    try:
        test = ViciValve(commConfig=commConfig,sensorName='valve')
    except KeyboardInterrupt:
        print("Exiting")
    test.startValve()
    test.stop()
    