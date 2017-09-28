#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 21st 2017
#
# DESCRIPTION:
# This class represents a generic model file and related tools for processing.
#------------------------------------------------------------------------------

import re
import os
import sys
import random
import datetime
import calendar
from numpy import *
from netCDF4 import Dataset




class GenericModelPlotTools:


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, fileName, latDim, lonDim, levDim, timeDim, \
                   latVar, lonVar, levVar, timeVar):

      self.fileName = fileName
      self.hdfData = Dataset (self.fileName, "r", format="NETCDF4")




      self.dateTime = None
      self.latSize = len(self.hdfData.dimensions[latDim])
      self.longSize = len(self.hdfData.dimensions[lonDim])
      self.levelSize = len(self.hdfData.dimensions[levDim])
      self.timeLength = len(self.hdfData.dimensions[timeDim])


      self.lat = self.hdfData.variables[latVar]
      self.long = self.hdfData.variables[lonVar]
      self.lev = self.hdfData.variables[levVar]
      self.time = self.hdfData.variables[timeVar]

      self.latVarName = latVar
      self.longVarName = lonVar
      self.levVarName = levVar
      self.timeVarName = timeVar

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

   def readNodesIntoArray (self, nodeFile):

      nodesRead = []

      myFile = open (nodeFile, "r")

      count = 0
      line = myFile.readline().rstrip()
      while line != '':
         nodesRead.append(line)

         if count == 10000: break
         count = count + 1
         line = myFile.readline().rstrip()

      myFile.close()

      nodesToReturn = []
      for node in nodesRead:
         if node not in nodesToReturn: nodesToReturn.append(node)
      
      return nodesToReturn


   def populateFieldList (self):

      print "Generic populateFieldList"
      
      self.fieldList = []
      for var in self.hdfData.variables:
         if var not in [self.latVarName, self.longVarName, \
                           self.levVarName, self.timeVarName]:
            self.fieldList.append (var)

   def returnFieldsInCommonNew (self, list1, list2):

      fieldsToCompare = []
      for item in list1[:]:
         
         for item2 in list2[:]:
            if item.lower() == item2.lower():
               fieldsToCompare.append(item)

      return fieldsToCompare
               
   def returnFieldsInCommon (self, list1, list2, order):

      print order, " has more fields than the other model!"
      print ""

      if order == "GEOS-CTM": # GEOS-CTM has more fields
         scanList = list1
      else:
         scanList = list2 # GMI has more fields

      print "Scanning GEOS-CTM fields- "
      count = 0
      for item in scanList[:]:
         if item[0:4] != "Var_" and \
                item[0:3] != "EM_" and \
                item[0:7] != "Var_EM_":
            scanList[count] = item

         count = count + 1

      if order == "GEOS-CTM": 
         list1 = scanList
      else:
         list2 = scanList

      print ""
      print "Scanning ", order, " fields for matches in other model."
      count = 0
      fieldsToCompare = []
      for item in list1[:]:

         # need to take out case insensitivity 
         for item2 in list2[:]:
            if item.lower() == item2.lower():
               fieldsToCompare.append(item)
            

         count = count + 1

      return fieldsToCompare
        

   def printMe (self) :

      print ""
      print "***************************************"
      print ""
      print self.MODEL_NAME, " information:"
      print ""

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

      print ""
      print "***************************************"
      print ""


   def convertLatLonAltToGMI (self, convertLat, convertLong):

      self.lat = self.g_lat * convertLatnnn
      self.long = self.g_long * convertLong
      self.p = self.p * convertPress

      # GMI uses 0-360 longitude
      if self.long < 0.0: 
         self.long = self.g_long + 360.0



