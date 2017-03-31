'''
Created on 20 Mar 2017

@author: root
'''

import os
import subprocess
import shlex

f = os.popen('ogrinfo -ro -so -al "http://map1.naturschutz.rlp.de/service_lanis/mod_wfs/wfs_getmap.php?mapfile=glb&service=WFS&version=1.0.0&Request=GetCapabilities"')

orgINFO = f.read()
orgINFO = orgINFO.replace('\n',', ')

fields = orgINFO.split('Geometry Column = msGeometry, ')[1].split(',')

for x in range(len(fields)):
    fields[x] = fields[x].split(':')[0]

fields = str(fields[:-1])[1:-1]
fields = fields.replace("'","")

cmd = 'ogr2ogr -append -f PostgreSQL PG:"host=localhost port=5432 dbname=DB_PhD user=lucas password=1gis!gis1" "http://map1.naturschutz.rlp.de/service_lanis/mod_wfs/wfs_getmap.php?mapfile=glb&service=WFS&version=1.0.0&Request=GetCapabilities" -sql "SELECT '+str(fields)+'  FROM glb"'

args = shlex.split(cmd)

subprocess.call(args)

