'''
Created on 12 Jan 2017

@author: lucas
'''
                
def xres(raster):
        
    nrows = raster.RasterXSize
    ncols = raster.RasterYSize
    
    geoTransform = raster.GetGeoTransform()
    xmin = geoTransform[0]
    ymax = geoTransform[3]
    xmax = xmin + geoTransform[1] * raster.RasterXSize
    ymin = ymax + geoTransform[5] * raster.RasterYSize
            
    return(xmax - xmin) / ncols

def yres(raster):
    
    nrows = raster.RasterXSize
    ncols = raster.RasterYSize
    
    geoTransform = raster.GetGeoTransform()
    xmin = geoTransform[0]
    ymax = geoTransform[3]
    xmax = xmin + geoTransform[1] * raster.RasterXSize
    ymin = ymax + geoTransform[5] * raster.RasterYSize
    
    return (ymax - ymin) / nrows

def res(raster):
    
    nrows = raster.RasterXSize
    ncols = raster.RasterYSize
    
    geoTransform = raster.GetGeoTransform()
    xmin = geoTransform[0]
    ymax = geoTransform[3]
    xmax = xmin + geoTransform[1] * raster.RasterXSize
    ymin = ymax + geoTransform[5] * raster.RasterYSize
    
    xr = (xmax - xmin) / ncols 
    yr = (ymax - ymin) / nrows
    
    return [xr, yr]

