#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Feb 18th 2020
#
# DESCRIPTION:
# This class represents a generic tracer and it's base information. 
#------------------------------------------------------------------------------

import re
import os
import sys
import random
import datetime
import calendar
import numpy
from numpy import *
from netCDF4 import Dataset

from GenericTracer import GenericTracer

class Be7Tracer(GenericTracer):

    
    tracerName = None
    tracerLongName = None
    tracerIntervalZM = None
    tracerIntervalSlices = None

    MOL_WEIGHT = 7 # g/mol

    #---------------------------------------------------------------------------  
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    #---------------------------------------------------------------------------  
    def __init__(self, tracerName, modelObject, keyFile, yAxisType):

        GenericTracer.__init__(self, tracerName, modelObject, keyFile)
        self.yAxisType = yAxisType

    def preConversion (self, array, simName, convFac = None, newUnits = None):

        if "TR_GOCART" in simName:
            print ("Converting Be7 to mol/mol")
            convertArray = array *((self.MOL_WEIGHT_DRY_AIR)/(self.MOL_WEIGHT))
            self.units = "mol mol-1"
            
        else:
            convertArray = array 

        return convertArray

    


    def createDiffContoursFromMinMaxNO (self, minVal, maxVal):

        print ("Be10 createDiff received: ", minVal, maxVal)

        diffContours = arange(minVal, maxVal, (maxVal-minVal)/12)

        newMin = float("%.g" % minVal)
        newMax = float("%.g" % maxVal)


        print ("Be10 createDiff mew min/max: ", minVal, maxVal, "...", newMin, newMax)

        minVal = newMin
        maxVal = newMax

        diffContours = arange(minVal, maxVal, (maxVal-minVal)/12)
        return diffContours
