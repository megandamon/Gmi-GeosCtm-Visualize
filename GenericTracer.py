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

    MOL_WEIGHT_DRY_AIR = 29 #g/mol dry air)
    
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
        return int(math.ceil(x / 10.0)) * 10


    #---------------------------------------------------------------------------  
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    #---------------------------------------------------------------------------  
    def __init__(self, tracerName, modelObject, keyFile):

        keyLines = GenericModelPlotTools.readFileAndReturnFileLines(GenericModelPlotTools, keyFile)

        lineCount = 0
        while lineCount < len(keyLines)-1:

            tracerMetData = keyLines[lineCount].split(':') # split this line into metdata tokens

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
                        nextTracer = True 
                        return # after we've filled in this info, we can exit


            lineCount = lineCount + 1



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
         
      print ("New min/max values: ", minContour, maxContour, step)



      contours = arange(minContour,maxContour, step) 

      print ("contours: ", contours)
      print ("len contours: ", len(contours))



      returnContours = []
      for contour in contours:
          returnContours.append(float('{:0.2e}'.format(contour)))

      if maxContour > float(returnContours[-1]):
         returnContours.append(maxContour)

      
      return returnContours

    def createDiffContoursFromMinMax (self, minVal, maxVal):


        
        print ("received: ", minVal, maxVal)
        avg = (abs(minVal) + abs(maxVal))/2.
        minValAvg = -self.roundup(avg)
        maxValAvg = abs(minValAvg)

        print ("new: ", minValAvg, maxValAvg)

        range = int(maxValAvg + abs(minValAvg))
        print ("range: ", range)
        
        step = int(ceil(range / 12))

        print ("step: ", step)

        if step > 10: step = self.roundup(step)
        elif step > 1:  step = round(step)

        print ("step: ", step)

        diffContours = arange(minValAvg,maxValAvg,step)

        if 0 in diffContours:
            newContours = diffContours
        else:
            print ("No zero")
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
                else :
                    newContours.append(lev)
                
        
        if newContours[-1] < maxValAvg: 
            newContours2 = zeros(len(newContours)+1)
            count = 0
            for contour in newContours:
                newContours2[count] = contour
                count = count + 1
            newContours2[count] = maxValAvg
            diffContours = newContours2
        else:
            diffContours = newContours
            

        return diffContours
        

        if (minVal < 1 and maxVal > 10) or \
                (minVal < 100 and maxVal > 200):

            if abs(maxVal) > minVal:
                maxValAbs = int(abs(round(maxVal)))
                if maxValAbs >= 10: maxVal = self.roundup(maxValAbs)
                else: maxVal = maxValAbs
                minVal = -maxVal            
            else:
                minValRound = int(round(minVal))
                if minValRound >= 10: maxVal = self.roundup(minValRound)
                else: minVal = minValRound
                maxVal = -minVal

        else:
            if abs(minVal) < maxVal:
                maxValAbs = int(abs(round(minVal)))
                if maxValAbs >= 10: maxVal = self.roundup(maxValAbs)
                else: maxVal = maxValAbs
                minVal = -maxVal            
            else:
                maxValRound = int(round(maxVal))
                if maxValRound >= 10: maxVal = self.roundup(maxValRound)
                else: maxVal = maxValRound
                minVal = -maxVal

            
        print ("min/max vals: ", minVal, maxVal)
        sys.exit(0)
                
        range = int(maxVal+ abs(minVal))
        step = int(ceil(range / 12)) # 12 contours for now
        if step > 10: step = self.roundup(step)
        diffContours = arange(minVal,maxVal+step,step)
        if diffContours[-1] != maxVal: diffContours[-1] = maxVal
        
        return diffContours

    def createTracerContoursFromMinMax (self, minVal, maxVal, step=.5):

        return self.returnContoursFromMinMax (minVal, maxVal, step)


    def createTracerContours (self, array, step=.5):

       
        return self.returnContoursFromMinMax (array.min(), array.max(), step)


    def preConversion (self, array, simName, convFac = None, newUnits = None):
        print ("\nGeneric tracers do not perform pre-conversions!")

        return array




