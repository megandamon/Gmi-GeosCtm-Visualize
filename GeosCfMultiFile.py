# ------------------------------------------------------------------------------
# NASA/GSFC
# ------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Oct 30 2020
#
# DESCRIPTION:
# This class is for GEOS CF Multi file operations. 
# ------------------------------------------------------------------------------

import re
from MultiHdfFile_Class import MultiHdfFile_Class


class GeosCfMultiFile(MultiHdfFile_Class):

    # ---------------------------------------------------------------------------
    # AUTHORS: Megan Damon NASA GSFC
    #
    # DESCRIPTION:
    # Constructor routine.
    # ---------------------------------------------------------------------------

    def __init__(self, startDateString, endDateString, pathBaseIn, collectionName, \
                 dateTimeStep, archiveStyle):

        print("\nInitializing GeosCfMultiFile object")

        if archiveStyle != "GeosCf_archive":
            print ("\nERROR: ", archiveStyle, \
                   " not supported for GeosCfMultiFile Class!")

        MultiHdfFile_Class.__init__(self, startDateString, endDateString, \
                                    pathBaseIn, collectionName, \
                                    dateTimeStep, archiveStyle)


    def setCurrentTimeComponents(self, currentDateObject):

        MultiHdfFile_Class.setCurrentTimeComponents(self, currentDateObject)

        print ("In GeosCfMultiFile")


        self.currentDatePath = self.basePath + "/Y" + self.currentYear + \
            "/M" + self.currentMonth + "/D" + self.currentDay

        self.currentFile = self.currentDatePath + "/*." + self.collectionName + \
            "*." + self.currentYear + self.currentMonth + \
            self.currentDay + "_" + self.currentHour + self.currentMinute + "z.nc4"

        self.currentDateObject = currentDateObject



    def createFileNamePressLevs (self, pressureLevels, newPath=None):

        numPressureLevels = len(pressureLevels)
        
        splitTokens = self.currentFile.split("_")


        # Look for token with "*.currenteDate"
        format = "%Y%m%d"
        dateFormat = self.currentDateObject.strftime(format)

        newTokens = []
        for token in splitTokens:
            if "." in token and dateFormat in token:
                newToken = "p" + str(numPressureLevels) + "." + dateFormat
                newTokens.append(newToken)
            else:
                newTokens.append(token)

      
        newFileName = ""
        count = 0
        for token in newTokens:
            if count == 0:
                newFileName = token
            else:
                newFileName = newFileName + "_" + token
            count+=1



        print (newFileName)

        if newPath != None:
            print ("\Creating new path as provided by user")
            splitTokens = newFileName.split("ana")
            newFileName = newPath + splitTokens[1]

         
        self.interpFile = newFileName
        
        return (newFileName)
