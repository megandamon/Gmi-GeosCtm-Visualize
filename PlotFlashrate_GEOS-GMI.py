#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         April 4 2019
#
# DESCRIPTION:
# Driver to plot differences in flashrate output between GEOS-5 and GMI-CTM.
# Different output units are used among the above model, and are treated 
# below.
#---------------------------------------------------------------------------
import re
import os
import sys
import random
import datetime
import calendar
import getopt
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

sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


NUM_ARGS = 6
def usage ():
    print("")
    print("usage: PlotFlashrate_GEOS-GMI.py [-c] [-g] [-r] [-d] [-f] [-e]")
    print("-c GEOS CTM file")
    print("-g GMI file")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-f field to compare for GEOS CTM")
    print("-e field to cmopare for GMI")
    print("")
    sys.exit (0)


print("Start plotting flashrate differences.")


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:e:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompareGeos = optList[4][1]
fieldToCompareGmi = optList[5][1]


#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile):
    print("The file you provided does not exist: ", geosCtmFile)
    sys.exit(0)

if not os.path.exists (gmiFile):
    print("The file you provided does not exist: ", gmiFile)
    sys.exit(0)


if int(timeRecord) > 31: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)



print(geosCtmFile)
print(gmiFile)

geosCtmSimName = geosCtmFile.split(".")[0]
gmiSimName = gmiFile.split("_")[1]


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosCtmObject = GeosCtmPlotTools (geosCtmFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


gmiObject = GmiPlotTools (gmiFile, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'hdr', 'const_labels')



gmiObject.fieldName = fieldToCompareGmi


# Arrays (one time record, one species)
longRecords = numpy.zeros(gmiObject.longSize, numpy.float32)

remappedGmiArray = numpy.zeros((gmiObject.latSize, \
                                    gmiObject.longSize), numpy.float32)
remappedMcorArray = numpy.zeros((gmiObject.latSize, \
                                    gmiObject.longSize), numpy.float32)


                             
plt.figure(figsize=(20,20))

field = fieldToCompareGeos
geosCtmFieldArray = geosCtmObject.returnField (field, timeRecord)
gmiFieldArray = gmiObject.returnField (fieldToCompareGmi, timeRecord, '')
gmiMcorArray = gmiObject.returnConstantField ('mcor')


print("")
print("Shape of GEOS-CTM ", field, geosCtmFieldArray.shape[:])
print("Shape of GMI ", fieldToCompareGmi, gmiFieldArray.shape[:])
print("")



# put GMI on -180 to 0 to 180
lenGmiLong = len(gmiObject.long[:])
midGmiLong = int(lenGmiLong/2)


remappedGmiArray [:,0:midGmiLong] = gmiFieldArray[:,midGmiLong:lenGmiLong]
remappedGmiArray [:,midGmiLong:lenGmiLong] = gmiFieldArray[:,0:midGmiLong]
remappedMcorArray [:,0:midGmiLong] = gmiMcorArray[:,midGmiLong:lenGmiLong]
remappedMcorArray [:,midGmiLong:lenGmiLong] = gmiMcorArray[:,0:midGmiLong]
remappedLong = numpy.zeros(lenGmiLong, float32)
remappedLong [0:midGmiLong] = gmiObject.long[midGmiLong:lenGmiLong] - 360.0
remappedLong [midGmiLong:lenGmiLong] = gmiObject.long[0:midGmiLong]
remappedLongPlus180 = numpy.zeros(lenGmiLong, float32)
remappedLongPlus180[:] = remappedLong[:] + 180.0
geosCtmLongPlus180 = numpy.zeros(geosCtmObject.longSize, float32)
geosCtmLongPlus180 [:] = geosCtmObject.long[:] + 180.0



# Prepares basemap objects for plotting
print("")
print("Creating GEOS-CTM plot objects...")
geosCtmObject.createPlotObjects()
print("Creating GMI plot objects...")
gmiObject.createPlotObjects()
print("")


print("")
print("shape of remappedGmiArray: ", shape(remappedGmiArray))
print("shape of remappedMcorArray: ", shape(remappedMcorArray))
print("")



z_GeosCtm = geosCtmFieldArray[:, :]
z_GeosCtm = z_GeosCtm  

print("mcorArray min/max; ", remappedMcorArray.min(), remappedMcorArray.max())

z_Gmi = remappedGmiArray[:, :]  / (remappedMcorArray[:,:] / 1e6) #convert to kg/s for compare
z_Diff = z_GeosCtm / z_Gmi

print("")
print("Min/max of GMI: ", z_Gmi.min(), "/", z_Gmi.max())
print("Min/max of GEOS: ", z_GeosCtm.min(), "/", z_GeosCtm.max())
print("Min/max of Ratios: ", z_Diff.min(), "/",  z_Diff.max())

minValueOfBoth = z_GeosCtm.min()
maxValueOfBoth = z_GeosCtm.max()
        
if z_Gmi.min() < minValueOfBoth:
    minValueOfBoth = z_Gmi.min()
if z_Gmi.max() > maxValueOfBoth:
    maxValueOfBoth = z_Gmi.max()

for lat in range(0, size(geosCtmObject.lat)):
    for int in range(0, size(geosCtmObject.long)):        
        if z_Gmi[lat, int] == 0 and z_GeosCtm[lat, int] == 0:
            z_Diff[lat, int] = 1.0


#-----------------------------------------------------#
# GEOS-CTM
            


# forcing scales to be the same for both models
useMin = minValueOfBoth
useMax = maxValueOfBoth


geosCtmObject.create2dSlice2 (z_GeosCtm, [useMin, useMax], \
                                  311, "GEOS-CTM " + geosCtmSimName + "        " + \
                                  fieldToCompareGeos + "_" + \
                                  dateYearMonth, "jet")

# GMI

geosCtmObject.create2dSlice2 (z_Gmi, [useMin, useMax], \
                                  312, "GMI " + gmiSimName + "        " + \
                                  fieldToCompareGmi + "_" + \
                                  dateYearMonth, "jet")


print("")
print("GEOS-CTM ", fieldToCompareGeos, " min/max/mean : ", z_GeosCtm.min(), " / ", z_GeosCtm.max(), " / ", z_GeosCtm.mean())
print("")
print("")
print("GMI ", fieldToCompareGmi, " min/max/mean : ", z_Gmi.min(), " / ", z_Gmi.max(), " / ", z_Gmi.mean())
print("") 

print("") 
geosCtmGlobalSum = sum(z_GeosCtm)
gmiCtmGlobalSum = sum(z_Gmi)
print("GEOS-CTM flashrate global sum: ", geosCtmGlobalSum) 
print("GMI flashrate global sum: ", gmiCtmGlobalSum)
print("Diff: ", (geosCtmGlobalSum/gmiCtmGlobalSum))
print() 
print("")



geosCtmObject.create2dSlice2 (z_Diff, \
                                  #[z_Diff.min(), z_Diff.max()], \
                                  [0, 1.5], \
                                  313, "Model ratio flashrate       " + \
                                  dateYearMonth, \
                                  "nipy_spectral", \
                                  normalize=True)

#-----------------------------------------------------#



file = "f"
if file == "f":
    plt.savefig("plots/Flashrate.GEOS-CTM.GMI." + dateYearMonth + ".", bbox_inches='tight')
elif file == "s":
    plt.show()
    
plt.clf()
                                  

print("")
print("Plotted Flashrate differences to plots/directory")
print("")
