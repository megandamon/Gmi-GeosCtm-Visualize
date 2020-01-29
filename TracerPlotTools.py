#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         October 22 2019
#
# DESCRIPTION:
# This class provides functionality for tracer-related operations.
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

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

import math
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap

from GenericModelPlotTools import GenericModelPlotTools


class TracerPlotTools:


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, keyFile=None):
      
      self.init = True 
      self.tracerDict = None
      if keyFile != None:
         self.tracerDict = self.createTracerDictFromKeyFile(keyFile)


   def setLevelInfo (self, fieldToPlot):

      count = 0
      found = False
      for tracer in range(len(self.tracerDict)):
    
         if fieldToPlot.lower() == self.tracerDict[count]["name"].lower():

            self.lowerLevel = self.tracerDict[count]['lowLevel']
            self.upperLevel = self.tracerDict[count]['highLevel']

            print ()
            print ("Found ", fieldToPlot, ", using levels: ", self.lowerLevel, \
                      self.upperLevel)
            print ()

            found = True
            break

         count = count + 1

      if found == False:
         print ()
         print ("ERROR: did not find: ", fieldToPlot, " in the key file: ", self.keyFile)
         print ()
         sys.exit(0)



   def setUnitInfo (self, fieldToPlot):
      
      count = 0
      found = False
      for tracer in range(len(self.tracerDict)):
    
         if fieldToPlot.lower() == self.tracerDict[count]["name"].lower():

            self.contourLevels = self.tracerDict[count]['contourLevels']
            self.unitConvert = self.tracerDict[count]['unitConvert']
            self.newUnit = self.tracerDict[count]['newUnit']
            self.longName = self.tracerDict[count]['long_name']
            print ()
            print ("Found ", fieldToPlot, ", using units: ", self.newUnit, \
                      " with conversion: ", self.unitConvert)
            print ()

            found = True
            break

         count = count + 1

      if found == False:
         print ()
         print ("ERROR: did not find: ", fieldToPlot, " in the key file: ", self.keyFile)
         print ()
         sys.exit(0)


      print ()
      if self.unitConvert == 1:
         self.units = model1Object.hdfData.variables[fieldToPlot].getncattr('units')
      else:
         self.units = self.newUnit
      print ("units: ", self.units)
      print ()



   def createTracerDictFromKeyFile (self, keyFile):
      keyLines = GenericModelPlotTools.readFileAndReturnFileLines(GenericModelPlotTools, keyFile)

      tracerDict = {}
      count = 0
      for line in keyLines:

         tracerDict[count] = {} # create new tracer info

         tracerMetData = line.split(':') # split this line into metdata tokens


         tracerDict[count]['name'] = tracerMetData[0]
         tracerDict[count]['long_name'] = tracerMetData[1]
         tracerDict[count]['slices'] = []
         
         tracer2DSlices = tracerMetData[2].split(',') # split 3r token into list of levels

         sliceCount = 0 # add a list item for eacxh slice
         for slice in range(len(tracer2DSlices)):
            tracerDict[count]['slices'].append(tracer2DSlices[sliceCount])
            sliceCount = sliceCount + 1


         tracerDict[count]['lowLevel'] = tracerMetData[3]
         tracerDict[count]['highLevel'] = tracerMetData[4]
    
         tracerDict[count]['unitConvert'] = tracerMetData[5]
         tracerDict[count]['newUnit'] = tracerMetData[6]

         tracerDict[count]['contourLevels'] = []

         if len(tracerMetData) > 7: # this tracer provide its own contour levels
            contourLevels = tracerMetData[7].split(',')
            levCount = 0
            for level in range(len(contourLevels)):
               tracerDict[count]['contourLevels'].append(contourLevels[levCount])
               levCount = levCount + 1

         count = count + 1

      return tracerDict

