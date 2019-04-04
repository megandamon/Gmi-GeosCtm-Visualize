#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         January 24th 2018
#
# DESCRIPTION:
# Driver to plot differences between fields & species coming from 2 GMI-CTM simulations.
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


NUM_ARGS = 8
def usage ():
    print ""
    print "usage: PlotCommonFields_GMI-GMI.py [-c] [-g] [-r] [-d] [-n] [-p] [-s] [-v]"
    print "-c GMI file 1"
    print "-g GMI file 2"
    print "-r time record to plot"
    print "-d date of comparision (YYYYMM)"
    print "-n PBS_NODEFILE"
    print "-p number of processes to use per node"
    print "-s string defining the GMI array with species/fields names (const_labels, etc.)"
    print "-v variable to extract GMI array fields from (const, scav. etc.)"
    print ""
    sys.exit (0)


print "Start plotting restart field differences"

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:n:p:s:v:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

gmiFile1 = optList[0][1]
gmiFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])
fieldNameArrayGMI = optList[6][1]
variableExtractField = optList[7][1]

#---------------------------------------------------------------
print ""
print "Checking command line options... "
print""
#---------------------------------------------------------------
if not os.path.exists (gmiFile1):
    print "The file you provided does not exist: ", gmiFile1
    sys.exit(0)

if not os.path.exists (gmiFile2):
    print "The file you provided does not exist: ", gmiFile2
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

print ""
print "Will be looking at GMI fields in: ", fieldNameArrayGMI
print ""

print gmiFile1
print gmiFile2
print ""

gmiSimName1 = gmiFile1.split(".")[0]
gmiSimName2 = gmiFile2.split("_")[1]


#---------------------------------------------------------------
print ""
print "Command line options look good."
print "GMI1 simulation name: ", gmiSimName1
print "GMI2 simulation name: ", gmiSimName2
print""
#--------------------------------------------------------------

gmiObject1 =  GmiPlotTools (gmiFile1, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'hdr', fieldNameArrayGMI)
print ""

gmiObject2 = GmiPlotTools (gmiFile2, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'hdr', fieldNameArrayGMI)
print ""

print fieldNameArrayGMI
print ""



order = "GMI2"
list1 = gmiObject2.fieldList
list2 = gmiObject1.fieldList


if len(gmiObject1.fieldList) >= len(gmiObject2.fieldList):
    list1 = gmiObject1.fieldList
    list2 = gmiObject2.fieldList
    order = "GMI1"

# Does not matter which object to use - this is weird code. :/
gmiObject2.fieldName = variableExtractField
fieldsToCompare = gmiObject2.returnFieldsInCommon (list1, list2, order)

print "variableExtractField: ", variableExtractField
print ""



print ""
print "Fields to compare: ", fieldsToCompare[:]
print ""

#print list1[:]
#print list2[:]


nodes = gmiObject2.readNodesIntoArray (pbsNodeFile)
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

#gmiFile1 gmiFile2, timeRecord, dateYearMonth
pythonCommand1 = "PlotField_GMI-GMI.py -c  " + gmiFile1 \
    + " -g " + gmiFile2 + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f "
pythonCommand2= "PlotField_ZonalMean_GMI.py -c " + gmiFile1 \
    + " -g " + gmiFile2 + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f"

for field in fieldsToCompare[:]:

    if procCount == numProcesses: 
        print "node count exceeds num processes per node: ", procCount
        procCount = 0
        nodeCount = nodeCount + 1

        if nodeCount >= len(nodes):
            print ""
            print "ERROR: number of commands added to queue ", len(commands)
            print "Number of nodes available: ", len(nodes)
            print "Number of processes per node: ", numProcesses
            print "number of fields to compare: ", len(fieldsToCompare)
            print "Node count: ", nodeCount
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
        pythonCommand1 + " " + field + " -v " + variableExtractField + \
        " \' "
    commands.append(sysCommand)

    sysCommand = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand2 + " " + field + " -v " + variableExtractField + \
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
pool.map(workerLocal, commands)
print ""

print ""
print "Calling pool.close"
pool.close()
print ""



sys.stdout.flush()
