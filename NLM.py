
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

cursor.execute("SELECT ST_MetaData(rast) As md FROM dem.dem25_trsr;")
raster_MD = cursor.fetchall()
raster_MD = [float(x) for x in raster_MD[0][0][1:-1].split(',')]


# Read in metadata
inFile = open('/home/lucas/Desktop/DEM.asc', 'r')

nCOL = raster_MD[2]
nROW = raster_MD[3]

grid = np.zeros((raster_MD[2], raster_MD[3]))
    
X_DIM = np.arange(grid.shape[0])
Y_DIM = np.arange(grid.shape[1])

X_ll = raster_MD[0]
Y_ll = raster_MD[1]

cellSIZE = raster_MD[4]

vsipath = '/vsimem/from_postgis'

cursor.execute("SELECT ST_AsGDALRaster(rast, 'GTiff') FROM dem.dem25_trsr;")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
DEM_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

cursor.execute("SELECT ST_AsGDALRaster(rast, 'GTiff') FROM public.stream_trsr_raster;")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
STREAM01_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

cursor.close()
conn.close()


#np.random.seed(0) # to produce same NLMs

nlm1 = nlmpy.randomElementNN(int(nROW), int(nCOL), 1000)
nlm1 = ((nlmpy.classifyArray(nlm1, [.666,.111,.222]) + 1) * 25) + 25

np.unique(nlm1)
np.sum(nlm1 == 50)/(nROW * nCOL)
np.sum(nlm1 == 75)/(nROW * nCOL)
np.sum(nlm1 == 100)/(nROW * nCOL)

nlm2 = nlmpy.randomElementNN(int(nROW), int(nCOL), 500)
nlm2 = ((nlmpy.classifyArray(nlm2, [.5,.4,.1]) + 1) * 25) + 25

np.unique(nlm2)
np.sum(nlm2 == 50)/(nROW * nCOL)
np.sum(nlm2 == 75)/(nROW * nCOL)
np.sum(nlm2 == 100)/(nROW * nCOL)

# URBAN = 100
# FOREST = 75
# AGRICULTUR = 50
# STREAM = 25

nlm3 = nlmpy.randomClusterNN(int(nROW), int(nCOL), .375, n = '8-neighbourhood')
nlm3 = ((nlmpy.classifyArray(nlm3, [.7,.1,.2]) + 1) * 25) + 25

np.unique(nlm3)
np.sum(nlm3 == 50)/(nROW * nCOL)
np.sum(nlm3 == 75)/(nROW * nCOL)
np.sum(nlm3 == 100)/(nROW * nCOL)

nlm4 = nlmpy.randomClusterNN(int(nROW), int(nCOL), .4, n = '8-neighbourhood')
nlm4 = ((nlmpy.classifyArray(nlm4, [.5,.4,.1]) + 1) * 25) + 25

np.unique(nlm4)
np.sum(nlm4 == 50)/(nROW * nCOL)
np.sum(nlm4 == 75)/(nROW * nCOL)
np.sum(nlm4 == 100)/(nROW * nCOL)

nlm_RE = np.where((DEM_ARRAY <= 300), nlm1, nlm2)

nlm_RC = np.where((DEM_ARRAY <= 300), nlm3, nlm4)
# Replace all values with an elevation of 348 with a no data value to ignore
# the lake.
# 
# nlm = np.where(DEM_ARRAY <= 250, nlm2, nlm4)

np.place(nlm_RE, STREAM01_ARRAY == 1, 25)

np.unique(nlm_RE)
np.sum(nlm_RE == 25)/(nROW * nCOL)
np.sum(nlm_RE == 50)/(nROW * nCOL)
np.sum(nlm_RE == 75)/(nROW * nCOL)
np.sum(nlm_RE == 100)/(nROW * nCOL)

np.place(nlm_RC, STREAM01_ARRAY == 1, 25)

np.unique(nlm_RC)
np.sum(nlm_RC == 25)/(nROW * nCOL)
np.sum(nlm_RC == 50)/(nROW * nCOL)
np.sum(nlm_RC == 75)/(nROW * nCOL)
np.sum(nlm_RC == 100)/(nROW * nCOL)

plt.close()

fig = plt.figure()
ax = fig.add_subplot(121)
ax.imshow(nlm_RE, interpolation="bicubic")

ax2 = fig.add_subplot(122)
ax2.imshow(nlm_RC, interpolation="bicubic")

#####

dst_filename = '/home/lucas/Desktop/pyPICS/nlm_RC.tiff'

wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'

driver = gdal.GetDriverByName('GTiff')

dataset=[]

dataset = driver.Create(
    dst_filename,
    int(nCOL),
    int(nROW),
    1,
    gdal.GDT_Float32)

dataset.SetGeoTransform((
    X_ll, 
    cellSIZE, 
    0,                    
    Y_ll,
    0,
    -cellSIZE))

dataset.FlushCache()  # Write to disk.

dataset.SetProjection(wkt_projection)
dataset.GetRasterBand(1).WriteArray(nlm_RC)

dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_RC), np.amax(nlm_RC), np.mean(nlm_RC), np.std(nlm_RC))
dataset.GetRasterBand(1).SetNoDataValue(-999)

print(dataset.GetRasterBand(1).ReadAsArray())

dataset.FlushCache()  # Write to disk.

raster = gdal.Open(dst_filename,gdal.GA_ReadOnly)

raster_array = raster.ReadAsArray()

print raster_array


conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

os.environ['PGPASSWORD'] = '1gis!gis1' 

cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F public.nlmrc_test | psql -d DB_PhD -h localhost -U lucas '
subprocess.call(cmds, shell=True)

#####

dst_filename = '/home/lucas/Desktop/pyPICS/nlm_RE.tiff'

wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'

driver = gdal.GetDriverByName('GTiff')

dataset=[]

dataset = driver.Create(
    dst_filename,
    int(nCOL),
    int(nROW),
    1,
    gdal.GDT_Float32)

dataset.SetGeoTransform((
    X_ll, 
    cellSIZE, 
    0,                    
    Y_ll,
    0,
    -cellSIZE))

dataset.FlushCache()  # Write to disk.

dataset.SetProjection(wkt_projection)
dataset.GetRasterBand(1).WriteArray(nlm_RE)

dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_RE), np.amax(nlm_RE), np.mean(nlm_RE), np.std(nlm_RE))
dataset.GetRasterBand(1).SetNoDataValue(-999)

print(dataset.GetRasterBand(1).ReadAsArray())

dataset.FlushCache()  # Write to disk.

raster = gdal.Open(dst_filename,gdal.GA_ReadOnly)

raster_array = raster.ReadAsArray()

print raster_array


conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

os.environ['PGPASSWORD'] = '1gis!gis1' 

cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F public.nlmre_test | psql -d DB_PhD -h localhost -U lucas '
subprocess.call(cmds, shell=True)



