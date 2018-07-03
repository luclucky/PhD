
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

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")
cursor = conn.cursor()

# cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
# 
# tables = cursor.fetchall()

def randomSAMPLE(randHAPTS_IDS, maxHABs):
    
    random_SAMPLE = random.sample(randHAPTS_IDS, maxHABs)
    return(random_SAMPLE)

#####

def randomSAMPLE_CLUSTER(nrCLU, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, startHABs, maxHABs):
    
#     cursor.execute("""SELECT ST_Extent(geom) FROM stream_network.rast_10x10 WHERE ids = """+str(net_ids)+""";""")
#     randHAPTS_EXTENT =  cursor.fetchall()
#     randHAPTS_EXTENT = re.findall(r"[\d\.\\d]+", randHAPTS_EXTENT[0][0])
#     randHAPTS_EXTENT = [float(i) for i in randHAPTS_EXTENT]
#     
#     coord_CLUSTERsCENTER = np.dstack([np.array(random.sample(range(int(randHAPTS_EXTENT[0]/100), int(randHAPTS_EXTENT[2]/100)), nrCLU))*100, np.array(random.sample(range(int(randHAPTS_EXTENT[1]/100), int(randHAPTS_EXTENT[3]/100)), nrCLU))*100])[0]
    
    randHAPTS_IDS_samp = [i for i in randHAPTS_IDS if i not in startHABs]
    
    coord_IDS = random.sample((randHAPTS_IDS_samp), nrCLU-len(startHABs)) + startHABs

    coord_CLUSTERsCENTER = np.array([[randHAPTS_X[randHAPTS_IDS.index(i)],randHAPTS_Y[randHAPTS_IDS.index(i)]] for i in coord_IDS]) 

    randHAPTS_IDS_CLUSTER = np.array([], int)

    for x in range(len(coord_CLUSTERsCENTER)):
    
        dist = np.array(np.sqrt((randHAPTS_X - coord_CLUSTERsCENTER[x][0])**2 + (randHAPTS_Y - coord_CLUSTERsCENTER[x][1])**2))
    
        randHAPTS_IDS_CLUSTER = np.append(randHAPTS_IDS_CLUSTER, np.array(randHAPTS_IDS)[np.where(dist < RADIUS)[0]])
    
    randHAPTS_IDS_CLUSTER = np.unique(randHAPTS_IDS_CLUSTER.flatten())

    randHAPTS_IDS_CLUSTER = [i for i in randHAPTS_IDS_CLUSTER if i not in coord_IDS]

    if (maxHABs != None and len(randHAPTS_IDS_CLUSTER) > maxHABs- len(coord_IDS)):
        
        randHAPTS_IDS_CLUSTER = random.sample(randHAPTS_IDS_CLUSTER, maxHABs - len(coord_IDS))
        
    else:
        print('toLESS')
        
    randHAPTS_IDS_CLUSTER = randHAPTS_IDS_CLUSTER + coord_IDS
    
    return(randHAPTS_IDS_CLUSTER)
        
#####

def randomSAMPLE_LINEAR(nrLIN, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, RADIUS, startHABs, maxHABs):
    
    randHAPTS_IDS_samp = [i for i in randHAPTS_IDS if i not in startHABs]
    
    coord_LINEsCENTER_IDs = random.sample((randHAPTS_IDS_samp), nrLIN-len(startHABs)) + startHABs
    
    coord_LINEsCENTER_XY = np.array([[randHAPTS_X[randHAPTS_IDS.index(i)],randHAPTS_Y[randHAPTS_IDS.index(i)]] for i in coord_LINEsCENTER_IDs]) 
    
    randHAPTS_IDS_LINEs = np.array([], int)
        
    for x in range(len(coord_LINEsCENTER_IDs)):
    
        dist = np.array(np.sqrt((randHAPTS_X - coord_LINEsCENTER_XY[x][0])**2 + (randHAPTS_Y - coord_LINEsCENTER_XY[x][1])**2))
    
        randHAPTS_IDS_LINE = np.array(randHAPTS_IDS)[np.where(dist < np.random.choice(range(int(RADIUS - RADIUS * .1) , int(RADIUS + RADIUS * .1))))[0]]
    
        randHAPTS_IDS_NDX = np.array([randHAPTS_IDS.index(i) for i in randHAPTS_IDS_LINE]) 
    
#         coord_X = np.array(randHAPTS_X)[randHAPTS_IDS_NDX]
#         coord_Y = np.array(randHAPTS_Y)[randHAPTS_IDS_NDX]
#     
#         toDEL = []
#     
#         for a in range(len(coord_X)):
#             
#             dist = np.array(np.sqrt((coord_X[a] - coord_X)**2 + (coord_Y[a] - coord_Y)**2))
#             
#             if sum(dist == 100) == 0:
#                 
#                 toDEL.append(a)
#             
#         randHAPTS_IDS_LINE = np.delete(randHAPTS_IDS_LINE, toDEL)

        randHAPTS_IDS_LINEs = np.append(randHAPTS_IDS_LINEs, randHAPTS_IDS_LINE)
    
    randHAPTS_IDS_LINEs = np.unique(randHAPTS_IDS_LINEs.flatten())
#     
#     randHAPTS_IDS_NDXs = np.array([randHAPTS_IDS.index(i) for i in randHAPTS_IDS_LINEs]) 
# 
#     coord_X = np.array(randHAPTS_X)[randHAPTS_IDS_NDXs]
#     coord_Y = np.array(randHAPTS_Y)[randHAPTS_IDS_NDXs]
#  
#     toDEL = []
#  
#     for a in range(len(coord_X)):
#          
#         dist = np.array(np.sqrt((coord_X[a] - coord_X)**2 + (coord_Y[a] - coord_Y)**2))
#          
#         if sum(dist < 150) < 2:
#              
#             toDEL.append(a)
#  
#     randHAPTS_IDS_LINEs = np.delete(randHAPTS_IDS_LINEs, toDEL)
#    
    randHAPTS_IDS_LINEs = [i for i in randHAPTS_IDS_LINEs if i not in coord_LINEsCENTER_IDs]

    if (maxHABs != None and len(randHAPTS_IDS_LINEs) > maxHABs - len(coord_LINEsCENTER_IDs)):
        
        randHAPTS_IDS_LINEs = random.sample(randHAPTS_IDS_LINEs, (maxHABs - len(coord_LINEsCENTER_IDs)))
    
    else:
        print('toLESS')
    
    randHAPTS_IDS_LINEs = randHAPTS_IDS_LINEs + coord_LINEsCENTER_IDs

    return(randHAPTS_IDS_LINEs)

# randomSAMPLE_LINEAR(10, randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 750, 500)

numRandPTs = 10

cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")
 
ids = cursor.fetchall()
ids = [i[0] for i in ids]
 
for xx in ids:
    
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.pts_habitat_red_"""+str(xx)+""";""")
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_02.dist_pts_2500_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.dist_pts_2500_"""+str(xx)+""";""")
    
    conn.commit()

    cursor.execute("""SELECT ids, ST_AsText(geom) FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+""";""")
    
    randHAPTS =  cursor.fetchall()
    
    randHAPTS = [list(x) for x in randHAPTS]
    
    randHAPTS = [[int(x[0]),[float(x[1].split(' ',1)[0][6:]), float(x[1].split(' ',1)[1][:-1])]] for x in randHAPTS] 
    
    randHAPTS_IDS = [int(x[0]) for x in randHAPTS] 
    randHAPTS_X = [float(x[1][0]) for x in randHAPTS] 
    randHAPTS_Y = [float(x[1][1]) for x in randHAPTS] 
    randHAPTS_XY = [x[1] for x in randHAPTS] 

    for x in range(numRandPTs):
        
        print(x)
     
        PTs_rSa = randomSAMPLE(randHAPTS_IDS, int(len(randHAPTS_IDS)*0.2+0.5))
#         PTs_rSa = randomSAMPLE_CLUSTER(int(len(randHAPTS_IDS)*0.0625+0.5), randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 500, xx, int(len(randHAPTS_IDS)*0.25+0.5))
      
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+""" WHERE ids IN ("""+str(PTs_rSa)[1:-1]+""");""")
        
        cursor.execute("""ALTER TABLE dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" RENAME COLUMN ids TO ids_org;""")
        
        cursor.execute("""ALTER TABLE dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" ADD column ids bigserial;""")
    
        conn.commit()
          
        cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""";""")
     
        ids = cursor.fetchall()
        ids = [int(i[0]) for i in ids]
         
        print(len(ids))
         
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_random_02.dist_pts_2500_"""+(str(xx))+""" WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")
    
        cursor.execute("""UPDATE dis_pts_2500_10x10_random_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" SET start = (SELECT dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE dis_pts_2500_10x10_random_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""".start = dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids_org);""")

        cursor.execute("""UPDATE dis_pts_2500_10x10_random_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" SET aim = (SELECT dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE dis_pts_2500_10x10_random_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""".aim = dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids_org);""")
    
        conn.commit()

### StartHABs

inHABs = []

for x in range(25):

    inHABs.append('pts_habitat_red_'+str(x+1))

for inHAB in inHABs:
    
    for z in range(10):
        
        cursor.execute("""SELECT idS, st_astext(geom) FROM dis_pts_2500_10x10_random_02."""+str(inHAB)+"""_start_"""+str(z)+""";""")
        xy_pts = cursor.fetchall()
        xy_pts = [[i[0],re.findall(r"[\w']+",i[1])[1:]] for i in xy_pts]
        xy_pts = [[i[0], float(i[1][0]), float(i[1][2])] for i in xy_pts]
        xy_pts.sort()
        
        hab_id = [int(s[0]) for s in xy_pts]
        list_SH = []
        
        for s in range(10):
        
            list_SH.append(np.random.choice(hab_id, int(len(hab_id)*0.1+0.5), replace = False).astype(int)) # number of occupied habitats first run
        
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_random_02."""+str(inHAB)+"""_starthabitas (sh_1 BIGINT, sh_2 BIGINT, sh_3 BIGINT, sh_4 BIGINT, sh_5 BIGINT, sh_6 BIGINT, sh_7 BIGINT, sh_8 BIGINT, sh_9 BIGINT, sh_10 BIGINT);""")
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_02."""+str(inHAB)+"""_starthabitas (sh_1 BIGINT, sh_2 BIGINT, sh_3 BIGINT, sh_4 BIGINT, sh_5 BIGINT, sh_6 BIGINT, sh_7 BIGINT, sh_8 BIGINT, sh_9 BIGINT, sh_10 BIGINT);""")
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_02."""+str(inHAB)+"""_starthabitas (sh_1 BIGINT, sh_2 BIGINT, sh_3 BIGINT, sh_4 BIGINT, sh_5 BIGINT, sh_6 BIGINT, sh_7 BIGINT, sh_8 BIGINT, sh_9 BIGINT, sh_10 BIGINT);""")

    toINS_list_SH = np.array(list_SH).T
    toINS_list_SH = toINS_list_SH.tolist()
    toINS_list_SH = str(np.array(toINS_list_SH).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')
    
    cursor.execute("""INSERT INTO dis_pts_2500_10x10_random_02."""+str(inHAB)+"""_starthabitas (sh_1, sh_2, sh_3, sh_4, sh_5, sh_6, sh_7, sh_8, sh_9, sh_10) values """+toINS_list_SH+""";""")  

    conn.commit()
           
### CLUSTER

cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")
 
ids = cursor.fetchall()
ids = [i[0] for i in ids]
 
for xx in ids:
    
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.pts_habitat_red_"""+str(xx)+""";""")
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_02.dist_pts_2500_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.dist_pts_2500_"""+str(xx)+""";""")
    
    conn.commit()

    cursor.execute("""SELECT ids, ST_AsText(geom) FROM dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+""";""")
    randHAPTS =  cursor.fetchall()
    randHAPTS = [list(x) for x in randHAPTS]
    randHAPTS = [[int(x[0]),[float(x[1].split(' ',1)[0][6:]), float(x[1].split(' ',1)[1][:-1])]] for x in randHAPTS] 
    
    randHAPTS_IDS = [int(x[0]) for x in randHAPTS] 
    randHAPTS_X = [float(x[1][0]) for x in randHAPTS] 
    randHAPTS_Y = [float(x[1][1]) for x in randHAPTS] 
    randHAPTS_XY = [x[1] for x in randHAPTS] 
    
    cursor.execute("""SELECT * FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_starthabitas;""")
    LIST_startHABs = cursor.fetchall()
    LIST_startHABs = np.array(LIST_startHABs).T
    
    toINS_list_SH = []
    
    for x in range(numRandPTs):
        
        print(x)
        
        cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE ids IN ("""+str(LIST_startHABs[x].tolist())[1:-1].replace('L','')+""");""")
        startHABs = cursor.fetchall()
        startHABs = [int(i[0]) for i in startHABs]
        
        PTs_rCl = randomSAMPLE_CLUSTER(int(len(randHAPTS_IDS)*0.05+0.5), randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 500, startHABs, int(len(randHAPTS_IDS)*0.2+0.5))
      
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+""" WHERE ids IN ("""+str(PTs_rCl)[1:-1]+""");""")
        
        cursor.execute("""ALTER TABLE dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" RENAME COLUMN ids TO ids_org;""")
        
        cursor.execute("""ALTER TABLE dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" ADD column ids bigserial;""")
        
                
        cursor.execute("""SELECT ids FROM dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE ids_org IN ("""+str(startHABs)[1:-1]+""");""")
        toINS = cursor.fetchall()
        toINS = [int(i[0]) for i in toINS]
    
        toINS_list_SH.append(toINS)

        conn.commit()
          
        cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""";""")
     
        ids = cursor.fetchall()
        ids = [int(i[0]) for i in ids]
         
        print(len(ids))
         
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_clustr_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_clustr_02.dist_pts_2500_"""+(str(xx))+""" WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")
    
        cursor.execute("""UPDATE dis_pts_2500_10x10_clustr_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" SET start = (SELECT dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids FROM dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE dis_pts_2500_10x10_clustr_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""".start = dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids_org);""")

        cursor.execute("""UPDATE dis_pts_2500_10x10_clustr_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" SET aim = (SELECT dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids FROM dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE dis_pts_2500_10x10_clustr_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""".aim = dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids_org);""")
    
        conn.commit()

    toINS_list_SH = np.array(toINS_list_SH).T
    toINS_list_SH = toINS_list_SH.tolist()
    toINS_list_SH = str(np.array(toINS_list_SH).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')
    
    cursor.execute("""INSERT INTO dis_pts_2500_10x10_clustr_02.pts_habitat_red_"""+str(xx)+"""_starthabitas (sh_1, sh_2, sh_3, sh_4, sh_5, sh_6, sh_7, sh_8, sh_9, sh_10) values """+toINS_list_SH+""";""")  

    conn.commit()

cursor.close()
conn.close()

### LINEAR

numRandPTs = 10

cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")
 
ids = cursor.fetchall()
ids = [i[0] for i in ids]
 
for xx in ids:
    
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.pts_habitat_red_"""+str(xx)+""";""")
    cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_02.dist_pts_2500_"""+str(xx)+""" AS SELECT * FROM dis_pts_2500_10x10_random_01.dist_pts_2500_"""+str(xx)+""";""")
    
    conn.commit()

    cursor.execute("""SELECT ids, ST_AsText(geom) FROM dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+""";""")
    randHAPTS =  cursor.fetchall()
    randHAPTS = [list(x) for x in randHAPTS]
    randHAPTS = [[int(x[0]),[float(x[1].split(' ',1)[0][6:]), float(x[1].split(' ',1)[1][:-1])]] for x in randHAPTS] 
    
    randHAPTS_IDS = [int(x[0]) for x in randHAPTS] 
    randHAPTS_X = [float(x[1][0]) for x in randHAPTS] 
    randHAPTS_Y = [float(x[1][1]) for x in randHAPTS] 
    randHAPTS_XY = [x[1] for x in randHAPTS] 
    
    cursor.execute("""SELECT * FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_starthabitas;""")
    LIST_startHABs = cursor.fetchall()
    LIST_startHABs = np.array(LIST_startHABs).T
    
    toINS_list_SH = []
    
    for x in range(numRandPTs):
        
        print(x)
        
        cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_random_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE ids IN ("""+str(LIST_startHABs[x].tolist())[1:-1].replace('L','')+""");""")
        startHABs = cursor.fetchall()
        startHABs = [int(i[0]) for i in startHABs]
        
        PTs_rLi = randomSAMPLE_LINEAR(int(len(randHAPTS_IDS)*0.025+0.5), randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 500, startHABs, int(len(randHAPTS_IDS)*0.2+0.5))
        
        if (len(PTs_rLi) < int(len(randHAPTS_IDS)*0.2+0.5)):
            PTs_rLi = randomSAMPLE_LINEAR(int(len(randHAPTS_IDS)*0.025+0.5), randHAPTS_X, randHAPTS_Y, randHAPTS_IDS, 500, startHABs, int(len(randHAPTS_IDS)*0.2+0.5))
            print(x)

        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+""" WHERE ids IN ("""+str(PTs_rLi)[1:-1]+""");""")
        
        cursor.execute("""ALTER TABLE dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" RENAME COLUMN ids TO ids_org;""")
        
        cursor.execute("""ALTER TABLE dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" ADD column ids bigserial;""")
        
                
        cursor.execute("""SELECT ids FROM dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE ids_org IN ("""+str(startHABs)[1:-1]+""");""")
        toINS = cursor.fetchall()
        toINS = [int(i[0]) for i in toINS]
    
        toINS_list_SH.append(toINS)

        conn.commit()
          
        cursor.execute("""SELECT ids_org FROM dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""";""")
     
        ids = cursor.fetchall()
        ids = [int(i[0]) for i in ids]
         
        print(len(ids))
         
        cursor.execute("""CREATE TABLE dis_pts_2500_10x10_linear_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" AS SELECT * FROM dis_pts_2500_10x10_linear_02.dist_pts_2500_"""+(str(xx))+""" WHERE start IN ("""+str(ids)[1:-1]+""") AND aim IN ("""+str(ids)[1:-1]+""");""")
    
        cursor.execute("""UPDATE dis_pts_2500_10x10_linear_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" SET start = (SELECT dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids FROM dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE dis_pts_2500_10x10_linear_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""".start = dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids_org);""")

        cursor.execute("""UPDATE dis_pts_2500_10x10_linear_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""" SET aim = (SELECT dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids FROM dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""" WHERE dis_pts_2500_10x10_linear_02.dist_pts_2500_"""+(str(xx))+"""_start_"""+str(x)+""".aim = dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_start_"""+str(x)+""".ids_org);""")
    
        conn.commit()

    toINS_list_SH = np.array(toINS_list_SH).T
    toINS_list_SH = toINS_list_SH.tolist()
    toINS_list_SH = str(np.array(toINS_list_SH).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')
    
    cursor.execute("""INSERT INTO dis_pts_2500_10x10_linear_02.pts_habitat_red_"""+str(xx)+"""_starthabitas (sh_1, sh_2, sh_3, sh_4, sh_5, sh_6, sh_7, sh_8, sh_9, sh_10) values """+toINS_list_SH+""";""")  

    conn.commit()

cursor.close()
conn.close()

