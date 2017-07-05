'''
created on 2 feb 2017

@author: lucas
'''

#from randshortpath import randshortpath as rsp
import numpy as np
import gdal, ogr, os, osr
import random
        
import psycopg2
import math

import matplotlib.pyplot as plt

import time

import re

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

start = time.time()

cursor.execute("select st_extent(geom) from demo_dispersal_pts;")
habitats_extent = cursor.fetchall()
habitats_extent = re.findall(r"[\w']+", habitats_extent[0][0])[1:]
habitats_extent = [float(i) for i in habitats_extent]

cursor.execute("select id, st_astext(geom) from demo_dispersal_pts;")
xy_pts = cursor.fetchall()
xy_pts = [[i[0],re.findall(r"[\w']+",i[1])[1:]] for i in xy_pts]
xy_pts = [[i[0], float(i[1][0]), float(i[1][1])] for i in xy_pts]
xy_pts.sort()

cursor.execute("select start, aim, costs from habitats_shortpath_red;")
habitats_shortpath_red = cursor.fetchall()
habitats_shortpath_red = np.array(habitats_shortpath_red).T

habitats_QUAL = np.load('/home/lucas/PhD/STRESSOR/TEST_DATA/habitatsQuality.npy')
habitats_QUAL[np.where(habitats_QUAL < 0.25)] = 0.25 # min HQ set to 0.25

cursor.execute("create table testtab_07062017 (pts_id bigint);")

conn.commit()

for xxxx in range(100):
    
    print('run ' + str(xxxx))
        
    cursor.execute("alter table testtab_07062017 add firstcol_"+str(xxxx+1)+"_timestep bigint, add origin_"+str(xxxx+1)+"_timestep bigint, add numindiv_"+str(xxxx+1)+"_timestep float, add first25_"+str(xxxx+1)+"_timestep bigint;")
    
    starthabitats = np.random.choice(np.unique([habitats_shortpath_red[0], habitats_shortpath_red[1]]), 2).astype(int) # number of occupied habitats first run
     
#     starthabitats = np.array([7,90,99,3,52,94,24,78,62,57,89,67,11,44,38,45,96,60,55,13,47,77,33,98])
#     print(starthabitats)

    starthabitats_hq = habitats_QUAL[starthabitats-1]

    occhabitats = np.array([range(100+1)[1:], [-999] * 100, [-999] * 100, [0.0] * 100, [-999] * 100]) # 100: should be len(test_pts_shift)
                
    occhabitats[1][(starthabitats-1).tolist()] = 0
    occhabitats[2][(starthabitats-1).tolist()] = 0
    occhabitats[3][(starthabitats-1).tolist()] = starthabitats_hq * 100.0
    occhabitats[4][(starthabitats-1).tolist()] = 0

    prob = (1 - (habitats_shortpath_red[2] / np.amax(habitats_shortpath_red[2])))**2 # function to calculate the probability of reaching new habitat
        
#     plt.plot( sorted(habitats_shortpath_red[2], reverse=false), sorted(prob, reverse=true))
#     plt.xlabel('costs')
#     plt.ylabel('probability')
#     plt.grid(true)
  
    timesteps = 100

    stresslevel = [0.025, 0.05, 0.075, 0.1] # intensity of stress events

    percstress_events = 0.0 # percentage of stress occurrences per timesteps
    
    stress_events = np.random.choice(timesteps, int(percstress_events*timesteps)) # random selection depending on percstress_events
    
    area_event = habitats_extent # area where stress occurs - in this case: total area 

    theta = 0.5
    igr = 10
    
    growthfunc = 'tlg'
         
    m_max = 0.20
    s = 0.5
     
    for x in range(timesteps):
        
        starthabitats = occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int)
        
        igr_rand = igr + igr*random.uniform(-0.25, 0.25) 

        starthabitats_hq = habitats_QUAL[starthabitats-1] # habitat-quality of starthabitats
        starthabitats_indnr = occhabitats[3][starthabitats-1] # number of individuals in starthabitats

        if growthfunc == 'lg': 
      
            starthabitats_indnr = starthabitats_indnr+igr_rand*starthabitats_indnr*(1-starthabitats_indnr/(starthabitats_hq*100))

        if growthfunc == 'tlg': 
            
            c = ((starthabitats_hq*100) * np.sqrt(starthabitats_indnr) - starthabitats_indnr * np.sqrt(starthabitats_hq*100)) / ((starthabitats_hq*100) * starthabitats_indnr)
        
            starthabitats_indnr = (starthabitats_hq*100) / (1 + np.exp(-theta * igr_rand) * c * np.sqrt(starthabitats_hq*100))**2

        occhabitats[3][starthabitats-1] = starthabitats_indnr

        if x in stress_events:
            
            extprob = [i[0]  for i in xy_pts if i[1] >= area_event[0] and i[1] <= area_event[2] and i[2] >= area_event[1] and i[2] <= area_event[3]]

            for xxxxx in range(len(extprob)):
    
                if extprob[xxxxx] in starthabitats:
                                    
                    ind = np.where(starthabitats == extprob[xxxxx])[0].tolist()  
                                    
                    stresslevel_ch = np.random.choice(stresslevel) # 
                    
                    yn = 1
                    
                    if starthabitats_hq[ind][0] >= stresslevel_ch:
                          
                        stress = round(1-(starthabitats_hq[ind][0]-stresslevel_ch)/starthabitats_hq[ind][0],3)
                        
                        redindnr = round(np.array(starthabitats_indnr[ind][0])**2/10**5.0, 3) # exp function to include number of individuals in extinction prob
                    
                        yn = np.random.choice([1, 0], 1, p=[stress - round(stress*redindnr,3), 1.0 - (stress - round(stress*redindnr,3))])[0] # p extinction gets bigger when low hq and small number of individuals in h
 
                    plt.plot( range(101)[1:], np.log10(range(101)[1:])/20)
                    plt.xlabel('# of Individuals')
                    plt.ylabel('VAR: redIndNR')
                    plt.grid(True)
 
                    plt.ylim([0.5,1])
                    plt.plot(range(101)[1:], np.full((100), 0.75) - (np.full((100), 0.75)  *(np.log10(range(101)[1:])/20)))
                    plt.xlabel('# Individuals')
                    plt.ylabel('Stress 0.75: Extinction Probability')
                    plt.grid(True)
 
 
                    plt.plot( range(101)[1:], np.array(range(101)[1:])**2/10**5.0)
                    plt.xlabel('# of Individuals')
                    plt.ylabel('VAR: redIndNR')
                    plt.grid(True)
                     
                    plt.ylim([0.5,1])
                    plt.plot(range(101)[1:], np.full((100), 0.75) - (np.full((100), 0.75)  *(np.array(range(101)[1:])**2/10**5.0)))
                    plt.xlabel('Individuals')
                    plt.ylabel('Stress 0.75: Extinction Probability')
                    plt.grid(True)
                                       
                    if yn == 1: # extinction -> individuals set 0
                    
                        starthabitats = np.delete(starthabitats, ind)
                        
                        occhabitats[1][(extprob[xxxxx]-1)] = -111
                        occhabitats[2][(extprob[xxxxx]-1)] = -111
                        occhabitats[3][(extprob[xxxxx]-1)] = 0
                        
                        #print('death ' + str(extprob[xxxxx]))
 
        starthabitats = starthabitats[np.where(occhabitats[3][starthabitats-1] >= 20)] # starthabitats with less than 20 individuals are remove from starthabitats 
           
        for xx in range(len(starthabitats)):

            if starthabitats[xx] in habitats_shortpath_red[0] or starthabitats[xx] in habitats_shortpath_red[1]:
                conhabitats_ind = np.hstack(np.array([np.where(habitats_shortpath_red[0] == starthabitats[xx])[0].tolist(), np.where(habitats_shortpath_red[1] == starthabitats[xx])[0].tolist()]).flat).tolist()
                
            else:
                continue
                
            torem = []

            for y in conhabitats_ind:
                
                if habitats_shortpath_red[0][y] != starthabitats[xx]:
                
                    if occhabitats[3][habitats_shortpath_red[0][y]-1] >= habitats_qual[occhabitats[0][habitats_shortpath_red[0][y]-1]-1]*100:
                        
                        torem.append(y)
                
                else:
                    
                    if occhabitats[3][habitats_shortpath_red[1][y]-1] >= habitats_qual[occhabitats[0][habitats_shortpath_red[1][y]-1]-1]*100:
                                                
                        torem.append(y)

            for yy in torem:
            
                conhabitats_ind.remove(yy)   

#             if len(conhabitats_ind) > 3:
#                 
#                 conhabitats_ind = np.unique(np.random.choice(conhabitats_ind, 3, p = (max(habitats_shortpath_red[2][conhabitats_ind])-habitats_shortpath_red[2][conhabitats_ind]) /sum(max(habitats_shortpath_red[2][conhabitats_ind])-habitats_shortpath_red[2][conhabitats_ind]))) # weighted p to select 3 h -> weighting accroding to costs 
            
            
            
#            disind = occhabitats[3][starthabitats[xx]-1]*0.25

            if conhabitats_ind == []:
            
                continue
                        
            disind = occhabitats[3][starthabitats[xx]-1] * m_max *( occhabitats[3][starthabitats[xx]-1] / (habitats_qual[starthabitats[xx]-1]*100)) **(s+1)

            occhabitats[3][starthabitats[xx]-1] = occhabitats[3][starthabitats[xx]-1] - disind
    
            costs_reverse = ((habitats_shortpath_red[2][conhabitats_ind]-max(habitats_shortpath_red[2][conhabitats_ind]))*-1+min(habitats_shortpath_red[2][conhabitats_ind]))
            
#             disind_part = costs_reverse/sum(costs_reverse)

            disind_part = np.round(costs_reverse**10/sum(costs_reverse**10),1)

#             plt.plot( range(101)[1:], np.log10(range(101)[1:]))
#             plt.xlabel('# of individuals')
#             plt.ylabel('var: redindnr')
#             plt.grid(true)

            for xxx in conhabitats_ind:
                                
                disind_perch = disind * disind_part[0]
                
                disind_part = disind_part[1:]
                
                if disind_perch == 0:
                    
                    continue
                
#                 else: 
#                     print(disind_perch)
                
                yn = np.random.choice([1, 0], 1, p=[prob[xxx], 1-prob[xxx]])[0]
            
                if yn == 1:
                    
                    if occhabitats[0][habitats_shortpath_red[0][xxx]-1] != starthabitats[xx]:
                        
                        if occhabitats[1][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                        
                            occhabitats[1][habitats_shortpath_red[0][xxx]-1] = x+1 # ts of first population of h
                            
                        if occhabitats[2][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                            
                            occhabitats[2][habitats_shortpath_red[0][xxx]-1] = starthabitats[xx] # h populated from which sh
                                    
                        if occhabitats[3][habitats_shortpath_red[0][xxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[0][xxx]-1]-1]*100): # max pop size hq * 100        
                                                                       
                            occhabitats[3][habitats_shortpath_red[0][xxx]-1] = occhabitats[3][habitats_shortpath_red[0][xxx]-1] + disind_perch # function to calculate number of individuals in h -> plus disind_perch
                            
                        if  occhabitats[4][habitats_shortpath_red[0][xxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[0][xxx]-1] >= 25.0:
                            occhabitats[4][habitats_shortpath_red[0][xxx]-1] = x+1
                            
                        starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[0][xxx]-1]]), return_index=true)
                        starthabitats = starthabitats[np.argsort(ind)].astype(int)
                        
                    if occhabitats[0][habitats_shortpath_red[1][xxx]-1] != starthabitats[xx]:
                           
                        if occhabitats[1][habitats_shortpath_red[1][xxx]-1] in (-111, -999):
                                                    
                            occhabitats[1][habitats_shortpath_red[1][xxx]-1] = x+1 # ts of first population of h
                        
                        if occhabitats[2][habitats_shortpath_red[1][xxx]-1] in (-111, -999):

                            occhabitats[2][habitats_shortpath_red[1][xxx]-1] = starthabitats[xx] # h populated from which sh
                        
                        if occhabitats[3][habitats_shortpath_red[1][xxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[1][xxx]-1]-1]*100): # max pop size hq * 100                

                            occhabitats[3][habitats_shortpath_red[1][xxx]-1] = occhabitats[3][habitats_shortpath_red[1][xxx]-1] + disind_perch# function to calculate number of individuals in h -> plus disind_perch
                      
                        if  occhabitats[4][habitats_shortpath_red[1][xxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[1][xxx]-1] >= 25:
                            occhabitats[4][habitats_shortpath_red[1][xxx]-1] = x+1
                            
                        starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[1][xxx]-1]]), return_index=true)
                        starthabitats = starthabitats[np.argsort(ind)].astype(int)
           
    toins = str(np.array(occhabitats).t.tolist())[1:-1].replace('[','(').replace(']',')')
    
    if xxxx == 0:
        cursor.execute("insert into testtab_07062017 (pts_id, firstcol_"+str(xxxx+1)+"_timestep, origin_"+str(xxxx+1)+"_timestep, numindiv_"+str(xxxx+1)+"_timestep, first25_"+str(xxxx+1)+"_timestep) values "+toins+";") 

    else:
        cursor.execute("update testtab_07062017 set firstcol_"+str(xxxx+1)+"_timestep = firstcol_"+str(xxxx+1)+"_timestep_arr, origin_"+str(xxxx+1)+"_timestep = origin_"+str(xxxx+1)+"_timestep_arr, numindiv_"+str(xxxx+1)+"_timestep = numindiv_"+str(xxxx+1)+"_timestep_arr, first25_"+str(xxxx+1)+"_timestep = first25_"+str(xxxx+1)+"_timestep_arr from (values "+toins+") as c(pts_id_arr, firstcol_"+str(xxxx+1)+"_timestep_arr, origin_"+str(xxxx+1)+"_timestep_arr, numindiv_"+str(xxxx+1)+"_timestep_arr, first25_"+str(xxxx+1)+"_timestep_arr) where pts_id = pts_id_arr;") 

conn.commit()

end = time.time()
print(end - start)

# close communication with the database
cursor.close()
conn.close()
