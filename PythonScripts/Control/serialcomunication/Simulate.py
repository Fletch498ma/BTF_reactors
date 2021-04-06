import serial
import time
from time import sleep

ser = serial.Serial()
ser.port ='/dev/ttyUSB0'
ser.open()
time.sleep(1)
print(ser.is_open)

def setup(ser):
    ser.read(ser.in_waiting)
    ser.write(b'[EK2 SEN SET]')
    sleep(0.1)
    ser.read(ser.in_waiting)

def measure(ser):
    ser.read(ser.in_waiting)
    ser.write(b'[EK2 SEN MEA]')
    sleep(0.1)
    ser.read(ser.in_waiting)

def zero(ser):
    ser.read(ser.in_waiting)
    
    ser.write(b'[EK2 CAA ZERO ENQ]')
    sleep(0.1)
    zeroA = ser.read(ser.in_waiting)
    
    ser.write(b'[EK2 CAB ZERO ENQ]')
    sleep(0.1)
    zeroB = ser.read(ser.in_waiting)
    
    print(zeroA)
    print(zeroB)
    
def span(ser):
    ser.read(ser.in_waiting)
    
    ser.write(b'[EK2 CAA SPAN ENQ]')
    sleep(0.1)
    spanA = ser.read(ser.in_waiting)
    
    ser.write(b'[EK2 CAB SPAN ENQ]')
    sleep(0.1)
    spanB = ser.read(ser.in_waiting)
    
    print(spanA)
    print(spanB)
    
def calbTA(ser):
    ser.read(ser.in_waiting)
    
    ser.write(b'[EK2 CAA ENQ]')
    sleep(0.1)
    TableA = ser.read(ser.in_waiting)
    
    print(TableA)

def mediumCR(ser):
    ser.read(ser.in_waiting)
    
    ser.write(b'[EK2 CAA RMI]')
    sleep(0.1)
    print(ser.read(ser.in_waiting))
    
def setSCG(ser):
    ser.read(ser.in_waiting)
    
    ser.write(b'[EK2 CAA SCG 0040000]')
    sleep(0.1)
    print(ser.read(ser.in_waiting))
    
setup(ser)
zero(ser)
span(ser)
mediumCR(ser)
#setSCG(ser)
#calbTA(ser)

measure(ser)
for i in range(10):
    print(ser.read(ser.in_waiting))
    sleep(1)