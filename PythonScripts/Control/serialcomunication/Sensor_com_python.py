import serial
import time
import datetime
import os
import csv

# change working directory to comp desktop
os.getcwd()
aPath = r'C:\Users\labuser\Desktop'
os.chdir(aPath)

ser = serial.Serial()   # define function
ser.baudrate = 9600
ser.port = 'COM3'
ser.timeout = 200
ser.open()
ser.is_open     # make sure com port is open
print('connected to: ' + ser.name)     # check which port was really used

ser.write(b'[EK3 ECM ENQ]')
Val_Pos = ser.readline()
res = int(Val_Pos,16)

print(Val_Pos)

with open("cleanCOM4.csv","a") as f:
    writer = csv.writer(f,delimiter=",")
    writer.writerow([time.ctime(),res])

#while True:
    #try:
        #ser_bytes = ser.readline()
        #print(ser_bytes)
        #with open("cleanCOM4.csv","a") as f:
            #writer = csv.writer(f,delimiter=",")
            #writer.writerow([time.time(),ser_bytes])
    #except:
        #print("Keyboard Interrupt")
        #break
