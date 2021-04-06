from Phidget22.Phidget import *
from Phidget22.Devices.VoltageInput import *
import time

def onSensorChange(self, sensorValue, sensorUnit):
    print("SensorValue: " + str(sensorValue))
    print("SensorUnit: " + str(sensorUnit.symbol))
    print("----------")
    
def onVoltageChange(self, voltage):
    print("Voltage: " + str(voltage))
    print("----------")

def main():
    #instance of VoltageInput() class
    voltageInput0 = VoltageInput()

    voltageInput0.setIsHubPortDevice(True)
    voltageInput0.setHubPort(0)

    voltageInput0.openWaitForAttachment(5000)

    #voltageInput0.setOnSensorChangeHandler(onSensorChange)
    voltageInput0.setOnVoltageChangeHandler(onVoltageChange)
    while True:
        voltage = voltageInput0.getVoltage()
        voltTemp = 7 - ((2.5 - voltage)/(0.257179+(0.000941468*43))) 
        print("Voltage: " + str(voltTemp))
        print("--------")
        time.sleep(1)

    #voltageInput0.setSensorType(VoltageSensorType.SENSOR_TYPE_1130_PH)
    voltageInput0.setSensorType(VoltageSensorType.SENSOR_TYPE_VOLTAGE)
    #Other valid sensor types for this sensor include: SENSOR_TYPE_1130_ORP

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    voltageInput0.close()

main()
