'''
Created on 27 Feb 2017

@author: lucas
'''

import numpy as np
import math
import matplotlib.pyplot as plt
import time

from  osgeo import ogr, osr

driver = ogr.GetDriverByName('ESRI Shapefile')
shp = driver.Open(r'/home/lucas/ownCloud/STRESSOR/geoDATA_HH/shortestPATH_costs.shp') # path has to be customized 

layer = shp.GetLayer()

habitats_shortpath_red = []

x= 0

for i in range(layer.GetFeatureCount()):
    
    inFeature = layer.GetNextFeature()
    
    toINS = inFeature.GetField('start'), inFeature.GetField('aim'), inFeature.GetField('costs')
    habitats_shortpath_red.append(toINS)

start = time.time()

habitats_shortpath_red = np.array(habitats_shortpath_red).T

habitats_QUAL = np.random.random_sample((100,))  # creates ramdom HQs

habitats_QUAL[np.where(habitats_QUAL < 0.25)] = 0.25 # worst HQ set 0.25

#####

startHABITATS = np.random.choice(np.unique([habitats_shortpath_red[0], habitats_shortpath_red[1]]), 2).astype(int) # number of occupied habitats first run -> 2
    
print(startHABITATS)
    
startHABITATS_HQ = habitats_QUAL[startHABITATS-1] # quality of startHABITATS

occHABITATS = np.array([range(100+1)[1:], [-999] * 100, [-999] * 100, [0] * 100]) # 100: should be len(test_pts_shift)
            
occHABITATS[1][(startHABITATS-1).tolist()] = 0 # colonization step 
occHABITATS[2][(startHABITATS-1).tolist()] = 0 # origin (habitat number)
occHABITATS[3][(startHABITATS-1).tolist()] = (startHABITATS_HQ * 100).astype(int) # number of indivduals

timeSTEPS = 100 # number of colonization events

proB = (1 - (habitats_shortpath_red[2] / np.amax(habitats_shortpath_red[2])))**2 # function to calculate the probability of reaching new habitat
    
for x in range(timeSTEPS):
    
    startHABITATS = startHABITATS[np.where(occHABITATS[3][startHABITATS-1] >= 25)] # habitats less 25 individuals removed 
    
    startHABITATS_HQ = habitats_QUAL[startHABITATS-1]
    
    extPROB = np.random.choice(100,2) # random 2 of 100 habitats may extinct

    for xxxxx in range(len(extPROB)): # loop to determine extinction

        if extPROB[xxxxx] in startHABITATS:
                            
            ind = np.where(startHABITATS == extPROB[xxxxx])[0].tolist()  
                            
            yn = np.random.choice([1, 0], 1, p=[1-startHABITATS_HQ[ind][0], startHABITATS_HQ[ind][0]])[0]
            
            if yn == 1:
            
                startHABITATS = np.delete(startHABITATS, ind)
                
                occHABITATS[1][(extPROB[xxxxx]-1).tolist()] = -111
                occHABITATS[2][(extPROB[xxxxx]-1).tolist()] = -111
                occHABITATS[3][(extPROB[xxxxx]-1).tolist()] = 0
                
                #print('DEATH ' + str(extPROB[xxxxx]))
        
    for xx in range(len(startHABITATS)): # loop to determine colonization

        conHABITATS_ind = np.hstack(np.array([np.where(habitats_shortpath_red[0] == startHABITATS[xx])[0].tolist(), np.where(habitats_shortpath_red[1] == startHABITATS[xx])[0].tolist()]).flat).tolist()
    
        if len(conHABITATS_ind) > 3:
            
            conHABITATS_ind = np.unique(np.random.choice(conHABITATS_ind, 3, p = (max(habitats_shortpath_red[2][conHABITATS_ind])-habitats_shortpath_red[2][conHABITATS_ind]) /sum(max(habitats_shortpath_red[2][conHABITATS_ind])-habitats_shortpath_red[2][conHABITATS_ind])))

        for xxx in conHABITATS_ind:
            
            yn = np.random.choice([1, 0], 1, p=[proB[xxx], 1-proB[xxx]])[0]
        
            if yn == 1:
                
                if occHABITATS[0][habitats_shortpath_red[0][xxx]-1] != startHABITATS[xx]:
                    
                    if occHABITATS[1][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                    
                        occHABITATS[1][habitats_shortpath_red[0][xxx]-1] = x+1

                    occHABITATS[2][habitats_shortpath_red[0][xxx]-1] = startHABITATS[xx]
                                
                    if occHABITATS[3][habitats_shortpath_red[0][xxx]-1] < (habitats_QUAL[occHABITATS[0][habitats_shortpath_red[0][xxx]-1]-1]*100).astype(int):        
                                                                   
                        occHABITATS[3][habitats_shortpath_red[0][xxx]-1] = occHABITATS[3][habitats_shortpath_red[0][xxx]-1] + (startHABITATS_HQ[xx]*25).astype(int)

                    startHABITATS, ind = np.unique(np.append(startHABITATS,[occHABITATS[0][habitats_shortpath_red[0][xxx]-1]]), return_index=True)
                    startHABITATS = startHABITATS[np.argsort(ind)]
                    
                if occHABITATS[0][habitats_shortpath_red[1][xxx]-1] != startHABITATS[xx]:
                       
                    if occHABITATS[1][habitats_shortpath_red[1][xxx]-1] in (-111, -999):
                                                
                        occHABITATS[1][habitats_shortpath_red[1][xxx]-1] = x+1
    
                    occHABITATS[2][habitats_shortpath_red[1][xxx]-1] = startHABITATS[xx]
                    
                    if occHABITATS[3][habitats_shortpath_red[1][xxx]-1] < (habitats_QUAL[occHABITATS[0][habitats_shortpath_red[1][xxx]-1]-1]*100).astype(int):        
                        
                        occHABITATS[3][habitats_shortpath_red[1][xxx]-1] = occHABITATS[3][habitats_shortpath_red[1][xxx]-1] + (startHABITATS_HQ[xx]*25).astype(int)

                    startHABITATS, ind = np.unique(np.append(startHABITATS,[occHABITATS[0][habitats_shortpath_red[1][xxx]-1]]), return_index=True)
                    startHABITATS = startHABITATS[np.argsort(ind)]
            
print(occHABITATS) 
