#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 21st 2017
#
# DESCRIPTION:
# Driver to plot differences between GMI and GEOS-CTM species
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
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


NUM_ARGS = 2

def usage ():
    print ""
    print "usage: PlotRestartSpecies.py [-c] [-g]"
    print "-c GEOS CTM restart file"
    print "-g GMI restart file"
    print ""
    sys.exit (0)


print "Start plotting restart species differences"

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]

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
                             'longitude_dim', 'eta_dim', 'hdr', \
                             'const_labels')
print ""


order = "GMI"
list1 = gmiObject.fieldList
list2 = geosCtmObject.fieldList

if len(geosCtmObject.fieldList) >= len(gmiObject.fieldList):
    list1 = geosCtmObject.fieldList
    list2 = gmiObject.fieldList
    order = "GEOS-CTM"

# Does not matter which object to use - this is weird code. :/
fieldsToCompare = gmiObject.returnFieldsInCommon (list1, list2, order)

print "Fields to compare: ", fieldsToCompare[:]


print "Long records GEOS: ", geosCtmObject.longSize

longRecords = numpy.zeros(gmiObject.longSize, numpy.float32)

remappedGmiArray = numpy.zeros((1, gmiObject.levelSize, \
                           gmiObject.latSize, \
                           gmiObject.longSize), numpy.float32)

newGmiArray = numpy.zeros((1, gmiObject.levelSize, \
                           gmiObject.latSize, \
                           geosCtmObject.longSize), numpy.float32)


diffArray = numpy.zeros((1, gmiObject.levelSize, \
                           gmiObject.latSize, \
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
print "Basemap info for Geos-Ctm: "
print "llcr lon: ", minGeosCtmLong
print "llcr lat: ", minGeosCtmLat
print "urc lon: ", maxGeosCtmLong
print "urc lat: ", maxGeosCtmLat
print "centers lat/long: ", cenGeosCtmLat, cenGeosCtmLong
print ""


# temporarily here while I debug the interpolation problem
# this is the Basemap for normal GMI fields
baseMapGmi =  Basemap(llcrnrlon=gmiObject.long[:].min(), \
                  llcrnrlat=gmiObject.lat[:].min(), \
                  urcrnrlon=gmiObject.long[:].max(), \
                  urcrnrlat=gmiObject.lat[:].max() ,\
                  projection='cyl', \
                  lat_0=cenGeosCtmLat,lon_0=cenGmiLong)


gridLonsGeosCtm,gridLatsGeosCtm = baseMapGeosCtm.makegrid(geosCtmObject.longSize, geosCtmObject.latSize)
X_GeosCtm, Y_GeosCtm = baseMapGeosCtm(gridLonsGeosCtm,gridLatsGeosCtm)


fieldCount = 0
for field in fieldsToCompare[:]:
    
    print ""
    print "Processing: ", field

    plt.figure(figsize=(20,20))

    gmiFieldArray = gmiObject.returnField (field)
    geosCtmFieldArray = geosCtmObject.returnField (field)

    # put GMI on -180 to 0 to 180
    lenGmiLong = len(gmiObject.long[:])
        
    remappedGmiArray [:,:,:,0:lenGmiLong/2] = gmiFieldArray[:,:,:,lenGmiLong/2:lenGmiLong]
    remappedGmiArray [:,:,:,lenGmiLong/2:lenGmiLong] = gmiFieldArray[:,:,:,0:lenGmiLong/2]
    remappedLong = numpy.zeros(lenGmiLong, float32)
    remappedLong [0:lenGmiLong/2] = gmiObject.long[lenGmiLong/2:lenGmiLong] - 360.0
    remappedLong [lenGmiLong/2:lenGmiLong] = gmiObject.long[0:lenGmiLong/2]
        

    remappedLongPlus180 = numpy.zeros(lenGmiLong, float32)
    remappedLongPlus180[:] = remappedLong[:] + 180.0

    geosCtmLongPlus180 = numpy.zeros(geosCtmObject.longSize, float32)
    geosCtmLongPlus180 [:] = geosCtmObject.long[:] + 180.0


    if gmiFieldArray.shape != geosCtmFieldArray.shape:
        print "Array shapes are different. Interpolation needed!"

        # GMI field array of shape:  (1, 72, 181, 288)
        # GEOS-CTM field array of shape:  (1, 72, 181, 360)
        # longitude from 288 to 360 (GMI->GEOS-CTM)
        # loop over model_levs and latitude

        levCount = 0
        for modelLev in gmiObject.lev[:]:
        
            latCount = 0
            for lat in gmiObject.lat[:]:

                longRecords[:] = remappedGmiArray [0, levCount, latCount,:]

                yinterp =  numpy.interp(geosCtmLongPlus180, remappedLongPlus180, longRecords)

                newGmiArray[0, levCount, latCount, :] = yinterp [:]

                latCount = latCount + 1

            levCount = levCount + 1
            if levCount != 0: break

    else:
        newGmiArray[:,:,:,:] = remappedGmiArray[:,:,:,:]



    print "old GMI array: min/max -- ", remappedGmiArray.min(), "/", remappedGmiArray.max()
    print "new GMI array: min/max -- ", newGmiArray.min(), "/", newGmiArray.max()

    z_GeosCtm = geosCtmFieldArray[0, 71, :, :]
    z_Gmi = newGmiArray[0, 0, :, :]
    z_Diff = z_GeosCtm - z_Gmi


    minValueOfBoth = z_GeosCtm.min()
    maxValueOfBoth = z_GeosCtm.max()

    if z_Gmi.min() < minValueOfBoth:
        minValueOfBoth = z_Gmi.min()
    if z_Gmi.max() > maxValueOfBoth:
        maxValueOfBoth = z_Gmi.max()



    #-----------------------------------------------------#
    # GEOS-CTM
    plt.subplot(311)

    imSlice = baseMapGeosCtm.pcolor(X_GeosCtm,Y_GeosCtm,z_GeosCtm, cmap='jet', \
                                        vmin=minValueOfBoth, vmax=maxValueOfBoth)
    # colorbar based on slice
    cb = plt.colorbar(imSlice, orientation='horizontal')
    cb.formatter.set_powerlimits((0, 0))
    cb.update_ticks()

    baseMapGeosCtm.drawparallels(numpy.arange(minGeosCtmLat,maxGeosCtmLat,40),labels=[1,0,0,0])
    baseMapGeosCtm.drawmeridians(numpy.arange(minGeosCtmLong,maxGeosCtmLong,80),labels=[0,1,0,1])
    baseMapGeosCtm.drawcoastlines()
    baseMapGeosCtm.drawstates()
    #-----------------------------------------------------#


    #-----------------------------------------------------#
    # GMI lev0 is surface
    plt.subplot(312)


    # this is for GMI data interpolated to GEOS-CTM
    cenGmiCtmLat = (gmiObject.lat[:].min() + gmiObject.lat[:].max() ) / 2.0
    baseMapGmiInterp = Basemap(llcrnrlon=minGeosCtmLong,\
                                   llcrnrlat=gmiObject.lat[:].min(), \
                                   urcrnrlon=maxGeosCtmLong,\
                                   urcrnrlat=gmiObject.lat[:].max(), \
                                   projection='cyl', \
                                   lat_0=cenGmiCtmLat,lon_0=cenGeosCtmLong)
    gridLonsGmiInterp,gridLatsGmiInterp = baseMapGmiInterp.makegrid(geosCtmObject.longSize, gmiObject.latSize)
    X_GmiInterp, Y_GmiInterp = baseMapGmiInterp(gridLonsGmiInterp,gridLatsGmiInterp)


    imSlice = baseMapGmiInterp.pcolor(X_GmiInterp,Y_GmiInterp,z_Gmi, cmap='jet', \
                                        vmin=minValueOfBoth, vmax=maxValueOfBoth)
 
    # colorbar based on slice
    cb = plt.colorbar(imSlice, orientation='horizontal')
    cb.formatter.set_powerlimits((0, 0))
    cb.update_ticks()

    baseMapGmiInterp.drawparallels(numpy.arange(gmiObject.lat[:].min(),gmiObject.lat[:].max(),40),labels=[1,0,0,0])
    baseMapGmiInterp.drawmeridians(numpy.arange(minGeosCtmLong,maxGeosCtmLong,80),labels=[0,1,0,1])
    baseMapGmiInterp.drawcoastlines()
    baseMapGmiInterp.drawstates()


    #-----------------------------------------------------#

    



    #-----------------------------------------------------#
    # diff/ratio of GMI and GEOS-CTM
    plt.subplot(313)

    imSlice = baseMapGeosCtm.pcolor(X_GeosCtm,Y_GeosCtm,z_Diff, cmap='jet', \
                           vmin=z_Diff.min(), vmax=z_Diff.max())

    # colorbar based on slice
    cb = plt.colorbar(imSlice, orientation='horizontal')
    cb.formatter.set_powerlimits((0, 0))
    cb.update_ticks()

    baseMapGeosCtm.drawparallels(numpy.arange(minGeosCtmLat,maxGeosCtmLat,40),labels=[1,0,0,0])
    baseMapGeosCtm.drawmeridians(numpy.arange(minGeosCtmLong,maxGeosCtmLong,80),labels=[0,1,0,1])
    baseMapGeosCtm.drawcoastlines()
    baseMapGeosCtm.drawstates()

    #-----------------------------------------------------#



    plt.show()


    print "Diff array min/max values are : ", diffArray.min(), "/", diffArray.max()

    fieldCount = fieldCount + 1
    if fieldCount == 2: break

    

