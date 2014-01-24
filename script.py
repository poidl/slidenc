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

print r.vars()
print r.dimlims()
print r.vardims('u')
print r.varshape_phys('u')
#tup=(slice(None))
#print r.varread('lonh',tup)



rr=reader.myreader(fname)
rr.set_var('u')

print rr.modelguess
print rr.varname
print rr.zcoord_trafo_available
rr.set_zcoord_active('added')
print rr.zcoord_active
tup=( 1,slice(None), 1,slice(None))

#rr.get_slice(tup)
y,x=rr.get_physgrid(tup)
#print np.shape(x)
#print np.shape(y)
#print x
#print y


#rr.set_zcoord_active('added')

#print rr.dims
#print rr.shape_phys
