#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         April 12 2019
#
# DESCRIPTION:
# Driver to plot zonal mean differences for one field between 2 GEOS files
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

NUM_ARGS = 6
def usage ():
    print("")
    print("usage: PlotField_ZonalMean.py [-c] [-g] [-r] [-d] [-f] [-m]")
    print("-c File1 (GEOS)")
    print("-g File2 (GEOS")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-f field to compare")
    print("-m model configuration (Replay, CCM, etc.)") 
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
    ax1.set_ylabel("levels")
    ax1.set_yscale('log')
    ax1.set_ylim(y.max(), y.min())
    #ax1.set_ylim(y.min(), y.max())
    subs = [1,2,5]
    
    print("y_max, y_min = ", y.max(), y.min())
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
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:m:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geos5File = optList[0][1]
file2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
modelConfig = optList[5][1]

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geos5File):
    print("The GEOS file you provided does not exist: ", geos5File)
    sys.exit(0)

if not os.path.exists (file2):
    print("The GEOS file you provided does not exist: ", file2)
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)


print(geos5File)
print(file2)

file2Flag = "GMI"


geos5SimName = geos5File.split(".")[0]

sim2Name = file2.split(".")[0]
plotTitleFile2 = modelConfig 
fileTitle = "." + modelConfig + ".inter."



plotTitleFile2 = plotTitleFile2 + " " + sim2Name 


print("")
print("geos5SimName1: ", geos5SimName)
print("geos5SimName2: ", sim2Name)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------



print("")
print("Reading: ", geos5File)
print("")
geos5Object = GeosCtmPlotTools (geos5File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


print("")
print("Reading: ", file2)
print("")
file2Object = GeosCtmPlotTools (file2, 'lat','lon',\
                                    'lev','time', 'lat', \
                                    'lon', 'lev', 'time' )



list1 = file2Object.fieldList
list2 = geos5Object.fieldList

if len(geos5Object.fieldList) >= len(file2Object.fieldList):
    list1 = geos5Object.fieldList
    list2 = file2Object.fieldList
            
file2Object.fieldName = fieldToCompare

fieldsToCompareAll = file2Object.returnFieldsInCommonNew (list1, list2)


fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" :
        fieldsToCompare.append(field)

print("")
print("Fields to compare: ", fieldsToCompare[:])
print("")



foundField = False
print("")
for fieldInList in fieldsToCompare[:]:

    if fieldToCompare.lower() == fieldInList.lower():
        print("Success: ", fieldToCompare, " can be compared!")
        foundField = True

if foundField == False:
    print("ERROR: ", fieldToCompare, " cannot be compared!")
    sys.exit(-1)


# Arrays (one time record, one field)
print("")
print("Processing: ", fieldToCompare)
print("Level size: ", file2Object.levelSize)
print("")



field = fieldToCompare

geos5FieldArray = geos5Object.returnField (field, timeRecord)

file2FieldArray = file2Object.returnField (field, timeRecord)

print("")
print("shapes of arrays: ", geos5FieldArray.shape, file2FieldArray.shape)
print("")




print("")
print("File2 is assumed to be in GEOS format. Will not remap longitude coordinate")
print("")
    

print("")
print("min/max of geos1: ", geos5FieldArray.min(), geos5FieldArray.max())
print("min/max of geos2: ", file2FieldArray.min(), file2FieldArray.max())
print("")


if file2FieldArray.shape != geos5FieldArray.shape:
    print("Array shapes are different. Interpolation needed!")
    sys.exit(0)
    


print("")
print("lev2: ", end=' ') 
print(file2Object.lev[:])
print("")



# find tropMaxLev and tropMinLev
tropMinLev = findLevelFromArray (file2Object.lev, 100.00)

print("")
print("Trop min level: ", tropMinLev)
print("")

print("")
print("Trop levels: ",  file2Object.lev[0:tropMinLev+1])
print("Strat levels: '", file2Object.lev[tropMinLev::])
print("")


geos5Surface = 0
geos5TropPause = tropMinLev + 1

print("")
print("GEOS surface and tropopause levels: ", geos5Surface, geos5TropPause)
print("")




tropGeosCtm = geos5FieldArray[0:geos5TropPause, :,:]
zmGeosCtmTrop = numpy.mean (tropGeosCtm[:,:,:], axis=2)

print("")
print("size of tropGeosCtm1: ", tropGeosCtm.shape)


tropFile2 = file2FieldArray[0:geos5TropPause, :, :]
zmFile2Trop = numpy.mean (tropFile2[:, :, :], axis=2)


print("") 
print("Size, max, min of Trop ZM GEOS1: ", \
    zmGeosCtmTrop.shape, zmGeosCtmTrop.max(), zmGeosCtmTrop.min())
print("Size, max, min of Trop ZM GEOS2: ", \
    zmFile2Trop.shape, zmFile2Trop.max(), zmFile2Trop.min())
print("")




minValueOfBoth = zmGeosCtmTrop.min()
maxValueOfBoth = zmGeosCtmTrop.max()

if zmFile2Trop.min() < minValueOfBoth:
    minValueOfBoth = zmFile2Trop.min()
if zmFile2Trop.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2Trop.max()

print("")
print("min/max of both data sets: ", minValueOfBoth, "/", maxValueOfBoth)
print("")




if file2Object.lev[0] == 0:
    useLevels = file2Object.lev[:] + 1
else:
    useLevels = file2Object.lev[:]


print("")
print("GEOS surface and tropopause levels: ", geos5Surface, geos5TropPause)
print(useLevels[0:geos5TropPause])
print("")

print("")
levelsSize = size(useLevels[0:geos5TropPause])
print("size of useLevels: ", levelsSize)
#useLevels = arange(1,levelsSize+1)
print(useLevels)
print("")


print("size of zmGeosCtmTrop: ", zmGeosCtmTrop.shape)
print(useLevels[0:geos5TropPause].size)
print("size of lat: ", geos5Object.lat.size)
print("")



fig = plt.figure(figsize=(20,20))

plotOpt = {}

ax1 = fig.add_subplot(311)
plotOpt['title'] = "Trop " + modelConfig + " " + geos5SimName \
    + " " + field + " ZM " + dateYearMonth


plotZM (zmGeosCtmTrop, geos5Object.lat[:], \
            useLevels[0:geos5TropPause], \
            fig, ax1, 'jet', \
            #minValueOfBoth, maxValueOfBoth, \
            zmGeosCtmTrop.min(), zmGeosCtmTrop.max(), \
            plotOpt)


ax2 = fig.add_subplot(312)
plotOpt['title'] = "Trop " + plotTitleFile2 + " " + field + " ZM " + dateYearMonth
plotZM (zmFile2Trop, file2Object.lat[:], \
            useLevels[0:geos5TropPause], \
            fig, ax2, 'jet', \
            #minValueOfBoth, maxValueOfBoth, \
            zmFile2Trop.min(), zmFile2Trop.max(), \
            plotOpt)


tropRatio = zmGeosCtmTrop[:,:]/zmFile2Trop[:,:]

print("")
print("tropRatio min/max: ", tropRatio.min(), tropRatio.max())
print("")


ax3 = fig.add_subplot(313)    
plotOpt['title'] = "Trop model ratio         " + \
    field + " " + " ZM " + dateYearMonth
plotZM (tropRatio, file2Object.lat[:], \
            #useLevels, \
            useLevels[0:geos5TropPause], \
            fig, ax3, 'bwr', \
            0.9, 1.1, plotOpt)


FILE = "f"
if FILE == "f":
    plt.savefig ("plots/" + field + fileTitle \
                     + "trop.", bbox_inches='tight')


else:
    plt.show()
plt.clf


sys.exit(0)

if file2Flag == "GMI": 
    # lev, lat, long
    zmFile2Strat = numpy.mean (newFile2Array[tropMinLev::,:,:], axis=2)
    stratFile2 = newFile2Array[tropMinLev::,:,:]
else:
    zmFile2Strat = numpy.mean (newFile2Array[0:geos5TropPause+1, :, :] ,\
                                     axis=2)
    stratFile2 = newFile2Array[0:geos5TropPause+1, :, :]

zmGeosCtmStrat = numpy.mean (geos5FieldArray[0:geos5TropPause+1, :, :], \
                                 axis=2)
stratGeosCtm = geos5FieldArray[0:geos5TropPause+1, :, :]





#########



# flip the array to the same orientation as FILE2
if file2Flag == "GMI":
    zmGeosCtmStratRev = zmGeosCtmStrat[::-1, :]
else:
    zmGeosCtmStratRev = zmGeosCtmStrat[:,:]





minValueOfBoth = zmGeosCtmStratRev.min()
maxValueOfBoth = zmGeosCtmStratRev.max()

if zmFile2Strat.min() < minValueOfBoth:
    minValueOfBoth = zmFile2Strat.min()
if zmFile2Strat.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2Strat.max()


print("Strat min / max of ", field, minValueOfBoth, " / ", maxValueOfBoth)
print("Strat min / max of GEOS ", field, zmGeosCtmStratRev.min(), " / ", zmGeosCtmStratRev.max())
print("Strat min / max of File2 ", field, zmFile2Strat.min(), " / ", zmFile2Strat.max())


fig = plt.figure(figsize=(20,20))
plotOpt = {}
ax1 = fig.add_subplot(311)
plotOpt['title'] = "Strat " + modelConfig + modelConfig + " " + geos5SimName + "         " + variableExtractField + \
    "_" + field + " ZM " + dateYearMonth
plotZM (zmGeosCtmStratRev, geos5Object.lat[:], \
            useLevels[tropMinLev::], \
            #file2Object.lev[tropMinLev::], \
            fig, ax1, 'jet', \
            minValueOfBoth, maxValueOfBoth, plotOpt)
#    	    zmGeosCtmStratRev.min(), zmGeosCtmStratRev.max(), plotOpt)
    
ax2 = fig.add_subplot(312)
plotOpt['title'] = "Strat " + plotTitleFile2 + "_" + field + " ZM " + dateYearMonth
plotZM (zmFile2Strat, file2Object.lat[:], \
            useLevels[tropMinLev::], \
            #file2Object.lev[tropMinLev::], \
            fig, ax2, 'jet', \
            minValueOfBoth, maxValueOfBoth, plotOpt)
#            zmFile2Strat.min(), zmFile2Strat.max(), plotOpt)
ax3 = fig.add_subplot(313)    
plotOpt['title'] = "Strat model ratio         " + variableExtractField + "_" + \
    field + " " + " ZM " + dateYearMonth

zmStratRatio = zmGeosCtmStratRev/zmFile2Strat
print("Min / max of ", field, " ratios ", zmStratRatio.min(), " / " , zmStratRatio.max())
plotZM (zmStratRatio, file2Object.lat[:], \
#            file2Object.lev[tropMinLev::], \
            useLevels[tropMinLev::], \
            fig, ax3, 'nipy_spectral', \
            0.0, 1.5, plotOpt)
        #zmStratRatio.min(), zmStratRatio.max(), plotOpt)

FILE = "f"
if FILE == "f":
    if variableExtractField != "":
        plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
                         + "strat.", bbox_inches='tight')
    else:
        plt.savefig ("plots/" + field + fileTitle \
                         + "strat.", bbox_inches='tight')
        
else:
    plt.show()
plt.clf





# This section is for tropCol and stratCol plots only
# Only certain species/fields need this 


#O3, NO2, and CH2O
if fieldToCompare.lower() == "moistq" or \
        fieldToCompare.lower() == "o3" or \
        fieldToCompare.lower() == "no2" or \
        fieldToCompare.lower() == "ch2o":


    # These are for 2D slices (lat/lon) only! 
    print("")
    print("Creating GEOS plot objects...")
    geos5Object.createPlotObjects()
    print("Creating File2 plot objects...")
    file2Object.createPlotObjects()
    print("")





    print("")
    print("")
    print("")
    print("Shape of GEOS troposphere: ", shape(tropGeosCtm))
    tropColGeosCtm = numpy.sum(tropGeosCtm[:,:,:], axis=0)
    print("Shape of tropCol GEOS troposphere: ", shape (tropColGeosCtm))
    print("") 


    print("")
    print("Shape of File2 troposphere: ", shape(tropFile2))
    tropColFile2 = numpy.sum(tropFile2[:,:,:], axis=0)
    print("Shape of tropCol file2 : ", shape(tropColFile2))
    print("")



    minValueOfBoth = tropColGeosCtm.min()
    maxValueOfBoth = tropColGeosCtm.max()

    if tropColFile2.min() < minValueOfBoth:
        minValueOfBoth = tropColFile2.min()
    if tropColFile2.max() > maxValueOfBoth:
        maxValueOfBoth = tropColFile2.max()

    print("")
    print("Trop Column min/max value of both: ", minValueOfBoth, "/", maxValueOfBoth)
    print("")




    fig = plt.figure(figsize=(20,20))

    plotOpt = {}
    ax1 = fig.add_subplot(311)
    plotTitle = "Trop Column " + modelConfig + " " + geos5SimName + "         " \
        + variableExtractField + \
        "_" + field + " " + dateYearMonth
    geos5Object.create2dSlice2 (tropColGeosCtm, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      311, plotTitle, "jet")

    ax2 = fig.add_subplot(312)
    plotTitle = "Trop Column  " + sim2Name + "         " + variableExtractField + "_" \
        + field + " " + dateYearMonth
    geos5Object.create2dSlice2 (tropColFile2, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      312, plotTitle, "jet")
                            

    tropColDiff = tropColGeosCtm / tropColFile2
    for lat in range(0, size(geos5Object.lat)):
        for int in range(0, size(geos5Object.long)):

            if tropColGeosCtm[lat, int] == 0 and tropColFile2[lat, int] == 0:
                #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
                tropColDiff[lat, int] = 1.0


    ax3 = fig.add_subplot(313)  
    plotTitle = "Trop Column model ratio for         " + variableExtractField + "_" + \
        field + " " + dateYearMonth  
    geos5Object.create2dSlice2(tropColDiff, \
                                     [0, 1.5], \
                                     313, plotTitle, "nipy_spectral", \
                                     normalize=True)
                                 


    FILE = "f"
    if FILE == "f":
        plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
                         + "tropColumn.", bbox_inches='tight')
    else:
        plt.show()
    plt.clf







    print("")


    print("")
    print("Shape of GEOS stratosphere: ", shape(stratGeosCtm))
    stratColGeosCtm = numpy.sum(stratGeosCtm[:,:,:], axis=0)
    print("Shape of stratCol GEOS: ", shape(stratColGeosCtm))
    print("")


    print("")
    print("Shape of File2 stratesphere: ", shape(stratFile2))
    stratColFile2 = numpy.sum(stratFile2[:,:,:], axis=0)
    print("Shape of stratCol file2: ", shape(stratColFile2))
    print("")


    print("")
    print("")




    minValueOfBoth = stratColGeosCtm.min()
    maxValueOfBoth = stratColGeosCtm.max()

    if stratColFile2.min() < minValueOfBoth:
        minValueOfBoth = stratColFile2.min()
    if stratColFile2.max() > maxValueOfBoth:
        maxValueOfBoth = stratColFile2.max()

    print("")
    print("Strat Column  min/max value of both: ", minValueOfBoth, "/", maxValueOfBoth)
    print("")


    fig = plt.figure(figsize=(20,20))

    plotOpt = {}
    ax1 = fig.add_subplot(311)
    plotTitle = "Strat Column " + modelConfig + " " + geos5SimName + "         " + \
        variableExtractField + "_" + field + " " + dateYearMonth
    geos5Object.create2dSlice2 (stratColGeosCtm, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      311, plotTitle, "jet")

    ax2 = fig.add_subplot(312)
    plotTitle = "Strat Column " + sim2Name + "         " + variableExtractField + "_" \
        + field + " " + dateYearMonth
    geos5Object.create2dSlice2 (stratColFile2, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      312, plotTitle, "jet")
                            
    stratColDiff = stratColGeosCtm / stratColFile2
    for lat in range(0, size(geos5Object.lat)):
        for int in range(0, size(geos5Object.long)):

            if stratColGeosCtm[lat, int] == 0 and stratColFile2[lat, int] == 0:
                #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
                stratColDiff[lat, int] = 1.0

    ax3 = fig.add_subplot(313)    
    plotTitle = "Strat Column model ratio for         " + variableExtractField + "_" + \
        field + " " + dateYearMonth
    geos5Object.create2dSlice2(stratColDiff, \
                                     [0, 1.5], \
                                     313, plotTitle, "nipy_spectral", \
                                     normalize=True)



    FILE = "f"
    if FILE == "f":
        if variableExtractField != "":
            plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
                             + "stratColumn.", bbox_inches='tight')
        else:
            plt.savefig ("plots/" + field + fileTitle \
                             + "stratColumn.", bbox_inches='tight')
            
    else:
        plt.show()
    plt.clf

    print("")
    print("Finished plotting strat/trop columns for : ", fieldToCompare, " to plots/ directory")
    print("")


else:
    print(fieldToCompare, " is not currently set for strat or trop column plotting!")


print("")
print("Finished plotting: ", fieldToCompare, " to plots/ directory")
print("")
    

