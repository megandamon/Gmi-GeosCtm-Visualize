#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         August 30 2020
#
# DESCRIPTION:
# Driver create a global sum for specified field for each file between
# start and end dates
#------------------------------------------------------------------------------
import getopt
import os
import sys
import subprocess
import multiprocessing
import shlex

from datetime import *
from datetime import timedelta


from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools

def subproc(cmd):
    name = multiprocessing.current_process().name
    print(f'Starting {name} ')
    cmds = shlex.split(cmd)
    print (cmds)
    p = subprocess.Popen(cmds,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              universal_newlines=True)
    output, errors = p.communicate()
    print (output)
    print (errors)
    print(f'Exiting {name}')
    return output


def usage ():
    print("")
    print("usage: PrepTimeSeries_GEOS-CF.py [-p] [-s] [-e] [-m] [-v] [-u]")
    print("-p path to data (year, month, and day subdirs will be created")
    print("-s start date in format YYYYMMDD_HHMM")
    print("-e end date in format YYYYMMDD_HHMM")
    print("-m metfield collection (ex: met_tavg_1h_g1440x721")
    print("-v field/variable to extract")
    print("-u untar archive? T/F")
    print("")
    sys.exit (0)


def main():
    print("\nStart setting up threads for each day between start and end dates.")

    NUM_ARGS = 6

    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'p:s:e:m:v:u:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    filePath = optList[0][1]
    startDate = optList[1][1]
    endDate = optList[2][1]
    metCollection = optList[3][1]
    fieldToExtract = optList[4][1]
    untar = str(optList[5][1])

    if not os.path.exists (filePath):
        print("The path you provided does not exist: ", filePath)
        sys.exit(0)

    if len(startDate) != 13:
        print("ERROR date must be in the format YYYYMMDD_HHMM")
        sys.exit(0)

    if len(endDate) != 13:
        print("ERROR date must be in the format YYYYMMDD_HHMM")
        sys.exit(0)



    startYear = startDate[0:4]
    startMonth = startDate[4:6]
    startDay = startDate[6:8]
    startHour = startDate[9:11]
    startMinute = startDate[11:13]
    endYear = endDate[0:4]
    endMonth = endDate[4:6]
    endDay = endDate[6:8]
    endHour = endDate[9:11]
    endMinute = endDate[11:13]

    
    startDateObject = datetime.strptime (startDate[0:8], "%Y%m%d")
    hhmmDelta = timedelta (hours=int(startHour), minutes=int(startMinute))
    startDateObject = startDateObject + hhmmDelta

    endDateObject = datetime.strptime (endDate[0:8], "%Y%m%d")
    hhmmDelta = timedelta (hours=int(endHour), minutes=int(endMinute))
    endDateObject = endDateObject + hhmmDelta

    stepObject = timedelta (hours=1)

    cwd = os.getcwd()
    commands = list()
    while startDateObject < endDateObject:

        currentYear = str(startDateObject.year)
        
        if startDateObject.month < 10:
            currentMonth = "0" + str(startDateObject.month)
        else:
            currentMonth = str(startDateObject.month)

        if startDateObject.day < 10:
            currentDay = "0" + str(startDateObject.day)
        else:
            currentDay = str(startDateObject.day)

        if startDateObject.hour < 10:
            currentHour = "0" + str(startDateObject.hour)
        else:
            currentHour = str(startDateObject.hour)

        if startDateObject.minute < 10:
            currentMinute = "0" + str(startDateObject.minute)
        else:
            currentMinute = str(startDateObject.minute)


        print (currentYear, currentMonth, currentDay, currentHour, currentMinute)

        #            currentDay + "/GEOS-CF.v01.rpl." + metCollection + \
        currentFile = filePath + "/Y" + currentYear + "/M" + currentMonth + "/D" + \
            currentDay + "/c360_GEOS-CF." + metCollection + \
            "_x1." + currentYear + currentMonth + \
            currentDay + "_" + currentHour + currentMinute + "z_uncompressed.nc4"
            #currentDay + "_" + currentHour + currentMinute + "z.nc4"

        currentCommand = "PrintRegionalGlobalSumToFile.py  -f " + \
            currentFile + " -v " + fieldToExtract + " -l -60 -e 60 -n -180 -g 180 -u  " + \
            untar
            

        sysCommand = "python " + cwd + "/" + currentCommand
        
        print (sysCommand)

        os.system(sysCommand)
        commands.append(sysCommand)
        startDateObject += stepObject

    
    #print("\n\nProcessing jobs...")

    
    
    # jobs = list()
    # for cmd in range(len(commands)):
    #     print (cmd)
    #     p = multiprocessing.Process(target=subproc, args=(commands[cmd],))
    #     jobs.append(p)
    #     p.start()

    # for j in jobs:
    #     j.join()
                           
                                        

if __name__ == "__main__":
    main()
