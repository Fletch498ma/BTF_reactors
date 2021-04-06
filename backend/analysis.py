from statistics import *
import numpy as np

class Analysis(object):
    """class that takes data frame as input"""
    
    def __init__(self,dataFrame,column):
        #TODO: create iterator that goes through the data and analyzes it instead of just selecting last half of gas sampling and assuming stable 
        self.data = dataFrame.loc[(int(len(dataFrame)*0.6)):(int(len(dataFrame)*0.9)),column]
    
    def basicStats(self):
        aveSingle = mean(self.data)
        stdSingle = stdev(self.data)
        return [aveSingle, stdSingle]
    
    