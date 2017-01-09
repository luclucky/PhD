'''
Created on 3 Jan 2017

@author: lucas

'''

from osgeo import gdal

gtif = gdal.Open( "/home/lucas/Desktop/rasterTEST.tif" )

print gtif.GetMetadata()
