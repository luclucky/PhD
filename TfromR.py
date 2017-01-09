
import gdal, ogr, os, osr
import numpy as np
from skimage.graph import route_through_array
import gdal, ogr, os, osr
import numpy as np
from gdalconst import * 
from scipy import sparse

def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):

    array = array[::-1]

    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(25832)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

rasterOrigin = (0,0)
pixelWidth = 10
pixelHeight = 10
newRasterfn = '/home/lucas/PhD/test.tif'
array = np.array([[ 1, 2, 3],[ 4, 5, 6],[ 7, 8, 9]])

#####

raster = gdal.Open('/home/lucas/PhD/test.tif')

def TM_from_R(raster, transFunc, directions, symm):
    
    prj=raster.GetProjection()
    srs=osr.SpatialReference(wkt=prj)
    
    geotransform = raster.GetGeoTransform() 
    
    class TransitionLayer:

        def __init__(self, raster, geotransform):
            self.nrows = raster.RasterXSize
            self.ncols = raster.RasterYSize
            self.crs = srs.GetAttrValue("AUTHORITY", 1)
            self.rasterOrigin = geotransform[0],geotransform[3]
            self.pixelWidth = geotransform[1]
            self.pixelHeight = geotransform[5]
            self.transitionMatrix = sparse.csc_matrix(np.zeros(shape = (raster.RasterXSize * raster.RasterYSize, raster.RasterXSize * raster.RasterYSize)))
            self.transitionCells = range(1, raster.RasterXSize * raster.RasterYSize + 1)
        
    TR = TransitionLayer(raster, geotransform)
    
    #TR.__dict__
    
    Cells = filter(lambda x: x!=None, [y for x in np.array(raster.GetRasterBand(1).ReadAsArray()).tolist() for y in x])
        
    
    
    
    
    
    
    
    
    
    
    
    
    