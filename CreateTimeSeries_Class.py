#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Februrary 15th 2018
#
# DESCRIPTION:
# This class contains basic methods for plotting a simple time series.
#------------------------------------------------------------------------------

__author__ = 'Megan Damon'
__version__ = '0.0'
__date__ = '2018/02/15'


import re
import getopt
import sys
import os
import numpy
import datetime



sys.path.append('/discover/nobackup/mrdamon/MERRA2')


from GmiIcarttConfiguration import GmiIcarttConfiguration
from GmiIcarttOperations import GmiIcarttOperations
from GmiIcarttEntryOutput import GmiIcarttEntryOutput
from GmiNetCdfFileTools import GmiNetCdfFileTools
from GmiIcarttEntry import GmiIcarttEntry
from IcarttFlightInfo_Class import IcarttFlightInfo_Class

from numpy import *
from netCDF4 import Dataset
import math
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap


class CreateTimeSeries_Class: 

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

   def __init__(self, icarttFile, fieldsFile, dateNcFile, field):

      print("")
      print("Create time series plot class initializing...")
      print("")

      self.icarttOperations = GmiIcarttOperations()

      self.fieldLabels = self.icarttOperations.readFieldsIntoArray (fieldsFile)

      self.field = field

      # get fieldIndexNc from NetCDF output
      fieldIndexNc = -1
      for label in self.fieldLabels[:]:

         # some field descriptions from ICARTT may
         # be in the format similar to CH4_units, etc. 
         if field in label: 
            fieldIndexNc = self.fieldLabels.index(label)


      if fieldIndexNc == -1:
         print("Field : ", field, " not available for plotting")
         sys.exit(-1)
      else:
         print(field, " found at : ", fieldIndexNc)
         self.fieldIndexNc = fieldIndexNc



      self.icarttOperations.setBeginDateTime (dateNcFile)
      self.icarttEntries = self.icarttOperations.getIcarttEntriesFromFile \
          (icarttFile, self.fieldLabels)

      self.icarttFile = icarttFile
      self.dateNcFile = dateNcFile
   



   def createMapDataSize (self, file):

      flightInfoObject = IcarttFlightInfo_Class(self.icarttFile, self.fieldLabels, \
                                                   self.dateNcFile)

      flightInfoObject.collectRecordsFromIcartt()
      flightInfoObject.fillFlightInfo()

      flightLength = flightInfoObject.lengthOfFlight.total_seconds()
      numValues = len(self.speciesArrayIcarttConvert)

      print("")
      print("length of flight: ", flightLength)
      print("number of values: ", numValues)
      self.ratio = flightLength / numValues
      print("ratio: ", self.ratio)

      print("round ratio: ", round(self.ratio))
      print("")


      if round(self.ratio) == 1:
         plt.figure(figsize=(28,14))
      else:
         plt.figure(figsize=(16,10))

      plt.plot(self.dateTimeArrayIcartt[:], self.speciesArrayIcarttConvert[:], color="blue")


      plt.title (self.field + " of flight path")
      plt.ylabel ("Interpolated species conc to flight path (ppbv)")
      plt.xlabel ("UTC since " + self.dateNcFile[0:8] + " 00z (sec)")


      plt.grid(True)



      if file == "f":
         plt.savefig("plots/" + self.dateNcFile + "." + self.field + ".png", 
                                      bbox_inches='tight')
      elif file == "s":
         plt.fig.show()




         
   def cleanUpBadEntries (self, badEntry):
      badEntries = 0
      goodEntries = 0
      count = 0

      for entry in self.speciesArrayIcarttConvert[:]:

         if entry == badEntry:

            badEntries = badEntries + 1

            if count == 0:
               afterVal = self.speciesArrayIcarttConvert[count+1]
               beforeVal = afterVal
            elif count == len(self.speciesArrayIcarttConvert)-1:
               beforeVal = self.speciesArrayIcarttConvert[count-1]
               afterVal = beforeVal
            else:
               beforeVal = self.speciesArrayIcarttConvert[count-1]
               afterVal = self.speciesArrayIcarttConvert[count+1]

            if afterVal == badEntry:
               afterVal = beforeVal
            if beforeVal == badEntry:
               beforeVal = afterVal

            missValue = (beforeVal + afterVal)/2.
            self.speciesArrayIcarttConvert[count] = missValue

            print("Missing value for ", self.field, " = (", beforeVal, " + ", \
                afterVal, ") / 2.", self.speciesArrayIcarttConvert[count])

         else:
            goodEntries = goodEntries + 1
         
         count = count + 1

      print("")
      print("Found ", badEntries, " bad entries out of ", goodEntries)
      print("")



   def extractTimeSeriesArrays (self):

      speciesArrayIcartt = []
      utcArrayIcartt = []
      self.dateTimeArrayIcartt = []
      self.speciesArrayIcarttConvert = []

      utcCount = 0
      print("")
      print("Extracting arrays from ICARTT...")
      print("")


      
      for icarttEntry in self.icarttEntries:

         utcArrayIcartt.append(icarttEntry.utc)
         GmiIcarttEntry.convertUtcToDateTime(icarttEntry, 
                                             self.icarttOperations.beginYear,
                                             self.icarttOperations.beginMonth, 
                                             self.icarttOperations.beginDay)
         self.dateTimeArrayIcartt.append(icarttEntry.dateTime)



         dataline = self.icarttOperations.datalines[utcCount]
         speciesArrayIcartt.append(icarttEntry.extractSpecies\
                                      (self.field,self.fieldLabels,dataline))

         self.speciesArrayIcarttConvert.append(float(speciesArrayIcartt[utcCount]))


         utcCount = utcCount + 1


