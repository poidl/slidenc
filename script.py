# -*- coding: utf-8 -*-

from netCDF4 import Dataset as NF
import numpy as np
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
fix2=slice(50,51,None) # strait
#fix2=slice(0,1,None)
tup=(fix1, sl, sl, fix2 )
#tup=(fix1, sl,fix2,  sl)

#rr.zcoord_added_framing=True
#stag=rr._get_staggervec('e','h')
#print stag
u=rr.get_var(tup)
u=np.squeeze(u)
#rr._get_envelope_tup(tup,ifixeddims,stag)

rr.cellgrid=True
y,x=rr.get_physgrid(tup)
print u.shape

print x.shape
print y.shape

# plt.contourf(x,y,u)
# plt.pcolor(x,y,u)
# plt.show()



print '*** end ***'

