'''
created on 2 feb 2017

@author: lucas
'''

#from randshortpath import randshortpath as rsp

import numpy as np
np.set_printoptions(suppress=True)

import gdal, ogr, os, osr
import random
import scipy 

import psycopg2
import math

import matplotlib.pyplot as plt

import time

import re

import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

import networkx as nx

import multiprocessing 
from multiprocessing import Pool

def proCON(confiQ):

    conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=streib_lucas password=1gis!gis1")
    cursor = conn.cursor()

    habARRAs = ('random_01','random_02','clustr_01','clustr_02','linear_01','linear_02')

    reS_sha = []

    reSults = []
    
    for habARRA in habARRAs: 

        reS_sha_mean = []

        for segM in range(25):
            
            for ruN in range(10):

                for habCONFIq in range(10):
    
                    print((confiQ)+"""_"""+(habARRA)+""".habitats_shortpath_red_nlmr_testarea_50x50_"""+str(ruN)+"""_"""+str(segM+1)+"""_start_"""+str(habCONFIq))
                    
                    cursor.execute("""SELECT ids FROM dis_pts_2500_10x10_"""+(habARRA)+""".pts_habitat_red_"""+str(segM+1)+"""_start_"""+str(habCONFIq)+""";""")
                    idS = cursor.fetchall()
                    idS = [i[0] for i in idS]

                    cursor.execute("""SELECT start, aim, costs FROM """+(confiQ)+"""_"""+(habARRA)+""".habitats_shortpath_red_nlmr_testarea_50x50_"""+str(ruN)+"""_"""+str(segM+1)+"""_start_"""+str(habCONFIq)+""";""")
                    arCs =  cursor.fetchall()
                    arCs = [list(x) for x in arCs]
            
                    for arC in arCs:

                        if arC[2] < 1250:                    
                            arC[2] = ((1 - (arC[2] / 1250))**2)                            
                        else:                            
                            arC[2] = None
                            
                    arCs = [x for x in arCs if x[2] is not None]

                    G = nx.Graph()
                    G.add_nodes_from(idS) 

                    for arC in arCs:
                        
                        G.add_edge(arC[0], arC[1], cost = -math.log(arC[2]))

                    SP_Len = nx.shortest_path_length(G, weight = 'cost')
    
                    lsT_SP_Len_proB = [] 
                    lsT_SP_Len_binA = [] 

                    for ite in SP_Len.items():
                                                
                        lsT_proB = [list(j) for j in ite[1].items() if j[1] is not 0]
                        lsT_proB = [[i[0],math.e**-i[1]] for i in lsT_proB]                                            
                        lsT_SP_Len_proB.append([ite[0],lsT_proB])

                        lsT_binA = [list(j) for j in ite[1].items() if j[1] is not 0]
                        lsT_binA = [[i[0], 1] for i in lsT_binA]                                            
                        lsT_SP_Len_binA.append([ite[0],lsT_binA])
                        
                    PC_bas = 0

                    for ite in lsT_SP_Len_proB:
                                        
                        for proB in ite[1]:
                            
                            PC_bas = PC_bas + (((0.1**2)**2) * proB[1])
     
                    PC_NLMR_proB = PC_bas / (10**2)**2
                    ECA_NLMR_proB = np.sqrt(PC_bas)

                    PC_bas = 0

                    for ite in lsT_SP_Len_binA:
                                        
                        for proB in ite[1]:
                            
                            PC_bas = PC_bas + (((0.1**2)**2) * proB[1])
                            
                    PC_NLMR_binA = PC_bas / (10**2)**2
                    ECA_NLMR_binA = np.sqrt(PC_bas)
              
                    #####
                    
                    print((confiQ)+"""_"""+(habARRA)+""".habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(ruN)+"""_"""+str(segM+1)+"""_start_"""+str(habCONFIq))
                    
                    cursor.execute("""SELECT ids FROM dis_pts_2500_10x10_"""+(habARRA)+""".pts_habitat_red_"""+str(segM+1)+"""_start_"""+str(habCONFIq)+""";""")
                    idS = cursor.fetchall()
                    idS = [i[0] for i in idS]

                    cursor.execute("""SELECT start, aim, costs FROM """+(confiQ)+"""_"""+(habARRA)+""".habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(ruN)+"""_"""+str(segM+1)+"""_start_"""+str(habCONFIq)+""";""")
                    arCs =  cursor.fetchall()
                    arCs = [list(x) for x in arCs]
            
                    for arC in arCs:

                        if arC[2] < 1250:                        
                            arC[2] = ((1 - (arC[2] / 1250))**2)                            
                        else:                            
                            arC[2] = None
                            
                    arCs = [x for x in arCs if x[2] is not None]
            
                    G = nx.Graph()
                    G.add_nodes_from(idS) 

                    for arC in arCs:

                        if arC[2] != None:
                            G.add_edge(arC[0], arC[1], cost = -math.log(arC[2]))
                        else:
                            G.add_edge(arC[0], arC[1], cost = 999999)
                            
                    SP_Len = nx.shortest_path_length(G, weight = 'cost')
    
                    lsT_SP_Len_proB = [] 
                    lsT_SP_Len_binA = [] 

                    for ite in SP_Len.items():
                                                
                        lsT_proB = [list(j) for j in ite[1].items() if j[1] is not 0]
                        lsT_proB = [[i[0],math.e**-i[1]] for i in lsT_proB]                                            
                        lsT_SP_Len_proB.append([ite[0],lsT_proB])

                        lsT_binA = [list(j) for j in ite[1].items() if j[1] is not 0]
                        lsT_binA = [[i[0], 1] for i in lsT_binA]                                            
                        lsT_SP_Len_binA.append([ite[0],lsT_binA])
                        
                    PC_bas = 0

                    for ite in lsT_SP_Len_proB:
                                        
                        for proB in ite[1]:
                            
                            PC_bas = PC_bas + (((0.1**2)**2) * proB[1])
     
                    PC_NLMRC_proB = PC_bas / (10**2)**2
                    ECA_NLMRC_proB = np.sqrt(PC_bas)

                    PC_bas = 0

                    for ite in lsT_SP_Len_binA:
                                        
                        for proB in ite[1]:
                            
                            PC_bas = PC_bas + (((0.1**2)**2) * proB[1])
                        
                    PC_NLMRC_binA = PC_bas / (10**2)**2
                    ECA_NLMRC_binA = np.sqrt(PC_bas)

                    ######
                    
                    print((confiQ)+"""_"""+(habARRA)+""".habitats_shortpath_red_nlmre_testarea_50x50_"""+str(ruN)+"""_"""+str(segM+1)+"""_start_"""+str(habCONFIq))
                    
                    cursor.execute("""SELECT ids FROM dis_pts_2500_10x10_"""+(habARRA)+""".pts_habitat_red_"""+str(segM+1)+"""_start_"""+str(habCONFIq)+""";""")
                    idS = cursor.fetchall()
                    idS = [i[0] for i in idS]

                    cursor.execute("""SELECT start, aim, costs FROM """+(confiQ)+"""_"""+(habARRA)+""".habitats_shortpath_red_nlmre_testarea_50x50_"""+str(ruN)+"""_"""+str(segM+1)+"""_start_"""+str(habCONFIq)+""";""")
                    arCs =  cursor.fetchall()
                    arCs = [list(x) for x in arCs]
            
                    for arC in arCs:

                        if arC[2] < 1250:                        
                            arC[2] = ((1 - (arC[2] / 1250))**2)                            
                        else:                            
                            arC[2] = None
                            
                    arCs = [x for x in arCs if x[2] is not None]
            
                    G = nx.Graph()
                    G.add_nodes_from(idS) 

                    for arC in arCs:

                        if arC[2] != None:
                            G.add_edge(arC[0], arC[1], cost = -math.log(arC[2]))
                        else:
                            G.add_edge(arC[0], arC[1], cost = 999999)
                            
                    SP_Len = nx.shortest_path_length(G, weight = 'cost')
    
                    lsT_SP_Len_proB = [] 
                    lsT_SP_Len_binA = [] 

                    for ite in SP_Len.items():
                                                
                        lsT_proB = [list(j) for j in ite[1].items() if j[1] is not 0]
                        lsT_proB = [[i[0],math.e**-i[1]] for i in lsT_proB]                                            
                        lsT_SP_Len_proB.append([ite[0],lsT_proB])

                        lsT_binA = [list(j) for j in ite[1].items() if j[1] is not 0]
                        lsT_binA = [[i[0], 1] for i in lsT_binA]                                            
                        lsT_SP_Len_binA.append([ite[0],lsT_binA])
                        
                    PC_bas = 0

                    for ite in lsT_SP_Len_proB:
                                        
                        for proB in ite[1]:
                            
                            PC_bas = PC_bas + (((0.1**2)**2) * proB[1])
     
                    PC_NLMRE_proB = PC_bas / (10**2)**2
                    ECA_NLMRE_proB = np.sqrt(PC_bas)

                    PC_bas = 0

                    for ite in lsT_SP_Len_binA:
                                        
                        for proB in ite[1]:
                            
                            PC_bas = PC_bas + (((0.1**2)**2) * proB[1])
                             
                    PC_NLMRE_binA = PC_bas / (10**2)**2  
                    ECA_NLMRE_binA = np.sqrt(PC_bas)

                    #####               
                    
                    reS_sha_mean.append([[PC_NLMR_proB,PC_NLMRC_proB,PC_NLMRE_proB],[ECA_NLMR_proB,ECA_NLMRC_proB,ECA_NLMRE_proB],[PC_NLMR_binA,PC_NLMRC_binA,PC_NLMRE_binA],[ECA_NLMR_binA,ECA_NLMRC_binA,ECA_NLMRE_binA]])
                    
            reS_sha = [habARRA, segM+1, (np.mean(reS_sha_mean, axis = 0)).tolist()]

            reSults.append(reS_sha)
        
    with open("""/home/streib/proCON/PC_"""+str(confiQ)+""".txt""", "w") as output:
        output.write(str(reSults))


def main():


    confiQs = ['stream_network_000050050','stream_network_025375375','stream_network_050025025','stream_network_075125125','stream_network_100000000','stream_network_050000050','stream_network_375025375','stream_network_025050025','stream_network_125075125','stream_network_000100000','stream_network_050050000','stream_network_375375025','stream_network_025025050','stream_network_125125075','stream_network_000000100']

    pool = multiprocessing.Pool(processes=12)
    pool.map(proCON, confiQs)

    pool.close()
    pool.join()
    
if __name__ in ['__builtin__', '__main__']:
    
    main()





