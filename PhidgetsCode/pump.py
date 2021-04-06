from Phidget22.Phidget import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.Devices.VoltageOutput import *
import time

#Note:
# all reactors need to run clockwise for proper inlet outlet of medium
# Duty = 0 is clockwise
# Duty = 1 is  counter clockwise
# Hub port for digital ouput = 2
# R4 Direction = Digital Channel 0
# R4 Speed + Start/stop = Voltage Output Channel 0
# R2 Direction = Digital Channel 1
# R2 Speed + Start/stop = Voltage Output Channel 1
# R3 Direction = Digital Channel 2
# R3 Speed + Start/stop = Voltage Output Channel 3

# 0.02 V is around 0.1-0.2

VoltOuput_1002_0B_SerialNumber = 589764
def main():
#    digitalOutput0 = DigitalOutput()
#    digitalOutput1 = DigitalOutput()
#    digitalOutput2 = DigitalOutput()
#    digitalOutput3 = DigitalOutput()

    voltageOutput0 = VoltageOutput()
    voltageOutput2 = VoltageOutput()
    voltageOutput3 = VoltageOutput()
    
#    digitalOutput0.setDeviceSerialNumber(611075)
#    digitalOutput0.setHubPort(2)
#    digitalOutput0.setChannel(3)
#    digitalOutput1.setDeviceSerialNumber(607325)
#    digitalOutput1.setHubPort(3)
#    digitalOutput1.setChannel(1)
#    digitalOutput2.setDeviceSerialNumber(607325)
#    digitalOutput2.setHubPort(2)
#    digitalOutput2.setChannel(2)
#    digitalOutput3.setDeviceSerialNumber(607325)
#    digitalOutput3.setHubPort(2)
#    digitalOutput3.setChannel(3)

    voltageOutput0.setChannel(0)
    voltageOutput2.setChannel(1)
    voltageOutput3.setChannel(3)
    
#    digitalOutput0.openWaitForAttachment(5000)
#    digitalOutput1.openWaitForAttachment(5000)
#    digitalOutput2.openWaitForAttachment(5000)
#    digitalOutput3.openWaitForAttachment(5000)
    
    voltageOutput0.openWaitForAttachment(5000)
    voltageOutput2.openWaitForAttachment(5000)
    voltageOutput3.openWaitForAttachment(5000)
    deviceSerialNumber = voltageOutput0.getDeviceSerialNumber()
    print("Device Serial Number: " + str(deviceSerialNumber))
    #voltageOutput3.openWaitForAttachment(5000)
    
#    for i in range(5):
#        digitalOutput0.setDutyCycle(0)
#        time.sleep(2)
#        digitalOutput0.setDutyCycle(1)
#    digitalOutput1.setDutyCycle(1) #pump direction reactors 1 and 2: pump direction should be CC for R1+R2 which is state=1
#    digitalOutput2.setDutyCycle(0)
#    digitalOutput3.setDutyCycle(1)

    def volt_setpoint(voltInst,setpt):
        volt_set = False
        
        while not volt_set:
            voltInst.setVoltage(setpt)
            time.sleep(3)
            voltage = voltInst.getVoltage()
            print("Voltage: " + str(voltage))
            if voltage == setpt:
                volt_set = True
            else:
                print("Voltage setpoint not acheived...retrying now")
    
    voltsR2 = 0.02
    voltsR3 = 0.02
    voltsR4 = 0.02
    
#    print("R2")
#    volt_setpoint(voltageOutput2,voltsR2)
    print("R3")
    volt_setpoint(voltageOutput3,voltsR3)
    print("R4")
    volt_setpoint(voltageOutput0,voltsR4)
    
    try:
        input("\nPress Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

#    digitalOutput0.close()
#    digitalOutput1.close()
#    digitalOutput2.close()
#    digitalOutput3.close()

    voltageOutput0.close()
    voltageOutput3.close()
main()