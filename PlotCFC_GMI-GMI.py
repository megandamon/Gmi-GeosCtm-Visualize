#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         April 25 2018
#
# DESCRIPTION:
# Driver to plot zonal mean CFCs quantities at the surface (between GMI runs only).
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


import math
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap






sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiPlotTools import GmiPlotTools


NUM_ARGS = 4

CFC_FIELDS = ["CFCl3", "CF2Cl2", "CFC113", "CFC114", "CFC115", "CCl4", \
                   "CH3CCl3", "HCFC22", "HCFC141b", "HCFC142b", "CF2ClBr", "CF2Br2", "CF3Br", "H2402", "CH3Br", "CH3Cl"]


def usage ():
    print("")
    print("usage: PlotCFC_GMI-GMI.py [-c] [-g] [-r] [-d]")
    print("-c GMI NetCDF file 1")
    print("-g GMI NetCDF file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("")
    sys.exit (0)



def createTimeSeriesSubPlot (plt, subPlotNum, xArray, yArray, \
                                 plotTitle, xLabel, yLabel):

    plt.subplot(subPlotNum)

    plt.plot (xArray, yArray, color="blue")

    ax = plt.gca()
    ax.get_yaxis().get_major_formatter().set_useOffset(False)

    plt.title (plotTitle)
    plt.ylabel (yLabel)
    plt.xlabel (xLabel)
    plt.grid(True)


print("Start CFC zonal mean difference plotting")


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

gmiFile1 = optList[0][1]
gmiFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]

#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (gmiFile1):
    print("The file you provided does not exist: ", gmiFile1)
    sys.exit(0)

if not os.path.exists (gmiFile2):
    print("The file you provided does not exist: ", gmiFile2)
    sys.exit(0)


if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)





gmiSimName1 = gmiFile1.split("_")[1]
gmiSimName2 = gmiFile2.split("_")[1]


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------


print("GMI sim 1: ", gmiSimName1)
print("GMI sim 2: ", gmiSimName2)
print("")




gmiObject1 = GmiPlotTools (gmiFile1, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'nymd', 'const_labels')

gmiObject2 = GmiPlotTools (gmiFile2, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', 'nymd', 'const_labels')





order = "GMI"
list1 = gmiObject1.fieldList
list2 = gmiObject2.fieldList


print("")
# print "GMI list1: ", list1
# print ""
# print "GMI list2: ", list2
print("")



if len(list1) != len(list2):
    print("Error: field lists are not the same size! Will exit.")
    sys.exit(-1)


fieldsToCompareAll = gmiObject1.returnFieldsInCommon (list1, list2, order)


fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)

print("")
print("Fields to compare: ", fieldsToCompare[:])
print("")



for CFC in CFC_FIELDS[:]:
    if CFC not in fieldsToCompare[:]:
        print("ERROR! ", CFC, " not found")
        sys.exit(-1)
    else:
        print(CFC, " match found!")

print("")
print("GMI model level 0 ", gmiObject1.lev[0])
print("")



longRecords = numpy.zeros(gmiObject1.longSize, numpy.float32)


# 2D arrays, need only at surface
gmiArray1 = numpy.zeros((gmiObject1.latSize), numpy.float32)
gmiArray2 = numpy.zeros((gmiObject2.latSize), numpy.float32)
gmiArrayRatio = numpy.zeros((gmiObject1.latSize), numpy.float32)

                             

plt.figure(figsize=(20,20))

count = 0
for CFC in CFC_FIELDS[:]:




    print("")
    print("Processing: ", CFC)
    print("")

    field = CFC
    plotTitle = CFC + " surface zonal mean "
    yLabel = "ppbv"
    xLabel = "Latitude"


    gmiFieldArray1 = gmiObject1.returnFieldAtSurface (field, timeRecord, 'const')
    gmiArray1 = numpy.mean(gmiFieldArray1, axis=1)
    gmiArray1[:] = gmiArray1[:] * 1.e9



    createTimeSeriesSubPlot (plt, 311, gmiObject1.lat[:], gmiArray1, \
                                 plotTitle + gmiSimName1, xLabel, yLabel)


    gmiFieldArray2 = gmiObject2.returnFieldAtSurface (field, timeRecord, 'const')
    gmiArray2 = numpy.mean(gmiFieldArray2, axis=1)
    gmiArray2[:] = gmiArray2[:] * 1.e9

    createTimeSeriesSubPlot (plt, 312, gmiObject2.lat[:], gmiArray2, \
                                 plotTitle + gmiSimName2, xLabel, yLabel)



    gmiArrayRatio = gmiArray1[:]/gmiArray2[:]
    

    createTimeSeriesSubPlot (plt, 313, gmiObject2.lat[:], gmiArrayRatio, \
                                 plotTitle + "ratio", xLabel, yLabel)


    file = "f"
    if file == "f":
        plt.savefig("plots/" + field + "." + \
                        gmiSimName1 + "." + gmiSimName2 + "_" + \
                        dateYearMonth + ".surface.", bbox_inches='tight')
    elif file == "s":
        plt.show()
        
    plt.clf()

#    if count == 0: sys.exit(0)
    count = count + 1

    print("")
    print("Plotted : ", field, " to plots/ directory")
    print("")
