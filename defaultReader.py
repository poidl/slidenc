#from  Scientific.IO.NetCDF  import NetCDFFile as NF
from netCDF4 import Dataset as NF
import numpy as np

class reader:
#    ff = NF('/home/stefan/arbeit/pyom/run03/pyOM.cdf', 'r')
    ff = NF('/suse/home/stefan/arbeit/Roms_tools/run128/ROMS_FILES/roms_avg_1.nc', 'r')
#    ff = NF('/home/stefan/arbeit/him/run43/saves/save0.00e00.041.016.nc', 'r')
        

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
            
    
 
    