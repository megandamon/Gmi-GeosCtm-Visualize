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

from GenericModelPlotTools import GenericModelPlotTools



class GenericTracer:

    NAME_INDEX = 0
    LONGNAME_INDEX = 1
    LOWLEVEL_INDEX = 2
    HIGHLEVEL_INDEX = 3
    UNITCONVERT_INDEX = 4
    NEWUNIT_INDEX = 5
    ZMCONTOUR_INDEX = 6
    
    name = None
    long_name = None
    lowLevel = None
    highLevel = None
    unitConvert = None
    newUnit = None
    unit = None
    zmContours = None
    slices = None
    

    #---------------------------------------------------------------------------  
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    #---------------------------------------------------------------------------  
    def __init__(self, tracerName, modelObject, keyFile):

        print ('\n Receieved key file, will now read lines... ')

        keyLines = GenericModelPlotTools.readFileAndReturnFileLines(GenericModelPlotTools, keyFile)

        lineCount = 0
        while lineCount < len(keyLines)-1:

            tracerMetData = keyLines[lineCount].split(':') # split this line into metdata tokens

            if tracerMetData[0] == tracerName:
                print ("\nFound ", tracerName, " ! in key file. In while loop for lines.")

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

                if len(tracerMetData) > 6: # this tracer provide its own contour levels for zm

                    contourLevels = tracerMetData[self.ZMCONTOUR_INDEX].split(',')
                    levCount = 0
                    self.zmContours = []
                    for level in range(len(contourLevels)):
                        self.zmContours.append(contourLevels[levCount])
                        levCount = levCount + 1
        
                self.slices = {} # create new dict for the slices for this tracer
                
                nextTracer = False
                while nextTracer == False and lineCount < len(keyLines)-1:

                    lineCount = lineCount + 1
                    sliceLine = keyLines[lineCount].split(':') # split this line into "slice", numSlice, contours (maybe)

                    if sliceLine[0] == "\tslice": 

                        slice = float(sliceLine[1])

                        self.slices[slice] = None
                        if len(sliceLine) > 2: 

                            contourLevels = sliceLine[2].split(",")
                            levCount = 0
                            self.slices[slice] = []
                            for level in range (len(contourLevels)):
                                self.slices[slice].append(float(contourLevels[levCount]))
                                levCount = levCount + 1
                                                       
                    else:
                        print ("\nDid not find slice. Appear to be on to the next tracer")
                        nextTracer = True 
                        return # after we've filled in this info, we can exit


            lineCount = lineCount + 1

        print ("\nLeft loop")



    def returnContoursFromMinMax (self, minVal, maxVal, step):
      minString = str(minVal)
      maxString = str(maxVal)

      print ("Original min/max values: ", minString, maxString)

      if "e" in minString:

         minRound = '{:0.2e}'.format(minVal) # use only two numbers after decimal point
         
         minLHS = minRound.split('.')[0]
         minRHS = minRound.split('.')[1]
         minDec = minRHS.split('e')[0]
         minExp = minRHS.split('e')[1]

         decimalMinOrig = (str(minVal).split('.')[1].split('e')[0])
         if int(minDec[0:2]) > int(decimalMinOrig[0:2]): # check the rounded version
                                                         # make sure we didn't round up
            newMinDec = int(minDec) - 1 # round down instead
            newMin = minLHS + "." + str(newMinDec) + "e" + minExp
            minContour = float(newMin)

         else:
            minContour = float(minRound)

      else: 
         minContour = floor(minVal*100)/100
         minContour = round(minContour, 2)

         
      if "e" in maxString:
         
         maxRound = '{:0.2e}'.format(maxVal) # use only two numbers after decimal point
         
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
            maxContour =  float(maxRound)
      
      else:
         maxContour = round(maxVal, 2)
         if maxContour < maxVal:
            maxContour = maxContour + .01
            maxContour = round(maxContour, 2)
         
      print ("New min/max values: ", minContour, maxContour)

      contours = arange(minContour,maxContour, step) 


      returnContours = []
      for contour in contours:
          returnContours.append(float('{:0.1e}'.format(contour)))

      if maxContour > float(returnContours[-1]):
         returnContours.append(maxContour)

      
      return returnContours


    def createTracerContoursFromMinMax (self, minVal, maxVal, step=.5):

        return self.returnContoursFromMinMax (minVal, maxVal, step)


    def createTracerContours (self, array, step=.5):
       
        return self.returnContoursFromMinMax (array.min(), array.max(), step)




