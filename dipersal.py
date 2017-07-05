'''
Created on 2 Feb 2017

@author: lucas
'''

#from randShortPath import randShortPath as rSP
import numpy as np
import gdal, ogr, os, osr

import psycopg2
import math

import matplotlib.pyplot as plt

import time

import re

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")

tables = cursor.fetchall()

cursor.execute("SELECT start, start_xy, aim, aim_xy, distance FROM dist_pts_2500;")

dist_pts_2500 =  cursor.fetchall()

dist_pts_2500 = [list(x) for x in dist_pts_2500]

dist_pts_2500 = [[x[0],[float(x[1].split(' ',1)[0][6:]), float(x[1].split(' ',1)[1][:-1])],x[2],[float(x[3].split(' ',1)[0][6:]), float(x[3].split(' ',1)[1][:-1])], x[4]] for x in dist_pts_2500] 

doub = [[x[2], x[0]]for x in dist_pts_2500],[[x[0], x[2]]for x in dist_pts_2500]
  
dist_pts_2500_red = dist_pts_2500
   
for x in range(len(doub[0])/2):
        
    y = doub[0][x]
        
    #print('x: ' + str(x))
        
    for xx in range(len(doub[0])):
            
        #print('xx: ' + str(xx))

        yy = doub[1][xx]
    
        if yy == y:
            
            doub[0].pop(xx)
            doub[1].pop(xx)
            dist_pts_2500_red.pop(xx)
            break
                    
cursor.execute("SELECT ST_AsGDALRaster(rast, 'GTiff') FROM costraster_triersaar;")

vsipath = '/vsimem/from_postgis'

gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

cost_raster = gdal.Open(vsipath)

gdal.Unlink(vsipath)

from skimage.graph import route_through_array

cr_band = cost_raster.GetRasterBand(1)
cr_array = cost_raster.ReadAsArray()

numrows = len(cr_array)
numcols = len(cr_array[0])

cr_gt = cost_raster.GetGeoTransform()

cost_raster.RasterXSize

def ind_to_Xcoord(ind_x):
    
    coord_x = ind_x * cr_gt[1] + cr_gt[0] + cr_gt[1]/2 # coord

    return(coord_x)
    
def ind_to_Ycoord(ind_y):
    
    coord_y = ind_y * cr_gt[5] + cr_gt[3] + cr_gt[5]/2 # coord

    return(coord_y)

cursor.execute("CREATE TABLE habitats_shortpath_red (start bigint, aim bigint, geom geometry, costs double precision);")

for x in range(len(dist_pts_2500_red)):

    start_x = int((dist_pts_2500_red[x][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
    start_y = int((dist_pts_2500_red[x][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
    
    aim_x = int((dist_pts_2500_red[x][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
    aim_y = int((dist_pts_2500_red[x][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
    
    indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)
    
    #print(route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True))

    indices = np.array(indices).T
    
    coordinates = []
    
    mPTs = ""
    
    for xx in range(len(indices[0])):
    
        coordinates.append([ind_to_Xcoord(indices[0][xx]), ind_to_Ycoord(indices[1][xx])])

        mPTs = mPTs + "ST_MakePoint("+str(coordinates[xx][0]) + ', ' + str(coordinates[xx][1])+"),"

    mPTs = mPTs[:-1]

    cursor.execute("INSERT INTO habitats_shortpath_red (start, aim, geom, costs) VALUES ("+str(dist_pts_2500_red[x][0])+", "+str(dist_pts_2500_red[x][2])+", ST_SetSRID(ST_MakeLine(ARRAY["+str(mPTs)+"]), 25832), "+str(weight)+");") 

conn.commit()

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

start = time.time()

cursor.execute("SELECT ST_Extent(geom) FROM demo_dispersal_pts;")
habitats_extent = cursor.fetchall()
habitats_extent = re.findall(r"[\w']+", habitats_extent[0][0])[1:]
habitats_extent = [float(i) for i in habitats_extent]

cursor.execute("SELECT id, ST_AsText(geom) FROM demo_dispersal_pts;")
xy_PTS = cursor.fetchall()
xy_PTS = [[i[0],re.findall(r"[\w']+",i[1])[1:]] for i in xy_PTS]
xy_PTS = [[i[0], float(i[1][0]), float(i[1][1])] for i in xy_PTS]
xy_PTS.sort()

cursor.execute("SELECT start, aim, costs FROM habitats_shortpath_red;")
habitats_shortpath_red = cursor.fetchall()

habitats_shortpath_red = np.array(habitats_shortpath_red).T

habitats_QUAL = np.random.random_sample((100,))  # creates ramdom HQs

habitats_QUAL = np.load('/home/lucas/PhD/STRESSOR/TEST_DATA/habitatsQuality.npy')

habitats_QUAL[np.where(habitats_QUAL < 0.25)] = 0.25 # min HQ set to 0.25

#cursor.execute("CREATE TABLE habitats_qual (pts_id bigint, quality float);")
hqINS = str(np.array([range(100+1)[1:], habitats_QUAL]).T.tolist())[1:-1].replace('[','(').replace(']',')')
#cursor.execute("INSERT INTO habitats_qual (pts_id, quality) VALUES "+hqINS+";") 

cursor.execute("CREATE TABLE dispresal100_end_5 (pts_id bigint);")

conn.commit()

for xxxx in range(100):
    
    print('run ' + str(xxxx))
        
    cursor.execute("ALTER TABLE dispresal100_end_5 ADD firstcol_"+str(xxxx+1)+"_timestep bigint, ADD origin_"+str(xxxx+1)+"_timestep bigint, ADD numindiv_"+str(xxxx+1)+"_timestep bigint, ADD first25_"+str(xxxx+1)+"_timestep bigint;")
    
    startHABITATS = np.random.choice(np.unique([habitats_shortpath_red[0], habitats_shortpath_red[1]]), 2).astype(int) # number of occupied habitats first run
     
#     startHABITATS = np.array([7,90,99,3,52,94,24,78,62,57,89,67,11,44,38,45,96,60,55,13,47,77,33,98])
       
#     print(startHABITATS)

    SH = startHABITATS
            
    startHABITATS_HQ = habitats_QUAL[startHABITATS-1]

    occHABITATS = np.array([range(100+1)[1:], [-999] * 100, [-999] * 100, [0] * 100, [-999] * 100]) # 100: should be len(test_pts_shift)
                
    occHABITATS[1][(startHABITATS-1).tolist()] = 0
    occHABITATS[2][(startHABITATS-1).tolist()] = 0
    occHABITATS[3][(startHABITATS-1).tolist()] = (startHABITATS_HQ * 100).astype(int)
    occHABITATS[4][(startHABITATS-1).tolist()] = 0

    proB = (1 - (habitats_shortpath_red[2] / np.amax(habitats_shortpath_red[2])))**2 # function to calculate the probability of reaching new habitat
        
#     plt.plot( sorted(habitats_shortpath_red[2], reverse=False), sorted(proB, reverse=True))
#     plt.xlabel('Costs')
#     plt.ylabel('Probability')
#     plt.grid(True)
  
    timeSTEPS = 100

    stressLEVEL = [0.025, 0.05, 0.075, 0.1] # intensity of stress events

    percSTRESS_EVENTS = 0.0 # percentage of stress occurrences per timeSTEPS
    
    STRESS_EVENTS = np.random.choice(timeSTEPS, int(percSTRESS_EVENTS*timeSTEPS)) # random selection depending on percSTRESS_EVENTS
    
    area_EVENT = habitats_extent # area where stress occurs - in this case: total area 

    for x in range(timeSTEPS):
        
        #startHABITATS = startHABITATS[np.where(occHABITATS[3][startHABITATS-1] >= 25)]
        
        startHABITATS_HQ = habitats_QUAL[startHABITATS-1] # habitat-quality of startHABITATS
        startHABITATS_IndNR = occHABITATS[3][startHABITATS-1] # number of individuals in startHABITATS
       
        #extPROB = np.random.choice(100,int(len(startHABITATS)*0.1)) # 0.1 resp. 10 % of startHABITATS may go extinct 
             
        if x in STRESS_EVENTS:
            
            extPROB = [i[0]  for i in xy_PTS if i[1] >= area_EVENT[0] and i[1] <= area_EVENT[2] and i[2] >= area_EVENT[1] and i[2] <= area_EVENT[3]]

            for xxxxx in range(len(extPROB)):
    
                if extPROB[xxxxx] in startHABITATS:
                                    
                    ind = np.where(startHABITATS == extPROB[xxxxx])[0].tolist()  
                                    
                    redIndNR = np.log10(np.array(startHABITATS_IndNR[ind][0])) # log10 function to include number of individuals in extinction prob
                     
                    np.log10(range(101)[1:]) 
                     
#                     plt.plot( range(101)[1:], np.log10(range(101)[1:]))
#                     plt.xlabel('# of Individuals')
#                     plt.ylabel('VAR: redIndNR')
#                     plt.grid(True)
                    
                                    
                    stressLEVEL_cH = np.random.choice(stressLEVEL) # 
                    
                    if startHABITATS_HQ[ind][0] >= stressLEVEL_cH:
                          
                        STRESS = 1-(startHABITATS_HQ[ind][0]-stressLEVEL_cH)/startHABITATS_HQ[ind][0]
                    
                    else:            
                                
                        STRESS = 1
                        
                    if  redIndNR < 1:
                        
                        yn = 1
                   
                    else: 
                        yn = np.random.choice([0, 1], 1, p=[1-STRESS*(1/redIndNR), STRESS*(1/redIndNR)])[0] # p extinction gets bigger when low HQ and small number of individuals in H
                    
                    if yn == 1: # extinction -> individuals set 0
                    
                        startHABITATS = np.delete(startHABITATS, ind)
                        
                        occHABITATS[1][(extPROB[xxxxx]-1)] = -111
                        occHABITATS[2][(extPROB[xxxxx]-1)] = -111
                        occHABITATS[3][(extPROB[xxxxx]-1)] = 0
                        
                        #print('DEATH ' + str(extPROB[xxxxx]))
 
        startHABITATS = startHABITATS[np.where(occHABITATS[3][startHABITATS-1] >= 25)] # startHABITATS with less than 25 individuals are remove from startHABITATS 
           
        for xx in range(len(startHABITATS)):

            if startHABITATS[xx] in habitats_shortpath_red[0] or startHABITATS[xx] in habitats_shortpath_red[1]:
                conHABITATS_ind = np.hstack(np.array([np.where(habitats_shortpath_red[0] == startHABITATS[xx])[0].tolist(), np.where(habitats_shortpath_red[1] == startHABITATS[xx])[0].tolist()]).flat).tolist()
        
            else:
                continue
                
            toREM = []

            for y in conHABITATS_ind:
                
                if habitats_shortpath_red[0][y] != startHABITATS[xx]:
                
                    if occHABITATS[3][habitats_shortpath_red[0][y]-1] >= int(habitats_QUAL[occHABITATS[0][habitats_shortpath_red[0][y]-1]-1]*100):
                        
                        toREM.append(y)
                
                else:
                    
                    if occHABITATS[3][habitats_shortpath_red[1][y]-1] >= int(habitats_QUAL[occHABITATS[0][habitats_shortpath_red[1][y]-1]-1]*100):
                                                
                        toREM.append(y)

            for yy in toREM:
            
                conHABITATS_ind.remove(yy)   

#             if len(conHABITATS_ind) > 3:
#                 
#                 conHABITATS_ind = np.unique(np.random.choice(conHABITATS_ind, 3, p = (max(habitats_shortpath_red[2][conHABITATS_ind])-habitats_shortpath_red[2][conHABITATS_ind]) /sum(max(habitats_shortpath_red[2][conHABITATS_ind])-habitats_shortpath_red[2][conHABITATS_ind]))) # weighted p to select 3 H -> weighting accroding to costs 
            
            disIND = int(occHABITATS[3][startHABITATS[xx]-1]*0.25)
            
            if conHABITATS_ind == []:
            
                continue
            
#             disIND_part = np.random.dirichlet(np.ones(len(conHABITATS_ind)),size=1)[0]          

            costs_REVERSe = ((habitats_shortpath_red[2][conHABITATS_ind]-max(habitats_shortpath_red[2][conHABITATS_ind]))*-1+min(habitats_shortpath_red[2][conHABITATS_ind]))
            
#             disIND_part = costs_REVERSe/sum(costs_REVERSe)
            disIND_part = np.round(costs_REVERSe**10/sum(costs_REVERSe**10),1)

#             plt.plot( range(101)[1:], np.log10(range(101)[1:]))
#             plt.xlabel('# of Individuals')
#             plt.ylabel('VAR: redIndNR')
#             plt.grid(True)


            for xxx in conHABITATS_ind:
                                
                disIND_perCH = int(disIND * disIND_part[0])
                
                disIND_part = disIND_part[1:]
                
                if disIND_perCH == 0:
                    
                    continue
                
#                 else: 
#                     print(disIND_perCH)
                
                yn = np.random.choice([1, 0], 1, p=[proB[xxx], 1-proB[xxx]])[0]
            
                if yn == 1:
                    
                    if occHABITATS[0][habitats_shortpath_red[0][xxx]-1] != startHABITATS[xx]:
                        
                        if occHABITATS[1][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                        
                            occHABITATS[1][habitats_shortpath_red[0][xxx]-1] = x+1 # TS of first population of H
                            
                        if occHABITATS[2][habitats_shortpath_red[0][xxx]-1] in (-111, -999):
                            
                            occHABITATS[2][habitats_shortpath_red[0][xxx]-1] = startHABITATS[xx] # H populated from which SH
                                    
                        if occHABITATS[3][habitats_shortpath_red[0][xxx]-1] < (habitats_QUAL[occHABITATS[0][habitats_shortpath_red[0][xxx]-1]-1]*100).astype(int): # max pop size HQ * 100        
                                                                       
                            occHABITATS[3][habitats_shortpath_red[0][xxx]-1] = occHABITATS[3][habitats_shortpath_red[0][xxx]-1] + disIND_perCH # function to calculate number of individuals in H -> plus disIND_perCH
                            
                        if  occHABITATS[4][habitats_shortpath_red[0][xxx]-1] in (-111, -999) and occHABITATS[3][habitats_shortpath_red[0][xxx]-1] >= 25:
                            occHABITATS[4][habitats_shortpath_red[0][xxx]-1] = x+1
                            
                        startHABITATS, ind = np.unique(np.append(startHABITATS,[occHABITATS[0][habitats_shortpath_red[0][xxx]-1]]), return_index=True)
                        startHABITATS = startHABITATS[np.argsort(ind)]
                        
                    if occHABITATS[0][habitats_shortpath_red[1][xxx]-1] != startHABITATS[xx]:
                           
                        if occHABITATS[1][habitats_shortpath_red[1][xxx]-1] in (-111, -999):
                                                    
                            occHABITATS[1][habitats_shortpath_red[1][xxx]-1] = x+1 # TS of first population of H
                        
                        if occHABITATS[2][habitats_shortpath_red[1][xxx]-1] in (-111, -999):

                            occHABITATS[2][habitats_shortpath_red[1][xxx]-1] = startHABITATS[xx] # H populated from which SH
                        
                        if occHABITATS[3][habitats_shortpath_red[1][xxx]-1] < (habitats_QUAL[occHABITATS[0][habitats_shortpath_red[1][xxx]-1]-1]*100).astype(int): # max pop size HQ * 100                

                            occHABITATS[3][habitats_shortpath_red[1][xxx]-1] = occHABITATS[3][habitats_shortpath_red[1][xxx]-1] + disIND_perCH# function to calculate number of individuals in H -> plus disIND_perCH
                      
                        if  occHABITATS[4][habitats_shortpath_red[1][xxx]-1] in (-111, -999) and occHABITATS[3][habitats_shortpath_red[1][xxx]-1] >= 25:
                            occHABITATS[4][habitats_shortpath_red[1][xxx]-1] = x+1
                            
                        startHABITATS, ind = np.unique(np.append(startHABITATS,[occHABITATS[0][habitats_shortpath_red[1][xxx]-1]]), return_index=True)
                        startHABITATS = startHABITATS[np.argsort(ind)]
           
    toINS = str(np.array(occHABITATS).T.tolist())[1:-1].replace('[','(').replace(']',')')
    
    if xxxx == 0:
        cursor.execute("INSERT INTO dispresal100_end_5 (pts_id, firstcol_"+str(xxxx+1)+"_timestep, origin_"+str(xxxx+1)+"_timestep, numindiv_"+str(xxxx+1)+"_timestep, first25_"+str(xxxx+1)+"_timestep) VALUES "+toINS+";") 

    else:
        cursor.execute("UPDATE dispresal100_end_5 SET firstcol_"+str(xxxx+1)+"_timestep = firstcol_"+str(xxxx+1)+"_timestep_arr, origin_"+str(xxxx+1)+"_timestep = origin_"+str(xxxx+1)+"_timestep_arr, numindiv_"+str(xxxx+1)+"_timestep = numindiv_"+str(xxxx+1)+"_timestep_arr, first25_"+str(xxxx+1)+"_timestep = first25_"+str(xxxx+1)+"_timestep_arr FROM (VALUES "+toINS+") AS c(pts_id_arr, firstcol_"+str(xxxx+1)+"_timestep_arr, origin_"+str(xxxx+1)+"_timestep_arr, numindiv_"+str(xxxx+1)+"_timestep_arr, first25_"+str(xxxx+1)+"_timestep_arr) WHERE pts_id = pts_id_arr;") 

conn.commit()

end = time.time()
print(end - start)

# Close communication with the database
cursor.close()
conn.close()

# ex32.py
from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt

# Verhulst logistic growth

r = 10 # growth rate / yr
K = 100 # carrying capacity
t = 100 # number of years
num = np.zeros(t+1)
num[0] = 1

for i in range(t):
    num[i+1] = num[i]+r*num[i]*(1-num[i]/K)
    
plt.plot(range(t+1),num, 'b')
plt.xlabel('Year')
plt.ylabel('Number')
plt.title('Growth rate: 0.25, Carrying Capacity = 100')
plt.axvline(np.argmax(np.diff(num)),  color = 'k'  )
plt.show()

theta=0.5
num0=1
r=.25
K=100
t = 100

numTL = np.zeros(t+1)
numTL[0] = 1

for i in range(t):
## closed-form solution for theta-logistic
    numTL[i+1] = (K**(-theta)+(num0**(-theta)-K**(-theta))*np.exp(-r*theta*i))**(-1/theta)

plt.plot(range(t+1),numTL, 'b')


## th