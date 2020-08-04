
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         August 9 2017
#
# DESCRIPTION:
# Driver to plot a single field between two GEOS Simulations.
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


NUM_ARGS = 5
def usage ():
    print("")
    print("usage: PlotField_GEOS.py [-c] [-g] [-r] [-d] [-f]")
    print("-c GEOS  file 1")
    print("-g GEOS  file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMMDD, YYYYMM, YYYYY)")
    print("-f field to compare")
    print("")
    sys.exit (0)


print("Start plotting field differences.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosFile1 = optList[0][1]
geosFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geosFile1):
    print("The file you provided does not exist: ", geosFile1)
    sys.exit(0)

if not os.path.exists (geosFile2):
    print("The file you provided does not exist: ", geosFile2)
    sys.exit(0)


if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) > 8:
    print("ERROR date must be in the format YYYY, YYYYMM, or YYYYYDD. Received: ", dateYearMonth)
    sys.exit(0)


print("")
print(geosFile1)
print(geosFile2)
print("")

geosSimName1 = geosFile1.split(".")[0]
geosSimName2 = geosFile2.split(".")[0]


print("")
print("Sim names: ")
print(geosSimName1)
print(geosSimName2)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosObject1 = GeosCtmPlotTools (geosFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


geosObject2 = GeosCtmPlotTools (geosFile2, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )



order = "GEOS"
list1 = geosObject1.fieldList
list2 = geosObject2.fieldList

if len(geosObject1.fieldList) >= len(geosObject2.fieldList):
    list1 = geosObject2.fieldList
    list2 = geosObject1.fieldList
    order = "GEOS"


# Does not matter which object to use - this is weird code. :/
fieldsToCompareAll = geosObject1.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)



print("")
print("Fields to compare: ", fieldsToCompare[:])
print("GEOS 1 model levels: ", geosObject1.lev[:])
print("")

print("")
if fieldToCompare in fieldsToCompare[:]:
    print("Success: ", fieldToCompare, " can be compared!")
else:
    print("ERROR: ", fieldToCompare, " cannot be compared!")
    sys.exit(-1)


modelLevsToPlot = [0]


print("")
print("Model levs to plot: ", modelLevsToPlot[:])
print("")


# Arrays (one time record, one species)
longRecords = numpy.zeros(geosObject1.longSize, numpy.float32)


minGeosLat = geosObject1.lat[:].min()
maxGeosLat = geosObject1.lat[:].max()
minGeosLong = geosObject1.long[:].min()
maxGeosLong = geosObject1.long[:].max()

cenGeosLat = (minGeosLat + maxGeosLat)/2.
cenGeosLong =  (minGeosLong + maxGeosLong)/2.


baseMapGeos = Basemap(llcrnrlon=minGeosLong,llcrnrlat=minGeosLat,\
                             urcrnrlon=maxGeosLong,urcrnrlat=maxGeosLat,\
                             projection='cyl', \
                             lat_0=cenGeosLat,lon_0=cenGeosLong)

print("")
print("Basemap info: ")
print("llcr lon: ", minGeosLong)
print("llcr lat: ", minGeosLat)
print("urc lon: ", maxGeosLong)
print("urc lat: ", maxGeosLat)
print("centers lat/long: ", cenGeosLat, cenGeosLong)
print("")



gridLonsGeos,gridLatsGeos = baseMapGeos.makegrid(geosObject1.longSize, \
                                                              geosObject1.latSize)
X_Geos, Y_Geos = baseMapGeos(gridLonsGeos,gridLatsGeos)


fieldCount = 0
plt.figure(figsize=(20,20))


    
print("")
print("Processing: ", fieldToCompare)
print("")



geosFieldArray1 = geosObject1.returnField (fieldToCompare, timeRecord)
geosFieldArray2 = geosObject2.returnField (fieldToCompare, timeRecord)

found2DArray = False
for modelLev in modelLevsToPlot:
        


    print("")
    print("GEOS vertical level : ", modelLev)
    print("")




    if geosFieldArray1.shape != geosFieldArray2.shape:
        print("\nArray shapes are different. Interpolation needed!")
        print("This feature is currently not supported for inter GEOS runs")
        sys.exit(0)

    else:
        print("\nArray shapes are the same, will continue with plotting...")




    if len(geosFieldArray1.shape) == 2:
        print("\n", fieldToCompare, " is 2D")
        
        found2DArray = True

        z_Geos1 = geosFieldArray1[:, :]
        z_Geos2 = geosFieldArray2[:, :]
        modelLev = 0

    else:
        print("\n", fieldToCompare, " is 3D")

        z_Geos1 = geosFieldArray1[modelLev, :, :]
        z_Geos2 = geosFieldArray2[modelLev, :, :]



    z_Diff = z_Geos1 / z_Geos2

    minValueOfBoth = z_Geos1.min()
    maxValueOfBoth = z_Geos1.max()

    if z_Geos2.min() < minValueOfBoth:
        minValueOfBoth = z_Geos2.min()
    if z_Geos2.max() > maxValueOfBoth:
        maxValueOfBoth = z_Geos2.max()


    print("\nShape of difference array: ", shape(z_Diff))


    print("\nSetting difference values to zero where both fields are zero...")
    
    for lat in range(0, size(geosObject1.lat)):
        for int in range(0, size(geosObject1.long)):

            if z_Geos1[lat, int] == 0 and z_Geos2[lat, int] == 0:
                z_Diff[lat, int] = 1.0





    #-----------------------------------------------------#
    # GEOS 1

    print("\nGEOS 1 min/max: ", z_Geos1.min(), " / ", z_Geos1.max())

    geosObject1.create2dSlice (baseMapGeos, X_Geos, Y_Geos, z_Geos1, \
                                      #[z_Geos1.min(),z_Geos1.max()], \
                                      [minValueOfBoth,maxValueOfBoth], \
                                      [minGeosLat,maxGeosLat], \
                                      [minGeosLong, maxGeosLong], 311, \
                                      "GEOS " + geosSimName1 + " " + \
                                      fieldToCompare + " @ " + str(modelLev) + \
                                      "lev " + geosObject1.DATE, "jet")

    print("\nGEOS 2: min/max", z_Geos2.min(), " / ", z_Geos2.max())

    geosObject2.create2dSlice (baseMapGeos, X_Geos, Y_Geos, z_Geos2, \
                                      #[z_Geos2.min(),z_Geos2.max()], \
                                      [minValueOfBoth,maxValueOfBoth], \
                                      [minGeosLat,maxGeosLat], \
                                      [minGeosLong, maxGeosLong], 312, \
                                      "GEOS " + geosSimName2 + " " + \
                                      fieldToCompare + " @ " + str(modelLev) + \
                                      "lev " + geosObject2.DATE, "jet")
    

    print("\ndiff min/max", z_Diff.min(), " / ", z_Diff.max())

    geosObject1.create2dSlice (baseMapGeos, X_Geos, Y_Geos, z_Diff, \
                                      #[z_Diff.min(), z_Diff.max()], \
                                      [0, 1.5], \
                                      [minGeosLat,maxGeosLat], \
                                      [minGeosLong, maxGeosLong], 313, \
                                      "Model ratio " + fieldToCompare + " @ " + str(modelLev) + \
                                      " lev ", \
                                      "nipy_spectral", \
                                      normalize=True)
    #-----------------------------------------------------#



    file = "f"
    if file == "f":
        plt.savefig("plots/" + fieldToCompare + "." + \
                    geosSimName1 + "." + geosSimName2 + "." \
                    + str(modelLev) + "." , bbox_inches='tight')
    elif file == "s":
        plt.show()
        
    plt.clf()

    if found2DArray == True:
        break

print("")
print("Plotted : ", fieldToCompare, " to plots/ directory")





    

