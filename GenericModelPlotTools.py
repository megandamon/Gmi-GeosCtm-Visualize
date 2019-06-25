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

      ncDims = [dim for dim in self.hdfData.dimensions]  # list of nc dimensions
      if timeDim in ncDims[:]:
         self.timeLength = len(self.hdfData.dimensions[timeDim])
         self.time = self.hdfData.variables[timeVar]
         self.timeVarName = timeVar
      else:
         self.timeLength = 1
         self.time = None
         self.timeVarName = None


      self.lat = self.hdfData.variables[latVar]
      self.long = self.hdfData.variables[lonVar]
      self.lev = self.hdfData.variables[levVar]


      self.latVarName = latVar
      self.longVarName = lonVar
      self.levVarName = levVar


      self.minLat = self.lat[:].min()
      self.maxLat = self.lat[:].max()
      self.minLong = self.long[:].min()
      self.maxLong = self.long[:].max()

      self.cenLat = (self.minLat + self.maxLat)/2.
      self.cenLong =  (self.minLong + self.maxLong)/2.

      # User must call "createPlotObjects" to create these
      self.baseMap = None
      self.gridLons = None
      self.gridLats = None
      self.X_grid = None
      self.Y_grid = None

      self.populateFieldList ()


   def createPlotObjects (self):

      self.baseMap = Basemap(llcrnrlon=self.minLong, \
                                llcrnrlat=self.minLat, \
                                urcrnrlon=self.maxLong, \
                                urcrnrlat=self.maxLat, \
                                projection='cyl', \
                                lat_0=self.cenLat,lon_0=self.cenLong)

      self.gridLons,self.gridLats = self.baseMap.makegrid \
          (self.longSize, self.latSize)
      self.X_grid, self.Y_grid = self.baseMap(self.gridLons,self.gridLats)


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Destructor routine.
   #---------------------------------------------------------------------------    

   def __del__(self):
      self.hdfData.close()
      pass


   def create2dSlice2 (self,  z, minMaxVals, subplotNum, plotTitle, \
                          colorMap, normalize=False):

      print("")
      print("min/max field vals in create2dSlice: ", minMaxVals[:])
      print("")
      
      plt.subplot(subplotNum)

      print("")
      print("Shape of field to plot: ", shape(z))
      print("")
      

      imSlice = self.baseMap.pcolor(self.X_grid, self.Y_grid, z, \
                                       cmap=colorMap, \
                                       vmin = minMaxVals[0], \
                                       vmax = minMaxVals[1])
      plt.colorbar()
        
      plt.title(plotTitle)
      plt.axis([self.X_grid.min(), self.X_grid.max(), self.Y_grid.min(), self.Y_grid.max()])

#      baseMap.drawparallels(numpy.arange(minMaxLat[0],minMaxLat[1],40),labels=[1,0,0,0])
      self.baseMap.drawparallels(numpy.arange(self.minLat,self.maxLat, 40),labels=[1,0,0,0])

#      baseMap.drawmeridians(numpy.arange(minMaxLong[0],minMaxLong[1],80),labels=[0,1,0,1])
      self.baseMap.drawmeridians(numpy.arange(self.minLong, self.maxLong,80),labels=[0,1,0,1])
 
      self.baseMap.drawcoastlines()
      self.baseMap.drawstates()



   # X_model, Y_model, and min/maxes 
   # can be members of the class
   def create2dSlice (self, baseMap, X_model, Y_model, z, \
                         minMaxVals, minMaxLat, \
                         minMaxLong, subplotNum, plotTitle, \
                         colorMap, \
                         normalize=False):

      #    print "min/max field vals in create2dSlice: ", minMaxVals[:]

      plt.subplot(subplotNum)



      imSlice = baseMap.pcolor(X_model, Y_model, z, \
                                  cmap=colorMap, \
                                  vmin = minMaxVals[0], \
                                  vmax = minMaxVals[1])
      plt.colorbar()
        
      plt.title(plotTitle)
      plt.axis([X_model.min(), X_model.max(), Y_model.min(), Y_model.max()])

      baseMap.drawparallels(numpy.arange(minMaxLat[0],minMaxLat[1],40),labels=[1,0,0,0])
      baseMap.drawmeridians(numpy.arange(minMaxLong[0],minMaxLong[1],80),labels=[0,1,0,1])
      baseMap.drawcoastlines()
      baseMap.drawstates()




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

      print("Generic populateFieldList")
      


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

      print(order, " has more fields than the other model!")
      print("")


      if order == "GEOS-CTM": # GEOS-CTM has more fields
         scanList = list1
      else:
         scanList = list2 # GMI has more fields

      print("Scanning GEOS-CTM fields- ")
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

      print("")
      print("Scanning ", order, " fields for matches in other model.")
      
      if hasattr(self, 'fieldName'):
         print("Field name is: ", self.fieldName)
      else:
         print("Field name does not exist!")
         self.fieldName = None


      count = 0
      fieldsToCompare = []
      for item in list1[:]:

         if self.fieldName == 'scav' and "SCAV_" in item:
            print("found scav field: ", item)
            print("ERROR: Logic reversed. This code needs help")
            sys.exit(-1)
            

         # need to take out case insensitivity 
         for item2 in list2[:]:
            
            if self.fieldName == 'scav' and "SCAV_" in item2:
               splitItem2 = item2.split("_")
               if item.lower() == splitItem2[1].lower():
                  print("Found SCAV match: ", item)
                  fieldsToCompare.append(item)
            
            if item.lower() == item2.lower():
               fieldsToCompare.append(item)
            

         count = count + 1

      return fieldsToCompare
        

   def printMe (self) :

      print("")
      print("***************************************")
      print("")
      print(self.MODEL_NAME, " information:")
      print("")

      print("file name : ", self.fileName)

      print("")
      print("Dimensional information:")
      print("")
      print("   lat/lon and levels: ", self.latSize, "/", self.longSize, \
          " ", self.levelSize)
      print("   time: ", self.timeLength)


      print("")
      print("field list : ")
      print(fieldList[:])
      print("")

      print("")
      print("***************************************")
      print("")


   def convertLatLonAltToGMI (self, convertLat, convertLong):

      self.lat = self.g_lat * convertLatnnn
      self.long = self.g_long * convertLong
      self.p = self.p * convertPress

      # GMI uses 0-360 longitude
      if self.long < 0.0: 
         self.long = self.g_long + 360.0


   def doDifferenceAnalysis (self, field1, field2, analysisType, fieldDiff):
      
      if field1.shape != field2.shape:
         print ("Fields of different sizes are not supported for difference analysis!")
         sys.exit(0)

      # Generic array to contain differences 
      levPoints = field1.shape[0]
      latPoints = field2.shape[1]

      # User requested percent difference
      if analysisType == "d":

         print ("")
         print ("Doing analysis type percent diff")
         print ("")

         for lev in range(0,levPoints):
            for lat in range(0,latPoints):

               absVal = abs(field1[lev,lat]-field2[lev,lat])
               denVal = (field1[lev,lat]+field2[lev,lat]) / 2.0
               fieldDiff [lev,lat] = (absVal/denVal) * 100.

               if math.isnan(fieldDiff[lev,lat]): 
                  fieldDiff[lev,lat] = 0

         minDiff = fieldDiff.min()
         maxDiff = fieldDiff.max()
    

         print ("")
         print(("Shape of fieldDiff for percent difference: ", fieldDiff.shape))
         print(("low end / high end: ", minDiff, maxDiff))
         print ("")



      # User requested absolute difference
      elif analysisType == "s":
         
         print("")
         print("Creating Absolute Differences")
         print("")

         fieldDiff = field1 - field2

         minDiff = fieldDiff.min()
         maxDiff = fieldDiff.max()

         if abs(minDiff) > abs(maxDiff):
            maxDiff = abs(minDiff)
         else:
            minDiff = -maxDiff

         print("")
         print("low end / high end for simple diffs: ", minDiff, " / ", maxDiff)
         print("")


      # User requested ratio
      elif analysisType == "r":

         fieldDiff = field1/field2

         print ("")
         print(("Ratios min / max: ", fieldDiff.min(), fieldDiff.max()))
         print ("")

         for lev in range(0,levPoints):
            for lat in range(0,latPoints):
               if field1[lev,lat] == 0.0 and field2[lev,lat] == 0.0:
                  fieldDiff[lev,lat] = 1.0
                  print ("Updating to 1.0")
               if field1[lev,lat] != 0.0 and field2[lev,lat] == 0.0:
                  if field1[lev,lat] > 0.0: fieldDiff[lev,lat] = 1.5
                  if field1[lev,lat] < 0.0: fieldDiff[lev,lat] = .5
                  print ("Found ratio .5 away from 1!")


         minDiff = fieldDiff.min()
         maxDiff = fieldDiff.max()

      else:
         print ("")
         print(("Analysis type not supported: ", analysisType))
         print ("")
           
      
      return minDiff, maxDiff, fieldDiff
