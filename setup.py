#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup
import os
setup(name='GRID_LRT',
      version='0.2',
      description='GRID LOFAR Reduction Tools',
      author='Alexandar Mechev',
      author_email='apmechev@strw.leidenuniv.nl',
      url='https://www.github.com/apmechev/GRID_LRT/',
      download_url = 'https://github.com/apmechev/GRID_LRT/archive/master.zip',
      keywords = ['surfsara', 'distributed-computing', 'lofar'],
      setup_requires=[
        'pyyaml', 
    ],
      tests_require=[
        'pytest',
    ],
      data_files = [(root, [os.path.abspath(os.path.join(root, f)) for f in files])
                  for root, dirs, files in os.walk('GRID_LRT/Sandbox')],
      packages=['GRID_LRT','GRID_LRT/Staging', 'GRID_LRT/Application', 'GRID_LRT/couchdb'] 
     )

