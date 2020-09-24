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

import sys

class BasicTools:

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

    def returnBaseArray (self, array, lev):
        

        shapeArray = array.shape

        print ("\nIncoming array shape: ", shapeArray)


        # look for and collection
        # dimensions of size 1
        count = 0
        zeroDims = []
            
        for dimension in shapeArray:
            if dimension == 1:
                zeroDims.append(count)
            count += 1

        print ("Dimensions with size = 1: ", zeroDims[:])
        print ("Number of dimensions of size 1: ", len(zeroDims))


        for zeroDim in zeroDims:
            
            if len(shapeArray) == 3:
                returnArray = array[0,:,:]
                

            elif len(shapeArray) == 4:
                returnArray = array[0,:,:,:]

            else:
                print("\nERROR only 2 and 3D arrays are supported")
                sys.exit(-1)
                
            shapeArray = returnArray.shape
            array = None
            array= returnArray

        if len(shapeArray) == 3:
            returnArray = array[lev-1,:,:]
            array = None
            array = returnArray


        print ("Shape of return array: ", array.shape)


        return array
