#!/usr/bin/env python

#-------------
# Load modules
#-------------

import os
import sys

from netCDF4 import Dataset
from numpy.random import uniform

from numpy import *

import matplotlib
import matplotlib.pyplot as plt            # pyplot module import
import matplotlib.cm as cm

from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.ticker import NullFormatter
from matplotlib import colors, ticker
from mpl_toolkits.basemap import Basemap, shiftgrid


from decimal import *

from PlotTools import PlotTools

def plotZM (data, x, y, fig, subplotNum, colorMap, dataMin, dataMax, \
                cmapUnder, cmapOver, yScale='log',plotOpt=None, contourLevels=None):

    """Create a zonal mean contour plot of one variable
    plotOpt is a dictionary with plotting options:
    'scale_factor': multiply values with this factor before plotting
    'units': a units label for the colorbar
    'levels': use list of values as contour intervals
    'title': a title for the plot
    """
    if plotOpt is None: plotOpt = {}

    ax1 = fig.add_subplot (subplotNum)

    plotTool = PlotTools ()
    cLabelFontsize = plotTool.returnContourLabelFromSubPlotNum (subplotNum)
    cTickFontSize = plotTool.returncTickSizeFromSubPlotNum (subplotNum)
    titleFontSize = plotTool.returnTitleFontSizeFromSubPlotNum (subplotNum)
    pad = plotTool.returnPadFromSubPlotNum (subplotNum)
    cBarFontSize = plotTool.returncBarFontSizeFromSubPlotNum (subplotNum)
    yTickFontSize = plotTool.returnYTickFontSizeFromSubPlotNum (subplotNum)
    xTickFontSize = plotTool.returnXTickFontSizeFromSubPlotNum (subplotNum)
    pad = plotTool.returnPadFromSubPlotNum (subplotNum)

    # scale data
    scale_factor = plotOpt.get('scale_factor', 1.0)
    pdata = data * scale_factor

    if contourLevels == []:
        # determine contour levels to be used; linear spacing, 20 levels
        clevs = plotOpt.get('levels', linspace(dataMin, dataMax, 10))

    else:
        clevs = contourLevels


    newClevs = plotTool.returnFormattedContours(clevs)

    clevs = None
    clevs = newClevs
    contourFormat = plotTool.returnContourFormatFromLevels(clevs)


    ax1.set_xticks([-90, -60, -30, 0, 30, 60, 90])
    ax1.set_xticklabels(["90S", "60S", "30S", "EQ", "30N", "60N", "90N"])

    extendValue = "both"
    if clevs[0] == 0:
        extendValue = "max"


    # map contour values to colors
    norm=colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    # draw the contours with contour labels
    CS = ax1.contour(x, y, pdata, levels=clevs, cmap=colorMap, extend=extendValue, norm=norm)
    ax1.clabel(CS,inline=1, fontsize=cLabelFontsize, colors="black", fmt=contourFormat)

    # draw the (filled) contours
    contour = ax1.contourf(x, y, pdata, levels=clevs, norm=norm, cmap=colorMap, \
                               extend=extendValue)

    # these assume a certain colormap
    contour.cmap.set_under(cmapUnder)
    contour.cmap.set_over(cmapOver)

    # add a title
    title = plotOpt.get('title',  'Zonal Mean')
    ax1.set_title(title, fontsize=titleFontSize)   # optional keyword: fontsize="small"


    cbar = fig.colorbar(contour, ax=ax1, orientation='horizontal', pad=pad, ticks=clevs, format=contourFormat)

    cbar.set_label(plotOpt.get('units', ''),size=cBarFontSize)

    #plotTool.setVisibleClevTicks (clevs, cbar.ax.get_xticklabels())


    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(cTickFontSize)

    plotTool.reviseTickLabels (cbar)

    # change font size of y labels
    ylabels = ax1.get_yticklabels()
    for z in ylabels:
        z.set_fontsize(yTickFontSize)


    # change font size of x labels
    xlabels = ax1.get_xticklabels()
    for x in xlabels:
        x.set_fontsize(xTickFontSize)

    ax1.tick_params(width=3, length=6)
        
    # zonal means are latitude versus pressure
    ax1.set_ylabel ("Pressure (hPa)", size=18)
    #ax1.set_xlabel ("Latitude", size=16)

    # all tracers are assumed to at least go to 100
    yRanges = [1000, 700, 500, 300, 200, 100]

    if y.min() <= 10.0:
        yRanges10 = [70, 50, 30, 20, 10]
        yNew = yRanges + yRanges10
        yRanges = None
        yRanges = yNew

    if y.min() <= 0.2:
        yRanges1 = [7, 5, 3, 2, 1, .7, .5, .3, .2, .1]
        yNew = yRanges + yRanges1
        yRanges = None
        yRanges = yNew

    if yRanges[-1] != y.min():
        yRanges.append(y.min())

    ax1.set_ylim(int(y.max()), y.min()) # make sure surface is bottom
    ax1.set_yscale(yScale)
    ax1.yaxis.set_minor_formatter(NullFormatter())
    ax1.set_yticks(yRanges)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%3.1f'))
    #ax1.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    


def plotZM_viz(fig, ax, data, x, y, coef,  plotTitle, cbarLabel=None, logScale=None, clevs=None):
    """
      Plot the zonal mean height

      Arguments
        data:      data to display
        x:         the x-axis meshgrid
        y:         the y-axis meshgrid
        coef:      coefficient to scale data
        figName:   figure name
        plotTitle: title of the plot
        cbarLabel: colorbar label
        logScale:  do we use log scale
        clevs:     user's prescribed countour levels
    """

    labelFontSize = "small"

    var = coef*data[:,:]

    ncont = 12  # number of contours
    # determine contour levels to be used; default: linear spacing, ncount levels
    #if not clevs.any():
    #   rmax = np.max(var)
    #   rmin = np.min(var)
    #   clevs = np.linspace(rmin, rmax, ncont)

    # map contour values to colors
    norm=matplotlib.colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    # draw the contours with contour labels
    CS = ax.contour(x, y, var, levels=clevs)
    ax.clabel(CS,inline=1, fontsize=10, colors='black')
    # draw the (filled) contours
    contour = ax.contourf(x, y, var, levels=clevs, norm=norm)

    # add colorbar
    # Note: use of the ticks keyword forces colorbar to draw all labels
    fmt = matplotlib.ticker.FormatStrFormatter("%3.2g")
    cbar = fig.colorbar(contour, ax=ax, orientation='horizontal', shrink=0.8,
                        ticks=clevs, format=fmt)
                        #ticks=clevs[::2], format=fmt)

    if (cbarLabel == None):
       cbarLabel = 'ppm'
    cbar.set_label(cbarLabel)

    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(labelFontSize)

    ax.yaxis.set_ticks_position('both')

    # set up y axes: log pressure labels on the left y axis, altitude labels
    # according to model levels on the right y axis
    ax.set_xlabel("Latitude (degrees)")
    ax.set_ylabel("Pressure [hPa]")
    if (logScale == 'Y'):
       ax.set_yscale('log')
    ax.set_ylim(10.*np.ceil(y.max()/10.), y.min()) # avoid truncation of 1000 hPa
    subs = [1,2,5]
    if y.max()/y.min() < 30.:
        subs = [1,2,3,4,5,6,7,8,9]
    if (logScale == 'Y'):
       y1loc = matplotlib.ticker.LogLocator(base=10., subs=subs)
    else:
       y1loc = matplotlib.ticker.LinearLocator()
    ax.yaxis.set_major_locator(y1loc)
    fmt = matplotlib.ticker.FormatStrFormatter("%5.2f")
    ax.yaxis.set_major_formatter(fmt)
    for t in ax.get_yticklabels():
        t.set_fontsize(labelFontSize)

    plt.title(plotTitle)


