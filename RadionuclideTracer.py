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

    #---------------------------------------------------------------------------  
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    #---------------------------------------------------------------------------  
    def __init__(self, tracerName, modelObject, keyFile, yAxisType, timeRecord, fileLevel, molWeight):

        self.tracerName = tracerName
        self.molWeight = molWeight
                
        GenericTracer.__init__(self, tracerName, modelObject, keyFile, timeRecord, fileLevel)

        if "TR_GOCART" in modelObject.fileName or "cycling" in modelObject.fileName or \
           "bench_i329" in modelObject.fileName:

            print (self.tracerName, " needs specific humidity for conversions.")


            specificHumidity = modelObject.returnField ("QV", timeRecord)

            if fileLevel == "ZM":

#                llIndex1 = modelObject.findLevelFromArray(modelObject.lev, float(self.lowLevel))
#                ulIndex1 = modelObject.findLevelFromArray(modelObject.lev, float(self.highLevel))
                self.specificHumidity = specificHumidity #mean(specificHumidity[llIndex1:ulIndex1+1, :, :], axis=2)

            else:
                print ("")
                print ("Extracting level: ", fileLevel, " from specific humidity")
                print ("")

                self.specificHumidity = modelObject.return2DSliceFromRefPressure (specificHumidity, fileLevel)

            print ("")
            print ("Min/max QV for RadionuclineTracer: ", \
                       self.specificHumidity.min(), self.specificHumidity.max())
            print ("")

        self.yAxisType = yAxisType

    def preConversion (self, array, simName, convFac = None, newUnits = None):


        print ("")
        print ("Min/max incoming array for Radionucline: ", array.min(), array.max())
        print ("Array shape preConversion: ", array.shape)
        print ("")

        if "TR_GOCART" in simName or "cycling" in simName:

            print ("")
            print ("Converting ", self.tracerName, "  to mol/mol")
            print ("QV shape: ", self.specificHumidity.shape)
            print ("")
                   
            convertArray = (array/(1.-self.specificHumidity)) *((self.MOL_WEIGHT_DRY_AIR)/(self.molWeight))
            self.units = "mol mol-1"
            
        else:
            convertArray = array 


        print ("")
        print ("Min/max outgoing array: ", convertArray.min(), convertArray.max())
        print ("")

        return convertArray
