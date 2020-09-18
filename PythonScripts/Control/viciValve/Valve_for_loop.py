import serial
import time
import datetime
from configparser import ConfigParser

seq = [1,5,2,6,3,7,4,8]
delta = 3600

class ViciValve(object): 
    
    def __init__(self,seq,delta,valve_state=False):
        self.seq = seq
        self.delta = delta
        self.valve_state = valve_state
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
        while ser.in_waiting > 0:
            ser.read(ser.in_waiting)
            
    def setup(self):
        # Check number of positions
        
        clear()
        SNP = bytes(str(self.num_positions),'utf-8')
        ser.write(b'NP\r')
        time.sleep(1)
        Val_Pos = ser.read(ser.in_waiting)
        while Val_Pos != b'NP = ' + SNP + b'\r':
            clear()
            ser.write(b'NP8\r')
            time.sleep(1)
            Val_Pos = ser.read(ser.in_waiting)
        print(Val_Pos)
    
    CFGFILE="/home/pi/BTF_reactors/backend/backend.cfg"
    def connect(self):
        global ser
        if path.exists(CFGFILE):
            cfg=ConfigParser()
            cfg.read(CFGFILE)
        valve_port = cfg.get("valve","port")
        while not self.valve_state:
            try:
                ser = serial.Serial(valve_port,9600,timeout=10)
                if ser.is_open:
                    self.valve_state = True
            except:
                time.sleep(1) #delay for 1 second and wait for port to be open

    def getPosition(self):      
        clear()
        
        ser.write(b'CP\r')
        time.sleep(1)
        Val_Pos = str(ser.read(ser.in_waiting),'utf-8')
        ValNum = int(Val_Pos[15])
        
        print('valve ' + Val_Pos + '\n')
        return Val_Pos
    
    def interpretPosition(self):
        
        pos = getPosition()
        ReacTable = ['Reactor1','Reactor2','Reactor3','Reactor4']
        
        if int(pos) < 5:
            flow = 'Outlet'
            self.reactor = 'R' + pos + ' ' +flow
        else:
            flow = 'Inlet'
            Val_Pos = str(int(pos) - 4)
            self.reactor = 'R' + Val_Pos + ' ' + flow 
        print(self.reactor)
        
        return self.reactor
        
            
    def move (self, position, direction = "f"):
            if direction not in self._move_commands:
                raise "Invalid direction"

            command = self._move_commands[direction]

            # Make sure position is between 1 and NP
            position = ((int(position) - 1) % self.num_positions) + 1
            
            while getPosition() =! str(position):
                ser.read(ser.in_waiting)
                ser.write(b'' + direction + str(position) + b'\r')
                time.sleep(2)
            
            print('Valve position = ' + getPosition())
            print(datetime.datetime.now(tz=None)) # print date and time stap after confirming valve has switched to the desired

    def reset(self)
        if ser.is_open:
            ser.close()

    print('connected to: ' + ser.name)     # check which port was really used
    ## Vale switching parameters:
    valve = [5,2,6,3,7,4,8,1]
    #valve = [1,5,2,6,3,7,4,8,1] # valve positions to switch between (1-4 is outlet streams and 5-8 is inlet) 
    switchdel = 3600# number of seconds valve is open
    sensIter = switchdel - 50 # the total time the valve is open is around 3700, however, running the IR_gas_data_function is slow and requires between 10-15 seconds to run "maintenance code" per run (clearing buffer,time delays,etc...)

    ser.read(ser.in_waiting)

    # Make sure the number of valve indices is set to 8 for the experiment 
    VPos = 8
    SNP = bytes(str(VPos),'utf-8')
    ser.write(b'NP\r')
    time.sleep(1)
    Val_Pos = ser.readline()
    if Val_Pos != b'NP = ' + SNP + b'\r':
        ser.read(ser.in_waiting)
        ser.write(b'NP8\r')
        time.sleep(1)
        Val_Pos = ser.readline()
    print(Val_Pos)
        
    # begin valve switching software for measuring gas compositions for all reactors 
    for i in range(0,len(valve)):
        uni = str(valve[i]) # int to string 
        vint = bytes(uni,'utf-8') # convert string to bytes by encoding with utf-8 to avoid the byte array format
        ser.write(b'GO0' + vint + b'\r') # ascii string to open vivi valve
        time.sleep(2) #0.1-1s delay for non-read commands is sufficient, just clear buffer by reading after write command
        ser.read(ser.in_waiting)
        ser.write(b'CP\r')
        time.sleep(1) #so I tried a 0.1s time delay in between write and read commands but it was enough because when I read it gives b'' so I found 1 sec gives enough time
        read_val = ser.readline()
        #check to make sure correct position and if not try again
        if read_val == b'Position is  = ' + vint + b'\r':
            print(read_val)
        else:
            ser.read(ser.in_waiting)
            ser.write(b'GO0' + vint + b'\r')
            time.sleep(2)
        now = datetime.datetime.now(tz=None)    # date and time stap for valve position
        print(now) # print date and time stap after confirming valve has switched to the desired

    # determine if it's a inlet or outlet stream and print reactor selected 
        if valve[i] <= 4:
            flow1 = 'Outlet'
            print('R' + uni + ' ' + flow1 + '\n')      
        else:
            flow2 = 'Inlet'
            itr = str(valve[i]-4)
            Stm = 'R' + itr + ' ' + flow2 + '\n'
            print(Stm)
        
    #    IR_gas_data_function(sensIter)
    # wat 1 hour (3600 sec) before switchng to next valve   
        time.sleep(switchdel)

    ser.close()

