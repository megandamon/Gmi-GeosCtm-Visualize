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

import re
import os
import sys
import random
import datetime
import calendar
import getopt
import numpy
from numpy import *

import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


import multiprocessing
from time import sleep
from multiprocessing import Pool

from netCDF4 import Dataset

import math

from matplotlib.colors import BoundaryNorm
import matplotlib.colors as colors
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.basemap import Basemap


sys.path.append('/discover/nobackup/ccruz/devel/CCM/GmiMetfieldProcessing')


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
