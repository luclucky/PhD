'''
Created on 25 Jan 2017

@author: lucas
'''

sP = [[10.0, 0.0], [30.0, 20.0]]

def rSPDistance(tr, start, aim, theta, totalNet="net", method=1)

    if(theta < 0 | theta > 20):
        
        return('theta value out of range (between 0 and 20)')
   
    if(method != 1 and method != 2):
        
       return("method should be either 1 or 2")
    
    cellnri = cellFromXY(tr, start)
    cellnrj = cellFromXY(tr, aim)
    
    transition = transitionSolidify(tr)
    
    tc = tr.transitionCells

    ci = [tc.index(x) if x in cellnri else None for x in cellnri]
    cj = [tc.index(x) if x in cellnrj else None for x in cellnrj]
        
    trM = transitionMatrix(tr, inflate=False)
    
    .rSPDist(trM, ci, cj, theta, totalNet, method)


def cellFromXY(tr, sP): 

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


def rSPDist(trM, ci, cj, theta, totalNet, method)

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
  
    for(j in range(len(cj))):
    
        ij = np.zeros((nr), float)
        ij.fill(1.0)
        ij[cj[j]] = ij[cj[j]] * 0
    
        ij[cj[j],cj[j]] = 0
        
        W.toarray()

        Wj = sparse.csc_matrix(W.multiply(ij).toarray())

        #Wj.toarray()
        
        IdMinusWj = ID - Wj
        
               
        ej <- rep(0,times=nr)
        ej[cj[j]] <- 1
        zcj <- solve(IdMinusWj, ej)
    
        for(i in 1:length(ci))
        {
            ei <- rep(0,times=nr)
            ei[ci[i]] <- 1
            zci <- solve(t(IdMinusWj),ei)
            zcij <- sum(ei*zcj)

            N <- (Diagonal(nr, as.vector(zci)) %*% Wj %*% Diagonal(nr, as.vector(zcj))) / zcij
      
      if(totalNet == "net"):
      
        N <- skewpart(N) * 2 #N is here the NET number of passages, like McRae-random walk
        N@x[N@x<0] <- 0
      

      # Computation of the cost dij between node i and node j
            D[i,j] <-  sum(trR * N)
            
    }
    }
    
    return(D)