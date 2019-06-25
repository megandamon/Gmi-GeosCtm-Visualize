

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         April 9 2019
#
# DESCRIPTION:
# Driver to plot a single field between two models using different coordinate 
# systems. Will interpolate if needed. Pass the desired coordinate system as
# file 1. 
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

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools


NUM_ARGS = 9
def usage ():
    print("")
    print("usage: PlotField_Generic.py [-c] [-g] [-l] [-k] [-r] [-d] [-u] [-f] [-a]")
    print("-c Model file 1")
    print("-g Model file 2")
    print("-l vertical level for file 1")
    print("-k vertical level for file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-u unit of vertical level (lev/hPa)")
    print("-f field to compare")
    print("-a analysis type (d=perc diff, s=simple diff, r=ratio")
    print("")
    sys.exit (0)


def createStringLevel (fileLevel, stringLevel):

    stringLevel.strip()

    if str(fileLevel) != stringLevel:
        print((str(file1Level) + " != " + stringLevel))
        returnString = stringLevel + "hPa"
    else:
        returnString = "lev" + stringLevel        

    return returnString

print("Start plotting field differences.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:l:k:r:d:u:f:a:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile1 = str(optList[0][1])
modelFile2 = str(optList[1][1])
file1Level = int(optList[2][1])
file2Level = int(optList[3][1])
timeRecord = int(optList[4][1])
dateYearMonth = optList[5][1]
levUnit = str(optList[6][1])
fieldToCompare = str(optList[7][1])
analType = str(optList[8][1])


#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (modelFile1):
    print("The file you provided does not exist: ", modelFile1)
    sys.exit(0)

if not os.path.exists (modelFile2):
    print("The file you provided does not exist: ", modelFile2)
    sys.exit(0)

if file1Level < 0:
    print("The level to plot must be >= 0 (check file 1 lev)")
    sys.exit(0)

if file2Level < 0:
    print("The level to plot must be >= 0 (check file 2 lev)")
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)

if analType != "r" and analType != "d" and analType != "s":
    print("ERROR: analysis type must be r (ratios) or d (percent differences) or s (simple difference)")
    sys.exit(0)


print("")
print(modelFile1)
print(modelFile2)
print("")

modelSimName1 = modelFile1.split(".")[0] + "-" + modelFile1.split(".")[1]
modelSimName2 = modelFile2.split(".")[0] + "-" + modelFile2.split(".")[1]



print("")
print("Sim names: ")
print(modelSimName1)
print(modelSimName2)
print("")




#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
modelObject1 = GeosCtmPlotTools (modelFile1, 'latitude','longitude',\
                                      'lev','time', 'latitude', \
                                      'longitude', 'lev', 'time' )


modelObject2 = GeosCtmPlotTools (modelFile2, 'latitude','longitude',\
                                      'lev','time', 'latitude', \
                                      'longitude', 'lev', 'time' )



order = "1"
list1 = modelObject1.fieldList
list2 = modelObject2.fieldList

if len(modelObject1.fieldList) >= len(modelObject2.fieldList):
    list1 = modelObject2.fieldList
    list2 = modelObject1.fieldList
    order = "1"


fieldsToCompareAll = modelObject1.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)



print("")
print("Fields to compare: ", fieldsToCompare[:])
print("Model-1 1 vertical levels: ", modelObject1.lev[:])
print("")


print("")
if fieldToCompare in fieldsToCompare[:]:
    print("Success: ", fieldToCompare, " can be compared!")
else:
    print("ERROR: ", fieldToCompare, " cannot be compared!")
    sys.exit(-1)
print("")





print("")
print("Model levs to plot: ", file1Level, " ", file2Level)
print("")





minModel1Lat = modelObject1.lat[:].min()
maxModel1Lat = modelObject1.lat[:].max()
minModel1Long = modelObject1.long[:].min()
maxModel1Long = modelObject1.long[:].max()

cenModel1Lat = (minModel1Lat + maxModel1Lat)/2.
cenModel1Long =  (minModel1Long + maxModel1Long)/2.


baseMapModel1 = Basemap(llcrnrlon=minModel1Long,llcrnrlat=minModel1Lat,\
                             urcrnrlon=maxModel1Long,urcrnrlat=maxModel1Lat,\
                             projection='cyl', \
                             lat_0=cenModel1Lat,lon_0=cenModel1Long)

print("")
print("Basemap info: ")
print("llcr lon: ", minModel1Long)
print("llcr lat: ", minModel1Lat)
print("urc lon: ", maxModel1Long)
print("urc lat: ", maxModel1Lat)
print("centers lat/long: ", cenModel1Lat, cenModel1Long)
print("")



gridLonsModel1,gridLatsModel1 = baseMapModel1.makegrid(modelObject1.longSize, \
                                                              modelObject1.latSize)
X_Model1, Y_Model1 = baseMapModel1(gridLonsModel1,gridLatsModel1)


plt.figure(figsize=(20,20))


    




print("")
print("Processing: ", fieldToCompare)
print("")
    






modelFieldArray1 = modelObject1.returnField (fieldToCompare, timeRecord)
modelFieldArray2 = modelObject2.returnField (fieldToCompare, timeRecord)

print("")
print("modelFieldArray1 shape: ", modelFieldArray1.shape)
print("modelFieldArray2 shape: ", modelFieldArray2.shape)
print("")


if len(modelFieldArray1.shape) == 2:
    print("")
    print("WARNING!!! Field is 2D")
    print("")
    z_Model1 = modelFieldArray1[:, :]
    z_Model2 = modelFieldArray2[:, :]
    file1Level = 0
    file2Level = 0 

elif len(modelFieldArray1.shape) == 3:
    print("Field is 3D (expected)")
    z_Model1 = modelFieldArray1[file1Level, :, :]
    z_Model2 = modelFieldArray2[file2Level, :, :]
else:
    print("")
    print("Unexpected rank of data!")
    print("")
    sys.exit(0)

print("")




if z_Model1.shape != z_Model2.shape:

    print("")
    print("Array shapes are different. Interpolation needed! ", z_Model1.shape, " verus ", z_Model2.shape)
    print("")

    # Arrays (one time record, one species)
    longRecords = numpy.zeros(modelObject2.longSize, numpy.float32)
    latRecords = numpy.zeros(modelObject2.latSize, numpy.float32)
    newModel2Array = numpy.zeros((modelObject2.latSize, modelObject1.longSize), numpy.float32)
    newModel2ArrayBoth = numpy.zeros((modelObject1.latSize, modelObject1.longSize), numpy.float32)


    latCount = 0
    for lat in modelObject2.lat[:]:
        
        # pull long records out of model 2
        longRecords[:] = z_Model2[latCount, :]

        yinterp = numpy.interp(modelObject1.long[:], modelObject2.long[:], longRecords)

        newModel2Array [latCount, :] = yinterp[:]
      
        latCount = latCount + 1

    print("")
    print("Model-2 min / max / shape", newModel2Array.min(), " / ", newModel2Array.max(), " / ", newModel2Array.shape)
    print("")        

    longCount = 0
    for int in modelObject1.long[:]:

        # pull lat records our of model 2
        latRecords[:] = newModel2Array[:,longCount]

        yinterp = numpy.interp(modelObject1.lat[:], modelObject2.lat[:], latRecords)

        newModel2ArrayBoth [:, longCount] = yinterp[:]

        longCount = longCount + 1

    print("")
    print("Interpolated model 2 array min / max / shape: ", newModel2ArrayBoth.min(), " / " , newModel2ArrayBoth.max(), newModel2ArrayBoth.shape)
    print("")

    z_Model2 = None
    z_Model2 = newModel2ArrayBoth

else:
    print("")
    print("Array shapes are the same, will continue with plotting...")
    print("")


minValueOfBoth = z_Model1.min()
maxValueOfBoth = z_Model1.max()

if z_Model2.min() < minValueOfBoth:
    minValueOfBoth = z_Model2.min()
if z_Model2.max() > maxValueOfBoth:
    maxValueOfBoth = z_Model2.max()


    


         
#-----------------------------------------------------#
# Model-1 

stringLevel1 = createStringLevel (file1Level, str(int(modelObject1.lev[file1Level])))
stringLevel2 = createStringLevel (file2Level, str(int(modelObject2.lev[file2Level])))

stringLevel1 = "lev" + str(file1Level)
stringLevel2 = "lev" + str(file2Level)


print("Model1 level: " , file1Level , "(" , stringLevel1 , ")") 
print("Model2 level: " , file2Level , "(" , stringLevel2 , ")") 



print("")

print("Model-1 min / max : ", z_Model1.min(), " / ", z_Model1.max())

print("")

modelObject1.create2dSlice (baseMapModel1, X_Model1, Y_Model1, z_Model1, \
                                #[z_Model1.min(),z_Model1.max()], \
                                [minValueOfBoth,maxValueOfBoth], \
                                [minModel1Lat,maxModel1Lat], \
                                [minModel1Long, maxModel1Long], 311, \
                                modelSimName1 + " " + \
                                fieldToCompare + " @ " + stringLevel1 + \
                                " " + str(levUnit) + " " + str(dateYearMonth), \
                                "jet")




print("")

print("Model-2 min / max ", z_Model2.min(), " / ", z_Model2.max())

print("")

modelObject2.create2dSlice (baseMapModel1, X_Model1, Y_Model1, z_Model2, \
                                #[z_Model2.min(),z_Model2.max()], \
                                [minValueOfBoth,maxValueOfBoth], \
                                [minModel1Lat,maxModel1Lat], \
                                [minModel1Long, maxModel1Long], 312, \
                                modelSimName2 + " " + \
                                fieldToCompare + " @ " + stringLevel2 + \
                                " " + levUnit + " " + str(dateYearMonth), \
                                "jet")




z_Diff = numpy.zeros((modelObject1.latSize, \
                          modelObject1.longSize), numpy.float32)

print("")
print("Size of z_Diff: ", z_Diff.shape)
print("")


latPoints = z_Diff.shape[0]
lonPoints = z_Diff.shape[1]


if analType == "d":

    
    print("")
    print("Creating Percent Differences")
    print("")

    for lat in range(0,latPoints):
        for lon in range(0,lonPoints):
            absVal = abs(z_Model1[lat,lon]-z_Model2[lat,lon])
            denVal = (z_Model1[lat,lon]+z_Model2[lat,lon]) / 2.0
            z_Diff [lat,lon] = (absVal/denVal) * 100.

    lowEnd = z_Diff.min()
    highEnd = z_Diff.max()

    print("")
    print("low end / high end for diffs: ", lowEnd, " / ", highEnd)
    print("")


    if abs(lowEnd) > abs(highEnd): 
        lowEnd = lowEnd
        highEnd = abs(lowEnd)
    else:
        lowEnd = -abs(highEnd)
        highEnd = highEnd

    modelObject1.create2dSlice (baseMapModel1, X_Model1, Y_Model1, z_Diff, \
                                    [lowEnd, highEnd], \
                                    [minModel1Lat,maxModel1Lat], \
                                    [minModel1Long, maxModel1Long], 313, \
                                    "Perc difference % " + modelSimName1 + "/" + \
                                    modelSimName2 + " " + \
                                    fieldToCompare + " ", \
                                    "PuOr", \
                                    normalize=True)

elif analType == "s":

    
    print("")
    print("Creating Simple Differences")
    print("")

    z_Diff = z_Model1 - z_Model2 

    lowEnd = z_Diff.min()
    highEnd = z_Diff.max()

    print("")
    print("low end / high end for diffs: ", lowEnd, " / ", highEnd)
    print("")

    if abs(lowEnd) > abs(highEnd): 
        lowEnd = lowEnd
        highEnd = abs(lowEnd)
    else:
        lowEnd = -abs(highEnd)
        highEnd = highEnd


    modelObject1.create2dSlice (baseMapModel1, X_Model1, Y_Model1, z_Diff, \
                                    [lowEnd, highEnd], \
                                    [minModel1Lat,maxModel1Lat], \
                                    [minModel1Long, maxModel1Long], 313, \
                                    "top-middle " + modelSimName1 + "/" + \
                                    modelSimName2 + " " + \
                                    fieldToCompare + " ", \
                                    "PuOr", \
                                    normalize=True)


elif analType == "r":

    print("")
    print("Creating Model Ratios")
    print("")



    z_Diff = z_Model1 / z_Model2

    print("")
    print("low end / high end for ratios: ", z_Diff.min(), " / ", z_Diff.max())
    print("")


    # play with ratios a little
    for lat in range(0, size(modelObject1.lat)):
        for int in range(0, size(modelObject1.long)):

            if z_Model1[lat, int] == 0.0 and z_Model2[lat, int] == 0.0:
                z_Diff[lat, int] = 1.0
            elif z_Model1[lat, int] != 0.0 and z_Model2[lat,int] == 0.0:
                if z_Model1[lat, int] > 0.0: z_Diff[lat,int] = 1.5 #saturate
                if z_Model1[lat, int] < 0.0: z_Diff[lat,int] = .5 #saturate


    modelObject1.create2dSlice (baseMapModel1, X_Model1, Y_Model1, z_Diff, \
                                    [.5, 1.5], \
                                    [minModel1Lat,maxModel1Lat], \
                                    [minModel1Long, maxModel1Long], 313, \
                                    "Model Ratios " + modelSimName1 + "/" + \
                                    modelSimName2 + " " + \
                                    fieldToCompare + " ", \
                                    "PuOr", \
                                    normalize=True)


else:
    print("")
    print("Analysis type: ", analType, " not supported!")
    print("")
    sys.exit(0)
    


#-----------------------------------------------------#



file = "f"
if file == "f":
    plt.savefig("plots/" + fieldToCompare + "__" + modelSimName1 + "_" + stringLevel1 \
                    + "." + modelSimName2 + "_" + stringLevel2 + "." + analType + ".", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()




print("")
print("Plotted : ", fieldToCompare, " to plots/ directory")
print("") 




    

