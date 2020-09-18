import serial
import time

ser = serial.Serial('COM3', 9600, timeout=None);
Output = open(time.strftime("%Y%m%d %H%M%S") + 'API200A.csv', 'a');
Output.write("APITime,NO,NO2,NOx\n");

Compounds = ['NO', 'NO2', 'NOX']
Results = []
while 1:
    ser.write("\x03\n")
    
    for Compound in Compounds:
        ser.write("T {}\n".format(Compound))
        Line = ser.readline()
        LineArray = Line.split()
        LineArray = LineArray[3].split('=')
        Results.append(LineArray[1])
        
        
    print "API:{},{},{},{}".format(time.strftime("%Y-%m-%d %H:%M:%S"),Results[0],Results[1], Results[2])
    Output.write( "{},{},{},{}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),Results[0],Results[1], Results[2]))
    Results = []
    time.sleep(1)
