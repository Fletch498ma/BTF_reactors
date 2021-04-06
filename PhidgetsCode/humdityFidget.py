from Phidget22.Phidget import *
from Phidget22.Devices.HumiditySensor import *
import time

#Declare any event handlers here. These will be called every time the associated event occurs.

def onHumiditySensor0_HumidityChange(self, humidity):
    print("Humidity: " + str(humidity))

def onHumiditySensor0_Attach(self):
    print("Attach!")

def onHumiditySensor0_Detach(self):
    print("Detach!")

def main():
    #Create your Phidget channels
    humiditySensor0 = HumiditySensor()

    #Set addressing parameters to specify which channel to open (if any)

    #Assign any event handlers you need before calling open so that no events are missed.
    humiditySensor0.setOnHumidityChangeHandler(onHumiditySensor0_HumidityChange)
    humiditySensor0.setOnAttachHandler(onHumiditySensor0_Attach)
    humiditySensor0.setOnDetachHandler(onHumiditySensor0_Detach)

    #Open your Phidgets and wait for attachment
    humiditySensor0.openWaitForAttachment(5000)

    #Do stuff with your Phidgets here or in your event handlers.

    try:
        input("Press Enter to Stop\n")
    except (Exception, KeyboardInterrupt):
        pass

    #Close your Phidgets once the program is done.
    humiditySensor0.close()

main()