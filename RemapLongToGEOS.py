#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         May 6 2019
#
# DESCRIPTION:
# Driver to convert a field on longitude 0:360 to -180:180
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
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


NUM_ARGS = 2
def usage ():
    print ""
    print "usage: RemapLongToGEOS.py [-c] [-f]"
    print "-c model file"
    print "-f field to remap"
    print ""
    sys.exit (0)


print "Start plotting field differences."


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile = optList[0][1]
fieldToRemap = optList[1][1]


#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (modelFile):
    print "The file you provided does not exist: ", modelFile
    sys.exit(0)


print modelFile



modelSimName = modelFile.split(".")[0]



#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------
modelObject = GeosCtmPlotTools (modelFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )




# put model on -180 to 0 to 180
lenLong = len(modelObject.long[:])


longRecords = numpy.zeros(modelObject.longSize, numpy.float32)

field = fieldToRemap

modelFieldArray = modelObject.returnField (field, 0)

print ""
print "Shape of field: ", modelFieldArray.shape[:]
levelSize = modelFieldArray.shape[0]
print ""


remappedModelArray = numpy.zeros((size(modelObject.time), \
                                      levelSize, \
                                      modelObject.latSize, \
                                      modelObject.longSize), numpy.float32)

remappedLong = numpy.zeros(lenLong, float32)
remappedLong [0:lenLong/2] = modelObject.long[lenLong/2:lenLong] - 360.0
remappedLong [lenLong/2:lenLong] = modelObject.long[0:lenLong/2]




newModelArray = numpy.zeros((modelObject.latSize, \
                               modelObject.longSize), numpy.float32)



                             
print ""
print "Processing: ", fieldToRemap, " with longitude of length: ", lenLong
print ""




for timeRecord in range(0, size(modelObject.time)):

    modelFieldArray = modelObject.returnField (field, timeRecord)

    print ""
    print "Shape of field: ", modelFieldArray.shape[:], " time: ", timeRecord
    print ""

    remappedModelArray [timeRecord,:,:, 0:lenLong/2] = modelFieldArray[:,:,lenLong/2:lenLong]
    remappedModelArray [timeRecord,:,:, lenLong/2:lenLong] = modelFieldArray[:,:,0:lenLong/2]


    

print ""
print "Min/max ", field, " values ", remappedModelArray.min(), "/", remappedModelArray.max()
print ""

                                  
print ""
print "Remapped longitude coordinate for : ", fieldToRemap
print ""

print ""
print remappedLong[:]
print ""


rootgrp = Dataset("test.nc", "w", format="NETCDF4")



#                                      'lon', 'lev', 'time' )

timeDim = rootgrp.createDimension("time", None)
levelDim = rootgrp.createDimension("lev", levelSize)
latDim = rootgrp.createDimension("lat", modelObject.latSize)
lonDim = rootgrp.createDimension("lon", modelObject.longSize)


levVar = rootgrp.createVariable("lev","f8",("lev",))
latVar = rootgrp.createVariable("lat","f8",("lat",))
lonVar = rootgrp.createVariable("lon","f8",("lon",))
fieldVar = rootgrp.createVariable(field,"f8",("time","lev","lat","lon"))

lonVar[:] = remappedLong[:]
latVar[:] = modelObject.lat[:]
levVar[:] = range(1,levelSize+1)
#timeVar[:] = modelObject.time[:]

fieldVar[:,:,:,:] = remappedModelArray[:,:,:,:]

rootgrp.close()
