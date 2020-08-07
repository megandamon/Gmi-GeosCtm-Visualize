#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         January 24th 2018
#
# DESCRIPTION:
# Driver to plot differences between fields & species
#  coming from 2 GMI-CTM simulations.
#------------------------------------------------------------------------------


import os
import sys
import getopt

import multiprocessing
import shlex
import subprocess


from GmiPlotTools import GmiPlotTools
from GmiDef import *

def subproc(cmd):
    print(" -> processing: ",cmd)
    cmds = shlex.split(cmd)
    p = subprocess.Popen(cmds,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              universal_newlines=True)

    output, errors = p.communicate()
    return output



NUM_ARGS = 9
def usage ():
    print("")
    print("usage: PlotCommonFields_GMI-GMI.py [-c][-g][-r][-d][-n][-p][-s][-v][-t]")
    print("-c GMI file 1")
    print("-g GMI file 2")
    print("-r time record to plot")
    print("-d date of comparision (YYYYMM)")
    print("-n PBS_NODEFILE")
    print("-p number of processes to use per node")
    print("-s array name of species/fields  (const_labels, etc.)")
    print("-v variable to extract GMI array fields from (const, scav. etc.)")
    print("-t type of plots (Q-quick, S-Standard, C-Complete")
    print("")
    sys.exit (0)


print("\nStart plotting restart field differences")

#---------------------------------------------------------------
# START:: Get options from command line
#---------------------------------------------------------------
optList, argList = getopt.getopt(sys.argv[1:],'c:g:r:d:n:p:s:v:t:')
if len (optList) != NUM_ARGS:
   usage ()
   sys.exit (0)

gmiFile1 = optList[0][1]
gmiFile2 = optList[1][1]
timeRecord = int(optList[2][1])
dateYearMonth = optList[3][1]
pbsNodeFile = optList[4][1]
numProcesses = int(optList[5][1])
fieldNameArrayGMI = optList[6][1]
variableExtractField = optList[7][1]
packageType = str(optList[8][1])

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

if not os.path.exists (pbsNodeFile): 
    print("The file you provided does not exist: ", pbsNodeFile)
    sys.exit(0)

if numProcesses <= 0:
    print("Number of processes must be larger than 0! ")
    print("Given: ", numProcesses)
    sys.exit(0)

if packageType != "Q" and packageType != "S" and packageType != "C":
    print("Please provide packageType as Q, S, or C")
    print("Given: ", packageType)
    sys.exit(0)



    
print("")
print("Plotting GMI fields from: ", fieldNameArrayGMI)
print("")

print(gmiFile1)
print(gmiFile2)
print("")



gmiSimName1 = gmiFile1.split(".")[0]
gmiSimName2 = gmiFile2.split("_")[1]


#---------------------------------------------------------------
print("")
print("Command line options look good.")
print("GMI1 simulation name: ", gmiSimName1)
print("GMI2 simulation name: ", gmiSimName2)
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

if simType1.strip() == "amonthly" or simType1.strip() == "idaily":
    timeVarName1 = "hdr"
else:
    timeVarName1 = "nymd"

if simType2.strip() == "amonthly" or simType2.strip() == "idaily":
    timeVarName2 = "hdr"
else:
    timeVarName2 = "nymd"


# here we can select nymd or hdr based on simType1,2 above

gmiObject1 =  GmiPlotTools (gmiFile1, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', timeVarName1, \
                            fieldNameArrayGMI)
print("")

gmiObject2 = GmiPlotTools (gmiFile2, 'latitude_dim', 'longitude_dim', \
                             'eta_dim', 'rec_dim', 'latitude_dim', \
                             'longitude_dim', 'eta_dim', timeVarName2, \
                           fieldNameArrayGMI)


print("")
print("Field to extract species names from: ", fieldNameArrayGMI)
print("")


order = "GMI2"
list1 = gmiObject2.fieldList
list2 = gmiObject1.fieldList


if len(gmiObject1.fieldList) >= len(gmiObject2.fieldList):
    list1 = gmiObject1.fieldList
    list2 = gmiObject2.fieldList
    order = "GMI1"

# Does not matter which object to use - this is weird code. :/
gmiObject2.fieldName = variableExtractField
fieldsToCompare = gmiObject2.returnFieldsInCommon (list1, list2, order)


cwd = os.getcwd()



commands = []
fieldCount = 0
procCount = 0
nodeCount = 0

#gmiFile1 gmiFile2, timeRecord, dateYearMonth
pythonCommand1 = "PlotField_GMI-GMI.py -c  " + gmiFile1 \
    + " -g " + gmiFile2 + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f "
pythonCommand2= "PlotField_ZonalMean_GMI.py -c " + gmiFile1 \
    + " -g " + gmiFile2 + " -r " + str(timeRecord) + " -d " + dateYearMonth + " -f"




print("")
print("Package type is: ", packageType)
if packageType == "Q": 
    fieldsToCompare = GmiDef.GMI_QUICK_FIELDS
elif packageType == "S":
    fieldsToCompare = GmiDef.GMI_STANDARD_FIELDS
else:
    print("all")
print("")


print("")



editedFields = []
print("")
for field in fieldsToCompare:
    if field not in GmiDef.GMI_IGNORE_FIELDS[:]:
        editedFields.append(field)
        
print("")

print("")
print(editedFields[:])
print("")


fieldsToCompare = None
fieldsToCompare = editedFields


procCount = 0
nodeCount = 0


for field in fieldsToCompare[:]:
    
    field = fieldsToCompare[fieldCount]



    sysCommand = " python " + cwd + "/" + \
        pythonCommand1 + " " + field + " -v " + variableExtractField
    
    commands.append(sysCommand)
    procCount = procCount + 1


    print("")
    print("Deciding if zonal mean is possible for : ", field)
    print("")

    if field in GmiDef.GMI_TWOD_FIELDS[:]:
        
        print("")
        print("2D field found. NO zonal mean!")
        print("")
        
    else:

        sysCommand = "python " + cwd + "/" + \
            pythonCommand2 + " " + field + " -v " + variableExtractField

        commands.append(sysCommand)
        procCount = procCount + 1
    


    fieldCount = fieldCount + 1


    
print("")
for command in commands[:]:
    print(command)






print("")
print("len of commands: ", len(commands))
print("")


print("\nProcess jobs, please wait...")
jobs = list()
for cmd in range(len(commands)):
    p = multiprocessing.Process(target=subproc, args=(commands[cmd],))
    jobs.append(p)
    p.start()

for j in jobs:
    j.join()
