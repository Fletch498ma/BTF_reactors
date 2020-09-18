import serial
import time
import os.path
import os
DATADIR = os.path.join(os.path.curdir,"Collected")

ser = serial.Serial('COM15', 9600, timeout=None)

if not os.path.exists(DATADIR):
    os.makedirs(DATADIR)
print "Data stored in:\'%s\'"%(os.path.abspath(DATADIR))
OutputName = time.strftime("MetOne%Y%m%d_%H%M.csv");
OutputFile = open(os.path.join(DATADIR,OutputName), "w")
OutputFile.write("Instr,Time,MetOne03,MetOne05,MetOne07,MetOne1,MetOne2,MetOne5\n")

Metrics = [
    ['0.3', 2],
    ['0.5', 4],
    ['0.7', 6],
    ['1.0', 8],
    ['2.0', 10],
    ['5.0', 12]
]

while 1:
    #Check to see if the instrument is logging data.  Command to send
    #is OP\r.  If the instrument is not logging, it will return OP S.
    #If the instrument is running, it will return OP R #.  I believe
    #the # is the number of seconds that the instrument has been running.
    ser.write("OP\r")
    
    line = ser.readline()   #It sends out extra info we don't need so call twice.
    line = ser.readline()   #This is the one we need.
    LineArray = line.split()
    
    #Check to see if the instrument is running
    if LineArray[1] == 'S':
        ser.write("S\r")
        time.sleep(1)
        continue
    
    line = ser.readline()

    LineArray = line.split(',')
    if len(LineArray) != 20:
        continue
    
    Location = int(LineArray[15])
    
    PrintString = "MetOne, {}, ".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    for Metric, Column in Metrics:
        PrintString += str(LineArray[Column]).strip()
        if Column < 12:
            PrintString += ', '
            
    print PrintString
    OutputFile.write(PrintString + "\n")
    OutputFile.flush()
    
ser.close()
OutputFile.close()
