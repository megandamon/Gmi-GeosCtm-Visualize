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
import os
import shutil
import glob
import tarfile

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
      print ("MultiHdfFile_Class __del__ called")
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
      self.archiveStyle = archiveStyle

      
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


   def createTimeDeltaFromString(self, timeDeltaString):
      
      self.timeDeltaDayString = timeDeltaString[0:2]
      self.timeDeltaHourString = timeDeltaString[3:5]
      self.timeDeltaMinuteString = timeDeltaString[5:7]

      self.dateTimeStep = timedelta (days=int(self.timeDeltaDayString), \
                                     hours=int(self.timeDeltaHourString), \
                                     minutes=int(self.timeDeltaMinuteString), \
                                     seconds=0)

      return self.dateTimeStep

      

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


      # self.currentDatePath = self.basePath + "/Y" + self.currentYear + \
      #    "/M" + self.currentMonth + "/D" + self.currentDay

      # self.currentFile = self.currentDatePath + "/*." + self.collectionName + \
      #    "*." + self.currentYear + self.currentMonth + \
      #    self.currentDay + "_" + self.currentHour + self.currentMinute + "z.nc4"

      # self.currentDateObject = currentDateObject



      
   def readCurrentFile (self, fieldName):
      

      self.currentFile = glob.glob(self.currentFile)[0]
      
      print ("\nReading: ", self.currentFile)

      with h5py.File (self.currentFile, 'r') as self.currentFileObject:
         field = self.currentFileObject[fieldName][:]

      self.lastFileRead = self.currentFile

      return field



   def compressData (self, dataPath, fileVersion):
      print ("\nCompressing data for file version: ", fileVersion)

      # This routine loops through all possible
      # date/time (i.e. files)
      self.currentDateObject = self.startDateObject
      self.startDateActual = self.currentDateObject


      if self.startDateObject == self.endDateObject:
         print ("\nWARNING: Start and end dates are the same!")


      while self.currentDateObject <= self.endDateObject:


         self.setCurrentTimeComponents (self.currentDateObject)
         print ("\ncurrentFile: ", self.currentFile)
         globFiles = glob.glob(self.currentFile)
         numFiles = len(globFiles)

         self.endDateActual = self.currentDateObject 
         self.currentDateObject += self.dateTimeStep





   
   def cleanData (self, dataPath, fileVersion):
      print ("\nCleaning data for file version: ", fileVersion)

      # This routine loops through all possible
      # date/time (i.e. files)
      self.currentDateObject = self.startDateObject
      self.startDateActual = self.currentDateObject


      if self.startDateObject == self.endDateObject:
         print ("\nWARNING: Start and end dates are the same!")

         print ("\ncurrentFile: ", self.currentFile)
         globFiles = glob.glob(self.currentFile)
         numFiles = len(globFiles)

         print ("num files: ", numFiles)

         if numFiles >= 1:
            print ("\nFound file(s) for this record!")
            sys.exit(0)
            for globFile in globFiles:
               
               if fileVersion in globFile:
                  print ("Need to compress: ", globFile)
                  sys.exit(0)
         




      numRemoves = 0
      while self.currentDateObject <= self.endDateObject:


         self.setCurrentTimeComponents (self.currentDateObject)         


         print ("\ncurrentFile: ", self.currentFile)
         globFiles = glob.glob(self.currentFile)
         numFiles = len(globFiles)
         

         if numFiles > 1:
            print ("\nFound multiple files for this record!")
            for globFile in globFiles:
               
               if fileVersion not in globFile:
                  print ("Removing: ", globFile)
                  os.remove(globFile)
                  numRemoves+=1
         
         self.endDateActual = self.currentDateObject 
         self.currentDateObject += self.dateTimeStep

      print ("Removed ", numRemoves, " files")

   
   def synchFilesToPath (self, sourcePath, fileVersion):

      # This routine loops through all possible
      # date/time (i.e. files)
      self.currentDateObject = self.startDateObject
      self.startDateActual = self.currentDateObject


      if self.startDateObject == self.endDateObject:
         print ("\nWARNING: Start and end dates are the same!")


      numReplaces = 0
      numReplacesUncompressed = 0
         
      while self.currentDateObject <= self.endDateObject:


         self.setCurrentTimeComponents (self.currentDateObject)         


         print ("currentFile: ", self.currentFile)
         
         globDestFiles = glob.glob(self.currentFile)
         numDestFiles = len(globDestFiles)

         # The string of the day/hour/minute we are missing 
         searchString = str(self.currentDay) + "_" + \
            str(self.currentHour) + str(self.currentMinute) + "z"

         
         if numDestFiles == 0:

            print ("\nCould not find a destination file for ", self.currentDateObject)


            # with GEOS_CF, the file will be in the next day if past 12z

            correctTarFileTime = self.currentDateObject
            if self.currentDateObject.hour > 12:
               print ("\nHour is greater than 12!")
               correctTarFileTime = self.currentDateObject + timedelta(days=1)

            # save the destination path (should be correct day)
            destinationDatePath = self.currentDatePath

            # will shift to next day or stay the same
            saveCurrentDateObject = self.currentDateObject
            self.setCurrentTimeComponents(correctTarFileTime)   

            # construct path to source tar
            self.sourceDatePath = sourcePath + "/Y" + self.currentYear + \
               "/M" + self.currentMonth + "/D" + self.currentDay
            self.sourceFile = self.sourceDatePath + "/*." + self.collectionName + \
               "*." + self.currentYear + self.currentMonth + \
               self.currentDay + "*.tar"


            
            self.sourceGlobFiles = glob.glob(self.sourceFile)
            numSourceFiles = len(self.sourceGlobFiles)


            if numSourceFiles == 0:
               print ("WARNING: No source files found for this date!")
               self.endDateActual = self.currentDateObject 
               self.currentDateObject += self.dateTimeStep
               continue 
            
            elif numSourceFiles >= 1:
               for globFile in self.sourceGlobFiles:
                  
                  if fileVersion in globFile:
                     print ("\nFound a source archive that matches the version: ", \
                            fileVersion)
                     tarFile = globFile
                     break
                  tarFile = globFile

            print ("\nReady to extract the file from: ", tarFile)
            
            tar = tarfile.open(tarFile)

            print ("\n\nSEARCH STRING : ", searchString)

            extractFile = None
            for member in tar.getmembers():
               if searchString in member.name:
                  extractFile = member.name
                  extractMember = member
                  break

            if extractFile == None:
               print ("ERROR: could not find file in archive for ", searchString)
               sys.exit(-1)

            print ("\nReady to extract: ", extractFile + " to : ",  destinationDatePath)

            
            tar.extractall(path=destinationDatePath, members=[extractMember])
            tar.close()

            fileName = destinationDatePath + "/" + member.name

            numReplaces+=1

            if "uncompressed" in fileName:
               newFileName = fileName.replace('_uncompressed','')
               print ("\nmove: ", fileName, " to ", newFileName)
               os.rename (fileName, newFileName)
               print ("Replaced with uncompressed version")
               numReplacesUncompressed+=1
            else:
               print ("\nReplaced with compressed version")

            self.currentDateObject = saveCurrentDateObject
            
         if numDestFiles >= 1:
            for globFile in globDestFiles:
               if fileVersion in globFile:
                  print ("\nFound a destination file for ", self.currentDateObject, " that matches the version: ", fileVersion, \
                         "; will not replace it.")
                  break
               else:
                  print ("\nFound a destination file for ", self.currentDateObject, " but it does not match verison!")
                  if "uncompressed" in globFile:
                     newFileName = globFile.replace('_uncompressed','')
                     print ("move: ", globFile, " to ", newFileName)
                     os.rename (globFile, newFileName)
         

         self.endDateActual = self.currentDateObject 
         self.currentDateObject += self.dateTimeStep

      print ("Number of total replacements: ", numReplaces)
      print ("Number of replacements using uncompressed file: ", numReplacesUncompressed)

   def createInterpolatedFiles (self, pressureLevels, newPath=None):

      self.currentDateObject = self.startDateObject
      self.startDateActual = self.currentDateObject

      self.fieldSum = None
      memoryAllocated = False

      if self.startDateObject == self.endDateObject:
         print ("\nStart and end dates are the same!")


      while self.currentDateObject <= self.endDateObject:
         command = ""

         self.setCurrentTimeComponents (self.currentDateObject)
         globFiles = glob.glob(self.currentFile)

         for globFile in globFiles:

            if "_p40." not in globFile and "_p23." not in globFile:
               self.currentFile = globFile
            
         print ("\nCurrent File: ", self.currentFile)


         format = "%Y%m%d_%H%M"
         dateFormat = self.currentDateObject.strftime(format)
         etaFile = "eta2prs." + dateFormat + "z.nc4"
         print ("eta file: ", etaFile)
         
         newFileName = self.createFileNamePressLevs (pressureLevels, newPath)
         metFileName = self.currentFile.replace("chm", "met")


         
         if not os.path.exists(metFileName):
            print ("\nERROR: ", metFileName, " does not exist!")
            sys.exit(0)
         
         if os.path.exists(newFileName):
            print ("\nWARNING! ", newFileName, " already exists! Will not create.")

         else:

            if os.path.exists(etaFile):
               print ("WARNING! ", etaFile + " already exists! Removing it")
               os.remove (etaFile)

            command = "/discover/nobackup/mrdamon/Models/Latest_GEOS-CF_tag/GEOSagcm/Linux/bin/eta2prs.x -levs "
            for lev in pressureLevels:
               command = command + str(lev) + " "

            command = command + "-eta " + self.currentFile + \
               " -prs " + metFileName 

            print ("\n", command)

            sysReturnCode = os.system(command)

            print ("\nMoving ", etaFile, " to ", newFileName)
            shutil.move (etaFile, newFileName)
            
         
         self.endDateActual = self.currentDateObject 
         self.currentDateObject += self.dateTimeStep
         self.numRecords += 1
         

      self.lastFileRead = self.currentFile
      print ("\nActual start and end dates: ", self.startDateActual, \
             self.endDateActual)
         


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
