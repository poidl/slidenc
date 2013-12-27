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
#        self.dims=[]
        self.zcoord_trafo_available=False
        self.zcoord_native=''
        self.zcoord_added=''
        self.zcoord_active=''
        
    def set_var(self,string):
        self.var=string
        if self.var not in self.ncvars:
            print 'variable \''+string+'\' not in netcdf file'
            return
        self.__ncread_vardata()
        self.__guess_trafo() 

    def __ncread_vardata(self):
        self.ncdims=self.ncr.vardims(self.var)
        self.ncshape=self.ncr.varshape(self.var)
        self.ncshape_phys=self.ncr.varshape_phys(self.var)
        
    def __guess_trafo(self):
        magicdim='Layer'
        if magicdim in self.ncdims:
            self.modelguess='him'
            if 'e' in self.ncvars: 
                self.zcoord_trafo_available=True
                self.zcoord_native=magicdim
                self.zcoord_added='z'
                self.zcoord_active=self.zcoord_native

    def set_zcoord_active(self,string):
        if string not in ['native','added']:
            print 'set_active_zcoord(string): '
            print '     argument must be \'native\' or \'added\''
            return
        if self.zcoord_trafo_available is False:
            print 'No coordinate transformation available.'
            return        
        elif string=='native':
            self.zcoord_active=self.zcoord_native
        elif string=='added': 
            self.zcoord_active=self.zcoord_added

                
        
            
        
        
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
                    
                    
                    
            
        
        
        


