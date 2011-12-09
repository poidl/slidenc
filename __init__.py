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
from matplotlib.lines import Line2D 
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

class button_box(QtGui.QGroupBox):
    def __init__(self,flag,myax,parent=None):
        QtGui.QGroupBox.__init__(self,parent)
        self.myax=myax  
        inds=range(myax.ndims) if flag==True else range(myax.ndims-1)
        self.buttonlist=[] 
        for ii in inds:
            self.buttonlist.append(QtGui.QRadioButton(self.myax.get_dimname(ii)))
            self.buttonlist[-1].setCheckable(True)
        
        if flag==True: layout= QtGui.QHBoxLayout()
        else: layout= QtGui.QVBoxLayout()
        
        self.modeGroup=QtGui.QButtonGroup()
        self.modeGroup.setExclusive(True)
        
        for ii in self.buttonlist: 
            layout.addWidget(ii)            
            self.modeGroup.addButton(ii)
            self.modeGroup.setId(ii,inds[self.buttonlist.index(ii)])
            
        self.buttonlist[-1].setChecked(True)
        self.setLayout(layout)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        layout.setContentsMargins(0,0,0,0)

        for ii in self.buttonlist: ii.hide()
    def update_txt(self,myax):
        cnt=0 
        for ii in self.buttonlist:
            ii.setText(myax.get_dimname(cnt)); cnt+=1 

class button_box_new(QtGui.QGroupBox):
    def __init__(self,flag,ndims_max,parent=None):
        QtGui.QGroupBox.__init__(self,parent)       
        self.buttonlist=[]
        inds=range(ndims_max) if flag==True else range(ndims_max-1) 
        for ii in inds:
            self.buttonlist.append(QtGui.QRadioButton())
            self.buttonlist[-1].setCheckable(True)
        
        if flag==True: layout= QtGui.QHBoxLayout()
        else: layout= QtGui.QVBoxLayout()
        
        self.modeGroup=QtGui.QButtonGroup()
        self.modeGroup.setExclusive(True)
        
        for ii in self.buttonlist: 
            layout.addWidget(ii)            
            self.modeGroup.addButton(ii)
        
        self.setLayout(layout)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        layout.setContentsMargins(0,0,0,0)

        for ii in self.buttonlist: ii.hide()
        
    def setbuttons(self,flag,myax):
            for ii in self.buttonlist: ii.hide()            
            inds=range(myax.ndims-1,-1,-1) if flag==True else range(myax.ndims-2,-1,-1)  
            for ii in inds:
                self.buttonlist[ii].setText(myax.get_dimname(ii))
                self.modeGroup.setId(self.buttonlist[ii],ii)
                if ii==inds[0]: self.buttonlist[ii].setChecked(True)
                self.buttonlist[ii].show()
    
    def update_txt(self,myax):
        inds=range(myax.ndims-2,-1,-1)  
        for ii in inds:
            self.buttonlist[ii].setText(myax.get_dimname(ii))
            if ii==inds[0]: self.buttonlist[ii].setChecked(True)              
                                    

class myslider(QtGui.QWidget):
    def __init__(self,*args):
        QtGui.QWidget.__init__(self,*args)
        
        self.mylabel = QtGui.QLabel() 
        self.mylcd = QtGui.QLCDNumber()  
        self.mylcd.setSegmentStyle(2)            
        self.myslider = QtGui.QSlider(QtCore.Qt.Horizontal)  
                                      
        layout=QtGui.QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.mylabel)
        layout.addWidget(self.mylcd)
        layout.addWidget(self.myslider)
        layout.setContentsMargins(3,3,3,3)

class slider_box(QtGui.QWidget):
    def __init__(self,ndims_max,*args):
        QtGui.QWidget.__init__(self,*args) 
        self.sliderlist=[] 
        for ii in range(ndims_max):
            sl=myslider()          
            self.sliderlist.append(sl)
            
        layout= QtGui.QVBoxLayout(self)
        for ii in self.sliderlist: 
            layout.addWidget(ii)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        
        for ii in self.sliderlist: ii.hide()            

    def setsliders(self,reader,myax):
            for ii in self.sliderlist: ii.hide()
            for ii in range(myax.ndims-2):
                tmp=len(reader.ff.dimensions[myax.get_dimname(ii)])
                ### using Scientific.IO.NetCDF
                #tmp=reader.ff.dimensions[myax.get_dimname(ii)]
                #if tmp==None: #unlimited dimension
                #    tmp=reader.get_current_time_dimension()
                #    print type(tmp)
                               
                self.sliderlist[ii].myslider.setMinimum(0)
                self.sliderlist[ii].myslider.setMaximum(int(tmp)-1)
                self.sliderlist[ii].myslider.setValue(1)
                self.sliderlist[ii].mylcd.display(myax.indices[ii])
                self.sliderlist[ii].mylabel.setText(myax.get_dimname(ii))
                self.sliderlist[ii].show()
                
    def disconnect_all(self):
        for ii in self.sliderlist:
            try: ii.myslider.valueChanged.disconnect()
            except: pass 
                     
            
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self,reader,show_contours=False,parent=None, width=5, height=4, dpi=100):
        self.reader=reader
        self.cf_str=''
        self.c_str=''
        self.myax=myax_new()
        self.flip=False
        self.show_contours=show_contours
        #fig = Figure(figsize=(width, height), dpi=dpi)
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
        if self.show_contours:
            v1=self.reader.get_var(self.c_str,self.myax.tup())
            if self.flip==True: v1=np.transpose(v1);
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
        if self.show_contours:
            self.ba=self.axes.contour(v1,colors='k')
            self.ba.clabel()
            self.axes.hold(False)
        self.draw()     
        
    def reset_figure(self):
        v=self.reader.get_var(self.cf_str,self.myax.tup())
        if self.flip==True: v=np.transpose(v);
        li= [str(self.myax.dim_names[self.myax.perm[-1]]),
             str(self.myax.dim_names[self.myax.perm[-2]])]
        if 'Interface' in li: vertical='Interface'
        elif 'Layer' in li: vertical='Layer'
        else: vertical='z'
        if vertical is not 'z':       
            try:
                for coll in self.axes.collections:  
                    self.axes.collections.remove(coll)  
            except AttributeError: pass
            e=self.reader.get_var('e',self.myax.tup())
            i1=self.myax.tup().index(slice(None))
            i2=self.myax.tup().index(slice(None),i1+1)
            i_vert=self.myax.dim_names.index(vertical)
            if i1==i_vert: 
                i_vert=0; i2=1
            else: i2=0; i_vert=1
            
            x=np.arange(e.shape[i2])
            x=np.r_[[x]*e.shape[i_vert]]
            if self.cf_str is  'e':
                c=np.ones((e.shape[i2]))
                c=np.r_[[ii*c for ii in range(e.shape[i_vert]-1)]]
                v=c
                if self.flip==True:v=c.transpose()
            #print self.flip
            #l=[0,0]; l[i_vert]=slice(None); 
            #if self.cf_str=='u':
            #    l[i2]=slice(1,-1,None)
            #elif self.cf_str=='v'
            #    v=v[:,:-1]+0.5*np.diff(v,1,axis=1)
            #v=v[tuple(l)]
#                #v=v[:,:-1]+0.5*np.diff(v,1,axis=1)
#           
            #f = sp.interpolate.interp1d(x[0,:], e)           
               
            if self.flip==True:                 
                pc=self.axes.pcolormesh(e,x,v.transpose())
                for ii in range(e.shape[i_vert]):
                    myline=Line2D(e[ii,:],x[ii,:],color='k')    
                    self.axes.add_line(myline)                 
            else:
                pc=self.axes.pcolormesh(x,e,v)
                for ii in range(e.shape[i_vert]):
                    myline=Line2D(x[ii,:],e[ii,:],color='k')    
                    self.axes.add_line(myline)    
            self.axes.set_aspect('auto')
            if hasattr(self,'cb'): #remove colorbar
                self.figure.delaxes(self.figure.axes[1])
                self.figure.subplots_adjust(right=0.90)  #default right padding
            self.cb = self.figure.colorbar(pc)
            
   #################################################             
                 
#                patches = []
#                for ii in range(v.shape[0]-1):
#                    p1=np.array([np.arange(v.shape[1]),v[ii]])
#                    p2=np.array([np.arange(v.shape[1]),v[ii+1]])
#                    p2=p2[:,-1::-1]
#                    pp=np.c_[p1,p2].transpose()
#                    poly=ptch.Polygon(pp)
#                    patches.append(poly)                
#                p = PatchCollection(patches, cmap=mpl.cm.jet , alpha=0.4)
#                colors = range(len(patches))  
#                p.set_array(np.array(colors))
#                self.axes.add_collection(p)
#                self.axes.set_xlim([min(pp[:,0]),max(pp[:,0]) ])
#                self.axes.set_ylim([min(pp[:,1]),max(pp[:,1]) ])
#                self.axes.set_aspect('auto')
                
#                if hasattr(self,'cb'): #remove colorbar
#                    self.figure.delaxes(self.figure.axes[1])
#                    self.figure.subplots_adjust(right=0.90)  #default right padding
#                self.cb = self.figure.colorbar(p)
                #self.draw()
        else:              
            #self.a=self.axes.imshow(v,interpolation='nearest',origin='lower')
            self.a=self.axes.contourf(v) 
            self.axes.set_aspect('auto')       
            if hasattr(self,'cb'):
                self.figure.delaxes(self.figure.axes[1])
                self.figure.subplots_adjust(right=0.90)  #default right padding
            self.cb = self.figure.colorbar(self.a)
        self.reset_contour()           

#    def update_imshow(self): 
#        #print self.cf_str
#        #print self.myax.tup()
#        v=self.reader.get_var(self.cf_str,self.myax.tup())
#        if self.flip==True: v=np.transpose(v);  
#        if hasattr(self,'a'): 
#            self.a.set_data(v)
#        else: self.a=self.axes.imshow(v,interpolation='nearest',origin='lower')        
#                    
#        self.a.set_clim(vmin=np.nanmin(v),vmax=np.nanmax(v))
#        if not hasattr(self,'cb'): self.cb = self.figure.colorbar(self.a)
#        self.draw()             
        
    def update_figure(self):
        tmp=self.myax.perm[-2:] 
        self.flip=True if tmp[0]>tmp[1] else False
        self.reset_figure()
        
    def pick_contour_var(self,text):
        self.c_str=str(text)
        self.update_figure()
               
    def toggle_contours(self,on):
        if on == True:
            self.show_contours=True
        else: 
            self.show_contours=False
        if self.c_str: self.update_figure()
    
    def slider_moved(self,index,active_dim):
        self.myax.indices[active_dim]=index  
        self.update_figure()

class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.main_widget = QtGui.QWidget(self)
        
        reader=pyomReader.reader()                    
        show_contours=False
        canvas = MyStaticMplCanvas(reader,show_contours,self.main_widget, width=5, height=4, dpi=100)
                                            
        buttons_horz=button_box_new(True,ndims_max)
        buttons_vert=button_box_new(False,ndims_max)                                                   
                               
        grpbox_contourf=QtGui.QGroupBox('Contour fill',self)
        grpbox_contourf.setLayout(QtGui.QHBoxLayout())
        varlist=reader.ff.variables.keys() 
        combo1 = QtGui.QComboBox(self)
        combo1.addItems(varlist)               
        grpbox_contourf.layout().addWidget(combo1) 
                            
        grpbox_contour=QtGui.QGroupBox('Show contours',self) 
        grpbox_contour.setCheckable(True)
        grpbox_contour.setChecked(False)
        combo2 = QtGui.QComboBox(self)
        grpbox_contour.setLayout(QtGui.QHBoxLayout())
        grpbox_contour.layout().addWidget(combo2)

        sublayout_varpicker = QtGui.QHBoxLayout()
        sublayout_varpicker.addWidget(grpbox_contourf)
        sublayout_varpicker.addWidget(grpbox_contour)
        
        layout_upper = QtGui.QGridLayout()
        layout_upper.addWidget(buttons_vert,0,0)
        layout_upper.addWidget(canvas,0,1)
        layout_upper.addWidget(buttons_horz,1,1,QtCore.Qt.AlignHCenter)
        layout_upper.setSpacing(0)

        sliderbox=slider_box(ndims_max)
        
        layout_lower=QtGui.QVBoxLayout()
        layout_lower.addWidget(sliderbox)        
        layout_lower.addLayout(sublayout_varpicker)
        
        layout_main = QtGui.QVBoxLayout(self.main_widget)
        
        layout_main.addLayout(layout_upper)
        layout_main.addLayout(layout_lower)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
##################################################################   
     
        def slot_buttons_horz(idnr):
            canvas.myax.permute(canvas.myax.ndims-1,idnr)
            canvas.update_figure()                      
            buttons_vert.update_txt(canvas.myax)
            sliderbox.setsliders(reader,canvas.myax)           
                       
        def slot_buttons_vert(idnr):
            goof=canvas.myax.dim_names.index(buttons_vert.buttonlist[idnr].text())           
            canvas.myax.permute(canvas.myax.ndims-2,goof)
            canvas.update_figure()         
            sliderbox.setsliders(reader,canvas.myax)            

        def connect_sliders(sliderbox,myax,reader):
            for ii in range(len(myax.indices)):    
                sliderbox.sliderlist[ii].myslider.valueChanged.connect(sliderbox.sliderlist[ii].mylcd.display)
                sliderbox.sliderlist[ii].myslider.valueChanged.connect(fpartial(canvas.slider_moved,active_dim=ii))        
        def setcombo2():
            combo2.clear()
            dn=canvas.myax.dim_names
            varlist=reader.get_combo2_vars(dn)
            combo2.addItems(varlist)
            canvas.c_str=varlist[0]
        
           
        def pick_cf_var(text):
            canvas.myax.setax(reader,str(text))
            if canvas.myax.ndims>1:
                canvas.cf_str=str(text)
                sliderbox.disconnect_all()
                sliderbox.setsliders(reader,canvas.myax)
                connect_sliders(sliderbox,canvas.myax,reader)            
                

                buttons_horz.setbuttons(True,canvas.myax)
                buttons_vert.setbuttons(False,canvas.myax)                
                setcombo2()
                canvas.update_figure()
            else: print 'cannot contour a 1-d variable'  
            
        combo1.activated[str].connect(pick_cf_var)
        grpbox_contour.toggled.connect(canvas.toggle_contours)       
        combo2.activated[str].connect(canvas.pick_contour_var)  
             
        buttons_horz.modeGroup.buttonClicked[int].connect(slot_buttons_horz)    
        buttons_vert.modeGroup.buttonClicked[int].connect(slot_buttons_vert)

 
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())

