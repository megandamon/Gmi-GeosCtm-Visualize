#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 21st 2017
#
# DESCRIPTION:
# This class represents a GMI NetCDF file and related tools for processing.
#------------------------------------------------------------------------------

import re
import os
import sys
import random
import datetime
import calendar
from numpy import *
from netCDF4 import Dataset

from GenericModelPlotTools import GenericModelPlotTools




class GmiPlotTools (GenericModelPlotTools):


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, fileName, latDim, lonDim, levDim, timeDim, \
                   latVar, lonVar, levVar, timeVar, speciesVar):

      GenericModelPlotTools.__init__(self, fileName,  
                                     latDim, lonDim, levDim, timeDim, 
                                     latVar, lonVar, levVar, timeVar)

      self.MODEL_NAME = "GMI"

      self.addSpeciesToFieldList (speciesVar)


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Destructor routine.
   #---------------------------------------------------------------------------    

   def __del__(self):
      GenericModelPlotTools.__del__(self)


   def addSpeciesToFieldList (self, speciesVar):
      print "Will extract species names from: ", speciesVar
      self.speciesVar = speciesVar

      speciesArray = self.hdfData.variables[speciesVar]

      self.speciesNames = []
      for sp in speciesArray[:]:
         self.speciesNames.append(re.sub(r'\W+', '', str(sp)))

      for species in self.speciesNames[:]:
         self.fieldList.append(species)



   def returnField (self, fieldName, timeRecord):

      print ""
      print "Extracting field from GMI: ", fieldName, " from const"
      print ""
      
#      speciesArray = self.hdfData.variables["const_freq1"]
      speciesArray = self.hdfData.variables["const"]
      
      indexLocation = self.speciesNames.index(fieldName)

      print "num time recs of speciesArray: ", speciesArray.shape[0], timeRecord

      if speciesArray.shape[0] - 1 < timeRecord: 
         print ""
         print "WARNING: time record: ", timeRecord, " is not avail. in GMI. ", \
             " Using rec dim 0"
         print ""
         returnArray = speciesArray[0,indexLocation,:,:,:]
      else:
         returnArray = speciesArray[timeRecord,indexLocation,:,:,:]
      
      return returnArray






