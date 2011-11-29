from Scientific.IO.NetCDF import NetCDFFile as NF
import numpy as np

class reader:
    ff = NF('/home/stefan/arbeit/pyom/run03/pyOM.cdf', 'r')
    modelVarNames = ff.variables.keys()
    customVarNames=['b_full']
    customVarDims=[4]
    varNames=modelVarNames+customVarNames
    
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
        

    def get_var(self,string,tup):
        try:
            va=self.ff.variables[string][tup]
        except KeyError:
            va=self.custom_var(string,tup)            
        va[va<-1e20]=np.nan;
        va[va>1e20]=np.nan;            
        return va


    def  get_axis(self,string):
        if string=='x':
            va=self.ff.variables['xt'][:]
        elif string=='y':
            va=self.ff.variables['yt'][:]
        elif string=='z':
            va=self.ff.variables['zt'][:]
        elif string=='time':
            va=self.ff.variables['Time'][:]
        va[va<-1e20]=np.nan;
        va[va>1e20]=np.nan;                       
        return va
 
    