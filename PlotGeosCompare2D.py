
 
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         April 17 2020
#
# DESCRIPTION:
# Driver to plot 2D comparisions between GEOS files. 
#-------------------------------------------------1----------------------------

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
import pandas as pd






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

import vertLevels_GEOS5 as pressLevels

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from TracerPlotTools import TracerPlotTools



#*********************
COLORMAP = "rainbow"
RATIO_COLORMAP = "bwr"
RATIO_CONTOUR_LEVELS = [.5,.6,.7,.8,.9,1.0,1.1,1.2,1.3,1.4,1.5]
DEFAULT_PERCHANGE_CONTOURS = [-1000, -500, -100, -50, -20, -10, -5, -2, -.05, 0.5, 2, 5, 10, 20, 50, 100, 500, 1000]
DEFAULT_PERCHANGE_CONTOURS = [-100, -75, -50, -40, -30, -20, -10, -5, 0, 5, 10, 20, 30, 40, 50, 75, 100]
NUM_ARGS = 7
#*********************



#*********************
def usage ():
    print("")
    print("usage: PlotGeosCompare2D.py [-g] [-c] [-r] [-d] [-k] [-f] [-p]")
    print("-g Model file 1")
    print("-c Model file 2")
    print("-r time record to plot")
    print("-d date (YYYYMM)")
    print("-k Key file for tracers")
    print("-p percentage change contours (d-default-+-100, a-algorithmic")
    print("-f tracer to plot")
    print("")
    sys.exit (0)
#*********************


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'g:c:r:d:k:p:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

model1File = str(optList[0][1])
model2File = str(optList[1][1])
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
keyFile = str(optList[4][1])
percChangeContours = str(optList[5][1])
fieldToPlot = str(optList[6][1])


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

if len(dateYearMonth) != 6 and len(dateYearMonth) != 4:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)

if not os.path.exists (keyFile):
    print("The file you provided does not exist: ", keyFile)
    sys.exit(0)

if percChangeContours != "d" and percChangeContours != "a":
    print("Percent change contours should be either d(deafult) or a(algorithmic)")
    sys.exit(0)



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#---------------------------------------------------------------


model1Object = GeosCtmPlotTools (model1File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )

model1SimName = model1File.split(".")[0] + "-" + model1File.split(".")[1]
model1SimName2 = model1SimName.split("_")[0] + "_" + model1SimName.split("_")[1]
model1SimName = model1SimName2
model2SimName = model2File.split(".")[0] + "-" + model2File.split(".")[1]
model2SimName2 = model2SimName.split("_")[0] + "_" + model2SimName.split("_")[1]
model2SimName = model2SimName2


print ("keyFile in PlotGeosCompare2D: ", keyFile)

tracerTools = TracerPlotTools (model1Object, keyFile)

if fieldToPlot not in model1Object.hdfData.variables.keys():

    if fieldToPlot.islower() == True:
        fieldToPlot1 = fieldToPlot.upper()
    else:
        fieldToPlot1 = fieldToPlot.lower()
else:
    fieldToPlot1 = fieldToPlot


model1FieldArray = model1Object.returnField (fieldToPlot, timeRecord)
print ("model1FieldArray min/max: ", model1FieldArray.min(), model1FieldArray.max())
#preConvertFieldArray1 = tracerTools.tracerDict[fieldToPlot].preConversion(model1FieldArray, model1SimName)

print (tracerTools, tracerTools.__dict__)

newModel1FieldArray = model1FieldArray * \
    float(tracerTools.tracerDict[fieldToPlot].unitConvert) # key convert

tracerTools.tracerDict[fieldToPlot].units  = tracerTools.tracerDict[fieldToPlot].newUnit

model1FieldArray = newModel1FieldArray
newModel1FieldArray = None

print ("model1FieldArray min/max: ", model1FieldArray.min(), model1FieldArray.max())

model2Object = GeosCtmPlotTools (model2File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )





model2FieldArray = model2Object.returnField (fieldToPlot, timeRecord)
#preConvertFieldArray2 = tracerTools.tracerDict[fieldToPlot].preConversion(model2FieldArraySlice, model2SimName)

newModel2DFieldArray = model2FieldArray * \
    float(tracerTools.tracerDict[fieldToPlot].unitConvert) # key convert

tracerTools.tracerDict[fieldToPlot].units  = tracerTools.tracerDict[fieldToPlot].newUnit

model2FieldArray = newModel2DFieldArray
newModel2FieldArray = None




#***********************************************
if model1FieldArray.shape != model2FieldArray.shape:

    print("")
    print("Field arrays are not the same, interpolation required!")
    print("")

    model1NumPoints = len(model1FieldArray.flatten())
    model2NumPoints = len(model2FieldArray.flatten())

    print ("")
    if model1NumPoints < model2NumPoints:
        
        print ("model1 has fewer points (", model1NumPoints, "<", model2NumPoints, ") ; will interpolate to the grid of model 1")


        model2FieldArrayInterp = model2Object.interpMaskedFieldLatLon (model1FieldArray, model2FieldArray, \
                                                                    model1Object.lat, model1Object.long, \
                                                                    timeRecord, replaceValue = None)

        model2FieldArray = None
        model2FieldArray = model2FieldArrayInterp

        modelObject = model1Object

    else:

        print ("model2 has fewer points (", model2NumPoints, "<", model1NumPoints, ") ; will interpolate to the grid of model 2")


        model1FieldArrayInterp = model1Object.interpMaskedFieldLatLon (model2FieldArray, model1FieldArray, \
                                                                     model2Object.lat, model2Object.long, \
                                                                     timeRecord, replaceValue = None)
        model1FieldArray = None
        model1FieldArray = model1FieldArrayInterp
        modelObject = model2Object

else:
    modelObject = model1Object

print ("")




minValueBoth = model1FieldArray.min()
maxValueBoth = model1FieldArray.max()

if model2FieldArray.min() < minValueBoth:
    minValueBoth = model2FieldArray.min()
if model2FieldArray.max() > maxValueBoth:
    maxValueBoth = model2FieldArray.max()
#***********************************************


print("")
print("min/max value of both models: ", minValueBoth, maxValueBoth)
print("Global sum 1 of ", fieldToPlot, " : ", sum(model1FieldArray))
print("Global sum 2 of ", fieldToPlot, " : ", sum(model2FieldArray))
print("")


#***********************************************
if tracerTools.tracerDict[fieldToPlot].units.find("days") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.tracerDict[fieldToPlot].units.find("years") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.tracerDict[fieldToPlot].units.find("kg-1") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.tracerDict[fieldToPlot].units.find("ppt") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.tracerDict[fieldToPlot].units.find("ppb") != -1:
    analType = "r"
    analString = "ratio"
if tracerTools.tracerDict[fieldToPlot].units.find("mol-1") != -1:
    analType = "r"
    analString = "ratio"

#***********************************************


#-----------------------------------------------------#
# Model  Plotting


if tracerTools.tracerDict[fieldToPlot].zmContours == None:

    print ("Calling createTracerContoursFromMinMax")
    step = (maxValueBoth - minValueBoth) / 10.
    contours = tracerTools.tracerDict[fieldToPlot].createTracerContoursFromMinMax(minValueBoth, \
                                                              maxValueBoth, \
                                                              step=float('{:0.2e}'.format(step)))
                                                              
else:
    contours = []
    for contour in tracerTools.tracerDict[fieldToPlot].zmContours:
        contours.append(float(contour))
    print ("Received 2d contours from input file")



fig = plt.figure(figsize=(20,20))
modelObject.createPlotObjects()


plotTitle1 = model1SimName + "     " + fieldToPlot + "    " + dateYearMonth
modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, model1FieldArray, \
                                       [minValueBoth, maxValueBoth], \
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()], \
                                       [modelObject.long[:].min(), modelObject.long[:].max()], \
                                       "fuchsia", "darkred", \
                                       221, \
                                       plotTitle1, \
                                       COLORMAP, tracerTools.tracerDict[fieldToPlot].units, \
                                       contourLevels=contours)



plotTitle2 = model2SimName + "     " + fieldToPlot + "    " + dateYearMonth
modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, model2FieldArray, \
                                       [minValueBoth, maxValueBoth], \
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()], \
                                       [modelObject.long[:].min(), modelObject.long[:].max()], 
                                       "fuchsia", "darkred", \
                                       222, \
                                       plotTitle2, COLORMAP, tracerTools.tracerDict[fieldToPlot].units, \
                                       contourLevels=contours)





analType = "s"
analString = "diff"
z_Model = modelObject.createComparisionLatLon(model1FieldArray, model2FieldArray, analType)

print (z_Model.min(), z_Model.max())


diffContourLevels = tracerTools.tracerDict[fieldToPlot].createDiffContoursFromMinMax(z_Model.min(), z_Model.max())


print (diffContourLevels)



plotTitle3 = analString + "     " + fieldToPlot + "   " + dateYearMonth
modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, z_Model, \
                                       [z_Model.min(), z_Model.max()], \
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()], \
                                       [modelObject.long[:].min(), modelObject.long[:].max()], 
                                       "navy", "darkred", \
                                       223, \
                                       plotTitle3, "coolwarm", units=tracerTools.tracerDict[fieldToPlot].units, \
                                       labelContours=False, \
                                       contourLevels=diffContourLevels)




analType = "c"
analString = "perc change"
z_Model = None
z_Model = modelObject.createComparisionLatLon(model1FieldArray, model2FieldArray, analType)


if percChangeContours == "d":
    percDiffContours =  DEFAULT_PERCHANGE_CONTOURS

else:
    print ("Create percDiffContours!")
    percDiffContours = tracerTools.tracerDict[fieldToPlot].createPercChangeContoursFromMinMax\
        (z_Model.min(), z_Model.max())
#    if percDiffContours [0] < -100.0:
#        percDiffContours = DEFAULT_PERCHANGE_CONTOURS


percDiffContours =  DEFAULT_PERCHANGE_CONTOURS 

print (percDiffContours)


plotTitle4 = analString + "     " + fieldToPlot + "   " + dateYearMonth
modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid, \
                                       modelObject.Y_grid, z_Model, \
                                       [z_Model.min(), z_Model.max()], \
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()], \
                                       [modelObject.long[:].min(), modelObject.long[:].max()], \
                                       "navy", "darkred", \
                                       224, \
                                       plotTitle4, "coolwarm", units="%", labelContours=False, \
                                       contourLevels=percDiffContours)

file = "f"
if file == "f":
    plt.savefig("plots/" + fieldToPlot + "-" + model1SimName + "_" + model2SimName + \
                    "_" + str(dateYearMonth) + ".", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()


print("")
print("Plotted slice for : ", fieldToPlot, " to plots/ directory")
print("") 
