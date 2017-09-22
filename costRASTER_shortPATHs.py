'''
Created on 2 Feb 2017

@author: lucas
'''

#from randShortPath import randShortPath as rSP
import numpy as np
import gdal, ogr, os, osr

import psycopg2
import math

import matplotlib.pyplot as plt

import time

import re

from skimage.graph import route_through_array


def ind_to_Xcoord(ind_x):
    
    coord_x = ind_x * cr_gt[1] + cr_gt[0] + cr_gt[1]/2 # coord

    return(coord_x)
    
def ind_to_Ycoord(ind_y):
    
    coord_y = ind_y * cr_gt[5] + cr_gt[3] + cr_gt[5]/2 # coord

    return(coord_y)


conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

numRandPTs = 10

for xxxxx in range(numRandPTs):
    
    print("RUN:" + str(xxxxx))

    cursor.execute("""SELECT start, start_xy, aim, aim_xy, distance FROM stream_network.dist_pts_2500_10x10_start_"""+str(xxxxx)+""";""")
    
    dist_pts_2500 =  cursor.fetchall()
    
    dist_pts_2500 = [list(x) for x in dist_pts_2500]
    
    dist_pts_2500 = [[x[0],[float(x[1].split(' ',1)[0][6:]), float(x[1].split(' ',1)[1][:-1])],x[2],[float(x[3].split(' ',1)[0][6:]), float(x[3].split(' ',1)[1][:-1])], x[4]] for x in dist_pts_2500] 
    
    doub = [[x[2], x[0]]for x in dist_pts_2500],[[x[0], x[2]]for x in dist_pts_2500]
      
    dist_pts_2500_red = dist_pts_2500
       
    for x in range(len(doub[0])/2):
            
        y = doub[0][x]
            
        #print('x: ' + str(x))
            
        for xx in range(len(doub[0])):
                
            #print('xx: ' + str(xx))
    
            yy = doub[1][xx]
        
            if yy == y:
                
                doub[0].pop(xx)
                doub[1].pop(xx)
                dist_pts_2500_red.pop(xx)
                break
    
    numNLMs = 10

    for xx in range(numNLMs):
    
        print(xx)
                        
        cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM stream_network.nlmr_testarea_10x10_"""+str(xx)+"""_resamp;""")
        
        vsipath = '/vsimem/from_postgis'
        
        gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))
        
        cost_raster = gdal.Open(vsipath)
        
        gdal.Unlink(vsipath)
        
        cr_band = cost_raster.GetRasterBand(1)
        cr_array = cost_raster.ReadAsArray()
        
        numrows = len(cr_array)
        numcols = len(cr_array[0])
        
        cr_gt = cost_raster.GetGeoTransform()
        
        cost_raster.RasterXSize

        cursor.execute("""CREATE TABLE stream_network.habitats_shortpath_red_nlmr_testarea_10x10_"""+str(xx)+"""_start_"""+str(xxxxx)+"""_resamp (start bigint, aim bigint, geom geometry, costs double precision);""")
        
        for xxx in range(len(dist_pts_2500_red)):
        
            start_x = int((dist_pts_2500_red[xxx][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
            start_y = int((dist_pts_2500_red[xxx][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
            
            aim_x = int((dist_pts_2500_red[xxx][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
            aim_y = int((dist_pts_2500_red[xxx][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
            
            indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)
            
            #print(route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True))
        
            indices = np.array(indices).T
            
            coordinates = []
            
            mPTs = ""
            
            for xxxx in range(len(indices[0])):
            
                coordinates.append([ind_to_Xcoord(indices[0][xxxx]), ind_to_Ycoord(indices[1][xxxx])])
        
                mPTs = mPTs + "ST_MakePoint("+str(coordinates[xxxx][0]) + ', ' + str(coordinates[xxxx][1])+"),"
        
            mPTs = mPTs[:-1]

            cursor.execute("""INSERT INTO stream_network.habitats_shortpath_red_nlmr_testarea_10x10_"""+str(xx)+"""_start_"""+str(xxxxx)+"""_resamp (start, aim, geom, costs) VALUES ("""+str(dist_pts_2500_red[xxx][0])+""", """+str(dist_pts_2500_red[xxx][2])+""", ST_SetSRID(ST_MakeLine(ARRAY["""+str(mPTs)+"""]), 25832), """+str(weight)+""");""") 

            conn.commit()

#####

    for xx in range(numNLMs):
    
        print(xx)
                        
        cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM stream_network.nlmrc_testarea_10x10_"""+str(xx)+"""_resamp;""")
        
        vsipath = '/vsimem/from_postgis'
        
        gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))
        
        cost_raster = gdal.Open(vsipath)
        
        gdal.Unlink(vsipath)
        
        cr_band = cost_raster.GetRasterBand(1)
        cr_array = cost_raster.ReadAsArray()
        
        numrows = len(cr_array)
        numcols = len(cr_array[0])
        
        cr_gt = cost_raster.GetGeoTransform()
        
        cost_raster.RasterXSize

        cursor.execute("""CREATE TABLE stream_network.habitats_shortpath_red_nlmrc_testarea_10x10_"""+str(xx)+"""_start_"""+str(xxxxx)+"""_resamp (start bigint, aim bigint, geom geometry, costs double precision);""")
        
        for xxx in range(len(dist_pts_2500_red)):
        
            start_x = int((dist_pts_2500_red[xxx][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
            start_y = int((dist_pts_2500_red[xxx][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
            
            aim_x = int((dist_pts_2500_red[xxx][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
            aim_y = int((dist_pts_2500_red[xxx][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
            
            indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)
            
            #print(route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True))
        
            indices = np.array(indices).T
            
            coordinates = []
            
            mPTs = ""
            
            for xxxx in range(len(indices[0])):
            
                coordinates.append([ind_to_Xcoord(indices[0][xxxx]), ind_to_Ycoord(indices[1][xxxx])])
        
                mPTs = mPTs + "ST_MakePoint("+str(coordinates[xxxx][0]) + ', ' + str(coordinates[xxxx][1])+"),"
        
            mPTs = mPTs[:-1]

            cursor.execute("""INSERT INTO stream_network.habitats_shortpath_red_nlmrc_testarea_10x10_"""+str(xx)+"""_start_"""+str(xxxxx)+"""_resamp (start, aim, geom, costs) VALUES ("""+str(dist_pts_2500_red[xxx][0])+""", """+str(dist_pts_2500_red[xxx][2])+""", ST_SetSRID(ST_MakeLine(ARRAY["""+str(mPTs)+"""]), 25832), """+str(weight)+""");""") 

            conn.commit()

#####

    for xx in range(numNLMs):
    
        print(xx)
                        
        cursor.execute("""SELECT ST_AsGDALRaster(rast, 'GTiff') FROM stream_network.nlmre_testarea_10x10_"""+str(xx)+"""_resamp;""")
        
        vsipath = '/vsimem/from_postgis'
        
        gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))
        
        cost_raster = gdal.Open(vsipath)
        
        gdal.Unlink(vsipath)
        
        cr_band = cost_raster.GetRasterBand(1)
        cr_array = cost_raster.ReadAsArray()
        
        numrows = len(cr_array)
        numcols = len(cr_array[0])
        
        cr_gt = cost_raster.GetGeoTransform()
        
        cost_raster.RasterXSize

        cursor.execute("""CREATE TABLE stream_network.habitats_shortpath_red_nlmre_testarea_10x10_"""+str(xx)+"""_start_"""+str(xxxxx)+"""_resamp (start bigint, aim bigint, geom geometry, costs double precision);""")
        
        for xxx in range(len(dist_pts_2500_red)):
        
            start_x = int((dist_pts_2500_red[xxx][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
            start_y = int((dist_pts_2500_red[xxx][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
            
            aim_x = int((dist_pts_2500_red[xxx][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
            aim_y = int((dist_pts_2500_red[xxx][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
            
            indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)
            
            #print(route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True))
        
            indices = np.array(indices).T
            
            coordinates = []
            
            mPTs = ""
            
            for xxxx in range(len(indices[0])):
            
                coordinates.append([ind_to_Xcoord(indices[0][xxxx]), ind_to_Ycoord(indices[1][xxxx])])
        
                mPTs = mPTs + "ST_MakePoint("+str(coordinates[xxxx][0]) + ', ' + str(coordinates[xxxx][1])+"),"
        
            mPTs = mPTs[:-1]

            cursor.execute("""INSERT INTO stream_network.habitats_shortpath_red_nlmre_testarea_10x10_"""+str(xx)+"""_start_"""+str(xxxxx)+"""_resamp (start, aim, geom, costs) VALUES ("""+str(dist_pts_2500_red[xxx][0])+""", """+str(dist_pts_2500_red[xxx][2])+""", ST_SetSRID(ST_MakeLine(ARRAY["""+str(mPTs)+"""]), 25832), """+str(weight)+""");""") 

            conn.commit()
            
          
conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()  
            
numRandPTs = 10

for x in range(numRandPTs):

    for y in range(numRandPTs):
        
# #         cursor.execute("""DROP TABLE IF EXISTS stream_network.habitats_shortpath_red_nlmr_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp;""")
#  
#         cursor.execute("""CREATE TABLE stream_network.habitats_shortpath_red_nlmr_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp_bku AS SELECT * FROM stream_network.habitats_shortpath_red_nlmr_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp;""")
#          
# #         cursor.execute("""DROP TABLE IF EXISTS stream_network.habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp;""")
#                   
#         cursor.execute("""CREATE TABLE stream_network.habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp_bku AS SELECT * FROM stream_network.habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp;""")
#               
# #         cursor.execute("""DROP TABLE IF EXISTS stream_network.habitats_shortpath_red_nlmre_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp;""")
#               
#         cursor.execute("""CREATE TABLE stream_network.habitats_shortpath_red_nlmre_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp_bku AS SELECT * FROM stream_network.habitats_shortpath_red_nlmre_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp;""")
#                           
#         conn.commit()
         
         
        cursor.execute("""UPDATE stream_network.habitats_shortpath_red_nlmr_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp SET aim = (SELECT stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids FROM stream_network.pts_habitat_red_50x50_start_"""+str(y)+""" WHERE stream_network.habitats_shortpath_red_nlmr_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp.aim = stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids_org);""")
    
        cursor.execute("""UPDATE stream_network.habitats_shortpath_red_nlmr_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp SET start = (SELECT stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids FROM stream_network.pts_habitat_red_50x50_start_"""+str(y)+""" WHERE stream_network.habitats_shortpath_red_nlmr_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp.start = stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids_org);""")
        
        conn.commit()

        cursor.execute("""UPDATE stream_network.habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp SET aim = (SELECT stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids FROM stream_network.pts_habitat_red_50x50_start_"""+str(y)+""" WHERE stream_network.habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp.aim = stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids_org);""")
    
        cursor.execute("""UPDATE stream_network.habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp SET start = (SELECT stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids FROM stream_network.pts_habitat_red_50x50_start_"""+str(y)+""" WHERE stream_network.habitats_shortpath_red_nlmrc_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp.start = stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids_org);""")
        
        conn.commit()    

        cursor.execute("""UPDATE stream_network.habitats_shortpath_red_nlmre_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp SET aim = (SELECT stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids FROM stream_network.pts_habitat_red_50x50_start_"""+str(y)+""" WHERE stream_network.habitats_shortpath_red_nlmre_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp.aim = stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids_org);""")
    
        cursor.execute("""UPDATE stream_network.habitats_shortpath_red_nlmre_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp SET start = (SELECT stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids FROM stream_network.pts_habitat_red_50x50_start_"""+str(y)+""" WHERE stream_network.habitats_shortpath_red_nlmre_testarea_50x50_"""+str(x)+"""_start_"""+str(y)+"""_resamp.start = stream_network.pts_habitat_red_50x50_start_"""+str(y)+""".ids_org);""")
        
        conn.commit()            
            
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
