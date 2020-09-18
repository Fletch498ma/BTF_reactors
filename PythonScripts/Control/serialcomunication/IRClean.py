import serial
import time
from find_comPort import serial_ports
from serial.tools import list_ports
## Note - in order to call clean() in a external program the COM port must be closed, otherwise when
# you try to call clean and the port is open clean will try to open a already open port and it will
# throw a 'Access denied error' ##



def cleanIR(port):
    ser = serial.Serial()   
    ser.baudrate = 9600
    ser.port = port
    bytesize=8
    parity='N'
    stopbits=1
    timeout = 0
    xonxoff=0
    rtscts=0
    if ser.is_open == False:
        ser.open()
    time.sleep(2)

    # check if buffer cache has stored bytes and clear and switch into measurement mode
    while ser.in_waiting > 0:
        ser.read(ser.in_waiting)
        x = str(ser.readline(),'utf-8')
        if x.find('NAK') > 0:
            ser.readline()
            continue
        elif x.find('ACK') > 0:
            ser.readline()
            continue
        ser.write(b'[EK2 SEN SET]')
        setreturn = str(ser.read(size=ser.in_waiting),'utf-8')
        if setreturn.find('ACK') > 0:
            print(setreturn + ser.port + ' is in set-up')
        ser.read(ser.in_waiting)
        time.sleep(1)
        doubchk = str(ser.read(ser.in_waiting),'utf-8')
        if doubchk == '':
            print('cleared')
        else:
            time.sleep(0.1)
            continue
    ser.read(ser.in_waiting)
    ser.close()
    

