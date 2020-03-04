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


#*********************
COLORMAP = "rainbow"
RATIO_COLORMAP = "bwr"
RATIO_CONTOUR_LEVELS = [.5,.6,.7,.8,.9,1.0,1.1,1.2,1.3,1.4,1.5]
NUM_ARGS = 6
#*********************

#*********************
def usage ():
    print("")
    print("usage: PlotTracerCompareZM.py [-g] [-c] [-r] [-d] [-k] [-f]")
    print("-g GEOS file 1")
    print("-c GEOS file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-k Key file for tracers")
    print("-f field to plot")
    print("")
    sys.exit (0)
#*********************




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
keyFile =     str(optList[4][1])
fieldToPlot = str(optList[5][1])



if not os.path.exists (modelFile1):
    print("The file you provided does not exist: ", modelFile1)
    sys.exit(0)

if not os.path.exists (modelFile2):
    print("The file you provided does not exist: ", modelFile2)
    sys.exit(0)

if int(timeRecord) > 31: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6 and len(dateYearMonth) != 4:
    print("ERROR date must be in the format YYYYMM")
    print("Received: ", dateYearMonth)
    sys.exit(0)

if not os.path.exists (keyFile):
    print("The file you provided does not exist: ", keyFile)
    sys.exit(0)


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------

model1Object = GeosCtmPlotTools (modelFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )

model1SimName = modelFile1.split(".")[0] + "-" + modelFile1.split(".")[1]
model1SimName2 = model1SimName.split("_")[0] + "_" + model1SimName.split("_")[1]
model1SimName = model1SimName2



tracerTools = TracerPlotTools (keyFile, model1Object)


if fieldToPlot not in model1Object.hdfData.variables.keys():
    print ("NOT IN KEYS")

    if fieldToPlot.islower() == True:
        fieldToPlot1 = fieldToPlot.upper()
    else:
        fieldToPlot1 = fieldToPlot.lower()
else:
    fieldToPlot1 = fieldToPlot


fillValue1 = model1Object.hdfData.variables[fieldToPlot1].getncattr('_FillValue')
modelFieldArray1 = model1Object.returnField (fieldToPlot, timeRecord)
preConvertFieldArray1 = tracerTools.tracerDict[fieldToPlot].preConversion(modelFieldArray1, \
                                                                              model1SimName)
newModel1FieldArray = preConvertFieldArray1 * float(tracerTools.tracerDict[fieldToPlot].unitConvert)
tracerTools.tracerDict[fieldToPlot].units  = tracerTools.tracerDict[fieldToPlot].newUnit

modelFieldArray1 = newModel1FieldArray
newModel1FieldArray = None
llIndex1 = model1Object.findLevelFromArray(model1Object.lev, float(tracerTools.tracerDict[fieldToPlot].lowLevel))
ulIndex1 = model1Object.findLevelFromArray(model1Object.lev, float(tracerTools.tracerDict[fieldToPlot].highLevel))
zmArray1 = mean(modelFieldArray1[llIndex1:ulIndex1+1, :, :], axis=2)


model2Object = GeosCtmPlotTools (modelFile2, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )

model2SimName = modelFile2.split(".")[0] + "-" + modelFile2.split(".")[1]
model2SimName2 = model2SimName.split("_")[0] + "_" + model2SimName.split("_")[1]
model2SimName = model2SimName2


if fieldToPlot not in model2Object.hdfData.variables.keys():
    print ("NOT IN KEYS")

    if fieldToPlot.islower() == True:
        fieldToPlot2 = fieldToPlot.upper()
    else:
        fieldToPlot2 = fieldToPlot.lower()
else:
    fieldToPlot2 = fieldToPlot


fillValue2 = model2Object.hdfData.variables[fieldToPlot2].getncattr('_FillValue')
modelFieldArray2 = model2Object.returnField (fieldToPlot, timeRecord)
preConvertFieldArray2 = tracerTools.tracerDict[fieldToPlot].preConversion(modelFieldArray2, \
                                                                             model2SimName)
newModel2FieldArray = preConvertFieldArray2 * float(tracerTools.tracerDict[fieldToPlot].unitConvert)
tracerTools.tracerDict[fieldToPlot].units  = tracerTools.tracerDict[fieldToPlot].newUnit

modelFieldArray2 = newModel2FieldArray
newModel2FieldArray = None
llIndex2 = model2Object.findLevelFromArray(model2Object.lev, float(tracerTools.tracerDict[fieldToPlot].lowLevel))
ulIndex2 = model2Object.findLevelFromArray(model2Object.lev, float(tracerTools.tracerDict[fieldToPlot].highLevel))
zmArray2 = mean(modelFieldArray2[llIndex2:ulIndex2+1, :, :], axis=2)











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

else:
    modelObject = model1Object

minValueBoth = zmArray1.min()
maxValueBoth = zmArray1.max()

if zmArray2.min() < minValueBoth:
    minValueBoth = zmArray2.min()
if zmArray2.max() > maxValueBoth:
    maxValueBoth = zmArray2.max()
 

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
    print ("Received zm contours from input file")



#-----------------------------------------------------#
# Model  Plotting


fig = plt.figure(figsize=(20,20))

plotOpt = {}



plotOpt['title'] = model1SimName + "     " + fieldToPlot +  "    Zonal Mean " + dateYearMonth
plotOpt['units'] = tracerTools.tracerDict[fieldToPlot].units


plotZM (zmArray1 ,modelObject.lat[:], modelObject.lev[llIndex1:ulIndex1+1], \
            fig, 221, COLORMAP, \
            minValueBoth, maxValueBoth, \
            "fuchsia", "darkred", \
            plotOpt=plotOpt, contourLevels=contours)



plotOpt['title'] = model2SimName + "     " + fieldToPlot +  "    Zonal Mean " + dateYearMonth


plotZM (zmArray2 ,modelObject.lat[:], modelObject.lev[llIndex2:ulIndex2+1], \
            fig, 222, COLORMAP, \
            minValueBoth, maxValueBoth, \
            "fuchsia", "darkred", \
            plotOpt=plotOpt, contourLevels=contours)

analType = "s"
analString = "diff"
zDiff = modelObject.createComparision2D(zmArray1, zmArray2, analType)

diffContourLevels = tracerTools.tracerDict[fieldToPlot].createDiffContoursFromMinMax\
    (zDiff.min(), zDiff.max())


plotOpt['title'] = analString + "     " + fieldToPlot + dateYearMonth

plotZM (zDiff ,modelObject.lat[:], modelObject.lev[llIndex1:ulIndex1+1], \
            fig, 223, "coolwarm", \
            zDiff.min(), zDiff.max(), \
            "navy", "darkred", \
            plotOpt=plotOpt,contourLevels=diffContourLevels)




percDiffContours =  [-100, -75, -50, -40, -30, -20, -10, -5, 0, 5, 10, 20, 30, 40, 50, 75, 100]

analType = "c"
analString = "perc change"

zDiff = None
zDiff = modelObject.createComparision2D(zmArray1, zmArray2, analType)
print ("zDiff min max for perc change", zDiff.min(), zDiff.max())

plotOpt['title'] = analString + "     " + fieldToPlot +  "    Zonal Mean " + dateYearMonth
plotOpt['units'] = "%"

plotZM (zDiff ,modelObject.lat[:], modelObject.lev[llIndex1:ulIndex1+1], \
            fig, 224, "coolwarm", \
            zDiff.min(), zDiff.max(), \
            "navy", "darkred", \
            plotOpt=plotOpt,contourLevels=percDiffContours)


fileTitle = "-" + model1SimName + "." + model2SimName + "_" + \
    str(dateYearMonth) + "_ZM."
plt.savefig ("plots/" + fieldToPlot + fileTitle \
                 + ".", bbox_inches='tight')


print("")
print("Plotted zonal mean for: ", fieldToPlot, " to plots/ directory")
print("") 
