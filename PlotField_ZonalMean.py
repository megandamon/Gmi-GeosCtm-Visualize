#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         September 20 2017
#
# DESCRIPTION:
# Driver to plot zonal mean differences for one field between:
# 1. A GEOS-CTM file
# 2. A GEOS-CTM file or GMI file
# Driver will always plot tropCol and stratCol 
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
    print ""
    print "usage: PlotRestartSpecies_ZonalMean.py [-c] [-g] [-r] [-d] [-f] [-v]"
    print "-c File1 (GEOS-CTM)"
    print "-g File2 (GMI  or GEOS-CTM) [if GMI format is gmi*.nc]"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print "-f field to compare"
    print "-v which variable to extract field from"
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
    ax1.set_ylabel("Pressure [hPa]")
    ax1.set_yscale('log')
    ax1.set_ylim(y.max(), y.min())
    subs = [1,2,5]
    
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
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:v:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
file2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
variableExtractField = optList[5][1]

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile):
    print "The GEOS-CTM file you provided does not exist: ", geosCtmFile
    sys.exit(0)

if not os.path.exists (file2):
    print "The GEOS-CTM or GMI file you provided does not exist: ", file2
    print "GMI format must be in gmi*.nc"
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
print file2

file2Flag = "GMI"

# known GMI prefixes
if (file2[0:3] == "gmi" or file2[0:3] == "gmp") and file2[-3:] == ".nc":
    print "File2 is GMI"
else:
    print "File2 is GEOS-CTM"
    file2Flag = "GEOS"


geosCtmSimName = geosCtmFile.split(".")[0]

if file2Flag == "GMI": 
    sim2Name = file2.split("_")[1]
    plotTitleFile2 = "GMI " 
    fileTitle = ".GEOS-CTM.GMI."
else :
    sim2Name = file2.split(".")[0]
    plotTitleFile2 = "GEOS-CTM " 
    fileTitle = ".GEOS-CTM.inter."


plotTitleFile2 = plotTitleFile2 + sim2Name + "        " + variableExtractField


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




if file2Flag == "GMI":
    order = "GMI"
    file2Object = GmiPlotTools (file2, 'latitude_dim', 'longitude_dim', \
                                  'eta_dim', 'rec_dim', 'latitude_dim', \
                                  'longitude_dim', 'eta_dim', 'hdr', 'const_labels')

else:
    order = "GEOS-CTM"
    file2Object = GeosCtmPlotTools (file2, 'lat','lon',\
                                        'lev','time', 'lat', \
                                        'lon', 'lev', 'time' )




list1 = file2Object.fieldList
list2 = geosCtmObject.fieldList

if len(geosCtmObject.fieldList) >= len(file2Object.fieldList):
    list1 = geosCtmObject.fieldList
    list2 = file2Object.fieldList
    order = "GEOS-CTM"
    
        


file2Object.fieldName = variableExtractField
fieldsToCompareAll = file2Object.returnFieldsInCommon (list1, list2, order)


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


print ""
print "Fields to compare: ", fieldsToCompare[:]
print ""




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




print ""
print "Processing: ", fieldToCompare
print ""




field = fieldToCompare

if variableExtractField == 'scav': 
    geosCtmFieldArray = geosCtmObject.returnField (field, timeRecord, "SCAV_")
else:
    geosCtmFieldArray = geosCtmObject.returnField (field, timeRecord)

file2FieldArray = file2Object.returnField (field, timeRecord, variableExtractField)

print "shapes of arrays: ", geosCtmFieldArray.shape, file2FieldArray.shape



lenFile2Long = len(file2Object.long[:])
remappedLong = numpy.zeros(lenFile2Long, float32)


print ""
print sim2Name
print ""


# put GMI on -180 to 0 to 180
if file2Flag == "GMI" or sim2Name == "MERRA2_300":

    print ""
    print "File2 appears to be in GMI format. Remapping longitude coordinate"
    print ""

        
    remappedFile2Array [:,:,0:lenFile2Long/2] = \
        file2FieldArray[:,:,lenFile2Long/2:lenFile2Long]

    remappedFile2Array [:,:,lenFile2Long/2:lenFile2Long] = \
        file2FieldArray[:,:,0:lenFile2Long/2]



    remappedLong [0:lenFile2Long/2] = file2Object.long[lenFile2Long/2:lenFile2Long] - 360.0

    remappedLong [lenFile2Long/2:lenFile2Long] = file2Object.long[0:lenFile2Long/2]
        
    remappedLongPlus180 = numpy.zeros(lenFile2Long, float32)
    remappedLongPlus180[:] = remappedLong[:] + 180.0

else: 

    print ""
    print "File2 appears to be in GEOS-CTM format. Will not remap longitude coordinate"
    print ""
    
    remappedFile2Array [:,:,:] = file2FieldArray[:,:,:]
    remappedLong [:] = file2Object.long[:]




print ""
print "Remapped long: ", remappedLong[:]
print ""


if file2FieldArray.shape != geosCtmFieldArray.shape:
    print "Array shapes are different. Interpolation needed!"
    
    modelLevCount = 0

    for modelLev in geosCtmObject.lev[:]:

        latCount = 0
        for lat in file2Object.lat[:]:

            longRecords[:] = remappedFile2Array [modelLevCount, latCount,:]
                        
            yinterp =  numpy.interp(geosCtmObject.long[:], remappedLong[:], longRecords)
            
            newFile2Array[modelLevCount, latCount, :] = yinterp [:]
            
            latCount = latCount + 1

        modelLevCount = modelLevCount + 1



else:
    newFile2Array[:,:, :] = remappedFile2Array[:,:,:]



if file2Flag == "GMI":
    # find tropMaxLev and tropMinLev from GMI
    tropMinLev = findLevelFromArray (file2Object.lev, 100.00)

    print ""
    print "Trop min level: ", tropMinLev
    print ""

    print ""
    print"Trop levels: ",  file2Object.lev[0:tropMinLev+1]
    print "Strat levels: '", file2Object.lev[tropMinLev+1::]
    print ""


else:

    tropMinLev = 34
    print ""
    print "WARNING: Default tropophere min level being used : ", tropMinLev
    print ""



geosCtmSurface = geosCtmObject.levelSize-1
geosCtmTropPause = (geosCtmObject.levelSize-1) - tropMinLev


if file2Flag == "GMI": 
    # lev, lat, long
    tropFile2 = newFile2Array[0:tropMinLev+1, :, :]
    zmFile2Trop = numpy.mean (newFile2Array[0:tropMinLev+1, :, :], axis=2)
else:
    tropFile2 = newFile2Array[geosCtmTropPause:geosCtmSurface+1, :, :]
    zmFile2Trop = numpy.mean(newFile2Array[geosCtmTropPause:geosCtmSurface+1, :, :], \
                                 axis=2)



zmGeosCtmTrop = numpy.mean (geosCtmFieldArray[geosCtmTropPause:geosCtmSurface+1, :, :], \
                                axis=2)
tropGeosCtm = geosCtmFieldArray[geosCtmTropPause:geosCtmSurface+1, :,:]


# flip the array to the same orientation as FILE2
if file2Flag == "GMI":
    zmGeosCtmTropRev = zmGeosCtmTrop[::-1, :]
else:
    zmGeosCtmTropRev = zmGeosCtmTrop[:,:]

print "Size of Trop ZM GEOS: ", zmGeosCtmTrop.shape
print "Size of Top ZM file2: ", zmFile2Trop.shape

minValueOfBoth = zmGeosCtmTropRev.min()
maxValueOfBoth = zmGeosCtmTropRev.max()

if zmFile2Trop.min() < minValueOfBoth:
    minValueOfBoth = zmFile2Trop.min()
if zmFile2Trop.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2Trop.max()


fig = plt.figure(figsize=(20,20))
plotOpt = {}

ax1 = fig.add_subplot(311)
plotOpt['title'] = "Trop GEOS-CTM " + geosCtmSimName + "        " + variableExtractField \
    + " " + field + " ZM " + dateYearMonth


if file2Object.lev[0] == 0:
    useLevels = file2Object.lev[:] + 1
else:
    useLevels = file2Object.lev[:]


plotZM (zmGeosCtmTropRev, geosCtmObject.lat[:], \
            useLevels[0:tropMinLev+1], \
            #file2Object.lev[0:tropMinLev+1], \
            fig, ax1, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
#            zmGeosCtmTropRev.min(), zmGeosCtmTropRev.max(), \
            plotOpt)


ax2 = fig.add_subplot(312)
plotOpt['title'] = "Trop " + plotTitleFile2 + " " + field + " ZM " + dateYearMonth
plotZM (zmFile2Trop, file2Object.lat[:], \
            useLevels[0:tropMinLev+1], \
            #file2Object.lev[0:tropMinLev+1], \
            fig, ax2, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
#            zmFile2Trop.min(), zmFile2Trop.max(), \
            plotOpt)

ax3 = fig.add_subplot(313)    
plotOpt['title'] = "Trop model ratio         " + variableExtractField + "_" + \
    field + " " + " ZM " + dateYearMonth
plotZM (zmGeosCtmTropRev/zmFile2Trop, file2Object.lat[:], \
            #file2Object.lev[0:tropMinLev+1], \
            useLevels[0:tropMinLev+1], \
            fig, ax3, 'nipy_spectral', \
            0.0, 1.5, plotOpt)



FILE = "f"
if FILE == "f":
    plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
                     + "trop.", bbox_inches='tight')
else:
    plt.show()
plt.clf



if file2Flag == "GMI": 
    # lev, lat, long
    zmFile2Strat = numpy.mean (newFile2Array[tropMinLev::,:,:], axis=2)
    stratFile2 = newFile2Array[tropMinLev::,:,:]
else:
    zmFile2Strat = numpy.mean (newFile2Array[0:geosCtmTropPause+1, :, :] ,\
                                     axis=2)
    stratFile2 = newFile2Array[0:geosCtmTropPause+1, :, :]

zmGeosCtmStrat = numpy.mean (geosCtmFieldArray[0:geosCtmTropPause+1, :, :], \
                                 axis=2)
stratGeosCtm = geosCtmFieldArray[0:geosCtmTropPause+1, :, :]





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


print "Strat min / max of ", field, minValueOfBoth, " / ", maxValueOfBoth
print "Strat min / max of GEOS-CTM ", field, zmGeosCtmStratRev.min(), " / ", zmGeosCtmStratRev.max()
print "Strat min / max of File2 ", field, zmFile2Strat.min(), " / ", zmFile2Strat.max()


fig = plt.figure(figsize=(20,20))
plotOpt = {}
ax1 = fig.add_subplot(311)
plotOpt['title'] = "Strat GEOS-CTM " + geosCtmSimName + "         " + variableExtractField + \
    "_" + field + " ZM " + dateYearMonth
plotZM (zmGeosCtmStratRev, geosCtmObject.lat[:], \
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
print "Min / max of ", field, " ratios ", zmStratRatio.min(), " / " , zmStratRatio.max()
plotZM (zmStratRatio, file2Object.lat[:], \
#            file2Object.lev[tropMinLev::], \
            useLevels[tropMinLev::], \
            fig, ax3, 'nipy_spectral', \
            0.0, 1.5, plotOpt)
        #zmStratRatio.min(), zmStratRatio.max(), plotOpt)

FILE = "f"
if FILE == "f":
    plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
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
    print ""
    print "Creating GEOS-CTM plot objects..."
    geosCtmObject.createPlotObjects()
    print "Creating File2 plot objects..."
    file2Object.createPlotObjects()
    print ""





    print ""
    print ""
    print ""
    print "Shape of GEOS-CTM troposphere: ", shape(tropGeosCtm)
    tropColGeosCtm = numpy.sum(tropGeosCtm[:,:,:], axis=0)
    print "Shape of tropCol GEOS-CTM troposphere: ", shape (tropColGeosCtm)
    print "" 


    print ""
    print "Shape of File2 troposphere: ", shape(tropFile2)
    tropColFile2 = numpy.sum(tropFile2[:,:,:], axis=0)
    print "Shape of tropCol file2 : ", shape(tropColFile2)
    print ""



    minValueOfBoth = tropColGeosCtm.min()
    maxValueOfBoth = tropColGeosCtm.max()

    if tropColFile2.min() < minValueOfBoth:
        minValueOfBoth = tropColFile2.min()
    if tropColFile2.max() > maxValueOfBoth:
        maxValueOfBoth = tropColFile2.max()

    print ""
    print "Trop Column min/max value of both: ", minValueOfBoth, "/", maxValueOfBoth
    print ""




    fig = plt.figure(figsize=(20,20))

    plotOpt = {}
    ax1 = fig.add_subplot(311)
    plotTitle = "Trop Column GEOS-CTM " + geosCtmSimName + "         " \
        + variableExtractField + \
        "_" + field + " " + dateYearMonth
    geosCtmObject.create2dSlice2 (tropColGeosCtm, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      311, plotTitle, "jet")

    ax2 = fig.add_subplot(312)
    plotTitle = "Trop Column  " + sim2Name + "         " + variableExtractField + "_" \
        + field + " " + dateYearMonth
    geosCtmObject.create2dSlice2 (tropColFile2, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      312, plotTitle, "jet")
                            

    tropColDiff = tropColGeosCtm / tropColFile2
    for lat in range(0, size(geosCtmObject.lat)):
        for long in range(0, size(geosCtmObject.long)):

            if tropColGeosCtm[lat, long] == 0 and tropColFile2[lat, long] == 0:
                #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
                tropColDiff[lat, long] = 1.0


    ax3 = fig.add_subplot(313)  
    plotTitle = "Trop Column model ratio for         " + variableExtractField + "_" + \
        field + " " + dateYearMonth  
    geosCtmObject.create2dSlice2(tropColDiff, \
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







    print ""


    print ""
    print "Shape of GEOS-CTM stratosphere: ", shape(stratGeosCtm)
    stratColGeosCtm = numpy.sum(stratGeosCtm[:,:,:], axis=0)
    print "Shape of stratCol GEOS-CTM: ", shape(stratColGeosCtm)
    print ""


    print ""
    print "Shape of File2 stratesphere: ", shape(stratFile2)
    stratColFile2 = numpy.sum(stratFile2[:,:,:], axis=0)
    print "Shape of stratCol file2: ", shape(stratColFile2)
    print ""


    print""
    print""




    minValueOfBoth = stratColGeosCtm.min()
    maxValueOfBoth = stratColGeosCtm.max()

    if stratColFile2.min() < minValueOfBoth:
        minValueOfBoth = stratColFile2.min()
    if stratColFile2.max() > maxValueOfBoth:
        maxValueOfBoth = stratColFile2.max()

    print ""
    print "Strat Column  min/max value of both: ", minValueOfBoth, "/", maxValueOfBoth
    print ""


    fig = plt.figure(figsize=(20,20))

    plotOpt = {}
    ax1 = fig.add_subplot(311)
    plotTitle = "Strat Column GEOS-CTM " + geosCtmSimName + "         " + \
        variableExtractField + "_" + field + " " + dateYearMonth
    geosCtmObject.create2dSlice2 (stratColGeosCtm, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      311, plotTitle, "jet")

    ax2 = fig.add_subplot(312)
    plotTitle = "Strat Column " + sim2Name + "         " + variableExtractField + "_" \
        + field + " " + dateYearMonth
    geosCtmObject.create2dSlice2 (stratColFile2, \
                                      [minValueOfBoth, maxValueOfBoth], \
                                      312, plotTitle, "jet")
                            
    stratColDiff = stratColGeosCtm / stratColFile2
    for lat in range(0, size(geosCtmObject.lat)):
        for long in range(0, size(geosCtmObject.long)):

            if stratColGeosCtm[lat, long] == 0 and stratColFile2[lat, long] == 0:
                #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
                stratColDiff[lat, long] = 1.0

    ax3 = fig.add_subplot(313)    
    plotTitle = "Strat Column model ratio for         " + variableExtractField + "_" + \
        field + " " + dateYearMonth
    geosCtmObject.create2dSlice2(stratColDiff, \
                                     [0, 1.5], \
                                     313, plotTitle, "nipy_spectral", \
                                     normalize=True)



    FILE = "f"
    if FILE == "f":
        plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
                         + "stratColumn.", bbox_inches='tight')
    else:
        plt.show()
    plt.clf

    print ""
    print "Finished plotting strat/trop columns for : ", fieldToCompare, " to plots/ directory"
    print ""


else:
    print fieldToCompare, " is not currently set for strat or trop column plotting!"


print ""
print "Finished plotting: ", fieldToCompare, " to plots/ directory"
print ""
    

