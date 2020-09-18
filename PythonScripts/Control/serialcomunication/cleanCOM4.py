import serial
import time
from IRClean import cleanIR
from find_comPort import serial_ports
from serial.tools import list_ports_common

Port_List = serial_ports()
print(Port_List)

# ser = serial.Serial()   
# ser.baudrate = 9600
# ser.port = Port_List[0]

cleanIR('com4')
