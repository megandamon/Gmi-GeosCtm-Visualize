
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         October 4 2018
#
# DESCRIPTION:
# Driver to plot a 2D single field between two GEOS-CTM Simulations.
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
    print("usage: PlotField_GEOS-CTM.2d.py [-c] [-g] [-r] [-d] [-f]")
    print("-c GEOS CTM file 1")
    print("-g GEOS CTM file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
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

geosCtmFile1 = optList[0][1]
geosCtmFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]

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

geosCtmSimName1 = geosCtmFile1.split(".")[0]
geosCtmSimName2 = geosCtmFile2.split(".")[0]


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



order = "GEOS-CTM"
list1 = geosCtmObject1.fieldList
list2 = geosCtmObject2.fieldList

if len(geosCtmObject1.fieldList) >= len(geosCtmObject2.fieldList):
    list1 = geosCtmObject2.fieldList
    list2 = geosCtmObject1.fieldList
    order = "GEOS-CTM"

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
print("GEOS-CTM 1 model levels: ", geosCtmObject1.lev[:])
print("")


print("")
if fieldToCompare in fieldsToCompare[:]:
    print("Success: ", fieldToCompare, " can be compared!")
else:
    print("ERROR: ", fieldToCompare, " cannot be compared!")
    sys.exit(-1)


# Arrays (one time record, one field)
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

if len(geosCtmFieldArray1.shape) != 2 or len(geosCtmFieldArray2.shape) != 2: 
    print("The fields to be compared must be 2D")
    sys.exit(-1)



if geosCtmFieldArray1.shape != geosCtmFieldArray2.shape:
    print("Array shapes are different. Interpolation needed!")
    print("This feature is currently not supported for inter GEOS-CTM runs")
    sys.exit(0)
    
else:
    print("Array shapes are the same, will continue with plotting...")


z_GeosCtm1 = geosCtmFieldArray1[:, :] 
z_GeosCtm2 = geosCtmFieldArray2[:, :]
    
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

        if z_GeosCtm1[lat, int] == 0 and z_GeosCtm2[lat, int] == 0:
            #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
            z_Diff[lat, int] = 1.0





#-----------------------------------------------------#
# GEOS-CTM 1

print("")
print("Min/max ", fieldToCompare)
print("")


print("GEOS-CTM 1: ", z_GeosCtm1.min(), " / ", z_GeosCtm1.max())

geosCtmObject1.create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm1, \
                                  #[z_GeosCtm1.min(),z_GeosCtm1.max()], \
                                  [minValueOfBoth,maxValueOfBoth], \
                                  [minGeosCtmLat,maxGeosCtmLat], \
                                  [minGeosCtmLong, maxGeosCtmLong], 311, \
                                  "GEOS-CTM " + geosCtmSimName1 + " " + \
                                  fieldToCompare + " " + geosCtmObject1.DATE, "jet")

print("GEOS-CTM 2: ", z_GeosCtm2.min(), " / ", z_GeosCtm2.max())

geosCtmObject2.create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm2, \
                                  #[z_GeosCtm2.min(),z_GeosCtm2.max()], \
                                  [minValueOfBoth,maxValueOfBoth], \
                                  [minGeosCtmLat,maxGeosCtmLat], \
                                  [minGeosCtmLong, maxGeosCtmLong], 312, \
                                  "GEOS-CTM " + geosCtmSimName2 + " " + \
                                  fieldToCompare + " " + geosCtmObject2.DATE, "jet")
    


geosCtmObject1.create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_Diff, \
                                  #[z_Diff.min(), z_Diff.max()], \
                                  [0, 1.5], \
                                  [minGeosCtmLat,maxGeosCtmLat], \
                                  [minGeosCtmLong, maxGeosCtmLong], 313, \
                                  "Model ratio " + fieldToCompare, "nipy_spectral", \
                                  normalize=True)
    #-----------------------------------------------------#



file = "f"
if file == "f":
    plt.savefig("plots/" + fieldToCompare + ".inter.GEOS-CTM."
                , bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()

print("")
print("Plotted : ", fieldToCompare, " to plots/ directory")
