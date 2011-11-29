from Scientific.IO.NetCDF import NetCDFFile as NF
import numpy as np

class reader:
    ff = NF('/suse/home/stefan/arbeit/Roms_tools/run128/ROMS_FILES/roms_avg_1.nc', 'r')
    modelVarNames = ff.variables.keys()
    customVarNames=[]
    varNames=modelVarNames+customVarNames
    
    
    def get_var_names_4d(self):
        l=[]
        for ii in self.modelVarNames:
            if len(self.ff.variables[ii].dimensions)==4: l.append(ii)
        #for ii in self.customVarNames:
        #    if len(self.custom_var(ii).shape)==4: l.append(ii)    
        return l    
        
    def get_var(self,string):
        #try:
        va=self.ff.variables[string][:]
        #except KeyError:
        #    va=self.custom_var(string)            
        va[va<-1e20]=np.nan;
        va[va>1e20]=np.nan;            
        return va
        
    def  get_axis(self,string):
        if string=='x':
            va=np.float_(np.arange(self.ff.dimensions['xi_u']))
        elif string=='y':
            va=np.float_(np.arange(self.ff.dimensions['eta_rho']))
        elif string=='z':
            va=np.float_(np.arange(self.ff.dimensions['s_rho']))
        elif string=='time':
            va=np.float_(self.ff.variables['scrum_time'][:])
        va[va<-1e20]=np.nan;
        va[va>1e20]=np.nan;                       
        return va

       
 
    