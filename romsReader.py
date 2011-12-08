#from Scientific.IO.NetCDF import NetCDFFile as NF
from netCDF4 import Dataset as NF
import numpy as np

class reader:
    ff = NF('/suse/home/stefan/arbeit/Roms_tools/run128/ROMS_FILES/roms_avg_1.nc', 'r')
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
    
    def get_var_names_4d(self):
        l=[]
        for ii in self.modelVarNames:
            if len(self.ff.variables[ii].dimensions)==4: l.append(ii)
        for ii in self.customVarNames:
            if self.customVarDims[self.customVarNames.index(ii)]==4: l.append(ii)            
        return l    

#    def get_var_names(self):
#        l=[]
#        for ii in self.modelVarNames:
#            if len(self.ff.variables[ii].dimensions)==4: l.append(ii)
#        for ii in self.customVarNames:
#            if self.customVarDims[self.customVarNames.index(ii)]==4: l.append(ii)            
#        return l         

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


    def  get_axis(self,string):
        try:
            va=self.ff.variables[string][:]
        except: #roms
            if string=='time': #roms
                va=range( self.ff.variables['u'].shape[0] )
            else: 
                va=range( self.ff.dimensions[string] ) 
        return va                          
#        if string=='x':
#            va=self.ff.variables['xt'][:]
#        elif string=='y':
#            va=self.ff.variables['yt'][:]
#        elif string=='z':
#            va=self.ff.variables['zt'][:]
#        elif string=='t':
#            va=self.ff.variables['Time'][:]                      
#        return va
 
       
 
    