#!/usr/bin/env python
# We start from an example file for user_interfaces/embedding_in_qt4
# available on the matplotlib website.
from PyQt4 import QtGui
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import defaultReader


ndims_max=5
class myax():
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
    
    #def get_orig_ind(self,ind):
        
    
    def tup(self):
        li=[]; cnt=0
        for ii in range(self.ndims):
            li.append('')
        for ii in range(self.ndims):
            if self.perm.index(ii)>self.ndims-3:
                li[ii]=slice(None)
            else: li[ii]=self.indices[cnt];  cnt+=1 
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
        self.vertical=''
        
    def update(self):
        self.field_2d=self.reader.get_var(self.cf_str,self.myax.tup())   
        tmp=self.myax.perm[-2:] 
        self.flip=True if tmp[0]>tmp[1] else False
       
        li= [str(self.myax.dim_names[self.myax.perm[-1]]),
             str(self.myax.dim_names[self.myax.perm[-2]])]
        if 'Interface' in li: self.vertical='Interface'
        elif 'Layer' in li: self.vertical='Layer'
        else: self.vertical='z'
        if self.vertical is not 'z':       
            try: e=self.reader.get_var('e',self.myax.tup())
            except: 
                try: e=self.reader.get_var('etm',self.myax.tup())
                except: print 'No interface height found'
                
            i1=self.myax.tup().index(slice(None))
            i2=self.myax.tup().index(slice(None),i1+1)
            self.i_vert=self.myax.dim_names.index(self.vertical)
            if i1==self.i_vert: 
                self.i_vert=0; i2=1
            else: i2=0; self.i_vert=1
            
            x1=np.arange(e.shape[i2])
            x1=np.r_[[x1]*e.shape[self.i_vert]]
            if self.cf_str is  'e':
                c=np.ones((e.shape[i2]))
                c=np.r_[[ii*c for ii in range(e.shape[self.i_vert]-1)]]
                self.field_2d=c  
                
            if self.flip==True:
                self.x=e
                self.y=x1
            else:
                self.x=x1
                self.y=e
                             
        else:    
            print self.cf_str  
            #self.field_2d=self.reader.get_var(self.cf_str,self.myax.tup())   
            if self.flip==True: 
                self.field_2d=np.transpose(self.field_2d);

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self,reader=None,show_contours=False,parent=None, width=5, height=4, dpi=100):
        self.pdata=pdata()
        fig=Figure()
        self.axes = fig.add_subplot(111)        
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)       
        self.colorbar=fig.colorbar

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        
        FigureCanvas.updateGeometry(self)

class MyStaticMplCanvas(MyMplCanvas):       
    def reset_contour(self):        
        if self.pdata.show_contours:
            self.axes.hold(True) 
        #what a mess. use hasattr(...) instead??
        try:
            for coll in self.ba.collections:
                try:    
                    self.axes.collections.remove(coll)
                except: pass  
        except AttributeError: pass     
        try:
            while len(self.ba.labelTexts)>0: self.ba.pop_label()
        except: pass
        if self.pdata.show_contours:
            self.ba=self.axes.contour(self.pdata.field_2d,colors='k')
            self.ba.clabel()
            self.axes.hold(False)
        self.draw()     
        
    def update_figure(self):
        
        if self.pdata.vertical is not 'z':       
            try:
                for coll in self.axes.collections:  
                    self.axes.collections.remove(coll)  
            except AttributeError: pass
                
            x=self.pdata.x
            y=self.pdata.y
            z=self.pdata.field_2d        
            pc=self.axes.pcolormesh(x,y,z)
            for ii in range(x.shape[self.pdata.i_vert]):
                myline=Line2D(x[ii,:],y[ii,:],color='k')    
                self.axes.add_line(myline) 
                
            self.axes.set_aspect('auto')
            if hasattr(self,'cb'): #remove colorbar
                self.figure.delaxes(self.figure.axes[1])
                self.figure.subplots_adjust(right=0.90)  #default right padding
            self.cb = self.figure.colorbar(pc) 
                          
        else:
            self.a=self.axes.contourf(self.pdata.field_2d,30) 
            self.axes.set_aspect('auto')       
            if hasattr(self,'cb'):
                self.figure.delaxes(self.figure.axes[1])
                self.figure.subplots_adjust(right=0.90)  #default right padding
            self.cb = self.figure.colorbar(self.a)
        self.reset_contour()           


