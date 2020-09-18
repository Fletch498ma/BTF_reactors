'''
Created on 10/03/2020

@author: Fletcher Gilbertson 
'''
# python_live_plot.py

import random
import numpy as np
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use('fivethirtyeight')

x_values = []
y_values = []

index = count()


def animate(i):
    data = pd.read_csv('C:\Program Files (x86)\Eclipse\Reactor Control\BTF_reactors\PythonScripts\DAQ\Collected\GasData.csv')
    x_values = np.arange(len(data['Time']))
    y_CH4 = data['CH4 (%v/v)']
    y_CO2 = data['CO2 (%v/v)']
    plt.cla()
    plt.plot(x_values,y_CH4,x_values,y_CO2)
    plt.xlabel('Time')
    plt.ylabel('CH4 and CO2 (%v/v)')
    plt.title('Live Data')
    #plt.gcf().autofmt_xdate()
    plt.tight_layout()

ani = FuncAnimation(plt.gcf(), animate, 5000)

plt.tight_layout()
plt.show()