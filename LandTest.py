#!/usr/bin/python

import re
import os
import sys
import random
import datetime
import calendar
import numpy
from numpy import *
from netCDF4 import Dataset

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

import math
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap

import vertLevels_GEOS5 as pressLevels



from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matplotlib.path import Path

fig = plt.figure(figsize=(8, 4.5))
plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.00)

# MPL searches for ne_10m_land.shp in the directory 'D:\\ne_10m_land'
m = Basemap(projection='robin',lon_0=0,resolution='c')
shp_info = m.readshapefile('shapeFiles/ne_10m_land', 'scalerank', drawbounds=True)
ax = plt.gca()
ax.cla()

paths = []
for line in shp_info[4]._paths:
    paths.append(Path(line.vertices, codes=line.codes))

coll = PathCollection(paths, linewidths=0, facecolors='grey', zorder=2)

m = Basemap(projection='robin',lon_0=0,resolution='c')
# drawing something seems necessary to 'initiate' the map properly
m.drawcoastlines(color='white', zorder=0)

ax = plt.gca()
ax.add_collection(coll)

plt.savefig('world.png',dpi=75)
