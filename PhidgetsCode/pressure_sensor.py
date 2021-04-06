from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
import time
from SSRPhidget import main1

def onSensorChange(self, sensorValue, sensorUnit):
    print("SensorValue: " + str(sensorValue))
    print("SensorUnit: " + str(sensorUnit.symbol))
    print("----------")

def main():
    print(VoltageRatioSensorType.SENSOR_TYPE_1136)
    voltageRatioInput0 = VoltageRatioInput()

    voltageRatioInput0.setIsHubPortDevice(True)
    voltageRatioInput0.setDeviceSerialNumber(607325)
    voltageRatioInput0.setHubPort(1)
    voltageRatioInput0.setChannel(0)
    
    voltageRatioInput0.setOnSensorChangeHandler(onSensorChange)

    voltageRatioInput0.openWaitForAttachment(5000)
    voltageRatioInput0.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1136)
    
    VoltageRatioSensorType.SENSOR_TYPE_1136
    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    voltageRatioInput0.close()

main1()
main()