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
progversion = "0.0"

class myax():
    def __init__(self):
        self.orientation0=['t','z','y','x']
        self.orientation=['t','z','y','x']
        self.indices=[0,0]        
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
        self.indices=[0,0]                   
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
        
        if flag==True: layout= QtGui.QHBoxLayout()
        else: layout= QtGui.QVBoxLayout()
        
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
    
        self.modeGroup=QtGui.QButtonGroup()
        self.modeGroup.setExclusive(True)
        self.modeGroup.addButton(self.button1)
        self.modeGroup.addButton(self.button2)
        self.modeGroup.addButton(self.button3)
        if flag==True: 
            #self.button4=QtGui.QPushButton(self.myax.orientation[inds[3]])
            self.button4=QtGui.QRadioButton(self.myax.orientation[inds[3]])
            self.button4.setCheckable(True)
            layout.addWidget(self.button4)
            self.modeGroup.addButton(self.button4)
            self.button4.setChecked(True)
        else: self.button3.setChecked(True)

        self.setLayout(layout)
        self.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                   QtGui.QSizePolicy.Maximum)
        
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
        #fig = Figure(figsize=(width, height), dpi=dpi)
        fig=Figure()
        self.axes = fig.add_subplot(111)        
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)       
        self.colorbar=fig.colorbar
        
        self.initialize_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        
        #def sizeHint(self):
        #    return QtCore.QSize(700,700)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        
        #FigureCanvas.setPreferredSize(QtCore.QSize(800,800))
        #FigureCanvas.setMaximumSize(int(800), int(800))
        FigureCanvas.updateGeometry(self)

    def initialize_figure(self):
        pass

class MyStaticMplCanvas(MyMplCanvas):     
    def initialize_figure(self):   
        pp1=self.reader.get_var(self.cf_str,self.myax.tup())
        self.a=self.axes.imshow(pp1,interpolation='nearest',origin='lower')
        #if not(np.all(np.isnan(pp1))):
        self.cb=self.colorbar(self.a)
        
    def reset_figure(self):
        #self.figure.delaxes(self.figure.axes[:])     
        pp1=self.reader.get_var(self.cf_str,self.myax.tup())
        if self.flip==True: pp1=np.transpose(pp1);
        self.a=self.axes.imshow(pp1,interpolation='nearest',origin='lower')        
        if self.cb:
            self.figure.delaxes(self.figure.axes[1])
            self.figure.subplots_adjust(right=0.90)  #default right padding
            #if not(np.all(np.isnan(pp1))): 
            self.cb = self.figure.colorbar(self.a)
        #self.draw()            

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
    
    def pick_contourf_var(self,text):
        self.cf_str=str(text)
        self.update_figure()
    def pick_contour_var(self,text):
        self.c_str=str(text)
        self.update_figure()
               
    def toggle_contours(self,on):
        if on == True:
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
        
        reader=pyomReader.reader()
        #reader=romsReader.reader()
                       
        show_contours=False
        canvas = MyStaticMplCanvas(reader,show_contours,self.main_widget, width=5, height=4, dpi=100)
               
        layout_main = QtGui.QVBoxLayout(self.main_widget)             
        
        buttons_horz=button_box(True,canvas.myax)
        buttons_vert=button_box(False,canvas.myax)        
        
        sublayout_slider1 = QtGui.QHBoxLayout()
        label_slider1 = QtGui.QLabel(self)
        label_slider1.setText(canvas.myax.orientation[1]) 
        lcd_slider1 = QtGui.QLCDNumber(self)   
        lcd_slider1.setSegmentStyle(2)            
        slider1 = QtGui.QSlider(QtCore.Qt.Horizontal, self)       
        
        sublayout_slider1.addWidget(label_slider1)
        sublayout_slider1.addWidget(lcd_slider1)
        sublayout_slider1.addWidget(slider1)

        sublayout_slider2 = QtGui.QHBoxLayout() 
        label_slider2 = QtGui.QLabel(self)
        label_slider2.setText(canvas.myax.orientation[0])
        lcd_slider2 = QtGui.QLCDNumber(self)
        lcd_slider2.setSegmentStyle(2)
        slider2 = QtGui.QSlider(QtCore.Qt.Horizontal, self)     
        sublayout_slider2.addWidget(label_slider2)
        sublayout_slider2.addWidget(lcd_slider2)
        sublayout_slider2.addWidget(slider2)                            
                               
        grpbox_contourf=QtGui.QGroupBox('Contour fill',self)
        grpbox_contourf.setLayout(QtGui.QHBoxLayout())
        varlist=reader.get_var_names_4d()
        combo1 = QtGui.QComboBox(self)
        combo1.addItems(varlist)               
        grpbox_contourf.layout().addWidget(combo1) 
                            
        grpbox_contour=QtGui.QGroupBox('Show contours',self) 
        grpbox_contour.setCheckable(True)
        grpbox_contour.setChecked(False)
        combo2 = QtGui.QComboBox(self)
        combo2.addItems(varlist)
        grpbox_contour.setLayout(QtGui.QHBoxLayout())
        grpbox_contour.layout().addWidget(combo2)
        
        #groupbox8=QtGui.QGroupBox(self)
        sublayout_varpicker = QtGui.QHBoxLayout()
        sublayout_varpicker.addWidget(grpbox_contourf)
        sublayout_varpicker.addWidget(grpbox_contour)
        
        layout_upper = QtGui.QGridLayout()
        layout_upper.addWidget(buttons_vert,0,0)
        layout_upper.addWidget(canvas,0,1)
        layout_upper.addWidget(buttons_horz,1,1,QtCore.Qt.AlignHCenter)

        layout_lower=QtGui.QVBoxLayout()
        layout_lower.addLayout(sublayout_slider1)        
        layout_lower.addLayout(sublayout_slider2)
        layout_lower.addLayout(sublayout_varpicker)

        #layout_main.setStretchFactor(canvas,10)
        #layout_main.setStretchFactor(groupbox_big,0.1)
        
        layout_main.addLayout(layout_upper)
        layout_main.addLayout(layout_lower)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
##################################################################
        
        tmp=reader.get_axis(canvas.myax.orientation[1])
        slider1.setMinimum(0)
        slider1.setMaximum(np.size(tmp)-1)
        tmp=reader.get_axis(canvas.myax.orientation[0])
        slider2.setMinimum(0)
        slider2.setMaximum(np.size(tmp)-1)
        
        combo1.activated[str].connect(canvas.pick_contourf_var)
        grpbox_contour.toggled.connect(canvas.toggle_contours)       
        combo2.activated[str].connect(canvas.pick_contour_var)        
        
        def slot_buttons_horz(self):
            canvas.myax.setax(3,str(self.text()))                        
            #print canvas.myax.orientation
            buttons_vert.update_txt(canvas.myax)
            buttons_vert.button3.setChecked(True)
            label_slider1.setText(canvas.myax.orientation[1])
            label_slider2.setText(canvas.myax.orientation[0])
            #myax.indices=[0,0]
            canvas.update_axis()
            slider1.setValue(0)
            slider2.setValue(0)
            tmp=reader.get_axis(canvas.myax.orientation[1])
            slider1.setMinimum(0)
            slider1.setMaximum(np.size(tmp)-1)
            tmp=reader.get_axis(canvas.myax.orientation[0])
            slider2.setMinimum(0)
            slider2.setMaximum(np.size(tmp)-1)
                       
        def slot_buttons_vert(self):
            canvas.myax.setax(2,str(self.text()))            
            label_slider1.setText(canvas.myax.orientation[1])
            label_slider2.setText(canvas.myax.orientation[0])
            #myax.indices=[0,0]            
            canvas.update_axis()
            slider1.setValue(0)
            slider2.setValue(0)
            tmp=reader.get_axis(canvas.myax.orientation[1])
            slider1.setMinimum(0)
            slider1.setMaximum(np.size(tmp)-1)
            tmp=reader.get_axis(canvas.myax.orientation[0])
            slider2.setMinimum(0)
            slider2.setMaximum(np.size(tmp)-1)
            #print canvas.myax.orientation
            #print canvas.myax.tup()
            
        buttons_horz.modeGroup.buttonClicked.connect(slot_buttons_horz)    
        buttons_vert.modeGroup.buttonClicked.connect(slot_buttons_vert) 

        slider1.valueChanged.connect(lcd_slider1.display)
        slider1.valueChanged.connect(fpartial(canvas.slider_moved,active_dim=1)) 
        
        slider2.valueChanged.connect(lcd_slider2.display)
        slider2.valueChanged.connect(fpartial(canvas.slider_moved,active_dim=0))  
        
                            
        
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())

