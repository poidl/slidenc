# -*- coding: utf-8 -*-

from netCDF4 import Dataset as NF
import numpy as np
import reader as reader

fname='/home/nfs/z3439823/backup/ncfiles/save1.00e00.376.195.nc'
ds=NF(fname)

print dir(ds)
print dir(ds.dimensions['lath'])

r=reader.ncreader(fname)

print r.ncfname
print r.ncf
print r.dims()
print r.vars()
print r.dimlims()
print r.vardims('u')
print r.varshape_phys('u')

rr=reader.myreader(fname)
rr.set_var('u')
#rr.set_zcoord_active('added')
rr.
#print rr.dims
#print rr.shape_phys
