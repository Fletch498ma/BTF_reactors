#from Phidget22.Phidget import *
#from Phidget22.Devices.DigitalOutput import *
#import time
#
#def main():
#    digitalOutput0 = DigitalOutput()
#    digitalOutput0.setHubPort(0)
#    digitalOutput0.setDeviceSerialNumber(611075)
#    digitalOutput0.setChannel(0)
#    
#    digitalOutput1 = DigitalOutput()
#    digitalOutput1.setHubPort(0)
#    digitalOutput1.setDeviceSerialNumber(611075)
#    digitalOutput1.setChannel(1)
#    
#    digitalOutput2 = DigitalOutput()
#    digitalOutput2.setHubPort(0)
#    digitalOutput2.setDeviceSerialNumber(611075)
#    digitalOutput2.setChannel(2)
#    
#    digitalOutput3 = DigitalOutput()
#    digitalOutput3.setHubPort(0)
#    digitalOutput3.setDeviceSerialNumber(611075)
#    digitalOutput3.setChannel(3)
#    
#    digitalOutput4 = DigitalOutput()
#    digitalOutput4.setHubPort(0)
#    digitalOutput4.setDeviceSerialNumber(611075)
#    digitalOutput4.setChannel(4)
#    
#    digitalOutput5 = DigitalOutput()
#    digitalOutput5.setHubPort(0)
#    digitalOutput5.setDeviceSerialNumber(611075)
#    digitalOutput5.setChannel(5)
#    
#    digitalOutput6 = DigitalOutput()
#    digitalOutput6.setHubPort(0)
#    digitalOutput6.setDeviceSerialNumber(611075)
#    digitalOutput6.setChannel(6)
#    
#    digitalOutput7 = DigitalOutput()
#    digitalOutput7.setHubPort(0)
#    digitalOutput7.setDeviceSerialNumber(611075)
#    digitalOutput7.setChannel(7)
#    
#    digitalOutput0.openWaitForAttachment(5000)
#    digitalOutput1.openWaitForAttachment(5000)
#    digitalOutput2.openWaitForAttachment(5000)
#    digitalOutput3.openWaitForAttachment(5000)
#    digitalOutput4.openWaitForAttachment(5000)
#    digitalOutput5.openWaitForAttachment(5000)
#    digitalOutput6.openWaitForAttachment(5000)
#    digitalOutput7.openWaitForAttachment(5000)
#
#    digitalOutput0.setDutyCycle(1)
#    digitalOutput1.setDutyCycle(1)
#    digitalOutput2.setDutyCycle(1)
#    digitalOutput3.setDutyCycle(1)
#    digitalOutput4.setDutyCycle(1)
#    digitalOutput5.setDutyCycle(1)
#    digitalOutput6.setDutyCycle(1)
#    digitalOutput7.setDutyCycle(1)
#
#    try:
#        input("Press Enter to Stop\n")
#    except (Exception, KeyboardInterrupt):
#        pass
#
#    digitalOutput0.close()
#
#main()

from Phidget22.Phidget import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.HumiditySensor import *
import time

def onHumiditySensor0_HumidityChange(self, humidity):
    print("Humidity: " + str(humidity))

def onHumiditySensor0_Attach(self):
    print("Attach!")

def onHumiditySensor0_Detach(self):
    print("Detach!")
    
def onSensorChange(self, sensorValue, sensorUnit):
    print("SensorValue: " + str(sensorValue))
    print("SensorUnit: " + str(sensorUnit.symbol))
    print("----------")
    
def main1():
    digitalOutput0 = DigitalOutput()
    digitalOutput0.setHubPort(0)
    digitalOutput0.setDeviceSerialNumber(607325)
    digitalOutput0.setChannel(4)#12
    #Create your Phidget channels
#    humiditySensor0 = HumiditySensor()
#    voltageRatioInput0 = VoltageRatioInput()
#
#    voltageRatioInput0.setIsHubPortDevice(True)
#    voltageRatioInput0.setDeviceSerialNumber(611075)
#    voltageRatioInput0.setHubPort(1)
#
#    voltageRatioInput0.setOnSensorChangeHandler(onSensorChange)
#
#    voltageRatioInput0.openWaitForAttachment(5000)
#
#    voltageRatioInput0.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1136)
#    digitalOutput2 = DigitalOutput()
#    digitalOutput2.setHubPort(0)
#    digitalOutput2.setDeviceSerialNumber(607325)
#    digitalOutput2.setChannel(12)#6
    digitalOutput3 = DigitalOutput()
    digitalOutput3.setHubPort(0)
    digitalOutput3.setDeviceSerialNumber(607325)
    digitalOutput3.setChannel(0)#0

    #Assign any event handlers you need before calling open so that no events are missed.
#    humiditySensor0.setOnHumidityChangeHandler(onHumiditySensor0_HumidityChange)
#    humiditySensor0.setOnAttachHandler(onHumiditySensor0_Attach)
#    humiditySensor0.setOnDetachHandler(onHumiditySensor0_Detach)
    
    digitalOutput0.openWaitForAttachment(5000)
    #digitalOutput2.openWaitForAttachment(5000)
    digitalOutput3.openWaitForAttachment(5000)
    #humiditySensor0.openWaitForAttachment(5000)
    
    digitalOutput0.setDutyCycle(1)
    #digitalOutput2.setDutyCycle(1)
    digitalOutput3.setDutyCycle(1)

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    digitalOutput0.close()
    #digitalOutput2.close()
    digitalOutput3.close()

main1()
#trying = True
#while trying:
#    try:
#        main()
#        trying == False
#    except:
#        pass
