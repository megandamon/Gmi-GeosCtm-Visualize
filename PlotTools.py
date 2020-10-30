#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Feb 21 2020
#
# DESCRIPTION:
# Creating this call so zonal mean plotting and slice plotting can share the same
# tools. 
#------------------------------------------------------------------------------
import decimal
from decimal import Decimal
import matplotlib
matplotlib.use('pdf')
import math

import sys

import random



class PlotTools:


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Constructor routine.
   #---------------------------------------------------------------------------  
   def __init__(self):
                pass
                

   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Destructor routine.
   #---------------------------------------------------------------------------    
   def __del__(self):
      pass


   def reviseTickLabelsFromFormats (self, cbar, fmtDict):


      count = 0
      labels = [item.get_text() for item in cbar.ax.get_xticklabels()]


      for key in fmtDict:

         value = fmtDict[key]
         label = labels[count]
         strLabel = str(label)

         labels[count] = value
         count = count + 1
         
                
      cbar.ax.set_xticklabels(labels)


   def reviseTickLabels (self, cbar):

      # remove unecessary decimals
      count = 0
      labels = [item.get_text() for item in cbar.ax.get_xticklabels()]

      for label in labels:

         strLabel = str(label)

         if "." in strLabel:
            rhs = strLabel.split(".")[1]
            lhs = strLabel.split(".")[0]
            
            if "e" in rhs or "E" in rhs:

               if "e" in rhs:
                  splitSciNot = rhs.split("e")
               else:
                  splitSciNot = rhs.split("E")

               if int(splitSciNot[0]) == 0:
                  newSciNot = lhs + ".e" + splitSciNot[1]
                  labels[count] = newSciNot

            elif int (rhs) == 0:
               labels[count] = strLabel.split(".")[0]
        
         count = count + 1

      cbar.ax.set_xticklabels(labels)

      # remove trailing zeros
      count = 0
      labels = [item.get_text() for item in cbar.ax.get_xticklabels()]
      for label in labels:
         strLabel = str(label)
         
         if "e" not in strLabel and "E" not in strLabel:
            if "." in strLabel:
               stripStrLabel = strLabel.rstrip('0')
               labels[count] = stripStrLabel
         
         count = count + 1
      
      cbar.ax.set_xticklabels(labels)

      labels = [item.get_text() for item in cbar.ax.get_xticklabels()]
      if float(labels[0]) == float(0):
         labels[0] = "0"


      cbar.ax.set_xticklabels(labels)
              
         
      
   def setVisibleClevTicks (self, clevs, clevTicks):

      if len(clevs) < 15:
         return clevs
      else:

         lhsIndex = 0
         rhsIndex = 1
         lhs = clevs[lhsIndex]
         rhs = clevs[rhsIndex]
         interval = round(rhs - lhs)

         clevTicks[lhsIndex].set_visible(True)
         clevTicks[rhsIndex].set_visible(True)   

         lhsIndex = lhsIndex + 1
         rhsIndex = rhsIndex + 1
      

         numFalse = 0
         count = 2
         for tick in clevTicks[3::]:

            lhsIndex = lhsIndex + 1
            rhsIndex = rhsIndex + 1

            lhs = clevs[lhsIndex]
            rhs = clevs[rhsIndex]
            interval2 = round(rhs - lhs)
            
#            print ('\n ', lhs, '-', rhs, interval2, " =?", interval)

            if interval == interval2:
#               print ("Found equal ", clevs[rhsIndex], " to False")
               clevTicks[rhsIndex].set_visible(False)
               numFalse = numFalse + 1
               if numFalse == 4: # prevent too many blank marks
                  clevTicks[rhsIndex].set_visible(True)
                  numFalse = 0

                  
            else:
#               print ("Found diff ", clevs[rhsIndex], " to True")
               clevTicks[rhsIndex].set_visible(True)
               clevTicks[lhsIndex].set_visible(True)


            interval = interval2
            count = count + 1

         clevTicks[-1].set_visible(True)



   def formatNumber (self, num):
      try:
         dec = decimal.Decimal(num)
      except:
         return 'bad'
      tup = dec.as_tuple()
      delta = len(tup.digits) + tup.exponent
      digits = ''.join(str(d) for d in tup.digits)
      if delta <= 0:
         zeros = abs(tup.exponent) - len(tup.digits)
         val = '0.' + ('0'*zeros) + digits
      else:
         val = digits[:delta] + ('0'*tup.exponent) + '.' + digits[delta:]
      val = val.rstrip('0')
      if val[-1] == '.':
         val = val[:-1]
      if tup.sign:
         return '-' + val
      return val


   #---------------------------------------------------------------------------  
   # AUTHORS: Megan Damon NASA GSFC 
   #
   # DESCRIPTION: 
   # Remove unnecessary decimals
   #---------------------------------------------------------------------------    
   def returnFormattedContours (self, clevs):

      newClevs = []
      for lev in clevs: 

         strLev = str(lev)

         if "." in strLev:
            rhs = strLev.split(".")[1]


            
            if "e" in rhs or "E" in rhs: 
               newLev = lev
               newClevs.append(lev)

            elif int(rhs) == 0:
               newLev = int(float(strLev))
               newClevs.append(newLev)


            else:
               newLev = lev
               newClevs.append(lev)



         else:
            newLev = lev
            newClevs.append(lev)


      return newClevs

   def returnXTickFontSizeFromSubPlotNum (self, subplotNum):
      if subplotNum == 111:           # single image on a page
         xtickFontSize = 'xx-large'
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         xtickFontSize = 'large'
      else:                           # 4-panel plot
         xtickFontSize = 'large'

      return xtickFontSize


   def returnYTickFontSizeFromSubPlotNum (self, subplotNum):
      if subplotNum == 111:           # single image on a page
         yTickFontSize = 'xx-large'
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         yTickFontSize = 'large'
      else:                           # 4-panel plot
         yTickFontSize = 'large'

      return yTickFontSize



   def returncBarFontSizeFromSubPlotNum (self, subplotNum):

      if subplotNum == 111:           # single image on a page
         cBarFontSize = 16
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         cBarFontSize = 14
      else:                           # 4-panel plot
         cBarFontSize = 14

      return cBarFontSize

   def returncTickSizeFromSubPlotNum (self, subplotNum):

      if subplotNum == 111:           # single image on a page
         cTickFontSize = 14
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         cTickFontSize = 12
      else:                           # 4-panel plot
         cTickFontSize = 12

      return cTickFontSize


   def returnOrientationFromSubPlotNum (self, subplotNum):

      if subplotNum == 111:           # single image on a page
         orientation = 'horizontal'
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         orientation = 'vertical'
      else:                           # 4-panel plot
         orientation = 'horizontal'

      return orientation

   def returnPadFromSubPlotNum (self, subplotNum):
      if subplotNum == 111:           # single image on a page
         pad = .05
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         pad = .05
      else:                           # 4-panel plot
         pad = .05

      return pad


   def returnFractionFromSubPlotNum (self, subplotNum):
      if subplotNum == 111:           # single image on a page
         fraction = .4
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         fraction = .4
      else:                           # 4-panel plot
         fraction = .4

      return fraction


   def returnFontSizeFromSubPlotNum (self, subplotNum):
      if subplotNum == 111:           # single image on a page
         fontSize = 'xx-large'
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         fontSize = 'large'
      else:                           # 4-panel plot
         fontSize = 'large'

      return fontSize


   def returnTitleFontSizeFromSubPlotNum (self, subplotNum):
      if subplotNum == 111:           # single image on a page
         titleFontSize = 20
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         titleFontSize = 16
      else:                           # 4-panel plot
         titleFontSize = 18

      return titleFontSize


   def returnLatLonFontSizeFromSubPlotNum (self, subplotNum):
      if subplotNum == 111:           # single image on a page
         latLonFontSize = 20
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         latLonFontSize = 16
      else:                           # 4-panel plot
         latLonFontSize = 16

      return latLonFontSize

   def returnContourLabelFromSubPlotNum (self, subplotNum):



      if subplotNum == 111:           # single image on a page
         cLabelSize = 14
      elif str(subplotNum)[0] == "3": # 3-panel vertical plot
         cLabelSize = 10
      else:                           # 4-panel plot
         cLabelSize = 10

      return cLabelSize

   def returnClevsForPlotting (self, clevs):
      


      newClevs = []
      for lev in clevs:
         clevsString = str(lev)

         if "e" in clevsString:
            #print ("Digits are in scientific notation")
            newClevs.append(lev)

         else:

            if "." not in clevsString:
               newClevs.append(int(lev))
            else:
               digits = clevsString.split('.')[1] # just get RHS of number

               if int(digits) == 0:
                  #            print ("The level: ", lev, " has no RHS!", int(lev))
                  newClevs.append(int(lev))
               else:
                  newClevs.append(lev)

      return newClevs

   def returnContourLabelDictFromLevels (self, levels):

      fmtDict = {}

      for lev in levels:

         if isinstance(lev, int):
            fmtDict [lev] = str(lev)

         elif isinstance(lev, float):

            
            # determine order
            # if conditions are met, will
            # change to sci notation
            oLev = math.floor(math.log10(abs(lev)))
            
            if oLev < -2 or oLev > 4:
               
               print ("\nChange level ", lev, " to sci notation")

               tempVar = "{:e}".format(lev)
               splitString = tempVar.split("e")
               numString = splitString[0].strip("0")
               expString = splitString[1].strip("0")
               expString2 = str(int(expString))
               
               newLev = numString + "e" + expString2
               
               fmtDict [lev] = newLev
            else:
               fmtDict [lev] = str(lev)

                      
         else:
            print ("\nERROR: label: ", lev, " is of unsupported type!")

      return fmtDict


   def returnContourFormatFromLevels (self, levels):

      digitsList = []
      numSciFormat = 0

      #print (levels)


      for lev in levels: # check each contour level

         clevsString = str(lev)

         if "e" in clevsString or "E" in clevsString: # sci notation

            numSciFormat = numSciFormat + 1

            print ("found e number")

            if "e" in clevsString or "E" in clevsString:

               splitClevString = clevsString.split('e')

               if len(splitClevString) == 1:
                      splitClevString = clevsString.split('E')
                      
               #print (splitClevString, len(splitClevString))                      
               
               pres = abs(int(splitClevString[1]))

               #print ('pres: ', pres)


               number = decimal.Decimal(lev)
               clevsString = str(round(number,pres+2))

               #print (clevsString)


               digits1 = clevsString.split('.')[1] # just get RHS of number
               
               #print (digits1)



               if "E" in str(digits1): 
                  digits = digits1.split('E')[0]   
                  digitsList.append(len(digits))

               elif "e" in str(digits1): 
                  digits = digits1.split('e')[0]   
                  digitsList.append(len(digits))
               
               else:
                  digitsList.append(len(digits1))

      
         elif "." not in clevsString: # not floating point 
            digitsList.append(0)
         else:
            digitsList.append(len(clevsString.split('.')[1])) # just get RHS of number

      digitsList.sort()

#       print ("numscieformat: ", numSciFormat)
#       print ("digitsList: ", digitsList)

      numType = "f"
      if numSciFormat > 1: numType = "e"

      if digitsList[-1] == 0: 
         contourFormat = "%d"
      elif digitsList[-1] <= 3:
         contourFormat = "%1." + str(digitsList[-1]) + numType
      else:
         contourFormat = "%1.1e"

      print ("contourFormat: ", contourFormat)

      
      return contourFormat
