
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         May 5 2019
#
# DESCRIPTION:
# Driver to plot a single field from one model.
#-----------------------------------------------------------------------------
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


from netCDF4 import Dataset
import math




from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap





sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools


NUM_ARGS = 6
def usage ():
    print("")
    print("usage: PlotField_Generic.py [-c] [-l] [-r] [-d] [-u] [-f]")
    print("-c Model file")
    print("-l vertical level")
    print("-r time record to plot")
    print("-d date (YYYYMM)")
    print("-u unit of vertical level (lev/hPa)")
    print("-f field to plot")
    print("")
    sys.exit (0)


print("Start plotting field differences.")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:l:r:d:u:f:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

modelFile = str(optList[0][1])
fileLevel = int(optList[1][1])
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
levUnit = str(optList[4][1])
fieldToPlot = str(optList[5][1])


#---------------------------------------------------------------
print("")
print("Checking command line options... ")
print("")
#---------------------------------------------------------------
if not os.path.exists (modelFile):
    print("The file you provided does not exist: ", modelFile)
    sys.exit(0)

if fileLevel < 0:
    print("The level to plot must be >= 0 (check file 1 lev)")
    sys.exit(0)

if int(timeRecord) > 31: 
    print("WARNING: time record is more than a typical daily file!")

if int(timeRecord) < 0: 
    print("ERROR: time record needs to be positive!")
    sys.exit(0)

if len(dateYearMonth) != 6:
    print("ERROR date must be in the format YYYYMM. Received: ", dateYearMonth)
    sys.exit(0)



print("")
print(modelFile)
print("")

modelSimName = modelFile.split(".")[0] + "-" + modelFile.split(".")[1]


print("")
print(modelSimName)
print("")



#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("")
#--------------------------------------------------------------
#modelObject = GeosCtmPlotTools (modelFile, 'latitude','longitude',\
#                                      'lev','time', 'latitude', \
#                                      'longitude', 'lev', 'time' )

modelObject = GeosCtmPlotTools (modelFile, 'lat','lon',\
                                      'lev','time', 'lat', \
                                      'lon', 'lev', 'time' )





print("")
print("Model vertical levels: ", modelObject.lev[:])
print("")







minModelLat = modelObject.lat[:].min()
maxModelLat = modelObject.lat[:].max()
minModelLong = modelObject.long[:].min()
maxModelLong = modelObject.long[:].max()

cenModelLat = (minModelLat + maxModelLat)/2.
cenModelLong =  (minModelLong + maxModelLong)/2.


baseMapModel = Basemap(llcrnrlon=minModelLong,llcrnrlat=minModelLat,\
                             urcrnrlon=maxModelLong,urcrnrlat=maxModelLat,\
                             projection='cyl', \
                             lat_0=cenModelLat,lon_0=cenModelLong)

print("")
print("Basemap info: ")
print("llcr lon: ", minModelLong)
print("llcr lat: ", minModelLat)
print("urc lon: ", maxModelLong)
print("urc lat: ", maxModelLat)
print("centers lat/long: ", cenModelLat, cenModelLong)
print("")



gridLonsModel,gridLatsModel = baseMapModel.makegrid(modelObject.longSize, \
                                                              modelObject.latSize)
X_Model, Y_Model = baseMapModel(gridLonsModel,gridLatsModel)


plt.figure(figsize=(20,20))


    




print("")
print("Processing: ", fieldToPlot)
print("")
    






modelFieldArray = modelObject.returnField (fieldToPlot, timeRecord)

print("")
print("modelFieldArray shape: ", modelFieldArray.shape)
print("")

print("")
print("Global sum of ", fieldToPlot, " : ", sum(modelFieldArray))
print("")



if len(modelFieldArray.shape) == 2:
    print("")
    print("WARNING!!! Field is 2D")
    print("")
    z_Model = modelFieldArray[:, :]
    fileLevel = 0

elif len(modelFieldArray.shape) == 3:
    print("Field is 3D (expected)")
    z_Model = modelFieldArray[fileLevel, :, :]
else:
    print("")
    print("Unexpected rank of data!")
    print("")
    sys.exit(0)

print("")



    


         
#-----------------------------------------------------#
# Model  Plotting

stringLevel = str(int(modelObject.lev[fileLevel]))




print("")
print("model level: ", fileLevel, stringLevel)
print("")


print("")

print("Model min / max : ", z_Model.min(), " / ", z_Model.max())

print("")

modelObject.create2dSliceContours (baseMapModel, X_Model, Y_Model, z_Model, \
                                [z_Model.min(),z_Model.max()], \
                                [minModelLat,maxModelLat], \
                                [minModelLong, maxModelLong], 311, \
                                fieldToPlot + " @ " + stringLevel + \
                                " " + str(levUnit), \
                                "jet")



file = "f"
if file == "f":
    plt.savefig("plots/" + fieldToPlot + "-" + modelSimName + "_" + stringLevel \
                    + ".", \
                    bbox_inches='tight')
elif file == "s":
    plt.show()
        
plt.clf()




print("")
print("Plotted : ", fieldToPlot, " to plots/ directory")
print("") 




    

