 
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
import os
import getopt
import sys

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools

if "GMIMetFieldProcessing" in os.environ:
    sys.path.append(os.environ.get("GMIMetFielProcessing"))
else:
    print("Please specify location of GMIMetFieldProcessing scripts")
    sys.exit(1)


#*********************
COLORMAP = "rainbow"
RATIO_COLORMAP = "bwr"
RATIO_CONTOUR_LEVELS = [.5,.6,.7,.8,.9,1.0,1.1,1.2,1.3,1.4,1.5]
DEFAULT_PERCHANGE_CONTOURS = [-1000, -500, -100, -50, -20, -10, -5, -2, -.5, .5, 2, 5, 10, 20, 50, 100, 500, 1000]
#DEFAULT_PERCHANGE_CONTOURS = [-100, -75, -50, -40, -30, -20, -10, -5, 0, 5, 10, 20, 30, 40, 50, 75, 100]
NUM_ARGS = 9
#*********************



#*********************
def usage ():
    print("")
    print("usage: PlotTracerCompareSlice.py [-c] [-g] [-l] [-r] [-d] [-n] [-k] [-f] [-p]")
    print("-g Model file 1")
    print("-c Model file 2")
    print("-l vertical level (hPa)")
    print("-r time record to plot")
    print("-d date (YYYYMM)")
    print("-n long name of tracer")
    print("-k Key file for tracers")
    print("-f tracer to plot")
    print("-p percentage change contours (d-default-+-100, a-algorithmic")
    print("")
    sys.exit (0)
#*********************


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'g:c:l:r:d:n:k:p:f:')
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
percChangeContours = str(optList[7][1])
fieldToPlot = str(optList[8][1])


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

if fileLevel < 0.1 and fileLevel > 1300.: 
    print("GEOS-5 pressure levels should be < 1300 and > 0.1 mb/hPa")
    sys.exit(0)

if percChangeContours != "d" and percChangeContours != "a":
    print("Percent change contours should be either d(deafult) or a(algorithmic)")
    sys.exit(0)


model1Object = GeosCtmPlotTools (model1File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )

model1SimName = model1File.split(".")[0] + "-" + model1File.split(".")[1]
model1SimName2 = model1SimName.split("_")[0] + "_" + model1SimName.split("_")[1]
model1SimName = model1SimName2
model2SimName = model2File.split(".")[0] + "-" + model2File.split(".")[1]
model2SimName2 = model2SimName.split("_")[0] + "_" + model2SimName.split("_")[1]
model2SimName = model2SimName2


tracerTools = TracerPlotTools (model1Object, keyFile, timeRecord, fileLevel)


if fieldToPlot not in model1Object.hdfData.variables.keys():

    if fieldToPlot.islower() == True:
        fieldToPlot1 = fieldToPlot.upper()
    else:
        fieldToPlot1 = fieldToPlot.lower()
else:
    fieldToPlot1 = fieldToPlot



model1FieldArray = model1Object.returnField (fieldToPlot, timeRecord)

print (model1FieldArray.shape)

model1FieldArraySlice = model1Object.return2DSliceFromRefPressure (model1FieldArray, fileLevel)

print ("2: ", model1FieldArraySlice.shape)

preConvertFieldArray1 = tracerTools.tracerDict[fieldToPlot].preConversion(model1FieldArraySlice, model1SimName)

print ("3: ", preConvertFieldArray1.shape)

newModel1FieldArray = preConvertFieldArray1 * \
    float(tracerTools.tracerDict[fieldToPlot].unitConvert) # key convert

if float(tracerTools.tracerDict[fieldToPlot].unitConvert) != 1.:
    tracerTools.tracerDict[fieldToPlot].units  = tracerTools.tracerDict[fieldToPlot].newUnit

model1FieldArray = newModel1FieldArray
newModel1FieldArray = None





model2Object = GeosCtmPlotTools (model2File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )





model2FieldArray = model2Object.returnField (fieldToPlot, timeRecord)
model2FieldArraySlice = model2Object.return2DSliceFromRefPressure (model2FieldArray, fileLevel)

preConvertFieldArray2 = tracerTools.tracerDict[fieldToPlot].preConversion(model2FieldArraySlice, model2SimName)

newModel2DFieldArray = preConvertFieldArray2 * \
    float(tracerTools.tracerDict[fieldToPlot].unitConvert) # key convert

if float(tracerTools.tracerDict[fieldToPlot].unitConvert) != 1.:
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

if tracerTools.tracerDict[fieldToPlot].slices[int(fileLevel)] == None:

    step = (maxValueBoth - minValueBoth) / 10.
    contours = tracerTools.tracerDict[fieldToPlot].createTracerContoursFromMinMax (minValueBoth, maxValueBoth, \
                                                               step=float('{:0.2e}'.format(step)))
else:
    contours = []
    for contour in tracerTools.tracerDict[fieldToPlot].slices[fileLevel]:
        contours.append(float(contour))



fig = plt.figure(figsize=(20,20))
modelObject.createPlotObjects()

print (model1FieldArray.shape)


plotTitle1 = model1SimName + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
    + " hPa  " + dateYearMonth
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



plotTitle2 = model2SimName + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
    + " hPa  " + dateYearMonth
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


print (tracerTools.tracerDict[fieldToPlot].slices)
print (tracerTools.tracerDict[fieldToPlot].diffSlices)


if tracerTools.tracerDict[fieldToPlot].diffSlices[fileLevel] == None:

    diffContourLevels = tracerTools.tracerDict[fieldToPlot].createDiffContoursFromMinMax(z_Model.min(), z_Model.max())

else:

    diffContourLevels = tracerTools.tracerDict[fieldToPlot].diffSlices[fileLevel]


print ("")
print ("Diff contours: ", diffContourLevels)
print ("")


plotTitle3 = analString + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
     + " hPa " + dateYearMonth
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


#sys.exit(0)

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


plotTitle4 = analString + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
     + " hPa " + dateYearMonth
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
                    "_" + str(dateYearMonth) + "_" +  str(int(fileLevel)) \
                    + "hPa.", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()


print("")
print("Plotted slice for : ", fieldToPlot, " to plots/ directory")
print("") 
