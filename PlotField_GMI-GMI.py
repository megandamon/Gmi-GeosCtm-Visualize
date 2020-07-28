#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         January 24 2019
#
# DESCRIPTION:
# Driver to plot differences of a single field between GMI species
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


NUM_ARGS = 6
def usage ():
    print("")
    print("usage: PlotField_GMI-GMI.py [-c] [-g] [-r] [-d] [-f] [-v]")
    print("-c GMI file1")
    print("-g GMI file2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-f field to compare")
    print("-v which variable to extract field from")
    print("")
    sys.exit (0)


print("Start plotting field differences.")


#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:f:v:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

gmiFile1 = optList[0][1]
gmiFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
fieldToCompare = optList[4][1]
variableExtractField = optList[5][1]

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



print(gmiFile1)
print(gmiFile2)

gmiSimName1 = gmiFile1.split("_")[1]
gmiSimName2 = gmiFile2.split("_")[1]


print(gmiSimName1)
print(gmiSimName2)

#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------

simType1 = gmiFile1.split(".")[1]
simType2 = gmiFile2.split(".")[1]

#---------------------------------------------------------------
print("")
print("GMI1 simulation type: ", simType1)
print("GMI2 simulation type: ", simType2)
print("")
#--------------------------------------------------------------

if simType1.strip() == "amonthly":
    timeVarName1 = "hdr"
else:
    timeVarName1 = "nymd"

if simType2.strip() == "amonthly":
    timeVarName2 = "hdr"
else:
    timeVarName2 = "nymd"

if simType1.strip() == "idaily" and \
	simType2.strip() == "idaily":
    timeVarName2 = "hdr"
    timeVarName1 = timeVarName2

print ("Variable to extract: ", variableExtractField)

print ("Time var: ", timeVarName2)

if variableExtractField == None or len(variableExtractField) == 0:
    print ("Equals None!")
    labelVar = None
else:
    labelVar = 'const_labels'


gmiObject1 = GmiPlotTools (gmiFile1, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', timeVarName1, labelVar)


gmiObject2 = GmiPlotTools (gmiFile2, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', timeVarName2, labelVar)


order = "GMI"
list1 = gmiObject2.fieldList
list2 = gmiObject1.fieldList

print("")
print("GMI field list: ", list1)
print("")
print("GMI field list2: ", list2)
print("")

if len(gmiObject1.fieldList) >= len(gmiObject2.fieldList):
    list1 = gmiObject1.fieldList
    list2 = gmiObject2.fieldList
    order = "GMI1"

# Does not matter which object to use - this is weird code. 

gmiObject2.fieldName = variableExtractField
fieldsToCompareAll = gmiObject2.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)

print("")
print("Fields to compare: ", fieldsToCompare[:])
print("")


foundField = False
print("")
for fieldInList in fieldsToCompare[:]:

    if fieldToCompare.lower() == fieldInList.lower():
        print("Success: ", fieldToCompare, " can be compared!")
        foundField = True

if foundField == False:
    print("ERROR: ", fieldToCompare, " cannot be compared!")
    sys.exit(-1)



print("GMI model levels: ", gmiObject2.lev[:])
modelLevsToPlotGmi = {}
levCount = 0
for lev in gmiObject2.lev[:]:
    if int(lev) == 992 or int(lev) == 506 or int(lev) == 192:
        modelLevsToPlotGmi [int(lev)] = levCount
    levCount = levCount + 1



# Arrays (one time record, one species)
longRecords = numpy.zeros(gmiObject2.longSize, numpy.float32)

newGmiArray1 = numpy.zeros((gmiObject1.latSize, \
                               gmiObject1.longSize), numpy.float32)
newGmiArray2 = numpy.zeros((gmiObject2.latSize, \
                               gmiObject1.longSize), numpy.float32)

                             


plt.figure(figsize=(20,20))

print("")
print("Processing: ", fieldToCompare)
print("")

field = fieldToCompare

gmiFieldArray1 = gmiObject1.returnField (field, timeRecord, variableExtractField)
gmiFieldArray2 = gmiObject2.returnField (field, timeRecord, variableExtractField)


rankArray1 = size(gmiFieldArray1.shape[:])
rankArray2 = size(gmiFieldArray1.shape[:])


if rankArray1 != rankArray2: 
    print("")
    print(field, " is not the same rank in each file!")
    print("")
    sys.exit(0)


print("")
print("Shape of GMI field 1 : ", gmiFieldArray1.shape[:])
print("Shape of GMI field 2 : ", gmiFieldArray2.shape[:])
print("")


# Prepares basemap objects for plotting
print("")
print("Creating GMI plot objects...")
gmiObject1.createPlotObjects()
gmiObject2.createPlotObjects()
print("")




levCount = 0
for modelLev in modelLevsToPlotGmi:
        
    print("")
    print("GMI : ", modelLev, " mb at index: ", modelLevsToPlotGmi[modelLev])
    print("")


    if gmiFieldArray2.shape != gmiFieldArray1.shape:
        print("Array shapes are different. Exiting.")
        sys.exit(-1)

    levCount = levCount + 1

    extractLevel = modelLevsToPlotGmi[modelLev]
    print("Extracting Gmi level: ", extractLevel)
    
    if rankArray1 == 3: 
        z_Gmi1 = gmiFieldArray1[extractLevel,:,:]
        z_Gmi2 = gmiFieldArray2[extractLevel,:,:]
    else:
        z_Gmi1 = gmiFieldArray1[:,:]
        z_Gmi2 = gmiFieldArray2[:,:]


    z_Diff = z_Gmi1 / z_Gmi2

    print("")
    print("Min/max of GMI1 : ", z_Gmi2.min(), "/", z_Gmi2.max())
    print("Min/max of GMI2: ", z_Gmi1.min(), "/", z_Gmi1.max())
    print("Differences: ", z_Gmi2.min() - z_Gmi1.min(), "/", z_Gmi2.max() - z_Gmi1.max())
    print("")

    zRangeGMI1 = z_Gmi2.max() - z_Gmi2.min()
    zRangeGMI2 = z_Gmi1.max() - z_Gmi1.min()

    print("")
    print("Ranges: ", zRangeGMI1, "/", zRangeGMI2)
    print("")

    orderGMI2 = 1
    orderGMI1 = 1
    if zRangeGMI1 != 0 and zRangeGMI2 !=0:
        orderGMI2 = math.log10(zRangeGMI1)
        orderGMI1 = math.log10(zRangeGMI2)

    print("Orders: ", orderGMI2, "/", orderGMI1)
    print("") 


    minValueOfBoth = z_Gmi1.min()
    maxValueOfBoth = z_Gmi1.max()
        
    if z_Gmi2.min() < minValueOfBoth:
        minValueOfBoth = z_Gmi2.min()
    if z_Gmi2.max() > maxValueOfBoth:
        maxValueOfBoth = z_Gmi2.max()


    # play with ratios a little
    for lat in range(0, size(gmiObject1.lat)):
        for int in range(0, size(gmiObject1.long)):

            if z_Gmi1[lat, int] == 0.0 and z_Gmi2[lat, int] == 0.0:
                z_Diff[lat, int] = 1.0
            elif z_Gmi1[lat, int] != 0.0 and z_Gmi2[lat,int] == 0.0:
                if z_Gmi1[lat, int] > 0.0: z_Diff[lat,int] = 1.5 #saturate
                if z_Gmi1[lat, int] < 0.0: z_Diff[lat,int] = .5 #saturate


    #-----------------------------------------------------#
    # GMI1

    print("")
    print("Min/max ", field, " values at level: ", modelLev)
    print("")


    print("")
    print("GMI1: ", z_Gmi1.min(), " / ", z_Gmi1.max())
    print("")


    if z_Gmi1.max() - z_Gmi1.min() == 0.0 or orderGMI1 < -13:

        print("")
        print("Constant field found for GMI1!")
        print("")

        useMin = z_Gmi1.min()
        useMax = z_Gmi1.max()

    else:
        useMin = minValueOfBoth
        useMax = maxValueOfBoth

    # forcing scales to be the same for both sims
    useMin = minValueOfBoth
    useMax = maxValueOfBoth



    gmiObject1.create2dSlice2 (z_Gmi1, \
#                                   [z_Gmi1.min(), z_Gmi1.max()], \
                                   [useMin, useMax], \
                                   311, "GMI " + gmiSimName1 + "        " + \
                                   variableExtractField + "_" + \
                                   field + " @ " + str(modelLev) + \
                                   "mb " + dateYearMonth, "jet")


    print("")
    print("GMI 2: ", z_Gmi2.min(), " / ", z_Gmi2.max())
    print("") 

    if z_Gmi2.max() - z_Gmi2.min() == 0.0 or orderGMI2 < -13:
        print("Constant field found for GMI2!")
        useMin = z_Gmi2.min()
        useMax = z_Gmi2.max()

    else:
        useMin = minValueOfBoth
        useMax = maxValueOfBoth



    # forcing scales to be the same for both sims
    useMin = minValueOfBoth
    useMax = maxValueOfBoth


    gmiObject1.create2dSlice2 (z_Gmi2, \
#                                   [z_Gmi2.min(), z_Gmi2.max()], \
                                   [useMin, useMax], \
                                   312, "GMI " + gmiSimName2 + "        " + \
                                   variableExtractField + "_" + \
                                   field + " @ " + str(modelLev) + \
                                   " mb " + dateYearMonth, "jet")


    gmiObject1.create2dSlice2 (z_Diff, \
                                     #[z_Diff.min(), z_Diff.max()], \
                                     [.5, 1.5], \
                                     313, "Model ratio        " + \
                                      variableExtractField + "_" + \
                                      field + " @ " + str(modelLev) + \
                                     " mb " + dateYearMonth, \
                                     "nipy_spectral", \
                                     normalize=True)

    #-----------------------------------------------------#



    file = "f"
    if file == "f":
        plt.savefig("plots/" + variableExtractField + "_" + field + ".GMI.GMI."
                    + str(modelLev) + "." , bbox_inches='tight')
    elif file == "s":
        plt.show()
        
    print("")
    print("Plotted : ", fieldToCompare, " @ ", str(modelLev), " to plots/directory")
    print("")


    plt.clf()

    if rankArray1 == 2:
        break

                          
sys.stdout.flush()




