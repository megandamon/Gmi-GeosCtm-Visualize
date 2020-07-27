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
    print("usage: PlotTracers_GEOS.py [-g] [-k] [-r] [-d] [-n] [-p] [-m]")
    print("-g GEOS file ")
    print("-k Key file for tracers ")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-n PBS_NODEFILE")
    print("-p number of processes to use per node")
    print("-m configuration name (Replay, CCM, etc.)")
    print("")
    sys.exit (0)


print("Start plotting field differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'g:k:r:d:n:p:m:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosFile = optList[0][1]
keyFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])
configName = optList[6][1]



#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (geosFile):
    print("The file you provided does not exist: ", geosFile)
    sys.exit(0)

if not os.path.exists (keyFile):
    print("The file you provided does not exist: ", keyFile)
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6 and len(dateYearMonth) != 4:
    print("ERROR date must be in the format YYYY or YYYYMM")
    print("Received: ", dateYearMonth)
    sys.exit(0)

if not os.path.exists (pbsNodeFile): 
    print("The file you provided does not exist: ", pbsNodeFile)
    sys.exit(0)

if numProcesses <= 0:
    print("Number of processes must be larger than 0! ")
    print("Given: ", numProcesses)
    sys.exit(0)


geosSimName1 = geosFile.split(".")[0] + "-" + geosFile.split(".")[1]




#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
geosObject1 = GeosCtmPlotTools (geosFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )


#print("")
#print("Date: ", geosObject1.DATE)
#print("")


tracerTools = TracerPlotTools (geosObject1, keyFile, timeRecord, "ZM")

fieldList = geosObject1.fieldList

fieldsToCompare = []
for field in fieldList[:]:
    if field[0:4] != "Var_" and field != "AIRDENS" and field != "PS":
        fieldsToCompare.append(field)



nodes = geosObject1.readNodesIntoArray (pbsNodeFile)
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


print ('\n', fieldsToCompare, '\n')


for field in fieldsToCompare[:]:

    print ("Setting up : ", field)

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

 
    isFieldThere = field in tracerTools.tracerDict
    if isFieldThere == False: 
        field = field.lower()
   
    for slice in tracerTools.tracerDict[field].slices:
        pythonCommand = "PlotTracerSlice.py -c  " + geosFile \
            + " -l " + str(int(slice)) \
            + " -r " + str(timeRecord) + " -d " + dateYearMonth \
            + " -n \"" + tracerTools.tracerDict[field].long_name + "\" " \
            + " -k " + keyFile


        sysCommand = "ssh -XYqt " + nodes[nodeCount] +  " \'. " + cwd + \
            "/setup_env ; cd " + cwd + " ; python " + cwd + "/" + \
            pythonCommand + " -f " + str(field) + " \'"

        commands.append(sysCommand)

        procCount = procCount + 1


    pythonCommandZM = "PlotTracerZM.py -g " + geosFile \
        + " -r " + str(timeRecord) + " -d " + dateYearMonth \
        + " -k " + keyFile
    sysCommandZM = "ssh -XYqt " + nodes[nodeCount] +  " \'. " + cwd + \
        "/setup_env ; cd " + cwd + " ; python " + cwd + "/" + \
        pythonCommandZM + " -f " + str(field) + " \'"
    commands.append(sysCommandZM)
    procCount = procCount + 1


    fieldCount = fieldCount + 1


print("")
for command in commands[:]:
#    if "e90" in command and "Slice" in command:
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


