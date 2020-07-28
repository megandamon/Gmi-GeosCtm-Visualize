#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 2 2020
#
# DESCRIPTION:
# Driver to create daily, monthly, or yearly averages.
#------------------------------------------------------------------------------



import re
import os
import glob
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


import multiprocessing
from time import sleep
from multiprocessing import Pool

from netCDF4 import Dataset

import math

from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap







sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')


from GmiNetCdfFileTools import GmiNetCdfFileTools

def worker (command):
    print("I will execute: ", command)
    return os.system(command)



NUM_ARGS = 5
def usage ():
    print("")
    print("usage: CreateAverages.py [-p] [-c] [-d] [-o] [-n]" )
    print("-p direct path to files ")
    print("-c GEOS collection name ")
    print("-d date of comparision (YYYYMMDD, YYYYMM, YYYY)")
    print("-o output path")
    print("-n new file name")
    print("")
    sys.exit (0)


print("Start plotting field differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'p:c:d:o:n:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

path = optList[0][1]
collection = optList[1][1]
date = optList[2][1]
outputPath = optList[3][1]
newFileName = optList[4][1]


#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (path):
    print("The path you provided does not exist: ", path)
    sys.exit(0)

if len(date) != 8 and len(date) != 6 and len(date) != 4:
    print("ERROR date must be in the format YYYYMMDD, YYYYMM, YYYY")
    print("Received: ", date)
    sys.exit(0)

#---------------------------------------------------------------
print("")
print("Command line options are good.")
print("")
#---------------------------------------------------------------
fileString = path + "/*" + collection +  "*" + date + "*.nc4"
print (fileString)

files = glob.glob(fileString)

for file in files:
    print (file)

ncFileTools = GmiNetCdfFileTools()

newFileNamePath = outputPath + "/" + newFileName

print ("New file name: ", newFileNamePath)


returnCode = ncFileTools.doGridPointAverages (files, newFileNamePath)

print ("Return code is: ", returnCode)

