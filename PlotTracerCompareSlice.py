
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


print("")
print("File1 name: ", model1File)
print("File2 name: ", model1File)
print("")

model1SimName = model1File.split(".")[0] + "-" + model1File.split(".")[1]
model2SimName = model2File.split(".")[0] + "-" + model2File.split(".")[1]


print("")
print("Simulation 1 name:", model1SimName)
print("Simulation 2 name:", model2SimName)
print("")


print("")
print("Field to plot: ", fieldToPlot)
print(longName)
print("")





model1Object = GeosCtmPlotTools (model1File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )

model2Object = GeosCtmPlotTools (model2File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )



fillValue1 = model1Object.hdfData.variables[fieldToPlot].getncattr('_FillValue')
fillValue2 = model2Object.hdfData.variables[fieldToPlot].getncattr('_FillValue')


print ("")
print ("Fill value1: ", fillValue1)
print ("Fill value2: ", fillValue2)
print ("")



levs1 = model1Object.returnPressureLevels()
levs2 = model2Object.returnPressureLevels()

print ()
print ("levs1: ", levs1)
print ("levs2: ", levs2)
print ()


model1FieldArray = model1Object.returnField (fieldToPlot, timeRecord)
model2FieldArray = model2Object.returnField (fieldToPlot, timeRecord)

print("")
print("Model 1 min / max raw: ", model1FieldArray.min(), " / ", model1FieldArray.max())
print("")
print("")
print("Model 2 min / max raw: ", model2FieldArray.min(), " / ", model2FieldArray.max())
print("")


newModel1FieldArray = model1Object.return2DSliceFromRefPressure (model1FieldArray, fileLevel)
newModel2FieldArray = model1Object.return2DSliceFromRefPressure (model2FieldArray, fileLevel)

print ()
print (type(newModel1FieldArray))
print (type(newModel2FieldArray))
print ()

model1FieldArray = None
model1FieldArray = newModel1FieldArray * float(tracerTools.unitConvert)
newModel1FieldArray = None

model2FieldArray = None
model2FieldArray = newModel2FieldArray * float(tracerTools.unitConvert)
newModel2FieldArray = None


print("")
print("model1FieldArray shape: ", model1FieldArray.shape)
print("model2FieldArray shape: ", model2FieldArray.shape)
print("")



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

#***********************************************

print("")
print("Model 1 2D min / max interp: ", model1FieldArray.min(), " / ", model1FieldArray.max())
print("")

print("")
print("Model 2 2D min / max interp: ", model2FieldArray.min(), " / ", model2FieldArray.max())
print("")



#***********************************************
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


print ()
print ("min/max Z values at pressure ", fileLevel, " are: ", z_Model.min(), z_Model.max())
print ()
#***********************************************










#-----------------------------------------------------#
# Model  Plotting


minModelLat = modelObject.lat[:].min()
maxModelLat = modelObject.lat[:].max()
minModelLong = modelObject.long[:].min()
maxModelLong = modelObject.long[:].max()


plt.figure(figsize=(20,20))


model1Object.createPlotObjects()
model2Object.createPlotObjects()


print ()
print ("Min / max values of both model 1 and 2: ", minValueBoth, maxValueBoth)
print ()

stringLevel = str(fileLevel)

print("")
print("Level: ", stringLevel)
print("")


plotTitle1 = model1SimName + "     " + fieldToPlot + " @ " + str(int(float(stringLevel))) \
    + " hPa (" + longName + ") " + dateYearMonth



modelObject.create2dSliceContours (modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, model1FieldArray, \
                                       [minValueBoth, maxValueBoth], \
                                       [minModelLat,maxModelLat], \
                                       [minModelLong, maxModelLong], 311, \
                                       plotTitle1, COLORMAP, tracerTools.units, \
                                       contourLevels=tracerTools.contourLevels)


plotTitle2 = model2SimName + "     " + fieldToPlot + " @ " + str(int(float(stringLevel))) \
     + " hPa (" + longName + ") " + dateYearMonth

modelObject.create2dSliceContours (modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, model2FieldArray, \
                                       [minValueBoth, maxValueBoth], \
                                       [minModelLat,maxModelLat], \
                                       [minModelLong, maxModelLong], 312, \
                                       plotTitle2, COLORMAP, tracerTools.units, \
                                       contourLevels=tracerTools.contourLevels)




plotTitle3 = analString + "     " + fieldToPlot + " @ " + str(int(float(stringLevel))) \
     + " hPa (" + longName + ") " + dateYearMonth

modelObject.create2dSliceContours (modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, z_Model, \
                                       [.5,1.5], \
                                       [minModelLat,maxModelLat], \
                                       [minModelLong, maxModelLong], 313, \
                                       plotTitle3, "nipy_spectral", units=None, contourLevels=[])

file = "f"
if file == "f":
    plt.savefig("plots/" + fieldToPlot + "-" + model1SimName + "_" + str(int(float(stringLevel))) \
                    + "hPa.", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()


print("")
print("Plotted : ", fieldToPlot, " to plots/ directory")
print("") 
