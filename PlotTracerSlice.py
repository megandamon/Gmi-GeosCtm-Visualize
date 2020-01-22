
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         May 5 2019
#
# DESCRIPTION:
# Driver to plot a single tracer slice at designated level.
#-----------------------------------------------------------------------------

import re
import os
import sys
import random
import datetime
import calendar
import getopt
import numpy
from numpy import *

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


from netCDF4 import Dataset
import math



from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap







sys.path.append('/discover/nobackup/mrdamon/MERRA2')

import vertLevels_GEOS5 as pressLevels

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from TracerPlotTools import TracerPlotTools



#*********************
COLORMAP = "rainbow"
NUM_ARGS = 7
#*********************




def usage ():
    print("")
    print("usage: PlotTracerSlice.py [-c] [-l] [-r] [-d] [-n] [-k] [-f]")
    print("-c Model file")
    print("-l vertical level")
    print("-r time record to plot")
    print("-d date (YYYYMM)")
    print("-n long name of tracer")
    print("-k Key file for tracers")
    print("-f tracer to plot")
    print("")
    sys.exit (0)


print("Start plotting field slice.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:l:r:d:n:k:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile = str(optList[0][1])
fileLevel = int(optList[1][1])
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
longName = str(optList[4][1])
keyFile = str(optList[5][1])
fieldToPlot = str(optList[6][1])


#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (modelFile):
    print("The file you provided does not exist: ", modelFile)
    sys.exit(0)

if fileLevel < 0:
    print("The level to plot must be >= 0 (check file 1 lev)")
    sys.exit(0)

if int(timeRecord) > 31: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)

if not os.path.exists (keyFile):
    print("The file you provided does not exist: ", keyFile)
    sys.exit(0)
#*********************


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#---------------------------------------------------------------




tracerTools = TracerPlotTools (keyFile)
tracerTools.setUnitInfo(fieldToPlot)

print("")
print("File name: ", modelFile)
print("")

modelSimName = modelFile.split(".")[0] + "-" + modelFile.split(".")[1]


print("")
print("Simulation name:", modelSimName)
print("")


print("")
print("Field to plot: ", fieldToPlot)
print("")



modelObject = GeosCtmPlotTools (modelFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


fillValue = modelObject.hdfData.variables[fieldToPlot].getncattr('_FillValue')

print ("")
print ("Fill value: ", fillValue)
print ("")

levs = modelObject.returnPressureLevels()


print("")
print("Model eta levels: ", levs)
print("")



modelFieldArray = modelObject.returnField (fieldToPlot, timeRecord)

print("")
print("Model min / max raw: ", modelFieldArray.min(), " / ", modelFieldArray.max())
print("")


newModelFieldArray = modelObject.return2DSliceFromRefPressure (modelFieldArray, fileLevel)

print ()
print (type(newModelFieldArray))
print ()


print (tracerTools.unitConvert)

modelFieldArray = None
modelFieldArray = newModelFieldArray[:,:] * float(tracerTools.unitConvert)
newModelFieldArray = None

print("")
print("modelFieldArray shape: ", modelFieldArray.shape)
print("")

print("")
print("Model  2D min / max: ", modelFieldArray.min(), " / ", modelFieldArray.max())
print("")


print("")
print("Global sum of ", fieldToPlot, " : ", sum(modelFieldArray))
print("")




         
#-----------------------------------------------------#
# Model  Plotting


minModelLat = modelObject.lat[:].min()
maxModelLat = modelObject.lat[:].max()
minModelLong = modelObject.long[:].min()
maxModelLong = modelObject.long[:].max()


plt.figure(figsize=(20,20))

modelObject.createPlotObjects()


print("")
print("Model min / max : ", modelFieldArray.min(), " / ", modelFieldArray.max())
print("")


stringLevel = str(fileLevel)

print("")
print("Level: ", stringLevel)
print("")


plotTitle = modelSimName + "     " + fieldToPlot + " @ " + str(int(float(stringLevel))) \
    + " hPa (" + longName + ") " + dateYearMonth

modelObject.create2dSliceContours (modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, modelFieldArray, \
                                       [modelFieldArray.min(),modelFieldArray.max()], \
                                       [minModelLat,maxModelLat], \
                                       [minModelLong, maxModelLong], 111, \
                                       plotTitle, COLORMAP, tracerTools.units, \
                                       contourLevels=tracerTools.contourLevels)


file = "f"
if file == "f":
    plt.savefig("plots/" + fieldToPlot + "-" + modelSimName + "_" + str(int(float(stringLevel))) \
                    + "hPa.", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()




print("")
print("Plotted : ", fieldToPlot, " to plots/ directory")
print("") 




    

