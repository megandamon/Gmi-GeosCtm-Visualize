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

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt

import multiprocessing
from time import sleep
from multiprocessing import Pool


import math
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import *

from GmiPlotTools import GmiPlotTools
from GmiDef import *


def workerLocal (command):
    print("I will execute: ", command)
    return os.system(command)


NUM_ARGS = 9
def usage ():
    print("")
    print("usage: PlotCommonFields_GEOS-GMI.py [-c] [-g] [-r] [-d] [-n] [-p] [-s] [-v]")
    print("-c GEOS CTM file")
    print("-g GMI file")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-n PBS_NODEFILE")
    print("-p number of processes to use per node")
    print("-s string defining the GMI array with species/fields names (const_labels, etc.)")
    print("-v variable to extract GMI array fields from (const, scav. etc.)")
    print("-t type of plots (Q-quick, S-Standard, C-Complete")
    print("")
    sys.exit (0)


print("Start plotting restart field differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:n:p:s:v:t:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])
fieldNameArrayGMI = optList[6][1]
variableExtractField = optList[7][1]
packageType = str(optList[8][1])

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

if not os.path.exists (pbsNodeFile): 
    print("The file you provided does not exist: ", pbsNodeFile)
    sys.exit(0)

if numProcesses <= 0:
    print("Number of processes must be larger than 0! ")
    print("Given: ", numProcesses)
    sys.exit(0)

if packageType != "Q" and packageType != "S" and packageType != "C":
    print("Please provide packageType as Q, S, or C")
    print("Given: ", packageType)
    sys.exit(0)


print("")
print("Will be looking at GMI fields in: ", fieldNameArrayGMI)
print("")

print(geosCtmFile)
print(gmiFile)
print("")


geosCtmSimName = geosCtmFile.split(".")[0]
gmiSimName = gmiFile.split("_")[1]


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("GEOS-CTM simulation name: ", geosCtmSimName)
print("GMI simulation name: ", gmiSimName)
print("")
#--------------------------------------------------------------

geosCtmObject = GeosCtmPlotTools (geosCtmFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


gmiObject = GmiPlotTools (gmiFile, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'hdr', fieldNameArrayGMI)
print("")
print(fieldNameArrayGMI)
print("")


order = "GMI"
list1 = gmiObject.fieldList
list2 = geosCtmObject.fieldList


if len(geosCtmObject.fieldList) >= len(gmiObject.fieldList):
    list1 = geosCtmObject.fieldList
    list2 = gmiObject.fieldList
    order = "GEOS-CTM"

# Does not matter which object to use - this is weird code. :/
gmiObject.fieldName = variableExtractField
fieldsToCompare = gmiObject.returnFieldsInCommon (list1, list2, order)

print("")
print("variableExtractField: ", variableExtractField)
print("")



print("")
print("Fields to compare: ", fieldsToCompare[:])
print("")




#print list1[:]
#print list2[:]


nodes = gmiObject.readNodesIntoArray (pbsNodeFile)
print("nodes: ", nodes)

# print ""
# print "*******************************"
# print "Testing nodes for access..."
# for node in nodes: 
#     sysCommand = "ssh " + node + " \'uname -n \'"
#     systemReturnCode = os.system(sysCommand)
#     print sysCommand
#     print systemReturnCode
#     if systemReturnCode != 0:
#         print "There is a problem with node: ", node
#         sys.exit(0)

# print "All nodes accessible"
# print "*******************************"
# print ""


cwd = os.getcwd()
print("current working directory: ", cwd)


commands = []
fieldCount = 0
procCount = 0
nodeCount = 0



print("")
print("Package type is: ", packageType)
if packageType == "Q": 
    fieldsToCompare = GmiDef.GMI_QUICK_FIELDS
elif packageType == "S":
    fieldsToCompare = GmiDef.GMI_STANDARD_FIELDS
else:
    print("all")
print("")


print("")

editedFields = []
print("")
for field in fieldsToCompare:
    if field not in GmiDef.GMI_IGNORE_FIELDS[:]:
        editedFields.append(field)
        
print("")

print("")
print(editedFields[:])
print("")


fieldsToCompare = None
fieldsToCompare = editedFields


#geosCtmFile gmiFile, timeRecord, dateYearMonth
pythonCommand1 = "PlotField_GEOS-GMI.py -c  " + geosCtmFile \
    + " -g " + gmiFile + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f "
pythonCommand2= "PlotField_ZonalMean.py -c " + geosCtmFile \
    + " -g " + gmiFile + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f"



for field in fieldsToCompare[:]:

    if procCount == numProcesses: 
        print("node count exceeds num processes per node: ", procCount)
        procCount = 0
        nodeCount = nodeCount + 1

        if nodeCount >= len(nodes):
            print("")
            print("ERROR: nodeCount cannot be > len(nodes): ", nodeCount, \
                " > ", len(nodes))
            print("Use more processes or more nodes")
            print("Number of processes per node: ", numProcesses)
            print("")
            sys.exit(-1)

    
    field = fieldsToCompare[fieldCount]


    print("")
    print("Processing: ", field, " to : ", nodes[nodeCount], " proc : ", procCount, \
        " and " , procCount+1)
    print("")

    sysCommand = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand1 + " " + field + " -v " + variableExtractField + \
        " \' "
    commands.append(sysCommand)


    # zonal means
    print("")
    print("Deciding if zonal mean is possible for : ", field)
    print("")

    if field in GmiDef.GMI_TWOD_FIELDS[:]:
        print("")
        print("2D field found. NO zonal mean!")
        print("")
        
    else:
        sysCommand = "ssh -XYqt " + nodes[nodeCount] + \
            " \'. " + cwd + "/setup_env ; " + \
            " cd " + cwd + " ; " + \
            " python " + cwd + "/" + \
            pythonCommand2 + " " + field + " -v " + variableExtractField + \
            " -m GEOS5 -a r\' "

        commands.append(sysCommand)
        procCount = procCount + 1


    fieldCount = fieldCount + 1


    
print("")
for command in commands[:]:
    print(command)
print("len of commands: ", len(commands))
print("")




pool = multiprocessing.Pool(processes=len(commands))

print("")
print("Calling pool.map")
pool.map(workerLocal, commands)
print("")

print("")
print("Calling pool.close")
pool.close()
print("")


