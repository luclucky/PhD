
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

# cursor.execute("""SELECT ids FROM stream_network.rast_20x20""")
# 
# ids = cursor.fetchall()
# ids = [i[0] for i in ids]

cursor.execute("""SELECT ST_MetaData(rast) As md FROM stream_network.rlp_stream_rast_testarea_50x50;""")
raster_MD = cursor.fetchall()
raster_MD = [float(xx) for xx in raster_MD[0][0][1:-1].split(',')]

nCOL = int(raster_MD[2])
nROW = int(raster_MD[3])

grid = np.zeros((nCOL, nROW))
    
X_DIM = np.arange(grid.shape[0])
Y_DIM = np.arange(grid.shape[1])

X_ll = raster_MD[0]
Y_ll = raster_MD[1]

cellSIZE = raster_MD[4]

vsipath = '/vsimem/from_postgis'

# cursor.execute("SELECT ST_AsGDALRaster(rast, 'GTiff') FROM dem.dem25_trsr;")
# gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))
# 
# ds = gdal.Open(vsipath)
# band = ds.GetRasterBand(1)
# DEM_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

# cursor.execute("""SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';""")

cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM stream_network.rlp_stream_rast_testarea_50x50;""")
gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

ds = gdal.Open(vsipath)
band = ds.GetRasterBand(1)
STREAM01_ARRAY = band.ReadAsArray()

ds = band = None
gdal.Unlink(vsipath)

cursor.close()
conn.close()

numNLMs = 10

for x in range(numNLMs):
    
    print(x)
    
#     cursor.execute("""ALTER TABLE stream_network.rlp_stream_rast_testarea_20x20_"""+str(x)+""" RENAME COLUMN st_clip TO rast;""")
#     
#     conn.commit()

    
    #np.random.seed(0) # to produce same NLMs
    
    # URBAN = 100
    # FOREST = 75
    # AGRICULTUR = 50
    # STREAM = 25
    
    #####
    
    nlm_R = nlmpy.random(int(nROW), int(nCOL))
    nlm_R = ((nlmpy.classifyArray(nlm_R, [.125,.25,.625]) + 1) * 25) + 25
    
    np.unique(nlm_R)
    np.sum(nlm_R == 50)/(nROW * nCOL)
    np.sum(nlm_R == 75)/(nROW * nCOL)
    np.sum(nlm_R == 100)/(nROW * nCOL)
    
    np.place(nlm_R, STREAM01_ARRAY == 1, 25)
    
    np.unique(nlm_R)
    np.sum(nlm_R == 25)/(nROW * nCOL)
    np.sum(nlm_R == 50)/(nROW * nCOL)
    np.sum(nlm_R == 75)/(nROW * nCOL)
    np.sum(nlm_R == 100)/(nROW * nCOL)
    
    #####
    
#     nlm_MPD = nlmpy.mpd(int(nROW), int(nCOL), 100000)
#     nlm_MPD = ((nlmpy.classifyArray(nlm_MPD, [.666,.111,.222]) + 1) * 25) + 25
#      
#     np.unique(nlm_MPD)
#     np.sum(nlm_MPD == 50)/(nROW * nCOL)
#     np.sum(nlm_MPD == 75)/(nROW * nCOL)
#     np.sum(nlm_MPD == 100)/(nROW * nCOL)
#      
#     np.place(nlm_MPD, STREAM01_ARRAY == 1, 25)
#      
#     np.unique(nlm_MPD)
#     np.sum(nlm_MPD == 25)/(nROW * nCOL)
#     np.sum(nlm_MPD == 50)/(nROW * nCOL)
#     np.sum(nlm_MPD == 75)/(nROW * nCOL)
#     np.sum(nlm_MPD == 100)/(nROW * nCOL)
    
    #####
    
#     nlm_RRC = nlmpy.randomRectangularCluster(int(nROW), int(nCOL), 50, 75)
#     nlm_RRC = ((nlmpy.classifyArray(nlm_RRC, [.666,.111,.222]) + 1) * 25) + 25
#      
#     np.unique(nlm_RRC)
#     np.sum(nlm_RRC == 50)/(nROW * nCOL)
#     np.sum(nlm_RRC == 75)/(nROW * nCOL)
#     np.sum(nlm_RRC == 100)/(nROW * nCOL)
#      
#     np.place(nlm_RRC, STREAM01_ARRAY == 1, 25)
#      
#     np.unique(nlm_RRC)
#     np.sum(nlm_RRC == 25)/(nROW * nCOL)
#     np.sum(nlm_RRC == 50)/(nROW * nCOL)
#     np.sum(nlm_RRC == 75)/(nROW * nCOL)
#     np.sum(nlm_RRC == 100)/(nROW * nCOL)
    
    #####
    
    ext = '50x50'
    
    if ext == '10x10':
    
        fac = 1
        
    if ext == '30x30':
    
        fac = 9
    
    if ext == '50x50':
    
        fac = 25
        
    
    nlm_RE = nlmpy.randomElementNN(int(nROW), int(nCOL), 1000*fac)
    nlm_RE = ((nlmpy.classifyArray(nlm_RE, [.125,.25,.625]) + 1) * 25) + 25
    
    np.unique(nlm_RE)
    np.sum(nlm_RE == 50)/(nROW * nCOL)
    np.sum(nlm_RE == 75)/(nROW * nCOL)
    np.sum(nlm_RE == 100)/(nROW * nCOL)
    
    np.place(nlm_RE, STREAM01_ARRAY == 1, 25)
    
    np.unique(nlm_RE)
    np.sum(nlm_RE == 25)/(nROW * nCOL)
    np.sum(nlm_RE == 50)/(nROW * nCOL)
    np.sum(nlm_RE == 75)/(nROW * nCOL)
    np.sum(nlm_RE == 100)/(nROW * nCOL)
    
    #####
    
    nlm_RC = nlmpy.randomClusterNN(int(nROW), int(nCOL), .3825, n = '8-neighbourhood')
    nlm_RC = ((nlmpy.classifyArray(nlm_RC, [.125,.25,.625]) + 1) * 25) + 25
    
    np.unique(nlm_RC)
    np.sum(nlm_RC == 50)/(nROW * nCOL)
    np.sum(nlm_RC == 75)/(nROW * nCOL)
    np.sum(nlm_RC == 100)/(nROW * nCOL)
    
    np.place(nlm_RC, STREAM01_ARRAY == 1, 25)
    
    np.unique(nlm_RC)
    np.sum(nlm_RC == 25)/(nROW * nCOL)
    np.sum(nlm_RC == 50)/(nROW * nCOL)
    np.sum(nlm_RC == 75)/(nROW * nCOL)
    np.sum(nlm_RC == 100)/(nROW * nCOL)
    
    #####
     
#     plt.close()
#     
#     fig = plt.figure()
#     ax = fig.add_subplot(221)
#     ax.imshow(nlm_R, interpolation="bicubic")
#     
#     ax2 = fig.add_subplot(222)
#     ax2.imshow(nlm_RRC, interpolation="bicubic")
#     
#     ax = fig.add_subplot(223)
#     ax.imshow(nlm_RE, interpolation="bicubic")
#     
#     ax2 = fig.add_subplot(224)
#     ax2.imshow(nlm_RC, interpolation="bicubic")
     
    #####

#     dst_filename = '/home/lucas/Desktop/pyPICS/nlm_R.tiff'
    dst_filename = '/home/streib/pY_rASTER/nlm_R.tiff'

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
    dataset.GetRasterBand(1).WriteArray(nlm_R)
    
    dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_R), np.amax(nlm_R), np.mean(nlm_R), np.std(nlm_R))
    dataset.GetRasterBand(1).SetNoDataValue(-999)
    
    print(dataset.GetRasterBand(1).ReadAsArray())
    
    dataset.FlushCache()  # Write to disk.
    
    raster = gdal.Open(dst_filename,gdal.GA_ReadOnly)
    
    raster_array = raster.ReadAsArray()
    
    print raster_array
    
    
#     conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
    conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")

    cursor = conn.cursor()
    
    os.environ['PGPASSWORD'] = '1gis!gis1' 
    
#     cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network.nlmr_testarea_50x50_'+str(x)+' | psql -d DB_PhD -h localhost -U lucas '
#     subprocess.call(cmds, shell=True)
#     
#     cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
#     subprocess.call(cmds, shell=True)
# 
#     cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network.nlmr_testarea_50x50_'+str(x)+'_resamp | psql -d DB_PhD -h localhost -U lucas '
#     subprocess.call(cmds, shell=True)
    
    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_125025625.nlmr_testarea_50x50_'+str(x)+' | psql -d DB_PhD -h localhost -U streib_lucas '
    subprocess.call(cmds, shell=True)
    
    cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
    subprocess.call(cmds, shell=True)

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_125025625.nlmr_testarea_50x50_'+str(x)+'_resamp | psql -d DB_PhD -h localhost -U streib_lucas '
    subprocess.call(cmds, shell=True)
    
    
    #####

#     dst_filename = '/home/lucas/Desktop/pyPICS/nlm_RRC.tiff'
#     
#     wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
#     
#     driver = gdal.GetDriverByName('GTiff')
#     
#     dataset=[]
#     
#     dataset = driver.Create(
#         dst_filename,
#         int(nCOL),
#         int(nROW),
#         1,
#         gdal.GDT_Float32)
#     
#     dataset.SetGeoTransform((
#         X_ll, 
#         cellSIZE, 
#         0,                    
#         Y_ll,
#         0,
#         -cellSIZE))
#     
#     dataset.FlushCache()  # Write to disk.
#     
#     dataset.SetProjection(wkt_projection)
#     dataset.GetRasterBand(1).WriteArray(nlm_RRC)
#     
#     dataset.GetRasterBand(1).SetStatistics(np.amin(nlm_RRC), np.amax(nlm_RRC), np.mean(nlm_RRC), np.std(nlm_RRC))
#     dataset.GetRasterBand(1).SetNoDataValue(-999)
#     
#     print(dataset.GetRasterBand(1).ReadAsArray())
#     
#     dataset.FlushCache()  # Write to disk.
#     
#     raster = gdal.Open(dst_filename,gdal.GA_ReadOnly)
#     
#     raster_array = raster.ReadAsArray()
#     
#     print raster_array
#     
#     
#     conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
#     cursor = conn.cursor()
#     
#     os.environ['PGPASSWORD'] = '1gis!gis1' 
#     
#     cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network.nlmrrc_testarea_50a75_20x20_'+str(x)+' | psql -d DB_PhD -h localhost -U lucas '
#     subprocess.call(cmds, shell=True)

    #####
    
#     dst_filename = '/home/lucas/Desktop/pyPICS/nlm_RC.tiff'
    dst_filename = '/home/streib/pY_rASTER/nlm_Rc.tiff'

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
    
#     conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
    conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")
    cursor = conn.cursor()
    
    os.environ['PGPASSWORD'] = '1gis!gis1' 
    
#     cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network.nlmrc_testarea_50x50_'+str(x)+' | psql -d DB_PhD -h localhost -U lucas '
#     subprocess.call(cmds, shell=True)
#     
#     cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
#     subprocess.call(cmds, shell=True)
# 
#     cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network.nlmrc_testarea_50x50_'+str(x)+'_resamp | psql -d DB_PhD -h localhost -U lucas '
#     subprocess.call(cmds, shell=True)

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_125025625.nlmrc_testarea_50x50_'+str(x)+' | psql -d DB_PhD -h localhost -U streib_lucas '
    subprocess.call(cmds, shell=True)
    
    cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
    subprocess.call(cmds, shell=True)

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_125025625.nlmrc_testarea_50x50_'+str(x)+'_resamp | psql -d DB_PhD -h localhost -U streib_lucas '
    subprocess.call(cmds, shell=True)   
    #####
    
#     dst_filename = '/home/lucas/Desktop/pyPICS/nlm_RE.tiff'
    dst_filename = '/home/streib/pY_rASTER/nlm_RE.tiff'

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
    
#     conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
    conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")
    cursor = conn.cursor()
    
    os.environ['PGPASSWORD'] = '1gis!gis1' 
    
#     cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network.nlmre_testarea_50x50_'+str(x)+' | psql -d DB_PhD -h localhost -U lucas '
#     subprocess.call(cmds, shell=True)
#     
#     cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
#     subprocess.call(cmds, shell=True)
# 
#     cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network.nlmre_testarea_50x50_'+str(x)+'_resamp | psql -d DB_PhD -h localhost -U lucas '
#     subprocess.call(cmds, shell=True)
        
    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename + '" -F stream_network_125025625.nlmre_testarea_50x50_'+str(x)+' | psql -d DB_PhD -h localhost -U streib_lucas '
    subprocess.call(cmds, shell=True)
    
    cmds = 'gdalwarp -tr 100 100 -r average "' + dst_filename + '" "' + dst_filename[:-5] + '_resamp.tif" -overwrite'
    subprocess.call(cmds, shell=True)

    cmds = 'raster2pgsql -s 25832 -I -C -M "' + dst_filename[:-5] + '_resamp.tif" -F stream_network_125025625.nlmre_testarea_50x50_'+str(x)+'_resamp | psql -d DB_PhD -h localhost -U streib_lucas '
    subprocess.call(cmds, shell=True)
        
