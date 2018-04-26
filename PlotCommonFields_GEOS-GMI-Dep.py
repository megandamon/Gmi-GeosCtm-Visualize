#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         August 20th 2017
#
# DESCRIPTION:
# Driver to plot differences between GMI and GEOS-CTM WetDep species.
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






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import *

from GmiPlotTools import GmiPlotTools


def workerLocal (command):
    print "I will execute: ", command
    return os.system(command)

def returnFieldsInCommon (gmiList, geosCtmList, fieldPrefixIn):
    
    fieldsToCompare = []

    print ""
    print "Scanning GEOS-CTM fields- "
    print geosCtmList[:]
    print ""

    count = 0
    for item in geosCtmList[:]:

        if fieldPrefixIn in item:

            print ""
            print "Found Dep field: ", item
            itemSplit = item.split("_")
            print "item split: ", itemSplit[1]

            for itemGmi in gmiList[:]:


                if itemGmi == itemSplit[1]:
                    print "Found GMI match: ", itemGmi
                    fieldsToCompare.append (itemGmi)
                    print ""


        count = count + 1


    return fieldsToCompare




NUM_ARGS = 7
def usage ():
    print ""
    print "usage: PlotCommonFields_GEOS-GMI-Dep.py [-c] [-g] [-r] [-d] [-n] [-p] [-f]"
    print "-c GEOS CTM restart file"
    print "-g GMI restart file"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print "-n PBS_NODEFILE"
    print "-p number of processes to use per node"
    print "-f field prefix"
    print ""
    sys.exit (0)


print "Start plotting restart field differences"

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:n:p:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])
fieldPrefix = optList[6][1]

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


if int(timeRecord) > 30: 
    print "WARNING: time record is more than a typical daily file!"

if int(timeRecord) < 0: 
    print "ERROR: time record needs to be positive!"
    sys.exit(0)

if len(dateYearMonth) != 6:
    print "ERROR date must be in the format YYYYMM. Received: ", dateYearMonth
    sys.exit(0)

if not os.path.exists (pbsNodeFile): 
    print "The file you provided does not exist: ", pbsNodeFile
    sys.exit(0)

if numProcesses <= 0:
    print "Number of processes must be larger than 0! "
    print "Given: ", numProcesses
    sys.exit(0)


if fieldPrefix == "WD_":
    gmiCharString = 'wetdep_spc_labels'
    titleString = "Wet dep of "
elif fieldPrefix == "DD_":
    gmiCharString = 'drydep_spc_labels'
    titleString = "Dry dep of "
elif fieldPrefix == "SCAV_":
    gmiCharString = "const_labels"
else:
    print "Fieldp prefix: ", fieldPrefix, " not supported!"
    sys.exit(0)


fieldNameArrayGMI = gmiCharString

print ""
print "Will be looking at GMI fields in: ", fieldNameArrayGMI
print ""



print geosCtmFile
print gmiFile
print ""

geosCtmSimName = geosCtmFile.split(".")[0]
gmiSimName = gmiFile.split("_")[1]


#---------------------------------------------------------------
print ""
print "Command line options look good."
print""
#--------------------------------------------------------------


geosCtmObject = GeosCtmPlotTools (geosCtmFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


gmiObject = GmiPlotTools (gmiFile, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'hdr', fieldNameArrayGMI)
print ""




fieldsToCompare = returnFieldsInCommon (gmiObject.fieldList, \
                                            geosCtmObject.fieldList, fieldPrefix)




print ""
print "Fields to compare: ", fieldsToCompare[:]
print ""



nodes = gmiObject.readNodesIntoArray (pbsNodeFile)
print "nodes: ", nodes

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
print "current working directory: ", cwd


commands = []
fieldCount = 0
procCount = 0
nodeCount = 0

#geosCtmFile gmiFile, timeRecord, dateYearMonth
pythonCommand1 = "PlotField_GEOS-GMI_Dep.py -c  " + geosCtmFile \
    + " -g " + gmiFile + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -p " \
    + fieldPrefix + " -f "

for field in fieldsToCompare[:]:

    if procCount == numProcesses: 
        print "node count exceeds num processes per node: ", procCount
        procCount = 0
        nodeCount = nodeCount + 1

        if nodeCount >= len(nodes):
            print ""
            print "ERROR: nodeCount cannot be > len(nodes): ", nodeCount, \
                " > ", len(nodes)
            print "Use more processes or more nodes"
            print "Number of processes per node: ", numProcesses
            print ""
            sys.exit(-1)

    
    field = fieldsToCompare[fieldCount]


    print ""
    print "Processing: ", field, " to : ", nodes[nodeCount], " proc : ", procCount, \
        " and " , procCount+1
    print ""

    sysCommand = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand1 + " " + field + \
        " \' "
    commands.append(sysCommand)


    procCount = procCount + 1
    fieldCount = fieldCount + 1


    
print ""
for command in commands[:]:
    print command
print "len of commands: ", len(commands)
print ""

pool = multiprocessing.Pool(processes=len(commands))

print ""
print "Calling pool.map"
pool.map(workerLocal, commands)
print ""

print ""
print "Calling pool.close"
pool.close()
print ""


