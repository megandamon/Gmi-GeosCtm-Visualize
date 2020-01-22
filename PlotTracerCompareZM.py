#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Nov 22 2019
#
# DESCRIPTION:
# Driver to plot comparisions of zonal means from tracer species.
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

import matplotlib.pyplot as plt            # pyplot module import
import matplotlib.cm as cm

import vertLevels_GEOS5 as pressLevels
from viz_functions import *

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from TracerPlotTools import TracerPlotTools


COLORMAP = "rainbow"
NUM_ARGS = 10

def usage ():
    print("")
    print("usage: PlotTracerCompareZM.py [-g] [-c] [-r] [-d] [-l] [-u] [-n] [-t] [-k] [-f]")
    print("-g GEOS file 1")
    print("-c GEOS file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-l lower level to plot (mbs)")
    print("-u lower level to plot (mbs)")
    print("-n unit conversion")
    print("-t new unit name (if -u is not 1)")
    print("-k Key file for tracers")
    print("-f field to plot")
    print("")
    sys.exit (0)


print("Start plotting field differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'g:c:r:d:l:u:n:t:k:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile1 = optList[0][1]
modelFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
lowerLevel = float(optList[4][1])
upperLevel = float(optList[5][1])
unitConvert = float(optList[6][1])
newUnitName = str(optList[7][1])
keyFile =     str(optList[8][1])
fieldToPlot = str(optList[9][1])



#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (modelFile1):
    print("The file you provided does not exist: ", modelFile1)
    sys.exit(0)

if not os.path.exists (modelFile2):
    print("The file you provided does not exist: ", modelFile1)
    sys.exit(0)

if int(timeRecord) > 31: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM")
    print("Received: ", dateYearMonth)
    sys.exit(0)

if lowerLevel < 0.1: 
    print("WARNING: the lower level is high in the atmsophere")

if upperLevel > 1000.0:
    print("WARNING: the upper level is low in the atmosphere")

if not os.path.exists (keyFile):
    print("The file you provided does not exist: ", keyFile)
    sys.exit(0)


print("")
print(modelFile1)
print(modelFile2)
print("")

model1SimName = modelFile1.split(".")[0] + "-" + modelFile1.split(".")[1]
model2SimName = modelFile2.split(".")[0] + "-" + modelFile2.split(".")[1]


print("")
print(model1SimName)
print(model2SimName)
print("")


print ("unit conversion: ", unitConvert)

tracerTools = TracerPlotTools (keyFile)
count = 0
for tracer in range(len(tracerTools.tracerDict)):
    
    if fieldToPlot == tracerTools.tracerDict[count]["name"]:
        contourLevelsLocal = tracerTools.tracerDict[count]['contourLevels']

    print (tracerTools.tracerDict[count]['name'], tracerTools.tracerDict[count]['long_name'], 
           tracerTools.tracerDict[count]['slices'], tracerTools.tracerDict[count]['lowLevel'], 
           tracerTools.tracerDict[count]['highLevel'], tracerTools.tracerDict[count]['unitConvert'], 
           tracerTools.tracerDict[count]['newUnit'])
    count = count + 1

print("")



contourLevelsFloat = zeros(len(contourLevelsLocal), dtype=float)

count = 0
for lev in contourLevelsLocal:
    contourLevelsFloat[count] = float(lev)
    count = count + 1

if len(contourLevelsFloat) == 0:
    contourLevelsFloat = []





#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------

model1Object = GeosCtmPlotTools (modelFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )

model2Object = GeosCtmPlotTools (modelFile2, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )





print("")
print("Model 1 vertical levels: ", model1Object.lev[:])
print("Model 2 vertical levels: ", model2Object.lev[:])
print("")



if unitConvert == 1:
    units = model1Object.hdfData.variables[fieldToPlot].getncattr('units')
else:
    units = newUnitName


fillValue1 = model1Object.hdfData.variables[fieldToPlot].getncattr('_FillValue')
fillValue2 = model2Object.hdfData.variables[fieldToPlot].getncattr('_FillValue')

print ("")
print ("Units: ", units)
print ("Fill value1: ", fillValue1)
print ("Fill value2: ", fillValue2)
print ("")



modelFieldArray1 = model1Object.returnField (fieldToPlot, timeRecord)
modelFieldArray2 = model2Object.returnField (fieldToPlot, timeRecord)

newModel1FieldArray = modelFieldArray1 * unitConvert
modelFieldArray1 = newModel1FieldArray
newModel1FieldArray = None

newModel2FieldArray = modelFieldArray2 * unitConvert
modelFieldArray2 = newModel2FieldArray
newModel2FieldArray = None



print("")
print("modelFieldArray1 shape: ", modelFieldArray1.shape)
print("modelFieldArray2 shape: ", modelFieldArray2.shape)
print("")

print("")
print("Global sum 1 of ", fieldToPlot, " : ", sum(modelFieldArray1))
print("Global sum 1 of ", fieldToPlot, " : ", sum(modelFieldArray2))
print("")


#print(type(model1Object.lev[0]))
#levs1 = pressLevels.calcPressureLevels(len(model1Object.lev))
#levs = levs1[::-1]


print ()
print ("Vertical layers between: ")
print (lowerLevel, upperLevel)
print ()

#llValue = (min(model1Object.lev, key=lambda x:abs(x-lowerLevel)))
#ulValue = (min(model1Object.lev, key=lambda x:abs(x-upperLevel)))
#llIndex1 = where(model1Object.lev == llValue)
#ulIndex1 = where(model1Object.lev == ulValue)
#llIndex = llIndex1[0][0]
#ulIndex =  ulIndex1[0][0]

llIndex = model1Object.findLevelFromArray(model1Object.lev, lowerLevel)
ulIndex = model1Object.findLevelFromArray(model1Object.lev, upperLevel)

print ()
print ("Index values are: ")
print (llIndex, ulIndex)
print ()


zmArray1 = mean(modelFieldArray1[llIndex:ulIndex+1, :, :], axis=2)
zmArray2 = mean(modelFieldArray2[llIndex:ulIndex+1, :, :], axis=2)

print ()
print ("Shape of zmArray1: ", zmArray1.shape)
print ("Shape of zmArray2: ", zmArray2.shape)
print ()



if zmArray1.shape != zmArray2.shape:

    print("")
    print("Field arrays are not the same, interpolation required!")
    print("")

    print (type(zmArray1))

    model1NumPoints = len(zmArray1.flatten())
    model2NumPoints = len(zmArray2.flatten())


    print("")
    print("Field 1 num points: ", model1NumPoints)
    print("Field 2 num points: ", model2NumPoints)
    print("")

    if model1NumPoints < model2NumPoints:

        modelObject = model1Object
        newZmArray2 = model2Object.returnInterpolatedFieldZM(zmArray2, 
                                                             model1Object.lat, 
                                                             timeRecord, 
                                                             replaceValue=fillValue2)
        zmArray2 = None
        zmArray2 = newZmArray2
        
        zmArray1[zmArray1>=fillValue1] = 0.0

    else:
        modelObject = model2Object
        newZmArray1 = model1Object.returnInterpolatedFieldZM(zmArray1, 
                                                             model2Object.lat,
                                                             timeRecord, 
                                                             replaceValue=fillValue1)
        zmArray1 = None
        zmArray1 = newZmArray1

        zmArray2[zmArray2>fillValue2] = 0.0


    




fig = plt.figure(figsize=(20,20))

plotOpt = {}


plotOpt['title'] = model1SimName + "     " + fieldToPlot +  "    Zonal Mean " + dateYearMonth
plotOpt['units'] = units

print (plotOpt['title'])
print (model1Object.lev[ulIndex:llIndex+1])


print (zmArray1.shape)
print (model1Object.lev[llIndex:ulIndex+1].shape)
print (modelObject.lat.shape)


minValueBoth = zmArray1.min()
maxValueBoth = zmArray1.max()

if zmArray2.min() < minValueBoth:
    minValueBoth = zmArray2.min()
if zmArray2.max() > maxValueBoth:
    maxValueBoth = zmArray2.max()




ax1 = fig.add_subplot(311)
plotZM (zmArray1 ,modelObject.lat[:], modelObject.lev[llIndex:ulIndex+1], \
            fig, ax1, COLORMAP, \
            minValueBoth, maxValueBoth, \
            plotOpt=plotOpt, contourLevels=contourLevelsFloat)


plotOpt['title'] = model2SimName + "     " + fieldToPlot +  "    Zonal Mean " + dateYearMonth

ax2 = fig.add_subplot(312)
plotZM (zmArray2 ,modelObject.lat[:], modelObject.lev[llIndex:ulIndex+1], \
            fig, ax2, COLORMAP, \
            minValueBoth, maxValueBoth, \
            plotOpt=plotOpt, contourLevels=contourLevelsFloat)

if units.find("days") != -1:
    analType = "r"
    analString = "ratio"
if units.find("years") != -1:
    analType = "r"
    analString = "ratio"
if units.find("kg-1") != -1:
    analType = "r"
    analString = "ratio"
if units.find("ppt") != -1:
    analType = "r"
    analString = "ratio"
if units.find("ppb") != -1:
    analType = "r"
    analString = "ratio"
if units.find("mol-1") != -1:
    analType = "r"
    analString = "ratio"



plotOpt['title'] = analString + "     " + fieldToPlot +  "    Zonal Mean " + dateYearMonth

zDiff = modelObject.createComparision2D (zmArray1, zmArray2, analType)

ax3 = fig.add_subplot(313)
plotZM (zDiff ,modelObject.lat[:], modelObject.lev[llIndex:ulIndex+1], \
            fig, ax3, 'nipy_spectral', \
            0.5, 1.5, \
            plotOpt=plotOpt,contourLevels=[])



fileTitle = "-" + model1SimName + "." + model2SimName + "_ZM."
plt.savefig ("plots/" + fieldToPlot + fileTitle \
                 + ".", bbox_inches='tight')
