'''
Created on 15/03/2020

@author: Fletcher Gilbertson 
'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ConfigurationFiles import configReactorFlow as Flow
from ConfigurationFiles import configReactorDim as Mater
from ConfigurationFiles import configReactorDim as Dimen
from cmath import pi
from numpy import amax


"""Slices the input data arrays according to given start and end dates. Function takes 4 pars: 2 strings correspdoning to the experiment start and end date and two column arrays containing  """
def dataRetreieve:

def startEnd(Day0,xIn,yIn,end=False):
    indx = 0
    if not end:
        end = len(xIn)
    for Inlet in xIn:
        indx += 1
        if Inlet == Day0:
            Start = indx
            xIn = xIn.iloc[Start:end]
            yIn = yIn.iloc[Start:end]
    return(xIn, yIn)

if __name__ == '__main__':
    OutletFileO2 = pd.read_csv('/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinalR1Outlet.csv')
    xOutO2_ = OutletFileO2['Date']
    yOutO2_ = OutletFileO2['O2 (%v/v)']
    Day0='2020-05-29'
    O2OutSplice =StartEnd(Day0,xOutO2_,yOutO2_,end='2020-05-31')
    print(O2OutSplice[0],O2OutSplice[1])