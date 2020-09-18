import serial
import time
from find_comPort import serial_ports
from serial.tools import list_ports
## Note - in order to call clean() in a external program the COM port must be closed, otherwise when
# you try to call clean and the port is open clean will try to open a already open port and it will
# throw a 'Access denied error' ##

class clean:
    def __init__(self,port):
        self.port = port
            
    def cleanIR(self):
        ser = serial.Serial()   
        ser.baudrate = 9600
        ser.port = self.port
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
            ser.read(ser.in_waiting) #sometimes when you clear buffer first time it leaves a \r so 2nd time quarantees
            setup = ser.write(b'[EK2 SEN SET]')
            setreturn = str(ser.read(size=ser.in_waiting),'utf-8')
            if setreturn.find('NAK') > 0:
                time.sleep(1)
                continue
            ser.read(ser.in_waiting)
            time.sleep(1)
            if str(ser.read(ser.in_waiting),'utf-8') == '':
                print('cleared')
                break
        ser.read(ser.in_waiting)
        ser.close()
        
    def __str__(self):
        return str(self.port)

def main():
    cleaning = clean('com4')
    cleaning.cleanIR()
    cleaning.__str__()

if __name__ == '__main__':
    main()

