
from selenium import webdriver

from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver import ActionChains

import time
import os

fire = webdriver.Firefox()

fire.get('http://map1.naturschutz.rlp.de/kartendienste_naturschutz/index.php')

fire.find_element_by_xpath(".//*[@id='menu']/li[3]/span").click()

fire.find_element_by_xpath(".//*[@id='menu']/li[3]/div/ul/li[8]/span").click()

#####

fire.find_element_by_xpath(".//*[@id='menu']/li[3]/div/ul/li[8]/div/ul/li/span").click()


# value="bt_f">Biotoptypen (Flächen)
# value="lrt_f">Lebensraumtypen (Flächen)
# value="bk_f">Biotopkataster (Flächen)
# value="para28_f">Biotoptypen §30 (Flächen)
# value="tiere_f">Fundpunkte Tiere (Raster)
# value="pflanzen_f">Fundpunkte Pflanzen (Raster)
# value="landschaften">Landschaftsbildeinheiten
# value="biotopverbund">Landesweiter Biotopverbund


element = fire.find_element_by_xpath(".//*[@id='mod_export_layer']")

element.send_keys(unicode("biotopverbund"))

element = fire.find_element_by_xpath(".//*[@id='mod_export_format']")

element.send_keys("ESRI Shapefile")

element = fire.find_element_by_xpath(".//*[@id='coord_bbox_result']")

xMin = 288500
yMin = 5423500

xMax = 465500
yMax = 5647500

fire.find_element_by_xpath(".//*[@id='exportWindow']/table/tbody/tr[4]/td/a/span").click()

while yMin < yMax:
    
    while xMin < xMax:
    

        element.send_keys(xMin, str(','), yMin, str(','), xMin+40000, str(','), yMin+40000)
    
        fire.find_element_by_xpath(".//*[@id='exportWindow']/table/tbody/tr[5]/td/a").click()
        
        try: 
            time.sleep(5) 
            
            fire.find_element_by_xpath(".//*[@id='mod_export_output']/strong/a").click()

        except:
            time.sleep(15) 
            
            fire.find_element_by_xpath(".//*[@id='mod_export_output']/strong/a").click()
            
        xMin = xMin + 40000
        
        fire.find_element_by_xpath(".//*[@id='exportWindow']/table/tbody/tr[4]/td/a/span").click()

    yMin = yMin + 40000
    
    xMin = 288500

###### 

import zipfile, os

shp_name = 'Biotopverbund'

dir_name = '/home/lucas/PhD/STRESSOR/geoDATA/'+str(shp_name)

os.chdir(dir_name)

x = 0

for item in os.listdir(dir_name): 
    
    if item.endswith('.zip'): 
        
        x = x+1
        
        file_name = os.path.abspath(item) 
        zip_ref = zipfile.ZipFile(file_name) 
        zip_ref.extractall(dir_name)
        zip_ref.close() 
        
        try:
            os.rename(file_name.split('(')[0] + str('.dbf'), file_name.split('(')[0] + str(x) + str('.dbf'))
            os.rename(file_name.split('(')[0] + str('.prj'), file_name.split('(')[0] + str(x) + str('.prj'))
            os.rename(file_name.split('(')[0] + str('.shx'), file_name.split('(')[0] + str(x) + str('.shx'))
            os.rename(file_name.split('(')[0] + str('.shp'), file_name.split('(')[0] + str(x) + str('.shp'))

        except:
            pass
        
        os.remove(file_name)

mergeLIST = []

for item in os.listdir(dir_name): 
    
    if item.endswith('.shp'): 
        
        if os.stat(item).st_size == 100:
            os.remove(item.split('.')[0] + str('.dbf'))
            os.remove(item.split('.')[0] + str('.prj'))
            os.remove(item.split('.')[0] + str('.shx'))
            os.remove(item.split('.')[0] + str('.shp'))
            
        else: 
            mergeLIST.append(dir_name + '/' + item)

mergeLIST = str(mergeLIST).replace(',',';')[1:-1]
mergeLIST = mergeLIST.replace("'","")
mergeLIST = mergeLIST.replace(" ","")

import sys

from qgis.core import *
from PyQt4.QtGui import *
from PyQt4.QtGui import QApplication

app = QgsApplication([], True)
app.setPrefixPath('/usr', True)
app.initQgis()
print app.showSettings()

from processing.core.Processing import Processing
Processing.initialize()
from processing.tools import *

import processing

processing.alglist()

# layer1 = '/home/lucas/PhD/STRESSOR/geoDATA/Biotoptypen_Flaechen/tab_bt_f_ohne30.shp'
# layer2 = '/home/lucas/PhD/STRESSOR/geoDATA/Biotoptypen_Flaechen/tab_bt_f_ohne20.shp'
output = '/home/lucas/PhD/STRESSOR/geoDATA/' +str(shp_name)+ '/merged.shp'
 
processing.tools.general.runalg("qgis:mergevectorlayers", mergeLIST, output)

import os
import subprocess
import shlex

cmd = 'ogr2ogr -append -f PostgreSQL PG:"host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1" -nlt GEOMETRY '+str(output)

args = shlex.split(cmd)

subprocess.call(args)

import gdal, ogr, os, osr

import psycopg2

conn = psycopg2.connect("host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE """+str(shp_name)+""" AS SELECT DISTINCT ON (ST_AsBinary(wkb_geometry)) * FROM merged""")
conn.commit()

cursor.execute("""DROP TABLE merged""")
conn.commit()

cursor.close()
conn.close()
