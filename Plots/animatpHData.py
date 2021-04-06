from animatio_test import *
from PhidgetsCode.pH import *

class pHAnimation(MyDataFetchClass):
    def __init__(self,dataClass):
        MyDataFetchClass.__init__(self,dataClass)
    
    def initSensor(self):
        startTemp = initTempSensors()
        self.T1 = startTemp[0]
        self.T2 = startTemp[1]
        self.T3 = startTemp[2]
        self.T4 = startTemp[3] 
        startpH = initpHSensors()
        self.pH1 = startpH[0]
        self.pH2 = startpH[1]
        self.pH3 = startpH[2]
        self.pH4 = startpH[3]

    def run(self):
        self.initSensor()
        while True:
            data = getReading(self.pH1,self.pH2,self.pH3,self.pH4,self.T1,self.T2,self.T3,self.T4)
            print(data)
            print("updating data")
            # add data to data class
            self._dataClass.XData.append(self._dataClass.XData[-1] + 1)
            self._dataClass.YData.append(data[11])
            # sleep until next execution
            self._nextCall = self._nextCall + self._period;
            time.sleep(1)
            #time.sleep(self._nextCall - time.time())

if __name__ == '__main__':
    data = MyDataClass(3.15)
    plotter = MyPlotClass(data)
    fetcher = pHAnimation(data)

    fetcher.start()
    plt.show()
    #fetcher.join()

