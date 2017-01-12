'''
Created on 9 Jan 2017

@author: lucas
'''

from distutils.core import setup, Extension

module1 = Extension('xyCell', sources = ['/home/lucas/PhD/STRESSOR/gdistance/Cpp/xyCell_py.cpp']) 

setup(
        name = 'xyCell',
        version = '1.0',
        ext_modules = module1
      )
