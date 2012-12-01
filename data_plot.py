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
        self.reader=defaultReader.reader()
        self.dim_names=[]
        self.dim_vals=[]
        self.ndims=0
        self.perm=[] # permutation of dimensions
        self.flip=[] # boolean array: if true, flip dimension 
        self.coords=[]  
        self.sl_inds_ini=[] # initial slider indices
        self.sl_inds=[] # slider indices
        self.vertaxEnableChoices='False'
    
    
    def setax(self,varname):
        self.dim_names=self.reader.ff.variables[str(varname)].dimensions
        if self.reader.vertaxType(varname)=='him':
            self.vertaxEnableChoices='True'
            
        self.ndims=len(self.dim_names)
        self.perm=range(self.ndims)  
        self.flip=[False]*self.ndims
        self.coords=['dim']*self.ndims     
        self.sl_inds_ini=[0]*(self.ndims-2) 
        self.sl_inds=self.sl_inds_ini[:]
        self.dim_vals=[]
        self.dim_inds=[]
        for ii in range(self.ndims):
            dn=self.dim_names[ii]
            # is the dimension also a variable? If not, set dim_vals
            # to the grid indices
            tmp=np.arange(len(self.reader.ff.dimensions[dn]))
            self.dim_inds.append(tmp)
            if dn in self.reader.ff.variables.keys():
                tmp=self.reader.ff.variables[dn][:]
            self.dim_vals.append(tmp)
            
    def permute(self,ind,val):
        tmp=self.perm[:]
        self.perm[ind]=val
        self.perm[tmp.index(val)]=tmp[ind]
        self.perm[:ind]=sorted(self.perm[:ind])
        self.sl_inds=self.sl_inds_ini[:]
        
    def get_dimname(self,ind):
        return self.dim_names[self.perm[ind]]
    
    def get_dim(self,ind):
        # modify
        return len(self.reader.ff.dimensions[self.get_dimname(ind)])
    
    def tup(self):
        li=[]; cnt=0
        for ii in range(self.ndims):
            if self.perm.index(ii)>self.ndims-3:
                li.append(slice(None))
            else: li.append(self.sl_inds[cnt]);  cnt+=1 
        return tuple(li)
    
    def get_var(self,cf_str):
        return self.reader.get_var(cf_str,self.tup())
    
    def keys_2d_variables(self):
        return self.reader.keys_2d_variables
    
    def get_combo2_vars(self,dn1):
        return self.reader.get_combo2_vars(dn1)
    
    def fname(self):
        return self.reader.fname
    
    def open(self,arg):
        return self.reader.open(arg)

class pdata:
    def __init__(self,myax):
        self.cf_str=''
        self.c_str=''
        self.myax=myax
        self.transp=False
        self.show_contours=False
        self.field_2d=np.nan
        self.field_2d_c=np.nan
        self.vertical_dimname=''
        self.vertical_trafo=False

    def update(self):
        self.update_cf()
        self.update_c()
            
    def update_cf(self):

        self.field_2d=self.myax.get_var(self.cf_str)   
        tmp=self.myax.perm[-2:]  
        d1,d2=sorted(tmp)
        self.transp=True if tmp[0]>tmp[1] else False
       
        li= [str(self.myax.dim_names[self.myax.perm[-1]]),
             str(self.myax.dim_names[self.myax.perm[-2]])]
        if 'Interface' in li: 
            self.vertical_dimname='Interface'
            self.vertical_trafo=True
        elif 'Layer' in li: 
            self.vertical_dimname='Layer'
            self.vertical_trafo=True
        else: 
            self.vertical='z'
            self.vertical_trafo=False
            
        if self.vertical_trafo is True:
            # read interface heights for plots against vertical axes 
            try: e=self.myax.get_var('e')
            except: 
                try: e=self.myax.get_var('etm')
                except:  'No interface height found'
                    
            #get the axis of the 2d-slice along which to transform
            self.ivert=[d1,d2].index( self.myax.dim_names.index(self.vertical_dimname) )
            self.inonvert = not self.ivert
            
            def regrid_vertcoord(e):
                #assume that the variable is horz. velocity 
                #of HIM 
                if self.ivert==0: 
                    e=np.c_[e[:,0],0.5*(e[:,:-1]+e[:,1:]),e[:,-1]]
                return e
                                
            
            #if the vertical coordinate is defined on a different
            #horizontal grid as the variable to plot, do this:
            if self.field_2d.shape[self.inonvert] != e.shape[self.inonvert]:
                e=regrid_vertcoord(e)
            
            ivert_full=[d1,d2][self.ivert]    
            if self.myax.coords[ivert_full]=='grd':
                e,tr=np.meshgrid(range(e.shape[self.ivert]),range(e.shape[self.inonvert]))
                if self.ivert<=self.inonvert:
                    e=e.transpose()         
            inonvert_full=[d1,d2][self.inonvert]
            # x1 holds the non-vertical coordinate
            if self.myax.coords[inonvert_full]=='dim':
                x1=self.myax.dim_vals[inonvert_full]
            elif self.myax.coords[inonvert_full]=='grd':        
                x1=self.myax.dim_inds[inonvert_full]
            x1=np.r_[[x1]*e.shape[self.ivert]]
            if self.ivert>self.inonvert:
                x1=x1.transpose()
                
            if self.cf_str is 'e':
                # color indicates number of layer
                c=np.ones((e.shape[self.inonvert]))
                c=np.r_[[ii*c for ii in range(e.shape[self.ivert]-1)]]
                self.field_2d=c
                
            if np.logical_xor( self.transp==True, self.ivert>self.inonvert ):      
                (self.x,self.y) = (e,x1)
            else: (self.x,self.y) =(x1,e)      
                              
        else:     
            if self.transp==True: 
                self.field_2d=np.transpose(self.field_2d);
                d1,d2=d2,d1
        
            if self.myax.coords[d1]=='dim':
                self.y=self.myax.dim_vals[d1]
            elif self.myax.coords[d1]=='grd':
                self.y=self.myax.dim_inds[d1]
                
            if self.myax.coords[d2]=='dim':
                self.x=self.myax.dim_vals[d2]
            elif self.myax.coords[d2]=='grd':
                self.x=self.myax.dim_inds[d2]   
            
            
            #self.y=self.myax.dim_inds[d1]
            #self.x=self.myax.dim_inds[d2]
               
    def update_c(self):
        #print self.c_str
        self.field_2d_c=self.myax.get_var(self.c_str)
        if self.vertical_trafo is False:
            if self.transp==True: 
                self.field_2d_c=np.transpose(self.field_2d_c);
        
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self,myax,show_contours=False,parent=None, width=5, height=4, dpi=100):
        self.pdata=pdata(myax)
        fig=Figure()
        self.axes = fig.add_subplot(111)        
        self.axes.hold(False)       
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        
        FigureCanvas.updateGeometry(self)

class MyStaticMplCanvas(MyMplCanvas): 
    def __init__(self,myax):   
        MyMplCanvas.__init__(self,myax)
        
    def update_figure(self):
        self.axes.cla()
        if hasattr(self,'cb'): #remove colorbar
                self.figure.delaxes(self.figure.axes[1])
                self.figure.subplots_adjust(right=0.90) 
        self.axes.set_aspect('auto')
        x=self.pdata.x
        y=self.pdata.y
        #print y
        z=self.pdata.field_2d
        if self.pdata.vertical_trafo is True:
        #if 1:
            print x.shape
            print y.shape
            print z.shape
#            x=x[1:,:]
#            y=y[1:,:]
#            z=z[:,1:] 

            self.axes.pcolormesh(x,y,z)  
            #self.axes.contourf(x,y,z)                               
            #self.axes.pcolormesh(x,y,z,shading='gouraud')
            if self.pdata.ivert>self.pdata.inonvert: 
                x=x.transpose(); y=y.transpose() 
            for ii in range(x.shape[0]):
                myline=Line2D(x[ii,:],y[ii,:],color='k')       
                self.axes.add_line(myline) 
                                                 
        else:
            self.a=self.axes.contourf(x,y,z,30)
            
        #flip plot along a dimension?
        tmp=self.pdata.myax.perm[-2:]            
        d1=min(tmp)
        d2=max(tmp)
        if self.pdata.transp==True:
            d1,d2=d2,d1
        xflipped=self.axes.get_xlim()[0]>self.axes.get_xlim()[1]
        yflipped=self.axes.get_ylim()[0]>self.axes.get_ylim()[1]
        if np.logical_xor(self.pdata.myax.flip[d1],yflipped):
            self.axes.invert_yaxis()
        if np.logical_xor(self.pdata.myax.flip[d2],xflipped):
            self.axes.invert_xaxis()
           
           
        self.cb = self.figure.colorbar(self.a)
            
        if self.pdata.show_contours:
            self.reset_contour()  
        self.draw()
              
    def reset_contour(self):   
        # don't delete color contours when drawing contours
        self.axes.hold(True)
        x=self.pdata.x
        y=self.pdata.y
        z=self.pdata.field_2d_c
        
        print x.shape
        print y.shape
        print z.shape
        
        tt=np.abs(z)
        tt2=tt[~np.isnan(tt)]
        # if the array is constant, don't contour
        if not np.all( tt2-np.max(tt2)==0. ):
            if self.pdata.vertical_trafo is True:
                if hasattr(self.pdata,'ivert'):
                    print self.pdata.ivert  
                    if self.pdata.ivert is 0:
                        x=0.5*(x[:-1,:]+x[1:,:])
                        y=0.5*(y[:-1,:]+y[1:,:])
                    else:
                        #x=x[:,1:]
                        #y=y[:,1:]
                        x=0.5*(x[:,:-1]+x[:,1:])
                        y=0.5*(y[:,:-1]+y[:,1:])
                print x.shape
                print y.shape
                print z.shape
            self.cs=self.axes.contour(x,y,z,colors='k')
            
            self.cs.clabel()
        self.axes.hold(False)       


