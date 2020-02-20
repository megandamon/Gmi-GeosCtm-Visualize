#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Oct 17 2019
#
# DESCRIPTION:
# Driver to plot 2D slices and zonal means of a list of tracer species. 
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
from TracerPlotTools import TracerPlotTools



def worker (command):
    print("I will execute: ", command)
    return os.system(command)



NUM_ARGS = 7
def usage ():
    print("")
    print("usage: PlotTracers_GEOS.py [-g] [-c] [-k] [-r] [-d] [-n] [-p]")
    print("-g GEOS file ")
    print("-c GEOS file ")
    print("-k Key file for tracers ")
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
optList, argList = getopt.getopt(sys.argv[1:],'g:c:k:r:d:n:p:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosFile1 = optList[0][1]
geosFile2 = optList[1][1]
keyFile = optList[2][1]
timeRecord = int(optList[3][1])
dateYearMonth = optList[4][1]
pbsNodeFile = optList[5][1]
numProcesses = int(optList[6][1])



#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geosFile1):
    print("The file you provided does not exist: ", geosFile1)
    sys.exit(0)

if not os.path.exists (geosFile2):
    print("The file you provided does not exist: ", geosFile2)
    sys.exit(0)

if not os.path.exists (keyFile):
    print("The file you provided does not exist: ", keyFile)
    sys.exit(0)

if int(timeRecord) > 31: 
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
print(geosFile1)
print(geosFile2)
print("")

geosSimName1 = geosFile1.split(".")[0] + "-" + geosFile1.split(".")[1]
geosSimName2 = geosFile2.split(".")[0] + "-" + geosFile2.split(".")[1]


print("")
print("Sim name: ")
print(geosSimName1)
print(geosSimName2)
print("")

#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosObject1 = GeosCtmPlotTools (geosFile1, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )

geosObject2 = GeosCtmPlotTools (geosFile2, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


print("")
print("Date 1: ", geosObject1.DATE)
print("Date 2: ", geosObject2.DATE)
print("")



tracerTools = TracerPlotTools (keyFile, geosObject1)

fieldList = geosObject1.fieldList

fieldsToCompare = []
for field in fieldList[:]:
    if field[0:4] != "Var_":
        fieldsToCompare.append(field)


print("")
print("Fields to compare: ", fieldsToCompare[:])
print("GEOS eta levels: ", geosObject1.lev[:])
print("")


nodes = geosObject1.readNodesIntoArray (pbsNodeFile)
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


    numTracers = len(tracerTools.tracerDict)
    print("")
    print("Num tracers: ", numTracers)
    print("")

    isFieldThere = field in tracerTools.tracerDict
    if isFieldThere == False: 
        field = field.lower()
    
    isFieldThere = field in tracerTools.tracerDict
    if isFieldThere == False: 
        fieldCount = fieldCount + 1 # tracer not found in key list
        continue
    

    sliceCommands = []
    sCount = 0
    for slice in tracerTools.tracerDict[field].slices:

        sliceCommands.append("PlotTracerCompareSlice.py -g " +  geosFile1 \
                                 + " -c " + geosFile2 \
                                 + " -l "  + str(int(slice)) \
                                 + " -r " + str(timeRecord) + " -d " + dateYearMonth \
                                 + " -l \"" + tracerTools.tracerDict[field].long_name + "\" " \
                                 + " -k " + keyFile)


        sCount = sCount + 1
                             
    pythonCommandZM = "PlotTracerCompareZM.py -g " +  geosFile1 \
        + " -c " + geosFile2 \
        + " -r " + str(timeRecord) + " -d " + dateYearMonth \
        + " -k " + keyFile



    sCount = 0
    for slice in tracerTools.tracerDict[field].slices:
        sysCommand = "ssh -XYqt " + nodes[nodeCount] +  " \'. " + cwd + \
            "/setup_env ; cd " + cwd + " ; python " + cwd + "/" + \
            sliceCommands[sCount] + " -f " + str(field) + " \'"
        commands.append(sysCommand)
        sCount = sCount + 1


    sysCommandZM = "ssh -XYqt " + nodes[nodeCount] +  " \'. " + cwd + \
        "/setup_env ; cd " + cwd + " ; python " + cwd + "/" + \
        pythonCommandZM + " -f " + str(field) + " \'"
    commands.append(sysCommandZM)



    procCount = procCount + 1 + len(tracerTools.tracerDict[field].slices)
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


