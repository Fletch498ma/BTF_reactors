import serial
import time
import os

# Initially based on ReadAlicat
# Neph output string: 4.460e-06  5.828e-04 1003 296 99 00
# Column idenity: bscat (m-1), calibrator coef (,-1), pressure (mb), temp (K), RH (%), relay status
DATADIR = os.path.join(os.path.curdir,"Collected")

ser = serial.Serial('COM14', 9600,bytesize=7,parity='N', timeout=None,);

if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)
print "Data stored in:\'%s\'"%(os.path.abspath(DATADIR))
OutputName = time.strftime("Aeth%Y%m%d_%H%M.csv");
OutputFile = open(os.path.join(DATADIR,OutputName), "w")
OutputFile.write("Instr,Time,BC\n")

while 1:
    Line = ser.readline()
    LineArray = map(str.strip,Line.split(','))
    timeStr = time.strftime("%Y-%m-%d %H:%M:%S")
    toFile=""
    if len(LineArray)<3:
        print "Error an invalid number of lines was sent."
    else:
        toFile = "Aeth,{},{}".format(timeStr, ",".join(LineArray))
        display = ", ".join(["Aeth",timeStr,LineArray[2]])
        print display
        #print zip(xrange(0,len(Line.split())),Line.split())
        OutputFile.write(toFile + "\n")
        OutputFile.flush()
ser.close()
OutputFile.close()
