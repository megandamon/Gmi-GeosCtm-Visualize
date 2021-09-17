#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Juy 1 2021
#
# DESCRIPTION:
# Driver to calculate 3d pressure from surface pressure and ak bk coordinates
#------------------------------------------------------------------------------

import re
import os
import sys
import random
import datetime
import calendar
import getopt
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
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


FILE = "f"

NUM_ARGS = 2
def usage ():
    print("")
    print("usage: Create3DPressure_GMI.py [-c] [-r]")
    print("-c File (GMI)")
    print("-r time record to use")
    print("")
    sys.exit (0)


print("Start creating 3d pressure field")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

gmiFile1 = optList[0][1]
timeRecord = int(optList[1][1])


#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (gmiFile1):
    print("The file you provided does not exist: ", gmiFile1)
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")


print(gmiFile1)
sim1Name = gmiFile1.split("_")[1]
plotTitleFile1 = "GMI " 
plotTitleFile1 = plotTitleFile1 + sim1Name



print("")
print("sim1Name: ", sim1Name)
print("")

print("")
print("plot title 1 : ", plotTitleFile1)
print("")


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------


if "amonthly" in gmiFile1 or "idaily" in gmiFile1:
    gmiTimeVar = "hdr"
else:
    gmiTimeVar = "nymd"


file1Object = GmiPlotTools (gmiFile1, 'latitude_dim', 'longitude_dim', \
                                'eta_dim', 'rec_dim', 'latitude_dim', \
                                'longitude_dim', 'eta_dim', gmiTimeVar, 'const_labels')

print("")
print("Processing 3d pressure calculation")
print("")


field = "psf"


psfField = file1Object.returnField (field, timeRecord, '')
print("shape of psf array: ", psfField.shape)



amCoords = file1Object.return1DArray ("am")
bmCoords = file1Object.return1DArray ("bm")

print ("Num levs: ", len(amCoords))
print ("Num lat lon: ", shape(psfField))
latSize = shape(psfField)[0]
lonSize = shape(psfField)[1]

press3d = numpy.zeros((len(amCoords), latSize, lonSize), numpy.float32)

print (shape(press3d))
pt = 0.01 #hPa or mb
count = 0
for level in amCoords[:]:
    press3d[count,:,:] = amCoords[count] + bmCoords[count]*psfField[:,:]
    print (count, amCoords[count], bmCoords[count], press3d[count,int(latSize/2),int(lonSize/2)])
    
    count = count + 1

rootgrp = Dataset("test.nc", "w", format="NETCDF4")

levelDim = rootgrp.createDimension("eta_dim", len(amCoords))
latDim = rootgrp.createDimension("latitude_dim", latSize)
lonDim = rootgrp.createDimension("longitude_dim", lonSize)


#levVar = rootgrp.createVariable("lev","f8",("lev",))
#latVar = rootgrp.createVariable("lat","f8",("lat",))
#lonVar = rootgrp.createVariable("lon","f8",("lon",))

fieldVar = rootgrp.createVariable("press3d","f8",("eta_dim","latitude_dim","longitude_dim"))
fieldVar[:,:,:] = press3d[:,:,:]


rootgrp.close()
       
print("")
print("Finished 3d pressure calculation")
print("")

sys.stdout.flush()
    

