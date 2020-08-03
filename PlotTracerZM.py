# ------------------------------------------------------------------------------
# NASA/GSFC
# ------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Oct 20 2019
#
# DESCRIPTION:
# Driver to plot zonal means of a tracer specie.
# ------------------------------------------------------------------------------
import os
import sys
import getopt
from numpy import mean
from viz_functions import plotZM

import matplotlib

matplotlib.use('pdf')
import matplotlib.pyplot as plt

from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools


def usage():
    print("")
    print("usage: PlotTracerZM.py [-g] [-r] [-d] [-k] [-f]")
    print("-g GEOS file ")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-k Key file for tracers")
    print("-f field to plot")
    print("")
    sys.exit(0)


def main():
    # *********************
    COLORMAP = "rainbow"
    NUM_ARGS = 5
    SUB_PLOT_NUM = 111
    # *********************

    optList, argList = getopt.getopt(sys.argv[1:], 'g:r:d:k:f:')
    if len(optList) != NUM_ARGS:
        usage()
        sys.exit(0)

    modelFile = optList[0][1]
    timeRecord = int(optList[1][1])
    dateYearMonth = optList[2][1]
    keyFile = str(optList[3][1])
    fieldToPlot = str(optList[4][1])

    if not os.path.exists(modelFile):
        print("The file you provided does not exist: ", modelFile)
        sys.exit(0)

    if int(timeRecord) > 30:
        print("WARNING: time record is more than a typical daily file!")

    if int(timeRecord) < 0:
        print("ERROR: time record needs to be positive!")
        sys.exit(0)

    if len(dateYearMonth) != 6 and len(dateYearMonth) != 4:
        print("ERROR date must be in the format YYYYMM")
        print("Received: ", dateYearMonth)
        sys.exit(0)

    modelObject = GeosCtmPlotTools(modelFile, 'lat', 'lon',
                                   'lev', 'time', 'lat',
                                   'lon', 'lev', 'time')

    tracerTools = TracerPlotTools(modelObject, keyFile, timeRecord, "ZM")

    modelFilebs = os.path.basename(modelFile)
    modelSimName = modelFilebs.split(".")[0] + "-" + modelFilebs.split(".")[1]

    # read bare field
    modelFieldArray = modelObject.returnField(fieldToPlot, timeRecord)
    preConvertFieldArray = tracerTools.tracerDict[fieldToPlot].preConversion \
        (modelFieldArray, modelSimName)  # pre-convert
    # key convert
    newModelFieldArray = preConvertFieldArray * \
                         float(tracerTools.tracerDict[fieldToPlot].unitConvert)

    if float(tracerTools.tracerDict[fieldToPlot].unitConvert) != 1.:
        tracerTools.tracerDict[fieldToPlot].units = tracerTools.tracerDict \
            [fieldToPlot].newUnit

    modelFieldArray = newModelFieldArray

    llIndex = modelObject.findLevelFromArray(modelObject.lev,
                                             float(tracerTools.tracerDict \
                                                       [fieldToPlot].lowLevel))
    ulIndex = modelObject.findLevelFromArray(modelObject.lev,
                                             float(tracerTools.tracerDict \
                                                       [fieldToPlot].highLevel))

    zmArray = mean(modelFieldArray[llIndex:ulIndex + 1, :, :], axis=2)

    # -----------------------------------------------------#
    # Model  Plotting

    fig = plt.figure(figsize=(18, 20))

    plotOpt = {'title': modelSimName + "    " + fieldToPlot + " Zonal Mean " + \
                        " (" + tracerTools.tracerDict[fieldToPlot].long_name + \
                        ") " + str(dateYearMonth), 'units': tracerTools.tracerDict[fieldToPlot].units}

    if tracerTools.tracerDict[fieldToPlot].zmContours is None:
        contours = tracerTools.tracerDict[fieldToPlot].createTracerContours \
            (zmArray, step=(zmArray.max() - zmArray.min()) / 10.)
    else:
        contours = []
        for contour in tracerTools.tracerDict[fieldToPlot].zmContours:
            contours.append(float(contour))

    plotZM(zmArray, modelObject.lat[:], modelObject.lev[llIndex:ulIndex + 1],
           fig, SUB_PLOT_NUM, COLORMAP,
           zmArray.min(), zmArray.max(),
           cmapUnder="fuchsia", cmapOver="darkred",
           yScale=tracerTools.tracerDict[fieldToPlot].yAxisType,
           plotOpt=plotOpt, contourLevels=contours)

    if not os.path.exists("plots"):
        os.mkdir("plots")
    fileTitle = "-" + modelSimName + "_ZM."
    plt.savefig("plots/" + fieldToPlot + fileTitle + ".", bbox_inches='tight')

    print("")
    print("Plotted zonal mean for: ", fieldToPlot, " to plots/ directory")
    print("")


if __name__ == "__main__":
    main()
