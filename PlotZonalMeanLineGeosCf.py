#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         September 22 2020
#
# DESCRIPTION:
# Driver to plot zonal mean time series of Geos quantities (Geos Cf)
#------------------------------------------------------------------------------

import getopt
import os
import sys
import subprocess
import multiprocessing
import shlex

import tarfile

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


from BasicTools import BasicTools
from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools
from MultiHdfFile_Class import MultiHdfFile_Class

from datetime import *
import numpy
from numpy import *


#*********************
COLORMAP = "rainbow"
RATIO_COLORMAP = "bwr"
RATIO_CONTOUR_LEVELS = [.5,.6,.7,.8,.9,.99,1.0,1.01,1.1,1.2,1.3,1.4,1.5]
DEFAULT_PERCHANGE_CONTOURS = [-1000, -500, -100, -50, -20, -10, -5, -2, -.5, -.1, .1, .5, 2, 5, 10, 20, 50, 100, 500, 1000]
#*********************


NUM_ARGS = 9


def usage ():
    print("")
    print("usage: PlotGeosCf.py [-p] [-a] [-s] [-e] [-k] [-c] [-f] [-l] [-r]")
    print("-p path to data in GEOS5 structure 1")
    print("-a path to data in GEOS5 structure 2")
    print("-s date of first comparison (YYYYMM)")
    print("-e date of first comparison (YYYYMM)")
    print("-k key file")
    print("-c collection")
    print("-f field")
    print("-l level")
    print("-r (r/c) ratio plot or percent change for 4th panel?")
    print("")
    sys.exit (0)



def createTimeSeriesSubPlot (plt, subPlotNum, xArray, yArray, \
                                 plotTitle, xLabel, yLabel):

    plt.subplot(subPlotNum)

    plt.plot (xArray, yArray, color="blue")

    ax = plt.gca()
    ax.get_yaxis().get_major_formatter().set_useOffset(False)

    plt.title (plotTitle)
    plt.ylabel (yLabel)
    plt.xlabel (xLabel)
    plt.grid(True)


def main():

    print ("Start plotting GEOS CF time series comparisions")


    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'p:a:s:e:k:c:f:l:r:')
    if len (optList) != NUM_ARGS:
        usage ()
        sys.exit (0)


    dataPath1 = optList[0][1]
    dataPath2 = optList[1][1]
    startDate = optList[2][1]
    endDate = optList[3][1]
    keyFile = optList[4][1]
    collection = optList[5][1]
    readField = str(optList[6][1])
    fileLevel = int(optList[7][1])
    ratioPlot = str(optList[8][1])

    # Clean up inputs
    readField = readField.strip()
    
    
    if not os.path.exists (dataPath1):
        print("The path you provided does not exist: ", dataPath1)
        sys.exit(0)

    if not os.path.exists (dataPath2):
        print("The path you provided does not exist: ", dataPath2)
        sys.exit(0)

    if len(startDate) != 13:
        print("ERROR date must be in the format YYYYMMDD_HHMM")
        sys.exit(0)

    if len(endDate) != 13:
        print("ERROR date must be in the format YYYYMMDD_HHMM")
        sys.exit(0)

    if not os.path.exists (keyFile):
        print("The path you provided does not exist: ", keyFile)
        sys.exit(0)

    if ratioPlot != "r" and ratioPlot != "c":
        print ("Ratio plot -r must be r for ratio or c for percent change")
        sys.exit(0)


    path1Tokens = dataPath1.split("/")
    count = 0
    for token in path1Tokens:
        if "GEOS-CF" in token:
            expName1 = token
            break
        count = count + 1
    expName2 = dataPath2.split("/")[count]

        
    
    print ("\nReady to create daily averages from collection: ", collection)

    multiFileObject1 = MultiHdfFile_Class (startDate, endDate, dataPath1, \
                                          collection, timedelta (hours=1), \
                                          "GEOS-CF_pub")

    multiFileObject1.sumFieldAcrossFiles (readField)
    multiFileObject1.averageField()
    

    multiFileObject2 = MultiHdfFile_Class (startDate, endDate, dataPath2, \
                                          collection, timedelta (hours=1), \
                                          "GEOS-CF_pub")

    multiFileObject2.sumFieldAcrossFiles (readField)
    multiFileObject2.averageField()



    geosObject1 = GeosCtmPlotTools (multiFileObject1.lastFileRead,
                                    'lat','lon',
                                    'lev','time', 'lat',
                                    'lon', 'lev', 'time' )

    geosObject2 = GeosCtmPlotTools (multiFileObject2.lastFileRead,
                                    'lat','lon',
                                    'lev','time', 'lat',
                                    'lon', 'lev', 'time' )




    basicTool = BasicTools ()

    
    baseArray1 = basicTool.returnBaseArray (multiFileObject1.fieldAverage, fileLevel)
    baseArray2 = basicTool.returnBaseArray (multiFileObject2.fieldAverage, fileLevel)


    tracerTools = TracerPlotTools (geosObject1, keyFile, 0, fileLevel)
    fieldInfo = tracerTools.tracerDict[readField]
    

    newModel1FieldArray = baseArray1 * \
        float(fieldInfo.unitConvert) # key convert

    newModel2FieldArray = baseArray2 * \
        float(fieldInfo.unitConvert) # key convert



    longRecords = numpy.zeros(geosObject1.longSize, numpy.float32)    
    modelArray1 = numpy.zeros((geosObject1.latSize), numpy.float32)
    modelArray2 = numpy.zeros((geosObject2.latSize), numpy.float32)
    modelArrayRatio = numpy.zeros((geosObject1.latSize), numpy.float32)


    format = "%b%d_%Y_%H-%M"
    startFormat = multiFileObject1.startDateActual.strftime(format)
    endFormat =  multiFileObject1.endDateActual.strftime(format)


    fig = plt.figure(figsize=(20,20))
    
    fontSize = 60
    pageTitle = collection + " " + startFormat
    fileName = collection + "-" + startFormat
    if startFormat != endFormat:
        pageTitle = pageTitle + "-" + endFormat
        fileName = fileName + "-" + endFormat
        fontSize = 48

    fig.suptitle(pageTitle, fontsize=fontSize)


    print("")
    print("Processing: ", readField)
    print("")

    plotTitle = readField + " zonal mean "
    yLabel = fieldInfo.units
    xLabel = "Latitude"



    modelArray1 = numpy.mean(newModel1FieldArray, axis=1)

    createTimeSeriesSubPlot (plt, 311, geosObject1.lat[:], modelArray1, \
                             plotTitle + expName1, xLabel, yLabel)


    modelArray2 = numpy.mean(newModel2FieldArray, axis=1)

    createTimeSeriesSubPlot (plt, 312, geosObject2.lat[:], modelArray2, \
                             plotTitle + expName2, xLabel, yLabel)


    modelArrayRatio = modelArray1[:] - modelArray2[:]
    
    createTimeSeriesSubPlot (plt, 313, geosObject2.lat[:], modelArrayRatio, \
                             plotTitle + "diff", xLabel, yLabel)



    file = "f"
    if file == "f":
        plt.savefig("plots/" + readField + "-" + \
                    expName1 + "_" + expName2 + \
                    "_" + fileName + ".2D.", \
                    bbox_inches='tight')
    elif file == "s":
        plt.show()
        
    plt.clf()

# #    if count == 0: sys.exit(0)
#     count = count + 1

#     print("")
#     print("Plotted : ", field, " to plots/ directory")
#     print("")


if __name__ == "__main__":
    main()
