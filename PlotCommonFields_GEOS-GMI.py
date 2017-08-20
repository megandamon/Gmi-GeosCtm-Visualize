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






sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


def readNodesIntoArray (nodeFile):

    nodesRead = []

    myFile = open (nodeFile, "r")

    count = 0
    line = myFile.readline().rstrip()
    while line != '':
        nodesRead.append(line)

        if count == 10000: break
        count = count + 1
        line = myFile.readline().rstrip()

    myFile.close()

    nodesToReturn = []
    for node in nodesRead:
         if node not in nodesToReturn: nodesToReturn.append(node)
      
    return nodesToReturn

def worker (command):
    print "I will execute: ", command
    return os.system(command)




NUM_ARGS = 6
def usage ():
    print ""
    print "usage: PlotRestartSpecies.py [-c] [-g] [-r] [-d] [-n] [-p]"
    print "-c GEOS CTM restart file"
    print "-g GMI restart file"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print "-n PBS_NODEFILE"
    print "-p number of processes to use per node"
    print ""
    sys.exit (0)


print "Start plotting restart field differences"

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:n:p:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosCtmFile = optList[0][1]
gmiFile = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])

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

print geosCtmFile
print gmiFile

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
                             'longitude_dim', 'eta_dim', 'hdr')
print ""


order = "GMI"
list1 = gmiObject.fieldList
list2 = geosCtmObject.fieldList

if len(geosCtmObject.fieldList) >= len(gmiObject.fieldList):
    list1 = geosCtmObject.fieldList
    list2 = gmiObject.fieldList
    order = "GEOS-CTM"

# Does not matter which object to use - this is weird code. :/
fieldsToCompare = gmiObject.returnFieldsInCommon (list1, list2, order)


print ""
print "Fields to compare: ", fieldsToCompare[:]
print ""

nodes = readNodesIntoArray (pbsNodeFile)
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
pythonCommand1 = "PlotField_GEOS-GMI.py -c  " + geosCtmFile \
    + " -g " + gmiFile + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f "
pythonCommand2= "PlotField_ZonalMean.py -c " + geosCtmFile \
    + " -g " + gmiFile + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f"

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

    sysCommand = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand2 + " " + field + \
        " \' "
    commands.append(sysCommand)



    procCount = procCount + 2
    fieldCount = fieldCount + 1


    
print ""
for command in commands[:]:
    print command
print "len of commands: ", len(commands)
print ""





pool = multiprocessing.Pool(processes=len(commands))

print ""
print "Calling pool.map"
pool.map(worker, commands)
print ""

print ""
print "Calling pool.close"
pool.close()
print ""

