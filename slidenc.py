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

import sys,os
from PyQt5 import QtGui, QtCore, QtWidgets
from functools import partial as fpartial
import data_plot as dp

progname = os.path.basename(sys.argv[0])

progversion = "0.0"

class button_box(QtWidgets.QGroupBox):
    def __init__(self,flag,ndims_max,parent=None):
        QtWidgets.QGroupBox.__init__(self,parent)       
        self.buttonlist=[]
        inds=range(ndims_max) if flag==True else range(ndims_max-1) 
        for ii in inds:
            self.buttonlist.append(QtWidgets.QRadioButton())
            self.buttonlist[-1].setCheckable(True)
        
        if flag==True: layout= QtWidgets.QHBoxLayout()
        else: layout= QtWidgets.QVBoxLayout()
        
        self.modeGroup=QtWidgets.QButtonGroup()
        self.modeGroup.setExclusive(True)
        
        for ii in self.buttonlist: 
            layout.addWidget(ii)            
            self.modeGroup.addButton(ii)
        
        self.setLayout(layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                   QtWidgets.QSizePolicy.Maximum)
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
                                    

class myslider(QtWidgets.QWidget):
    def __init__(self,*args):
        QtWidgets.QWidget.__init__(self,*args)
        
        self.mylabel = QtWidgets.QLabel() 
        self.mylcd = QtWidgets.QLCDNumber()  
        self.mylcd.setSegmentStyle(2)            
        self.myslider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  
                                      
        layout=QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.mylabel)
        layout.addWidget(self.mylcd)
        layout.addWidget(self.myslider)
        layout.setContentsMargins(3,3,3,3)

class slider_box(QtWidgets.QWidget):
    def __init__(self,ndims_max,*args):
        QtWidgets.QWidget.__init__(self,*args) 
        self.sliderlist=[] 
        for ii in range(ndims_max):
            sl=myslider()          
            self.sliderlist.append(sl)
            
        layout= QtWidgets.QVBoxLayout(self)
        for ii in self.sliderlist: 
            layout.addWidget(ii)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        
        for ii in self.sliderlist: ii.hide()            

    def setsliders(self,reader,myax):
            for ii in self.sliderlist: ii.hide()
            for ii in range(myax.ndims-2):
                tmp=len(reader.ff.dimensions[myax.get_dimname(ii)])
                               
                self.sliderlist[ii].myslider.setMinimum(0)
                self.sliderlist[ii].myslider.setMaximum(int(tmp)-1)
                self.sliderlist[ii].myslider.setValue(0)
                self.sliderlist[ii].mylcd.display(myax.sl_inds[ii])
                self.sliderlist[ii].mylabel.setText(myax.get_dimname(ii))
                self.sliderlist[ii].show()
                
    def disconnect_all(self):
        for ii in self.sliderlist:
            try: ii.myslider.valueChanged.disconnect()
            except: pass 
            
            
            
class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.canvas=dp.MyStaticMplCanvas()

        self.buttons_horz=button_box(True,dp.ndims_max)
        self.buttons_vert=button_box(False,dp.ndims_max)                                                   
                               
        grpbox_contourf=QtWidgets.QGroupBox('Contour fill',self)
        grpbox_contourf.setLayout(QtWidgets.QHBoxLayout())

        self.combo1 = QtWidgets.QComboBox(self)
        grpbox_contourf.layout().addWidget(self.combo1)
        
        self.grpbox_contour=QtWidgets.QGroupBox('Show contours',self) 
        self.grpbox_contour.setCheckable(True)
        self.grpbox_contour.setChecked(False)
        self.combo2 = QtWidgets.QComboBox(self)
        self.grpbox_contour.setLayout(QtWidgets.QHBoxLayout())
        self.grpbox_contour.layout().addWidget(self.combo2)
        
        sublayout_varpicker = QtWidgets.QHBoxLayout()
        sublayout_varpicker.addWidget(grpbox_contourf)
        sublayout_varpicker.addWidget(self.grpbox_contour)
        
        layout_upper = QtWidgets.QGridLayout()
        layout_upper.addWidget(self.buttons_vert,0,0)
        layout_upper.addWidget(self.canvas,0,1)
        layout_upper.addWidget(self.buttons_horz,1,1,QtCore.Qt.AlignHCenter)
        layout_upper.setSpacing(0)   
        
        self.sliderbox=slider_box(dp.ndims_max)
        
        layout_lower=QtWidgets.QVBoxLayout()
        layout_lower.addWidget(self.sliderbox)        
        layout_lower.addLayout(sublayout_varpicker)
        
        layout_main = QtWidgets.QVBoxLayout(self)        
        layout_main.addLayout(layout_upper)
        layout_main.addLayout(layout_lower) 

        self.combo1.activated[str].connect(self.pick_cf_var)
        self.grpbox_contour.toggled.connect(self.toggle_contours)       
        self.combo2.activated[str].connect(self.pick_c_var)              
        self.buttons_horz.modeGroup.buttonClicked[int].connect(self.slot_buttons_horz)    
        self.buttons_vert.modeGroup.buttonClicked[int].connect(self.slot_buttons_vert)
    
    def pick_cf_var(self,text):
        # arrange sliders, buttons and contour variables
        self.new_ax(text) 
        self.canvas.pdata.cf_str=str(text)
        self.canvas.pdata.update()
        self.canvas.update_figure()
    
    def pick_c_var(self,text):
        self.canvas.pdata.c_str=str(text)
        self.canvas.pdata.update_c()
        self.canvas.update_figure()
               
    def toggle_contours(self,on):
        if on == True:
            self.canvas.pdata.show_contours=True
        else: 
            self.canvas.pdata.show_contours=False
        self.canvas.pdata.update_c()
        self.canvas.update_figure()
        
    def slider_moved(self,index,active_dim):
        self.canvas.pdata.myax.sl_inds[active_dim]=index
        self.canvas.pdata.update()  
        self.canvas.update_figure()
 
    def slot_buttons_horz(self,idnr):
        self.canvas.pdata.myax.permute(self.canvas.pdata.myax.ndims-1,idnr)
        self.canvas.pdata.update()
        self.canvas.update_figure()                      
        self.sliderbox.setsliders(self.canvas.pdata.reader,self.canvas.pdata.myax)           
        self.buttons_vert.update_txt(self.canvas.pdata.myax) 
                  
    def slot_buttons_vert(self,idnr):
        goof=self.canvas.pdata.myax.dim_names.index(self.buttons_vert.buttonlist[idnr].text() .replace('&', ''))           
        self.canvas.pdata.myax.permute(self.canvas.pdata.myax.ndims-2,goof)
        self.canvas.pdata.update()
        self.canvas.update_figure()         
        self.sliderbox.setsliders(self.canvas.pdata.reader,self.canvas.pdata.myax)            

            
    def setcombo1(self):
        self.combo1.clear()
        varlist=self.canvas.pdata.reader.keys_2d_variables
        self.combo1.addItems(varlist)
    
    def setcombo2(self):
        self.combo2.clear()
        dn=self.canvas.pdata.myax.dim_names
        varlist=self.canvas.pdata.reader.get_combo2_vars(dn)
        self.combo2.addItems(varlist)
        self.canvas.pdata.c_str=varlist[0]
           
    def new_ax(self,text):
        self.canvas.pdata.myax.setax(self.canvas.pdata.reader,str(text))
            # set and connect sliders
        self.sliderbox.disconnect_all()
        self.sliderbox.setsliders(self.canvas.pdata.reader,self.canvas.pdata.myax)
        for ii in range(len(self.canvas.pdata.myax.sl_inds)):    
            self.sliderbox.sliderlist[ii].myslider.valueChanged.connect(self.sliderbox.sliderlist[ii].mylcd.display)
            self.sliderbox.sliderlist[ii].myslider.valueChanged.connect(fpartial(self.slider_moved,active_dim=ii))        
        self.buttons_horz.setbuttons(True,self.canvas.pdata.myax)
        self.buttons_vert.setbuttons(False,self.canvas.pdata.myax)                
        self.setcombo2()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)                               
        self.main_widget=MainWidget()
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
##################################################################   
        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        openFile = QtWidgets.QAction(QtGui.QIcon('open.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)
        
        reloadFile = QtWidgets.QAction(QtGui.QIcon('reload.png'), 'Reload', self)
        reloadFile.setShortcut('Ctrl+R')
        reloadFile.setStatusTip('Reload File')      
        reloadFile.triggered.connect(self.fileReload)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(reloadFile)
        fileMenu.addAction(exitAction)
        
        # start from command line with filename as argument 
        if len(sys.argv)>1:
            self.cmdline_arg(sys.argv[1])
                
        # choose nc file for debugging
        debug=0
        if debug:
            ncfile='/ubuntu10.4_home/stefan/arbeit/him/run15/saves/save1.00e00.376.195.nc'
            self.cmdline_arg(ncfile)
        
    def fileQuit(self):
        self.close()
    
    def fileReload(self):
        fname=self.main_widget.canvas.pdata.reader.fname
        self.cmdline_arg(fname)
    
    def cmdline_arg(self,arg):
        self.main_widget.canvas.pdata.reader.open(arg)
        self.main_widget.setcombo1()
        self.main_widget.pick_cf_var(self.main_widget.canvas.pdata.reader.keys_2d_variables[0])
   
    def showDialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 
                '/home')
        self.main_widget.canvas.pdata.reader.open(fname)
        self.main_widget.setcombo1()
        self.main_widget.pick_cf_var(self.main_widget.canvas.pdata.reader.keys_2d_variables[0])

    def closeEvent(self, ce):
        self.fileQuit()

qApp = QtWidgets.QApplication(sys.argv)

aw = ApplicationWindow()
aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())            
