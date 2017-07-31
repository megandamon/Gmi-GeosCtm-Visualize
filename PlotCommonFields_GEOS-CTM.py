#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         July 31st 2017
#
# DESCRIPTION:
# Driver to plot differences between two sets of  GEOS-CTM species
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
from netCDF4 import Dataset

import math
import matplotlib.pyplot as plt
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

#    print "min/max field vals in create2dSlice: ", minMaxVals[:]

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


NUM_ARGS = 4
def usage ():
    print ""
    print "usage: PlotCommonFields_GEOS-CTM.py [-c] [-g] [-r] [-d]"
    print "-c GEOS CTM file 1"
    print "-g GEOS CTM file 2"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print ""
    sys.exit (0)


print "Start plotting restart species differences"

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile1 = optList[0][1]
geosCtmFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]

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

if len(geosCtmObject1.fieldList) >= len(geosCtmObject2.fieldList):
    list1 = geosCtmObject2.fieldList
    list2 = geosCtmObject1.fieldList
    order = "GEOS-CTM"

# Does not matter which object to use - this is weird code. :/
fieldsToCompareAll = geosCtmObject1.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and field[0:2] != "EM" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)


print ""
print "Fields to compare: ", fieldsToCompare[:]
print "GEOS-CTM 1 model levels: ", geosCtmObject1.lev[:]
print ""




modelLevsToPlot = []
modelLevsToPlot.append(71)
modelLevsToPlot.append(49)
modelLevsToPlot.append(41)


print ""
print "Model levs to plot: ", modelLevsToPlot[:]
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
for field in fieldsToCompare[:]:
    

    print ""
    print "Processing: ", field
    print ""
    



    geosCtmFieldArray1 = geosCtmObject1.returnField (field, timeRecord)
    geosCtmFieldArray2 = geosCtmObject2.returnField (field, timeRecord)


    for modelLev in modelLevsToPlot:
        
        plt.figure(figsize=(20,20))

        print ""
        print "GEOS-CTM level : ", modelLev
        print ""



        if geosCtmFieldArray1.shape != geosCtmFieldArray2.shape:
            print "Array shapes are different. Interpolation needed!"
            print "This feature is currently not supported for inter GEOS-CTM runs"
            sys.exit(0)

        else:
            print "Array shapes are the same, will continue with plotting..."




        z_GeosCtm1 = geosCtmFieldArray1[modelLev, :, :]
        z_GeosCtm2 = geosCtmFieldArray2[modelLev, :, :]

        z_Diff = z_GeosCtm1 / z_GeosCtm2


        minValueOfBoth = z_GeosCtm1.min()
        maxValueOfBoth = z_GeosCtm1.max()

        if z_GeosCtm2.min() < minValueOfBoth:
            minValueOfBoth = z_GeosCtm2.min()
        if z_GeosCtm2.max() > maxValueOfBoth:
            maxValueOfBoth = z_GeosCtm2.max()




        #-----------------------------------------------------#
        # GEOS-CTM 1

        print ""
        print "Min/max ", field, " values at level: ", modelLev
        print ""


        print "GEOS-CTM 1: ", z_GeosCtm1.min(), " / ", z_GeosCtm1.max()

        create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm1, \
                           [minValueOfBoth,maxValueOfBoth], \
                           [minGeosCtmLat,maxGeosCtmLat], \
                           [minGeosCtmLong, maxGeosCtmLong], 311, \
                           "GEOS-CTM " + geosCtmSimName1 + " " + \
                           field + " @ " + str(modelLev) + \
                            "mb " + dateYearMonth, "jet")

        print "GEOS-CTM 2: ", z_GeosCtm2.min(), " / ", z_GeosCtm2.max()

        create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm2, \
                           [minValueOfBoth,maxValueOfBoth], \
                           [minGeosCtmLat,maxGeosCtmLat], \
                           [minGeosCtmLong, maxGeosCtmLong], 312, \
                           "GEOS-CTM " + geosCtmSimName2 + " " + \
                           field + " @ " + str(modelLev) + \
                            "mb " + dateYearMonth, "jet")

        create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_Diff, \
#                           [z_Diff.min(), z_Diff.max()], \
                           [0, 1.5], \
                           [minGeosCtmLat,maxGeosCtmLat], \
                           [minGeosCtmLong, maxGeosCtmLong], 313, \
                           "Model ratio " + field + " @ " + str(modelLev) + \
                           " mb " + dateYearMonth, \
                           "nipy_spectral", \
                           normalize=True)
        #-----------------------------------------------------#



        file = "f"
        if file == "f":
            plt.savefig("plots/" + field + ".inter.GEOS-CTM."
                        + str(modelLev) + "." , bbox_inches='tight')
        elif file == "s":
            plt.show()

    fieldCount = fieldCount + 1


    

