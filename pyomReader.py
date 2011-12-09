#from  Scientific.IO.NetCDF  import NetCDFFile as NF
from netCDF4 import Dataset as NF
import numpy as np

class reader:
    #ff = NF('/home/stefan/arbeit/pyom/run03/pyOM.cdf', 'r')
    ff = NF('/home/stefan/arbeit/pyom/run03/zonal_ave.cdf', 'r')
#    ff = NF('/home/stefan/arbeit/pyom/bin/acc_gyre1/pyOM.cdf', 'r')
#    ff = NF('/home/stefan/arbeit/pyom/bin/barbi_exp1/pyOM.cdf', 'r')
#    ff = NF('/home/stefan/arbeit/pyom/bin/internal_wave1/pyOM.cdf', 'r')
#    ff = NF('/home/stefan/arbeit/pyom/bin/kelv_helm1/pyOM.cdf', 'r')
    #ff = NF('/home/stefan/arbeit/pyom/run03/zonal_ave.cdf', 'r')
    modelVarNames = ff.variables.keys()
    customVarNames=['b_full']
    customVarDims=[4]
    varNames=modelVarNames+customVarNames
    
    def set_filename(self,string):
        ff = NF(string, 'r')
        return ff
    def custom_var(self,string,tup):
        if string=='b_full':
            bd=self.ff.variables['b'][tup]
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

    def get_current_time_dimension(self):
        return self.ff.variables['u'].shape[0] 

    def get_bool(self,dn): #dn: list of dim_names
        l=[['Time'], #l: aequivalent dims
           ['zt','zu'],
           ['yt','yu'],
           ['xt','xu']]
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
            
    
 
    