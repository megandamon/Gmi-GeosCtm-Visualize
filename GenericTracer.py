#!/usr/bin/python

# ------------------------------------------------------------------------------
# NASA/GSFC
# ------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Feb 18th 2020
#
# DESCRIPTION:
# This class represents a generic tracer and it's base information.
# ------------------------------------------------------------------------------
import numpy as np

from GenericModelPlotTools import GenericModelPlotTools


class GenericTracer:
    NAME_INDEX = 0
    LONGNAME_INDEX = 1
    LOWLEVEL_INDEX = 2
    HIGHLEVEL_INDEX = 3
    UNITCONVERT_INDEX = 4
    NEWUNIT_INDEX = 5
    ZMCONTOUR_INDEX = 6

    MOL_WEIGHT_DRY_AIR = 28.965  # g/mol dry air)
    MOL_WEIGHT_H2O = 18.015

    name = None
    long_name = None
    lowLevel = None
    highLevel = None
    unitConvert = None
    newUnit = None
    unit = None
    zmContours = None
    slices = None
    yAxisType = 'log'

    def roundup(self, x):
        return int(np.ceil(x / 10.0)) * 10

    # ---------------------------------------------------------------------------
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    # ---------------------------------------------------------------------------
    def __init__(self, tracerName, modelObject, keyFile, timeRecord, fileLevel):

        keyLines = GenericModelPlotTools.readFileAndReturnFileLines(GenericModelPlotTools, keyFile)

        #        print ("key file lines: ", len(keyLines) -1)
        #        print ("tracer name: ", tracerName)

        foundzZm = False

        lineCount = 0

        while lineCount < len(keyLines) - 1:

            tracerMetData = keyLines[lineCount].split(':')  # split this line into metdata tokens
            #            print ("Tracer met data: ", tracerMetData)

            if tracerMetData[0] == tracerName:

                self.name = tracerMetData[self.NAME_INDEX]
                self.long_name = tracerMetData[self.LONGNAME_INDEX]
                self.lowLevel = tracerMetData[self.LOWLEVEL_INDEX]
                self.highLevel = tracerMetData[self.HIGHLEVEL_INDEX]
                self.unitConvert = tracerMetData[self.UNITCONVERT_INDEX]
                self.newUnit = tracerMetData[self.NEWUNIT_INDEX]
                self.zmContours = None

                if self.unitConvert == 1:
                    self.units = modelObject.hdfData.variables[tracerName].getncattr('units')
                else:
                    self.units = self.newUnit

                if len(tracerMetData) > 6:  # this tracer provide its own contour levels for zm

                    contourLevels = tracerMetData[self.ZMCONTOUR_INDEX].split(',')
                    levCount = 0
                    self.zmContours = []
                    for level in range(len(contourLevels)):
                        self.zmContours.append(contourLevels[levCount])
                        levCount = levCount + 1

                self.slices = {}  # create new dict for the slices for this tracer

                nextTracer = False
                while not nextTracer and lineCount < len(keyLines) - 1:

                    lineCount = lineCount + 1
                    sliceLine = keyLines[lineCount].split(
                        ':')  # split this line into "slice", numSlice, contours (maybe)

                    #                   print ("")
                    #                   print (sliceLine)
                    #                   print (sliceLine[0])
                    #                   print ("")

                    if "slice" in sliceLine[0] and "z_slice" not in sliceLine[0]:

                        #                      print ("")
                        #                      print ("Found regular slice")
                        #                      print ("")

                        sliver = float(sliceLine[1])

                        self.slices[sliver] = None
                        if len(sliceLine) > 2:

                            contourLevels = sliceLine[2].split(",")
                            levCount = 0
                            self.slices[sliver] = []
                            for level in range(len(contourLevels)):
                                self.slices[sliver].append(float(contourLevels[levCount]))
                                levCount = levCount + 1

                    elif "z_slice" in sliceLine[0]:
                        #                     print ("")
                        #                     print ("foudn first z_slice, breaking")
                        #                     print ("")
                        break

                #             print ("")
                #             print ("creating diffSlices")
                #             print ("")

                lineCount = lineCount - 1  # need to back up and let the next loop read the zslices

                self.diffSlices = {}  # create new dict for the difference contours for each slice
                nextTracer = False

                sliceLine = 0
                while not nextTracer and lineCount < len(keyLines) - 1:

                    lineCount = lineCount + 1
                    sliceLine = keyLines[lineCount].split(
                        ':')  # split this line into "z_slice", numSlice, contours (maybe)

                    if "z_slice" in sliceLine[0]:

                        #                         print ("")
                        #                         print ("Found z_slice")
                        #                         print ("")

                        sliver = float(sliceLine[1])

                        #                        print ("")
                        #                        print ("zslice: ", slice)
                        #                        print ("")

                        self.diffSlices[sliver] = None
                        if len(sliceLine) > 2:

                            contourLevels = sliceLine[2].split(",")
                            levCount = 0
                            self.diffSlices[sliver] = []
                            for level in range(len(contourLevels)):
                                self.diffSlices[sliver].append(float(contourLevels[levCount]))
                                levCount = levCount + 1

                    elif "z_zm" in sliceLine[0]:
                        #                        print ("")
                        #                        print ("foudn z_zm, breaking")
                        #                        print ("")
                        break

                #                print (sliceLine, "length of sliceLine: ", len(sliceLine))
                self.z_zm = []
                if len(sliceLine) > 1:

                    contourLevels = sliceLine[1].split(",")
                    #                    print (contourLevels, 'length of contourLevels: ', len(contourLevels))
                    levCount = 0
                    if len(contourLevels) > 1:
                        for level in range(len(contourLevels)):
                            self.z_zm.append(float(contourLevels[levCount]))
                            levCount = levCount + 1
                    else:
                        self.z_zm = None

                #               print ("Before return: ", self.z_zm)
                return

            lineCount = lineCount + 1

    def returnContoursFromMinMax(self, minVal, maxVal, step):
        minString = str(minVal)
        maxString = str(maxVal)

        print("Original min/max values: ", minString, maxString)

        if "e" in minString:

            minRound = '{:0.2e}'.format(minVal)  # use only two numbers after decimal point

            minLHS = minRound.split('.')[0]
            minRHS = minRound.split('.')[1]
            minDec = minRHS.split('e')[0]
            minExp = minRHS.split('e')[1]

            decimalMinOrig = (str(minVal).split('.')[1].split('e')[0])
            if int(minDec[0:2]) > int(decimalMinOrig[0:2]):  # check the rounded version
                # make sure we didn't round up
                newMinDec = int(minDec) - 1  # round down instead
                newMin = minLHS + "." + str(newMinDec) + "e" + minExp
                minContour = float(newMin)

            else:
                minContour = float(minRound)

        else:
            minContour = np.floor(minVal * 100) / 100
            minContour = round(minContour, 2)

        if "e" in maxString:

            maxRound = '{:0.2e}'.format(maxVal)  # use only two numbers after decimal point

            maxLHS = maxRound.split('.')[0]
            maxRHS = maxRound.split('.')[1]
            maxDec = maxRHS.split('e')[0]
            maxExp = maxRHS.split('e')[1]

            decimalMaxOrig = (str(maxVal).split('.')[1].split('e')[0])
            floatMaxDec = float("0." + maxDec)
            floatMaxDecOrig = float("0." + decimalMaxOrig)

            if floatMaxDec < floatMaxDecOrig:

                floatMaxDec = floatMaxDec + .01
                newMaxString = maxLHS + "." + str(floatMaxDec).split(".")[1] + "e" + maxExp
                maxContour = float(newMaxString)
            else:
                maxContour = float(maxRound)

        else:
            maxContour = round(maxVal, 2)
            if maxContour < maxVal:
                maxContour = maxContour + .01
                maxContour = round(maxContour, 2)

        print("New min/max values: ", minContour, maxContour, step)

        contours = np.arange(minContour, maxContour, step)

        print("contours: ", contours)
        print("len contours: ", len(contours))

        returnContours = []
        for contour in contours:
            returnContours.append(float('{:0.2e}'.format(contour)))

        if maxContour > float(returnContours[-1]):
            returnContours.append(maxContour)

        return returnContours

    def createPercChangeContoursFromMinMax(self, minVal, maxVal):

        if maxVal - minVal == 0:
            return [-1, -.5, -.25, 0, .25, .5, 1]

        absMinVal = abs(minVal)
        absMaxVal = abs(maxVal)

        if absMinVal > absMaxVal:
            newMaxVal = absMinVal
            newMinVal = -absMinVal
        else:
            newMaxVal = absMaxVal
            newMinVal = -absMaxVal

        print("new max: ", newMaxVal)

        if newMaxVal > 1.:
            roundNewMaxVal = round(newMaxVal)
            roundNewMinVal = -roundNewMaxVal
        else:
            roundNewMaxVal = round(newMaxVal, 2)
            roundNewMinVal = -roundNewMaxVal

        print("old: ", minVal, maxVal)
        print("new: ", newMinVal, newMaxVal)
        print("round: ", -roundNewMaxVal, roundNewMaxVal)

        rng = 2. * roundNewMaxVal
        print("range: ", rng)

        if rng > 2:
            step = int(np.ceil(rng / 12))
        else:
            step = round(rng / 12, 2)

        if step > 10:
            step = self.roundup(step)
        elif step > 1:
            step = round(step)

        print("step: ", step)

        diffContoursLeft = np.arange(roundNewMinVal, 0, step)
        diffContoursRight = -diffContoursLeft
        diffContoursRightRev = diffContoursRight[::-1]

        print(diffContoursLeft)
        print(diffContoursRightRev)

        diffContours = np.concatenate([diffContoursLeft, diffContoursRightRev])
        print(diffContours)

        if 0 in diffContours:
            newContours = diffContours
        else:
            print("No zero")
            negative = False
            newContours = []
            for lev in diffContours:
                if lev < 0:
                    newContours.append(lev)
                    negative = True
                elif lev > 0 and negative:
                    newContours.append(0)
                    newContours.append(lev)
                    negative = False
                else:
                    newContours.append(lev)

        if newContours[-1] < roundNewMaxVal:
            newContours2 = np.zeros(len(newContours) + 1)
            count = 0
            for contour in newContours:
                newContours2[count] = contour
                count = count + 1
            newContours2[count] = roundNewMaxVal
            diffContours = newContours2
        else:
            diffContours = newContours

        # convert from sci notation to float
        print("oth element diffContours: ", str(diffContours[0]))
        if "e" in str(diffContours[0]):
            print("found e")

        newDiffContours = []
        for lev in diffContours:
            newDiffContours.append(round(lev, 3))

        print(newDiffContours)

        # remove double zeros 
        newNewDiffContours = []
        foundZero = False
        for lev in newDiffContours:
            if lev == 0.0:
                if not foundZero:
                    foundZero = True
                    newNewDiffContours.append(lev)
            else:
                newNewDiffContours.append(lev)

        # remove double last elements
        if newNewDiffContours[-1] == newNewDiffContours[-2]:
            del newNewDiffContours[-1]

        return newNewDiffContours

    def createDiffContoursFromMinMax(self, minVal, maxVal):

        #        print ("received: ", minVal, maxVal)

        if maxVal - minVal == 0:
            return [-1, -.5, -.25, 0, .25, .5, 1]

        avg = (abs(minVal) + abs(maxVal)) / 2.

        #        print ("avg: ", avg)

        if "e" in str(avg):
            return self.returnContoursFromMinMax(-avg, avg, (avg * 2) / 12.)

        if avg > 1:
            minValAvg = -self.roundup(avg)
            maxValAvg = abs(minValAvg)
            rng = int(maxValAvg + abs(minValAvg))
            step = int(np.ceil(rng / 12))

        else:
            #            print ("avg < 1")
            print(minVal, maxVal)

            if abs(minVal) > abs(maxVal):
                minValAvg = round(minVal, 5)
                maxValAvg = abs(minValAvg)
            else:
                minValAvg = -round(maxVal, 5)
                maxValAvg = maxVal

            rng = maxValAvg + abs(minValAvg)
            #            print ("range: ", range)
            step = rng / 12.

        print(minValAvg, maxValAvg, rng)

        if step > 10:
            step = self.roundup(step)
        elif step > 1:
            step = round(step)

        #        print ("step: ", step)

        diffContoursLeft = np.arange(minValAvg, 0., step)
        diffContoursRight = -diffContoursLeft
        diffContoursRightRev = diffContoursRight[::-1]

        #        print (diffContoursLeft)
        #        print (diffContoursRightRev)

        diffContours = np.concatenate([diffContoursLeft, diffContoursRightRev])
        #        print (diffContours)

        if 0 in diffContours:
            newContours = diffContours
        else:
            #            print ("No zero")
            negative = False
            newContours = []
            for lev in diffContours:
                if lev < 0:
                    newContours.append(lev)
                    negative = True
                elif lev > 0 and negative:
                    newContours.append(0)
                    newContours.append(lev)
                    negative = False
                else:
                    newContours.append(lev)

        if newContours[-1] < maxValAvg:
            newContours2 = np.zeros(len(newContours) + 1)
            count = 0
            for contour in newContours:
                newContours2[count] = contour
                count = count + 1
            newContours2[count] = maxValAvg
            diffContours = newContours2
        else:
            diffContours = newContours

        return diffContours

    def createTracerContoursFromMinMax(self, minVal, maxVal, step=.5):

        return self.returnContoursFromMinMax(minVal, maxVal, step)

    def createTracerContours(self, array, step=.5):

        return self.returnContoursFromMinMax(array.min(), array.max(), step)

    def preConversion(self, array, simName, convFac=None, newUnits=None):
        #        print ("\nGeneric tracers do not perform pre-conversions!")

        return array
