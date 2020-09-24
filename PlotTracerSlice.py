#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         May 5 2019
#
# DESCRIPTION:
# Driver to plot a single tracer slice at designated level.
#-----------------------------------------------------------------------------
import os
import sys
import getopt

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools

#*********************
COLORMAP = "rainbow"
NUM_ARGS = 7
#*********************

def usage ():
    print("")
    print("usage: PlotTracerSlice.py [-c] [-l] [-r] [-d] [-n] [-k] [-f]")
    print("-c Model file")
    print("-l vertical level")
    print("-r time record to plot")
    print("-d date (YYYYMM)")
    print("-n long name of tracer")
    print("-k Key file for tracers")
    print("-f tracer to plot")
    print("")
    sys.exit (0)

def main():
    print("Start plotting field slice.")

    optList, argList = getopt.getopt(sys.argv[1:],'c:l:r:d:n:k:f:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    modelFile = str(optList[0][1])
    fileLevel = float(optList[1][1])
    timeRecord = int(optList[2][1])
    dateString = optList[3][1]
    longName = str(optList[4][1])
    keyFile = str(optList[5][1])
    fieldToPlot = str(optList[6][1])

    if not os.path.exists (modelFile):
        print("The file you provided does not exist: ", modelFile)
        sys.exit(0)

    if fileLevel < 0.0:
        print("The level to plot must be >= 0 (check file 1 lev)")
        sys.exit(0)

    if int(timeRecord) > 31:
        print("WARNING: time record is more than a typical daily file!")

    if int(timeRecord) < 0:
        print("ERROR: time record needs to be positive!")
        sys.exit(0)

    if len(dateString) != 6 and len(dateString) != 4 and len(dateString) != 8:
        print("ERROR date must be in the format YYYYMM. Received: ", dateString, len(dateString))
        sys.exit(0)

    if not os.path.exists (keyFile):
        print("The file you provided does not exist: ", keyFile)
        sys.exit(0)


    checkFor2D = None

    modelObject = GeosCtmPlotTools (modelFile, 'lat','lon',
                                          'lev','time', 'lat',
                                          'lon', 'lev', 'time' )

    modelFilebs = os.path.basename(modelFile)
    modelSimName = modelFilebs.split(".")[0] + "-" + modelFilebs.split(".")[1]

    tracerTools = TracerPlotTools (modelObject, keyFile, timeRecord, fileLevel)
    modelFieldArray = modelObject.returnField (fieldToPlot, timeRecord) # read bare field
    modelFieldArraySlice = modelObject.return2DSliceFromRefPressure (modelFieldArray, fileLevel, checkFor2D)

    print ("min max of array: ", modelFieldArraySlice.min(), modelFieldArraySlice.max())

    preConvertFieldArray = tracerTools.tracerDict[fieldToPlot].preConversion(modelFieldArraySlice, modelSimName)

    print ("min max of array after pre-conv: ", preConvertFieldArray.min(), preConvertFieldArray.max())

    newModelFieldArray = preConvertFieldArray * \
        float(tracerTools.tracerDict[fieldToPlot].unitConvert) # key convert

    print ("min max of array after conv: ", newModelFieldArray.min(), newModelFieldArray.max())

    if float(tracerTools.tracerDict[fieldToPlot].unitConvert) != 1.:
        tracerTools.tracerDict[fieldToPlot].units  = tracerTools.tracerDict[fieldToPlot].newUnit

    modelFieldArray =  newModelFieldArray
    newModelFieldArray = None


    longName = tracerTools.tracerDict[fieldToPlot].long_name

    #-----------------------------------------------------#
    # Model  Plotting

    fig = plt.figure(figsize=(20,20))

    modelObject.createPlotObjects()

    if checkFor2D == False: 
        plotTitle = modelSimName + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
            + " hPa (" + longName + ") " + dateString
    else: 
        plotTitle = modelSimName + "     " + fieldToPlot \
            + " hPa (" + longName + ") " + dateString


    if tracerTools.tracerDict[fieldToPlot].slices[fileLevel] == None:
        print ("Calling createTracerContours")
        print ((modelFieldArray.max() - modelFieldArray.min())/10)
    #    contours = tracerTools.tracerDict[fieldToPlot].createTracerContours(modelFieldArray, step=.5)
        contours = tracerTools.tracerDict[fieldToPlot].createTracerContours(modelFieldArray,
                                                        step=(modelFieldArray.max() - modelFieldArray.min())/10)
        print (contours)
    else:
        contours = []
        for contour in tracerTools.tracerDict[fieldToPlot].slices[fileLevel]:
            contours.append(float(contour))
        print ("Received contours from input file")


    print ( "model min/max values: ",  modelFieldArray.min(),modelFieldArray.max())
    print ( "(max-min)/100: ",  (modelFieldArray.max() - modelFieldArray.min())/10)

    modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid,
                                           modelObject.Y_grid, modelFieldArray,
                                           [modelFieldArray.min(),modelFieldArray.max()],
                                           [modelObject.lat[:].min(),modelObject.lat[:].max()],
                                           [modelObject.long[:].min(), modelObject.long[:].max()],
                                           "fuchsia", "darkred", 111,
                                           plotTitle, COLORMAP, tracerTools.tracerDict[fieldToPlot].units,
                                           contourLevels=contours)


    if not os.path.exists("plots"):
        os.mkdir("plots")
    file = "f"
    if file == "f":
        plt.savefig("plots/" + fieldToPlot + "-" + modelSimName + "_" + str(int(fileLevel)) \
                        + "hPa.", bbox_inches='tight')
    elif file == "s":
        plt.show()

    plt.clf()

    print("")
    print("Plotted : ", fieldToPlot, " to plots/ directory")
    print("")

if __name__ == "__main__":
    main()



    

