#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         September 20 2017
#
# DESCRIPTION:
# Driver to plot zonal mean differences for one field between:
# 1. A GEOS file
# 2. A GEOS file or GMI file
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

NUM_ARGS = 8
def usage ():
    print("")
    print("usage: PlotField_ZonalMean.py [-c] [-g] [-r] [-d] [-f] [-v] [-m] [-a]")
    print("-c File1 (GEOS)")
    print("-g File2 (GMI  or GEOS) [if GMI format is gmi*.nc]")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-f field to compare")
    print("-v which variable to extract field from")
    print("-m model configuration (Replay, CCM, etc.)") 
    print("-a analysis type (d=perc diff, r=ratio, s=simple difference")
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


def plotZM(data, x, y, fig, ax1, colorMap, dataMin, dataMax, xAxisLabel, plotOpt=None):
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

    print(("clevs:", clevs))

    # map contour values to colors
    norm=colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    #print "data min/ max: ", dataMin,  " / " , dataMax

    # draw the (filled) contours
    contour = ax1.contourf(x, y, pdata, levels=clevs, norm=norm, cmap=colorMap, \
                               vmin = dataMin, vmax = dataMax, extend='both')

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
    ax1.set_ylabel("hPa")
    ax1.set_yscale('log')
    ax1.set_ylim(y.max(), y.min())
    #ax1.set_ylim(y.min(), y.max())
    subs = [1,2,5]

    ax1.set_xlabel(xAxisLabel)
    
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
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:v:m:a:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geos5File = optList[0][1]
file2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
variableExtractField = optList[5][1]
modelConfig = optList[6][1]
analType = str(optList[7][1])

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geos5File):
    print("The GEOS file you provided does not exist: ", geos5File)
    sys.exit(0)

if not os.path.exists (file2):
    print("The GEOS or GMI file you provided does not exist: ", file2)
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

if analType != "r" and analType != "d" and analType != "s":
    print("ERROR: analysis type must be r (ratios) or d (percent differences)")
    sys.exit(0)

print(geos5File)
print(file2)


if variableExtractField == "None": 
    variableExtractField = ''

file2Flag = "GMI"

# known GMI prefixes
if (file2[0:3] == "gmi" or file2[0:3] == "gmp") and file2[-3:] == ".nc":
    print("File2 is GMI")
else:
    print("File2 is GEOS")
    file2Flag = "GEOS"


geos5SimName = geos5File.split(".")[0] + "-" + geos5File.split(".")[1]

if file2Flag == "GMI": 
    sim2Name = file2.split("_")[1]
    plotTitleFile2 = "GMI " 
    fileTitle = "." + modelConfig + ".GMI."
else :
    sim2Name = file2.split(".")[0] + "-" + file2.split(".")[1]
    plotTitleFile2 = modelConfig 
    fileTitle = "." + modelConfig + ".inter."



plotTitleFile2 = plotTitleFile2 + " " + sim2Name + "        " + variableExtractField


print("")
print("geos5SimName: ", geos5SimName)
print("sim2Name: ", sim2Name)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geos5Object = GeosCtmPlotTools (geos5File, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )




if file2Flag == "GMI":
    order = "GMI"
    file2Object = GmiPlotTools (file2, 'latitude_dim', 'longitude_dim', \
                                  'eta_dim', 'rec_dim', 'latitude_dim', \
                                  'longitude_dim', 'eta_dim', 'hdr', 'const_labels')

else:
    order = "GEOS"
    file2Object = GeosCtmPlotTools (file2, 'lat','lon',\
                                        'lev','time', 'lat', \
                                        'lon', 'lev', 'time' )



if file2Object.lev[0] == 0:
    useLevels = file2Object.lev[:] + 1
else:
    useLevels = file2Object.lev[:]


count = 0 
for level in useLevels[:]:
    print(level)
    if int(level) == 100:
        print("Found 100 mb! ", count)
    count = count + 1


tropLevels = useLevels [37::]

print("")
print("trop levels: ")
print(tropLevels[:])
print("")



list1 = file2Object.fieldList
list2 = geos5Object.fieldList

if len(geos5Object.fieldList) >= len(file2Object.fieldList):
    list1 = geos5Object.fieldList
    list2 = file2Object.fieldList
    order = "GEOS"
    
        

if variableExtractField != "":
    file2Object.fieldName = variableExtractField
else:
    file2Object.fileName = fieldToCompare

fieldsToCompareAll = file2Object.returnFieldsInCommonNew (list1, list2)


fieldsToCompare = []
for field in fieldsToCompareAll[:]:
#    if field[0:4] != "Var_" and field[0:2] != "EM" and \
    if field[0:4] != "Var_" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)

print("")
print("Order: ", order)
print("")

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


#print ""
#print "Fields to compare: ", fieldsToCompare[:]
#print ""




# Arrays (one time record, one species or field)

# file2 has the potential to have a different lognitude system and length 
# This is because GMI is on a 0-360 system
longRecords = numpy.zeros(file2Object.longSize, numpy.float32)

remappedFile2Array = numpy.zeros((file2Object.levelSize, \
                                    file2Object.latSize, \
                                    file2Object.longSize), numpy.float32)

newFile2Array = numpy.zeros((file2Object.levelSize, \
                               file2Object.latSize, \
                               geos5Object.longSize), numpy.float32)

file2ZonalArray = numpy.zeros ((file2Object.levelSize, \
                                  file2Object.latSize), numpy.float32)

geos5ZonalArray = numpy.zeros ((geos5Object.levelSize, \
                                      geos5Object.latSize), numpy.float32)




print("")
print("Processing: ", fieldToCompare)
print("")




field = fieldToCompare

if variableExtractField == 'scav': 
    geos5FieldArray = geos5Object.returnField (field, timeRecord, "SCAV_")
else:
    geos5FieldArray = geos5Object.returnField (field, timeRecord)

file2FieldArray = file2Object.returnField (field, timeRecord, variableExtractField)

print("shapes of arrays: ", geos5FieldArray.shape, file2FieldArray.shape)



lenFile2Long = len(file2Object.long[:])
remappedLong = numpy.zeros(lenFile2Long, float32)


print("")
print(sim2Name)
print("")

print("")
print("lenFile2Long: ", lenFile2Long, int(lenFile2Long/2))
print("")

midLong = int(lenFile2Long/2)



# put GMI on -180 to 0 to 180
if file2Flag == "GMI" or sim2Name == "MERRA2_300":

    print("")
    print("File2 appears to be in GMI format. Remapping longitude coordinate")
    print("")

        
    remappedFile2Array [:,:,0:midLong] = \
        file2FieldArray[:,:,midLong:lenFile2Long]

    remappedFile2Array [:,:,midLong:lenFile2Long] = \
        file2FieldArray[:,:,0:midLong]



    remappedLong [0:midLong] = file2Object.long[midLong:lenFile2Long] - 360.0

    remappedLong [midLong:lenFile2Long] = file2Object.long[0:midLong]
        
    remappedLongPlus180 = numpy.zeros(lenFile2Long, float32)
    remappedLongPlus180[:] = remappedLong[:] + 180.0

else: 

    print("")
    print("File2 appears to be in GEOS format. Will not remap longitude coordinate")
    print("")
    
    remappedFile2Array [:,:,:] = file2FieldArray[:,:,:]
    remappedLong [:] = file2Object.long[:]




print("")
print("Remapped long: ", remappedLong[:])
print("")




if file2FieldArray.shape != geos5FieldArray.shape:

    print("")
    print("Array shapes are different. Interpolation needed!")
    print("")

    
    # Arrays (one time record at a time)
    longRecords = numpy.zeros(file2Object.longSize, numpy.float32)
    latRecords = numpy.zeros(file2Object.latSize, numpy.float32)

    newModel2Array = numpy.zeros((geos5Object.levelSize, file2Object.latSize, geos5Object.longSize), numpy.float32)
    newModel2ArrayBoth = numpy.zeros((geos5Object.levelSize, geos5Object.latSize, geos5Object.longSize), numpy.float32)


    print("")
    print(geos5Object.lev[:])
    print("")

    for modelLev in geos5Object.lev[:]:

        modelLevIndex = modelLev - 1

        print("")
        print("Interpolating data from model level: ", int(modelLev))
        print("")

        latCount = 0
        for lat in file2Object.lat[:]:
        
            # pull long records out of model 2
            longRecords[:] = remappedFile2Array[modelLevIndex, latCount, :]

            yinterp = numpy.interp(geos5Object.long[:], file2Object.long[:], longRecords)
            
            newModel2Array [modelLevIndex, latCount, :] = yinterp[:]
      
            latCount = latCount + 1

            #print ""
            #print "Model-2 min / max / shape", newModel2Array.min(), " / ", newModel2Array.max(), " / ", newModel2Array.shape
            #print ""        


        #print ""
        #print "Interpolated model 2 array min / max / shape: ", newModel2ArrayBoth.min(), " / " , newModel2ArrayBoth.max(), newModel2ArrayBoth.shape
        #print ""


        longCount = 0
        for int in geos5Object.long[:]:

            # pull lat records our of model 2
            latRecords[:] = newModel2Array[modelLevIndex,:,longCount]

            yinterp = numpy.interp(geos5Object.lat[:], file2Object.lat[:], latRecords)

            newModel2ArrayBoth [modelLevIndex, :, longCount] = yinterp[:]

            longCount = longCount + 1

        #print ""
        #print "Interpolated model 2 array min / max / shape: ", newModel2ArrayBoth.min(), " / " , newModel2ArrayBoth.max(), newModel2ArrayBoth.shape
        #print ""


    newFile2Array = None
    newFile2Array = newModel2ArrayBoth


else:
    print("Array shapes are the same. Will not interpolate")
    newFile2Array[:,:, :] = remappedFile2Array[:,:,:]



if file2Flag == "GMI": 
    zmFile2 = numpy.mean (newFile2Array[:, :, :], axis=2)
else:
    zmFile2 = numpy.mean(newFile2Array[:, :, :], axis=2)



zmGeosCtm = numpy.mean (geos5FieldArray[:, :, :], \
                                axis=2)



# flip the array to the same orientation as FILE2
if file2Flag == "GMI":
    zmGeosCtmRev = zmGeosCtm[::-1, :]
else:
    print("")
    print("No data flipping necessary")
    print("")
    zmGeosCtmRev = zmGeosCtm[:,:]




minValueOfBoth = zmGeosCtmRev.min()
maxValueOfBoth = zmGeosCtmRev.max()

if zmFile2.min() < minValueOfBoth:
    minValueOfBoth = zmFile2.min()
if zmFile2.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2.max()



fig = plt.figure(figsize=(20,20))
plotOpt = {}




numTropLevels = len(tropLevels)

print("")
print("Plotting on these levels: ", tropLevels[:])
print("") 


zmGeosCtmTrop = zmGeosCtmRev[0:len(tropLevels),:]
zmFile2Trop = zmFile2[0:len(tropLevels),:]

# minValueOfBoth = zmGeosCtmTrop.min()
# maxValueOfBoth = zmGeosCtmTrop.max()
# if zmFile2Trop.min() < minValueOfBoth:
#     minValueOfBoth = zmFile2Trop.min()
# if zmFile2Trop.max() > maxValueOfBoth:
#     maxValueOfBoth = zmFile2Trop.max()




ax1 = fig.add_subplot(311)
plotOpt['title'] = modelConfig + " " + geos5SimName + "        " + variableExtractField \
    + " " + field + " ZM " + dateYearMonth
plotZM (zmGeosCtmRev, geos5Object.lat[:], \
#plotZM (zmGeosCtmTrop, geos5Object.lat[:], \
            useLevels[:], \
#            tropLevels[:], \
            fig, ax1, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            "Model values", plotOpt)




ax2 = fig.add_subplot(312)
plotOpt['title'] = plotTitleFile2 + " " + field + " ZM " + dateYearMonth

plotZM (zmFile2, geos5Object.lat[:], \
#plotZM (zmFile2Trop, geos5Object.lat[:], \
            useLevels[:], \
#            tropLevels[:], \
            fig, ax2, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            #zmFile2.min(), zmFile2.max(), \
            "Model values", plotOpt)

ax3 = fig.add_subplot(313)    

levPoints = zmGeosCtmRev.shape[0]
latPoints = zmGeosCtmRev.shape[1]


zmDiff = numpy.zeros((geos5Object.levelSize, \
                          geos5Object.latSize), numpy.float32)
if analType == "d":

    for lev in range(0,levPoints):
        for lat in range(0,latPoints):
            absVal = abs(zmGeosCtmRev[lev,lat]-zmFile2[lev,lat])
            denVal = (zmGeosCtmRev[lev,lat]+zmFile2[lev,lat]) / 2.0
            zmDiff [lev,lat] = (absVal/denVal) * 100.



    zmDiffTrop = zmDiff[0:len(tropLevels),:]

    lowEnd = -zmDiff.mean()
    highEnd = zmDiff.mean()
    
    if zmDiff.mean() < 0.0: 
        print("")
        print("WARNING: zmDiff mean is < 0!")
        print("")

        lowEnd = zmDiff.mean()
        highEnd = -zmDiff.mean()



    print ("")
    print(("Shape of zmDiff: ", zmDiff.shape))
    print(("Shape of lat: ", len(geos5Object.lat)))
    print ("")




    plotOpt['title'] = "Percent Difference " + geos5SimName + " vs " + sim2Name + "   " + \
        field + " " + " ZM " + dateYearMonth

    plotZM (zmDiff, geos5Object.lat[:], \
#    plotZM (zmDiffTrop, geos5Object.lat[:], \
                useLevels[:], \
#                useLevelsTrop[:], \
                fig, ax3, 'PuOr', \
                lowEnd, highEnd, \
                "Perc difference %", plotOpt)



elif analType == "s":

    print("")
    print("Creating Simple Differences")
    print("")

    zmDiff = zmGeosCtmRev - zmFile2

    zmDiffTrop = zmDiff[0:len(tropLevels),:]

    lowEnd = zmDiff.min()
    highEnd = zmDiff.max()


    print("")
    print("low end / high end for simple diffs: ", lowEnd, " / ", highEnd)
    print("")

    plotOpt['title'] = "Simple Difference " + geos5SimName + " vs " + sim2Name + "   " + \
        field + " " + " ZM " + dateYearMonth


    plotZM (zmDiff, geos5Object.lat[:], \
#    plotZM (zmDiffTrop, geos5Object.lat[:], \
                useLevels[:], \
#                tropLevels[:], \
                fig, ax3, 'PuOr', \
                lowEnd, highEnd, \
                "Absolute Difference ", plotOpt)




elif analType == "r":

    zmDiff = zmGeosCtmRev/zmFile2

    print ("")
    print(("ratios min / max: ", zmDiff.min(), zmDiff.max()))
    print ("")

    for lev in range(0,levPoints):
        for lat in range(0,latPoints):
            if zmGeosCtmRev[lev,lat] == 0.0 and zmFile2[lev,lat] == 0.0:
                zmDiff[lev,lat] = 1.0
                print ("Updating to 1.0")
            if zmGeosCtmRev[lev,lat] != 0.0 and zmFile2[lev,lat] == 0.0:
                if zmGeosCtmRev[lev,lat] > 0.0: zmDiff[lev,lat] = 1.5
                if zmGeosCtmRev[lev,lat] < 0.0: zmDiff[lev,lat] = .5
                print ("Found ratio .5 away from 1!")


    plotOpt['title'] = "Ratios " + geos5SimName + " vs " + sim2Name + "   " + \
        field + " " + " ZM " + dateYearMonth

    plotZM (zmDiff, geos5Object.lat[:], \
                useLevels[:], fig, ax3, \
                "PuOr", \
                -5, 1.5, \
#                zmDiff.min(), zmDiff.max(), \
                "Model ratios", plotOpt)



else:
    print ("")
    print(("Analysis type not supported: ", analType))
    print ("")
           


FILE = "f"
if FILE == "f":
    plt.savefig ("plots/" + field + fileTitle \
                     + ".", bbox_inches='tight')
else:
    plt.show()
plt.clf



print("")
print("Finished plotting: ", fieldToCompare, " to plots/ directory")
print("Zonal mean diff min/max/mean: ", zmDiff.min(), "/", zmDiff.max(), zmDiff.mean())
print("")
    

