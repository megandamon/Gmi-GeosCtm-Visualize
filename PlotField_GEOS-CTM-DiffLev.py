#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         September 21 2017
#
# DESCRIPTION:
# Driver to plot a single but potentially diff. field between two GEOS-CTM Simulations.
# Lat/lon shapes should be the same. Number of vertical levels assumed different.
# Assumes file1 has top level as surface, and file2 has bottom level as surface.
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





# This routine can go into the Generic class
# and X_model, Y_model, and min/maxes 
# can be members of the class
def create2dSlice (baseMap, X_model, Y_model, z, \
                       minMaxVals, minMaxLat, \
                       minMaxLong, subplotNum, plotTitle, \
                       colorMap, \
                       normalize=False):

    print "min/max field vals in create2dSlice: ", minMaxVals[:]

    plt.subplot(subplotNum)



    imSlice = baseMap.pcolor(X_model, Y_model, z, \
                                 cmap=colorMap, \
                                 vmin = minMaxVals[0], \
                                 vmax = minMaxVals[1])
    plt.colorbar()
        
    plt.title(plotTitle)
    plt.axis([X_model.min(), X_model.max(), Y_model.min(), Y_model.max()])

    baseMap.drawparallels(numpy.arange(minMaxLat[0],minMaxLat[1],40),labels=[1,0,0,0])
    baseMap.drawmeridians(numpy.arange(minMaxLong[0],minMaxLong[1],80),labels=[0,1,0,1])
    baseMap.drawcoastlines()
    baseMap.drawstates()


NUM_ARGS = 6
def usage ():
    print ""
    print "usage: PlotField_GEOS-CTM-DiffLev.py [-c] [-g] [-r] [-d] [-f] [-o]"
    print "-c GEOS CTM file 1"
    print "-g GEOS CTM file 2"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print "-f field to compare"
    print "-o other field to compare"
    print ""
    sys.exit (0)


print "Start plotting field differences."

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:o:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile1 = optList[0][1]
geosCtmFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
otherFieldToCompare = optList[5][1]

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile1):
    print "The file you provided does not exist: ", geosCtmFile1
    sys.exit(0)

if not os.path.exists (geosCtmFile2):
    print "The file you provided does not exist: ", geosCtmFile2
    sys.exit(0)


if int(timeRecord) > 30: 
    print "WARNING: time record is more than a typical daily file!"

if int(timeRecord) < 0: 
    print "ERROR: time record needs to be positive!"
    sys.exit(0)

if len(dateYearMonth) != 6:
    print "ERROR date must be in the format YYYYMM. Received: ", dateYearMonth
    sys.exit(0)


print ""
print geosCtmFile1
print geosCtmFile2
print ""

geosCtmSimName1 = geosCtmFile1.split(".")[0]
geosCtmSimName2 = geosCtmFile2.split(".")[0]


print ""
print "Sim names: "
print geosCtmSimName1
print geosCtmSimName2
print ""



#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------
geosCtmObject1 = GeosCtmPlotTools (geosCtmFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


geosCtmObject2 = GeosCtmPlotTools (geosCtmFile2, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


print ""


order = "GEOS-CTM"
list1 = geosCtmObject1.fieldList
list2 = geosCtmObject2.fieldList

print "list 1: ", list1[:]
print "list 2: ", list2[:]



print ""
print "Fields to compare: ", fieldToCompare, otherFieldToCompare
print ""


successFlag = False
print ""
if fieldToCompare in list1[:]:
    print "Success: ", fieldToCompare, " can be compared!"
    if otherFieldToCompare in list2[:]:
        print "Success: ", otherFieldToCompare, " can be compared!"
        successFlag = True

if successFlag == False:
        print "ERROR: ", fieldToCompare, " or ", otherFieldToCompare, " cannot be compared!"
        sys.exit(-1)





print ""
print "Top, bottom, and middle plot slices will be shown."
print ""




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

print ""
print "Basemap info: "
print "llcr lon: ", minGeosCtmLong
print "llcr lat: ", minGeosCtmLat
print "urc lon: ", maxGeosCtmLong
print "urc lat: ", maxGeosCtmLat
print "centers lat/long: ", cenGeosCtmLat, cenGeosCtmLong
print ""



gridLonsGeosCtm,gridLatsGeosCtm = baseMapGeosCtm.makegrid(geosCtmObject1.longSize, \
                                                              geosCtmObject1.latSize)
X_GeosCtm, Y_GeosCtm = baseMapGeosCtm(gridLonsGeosCtm,gridLatsGeosCtm)


fieldCount = 0
plt.figure(figsize=(20,20))


    
print ""
print "Processing: ", fieldToCompare, " and ", otherFieldToCompare
print ""
    


geosCtmFieldArray1 = geosCtmObject1.returnField (fieldToCompare, timeRecord)
geosCtmFieldArray2 = geosCtmObject2.returnField (otherFieldToCompare, timeRecord)

for modelLev in ['top','surface','middle']:
        


    print ""
    print "GEOS-CTM level : ", modelLev
    print ""

    # 2nd file is with 42 levels
    if modelLev == "surface":
        lev1 = geosCtmFieldArray1.shape[0]-1
        lev2 = 0
    elif modelLev == "top":
        lev1 = 0
        lev2 = geosCtmFieldArray2.shape[0]-1
    elif modelLev == "middle":
        lev1 = geosCtmFieldArray1.shape[0]/2
        lev2 = geosCtmFieldArray2.shape[0]/2
    else:
        print "model level: ", modelLev, " not available!"
        sys.exit(0)
    
    print "Comparing levels: ", lev1, " and ", lev2


    if geosCtmFieldArray1.shape[1:3] != geosCtmFieldArray2.shape[1:3]:
        print ""
        print "Array 2D shapes are different. Interpolation needed!"
        print "This feature is currently not supported for inter GEOS-CTM runs"
        print ""
        sys.exit(0)

    else:
        print ""
        print "Array 2D shapes are the same, will continue with plotting..."
        print ""



    z_GeosCtm1 = geosCtmFieldArray1[lev1, :, :]
    z_GeosCtm2 = geosCtmFieldArray2[lev2, :, :]

    z_Diff = z_GeosCtm1 / z_GeosCtm2


    minValueOfBoth = z_GeosCtm1.min()
    maxValueOfBoth = z_GeosCtm1.max()

    print ""
    print "min/max of GeosCtm1: ", z_GeosCtm1.min(), z_GeosCtm1.max()
    print "min/max of GeosCtm2: ", z_GeosCtm2.min(), z_GeosCtm2.max()
    print ""

    if z_GeosCtm2.min() < minValueOfBoth:
        minValueOfBoth = z_GeosCtm2.min()
    if z_GeosCtm2.max() > maxValueOfBoth:
        maxValueOfBoth = z_GeosCtm2.max()

    print ""
    print "min/max of both: ", minValueOfBoth, maxValueOfBoth
    print ""

    for lat in range(0, size(geosCtmObject1.lat)):
        for long in range(0, size(geosCtmObject1.long)):

            if z_GeosCtm1[lat, long] == 0 and z_GeosCtm2[lat, long] == 0:
                #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
                z_Diff[lat, long] = 1.0




    #-----------------------------------------------------#
    # GEOS-CTM 1

    print "GEOS-CTM 1: ", z_GeosCtm1.min(), " / ", z_GeosCtm1.max()

    create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm1, \
                       [z_GeosCtm1.min(), z_GeosCtm1.max()], \
#                       [minValueOfBoth,maxValueOfBoth], \
                       [minGeosCtmLat,maxGeosCtmLat], \
                       [minGeosCtmLong, maxGeosCtmLong], 311, \
                       "GEOS-CTM " + geosCtmSimName1 + " " + \
                       fieldToCompare + " @ " + str(lev1) + \
                       "lev " + dateYearMonth, "jet")

    print "GEOS-CTM 2: ", z_GeosCtm2.min(), " / ", z_GeosCtm2.max()

    create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm2, \
                       [z_GeosCtm2.min(), z_GeosCtm2.max()], \
#                       [minValueOfBoth,maxValueOfBoth], \
                       [minGeosCtmLat,maxGeosCtmLat], \
                       [minGeosCtmLong, maxGeosCtmLong], 312, \
                       "GEOS-CTM " + geosCtmSimName2 + " " + \
                       otherFieldToCompare + " @ " + str(lev2) + \
                       "lev " + dateYearMonth, "jet")
    


    create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_Diff, \
                       [z_Diff.min(), z_Diff.max()], \
#                       [0, 1.5], \
                       [minGeosCtmLat,maxGeosCtmLat], \
                       [minGeosCtmLong, maxGeosCtmLong], 313, \
                       "Model ratio " + fieldToCompare + " @ " + str(modelLev) + \
                       " lev " + dateYearMonth, \
                       "nipy_spectral", \
                       normalize=True)
    #-----------------------------------------------------#



    file = "f"
    if file == "f":
        plt.savefig("plots/" + fieldToCompare + \
                        "." + otherFieldToCompare + ".GEOS-CTM."
                    + str(modelLev) + "." , bbox_inches='tight')
    elif file == "s":
        plt.show()
        
    plt.clf()





    

