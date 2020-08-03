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
    print("usage: PlotTracers_GEOS.py [-g] [-k] [-r] [-d] [-n] [-p] [-m]")
    print("-g GEOS file ")
    print("-k Key file for tracers ")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-n PBS_NODEFILE")
    print("-p number of processes to use per node")
    print("-m configuration name (Replay, CCM, etc.)")
    print("")
    sys.exit (0)


def main():


    NUM_ARGS = 7

    #---------------------------------------------------------------
    # START:: Get options from command line
    #---------------------------------------------------------------
    optList, argList = getopt.getopt(sys.argv[1:],'g:k:r:d:n:p:m:')
    if len (optList) != NUM_ARGS:
       usage ()
       sys.exit (0)

    geosFile = optList[0][1]
    keyFile = optList[1][1]
    timeRecord = int(optList[2][1])
    dateYearMonth = optList[3][1]
    pbsNodeFile = optList[4][1]
    numProcesses = int(optList[5][1])
    configName = optList[6][1]

    if not os.path.exists (geosFile):
        print("The geos file you provided does not exist: ", geosFile)
        sys.exit(0)

    if not os.path.exists (keyFile):
        print("The key file you provided does not exist: ", keyFile)
        sys.exit(0)

    if int(timeRecord) > 30:
        print("WARNING: time record is more than a typical daily file!")

    if int(timeRecord) < 0:
        print("ERROR: time record needs to be positive!")
        sys.exit(0)

    if len(dateYearMonth) != 6 and len(dateYearMonth) != 4:
        print("ERROR date must be in the format YYYY or YYYYMM")
        print("Received: ", dateYearMonth)
        sys.exit(0)

    if not os.path.exists (pbsNodeFile):
        print("The file you provided does not exist: ", pbsNodeFile)
        sys.exit(0)

    if numProcesses <= 0:
        print("Number of processes must be larger than 0! ")
        print("Given: ", numProcesses)
        sys.exit(0)

    geosObject1 = GeosCtmPlotTools (geosFile, 'lat','lon',\
                                          'lev','time', 'lat', \
                                          'lon', 'lev', 'time' )

    tracerTools = TracerPlotTools (geosObject1, keyFile, timeRecord, "ZM")

    fieldList = geosObject1.fieldList

    fieldsToCompare = []
    for field in fieldList[:]:
        if field[0:4] != "Var_" and field != "AIRDENS" and field != "PS":
            fieldsToCompare.append(field)

    cwd = os.getcwd()
    commands = list()

    for field in fieldsToCompare[:]:

        print ("Setting up : ", field)

        if not field in tracerTools.tracerDict:
            continue

        for slice in tracerTools.tracerDict[field].slices:
            pythonCommand = "PlotTracerSlice.py -c  " + geosFile \
                + " -l " + str(int(slice)) \
                + " -r " + str(timeRecord) + " -d " + dateYearMonth \
                + " -n \"" + tracerTools.tracerDict[field].long_name + "\" " \
                + " -k " + keyFile

            sysCommand = "python " + cwd + "/" + pythonCommand + " -f " + str(field)

            commands.append(sysCommand)

        pythonCommandZM = "PlotTracerZM.py -g " + geosFile \
            + " -r " + str(timeRecord) + " -d " + dateYearMonth \
            + " -k " + keyFile

        sysCommandZM = "python " + cwd + "/" + pythonCommandZM + " -f " + str(field)
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
