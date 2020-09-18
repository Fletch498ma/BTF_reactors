import serial
import time
import datetime

ser = serial.Serial()   # define function
ser.baudrate = 9600
ser.port = 'COM4'
ser.open()
ser.is_open     # make sure com port is open
print(ser.name)     # check which port was really used
time.sleep(1)

ser.read(ser.in_waiting)
# clearing IR sensor buffer and switching to 'measurement' mode
while ser.in_waiting == 0:
    ser.read(ser.in_waiting)
    ser.write(b'[EK2 SEN MEA]')
    ser.readline()
    time.sleep(0.1)
##    setreturn = str(ser.read(size=ser.in_waiting),'utf-8')
##    if setreturn.find('ACK') > 0:
##        break

##chk = str(ser.read(size=ser.in_waiting),'utf-8')
##while chk.find('NAK') > 0:
##    chk = str(ser.read(size=ser.in_waiting),'utf-8')
##    ser.read(ser.in_waiting)

##nak = str(ser.read(size=ser.in_waiting),'utf-8')
##while ser.in_waiting:
##    if nak.find('NAK') > 0:
##        ser.read(ser.in_waiting)
##    if nak.find('ACK') > 0:
##        ser.read(ser.in_waiting)
##        nak = str(ser.read(size=ser.in_waiting),'utf-8')

ser.readline()    
for i in range(10):
    x = str(ser.readline(),'utf-8')
    if x.find('NAK') > 0:
        ser.readline()
    if x.find('ACK') > 0:
        ser.readline()
    CH4 = round((int(x[26:32])/1E6)*100,4)
    CO2 = round((int(x[34:40])/1E6)*100,4)
##    Temp = float(x[42:46])
##    BulbV = int(x[47:51],16)*DAC_Vrange/Hex_range
##    Ref = int(x[10:14],16)*DAC_Vrange/Hex_range
##    ChA = int(x[15:19],16)*DAC_Vrange/Hex_range
##    ChB = int(x[20:24],16)*DAC_Vrange/Hex_range
##    print(Ref,ChA,ChB,Temp)
    print(x,CH4,CO2)
