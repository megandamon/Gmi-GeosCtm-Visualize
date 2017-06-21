#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 21st 2017
#
# DESCRIPTION:
# Driver to plot differences between GMI and GEOS-CTM species
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





sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools


NUM_ARGS = 2

def usage ():
    print ""
    print "usage: PlotRestartSpecies.py [-c] [-g]"
    print "-c GEOS CTM restart file"
    print "-g GMI restart file"
    print ""
    sys.exit (0)


print "Start plotting restart species differences"

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile):
    print "The file you provided does not exist: ", geosCtmFile
    sys.exit(0)

if not os.path.exists (gmiFile):
    print "The file you provided does not exist: ", gmiFile
    sys.exit(0)



#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------
geosCtmObject = GeosCtmPlotTools(geosCtmFile)

geosCtmObject.printMe()


print ""


