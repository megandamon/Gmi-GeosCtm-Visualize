#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 5 2020
#
# DESCRIPTION:
# Driver to create daily averages of a month's worth of files.
#------------------------------------------------------------------------------



import re
import os
import glob
import sys
import random
import datetime
from calendar import monthrange
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


from BasicTools import BasicTools

TESTING = False
DO_SSH = False

def worker (command):
    print("I will execute: ", command)
    return os.system(command)



NUM_ARGS = 6
def usage ():
    print("")
    print("usage: CreateDailyAverages.py [-p] [-c] [-d] [-o] [-p] [-q] ")
    print("-p direct path to files ")
    print("-c GEOS collection name ")
    print("-d date of comparision (YYYYMM)")
    print("-o output path")
    print("-p PBS_NODEFILE")
    print("-q number of processes to use per node")
    print("")
    sys.exit (0)


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'p:c:d:o:p:q:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

path = optList[0][1]
collection = optList[1][1]
date = optList[2][1]
outputPath = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])



#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (pbsNodeFile): 
    print("The file you provided does not exist: ", pbsNodeFile)
    sys.exit(0)

if numProcesses <= 0:
    print("Number of processes must be larger than 0! ")
    print("Given: ", numProcesses)
    sys.exit(0)

if not os.path.exists (path):
    print("The path you provided does not exist: ", path)
    sys.exit(0)

if len(date) != 8 and len(date) != 6 and len(date) != 4:
    print("ERROR date must be in the format YYYYMMDD, YYYYMM, YYYY")
    print("Received: ", date)
    sys.exit(0)


print("")



basicTools = BasicTools()
nodes = basicTools.readNodesIntoArray (pbsNodeFile)
print("nodes: ", nodes)

if TESTING == True:
    print ("Testing nodes for access...")
    for node in nodes: 
        sysCommand = "ssh " + node + " \'uname -n \'"
        systemReturnCode = os.system(sysCommand)
        print (sysCommand)
        print (systemReturnCode)
        if systemReturnCode != 0:
            print ("There is a problem with node: ", node)
            sys.exit(0)



year = int(date[0:4])
month = int(date[4:6])


cwd = os.getcwd()
print("\ncurrent working directory: ", cwd)


fileString = path + "/*" + collection +  "*" + date + "*.nc4"
files = glob.glob(fileString)
fileName = files[0]
splitFileName = fileName.split("/")
currentFileName = splitFileName [-1]
splitFileName = currentFileName.split(date)



numDaysInMonth =  (monthrange(year, month))[1]

print ("\nNumber of days in the month ", month, " : ", numDaysInMonth)


commands = []
dayCount = 0 
procCount = 0
nodeCount = 0


for dayOfMonth in range (1,numDaysInMonth+1):

    print ("Creating command for : ", dayOfMonth)
    if dayOfMonth < 10:
        stringDay = "0" + str(dayOfMonth)
        dayOfMonth = stringDay
    
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

    

    newFileName = splitFileName[0] + date + str(dayOfMonth) + ".nc4"
    print (newFileName)


            
    pythonCommand = "CreateAverages.py -p " +  path \
        + " -c " + collection \
        + " -d " + date + str(dayOfMonth) \
        + " -o " + outputPath + " -n " + newFileName 


    if DO_SSH == True:
        sysCommand = "ssh -XYqt " + nodes[nodeCount] +  " \'. " + cwd + \
            "/setup_env ; cd " + cwd + " ; python " + cwd + "/" + \
            pythonCommand + " \'"
        commands.append(sysCommand)
    else:
        commands.append("python " + pythonCommand)


    procCount = procCount + 1 
    dayCount = dayCount + 1


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


