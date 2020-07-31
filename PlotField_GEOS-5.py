

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         April 9 2019
#
# DESCRIPTION:
# Driver to plot a single field between two GEOS-5 Simulations.
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


NUM_ARGS = 7
def usage ():
    print("")
    print("usage: PlotField_GEOS-5.py [-c] [-g] [-r] [-d] [-u] [-f] [-m]")
    print("-c GEOS CTM file 1")
    print("-g GEOS CTM file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-u unit of vertical level (lev/hPa)")
    print("-f field to compare")
    print("-m model config (Replay, CCM, etc.)")
    print("")
    sys.exit (0)


print("Start plotting field differences.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:u:f:m:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile1 = str(optList[0][1])
geosCtmFile2 = str(optList[1][1])
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
levUnit = str(optList[4][1])
fieldToCompare = str(optList[5][1])
configName = str(optList[6][1])

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile1):
    print("The file you provided does not exist: ", geosCtmFile1)
    sys.exit(0)

if not os.path.exists (geosCtmFile2):
    print("The file you provided does not exist: ", geosCtmFile2)
    sys.exit(0)


if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)


print("")
print(geosCtmFile1)
print(geosCtmFile2)
print("")

geosCtmSimName1 = geosCtmFile1.split(".")[0] + "-" + geosCtmFile1.split(".")[1]
geosCtmSimName2 = geosCtmFile2.split(".")[0] + "-" + geosCtmFile2.split(".")[1]



print("")
print("Sim names: ")
print(geosCtmSimName1)
print(geosCtmSimName2)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosCtmObject1 = GeosCtmPlotTools (geosCtmFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


geosCtmObject2 = GeosCtmPlotTools (geosCtmFile2, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )



order = "GEOS"
list1 = geosCtmObject1.fieldList
list2 = geosCtmObject2.fieldList

if len(geosCtmObject1.fieldList) >= len(geosCtmObject2.fieldList):
    list1 = geosCtmObject2.fieldList
    list2 = geosCtmObject1.fieldList
    order = "GEOS"

print("")
print(list1)
print("")
print(list2)
print("")


# Does not matter which object to use - this is weird code. :/
fieldsToCompareAll = geosCtmObject1.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)



print("")
print("Fields to compare: ", fieldsToCompare[:])
print("GEOS-5 1 model levels: ", geosCtmObject1.lev[:])
print("")


print("")
if fieldToCompare in fieldsToCompare[:]:
    print("Success: ", fieldToCompare, " can be compared!")
else:
    print("ERROR: ", fieldToCompare, " cannot be compared!")
    sys.exit(-1)


modelLevsToPlot = []
#modelLevsToPlot.append(23)
#modelLevsToPlot.append(34)
#modelLevsToPlot.append(50)
#modelLevsToPlot.append(60)
modelLevsToPlot.append(21)



print("")
print("Model levs to plot: ", modelLevsToPlot[:])
print("")



# Arrays (one time record, one species)
longRecords = numpy.zeros(geosCtmObject1.longSize, numpy.float32)


minGeosCtmLat = geosCtmObject1.lat[:].min()
maxGeosCtmLat = geosCtmObject1.lat[:].max()
minGeosCtmLong = geosCtmObject1.long[:].min()
maxGeosCtmLong = geosCtmObject1.long[:].max()

cenGeosCtmLat = (minGeosCtmLat + maxGeosCtmLat)/2.
cenGeosCtmLong =  (minGeosCtmLong + maxGeosCtmLong)/2.


baseMapGeosCtm = Basemap(llcrnrlon=minGeosCtmLong,llcrnrlat=minGeosCtmLat,\
                             urcrnrlon=maxGeosCtmLong,urcrnrlat=maxGeosCtmLat,\
                             projection='cyl', \
                             lat_0=cenGeosCtmLat,lon_0=cenGeosCtmLong)

print("")
print("Basemap info: ")
print("llcr lon: ", minGeosCtmLong)
print("llcr lat: ", minGeosCtmLat)
print("urc lon: ", maxGeosCtmLong)
print("urc lat: ", maxGeosCtmLat)
print("centers lat/long: ", cenGeosCtmLat, cenGeosCtmLong)
print("")



gridLonsGeosCtm,gridLatsGeosCtm = baseMapGeosCtm.makegrid(geosCtmObject1.longSize, \
                                                              geosCtmObject1.latSize)
X_GeosCtm, Y_GeosCtm = baseMapGeosCtm(gridLonsGeosCtm,gridLatsGeosCtm)


fieldCount = 0
plt.figure(figsize=(20,20))


    
print("")
print("Processing: ", fieldToCompare)
print("")
    

geosCtmFieldArray1 = geosCtmObject1.returnField (fieldToCompare, timeRecord)
geosCtmFieldArray2 = geosCtmObject2.returnField (fieldToCompare, timeRecord)

found2DArray = False
for modelLev in modelLevsToPlot:
        


    print("")
    print("GEOS-5 level : ", modelLev)
    print("")



    if geosCtmFieldArray1.shape != geosCtmFieldArray2.shape:
        print("Array shapes are different. Interpolation needed!")
        print("This feature is currently not supported for inter GEOS-5 runs")
        sys.exit(0)

    else:
        print("Array shapes are the same, will continue with plotting...")




    if len(geosCtmFieldArray1.shape) == 2:
        print("Field is 2D")
        found2DArray = True
        z_GeosCtm1 = geosCtmFieldArray1[:, :]
        z_GeosCtm2 = geosCtmFieldArray2[:, :]
        modelLev = 0

    else:
        print("Field is 3D")
        z_GeosCtm1 = geosCtmFieldArray1[modelLev, :, :]
        z_GeosCtm2 = geosCtmFieldArray2[modelLev, :, :]

    z_Diff = z_GeosCtm1 / z_GeosCtm2

    minValueOfBoth = z_GeosCtm1.min()
    maxValueOfBoth = z_GeosCtm1.max()

    if z_GeosCtm2.min() < minValueOfBoth:
        minValueOfBoth = z_GeosCtm2.min()
    if z_GeosCtm2.max() > maxValueOfBoth:
        maxValueOfBoth = z_GeosCtm2.max()


    print(list(range(0, size(geosCtmObject1.long))))
    print(list(range(0, size(geosCtmObject1.lat))))

    print(shape(z_GeosCtm1))
    print(shape(z_GeosCtm2))
    print(shape(z_Diff))


    for lat in range(0, size(geosCtmObject1.lat)):
        for int in range(0, size(geosCtmObject1.long)):

            if z_GeosCtm1[lat, int] == 0.0 and z_GeosCtm2[lat, int] == 0.0:
                z_Diff[lat, int] = 1.0
            if z_GeosCtm1[lat, int] != 0.0 and z_GeosCtm2[lat,int] == 0.0:
                if z_GeosCtm1[lat, int] > 0.0: z_Diff[lat,int] = 2.5
                if z_GeosCtm1[lat, int] < 0.0: z_Diff[lat,int] = .5
                
    #-----------------------------------------------------#
    # GEOS-5 1

    print("")
    print("Min/max ", fieldToCompare, " values at level: ", modelLev)
    print("")


    print("GEOS-5 1: ", z_GeosCtm1.min(), " / ", z_GeosCtm1.max())


    plot1Title = configName + " " + geosCtmSimName1 + " " + configName + " " + geosCtmSimName1 + " " + \
        fieldToCompare + " @ " + str(geosCtmObject1.lev[modelLev]) + " " + levUnit + " " + \
        geosCtmObject1.DATE


    geosCtmObject1.create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm1, \
                                      #[z_GeosCtm1.min(),z_GeosCtm1.max()], \
                                      [minValueOfBoth,maxValueOfBoth], \
                                      [minGeosCtmLat,maxGeosCtmLat], \
                                      [minGeosCtmLong, maxGeosCtmLong], 311, \
                                      plot1Title, \
                                      "jet")

    print("GEOS-5 2: ", z_GeosCtm2.min(), " / ", z_GeosCtm2.max())


    plot2Title = configName + " " + geosCtmSimName2 + " " + \
        fieldToCompare + " @ " + str(geosCtmObject1.lev[modelLev]) + " " + levUnit + " " \
        + geosCtmObject1.DATE

    geosCtmObject2.create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm2, \
                                      #[z_GeosCtm2.min(),z_GeosCtm2.max()], \
                                      [minValueOfBoth,maxValueOfBoth], \
                                      [minGeosCtmLat,maxGeosCtmLat], \
                                      [minGeosCtmLong, maxGeosCtmLong], 312, \
                                      plot2Title, "jet")
    

    plot3Title = "Model ratio " + geosCtmSimName1 + "/" + geosCtmSimName2 + " " + \
        fieldToCompare + " @ " + \
        str(geosCtmObject1.lev[modelLev]) + \
        " " + levUnit + " " 

    geosCtmObject1.create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_Diff, \
                                      #[z_Diff.min(), z_Diff.max()], \
                                      [.5, 1.5], \
                                      [minGeosCtmLat,maxGeosCtmLat], \
                                      [minGeosCtmLong, maxGeosCtmLong], 313, \
                                      plot3Title, \
                                      "PuOr", \
                                      normalize=True)
    #-----------------------------------------------------#



    file = "f"
    if file == "f":
        plt.savefig("plots/" + fieldToCompare + ".inter."+ configName + "."
                    + str(geosCtmObject1.lev[modelLev]) + "." , bbox_inches='tight')
    elif file == "s":
        plt.show()
        
    plt.clf()


    if found2DArray == True:
        break


print("")
print("Plotted : ", fieldToCompare, " to plots/ directory")





    

