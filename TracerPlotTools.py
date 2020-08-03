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

from configparser import ConfigParser
import json
import sys

class TracerPlotTools:


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, modelObject, keyFile, timeRecord, fileLevel):
      
      self.init = True 
      self.tracerDict = {}
      self.timeRecord = timeRecord
      self.fileLevel = fileLevel
      
      if keyFile != None:
         self.createTracerDict \
            (modelObject, keyFile, timeRecord, fileLevel)

      else:
         print("\nWARNING: keyFile is None. Tracer dict will not be created!")


   def createTracerDict (self, modelObject, keyFile, \
                                           timeRecord, fileLevel):

      parser = ConfigParser()
      parser.read(keyFile)
      
      for tracer in parser.sections():

         tracerName = tracer

         if tracerName.lower() == "aoa_bl":

            self.tracerDict[tracerName] = AoaBlTracer \
               (tracerName, modelObject, parser, 'linear', timeRecord,fileLevel)


         elif tracerName.lower() == "be7" or tracerName.lower() == "be7s":

            self.tracerDict[tracerName] = RadionuclideTracer \
               (tracerName, modelObject, parser, 'log', timeRecord, fileLevel, 7.)

         elif tracerName.lower() == "be10" or tracerName.lower() == "be10s":

            self.tracerDict[tracerName] = RadionuclideTracer \
               (tracerName, modelObject, parser, 'log', timeRecord, fileLevel, 10.)

         elif tracerName.lower() == "pb210" or tracerName.lower() == "pb210s":
            
            self.tracerDict[tracerName] = RadionuclideTracer \
               (tracerName, modelObject, parser, 'log', timeRecord, fileLevel, 210.)

         elif tracerName.lower() == "rn222":
            
            self.tracerDict[tracerName] = RadionuclideTracer \
               (tracerName, modelObject, parser, 'log', timeRecord, fileLevel, 222.)

         else:
            self.tracerDict[tracerName] = GenericTracer(tracerName, modelObject, \
                                                        parser, timeRecord,fileLevel)
            


