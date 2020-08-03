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
import json
import numpy
import numpy as np


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

    PRECONVERT_SIMS = ['TR_GOCART', 'cycling', 'bench']

    def roundup(self, x):
        return int(np.ceil(x / 10.0)) * 10

    def testForPreConvert(self, string):

        for sim in self.PRECONVERT_SIMS:
            if sim in string:
                return True

        return False

        # ---------------------------------------------------------------------------

    # AUTHORS: Megan Damon NASA GSFC
    #
    # DESCRIPTION: 
    # Constructor routine.
    # ---------------------------------------------------------------------------
    def __init__(self, tracerName, modelObject, parser, timeRecord, fileLevel):

        self.name = tracerName
        self.long_name = parser.get(tracerName, 'long_name')
        self.lowLevel = parser.get(tracerName, 'zmlowlevel')
        self.highLevel = parser.get(tracerName, 'zmhighlevel')
        self.unitConvert = parser.get(tracerName, 'unitconversion')
        self.newUnit = parser.get(tracerName, 'unitname')
        self.zmContours = json.loads(parser.get(tracerName, "zmcontours"))
        self.z_zm = json.loads(parser.get(tracerName, "zmdiffcontours"))

        if self.unitConvert == 1:
            self.units = modelObject.hdfData.variables[tracerName].getncattr('units')
        else:
            self.units = self.newUnit

        # there is an undetermined number of slices for each tracer
        # so we must loop over them to discover what the slices are

        self.slices = {}
        self.diffSlices = {}

        for entry in dict(parser.items(tracerName)):
            if "slice" in entry:
                slicehPa = entry.split("_")[1]
                if "diffslice" not in entry:
                    self.slices[float(slicehPa)] = json.loads \
                        (parser.get(tracerName, entry))
                else:
                    self.diffSlices[float(slicehPa)] = json.loads \
                        (parser.get(tracerName, entry))

    def returnContoursFromMinMax(self, minVal, maxVal, step):
        minString = str(minVal)
        maxString = str(maxVal)

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

        contours = np.arange(minContour, maxContour, step)

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
        else:
            newMaxVal = absMaxVal

        if newMaxVal > 1.:
            roundNewMaxVal = round(newMaxVal)
            roundNewMinVal = -roundNewMaxVal
        else:
            roundNewMaxVal = round(newMaxVal, 2)
            roundNewMinVal = -roundNewMaxVal

        my_range = 2. * roundNewMaxVal

        if my_range > 2:
            step = int(np.ceil(my_range / 12))
        else:
            step = round(my_range / 12, 2)

        if step > 10:
            step = self.roundup(step)
        elif step > 1:
            step = round(step)

        diffContoursLeft = np.arange(roundNewMinVal, 0, step)
        diffContoursRight = -diffContoursLeft
        diffContoursRightRev = diffContoursRight[::-1]
        diffContours = numpy.concatenate([diffContoursLeft, diffContoursRightRev])

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
                elif lev > 0 and negative == True:
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
        if "e" in str(diffContours[0]):
            print("found e")

        newDiffContours = []
        for lev in diffContours:
            newDiffContours.append(round(lev, 3))

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
        if maxVal - minVal == 0:
            return [-1, -.5, -.25, 0, .25, .5, 1]

        avg = (abs(minVal) + abs(maxVal)) / 2.

        if "e" in str(avg):
            return self.returnContoursFromMinMax(-avg, avg, (avg * 2) / 12.)

        if avg > 1:
            minValAvg = -self.roundup(avg)
            maxValAvg = abs(minValAvg)
            range = int(maxValAvg + abs(minValAvg))
            step = int(np.ceil(range / 12))

        else:
            print(minVal, maxVal)

            if abs(minVal) > abs(maxVal):
                minValAvg = round(minVal, 5)
                maxValAvg = abs(minValAvg)
            else:
                minValAvg = -round(maxVal, 5)
                maxValAvg = maxVal

            range = maxValAvg + abs(minValAvg)
            step = range / 12.

        if step > 10:
            step = self.roundup(step)
        elif step > 1:
            step = round(step)

        diffContoursLeft = np.arange(minValAvg, 0., step)
        diffContoursRight = -diffContoursLeft
        diffContoursRightRev = diffContoursRight[::-1]
        diffContours = numpy.concatenate([diffContoursLeft, diffContoursRightRev])

        if 0 in diffContours:
            newContours = diffContours
        else:
            negative = False
            newContours = []
            for lev in diffContours:
                if lev < 0:
                    newContours.append(lev)
                    negative = True
                elif lev > 0 and negative == True:
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
        return array
