#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         September 4th 2020
#
# DESCRIPTION:
# This class contains methods for dealing with multiple HDF files
# and their data.
#------------------------------------------------------------------------------

__author__ = 'Megan Damon'
__version__ = '0.0'
__date__ = '2018/02/15'

import h5py
import numpy as np
import sys
import glob
from datetime import *




class MultiHdfFile_Class:

   startDate = None
   endDate = None
   startDateActual = None
   endDateActual = None
   basePath = None
   collectionName = None
   dateTimeStep = None
   archiveStyle = None
   fieldName = None
   numRecords = None

   fieldSum = None
   fieldAverage = None
   
   startDateObject = None
   endDateObject = None

   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Destructor routine.
   #---------------------------------------------------------------------------    

   def __del__(self):
      pass
            
  #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC / NGIT / TASC
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  

   def __init__(self, startDateString, endDateString, pathBaseIn, collectionName, \
                dateTimeStep, archiveStyle):

      print("\nInitializing MultiHdfFile_Class object")

      if archiveStyle == "GEOS-CF_archive":
         print ("\nERROR: ", archiveStyle, " not supported!")
         #tarFile = datePath + "/" + expName + "." + collection \
         #   + "_g1440x721_p23." + startDate + ".ana.uncompressed.tar"
         #tar = tarfile.open(tarFile)
         #tar.extractall()
         #tar.close()
         sys.exit(-1)

      self.startYearString = startDateString[0:4]
      self.startMonthString = startDateString[4:6]
      self.startDayString = startDateString[6:8]
      self.startHourString = startDateString[9:11]
      self.startMinuteString = startDateString[11:13]
      self.startEndYearString = endDateString[0:4]
      self.endMonthString = endDateString[4:6]
      self.endDayString = endDateString[6:8]
      self.endHourString = endDateString[9:11]
      self.endMinuteString = endDateString[11:13]

      self.basePath = pathBaseIn


      
      self.collectionName = collectionName
      self.dateTimeStep = dateTimeStep

      self.startDateObject = datetime.strptime (startDateString[0:8], "%Y%m%d")
      hhmmDelta = timedelta (hours=int(self.startHourString), \
                             minutes=int(self.startMinuteString))
      self.startDateObject = self.startDateObject + hhmmDelta

      self.endDateObject = datetime.strptime (endDateString[0:8], "%Y%m%d")
      hhmmDelta = timedelta (hours=int(self.endHourString), \
                             minutes=int(self.endMinuteString))
      self.endDateObject = self.endDateObject + hhmmDelta

      print ("\nCreated MultiHdfFile_Object for the interval: ", \
             self.startDateObject, " : ", self.endDateObject)

      self.numRecords = 0

   def setCurrentTimeComponents(self, currentDateObject):

      self.currentYear = str(currentDateObject.year)
        
      if currentDateObject.month < 10:
         self.currentMonth = "0" + str(currentDateObject.month)
      else:
         self.currentMonth = str(currentDateObject.month)

      if currentDateObject.day < 10:
         self.currentDay = "0" + str(currentDateObject.day)
      else:
         self.currentDay = str(currentDateObject.day)

      if currentDateObject.hour < 10:
         self.currentHour = "0" + str(currentDateObject.hour)
      else:
         self.currentHour = str(currentDateObject.hour)

      if currentDateObject.minute < 10:
         self.currentMinute = "0" + str(currentDateObject.minute)
      else:
         self.currentMinute = str(currentDateObject.minute)


      self.currentDatePath = self.basePath + "/Y" + self.currentYear + \
         "/M" + self.currentMonth + "/D" + self.currentDay

      self.currentFile = self.currentDatePath + "/*." + self.collectionName + \
         "_*." + self.currentYear + self.currentMonth + \
         self.currentDay + "_" + self.currentHour + self.currentMinute + "z.nc4"



   def sumFieldAcrossFiles (self, fieldName):

      print("\nSumming ", fieldName, " across files.")


      self.fieldName = fieldName
      
      currentDateObject = self.startDateObject
      self.startDateActual = currentDateObject

      self.fieldSum = None
      memoryAllocated = False

      if self.startDateObject == self.endDateObject:
         print ("Start and end dates are the same.")
         print ("Please support this.")

      
      while currentDateObject <= self.endDateObject:


         self.setCurrentTimeComponents (currentDateObject)
         
         print ("Current file: ", self.currentFile)
         self.currentFile = glob.glob(self.currentFile)[0]

         hdfFileObject = None
         hdfFileObject = h5py.File (self.currentFile, 'r')

         field = hdfFileObject[fieldName]
         
         
         if memoryAllocated == False:
            fieldShape = field.shape
            self.fieldSum = np.zeros(fieldShape, np.float32)
            memoryAllocated = True

         self.fieldSum = self.fieldSum + field
         print ("\nmax/min of sum: ", self.fieldSum.max(), self.fieldSum.min())

         self.endDateActual = currentDateObject 
         currentDateObject += self.dateTimeStep
         self.numRecords += 1

         

      self.lastFileRead = self.currentFile
      print ("\nTotal records read and accumulated: ", self.numRecords)
      print ("Actual start and end dates: ", self.startDateActual, \
             self.endDateActual)
         
   def averageField (self,createFile=False):

      print ("\nAveraging ", self.fieldName)
      print ("\nSum max and min: ", self.fieldSum.max(), self.fieldSum.min())
      print ("\nTotal records in sum: ", self.numRecords)
      self.fieldAverage = self.fieldSum / float(self.numRecords)

      
   def reset (self):

      if self.fieldData != None:
         self.fieldData = None

      self.numRecords = 0
