#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:03:13 2018

@author: henriette
"""

import numpy as np
from  osgeo import ogr
from gurobipy import *
import time
import networkx as nx
# import resource



################################################################################
#                                                                              #
#                              run simulations                                 #
#                                                                              #
################################################################################
      
Nmin = 20
TimeHorizon = 30
disp_perc = 0.25 # wenn disp_perc erhoeht wird, muss auch upper bound der flow variables angepasst werden
inf = 8888
growth = 1
numberofruns = 1

data = '50x50'
sp_type = '_nlmr'

maxcost = 1250
mort_perc = 0.0008

timelimit = 360000
result = []
Times = []


def lowerBounds(): 

    start_sp, aim_sp, cost_sp, id_sp, habitats, Startsets, Endsets = loadData(maxcost, data, sp_type)
    Start = Startsets[k]
    End = Endsets[i]
#    Start = Startsets[0]
#    End = Endsets[1]


    # return 0 time steps, if all EH are also SH
    if np.prod([end in Start for end in End]) == 1:
        result = [0,0.0]
        TEN = nx.DiGraph()
        m = Model()
        G = nx.Graph()
        
    else:
        End = list(set(End) - set(Start)) # remove those EH that are also SH
        start_sp, aim_sp, cost_sp, id_sp, habitats, Start, G, keep, to_delete, keep_index, length_dict = preprocess(TimeHorizon, start_sp, aim_sp, cost_sp, id_sp, habitats, Start, End)

        TEN = constructGraph(TimeHorizon, habitats, start_sp, aim_sp, cost_sp, 
                 Start, End, disp_perc, inf)   
    
        m = buildModel(TEN, Start, End, habitats, TimeHorizon, Nmin, mort_perc, 
                   [], growth, timelimit)
        try:
            m, liste, timesteps, gap =  solve(m, TEN, Start, End, [], [], [], start_sp, 
                                      aim_sp, id_sp)   
            result = [timesteps, gap]
        except:   
            result = [inf, 'infeasible']
        File = open('/home/streib/Schreibtisch/timeit_HH/OutPUT/Starthabitats50x50_Timehorizon'+str(TimeHorizon)+'/Startset'+str(k)+'Endset'+str(i)+'.csv', 'w')
#        File = open('/Users/henriette/Python/IP/speedup/Starthabitats50x50_Timehorizon'+str(TimeHorizon)+'/Startset'+str(k)+'Endset'+str(i)+'.csv', 'w')
        File.write(str(result[0]) + ';' + str(result[1]) + '\n')
                         
    return(result, TEN, m) 
                         

###############################################################################
#                                                                             #
#                            load data                                        #
#                                                                             #
###############################################################################
def loadData(maxcost, data, sp_type):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open('/home/streib/Schreibtisch/timeit_HH/SHPs_2/habitats_shortpath_red'+str(sp_type)+'_testarea_'+str(data)+'_0_start_0_resamp.shp')
    layer = shp.GetLayer()
    
    start_sp = []
    aim_sp = []
    cost_sp = []
    id_sp = []
        
    for i in range(layer.GetFeatureCount()):
        inFeature = layer.GetNextFeature()
    
        startsp = inFeature.GetField('start')
        aimsp = inFeature.GetField('aim')
        costsp = inFeature.GetField('costs')
        idsp = inFeature.GetField('ids')
        
    
        if costsp < maxcost:
            start_sp.append(int(startsp))
            aim_sp.append(int(aimsp))
            cost_sp.append(int(costsp))
            id_sp.append(int(idsp))
    habitatsQual = np.load('/home/streib/Schreibtisch/timeit_HH/habitatsQual.npy')
    
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open('/home/streib/Schreibtisch/timeit_HH/SHPs_2/pts_habitat_red_'+str(data)+'_start_0.shp')
    layer = shp.GetLayer()
    
    habitats = {}


    for i in range(layer.GetFeatureCount()):
        inFeature = layer.GetNextFeature()
    
        habitat_pts = inFeature.GetField('ids')
        
        habitats[int(habitat_pts)] = habitatsQual[int(habitat_pts)-1]
                 
    # load source and sink habitats
                 
    Starthabitats = []
    Startsets = []
            
    for line in open('/home/streib/Schreibtisch/timeit_HH/StartHabitats'+str(data)+'.csv'):
        
        Starthabitats.append(line.split(';'))        
            
    for startset in Starthabitats:
        if '\n' in startset:
            startset.remove('\n')
        
        Start = []
        for start in startset:
            Start.append(int(start))
        Startsets.append(Start)
        
    Endhabitats = []
    Endsets = []

#    for line in open('/Users/henriette/Python/IP/EndHabitats_'+str(lenEnd)+'_'+str(data)+'.csv'):
#        Endhabitats.append(line.split(';'))
#        
#    for endset in Endhabitats:
#        if '\n' in endset:
#            endset.remove('\n')
#        End = []
#        for end in endset:
#            End.append(int(end))
#        Endsets.append(End)

    for end in open('/home/streib/Schreibtisch/timeit_HH/EndHabitats50x50.csv'):
        Endsets.append([int(end)])
        
    return(start_sp, aim_sp, cost_sp, id_sp, habitats, Startsets, Endsets)
    
    
###############################################################################
#                                                                             #
#                            preprocess data                                  #
#                                                                             #
###############################################################################

def preprocess(TimeHorizon, start_sp, aim_sp, cost_sp, id_sp, habitats, Start, End):
    
    G = nx.Graph()
    G.add_nodes_from(habitats)
        
    G.add_edges_from([start_sp[i], aim_sp[i]] for i in range(len(start_sp)))
    
    keep = []
    for end in End:
        path = nx.single_source_shortest_path(G,end)
        length_dict = {}
        for i in G.nodes():
            try:
                length_dict[i] = len(path[i])
            except:
                length_dict[i] = TimeHorizon + 10

        for v in length_dict:
            if length_dict[v] < TimeHorizon + 1:
                    keep.append(v)
                
    to_delete = []
    for v in habitats:
        if v not in keep:
            to_delete.append(v)
            
    for v in to_delete:
        del habitats[v]

    keep_index = []
    for i in range(len(start_sp)):
        if start_sp[i] in keep and aim_sp[i] in keep:
            keep_index.append(i)

    start_new = []
    aim_new = []
    cost_new = []
    id_new = []
    
    for i in keep_index:
        start_new.append(start_sp[i])
        aim_new.append(aim_sp[i])
        cost_new.append(cost_sp[i])
        id_new.append(id_sp[i])
        
    Start = [s for s in Start if s in habitats]
    
    return(start_new, aim_new, cost_new, id_new, habitats, Start, G, keep, to_delete, keep_index, length_dict)



             
###############################################################################
#                                                                             #
#                            construct graph                                  #
#                                                                             #
###############################################################################

def constructGraph(TimeHorizon, habitats, start_sp, aim_sp, cost_sp, Start, 
                   End, disp_perc, inf):
    TEN = nx.DiGraph()
    # bounds:
    for v in habitats:
        for t in range(TimeHorizon+1):
            TEN.add_node(v + 100000*t, bounds = int(habitats[v]*100*disp_perc))
    
            
    # add edges from v_t to v_t+1
    for t in range(TimeHorizon):
        for v in habitats:
            TEN.add_edge(v+100000*t, v+100000*(t+1), cost = 0)        
            
    # add edges from original graph
    for i in range(len(start_sp)):
        for t in range(TimeHorizon):
            TEN.add_edge(start_sp[i] + 100000*t, aim_sp[i] + 100000*(t+1), 
                         cost = cost_sp[i])        
            TEN.add_edge(aim_sp[i] + 100000*t, start_sp[i] + 100000*(t+1), 
                         cost = cost_sp[i])  
                
    # super source 0 
    TEN.add_node(0, bounds = inf)
    for s in Start:     
        TEN.add_edge(0,s, cost = 0)
                    
    # super sinks 999, 1999, ..., 99999
    TEN.add_node(9999999, bounds = inf)
    
    for t in range(TimeHorizon+1):
        TEN.add_node(99999 + 100000*t, bounds = inf)
        TEN.add_edge(99999 + 100000*t, 9999999, cost = 0)
        
    return(TEN)
    
    
    

                         
    
                     
#################################################################################                     
#                                                                               #                  
#                         build model                                           #                  
#                                                                               #
#################################################################################                     
def buildModel(TEN, Start, End, habitats, TimeHorizon, Nmin, mort_perc, 
               VTstress, growth, timelimit):
        
    m = Model()
    
    # define variables
    f = {}
    x ={}
    
    # add variables
    x =m.addVars(TEN.nodes(), vtype = GRB.BINARY, name = "x")
    f = m.addVars(TEN.edges(), lb = 0, ub = 25, name = "f")    
    
    for sink in End:
        for t in range(TimeHorizon+1):
            f[sink+100000*t, 99999 + 100000*t] = m.addVar(name = "f[%s,%s]"%(sink+100000*t, 99999+100000*t))     
    m.update()        
    
    # define obj function
    m.setObjective(quicksum(t*f[99999 + 100000*t, 9999999] for t in range(TimeHorizon+1)), GRB.MINIMIZE)
    
    # define constraints   
    for v in TEN.nodes():
        if v != 0 and v%100000 != 99999:
            c1 = m.addConstr(Nmin*x[v] <= quicksum(f[u,v] for u in TEN.predecessors(v)), name = 'c1[%s]'%v)
        
    for v in habitats:
        for t in range(TimeHorizon):
            # c2 sends biomass from v_t to v_t+1
            if v + 100000*t not in VTstress:
                c2 = m.addConstr(f[v + 100000*t, v + 100000*(t+1)] == growth*quicksum(f[u, v+100000*t]
                    for u in TEN.predecessors(v+100000*t)), name = 'c2[%s]'%(v+100000*t))

                
    for v in TEN.nodes():
        c3 = m.addConstr(quicksum(f[v,w] / (1- TEN.edge[v][w]['cost']*mort_perc) 
            for w in TEN.successors(v)) <= TEN.node[v]['bounds'] * x[v] 
            + quicksum(f[u,v] for u in TEN.predecessors(v)), name = 'c3[%s]'%v)
    for start in Start:
        c4 = m.addConstr(f[0,start] == Nmin, name = 'c4[%s]'%start)

    # c5 - c8 ensure the flow to the super sinks
    for t in range(TimeHorizon+1):       
        for sink in End:        
            c5 = m.addConstr(f[sink + 100000*t, 99999 + 100000*t] == x[sink + 100000*t], 
                             name = 'c5[%s]'%(sink+100000*t))

        c6 = m.addConstr(len(End)*x[99999 + 100000*t] <= quicksum(f[u + 100000*t, 
                         99999 + 100000*t] 
                         for u in End), name = 'c6[%s]'%(99999 + 100000*t))
    
        c7 = m.addConstr(f[99999 + 100000*t, 9999999] == x[99999 + 100000*t], name = 
        'c7[%s]'%(99999+ 100000*t))
        

    c8 = m.addConstr(quicksum(f[99999 + 100000*t, 9999999] for t in 
                              range(TimeHorizon+1)) >= 1, 
                         name = 'c8[%s]'%9999999)

    m.Params.OutputFlag = 0                     
    m.Params.timeLimit = timelimit
        
    return(m)
  






################################################################################
#                                                                              #
#                              solving                                         #
#                                                                              #
################################################################################

def solve(m, TEN, Start, End, Vstress, Tstress, Estress, start_sp, aim_sp, id_sp):
    m.write('newObjFct.lp')                     
    m.optimize()
#    m.printAttr('X')

    gap = m.MIPGap
#    gap = 0
    liste = []
    
    for v in m.getVars():
        if v.X != 0:
            try:
                a,b = (v.Varname).split(',')
                aa = a.replace('f[','')
                bb = b.replace(']','')
                a = int(float(aa))
                b = int(float(bb))
                if a != 0 and b != 9999999 and a+100000 != b:
                    liste += [[a, b, v.X]]
                if b == 9999999:
                    timesteps = int(a/100000)
            except:
                1 == 1

            
        
    ######################################################################
    #                     save path of colonization                      #
    ######################################################################
#need to define file first    
#    file.write('Start:;')
#    for start in Start: 
#        file.write(str(start)+';')
#        
#    file.write('\n End:;')
#    for end in End:
#        file.write(str(end)+';')
#        
#    file.write('\n Timesteps needed;'+ str(timesteps)+ '\n')  
#    file.write('start; aim; individuals; id \n')
#    
#    for e in liste:
#        for i in range(len(start_sp)):
#            if e[0] < timesteps*100000:
#                if e[0]%100000 == start_sp[i] and e[1]%100000 == aim_sp[i]:
#                    e.append(id_sp[i])
#                    
#                    file.write(str(e[0])+';')
#                    file.write(str(e[1])+';')
#                    file.write(str(e[2])+';')
#                    file.write(str(e[3])+'\n')              
#                    
#                elif e[1]%100000 == start_sp[i] and e[0]%100000 == aim_sp[i]:
#                    e.append(id_sp[i])
#                    
#                    file.write(str(e[0])+';')
#                    file.write(str(e[1])+';')
#                    file.write(str(e[2])+';')
#                    file.write(str(e[3])+'\n')
#    file.close()
    return(m, liste, timesteps, gap)
              
#################################################################################
#                                                                               #
#                       run & time model                                        #
#                                                                               #
#################################################################################

import timeit
for k in range(numberofruns):
    results = []
    for i in range(numberofruns):
        t = timeit.Timer("lowerBounds()", setup="from __main__ import lowerBounds")

        repeat, number = 10,1
        r = t.repeat(repeat, number)
#        best, worst = min(r), max(r)
#        average = sum(r)/len(r)

#        print("{number} loops, best of {repeat}: {best:.3g} seconds per loop, "  "worst of {repeat}: {worst:.3g} seconds per loop, " "average of {repeat}: {average:.3g} seconds per loop".format(**vars()))

        results.append(r)
    
    countEH = 0    
    file = open('/home/streib/Schreibtisch/timeit_HH/OutPUT/Starthabitats50x50_Timehorizon'+str(TimeHorizon)+'output_timeNoStress/Startsets'+str(k)+'.csv', 'w')
#    file = open('/Users/henriette/Python/IP/speedup/Starthabitats50x50_Timehorizon'+str(TimeHorizon)+'output_timeNoStress/Startsets'+str(k)+'.csv', 'w')
    file.write('Endset;times needed\n')
    for e in results:
        file.write(str(countEH)+';')
        countEH += 1
        for i in e: 
            file.write(str(i) + ';')
        file.write('\n')
    
    file.close()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    