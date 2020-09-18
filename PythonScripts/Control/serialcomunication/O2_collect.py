'''
Created on 13/03/2020

@author: Fletcher Gilbertson
'''
from O2_dataCollect import O2_dataCollect
import csv_appending
from csv_appending import append_list_as_row
from  PythonScripts.Analysis.ConfigurationFiles import configO2
import statistics
from statistics import mean, stdev
import datetime
from datetime import date 

valvTime = 333000
for i in range(0,valvTime):
    O2_dataCollect()
    if configO2.dfO2.iloc[0,0] != configO2.dfO2.iloc[len(configO2.dfO2)-1,0]:
        RecStream = configO2.dfO2.iloc[len(configO2.dfO2)-2,0]
        Date = datetime.date.today()
        Time = datetime.datetime.now().time()
        start = int(len(configO2.dfO2)/2)
        end = len(configO2.dfO2)
        avg = configO2.dfO2['O2 (%v/v)']
        avgO2 = round(mean(avg[start:end]),4)
        std = configO2.dfO2['O2 (%v/v)']
        stdO2 = round(stdev(std[start:end]),4)
        cache = [RecStream,Date,Time,avgO2,stdO2]
        myFile = '/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2DataFinal'+RecStream+'.csv'
        append_list_as_row(myFile,cache)
        print(cache)
        configO2.dfO2.drop(configO2.dfO2.index,inplace=True)
        
