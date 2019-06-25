#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         May 14 2019
#
# DESCRIPTION:
# Driver to plot vertical profiles at an area that has the maximum difference
# between the two data sets.
# 
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
import pylab as pl


import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


from netCDF4 import Dataset
import math




from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap

a60 = [ 4.000000,      8.410209,     15.007380,     23.882399, \
            35.228500,     49.614000,     67.954499,     91.591501, \
            122.426903,    163.065100,    216.956210,    288.637590, \
            384.077191,    511.065197,    679.737186,    903.167152, \
            1197.636032,   1582.196045,   2077.680969,   2705.458069, \
            3485.707092,   4436.783981,   5576.924133,   6926.213837, \
            8506.793976,  10315.518812,  12289.374161,  14334.020781, \
            16321.404725,  18110.111092,  19576.032411,  20638.077710, \
            21266.755819,  21473.879844,  21296.160346,  20781.830521, \
            19984.194862,  18959.598129,  17762.956794,  16445.772200, \
            15056.029843,  13637.103590,  12228.047148,  10861.943576, \
            9562.669233,   8346.207025,   7221.649057,   6192.382004, \
            5257.727627,   4415.565315,   3664.005389,   3000.188436, \
            2419.896338,   1918.332467,   1489.726127,   1127.297079, \
            824.574520,    573.157962,    359.606242,    170.947814, \
            0.000000 ]


b60 = [ 0.00000000,  0.00000000,  0.00000000,  0.00000000, \
            0.00000000,  0.00000000,  0.00000000,  0.00000000, \
            0.00000000,  0.00000000,  0.00000000,  0.00000000, \
            0.00000000,  0.00000000,  0.00000000,  0.00000000, \
            0.00000000,  0.00000000,  0.00000000,  0.00000000, \
            0.00000000,  0.00000000,  0.00000000,  0.00000000, \
            0.00000000,  0.00022552,  0.00143056,  0.00463150, \
            0.01113877,  0.02235216,  0.03944360,  0.06309207, \
            0.09342443,  0.13012139,  0.17256010,  0.21993621, \
            0.27124611,  0.32530609,  0.38094920,  0.43706170, \
            0.49258491,  0.54656649,  0.59815258,  0.64665151, \
            0.69163948,  0.73290408,  0.77040631,  0.80424500, \
            0.83460701,  0.86168867,  0.88564998,  0.90666068, \
            0.92491567,  0.94061267,  0.95396912,  0.96522278, \
            0.97459513,  0.98236012,  0.98894250,  0.99474782, \
            1.00000000 ]

a72 = [ 1.0000000,       2.0000002,       3.2700005,       4.7585009,       6.6000011, \
            8.9345014,       11.970302,       15.949503,       21.134903,       27.852606, \
            36.504108,       47.580610,       61.677911,       79.513413,       101.94402, \
            130.05102,       165.07903,       208.49704,       262.02105,       327.64307, \
            407.65710,       504.68010,       621.68012,       761.98417,       929.29420, \
            1127.6902,       1364.3402,       1645.7103,       1979.1604,       2373.0405, \
            2836.7806,       3381.0007,       4017.5409,       4764.3911,       5638.7912, \
            6660.3412,       7851.2316,       9236.5722,       10866.302,       12783.703, \
            15039.303,       17693.003,       20119.201,       21686.501,       22436.301, \
            22389.800,       21877.598,       21214.998,       20325.898,       19309.696, \
            18161.897,       16960.896,       15625.996,       14290.995,       12869.594, \
            11895.862,       10918.171,       9936.5219,       8909.9925,       7883.4220, \
            7062.1982,       6436.2637,       5805.3211,       5169.6110,       4533.9010, \
            3898.2009,       3257.0809,       2609.2006,       1961.3106,       1313.4804, \
            659.37527,       4.8048257,       0.0000000 ]

b72 = [ 0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,       0.0000000,       0.0000000,       0.0000000,       0.0000000, \
            0.0000000,   8.1754130e-09,    0.0069600246,     0.028010041,     0.063720063, \
            0.11360208,      0.15622409,      0.20035011,      0.24674112,      0.29440312, \
            0.34338113,      0.39289115,      0.44374018,      0.49459020,      0.54630418, \
            0.58104151,      0.61581843,      0.65063492,      0.68589990,      0.72116594, \
            0.74937819,      0.77063753,      0.79194696,      0.81330397,      0.83466097, \
            0.85601798,      0.87742898,      0.89890800,      0.92038701,      0.94186501, \
            0.96340602,      0.98495195,       1.0000000 ]



sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools


NUM_ARGS = 9
def usage ():
    print("")
    print("usage: PlotVerticalProfiles.py [-c] [-g] [-l] [-k] [-r] [-d] [-u] [-f] [-a]")
    print("-c Model file 1")
    print("-g Model file 2")
    print("-l vertical level for file 1")
    print("-k vertical level for file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-u unit of vertical level (lev/hPa)")
    print("-f field to compare")
    print("-a analysis type (d=perc diff, s=simple diff, r=ratio")
    print("")
    sys.exit (0)



print("Start plotting field differences.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:l:k:r:d:u:f:a:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile1 = str(optList[0][1])
modelFile2 = str(optList[1][1])
file1Level = int(optList[2][1])
file2Level = int(optList[3][1])
timeRecord = int(optList[4][1])
dateYearMonth = optList[5][1]
levUnit = str(optList[6][1])
fieldToCompare = str(optList[7][1])
analType = str(optList[8][1])


#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (modelFile1):
    print("The file you provided does not exist: ", modelFile1)
    sys.exit(0)

if not os.path.exists (modelFile2):
    print("The file you provided does not exist: ", modelFile2)
    sys.exit(0)

if file1Level < 0:
    print("The level to plot must be >= 0 (check file 1 lev)")
    sys.exit(0)

if file2Level < 0:
    print("The level to plot must be >= 0 (check file 2 lev)")
    sys.exit(0)

if int(timeRecord) > 30: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)

if analType != "r" and analType != "d" and analType != "s":
    print("ERROR: analysis type must be r (ratios) or d (percent differences) or s (simple difference)")
    sys.exit(0)


print("")
print(modelFile1)
print(modelFile2)
print("")

modelSimName1 = modelFile1.split(".")[0] + "-" + modelFile1.split(".")[1]
modelSimName2 = modelFile2.split(".")[0] + "-" + modelFile2.split(".")[1]



print("")
print("Sim names: ")
print(modelSimName1)
print(modelSimName2)
print("")

splitString1= re.split('[_-]',modelSimName1)
splitString2= re.split('[_-]', modelSimName2)

dateModel1 = splitString1[1]
dateModel2 = splitString2[1]

print("")
print("Dates: ")
print(dateModel1, dateModel2)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
modelObject1 = GeosCtmPlotTools (modelFile1, 'latitude','longitude',\
                                      'lev','time', 'latitude', \
                                      'longitude', 'lev', 'time' )


modelObject2 = GeosCtmPlotTools (modelFile2, 'latitude','longitude',\
                                      'lev','time', 'latitude', \
                                      'longitude', 'lev', 'time' )



order = "1"
list1 = modelObject1.fieldList
list2 = modelObject2.fieldList

if len(modelObject1.fieldList) >= len(modelObject2.fieldList):
    list1 = modelObject2.fieldList
    list2 = modelObject1.fieldList
    order = "1"


fieldsToCompareAll = modelObject1.returnFieldsInCommon (list1, list2, order)

fieldsToCompare = []
for field in fieldsToCompareAll[:]:
    if field[0:4] != "Var_" and \
            field[0:3] != "GMI":
        fieldsToCompare.append(field)



print("")
print("Fields to compare: ", fieldsToCompare[:])
print("Model-1 1 vertical levels: ", modelObject1.lev[:])
print("")


print("")
if fieldToCompare in fieldsToCompare[:]:
    print("Success: ", fieldToCompare, " can be compared!")
else:
    print("ERROR: ", fieldToCompare, " cannot be compared!")
    sys.exit(-1)
print("")





print("")
print("Model levs to search for maximum differences: ", file1Level, " ", file2Level)
print("")


    
print("")
print("Processing: ", fieldToCompare)
print("")
    






modelFieldArray1 = modelObject1.returnField (fieldToCompare, timeRecord)
modelFieldArray2 = modelObject2.returnField (fieldToCompare, timeRecord)
psArray1 = modelObject1.returnField ("PS", timeRecord)
psArray2 = modelObject2.returnField ("PS", timeRecord)



if len(modelFieldArray1.shape) == 2:
    print("")
    print("WARNING!!! Field is 2D")
    print("")
    z_Model1 = modelFieldArray1[:, :]
    z_Model2 = modelFieldArray2[:, :]
    file1Level = 0
    file2Level = 0 

elif len(modelFieldArray1.shape) == 3:
    print("Field is 3D (expected)")
    z_Model1 = modelFieldArray1[file1Level, :, :]
    z_Model2 = modelFieldArray2[file2Level, :, :]
else:
    print("")
    print("Unexpected rank of data!")
    print("")
    sys.exit(0)

print("")


print("")
print("Shape of PS 1: ", psArray1.shape)
print("Shape of PS 2: ", psArray2.shape)
print("")




if z_Model1.shape != z_Model2.shape:

    print("")
    print("Array shapes are different. Interpolation needed!")
    print("")

    # Arrays (one time record, one species)
    longRecords = numpy.zeros(modelObject2.longSize, numpy.float32)
    latRecords = numpy.zeros(modelObject2.latSize, numpy.float32)
    newModel2Array = numpy.zeros((modelObject2.latSize, modelObject1.longSize), numpy.float32)
    newModel2ArrayBoth = numpy.zeros((modelObject1.latSize, modelObject1.longSize), numpy.float32)


    latCount = 0
    for lat in modelObject2.lat[:]:
        
        # pull long records out of model 2
        longRecords[:] = z_Model2[latCount, :]

        yinterp = numpy.interp(modelObject1.long[:], modelObject2.long[:], longRecords)

        newModel2Array [latCount, :] = yinterp[:]
      
        latCount = latCount + 1

    print("")
    print("Model-Temp min / max / shape", newModel2Array.min(), " / ", newModel2Array.max(), " / ", newModel2Array.shape)
    print("")        

    longCount = 0
    for int in modelObject1.long[:]:

        # pull lat records our of model 2
        latRecords[:] = newModel2Array[:,longCount]

        yinterp = numpy.interp(modelObject1.lat[:], modelObject2.lat[:], latRecords)

        newModel2ArrayBoth [:, longCount] = yinterp[:]

        longCount = longCount + 1

    print("")
    print("Interpolated model 2 array min / max: ", newModel2ArrayBoth.min(), " / " , newModel2ArrayBoth.max())
    print("")

    z_Model2 = None
    z_Model2 = newModel2ArrayBoth


    print("")
    print("WARNING: interpolation of PS is not complete! ")
    print("Please finish the implementation before proceeding.")
    print("")

    sys.exit(0)

else:
    print("")
    print("Array shapes are the same, will continue with plotting...")
    print("")



minValueOfBoth = z_Model1.min()
maxValueOfBoth = z_Model1.max()

if z_Model2.min() < minValueOfBoth:
    minValueOfBoth = z_Model2.min()
if z_Model2.max() > maxValueOfBoth:
    maxValueOfBoth = z_Model2.max()


    


         
#-----------------------------------------------------#
# Model-1 

stringLevel1 = str(int(modelObject1.lev[file1Level]))
stringLevel2 = str(int(modelObject2.lev[file2Level]))





print("")
print("model 1 level: ", file1Level, stringLevel1)
print("model 2 level: ", file2Level, stringLevel2)
print("")





print("")

print("Model-1 min / max : ", z_Model1.min(), " / ", z_Model1.max())

print("")


print("")

print("Model-2 min / max ", z_Model2.min(), " / ", z_Model2.max())

print("")





z_Diff = numpy.zeros((modelObject1.latSize, \
                          modelObject1.longSize), numpy.float32)

print("")
print("Size of z_Diff: ", z_Diff.shape)
print("")


latPoints = z_Diff.shape[0]
lonPoints = z_Diff.shape[1]

if analType == "s":

    
    print("")
    print("Getting Simple Differences")
    print("")

    z_Diff = z_Model1 - z_Model2 

    lowEnd = z_Diff.min()
    highEnd = z_Diff.max()

    print("")
    print("low end / high end for diffs: ", lowEnd, " / ", highEnd)
    print("")


    flatzDiff = z_Diff.flatten()

    maxDiffIndex = numpy.argmax(flatzDiff)
    minDiffIndex = numpy.argmin(flatzDiff)

    print("")
    print("max diff @ ", maxDiffIndex, " : ", flatzDiff[maxDiffIndex])
    print("min diff @ ", minDiffIndex, " : ", flatzDiff[minDiffIndex])
    print("")

    
    largestDiff = flatzDiff[maxDiffIndex]

    if abs(flatzDiff[minDiffIndex]) > largestDiff:
        largestDiff = flatzDiff[minDiffIndex]
        maxDiffIndex = minDiffIndex

    print("")
    print("Largest differences @ ", maxDiffIndex, " : ", largestDiff)
    print("")

    print("")
    index2d = unravel_index(maxDiffIndex, (latPoints, lonPoints))
    print("Un-raveled index: ", index2d)
    print("")

    value1 = z_Model1[index2d[0], index2d[1]]
    value2 = z_Model2[index2d[0], index2d[1]]

    if abs(value1-value2) != abs(largestDiff):
        print("")
        print("There was a problem unraveling the index of the largest difference")
        sys.exit(0)
    else:
        print("")
        print("abs value1-value2 = ", abs(value1-value2))
        print("")

    latCoord = modelObject1.lat[index2d[0]]
    lonCoord = modelObject1.long[index2d[1]]

    print("")
    print("lat/lon coord: ", latCoord, "/", lonCoord)
    print("")

           
       
else: 

    print("")
    print("Analysis type: ", analType, " not supported!")
    print("")
    sys.exit(0)
    




print("")
print("modelFieldArray1 shape: ", modelFieldArray1.shape)
print("modelFieldArray2 shape: ", modelFieldArray2.shape)
print("")

levPoints1 = modelFieldArray1.shape[0]
levPoints2 = modelFieldArray2.shape[0]

print("")
print("model levs field1: ", levPoints1)
print("model levs field2: ", levPoints2)
print("")





#  Model 1 / NRL 

vertProfile1 = []


print("")
print("Creating vertical profile bottom to top of model 1")
print("")

for lev1 in range(0,levPoints1): # bottom to top of NRL
    field12dFlat = modelFieldArray1[lev1,:,:].flatten()
    vertProfile1.append(field12dFlat[maxDiffIndex])

print("")
print("Creating pressure coordinates for model 1")
print("")
edgePress1 = []
psArray1Flatten = psArray1.flatten()
a60Rev = a60[::-1]
b60Rev = b60[::-1]
for lev1 in range(0,size(a60)): 
    edgePress1.append(a60Rev[lev1] + (b60Rev[lev1] * psArray1Flatten[maxDiffIndex]))

print("")
print("Edge pressures calculated for ", size(edgePress1[:]), " levels for model 1.")
print("")

midPress1 = []
for lev1 in range(0,levPoints1):
    midPress = exp ( .5 *(log(edgePress1[lev1]) + log(edgePress1[lev1+1])) )
    midPress1.append(midPress/100.)

print("")
print("Mid-level pressures calculated for ", size(midPress1[:]), " levels for model 1.")
print("")


# Model 2 / GEOS

vertProfile2 = []
for lev2 in range(0,levPoints2):

    field22dFlat = modelFieldArray2[lev2,:,:].flatten()
    vertProfile2.append(field22dFlat[maxDiffIndex])

vertProfile2Rev = vertProfile2[::-1] # reverse to surface at level 0
vertProfile2 = vertProfile2Rev


print("")
print("Creating pressure coordinates for model 2")
print("")

edgePress2 = []
psArray2Flatten = psArray2.flatten()
a72Rev = a72[::-1]
b72Rev = b72[::-1]
for lev2 in range(0,size(a72)): 
    edgePress2.append(a72Rev[lev2] + (b72Rev[lev2] * psArray2Flatten[maxDiffIndex]))

print("")
print("Edge pressures calculated for ", size(edgePress2[:]), " levels for model 2.")
print("")

midPress2 = []
for lev2 in range(0,levPoints2):
    midPress = exp ( .5 *(log(edgePress2[lev2]) + log(edgePress2[lev2+1])) )
    midPress2.append(midPress/100.)


print("")
print("Mid-level pressures calculated for ", size(midPress2[:]), " levels for model 2.")
print("")

plt.figure(figsize=(20,20))

print("")
print("Vert profile 1 at surface: ", vertProfile1[0], "(", midPress1[0], " hPa) at : ", vertProfile1[30], " (", midPress1[30], " hPa)")
print("Vert profile 2 at surface: ", vertProfile2[0], "(", midPress2[0], " hPa) at : ", vertProfile2[47], " (", midPress2[47], " hPa)")
print("")

plt.plot(vertProfile1, midPress1[:], color="blue", label='NRL Replayed ')
plt.plot(vertProfile2, midPress2[:], color="red", label='NRL Eta Input')
degree_sign= '\N{DEGREE SIGN}'
plotTitle = dateModel1 + " " + str(latCoord) + degree_sign + " " + str(lonCoord) + degree_sign + " where lev(" + stringLevel1 + \
    ") difference = " + str(flatzDiff[maxDiffIndex])
plt.title (plotTitle)
#plt.title ("Vertical profile at " + str(latCoord) + chr(176) + str(lonCoord) + chr(176) + " where lev(" + stringLevel1 + \
#               ") difference = " + str(flatzDiff[maxDiffIndex]))
plt.ylabel ("pressure coordinates (hPa) ")
plt.xlabel (fieldToCompare)
plt.grid(True)
plt.legend(loc='upper right', shadow=False, fontsize='large')

axes = plt.gca()
axes.invert_yaxis()
axes.set_yscale('log')

minPress = min(min(midPress1), min(midPress2))
maxPress = max(max(midPress1), max(midPress2))
print("min of mid press 1 & 2: ", minPress)
print("max of mid press 1 & 2: ", maxPress)

pressureRange1 = pl.frange (minPress,10.,1.)
pressureRange2 = pl.frange(15,100.,10.)
pressureRange3 = pl.frange(150.,maxPress,150.)
pressureRange = concatenate([pressureRange1,pressureRange2, pressureRange3])
print("pressure range to plot: ", pressureRange[:])

#axes.set_yticks(midPress2[::4])
axes.set_yticks(pressureRange)
axes.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())





#-----------------------------------------------------#


file = "f"
if file == "f":
    plt.savefig("plots/vertProfile." + fieldToCompare + "-" + modelSimName1 \
                    + "." + modelSimName2 + "." + str(flatzDiff[maxDiffIndex]) + ".", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()




print("")
print("Plotted : ", fieldToCompare, " to plots/ directory")
print("") 




    

