'''
Created on 8 Feb 2017

@author: lucas
'''
import sys

from qgis.core import *
import qgis.utils
from PyQt4.QtCore import QFileInfo, QSettings

from PyQt4.QtGui import QApplication
app = QApplication([])

QgsApplication.setPrefixPath('/usr/share/qgis', True)
QgsApplication.initQgis()

sys.path.append('/usr/share/qgis/python/plugins')

import processing

from processing.core.Processing import processing

from processing.tools import *

processing.alglist()

QgsApplication.exitQgis()
QApplication.exit()