
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

cursor.execute("""SELECT ids FROM stream_network.rast_20x20""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]

for x in ids:
    
    print(x)
    
    cursor.execute("""SELECT ST_Extent(geom) FROM stream_network.rast_20x20 WHERE ids = """+str(x)+""";""")
    ext =  cursor.fetchone()
    ext = re.findall(r"[\w.]+", ext[0])[1:]
    ext = [float(i) for i in ext]

    cursor.execute("""CREATE TABLE stream_network.rlp_stream_rast_testarea_20x20_"""+str(x)+""" AS SELECT ST_Clip(rast, (ST_SetSRID(ST_MakeEnvelope("""+str(ext)[1:-1]+"""), 25832))) AS rast FROM stream_network.rlp_stream_rast_testarea;""")
    
    
    cursor.execute("""SELECT AddRasterConstraints('stream_network'::name, 'rlp_stream_rast_testarea_20x20_"""+str(x)+"""'::name, 'rast'::name,'regular_blocking', 'blocksize');""")

    cursor.execute("""UPDATE stream_network.rlp_stream_rast_testarea_20x20_"""+str(x)+""" SET rast = ST_SetSRID(rast,25832);""")

    conn.commit()

cursor.close()
conn.close()