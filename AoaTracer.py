#!/usr/bin/python

#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Feb 18th 2020
#
# DESCRIPTION:
# This class represents a generic tracer and it's base information. 
#------------------------------------------------------------------------------

import re
import os
import sys
import random
import datetime
import calendar
import numpy
from numpy import *
from netCDF4 import Dataset


class AoaTracer(GenericTracer):

    
    tracerName = None
    tracerLongName = None
    tracerIntervalZM = None
    tracerIntervalSlices = None

    #---------------------------------------------------------------------------  
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    #---------------------------------------------------------------------------  
    def __init__(self, tracerName):

        GenericTracer.__init__(self, tracerName)

