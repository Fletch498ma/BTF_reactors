import serial
import time

ser = serial.Serial()
ser.port ='COM4'
ser.open()
time.sleep(1)

ser.write(b'[EK2 SEN MEA]')
time.sleep(2)
print(ser.in_waiting)

execfile('Valve_for_loop.py')