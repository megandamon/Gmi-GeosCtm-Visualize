#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         August 14 2017
#
# DESCRIPTION:
# Driver to plot differences of a single field between GMI and GEOS-CTM species
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

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


import math
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools




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


NUM_ARGS = 5
def usage ():
    print ""
    print "usage: PlotField_GEOS-GMI.py [-c] [-g] [-r] [-d] [-f]"
    print "-c GEOS CTM restart file"
    print "-g GMI restart file"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print "-f field to compare"
    print ""
    sys.exit (0)


print "Start plotting field differences."


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile):
    print "The file you provided does not exist: ", geosCtmFile
    sys.exit(0)

if not os.path.exists (gmiFile):
    print "The file you provided does not exist: ", gmiFile
    sys.exit(0)


if int(timeRecord) > 30: 
    print "WARNING: time record is more than a typical daily file!"

if int(timeRecord) < 0: 
    print "ERROR: time record needs to be positive!"
    sys.exit(0)

if len(dateYearMonth) != 6:
    print "ERROR date must be in the format YYYYMM. Received: ", dateYearMonth
    sys.exit(0)



print geosCtmFile
print gmiFile

geosCtmSimName = geosCtmFile.split(".")[0]
gmiSimName = gmiFile.split("_")[1]


#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------
geosCtmObject = GeosCtmPlotTools (geosCtmFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


gmiObject = GmiPlotTools (gmiFile, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'hdr', 'const_labels')
print ""


order = "GMI"
list1 = gmiObject.fieldList
list2 = geosCtmObject.fieldList

if len(geosCtmObject.fieldList) >= len(gmiObject.fieldList):
    list1 = geosCtmObject.fieldList
    list2 = gmiObject.fieldList
    order = "GEOS-CTM"

# Does not matter which object to use - this is weird code. :/
fieldsToCompareAll = gmiObject.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and field[0:2] != "EM" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)

print ""
print "Fields to compare: ", fieldsToCompare[:]
print ""

foundField = False
print ""
for fieldInList in fieldsToCompare[:]:

    if fieldToCompare.lower() == fieldInList.lower():
        print "Success: ", fieldToCompare, " can be compared!"
        foundField = True

if foundField == False:
    print "ERROR: ", fieldToCompare, " cannot be compared!"
    sys.exit(-1)






print "GMI model levels: ", gmiObject.lev[:]
modelLevsToPlotGmi = {}
levCount = 0
for lev in gmiObject.lev[:]:
    if int(lev) == 992 or int(lev) == 506 or int(lev) == 192:
        modelLevsToPlotGmi [int(lev)] = levCount
    levCount = levCount + 1



# Arrays (one time record, one species)
longRecords = numpy.zeros(gmiObject.longSize, numpy.float32)

remappedGmiArray = numpy.zeros((gmiObject.levelSize, \
                                    gmiObject.latSize, \
                                    gmiObject.longSize), numpy.float32)

newGmiArray = numpy.zeros((gmiObject.latSize, \
                               geosCtmObject.longSize), numpy.float32)


minGeosCtmLat = geosCtmObject.lat[:].min()
maxGeosCtmLat = geosCtmObject.lat[:].max()
minGeosCtmLong = geosCtmObject.long[:].min()
maxGeosCtmLong = geosCtmObject.long[:].max()

cenGeosCtmLat = (minGeosCtmLat + maxGeosCtmLat)/2.
cenGeosCtmLong =  (minGeosCtmLong + maxGeosCtmLong)/2.


baseMapGeosCtm = Basemap(llcrnrlon=minGeosCtmLong,llcrnrlat=minGeosCtmLat,\
                             urcrnrlon=maxGeosCtmLong,urcrnrlat=maxGeosCtmLat,\
                             projection='cyl', \
                             lat_0=cenGeosCtmLat,lon_0=cenGeosCtmLong)

cenGmiLong = (gmiObject.long[:].min() + gmiObject.long[:].max()) / 2.0

print ""
print "Basemap info: "
print "llcr lon: ", minGeosCtmLong
print "llcr lat: ", minGeosCtmLat
print "urc lon: ", maxGeosCtmLong
print "urc lat: ", maxGeosCtmLat
print "centers lat/long: ", cenGeosCtmLat, cenGeosCtmLong
print ""


gridLonsGeosCtm,gridLatsGeosCtm = baseMapGeosCtm.makegrid(geosCtmObject.longSize, geosCtmObject.latSize)
X_GeosCtm, Y_GeosCtm = baseMapGeosCtm(gridLonsGeosCtm,gridLatsGeosCtm)


plt.figure(figsize=(20,20))

print ""
print "Processing: ", fieldToCompare
print ""

field = fieldToCompare

geosCtmFieldArray = geosCtmObject.returnField (field, timeRecord)
gmiFieldArray = gmiObject.returnField (field, timeRecord)

print ""
print "Shape of GEOS-CTM field: ", geosCtmFieldArray.shape[:]
print "Shape of GMI field: ", gmiFieldArray.shape[:]
print ""



# put GMI on -180 to 0 to 180
lenGmiLong = len(gmiObject.long[:])
        
remappedGmiArray [:,:,0:lenGmiLong/2] = gmiFieldArray[:,:,lenGmiLong/2:lenGmiLong]
remappedGmiArray [:,:,lenGmiLong/2:lenGmiLong] = gmiFieldArray[:,:,0:lenGmiLong/2]
remappedLong = numpy.zeros(lenGmiLong, float32)
remappedLong [0:lenGmiLong/2] = gmiObject.long[lenGmiLong/2:lenGmiLong] - 360.0
remappedLong [lenGmiLong/2:lenGmiLong] = gmiObject.long[0:lenGmiLong/2]
        

remappedLongPlus180 = numpy.zeros(lenGmiLong, float32)
remappedLongPlus180[:] = remappedLong[:] + 180.0

geosCtmLongPlus180 = numpy.zeros(geosCtmObject.longSize, float32)
geosCtmLongPlus180 [:] = geosCtmObject.long[:] + 180.0


levCount = 0
for modelLev in modelLevsToPlotGmi:
        
    print ""
    print "GMI : ", modelLev, " mb at index: ", modelLevsToPlotGmi[modelLev], \
        " GEOS-CTM index: ", (geosCtmObject.levelSize - 1) - modelLevsToPlotGmi[modelLev]
    print ""



    if gmiFieldArray.shape != geosCtmFieldArray.shape:
        print "Array shapes are different. Interpolation needed!"

        latCount = 0
        for lat in gmiObject.lat[:]:

            longRecords[:] = remappedGmiArray [modelLevsToPlotGmi[modelLev], latCount,:]
            
            yinterp =  numpy.interp(geosCtmLongPlus180, remappedLongPlus180, longRecords)
                
            newGmiArray[latCount, :] = yinterp [:]

            latCount = latCount + 1


    else:
        newGmiArray[:,:] = remappedGmiArray[modelLevsToPlotGmi[modelLev],:,:]


    levCount = levCount + 1

    print "Extracting GeosCtm level: ", (geosCtmObject.levelSize-1) - \
        modelLevsToPlotGmi[modelLev]

    z_GeosCtm = geosCtmFieldArray[(geosCtmObject.levelSize-1) \
                                      - modelLevsToPlotGmi[modelLev], :, :]
    z_Gmi = newGmiArray[:, :]
    z_Diff = z_GeosCtm / z_Gmi


    minValueOfBoth = z_GeosCtm.min()
    maxValueOfBoth = z_GeosCtm.max()
        
    if z_Gmi.min() < minValueOfBoth:
        minValueOfBoth = z_Gmi.min()
    if z_Gmi.max() > maxValueOfBoth:
        maxValueOfBoth = z_Gmi.max()


    #-----------------------------------------------------#
    # GEOS-CTM

    print ""
    print "Min/max ", field, " values at level: ", modelLev
    print ""


    print "GEOS-CTM: ", z_GeosCtm.min(), " / ", z_GeosCtm.max()

    create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_GeosCtm, \
                       [minValueOfBoth,maxValueOfBoth], \
                       [minGeosCtmLat,maxGeosCtmLat], \
                       [minGeosCtmLong, maxGeosCtmLong], 311, \
                       "GEOS-CTM " + geosCtmSimName + " " + \
                       field + " @ " + str(modelLev) + \
                       "mb " + dateYearMonth, "jet")


    print "GMI: ", z_Gmi.min(), " / ", z_Gmi.max()
    print "" 

    # GMI lev0 is surface
    create2dSlice (baseMapGeosCtm, X_GeosCtm, Y_GeosCtm, z_Gmi, \
                       [minValueOfBoth,maxValueOfBoth], \
                       [minGeosCtmLat,maxGeosCtmLat], \
                       [minGeosCtmLong, maxGeosCtmLong], 312, \
                       "GMI " + gmiSimName + " " + \
                       field + " @ " + str(modelLev) + \
                       " mb " + dateYearMonth, "jet")

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
        plt.savefig("plots/" + field + ".GEOS-CTM.GMI."
                    + str(modelLev) + "." , bbox_inches='tight')
    elif file == "s":
        plt.show()
        
    plt.clf()


print ""
print "Plotted : ", fieldToCompare, " to plots/directory"
