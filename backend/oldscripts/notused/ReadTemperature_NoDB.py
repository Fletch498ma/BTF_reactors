import serial
import time

Line = time.strftime("%Y%m%d%H%M%S") + 'Temperature.csv';
ser = serial.Serial('COM10', 9600, timeout=None);
Output = open(Line, 'a');
Output.write("TempTime,AmbientT,HoodT,HoodState\n");
while 1:
    Line = ser.readline();
    Line = Line.strip();
    
    LineArray = Line.split(",")
    Line = time.strftime("%Y-%m-%d %H:%M:%S") + "," + ",".join(LineArray)
    print Line
    Output.write(Line + "\n")