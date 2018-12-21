
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





sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools


NUM_ARGS = 2
def usage ():
    print ""
    print "usage: LightningDiagnostics.py [-c] [-t] "
    print "-c GEOS CTM file 1"
    print "-r time record"
    print ""
    sys.exit (0)


print "Start plotting field differences."

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:t:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile1 = optList[0][1]
timeRecord = int(optList[1][1])

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile1):
    print "The file you provided does not exist: ", geosCtmFile1
    sys.exit(0)

if int(timeRecord) > 30: 
    print "WARNING: time record is more than a typical daily file!"

if int(timeRecord) < 0: 
    print "ERROR: time record needs to be positive!"
    sys.exit(0)


print ""
print geosCtmFile1
print timeRecord
print ""


geosCtmSimName1 = geosCtmFile1.split(".")[0]

print ""
print "Sim name: "
print geosCtmSimName1
print ""



#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------
geosCtmObject1 = GeosCtmPlotTools (geosCtmFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


list1 = geosCtmObject1.fieldList


print ""
print list1
print ""



fieldsToCompare = []
for field in list1[:]:
    if field[0:9] == "FLASHRATE" or \
            field[0:6] == "PNOX2D":
        fieldsToCompare.append(field)



print ""
print "Fields to analyze: ", fieldsToCompare[:]
print "GEOS-CTM 1 model levels: ", geosCtmObject1.lev[:]
print ""

print ""
print ""



longRecords = numpy.zeros(geosCtmObject1.longSize, numpy.float32)
fieldCount = 0


for field in fieldsToCompare[:]:    

    print ""
    geosCtmFieldArray1 = geosCtmObject1.returnField (field, timeRecord)
    print ""

    print ""    
    print "Global mean of: ", field, " : ", mean(geosCtmFieldArray1)
    print "Global sum of: ", field, " : ", sum(geosCtmFieldArray1)
    print ""    
    




    

