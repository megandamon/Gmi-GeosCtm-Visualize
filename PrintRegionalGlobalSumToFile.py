
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         August 30 2020
#
# DESCRIPTION:
# Will read the field from the provided file, and create
# a single file with its regional sum.
#------------------------------------------------------------------------------





import re
import os
import sys
import random
import calendar
import getopt
import numpy
from numpy import *






sys.path.append('/discover/nobackup/mrdamon/Devel/ICARTT/GMI_ICARTT_Processing')


import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


from netCDF4 import Dataset
import math

import tarfile


from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap





sys.path.append('/discover/nobackup/mrdamon/MERRA2')

from GeosCtmPlotTools import GeosCtmPlotTools
from GenericModelPlotTools import GenericModelPlotTools
from GmiIcarttOperations import *

from datetime import *


NUM_ARGS = 7
def usage ():
    print("")
    print("usage: PrintRegionalGlobalSumToFile.py [-f][-v][-l][-e][-n][-g][-u]")
    print("-f File")
    print("-v Field/variable")
    print ("-l latitude start (degrees)")
    print ("-e latitude end (degrees)")
    print ("-n longitude start (degrees)")
    print ("-g longitude end (degrees)")
    print("-u untar archive? T/F")
    sys.exit (0)


def main():
    print ("\nWill create file for regional sum for file")

    
    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'f:v:l:e:n:g:u:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    hdfFile = optList[0][1]
    field = optList[1][1]
    startLat = float(optList[2][1])
    endLat = float(optList[3][1])
    startLon = float(optList[4][1])
    endLon = float(optList[5][1])
    untar = str(optList[6][1])


    #---------------------------------------------------------------
    print("")
    print("Checking command line options... ")
    print("")
    #---------------------------------------------------------------
    if not os.path.exists (hdfFile):
        
        print("The file you provided does not exist: ", hdfFile)

        # extract the file's hhmm and yymmdd 
        hdfFileTokens1 = hdfFile.split("_x1")
        hdfFileTokens2 = hdfFileTokens1[-1].split(".")
        hdfFileTokens3 = hdfFileTokens2[-2].split("_")
        hhmm = hdfFileTokens3[-2][0:4]
        yymmdd = hdfFileTokens3[-3][0:8]

        # the archive that has the file we are looking for
        # may not be the same day!
        untarDay = datetime.strptime(yymmdd, "%Y%m%d")
        untarFile = hdfFile        
        if int(hhmm) > 1130:
            print ("\nUntarring the next day!")
            timeDelta = timedelta (days=1)
            untarDay = untarDay + timeDelta

        untarYear = str(untarDay.year)
        if untarDay.month < 10:
            untarMonth = "0" + str(untarDay.month)
        else:
            untarMonth = str(untarDay.month)

        if untarDay.day < 10:
            untarDay = "0" + str(untarDay.day)
        else:
            untarDay = str(untarDay.day)

        untarYYMMDD = untarYear + untarMonth + untarDay

        untarFile = untarFile.replace(yymmdd,untarYYMMDD)

        # generate the tar file name
        untarFile = untarFile.replace("_" + hhmm + "z_uncompressed.nc4", ".ana.uncompressed.tar")
        untarFile = untarFile.replace("Y"+yymmdd[0:4], "Y"+untarYear)
        untarFile = untarFile.replace("M"+yymmdd[4:6], "M"+untarMonth)
        untarFile = untarFile.replace("D"+yymmdd[6:8], "D"+untarDay)

        hdfFile = hdfFile.replace("Y"+yymmdd[0:4], "Y"+untarYear)
        hdfFile = hdfFile.replace("M"+yymmdd[4:6], "M"+untarMonth)
        hdfFile = hdfFile.replace("D"+yymmdd[6:8], "D"+untarDay)

        print ("\nUntar file: ", untarFile)
        print ("\nHdf file: ", hdfFile)
        
        untarDirTokens = untarFile.split("c360_GEOS-CF.")
        untarDir = untarDirTokens[0]

        myTar = tarfile.open(untarFile)
        myTar.extractall (untarDir)
        myTar.close()


    icarttOperations = GmiIcarttOperations()

    ncData = Dataset(hdfFile, "r", format="NETCDF4")
    lonArray = ncData.variables['lon']
    latArray = ncData.variables['lat']
    levArray = ncData.variables['lev']
    timeArray = ncData.variables['time']


    # based on the input args, get the lat and lon coordinates of this region
    reducedLatCoords = icarttOperations.returnMinMaxGmiCoords (startLat, endLat, latArray)
    reducedLonCoords = icarttOperations.returnMinMaxGmiCoords (startLon, endLon, lonArray)

    minLong = reducedLonCoords[0]
    maxLong = reducedLonCoords[-1]

    minLat = reducedLatCoords[0]
    maxLat = reducedLatCoords[-1]

    print("\n")
    print("Min long / max long : ", minLong, "/", maxLong)
    print("Min lat / max lat : ", minLat, "/", maxLat)
    print("")

    newArray2D = numpy.zeros(((maxLat-minLat) + 1 , (maxLong-minLong) + 1))

    varObject = ncData.variables[field]
    newArray2D[:,:] = varObject[0, minLat:maxLat+1,minLong:maxLong+1]

    globalAvg = numpy.average(newArray2D) * 86400.

    print ("\nAvg of ", field, " : ", globalAvg)


    fileNameTokens1 = hdfFile.split(".")
    dateTimeToken = fileNameTokens1[-2]

    #print (dateTimeToken)
    #print (fileNameTokens1)

    fileName = dateTimeToken + ".dat"

    print ("\n", fileName)

#    fileOut = open("timeSeriesGEOS-CF_NRT/" + field + "." + fileName, "w")
    fileOut = open("timeSeries_GEOS-CF_fix12z/" + field + "." + fileName, "w")
    fileOut.write(str(globalAvg))
    fileOut.close()

    ncData.close()

if __name__ == "__main__":
    main()
