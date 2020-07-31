#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Oct 17 2019
#
# DESCRIPTION:
# Driver to plot 2D slices and zonal means of a list of tracer species. 
#------------------------------------------------------------------------------
import getopt
import os
import sys
import subprocess
import multiprocessing
import shlex

import matplotlib
matplotlib.use('pdf')

from GeosCtmPlotTools import GeosCtmPlotTools
from TracerPlotTools import TracerPlotTools

def subproc(cmd):
    print(" -> processing: ",cmd)
    cmds = shlex.split(cmd)
    p = subprocess.Popen(cmds,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              universal_newlines=True)

    output, errors = p.communicate()
    return output

def usage ():
    print("")
    print("usage: PlotTracers_GEOS.py [-g] [-c] [-k] [-r] [-d] [-n] [-p] [-t]")
    print("-g GEOS file ")
    print("-c GEOS file ")
    print("-k Key file for tracers ")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-n PBS_NODEFILE")
    print("-p number of processes to use per node")
    print("-t percentage change contours (d-default-+-100, a-algorithmic")
    print("")
    sys.exit (0)


def main():
    print("Start plotting field differences")

    NUM_ARGS = 8

    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'g:c:k:r:d:n:p:t:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    geosFile1 = optList[0][1]
    geosFile2 = optList[1][1]
    keyFile = optList[2][1]
    timeRecord = int(optList[3][1])
    dateYearMonth = optList[4][1]
    pbsNodeFile = optList[5][1]
    numProcesses = int(optList[6][1])
    percChangeContours = str(optList[7][1])

    if not os.path.exists (geosFile1):
        print("The file you provided does not exist: ", geosFile1)
        sys.exit(0)

    if not os.path.exists (geosFile2):
        print("The file you provided does not exist: ", geosFile2)
        sys.exit(0)

    if not os.path.exists (keyFile):
        print("The file you provided does not exist: ", keyFile)
        sys.exit(0)

    if int(timeRecord) > 31:
        print("WARNING: time record is more than a typical daily file!")

    if int(timeRecord) < 0:
        print("ERROR: time record needs to be positive!")
        sys.exit(0)

    if len(dateYearMonth) != 6 and len(dateYearMonth) != 4:
        print("ERROR date must be in the format YYYYMM")
        print("Received: ", dateYearMonth)
        sys.exit(0)

    if not os.path.exists (pbsNodeFile):
        print("The file you provided does not exist: ", pbsNodeFile)
        sys.exit(0)

    if numProcesses <= 0:
        print("Number of processes must be larger than 0! ")
        print("Given: ", numProcesses)
        sys.exit(0)

    if percChangeContours != "d" and percChangeContours != "a":
        print("Percent change contours should be either d(deafult) or a(algorithmic)")
        sys.exit(0)

    geosObject1 = GeosCtmPlotTools (geosFile1, 'lat','lon',
                                    'lev','time', 'lat',
                                    'lon', 'lev', 'time' )

    tracerTools = TracerPlotTools (geosObject1, keyFile, timeRecord, "ZM")

    fieldList = geosObject1.fieldList

    fieldsToCompare = []
    for field in fieldList[:]:
        if field[0:4] != "Var_":
            fieldsToCompare.append(field)

    print("Fields to compare: ", fieldsToCompare[:])
    print("GEOS eta levels: ", geosObject1.lev[:])

    cwd = os.getcwd()

    numTracers = len(tracerTools.tracerDict)
    print("Num tracers: ", numTracers)

    commands = []
    for field in fieldsToCompare[:]:


        isFieldThere = field in tracerTools.tracerDict
        if isFieldThere == False:
            field = field.lower()

        if not field in tracerTools.tracerDict:
            continue

        sliceCommands = []
        for slice in tracerTools.tracerDict[field].slices:

            sliceCommands.append("PlotTracerCompareSlice.py -g " +  geosFile1 \
                                     + " -c " + geosFile2 \
                                     + " -l "  + str(int(slice)) \
                                     + " -r " + str(timeRecord) + " -d " + dateYearMonth \
                                     + " -l \"" + tracerTools.tracerDict[field].long_name + "\" " \
                                     + " -k " + keyFile + " -p " + percChangeContours)

        pythonCommandZM = "PlotTracerCompareZM.py -g " +  geosFile1 \
            + " -c " + geosFile2 \
            + " -r " + str(timeRecord) + " -d " + dateYearMonth \
            + " -k " + keyFile + " -p " + percChangeContours

        sCount = 0
        for _ in tracerTools.tracerDict[field].slices:
            sysCommand = "python " + cwd + "/" + sliceCommands[sCount] + " -f " + str(field)
            commands.append(sysCommand)
            sCount = sCount + 1

        sysCommandZM =  "python " + cwd + "/" + pythonCommandZM + " -f " + str(field)
        commands.append(sysCommandZM)

    print("Process jobs, please wait...")
    jobs = list()
    for cmd in range(len(commands)):
        p = multiprocessing.Process(target=subproc, args=(commands[cmd],))
        jobs.append(p)
        p.start()

    for j in jobs:
        j.join()


if __name__ == "__main__":
    main()

