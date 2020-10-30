#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Oct 1 2020
#
# DESCRIPTION:
# Driver to interpolate GEOS_CF fields to
# pressure levels from eta and save the data.
#------------------------------------------------------------------------------


import getopt
import os
import sys
from datetime import timedelta

from MultiHdfFile_Class import MultiHdfFile_Class

#*********************
PRESSURE_LEVELS = [1000, 975, 950, 925, 900, 850, 800, 750, 700, 650, 600, 550, \
                   500, 450, 400, 350, 316, 261, 215, 178, 147, 121, 100, 83, \
                   68, 56, 50, 46, 38, 31, 26, 22, 18, 15, 12, 10, 8, 5, 2, 1]
#*********************



def usage ():
    print("")
    print("usage: InterpSaveCf.py [-p] [-a] [-x] [-s] [-e] [-c] ")
    print("-p path to data in GEOS5 structure 1")
    print("-a path to data in GEOS5 structure 2")
    print("-x path to save pressure data from GEOS5 structure 2")
    print("-s date of first comparison (YYYYMM)")
    print("-e date of first comparison (YYYYMM)")
    print("-c collection")
    print("-t time delta DD_HHMM format")
    print("")
    sys.exit (0)


def main():
    
    print("\nStart interpolating CF collections")

    NUM_ARGS = 7

    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'p:a:x:s:e:c:t:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    dataPath1 = optList[0][1]
    dataPath2 = optList[1][1]
    dataPathPress2 = optList[2][1]
    startDate = optList[3][1]
    endDate = optList[4][1]
    collection = optList[5][1]
    timeDelta = str(optList[6][1])

    
    
    if not os.path.exists (dataPath1):
        print("The path you provided does not exist: ", dataPath1)
        sys.exit(0)

    if not os.path.exists (dataPath2):
        print("The path you provided does not exist: ", dataPath2)
        sys.exit(0)

    if not os.path.exists (dataPathPress2):
        print("The path you provided does not exist: ", dataPathPress2)
        sys.exit(0)

    if len(startDate) != 13:
        print("ERROR date must be in the format YYYYMMDD_HHMM")
        sys.exit(0)

    if len(endDate) != 13:
        print("ERROR date must be in the format YYYYMMDD_HHMM")
        sys.exit(0)

    if len(timeDelta) != 7:
        print("ERROR time delta must be in the format DD_HHMM")
        sys.exit(0)




    path1Tokens = dataPath1.split("/")
    count = 0
    for token in path1Tokens:
        if "GEOS-CF" in token:
            expName1 = token
            break
        count = count + 1
    expName2 = dataPath2.split("/")[count]

        
    
    print ("\nReady to interpolate files from collection: ", collection)



    
    multiFileObject1 = MultiHdfFile_Class (startDate, endDate, dataPath1, \
                                          collection, timedelta (hours=1), \
                                          "GEOS-CF_pub")

    timeResolution = multiFileObject1.createTimeDeltaFromString (timeDelta)


    multiFileObject2 = MultiHdfFile_Class (startDate, endDate, dataPath2, \
                                          collection, timedelta (hours=1), \
                                          "GEOS-CF_pub")

    timeResolution = multiFileObject2.createTimeDeltaFromString (timeDelta)


    
    multiFileObject1.createInterpolatedFiles (PRESSURE_LEVELS)
    multiFileObject2.createInterpolatedFiles (PRESSURE_LEVELS, newPath=dataPathPress2)


if __name__ == "__main__":
    main()
