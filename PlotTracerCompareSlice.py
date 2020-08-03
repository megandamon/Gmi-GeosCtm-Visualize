 #------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Nobember 20th 2019
#
# DESCRIPTION:
# Driver to plot comparisions of a lat/lon slice of a tracer (mb/hPa).
#-----------------------------------------------------------------------------
import os
import getopt
import sys

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools

#*********************
COLORMAP = "rainbow"
RATIO_COLORMAP = "bwr"
RATIO_CONTOUR_LEVELS = [.5,.6,.7,.8,.9,1.0,1.1,1.2,1.3,1.4,1.5]
DEFAULT_PERCHANGE_CONTOURS = [-1000, -500, -100, -50, -20, -10, -5, -2, -.5, .5, 2, 5, 10, 20, 50, 100, 500, 1000]
NUM_ARGS = 9
#*********************

def usage ():
    print("")
    print("usage: PlotTracerCompareSlice.py [-c] [-g] [-l] [-r] [-d] [-n] [-k] [-p] [-f]")
    print("-g Model file 1")
    print("-c Model file 2")
    print("-l vertical level (hPa)")
    print("-r time record to plot")
    print("-d date (YYYYMM)")
    print("-n long name of tracer")
    print("-k Key file for tracers")
    print("-p percentage change contours (d-default-+-100, a-algorithmic")
    print("-f tracer to plot")
    print("")
    sys.exit (0)


def main():
    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'g:c:l:r:d:n:k:p:f:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    model1File = str(optList[0][1])
    model2File = str(optList[1][1])
    fileLevel = float(optList[2][1])
    timeRecord = int(optList[3][1])
    dateYearMonth = optList[4][1]
    longName = str(optList[5][1])
    keyFile = str(optList[6][1])
    percChangeContours = str(optList[7][1])
    fieldToPlot = str(optList[8][1])


    if not os.path.exists (model1File):
        print("The file you provided does not exist: ", model1File)
        sys.exit(0)

    if not os.path.exists (model2File):
        print("The file you provided does not exist: ", model2File)
        sys.exit(0)

    if int(timeRecord) > 31:
        print("WARNING: time record is more than a typical daily file!")

    if int(timeRecord) < 0:
        print("ERROR: time record needs to be positive!")
        sys.exit(0)

    if len(dateYearMonth) != 6 and len(dateYearMonth) != 4:
        print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
        sys.exit(0)

    if not os.path.exists (keyFile):
        print("The file you provided does not exist: ", keyFile)
        sys.exit(0)

    if fileLevel < 0.1 and fileLevel > 1300.:
        print("GEOS-5 pressure levels should be < 1300 and > 0.1 mb/hPa")
        sys.exit(0)

    if percChangeContours != "d" and percChangeContours != "a":
        print("Percent change contours should be either d(deafult) or a(algorithmic)")
        sys.exit(0)




        
    model1Object = GeosCtmPlotTools (model1File, 'lat','lon',
                                          'lev','time', 'lat',
                                          'lon', 'lev', 'time' )

    model2Object = GeosCtmPlotTools (model2File, 'lat','lon',
                                     'lev','time', 'lat',
                                     'lon', 'lev', 'time' )

    



    

    modelFilebs = os.path.basename(model1File)
    model1SimName = modelFilebs.split(".")[0] + "-" + modelFilebs.split(".")[1]
    model1SimName2 = model1SimName.split("_")[0] + "_" + model1SimName.split("_")[1]
    model1SimName = model1SimName2

    modelFilebs = os.path.basename(model2File)
    model2SimName = modelFilebs.split(".")[0] + "-" + modelFilebs.split(".")[1]
    model2SimName2 = model2SimName.split("_")[0] + "_" + model2SimName.split("_")[1]
    model2SimName = model2SimName2



    
    tracerTools1 = TracerPlotTools (model1Object, keyFile, timeRecord, fileLevel)
    tracerTools2 = TracerPlotTools (model2Object, keyFile, timeRecord, fileLevel)



    
    if fieldToPlot not in model1Object.hdfData.variables.keys():

        if fieldToPlot.islower() == True:
            fieldToPlot1 = fieldToPlot.upper()
        else:
            fieldToPlot1 = fieldToPlot.lower()
    else:
        fieldToPlot1 = fieldToPlot

    model1FieldArray = model1Object.returnField (fieldToPlot, timeRecord)

    model1FieldArraySlice = model1Object.return2DSliceFromRefPressure (model1FieldArray, fileLevel)

    preConvertFieldArray1 = tracerTools1.tracerDict[fieldToPlot].preConversion(model1FieldArraySlice, model1SimName)

    newModel1FieldArray = preConvertFieldArray1 * \
        float(tracerTools1.tracerDict[fieldToPlot].unitConvert) # key convert

    if float(tracerTools1.tracerDict[fieldToPlot].unitConvert) != 1.:
        tracerTools1.tracerDict[fieldToPlot].units  = tracerTools1.tracerDict[fieldToPlot].newUnit

    model1FieldArray = newModel1FieldArray
    newModel1FieldArray = None


    model2FieldArray = model2Object.returnField (fieldToPlot, timeRecord)
    model2FieldArraySlice = model2Object.return2DSliceFromRefPressure (model2FieldArray, fileLevel)

    preConvertFieldArray2 = tracerTools2.tracerDict[fieldToPlot].preConversion(model2FieldArraySlice, model2SimName)

    newModel2DFieldArray = preConvertFieldArray2 * \
        float(tracerTools2.tracerDict[fieldToPlot].unitConvert) # key convert

    if float(tracerTools2.tracerDict[fieldToPlot].unitConvert) != 1.:
        tracerTools2.tracerDict[fieldToPlot].units  = tracerTools2.tracerDict[fieldToPlot].newUnit

    model2FieldArray = newModel2DFieldArray
    newModel2FieldArray = None

    
    if model1FieldArray.shape != model2FieldArray.shape:

        print("\n")
        print("Field arrays are not the same, interpolation required!")
        print("")

        model1NumPoints = len(model1FieldArray.flatten())
        model2NumPoints = len(model2FieldArray.flatten())

        print ("")
        if model1NumPoints < model2NumPoints:

            print ("\nmodel1 has fewer points (", model1NumPoints, "<", model2NumPoints, ") ; will interpolate to the grid of model 1")


            model2FieldArrayInterp = model2Object.interpMaskedFieldLatLon (model1FieldArray, model2FieldArray,
                                                                        model1Object.lat, model1Object.long,
                                                                        timeRecord, replaceValue = None)

            model2FieldArray = None
            model2FieldArray = model2FieldArrayInterp

            modelObject = model1Object

        else:

            print ("\nmodel2 has fewer points (", model2NumPoints, "<", model1NumPoints, ") ; will interpolate to the grid of model 2")


            model1FieldArrayInterp = model1Object.interpMaskedFieldLatLon (model2FieldArray, model1FieldArray,
                                                                         model2Object.lat, model2Object.long,
                                                                         timeRecord, replaceValue = None)
            model1FieldArray = None
            model1FieldArray = model1FieldArrayInterp
            modelObject = model2Object

    else:
        modelObject = model1Object

    print ("")

    minValueBoth = model1FieldArray.min()
    maxValueBoth = model1FieldArray.max()

    if model2FieldArray.min() < minValueBoth:
        minValueBoth = model2FieldArray.min()
    if model2FieldArray.max() > maxValueBoth:
        maxValueBoth = model2FieldArray.max()
    #***********************************************


    

    print("")
    print("min/max value of both models: ", minValueBoth, maxValueBoth)
    print("")

    
    # by now, all the tracers should be in the same units for comparision
    # so we can reference just tracerTools1 
    if tracerTools1.tracerDict[fieldToPlot].units.find("days") != -1:
        analType = "r"
        analString = "ratio"
    if tracerTools1.tracerDict[fieldToPlot].units.find("years") != -1:
        analType = "r"
        analString = "ratio"
    if tracerTools1.tracerDict[fieldToPlot].units.find("kg-1") != -1:
        analType = "r"
        analString = "ratio"
    if tracerTools1.tracerDict[fieldToPlot].units.find("ppt") != -1:
        analType = "r"
        analString = "ratio"
    if tracerTools1.tracerDict[fieldToPlot].units.find("ppb") != -1:
        analType = "r"
        analString = "ratio"
    if tracerTools1.tracerDict[fieldToPlot].units.find("mol-1") != -1:
        analType = "r"
        analString = "ratio"


    #-----------------------------------------------------#
    # Model  Plotting

    if tracerTools1.tracerDict[fieldToPlot].slices[int(fileLevel)] == None:

        step = (maxValueBoth - minValueBoth) / 10.
        contours = tracerTools1.tracerDict[fieldToPlot].createTracerContoursFromMinMax \
            (minValueBoth, maxValueBoth, \
             step=float('{:0.2e}'.format(step)))
    else:
        contours = []
        for contour in tracerTools1.tracerDict[fieldToPlot].slices[fileLevel]:
            contours.append(float(contour))



            
    fig = plt.figure(figsize=(20,20))
    modelObject.createPlotObjects()


    

    plotTitle1 = model1SimName + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
        + " hPa  " + dateYearMonth
    modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid,
                                       modelObject.Y_grid, model1FieldArray,
                                       [minValueBoth, maxValueBoth],
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()],
                                       [modelObject.long[:].min(), modelObject.long[:].max()],
                                       "fuchsia", "darkred",
                                       221,
                                       plotTitle1,
                                       COLORMAP, tracerTools1.tracerDict[fieldToPlot].units,
                                       contourLevels=contours)

    plotTitle2 = model2SimName + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
        + " hPa  " + dateYearMonth
    modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid,
                                       modelObject.Y_grid, model2FieldArray,
                                       [minValueBoth, maxValueBoth],
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()],
                                       [modelObject.long[:].min(), modelObject.long[:].max()],
                                           "fuchsia", "darkred",
                                       222,
                                       plotTitle2, COLORMAP, tracerTools2.tracerDict[fieldToPlot].units,
                                       contourLevels=contours)

    analType = "s"
    analString = "diff"
    z_Model = modelObject.createComparisionLatLon(model1FieldArray, model2FieldArray, analType)


    if tracerTools1.tracerDict[fieldToPlot].diffSlices[fileLevel] == None:

        diffContourLevels = tracerTools1.tracerDict[fieldToPlot].createDiffContoursFromMinMax(z_Model.min(), z_Model.max())

    else:

        diffContourLevels = tracerTools1.tracerDict[fieldToPlot].diffSlices[fileLevel]


    plotTitle3 = analString + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
         + " hPa " + dateYearMonth
    modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid,
                                       modelObject.Y_grid, z_Model,
                                       [z_Model.min(), z_Model.max()],
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()],
                                       [modelObject.long[:].min(), modelObject.long[:].max()],
                                           "navy", "darkred",
                                       223,
                                       plotTitle3, "coolwarm", units=tracerTools1.tracerDict[fieldToPlot].units,
                                       labelContours=False,
                                       contourLevels=diffContourLevels)

    analType = "c"
    analString = "perc change"
    z_Model = None
    z_Model = modelObject.createComparisionLatLon(model1FieldArray, model2FieldArray, analType)


    if percChangeContours == "d":
        percDiffContours =  DEFAULT_PERCHANGE_CONTOURS

    else:
        print ("\nCreating percent difference contours")
        percDiffContours = tracerTools1.tracerDict[fieldToPlot].createPercChangeContoursFromMinMax\
            (z_Model.min(), z_Model.max())
    #    if percDiffContours [0] < -100.0:
    #        percDiffContours = DEFAULT_PERCHANGE_CONTOURS

    percDiffContours =  DEFAULT_PERCHANGE_CONTOURS


    plotTitle4 = analString + "     " + fieldToPlot + " @ " + str(int(fileLevel)) \
         + " hPa " + dateYearMonth
    modelObject.create2dSliceContours (fig, modelObject.baseMap, modelObject.X_grid,
                                       modelObject.Y_grid, z_Model,
                                       [z_Model.min(), z_Model.max()],
                                       [modelObject.lat[:].min(),modelObject.lat[:].max()],
                                       [modelObject.long[:].min(), modelObject.long[:].max()],
                                       "navy", "darkred",
                                       224,
                                       plotTitle4, "coolwarm", units="%", labelContours=False,
                                       contourLevels=percDiffContours)

    if not os.path.exists("plots"):
        os.mkdir("plots")
    file = "f"
    if file == "f":
        plt.savefig("plots/" + fieldToPlot + "-" + model1SimName + "_" + model2SimName +
                    "_" + str(dateYearMonth) + "_" +  str(int(fileLevel))
                    + "hPa.",
                    bbox_inches='tight')
    elif file == "s":
        plt.show()

    plt.clf()

    print("\nPlotted slice for : ", fieldToPlot, " to plots/ directory")


if __name__ == "__main__":
    main()
