'''
Created on 9 Jan 2017

@author: lucas
'''
 
def xyFromCell(raster, cell):
            
    geoTransform = raster.GetGeoTransform()
    xmin = geoTransform[0]
    ymin = geoTransform[3]
    xmax = xmin + geoTransform[1] * raster.RasterXSize
    ymax = ymin + geoTransform[5] * raster.RasterYSize
    nrows = raster.RasterXSize
    ncols = raster.RasterYSize
                
    xy = xyCell.doXYFromCell(ncols,nrows,xmin,xmax,ymin,ymax,cell)
    
    xy = [xy[:(len(xy)/2)],xy[(len(xy)/2):]]    
                     
    return(xy)
