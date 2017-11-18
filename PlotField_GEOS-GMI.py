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




order = "GMI"
list1 = gmiObject.fieldList
list2 = geosCtmObject.fieldList

print ""
print "Geos CTM field list: ", list2
print ""
print "GMI field list: ", list1


if len(geosCtmObject.fieldList) >= len(gmiObject.fieldList):
    list1 = geosCtmObject.fieldList
    list2 = gmiObject.fieldList
    order = "GEOS-CTM"

# Does not matter which object to use - this is weird code. 
fieldsToCompareAll = gmiObject.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and \
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



# Prepares basemap objects for plotting
print ""
print "Creating GEOS-CTM plot objects..."
geosCtmObject.createPlotObjects()
print "Creating GMI plot objects..."
gmiObject.createPlotObjects()
print ""


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

    print ""
    print "Min/max of GMI: ", z_Gmi.min(), "/", z_Gmi.max()
    print "Min/max of GEOS: ", z_GeosCtm.min(), "/", z_GeosCtm.max()
    print "Differences: ", z_Gmi.min() - z_GeosCtm.min(), "/", z_Gmi.max() - z_GeosCtm.max()


    zRangeGMI = z_Gmi.max() - z_Gmi.min()
    zRangeGEOS = z_GeosCtm.max() - z_GeosCtm.min()


    print "Ranges: ", zRangeGMI, "/", zRangeGEOS


    orderGMI = 1
    orderGEOS = 1
    if zRangeGMI != 0 and zRangeGEOS !=0:
        orderGMI = int(math.log10(zRangeGMI))
        orderGEOS = int(math.log10(zRangeGEOS))

    print orderGMI, "/", orderGEOS
    print "" 




    minValueOfBoth = z_GeosCtm.min()
    maxValueOfBoth = z_GeosCtm.max()
        
    if z_Gmi.min() < minValueOfBoth:
        minValueOfBoth = z_Gmi.min()
    if z_Gmi.max() > maxValueOfBoth:
        maxValueOfBoth = z_Gmi.max()

    for lat in range(0, size(geosCtmObject.lat)):
        for long in range(0, size(geosCtmObject.long)):

            if z_Gmi[lat, long] == 0 and z_GeosCtm[lat, long] == 0:
                #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
                z_Diff[lat, long] = 1.0






    #-----------------------------------------------------#
    # GEOS-CTM

    print ""
    print "Min/max ", field, " values at level: ", modelLev
    print ""


    print ""
    print "GEOS-CTM: ", z_GeosCtm.min(), " / ", z_GeosCtm.max()
    print ""


    if z_GeosCtm.max() - z_GeosCtm.min() == 0.0 or orderGEOS < -13:
        print "Constant field found for GEOS-CTM!"
        useMin = z_GeosCtm.min()
        useMax = z_GeosCtm.max()

    else:
        useMin = minValueOfBoth
        useMax = maxValueOfBoth


    geosCtmObject.create2dSlice2 (z_GeosCtm, [useMin, useMax], \
                                      311, "GEOS-CTM " + geosCtmSimName + " " + \
                                      field + " @ " + str(modelLev) + \
                                      "mb " + dateYearMonth, "jet")


    print ""
    print "GMI: ", z_Gmi.min(), " / ", z_Gmi.max()
    print "" 

    if z_Gmi.max() - z_Gmi.min() == 0.0 or orderGMI < -13:
        print "Constant field found for GMI"
        useMin = z_Gmi.min()
        useMax = z_Gmi.max()

    else:
        useMin = minValueOfBoth
        useMax = maxValueOfBoth


    # GMI lev0 is surface
    # using geosCtmObject because GMI should now be on lat/long system of GEOS-CTM
    geosCtmObject.create2dSlice2 (z_Gmi, [useMin, useMax], \
                                      312, "GMI " + gmiSimName + " " + \
                                      field + " @ " + str(modelLev) + \
                                      " mb " + dateYearMonth, "jet")


    geosCtmObject.create2dSlice2 (z_Diff, \
                                     #[z_Diff.min(), z_Diff.max()], \
                                     [0, 1.5], \
                                     313, "Model ratio " + field + " @ " + str(modelLev) + \
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
print ""
