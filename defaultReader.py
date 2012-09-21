# -*- coding: utf-8 -*-
from netCDF4 import Dataset as NF
import numpy as np

class reader:
    def __init__(self):
        
        self.fname=""
        self.ff=""
        self.keys_2d_variables=[]

    def open(self,string):
        self.fname=string
        self.ff = NF(str(string), 'r')
        li=self.ff.variables.keys()
        self.keys_2d_variables=[]
        for ii in li:
            dl=self.ff.variables[ii].dimensions
            if len(dl)>1:
                self.keys_2d_variables.append(ii)


    def get_var(self,string,tup):
        try:
            va=self.ff.variables[string][tup]
        except KeyError:
            va=self.custom_var(string,tup) 
        
        # int32? e.g. in WOA09, variable 't_dd' (number of observations)
        if va.dtype=='int32': 
            va=va.astype(np.float32) 
        va[va<-1e20]=np.nan;
        va[va>1e20]=np.nan;
        if np.all(np.isnan(va)):
            va=np.zeros(np.shape(va));
            va=np.zeros(np.shape(va));    
        return va 
            
    def get_combo2_vars(self,dn1): 
        varlist=[]
        for ii in self.ff.variables.keys():
            dn2=self.ff.variables[ii].dimensions
            if dn1==dn2:
                varlist.append(ii)
        return varlist
            
 
    
