#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 18 2019
#
# DESCRIPTION:
# Driver to plot zonal mean differences for one field between GEOS files
# On pressure levels. (not eta / terrain following)
#------------------------------------------------------------------------------

from __future__ import division

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

NUM_ARGS = 8
def usage ():
    print ""
    print "usage: PlotField_ZonalMeanPrs.py [-c] [-g] [-r] [-d] [-f] [-m] [-a] [-p]"
    print "-c File1 (GEOS)"
    print "-g File2 (GEOS)"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print "-f field to compare"
    print "-m model configuration (Replay, CCM, etc.)" 
    print "-a analysis type (d=perc diff, r=ratio, s=simple difference"
    print "-p pressure level to plot to"
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


def plotZM(data, x, y, fig, ax1, colorMap, dataMin, dataMax, xAxisLabel, numLevs, \
               diffFormatter=None, plotOpt=None):
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

    # determine contour levels to be used; default: linear spacing
    clevs = plotOpt.get('levels', numpy.linspace(dataMin, dataMax, numLevs))

    print ("clevs:", clevs)


    # map contour values to colors
    norm=colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    print "data min/ max: ", dataMin,  " / " , dataMax

    # draw the (filled) contours
    contour = ax1.contourf(x, y, pdata, levels=clevs, norm=norm, cmap=colorMap, \
                               vmin = dataMin, vmax = dataMax, extend='both')

    # add a title
    title = plotOpt.get('title',  'Zonal Mean')
    ax1.set_title(title)   # optional keyword: fontsize="small"

    # add colorbar
    # Note: use of the ticks keyword forces colorbar to draw all labels
    fmt = ticker.FormatStrFormatter(diffFormatter)
    cbar = fig.colorbar(contour, ax=ax1, orientation='horizontal', shrink=0.8, \
                        format=fmt)

    cbar.set_label(plotOpt.get('units', ''))
    for t in cbar.ax.get_xticklabels():
        t.set_fontsize("x-small")



    # change font size of x labels
    xlabels = ax1.get_xticklabels()
    for t in xlabels:
        t.set_fontsize("x-small")



    # set up x axis
    xsubs = [-90,-45, 0, 45, 90]
    loc = ticker.LogLocator(base=10., subs=xsubs)
    ax1.xaxis.set_major_locator(loc)
    ax1.set_xlabel(xAxisLabel)


    # set up y axes: log pressure labels on the left y axis
    ax1.set_ylabel("hPa")
    ax1.set_ylim(y.max(), y.min())
    subs = [1,2,5]
    ax1.set_yscale('log')
    print "y_max, y_min = ", y.max(), y.min()
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
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:m:a:p:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

file1 = optList[0][1]
file2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
modelConfig = optList[5][1]
analysisType = str(optList[6][1])
pressureLevelTop = optList[7][1]

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (file1) or not os.path.exists (file2):
    print ("One of the files you provided did not exist!")
    sys.exit(0)

if int(timeRecord) > 30: 
    print "WARNING: time record is more than a typical daily file!"

if int(timeRecord) < 0: 
    print "ERROR: time record needs to be positive!"
    sys.exit(0)

if len(dateYearMonth) != 6:
    print "ERROR date must be in the format YYYYMM. Received: ", dateYearMonth
    sys.exit(0)

if analysisType != "r" and analysisType != "d" and analysisType != "s":
    print "ERROR: analysis type must be r (ratios) or d (percent differences)"
    sys.exit(0)


file1SimName = file1.split(".")[0] 
file2SimName = file2.split(".")[0]

if modelConfig != '':
    plotTitleFile1 = modelConfig 
    plotTitleFile2 = modelConfig 
    fileTitle = "." + modelConfig + ".inter."
else:
    plotTitleFile1 = ".inter."
    plotTitleFile2 = ".inter."
    fileTitle = ".inter."



#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------
file1Object = GeosCtmPlotTools (file1, 'lat','lon',\
                                    'lev','time', 'lat', \
                                    'lon', 'lev', 'time' )


file2Object = GeosCtmPlotTools (file2, 'lat','lon',\
                                    'lev','time', 'lat', \
                                    'lon', 'lev', 'time' )


genericPlotTools = GenericModelPlotTools (file1, 'lat','lon',\
                                              'lev','time', 'lat', \
                                              'lon', 'lev', 'time' )



print ("")
print ("Pressure level top: ", pressureLevelTop)
print ("")


levelsFile1 = file1Object.lev[:]
print ("")
print ("Number of vertical levels in file: ", len(levelsFile1))
print ("")
 

foundPressureTop = False
pressureTopIndex = None
levCount = 0

print ("")
print ("Looking for: ", pressureLevelTop)
print ("")

for lev in levelsFile1[:]:

    print (lev, "=?", pressureLevelTop)

    if float(lev) == float(pressureLevelTop) or foundPressureTop == True:

        if foundPressureTop == False:
            print ("")
            print ("Start index of levels to plot: ", levCount)
            print ("")
            pressureTopIndex = levCount
            foundPressureTop = True
            break
                       
    levCount = levCount + 1



if foundPressureTop == False:
    print ("")
    print ("Error: pressure top specified was not found in level array!")
    print ("")
    sys.exit(0)

numLevelsToPlot = size(levelsFile1) - pressureTopIndex

print ("")
print ("Pressure top index: ", pressureTopIndex)
print ("Num levels to plot: ", numLevelsToPlot)
print ("")


pressuresToPlot = numpy.zeros(numLevelsToPlot)
levCount = 0
for lev in levelsFile1[pressureTopIndex:]:
    pressuresToPlot[levCount] = lev
    levCount+=1


print ("")
print ("pressures to plot: ", pressuresToPlot[:])
print ("")






list1 = file1Object.fieldList
list2 = file2Object.fieldList


fieldsToCompare = file2Object.returnFieldsInCommonNew (list1, list2)

print ("")
print ("Fields in common to both files: ", fieldsToCompare[:])
print ("")



foundField = False
print ""
for fieldInList in fieldsToCompare[:]:

    if fieldToCompare.lower() == fieldInList.lower():
        print "Success: ", fieldToCompare, " can be compared!"
        foundField = True

if foundField == False:
    print "ERROR: ", fieldToCompare, " cannot be compared!"
    sys.exit(-1)



# Arrays (one time record, one field)

# file2 has the potential to have a different lognitude system 
longRecords = numpy.zeros(file2Object.longSize, numpy.float32)
remappedFile2Array = numpy.zeros((file2Object.levelSize, \
                                    file2Object.latSize, \
                                    file2Object.longSize), numpy.float32)
file2FieldArray = numpy.zeros((file2Object.levelSize, \
                                   file2Object.latSize, \
                                   file1Object.longSize), numpy.float32)


print ("")
print ("Processing: ", fieldToCompare)
print ("")



field = fieldToCompare


file1FieldArray = file1Object.returnField (field, timeRecord)
file2FieldArray = file2Object.returnField (field, timeRecord)


print ("")
print ("Shapes of arrays: ", file1FieldArray.shape, file2FieldArray.shape)
print ("")

if (file1FieldArray.shape == file2FieldArray.shape) != True:
    print ("Error: field shapes are not the same")
    sys.exit(0)



zmFile1 = numpy.mean (file1FieldArray[:, :, :], axis=2)
zmFile2 = numpy.mean (file2FieldArray[:, :, :], axis=2)


minValueOfBoth = zmFile1.min()
maxValueOfBoth = zmFile1.max()

if zmFile2.min() < minValueOfBoth:
    minValueOfBoth = zmFile2.min()
if zmFile2.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2.max()


print ("")
print ("Min/max values of the two fields: ", minValueOfBoth, maxValueOfBoth)
print ("")





# Figure contains all the plot eleements. Top Level.
fig = plt.figure(figsize=(20,20))
plotOpt = {}










# Figure to contain plot of file1 field
ax1 = fig.add_subplot(311) # 3 rows, 1 colummn, position 1

plotOpt['title'] = modelConfig + " " + file1SimName \
    + " " + field + " ZM " + dateYearMonth

print zmFile1.shape
print pressuresToPlot
print type(pressuresToPlot), type(levelsFile1)

plotZM (zmFile1[pressureTopIndex:,:], file1Object.lat[:], \
            pressuresToPlot[:], \
            fig, ax1, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            "latitude", 100, "%.3f", plotOpt)







# Figure to contain plot of file2 field
ax2 = fig.add_subplot(312) # 3 rows, 1 colummn, position 2
plotOpt['title'] = modelConfig + " " + file2SimName \
    + " " + field + " ZM " + dateYearMonth


plotZM (zmFile2[pressureTopIndex:,:], file1Object.lat[:], \
            pressuresToPlot[:], \
            fig, ax2, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            "latitude", 100, "%.3f", plotOpt)









#Figure to contain plot of differences or ratios
ax3 = fig.add_subplot(313) #  3 rows, 1 colummn, position 3  



# Generic array to contain differences 
zmDiff = numpy.zeros((numLevelsToPlot, zmFile1.shape[1]), numpy.float32)

lowEnd, highEnd, zmDiff = genericPlotTools.doDifferenceAnalysis (zmFile1[pressureTopIndex:,:], zmFile2[pressureTopIndex:,:], \
                                                                     analysisType, zmDiff)
zmDiffArray = zmDiff

if analysisType == "d":
    plotOpt['title'] = "Percent Difference " + file1SimName + " vs " + file2SimName + "   " + \
        field + " " + " ZM " + dateYearMonth

    print ("")
    print ("Low / high ends for percent difference: ", lowEnd, highEnd)
    print ("")
    
    if lowEnd == 0.0:
        print ("")
        print ("Low end for percent difference is 0!")
        print ("")
        colorMap = 'Reds'
    elif highEnd == 0.0:
        print ("")
        print ("High end for percent difference is 0!")
        print ("")
        colorMap = 'Blues'
    else:
        if abs(highEnd) > abs(lowEnd):
            lowEnd = -highEnd
        else:
            highEnd = abs(lowEnd)
        colorMap = "bwr"


    plotZM (zmDiffArray, file1Object.lat[:], \
                pressuresToPlot[:], \
                fig, ax3, colorMap, \
                lowEnd, highEnd, \
                "latitude", 100, "%.0f", plotOpt)

elif analysisType == "s":
    plotOpt['title'] = "Absolute Difference " + file1SimName + " vs " + file2SimName + "   " + \
        field + " " + " ZM " + dateYearMonth
    plotZM (zmDiffArray, file1Object.lat[:], \
                pressuresToPlot[:], \
                fig, ax3, 'Spectral', \
                lowEnd, highEnd, \
                "latitude", 100, "%.0f", plotOpt)

elif analysisType == "r":
    plotOpt['title'] = "Ratios " + file1SimName + " vs " + file2SimName + "   " + \
        field + " " + " ZM " + dateYearMonth
    plotZM (zmDiffArray, file1Object.lat[:], \
                pressuresToPlot[:], fig, ax3, \
                "Spectral", \
                .5, 1.5, \
                "latitude", 50, "%.2f", plotOpt)
    
FILE = "f"
if FILE == "f":
    plt.savefig ("plots/" + field + "." + dateYearMonth + fileTitle \
                     + analysisType + ".ZonalMean.", bbox_inches='tight')
else:
    plt.show()
plt.clf



print ""
print "Finished plotting: ", fieldToCompare, " to plots/ directory"
print "Zonal mean diff min/max/mean: ", zmDiffArray.min(), "/", zmDiffArray.max(), "/", zmDiff.mean()
print ""
    

