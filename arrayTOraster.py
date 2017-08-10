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


dst_filename = '/home/lucas/Desktop/pyPICS/xxxx.tiff'
x_pixels = 120 # number of pixels in x
y_pixels = 120  # number of pixels in y
PIXEL_SIZE = 100

x_min = 316050.0  
y_max = 5506050.0  
wkt_projection = 'PROJCS["ETRS89 / UTM zone 32N",GEOGCS["ETRS89",DATUM["European_Terrestrial_Reference_System_1989",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],AUTHORITY["EPSG","6258"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4258"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",9],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],AUTHORITY["EPSG","25832"],AXIS["Easting",EAST],AXIS["Northing",NORTH]]'

driver = gdal.GetDriverByName('GTiff')

dataset = driver.Create(
    dst_filename,
    x_pixels,
    y_pixels,
    1,
    gdal.GDT_Float32)

dataset.SetGeoTransform((
    x_min, 
    PIXEL_SIZE, 
    0,                    
    y_max,
    0,
    -PIXEL_SIZE))

dataset.FlushCache()  # Write to disk.

dataset.SetProjection(wkt_projection)
dataset.GetRasterBand(1).WriteArray(spaSTRESS_gRID)

dataset.GetRasterBand(1).SetStatistics(np.amin(spaSTRESS_gRID), np.amax(spaSTRESS_gRID), np.mean(spaSTRESS_gRID), np.std(spaSTRESS_gRID))
dataset.GetRasterBand(1).SetNoDataValue(-999)

print(dataset.GetRasterBand(1).ReadAsArray())

dataset.FlushCache()  # Write to disk.


