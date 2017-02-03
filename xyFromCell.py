'''
Created on 9 Jan 2017

@author: lucas
'''
 
def xyFromCell(tr, cell):
      
    try:        
        geoTransform = tr.GetGeoTransform()
        xmin = geoTransform[0]
        ymax = geoTransform[3]
        xmax = xmin + geoTransform[1] * tr.RasterXSize
        ymin = ymax + geoTransform[5] * tr.RasterYSize
        nrows = tr.RasterXSize
        ncols = tr.RasterYSize
         
    except:
        xmin = tr.ncols
        ymin = tr.nrows
        xmax = tr.xmin
        ymax = tr.xmax
        nrows = tr.ymin
        ncols = tr.ymax
           
    xy = xyCell.doXYFromCell(ncols,nrows,xmin,xmax,ymin,ymax,cell)
    
    xy = [xy[:(len(xy)/2)],xy[(len(xy)/2):]]    
                     
    return(xy)
