# ################################################################
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

from netCDF4 import Dataset as NF
import numpy as np
import regrid as regrid


class ncreader:
    def __init__(self, string):
        self.ncfname = string
        self.ncf = NF(str(string), 'r')

    def dims(self):
        return self.ncf.dimensions.keys()

    def vars(self):
        return self.ncf.variables.keys()

    def dimlims(self):
        return [len(self.ncf.dimensions.values()[i]) \
                for i in range(len(self.ncf.dimensions.values()))]

    def vardims(self, varname):
        return self.ncf.variables[varname].dimensions

    def varshape(self, varname):
        return self.ncf.variables[varname].shape

    def ndims(self, varname):
        return self.ncf.variables[varname].ndims

    def varread(self, *args):
        varname = args[0]
        if len(args) == 1:
            return self.ncf.variables[varname][:]
        else:
            tup = args[1]
            return self.ncf.variables[varname][tup]


    def varshape_phys(self, varname):
        dims = self.vardims(varname)
        l = []
        for ii in dims:
            mi = self.varread(ii, (0))
            ma = self.varread(ii, (-1))
            l.append([mi, ma])
        return l


class myreader:
    def __init__(self, string):
        self.model=''
        self.ncr = ncreader(string)
        self.ncvars = self.ncr.vars()  # tuple
        self.zcoord_trafo_available = False
        self.zcoords_native = ''
        self.zcoord_native_var = ''  # native zcoord of the variable
        self.zcoord_active = ''
        self.zcoord_index = ''
        self.zcoord_added = ''
        self.cellgrid = False

    def set_var(self, string):
        self.varname = string
        if self.varname not in self.ncvars:
            print 'variable \'' + string + '\' not in netcdf file'
            return
        self._ncread_vardata()
        #self.__guess_trafo()
        #self.set_trafo_roms()

    def set_trafo(self,trafoname):
        if trafoname=='him':
            self.model = 'him'
            self.zcoords_native = ['Layer', 'Interface']
            self.zcoord_added = 'z'
            self.zcoord_direction='inverted' # k decreases with z
            self._set_trafo_default()

        elif trafoname=='roms':
            self.model = 'roms'
            self.zcoords_native = ['s_rho', 's_w']
            self.zcoord_added = 'z'
            self.zcoord_direction='normal' # k increases with z
            self._set_trafo_default()


    def set_zcoord_active(self, string):
        if self.zcoord_trafo_available is False:
            raise Exception('No coordinate transformation available.')
            return
        elif string not in ['native', 'added']:
            raise Exception('Argument must be \'native\' or \'added\'')
            return

        elif string == 'native':
            self.zcoord_active = 'native'
        elif string == 'added':
            self.zcoord_active = 'added'


    def get_var(self, tup):

        ifixeddims = [i for i, x in enumerate(tup) if x != slice(None)]

        if (self.zcoord_index in ifixeddims) and \
                        self.zcoord_active == 'added':
            # get data at constant added zcoord.

            # Interpolate zcoord onto variable grid
            z=self._get_z_on_v(tup)

            va=self._reduce_v_vert(z,tup)

        else:
            va = self.ncr.varread(self.varname, tup)

        return va

    #     def get_physcoord(self,name):
    #         if self.model=='him':

#    def trafo(self, dimname):
#        return self.trafodict[dimname]


    def get_physgrid(self, tup):

        isliceddims = [i for i, x in enumerate(tup) if x == slice(None)]
        #ifixeddims = [i for i, x in enumerate(tup) if x != slice(None)]
        #sliceddims = [self.ncdims[i] for i in isliceddims]

        regr = regrid.regrid()

        if self.zcoord_index != isliceddims[0]:
            x = self._get_physdimvec(self.varname,isliceddims[0])
            if self.cellgrid == True:
                x = regr.d1_point_to_cellvertices(x)

        if self.zcoord_index != isliceddims[1]:
            y = self._get_physdimvec(self.varname,isliceddims[1])
            if self.cellgrid == True:
                y = regr.d1_point_to_cellvertices(y)

        if (self.zcoord_index in isliceddims) and \
                        self.zcoord_active == 'added':

            z=self._get_z_cellgrid(tup)

            if self.zcoord_index == isliceddims[0]:
                x = z
                y, dummy = np.meshgrid(y, x[:, 0])
            elif self.zcoord_index == isliceddims[1]:
                y = z
                dummy, x = np.meshgrid(y[0, :], x)

        else:  # self.zcoord_index in isliceddims:
            y, x = np.meshgrid(y, x)

        return x, y

    def _get_z_on_v(self,tup):

        isliceddims = [i for i, x in enumerate(tup) if x == slice(None)]
        # tuple for extraction of zeta is similar to that of v, except that...
        # 1) ...vertical index k is running...
        vatup = list(tup)
        vatup[self.zcoord_index] = slice(None)
        # 2) ...the other (than k) fixed coordinate may be staggered
        # find the other fixed index
        ifixeddims_tmp = [i for i, x in enumerate(vatup) if x != slice(None)]

        # get envelope tuple and check if zeta must be extrapolated

        # determine staggering between zeta and v
        stag = self._get_z_staggering(self.varname)
        envtup, guessed = self._get_envelope_tup(vatup, ifixeddims_tmp, stag)
        # extract envelope tuple of zeta
        z = self._get_z(envtup)
        # reduce other (than k) fixed dimension to singleton
        regr = regrid.regrid()
        z = regr.reduce(z, envtup, guessed)

        # re-grid 3d zeta onto grid of v
        stag_tmp = stag
        for ii in ifixeddims_tmp:
            stag_tmp[ii] = 0  # do nothing for the (fixed) singleton dimension
        z = regr.on_points_multidim(z, stag_tmp)

        # z regridding fix: monotonicity of the vertical coordinate may have
        # been destroyed during extrapolation. restore here. example: HIM Gibraltar e onto u
        # save1.00e00.376.195.nc tuple ((slice(1,2,None), z=1000, :, : ))
        l=list(vatup)
        for ii in ifixeddims_tmp: # singular dimensions
            l[ii]=slice(0,1)

        for ii in isliceddims: # check only start and end of each sliceddim
            n=self.ncshape[ii]
            for slic in [slice(0,1),slice(n-1,n)]: # start and end
                ltmp=l[:]
                ltmp[ii]=slic
                tmptup=tuple(ltmp)
                ztmp=z[tmptup] # view, not copy!
                ha=np.diff(ztmp,1,self.zcoord_index)

                if self.zcoord_direction=='inverted': # e.g. HIM
                    ha=-ha

                ha[ha<0.]=0. # delete bad dz's
                cs=np.cumsum(ha,self.zcoord_index) # integrate
                ltmp[ii]=slice(0,1)
                ltmp2=ltmp[:]
                ltmp[self.zcoord_index]=slice(1,None)
                ltmp2[self.zcoord_index]=slice(0,1)

                if self.zcoord_direction=='inverted': # e.g. HIM
                    ztmp[tuple(ltmp)]=ztmp[tuple(ltmp2)]-cs
                else:
                    ztmp[tuple(ltmp)]=ztmp[tuple(ltmp2)]+cs

        return z

    def _reduce_v_vert(self,z,tup):
        # z must *already* be interpolated onto the grid of v

        #### linear interpolation in z-direction

        isliceddims = [i for i, x in enumerate(tup) if x == slice(None)]
        zlevel = tup[self.zcoord_index]

        if self.zcoord_direction=='normal':
            bl = z <= zlevel
        if self.zcoord_direction=='inverted': # 'bottom' and 'surf' below have the opposite meaning
            bl = z >= zlevel

        s = np.sum(bl, self.zcoord_index)
        s = np.squeeze(s)

        n1 = self.ncshape[isliceddims[0]]
        n2 = self.ncshape[isliceddims[1]]
        n3 = self.ncshape[self.zcoord_index]

        # if time is fixed:
        if (self.zcoord_index < isliceddims[0]) and (self.zcoord_index < isliceddims[1]):
            # python has row major order
            sr = s.ravel()
            inds1 = np.arange(n1*n2)+ (sr-1)*n1*n2
            inds2=inds1+n1*n2

        # if z and either lat or lon is fixed:
        if (self.zcoord_index > isliceddims[0]) and (self.zcoord_index < isliceddims[1]):

            sr = s.ravel()

            slowest=np.ones((n2,1),dtype='int64')*np.arange(n1)*(n2*n3) # indices are integers
            slowest=slowest.transpose()
            slow=n2*(sr-1)
            fast=np.ones((n1,1),dtype='int64')*np.arange(n2)

            inds1=slowest.flat+slow+fast.flat
            inds2=inds1+n2

        bottom= sr==0.
        surf = sr==n3
        inds1[bottom]=0 # dummy, correct later
        inds2[surf] = 1 # dummy, correct later

        vatup = list(tup)
        vatup[self.zcoord_index] = slice(None)

        va1 = self.ncr.ncf.variables[self.varname][vatup].flat[inds1]
        va2 = self.ncr.ncf.variables[self.varname][vatup].flat[inds2]
        z1 = z.flat[inds1]
        z2 = z.flat[inds2]
        dz = (zlevel - z2) / (z1 - z2)
        va = va2 + (va1 - va2) * dz
        lower_only = dz == 0  # in case dz is zero and upper point is nan
        va[lower_only] = va1[lower_only]

        # correct bottom and surface
        va[bottom]=np.nan
        va[surf] = self.ncr.ncf.variables[self.varname][vatup].flat[inds1[surf]]
        inan = z.flat[inds1] > zlevel
        va[np.logical_and(surf,inan)] = np.nan

        va = np.reshape(va, (n1, n2))
        return va


    def _set_trafo_default(self):
        self.zcoord_trafo_available = True
        self.zcoord_active = 'native'
        vdims = self.ncr.vardims(self.varname)
        zcoord = [i for i in self.zcoords_native if i in vdims]
        self.zcoord_native_var = zcoord[0]
        self.zcoord_index = self.ncdims.index(zcoord[0])


    def _ncread_vardata(self):
        self.ncdims = self.ncr.vardims(self.varname)
        self.ncshape = self.ncr.varshape(self.varname)


    def _get_envelope_tup(self, tup, ifixeddims, stag):

        # compute envelope tuple, or tuple which has to be extracted from variable A such that it can be
        # interpolated onto the grid of variable B (which is potentially staggered with respect to grid
        # of A).
        # example from HIM: we want the z coordinates of u(layer,lath,lonq)
        # for the slice u(:,:,5).
        # z is defined on z(interface,lath,lonh) and
        # needs be interpolated onto (layer,lath,lonq). the envelope tuple is
        # (:,:,4:5) and contains all data needed for interpolation

        def mod_slice(sl, m):
            # modify slice object sl: add elements of vector m=[delta_start,delta_stop]
            if m[0] != 0:  # modify start
                istart = sl.start + m[0]
                istop = sl.stop

            if m[1] != 0:  # modify stop
                istop = sl.stop + m[1]
                istart = sl.start

            istep = sl.step
            return slice(istart, istop, istep)

        l = list(tup)
        # `guessing` means extrapolation. Necessary at start- and end-point if grid of A is smaller than B
        # values: 1 if extrapolating at origin, 2 if extr. at end
        guessing = [0] * len(tup)

        for i in ifixeddims:
            if stag[i] == 1:
                if l[i].start < self.ncshape[i] - 1:
                    l[i] = mod_slice(l[i], [0, 1])
                else:  # for the last grid point, extrapolate linearly from interior
                    l[i] = mod_slice(l[i], [-1, 0])
                    guessing[i] = 2
            elif stag[i] == -1:
                if l[i].start > 0:
                    l[i] = mod_slice(l[i], [-1, 0])
                else:  # for the first grid point, extrapolate
                    l[i] = mod_slice(l[i], [0, 1])
                    guessing[i] = 1
            elif stag[i] == 2:
                l[i] = mod_slice(l[i], [0, 1])
            elif stag[i] == -2:
                if l[i].start > 0 and l[i].start < self.ncshape[i] - 1:
                    l[i] = mod_slice(l[i], [-1, 0])
                elif l[i].start == 0:  # first
                    l[i] = mod_slice(l[i], [0, 1])
                    guessing[i] = 1
                elif l[i].start == self.ncshape[i] - 1:  # last
                    l[i] = mod_slice(l[i], [-1, 0])
                    guessing[i] = 2

        tup = tuple(l)

        return tup, guessing


    def _get_staggerflag(self, vec1, vec2):
        # vec1 and vec2 are 1 dimensional arrays
        start = vec1[:2]
        end = vec1[-2:]
        v1 = np.concatenate([start, end])
        start = vec2[:2]
        end = vec2[-2:]
        v2 = np.concatenate([start, end])
        if v1[0] < v2[0] and v2[0] < v1[1]:
            if v2[-2] < v1[-1] and v1[-1] < v2[-1]:
                return 1
            elif v1[-2] < v2[-1] and v2[-1] < v1[-1]:
                return 2
            else:
                return 99
        elif v2[0] < v1[0] and v1[0] < v2[1]:
            if v1[-2] < v2[-1] and v2[-1] < v1[-1]:
                return -1
            elif v2[-2] < v1[-1] and v1[-1] < v2[-1]:
                return -2
            else:
                return 99
        else:
            return 99
        return



    def _get_staggervec(self, varname1, varname2):
        #0:--- 1:- - -  (-1): - - - (2):- - - (-2): - - -  (99): none of the above
        #  xxx    x x x      x x x       x x       x x x x
        ncdims1 = self.ncr.vardims(varname1)
        ncdims2 = self.ncr.vardims(varname2)
        staggered = self._staggered_bool(ncdims1, ncdims2)

        for i in range(len(staggered)):
            if staggered[i]:

                dimvec1 = self._get_physdimvec(varname1, i)
                dimvec2 = self._get_physdimvec(varname2, i)
                staggered[i] = self._get_staggerflag(dimvec1, dimvec2)
            else:

                staggered[i] = 0

        return staggered


#########################################################################
# all functions below use self.model

    def _get_z(self, envtup):
        if self.model == 'him':
            z = self.ncr.varread('e', envtup)
        if self.model == 'roms':
            # scalars
            vtrans = self.ncr.varread('Vtransform')
            hc = self.ncr.varread('hc')
            # 1d vertical

            s_ = self.ncr.varread(self.zcoord_native_var)
            if self.zcoord_native_var == 's_rho':
                cs = 'Cs_r'
            if self.zcoord_native_var == 's_w':
                cs = 'Cs_w'
            Cs_ = self.ncr.varread(cs)
            # 2d horizontal
            h = self.ncr.varread('h', envtup[2:])

            # in case the Cs_ is not available in the nc file
            #             vstretch=self.ncr.varread('Vstretching')
            #             theta_s=self.ncr.varread('theta_s')
            #             theta_b=self.ncr.varread('theta_b')
            #
            #             if vstretch==4:
            #                 if theta_s>0:
            #                     C=(1-np.cosh(theta_s*s_))/(np.cosh(theta_s)-1)
            #                 else:
            #                     C=-s_**2
            #
            #                 if theta_b>0:
            #                     Cs_=(np.exp(theta_b*C)-1)/(1-np.exp(-theta_b))

            if vtrans == 2:
                #                 # S=((hc*s_)+h*Cs_)/(hc+h)
                #                 S=(hc*s_[:,None,None]+h[None,:,:]*Cs_[:,None,None])/ \
                #                     (hc+h[None,:,:])
                #                 zsurf=self.ncr.varread('zeta')
                #                 # z=zsurf+(zsurf+h)*S
                #                 z= zsurf[:,None,:,:]+(zsurf[:,None,:,:]+h[None,None,:,:])*S[None,:,:,:]

                # S=((hc*s_)+h*Cs_)/(hc+h)
                S = (hc * s_[:, None, None] + h[None, :, :] * Cs_[:, None, None]) / \
                    (hc + h[None, :, :])
                zsurf = self.ncr.varread('zeta', (envtup[0],) + envtup[2:])
                # z=zsurf+(zsurf+h)*S
                z = zsurf[:, None, :, :] + (zsurf[:, None, :, :] + h[None, None, :, :]) * S[None, :, :, :]

        return z


    def _get_z_staggering(self, varname):
        if self.model == 'him':
            return self._get_staggervec('e', varname)
        if self.model == 'roms':
            # s1 (time) is 0
            # s2 (s_rho or s_w) is 0, provided we extract the correct one in get_z
            horzdims = self.ncr.vardims(varname)[2:]
            hdims = self.ncr.vardims('h')
            staggered = self._staggered_bool(hdims, horzdims)
            if staggered[0]:
                dimvec1 = self._get_physdimvec('h', 0)
                # TODO: don't hardcode second argument to get_dimvec. Works only when variable has same same axes than vertical var
                dimvec2 = self._get_physdimvec(varname, 2)
                s2 = self._get_staggerflag(dimvec1, dimvec2)
            else:
                s2 = 0

            if staggered[1]:
                dimvec1 = self._get_physdimvec('h', 1)
                # TODO: don't hardcode second argument to get_dimvec. Works only when variable has same same axes than vertical var
                dimvec2 = self._get_physdimvec(varname, 3)
                s3 = self._get_staggerflag(dimvec1, dimvec2)
            else:
                s3 = 0
                #stag=self._get_staggervec('zeta',vd[2])
                #s2=self._get_staggervec('zeta',vd[2])
                #s3=self._get_staggervec('xi_rho',vd[3])
            return [0, 0, s2, s3]


    def _get_physdimvec(self, varname, idim):
        # vector of physical dimension idim
        dim = self.ncr.vardims(varname)[idim]

        if self.model == 'him':
            dimvec = self.ncr.ncf.variables[dim]
        if self.model == 'roms':
            if dim == 'ocean_time':
                dimvec = self.ncr.varread('ocean_time')
            if dim == 's_rho' or dim == 's_w':
                dimvec = self.ncr.varread(dim)
            if dim == 'xi_rho' or dim == 'xi_v':
                dimvec = self.ncr.varread('x_rho')[0]
            if dim == 'eta_rho' or dim == 'eta_u':
                dimvec = self.ncr.varread('y_rho')[:, 0]
            if dim == 'xi_psi' or dim == 'xi_u':
                dimvec = self.ncr.varread('x_psi')[0]
            if dim == 'eta_psi' or dim == 'eta_v':
                dimvec = self.ncr.varread('y_psi')[:, 0]

        if self.model == '':
            vl=self.ncr.vars()
            if dim in vl:
                dimvec = self.ncr.ncf.variables[dim]
                if len(dimvec.shape) != 1:
                    raise Exception('physical dimension has more than one dimension')
            else:
                # return grid dimensions
                d=self.ncr.dimlims()
                dimvec=np.arange(d[idim])

        return dimvec


    def _staggered_bool(self, ncdims1, ncdims2):
        if self.model == 'him':
            return [i != j for i, j in zip(ncdims1, ncdims2)]
        if self.model == 'roms':
            def roms_unique_dims(ncdims):
                for ii in range(len(ncdims)):
                    ncdims = list(ncdims)
                    dim = ncdims[ii]
                    if dim == 'xi_v':
                        ncdims[ii] = 'xi_rho'
                    elif dim == 'eta_u':
                        ncdims[ii] = 'eta_rho'
                    elif dim == 'xi_u':
                        ncdims[ii] = 'xi_psi'
                    elif dim == 'eta_v':
                        ncdims[ii] = 'eta_psi'
                return ncdims

            ncdims1 = roms_unique_dims(ncdims1)
            ncdims2 = roms_unique_dims(ncdims2)

            return [i != j for i, j in zip(ncdims1, ncdims2)]
        #             if dim=='xi_rho' or dim=='xi_v':
        #                 dimvec=self.ncr.varread('x_rho')[:,0]
        #             if dim=='eta_rho' or dim=='eta_u':
        #                 dimvec=self.ncr.varread('y_rho')[0]
        #             if dim=='xi_psi' or dim=='xi_u':
        #                 dimvec=self.ncr.varread('x_psi')[0]
        #             if dim=='eta_psi' or dim=='eta_v' :
        #                 dimvec=self.ncr.varread('y_psi')[0]


    def _get_z_cellgrid(self,tup):

        isliceddims = [i for i, x in enumerate(tup) if x == slice(None)]
        ifixeddims = [i for i, x in enumerate(tup) if x != slice(None)]
        stag = self._get_z_staggering(self.varname)

        ###################################################
        # regrid onto fixed indices

        envtup, guessed = self._get_envelope_tup(tup, ifixeddims, stag)

        if self.cellgrid:
           # Whether or not regridding has to be done in the vertical
           # for cellgrid plots depends on the vertical coorinate.
           # *) For him, the interface height is the cell boundary.
           # *) In ROMS, get z on w points
           if self.model=='roms':
               if self.zcoord_native_var=='s_rho':
                   ztmp='s_rho'
                   self.zcoord_native_var='s_w' # change temporarily
                   stag[self.zcoord_index]=2 # adjust for call to regr.on_cellvertices

        z = self._get_z(envtup)

        if self.cellgrid:
            if self.model=='roms':
                if ztmp=='s_rho':
                    self.zcoord_native_var='s_rho' # restore

        regr = regrid.regrid()
        z = regr.reduce(z, envtup, guessed)
        z = np.squeeze(z)

        ###################################################
        # regrid onto plotting axis

        stag1 = stag[isliceddims[0]]
        stag2 = stag[isliceddims[1]]

        if self.cellgrid is False:
            z = regr.on_points_multidim(z, [stag1, stag2])
        else:
            z = regr.on_cellvertices(z, stag1, stag2)

        return z

