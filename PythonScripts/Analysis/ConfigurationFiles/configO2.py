'''
Created on 13/03/2020

@author: Fletcher Gilbertson
'''
import pandas as pd

cacheO2 = ['Reactor Stream','Date','Time','O2 (%v/v)']
dO2 = {'Reactor Stream':[],
                'Date':[],
                'Time':[],
                'O2 (%v/v)':[]}
dfO2 = pd.DataFrame(dO2,columns=['Reactor Stream','Date','Time','O2 (%v/v)'])