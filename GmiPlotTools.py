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
                   latVar, lonVar, levVar, timeVar, constString):

      GenericModelPlotTools.__init__(self, fileName,  
                                     latDim, lonDim, levDim, timeDim, 
                                     latVar, lonVar, levVar, timeVar)

      self.gmiConstString = constString

      if fileName.find('idaily') != -1:
         self.gmiConstString = 'freq1_labels'

      self.MODEL_NAME = "GMI"

      self.addSpeciesToFieldList (self.gmiConstString)



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
      print self.gmiConstString
      print ""

      if self.gmiConstString == "const_labels":
         self.constVarName = "const"
      elif self.gmiConstString == 'wetdep_spc_labels':
         self.constVarName = "wet_depos"
      elif self.gmiConstString == 'drydep_spc_labels':
         self.constVarName = "dry_depos"
      else:
         self.constVarName = "const_freq1"


      if fieldName.lower() == "moistq":
         print ""
         print "Extracting field from GMI: ", fieldName
         print ""
               
         fieldArray = self.hdfData.variables[fieldName]   

         if fieldArray.shape[0] - 1 < timeRecord:
            print ""
            print "WARNING: time record: ", timeRecord, " is not avail. in GMI. ", \
                " Using rec dim 0"
            print ""
            returnTime = 0
         else:
            returnTime = timeRecord

         returnArray = fieldArray[timeRecord,:,:,:]

      else:

         print ""
         print "Extracting field from GMI: ", fieldName, " from ", self.constVarName
         print ""


         speciesArray = self.hdfData.variables[self.constVarName]


         print self.speciesNames[:]

         indexLocation = 0
         for speciesName in self.speciesNames[:]:
            if speciesName.lower() == fieldName.lower():
               break
            indexLocation = indexLocation + 1
 
         if speciesArray.shape[0] - 1 < timeRecord: 
            print ""
            print "WARNING: time record: ", timeRecord, " is not avail. in GMI. ", \
                " Using rec dim 0"
            print ""
            returnTime = 0
         else:
            returnTime = timeRecord
      
         print speciesArray.shape[:]
         print "index loc: ", indexLocation

      
         if len(speciesArray.shape[:]) == 5:
            returnArray = speciesArray[returnTime,indexLocation,:,:,:]    
         if len(speciesArray.shape[:]) == 4:
            returnArray = speciesArray[returnTime, indexLocation,:,:]


      return returnArray






