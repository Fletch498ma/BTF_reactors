import serial
import time
import datetime

ser = serial.Serial()   # define function
ser.baudrate = 9600
ser.port = 'COM4'
timeout = 0
ser.open()
ser.is_open     # make sure com port is open
print(ser.name)     # check which port was really used

# getting sensor serial number and firmware version
ser.reset_input_buffer()
ser.write(b'[WHO]')
res = ser.readline()
print(res)

# measure current ouput 
ser.reset_input_buffer()
ser.write(b'[EK3 ECM ENQ]')


# function for reading data every second from open serial port 
class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

rc = ReadLine(ser)
res = rc.readline()
clc = res[26:34]
cov = int(clc, 16)
while True:

    print(cov)

