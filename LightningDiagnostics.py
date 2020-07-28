
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         July 6 2018
#
# DESCRIPTION:
# Driver print out some lightning diagnostics
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

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


from netCDF4 import Dataset
import math




from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap





sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')

from GeosCtmPlotTools import GeosCtmPlotTools
from GmiPlotTools import GmiPlotTools
from GenericModelPlotTools import GenericModelPlotTools


NUM_ARGS = 2
def usage ():
    print("")
    print("usage: LightningDiagnostics.py [-c] [-t] ")
    print("-c GEOS CTM or GMI file")
    print("-t time record")
    print("")
    sys.exit (0)


print("Start plotting field differences.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:t:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

inputFile = optList[0][1]
timeRecord = int(optList[1][1])

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (inputFile):
    print("The file you provided does not exist: ", inputFile)
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------



print("")
print(inputFile)
print(timeRecord)
print("")


fileType = None

print ("")
if inputFile[0:3] == "gmi":
    print ("File is GMI: ", inputFile)
    simulationName = inputFile.split("_")[1]
    inputFileObject = GmiPlotTools (inputFile, 'latitude_dim', 'longitude_dim', \
                                        'eta_dim', 'rec_dim', 'latitude_dim', \
                                        'longitude_dim', 'eta_dim', 'hdr', 'const_labels')
    mcor = inputFileObject.returnConstantField ('mcor')

    fileType = "GMI"

else:
    print ("File is GEOS: ", inputFile)
    simulationName = inputFile.split(".")[0]
    inputFileObject = GeosCtmPlotTools (inputFile, 'lat','lon',\
                                           'lev','time', 'lat', \
                                           'lon', 'lev', 'time' )
    fileType = "GEOS"


# print("")
# print("Simulation name: ")
# print(simulationName)
# print("")


list1 = inputFileObject.fieldList


# print("")
# print(list1)
# print("")



fieldsToCompare = []
for field in list1[:]:
    if field[0:9] == "FLASHRATE" or \
            field[:] == "flashrate_nc":
        fieldsToCompare.append(field)



# print("")
# print("Fields to analyze: ", fieldsToCompare[:])
# print("Input file vertical levels: ", inputFileObject.lev[:])
# print("")


# print("")    

if fileType == "GEOS":
    fieldArray = inputFileObject.returnField (fieldsToCompare[0], timeRecord)
    print("Global mean of: ", fieldsToCompare[0], " : ", mean(fieldArray) * 3.154e7, " 1/km2y")
    print("Global sum of: ", fieldsToCompare[0], " : ", sum(fieldArray))
else:
    fieldArray = inputFileObject.returnField (fieldsToCompare[0], timeRecord, None)
    gmiFieldArray = fieldArray [:,:] / (mcor[:,:] / 1e6) # convert to kg/2
    print("Global mean of: ", fieldsToCompare[0], " : ", mean(gmiFieldArray) * 3.154e7, " 1/km2y")
    print("Global sum of: ", fieldsToCompare[0], " : ", sum(gmiFieldArray))


print("")    
    




    

