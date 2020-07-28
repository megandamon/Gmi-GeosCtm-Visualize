#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE: June 10 2019
#
# DESCRIPTION:
# Driver to plot differences between local flash ratios on the GMI grid: 0-360
#      double ratio_local(year_dim, month_dim, latitude_dim, longitude_dim) 
# And the GEOS inputs: -180-180
#      float ratio_local(time, lat, lon)
#------------------------------------------------------------------------------

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


NUM_ARGS = 4
def usage ():
    print("")
    print("usage: CompareFlashInputs_GEOS-GMI.py [-c] [-g] [-r] [-d]")
    print("-c GEOS input file (lat,lon)")
    print("-g GMI input file (year, month, lat, lon)")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("")
    sys.exit (0)


print("Start plotting ratio local differences.")


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]

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

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)



print(geosCtmFile)
print(gmiFile)


geosCtmSimName = "GEOS-ratios"
gmiSimName = "GMI-ratios"


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosCtmObject = GeosCtmPlotTools (geosCtmFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )







gmiObject = GmiPlotTools (gmiFile, 'latitude_dim', 'longitude_dim', \
                             'lev', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'lev', 'hdr', None)




gmiObject.fieldName = "ratio_local"
geosCtmObject.fieldName = gmiObject.fieldName


# Arrays (one time record, one species)
longRecords = numpy.zeros(gmiObject.longSize, numpy.float32)

remappedGmiArray = numpy.zeros((gmiObject.latSize, \
                                    gmiObject.longSize), numpy.float32)

newGmiArray = numpy.zeros((gmiObject.latSize, \
                               geosCtmObject.longSize), numpy.float32)

                             


plt.figure(figsize=(20,20))

print("")
print("Processing local ratios...")
print("")

geosCtmFieldArray = geosCtmObject.returnField (geosCtmObject.fieldName, timeRecord)

year = dateYearMonth[0:4]
month = dateYearMonth[4:6]

gmiFieldArray = gmiObject.returnFlashRateData (gmiObject.fieldName, int(year)-1980, int(month)-1)


print("")
print("Shape of GEOS-CTM field: ", geosCtmFieldArray.shape[:])
print("Shape of GMI field: ", gmiFieldArray.shape[:])
print("")



# put GMI on -180 to 0 to 180
lenGmiLong = len(gmiObject.long[:])

midGmiLong = int(lenGmiLong/2)        
remappedGmiArray [:,0:midGmiLong] = gmiFieldArray[:,midGmiLong:lenGmiLong]

remappedGmiArray [:,midGmiLong:lenGmiLong] = gmiFieldArray[:,0:midGmiLong]
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




if gmiFieldArray.shape != geosCtmFieldArray.shape:
    print("Array shapes are different. Interpolation needed!")

    latCount = 0
    for lat in gmiObject.lat[:]:

        longRecords[:] = remappedGmiArray [latCount,:]
        
        yinterp =  numpy.interp(geosCtmLongPlus180, remappedLongPlus180, longRecords)
        
        newGmiArray[latCount, :] = yinterp [:]
        
        latCount = latCount + 1


else:
    newGmiArray[:,:] = remappedGmiArray[:,:]




z_GeosCtm = geosCtmFieldArray
                             
z_Gmi = newGmiArray[:, :]
z_Diff = z_GeosCtm / z_Gmi

print("")
print("Min/max of GMI: ", z_Gmi.min(), "/", z_Gmi.max())
print("Min/max of GEOS: ", z_GeosCtm.min(), "/", z_GeosCtm.max())
print("Differences: ", z_Gmi.min() - z_GeosCtm.min(), "/", z_Gmi.max() - z_GeosCtm.max())



zRangeGMI = z_Gmi.max() - z_Gmi.min()
zRangeGEOS = z_GeosCtm.max() - z_GeosCtm.min()


print("Ranges: ", zRangeGMI, "/", zRangeGEOS)


minValueOfBoth = z_GeosCtm.min()
maxValueOfBoth = z_GeosCtm.max()

if z_Gmi.min() < minValueOfBoth:
    minValueOfBoth = z_Gmi.min()
if z_Gmi.max() > maxValueOfBoth:
    maxValueOfBoth = z_Gmi.max()

for lat in range(0, size(geosCtmObject.lat)):
    for int in range(0, size(geosCtmObject.long)):

        if z_Gmi[lat, int] == 0 and z_GeosCtm[lat, int] == 0:
            #print "Setting 0/0 to 1 in difference array at: [", long, ",", lat,"]"
            z_Diff[lat, int] = 1.0




#-----------------------------------------------------#
# GEOS-CTM



print("")
print("Min/max ", gmiObject.fieldName)
print("")


print("")
print("GEOS-CTM: ", z_GeosCtm.min(), " / ", z_GeosCtm.max())
print("")


if z_GeosCtm.max() - z_GeosCtm.min() == 0.0:
    print("Constant field found for GEOS-CTM!")
    useMin = z_GeosCtm.min()
    useMax = z_GeosCtm.max()

else:
    useMin = minValueOfBoth
    useMax = maxValueOfBoth

# forcing scales to be the same for both models
useMin = minValueOfBoth
useMax = maxValueOfBoth



geosCtmObject.create2dSlice2 (z_GeosCtm, [useMin, useMax], \
                                  311, "GEOS-CTM " + geosCtmSimName + "        " + \
                                  geosCtmObject.fieldName + "_" + dateYearMonth, "jet")

print("")
print("GMI: ", z_Gmi.min(), " / ", z_Gmi.max())
print("") 

if z_Gmi.max() - z_Gmi.min() == 0.0:
    print("Constant field found for GMI")
    useMin = z_Gmi.min()
    useMax = z_Gmi.max()

else:
    useMin = minValueOfBoth
    useMax = maxValueOfBoth



# forcing scales to be the same for both models
useMin = minValueOfBoth
useMax = maxValueOfBoth


# GMI lev0 is surface
# using geosCtmObject because GMI should now be on lat/long system of GEOS-CTM
geosCtmObject.create2dSlice2 (z_Gmi, [useMin, useMax], \
                                  312, "GMI " + gmiSimName + "        " + 
                                  gmiObject.fieldName + "_" + dateYearMonth, "jet")


geosCtmObject.create2dSlice2 (z_Diff, \
                                  #[z_Diff.min(), z_Diff.max()], \
                                  [0, 1.5], \
                                  313, "Model ratio        " + \
                                  gmiObject.fieldName + "_" + dateYearMonth, "nipy_spectral", \
                                  normalize=True)

#-----------------------------------------------------#



file = "f"
fileName = "ratio_local.GEOS-CTM.GMI." + year + month + "."
if file == "f":
    plt.savefig("plots/" + fileName, bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()
                                 

print("")
print("Plotted ratio_lcoal to plots/directory")
print("")
