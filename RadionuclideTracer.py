 #!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         May 18th 2020
#
# DESCRIPTION:
# This class represents a Radionuclide tracer.
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

class RadionuclideTracer(GenericTracer):

    
    tracerName = None
    tracerLongName = None
    tracerIntervalZM = None
    tracerIntervalSlices = None

    specificHumidity = None

    molWeight = None  # g/mol, float

    preConvert = False

    def testForPreConvert(self, tracerName, modelObject):

        if tracerName in modelObject.hdfData.variables:
            return (modelObject.hdfData[tracerName].units == "kg kg-1")
        else:
            return False


    #---------------------------------------------------------------------------  
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    #---------------------------------------------------------------------------  
    def __init__(self, tracerName, modelObject, parser, yAxisType, timeRecord, \
                 fileLevel, molWeight):

        self.tracerName = tracerName
        self.molWeight = molWeight
                
        GenericTracer.__init__(self, tracerName, modelObject, parser, \
                               timeRecord, fileLevel)


        if self.testForPreConvert (tracerName, modelObject):

            print ("\nConverting ", \
                   tracerName, " from ", modelObject.fileName, " to mol/mol")
            
            self.preConvert = True

            if "QV" not in modelObject.hdfData.variables:
                print ("\nERROR: Specific Humidity (QV) is required for conversions on: ", tracerName)
                sys.exit(-1)
            else:
                specificHumidity = modelObject.returnField ("QV", timeRecord)

            if fileLevel == "ZM":

                self.specificHumidity = specificHumidity 

            else:

                self.specificHumidity = modelObject.return2DSliceFromRefPressure \
                    (specificHumidity, fileLevel)

        self.yAxisType = yAxisType


    def preConversion (self, array, simName, convFac = None, newUnits = None):


        
        if self.preConvert == True:

            print ("")
            print ("Converting ", self.tracerName, "  to mol/mol")
            print ("")
                   
            convertArray = (array/(1.-self.specificHumidity)) * \
                ((self.MOL_WEIGHT_DRY_AIR)/(self.molWeight))
            self.units = "mol mol-1"
            
        else:
            convertArray = array 


        return convertArray
