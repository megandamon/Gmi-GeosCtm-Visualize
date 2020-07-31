# ------------------------------------------------------------------------------
# NASA/GSFC
# ------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         Feb 18th 2020
#
# DESCRIPTION:
# This class represents a generic tracer and it's base information. 
# ------------------------------------------------------------------------------
from GenericTracer import GenericTracer


class AoaBlTracer(GenericTracer):
    tracerName = None
    tracerLongName = None
    tracerIntervalZM = None
    tracerIntervalSlices = None

    # ---------------------------------------------------------------------------
    # AUTHORS: Megan Damon NASA GSFC 
    #
    # DESCRIPTION: 
    # Constructor routine.
    # ---------------------------------------------------------------------------
    def __init__(self, tracerName, modelObject, keyFile, yAxisType, timeRecord, fileLevel):
        GenericTracer.__init__(self, tracerName, modelObject, keyFile, timeRecord, fileLevel)
        self.yAxisType = yAxisType
