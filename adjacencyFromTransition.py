'''
Created on 25 Jan 2017

@author: lucas
'''



def adjacencyFromTransition(x):

    tc = x.transitionCells
    tm = x.transitionMatrix
    
    dgTMatrix = rpy2.robjects.r['as(*,"dgTMatrix")']

    
    transition.dgT <- as(tm,"dgTMatrix")
    
    adj <- cbind(transition.dgT@i+1,transition.dgT@j+1)
    adj <- cbind(tc[adj[,1]], tc[adj[,2]])
    return(adj)


.adjacentUD <- function(x, cells, ngb, include) {
  # ngb should be a matrix with 
  # one and only one cell with value 0 (the focal cell), 
  # at least one cell with value 1 (the adjacent cells)
  # cells with other values are ignored (not considered adjacent)
  rs <- res(x)
  
  rn <- raster(ngb)
  center <- which(values(rn)==0)
  if (include) {
    ngb[center] <- 1
  }
  rc <- rowFromCell(rn, center)
  cc <- colFromCell(rn, center)
  
  xngb <- yngb <- ngb
  xngb[] <- rep(1:ncol(ngb), each=nrow(ngb)) - cc 
  yngb[] <- rep(nrow(ngb):1, ncol(ngb)) - (nrow(ngb)-rc+1)
  ngb[ngb != 1] <- NA
  xngb <- stats::na.omit(as.vector( xngb * rs[1] * ngb))
  yngb <- stats::na.omit(as.vector( yngb * rs[2] * ngb))
  
  xy <- xyFromCell(x, cells)
  X <- apply(xy[,1,drop=FALSE], 1, function(z) z + xngb )
  Y <- apply(xy[,2,drop=FALSE], 1, function(z) z + yngb )
  
  c(as.vector(X), as.vector(Y))
}
