
#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         August 30 2020
#
# DESCRIPTION:
# Will read the field from the files and create a time series plot
#------------------------------------------------------------------------------





import re
import os
import glob
import sys
import random
import calendar
import getopt
import numpy
from numpy import *
from scipy.interpolate import interp1d






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

from datetime import datetime


NUM_ARGS = 3
def usage ():
    print("")
    print("usage: PlotTimeSeriesFromFile.py [-p][-d] [-v]")
    print("-p Path to time records 1")
    print("-d Path to time records 2")
    print("-v Field/variable")
    sys.exit (0)


def main():
    print ("\nWill create file for regional sum for file")

    
    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'p:v:d:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    filePath = optList[0][1]
    filePath2 = optList[1][1]
    field = optList[2][1]


    #---------------------------------------------------------------
    print("")
    print("Checking command line options... ")
    print("")
    #---------------------------------------------------------------


    icarttOperations = GmiIcarttOperations()


    filesFromPath = glob.glob (filePath + "/" + field + "*")
    filesFromPath.sort()

    globalAverages = []
    dateTimes = []
    dateShorts = []
    
    for aFile in filesFromPath:
        fileToken = aFile.split(field)[1]
        dateTime1 = fileToken.split("z_")[0]
        dateTime = dateTime1.split(".")[1]
        dateShort = dateTime.split("_")[0]
        dateTimes.append(dateTime)
        dateShorts.append((dateShort))
        
        fileIn = open(aFile, "r")
        readIn = fileIn.read()
        globalAverages.append(float(readIn))
        fileIn.close()


    filesFromPath2 = glob.glob (filePath2 + "/" + field + "*")
    filesFromPath2.sort()


    globalAverages2 = []
    dateTimes2 = []
    dateShorts2 = []
    
    for aFile in filesFromPath2:
        fileToken = aFile.split(field)[1]
        dateTime1 = fileToken.split("z_")[0]
        dateTime = dateTime1.split(".")[1]
        dateShort = dateTime.split("_")[0]
        dateTimes2.append(dateTime)
        dateShorts2.append((dateShort))
        
        fileIn = open(aFile, "r")
        readIn = fileIn.read()
        globalAverages2.append(float(readIn))
        fileIn.close()


    xValues = [datetime.strptime(d, "%Y%m%d").date() for d in dateShorts]
    xValues2 = [datetime.strptime(d, "%Y%m%d").date() for d in dateShorts2]


    #gA1Array = numpy.array(globalAverages)
    #f = interp1d(dateShorts, gA1Array)
    #f2 = interp1d(dateShorts, gA1Array, kind='cubic')
    
    plt.figure(figsize=(26,10))



    plt.plot(xValues, globalAverages, color="blue", label="fix12",marker='.', ls='none')
    plt.plot(xValues2, globalAverages2, color="red", label="NRT", marker='.', ls='none')
    #plt.plot (gA1Array, f(gA1Array), '_')


    plt.title ("Global Averages of TPREC", size=30)
    plt.ylabel ("TPREC (kg m-2 s-1) * 86400", size=20)

    plt.legend(prop={'size':25})


    plt.grid(True)



    plt.savefig("plots/test.png", 
                bbox_inches='tight')


    
if __name__ == "__main__":
    main()
