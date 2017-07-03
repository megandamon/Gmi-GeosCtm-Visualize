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
import os
import sys
import random
import datetime
import calendar
from numpy import *
from netCDF4 import Dataset
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



   def returnField (self, fieldName, timeRecord):

      print "Return time record: ", timeRecord
      fieldAllTime = self.hdfData.variables[fieldName]

      if fieldAllTime.shape[0] - 1 < timeRecord:
         print ""
         print "WARNING: time record: ", timeRecord, " is not avail. in GEOS-CTM. ", \
             " Using rec dim 0"
         print ""

         return fieldAllTime[0, :, :, :]
      else:
         return fieldAllTime[timeRecord, :, :, :]


