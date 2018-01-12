
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

# conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")

cursor = conn.cursor()

cursor.execute("""SELECT ids FROM stream_network.rast_10x10""")

ids = cursor.fetchall()
ids = [i[0] for i in ids]

for x in ids:
    
    print(x)
    
    cursor.execute("""SELECT ST_Extent(geom) FROM stream_network.rast_10x10 WHERE ids = """+str(x)+""";""")
    ext =  cursor.fetchone()
    ext = re.findall(r"[\w.]+", ext[0])[1:]
    ext = [float(i) for i in ext]

    for xx in range(10):
    
        cursor.execute("""CREATE TABLE stream_network_625125025.nlmr_testarea_50x50_"""+str(xx)+"""_"""+str(x)+""" AS SELECT ST_Clip(rast, (ST_SetSRID(ST_MakeEnvelope("""+str(ext)[1:-1]+"""), 25832))) AS rast FROM stream_network_625125025.nlmr_testarea_50x50_"""+str(xx)+"""_resamp;""")
    
        cursor.execute("""select addrasterconstraints('stream_network_625125025'::name, 'nlmr_testarea_50x50_"""+str(xx)+"""_"""+str(x)+"""'::name, 'rast'::name,'regular_blocking', 'blocksize');""")

        cursor.execute("""UPDATE stream_network_625125025.nlmr_testarea_50x50_"""+str(xx)+"""_"""+str(x)+""" SET rast = ST_SetSRID(rast,25832);""")

#####

        cursor.execute("""CREATE TABLE stream_network_625125025.nlmrc_testarea_50x50_"""+str(xx)+"""_"""+str(x)+""" AS SELECT ST_Clip(rast, (ST_SetSRID(ST_MakeEnvelope("""+str(ext)[1:-1]+"""), 25832))) AS rast FROM stream_network_625125025.nlmrc_testarea_50x50_"""+str(xx)+"""_resamp;""")
    
        cursor.execute("""SELECT AddRasterConstraints('stream_network_625125025'::name, 'nlmrc_testarea_50x50_"""+str(xx)+"""_"""+str(x)+"""'::name, 'rast'::name,'regular_blocking', 'blocksize');""")

        cursor.execute("""UPDATE stream_network_625125025.nlmrc_testarea_50x50_"""+str(xx)+"""_"""+str(x)+""" SET rast = ST_SetSRID(rast,25832);""")

#####

        cursor.execute("""CREATE TABLE stream_network_625125025.nlmre_testarea_50x50_"""+str(xx)+"""_"""+str(x)+""" AS SELECT ST_Clip(rast, (ST_SetSRID(ST_MakeEnvelope("""+str(ext)[1:-1]+"""), 25832))) AS rast FROM stream_network_625125025.nlmre_testarea_50x50_"""+str(xx)+"""_resamp;""")
    
        cursor.execute("""SELECT AddRasterConstraints('stream_network_625125025'::name, 'nlmre_testarea_50x50_"""+str(xx)+"""_"""+str(x)+"""'::name, 'rast'::name,'regular_blocking', 'blocksize');""")

        cursor.execute("""UPDATE stream_network_625125025.nlmre_testarea_50x50_"""+str(xx)+"""_"""+str(x)+""" SET rast = ST_SetSRID(rast,25832);""")

conn.commit()

cursor.close()
conn.close()