'''
Created on 1 Feb 2017

@author: lucas
'''

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
#raster = importr('raster')


def rSPDistance(tr, start, aim, theta, totalNet="net", method=1):

    if(theta < 0 | theta > 20):
        
        return('theta value out of range (between 0 and 20)')
   
    if(method != 1 and method != 2):
        
       return("method should be either 1 or 2")
    
    cellnri = cell_From_XY(tr, start)
    cellnrj = cell_From_XY(tr, aim)
    
    transition = transitionSolidify(tr)
    
    tc = tr.transitionCells

    ci = [tc.index(x) if x in cellnri else None for x in cellnri]
    cj = [tc.index(x) if x in cellnrj else None for x in cellnrj]
        
    trM = transitionMatrix(tr, inflate=False)
    
    rsP = rSPDist(trM, ci, cj, theta, totalNet, method)

    return(rsP)


def cell_From_XY(tr, sP): 

    inherits = rpy2.robjects.r['inherits']

    if (str(inherits(sP, 'SpatialPoints'))[4:9] == 'TRUE'):
  
        coordinates = rpy2.robjects.r['coordinates']

        sP = coordinates(sP)
        
        x = sP[0]
        y = sP[1]
        
    is_null = rpy2.robjects.r['is.null']
    dim = rpy2.robjects.r['dim']
    asMATRIX = rpy2.robjects.r['as.matrix']

    if (str(is_null(dim(asMATRIX(sP))))[4:9] == 'TRUE'):
          
        x = sP[0]
        y = sP[1] 
    
    else: 
    
        x = sP[0]
        y = sP[1] 
  
    cell = xyCell.doCellFromXY(tr.ncols, tr.nrows, tr.xmin, tr.xmax, tr.ymin, tr.ymax, x, y)
  
    return(cell)


def transitionSolidify(tr):

    y = transitionMatrix(tr,inflate=False).toarray()

    y_mean = [np.mean(y[i]) for i in range(len(y))]

    select = [i for i, x in enumerate([y_mean[i] > 1e-300 for i in range(len(y_mean))]) if x]

    tr.transitionCells = [tr.transitionCells[i] for i in select]

    tr.transitionMatrix = transitionMatrix(tr,inflate=False)[select][select]
    
    return(tr)


def rSPDist(trM, ci, cj, theta, totalNet, method):

    trR = sparse.csc_matrix(trM)
    trR.data = 1/trR.data

    nr = trR.get_shape()
    
    id = np.zeros((nr), float)
    np.fill_diagonal(id, 1.0)
    
    ID = sparse.csc_matrix(id)
    
    rs = 1 / trM.sum(axis=1)
    P = sparse.csc_matrix(trM.multiply(rs))
  
  
    if(method == 1):
  
        W = sparse.csc_matrix(trR)
        W.data = np.exp(-theta * trR.data) 
        W = W.multiply(P)
    
    else:
    
        return('method 2 not yet implemented')
        #adj = adjacencyFromTransition(trR)
        #W <- trR
        #W[adj] <- exp(-theta * -log(P[adj])) #if the value is 1 then you get a natural random walk
  
    D = np.zeros((len(ci),len(cj)), float)
  
    for j in range(len(cj)):
    
        ij = np.zeros((nr), float)
        ij.fill(1.0)
        ij[cj[j]] = ij[cj[j]] * 0
    
        ij[cj[j],cj[j]] = 0
        
        Wj = sparse.csc_matrix(W.multiply(ij).toarray())

        #Wj.toarray()
        
        IdMinusWj = ID - Wj
        
        ej = nr[1] * [0]
               
        ej[cj[j]] = 1
        
        zcj = np.linalg.solve(IdMinusWj.toarray(), ej)
            
        for i in range(len(ci)):
         
            ei = nr[1] * [0]
               
            ei[ci[i]] = 1
        
            zci = np.linalg.solve(np.transpose(IdMinusWj).toarray(),ei)
                                    
            zcij = (zcj * ei).sum()
    
            N = sparse.csc_matrix(np.dot(np.dot(np.diag(zci), Wj.toarray()),np.diag(zcj)) / zcij)

            if(totalNet == "net"):
      
                N = ((N - np.transpose(N)) * 0.5) * 2
      
                N.data = np.where(N.data > 0, N.data, 0) 
      

      # Computation of the cost dij between node i and node j
            D[i,j] = trR.multiply(N).sum(axis=1).sum()
      
    return(D)


def transitionMatrix(tr, inflate=False, nc=0):

    if(inflate and (len(tr.transitionCells) != tr.nrows*tr.ncols)):
    
        trM <- Matrix(0, nc, nc)
        cells <- tr.transitionCells
        tr[cells,cells] <- tr.transitionMatrix
    
    if(not inflate | len(tr.transitionCells) == nc):
        
        trM = tr.transitionMatrix
    
    return(trM)

    
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
            self.ymax = geotransform[3]
            self.xmax = geotransform[0] + geotransform[1] * raster.RasterXSize
            self.ymin = geotransform[3] + geotransform[5] * raster.RasterYSize
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
        
    #directions = 8 
        
    adj = adjacent(raster, cells=cells, pairs=True, target=cells, directions=directions)
    adj = [map(int,adj[0]), map(int,adj[1])]

    #symm = False

    if(symm):
        
        adj0 = [i for i,j in zip(adj[0],adj[1]) if i < j]
        adj1 = [j for i,j in zip(adj[0],adj[1]) if i < j]
        
        adj[0] = adj0
        adj[1] = adj1
            
    dataVals = [cellsDV[i-1] for i in adj[0]], [cellsDV[i-1] for i in adj[1]]    
    
    #def transFunc(i):   
    #    j = np.mean(i)  
    #    return j        
    
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
    
    #TR.__dict__

    return(TR)
    