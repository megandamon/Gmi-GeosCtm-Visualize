#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Oct 20 2019
#
# DESCRIPTION:
# Driver to plot zonal means of a tracer specie.
#------------------------------------------------------------------------------

#-------------
# Load modules
#-------------
import os
import sys
import getopt
import glob

from netCDF4 import Dataset

from numpy.random import uniform
from numpy import *

import matplotlib.pyplot as plt            # pyplot module import
from matplotlib.ticker import NullFormatter
import matplotlib.cm as cm
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import colors, ticker
from matplotlib.backends.backend_pdf import PdfPages

import vertLevels_GEOS5 as pressLevels
from viz_functions import *

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from TracerPlotTools import TracerPlotTools


COLORMAP = "rainbow"
NUM_ARGS = 5

def usage ():
    print("")
    print("usage: PlotTracerZM.py [-g] [-r] [-d] [-k] [-f]")
    print("-g GEOS file ")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-k Key file for tracers")
    print("-f field to plot")
    print("")
    sys.exit (0)


print("Start plotting field")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'g:r:d:k:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile = optList[0][1]
timeRecord = int(optList[1][1])
dateYearMonth = optList[2][1]
keyFile =     str(optList[3][1])
fieldToPlot = str(optList[4][1])



#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (modelFile):
    print("The file you provided does not exist: ", modelFile)
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM")
    print("Received: ", dateYearMonth)
    sys.exit(0)

#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------




tracerTools = TracerPlotTools (keyFile)
tracerTools.setUnitInfo(fieldToPlot)
tracerTools.setLevelInfo(fieldToPlot)

contourLevelsFloat = zeros(len(tracerTools.contourLevels), dtype=float)
count = 0
for lev in tracerTools.contourLevels:
    contourLevelsFloat[count] = float(lev)
    count = count + 1

if len(contourLevelsFloat) == 0:
    contourLevelsFloat = []


modelObject = GeosCtmPlotTools (modelFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )
modelFieldArray = modelObject.returnField (fieldToPlot, timeRecord)
newModelFieldArray = modelFieldArray * float(tracerTools.unitConvert)
modelFieldArray = newModelFieldArray
newModelFieldArray = None

llIndex = modelObject.findLevelFromArray(modelObject.lev, float(tracerTools.lowerLevel))
ulIndex = modelObject.findLevelFromArray(modelObject.lev, float(tracerTools.upperLevel))

zmArray = mean(modelFieldArray[llIndex:ulIndex+1, :, :], axis=2)




#-----------------------------------------------------#
# Model  Plotting

fig = plt.figure(figsize=(20,20))

plotOpt = {}

modelSimName = modelFile.split(".")[0] + "-" + modelFile.split(".")[1]


plotOpt['title'] = modelSimName + "    " + fieldToPlot +  " Zonal Mean " + \
    " (" + tracerTools.longName + ") " + str(dateYearMonth )
plotOpt['units'] = tracerTools.units


ax1 = fig.add_subplot(111)
plotZM (zmArray, modelObject.lat[:], modelObject.lev[llIndex:ulIndex+1], \
            fig, ax1, COLORMAP, \
            zmArray.min(), zmArray.max(), \
            plotOpt=plotOpt, contourLevels=contourLevelsFloat)

fileTitle = "-" + modelSimName + "_ZM."
plt.savefig ("plots/" + fieldToPlot + fileTitle \
                 + ".", bbox_inches='tight')

print("")
print("Plotted zonal mean for: ", fieldToPlot, " to plots/ directory")
print("") 

