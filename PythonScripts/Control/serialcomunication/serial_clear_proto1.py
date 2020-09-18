import serial
import time
import datetime
import io

ser = serial.Serial()   # define function
ser.baudrate = 9600
ser.port = 'COM4'
bytesize=8
parity='N'
stopbits=1
timeout = 1
xonxoff=0
rtscts=0
ser.open()
time.sleep(0.1)
ser.is_open     # make sure com port is open
print(ser.name)     # check which port was really used

# ensuring the input and output buffers of the python interpreter/windows is clear
while ser.in_waiting != 0:
    ser.reset_input_buffer()
while ser.out_waiting != 0:
    ser.reset_output_buffer()

cmd_1 = ser.write(b'[EK2 SEN SET]\r\n')
while True:
    if ser.in_waiting == 14: # first if and elif checks to make sure the input buffer to device has the correct number of bytes for the command. If not it clears input buffer and re-runs the command
        pass
    elif ser.in_waiting != 14:
        ser.reset_input_buffer()
        cmd_1
        continue 
    if ser.out_waiting == 0:
        cov = str(ser.readline(),'utf-8')
        if cov.find('\r') != -1 and cov.find('\n') != -1:
            blah blah
        elif cov.find('\r') != -1 and cov.find('\n') != -1:
        cov.replace('\n','')
        cov.replace('\r','')
    elif ser.out_waiting == 0:
        cmd_1
        if cov != '[ACK]':
            ser.reset_input_buffer()
            ser.reset_output_buffer()
print(cov)

while ser.in_waiting != 0:
    ser.reset_input_buffer()
while ser.out_waiting != 0:
    ser.reset_output_buffer()

