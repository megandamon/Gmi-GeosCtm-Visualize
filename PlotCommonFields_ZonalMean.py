#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         July 3 2017
#
# DESCRIPTION:
# Driver to plot zonal mean differences between GMI and GEOS-CTM species
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
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


FILE = "f"

NUM_ARGS = 4
def usage ():
    print ""
    print "usage: PlotRestartSpecies_ZonalMean.py [-c] [-g] [-r] [-d]"
    print "-c GEOS CTM file"
    print "-g GMI  file"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print ""
    sys.exit (0)

def find_nearest(array, value):
    idx = (numpy.abs(array-value)).argmin()
    return array[idx]

def findLevelFromArray(array, value):

    theValue = find_nearest(array[:], value)

    levCount = 0
    for item in array[:]:
        if item == theValue:
            returnLev = levCount
        levCount = levCount + 1
        
    return returnLev


def plotZM(data, x, y, fig, ax1, colorMap, dataMin, dataMax, plotOpt=None):
    """Create a zonal mean contour plot of one variable
    plotOpt is a dictionary with plotting options:
    'scale_factor': multiply values with this factor before plotting
    'units': a units label for the colorbar
    'levels': use list of values as contour intervals
    'title': a title for the plot
    """

    if plotOpt is None: plotOpt = {}


    # scale data if requested
    scale_factor = plotOpt.get('scale_factor', 1.0)
    pdata = data * scale_factor

    # determine contour levels to be used; default: linear spacing, 20 levels
    clevs = plotOpt.get('levels', numpy.linspace(dataMin, dataMax, 20))

    # map contour values to colors
    norm=colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    print "data min/ max: ", dataMin,  " / " , dataMax

    # draw the (filled) contours
    contour = ax1.contourf(x, y, pdata, levels=clevs, norm=norm, cmap=colorMap, \
                               vmin = dataMin, vmax = dataMax)

    # add a title
    title = plotOpt.get('title',  'Zonal Mean')
    ax1.set_title(title)   # optional keyword: fontsize="small"

    # add colorbar
    # Note: use of the ticks keyword forces colorbar to draw all labels
    fmt = ticker.FormatStrFormatter("%.2g")
    cbar = fig.colorbar(contour, ax=ax1, orientation='horizontal', shrink=0.8,
                        format=fmt)

    cbar.set_label(plotOpt.get('units', ''))
    for t in cbar.ax.get_xticklabels():
        t.set_fontsize("x-small")



    # change font size of x labels
    xlabels = ax1.get_xticklabels()
    for t in xlabels:
        t.set_fontsize("x-small")

    # set up y axes: log pressure labels on the left y axis
    ax1.set_ylabel("Pressure [hPa]")
    ax1.set_yscale('log')
    ax1.set_ylim(y.max(), y.min())
    subs = [1,2,5]
    print "y_max/y_min = ", y.max()/y.min()
    if y.max()/y.min() < 30.:
        subs = [1,2,3,4,5,6,7,8,9]
    loc = ticker.LogLocator(base=10., subs=subs)
    ax1.yaxis.set_major_locator(loc)
    fmt = ticker.FormatStrFormatter("%g")
    ax1.yaxis.set_major_formatter(fmt)
    ylabels = ax1.get_yticklabels()
    for t in ylabels:
        t.set_fontsize("x-small")



print "Start plotting zonal mean differences"

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]

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
                             'longitude_dim', 'eta_dim', 'hdr', \
#                              'freq1_labels')
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

print ""
print "Fields to compare: ", fieldsToCompare[:]
print "GMI model levels: ", gmiObject.lev[:]
print ""


# Arrays (one time record, one species)
longRecords = numpy.zeros(gmiObject.longSize, numpy.float32)

remappedGmiArray = numpy.zeros((gmiObject.levelSize, \
                                    gmiObject.latSize, \
                                    gmiObject.longSize), numpy.float32)

newGmiArray = numpy.zeros((gmiObject.levelSize, \
                               gmiObject.latSize, \
                               geosCtmObject.longSize), numpy.float32)

gmiZonalArray = numpy.zeros ((gmiObject.levelSize, \
                                  gmiObject.latSize), numpy.float32)

geosCtmZonalArray = numpy.zeros ((geosCtmObject.levelSize, \
                                      geosCtmObject.latSize), numpy.float32)

fieldCount = 9
for field in fieldsToCompare[:]:
    
    field = fieldsToCompare[fieldCount]
    print ""
    print "Processing: ", field



    geosCtmFieldArray = geosCtmObject.returnField (field, timeRecord)
    gmiFieldArray = gmiObject.returnField (field, timeRecord)

    print "shapes of arrays: ", geosCtmFieldArray.shape, gmiFieldArray.shape

    # put GMI on -180 to 0 to 180
    lenGmiLong = len(gmiObject.long[:])
        
    remappedGmiArray [:,:,0:lenGmiLong/2] = gmiFieldArray[:,:,lenGmiLong/2:lenGmiLong]
    remappedGmiArray [:,:,lenGmiLong/2:lenGmiLong] = gmiFieldArray[:,:,0:lenGmiLong/2]
    remappedLong = numpy.zeros(lenGmiLong, float32)
    remappedLong [0:lenGmiLong/2] = gmiObject.long[lenGmiLong/2:lenGmiLong] - 360.0
    remappedLong [lenGmiLong/2:lenGmiLong] = gmiObject.long[0:lenGmiLong/2]
        
    remappedLongPlus180 = numpy.zeros(lenGmiLong, float32)
    remappedLongPlus180[:] = remappedLong[:] + 180.0


    if gmiFieldArray.shape != geosCtmFieldArray.shape:
            print "Array shapes are different. Interpolation needed!"
    
            modelLevCount = 0

            for modelLev in geosCtmObject.lev[:]:

                latCount = 0
                for lat in gmiObject.lat[:]:

                    longRecords[:] = remappedGmiArray [modelLevCount, latCount,:]
                        
                    yinterp =  numpy.interp(geosCtmObject.long[:], remappedLong[:], longRecords)
            
                    newGmiArray[modelLevCount, latCount, :] = yinterp [:]

                    latCount = latCount + 1

                modelLevCount = modelLevCount + 1



    else:
        newGmiArray[:,:, :] = remappedGmiArray[:,:,:]

        

    # Now we should have arrays of the same size on the same long coordinate system
    print ""
    print "Length of new GMI array: ", newGmiArray.shape
    print "Length of GEOS-CTM array: ", geosCtmFieldArray.shape
    print ""

    # now we can create zonal means

    print "Geos-CTM levs: ", geosCtmObject.lev[:]
    print "GMI levs: ", gmiObject.lev[:]

    # Need to find tropMaxLev and tropMinLev from GMI
    tropMinLev = findLevelFromArray (gmiObject.lev, 100.00)

    print ""
    print gmiObject.lev[:]
    print ""

    print ""
    print"Trop levels: ",  gmiObject.lev[0:tropMinLev+1]
    print "Strat levels: '", gmiObject.lev[tropMinLev+1::]
    print ""


    # lev, lat, long
    zmGmiTrop = numpy.mean (newGmiArray[0:tropMinLev+1, :, :], axis=2)

    geosCtmSurface = geosCtmObject.levelSize-1
    geosCtmTropPause = (geosCtmObject.levelSize-1) - tropMinLev


    print ""
    print "GMI trop 0 : ", tropMinLev
    print "GEOS-CTM trop ", geosCtmTropPause, " : ", geosCtmSurface
    print ""


    zmGeosCtmTrop = numpy.mean (geosCtmFieldArray[geosCtmTropPause:geosCtmSurface+1, :, :], \
                                    axis=2)

    # flip the array to the same orientation as GMI 
    zmGeosCtmTropRev = zmGeosCtmTrop[::-1, :]

    print "Size of zm GEOS: ", zmGeosCtmTrop.shape
    print "Size of zm GMI: ", zmGmiTrop.shape

    minValueOfBoth = zmGeosCtmTropRev.min()
    maxValueOfBoth = zmGeosCtmTropRev.max()

    if zmGmiTrop.min() < minValueOfBoth:
        minValueOfBoth = zmGmiTrop.min()
    if zmGmiTrop.max() > maxValueOfBoth:
        maxValueOfBoth = zmGmiTrop.max()


    fig = plt.figure(figsize=(20,20))
    plotOpt = {}

    ax1 = fig.add_subplot(311)
    plotOpt['title'] = "GEOS-CTM " + geosCtmSimName + " " + field + " ZM " + dateYearMonth
    plotZM (zmGeosCtmTropRev, geosCtmObject.lat[:], \
                gmiObject.lev[0:tropMinLev+1], fig, ax1, 'jet', minValueOfBoth, \
                maxValueOfBoth, plotOpt)
    ax2 = fig.add_subplot(312)
    plotOpt['title'] = "GMI " + gmiSimName + " " + field + " ZM " + dateYearMonth
    plotZM (zmGmiTrop, gmiObject.lat[:], gmiObject.lev[0:tropMinLev+1], \
                fig, ax2, 'jet', minValueOfBoth, maxValueOfBoth, plotOpt)
    ax3 = fig.add_subplot(313)    
    plotOpt['title'] = "Model ratio " + field + " " + " ZM " + dateYearMonth
    plotZM (zmGeosCtmTropRev/zmGmiTrop, gmiObject.lat[:], \
                gmiObject.lev[0:tropMinLev+1], fig, ax3, 'nipy_spectral', \
                0.0, 1.5, plotOpt)



    if FILE == "f":
        plt.savefig ("plots/" + field + ".GEOS-CTM.GMI."
                     + "trop.", bbox_inches='tight')
    else:
        plt.show()


    zmGmiStrat = numpy.mean (newGmiArray[tropMinLev::], axis=2)
    zmGeosCtmStrat = numpy.mean (geosCtmFieldArray[0:geosCtmTropPause+1, :, :] ,\
                                     axis=2)

    print ""
    print "size of gmi strat: ", zmGmiStrat.shape
    print "size of geosctm strat: ", zmGeosCtmStrat.shape
    print ""
    
    print ""
    print "gmi strat: ", tropMinLev, " : ", len(newGmiArray) -1 
    print "geos ctm strat: 0 : ", geosCtmTropPause
    print ""


    # flip the array to the same orientation as GMI 
    zmGeosCtmStratRev = zmGeosCtmStrat[::-1, :]

    minValueOfBoth = zmGeosCtmStratRev.min()
    maxValueOfBoth = zmGeosCtmStratRev.max()

    if zmGmiStrat.min() < minValueOfBoth:
        minValueOfBoth = zmGmiStrat.min()
    if zmGmiStrat.max() > maxValueOfBoth:
        maxValueOfBoth = zmGmiStrat.max()



    fig = plt.figure(figsize=(20,20))
    plotOpt = {}
    ax1 = fig.add_subplot(311)
    plotOpt['title'] = "GEOS-CTM " + geosCtmSimName + " " + field + " ZM " + dateYearMonth
    plotZM (zmGeosCtmStratRev, geosCtmObject.lat[:], \
                gmiObject.lev[tropMinLev::], fig, ax1, 'jet', minValueOfBoth, \
                maxValueOfBoth, plotOpt)
    ax2 = fig.add_subplot(312)
    plotOpt['title'] = "GMI " + gmiSimName + " " + field + " ZM " + dateYearMonth
    plotZM (zmGmiStrat, gmiObject.lat[:], gmiObject.lev[tropMinLev::], \
                fig, ax2, 'jet', minValueOfBoth, maxValueOfBoth, plotOpt)
    ax3 = fig.add_subplot(313)    
    plotOpt['title'] = "Model ratio " + field + " " + " ZM " + dateYearMonth
    plotZM (zmGeosCtmStratRev/zmGmiStrat, gmiObject.lat[:], \
                gmiObject.lev[tropMinLev::], fig, ax3, 'nipy_spectral', \
                0.0, 1.5, plotOpt)


    if FILE == "f":
        plt.savefig ("plots/" + field + ".GEOS-CTM.GMI."
                     + "strat.", bbox_inches='tight')
    else:
        plt.show()


    fieldCount = fieldCount + 1


    

