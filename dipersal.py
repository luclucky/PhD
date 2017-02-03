'''
Created on 2 Feb 2017

@author: lucas
'''

from randShortPath import randShortPath as rSP
import numpy as np
import gdal, ogr, os, osr

raster = gdal.Open('/home/lucas/PhD/r.tif')
raster_test = gdal.Open('/home/lucas/PhD/test.tif')


# def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
# 
#     array = array[::-1]
# 
#     cols = array.shape[1]
#     rows = array.shape[0]
#     originX = rasterOrigin[0]
#     originY = rasterOrigin[1]
# 
#     driver = gdal.GetDriverByName('GTiff')
#     outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
#     outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
#     outband = outRaster.GetRasterBand(1)
#     outband.WriteArray(array)
#     outRasterSRS = osr.SpatialReference()
#     outRasterSRS.ImportFromEPSG(25832)
#     outRaster.SetProjection(outRasterSRS.ExportToWkt())
#     outband.FlushCache()
# 
# rasterOrigin = (0,0)
# pixelWidth = 10
# pixelHeight = 10
# newRasterfn = '/home/lucas/PhD/test.tif'
# array = np.array([[ 1, 2, 3],[ 4, 5, 6],[ 7, 8, 9]])


sP = [[10.0, 0.0], [30.0, 20.0]]

def transFunc(i):   
    j = np.mean(i)  
    return j       
    
tr1 = rSP.TM_from_R(raster_test, transFunc, directions = 8, symm = False)
tr1 = rSP.TM_from_R(raster, transFunc, directions = 8, symm = False)

tr1.__dict__
tr1.transitionMatrix.toarray()

tr = tr1
start = sP
aim = sP
theta = 1
totalNet="net"
method=1

aaa = rSP.rSPDistance(tr, start, aim, theta, totalNet="net", method=1)



