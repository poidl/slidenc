#!/usr/bin/env python

#################################################################
# slidenc is a data visualization tool
# Copyright (C) 2011-2014  Stefan Riha

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


# We start from an example file for user_interfaces/embedding_in_qt4
# available on the matplotlib website.
from PyQt5 import QtGui, QtWidgets
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import defaultReader


ndims_max=5
class myax():
    def __init__(self):
        self.dim_names=[]
        self.ndims=0
        self.perm=[] # permutation of dimensions      
        self.sl_inds_ini=[] # initial slider indices
        self.sl_inds=[] # slider indices
    
    def setax(self,reader,string):
        self.dim_names=reader.ff.variables[str(string)].dimensions
        self.ndims=len(self.dim_names)
        self.perm=list(range(self.ndims))   
        self.sl_inds_ini=[0]*(self.ndims-2) 
        self.sl_inds=self.sl_inds_ini[:]
    def permute(self,ind,val):
        tmp=self.perm[:]
        self.perm[ind]=val
        self.perm[tmp.index(val)]=tmp[ind]
        self.perm[:ind]=sorted(self.perm[:ind])
        self.sl_inds=self.sl_inds_ini[:]
        
    def get_dimname(self,ind):
        return self.dim_names[self.perm[ind]]
    
    def tup(self):
        li=[]; cnt=0
        for ii in range(self.ndims):
            if self.perm.index(ii)>self.ndims-3:
                li.append(slice(None))
            else: li.append(self.sl_inds[cnt]);  cnt+=1 
        return tuple(li)

class pdata:
    def __init__(self):
        self.reader=defaultReader.reader()
        self.cf_str=''
        self.c_str=''
        self.myax=myax()
        self.flip=False
        self.show_contours=False
        self.field_2d=np.nan
        self.field_2d_c=np.nan
        self.vertical=''

    def update(self):
        self.update_cf()
        self.update_c()
            
    def update_cf(self):

        self.field_2d=self.reader.get_var(self.cf_str,self.myax.tup())   
        tmp=self.myax.perm[-2:]  
   
        self.flip=True if tmp[0]>tmp[1] else False
        
        #self.z_const=1
        #if self.z_const==1:
            
       
        li= [str(self.myax.dim_names[self.myax.perm[-1]]),
             str(self.myax.dim_names[self.myax.perm[-2]])]
        if 'Interface' in li: self.vertical='Interface'
        elif 'Layer' in li: self.vertical='Layer'
        else: self.vertical='z'
        if self.vertical is not 'z':
            # read interface heights for plots against vertical axes 
            try: e=self.reader.get_var('e',self.myax.tup())
            except: 
                try: e=self.reader.get_var('etm',self.myax.tup())
                except:  'No interface height found'
                
            # ivert is the vertical index in the 2d-field (0 or 1)    
            i1,i2=sorted(self.myax.perm[-2:])
            self.ivert=[i1,i2].index( self.myax.dim_names.index(self.vertical) )
            self.inonvert=1 if self.ivert==0 else 0
            
            # x1 holds the non-vertical coordinate
            x1=np.arange(e.shape[self.inonvert])
            x1=np.r_[[x1]*e.shape[self.ivert]]
            if self.ivert>self.inonvert:
                x1=x1.transpose()
                
            if self.cf_str is 'e':
                # color indicates number of layer
                c=np.ones((e.shape[self.inonvert]))
                c=np.r_[[ii*c for ii in range(e.shape[self.ivert]-1)]]
                self.field_2d=c
                
            if np.logical_xor( self.flip==True, self.ivert>self.inonvert ):      
                (self.x,self.y) = (e,x1)
            else: (self.x,self.y) =(x1,e)      
                              
        else:      
            if self.flip==True: 
                self.field_2d=np.transpose(self.field_2d);
                
    def update_c(self):
        self.field_2d_c=self.reader.get_var(self.c_str,self.myax.tup())    
        if self.flip==True: 
            self.field_2d_c=np.transpose(self.field_2d_c);
        
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self,reader=None,show_contours=False,parent=None, width=5, height=4, dpi=100):
        self.pdata=pdata()
        fig=Figure()
        self.axes = fig.add_subplot(111)        
        self.axes.hold(False)       
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        
        FigureCanvas.updateGeometry(self)

class MyStaticMplCanvas(MyMplCanvas):    
        
    def update_figure(self):
        self.axes.cla() 
        if hasattr(self,'cb'): #remove colorbar
                self.figure.delaxes(self.figure.axes[1])
                self.figure.delaxes(self.figure.axes[0])
                self.axes=self.figure.add_subplot(111) 
                #self.figure.delaxes(self.figure.axes[1])
                #self.figure.subplots_adjust(right=0.90)                
        self.axes.set_aspect('auto')
        if self.pdata.vertical is not 'z':                                 
            x=self.pdata.x
            y=self.pdata.y
            z=self.pdata.field_2d 
            self.axes.pcolormesh(x,y,z)
            if self.pdata.ivert>self.pdata.inonvert: 
                x=x.transpose(); y=y.transpose() 
            for ii in range(x.shape[0]):
                myline=Line2D(x[ii,:],y[ii,:],color='k')       
                self.axes.add_line(myline) 
                                                 
        else:
            self.a=self.axes.contourf(self.pdata.field_2d,30) 

        self.cb = self.figure.colorbar(self.a)
            
        if self.pdata.show_contours:
            self.reset_contour()  
        self.draw()
              
    def reset_contour(self):   
        # don't delete color contours when drawing contours
        self.axes.hold(True)
        # if the array is constant, don't contour
        tt=np.abs(self.pdata.field_2d_c)
        tt2=tt[~np.isnan(tt)]
        if not np.all( tt2-np.max(tt2)==0. ):
            self.cs=self.axes.contour(self.pdata.field_2d_c,colors='k')
            self.cs.clabel()
        self.axes.hold(False)       


