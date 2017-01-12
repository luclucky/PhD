'''
Created on 9 Jan 2017

@author: lucas
'''

import xyCell
import math

ncols = 3
nrows = 3
xmin = -180.0
xmax = 180.0
ymin = -90.0
ymax = 90.0
cell = [1, 2, 3, 4, 5, 6, 7, 8, 9]

xyCell.doXYFromCell(ncols,nrows,xmin,xmax,ymin,ymax,cell)
 
xyFromCell <- function(object, cell, spatial=FALSE) {
    if (rotated(object)) {
        xy <- object@rotation@transfun( 
            cbind(x=colFromCell(object, cell), y=rowFromCell(object, cell)) 
        )
        
    } else {
        e <- object@extent 
        
        xy = xyCell.doXYFromCell(ncols,nrows,xmin,xmax,ymin,ymax,cell)
        
        dimnames(xy) <- list(NULL, c("x", "y"))
    }

    if (spatial) {
        xy <- SpatialPoints(stats::na.omit(xy), crs(object))
    }
    return(xy)
}