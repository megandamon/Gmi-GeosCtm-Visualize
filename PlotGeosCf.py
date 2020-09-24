#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Aug 25 2020
#
# DESCRIPTION:
# Driver to plot GEOS_CF comparisions

    # collection = "met_tavg_1hr"
    # For TROPPB, T, Q, SLP, 
    # NRT uses 35 model levels
    # DEVEL uses 1 level
    # zonal mean for TROPPB?

    # collection = "met_tavg_1hr"
    # TPREC in pub (not priv) for NRT

    # DEVEL uses 23 pressure levels
    #collection = "met_inst_1hr"    
    # NRT uses 72 model levels
    #multiFileObject2.sumFieldAcrossFiles ("T")
    #If we are doing any time averaging we need to
    #interpolate the model levels to pressure levels


    # DEVEL uses 23 pressure levels
    # NRT uses 72 model levels
    # O3,CO,NO2
    #collection = "chm_inst_1hr"
    #zonal mean differences for ['O3','CO','NO2','T','U','V','Q']
    #from the inst_1hr_g collections. daily average of last day ; animation?


    # both output surface level only 
    # For TOTCOL_O3, O3, CO, NO2, SO2, PM25_RH35_GCC
    #collection = "chm_tavg_24hr"

    # O3, CO, NO2, SO2, PM25_RH35_GCC
    #collection = chm_tavg_1hr
    



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


def main():
    
    print("\nStart plotting GEOS CF comparisions")

    NUM_ARGS = 9

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

    
    
    minValueBoth = newModel1FieldArray.min()
    maxValueBoth = newModel1FieldArray.max()
    if newModel2FieldArray.min() < minValueBoth:
        minValueBoth = newModel2FieldArray.min()
    if newModel2FieldArray.max() > maxValueBoth:
        maxValueBoth = newModel2FieldArray.max()
        
    
    contours = []
    for contour in fieldInfo.slices[float(fileLevel)]:
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


    
    analType = "s"
    z_Model = geosObject1.createComparisionLatLon(newModel1FieldArray, \
                                                  newModel2FieldArray, \
                                                  analType)

    
    if fieldInfo.diffSlices[float(fileLevel)] == None:
        diffContourLevels = fieldInfo.createDiffContoursFromMinMax(z_Model.min(), z_Model.max())

    else:
        diffContourLevels = fieldInfo.diffSlices[float(fileLevel)]



    plotTitle = expName1 + "-" + expName2
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

    z_Model = None
    z_Model = geosObject1.createComparisionLatLon(newModel1FieldArray, \
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
    geosObject2.create2dSliceContours (fig, geosObject2.baseMap, geosObject2.X_grid,
                                       geosObject2.Y_grid, z_Model,
                                       [useMin, useMax],
                                       [geosObject2.lat[:].min(),geosObject2.lat[:].max()],
                                       [geosObject2.long[:].min(), geosObject2.long[:].max()],
                                       lowEnd, highEnd, 
                                       224,
                                       plotTitle, useColorMap, units=useUnits, labelContours=False,
                                       contourLevels=panelContours)



    
    if not os.path.exists("plots"):
        os.mkdir("plots")
    file = "f"
    if file == "f":
        plt.savefig("plots/" + readField + "-" + \
                    expName1 + "_" + expName2 + \
                    "_" + fileName + ".", \
                    bbox_inches='tight')
    elif file == "s":
        plt.show()

    plt.clf()

if __name__ == "__main__":
    main()
