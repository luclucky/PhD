'''
Created on 16 Jan 2017

@author: lucas
'''

def cellFromXY(tr, dd):
    
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
    
    x = dd[0]
    y = dd[1] 

    cell = xyCell.doCellFromXY(ncols, nrows, xmin, xmax, ymin, ymax, x, y)

    return(cell)
