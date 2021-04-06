from controlDevices import GilsonMinipuls
from threading import Event
from time import sleep

e = Event()

commConfig = {'port':'/dev/ttyUSB4','baudrate':19200,'timeout':10,'bytesize':7,'parity':'E','stopbits':1}
rowType = (('test',str),('dummy',str))

test = GilsonMinipuls(commConfig=commConfig,sensorName='test',GilsonCache=None,threadName='test',
                      eventType='test_event',event=e,rowType=rowType,rateSec=1,avg=10,timer=None,db=None,log=None)

test._connect()
sleep(3)
test._reset()
sleep(5)
test.setSpeed(25)
sleep(3)
test.start()
test._disconnect()

def flow():
    result = test.getFlow()
    print(result)
    return result

#while True:
#    for i in range(10):
#        test._connect()
#        sleep(3)
#        test.stop()
#        sleep(3)
#        test._reset()
#        #test.stop()
#        sleep(5)
#        test.setSpeed(i+5)
#        sleep(3)
#        #flow()
#        test.backward()
#        sleep(3)
#        test.start()
#        sleep(3)
#        test._disconnect()
#flow()
#test.start()
#value=flow()
#print(len(value),type(value),repr(value))

#test.setSpeed(60)


