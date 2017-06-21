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




class GeosCtmPlotTools:


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, fileName):

      self.fileName = fileName
      self.hdfData = Dataset (self.fileName, "r", format="NETCDF4")

      #print ""
      #print "HDF object contains: ", self.hdfData
      #print ""


      self.dateTime = None
      self.latSize = len(self.hdfData.dimensions['lat'])
      self.longSize = len(self.hdfData.dimensions['lon'])
      self.levelSize = len(self.hdfData.dimensions['lev'])
      self.timeLength = len(self.hdfData.dimensions['time'])


      self.lat = self.hdfData.variables['lat']
      self.long = self.hdfData.variables['lon']
      self.lev = self.hdfData.variables['lev']

      self.populateFieldList ()


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Destructor routine.
   #---------------------------------------------------------------------------    

   def __del__(self):
      self.hdfData.close()
      pass

   def populateFieldList (self):

      self.fieldList = []
      for var in self.hdfData.variables:
         if var not in ['lon', 'lat', 'lev', 'time']:
            self.fieldList.append (var)

      
        

   def printMe (self) :

       print "file name : ", self.fileName

       print ""
       print "Dimensional information:"
       print ""
       print "   lat/lon and levels: ", self.latSize, "/", self.longSize, \
           " ", self.levelSize
       print "   time: ", self.timeLength


       print ""
       print "field list : "
       for field in self.fieldList[:]:
          print field, 
       print ""

   def convertLatLonAltToGMI (self, convertLat, convertLong):

      self.lat = self.g_lat * convertLatnnn
      self.long = self.g_long * convertLong
      self.p = self.p * convertPress

      # GMI uses 0-360 longitude
      if self.long < 0.0: 
         self.long = self.g_long + 360.0



