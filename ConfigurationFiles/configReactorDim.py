'''
Created on 16/03/2020

@author: Fletcher Gilbertson
'''
import pandas as pd

# Configuration file which contains the biotrickling reactor dimensions and material.
# I will include the fundumental parameters, such as packing material and dimensions but all calculatable parameters such as empty bed volume, etc... will be calculated in scripts 
dmat = {'Date':['16/03/2020','10/06/2020'],
        'Material':['Glass Beads','Pumice Rock'],
        'Packing dimension':['Sphere','Nonuniform'],
        'Diameter (mm)':[4,4],
        'Volume (mm3)':[33.51,33.51],
        'Weight (g)':[0.158,0.2],
        'Porosity':[0,0.5]}
        
dfMater= pd.DataFrame(dmat,columns=['Date','Material','Packing dimension','Diameter (mm)','Volume (mm3)','Weight (g)','Porosity'])
# Note: sphere equation is 4/3*pi*r^3
#       glass bead weight was calculated by weighing multiple glass beads and counting number of beads and dividing by number of beads, the resulting g per bead was averaged between 3 trials at different number of beads, procedure below
#       10 beads = 1.6 g , 0.16 g / bead
#       8 beads = 1.3 g , 0.1625 g / bead
#       6 beads = 0.9 g , 0.15 g / bead
#       Average = 0.1575 g / bead

# Reactor dimensions

dDim = {'Parameter':['Bed height (mm)','Reactor diameter (mm)','Packing bone dry weight (g)'],
        'R1':[220,56,700],
        'R2':[210,56,683.2],
        'R3':[205,56,708.2],
        'R4':[220,56,724.9]}
        
dfBedDim = pd.DataFrame(dDim,columns=['Parameter','R1','R2','R3','R4'])

#print(dfBedDim.iloc[1,2])
#print(dfBedDim.iloc[0,1])                         
# **IMPORTANT**
# I forgot to measure the weight of the glass beads in R1 before starting so make sure to clean beads, dry and weight at end of experiment 
# Packing bone dry weight above for R1 is an estimate based on the weights of the other reactor bed packings