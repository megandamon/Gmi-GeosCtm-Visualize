#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         July 31st 2017
#
# DESCRIPTION:
# Driver to plot differences between two sets of  GEOS-CTM species
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


import multiprocessing
from time import sleep
from multiprocessing import Pool

from netCDF4 import Dataset

import math

from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap







sys.path.append('/discover/nobackup/mrdamon/MERRA2')


from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools



def worker (command):
    print("I will execute: ", command)
    return os.system(command)



NUM_ARGS = 6
def usage ():
    print("")
    print("usage: PlotCommonFields_GEOS-CTM.py [-c] [-g] [-r] [-d] [-n] [-p]")
    print("-c GEOS CTM file 1")
    print("-g GEOS CTM file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-n PBS_NODEFILE")
    print("-p number of processes to use per node")
    print("")
    sys.exit (0)


print("Start plotting field differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:n:p:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile1 = optList[0][1]
geosCtmFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])



#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geosCtmFile1):
    print("The file you provided does not exist: ", geosCtmFile1)
    sys.exit(0)

if not os.path.exists (geosCtmFile2):
    print("The file you provided does not exist: ", geosCtmFile2)
    sys.exit(0)


if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM")
    print("Received: ", dateYearMonth)
    sys.exit(0)

if not os.path.exists (pbsNodeFile): 
    print("The file you provided does not exist: ", pbsNodeFile)
    sys.exit(0)

if numProcesses <= 0:
    print("Number of processes must be larger than 0! ")
    print("Given: ", numProcesses)
    sys.exit(0)




print("")
print(geosCtmFile1)
print(geosCtmFile2)
print("")

geosCtmSimName1 = geosCtmFile1.split(".")[0]
geosCtmSimName2 = geosCtmFile2.split(".")[0]


print("")
print("Sim names: ")
print(geosCtmSimName1)
print(geosCtmSimName2)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosCtmObject1 = GeosCtmPlotTools (geosCtmFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


geosCtmObject2 = GeosCtmPlotTools (geosCtmFile2, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


print("")
print("geos ctm 1: ", geosCtmObject1.DATE)
print("geos ctm 2: ", geosCtmObject2.DATE)
print("")

print("")


order = "GEOS-CTM"
list1 = geosCtmObject1.fieldList
list2 = geosCtmObject2.fieldList

if len(geosCtmObject1.fieldList) >= len(geosCtmObject2.fieldList):
    list1 = geosCtmObject2.fieldList
    list2 = geosCtmObject1.fieldList
    order = "GEOS-CTM"

# Does not matter which object to use - this is weird code. :/
fieldsToCompareAll = geosCtmObject1.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and field[0:3] != "GMI":
        fieldsToCompare.append(field)


print("")
print("Fields to compare: ", fieldsToCompare[:])
print("GEOS-CTM 1 model levels: ", geosCtmObject1.lev[:])
print("")

nodes = geosCtmObject1.readNodesIntoArray (pbsNodeFile)
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

#geosCtmFile1, geosCtmFile2, timeRecord, dateYearMonth
pythonCommand = "PlotField_GEOS-CTM.py -c  " + geosCtmFile1 \
    + " -g " + geosCtmFile2 + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f "

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
    print("Processing: ", field, " to : ", nodes[nodeCount], " proc : ", procCount)
    print("")
    

    sysCommand = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand + " " + field + \
        " \' "
    commands.append(sysCommand)



    procCount = procCount + 1
    fieldCount = fieldCount + 1


print("")
for command in commands[:]:
    print(command)
print("")


pool = multiprocessing.Pool(processes=len(commands))

print("")
print("Calling pool.map")
pool.map(worker, commands)
print("")

print("")
print("Calling pool.close")
pool.close()
print("")


