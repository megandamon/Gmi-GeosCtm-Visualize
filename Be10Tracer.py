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
from numpy import arange
from GenericTracer import GenericTracer


class Be10Tracer(GenericTracer):
    tracerName = None
    tracerLongName = None
    tracerIntervalZM = None
    tracerIntervalSlices = None

    MOL_WEIGHT = 10.  # g/mol

    # ---------------------------------------------------------------------------
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    # ---------------------------------------------------------------------------
    def __init__(self, tracerName, modelObject, keyFile, yAxisType, timeRecord, fileLevel):
        GenericTracer.__init__(self, tracerName, modelObject, keyFile, timeRecord, fileLevel)

        print(dir(modelObject))

        if "TR_GOCART" in modelObject.fileName or "cycling" in modelObject.fileName:
            print("Be10 tracer needs specific humidity")
            print(modelObject.time)
            self.specificHumidity = modelObject.returnField("QV", timeRecord)

            print("")
            print("Min/max QV: ", self.specificHumidity.min(), self.specificHumidity.max())
            print("")

        self.yAxisType = yAxisType

    def preConversion(self, array, simName, convFac=None, newUnits=None):

        print("Min/max incoming array: ", array.min(), array.max())

        #         if "MERRA2_GMI" in simName:

        #             print ("Converting mol mol-1 to kg kg-1 or VMR to MMR")

        #             # VMR_m  *   ( 1  +  ((Q/1- Q) * (MW_dry_air/MW_H2O))  )  =   VMR_d

        #             VMR_d = array * (1. + ((self.specificHumidity/(1. - self.specificHumidity)) * \
        #                                        (self.MOL_WEIGHT_DRY_AIR/self.MOL_WEIGHT_H2O)) )

        # #            print ("Min/max VMR_D: ", VMR_d.min(), VMR_d.max())
        # #            print ("MOL_WEIGHT: , ", self.MOL_WEIGHT)
        # #            print ("MOL_WEIGHT_DRY_AIR: ", self.MOL_WEIGHT_DRY_AIR)

        #             MMR_d = VMR_d * (self.MOL_WEIGHT/self.MOL_WEIGHT_DRY_AIR)

        # #            print ("Min/max MMR_D: ", MMR_d.min(), VMR_d.max())

        # #            print ("Min/max QV: ", self.specificHumidity.min(), self.specificHumidity.max())

        #             MMR_m = MMR_d * (1.-self.specificHumidity)

        #             convertArray = MMR_m

        #             self.units = "kg kg-1"

        if "TR_GOCART" in simName or "cycling" in simName:

            print("Converting Be10 to mol/mol")
            #            convertArray = array *((self.MOL_WEIGHT_DRY_AIR)/(self.MOL_WEIGHT))
            convertArray = (array / (1. - self.specificHumidity)) * (self.MOL_WEIGHT_DRY_AIR / self.MOL_WEIGHT)
            self.units = "mol mol-1"

        else:
            convertArray = array

        print("Min/max outgoing array: ", convertArray.min(), convertArray.max())

        return convertArray

    def createDiffContoursFromMinMaxBe10(self, minVal, maxVal):

        print("Be10 createDiff received: ", minVal, maxVal)

        newMin = float("%.g" % minVal)
        newMax = float("%.g" % maxVal)

        print("Be10 createDiff mew min/max: ", minVal, maxVal, "...", newMin, newMax)

        minVal = newMin
        maxVal = newMax

        diffContours = arange(minVal, maxVal, (maxVal - minVal) / 12)

        return diffContours
