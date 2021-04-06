from Phidget22.Phidget import *
from Phidget22.Devices.PHSensor import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.TemperatureSensor import *
import time

def onPHChange(self, PH):
    print("pH: " + str(PH))
    
def onVoltageChange(self, voltage):
    print("Calculated pH: " + str(voltage))
    
def onTemperatureChange(self, temperature):
    print("Temperature: " + str(temperature))
    
    return temperature

def main():
    phSensor0 = PHSensor()
    temperatureSensor0 = TemperatureSensor()
    voltageInput0 = VoltageInput()
    
    phSensor0.setHubPort(3)
    voltageInput0.setHubPort(3)
    temperatureSensor0.setHubPort(1)
    
    phSensor0.setDeviceSerialNumber(611075)
    voltageInput0.setDeviceSerialNumber(611075)
    temperatureSensor0.setDeviceSerialNumber(611075)
    
    temperatureSensor0.setChannel(3)

    phSensor0.setOnPHChangeHandler(onPHChange)
    temperature = temperatureSensor0.setOnTemperatureChangeHandler(onTemperatureChange)
    #voltageInput0.setOnVoltageChangeHandler(onVoltageChange)

    phSensor0.openWaitForAttachment(5000)
    temperatureSensor0.openWaitForAttachment(5000)
    #voltageInput0.openWaitForAttachment(5000)
    
    if temperature:
        phSensor0.setCorrectionTemperature(temperature)
    else:
        phSensor0.setCorrectionTemperature(43.5)

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    phSensor0.close()
    temperatureSensor0.close()
    #voltageInput0.close()

main()

