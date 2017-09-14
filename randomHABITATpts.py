
import numpy as np
import sys, gdal, ogr, os, osr
import random
import scipy 

import psycopg2
import math
import subprocess 

import matplotlib.pyplot as plt

import time
import nlmpy
import re

import bokeh
from bokeh.plotting import figure, show, output_file

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

# cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
# 
# tables = cursor.fetchall()

cursor.execute("SELECT ids, ST_AsText(geom) FROM stream_network.pts_habitat_red_50x50;")

randHAPTS =  cursor.fetchall()

randHAPTS = [list(x) for x in randHAPTS]

randHAPTS = [[int(x[0]),[float(x[1].split(' ',1)[0][6:]), float(x[1].split(' ',1)[1][:-1])]] for x in randHAPTS] 

randHAPTS_IDS = [int(x[0]) for x in randHAPTS] 
randHAPTS_X = [float(x[1][0]) for x in randHAPTS] 
randHAPTS_Y = [float(x[1][1]) for x in randHAPTS] 
randHAPTS_XY = [x[1] for x in randHAPTS] 

def randomSAMPLE(randHAPTS_IDS, maxHABs):
    
    random_SAMPLE = random.sample(randHAPTS_IDS, maxHABs)
    return(random_SAMPLE)

numRandPTs = 10

for x in range(numRandPTs):
    
    print(x)

    PTs_rSa = randomSAMPLE(randHAPTS_IDS, int(len(randHAPTS_IDS)*0.1+0.5))

    cursor.execute("""CREATE TABLE stream_network.pts_habitat_red_50x50_start_"""+str(x)+""" AS SELECT * FROM stream_network.pts_habitat_red_50x50 WHERE ids IN ("""+str(PTs_rSa)[1:-1]+""");""")
    
    conn.commit()
    
    cursor.execute("""SELECT ids FROM stream_network.pts_habitat_red_50x50_start_"""+str(x)+""";""")

    ids = cursor.fetchall()
    ids = [int(i[0]) for i in ids]
    
    cursor.execute("""CREATE TABLE stream_network.dist_pts_2500_50x50_start_"""+str(x)+""" AS SELECT * FROM stream_network.dist_pts_2500_50x50 WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")

    conn.commit()

cursor.close()
conn.close()


#####

def randomSAMPLE_CLUSTER(nrCLU, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, maxHABs = None):
    
    cursor.execute("SELECT ST_Extent(geom) FROM public.pts_habitat_triersaar_shift;")
    randHAPTS_EXTENT =  cursor.fetchall()
    randHAPTS_EXTENT = re.findall(r"[\w']+", randHAPTS_EXTENT[0][0])[1:]
    randHAPTS_EXTENT = [float(i) for i in randHAPTS_EXTENT]
    
    coord_CLUSTERsCENTER = np.dstack([np.array(random.sample(range(int(randHAPTS_EXTENT[0]/100), int(randHAPTS_EXTENT[2]/100)), nrCLU))*100, np.array(random.sample(range(int(randHAPTS_EXTENT[1]/100), int(randHAPTS_EXTENT[3]/100)), nrCLU))*100])[0]
    
    randHAPTS_IDS_CLUSTER = np.array([], int)

    for x in range(len(coord_CLUSTERsCENTER)):
    
        dist = np.array(np.sqrt((randHAPTS_X - coord_CLUSTERsCENTER[x][0])**2 + (randHAPTS_Y - coord_CLUSTERsCENTER[x][1])**2))
    
        randHAPTS_IDS_CLUSTER = np.append(randHAPTS_IDS_CLUSTER, np.array(randHAPTS_IDS)[np.where(dist < RADIUS)[0]])
    
    randHAPTS_IDS_CLUSTER = np.unique(randHAPTS_IDS_CLUSTER.flatten())

    if (maxHABs != None and len(randHAPTS_IDS_CLUSTER) > maxHABs):
        
        randHAPTS_IDS_CLUSTER = random.sample(randHAPTS_IDS_CLUSTER, maxHABs)
        
    return(randHAPTS_IDS_CLUSTER)
        
randomSAMPLE_CLUSTER(5, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 1250, 500)

#####

def randomSAMPLE_LINEAR(nrLIN, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, maxHABs = None):
    
    coord_LINEsCENTER_IDs = random.sample(randHAPTS_IDS, nrLIN)
    coord_LINEsCENTER_XY = np.array(randHAPTS_XY)[coord_LINEsCENTER_IDs]
    
    randHAPTS_IDS_LINEs = np.array([], int)
        
    for x in range(len(coord_LINEsCENTER_IDs)):
    
        dist = np.array(np.sqrt((randHAPTS_X - coord_LINEsCENTER_XY[x][0])**2 + (randHAPTS_Y - coord_LINEsCENTER_XY[x][1])**2))
    
        randHAPTS_IDS_LINE = np.array(randHAPTS_IDS)[np.where(dist < np.random.choice(range(int(RADIUS - RADIUS * .1) , int(RADIUS + RADIUS * .1))))[0]]
    
        coord_X = np.array(randHAPTS_X)[randHAPTS_IDS_LINE-1]
        coord_Y = np.array(randHAPTS_Y)[randHAPTS_IDS_LINE-1]
    
        toDEL = []
    
        for a in range(len(coord_X)):
            
            dist = np.array(np.sqrt((coord_X[a] - coord_X)**2 + (coord_Y[a] - coord_Y)**2))
            
            if sum(dist == 100) == 0:
                
                toDEL.append(a)
            
        randHAPTS_IDS_LINE = np.delete(randHAPTS_IDS_LINE, toDEL)

        randHAPTS_IDS_LINEs = np.append(randHAPTS_IDS_LINEs, randHAPTS_IDS_LINE)
    
    randHAPTS_IDS_LINEs = np.unique(randHAPTS_IDS_LINEs.flatten())
    

    coord_X = np.array(randHAPTS_X)[randHAPTS_IDS_LINEs-1]
    coord_Y = np.array(randHAPTS_Y)[randHAPTS_IDS_LINEs-1]
 
    toDEL = []
 
    for a in range(len(coord_X)):
         
        dist = np.array(np.sqrt((coord_X[a] - coord_X)**2 + (coord_Y[a] - coord_Y)**2))
         
        if sum(dist < 150) < 2:
             
            toDEL.append(a)
 
    randHAPTS_IDS_LINEs = np.delete(randHAPTS_IDS_LINEs, toDEL)
   
    if (maxHABs != None and len(randHAPTS_IDS_LINEs) > maxHABs):
        
        randHAPTS_IDS_LINEs = random.sample(randHAPTS_IDS_LINEs, maxHABs)
        
    return(randHAPTS_IDS_LINEs)

randomSAMPLE_LINEAR(10, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 750, 500)

#####


randHAPTS_IDS_clusT = randomSAMPLE_CLUSTER(3, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 2500)
randHAPTS_X_clusT = np.array(randHAPTS_X)[randHAPTS_IDS_clusT-1]
randHAPTS_Y_clusT = np.array(randHAPTS_Y)[randHAPTS_IDS_clusT-1]



# close communication with the database
cursor.close()
conn.close()


