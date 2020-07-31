#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         June 5 2020
#
# DESCRIPTION:
# Class to hold basic tools.
#------------------------------------------------------------------------------

import os
import sys

import matplotlib
matplotlib.use('pdf')

if "GMIMetFieldProcessing" in os.environ:
    sys.path.append(os.environ.get("GMIMetFielProcessing"))
else:
    print("Please specify location of GMIMetFieldProcessing scripts")
    sys.exit(1)


class BasicTools:

    def __init__(self):
        pass

    def readNodesIntoArray (self, nodeFile):

        nodesRead = []
        
        myFile = open (nodeFile, "r")
        
        count = 0
        line = myFile.readline().rstrip()
        while line != '':
            nodesRead.append(line)
            
            if count == 10000: break
            count = count + 1
            line = myFile.readline().rstrip()

        myFile.close()

        nodesToReturn = []
        for node in nodesRead:
            if node not in nodesToReturn: nodesToReturn.append(node)
      
        return nodesToReturn
