
#from randShortPath import randShortPath as rSP
import numpy as np
import gdal, ogr, os, osr
import random
        
import psycopg2
import math

import matplotlib.pyplot as plt

import time

import re

r=2

r_rand = r 

startHABITATS_HQ = np.array([0.25,1.0]) # habitat-quality of startHABITATS
startHABITATS_IndNR = np.array([10,10]) # number of individuals in startHABITATS
       
numTL3 = np.zeros(25)
numTL4 = np.zeros(25)



for x in range(25):

    numTL3[x] = startHABITATS_IndNR[0]
    numTL4[x] = startHABITATS_IndNR[1]
    
    startHABITATS_IndNR = startHABITATS_IndNR+r_rand*startHABITATS_IndNR*(1-startHABITATS_IndNR/(startHABITATS_HQ*100))
    print(startHABITATS_IndNR)

plt.plot(range(25),numTL3, color = 'Aqua', label='VLG - r = 2 & K = 25')
plt.plot(range(25),numTL4, color = 'Aquamarine', label='VLG - r = 2 & K = 100')

startHABITATS_HQ = np.array([0.25,1.0]) # habitat-quality of startHABITATS
startHABITATS_IndNR = np.array([10,10]) # number of individuals in startHABITATS
       
numTL3 = np.zeros(25)
numTL4 = np.zeros(25)

theta=1
r=2.0

for x in range(25):
    
    numTL3[x] = startHABITATS_IndNR[0]
    numTL4[x] = startHABITATS_IndNR[1]
    
    C = ((startHABITATS_HQ*100) * np.sqrt(startHABITATS_IndNR) - startHABITATS_IndNR * np.sqrt(startHABITATS_HQ*100)) / ((startHABITATS_HQ*100) * startHABITATS_IndNR)
    
    startHABITATS_IndNR = (startHABITATS_HQ*100) / (1 + np.exp(-theta * r_rand) * C * np.sqrt(startHABITATS_HQ*100))**2
    print(startHABITATS_IndNR)

plt.plot(range(25),numTL3, 'DarkMagenta', label='TLG - r = 2 & K = 25 & t = 1')
plt.plot(range(25),numTL4, 'DarkOrchid', label='TLG - r = 2 & K = 100 & t = 1')

startHABITATS_HQ = np.array([0.25,1.0]) # habitat-quality of startHABITATS
startHABITATS_IndNR = np.array([10,10]) # number of individuals in startHABITATS
       
numTL3 = np.zeros(25)
numTL4 = np.zeros(25)

theta=0.5
r=2.0

for x in range(25):
    
    numTL3[x] = startHABITATS_IndNR[0]
    numTL4[x] = startHABITATS_IndNR[1]
    
    C = ((startHABITATS_HQ*100) * np.sqrt(startHABITATS_IndNR) - startHABITATS_IndNR * np.sqrt(startHABITATS_HQ*100)) / ((startHABITATS_HQ*100) * startHABITATS_IndNR)
    
    startHABITATS_IndNR = (startHABITATS_HQ*100) / (1 + np.exp(-theta * r_rand) * C * np.sqrt(startHABITATS_HQ*100))**2
    print(startHABITATS_IndNR)

plt.plot(range(25),numTL3, 'DodgerBlue', label='TLG - r = 2 & K = 25 & t = .5')
plt.plot(range(25),numTL4, 'DeepSkyBlue', label='TLG - r = 2 & K = 100 & t = .5')

plt.legend()
plt.xlabel('Year')
plt.ylabel('Number')
plt.grid(True)
plt.show()



