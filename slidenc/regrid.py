#################################################################
# slidenc is a data visualization tool
# Copyright (C) 2011-2014  Stefan Riha

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#################################################################

import numpy as np

class regrid:

    def envelope(x, axis=-1):
    """
    Regrid to envelope.

    Parameters
    ----------
    x: array of arbitrary dimension
    axis: axis along which to regrid
    """

    shape = list(x.shape)
    shape[axis] = shape[axis] + 1
    xn = np.nan * np.ones(shape)

    dx = np.diff(x, 1, axis=axis)

    s = [slice(None)]
    t = s * x.ndim
    t1 = t.copy()
    t2l = t.copy()
    t2r = t.copy()
    t3 = t.copy()
    t1[axis] = slice(0, 1)
    t2l[axis] = slice(1, -1, None)
    t2r[axis] = slice(None, -1, None)
    t3[axis] = slice(-1, None)

    xn[t2l] = x[t2r] + 0.5 * dx

    xn[t1] = x[t1] - 0.5 * dx[t1]
    xn[t3] = x[t3] + 0.5 * dx[t3]

    return xn

    def reduce(self,var,envtup,guessed):
        # example: if var.shape is (5,5,2) and l[2] is not slice(None)
        # then the third dimension is re-gridded to the center, output is of shape (5,5)
        # assumes that every index which is not a slice, is of dimension 2

        # `guessed` is nonzero if the indices to be reduced are from the origin or
        # end of a dimension, and the grid is staggered and extrapolated
        # (see _get_envelope_tup)
        l=list(envtup)
        ireduce=[ind for ind,item in enumerate(l) if not (item.start==None or ((item.start!=None and item.stop==item.start+1))) ]
#        [i for i in l if i.start==None or ((i.start!=None) and (i.stop>i.start+1))]
        inot_reduce=[ind for ind,item in enumerate(l) if item.start!=None and item.stop==item.start+1]
        guessed=[guessed[i] for i in ireduce]

        for i in ireduce:
            l[i]=slice(0,2,None) #
        for i in inot_reduce:
            l[i]=slice(0,1,None) #

        for i,g in zip(ireduce,guessed):

            l1=l[:]
            l2=l[:]

            l1[i]=slice(0,1,None)
            l2[i]=slice(1,2,None)

            tup1=tuple(l1)
            tup2=tuple(l2)
            if g==0:
                var=0.5*(var[tup1]+var[tup2])
            elif g==1: # extrapolation at origin
                var=var[tup1]-0.5*(var[tup2]-var[tup1])
                print 'extrap. at origin'
            elif g==2: # extrapolation at end
                print 'extrap. at end'
                var=var[tup2]+0.5*(var[tup2]-var[tup1])

            l[i]=slice(0,1,None)

        return var


    def reduce_test(self):
        va=np.ones([5,2,5,2])
        l=[slice(None),slice(3,5,None),slice(None),slice(3,5,None)]
        guessed=[0,0,0,0]
        out=self.reduce(va,l,guessed)
        print out.shape


    def d1_point_to_cellvertices(self,var):
        if var.ndim!=1:
            raise Exception('input must be a vector')
        dif=0.5*np.diff(var,1,0)
        v=var[0:-1]+dif
        v=v[np.r_[0,range(0,len(v)),0]]
        v[0]=var[0]-dif[0]
        v[-1]=var[-1]+dif[-1]
        return v

    def on_points_multidim(self,var,stag):
        # like on_points but the input field is multi-dimensional
        # example from HIM: The objective is to get horizontal slice of u (i.e. constant z).
        # This requires as a first step to read interface heights 'e', interpolating e on the same
        # *horizontal* (but not vertical) grid as u. This function interpolates.
        # In this example, 'stag' must be zero for the vertical axis.
        def rgrd(var,stag):

            shp0=var.shape[0]
            dif=0.5*np.diff(var,1,0)
            if stag==1: # linear interpolation, then extrapolate last grid point
                var[0:-1,...]=var[0:-1,...]+dif
                var[-1,...]=var[-1,...]+dif[-1]
            if stag==2: # lin. int.
                var=var[0:-1,...]+dif
            if stag==-1: # lin. int., then extrapolate first grid point
                var[1:,...]=var[0:-1,...]+dif
                var[0,...]=var[0,...]-dif[0]
            if stag==-2: # lin. int, then extrapolate first and last grid point
                vi=var[0:-1,...]+dif
                var=var[np.r_[0,range(0,shp0)]]
                var[-1,...]=var[-1,...]+dif[-1]
                var[0,...]=var[0,...]-dif[0]
                var[1:-1,...]=vi

            return var

        for ii in range(len(stag)):

            if stag[ii]!=0:
                var=np.rollaxis(var,ii,0)
                var=rgrd(var,stag[ii])
                var=np.rollaxis(var,0,ii+1)

        return var



    def on_points(self,var,stag1,stag2):
        # remove this function
        raise Exception('replace by function on_points_multidim?')
        def rgrd(var,stag):

            xn,yn=var.shape
            dif=0.5*np.diff(var,1,0)
            if stag==1: # linear interpolation, then extrapolate last grid point
                var[0:-1,:]=var[0:-1,:]+dif
                var[-1,:]=var[-1,:]+dif[-1]
            if stag==2: # lin. int.
                var=var[0:-1,:]+dif
            if stag==-1: # lin. int., then extrapolate first grid point
                var[1:,:]=var[0:-1,:]+dif
                var[0,:]=var[0,:]-dif[0]
            if stag==-2: # lin. int, then extrapolate first and last grid point
                vi=var[0:-1,:]+dif
                var=var[np.r_[0,range(0,xn)]]
                var[-1,:]=var[-1,:]+dif[-1]
                var[0,:]=var[0,:]-dif[0]
                var[1:-1,:]=vi

            return var

        if stag1!=0:
            var=rgrd(var,stag1)

        if stag2 != 0:
            var=var.transpose()
            var=rgrd(var,stag2)
            var=var.transpose()

        return var


    def on_cellvertices(self,var,stag1,stag2):
        # var must be 2d
        # whereas on_points outputs a field which is defined on the same grid
        # as the plotted variable (stag=0), this function will produce stag=2,
        # i.e. the output points lie between the points of the plotted variable
        # (or, viewed in two dimensions, on the cell vertices)

        def rgrd(var,stag):
            #raise Exception('this does not make sense if regridding a coordinate in direction of itself')
            xn,yn=var.shape
            if stag==1: # at end, increase dimension by one and extrapolate
                var=var[np.r_[range(0,xn),xn-1]]
                var[-1,:]=var[-2,:]+(var[-2,:]-var[-3,:])
            if stag==-1: # at start, increase dimension by one and extrapolate
                var=var[np.r_[0,range(0,xn)]]
                var[0,:]=var[1,:]-(var[2,:]-var[1,:])
            if stag==0: # interpolate to mid-points, increase and extrapolate
                dif=0.5*np.diff(var,1,0)
                v1=var[0,:]-dif[0]
                v2=var[-1,:]+dif[-1]
                var[:-1,:]=var[:-1,:]+dif # keep last
                var=var[np.r_[0,range(0,xn)]] # append at start
                var[0,:]=v1
                var[-1,:]=v2
            if stag==-2: # increase and extrapolate
                v1=var[1,:]-var[0,:]
                v2=var[-1,:]-var[-2,:]
                var=var[np.r_[0,range(0,xn),xn-1]]
                var[0,:]=v1
                var[-1,:]=v2

            return var

        if stag1!=2:
            var=rgrd(var,stag1)

        if stag2 != 2:
            var=var.transpose()
            var=rgrd(var,stag2)
            var=var.transpose()

        return var

#     def d2(self,var,stag1,stag2):
#
#         def rgrd(var,stag):
#             #raise Exception('this does not make sense if regridding a coordinate in direction of itself')
#             xn,yn=var.shape
#             if stag==1: # linear interpolation, then append last grid point unmodified
#                 var[0:-1,:]=var[0:-1,:]+0.5*np.diff(var,1,0)
#             if stag==2: # lin. int.
#                 var=var[0:-1,:]+0.5*np.diff(var,1,0)
#             if stag==-1: # lin. int., then append first grid point unmodified
#                 var[1:,:]=var[0:-1,:]+0.5*np.diff(var,1,0)
#             if stag==-2: # lin. int, then append first and last grid point unmodified
#                 vi=var[0:-1,:]+0.5*np.diff(var,1,0)
#                 var=var[np.r_[0,range(0,xn),:]]
#                 var[1:-1,:]=vi
#             return var
#
#         if stag1!=0:
#             var=rgrd(var,stag1)
#
#         if stag2 != 0:
#             var=var.transpose()
#             var=rgrd(var,stag2)
#             var=var.transpose()
#
#         return var


#        if stag2==-1: # leave first gridpoint untouched
#            var[:,1:]=var[:,0:-1]+0.5*np.diff(var,1,1)
#        if stag2==-2:
#            vi=var[:,0:-1]+0.5*np.diff(var,1,1)
#            var=var[:,np.r_[0,range(0,yn)]]
#            var[:,1:-1]=vi
