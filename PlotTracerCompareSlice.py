
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Nobember 20th 2019
#
# DESCRIPTION:
# Driver to plot comparisions of a lat/lon slice of a tracer (mb/hPa).
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
NUM_ARGS = 8
#*********************



#*********************
def usage ():
    print("")
    print("usage: PlotTracerCompareSlice.py [-c] [-g] [-l] [-r] [-d] [-n] [-k] [-f] ")
    print("-g Model file 1")
    print("-c Model file 2")
    print("-l vertical level (hPa)")
    print("-r time record to plot")
    print("-d date (YYYYMM)")
    print("-n long name of tracer")
    print("-k Key file for tracers")
    print("-f tracer to plot")
    print("")
    sys.exit (0)


print("Start plotting field differences.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'g:c:l:r:d:n:k:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

model1File = str(optList[0][1])
model2File = str(optList[1][1])
fileLevel = float(optList[2][1])
timeRecord = int(optList[3][1])
dateYearMonth = optList[4][1]
longName = str(optList[5][1])
keyFile = str(optList[6][1])
fieldToPlot = str(optList[7][1])

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (model1File):
    print("The file you provided does not exist: ", model1File)
    sys.exit(0)

if not os.path.exists (model2File):
    print("The file you provided does not exist: ", model2File)
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

if fileLevel < 0.1 and fileLevel > 1300.: 
    print("GEOS-5 pressure levels should be < 1300 and > 0.1 mb/hPa")
    sys.exit(0)
#*********************


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#---------------------------------------------------------------



tracerTools = TracerPlotTools (keyFile)
tracerTools.setUnitInfo(fieldToPlot)


model1Object = GeosCtmPlotTools (model1File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )
fillValue1 = model1Object.hdfData.variables[fieldToPlot].getncattr('_FillValue')
model1FieldArray = model1Object.return2DSliceAndConvert (fieldToPlot, timeRecord, \
                                                             fileLevel, float(tracerTools.unitConvert))


model2Object = GeosCtmPlotTools (model2File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )
fillValue2 = model2Object.hdfData.variables[fieldToPlot].getncattr('_FillValue')
model2FieldArray = model2Object.return2DSliceAndConvert (fieldToPlot, timeRecord, \
                                                             fileLevel, float(tracerTools.unitConvert))


#***********************************************
if model1FieldArray.shape != model2FieldArray.shape:

    print("")
    print("Field arrays are not the same, interpolation required!")
    print("")

    model1NumPoints = len(model1FieldArray.flatten())
    model2NumPoints = len(model2FieldArray.flatten())


    print("")
    print("Field 1 num points: ", model1NumPoints)
    print("Field 2 num points: ", model2NumPoints)
    print("")

    if model1NumPoints < model2NumPoints:

        modelObject = model1Object
        newModel2FieldArray = model2Object.returnInterpolatedFieldLatLon(model2FieldArray, 
                                                                         model1Object.lat, 
                                                                         model1Object.long,
                                                                         timeRecord, 
                                                                         replaceValue=fillValue2)
        model2FieldArray = None
        model2FieldArray = newModel2FieldArray
        
        model1FieldArray[model1FieldArray>=fillValue1] = 0.0

    else:
        modelObject = model2Object
        newModel1FieldArray = model1Object.returnInterpolatedFieldLatLon(model1FieldArray, 
                                                                         model2Object.lat,
                                                                         model2Object.long,
                                                                         timeRecord, 
                                                                         replaceValue=fillValue1)
        model1FieldArray = None
        model1FieldArray = newModel1FieldArray

        model2FieldArray[model2FieldArray>=fillValue2] = 0.0


minValueBoth = model1FieldArray.min()
maxValueBoth = model1FieldArray.max()

if model2FieldArray.min() < minValueBoth:
    minValueBoth = model2FieldArray.min()
if model2FieldArray.max() > maxValueBoth:
    maxValueBoth = model2FieldArray.max()
#***********************************************


print("")
print("Global sum 1 of ", fieldToPlot, " : ", sum(model1FieldArray))
print("Global sum 2 of ", fieldToPlot, " : ", sum(model2FieldArray))
print("")



#***********************************************
if tracerTools.units.find("days") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.units.find("years") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.units.find("kg-1") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.units.find("ppt") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.units.find("ppb") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.units.find("mol-1") != -1:
    analType = "r"
    analString = "ratio"


z_Model = modelObject.createComparisionLatLon(model1FieldArray, model2FieldArray, analType)
#***********************************************


#-----------------------------------------------------#
# Model  Plotting

plt.figure(figsize=(20,20))
modelObject.createPlotObjects()

model1SimName = model1File.split(".")[0] + "-" + model1File.split(".")[1]
plotTitle1 = model1SimName + "     " + fieldToPlot + " @ " + str(fileLevel) \
    + " hPa (" + longName + ") " + dateYearMonth
modelObject.create2dSliceContours (modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, model1FieldArray, \
                                       [minValueBoth, maxValueBoth], \
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()], \
                                       [modelObject.long[:].min(), modelObject.long[:].max()], 311, \
                                       plotTitle1, COLORMAP, tracerTools.units, \
                                       contourLevels=tracerTools.contourLevels)


model2SimName = model2File.split(".")[0] + "-" + model2File.split(".")[1]
plotTitle2 = model2SimName + "     " + fieldToPlot + " @ " + str(fileLevel) \
     + " hPa (" + longName + ") " + dateYearMonth
modelObject.create2dSliceContours (modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, model2FieldArray, \
                                       [minValueBoth, maxValueBoth], \
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()], \
                                       [modelObject.long[:].min(), modelObject.long[:].max()], 312, \
                                       plotTitle2, COLORMAP, tracerTools.units, \
                                       contourLevels=tracerTools.contourLevels)




plotTitle3 = analString + "     " + fieldToPlot + " @ " + str(fileLevel) \
     + " hPa (" + longName + ") " + dateYearMonth
modelObject.create2dSliceContours (modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, z_Model, \
                                       [.5,1.5], \
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()], \
                                       [modelObject.long[:].min(), modelObject.long[:].max()], 313, \
                                       plotTitle3, "nipy_spectral", units=None, contourLevels=[])

file = "f"
if file == "f":
    plt.savefig("plots/" + fieldToPlot + "-" + model1SimName + "_" + str(fileLevel) \
                    + "hPa.", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()


print("")
print("Plotted slice for : ", fieldToPlot, " to plots/ directory")
print("") 
