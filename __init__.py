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
from Scientific.IO.NetCDF import NetCDFFile as NF
import pyomReader
import romsReader

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

class myax():
    def __init__(self):
        self.orientation0=['t','z','y','x']
        self.orientation=['t','z','y','x']
        self.indices=[1,1]        
    def setax(self,ind,string):
        swap=self.orientation[ind]
        oldind=self.orientation.index(string)
        self.orientation[ind]=string
        self.orientation[oldind]=swap
        
        left=self.orientation[:ind]
        tmp=[]
        for ii in left:
            tmp.append([ii,self.orientation0.index(ii)])              
        srt_list= sorted(tmp, key=lambda x: x[1])
        self.orientation[:ind]=[li[0] for li in srt_list]                   
    def tup(self):
        li=['','','','']; cnt=0 
        for ii in range(4):
            varstr=self.orientation0[ii]
            ind=self.orientation.index(varstr)
            if ind>1: li[ii]=slice(None)
            else:     li[ii]=self.indices[cnt];  cnt+=1              
        return tuple(li)    

class button_box(QtGui.QGroupBox):
    def __init__(self,flag,myax,parent=None):
        QtGui.QGroupBox.__init__(self,parent)
        self.myax=myax  
        inds=[0,1,2,3] if flag==True else [0,1,2] 

        self.button1=QtGui.QRadioButton(self.myax.orientation[inds[0]])
        self.button1.setCheckable(True)
        self.button2=QtGui.QRadioButton(self.myax.orientation[inds[1]])
        self.button2.setCheckable(True)
        self.button3=QtGui.QRadioButton(self.myax.orientation[inds[2]])
        self.button3.setCheckable(True)
        
        hbox = QtGui.QHBoxLayout() 
        hbox.addWidget(self.button1)
        hbox.addWidget(self.button2)
        hbox.addWidget(self.button3)
    
        self.modeGroup=QtGui.QButtonGroup()
        self.modeGroup.setExclusive(True)
        self.modeGroup.addButton(self.button1)
        self.modeGroup.addButton(self.button2)
        self.modeGroup.addButton(self.button3)
        if flag==True: 
            #self.button4=QtGui.QPushButton(self.myax.orientation[inds[3]])
            self.button4=QtGui.QRadioButton(self.myax.orientation[inds[3]])
            self.button4.setCheckable(True)
            hbox.addWidget(self.button4)
            self.modeGroup.addButton(self.button4)
            self.button4.setChecked(True)
        else: self.button3.setChecked(True)

        self.setLayout(hbox)
        
    def update_txt(self,myax):
        self.button1.setText(myax.orientation[0])
        self.button2.setText(myax.orientation[1])
        self.button3.setText(myax.orientation[2])
            
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self,reader,show_contours=False,parent=None, width=5, height=4, dpi=100):
        self.reader=reader
        self.cf_str=reader.get_var_names_4d()[0]
        self.c_str=reader.get_var_names_4d()[0]
        self.myax=myax()
        self.flip=False
        self.show_contours=show_contours
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)        
        # We want the axes cleared every time plot() is called
        #self.axes.hold(False)       
        self.colorbar=fig.colorbar
        
        self.initialize_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def initialize_figure(self):
        pass

class MyStaticMplCanvas(MyMplCanvas):     
    def initialize_figure(self):   
        pp1=self.reader.get_var(self.cf_str,self.myax.tup())
        self.a=self.axes.imshow(pp1,interpolation='nearest',origin='lower')
        self.cb=self.colorbar(self.a)
        
    def reset_figure(self):
        #self.figure.delaxes(self.figure.axes[:])     
        pp1=self.reader.get_var(self.cf_str,self.myax.tup())
        if self.flip==True: pp1=np.transpose(pp1);
        self.a=self.axes.imshow(pp1,interpolation='nearest',origin='lower')        
        if self.cb:
            self.figure.delaxes(self.figure.axes[1])
            self.figure.subplots_adjust(right=0.90)  #default right padding
            self.cb = self.figure.colorbar(self.a)
        self.draw()            

    def update_contourf(self):   
        pp1=self.reader.get_var(self.cf_str,self.myax.tup())
        if self.flip==True: pp1=np.transpose(pp1);  
        self.a.set_data(pp1)                    
        self.a.set_clim(vmin=np.nanmin(pp1),vmax=np.nanmax(pp1))
        self.draw() 
    
    def update_contour(self):
        v1=self.reader.get_var(self.c_str,self.myax.tup())
        if self.flip==True: v1=np.transpose(v1);
        if self.show_contours: self.axes.hold(True)        
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
        
    def update_figure(self):
        self.update_contourf()
        self.update_contour()

    def update_axis(self):
        string=self.myax.orientation[2:]
        tmp=[]
        for ii in string:
            tmp.append([ii,self.myax.orientation0.index(ii)])
        self.flip=True if tmp[0]<tmp[1] else False          
        self.reset_figure()
        self.update_contour()
    
    def pick_var(self,text):
        self.cf_str=str(text)
        self.update_figure()
               
    def toggle_contours(self,state):
        if state == QtCore.Qt.Checked:
            self.show_contours=True
        else: 
            self.show_contours=False
        self.update_figure()
    
    def slider_moved(self,index,active_dim): 
        self.myax.indices[active_dim]=index  
        self.update_figure()


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.main_widget = QtGui.QWidget(self)
        
        pr=pyomReader.reader()
        #pr=romsReader.reader()
        
        zt=pr.get_axis('z')
        lcd = QtGui.QLCDNumber(self)               
        sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)       
        sld.setMinimum(0)
        sld.setMaximum(np.size(zt)-1)
        
        time=pr.get_axis('time')
        lcd2 = QtGui.QLCDNumber(self)
        sld2 = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        sld2.setMinimum(0)
        sld2.setMaximum(np.size(time)-1)
               
        show_contours=False
        sc = MyStaticMplCanvas(pr,show_contours,self.main_widget, width=5, height=4, dpi=100)

        varlist=pr.get_var_names_4d()
        combo = QtGui.QComboBox(self)
        combo.addItems(varlist)
               
        combo.activated[str].connect(sc.pick_var)

        cb = QtGui.QCheckBox('Show contour lines', self)
        
        cb.stateChanged.connect(sc.toggle_contours)
               
        l = QtGui.QVBoxLayout(self.main_widget)             
        
        groupbox=button_box(True,sc.myax)
        groupbox_2=button_box(False,sc.myax)        
        
        groupbox3=QtGui.QGroupBox(self)
        hbox3 = QtGui.QHBoxLayout(groupbox3)
        lbl3 = QtGui.QLabel(self)
        lbl3.setText(sc.myax.orientation[0]) 
        hbox3.addWidget(lbl3)
        hbox3.addWidget(lcd) 
        
        groupbox4=QtGui.QGroupBox(self)
        hbox4 = QtGui.QHBoxLayout(groupbox4) 
        lbl4 = QtGui.QLabel(self)
        lbl4.setText(sc.myax.orientation[1])        
        hbox4.addWidget(lbl4)
        hbox4.addWidget(lcd2)  
         
        groupbox5=QtGui.QGroupBox(self) 
        hbox5 = QtGui.QHBoxLayout(groupbox5)
        lbl5 = QtGui.QLabel(self)
        lbl6 = QtGui.QLabel(self)
        lbl5.setText('horz_ax')
        lbl6.setText('vert_ax')
        hbox5.addWidget(lbl5)
        hbox5.addWidget(groupbox)
        hbox5.addWidget(lbl6)
        hbox5.addWidget(groupbox_2)
        
        lbl3.setText(sc.myax.orientation[1])
        lbl4.setText(sc.myax.orientation[0])                   
        
        def doit(self):
            sc.myax.setax(3,str(self.text()))                        
            #print sc.myax.orientation
            groupbox_2.update_txt(sc.myax)
            groupbox_2.button3.setChecked(True)
            lbl3.setText(sc.myax.orientation[1])
            lbl4.setText(sc.myax.orientation[0])
            sc.update_axis()
            print sc.axes
            print sc.colorbar
            #print sc.myax.orientation
            #print sc.myax.tup()
                       
        def doit2(self):
            sc.myax.setax(2,str(self.text()))            
            lbl3.setText(sc.myax.orientation[1])
            lbl4.setText(sc.myax.orientation[0])
            sc.update_axis()
            #print sc.myax.orientation
            #print sc.myax.tup()
                
        groupbox.modeGroup.buttonClicked.connect(doit)    
        groupbox_2.modeGroup.buttonClicked.connect(doit2)    
            
        l.addWidget(sc)
        l.addWidget(groupbox5)
        l.addWidget(groupbox3)        
        l.addWidget(sld)
        l.addWidget(groupbox4)
        l.addWidget(sld2)
        l.addWidget(combo)
        l.addWidget(cb)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        sld.valueChanged.connect(lcd.display)
        sld.valueChanged.connect(fpartial(sc.slider_moved,active_dim=1)) 
        
        sld2.valueChanged.connect(lcd2.display)
        sld2.valueChanged.connect(fpartial(sc.slider_moved,active_dim=0))  
        
                            
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())

