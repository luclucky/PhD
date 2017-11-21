

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 12:05:26 2017

@author: henriette
"""
import numpy as np
from  osgeo import ogr
from gurobipy import *
import time
import networkx as nx
from random import sample
import matplotlib.pyplot as plt
import random
import os

###############################################################################
#                                                                             #
#                            load data                                        #
#                                                                             #
###############################################################################
def loadData(maxcost, data, sp_type):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open('/home/lucas/Desktop/PhD/Henriette/SHPs_2/habitats_shortpath_red'+str(sp_type)+'_testarea_'+str(data)+'_0_start_0_resamp.shp')
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
#        idsp = inFeature.GetField('id')


        if costsp < maxcost:
            start_sp.append(int(startsp))
            aim_sp.append(int(aimsp))
            cost_sp.append(int(costsp))
#            id_sp.append(int(idsp))
            id_sp.append(i)
    habitatsQual = np.load('/home/lucas/Desktop/PhD/Henriette/habitatsQual.npy')

    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp = driver.Open('/home/lucas/Desktop/PhD/Henriette/SHPs_2/pts_habitat_red_'+str(data)+'_start_0.shp')
    layer = shp.GetLayer()

    habitats = {}


    for i in range(layer.GetFeatureCount()):
        inFeature = layer.GetNextFeature()

        habitat_pts = inFeature.GetField('ids')

        habitats[int(habitat_pts)] = habitatsQual[int(habitat_pts)-1]
    return(start_sp, aim_sp, cost_sp, id_sp, habitats)

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

    m.Params.timeLimit = timelimit


    return(m)







################################################################################
#                                                                              #
#                              solving                                         #
#                                                                              #
################################################################################

def solve(m, TEN, Start, End, Vstress, Tstress, Estress, file, start_sp, aim_sp, id_sp):
    m.write('newObjFct.lp')
    m.optimize()
#    m.printAttr('X')

    gap = m.MIPGap
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


    print("\n Start: ", Start)
    print("End: ", End)
    print("Vstress: ", Vstress)
    print("Tstress: ", Tstress)
    print("%s Habitats are occupied after %s time steps"%(len(End),timesteps))

    file.write('Start:;')
    for start in Start:
        file.write(str(start)+';')

    file.write('\n End:;')
    for end in End:
        file.write(str(end)+';')

    file.write('\n Timesteps needed;'+ str(timesteps)+ '\n')
    file.write('start; aim; individuals; id \n')

    for e in liste:
        for i in range(len(start_sp)):
            if e[0] < timesteps*100000:
                if e[0]%100000 == start_sp[i] and e[1]%100000 == aim_sp[i]:
                    e.append(id_sp[i])

                    file.write(str(e[0])+';')
                    file.write(str(e[1])+';')
                    file.write(str(e[2])+';')
                    file.write(str(e[3])+'\n')

                elif e[1]%100000 == start_sp[i] and e[0]%100000 == aim_sp[i]:
                    e.append(id_sp[i])

                    file.write(str(e[0])+';')
                    file.write(str(e[1])+';')
                    file.write(str(e[2])+';')
                    file.write(str(e[3])+'\n')
    file.close()
    return(m, liste, timesteps, gap)



################################################################################
#                                                                              #
#                              run simulations                                 #
#                                                                              #
################################################################################


starttime = time.clock()

Nmin = 20
TimeHorizon = 30
disp_perc = 0.25 # wenn disp_perc erhoeht wird, muss auch upper bound der flow variables angepasst werden
inf = 8888
growth = 1
numberofruns = 50

data = '50x50'
sp_type = '_nlmr'

maxcost = 1250
mort_perc = 0.0008

timelimit = 1200
result = []
Times = []

start_sp, aim_sp, cost_sp, id_sp, habitats = loadData(maxcost, data, sp_type)
Starthabitats = []
Startsets = []

for line in open('/home/lucas/Desktop/PhD/Henriette/StartHabitats'+str(data)+'.csv'):

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

#    for line in open('/home/lucas/Desktop/PhD/Henriette/EndHabitats_'+str(lenEnd)+'_'+str(data)+'.csv'):
#        Endhabitats.append(line.split(';'))
#
#    for endset in Endhabitats:
#        if '\n' in endset:
#            endset.remove('\n')
#        End = []
#        for end in endset:
#            End.append(int(end))
#        Endsets.append(End)

for end in open('/home/lucas/Desktop/PhD/Henriette/Endhabitats50x50.csv'):
    Endsets.append([int(end)])



for k in range(numberofruns):
    for i in range(numberofruns):
#            for j in [[1, 87], [1, 26], [4, 719], [7, 53],
#                      [8, 672], [9, 833], [10, 87], [10, 26],
#                      [12, 53], [14, 53], #
#                      [14, 1447], [15, 1069],
#                      [18, 53], #
#                      [20, 87],[20, 26], [22, 87], [22, 26], [23, 1760],
#                      [25, 244], [27, 876], [31, 1937],
#                      [33, 53], [34, 53], [35, 53], #
#                      [36, 87], [36, 26], [37, 87], [37, 26],
#                      [37, 53], #
#                      [37, 1760],
#                      [42, 53], #
#                      [47, 244]]:
#                end = j[1]
#                k = j[0]
#            for j in [67, 82, 83, 118, 136, 137, 139, 150, 157]:

            print('\n run', k, i)
            timestart = time.clock()
            file = open('/home/lucas/Desktop/PhD/Henriette/Starthabitats50x50_Timehorizon'+str(TimeHorizon)+'/newData_output_'+str(i)+'.csv', 'w')
#                file = open('/home/lucas/Desktop/PhD/Henriette/Test/path_to'+str(end)+'from Startset'+str(k)+'.csv','w')

#                Start = Startsets[0]
#                End = Endsets[j]

            Start = Startsets[k]
            End = Endsets[i]

#                Start = Startsets[k]
#                End = [end]

            print('Start:', Start)
            print('End:', End)

            TEN = constructGraph(TimeHorizon, habitats, start_sp, aim_sp, cost_sp, Start, End, disp_perc, inf)

            m = buildModel(TEN, Start, End, habitats, TimeHorizon, Nmin, mort_perc, [], growth, timelimit)
            
            try:
                m, liste, timesteps, gap =  solve(m, TEN, Start, End, [], [], [], file, start_sp, aim_sp, id_sp)
                result.append([TimeHorizon,timesteps, gap])

                timeend = time.clock()
                Times.append([Start, End, timesteps, timeend-timestart, gap])
            except:
                text = 'infeasible'
                for end in End:
                    count = 0
                    for start in Start:
                        if nx.has_path(TEN, start, TimeHorizon*100000+end):
                            count += 1
                    if count == 0:
                        text = 'not connected'


                result.append([TimeHorizon, inf, text])

                timeend = time.clock()
                Times.append([Start, End, text, timeend-timestart, 99999])
            print(result)

    endtime = time.clock()
    print("\n time needed:", endtime - starttime, "seconds")
    print("result: ", result)

    File = open('/home/lucas/Desktop/PhD/Henriette/Starthabitats50x50_Timehorizon'
    +str(TimeHorizon)+'/newData.csv', 'w')
#        File = open('/home/lucas/Desktop/PhD/Henriette/Test/newData.csv','w')

    File.write('Start;End;Timesteps;time needed; gap\n')

for e in Times:
    for start in e[0]:
        File.write(str(start)+' ')
    File.write(';')
    for end in e[1]:
        File.write(str(end)+' ')
    File.write(';'+str(e[2])+';'+str(e[3])+';'+str(e[4])+'\n')
File.close()



