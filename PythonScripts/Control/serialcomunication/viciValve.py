import serial
import time
import datetime
from os import path,mkdir,makedirs
from configparser import ConfigParser

global CFGFILE
CFGFILE="/home/pi/BTF_reactors/backend/backend.cfg"

class ViciValve(object): 
    
    def __init__(self,valve_state=False,timeout=None):
        self.valve_state = valve_state
        self.num_positions = 8
        self.timeout = timeout
        
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
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
    
    #readlineR and comand really should be in a separate serial protocol module which ViciVave class should inherit from 
    def readlineR(self,ser,delim):
        timeout = 10
        line = ""
        start = time.time()
        waiting = True
        while(waiting):
            if ser.in_waiting: 
                c = str(ser.read(1),'utf-8')
                line = line + c
                waiting = not line.endswith(delim)
                start = time.time()
            else:
                time.sleep(1.0/ser.baudrate)
                waiting = time.time()-start < timeout
                if not waiting: line = None
        return line.strip()
        
    def comand(self,ser,cmd,length):
        com = False
        while not com:
            ser.read(ser.in_waiting)
            ser.write(cmd)
            time.sleep(1)
            line = self.readlineR(ser,'\r')
            if len(line) == length:
                com = True
                return line
            else:
                continue
    
    def setup(self):
        # Check number of positions and set to self.num_positions if not same
        
        self.clear()
        SNP = str(self.num_positions)
        NP = self.comand(ser,b'NP\r',6)
        time.sleep(1)
        while NP != 'NP = ' + SNP:
            self.clear()
            NP = self.comand(ser,b'NP'+SNP+b'\r',6)
            time.sleep(1)
        print('Number of valve positions set to ' + str(self.num_positions)+'\n')
    
    def connect(self):
        global ser, valve_port
        if path.exists(CFGFILE):
            cfg=ConfigParser()
            cfg.read(CFGFILE)
        valve_port = cfg.get("valve","port")
        while not self.valve_state:
            try:
                ser = serial.Serial(valve_port,9600,timeout=10)
                if ser.is_open:
                    self.valve_state = True
                    print('connected to port ' + valve_port)
            except:
                time.sleep(1) #delay for 1 second and wait for port to be open

    def getPosition(self,label=False):      
        self.clear()
        
        ser.write(b'CP\r')
        time.sleep(1)
        Val_Pos = str(ser.read(ser.in_waiting),'utf-8')
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
        print(self.reactor+'\n')
        
        return self.reactor
        
            
    def move (self, position, direction = "f"):
            if direction not in self._move_commands:
                raise "Invalid direction"

            command = self._move_commands[direction]

            # Make sure position is between 1 and NP
            position = ((int(position) - 1) % self.num_positions) + 1
            
            while self.getPosition() != position:
                self.clear()
                ser.write(b''+bytes(command,'utf-8') + b'0'+bytes(str(position),'utf-8') + b'\r')
                time.sleep(2)
            
            print(datetime.datetime.now(tz=None)) # print date and time stap after confirming valve has switched to the desired
            self.getPosition(label=True)
            
    def reset(self):
        if ser.is_open:
            ser.close()
            print('closing port ' + valve_port + '...\n')

    