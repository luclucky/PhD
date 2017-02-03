'''
Created on 6 Jan 2017

@author: lucas
'''


def isgloballonglat(x):
        
    geotransform = x.GetGeoTransform() 

    res = False
        
    if (geotransform[0] + geotransform[1] * x.RasterXSize == 180) & (geotransform[0] == -180):
                    
        res = True
      
    return(res)


def adjacent(raster, cells, directions=8, pairs=True, target=None, sorted=False, include=False, id=False):

    r = res(raster)
    xy = xyFromCell(raster, cells)
    
    if (directions==4):
        
        if (include):
            d = xy[0], [x-r[0] for x in xy[0]], [x+r[0] for x in xy[0]], xy[0], xy[0], xy[1], xy[1], xy[1], [x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]
            d = [j for i in d for j in i]
            
        else:
            d = [x-r[0] for x in xy[0]],[x+r[0] for x in xy[0]], xy[0], xy[0], xy[1], xy[1], [x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]
            d = [j for i in d for j in i]
        
        
    if (directions==8):
        
        if (include):
            d = xy[0], [x-r[0] for x in xy[0]]*3, [x+r[0] for x in xy[0]]*3, xy[0], xy[0], xy[1], [j for i in [x+r[1] for x in xy[1]], xy[1], [x-r[1] for x in xy[1]] in d for j in i]*2, [x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]
            d = [j for i in d for j in i]

        else:
            d = [x-r[0] for x in xy[0]]*3, [x+r[0] for x in xy[0]]*3, xy[0], xy[0], [j for i in [x+r[1] for x in xy[1]], xy[1], [x-r[1] for x in xy[1]] for j in i]*2, [x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]
            d = [j for i in d for j in i]
                                
    if (directions==16):
        
        r2 = [x*2 for x in r]
        
        if (include):
            d = xy[0], [x-r2[0] for x in xy[0]]*2, [x+r2[0] for x in xy[0]]*2, [x-r[0] for x in xy[0]]*5, [x+r[0] for x in xy[0]]*5, xy[0], xy[0], xy[1], [j for i in [[x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]] for j in i]*2, [j for i in [[x+r2[1] for x in xy[1]], [x+r[1] for x in xy[1]],  xy[1], [x-r[1] for x in xy[1]], [x-r2[1] for x in xy[1]]] for j in i]*2, [x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]
            d = [j for i in d for j in i]

        else:
            d = [x-r2[0] for x in xy[0]]*2, [x+r2[0] for x in xy[0]]*2, [x-r[0] for x in xy[0]]*5, [x+r[0] for x in xy[0]]*5, xy[0], xy[0], [j for i in [[x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]] for j in i]*2, [j for i in [[x+r2[1] for x in xy[1]], [x+r[1] for x in xy[1]],  xy[1], [x-r[1] for x in xy[1]], [x-r2[1] for x in xy[1]]] for j in i]*2, [x+r[1] for x in xy[1]], [x-r[1] for x in xy[1]]
            d = [j for i in d for j in i]

    if (include):
        directions = directions + 1
  
    dd = [d[0:len(d)/2] , d[len(d)/2:len(d)]]
    
    if isgloballonglat(raster):
        
        dd[0] = [(i+180) % 360 - 180 for i in dd[0]] 

    if (pairs):
        
        cell = cells*directions
         
        if (id):
            ID = range(1, len(cells)) * directions
            #ID.sort()
          
            ddd = [ID, cell, cellFromXY(raster, dd)]
          
            ind = [i for i,val in enumerate(ddd[2]) if val==-99999]
            
            ddd[0] = [i for j, i in enumerate(ddd[0]) if j not in ind]  
            ddd[1] = [i for j, i in enumerate(ddd[1]) if j not in ind]  
            ddd[2] = [i for j, i in enumerate(ddd[2]) if j not in ind]               

#           if (! is.null(target)) {
#             d <- d[d[,3] %in% target, ]
#           }
          
        else:
            ddd = [cell, cellFromXY(raster, dd)]
          
            ind = [i for i,val in enumerate(ddd[1]) if val==-99999]
            
            ddd[0] = [i for j, i in enumerate(ddd[0]) if j not in ind]  
            ddd[1] = [i for j, i in enumerate(ddd[1]) if j not in ind]  
            
#           if (! is.null(target)) {
#             d <- d[d[,2] %in% target, ]
#           }
        
        if (sorted):
            
            ddd = zip(ddd[0],ddd[1])
            ddd.sort()
            ddd = zip(*ddd)
          
    else:
         
        ddd = [cell, cellFromXY(raster, dd)]
          
        ind = [i for i,val in enumerate(ddd[1]) if val==-99999]
            
        ddd[0] = [i for j, i in enumerate(ddd[0]) if j not in ind]  
        ddd[1] = [i for j, i in enumerate(ddd[1]) if j not in ind]         
        
#         if (! is.null(target)) 
#           d <- intersect(d, target)
        
        if (sorted): 
            dd = zip(ddd[0],ddd[1])
            ddd.sort()
            ddd = zip(*ddd)        
            
    return(ddd)

