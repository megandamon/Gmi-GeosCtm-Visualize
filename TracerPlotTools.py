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

from GenericModelPlotTools import GenericModelPlotTools

from GenericTracer import GenericTracer

from RadionuclideTracer import RadionuclideTracer

from AoaBlTracer import AoaBlTracer
from Be10Tracer import Be10Tracer
from Be10sTracer import Be10sTracer
from Be7Tracer import Be7Tracer
from Be7sTracer import Be7sTracer
from Pb210Tracer import Pb210Tracer
from Pb210sTracer import Pb210sTracer
from Rn222Tracer import Rn222Tracer

class TracerPlotTools:


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, modelObject, keyFile, timeRecord, fileLevel):
      
      self.init = True 
      self.tracerDict = None
      self.timeRecord = timeRecord
      self.fileLevel = fileLevel

      if keyFile != None:
         self.tracerDict = self.createTracerDictFromKeyFileObjects(modelObject, keyFile, timeRecord, fileLevel)

   def createTracerDictFromKeyFileObjects (self, modelObject, keyFile, timeRecord, fileLevel):

      keyLines = GenericModelPlotTools.readFileAndReturnFileLines(GenericModelPlotTools, keyFile)

      self.tracerDict = {}
      lineCount = 0
      while lineCount < len(keyLines)-1:

         tracerMetData = keyLines[lineCount].split(':') # split this line into metdata tokens

         if 'slice' not in tracerMetData[0] and 'z_zm' not in tracerMetData[0]:


            tracerName = tracerMetData[0]


            if tracerName.lower() == "aoa_bl":
               self.tracerDict[tracerName] = AoaBlTracer(tracerName, modelObject, keyFile, 'linear', timeRecord,fileLevel)

            elif tracerName.lower() == "be7" or tracerName.lower() == "be7s":

               print ("Calling RadionuclideTracer for: ", tracerName)

               self.tracerDict[tracerName] = RadionuclideTracer \
                   (tracerName, modelObject, keyFile, 'log', timeRecord, fileLevel, 7.)

            elif tracerName.lower() == "be10" or tracerName.lower() == "be10s":

               print ("Calling RadionuclideTracer for: ", tracerName)

               self.tracerDict[tracerName] = RadionuclideTracer \
                   (tracerName, modelObject, keyFile, 'log', timeRecord, fileLevel, 10.)

            elif tracerName.lower() == "pb210" or tracerName.lower() == "pb210s":
               
               print ("Calling RadionuclideTracer for: ", tracerName)

               self.tracerDict[tracerName] = RadionuclideTracer \
                   (tracerName, modelObject, keyFile, 'log', timeRecord, fileLevel, 210.)

            elif tracerName.lower() == "rn222":

               print ("Calling RadionuclideTracer for: ", tracerName)

               self.tracerDict[tracerName] = RadionuclideTracer \
                   (tracerName, modelObject, keyFile, 'log', timeRecord, fileLevel, 222.)

            else:
               self.tracerDict[tracerName] = GenericTracer(tracerName, modelObject, keyFile, timeRecord,fileLevel) # create new tracer info
            
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

