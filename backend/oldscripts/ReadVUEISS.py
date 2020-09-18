import serial
import time
import math
import ctypes
import os
import time
import struct

DATADIR = os.path.join(os.path.curdir,"Collected")

#WeatherLink COM PORT
COMM = 'COM6'
BAUD = 19200
TIMEOUT = 30
INSTR = "WeatherLink"
#Verify connection using VER and TEST
#Dump and Decode EEPROM
#
#LOOPFORMAT = [1]*5+[2]*3+[1]*1+[2]*1+[1]*2+[2]*8+[1]*3+[2]*4+[1]*1+[2]*8+[1]*1+[2]*5+[1]*12+[2]*6+[1]*2+[2]*1
LOOPFORMAT  = "=cccbBxxHhBhBxHHHHHxxxxhxBxhhhHBHHHHHHHHBhhhhhxxBBBBBBBBBBxxxxxxxxxxxxccH"
LABELS=["L","O","O","Bar Trend","Packet Type","Barometer","Inside Temp","Inside Humidity",
        "Outside Temp","Wind Speed","Wind Direction","10-Min Avg. Wind Speed",
        "2-Min Avg. Wind Speed","10-Min Wind Gust","Wind Direction for 10-Min Wind Gust",
        "Dew Point","Outside Humidity","Heat Index","Wind Chill","THSW Index","Rain Rate",
        "UV","Solar Radiation","Storm Rain","Start Date of current Storm","Daily Rain",
        "Last 15-Min Rain","Last Hour Rain","Daily ET","Last 24-Hour Rain",
        "Barometric Reduction Method","User-ntered Barometric Offset","Barometric calibration number","Barometric Sensor Raw Reading","Absolute Barometric Preasure","Altimeter Setting","Ptr","Ptr","Ptr","Ptr","Ptr","Ptr","Ptr","Ptr","Ptr","Ptr","LF","CR","CRC"]
print len(LOOPFORMAT)

def parseLOOP2(loop):
    print struct.calcsize(LOOPFORMAT)    
    return struct.unpack(LOOPFORMAT,loop)

def clearBuff(ser):
    while ser.inWaiting():
        ser.read(1)

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

def readChar(ser,timeout = 30):
    tStart = time.time()
    while(1):
        if ser.inWaiting():
            return ser.read(1)
        else:
            time.sleep(.01)
        if time.time()-tStart > timeout:
            raise Exception()
            
def test(serial,expecting,timeout=30):
    tStart = time.time()
    while(1):
        if serial.inWaiting():
            time.sleep(.01)
            c = serial.read(1)
            if c == expecting[0]:
                expecting = expecting[1:]
                print repr(c),
        if expecting == "":
            return True
        if time.time()-tStart > timeout:
            return False
    return False

# Initially based on ReadAlicat
# Neph output string: 4.460e-06  5.828e-04 1003 296 99 00
# Column idenity: bscat (m-1), calibrator coef (,-1), pressure (mb), temp (K), RH (%), relay status

OutputName = time.strftime(INSTR + "%Y%m%d_%H%M.csv");

ser = serial.Serial(COMM, BAUD, timeout=TIMEOUT);

if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)
OutputFile = open(os.path.join(DATADIR,OutputName), "w")
OutputFile.write("Instr,Time,BC\n")

print "Data stored in:\'%s\'"%(os.path.abspath(DATADIR))

for i in range(0,3):
    ser.write("\n")
    time.sleep(1)
clearBuff(ser)
ser.write("TEST\n")
print "Recieved TEST back?:%s" % (repr(test(ser,"TEST\n\r")))

try:
    while 1:
        clearBuff(ser)
        ser.write("LOOP 1\n")
        ack = ser.read(1)
        if ord(ack) != 6:
            print "ACK not recieved from VUE"
        time.sleep(1)
        line = bytearray(ser.read(99))
        output = map(str,parseLOOP2(line))
        
        for x,y in zip(LABELS,output):
            print x +":" + y

        time.sleep(10)
        continue
        values = (float(LineArray[0]),float(LineArray[1]))
        toAvg.append(values)
        if len(LineArray)<5:
            print "Error an invalid number of lines was sent."
        elif math.floor(time.time())%60 == 0:
            avgVal = (sum(zip(*toAvg)[0])/len(toAvg),sum(zip(*toAvg)[1])/len(toAvg))
            timeStr = time.strftime("%Y-%m-%d %H:%M:%S") 
            toFile = "\'{},{}\'".format(timeStr, ",".join(LineArray))
            display = ",".join([timeStr]+list(map(str,values)))
            print display
            #print zip(xrange(0,len(Line.split())),Line.split())
            OutputFile.write(toFile + "\n")
            toAvg=[]
            time.sleep(1)
except KeyboardInterrupt:
    ser.close()
    exit()
