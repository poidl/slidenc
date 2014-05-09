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

from netCDF4 import Dataset as NF
import numpy as np
import regrid as regrid
        
        
class ncreader:
    def __init__(self,string):
        self.ncfname=string
        self.ncf = NF(str(string), 'r')
        
    def dims(self):
        return self.ncf.dimensions.keys()

    def vars(self):
        return self.ncf.variables.keys() 

    def dimlims(self):
        return [len(self.ncf.dimensions.values()[i]) \
        for i in range(len(self.ncf.dimensions.values()))]

    def vardims(self,varname):
        return self.ncf.variables[varname].dimensions
                
    def varshape(self,varname):
        return self.ncf.variables[varname].shape
    
    def ndims(self,varname):
        return self.ncf.variables[varname].ndims
        
    def varread(self,varname,tup):
        return self.ncf.variables[varname][tup]
  
    
    def varshape_phys(self,varname):
        dims=self.vardims(varname)
        l = []
        for ii in dims:
            mi=self.varread(ii, (0))
            ma=self.varread(ii, (-1))
            l.append([mi,ma])
        return l



class myreader:
    def __init__(self,string):
#        self.model=''
        self.ncr=ncreader(string)
        self.ncvars=self.ncr.vars() # tuple
        self.zcoord_trafo_available=False
        self.zcoord_native=''
        self.zcoord_active=''
        self.zcoord_index='' 
        self.zcoord_added=''    
        self.cellgrid=False        
        
    def set_var(self,string):
        self.varname=string
        if self.varname not in self.ncvars:
            print 'variable \''+string+'\' not in netcdf file'
            return
        self.__ncread_vardata()
        #self.__guess_trafo()
        #self.set_trafo_roms() 
        
    def set_trafo_him(self):
        self.zcoord_native='Layer'
        self.zcoord_added='e' 
        self.set_trafo_default()
           
    def set_trafo_roms(self):
        self.zcoord_native='s_rho'
        self.zcoord_added='z'
        self.set_trafo_default()
    
    def set_trafo_default(self):
        self.zcoord_trafo_available=True
        self.zcoord_active='native'
        self.zcoord_index=self.ncdims.index(self.zcoord_native)    
        
    def __ncread_vardata(self):
        self.ncdims=self.ncr.vardims(self.varname)
        self.ncshape=self.ncr.varshape(self.varname)
#        self.ncshape_phys=self.ncr.varshape_phys(self.varname)
        
#     def __guess_trafo(self):
#         magicdim='Layer'
#         if magicdim in self.ncdims:
#             self.modelguess='him'
#             if 'e' in self.ncvars: 
#                 self.zcoord_trafo_available=True
#                 self.zcoord_native=magicdim
#                 self.zcoord_active='native'
#                 self.zcoord_index=self.ncdims.index(magicdim)
#                 self.zcoord_added='e'


    def set_zcoord_active(self,string):
        if self.zcoord_trafo_available is False:
            raise Exception('No coordinate transformation available.')
            return 
        elif string not in ['native','added']:
            raise Exception('Argument must be \'native\' or \'added\'')           
            return
       
        elif string=='native':
            self.zcoord_active='native'
        elif string=='added': 
            self.zcoord_active='added'
            
        

    def get_var(self,tup):
        
        ifixeddims=[i for i, x in enumerate(tup) if x != slice(None)]
        isliceddims=[i for i, x in enumerate(tup) if x == slice(None)]
             
        if (self.zcoord_index in ifixeddims) and \
            self.zcoord_active=='added':
                # we want to plot data on an iso-surface of the added coordinate, 
                # i.e. get data at constant zcoord.
                
                
                # First, interpolate zcoord onto variable grid
                
                # need to extract a 3-d slice of the coordinate. Two of them are the axes against
                # which is plotted, the third is the vertical direction. 
                
                #The remaining fixed indices could be staggered
                stag=self._get_staggervec(self.zcoord_added,self.varname)
                z=tup[self.zcoord_index]
                etup=list(tup)
                etup[self.zcoord_index]=slice(None)
                vatup=etup
                ifixeddims_tmp=[i for i, x in enumerate(etup) if x != slice(None)]
                envtup,guessed=self._get_envelope_tup(etup,ifixeddims_tmp,stag)                                                 
                e=self.ncr.varread(self.zcoord_added,envtup)
                regr=regrid.regrid()
                e=regr.reduce(e,envtup,guessed)                
                #e=np.squeeze(e)         
                
                # re-grid the plot axes 
                stag_tmp=stag
                for ii in ifixeddims_tmp:
                    stag_tmp[ii]=0
                e=regr.on_points_multidim(e, stag_tmp)
                #e=np.squeeze(e)
                bl=e>=z
                s=np.sum(bl,self.zcoord_index)
                s=np.squeeze(s)
                
                n1=self.ncshape[isliceddims[0]]
                n2=self.ncshape[isliceddims[1]]
                n3=self.ncshape[self.zcoord_index]
                # row major order
                if (self.zcoord_index<isliceddims[0]) and (self.zcoord_index<isliceddims[1]):
                    sr=s.ravel()
                    inds1=(sr-1)*n1*n2+np.arange(n1*n2)-1
                    bottom=inds1>(n3-1)*n1*n2
                    inds1[bottom]=1 # dummy, correct later
                    inds2=inds1+n1*n2
                                  
                    
                va1=self.ncr.ncf.variables[self.varname][vatup].flat[inds1]
                va2=self.ncr.ncf.variables[self.varname][vatup].flat[inds2]
                z1=e.flat[inds1]
                z2=e.flat[inds2]
                dz=(z-z2)/(z1-z2)
                va=va2+(va1-va2)*dz
                upper_only= dz==0 # in case dz is zero and lower bottle is nan
                va[upper_only]=va1[upper_only]
                va=np.reshape(va,(n1,n2))
                
        else:
            va=self.ncr.varread(self.varname,tup)   
            
        return va       
        
    def get_physgrid(self,tup):
        isliceddims=[i for i, x in enumerate(tup) if x == slice(None)]
        ifixeddims=[i for i, x in enumerate(tup) if x != slice(None)]
        sliceddims=[self.ncdims[i] for i in isliceddims]

        regr=regrid.regrid()

        if self.zcoord_index!=isliceddims[0]:
            x=self.ncr.varread(sliceddims[0],slice(None))
            if self.cellgrid==True:
                x=regr.d1_point_to_cellvertices(x)     
                       
        if self.zcoord_index!=isliceddims[1]:
            y=self.ncr.varread(sliceddims[1],slice(None))
            if self.cellgrid==True:
                y=regr.d1_point_to_cellvertices(y)                        
          
        
        if (self.zcoord_index in isliceddims) and \
            self.zcoord_active=='added':
                 
                stag=self._get_staggervec(self.zcoord_added,self.varname)
 
                ###################################################
                # regrid indices against which is *not* plotted (fixed
                # indices)
                envtup,guessed=self._get_envelope_tup(tup,ifixeddims,stag)                                                 
                e=self.ncr.varread(self.zcoord_added,envtup)
                 
                e=regr.reduce(e,envtup,guessed)
                
                e=np.squeeze(e)

                print e.shape
                
                
                ###################################################
                # regrid indices against which *is* plotted 
                 
                stag1=stag[isliceddims[0]]
                stag2=stag[isliceddims[1]] 
                
                if self.cellgrid is False:     
                    e=regr.on_points_multidim(e,[stag1,stag2])
                else:
                    e=regr.on_cellvertices(e,stag1,stag2)
                    
                print e.shape 
                
                if self.zcoord_index==isliceddims[0]:
                    x=e
                    y,dummy=np.meshgrid(y,x[:,0])
                elif self.zcoord_index==isliceddims[1]:
                    y=e    
                    dummy,x=np.meshgrid(y[0,:],x)  
                                 
                                 
        else: # self.zcoord_index in isliceddims:
            y,x=np.meshgrid(y,x) 
          
        return x,y 
    
    
    def _get_envelope_tup(self,tup,ifixeddims,stag):
        
        # compute envelope tuple, or tuple which has to be extracted from variable A such that it can be 
        # interpolated onto the grid of variable B (which is potentially staggered with respect to grid 
        # of A).
        # example from HIM: we want the z coordinates of u(layer,lath,lonq)
        # for the slice u(:,:,5). 
        # z is defined on z(interface,lath,lonh) and 
        # needs be interpolated onto (layer,lath,lonq). the envelope tuple is
        # (:,:,4:5) and contains all data needed for interpolation
        
        def mod_slice(sl,m):
        # modify slice object sl: add elements of vector m=[delta_start,delta_stop]
            if m[0]!=0: # modify start
                istart=sl.start+m[0]
                istop=sl.stop
                              
            if m[1]!=0: # modify stop
                istop=sl.stop+m[1]
                istart=sl.start
                
            istep=sl.step
            return slice(istart,istop,istep)
        
        l=list(tup)
        # `guessing` means extrapolation. Necessary at start- and end-point if grid of A is smaller than B
        # values: 1 if extrapolating at origin, 2 if extr. at end
        guessing=[0]*len(tup) 
        
        for i in ifixeddims:
            if stag[i]==1:
                if l[i].start<self.ncshape[i]-1:
                    l[i]=mod_slice(l[i],[0,1])
                else: # for the last grid point, extrapolate linearly from interior
                    l[i]=mod_slice(l[i],[-1,0])
                    guessing[i]=2
            elif stag[i]==-1:
                if l[i].start>0:
                    l[i]=mod_slice(l[i],[-1,0])                   
                else: # for the first grid point, extrapolate 
                    l[i]=mod_slice(l[i],[0,1])
                    guessing[i]=1
            elif stag[i]==2:    
                    l[i]=mod_slice(l[i],[0,1])            
            elif stag[i]==-2:
                if l[i].start>0 and l[i].start<self.ncshape[i]-1:
                    l[i]=mod_slice(l[i],[-1,0])                   
                elif l[i].start==0: # first
                    l[i]=mod_slice(l[i],[0,1])  
                    guessing[i]=1
                elif l[i].start==self.ncshape[i]-1: # last
                    l[i]=mod_slice(l[i],[-1,0])                   
                    guessing[i]=2
                    
                    
        tup=tuple(l)       
        
        return tup,guessing
        
    
    def _get_staggervec(self,var1name,var2name):
        #0:--- 1:- - -  (-1): - - - (2):- - - (-2): - - -  (99): none of the above
        #  xxx    x x x      x x x       x x       x x x x     
        ncdims1=self.ncr.vardims(var1name)
        ncdims2=self.ncr.vardims(var2name)
        staggered=[i!=j for i,j in zip(ncdims1,ncdims2)]
        #print staggered
        for i in range(len(staggered)):
            if staggered[i]:
                start=self.ncr.ncf.variables[ncdims1[i]][:2]
                end=self.ncr.ncf.variables[ncdims1[i]][-2:]
                v1=np.concatenate([start,end])
                start=self.ncr.ncf.variables[ncdims2[i]][:2]
                end=self.ncr.ncf.variables[ncdims2[i]][-2:]
                v2=np.concatenate([start,end])
                if v1[0]<v2[0] and v2[0]<v1[1]:
                    if v2[-2]<v1[-1] and v1[-1]<v2[-1]:
                        staggered[i]=1
                    elif v1[-2]<v2[-1] and v2[-1]<v1[-1]:                
                        staggered[i]=2
                    else:
                        staggered[i]=99
                elif v2[0]<v1[0] and v1[0]<v2[1]:
                    if v1[-2]<v2[-1] and v2[-1]<v1[-1]:
                        staggered[i]=-1
                    elif v2[-2]<v1[-1] and v1[-1]<v2[-1]:
                        staggered[i]=-2
                    else:
                        staggered[i]=99 
                else:
                    staggered[i]=99
            else:
                staggered[i]=0
                
        return staggered
     
#                z=self.ncr.varread(self.zcoord_added,tup) 
        
#        self.__set_dims()
#        self.__set_shape()
#        self.__set_shape_phys()
        
#    def __set_dims(self):
#        if self.zcoord_native=='Layer':
#            lncdims=list(self.ncdims)
#            if 'e' in self.ncr.vars(): 
#                self.zcoord_trafo_available=True
#                t=(u'Layer',u'z')       
#                ii=self.ncdims.index('Layer')
#                lncdims[ii]=t
#            else:
#                print 'No interface height found'   
#            self.dims=tuple(lncdims)
#        
#    def __set_shape(self):
#        self.shape=self.ncshape 
#        
#    def __set_shape_phys(self):
#        self.shape_phys=self.ncshape_phys
#        if self.model=='him':
#            if self.zcoord_trafo_available:
#                e=self.ncr.varread('e',slice(None))
#                e_lims=[e.min(), e.max()]               
#                ii=self.ncdims.index('Layer')                
#                layer_lims=self.ncshape_phys[ii]              
#                self.shape_phys[ii]=[layer_lims, e_lims]
#        
    
#    def set_active_zcoord(self,string):
#        if string not in ['native','z']:
#            print 'set_active_zcoord(string): '
#            print '     argument must be \'native\' or \'z\''
#        if self.shape_phys()
#            return
#        
