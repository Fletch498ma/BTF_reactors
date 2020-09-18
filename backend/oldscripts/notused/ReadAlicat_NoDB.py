import serial
import time

Line = time.strftime("%Y%m%d%H%M%S") + 'GasFlow.csv';
ser = serial.Serial('COM7', 19200, timeout=None);
Output = open(Line, 'a');

while 1:
    ser.write("A\r")
    time.sleep(1)

        
    Line = ""
    while ser.inWaiting() > 0:
        Line = Line + ser.read()
    
    LineArray = Line.split()
    Line = time.strftime("%Y-%m-%d %H:%M:%S") + "," + ",".join(LineArray)
    print "CH4: {},{}LPM".format(time.strftime("%Y-%m-%d %H:%M:%S"), float(LineArray[4]))
    Output.write(Line + "\n")
