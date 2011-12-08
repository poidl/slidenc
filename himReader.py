#from Scientific.IO.NetCDF import NetCDFFile as NF
from netCDF4 import Dataset as NF
import numpy as np

class reader:
    ff = NF('/home/stefan/arbeit/him/run43/saves/save0.00e00.041.016.nc', 'r')
    modelVarNames = ff.variables.keys()
    customVarNames=['b_full']
    customVarDims=[4]
    varNames=modelVarNames+customVarNames
    
    def set_filename(self,string):
        ff = NF(string, 'r')
        return ff
    def custom_var(self,string,tup):
        if string=='tra':
            e=self.ff.variables['e'][tup]
            bback=-self.ff.variables['back'][tup[1:]];
            bd[bd>1e3]=np.nan;
            if bd.shape != bback.shape: # 'back' has no time axis
                b=bd+np.tile(bback[np.newaxis,:],(bd.shape[0],1));
            else:
                b=bd+bback
            return b          

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
    
    def get_var_names(self):
        l=[]
        for ii in self.modelVarNames:
            if len(self.ff.variables[ii].dimensions)==4: l.append(ii)
        for ii in self.customVarNames:
            if self.customVarDims[self.customVarNames.index(ii)]==4: l.append(ii)            
        return l

    def get_current_time_dimension(self):
        return self.ff.variables['u'].shape[0]
    
    def get_bool(self,dn): #dn: list of dim_names
        l=[['Time'], #l: aequivalent dims
           ['Layer'],
           ['Interface'],
           ['lath','latq'],
           ['lonh','lonq']]
        bo=[False]*len(l); 
        for string in dn:
            for ii in range(len(bo)):
                if string in l[ii]:
                    bo[ii]=True
        return bo
            
    def get_combo2_vars(self,dn1): 
        varlist=[]
        for ii in self.ff.variables.keys():
            dn2=self.ff.variables[ii].dimensions
            if (self.get_bool(dn1)==self.get_bool(dn2)):
                varlist.append(ii)
        return varlist
    
    
 
    