
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

# cursor.execute("""SELECT ids FROM stream_network.rast_20x20""")
# 
# ids = cursor.fetchall()
# ids = [i[0] for i in ids]
# 
# for x in ids:
#     
#     print(x)
#     
#     cursor.execute("""CREATE TABLE stream_network.dist_pts_2500_20x20_"""+str(x)+""" AS SELECT * FROM stream_network.dist_pts_2500 WHERE ST_Contains(geom, (SELECT geom FROM stream_network.rast_20x20 WHERE ids = """+str(x)+"""));""")
#     
# 
#     conn.commit()
    
cursor.execute("""CREATE TABLE stream_network.dist_pts_2500_30x30 AS SELECT * FROM stream_network.dist_pts_2500 WHERE ST_Contains((SELECT ST_Union(geom) FROM stream_network.rast_30x30), geom);""")

conn.commit()

cursor.close()
conn.close()
    

