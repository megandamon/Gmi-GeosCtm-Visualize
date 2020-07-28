#!/usr/bin/env python


# AUTHORS: Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# BEGIN DATE:        June 12 2017
#
# DESCRIPTION:


__author__ = 'Megan Damon'
__version__ = '0.0'
__date__ = '2017/06/12'

import re
import getopt
import sys
import os
import numpy
import datetime



sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')


from GmiIcarttConfiguration import GmiIcarttConfiguration
from GmiIcarttOperations import GmiIcarttOperations
from GmiIcarttEntryOutput import GmiIcarttEntryOutput
from GmiNetCdfFileTools import GmiNetCdfFileTools
from GmiIcarttEntry import GmiIcarttEntry
from numpy import *
from netCDF4 import Dataset
import math
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap

from CreateTimeSeries_Class import CreateTimeSeries_Class

NUM_ARGS = 5

def usage ():
    print("")
    print("usage: CreateTimeSeriesPlot.py [-i] [-c] -[f] [-d] [-s]")
    print("-i icartt file")
    print("-c specified which chemical species to output")
    print("-f specify f for file or s for screen (f/s)")
    print("-d Date of NetCDF file")
    print("-s file with list of species")
    print("")
    sys.exit (0)

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'i:c:f:d:s:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

icarttFile = optList[0][1]
species = optList[1][1]
file = optList[2][1]
dateNcFile = optList[3][1]
outputSpeciesFile = optList[4][1]

#---------------------------------------------------------------
print("")
print("Checking command line options")
print("")
#---------------------------------------------------------------
if not os.path.exists (icarttFile): 
    print(("The file you provided does not exist: ", icarttFile))
    sys.exit(0)

file = file.strip()
if file != "f" and file != "s":
    print("Please specify -f f or -f s")
    sys.exit(0)

if len(dateNcFile) != 8:
    print("The date you provided is not in the format YYYYMMDD")
    sys.exit(0)


if not os.path.exists (outputSpeciesFile):
    print(("The file you provided does not exist: ", outputSpeciesFile))
    sys.exit(0)


timeSeriesObject = CreateTimeSeries_Class(icarttFile, outputSpeciesFile, dateNcFile, \
                                              species)



print("")
print(("Flight begin time: ", timeSeriesObject.icarttOperations.beginTime))
print("")


timeSeriesObject.extractTimeSeriesArrays ()
timeSeriesObject.cleanUpBadEntries (-9999.00)

timeSeriesObject.createMapDataSize (file)




