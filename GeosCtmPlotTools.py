#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 21st 2017
#
# DESCRIPTION:
# This class represents a GEOS-CTM HDF file and related tools for processing.
#------------------------------------------------------------------------------

import re
from GenericModelPlotTools import GenericModelPlotTools

class GeosCtmPlotTools (GenericModelPlotTools):

   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, fileName, latDim, lonDim, levDim, timeDim, \
                   latVar, lonVar, levVar, timeVar):

      GenericModelPlotTools.__init__(self, fileName, latDim, lonDim, levDim, \
                                        timeDim, latVar, lonVar, levVar, timeVar)

      self.MODEL_NAME = "GEOS-CTM"

      splitString= re.split('_', fileName)
      tokens = []
      for token in splitString[:]:
         splitTokens = re.split('\.', token)
         for splitToken in splitTokens[:]:
            tokens.append(splitToken)

      for token in tokens[:]:
         if token.isdigit():
            self.DATE = token


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Destructor routine.
   #---------------------------------------------------------------------------    

   def __del__(self):

      GenericModelPlotTools.__del__(self)
      
        
   def convertLatLonAltToGMI (self, convertLat, convertLong):

      self.lat = self.g_lat * convertLatnnn
      self.long = self.g_long * convertLong
      self.p = self.p * convertPress

      # GMI uses 0-360 longitude
      if self.long < 0.0: 
         self.long = self.g_long + 360.0



   def returnField (self, fieldName, timeRecord, prefix=''):

#      print(("Return time record: ", timeRecord, " for : ", fieldName))

      fieldName = prefix + fieldName


      if fieldName not in self.hdfData.variables.keys():
         if fieldName.islower(): 
            fieldName = fieldName.upper()
         else: 
            fieldName = fieldName.lower()

      fieldAllTime = self.hdfData.variables[fieldName]

      if fieldAllTime.shape[0] - 1 < timeRecord:
         print("")
         print(("WARNING: time record: ", timeRecord, " is not avail. in GEOS-CTM. ", \
             " Using rec dim 0"))
         print("")
         returnTime = 0
      else:
         returnTime = timeRecord

      #(1, 181, 360) - GEOS-CTM "2D field"
      #(1, 72, 181, 360) - GEOS-CTM "3d field"xs

#       print("")
#       print(("Dims of array: ", len(fieldAllTime.shape)))
#       print(("No Time? ", self.time==None))
#       print(("Shape: ", fieldAllTime.shape)) 
#       print("")

      if len(fieldAllTime.shape[:]) == 4:                                         
         return fieldAllTime[returnTime, :, :, :]
      elif len(fieldAllTime.shape[:]) == 3 and self.time==None:
         return fieldAllTime[:, :, :]
      elif len(fieldAllTime.shape[:]) == 2:
         return fieldAllTime[:,:]
      else:
         return fieldAllTime[returnTime, :, :]


