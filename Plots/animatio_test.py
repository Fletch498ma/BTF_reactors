'''
Created on 10/03/2020

@author: labuser
'''
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import threading
import random
import time

class MyDataClass():

    def __init__(self,start):
        
        self.XData = [0]
        self.YData = [start]


class MyPlotClass():

    def __init__(self, dataClass):

        self._dataClass = dataClass

        self.hLine, = plt.plot(0, 0)

        self.ani = FuncAnimation(plt.gcf(), self.run, interval = 1000, repeat=True)


    def run(self, i):  
        print("plotting data")
        self.hLine.set_data(self._dataClass.XData, self._dataClass.YData)
        self.hLine.axes.relim()
        self.hLine.axes.autoscale_view()


class MyDataFetchClass(threading.Thread):

    def __init__(self, dataClass):

        threading.Thread.__init__(self)

        self._dataClass = dataClass
        self._period = 0.25
        self._nextCall = time.time()

#    def initSensor(self):
#        pass
#    
    def run(self):
#        instances = self.initSensor()
#        time.sleep(2)
        while True:
            print("waiting for data...")
            # check data if data has been added
            if not self._dataClass.YData:
                break
            print("updating graph")
            # add data to data class
            self._dataClass.XData.append(self._dataClass.XData[-1] + 1)
            self._dataClass.YData.append(self._dataClass.YData)
            # sleep until next execution
            self._nextCall = self._nextCall + self._period;
            time.sleep(self._nextCall - time.time())

if __name__ == '__main__':
    data = MyDataClass()
    plotter = MyPlotClass(data)
    fetcher = MyDataFetchClass(data)

    fetcher.start()
    plt.show()
    #fetcher.join()
