# -*- coding: utf-8 -*-
#from  Scientific.IO.NetCDF  import NetCDFFile as NF
from netCDF4 import Dataset as NF
import numpy as np

class reader:
    def __init__(self):
        
        self.ff=""
        self.keys_2d_variables=[]

    def open(self,string):
#        self.ff = NF('/ubuntu10.4_home/stefan/arbeit/him/run75/saves/save0.00e00.213.085.nc', 'r')
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
            
#    def get_first_2d_var(self):
#        li=self.ff.variables.keys() 
#        for ii in range(len(li)):
#            dl=self.ff.variables[li[ii]].dimensions
#            if len(dl)>1:
#                return ii,li[ii]
 
    
