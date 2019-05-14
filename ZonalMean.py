#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         March 29 2018
#
# DESCRIPTION:
# Driver to plot zonal mean differences for one field between 2 GEOS files.
# Ignores lev field and uses 1-levSize model levels.
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






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


FILE = "f"

NUM_ARGS = 7
def usage ():
    print ""
    print "usage: ZonalMean.py [-c] [-g] [-r] [-d] [-f] [-v] [-m]"
    print "-c File1 (GEOS)"
    print "-g File2 (GEOS)"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMMDD)"
    print "-f field to compare"
    print "-v which variable to extract field from"
    print "-m model configuration (Replay, CCM, etc.)"
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
    ax1.set_ylabel("Model levels")
    ax1.set_yscale('log')


    yMax = y[-1]
    yMin = y[0]

    #ax1.set_ylim(y.max(), y.min())
    ax1.set_ylim(yMax, yMin)

    subs = [1,2,5]
    subs = [1,2,3,4,5,6,7,8,9]
    
    print ""
    print "y_max, y_min = ", yMax, yMin
    print ""

    if yMax/yMin < 30.:
        print "Setting subs"
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
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:v:m:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
file2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
variableExtractField = optList[5][1]
modelConfig = optList[6][1]

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile):
    print "The GEOS file you provided does not exist: ", geosCtmFile
    sys.exit(0)

if not os.path.exists (file2):
    print "The GEOS file provided does not exist: ", file2
    sys.exit(0)

if int(timeRecord) > 30: 
    print "WARNING: time record is more than a typical daily file!"

if int(timeRecord) < 0: 
    print "ERROR: time record needs to be positive!"
    sys.exit(0)

if len(dateYearMonth) != 8:
    print "ERROR date must be in the format YYYYMMDD. Received: ", dateYearMonth
    sys.exit(0)


print geosCtmFile
print file2

geosCtmSimName = geosCtmFile.split(".")[0]


sim2Name = file2.split(".")[0]
plotTitleFile2 = "" 
fileTitle = ".GEOS.inter."


plotTitleFile2 = plotTitleFile2 + " " + modelConfig + " " + sim2Name + "        " + variableExtractField


print ""
print "geosCtmSimName: ", geosCtmSimName
print "sim2Name: ", sim2Name
print ""



#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------
geosCtmObject = GeosCtmPlotTools (geosCtmFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )




order = "GEOS"
file2Object = GeosCtmPlotTools (file2, 'lat','lon',\
                                    'lev','time', 'lat', \
                                    'lon', 'lev', 'time' )


list1 = file2Object.fieldList
list2 = geosCtmObject.fieldList

if len(geosCtmObject.fieldList) >= len(file2Object.fieldList):
    list1 = geosCtmObject.fieldList
    list2 = file2Object.fieldList
    order = "GEOS"
    
        
if variableExtractField != "":
    file2Object.fieldName = variableExtractField
else:
    file2Object.fieldName = fieldToCompare

fieldsToCompareAll = file2Object.returnFieldsInCommonNew (list1, list2)


fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_":
        fieldsToCompare.append(field)

print ""
print "Order: ", order
print ""

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





# Arrays (one time record, one species or field)

# file2 has the potential to have a different lognitude system and length 
# This is because GMI is on a 0-360 system
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




print ""
print "Processing: ", fieldToCompare
print ""


field = fieldToCompare

if variableExtractField == 'scav': 
    geosCtmFieldArray = geosCtmObject.returnField (field, timeRecord, "SCAV_")
else:
    geosCtmFieldArray = geosCtmObject.returnField (field, timeRecord)

file2FieldArray = file2Object.returnField (field, timeRecord, variableExtractField)

print ""
print "shapes of arrays: ", geosCtmFieldArray.shape, file2FieldArray.shape
print ""

print "file 2: array max/min: ", file2FieldArray.max(), file2FieldArray.min()
print""


lenFile2Long = len(file2Object.long[:])

print ""
print "File2 assumed to be in GEOS format. Will not remap longitude coordinate"
print ""
    

geosCtmSurface = geosCtmObject.levelSize

print ""
print "File1 surface:", geosCtmSurface
print ""


zmFile2 = numpy.mean(file2FieldArray[:, :, :], \
                                 axis=2)

zmGeosCtm = numpy.mean (geosCtmFieldArray[:, :, :], \
                            axis=2)

print "zm file 2: array max/min: ", zmFile2.max(), zmFile2.min()
print""




print ""
print "No data flipping necessary"
print ""
zmGeosCtmRev = zmGeosCtm[:,:]

print "Size of ZM GEOS: ", zmGeosCtm.shape
print "Size of ZM file2: ", zmFile2.shape
print ""



minValueOfBoth = zmGeosCtmRev.min()
maxValueOfBoth = zmGeosCtmRev.max()

if zmFile2.min() < minValueOfBoth:
    minValueOfBoth = zmFile2.min()
if zmFile2.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2.max()


fig = plt.figure(figsize=(20,20))
plotOpt = {}

ax1 = fig.add_subplot(311)
plotOpt['title'] = modelConfig + " " + geosCtmSimName + "        " + variableExtractField \
    + " " + field + " ZM " + dateYearMonth


print""
useLevels = range(1,geosCtmObject.lev.size+1)
print ""
print useLevels[:]

plotZM (zmGeosCtmRev, geosCtmObject.lat[:], \
            #useLevels[0:tropMinLev], \
            useLevels[:], \
            fig, ax1, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            plotOpt)


print""
useLevels = range(1,file2Object.lev.size+1)
print ""
print useLevels[:]



ax2 = fig.add_subplot(312)
plotOpt['title'] = plotTitleFile2 + " " + field + " ZM " + dateYearMonth
plotZM (zmFile2, file2Object.lat[:], \
            useLevels[:], \
            fig, ax2, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            plotOpt)


FILE = "f"
if FILE == "f":
    if variableExtractField != "":
        plt.savefig ("plots/" + variableExtractField + "_" + field + "_" + fileTitle + modelConfig  + ".", bbox_inches='tight')
    else:
        plt.savefig ("plots/" + field + fileTitle + modelConfig + ".", bbox_inches='tight')


else:
    plt.show()
plt.clf




print ""
print "Finished plotting: ", fieldToCompare, " to plots/ directory"
print ""
    

