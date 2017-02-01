
import gdal, ogr, os, osr
import numpy as np
from skimage.graph import route_through_array
from gdalconst import * 
from scipy import sparse
import xyCell
import numpy as np
import rpy2

from rpy2.robjects.packages import importr

Matrix = importr('Matrix')
stats = importr('stats')
raster = importr('raster')

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
            self.xmin = geotransform[0]
            self.ymin = geotransform[3]
            self.xmax = geotransform[0] + geotransform[1] * raster.RasterXSize
            self.ymax = geotransform[3] + geotransform[5] * raster.RasterYSize
            self.pixelWidth = geotransform[1]
            self.pixelHeight = geotransform[5]
            self.transitionMatrix = sparse.csc_matrix(np.zeros(shape = (raster.RasterXSize * raster.RasterYSize, raster.RasterXSize * raster.RasterYSize)))
            self.transitionCells = range(1, raster.RasterXSize * raster.RasterYSize + 1)
            self.Values = ''

        
    TR = TransitionLayer(raster, geotransform)

    transitionMatr = TR.transitionMatrix
        
    cells = filter(lambda x: x!=None, [y for x in np.array(raster.GetRasterBand(1).ReadAsArray()).tolist() for y in x])
    cellsDV = cells
    #cells.sort()
        
    directions = 8 # comment 
        
    adj = adjacent(raster, cells=cells, pairs=True, target=cells, directions=directions)

    symm = False # comment

    if(symm):
        
        adj0 = [i for i,j in zip(adj[0],adj[1]) if i < j]
        adj1 = [j for i,j in zip(adj[0],adj[1]) if i < j]
        
        adj[0] = adj0
        adj[1] = adj1
            
    dataVals = [cellsDV[i-1] for i in adj[0]], [cellsDV[i-1] for i in adj[1]]    
    
    def transFunc(i):   # comment
        j = np.mean(i)  # comment
        return j        # comment
    
    trans_values = [transFunc(i) for i in zip(dataVals[0],dataVals[1])] 
    
    if trans_values < 0:
        print("WARNING: transition function gives negative values")
    
    j = 0

    for i in zip(adj[0],adj[1]):
        
        transitionMatr[i[0]-1, i[1]-1] = trans_values[j]

        j = j+1
        
    #transitionMatr.toarray() 
    
    if(symm):
        
        from rpy2.robjects.numpy2ri import numpy2ri
        rpy2.robjects.numpy2ri.activate()
        
        forceSymmetric = rpy2.robjects.r['forceSymmetric']
        
        asMATRIX = rpy2.robjects.r['as.matrix']

        transitionMatr = sparse.csr_matrix(np.array(asMATRIX(forceSymmetric(transitionMatr.toarray()))))
        
    TR.transitionMatrix = transitionMatr

    TR.Values = "conductance"
    
    TR.__dict__

    return(TR)
    
}

    
    
    
    
    
    
    
    