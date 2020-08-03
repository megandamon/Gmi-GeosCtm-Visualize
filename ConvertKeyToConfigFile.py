#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         August 2 2020
#------------------------------------------------------------------------------

import sys
from GenericModelPlotTools import GenericModelPlotTools
import configparser

class GenericTracer:

    NAME_INDEX = 0
    LONGNAME_INDEX = 1
    LOWLEVEL_INDEX = 2
    HIGHLEVEL_INDEX = 3
    UNITCONVERT_INDEX = 4
    NEWUNIT_INDEX = 5
    ZMCONTOUR_INDEX = 6

    MOL_WEIGHT_DRY_AIR = 28.965  #g/mol dry air)
    MOL_WEIGHT_H2O = 18.015
    
    name = None
    long_name = None
    lowLevel = None
    highLevel = None
    unitConvert = None
    newUnit = None
    units = None
    zmContours = None
    slices = None
    yAxisType = 'log'


def createGenericTracer (tracerDict, tracerName, keyLines):

    tracerDict[tracerName] = GenericTracer()

    foundzZm = False
    lineCount = 0

    while lineCount < len(keyLines)-1:

        tracerMetData = keyLines[lineCount].split(':') 

        if tracerMetData[0] == tracerName:

            tracerDict[tracerName].name = \
                tracerMetData[tracerDict[tracerName].NAME_INDEX]

            tracerDict[tracerName].long_name = \
                tracerMetData[tracerDict[tracerName].LONGNAME_INDEX]
            tracerDict[tracerName].lowLevel = \
                tracerMetData[tracerDict[tracerName].LOWLEVEL_INDEX]
            tracerDict[tracerName].highLevel = \
                tracerMetData[tracerDict[tracerName].HIGHLEVEL_INDEX]
            tracerDict[tracerName].unitConvert = \
                tracerMetData[tracerDict[tracerName].UNITCONVERT_INDEX]
            tracerDict[tracerName].newUnit = \
                tracerMetData[tracerDict[tracerName].NEWUNIT_INDEX]
            tracerDict[tracerName].zmContours = None

            tracerDict[tracerName].units = tracerDict[tracerName].newUnit

            # this tracer provide its own contour levels for zm
            if len(tracerMetData) > 6: 

                contourLevels = tracerMetData \
                    [tracerDict[tracerName].ZMCONTOUR_INDEX].split(',')
                levCount = 0
                tracerDict[tracerName].zmContours = []
                for level in range(len(contourLevels)):
                    tracerDict[tracerName].zmContours.append \
                        (float(contourLevels[levCount]))
                    levCount = levCount + 1

            # create new dict for the slices for this tracer
            tracerDict[tracerName].slices = {}

            nextTracer = False
            while nextTracer == False and lineCount < len(keyLines)-1:

                lineCount = lineCount + 1
                
                # split this line into "slice", numSlice, contours (maybe)
                sliceLine = keyLines[lineCount].split(':')

                if "slice" in sliceLine[0] and "z_slice" not in sliceLine[0]:
                    slice = float(sliceLine[1])
                    
                    tracerDict[tracerName].slices[slice] = []
                    if len(sliceLine) > 2: 

                        contourLevels = sliceLine[2].split(",")
                        levCount = 0
                        tracerDict[tracerName].slices[slice] = []
                        for level in range (len(contourLevels)):
                            tracerDict[tracerName].slices[slice].append \
                                (float(contourLevels[levCount]))
                            levCount = levCount + 1

                elif "z_slice" in sliceLine[0]:
                    break

            # need to back up and let the next loop read the zslices
            lineCount = lineCount - 1 

            # create new dict for the difference contours for each slice 
            tracerDict[tracerName].diffSlices = {}
            
            nextTracer = False

            while nextTracer == False and lineCount < len(keyLines)-1:

                lineCount = lineCount + 1

                # split this line into "z_slice", numSlice, contours (maybe)
                sliceLine = keyLines[lineCount].split(':')

                if "z_slice" in sliceLine[0]:
                    
                    slice = float(sliceLine[1])

                    
                    tracerDict[tracerName].diffSlices[slice] = []
                    
                    if len(sliceLine) > 2:
                        contourLevels = sliceLine[2].split(",")
                        levCount = 0

                        for level in range (len(contourLevels)):
                            tracerDict[tracerName].diffSlices[slice].append \
                                (float(contourLevels[levCount]))
                            levCount = levCount + 1

                elif "z_zm" in sliceLine[0]:
                    break

            tracerDict[tracerName].z_zm = []
            if len(sliceLine) > 1: 

                contourLevels = sliceLine[1].split(",")

                levCount = 0

                if len(contourLevels) > 1:
                    for level in range (len(contourLevels)):
                        tracerDict[tracerName].z_zm.append \
                            (float(contourLevels[levCount]))
                        levCount = levCount + 1

                else:
                    tracerDict[tracerName].z_zm = []



            return tracerDict

        lineCount = lineCount + 1


def createTracerDictFromKeyFileObjects (keyLines):

    tracerDict = {}
    lineCount = 0
    while lineCount < len(keyLines)-1:

         # split this line into metdata tokens
        tracerMetData = keyLines[lineCount].split(':')

        if 'slice' not in tracerMetData[0] and 'z_zm' not in tracerMetData[0]:

            tracerName = tracerMetData[0]
            tracerDict = createGenericTracer (tracerDict, tracerName, keyLines)
            
        lineCount = lineCount + 1

    return tracerDict








keyFile = "Tracers.GEOS.TR-bench.diffSlices.list"
keyLines = GenericModelPlotTools.readFileAndReturnFileLines \
    (GenericModelPlotTools, keyFile)


tracerDictMain = createTracerDictFromKeyFileObjects (keyLines)




config = configparser.RawConfigParser()





for tracer in tracerDictMain:
    
    print ("Adding config section for: ", tracerDictMain[tracer].name)

    info = tracerDictMain[tracer]

    config.add_section(info.name)
    config.set(info.name, 'long_name', info.long_name)
    config.set(info.name, 'zmLowLevel', info.lowLevel)
    config.set(info.name, 'zmHighLevel', info.highLevel)
    config.set(info.name, 'unitConversion', info.unitConvert)
    config.set(info.name, 'unitName', info.units)
    config.set(info.name, 'zmContours', info.zmContours[:])
    config.set(info.name, 'zmDiffContours', info.z_zm[:])

    for slice in info.slices:
        config.set(info.name, "slice_" + str(int(slice)), info.slices[slice])
        config.set(info.name, "diffslice_" + str(int(slice)), info.diffSlices[slice])
    

with open('example.cfg', 'w') as configfile:
    config.write(configfile)




      
