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
