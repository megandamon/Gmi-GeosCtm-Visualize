#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Aug 25 2020
#
# DESCRIPTION:
# Driver to plot GEOS_CF comparisions

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
import numpy as np

from viz_functions import plotZM
from BasicTools import BasicTools
from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools
from GeosCfMultiFile import GeosCfMultiFile

from datetime import *

#*********************
COLORMAP = "rainbow"
RATIO_COLORMAP = "bwr"
RATIO_CONTOUR_LEVELS = [.5,.6,.7,.8,.9,.99,1.0,1.01,1.1,1.2,1.3,1.4,1.5]
DEFAULT_PERCHANGE_CONTOURS = [-1000, -500, -100, -50, -20, -10, -5, -2, -.5, -.1, .1, .5, 2, 5, 10, 20, 50, 100, 500, 1000]
#*********************


def subproc(cmd):
    name = multiprocessing.current_process().name
    print(f'Starting {name} ')
    cmds = shlex.split(cmd)
    p = subprocess.Popen(cmds,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              universal_newlines=True)
    output, errors = p.communicate()
    print(f'Exiting {name}')
    return output


def createTimeSeriesSubPlot (plt, subPlotNum, xArray, yArray, \
                                 plotTitle, xLabel, yLabel):

    plt.subplot(subPlotNum)

    plt.plot (xArray, yArray, color="black")

    #ax = plt.gca()
    #ax.get_yaxis().get_major_formatter().set_useOffset(False)

    #plt.title (plotTitle)
    #plt.ylabel (yLabel)
    #plt.xlabel (xLabel)
    #plt.grid(True)




def usage ():
    print("")
    print("usage: PlotGeosCf.py [-p] [-a] [-s] [-e] [-k] [-c] [-f] [-l] [-r] [-z] [-t] [-d]")
    print("-p path to data in GEOS5 structure 1")
    print("-a path to data in GEOS5 structure 2")
    print("-s date of first comparison (YYYYMM)")
    print("-e date of first comparison (YYYYMM)")
    print("-k key file")
    print("-c collection")
    print("-f field")
    print("-l level")
    print("-r (r/c) ratio plot or percent change for 4th panel?")
    print("-z (y/n) plot zonal mean - y or slice - n")
    print("-t (y/n) superimpose tropopause pressure (zonal mean only)")
    print("-d time delta (DD_HHMM)")
    print("")
    sys.exit (0)


def main():
    
    print("\nStart plotting GEOS CF comparisions")

    NUM_ARGS = 12

    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'p:a:s:e:k:c:f:l:r:z:t:d:')
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
    zonalMean = str(optList[9][1])
    tropPress = str(optList[10][1])
    timeDelta = str(optList[11][1])
    

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

    if zonalMean != "y" and zonalMean != "n":
        print ("Please enter y o no for zonal mean")
        sys.exit(0)

    if zonalMean == "n" and tropPress == "y":
        print("Tropopause pressure overlay is only available for zonal means!")
        sys.exit(0)

    if len(timeDelta) != 7:
        print("ERROR time delta must be in the format DD_HHMM")
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

    multiFileObject1 = GeosCfMultiFile (startDate, endDate, dataPath1, \
                                          collection, timedelta (hours=1), \
                                          "GEOS-CF_pub")

    timeResolution = multiFileObject1.createTimeDeltaFromString (timeDelta)

    multiFileObject1.sumFieldAcrossFiles (readField)
    multiFileObject1.averageField()
    


    
    multiFileObject2 = GeosCfMultiFile (startDate, endDate, dataPath2, \
                                          collection, timedelta (hours=1), \
                                          "GEOS-CF_pub")
    
    timeResolution = multiFileObject2.createTimeDeltaFromString (timeDelta)

    multiFileObject2.sumFieldAcrossFiles (readField)
    multiFileObject2.averageField()

    if tropPress == "y":
        multiFileObject1b = GeosCfMultiFile (startDate, endDate, dataPath1, \
                                                collection, timedelta (hours=1), \
                                                "GEOS-CF_pub")

        timeResolution = multiFileObject1b.createTimeDeltaFromString (timeDelta)

        multiFileObject1b.sumFieldAcrossFiles ("TROPPB")
        multiFileObject1b.averageField()

        multiFileObject2b = GeosCfMultiFile (startDate, endDate, dataPath2, \
                                                collection, timedelta (hours=1), \
                                                "GEOS-CF_pub")

        timeResolution = multiFileObject2b.createTimeDeltaFromString (timeDelta)

        multiFileObject2b.sumFieldAcrossFiles ("TROPPB")
        multiFileObject2b.averageField()




    geosObject1 = GeosCtmPlotTools (multiFileObject1.lastFileRead,
                                    'lat','lon',
                                    'lev','time', 'lat',
                                    'lon', 'lev', 'time' )

    geosObject2 = GeosCtmPlotTools (multiFileObject2.lastFileRead,
                                    'lat','lon',
                                    'lev','time', 'lat',
                                    'lon', 'lev', 'time' )




    basicTool = BasicTools ()


    # Logic for zonal means or not
    passLev = None
    if zonalMean != "y":
        passLev = fileLevel
    
    baseArray1 = basicTool.returnBaseArray (multiFileObject1.fieldAverage, passLev)
    baseArray2 = basicTool.returnBaseArray (multiFileObject2.fieldAverage, passLev)

    print ("\nshape of base arrays: ", baseArray1.shape, baseArray2.shape)
    print ("\nbase arrays min : ", baseArray1.min(), baseArray1.max())
    print ("\nbase arrays max: ", baseArray2.min(), baseArray2.max())


    
    if tropPress == "y":
        troppArray1 = basicTool.returnBaseArray(multiFileObject1b.fieldAverage, passLev)
        troppArray2 = basicTool.returnBaseArray(multiFileObject2b.fieldAverage, passLev)




    tracerTools = TracerPlotTools (geosObject1, keyFile, 0, fileLevel)
    fieldInfo = tracerTools.tracerDict[readField]
    

    newModel1FieldArray = baseArray1 * \
        float(fieldInfo.unitConvert) # key convert

    newModel2FieldArray = baseArray2 * \
        float(fieldInfo.unitConvert) # key convert



    
    if tropPress == "y":
        troppFieldInfo = tracerTools.tracerDict["TROPPB"]

        newTropp1Array = troppArray1 * \
        float(troppFieldInfo.unitConvert) # key convert

        newTropp2Array = troppArray2 * \
        float(troppFieldInfo.unitConvert) # key convert



    
    # zonal mean
    if zonalMean == "y":

        maskedArray1 = np.ma.masked_where(newModel1FieldArray >= 1000000000, newModel1FieldArray)
        maskedArray2 = np.ma.masked_where(newModel2FieldArray >= 1000000000, newModel2FieldArray)

        zmArray1 = np.mean(maskedArray1, axis=2)
        zmArray2 = np.mean(maskedArray2, axis=2)
        
        newModel1FieldArray = None
        newModel1FieldArray = zmArray1
        newModel2FieldArray = None
        newModel2FieldArray = zmArray2

        
        
    minValueBoth = newModel1FieldArray.min()
    maxValueBoth = newModel1FieldArray.max()
    if newModel2FieldArray.min() < minValueBoth:
        minValueBoth = newModel2FieldArray.min()
    if newModel2FieldArray.max() > maxValueBoth:
        maxValueBoth = newModel2FieldArray.max()
        

    contours = []
    if zonalMean == "n":
        extractContours = fieldInfo.slices[float(fileLevel)]
    else:
        extractContours = fieldInfo.zmContours

    for contour in extractContours:
        contours.append(float(contour))


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





    geosObject1.createPlotObjects()
    geosObject2.createPlotObjects()






    

    plotTitle = readField + "     " + expName1

    if zonalMean == "n":

        
        geosObject1.create2dSliceContours(fig, geosObject1.baseMap, geosObject1.X_grid, \
                                          geosObject1.Y_grid, newModel1FieldArray, \
                                          [minValueBoth, maxValueBoth],
                                          [geosObject1.lat[:].min(),geosObject1.lat[:].max()],
                                          [geosObject1.long[:].min(), geosObject1.long[:].max()],
                                          "fuchsia", "darkred",
                                          221,
                                          plotTitle,
                                          COLORMAP, fieldInfo.units,
                                          contourLevels=contours)

        plotTitle = readField + "     " + expName2
        geosObject2.create2dSliceContours(fig, geosObject2.baseMap, geosObject2.X_grid, \
                                          geosObject2.Y_grid, newModel2FieldArray, \
                                          [minValueBoth, maxValueBoth],
                                          [geosObject2.lat[:].min(),geosObject2.lat[:].max()],
                                          [geosObject2.long[:].min(), geosObject2.long[:].max()],
                                          "fuchsia", "darkred",
                                          222,
                                          plotTitle,
                                          COLORMAP, fieldInfo.units,
                                          contourLevels=contours)
    else:
        plotOpt = {}

        plotOpt['title'] = readField + "     " + expName1
        plotOpt['units'] = fieldInfo.units

        plotZM (newModel1FieldArray, geosObject1.lat[:], geosObject1.lev[:],
                fig, 221, COLORMAP,
                minValueBoth, maxValueBoth,
                "fuchsia", "darkred",
                plotOpt=plotOpt, contourLevels=contours)

        oneDTropp1 = np.mean(newTropp1Array, axis=1)
        
        createTimeSeriesSubPlot (plt, 221, geosObject1.lat[:], oneDTropp1, \
                                 "", "", "")


        plotOpt['title'] = readField + "     " + expName2
        
        plotZM (newModel2FieldArray, geosObject2.lat[:], geosObject2.lev[:],
                fig, 222, COLORMAP,
                minValueBoth, maxValueBoth,
                "fuchsia", "darkred",
                plotOpt=plotOpt, contourLevels=contours)



        
        oneDTropp2 = np.mean(newTropp2Array, axis=1)
        
        createTimeSeriesSubPlot (plt, 222, geosObject1.lat[:], oneDTropp2, \
                                 "", "", "")


    # simple differences
    analType = "s"
    plotTitle = expName1 + "-" + expName2
    
    if zonalMean == "n":
        z_Model = geosObject1.createComparisionLatLon(newModel1FieldArray, \
                                                      newModel2FieldArray, \
                                                      analType)

    
        if fieldInfo.diffSlices[float(fileLevel)] == None:
            diffContourLevels = fieldInfo.createDiffContoursFromMinMax(z_Model.min(), z_Model.max())

        else:
            diffContourLevels = fieldInfo.diffSlices[float(fileLevel)]

        geosObject2.create2dSliceContours(fig, geosObject2.baseMap, geosObject2.X_grid, \
                                        geosObject2.Y_grid, z_Model, \
                                          [z_Model.min(), z_Model.max()],
                                          [geosObject2.lat[:].min(),geosObject2.lat[:].max()],\
                                          [geosObject2.long[:].min(), geosObject2.long[:].max()], \
                                          fieldInfo.diffMin, fieldInfo.diffMax, \
                                          223, \
                                          plotTitle, \
                                          str(fieldInfo.diffColorMap), \
                                          fieldInfo.units, \
                                          labelContours=False, \
                                          contourLevels=diffContourLevels)

    else:
        z_Model = geosObject1.createComparision2D(newModel1FieldArray, \
                                                  newModel2FieldArray, \
                                                  analType)
        if fieldInfo.z_zm == None:
            diffContourLevels = fieldInfo.createDiffContoursFromMinMax\
                (z_Model.min(), z_Model.max())
        else:
            diffContourLevels = fieldInfo.z_zm
            
        plotOpt['title'] = plotTitle
            
        plotZM (z_Model, geosObject2.lat[:], geosObject2.lev[:],
                fig, 223, str(fieldInfo.diffColorMap), \
                z_Model.min(), z_Model.max(),
                fieldInfo.diffMin, fieldInfo.diffMax, \
                plotOpt=plotOpt, contourLevels=diffContourLevels, cLabels=False)

                                            


    

    z_Model = None

    if zonalMean == "n":
        z_Model = geosObject1.createComparisionLatLon(newModel1FieldArray, \
                                                      newModel2FieldArray, \
                                                      ratioPlot)
    else:
        z_Model = geosObject1.createComparision2D(newModel1FieldArray, \
                                                  newModel2FieldArray, \
                                                  ratioPlot)        
    
    if ratioPlot == "r":
        useMin = .5
        useMax = 1.5
        panelContours =  RATIO_CONTOUR_LEVELS
        #useColorMap = "nipy_spectral"
        #lowEnd = "black"
        #highEnd = "white"
        useColorMap = "coolwarm"
        lowEnd = "navy"
        highEnd = "darkred"
        useUnits = "Model ratio"
        quantity = "MODEL RATIOS"
        print ("\n4th panel plot will contain ratios")
    else:
        useMin = z_Model.min()
        useMax = z_Model.max()
        panelContours =  DEFAULT_PERCHANGE_CONTOURS
        useColorMap = "coolwarm"
        lowEnd = "navy"
        highEnd = "darkred"
        useUnits = "%"
        quantity = "PERC CHANGE"
        print ("\n4th panel plot will contain percent change")


    plotTitle = quantity + "  " + expName1 + "-" + expName2

    if zonalMean == "n":
        geosObject2.create2dSliceContours (fig, geosObject2.baseMap, geosObject2.X_grid,
                                           geosObject2.Y_grid, z_Model,
                                           [useMin, useMax],
                                           [geosObject2.lat[:].min(),geosObject2.lat[:].max()],
                                           [geosObject2.long[:].min(), geosObject2.long[:].max()],
                                           lowEnd, highEnd, 
                                           224,
                                           plotTitle, useColorMap, units=useUnits, labelContours=False,
                                           contourLevels=panelContours)

    else:

        plotOpt['title'] = plotTitle
        plotOpt['units'] = useUnits
            
        plotZM (z_Model, geosObject2.lat[:], geosObject2.lev[:],
                fig, 224, useColorMap, \
                useMin, useMax, \
                lowEnd, highEnd, \
                plotOpt=plotOpt, contourLevels=panelContours, cLabels=False)

        
    
    if not os.path.exists("plots"):
        os.mkdir("plots")
        
    file = "f"
    if file == "f":
        
        fileName = "plots/" + readField + "-" + \
                    expName1 + "_" + expName2 + \
                    "_" + fileName + "."

        if zonalMean == "y":
            fileName = fileName + "ZM."
            
        plt.savefig(fileName, bbox_inches='tight')
    elif file == "s":
        plt.show()

    plt.clf()

if __name__ == "__main__":
    main()
