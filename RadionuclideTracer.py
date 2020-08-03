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
    def __init__(self, tracerName, modelObject, parser, yAxisType, timeRecord, \
                 fileLevel, molWeight):

        self.tracerName = tracerName
        self.molWeight = molWeight
                
        GenericTracer.__init__(self, tracerName, modelObject, parser, \
                               timeRecord, fileLevel)

        if GenericTracer.testForPreConvert (self,modelObject.fileName):
        
            specificHumidity = modelObject.returnField ("QV", timeRecord)

            if fileLevel == "ZM":

                self.specificHumidity = specificHumidity 

            else:

                self.specificHumidity = modelObject.return2DSliceFromRefPressure \
                    (specificHumidity, fileLevel)

        self.yAxisType = yAxisType


    def preConversion (self, array, simName, convFac = None, newUnits = None):


        
        if GenericTracer.testForPreConvert (self, simName):

            print ("")
            print ("Converting ", self.tracerName, "  to mol/mol")
            print ("")
                   
            convertArray = (array/(1.-self.specificHumidity)) * \
                ((self.MOL_WEIGHT_DRY_AIR)/(self.molWeight))
            self.units = "mol mol-1"
            
        else:
            convertArray = array 


        return convertArray
