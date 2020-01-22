#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         January 25 2019
#
# DESCRIPTION:
# Driver to plot zonal mean differences for one field between two GMI files
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
    print("usage: PlotField_GMI.py [-c] [-g] [-r] [-d] [-f] [-v]")
    print("-c File1 (GMI)")
    print("-g File2 (GMI)")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-f field to compare")
    print("-v which variable to extract field from")
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

    # determine contour levels to be used; default: linear spacing, 10 levels
    clevs = plotOpt.get('levels', numpy.linspace(dataMin, dataMax, 10))

    print("")
    print("clevs: ", clevs)
    print("")

    # map contour values to colors
    norm=colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    print("data min/ max: ", dataMin,  " / " , dataMax)

    # draw the (filled) contours
    contour = ax1.contourf(x, y, pdata, levels=clevs, norm=norm, cmap=colorMap, \
                               vmin = dataMin, vmax = dataMax)

    # add a title
    title = plotOpt.get('title',  'Zonal Mean')
    ax1.set_title(title)   # optional keyword: fontsize="small"

    # add colorbar
    # Note: use of the ticks keyword forces colorbar to draw all labels
    fmt = ticker.FormatStrFormatter("%.4g")
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
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:v:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

gmiFile1 = optList[0][1]
gmiFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
variableExtractField = optList[5][1]

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (gmiFile1):
    print("The file you provided does not exist: ", gmiFile1)
    sys.exit(0)

if not os.path.exists (gmiFile2):
    print("The file you provided does not exist: ", file2)
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)


print(gmiFile1)
print(gmiFile2)

sim1Name = gmiFile1.split("_")[1]
sim2Name = gmiFile2.split("_")[1]
plotTitleFile1 = "GMI " 
plotTitleFile2 = "GMI " 
fileTitle = ".GMI-inter."



plotTitleFile1 = plotTitleFile1 + sim1Name + "        " + variableExtractField
plotTitleFile2 = plotTitleFile2 + sim2Name + "        " + variableExtractField


print("")
print("sim1Name: ", sim1Name)
print("sim2Name: ", sim2Name)
print("")

print("")
print("plot title 1 : ", plotTitleFile1)
print("plot title 2 : ", plotTitleFile2)
print("")


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------


if "amonthly" in gmiFile1: 
    gmiTimeVar = "hdr"
else:
    gmiTimeVar = "nymd"


file1Object = GmiPlotTools (gmiFile1, 'latitude_dim', 'longitude_dim', \
                                'eta_dim', 'rec_dim', 'latitude_dim', \
                                'longitude_dim', 'eta_dim', gmiTimeVar, 'const_labels')

file2Object = GmiPlotTools (gmiFile2, 'latitude_dim', 'longitude_dim', \
                                'eta_dim', 'rec_dim', 'latitude_dim', \
                                'longitude_dim', 'eta_dim', gmiTimeVar, 'const_labels')



list1 = file1Object.fieldList
list2 = file2Object.fieldList

if len(file1Object.fieldList) >= len(file2Object.fieldList):
    list1 = file1Object.fieldList
    list2 = file2Object.fieldList
    order = "GMI1"
else: order = "GMI2"


        
if variableExtractField != "":
    file2Object.fieldName = variableExtractField
else:
    file2Object.fileName = fieldToCompare

fieldsToCompareAll = file2Object.returnFieldsInCommonNew (list1, list2)


print (fieldsToCompareAll)
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

# Arrays (one time record, one species or field)


print("")
print("Processing: ", fieldToCompare)
print("")


field = fieldToCompare


file1FieldArray = file1Object.returnField (field, timeRecord, variableExtractField)
file2FieldArray = file2Object.returnField (field, timeRecord, variableExtractField)

print("shapes of arrays: ", file1FieldArray.shape, file2FieldArray.shape)


if file2FieldArray.shape != file1FieldArray.shape:
    print("Array shapes are different. Exiting!")
    sys.exit(0)
    


# find tropMaxLev and tropMinLev
tropMinLev = findLevelFromArray (file2Object.lev, 100.00)

print("")
print("Trop min level: ", tropMinLev)
print("")

print("")
print("Trop levels: ",  file2Object.lev[0:tropMinLev+1])
print("Strat levels: '", file2Object.lev[tropMinLev+1::])
print("")



gmiSurface = file1Object.levelSize
gmiTropPause = (file1Object.levelSize) - tropMinLev

print("")
print("GMI surface and tropopause levels: ", gmiSurface, gmiTropPause)
print("")


tropFile1 = file1FieldArray[0:tropMinLev+1, :, :]
zmFile1Trop = numpy.mean (file1FieldArray[0:tropMinLev+1, :, :], axis=2)
tropFile2 = file2FieldArray[0:tropMinLev+1, :, :]
zmFile2Trop = numpy.mean (file2FieldArray[0:tropMinLev+1, :, :], axis=2)



print("")
print("Size of Top ZM file1: ", zmFile1Trop.shape)
print("Size of Top ZM file2: ", zmFile2Trop.shape)
print("")


minValueOfBoth = zmFile1Trop.min()
maxValueOfBoth = zmFile1Trop.max()

if zmFile2Trop.min() < minValueOfBoth:
    minValueOfBoth = zmFile2Trop.min()
if zmFile2Trop.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2Trop.max()



fig = plt.figure(figsize=(20,20))
plotOpt = {}

ax1 = fig.add_subplot(311)


print("")
print(file2Object.lev[0])
print("")

# if file2Object.lev[0] == 0:
#     useLevels = file2Object.lev[:] + 1
# else:

useLevels = file2Object.lev[:]


print("")
print("GMI surface and tropopause levels: ", gmiSurface, gmiTropPause)
print(useLevels[gmiTropPause:gmiSurface])
print("")

print("")
print("Shape of zmFile1Trop: ", shape(zmFile1Trop))
print("Len of file2Ojbect.lat: ", len(file1Object.lat))
print("len UseLevels: ", len(useLevels[0:tropMinLev+1]))
print("")

plotOpt['title'] = "Trop " + plotTitleFile1 + " " + field + " ZM " + dateYearMonth
plotZM (zmFile1Trop, file1Object.lat[:], \
            useLevels[0:tropMinLev+1], \
            #useLevels[gmiTropPause:gmiSurface], \
            fig, ax1, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            #            zmFile1Trop.min(), zmFile1Trop.max(), \
            plotOpt)




ax2 = fig.add_subplot(312)
plotOpt['title'] = "Trop " + plotTitleFile2 + " " + field + " ZM " + dateYearMonth
plotZM (zmFile2Trop, file2Object.lat[:], \
            useLevels[0:tropMinLev+1], \
            #useLevels[gmiTropPause:gmiSurface], \
            fig, ax2, 'jet', \
            minValueOfBoth, maxValueOfBoth, \
            #zmFile2Trop.min(), zmFile2Trop.max(), \
            plotOpt)

ax3 = fig.add_subplot(313)    
plotOpt['title'] = "Trop model ratio         " + variableExtractField + "_" + \
    field + " " + " ZM " + dateYearMonth
plotZM (zmFile1Trop/zmFile2Trop, file2Object.lat[:], \
            useLevels[0:tropMinLev+1], \
            #useLevels[gmiTropPause:gmiSurface], \
            fig, ax3, 'nipy_spectral', \
            0.9, 1.1, plotOpt)



FILE = "f"
if FILE == "f":
    if variableExtractField != "":
        plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
                         + "trop.", bbox_inches='tight')
    else:
        plt.savefig ("plots/" + field + fileTitle \
                         + "trop.", bbox_inches='tight')


else:
    plt.show()

plt.clf


zmFile1Strat = numpy.mean (file1FieldArray[tropMinLev::,:,:], axis=2)
stratFile1 = file1FieldArray[tropMinLev::,:,:]
zmFile2Strat = numpy.mean (file2FieldArray[tropMinLev::,:,:], axis=2)
stratFile2 = file2FieldArray[tropMinLev::,:,:]

minValueOfBoth = zmFile1Strat.min()
maxValueOfBoth = zmFile1Strat.max()

if zmFile2Strat.min() < minValueOfBoth:
    minValueOfBoth = zmFile2Strat.min()
if zmFile2Strat.max() > maxValueOfBoth:
    maxValueOfBoth = zmFile2Strat.max()


print("Strat min / max of ", field, minValueOfBoth, " / ", maxValueOfBoth)
print("Strat min / max of File1 ", field, zmFile1Strat.min(), " / ", zmFile1Strat.max())
print("Strat min / max of File2 ", field, zmFile2Strat.min(), " / ", zmFile2Strat.max())


fig = plt.figure(figsize=(20,20))
plotOpt = {}

ax1 = fig.add_subplot(311)

plotOpt['title'] = "Strat GMI " + sim1Name + "           " + field + " ZM " + dateYearMonth
plotZM (zmFile1Strat, file1Object.lat[:], \
            useLevels[tropMinLev::], \
            #file2Object.lev[tropMinLev::], \
            fig, ax1, 'jet', \
            minValueOfBoth, maxValueOfBoth, plotOpt)
#    	    zmFile1Strat.min(), zmFile1Strat.max(), plotOpt)
    
ax2 = fig.add_subplot(312)

plotOpt['title'] = "Strat GMI " + sim2Name + "           " + field + " ZM " + dateYearMonth
plotZM (zmFile2Strat, file2Object.lat[:], \
            useLevels[tropMinLev::], \
            #file2Object.lev[tropMinLev::], \
            fig, ax2, 'jet', \
            minValueOfBoth, maxValueOfBoth, plotOpt)
#            zmFile2Strat.min(), zmFile2Strat.max(), plotOpt)

ax3 = fig.add_subplot(313)    
plotOpt['title'] = "Strat model ratio         " + variableExtractField + "_" + \
    field + " " + " ZM " + dateYearMonth

zmStratRatio = zmFile1Strat/zmFile2Strat
print("Min / max of ", field, " ratios ", zmStratRatio.min(), " / " , zmStratRatio.max())
plotZM (zmStratRatio, file2Object.lat[:], \
#            file2Object.lev[tropMinLev::], \
            useLevels[tropMinLev::], \
            fig, ax3, 'nipy_spectral', \
            0.9, 1.1, plotOpt)
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


# #O3, NO2, and CH2O
# if fieldToCompare.lower() == "moistq" or \
#         fieldToCompare.lower() == "o3" or \
#         fieldToCompare.lower() == "no2" or \
#         fieldToCompare.lower() == "ch2o":


#     # These are for 2D slices (lat/lon) only! 
#     print("")
#     print("Creating GMI plot objects...")
#     file1Object.createPlotObjects()
#     file2Object.createPlotObjects()
#     print("")





#     print("")
#     print("")
#     print("")
#     print("Shape of GMI troposphere 1: ", shape(tropFile1))
#     tropColFile1 = numpy.sum(tropFile1[:,:,:], axis=0)
#     print("Shape of tropCol GMI troposphere 1: ", shape (tropColFile1))
#     print("") 


#     print("")
#     print("Shape of GMI troposphere 2: ", shape(tropFile2))
#     tropColFile2 = numpy.sum(tropFile2[:,:,:], axis=0)
#     print("Shape of tropCol file2 : ", shape(tropColFile2))
#     print("")



#     minValueOfBoth = tropColFile1.min()
#     maxValueOfBoth = tropColFile1.max()

#     if tropColFile2.min() < minValueOfBoth:
#         minValueOfBoth = tropColFile2.min()
#     if tropColFile2.max() > maxValueOfBoth:
#         maxValueOfBoth = tropColFile2.max()

#     print("")
#     print("Trop Column min/max value of both: ", minValueOfBoth, "/", maxValueOfBoth)
#     print("")




#     fig = plt.figure(figsize=(20,20))

#     plotOpt = {}
#     ax1 = fig.add_subplot(311)
#     plotTitle = "Trop Column GMI" + sim1Name + "         " \
#         + variableExtractField + \
#         "_" + field + " " + dateYearMonth
#     file1Object.create2dSlice2 (tropColFile1, \
#                                       [minValueOfBoth, maxValueOfBoth], \
#                                       311, plotTitle, "jet")

#     ax2 = fig.add_subplot(312)
#     plotTitle = "Trop Column GMI" + sim2Name + "         " \
#         + variableExtractField + \
#         "_" + field + " " + dateYearMonth

#     file1Object.create2dSlice2 (tropColFile2, \
#                                       [minValueOfBoth, maxValueOfBoth], \
#                                       312, plotTitle, "jet")
                            

#     tropColDiff = tropColFile1 / tropColFile2
#     for lat in range(0, size(file1Object.lat)):
#         for int in range(0, size(file1Object.long)):

#             if tropColFile1[lat, int] == 0 and tropColFile2[lat, int] == 0:
#                 #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
#                 tropColDiff[lat, int] = 1.0


#     ax3 = fig.add_subplot(313)  
#     plotTitle = "Trop Column model ratio for         " + variableExtractField + "_" + \
#         field + " " + dateYearMonth  
#     file1Object.create2dSlice2(tropColDiff, \
#                                      [.9, 1.1], \
#                                      313, plotTitle, "nipy_spectral", \
#                                      normalize=True)
                                 


#     FILE = "f"
#     if FILE == "f":
#         plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
#                          + "tropColumn.", bbox_inches='tight')
#     else:
#         plt.show()
#     plt.clf



#     if fieldToCompare.lower() == "o3":
   
#         print("")
#         totalColFile1 = numpy.sum(file1FieldArray[:,:,:], axis=0)
#         print("Shape of totalCol GMI 1: ", shape(totalColFile1))
#         print("")


#         print("")
#         totalColFile2 = numpy.sum(file2FieldArray[:,:,:], axis=0)
#         print("Shape of totalCol GMI 2: ", shape(totalColFile2))
#         print("")


#         print("")
#         print("")

#         minValueOfBoth = totalColFile1.min()
#         maxValueOfBoth = totalColFile1.max()

#         if totalColFile2.min() < minValueOfBoth:
#             minValueOfBoth = totalColFile2.min()
#             if totalColFile2.max() > maxValueOfBoth:
#                 maxValueOfBoth = totalColFile2.max()

#         print("")
#         print("Total O3 Column min/max value of both: ", minValueOfBoth, "/", maxValueOfBoth)
#         print("")


#         fig = plt.figure(figsize=(20,20))

#         plotOpt = {}
#         ax1 = fig.add_subplot(311)
#         plotTitle = "Total Column GMI 1 " + sim1Name + "         " + \
#             variableExtractField + "_" + field + " " + dateYearMonth
#         file1Object.create2dSlice2 (totalColFile1, \
#                                         [minValueOfBoth, maxValueOfBoth], \
#                                         311, plotTitle, "jet")

#         ax2 = fig.add_subplot(312)
#         plotTitle = "Total Column GMI 2 " + sim2Name + "         " + \
#             variableExtractField + "_" + field + " " + dateYearMonth
#         file1Object.create2dSlice2 (totalColFile2, \
#                                         [minValueOfBoth, maxValueOfBoth], \
#                                         312, plotTitle, "jet")
                            
#         totalColDiff = totalColFile1 / totalColFile2
#         for lat in range(0, size(file1Object.lat)):
#             for int in range(0, size(file1Object.long)):

#                 if totalColFile1[lat, int] == 0 and totalColFile2[lat, int] == 0:
#                 #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
#                     totalColDiff[lat, int] = 1.0

#         ax3 = fig.add_subplot(313)    
#         plotTitle = "Total Column model ratio for         " + variableExtractField + "_" + \
#             field + " " + dateYearMonth
#         file1Object.create2dSlice2(totalColDiff, \
#                                        [.9, 1.1], \
#                                        313, plotTitle, "nipy_spectral", \
#                                        normalize=True)


#         FILE = "f"
#         if FILE == "f":
#             if variableExtractField != "":
#                 plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
#                                  + "totalColumn.", bbox_inches='tight')
#             else:
#                 plt.savefig ("plots/" + field + fileTitle \
#                                  + "totalColumn.", bbox_inches='tight')
            
#         else:
#             plt.show()

#         plt.clf

#     else:
#         print("Wil plot strat column")

#         print("")
#         print("Shape of GMI stratosphere 1: ", shape(stratFile1))
#         stratColFile1 = numpy.sum(stratFile1[:,:,:], axis=0)
#         print("Shape of stratCol GMI 1: ", shape(stratColFile1))
#         print("")


#         print("")
#         print("Shape of GMI stratesphere 2: ", shape(stratFile2))
#         stratColFile2 = numpy.sum(stratFile2[:,:,:], axis=0)
#         print("Shape of stratCol GMI 2: ", shape(stratColFile2))
#         print("")


#         print("")
#         print("")


#         print(useLevels[:])
#         print(len(useLevels))
#         print(useLevels[tropMinLev::])




#         minValueOfBoth = stratColFile1.min()
#         maxValueOfBoth = stratColFile1.max()

#         if stratColFile2.min() < minValueOfBoth:
#             minValueOfBoth = stratColFile2.min()
#             if stratColFile2.max() > maxValueOfBoth:
#                 maxValueOfBoth = stratColFile2.max()

#         print("")
#         print("Strat Column  min/max value of both: ", minValueOfBoth, "/", maxValueOfBoth)
#         print("")


#         fig = plt.figure(figsize=(20,20))

#         plotOpt = {}
#         ax1 = fig.add_subplot(311)
#         plotTitle = "Strat Column GMI 1 " + sim1Name + "         " + \
#             variableExtractField + "_" + field + " " + dateYearMonth
#         file1Object.create2dSlice2 (stratColFile1, \
#                                         [minValueOfBoth, maxValueOfBoth], \
#                                         311, plotTitle, "jet")

#         ax2 = fig.add_subplot(312)
#         plotTitle = "Strat Column GMI 2 " + sim2Name + "         " + \
#             variableExtractField + "_" + field + " " + dateYearMonth
#         file1Object.create2dSlice2 (stratColFile2, \
#                                         [minValueOfBoth, maxValueOfBoth], \
#                                         312, plotTitle, "jet")
                            
#         stratColDiff = stratColFile1 / stratColFile2
#         for lat in range(0, size(file1Object.lat)):
#             for int in range(0, size(file1Object.long)):

#                 if stratColFile1[lat, int] == 0 and stratColFile2[lat, int] == 0:
#                 #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
#                     stratColDiff[lat, int] = 1.0

#         ax3 = fig.add_subplot(313)    
#         plotTitle = "Strat Column model ratio for         " + variableExtractField + "_" + \
#             field + " " + dateYearMonth
#         file1Object.create2dSlice2(stratColDiff, \
#                                        [.9, 1.1], \
#                                        313, plotTitle, "nipy_spectral", \
#                                        normalize=True)


#         FILE = "f"
#         if FILE == "f":
#             if variableExtractField != "":
#                 plt.savefig ("plots/" + variableExtractField + "_" + field + fileTitle \
#                                  + "stratColumn.", bbox_inches='tight')
#             else:
#                 plt.savefig ("plots/" + field + fileTitle \
#                                  + "stratColumn.", bbox_inches='tight')
            
#         else:
#             plt.show()

#         plt.clf



#     print("")
#     print("Finished plotting columns for : ", fieldToCompare, " to plots/ directory")
#     print("")


# else:
#     print(fieldToCompare, " is not currently set column plotting!")


print("")
print("Finished plotting: ", fieldToCompare, " to plots/ directory")
print("")

sys.stdout.flush()
    

