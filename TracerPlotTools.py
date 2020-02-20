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
from GenericTracer import GenericTracer


class TracerPlotTools:


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, modelObject, keyFile):
      
      self.init = True 
      self.tracerDict = None
      if keyFile != None:
         self.tracerDict = self.createTracerDictFromKeyFileObjects(keyFile, modelObject)

   def createTracerDictFromKeyFileObjects (self, modelObject, keyFile):

      keyLines = GenericModelPlotTools.readFileAndReturnFileLines(GenericModelPlotTools, keyFile)

      self.tracerDict = {}
      lineCount = 0
      while lineCount < len(keyLines)-1:

         tracerMetData = keyLines[lineCount].split(':') # split this line into metdata tokens

         if 'slice' not in tracerMetData[0]:
         
            tracerName = tracerMetData[0]
            self.tracerDict[tracerName] = GenericTracer(tracerName, modelObject, keyFile)# create new tracer info
            
         lineCount = lineCount + 1
      
      return self.tracerDict




   def createTracerDictFromKeyFile (self, keyFile):
      keyLines = GenericModelPlotTools.readFileAndReturnFileLines(GenericModelPlotTools, keyFile)

      tracerDict = {}

      tracerCount = 0
      lineCount = 0

      while lineCount < len(keyLines)-1:

         tracerDict[tracerCount] = {} # create new tracer info

         tracerMetData = keyLines[lineCount].split(':') # split this line into metdata tokens

         tracerDict[tracerCount]['name'] = tracerMetData[0]
         tracerDict[tracerCount]['long_name'] = tracerMetData[1]
         tracerDict[tracerCount]['lowLevel'] = tracerMetData[2]
         tracerDict[tracerCount]['highLevel'] = tracerMetData[3]
         tracerDict[tracerCount]['unitConvert'] = tracerMetData[4]
         tracerDict[tracerCount]['newUnit'] = tracerMetData[5]
         tracerDict[tracerCount]['zmContours'] = None

         if len(tracerMetData) > 6: # this tracer provide its own contour levels for zm

            contourLevels = tracerMetData[6].split(',')
            levCount = 0
            tracerDict[tracerCount]['zmContours'] = []
            for level in range(len(contourLevels)):
               tracerDict[tracerCount]['zmContours'].append(contourLevels[levCount])
               levCount = levCount + 1

         tracerDict[tracerCount]['slices'] = {} # create new dict for the slices for this tracer

         nextTracer = False
         while nextTracer == False and lineCount < len (keyLines)-1:

            lineCount = lineCount + 1
            sliceLine = keyLines[lineCount].split(':') # split this line into "slice", numSlice, contours (maybe)


            if sliceLine[0] == "\tslice": 

               slice = float(sliceLine[1])
                      
               tracerDict[tracerCount]['slices'][slice] = None
               if len(sliceLine) > 2: 

                  contourLevels = sliceLine[2].split(",")
                  levCount = 0
                  tracerDict[tracerCount]['slices'][slice] = []
                  for level in range (len(contourLevels)):
                     tracerDict[tracerCount]['slices'][slice].append(float(contourLevels[levCount]))
                     levCount = levCount + 1
                                                       
            else:
               tracerCount = tracerCount + 1
               nextTracer = True
               continue

      return tracerDict

