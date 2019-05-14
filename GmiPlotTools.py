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

      if self.gmiConstString == None:
         print ""
         print "Looking for standalone GMI variable"
         print""
      
      elif 'dep_spc_labels' in self.gmiConstString:
         print ""
         print "Doing deposition field extraction"
         print ""

      elif fileName.find('idaily') != -1:

         print ""
         print "Doing freq1 idaily field extraction"
         print ""
         self.gmiConstString = 'freq1_labels'

      elif fileName.find('tracers') != -1:

         print ""
         print "Doing freq2 tracer field extraction"
         print ""

         self.gmiConstString = 'freq2_labels'

      elif fileName.find('amonthly') != -1 or fileName.find('adaily') != -1:

         print ""
         print "Doing field extraction using const_labels"
         print ""


         self.gmiConstString = 'const_labels'

      self.MODEL_NAME = "GMI"


      print self.gmiConstString


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

      if speciesVar == None:
         print ""
         print "speciesVar is None"
         print ""
         return 

      print "Will extract species names from: ", speciesVar
      self.speciesVar = speciesVar

      speciesArray = self.hdfData.variables[speciesVar]

      self.speciesNames = []
      for sp in speciesArray[:]:
         self.speciesNames.append(re.sub(r'\W+', '', str(sp)))

      for species in self.speciesNames[:]:
         self.fieldList.append(species)



   def returnConstantField (self, fieldName):


      print fieldName
      print fieldName.lower()

      print ""
      print "Extracting field from GMI: ", fieldName
      print ""
               
      fieldArray = self.hdfData.variables[fieldName]   

      returnArray = fieldArray[:,:]

      return returnArray


   def returnField (self, fieldName, timeRecord, arrayName):


      if arrayName == 'SCAV_' or arrayName == 'scav':
         self.constVarName = 'scav'
      elif self.gmiConstString == "const_labels":
         self.constVarName = "const"
      elif self.gmiConstString == 'wetdep_spc_labels':
         self.constVarName = "wet_depos"
      elif self.gmiConstString == 'drydep_spc_labels':
         self.constVarName = "dry_depos"
      elif self.gmiConstString == 'freq2_labels':
         self.constVarName = "const_freq2"
      else:
         self.constVarName = "const_freq1"


      print fieldName
      print fieldName.lower()

      if fieldName.lower() == "moistq" or fieldName.lower() == "EM_LGTNO" \
             or fieldName.lower() == "flashrate_nc" or fieldName.lower() == "lfr" \
             or fieldName.lower() == "mcor" or fieldName.lower() == "psf":
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

            if fieldName.lower() != "flashrate_nc" and fieldName.lower() != 'lfr' \
                   and fieldName.lower () != "mcor" and fieldName.lower() != "psf":
               returnArray = fieldArray[timeRecord,:,:,:]
            else:
               returnArray = fieldArray[timeRecord,:,:]


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

   def returnFieldAtSurface (self, fieldName, timeRecord, arrayName):


      if arrayName == 'SCAV_' or arrayName == 'scav':
         self.constVarName = 'scav'
      elif self.gmiConstString == "const_labels":
         self.constVarName = "const"
      elif self.gmiConstString == 'wetdep_spc_labels':
         self.constVarName = "wet_depos"
      elif self.gmiConstString == 'drydep_spc_labels':
         self.constVarName = "dry_depos"
      elif self.gmiConstString == 'freq2_labels':
         self.constVarName = "const_freq2"
      else:
         self.constVarName = "const_freq1"


      if fieldName.lower() == "moistq" or fieldName.lower() == "EM_LGTNO":
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
            returnArray = speciesArray[returnTime,indexLocation,0,:,:]    
         if len(speciesArray.shape[:]) == 4:
            returnArray = speciesArray[returnTime, indexLocation,0,:]


      return returnArray







