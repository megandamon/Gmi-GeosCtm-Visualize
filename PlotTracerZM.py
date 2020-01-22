#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Oct 20 2019
#
# DESCRIPTION:
# Driver to plot zonal means of a tracer specie.
#------------------------------------------------------------------------------

#-------------
# Load modules
#-------------
import os
import sys
import getopt
from netCDF4 import Dataset
import glob
from numpy.random import uniform
from numpy import *
import matplotlib.pyplot as plt            # pyplot module import
from matplotlib.ticker import NullFormatter
import matplotlib.cm as cm
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib import colors, ticker
from matplotlib.backends.backend_pdf import PdfPages

import vertLevels_GEOS5 as pressLevels

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools



def is_leap_year(year):
    """Determine whether a year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def plotZMLocal(data, x, y, fig, ax1, colorMap, dataMin, dataMax, plotOpt=None):

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

    # determine contour levels to be used; linear spacing, 20 levels
    clevs = plotOpt.get('levels', linspace(dataMin, dataMax, 20))

    # map contour values to colors
    norm=colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    # draw the contours with contour labels
    CS = ax1.contour(x, y, pdata, levels=clevs, cmap=colorMap)
    ax1.clabel(CS,inline=1, fontsize=10, colors="black",fmt="%1.1e")

    # draw the (filled) contours
    contour = ax1.contourf(x, y, pdata, levels=clevs, norm=norm, cmap=colorMap, \
                               vmin = dataMin, vmax = dataMax)

    # add a title
    title = plotOpt.get('title',  'Zonal Mean')
    ax1.set_title(title, fontsize=20)   # optional keyword: fontsize="small"

    # add colorbar
    cbar = fig.colorbar(contour, ax=ax1, orientation='horizontal') #, xshrink=0.8,                     
    cbar.set_label(plotOpt.get('units', ''))
    for t in cbar.ax.get_xticklabels():
        t.set_fontsize("medium")

    # change font size of x labels
    xlabels = ax1.get_xticklabels()
    for t in xlabels:
        t.set_fontsize("medium")

    # zonal means are latitude versus pressure
    ax1.set_ylabel ("Pressure (hPa)")
    ax1.set_xlabel ("Latitude")

    

    yRangesTop = arange(float(y.min()), 130., 10.) # 10 mb apart in strat
    yRangesBottom = arange(130., float(y.max()), 120.) # 120 mb apart in trop

    print ()
    print ("yBottom: ", yRangesBottom[:])
    print ("yTop: ", yRangesTop[:])
    print ()



    yRanges = concatenate((yRangesTop, yRangesBottom), axis=0)
    print (yRanges)


    ax1.set_ylim(float(y.max()), float(y.min())) # make sure surface is bottom
    ax1.set_yscale('log')
    ax1.yaxis.set_minor_formatter(NullFormatter())
    ax1.set_yticks(yRanges)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%3.1f'))
    
    # change font size of y labels
    ylabels = ax1.get_yticklabels()
    for t in ylabels:
        t.set_fontsize("medium")


NUM_ARGS = 6
def usage ():
    print("")
    print("usage: PlotTracerZM.py [-g] [-r] [-d] [-l] [-u] [-f]")
    print("-g GEOS file ")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-l lower level to plot (mbs)")
    print("-u lower level to plot (mbs)")
    print("-f field to plot")
    print("")
    sys.exit (0)


print("Start plotting field differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'g:r:d:l:u:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile = optList[0][1]
timeRecord = int(optList[1][1])
dateYearMonth = optList[2][1]
lowerLevel = float(optList[3][1])
upperLevel = float(optList[4][1])
fieldToPlot = str(optList[5][1])



#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (modelFile):
    print("The file you provided does not exist: ", modelFile)
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM")
    print("Received: ", dateYearMonth)
    sys.exit(0)

if lowerLevel < 0.1: 
    print("WARNING: the lower level is high in the atmsophere")

if upperLevel > 1000.0:
    print("WARNING: the upper level is low in the atmosphere")


print("")
print(modelFile)
print("")

modelSimName = modelFile.split(".")[0] + "-" + modelFile.split(".")[1]


print("")
print(modelSimName)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------

modelObject = GeosCtmPlotTools (modelFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )





print("")
print("Model vertical levels: ", modelObject.lev[:])
print("")



units = modelObject.hdfData.variables[fieldToPlot].getncattr('units')
print ("")
print ("Units: ", units)
print ("")


modelFieldArray = modelObject.returnField (fieldToPlot, timeRecord)

print("")
print("modelFieldArray shape: ", modelFieldArray.shape)
print("")

print("")
print("Global sum of ", fieldToPlot, " : ", sum(modelFieldArray))
print("")


levUnits = modelObject.hdfData.variables['lev'].getncattr('units')


print("lev units: ", levUnits, type(modelObject.lev[0]))


if levUnits == "layer":

    print ()
    print ("File uses model levels / layers")
    print ()

    levs1 = pressLevels.calcPressureLevels(len(modelObject.lev))
    levs = levs1[::-1]

elif levUnits == "hPa":

    print ()
    print ("File uses pressure levels / layers")
    print ("Vertical dimension, lev, is in hPa!")
    print ()

    levs1 = zeros(len(modelObject.lev))

    count = 0
    for modelLev in modelObject.lev[:]:
        levs1[count] = modelLev
        count = count + 1

    levs = levs1[::-1]

else:
    print ("Vertical dimension with units: ", levUnits, " not yet supported!")
    sys.exit(0)



print ()
print (levs)
print ()
print ("Number of levels: ", len(levs))
print ()
print ("Vertical layers between: ")
print (lowerLevel, upperLevel)
print ()


llValue = (min(levs, key=lambda x:abs(x-lowerLevel)))
ulValue = (min(levs, key=lambda x:abs(x-upperLevel)))
llIndex1 = where(levs == llValue)
ulIndex1 = where(levs == ulValue)
llIndex = llIndex1[0][0]
ulIndex =  ulIndex1[0][0]

print ()
print ("Index values are: ")
print (llIndex, ulIndex)
print ()


zmArray = mean(modelFieldArray[ulIndex:llIndex+1, :, :], axis=2)



min_val = (zmArray.min())
max_val = (zmArray.max())

fig = plt.figure(figsize=(20,20))
ax1 = fig.add_subplot(111)
plotOpt = {}


plotOpt['title'] = fieldToPlot +  " Zonal Mean " + dateYearMonth
plotOpt['units'] = units

print (plotOpt['title'])
print (levs[ulIndex:llIndex+1])


plotZMLocal(zmArray, modelObject.lat[:], levs[ulIndex:llIndex+1], \
               fig, ax1, 'YlGnBu', \
                min_val, max_val, \
                plotOpt)


fileTitle = "-" + modelSimName + "_ZM."
plt.savefig ("plots/" + fieldToPlot + fileTitle \
                 + ".", bbox_inches='tight')
