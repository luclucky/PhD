
import numpy as np
np.set_printoptions(suppress=True)

import sys, gdal, ogr, os, osr
import random
        
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

# inHABs = ['pts_habitat_red_10x10', 'pts_habitat_red_30x30', 'pts_habitat_red_50x50']

inHABs = []

for x in range(25):

    inHABs.append('pts_habitat_red_50x50_'+str(x+1))

for inHAB in inHABs:
    
    cursor.execute("""SELECT idS, st_astext(geom) FROM stream_network_10x10."""+str(inHAB)+"""_start_"""+str(z)+""";""")
    xy_pts = cursor.fetchall()
    xy_pts = [[i[0],re.findall(r"[\w']+",i[1])[1:]] for i in xy_pts]
    xy_pts = [[i[0], float(i[1][0]), float(i[1][2])] for i in xy_pts]
    xy_pts.sort()
    
    hab_id = [int(s[0]) for s in xy_pts]
    
    list_SH = []
    
    for s in range(10):
    
        list_SH.append(np.random.choice(hab_id, int(len(hab_id)*0.1+0.5)).astype(int)) # number of occupied habitats first run
    
    cursor.execute("""CREATE TABLE res_SHequal_50x50."""+str(inHAB)+"""_starthabitas (sh_1 BIGINT, sh_2 BIGINT, sh_3 BIGINT, sh_4 BIGINT, sh_5 BIGINT, sh_6 BIGINT, sh_7 BIGINT, sh_8 BIGINT, sh_9 BIGINT, sh_10 BIGINT);""")
    
    toINS_list_SH = np.array(list_SH).T
    toINS_list_SH = toINS_list_SH.tolist()
    toINS_list_SH = str(np.array(toINS_list_SH).tolist())[1:-1].replace('[','(').replace(']',')').replace('\'','')
    
    cursor.execute("""INSERT INTO res_SHequal_50x50."""+str(inHAB)+"""_starthabitas (sh_1, sh_2, sh_3, sh_4, sh_5, sh_6, sh_7, sh_8, sh_9, sh_10) values """+toINS_list_SH+""";""")  
    
    conn.commit()
                
cursor.close()
conn.close()