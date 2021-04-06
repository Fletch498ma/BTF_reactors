import serial
import time
import os
DATADIR = os.path.join(os.path.curdir,"Collected")
HEADER = "instr,time,Record,Mode,Flags,CN,ST,LT,CNT,PM,RP"
INSTR = "CPC"
ser = serial.Serial('COM13', 115200, timeout=None);

if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)

OutputName = time.strftime(INSTR+"%Y%m%d_%H%M.csv");
OutputFile = open(os.path.join(DATADIR,OutputName), "w")
OutputFile.write(HEADER+"\n")

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
print "Data stored in:\'%s\'"%(os.path.abspath(DATADIR))


#Read a line from the port ending in '\r' return
#Theoretically the io library and TextIOWrapper should do this
def readlineR(ser):
    Line = ""
    while(1):
        if ser.inWaiting():
            c = ser.read(1)
            if c =='\r':
                break
            else:
                Line = Line + c
    return Line

readlineR(ser)  #clear buffer
while 1:    
    LineArray = readlineR(ser).split(",")
    print LineArray
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S")
    toFile = ",".join( [INSTR,timeStr] + LineArray[2:] )
    OutputFile.write(toFile+"\n")
    OutputFile.flush()
    print ", ".join([INSTR,timeStr, LineArray[3]])

ser.close()
OutputFile.close()
