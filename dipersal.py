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

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")

tables = cursor.fetchall()

cursor.execute("SELECT start, start_xy, aim, aim_xy, distance FROM dist_pts_2500;")

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
                    
cursor.execute("SELECT ST_AsGDALRaster(rast, 'GTiff') FROM costraster_triersaar;")

vsipath = '/vsimem/from_postgis'

gdal.FileFromMemBuffer(vsipath, bytes(cursor.fetchone()[0]))

cost_raster = gdal.Open(vsipath)

gdal.Unlink(vsipath)

from skimage.graph import route_through_array

cr_band = cost_raster.GetRasterBand(1)
cr_array = cost_raster.ReadAsArray()

numrows = len(cr_array)
numcols = len(cr_array[0])

cr_gt = cost_raster.GetGeoTransform()

cost_raster.RasterXSize

def ind_to_Xcoord(ind_x):
    
    coord_x = ind_x * cr_gt[1] + cr_gt[0] + cr_gt[1]/2 # coord

    return(coord_x)
    
def ind_to_Ycoord(ind_y):
    
    coord_y = ind_y * cr_gt[5] + cr_gt[3] + cr_gt[5]/2 # coord

    return(coord_y)

cursor.execute("CREATE TABLE habitats_shortpath_red (start bigint, aim bigint, geom geometry, costs double precision);")

for x in range(len(dist_pts_2500_red)):

    start_x = int((dist_pts_2500_red[x][1][0] - cr_gt[0]) / cr_gt[1]) #x pixel
    start_y = int((dist_pts_2500_red[x][1][1] - cr_gt[3]) / cr_gt[5]) #y pixel
    
    aim_x = int((dist_pts_2500_red[x][3][0] - cr_gt[0]) / cr_gt[1]) #x pixel
    aim_y = int((dist_pts_2500_red[x][3][1] - cr_gt[3]) / cr_gt[5]) #y pixel
    
    indices, weight = route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True)
    
    #print(route_through_array(cr_array, [start_x, start_y], [aim_x, aim_y],fully_connected=True))

    indices = np.array(indices).T
    
    coordinates = []
    
    mPTs = ""
    
    for xx in range(len(indices[0])):
    
        coordinates.append([ind_to_Xcoord(indices[0][xx]), ind_to_Ycoord(indices[1][xx])])

        mPTs = mPTs + "ST_MakePoint("+str(coordinates[xx][0]) + ', ' + str(coordinates[xx][1])+"),"

    mPTs = mPTs[:-1]

    cursor.execute("INSERT INTO habitats_shortpath_red (start, aim, geom, costs) VALUES ("+str(dist_pts_2500_red[x][0])+", "+str(dist_pts_2500_red[x][2])+", ST_SetSRID(ST_MakeLine(ARRAY["+str(mPTs)+"]), 25832), "+str(weight)+");") 

conn.commit()

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

start = time.time()

cursor.execute("SELECT start, aim, costs FROM habitats_shortpath_red;")

habitats_shortpath_red = cursor.fetchall()

habitats_shortpath_red = np.array(habitats_shortpath_red).T

habitats_QUAL = np.random.random_sample((100,)) # creates ramdom HQs

cursor.execute("CREATE TABLE dispresal100_SH2_pro2 (pts_id bigint);")

for xxxx in range(100):
    
    print('run ' + str(xxxx))
        
    cursor.execute("ALTER TABLE dispresal100_SH2_pro2 ADD run_"+str(xxxx+1)+"_timestep bigint;")
    
    startHABITATS = np.random.choice(np.unique([habitats_shortpath_red[0], habitats_shortpath_red[1]]), 2)# number of occupied habitats first run
    occHABITATS = np.array([range(100+1)[1:], [999] * 100, [999] * 100]) # 100: should be len(test_pts_shift)
    
    occHABITATS[1][(startHABITATS-1).tolist()] = 0
    occHABITATS[2][(startHABITATS-1).tolist()] = 0

    timeSTEPS = 100
    
    proB = (1 - (habitats_shortpath_red[2] / np.amax(habitats_shortpath_red[2])))**2 # function to calculate the probability of reaching new habitat
        
    plt.plot( sorted(habitats_shortpath_red[2], reverse=False), sorted(proB, reverse=True))
    #plt.xlabel('Costs')
    #plt.ylabel('Probability')
    plt.grid(True)
  
    for x in range(timeSTEPS):
                        
        for xx in range(len(startHABITATS)):

            conHABITATS_ind = np.hstack(np.array([np.where(habitats_shortpath_red[0] == startHABITATS[xx])[0].tolist(), np.where(habitats_shortpath_red[1] == startHABITATS[xx])[0].tolist()]).flat).tolist()
        
            if len(conHABITATS_ind) > 3:
                
                conHABITATS_ind = np.unique(np.random.choice(conHABITATS_ind, 3, p = (max(habitats_shortpath_red[2][conHABITATS_ind])-habitats_shortpath_red[2][conHABITATS_ind]) /sum(max(habitats_shortpath_red[2][conHABITATS_ind])-habitats_shortpath_red[2][conHABITATS_ind])))
    
            for xxx in conHABITATS_ind:
                
                yn = np.random.choice([1, 0], 1, p=[proB[xxx], 1-proB[xxx]])[0]
            
                if yn == 1:
                    
                    if occHABITATS[1][habitats_shortpath_red[0][xxx]-1] == 999:
                        
                        occHABITATS[1][habitats_shortpath_red[0][xxx]-1] = x+1
                        
                        occHABITATS[2][habitats_shortpath_red[0][xxx]-1] = startHABITATS[xx]
                        
                        startHABITATS, ind = np.unique(np.append(startHABITATS,[occHABITATS[0][habitats_shortpath_red[0][xxx]-1]]), return_index=True)
                        startHABITATS = startHABITATS[np.argsort(ind)]
                        
                    if occHABITATS[1][habitats_shortpath_red[1][xxx]-1] == 999:
                        
                        occHABITATS[1][habitats_shortpath_red[1][xxx]-1] = x+1
        
                        occHABITATS[2][habitats_shortpath_red[1][xxx]-1] = startHABITATS[xx]

                        startHABITATS, ind = np.unique(np.append(startHABITATS,[occHABITATS[0][habitats_shortpath_red[1][xxx]-1]]), return_index=True)
                        startHABITATS = startHABITATS[np.argsort(ind)]
                        
    toINS = str(np.array(occHABITATS[0:2]).T.tolist())[1:-1]
    toINS = toINS.replace('[','(')
    toINS = toINS.replace(']',')')
    
    if xxxx == 0:
        cursor.execute("INSERT INTO dispresal100_SH2_pro2 (pts_id, run_"+str(xxxx+1)+"_timestep) VALUES "+toINS+";") 

    else:
        cursor.execute("UPDATE dispresal100_SH2_pro2 SET run_"+str(xxxx+1)+"_timestep = run_"+str(xxxx+1)+"_timestep_arr FROM (VALUES "+toINS+") AS c(pts_id_arr, run_"+str(xxxx+1)+"_timestep_arr) WHERE pts_id = pts_id_arr;;") 

conn.commit()

end = time.time()
print(end - start)

# Close communication with the database
cursor.close()
conn.close()









#raster = gdal.Open('/home/lucas/PhD/r.tif')
#raster_test = gdal.Open('/home/lucas/PhD/test.tif')


# def array2raster(newRasterfn, rasterOrigin, pixelWidth, pixelHeight, array):
# 
#     array = array[::-1]
# 
#     cols = array.shape[1]
#     rows = array.shape[0]
#     originX = rasterOrigin[0]
#     originY = rasterOrigin[1]
# 
#     driver = gdal.GetDriverByName('GTiff')
#     outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
#     outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
#     outband = outRaster.GetRasterBand(1)
#     outband.WriteArray(array)
#     outRasterSRS = osr.SpatialReference()
#     outRasterSRS.ImportFromEPSG(25832)
#     outRaster.SetProjection(outRasterSRS.ExportToWkt())
#     outband.FlushCache()
# 
# rasterOrigin = (0,0)
# pixelWidth = 10
# pixelHeight = 10
# newRasterfn = '/home/lucas/PhD/test.tif'
# array = np.array([[ 1, 2, 3],[ 4, 5, 6],[ 7, 8, 9]])


sP = [[10.0, 0.0], [30.0, 20.0]]

def transFunc(i):   
    j = np.mean(i)  
    return j       
    
tr1 = rSP.TM_from_R(cost_raster, transFunc, directions = 8, symm = False)
tr1 = rSP.TM_from_R(raster, transFunc, directions = 8, symm = False)

tr1.__dict__
tr1.transitionMatrix.toarray()

tr = tr1
start = sP
aim = sP
theta = 1
totalNet="net"
method=1

aaa = rSP.rSPDistance(tr, start, aim, theta, totalNet="net", method=1)




