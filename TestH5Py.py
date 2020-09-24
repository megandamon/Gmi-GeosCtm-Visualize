import h5py
import numpy as np

print ("Hello from TestH5Py.py")

fileName1 = "/discover/nobackup/projects/gmao/geos_cf/priv/GEOS-CF_NRT/ana//Y2020/M08/D27/GEOS-CF.v01.rpl.met_tavg_1hr_g1440x721_v36.20200827_0030z.nc4"







numFiles = 24
count = 0

hdfFileObject = h5py.File (fileName1, 'r')
uField = hdfFileObject['U']
uShape = uField.shape
uAverage = np.zeros(uShape, np.float32)
uAverage = uAverage + uField

while count < 24:

    print ("\ncount: ", count)
    count+=1
    
    
    hdfFileObject.close()
    
    currentFileName = fileName1

    print ("\nopening: ", currentFileName)
    hdfFileObject = h5py.File (currentFileName, 'r')
    uField = hdfFileObject['U']
    print ("\nCreating average")
    
    uAverage = uAverage + uField


print ("\nLeft loop, count is: ", count)

uAverage = uAverage / float(count)
