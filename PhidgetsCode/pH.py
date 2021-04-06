#local imports
#from animatio_test import*

#phidget imports
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.TemperatureSensor import *
from Phidget22.Devices.VoltageRatioInput import *
import time

#parameters for VINT
VINT_num = 611075

def onTemperatureChange(self, temperature):
    print("Temperature: " + str(temperature))
    time.sleep(1)
    
def onSensorChange(self, sensorValue, sensorUnit):
    print("SensorValue: " + str(sensorValue))
    print("SensorUnit: " + str(sensorUnit.symbol))
    print("----------")
    time.sleep(1)

def initTempSensors():
    temperatureSensorR1 = TemperatureSensor()
    temperatureSensorR2 = TemperatureSensor()
    temperatureSensorR3 = TemperatureSensor()
    temperatureSensorR4 = TemperatureSensor()
    
    temperatureSensorR1.setDeviceSerialNumber(VINT_num)#607325
    temperatureSensorR2.setDeviceSerialNumber(VINT_num)
    temperatureSensorR3.setDeviceSerialNumber(VINT_num)
    temperatureSensorR4.setDeviceSerialNumber(VINT_num)
    
    temperatureSensorR1.setHubPort(1)
    temperatureSensorR2.setHubPort(1)
    temperatureSensorR3.setHubPort(1)
    temperatureSensorR4.setHubPort(1)
    
    temperatureSensorR1.setChannel(0)
    temperatureSensorR2.setChannel(1)
    temperatureSensorR3.setChannel(2)
    temperatureSensorR4.setChannel(3)
    
    temperatureSensorR1.openWaitForAttachment(10000)
    temperatureSensorR2.openWaitForAttachment(10000)
    temperatureSensorR3.openWaitForAttachment(10000)
    temperatureSensorR4.openWaitForAttachment(10000)
    
    return temperatureSensorR1,temperatureSensorR2,temperatureSensorR3,temperatureSensorR4
    
def initpHSensors():
    voltageInputR1 = VoltageInput()
    voltageInputR2 = VoltageInput()
    voltageInputR3 = VoltageInput()
    voltageInputR4 = VoltageInput()
    
    voltageInputR1.setDeviceSerialNumber(VINT_num)
    voltageInputR2.setDeviceSerialNumber(VINT_num)
    voltageInputR3.setDeviceSerialNumber(VINT_num)
    voltageInputR4.setDeviceSerialNumber(VINT_num) 
    
    voltageInputR1.setHubPort(0)
    voltageInputR2.setHubPort(0)
    voltageInputR3.setHubPort(0)
    voltageInputR4.setHubPort(0)
    
    voltageInputR1.setChannel(0)
    voltageInputR2.setChannel(1)
    voltageInputR3.setChannel(2)
    voltageInputR4.setChannel(3)

#    voltageInput0.setOnSensorChangeHandler(onSensorChange)
#    temperatureSensor0.setOnTemperatureChangeHandler(onTemperatureChange)

    voltageInputR1.openWaitForAttachment(10000)
    voltageInputR2.openWaitForAttachment(10000)
    voltageInputR3.openWaitForAttachment(10000)
    voltageInputR4.openWaitForAttachment(10000)
    
    return voltageInputR1,voltageInputR2,voltageInputR3,voltageInputR4
#    voltageInputR1.setSensorType(VoltageSensorType.SENSOR_TYPE_1130_PH)
#    temperatureSensorR1.setThermocoupleType(ThermocoupleType.THERMOCOUPLE_TYPE_K)

def initPressureSensors():
    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput1 = VoltageRatioInput()
    voltageRatioInput2 = VoltageRatioInput()
    voltageRatioInput3 = VoltageRatioInput()
    
    voltageRatioInput0.setDeviceSerialNumber(VINT_num)
    voltageRatioInput1.setDeviceSerialNumber(VINT_num)
    voltageRatioInput2.setDeviceSerialNumber(VINT_num)
    voltageRatioInput3.setDeviceSerialNumber(VINT_num)
    
    voltageRatioInput0.setHubPort(0)
    voltageRatioInput1.setHubPort(0)
    voltageRatioInput2.setHubPort(0)
    voltageRatioInput3.setHubPort(0)
    
    voltageRatioInput0.setChannel(7)
    voltageRatioInput1.setChannel(6)
    voltageRatioInput2.setChannel(5)
    voltageRatioInput3.setChannel(4)

    #voltageRatioInput0.setOnSensorChangeHandler(onSensorChange)

    voltageRatioInput0.openWaitForAttachment(5000)
    voltageRatioInput1.openWaitForAttachment(5000)
    voltageRatioInput2.openWaitForAttachment(5000)
    voltageRatioInput3.openWaitForAttachment(5000)
    
    voltageRatioInput0.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1136)
    voltageRatioInput1.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1136)
    voltageRatioInput2.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1136)
    voltageRatioInput3.setSensorType(VoltageRatioSensorType.SENSOR_TYPE_1136)
        
    return voltageRatioInput0,voltageRatioInput1,voltageRatioInput2,voltageRatioInput3

def stopTempSensors(t1,t2,t3,t4):
    t1.close()
    t2.close()
    t3.close()
    t4.close()
    
def stoppHSensors(v1,v2,v3,v4):
    v1.close()
    v2.close()
    v3.close()
    v4.close()

def stopPressureSensors(p1,p2,p3,p4):
    p1.close()
    p2.close()
    p3.close()
    p4.close()
    
def getReading(v1,v2,v3,v4,t1,t2,t3,t4,p1,p2,p3,p4):
    voltageR1 = v1.getVoltage()
    voltageR2 = v2.getVoltage()
    voltageR3 = v3.getVoltage()
    voltageR4 = v4.getVoltage()
    
    temperatureR1 = t1.getTemperature()
    temperatureR2 = t2.getTemperature()
    temperatureR3 = t3.getTemperature()
    temperatureR4 = t4.getTemperature()
    
    pressureR1 = p1.getVoltageRatio()
    pressureR2 = p2.getVoltageRatio()
    pressureR3 = p3.getVoltageRatio()
    pressureR4 = p4.getVoltageRatio()

    pH_R1 = 7 - ((2.5 - voltageR1)/(0.257179+(0.000941468*45)))
    pH_R2 = 7 - ((2.5 - voltageR2)/(0.257179+(0.000941468*temperatureR2)))
    pH_R3 = 7 - ((2.5 - voltageR3)/(0.257179+(0.000941468*temperatureR3)))
    pH_R4 = 7 - ((2.5 - voltageR4)/(0.257179+(0.000941468*temperatureR4)))
    
    print("----------------------------------------------------------------")
    print("            Reactor 1    Reactor 2    Reactor 3    Reactor 4    ")
    print("----------------------------------------------------------------")
    print("pH            |" + str(round(pH_R1,3)) + "        " + str(round(pH_R2,3)) + "        " + str(round(pH_R3,3)) + "        " + str(round(pH_R4,3)) + "        ")
    print("Temperature(C)|" + str(temperatureR1) +  "        " + str(temperatureR2) +   "        " + str(temperatureR3) + "        " + str(temperatureR4) +  "        ")
    print("Pressure(kPa) |" + str(pressureR1) +     "        " + str(pressureR2) +      "        " + str(pressureR3) +    "        " + str(pressureR4) +     "        ")
    print("----------------------------------------------------------------\n")

    return pH_R1,pH_R2,pH_R3,pH_R4,temperatureR1,temperatureR2,temperatureR3,temperatureR4,voltageR1,voltageR2,voltageR3,voltageR4,pressureR1,pressureR2,pressureR3,pressureR4
    
if __name__ == '__main__':
    startTemp = initTempSensors()
    T1 = startTemp[0]
    T2 = startTemp[1]
    T3 = startTemp[2]
    T4 = startTemp[3]
    startpH = initpHSensors()
    pH1 = startpH[0]
    pH2 = startpH[1]
    pH3 = startpH[2]
    pH4 = startpH[3]
    startPressure = initPressureSensors()
    P1 = startPressure[0]
    P2 = startPressure[1]
    P3 = startPressure[2]
    P4 = startPressure[3]
    
    while True:
        try:
            data = getReading(pH1,pH2,pH3,pH4,T1,T2,T3,T4,P1,P2,P3,P4)
        except (Exception, KeyboardInterrupt, SystemExit):
            stopTempSensors(T1,T2,T3,T4)
            stoppHSensors(pH1,pH2,pH3,pH4)
            stopPressureSensors(P1,P2,P3,P4)
        
        time.sleep(1)
        

#from Phidget22.PhidgetException import *
#from Phidget22.Phidget import *
#from Phidget22.Devices.Log import *
#from Phidget22.LogLevel import *
#from Phidget22.Devices.VoltageInput import *
#import traceback
#import time
#
##Declare any event handlers here. These will be called every time the associated event occurs.
#
#def onVoltageInput0_VoltageChange(self, voltage):
#    print("Voltage: " + str(voltage))
#
#def onVoltageInput0_Attach(self):
#    print("Attach!")
#
#def onVoltageInput0_Detach(self):
#    print("Detach!")
#
#def onVoltageInput0_Error(self, code, description):
#    print("Code: " + ErrorEventCode.getName(code))
#    print("Description: " + str(description))
#    print("----------")
#
#def main():
#    try:
#        Log.enable(LogLevel.PHIDGET_LOG_INFO, "phidgetlog.log")
#        #Create your Phidget channels
#        voltageInput0 = VoltageInput()
#
#        #Set addressing parameters to specify which channel to open (if any)
#        voltageInput0.setHubPort(0)
#        voltageInput0.setDeviceSerialNumber(607325)
#        voltageInput0.setChannel(0)
#
#        #Assign any event handlers you need before calling open so that no events are missed.
#        voltageInput0.setOnVoltageChangeHandler(onVoltageInput0_VoltageChange)
#        voltageInput0.setOnAttachHandler(onVoltageInput0_Attach)
#        voltageInput0.setOnDetachHandler(onVoltageInput0_Detach)
#        voltageInput0.setOnErrorHandler(onVoltageInput0_Error)
#
#        #Open your Phidgets and wait for attachment
#        voltageInput0.openWaitForAttachment(5000)
#
#        #Do stuff with your Phidgets here or in your event handlers.
#
#        try:
#            input("Press Enter to Stop\n")
#        except (Exception, KeyboardInterrupt):
#            pass
#
#        #Close your Phidgets once the program is done.
#        voltageInput0.close()
#
#    except PhidgetException as ex:
#        #We will catch Phidget Exceptions here, and print the error informaiton.
#        traceback.print_exc()
#        print("")
#        print("PhidgetException " + str(ex.code) + " (" + ex.description + "): " + ex.details)
#
#
#main()