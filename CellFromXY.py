'''
Created on 16 Jan 2017

@author: lucas
'''

def cellFromXY(raster, dd):
    
    geoTransform = raster.GetGeoTransform()
    xmin = geoTransform[0]
    ymin = geoTransform[3]
    xmax = xmin + geoTransform[1] * raster.RasterXSize
    ymax = ymin + geoTransform[5] * raster.RasterYSize
    nrows = raster.RasterXSize
    ncols = raster.RasterYSize    
    
    x = dd[0]
    y = dd[1] 

    cell = xyCell.doCellFromXY(ncols, nrows, xmin, xmax, ymin, ymax, x, y)

    return(cell)

