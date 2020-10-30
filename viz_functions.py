#!/usr/bin/env python

# -------------
# Load modules
# -------------

import sys

import matplotlib
import matplotlib.pyplot as plt  # pyplot module import
from matplotlib import colors
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.ticker import NullFormatter
from numpy import linspace, ceil

from PlotTools import PlotTools


"""Create a zonal mean contour plot of one variable
plotOpt is a dictionary with plotting options:
'scale_factor': multiply values with this factor before plotting
'units': a units label for the colorbar
'levels': use list of values as contour intervals
'title': a title for the plot
"""

def plotZM(data, x, y, fig, subplotNum, colorMap, dataMin, dataMax,
           cmapUnder, cmapOver, yScale='log', plotOpt=None, contourLevels=None,
           cLabels=True):
    
    if plotOpt is None: plotOpt = {}

    ax1 = fig.add_subplot(subplotNum)

    plotTool = PlotTools()

    # these routines look at the subplot arrangment (subplotNum)
    # and determine optimal font sizes 
    cLabelFontsize = plotTool.returnContourLabelFromSubPlotNum(subplotNum)
    cTickFontSize = plotTool.returncTickSizeFromSubPlotNum(subplotNum)
    titleFontSize = plotTool.returnTitleFontSizeFromSubPlotNum(subplotNum)
    cBarFontSize = plotTool.returncBarFontSizeFromSubPlotNum(subplotNum)
    yTickFontSize = plotTool.returnYTickFontSizeFromSubPlotNum(subplotNum)
    xTickFontSize = plotTool.returnXTickFontSizeFromSubPlotNum(subplotNum)
    pad = plotTool.returnPadFromSubPlotNum(subplotNum)

    # scale data
    scale_factor = plotOpt.get('scale_factor', 1.0)
    pdata = data * scale_factor


    # if contourLevels aren't provided, make something up
    if not contourLevels:
        # determine contour levels to be used; linear spacing
        clevs = plotOpt.get('levels', linspace(dataMin, dataMax, 10))
    else:
        clevs = contourLevels

    
    # clean up clevs, newClevs should be in int/float (numerical)
    newClevs = plotTool.returnFormattedContours(clevs)
    clevs = None
    clevs = newClevs

    # contourFormat gives us an idea of the scale of the idea
    # should return the format for the amount of decimal points
    # that is needed to represent the entire colormap values
    contourFormat = plotTool.returnContourFormatFromLevels(clevs)

    print ("\ncontourFormat needed: ", contourFormat)

    # full global map assumed
    ax1.set_xticks([-90, -60, -30, 0, 30, 60, 90])
    ax1.set_xticklabels(["90S", "60S", "30S", "EQ", "30N", "60N", "90N"])

    extendValue = "both"
    if clevs[0] == 0:
        extendValue = "max"

    # map contour values to colors
    norm = colors.BoundaryNorm (clevs, ncolors=256, clip=False)


    # converts clevs to strings, some to sci notation
    # depending on criteria in routine
    # returns dictionary (clabel will accept this format)
    fmtDict = plotTool.returnContourLabelDictFromLevels(clevs)
    
    if cLabels == True:
        # draw the contours with contour labels
        CS = ax1.contour(x, y, pdata, levels=clevs, cmap=colorMap, \
                         extend=extendValue, norm=norm)

        ax1.clabel(CS, inline=1, fontsize=cLabelFontsize, colors="black", fmt=fmtDict)

    # draw the (filled) contours
    contour = ax1.contourf(x, y, pdata, levels=clevs, norm=norm, cmap=colorMap,
                           extend=extendValue)

    # these assume a certain colormap
    contour.cmap.set_under(cmapUnder)
    contour.cmap.set_over(cmapOver)

    # add a title
    title = plotOpt.get('title', 'Zonal Mean')
    ax1.set_title(title, fontsize=titleFontSize)  

    # pass contourFormat so that all numbers
    # in cbar have the decimal representation that is needed
    cbar = fig.colorbar(contour, ax=ax1, orientation='horizontal', \
                        pad=pad, ticks=clevs, format=contourFormat)

    cbar.set_label(plotOpt.get('units', ''), size=cBarFontSize)

    # plotTool.setVisibleClevTicks (clevs, cbar.ax.get_xticklabels())

    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(cTickFontSize)

    # fmtDict has the labels as strings, with the optimized formatting
    # to conserve space
    plotTool.reviseTickLabelsFromFormats(cbar,fmtDict)

    # change font size of y labels
    ylabels = ax1.get_yticklabels()
    for z in ylabels:
        z.set_fontsize(yTickFontSize)

    # change font size of x labels
    xlabels = ax1.get_xticklabels()
    for x in xlabels:
        x.set_fontsize(xTickFontSize)

    ax1.tick_params(width=3, length=6)

    yMin = y.min()
    yMax = y.max()
    
    
    # zonal means are latitude versus pressure
    ax1.set_ylabel("Pressure (hPa)", size=18)
    # ax1.set_xlabel ("Latitude", size=16)

    # all data are assumed to at least go to 100 hPa
    # and start at 1000 hPa
    yRanges = [1000, 700, 500, 300, 200, 100]

    if y.min() <= 10.0:
        yRanges10 = [70, 50, 30, 20, 10]
        yNew = yRanges + yRanges10
        yRanges = yNew

    if y.min() <= 0.2:
        yRanges1 = [7, 5, 3, 2, 1, .7, .5, .3, .2, .1]
        yNew = yRanges + yRanges1
        yRanges = yNew

    if yRanges[-1] != y.min():
        yRanges.append(y.min())

    ax1.set_ylim(int(y.max()), y.min())  # make sure surface is bottom
    ax1.set_yscale(yScale)
    ax1.yaxis.set_minor_formatter(NullFormatter())
    ax1.set_yticks(yRanges)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%3.1f'))
    # ax1.yaxis.set_major_formatter(FormatStrFormatter('%d'))


def plotZM_viz(fig, ax, data, x, y, coef, plotTitle, cbarLabel=None, logScale=None, clevs=None):
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

    var = coef * data[:, :]

    # ncont = 12  # number of contours
    # determine contour levels to be used; default: linear spacing, ncount levels
    # if not clevs.any():
    #   rmax = np.max(var)
    #   rmin = np.min(var)
    #   clevs = np.linspace(rmin, rmax, ncont)

    # map contour values to colors
    norm = matplotlib.colors.BoundaryNorm(clevs, ncolors=256, clip=False)

    # draw the contours with contour labels
    CS = ax.contour(x, y, var, levels=clevs)
    ax.clabel(CS, inline=1, fontsize=10, colors='black')
    # draw the (filled) contours
    contour = ax.contourf(x, y, var, levels=clevs, norm=norm)

    # add colorbar
    # Note: use of the ticks keyword forces colorbar to draw all labels
    fmt = matplotlib.ticker.FormatStrFormatter("%3.2g")
    cbar = fig.colorbar(contour, ax=ax, orientation='horizontal', shrink=0.8,
                        ticks=clevs, format=fmt)
    # ticks=clevs[::2], format=fmt)

    if cbarLabel is None:
        cbarLabel = 'ppm'
    cbar.set_label(cbarLabel)

    for t in cbar.ax.get_xticklabels():
        t.set_fontsize(labelFontSize)

    ax.yaxis.set_ticks_position('both')

    # set up y axes: log pressure labels on the left y axis, altitude labels
    # according to model levels on the right y axis
    ax.set_xlabel("Latitude (degrees)")
    ax.set_ylabel("Pressure [hPa]")
    if logScale == 'Y':
        ax.set_yscale('log')
    ax.set_ylim(10. * ceil(y.max() / 10.), y.min())  # avoid truncation of 1000 hPa
    subs = [1, 2, 5]
    if y.max() / y.min() < 30.:
        subs = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if logScale == 'Y':
        y1loc = matplotlib.ticker.LogLocator(base=10., subs=subs)
    else:
        y1loc = matplotlib.ticker.LinearLocator()
    ax.yaxis.set_major_locator(y1loc)
    fmt = matplotlib.ticker.FormatStrFormatter("%5.2f")
    ax.yaxis.set_major_formatter(fmt)
    for t in ax.get_yticklabels():
        t.set_fontsize(labelFontSize)

    plt.title(plotTitle)
