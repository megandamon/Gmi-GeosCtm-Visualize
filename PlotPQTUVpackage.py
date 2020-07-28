#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         July 22 2019
#
# DESCRIPTION:
# Driver to plot differences between surface pressure, specific humidity,
# temperature, and u/v winds.
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







sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')


from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools



def worker (command):
    print("I will execute: ", command)
    return os.system(command)



NUM_ARGS = 7
def usage ():
    print("")
    print("usage: PlotPQTUVpackage.py [-c] [-g] [-r] [-l] [-d] [-n] [-p]")
    print("-c GEOS file 1")
    print("-g GEOS file 2")
    print("-l model level to plot in addition to surface level")
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
optList, argList = getopt.getopt(sys.argv[1:],'c:g:l:r:d:n:p:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

geosFile1 = optList[0][1]
geosFile2 = optList[1][1]
modelLevPlot = optList[2][1]
timeRecord = int(optList[3][1])
dateYearMonthDay = optList[4][1]
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

if int(modelLevPlot) < 0 or int(modelLevPlot) > 72:
    print("The model level for plotting should be >=0 and <=72")

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonthDay) != 8:
    print("ERROR date must be in the format YYYYMMDD")
    print("Received: ", dateYearMonthDay)
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

geosSimName1 = geosFile1.split(".")[0]
geosSimName2 = geosFile2.split(".")[0]


print("")
print("Sim names: ")
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
print("geos 1: ", geosObject1.DATE)
print("geos 2: ", geosObject2.DATE)
print("")

print("")


order = "GEOS"
list1 = geosObject1.fieldList
list2 = geosObject2.fieldList

if len(geosObject1.fieldList) >= len(geosObject2.fieldList):
    list1 = geosObject2.fieldList
    list2 = geosObject1.fieldList
    order = "GEOS"

# Does not matter which object to use - this is weird code. :/
fieldsToCompareAll = geosObject1.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and field[0:3] != "GMI":
        fieldsToCompare.append(field)


print("")
print("Fields to compare: ", fieldsToCompare[:])
print("GEOS 1 model levels: ", geosObject1.lev[:])
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

#geosFile1, geosFile2, timeRecord, dateYearMonthDay
command1 = "PlotField_Generic.py -c  " + geosFile1 + " -g " + geosFile2 + \
    " -l " + modelLevPlot + " -k " + modelLevPlot + \
    " -r " + str(timeRecord) + " -d " + dateYearMonthDay[0:6] + " -u lev " + \
    " -f "

command2 = "PlotField_Generic.py -c  " + geosFile1 + " -g " + geosFile2 + \
    " -l 71 -k 71 "  + \
    " -r " + str(timeRecord) + " -d " + dateYearMonthDay[0:6] + " -u lev " + \
    " -f "

command3 = "PlotField_ZonalMean.py -c " + geosFile1 + " -g " + geosFile2 + \
    " -r " + str(timeRecord) + " -d " + dateYearMonthDay[0:6] + " -f "

for field in ['T', 'QV', 'U', 'V']:


    if field == 'T' or field == "U" or field == "V":
        pythonCommand1 = command1 + field + " -a s"
        pythonCommand2 = command2 + field + " -a s"
        pythonCommand3 = command3 + field + " -v None -m Replay -a s"
    elif field == "QV":
        pythonCommand1 = command1 + field + " -a r"
        pythonCommand2 = command2 + field + " -a r"
        pythonCommand3 = command3 + field + " -v None -m Replay -a r"
        

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


    print("")
    print("Processing: ", field, " to : ", nodes[nodeCount], " proc : ", procCount)
    print("")
    

    sysCommand1 = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand1 + " " + \
        " \' "
    commands.append(sysCommand1)


    sysCommand2 = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand2 + " " + \
        " \' "
    commands.append(sysCommand2)

    sysCommand3 = "ssh -XYqt " + nodes[nodeCount] + \
        " \'. " + cwd + "/setup_env ; " + \
        " cd " + cwd + " ; " + \
        " python " + cwd + "/" + \
        pythonCommand3 + " " + \
        " \' "
    commands.append(sysCommand3)



    procCount = procCount + 3
    fieldCount = fieldCount + 1



# Treat PS alone, since it is a 2D field

psCommand = "PlotField_GEOS-CTM.2D.py -c  " + geosFile1 + " -g " + geosFile2 + \
    " -r " + str(timeRecord) + " -d " + dateYearMonthDay[0:6] + " -f PS "
sysCommandPs = "ssh -XYqt " + nodes[nodeCount] + \
    " \'. " + cwd + "/setup_env ; " + \
    " cd " + cwd + " ; " + \
    " python " + cwd + "/" + \
    psCommand + " " + \
    " \' "
commands.append(sysCommandPs)


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


