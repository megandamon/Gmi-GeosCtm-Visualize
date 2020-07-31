#!/usr/bin/env python
from __future__ import print_function

# -------------
# Load modules
# -------------
import os
import sys

import numpy as np

# Determine the location (absolute path) of this script
curDir = os.path.dirname(os.path.abspath(__file__))
modDir = curDir + '/../io'
sys.path.append(modDir)

modDir = curDir + '/../utils'
sys.path.append(modDir)


def calcPressureLevels(nlevs):
    """
      This function takes the number of vertical levels
      to read a file that contains the values of ak and bk.
      It then computes the pressure levels using the formula:

          0.5*(ak[l]+ak[l+1]) + 0.1*1.0e5*(bk[l]+bk[l+1])

      Input Varialble:
        nlevs: number of vertical levels

      Returned Value:
        phPa: pressure levels from bottom to top
    """
    ak = np.zeros(nlevs + 1)
    bk = np.zeros(nlevs + 1)
    phPa = np.zeros(nlevs)

    fileName = str(nlevs) + '-layer.p'

    fid = open(curDir + '/' + fileName, 'r')
    lnum = 0
    k = 0
    for line in fid:
        lnum += 1
        if (lnum > 2):
            line = line.strip()
            columns = line.split()
            ak[k] = float(columns[1])
            bk[k] = float(columns[2])
            k += 1
    fid.close()

    for k in range(nlevs):
        phPa[k] = 0.50 * ((ak[k] + ak[k + 1]) + 0.01 * 1.00e+05 * (bk[k] + bk[k + 1]))

    print('Pressure range: ', np.max(phPa), np.min(phPa))
    return phPa[::-1]


if __name__ == "__main__":
    nlevs = 72
    phPa = calcPressureLevels(nlevs)
    print(phPa[0])
    print(phPa[-1])
