#################################################################
# slidenc is a data visualization tool
# Copyright (C) 2011-2013  Stefan Riha

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
        self.zcoord_added=''
        self.zcoord_active=''
        
    def set_var(self,string):
        self.varname=string
        if self.varname not in self.ncvars:
            print 'variable \''+string+'\' not in netcdf file'
            return
        self.__ncread_vardata()
        self.__guess_trafo() 

    def __ncread_vardata(self):
        self.ncdims=self.ncr.vardims(self.varname)
        self.ncshape=self.ncr.varshape(self.varname)
        self.ncshape_phys=self.ncr.varshape_phys(self.varname)
        
    def __guess_trafo(self):
        magicdim='Layer'
        if magicdim in self.ncdims:
            self.modelguess='him'
            if 'e' in self.ncvars: 
                self.zcoord_trafo_available=True
                self.zcoord_native=magicdim
                self.zcoord_added='z'
                self.zcoord_active='native'
                self.zcoord_index=self.ncdims.index(magicdim)
                self.zcoord_trafovarname='e'

    def set_zcoord_active(self,string):
        if string not in ['native','added']:
            print 'set_active_zcoord(string): '
            print '     argument must be \'native\' or \'added\''
            return
        if self.zcoord_trafo_available is False:
            print 'No coordinate transformation available.'
            return        
        elif string=='native':
            self.zcoord_active='native'
        elif string=='added': 
            self.zcoord_active='added'
            
#    def get_slice(self,tup):
#        if self.zcoord_trafo_available is False:
#            va=self.ncr.varread(self.varname,tup)
#        else:
#            if self.zcoord_active=='native':
#                va=self.ncr.varread(self.varname,tup)
#            if self.zcoord_active=='added':
#                va=self.__regrid(tup)
#        return va

#    def __regrid(self,tup):
#        izc=self.zcoord_index
#        ncdims2=self.ncr.vardims(self.zcoord_trafovarname) 
#        # check for staggered grid
#        staggered=[i==j for i,j in zip(self.ncdims,ncdims2)]
#        
#        
#        self.ncdims=self.ncr.vardims(self.varname)
#        islice = [i for i, x in enumerate(tup) if x == slice(None)]
#        dimslice=[self.ncdims[i] for i in islice]
#        if izc in islice:
#            dim2=dimslice[islice.index(izc)-1] #non-vertical dim
#            print dim2
#            #data=self.ncr.varread(self.varname,tup)
#            #if self.modelguess='him'
#    
    
    def _get_staggervec(self,var1name,var2name):
        #0:--- 1:- - -  (-1): - - - (2):- - - (-2): - - -  (99): none of the above
        #  xxx    x x x      x x x       x x       x x x x     
        ncdims1=self.ncr.vardims(var1name)
        ncdims2=self.ncr.vardims(var2name)
        staggered=[i!=j for i,j in zip(ncdims1,ncdims2)]
        print staggered
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
                 
  
         
         
                 
            
#                z=self.ncr.varread(self.zcoord_trafovarname,tup) 
            
        
        
#        
        
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
                    
                    
                    
            
        
        
        


