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

import numpy
from numpy import *
from netCDF4 import Dataset

import matplotlib
matplotlib.use('pdf')

import math
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap

import vertLevels_GEOS5 as pressLevels

from BasicTools import BasicTools
from PlotTools import PlotTools


class GenericModelPlotTools:

   zmLowLevel = None
   zzmHighLevel = None


   def find_nearest(self, array, value):
      idx = (numpy.abs(array-value)).argmin()
      return array[idx]

   def findLevelFromArray(self, array, value):

      theValue = self.find_nearest(array[:], value)

      levCount = 0
      for item in array[:]:
         if item == theValue:
            returnLev = levCount
         levCount = levCount + 1

      return returnLev

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



   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC / SSAI
   #
   # DESCRIPTION: 
   # This routine returns pressure levels and inverts them. 
   #---------------------------------------------------------------------------  
   def return2DSliceAndConvert (self, field, timeRecord, fileLevel, unitConvert):


      modelFieldArray = self.returnField (field, timeRecord)
      newModelFieldArray = self.return2DSliceFromRefPressure (modelFieldArray, fileLevel)
      modelFieldArray = None
      modelFieldArray = newModelFieldArray[:,:] * float(unitConvert)
      newModelFieldArray = None

      return modelFieldArray


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC / SSAI
   #
   # DESCRIPTION: 
   # This routine returns pressure levels and inverts them. 
   #---------------------------------------------------------------------------  

   def returnPressureLevels (self):

      levUnits = self.hdfData.variables['lev'].getncattr('units')

      if levUnits == "layer":

#          print ()
#          print ("Object uses model levels.")
#          print ()

         levs1 = pressLevels.calcPressureLevels(len(self.lev))
         levs = levs1[::-1]

      elif levUnits == "hPa":

#          print ()
#          print ("File uses pressure levels / layers")
#          print ("Vertical dimension, lev, is in hPa!")
#          print ()

         Levs1 = zeros(len(self.lev))

         count = 0
         for modelLev in self.lev[:]:
            levs1[count] = modelLev
            count = count + 1

         levs = levs1[::-1]

      else:
         print ("Vertical dimension with units: ", levUnits, " not yet supported!")
         sys.exit(0)

      return levs



   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC / SSAI
   #
   # DESCRIPTION: 
   # This routine returns the lines in the file or an error if necessary.
   #---------------------------------------------------------------------------  

   def readFileAndReturnFileLines (self, fileName):

      try:
         fileObject = open (fileName, 'r')
         fileContents = fileObject.read ()
         fileObject.close ()
      except:
         sys.exit(-1)

      if len (fileContents) == 0:
         sys.exit(-1)


      fileLines = fileContents.splitlines()

      return fileLines


   def createComparision2D (self, array1, array2, analType):

      if array1.shape != array2.shape:

         print("")
         print("Array shapes are not the same, will return None")
         print("")

         return None

      else:

         print("")
         print("Array shapes are the same, will continue")
         print("")



      dim1 = array1.shape[0]
      dim2 = array2.shape[1]


      if analType == "d":

#          print("")
#          print("Creating Percent Differences")
#          print("")

         z_Diff = numpy.zeros((dim1,dim2), numpy.float32)

         for dim1It in range(0,dim1):
            for dim2It in range(0,dim2):
               absVal = abs(array1[dim1It,dim2It]-array2[dim1It,dim2It])
               denVal = (array1[dim1It,dim2It]+array2[dim1It,dim2It]) / 2.0
               z_Diff[dim1It,dim2It] = (absVal/denVal) * 100.


      elif analType == "c":

#          print("")
#          print("Creating percent change")
#          print("")

         num = array1 - array2
         z_Diff = (num / array2)

         z_Diff = z_Diff * 100.

      elif analType == "s":
         
#          print("")
#          print("Creating Absolute Differences")
#          print("")

         z_Diff = array1 - array2

      elif analType == "r":

         print("")
         print("Creating Model Ratios")
         print("")

         z_Diff = array1 / array2

         print(type(z_Diff))


         for dim1It in range(0, dim1):
            for dim2It in range(0, dim2):

               if array1[dim1It, dim2It] == 0.0 and array2[dim1It, dim2It] == 0.0:
                  z_Diff[dim1It, dim2It] = 1.0
               elif array1[dim1It, dim2It] != 0.0 and array2[dim1It,dim2It] == 0.0:
                  if array1[dim1It, dim2It] > 0.0: z_Diff[dim1It,dim2It] = 1.5 #saturate
                  if array1[dim1It, dim2It] < 0.0: z_Diff[dim1It,dim2It] = .5 #saturate

      else:
         print("")
         print("Analysis type: ", analType, " not supported!")
         print("")

         z_Diff = None

      return z_Diff [:,:]



   def createComparisionLatLon (self, array1, array2, analType):

      if analType == "d":

         print("")
         print("Creating Percent Differences")
         print("")

         z_Diff = numpy.zeros((size(self.lat),size(self.long)), numpy.float32)

         for lat in range(0,size(self.lat)):
            for lon in range(0,size(self.long)):
               absVal = abs(array1[lat,lon]-array2[lat,lon])
               denVal = (array1[lat,lon]+array2[lat,lon]) / 2.0
               z_Diff[lat,lon] = (absVal/denVal) * 100.
                             

      elif analType == "c":

#          print("")
#          print("Creating percent change")
#          print("")

         num = array1 - array2
         z_Diff = (num / array2)
         
         z_Diff = z_Diff * 100.

         # z_Diff = numpy.zeros((size(self.lat),size(self.long)), numpy.float32)

         # for lat in range(0,size(self.lat)):
         #    for lon in range(0,size(self.long)):

         #       if array1[lat,lon] == 0. and array2[lat,lon] == 0.:
         #          z_Diff[lat,lon] == 0.
         #       else:
         #          num = array1[lat,lon] - array2[lat,lon]
         #          z_Diff[lat,lon] = (num / array2[lat,lon])
         #          z_Diff[lat,lon] = z_Diff[lat,lon] * 100.



      # User requested absolute difference
      elif analType == "s":
         
#          print("")
#          print("Creating Absolute Differences")
#          print("")

         z_Diff = array1 - array2


      elif analType == "r":

         print("")
         print("Creating Model Ratios")
         print("")

         z_Diff = array1 / array2

         print(type(z_Diff))


         for lat in range(0, size(self.lat)):
            for lon in range(0, size(self.long)):

               if array1[lat, lon] == 0.0 and array2[lat, lon] == 0.0:
                  z_Diff[lat, lon] = 1.0
               elif array1[lat, lon] != 0.0 and array2[lat,lon] == 0.0:
                  if array1[lat, lon] > 0.0: z_Diff[lat,lon] = 1.5 #saturate
                  if array1[lat, lon] < 0.0: z_Diff[lat,lon] = .5 #saturate

      else:
         print("")
         print("Analysis type: ", analType, " not supported!")
         print("")

         z_Diff = None

      return z_Diff [:,:]



   def create2dSlice2 (self,  z, minMaxVals, subplotNum, plotTitle, \
                          colorMap, normalize=False, units=None):

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
      cbar = plt.colorbar()

      if units != None:
         cbar.set_label(units)
        
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
   def create2dSliceContours (self, fig, baseMap, X_model, Y_model, z, \
                                 minMaxVals, minMaxLat, \
                                 minMaxLong, cmapUnder, cmapOver, subplotNum, \
                                 plotTitle, \
                                 colorMap, units, \
                                 labelContours=True,normalize=False, contourLevels=None):


      axPlot = fig.add_subplot(subplotNum)

      minVal = minMaxVals[0]
      maxVal = minMaxVals[1]

      if contourLevels != []:
         clevs = contourLevels
      else:         

         print ("Need to create contour levels")
         clevs = linspace(minVal, maxVal, 10)

      plotTool = PlotTools ()


      print (clevs)
      newClevs = plotTool.returnFormattedContours(clevs)

      clevs = None
      clevs = newClevs
      print ("clevs after formatting: ", clevs)



      # map contour values to colors
      norm=colors.BoundaryNorm(clevs, ncolors=256, clip=False)



      contourFormat = plotTool.returnContourFormatFromLevels(clevs)
      cLabelSize = plotTool.returnContourLabelFromSubPlotNum (subplotNum)

      extendValue = "both"
      if clevs[0] == 0:
#         print ("first contour is 0")
         extendValue = "max"

         
      CS = plt.contour(X_model, Y_model, z, levels=clevs, cmap=colorMap, extend=extendValue, norm=norm)
      if labelContours == True:
         plt.clabel(CS, inline=1, colors="black", fmt=contourFormat, fontsize=cLabelSize)


      CF = plt.contourf(X_model, Y_model, z, levels=clevs, norm=norm, cmap=colorMap, extend=extendValue)

      CF.cmap.set_under(cmapUnder)
      CF.cmap.set_over(cmapOver)


      orientation = plotTool.returnOrientationFromSubPlotNum (subplotNum)
      pad = plotTool.returnPadFromSubPlotNum (subplotNum)
      fraction = plotTool.returnFractionFromSubPlotNum (subplotNum)
      fontSize = plotTool.returnFontSizeFromSubPlotNum (subplotNum)
      titleFontSize = plotTool.returnTitleFontSizeFromSubPlotNum (subplotNum)
      latLonFontSize = plotTool.returnLatLonFontSizeFromSubPlotNum (subplotNum)
      

      cbar = fig.colorbar(CF, ax=axPlot, orientation=orientation, pad=pad, fraction=fraction, \
                             format=contourFormat, ticks=clevs)


      if units != None:
         cbar.set_label(label=units,size=16)

#      print ("Num clevs: ", len(clevs)) 
#      plotTool.setVisibleClevTicks (clevs, cbar.ax.get_xticklabels())

      for t in cbar.ax.get_xticklabels():
         t.set_fontsize(fontSize)

      plotTool.reviseTickLabels (cbar)

      
      plt.title(plotTitle, fontsize=titleFontSize)
      plt.axis([X_model.min(), X_model.max(), Y_model.min(), Y_model.max()])


      latLabels = [-90, -60, -30, 0, 30, 60]
      lonLabels = [-180, -120, -60, 0, 60, 120,180]

      baseMap.drawparallels(latLabels,labels=[1,0,0,0], color='grey', \
                               fontsize=latLonFontSize)
      baseMap.drawmeridians(lonLabels,labels=[1,1,0,1], color='grey', \
                               fontsize=latLonFontSize)
      baseMap.drawcoastlines()
      baseMap.drawcountries()

      if str(subplotNum)[0:2] == "22":
         plt.subplots_adjust(left=0.10, right=0.95, hspace=.0000001)#, wspace=0.35, hspace=0.25)


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

      basicTools = BasicTools ()
      return basicTools.readNodesIntoArray (nodeFile)
      

   def populateFieldList (self):

#      print("Generic populateFieldList")
      


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

#      print(order, " has more fields than the other model!")
#      print("")


      if order == "GEOS-CTM": # GEOS-CTM has more fields
         scanList = list1
      else:
         scanList = list2 # GMI has more fields

#      print("Scanning fields- ")
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

#       print("")
#       print("Scanning ", order, " fields for matches in other model.")
      
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


   def return2DSliceFromRefPressure (self, fieldArray, refPressure):

      if len(fieldArray.shape) == 2:
         print("")
         print("WARNING!!! Field 1 is 2D")
         print("")
         slice = fieldArray[:, :]

      elif len(fieldArray.shape) == 3:
         modelLev = self.findLevelFromArray(self.lev[:], refPressure)
         slice = fieldArray[modelLev, :, :]

      else:
         print("")
         print("Unexpected rank of data!")
         print("")
         slice = None

      return slice



   def interpMaskedFieldZM (self, maskedField1, maskedField2, latPoints1, timeRecord, replaceValue=None):

      realMax = maskedField2.max()

      newMaskedField2 = self.returnInterpolatedFieldZM (maskedField2, latPoints1, timeRecord, replaceValue)

      maskedField2 = None
      maskedField2 = newMaskedField2

      maskedArray2 = numpy.ma.masked_where(maskedField1.mask == True, maskedField2)

      maskedField2 = None
      maskedField2 = numpy.ma.masked_where(maskedArray2 >= realMax, maskedArray2)

      return maskedField2

   def returnInterpolatedFieldZM (self, fieldArray, latPoints, timeRecord, replaceValue=None):

#       print ("")
#       print ("Interplating to lat size: ", len(latPoints))
#       print ("Native resolution: ", fieldArray.shape)
#       print ("fieldArray min/max: ", fieldArray.min(), fieldArray.max())
#       print ("")


      levCount = 0
      levPoints = size(fieldArray,0)

      newFieldArray = numpy.zeros((levPoints, len(latPoints)), numpy.float32)

      for lev in range(0,levPoints):

         # pull lat records out 
         latRecords = fieldArray[levCount, :]

         if replaceValue != None:
            latRecords[latRecords >= replaceValue] = 0.0

#         print("LR min/max: ", latRecords.min(), latRecords.max(), levCount)         

         yinterp  = numpy.interp(latPoints[:], self.lat[:], latRecords)

#         print("yinterp min/max: ", yinterp.min(), yinterp.max(), levCount)
         
         newFieldArray [levCount, :] = yinterp

         levCount = levCount + 1

#       print("")
#       print("New 1 min / max / shape",  newFieldArray.min(), " / ", newFieldArray.max(), " / ", 
#             newFieldArray.shape)
#       print("")

      return newFieldArray


   # maskedField2 is going to the resolution of maskedField1
   def interpMaskedFieldLatLon (self, maskedField1, maskedField2, lat1, lon1, timeRecord, replaceValue=None):

      realMax = maskedField2.max()

      newMaskedField2 = self.returnInterpolatedFieldLatLon (maskedField2, lat1, lon1, timeRecord, replaceValue)

      maskedField2 = None
      maskedField2 = newMaskedField2

      maskedArray2 = numpy.ma.masked_where(maskedField1.mask == True, maskedField2)

      maskedField2 = None
      maskedField2 = numpy.ma.masked_where(maskedArray2 >= realMax, maskedArray2)

      return maskedField2



   def returnInterpolatedFieldLatLon (self, fieldArray, latPoints, longPoints, timeRecord, replaceValue=None):

      if replaceValue != None:
         print("Received replace value! = ", replaceValue)

      newFieldArray = numpy.zeros((self.latSize, len(longPoints)), numpy.float32)
      longRecords = numpy.zeros((self.longSize), numpy.float32)



      latCount = 0
      for lat in self.lat[:]:

         # pull long records out 
         longRecords = fieldArray[latCount, :]

         if replaceValue != None:
            longRecords[longRecords >= replaceValue] = 0.0

#         print("LR min/max: ", longRecords.min(), longRecords.max(), latCount)         

         yinterp  = numpy.interp(longPoints[:], self.long[:], longRecords)

#         print("yinterp min/max: ", yinterp.min(), yinterp.max(), latCount)
         
         newFieldArray [latCount, :] = yinterp

         latCount = latCount + 1



      newFieldArrayBoth = numpy.zeros((len(latPoints), len(longPoints)), numpy.float32)
      latRecords = numpy.zeros(self.latSize, numpy.float32)


      longCount = 0
      for lon in longPoints[:]:

         # pull lat records out
         latRecords  = newFieldArray[:, longCount]

         if replaceValue != None:
            latRecords[latRecords >= replaceValue] = 0.0

         yinterp = numpy.interp(latPoints[:], self.lat[:], latRecords)

         newFieldArrayBoth [:, longCount] = yinterp[:]

         longCount = longCount + 1 

      
      newFieldArray = None
      longRecords = None
      latRecords = None

      return newFieldArrayBoth


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
         
#          print("")
#          print("Creating Absolute Differences")
#          print("")

         fieldDiff = field1 - field2

         minDiff = fieldDiff.min()
         maxDiff = fieldDiff.max()

         if abs(minDiff) > abs(maxDiff):
            maxDiff = abs(minDiff)
         else:
            minDiff = -maxDiff

#          print("")
#          print("low end / high end for simple diffs: ", minDiff, " / ", maxDiff)
#          print("")


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
