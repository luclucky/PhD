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


def spatialSTRESS_RAST(raster_MD, SL, numEVENTS, rAdius):
    
    grid = np.zeros((raster_MD[2], raster_MD[3]))
    
    X_DIM = np.arange(grid.shape[0])
    Y_DIM = np.arange(grid.shape[1])
    
    circles = [[random.choice(X_DIM.tolist()),random.choice(Y_DIM.tolist())] for x in range(numEVENTS)]
    
    for x in range(len(circles)):
           
        grid_INTER = np.round(np.sqrt((X_DIM[:,None] - circles[x][0]) ** 2 + (Y_DIM[None, :] - circles[x][1]) ** 2), 2)
        
        grid_INTER[grid_INTER > rAdius] = None
        
        grid_INTER = np.round(SL - (SL * (grid_INTER / rAdius)), 5)
            
        grid = np.nansum([grid_INTER, grid],axis=0)
    
    return grid

# spaSTRESS_gRID = spatialSTRESS_RAST(raster_MD, SL = stresslevel_ch, numEVENTS = 5, rAdius = 2500)
#        
# masked_array = np.ma.masked_where(spaSTRESS_gRID == 0, spaSTRESS_gRID)
# 
# cmap = plt.cm.spring
# cmap.set_bad(color='white')
# 
# plt.imshow(masked_array, cmap="cool")
# plt.colorbar()
# plt.show()
# 
# plt.clf()

def PROBreachCONHABITAT(Co):
    P = (1 - (Co / np.amax(Co)))**2
    return P

def logGRO(K, N, r, t):
    
    Nt = (K * N) / (N + (K - N) * np.exp(-r*t)) 
    return Nt

def logGRO_T(T, N, r, t):

    Nt = (T * N) / (N + (T - N) * np.exp(r*t))
    return Nt

def THETAlogGRO(K, N, r, t):

    C = (K * np.sqrt(N) - N * np.sqrt(K)) / (K * N)
    Nt = K / (1 + np.exp(-theta * r * t) * C * np.sqrt(K))**2
    return Nt

def THETAlogGRO_T(T, N, r, t):
    
    C = (T * np.sqrt(N) - N * np.sqrt(T)) / (T * N)
    Nt = T / (1 + np.exp(-theta * -r * t) * C * np.sqrt(T))**2
    return Nt

def DENdepEMI_RATE(M, N, K, s):

    EmRa = N * M * (N / (K)) **(s+1)
    return EmRa

def percDISTRI_INDIdisper(HQ, VAR):

    CO_rev = ((HQ-max(HQ))*-1+min(HQ))
            
    if VAR == 'linear':
        percIND = np.round(CO_rev/sum(CO_rev),2)

    if VAR == 'exponential':   
        percIND = np.round(CO_rev**10/sum(CO_rev**10),2)
        
    return percIND            

def simSTRESS_VALUE(HQ, SL):

    STRESS = round(1-(HQ-SL)/HQ,3)
 
    return STRESS            

#####

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

cursor.execute("SELECT rid, ST_MetaData(rast) As md FROM costraster_triersaar;")
raster_MD = cursor.fetchall()
raster_MD = [float(x) for x in raster_MD[0][1][1:-1].split(',')]

cursor.execute("select start, aim, costs from habitats_shortpath_red;")
habitats_shortpath_red = cursor.fetchall()
habitats_shortpath_red = np.array(habitats_shortpath_red).T

habitats_qual = np.load('/home/lucas/PhD/STRESSOR/TEST_DATA/habitatsQuality.npy')
habitats_qual[np.where(habitats_qual < 0.25)] = 0.25 # min HQ set to 0.25

cursor.execute("create table testtab_28072017 (pts_id bigint);")

conn.commit()

for xxxx in range(100):
    
    print('run ' + str(xxxx))
        
#     cursor.execute("alter table testtab_07062017 add firstcol_"+str(xxxx+1)+"_timestep bigint, add origin_"+str(xxxx+1)+"_timestep bigint, add numindiv_"+str(xxxx+1)+"_timestep float, add first25_"+str(xxxx+1)+"_timestep bigint;")
    
    starthabitats = np.random.choice(np.unique([habitats_shortpath_red[0], habitats_shortpath_red[1]]), 2).astype(int) # number of occupied habitats first run
     
    starthabitats_hq = habitats_qual[starthabitats-1]

    occhabitats = np.array([range(len(habitats_qual)+1)[1:], [-999] * len(habitats_qual), [-999] * len(habitats_qual), [0.0] * len(habitats_qual), [-999] * len(habitats_qual)])
                
    occhabitats[1][(starthabitats-1).tolist()] = 0
    occhabitats[2][(starthabitats-1).tolist()] = 0
    occhabitats[3][(starthabitats-1).tolist()] = starthabitats_hq * 100.0
    occhabitats[4][(starthabitats-1).tolist()] = 0

    prob = PROBreachCONHABITAT(Co = habitats_shortpath_red[2])

    timesteps = 100

    stresslevel = [0.025, 0.05, 0.075, 0.1] # intensity of stress events

#     stresslevel = (np.random.choice(50, 3)/100.0).tolist()

    percstress_events = 0.0 # percentage of stress occurrences per timesteps
    
    stress_events = np.random.choice(timesteps, int(percstress_events*timesteps)) # random selection depending on percstress_events
    
    area_event = habitats_extent # area where stress occurs - in this case: total area 
    
    growthfunc = 'THETAlogGRO'    
    theta = 0.5
    igr = 2
    t  = 1
    TH = 5
         
    m_max = 0.20
    s = 0.5
     
    for x in range(timesteps):
        
        starthabitats = occhabitats[0][np.where(occhabitats[3] > 0.0)].astype(int)
        
        igr_rand = igr + igr*random.uniform(-0.25, 0.25) 

        starthabitats_hq = habitats_qual[starthabitats-1] # habitat-quality of starthabitats
        starthabitats_indnr = occhabitats[3][starthabitats-1] # number of individuals in starthabitats

        if growthfunc == 'logGRO': 
            
            starthabitats_indnr = logGRO(K = starthabitats_hq*100, N = starthabitats_indnr, r = igr_rand, t = 1)

        if growthfunc == 'logGRO_T': 
            
            starthabitats_indnr[np.where(starthabitats_indnr > TH)] = logGRO(K = starthabitats_hq[np.where(starthabitats_indnr > TH)]*100, N = starthabitats_indnr[np.where(starthabitats_indnr > TH)], r = igr_rand, t = 1)

            starthabitats_indnr[np.where(starthabitats_indnr <= TH)] = logGRO_T(T = TH, N = starthabitats_indnr[np.where(starthabitats_indnr <= 10)], r = igr_rand, t = 1)
            
        if growthfunc == 'THETAlogGRO': 
            
            starthabitats_indnr = THETAlogGRO(K = starthabitats_hq*100, N = starthabitats_indnr, r = igr_rand, t = 1)

        if growthfunc == 'THETAlogGRO_T': 
            
            starthabitats_indnr[np.where(starthabitats_indnr > TH)] = THETAlogGRO(K = starthabitats_hq[np.where(starthabitats_indnr > TH)]*100, N = starthabitats_indnr[np.where(starthabitats_indnr > TH)], r = igr_rand, t = 1)

            starthabitats_indnr[np.where(starthabitats_indnr <= TH)] = THETAlogGRO_T(T = TH, N = starthabitats_indnr[np.where(starthabitats_indnr <= 10)], r = igr_rand, t = 1)
            
        occhabitats[3][starthabitats-1] = starthabitats_indnr

        if x in stress_events:
            
            extprob = [i[0]  for i in xy_pts if i[1] >= area_event[0] and i[1] <= area_event[2] and i[2] >= area_event[1] and i[2] <= area_event[3]]

            stresslevel_ch = np.random.choice(stresslevel) 

            spaSTRESS_gRID = spatialSTRESS_RAST(raster_MD, SL = stresslevel_ch, numEVENTS = 5, rAdius = 25)

            for xxxxx in range(len(extprob)):
    
                if extprob[xxxxx] in starthabitats:
                                    
                    ind = np.where(starthabitats == extprob[xxxxx])[0].tolist()  
                    
#                     yn = 1
#                     
#                     if starthabitats_hq[ind][0] >= stresslevel_ch:
#                           
#                         stress = round(1-(starthabitats_hq[ind][0]-stresslevel_ch)/starthabitats_hq[ind][0],3)
#                         
#                         redindnr = round(np.array(starthabitats_indnr[ind][0])**2/10**5.0, 3) # exp function to include number of individuals in extinction prob
#                     
#                         yn = np.random.choice([1, 0], 1, p=[stress - round(stress*redindnr,3), 1.0 - (stress - round(stress*redindnr,3))])[0] # p extinction gets bigger when low hq and small number of individuals in h
#                           
#                     if yn == 1: # extinction -> individuals set 0
#                     
#                         starthabitats = np.delete(starthabitats, ind)
#                         
#                         occhabitats[1][(extprob[xxxxx]-1)] = -111
#                         occhabitats[2][(extprob[xxxxx]-1)] = -111
#                         occhabitats[3][(extprob[xxxxx]-1)] = 0
#                         
#                         #print('death ' + str(extprob[xxxxx]))
                    
                    SLpPT = spaSTRESS_gRID[int((raster_MD[1]-xy_pts[0][2])/100)][int((xy_pts[0][1]-raster_MD[0])/100)]
 
                    stress = simSTRESS_VALUE(starthabitats_hq[ind][0], SLpPT)
                     
                    occhabitats[3][(extprob[xxxxx]-1)] = occhabitats[3][(extprob[xxxxx]-1)]-occhabitats[3][(extprob[xxxxx]-1)]*stress
 
                    if occhabitats[3][(extprob[xxxxx]-1)] == 0:
                        
                        occhabitats[1][(extprob[xxxxx]-1)] = -111
                        occhabitats[2][(extprob[xxxxx]-1)] = -111

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

            if conhabitats_ind == []:
            
                continue
            
            disind = DENdepEMI_RATE(M = m_max, N = occhabitats[3][starthabitats[xx]-1], K = habitats_qual[starthabitats[xx]-1]*100, s = s)
                   
            occhabitats[3][starthabitats[xx]-1] = occhabitats[3][starthabitats[xx]-1] - disind
    
            disind_part = percDISTRI_INDIdisper(HQ = habitats_shortpath_red[2][conhabitats_ind], VAR = 'exponential')

            for xxx in conhabitats_ind:
                                
                disind_perc = disind * disind_part[0]
                
                disind_part = disind_part[1:]
                
                if disind_perc == 0:
                    
                    continue
                
#                 yn = np.random.choice([1, 0], 1, p=[prob[xxx], 1-prob[xxx]])[0]
            
#                 if yn == 1:

                disind_perc = disind_perc * prob[xxx]
                            
                if occhabitats[0][habitats_shortpath_red[0][xxx]-1] != starthabitats[xx]:
                    
                    if occhabitats[1][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                    
                        occhabitats[1][habitats_shortpath_red[0][xxx]-1] = x+1 # ts of first population of h
                        
                    if occhabitats[2][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                        
                        occhabitats[2][habitats_shortpath_red[0][xxx]-1] = starthabitats[xx] # h populated from which sh
                                
                    if occhabitats[3][habitats_shortpath_red[0][xxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[0][xxx]-1]-1]*100): # max pop size hq * 100        
                                                                   
                        occhabitats[3][habitats_shortpath_red[0][xxx]-1] = occhabitats[3][habitats_shortpath_red[0][xxx]-1] + disind_perc # function to calculate number of individuals in h -> plus disind_perc
                        
                    if  occhabitats[4][habitats_shortpath_red[0][xxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[0][xxx]-1] >= 25.0:
                        occhabitats[4][habitats_shortpath_red[0][xxx]-1] = x+1
                        
                    starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[0][xxx]-1]]), return_index=True)
                    starthabitats = starthabitats[np.argsort(ind)].astype(int)
                    
                if occhabitats[0][habitats_shortpath_red[1][xxx]-1] != starthabitats[xx]:
                       
                    if occhabitats[1][habitats_shortpath_red[1][xxx]-1] in (-111, -999):
                                                
                        occhabitats[1][habitats_shortpath_red[1][xxx]-1] = x+1 # ts of first population of h
                    
                    if occhabitats[2][habitats_shortpath_red[1][xxx]-1] in (-111, -999):

                        occhabitats[2][habitats_shortpath_red[1][xxx]-1] = starthabitats[xx] # h populated from which sh
                    
                    if occhabitats[3][habitats_shortpath_red[1][xxx]-1] < (habitats_qual[occhabitats[0][habitats_shortpath_red[1][xxx]-1]-1]*100): # max pop size hq * 100                

                        occhabitats[3][habitats_shortpath_red[1][xxx]-1] = occhabitats[3][habitats_shortpath_red[1][xxx]-1] + disind_perc# function to calculate number of individuals in h -> plus disind_perc
                  
                    if  occhabitats[4][habitats_shortpath_red[1][xxx]-1] in (-111, -999) and occhabitats[3][habitats_shortpath_red[1][xxx]-1] >= 25:
                        occhabitats[4][habitats_shortpath_red[1][xxx]-1] = x+1
                        
                    starthabitats, ind = np.unique(np.append(starthabitats,[occhabitats[0][habitats_shortpath_red[1][xxx]-1]]), return_index=True)
                    starthabitats = starthabitats[np.argsort(ind)].astype(int)
                   
    toins = str(np.array(occhabitats).T.tolist())[1:-1].replace('[','(').replace(']',')')
    
    if xxxx == 0:
        cursor.execute("insert into testtab_28072017 (pts_id, firstcol_"+str(xxxx+1)+"_timestep, origin_"+str(xxxx+1)+"_timestep, numindiv_"+str(xxxx+1)+"_timestep, first25_"+str(xxxx+1)+"_timestep) values "+toins+";") 

    else:
        cursor.execute("update testtab_28072017 set firstcol_"+str(xxxx+1)+"_timestep = firstcol_"+str(xxxx+1)+"_timestep_arr, origin_"+str(xxxx+1)+"_timestep = origin_"+str(xxxx+1)+"_timestep_arr, numindiv_"+str(xxxx+1)+"_timestep = numindiv_"+str(xxxx+1)+"_timestep_arr, first25_"+str(xxxx+1)+"_timestep = first25_"+str(xxxx+1)+"_timestep_arr from (values "+toins+") as c(pts_id_arr, firstcol_"+str(xxxx+1)+"_timestep_arr, origin_"+str(xxxx+1)+"_timestep_arr, numindiv_"+str(xxxx+1)+"_timestep_arr, first25_"+str(xxxx+1)+"_timestep_arr) where pts_id = pts_id_arr;") 

conn.commit()

end = time.time()
print(end - start)

# close communication with the database
cursor.close()
conn.close()

