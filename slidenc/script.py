# -*- coding: utf-8 -*-

from netCDF4 import Dataset as NF
import numpy as np
import reader as reader
import matplotlib.pyplot as plt
import numpy.ma as ma

# enable interactive plotting in pydev:
#get_ipython().enable_pylab()
model='him'
#model='roms'

if model=='him':
    fname='/home/nfs/z3439823/backup/ncfiles/save1.00e00.376.195.nc'
elif model=='roms':
    #fname='/home/nfs/z3439823/backup/ncfiles/roms_avg_8.nc'
    fname='/home/nfs/z3439823/models/roms/ocean_his.nc'

ds=NF(fname)
rr=reader.myreader(fname)
rr.set_var('u')

sl=slice(None)
fix1=slice(64,65,None)
fix2=slice(25,26,None)
#fix2=slice(45,46,None)
#tup=(fix1, -800, sl, sl )
tup=(fix1, sl,fix2,  sl)
#tup=(fix1, sl, sl, fix2)
#tup=(sl,sl,slice(48,49,None), slice(68,69,None))

if 1:
    rr.set_trafo(model)
    rr.set_zcoord_active('added')

va=rr.get_var(tup)
va=np.squeeze(va)

rr.cellgrid=True
y,x=rr.get_physgrid(tup)

if 1:
    mva = ma.masked_array(va,mask=np.isnan(va))
    #plt.pcolormesh(x,y,mva,edgecolors='k')
    plt.pcolormesh(x,y,mva)
    #plt.pcolormesh(va)
    plt.autoscale(tight=True)
else:
    plt.imshow(va,interpolation='none')
plt.colorbar()
plt.show()

############################################
if 0:
    #print rr.modelguess
    #print rr.varname
    #print rr.zcoord_trafo_available


    #print rr.zcoord_active
    sl=slice(None)
    fix1=slice(1,2,None)
    #fix2=slice(50,51,None) # strait
    #fix2=slice(0,1,None)

    fix2=slice(1,2,None)
    #tup=(fix1, fix2, sl, sl )
    #tup=(fix1, -10, sl, sl )
    tup=(fix1, sl,fix2,  sl)



    rr.set_trafo_him()
    #print rr.zcoord_trafo_available
    rr.set_zcoord_active('added')
    u=rr.get_var(tup)
    u=np.squeeze(u)
    #rr._get_envelope_tup(tup,ifixeddims,stag)

    rr.cellgrid=False
    y,x=rr.get_physgrid(tup)
    print u.shape

    rr.get_physgrid2(tup)
    #print x.shape
    #print y.shape

    #plt.contourf(x,y,u)
    #plt.contourf(u)
    # plt.pcolor(x,y,u)
    #plt.colorbar()
    #plt.show()



#print '*** end ***'

