#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         September 21 2017
#
# DESCRIPTION:
# Driver to plot zonal mean differences for potentially two different fields
# 1. A GEOS-CTM file in 72 model levels
# 2. A GEOS-CTM file in 42 pressure levels or in 72 model levels
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
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


FILE = "f"

NUM_ARGS = 6
def usage ():
    print("")
    print("usage: PlotField_ZonalMean-DiffLev.py [-c] [-g] [-r] [-d] [-f] [-o]")
    print("-c File1 (GEOS-CTM)")
    print("-g File2 (GMI  or GEOS-CTM) [if GMI format is gmi*.nc]")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-f field to compare")
    print("-o other field to compare")
    print("")
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

    #print "data min/ max: ", dataMin,  " / " , dataMax

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
    #print "y_max/y_min = ", y.max()/y.min()
    if y.max()/y.min() < 30.:
        subs = [1,2,3,4,5,6,7,8,9]
    loc = ticker.LogLocator(base=10., subs=subs)
    ax1.yaxis.set_major_locator(loc)
    fmt = ticker.FormatStrFormatter("%g")
    ax1.yaxis.set_major_formatter(fmt)
    ylabels = ax1.get_yticklabels()
    for t in ylabels:
        t.set_fontsize("x-small")



print("Start plotting zonal mean differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:o:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
file2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
otherFieldToCompare = optList[5][1]

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile):
    print("The GEOS-CTM file you provided does not exist: ", geosCtmFile)
    sys.exit(0)

if not os.path.exists (file2):
    print("The GEOS-CTM or GMI file you provided does not exist: ", file2)
    print("GMI format must be in gmi*.nc")
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)


print(geosCtmFile)
print(file2)

geosCtmSimName = geosCtmFile.split(".")[0]

sim2Name = file2.split(".")[0]
plotTitleFile2 = "GEOS-CTM " + sim2Name
fileTitle = ".GEOS-CTM."




print("")
print("geosCtmSimName: ", geosCtmSimName)
print("sim2Name: ", sim2Name)
print("")

#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosCtmObject = GeosCtmPlotTools (geosCtmFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


file2Object = GeosCtmPlotTools (file2, 'lat','lon',\
                                    'lev','time', 'lat', \
                                    'lon', 'lev', 'time' )


list1 = geosCtmObject.fieldList
list2 = file2Object.fieldList


print("")
print("Fields to compare: ", fieldToCompare, otherFieldToCompare)
print("")


successFlag = False
print("")
if fieldToCompare in list1[:]:
    print("Success: ", fieldToCompare, " can be compared!")
    if otherFieldToCompare in list2[:]:
        print("Success: ", otherFieldToCompare, " can be compared!")
        successFlag = True

if successFlag == False:
        print("ERROR: ", fieldToCompare, " or ", otherFieldToCompare, " cannot be compared!")
        sys.exit(-1)




# Arrays (one time record, one species or field)

# file2 has the potential to have a different lognitude system and length 
# This is because GMI is on a 0-360 system
# And GEOS-CTM is very flexible about resolution
longRecords = numpy.zeros(file2Object.longSize, numpy.float32)

remappedFile2Array = numpy.zeros((file2Object.levelSize, \
                                    file2Object.latSize, \
                                    file2Object.longSize), numpy.float32)

newFile2Array = numpy.zeros((file2Object.levelSize, \
                               file2Object.latSize, \
                               geosCtmObject.longSize), numpy.float32)

file2ZonalArray = numpy.zeros ((file2Object.levelSize, \
                                  file2Object.latSize), numpy.float32)

geosCtmZonalArray = numpy.zeros ((geosCtmObject.levelSize, \
                                      geosCtmObject.latSize), numpy.float32)




print("")
print("Processing: ", fieldToCompare, " and ", otherFieldToCompare)
print("")



geosCtmFieldArray = geosCtmObject.returnField (fieldToCompare, timeRecord)
file2FieldArray = file2Object.returnField (otherFieldToCompare, timeRecord)

print("shapes of arrays: ", geosCtmFieldArray.shape, file2FieldArray.shape)



print("")
print("File2 assumed to be in GEOS-CTM format. Will not remap longitude coordinate")
print("")
    
remappedFile2Array [:,:,:] = file2FieldArray[:,:,:]
remappedLong  = file2Object.long[:]
newFile2Array[:,:, :] = remappedFile2Array[:,:,:]


zmGeosCtm = numpy.mean (geosCtmFieldArray[:, :, :], axis=2)

zmFile2 = numpy.mean(newFile2Array[:, :, :],axis=2)


print("")
print("shape of zm from file1: ", shape(zmGeosCtm))
print("shape of zm from file2: ", shape(zmFile2))
print("")

minValueOfBoth = zmGeosCtm.min()
maxValueOfBoth = zmGeosCtm.max()

if zmFile2.min() < minValueOfBoth:
    minValueOfBoth = zmFile2.min()
if zmFile2.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2.max()


print("")
print("min/max of both: ", minValueOfBoth, "/", maxValueOfBoth)


fig = plt.figure(figsize=(20,20))
plotOpt = {}

ax1 = fig.add_subplot(311)
plotOpt['title'] = "GEOS-CTM " + geosCtmSimName + " " + fieldToCompare + \
    " ZM " + dateYearMonth
plotZM (zmGeosCtm, geosCtmObject.lat[:], \
            geosCtmObject.lev[:], fig, ax1, 'jet', \
#            minValueOfBoth, maxValueOfBoth, \
            zmGeosCtm.min(), zmGeosCtm.max(), \
            plotOpt)

ax2 = fig.add_subplot(312)
plotOpt['title'] = plotTitleFile2 + " " + otherFieldToCompare + \
    " ZM " + dateYearMonth
plotZM (zmFile2, file2Object.lat[:], file2Object.lev[:], \
            fig, ax2, 'jet', \
#            minValueOfBoth, maxValueOfBoth, \
            zmFile2.min(), zmFile2.max(), \
            plotOpt)


if shape(file2Object.lev) == shape(geosCtmObject.lev):
    print("")
    print("Levels are the same across files, will plot ratio!")
    print("")
    ax3 = fig.add_subplot(313)    
    plotOpt['title'] = "Model ratio " + " " + " ZM " + dateYearMonth
    plotZM (zmGeosCtm/zmFile2, file2Object.lat[:], \
                file2Object.lev[:], fig, ax3, 'nipy_spectral', \
                0.0, 1.5, plotOpt)



FILE = "f"
if FILE == "f":
    plt.savefig ("plots/" + fieldToCompare + "." + \
                     otherFieldToCompare + fileTitle \
                     + "ZM.", bbox_inches='tight')
else:
    plt.show()
plt.clf


