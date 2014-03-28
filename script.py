# -*- coding: utf-8 -*-

from netCDF4 import Dataset as NF
#import numpy as np
import reader as reader
import matplotlib.pyplot as plt

fname='/home/nfs/z3439823/backup/ncfiles/save1.00e00.376.195.nc'
#fname='/home/nfs/z3439823/backup/ncfiles/roms_avg_8.nc'
ds=NF(fname)

print dir(ds)
#print dir(ds.dimensions['lath'])

r=reader.ncreader(fname)

print r.ncfname

#print r.vars()
#print r.dimlims()
#print r.vardims('u')
#print r.varshape_phys('u')
#tup=(slice(None))
#print r.varread('lonh',tup)



rr=reader.myreader(fname)
rr.set_var('u')

#print rr.modelguess
#print rr.varname
#print rr.zcoord_trafo_available
rr.set_zcoord_active('added')
#print rr.zcoord_active
sl=slice(None)
fix1=slice(1,2,None)
fix2=slice(0,1,None)
tup=(fix1, sl, fix2, sl)

#rr.zcoord_added_framing=True
#stag=rr._get_staggervec('e','h')
#print stag
u=rr.get_var(tup)
#rr._get_envelope_tup(tup,ifixeddims,stag)
print u.shape
rr.cellgrid=True
rr.get_physgrid(tup)

#print x.shape
#print y.shape
#print v.shape


#print v.shape
#plt.plot(x[0,:])
#plt.contourf(y,x,v)
#plt.pcolor(y,x,v)
#plt.show()
#print np.shape(x)
#print np.shape(y)
#print x
#print y


#rr.set_zcoord_active('added')

#print rr.dims
#print rr.shape_phys
