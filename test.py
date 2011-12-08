# We start from an example file for user_interfaces/embedding_in_qt4
# available on the matplotlib website.
import sys, os, random
from functools import partial as fpartial
from PyQt4 import QtGui, QtCore
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.artist as mpla
from matplotlib.colorbar import Colorbar as cb
import matplotlib.patches as ptch
from matplotlib.collections import PatchCollection
import matplotlib as mpl
#from  Scientific.IO.NetCDF  import NetCDFFile as NF
from netCDF4 import Dataset as NF
import pyomReader
import romsReader
import himReader

progname = os.path.basename(sys.argv[0])

progversion = "0.0"
ndims_max=5
class myax_new():
    def __init__(self):
        self.dim_names=[]
        self.ndims=0
        self.perm=[]       
        self.indices_ini=[] 
        self.indices=[]
    
    def setax(self,reader,string):
        self.dim_names=reader.ff.variables[str(string)].dimensions
        self.ndims=len(self.dim_names)
        self.perm=range(self.ndims)        
        self.indices_ini=[1]*(self.ndims-2) 
        self.indices=self.indices_ini[:]
    def permute(self,ind,val):
        tmp=self.perm[:]
        self.perm[ind]=val
        self.perm[tmp.index(val)]=tmp[ind]
        self.perm[:ind]=sorted(self.perm[:ind])
        self.indices=self.indices_ini[:]
        
    def get_dimname(self,ind):
        return self.dim_names[self.perm[ind]]
    
    def tup(self):
        li=[]; cnt=0
        for ii in range(self.ndims):
            li.append('')
        for ii in range(self.ndims):
            if self.perm.index(ii)>self.ndims-3:
                li[ii]=slice(None)
            else: li[ii]=self.indices[cnt];  cnt+=1 
        return tuple(li)

reader=pyomReader.reader()

ax=myax_new()
ax.setax(reader, 'u')
print ax.dim_names
print ax.ndims-1
ax.permute(ax.ndims-1,1)
print ax.perm
ax.permute(ax.ndims-2,1)
 
    
         
        
    
                
            