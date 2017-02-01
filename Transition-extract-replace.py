'''
Created on 25 Jan 2017

@author: lucas
'''


# 
# setMethod ("transitionMatrix", signature(x = "TransitionLayer", inflate="logical"),
#     function(x, inflate)
#     {
#         .tr(x, inflate, ncell(x))
#     }
# )
# 
# setMethod ("transitionMatrix", signature(x = "TransitionData", inflate="missing"),
#     function(x)
#     {
#         .tr(x=x, inflate=FALSE, nc=0)
#     }
# )

def transitionMatrix(tr, inflate=False, nc=0):

    if(inflate and (len(tr.transitionCells) != tr.nrows*tr.ncols)):
    
        trM <- Matrix(0, nc, nc)
        cells <- tr.transitionCells
        tr[cells,cells] <- tr.transitionMatrix
    
    if(not inflate | len(tr.transitionCells) == nc):
        
        trM = tr.transitionMatrix
    
    return(trM)

