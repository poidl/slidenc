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
import slidenc.data_plot as dp

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
        else:
            layout= QtWidgets.QVBoxLayout()

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
        self.mylcd2 = QtWidgets.QLCDNumber()
        self.mylcd2.setSegmentStyle(2)
        self.myslider = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        layout=QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.mylabel)
        layout.addWidget(self.mylcd)
        layout.addWidget(self.mylcd2)
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

    def setdisplay(self,myax,ii):
        self.sliderlist[ii].mylcd.display(myax.sl_inds[ii])
        self.sliderlist[ii].mylcd2.display(myax.dim_vals[myax.perm[ii]][myax.sl_inds[ii]])

    def setsliders(self,myax):
            for ii in self.sliderlist: ii.hide()
            for ii in range(myax.ndims-2):
                tmp=myax.get_dim(ii)
                self.sliderlist[ii].myslider.setMinimum(0)
                self.sliderlist[ii].myslider.setMaximum(int(tmp)-1)
                self.sliderlist[ii].myslider.setValue(0)
                self.setdisplay(myax,ii)
                self.sliderlist[ii].mylabel.setText(myax.get_dimname(ii))
                self.sliderlist[ii].show()

    def disconnect_all(self):
        for ii in self.sliderlist:
            try: ii.myslider.valueChanged.disconnect()
            except: pass


class MainWidget(QtWidgets.QWidget):
    def __init__(self,myax):
        QtWidgets.QWidget.__init__(self)

        self.popup=MyPopup(myax,dp.ndims_max,parent=self)
        #self.popup.setParent(self)

        self.canvas=dp.MyStaticMplCanvas(myax)
        self.c=Communicate()

        self.buttons_horz=button_box(True,dp.ndims_max)
        self.buttons_vert=button_box(False,dp.ndims_max)


        self.grpbox_contourf=QtWidgets.QGroupBox('Plot type',self)
        self.grpbox_contourf.setLayout(QtWidgets.QHBoxLayout())
        self.grpbox_contourf.setCheckable(True)
        self.grpbox_contourf.setChecked(False)
        self.combo1 = QtWidgets.QComboBox(self)
        self.grpbox_contourf.layout().addWidget(self.combo1)

        self.grpbox_contour=QtWidgets.QGroupBox('Show contours',self)
        self.grpbox_contour.setCheckable(True)
        self.grpbox_contour.setChecked(False)
        self.combo2 = QtWidgets.QComboBox(self)
        self.grpbox_contour.setLayout(QtWidgets.QHBoxLayout())
        self.grpbox_contour.layout().addWidget(self.combo2)

#        self.grpbox_axis=QtWidgets.QGroupBox('Vertical axis',self)
#        self.grpbox_axis.setLayout(QtWidgets.QHBoxLayout())
#        self.combo3 = QtWidgets.QComboBox(self)
#        self.grpbox_axis.layout().addWidget(self.combo3)
#        sublayout_axispicker = QtWidgets.QHBoxLayout()
#        sublayout_axispicker.addWidget(self.grpbox_axis)


        sublayout_varpicker = QtWidgets.QHBoxLayout()
        sublayout_varpicker.addWidget(self.grpbox_contourf)
        sublayout_varpicker.addWidget(self.grpbox_contour)

        layout_upper = QtWidgets.QGridLayout()
        layout_upper.addWidget(self.buttons_vert,0,0)
        layout_upper.addWidget(self.canvas,0,1)
        layout_upper.addWidget(self.buttons_horz,1,1,QtCore.Qt.AlignHCenter)
        layout_upper.setSpacing(0)

        self.sliderbox=slider_box(dp.ndims_max)

        layout_lower=QtWidgets.QVBoxLayout()
        layout_lower.addWidget(self.sliderbox)
#        layout_lower.addLayout(sublayout_axispicker)
        layout_lower.addLayout(sublayout_varpicker)

        layout_main = QtWidgets.QVBoxLayout(self)
        layout_main.addLayout(layout_upper)
        layout_main.addLayout(layout_lower)

        self.combo1.activated[str].connect(self.pick_cf_var)
        self.grpbox_contourf.toggled.connect(self.toggle_plot_type)
        self.grpbox_contour.toggled.connect(self.toggle_contours)
        self.combo2.activated[str].connect(self.pick_c_var)
        self.buttons_horz.modeGroup.buttonClicked[int].connect(self.slot_buttons_horz)
        self.buttons_vert.modeGroup.buttonClicked[int].connect(self.slot_buttons_vert)

        self.destroyed.connect(self.popup.destroy)
#########
        self.c.signal.connect(self.popup.slot_doit)
        self.popup.modeGroup1.buttonClicked[int].connect(self.slot_flip)
        for bbox in self.popup.modeGroup2_list:
            bbox.buttonClicked[int].connect(self.slot_setCoords)

    def showpop(self):
        self.popup.show()
#########


    def pick_cf_var(self,varname):
        # arrange sliders, buttons and contour variables
        self.renew_ax(varname)
        self.canvas.pdata.cf_str=str(varname)
        #self.canvas.pdata.c_str=str(varname)
        self.canvas.pdata.update()
        self.canvas.update_figure()

    def pick_c_var(self,varname):
        self.canvas.pdata.c_str=str(varname)
        self.canvas.pdata.update_c()
        self.canvas.update_figure()

    def toggle_plot_type(self,on):
        if on == False:
            self.canvas.pdata.plot_type="contourf"
        else:
            self.canvas.pdata.plot_type="pcolormesh"
        self.canvas.pdata.update_c()
        self.canvas.update_figure()

    def toggle_contours(self,on):
        if on == True:
            self.canvas.pdata.show_contours=True
        else:
            self.canvas.pdata.show_contours=False
        self.canvas.pdata.update_c()
        self.canvas.update_figure()

    def slider_moved(self,index,ii):
        myax=self.canvas.pdata.myax
        myax.sl_inds[ii]=index
        self.sliderbox.setdisplay(myax, ii)
        self.canvas.pdata.update()
        self.canvas.update_figure()

    def slot_buttons_horz(self,idnr):
        myax=self.canvas.pdata.myax
        myax.permute(myax.ndims-1,idnr)
        self.canvas.pdata.update()
        self.canvas.update_figure()
        self.sliderbox.setsliders(myax)
        self.buttons_vert.update_txt(myax)

    def slot_buttons_vert(self,idnr):
        myax=self.canvas.pdata.myax
        goof=myax.dim_names.index(self.buttons_vert.buttonlist[idnr].text().replace('&',''))
        myax.permute(myax.ndims-2,goof)
        self.canvas.pdata.update()
        self.canvas.update_figure()
        self.sliderbox.setsliders(myax)


    def setcombo1(self):
        self.combo1.clear()
        varlist=self.canvas.pdata.myax.keys_2d_variables()
        self.combo1.addItems(varlist)

    def setcombo2(self):
        myax=self.canvas.pdata.myax
        self.combo2.clear()
        dn=myax.dim_names
        varlist=myax.get_combo2_vars(dn)
        self.combo2.addItems(varlist)
        self.canvas.pdata.c_str=varlist[0]

    def vertaxChoice(self):
        myax=self.canvas.pdata.myax
        if myax.vertaxEnableChoices=='True':
            pass


    def renew_ax(self,varname):
        myax=self.canvas.pdata.myax
        myax.setax(str(varname))
            # set and connect sliders
        self.sliderbox.disconnect_all()
        self.sliderbox.setsliders(myax)
        for ii in range(len(myax.sl_inds)):
            self.sliderbox.sliderlist[ii].myslider.valueChanged.connect(fpartial(self.slider_moved,ii=ii))
        self.buttons_horz.setbuttons(True,myax)
        self.buttons_vert.setbuttons(False,myax)
        self.setcombo2()
        self.vertaxChoice()
        self.c.signal.emit()

    def slot_flip(self,idnr):
        myax=self.canvas.pdata.myax
        myax.flip[idnr] = not myax.flip[idnr]
        self.canvas.pdata.update()
        self.canvas.update_figure()

    def slot_setCoords(self,idnr):
        myax=self.canvas.pdata.myax
        line=int(idnr/2)
        col=idnr%2
        myax.coords[line]=['dim','grd'][col]
        self.canvas.pdata.update()
        self.canvas.update_figure()

class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal()

class MyPopup(QtWidgets.QWidget):
    def __init__(self,myax,ndims_max,parent=None):
        QtWidgets.QWidget.__init__(self)
        self.myax=myax

        self.box1=QtWidgets.QGroupBox('Flip dimension')

        self.buttonlist1=[]
        inds=range(ndims_max)
        for ii in inds:
            self.buttonlist1.append(QtWidgets.QCheckBox(self))
            self.buttonlist1[-1].setCheckable(True)

        layout1= QtWidgets.QVBoxLayout(self)

        self.modeGroup1=QtWidgets.QButtonGroup(self)
        self.modeGroup1.setExclusive(False)

        for ii in self.buttonlist1:
            layout1.addWidget(ii)
            self.modeGroup1.addButton(ii)

        self.box1.setLayout(layout1)

        #self.box1.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
        #                           QtWidgets.QSizePolicy.Maximum)
        #layout.setContentsMargins(0,0,0,0)
        for ii in self.buttonlist1: ii.hide()


############################
        self.box2=QtWidgets.QGroupBox('Coordinates')
        self.buttonlist2=[]
        # maximum number of transformations per dimension
        ntrans_max=3
        inds=range(ndims_max*ntrans_max)
        for ii in inds:
            self.buttonlist2.append(QtWidgets.QCheckBox(self))
            self.buttonlist2[-1].setCheckable(True)

        layout2= QtWidgets.QGridLayout()
        # each element of this list is a buttongroup.
        # one buttongroup for each dimension
        self.modeGroup2_list=[]
        inds=range(ndims_max)
        for ii in inds:
            self.modeGroup2_list.append(QtWidgets.QButtonGroup(self))
            self.modeGroup2_list[-1].setExclusive(True)
#
        self.labelvert=[]
        self.labelhorz=[]
        for ii in range(ndims_max+1):
            self.labelvert.append(QtWidgets.QLabel(self))
            layout2.addWidget(self.labelvert[-1],ii,0)
        for ii in range(ndims_max):
            self.labelhorz.append(QtWidgets.QLabel())
            layout2.addWidget(self.labelhorz[-1],0,ii+1)

        for ii in range(len(self.buttonlist2)):
            button= self.buttonlist2[ii]
            line=ii/2
            column=ii%2
            layout2.addWidget(button,line+1,column+1)

        for ii in range(ndims_max):
            b1=self.buttonlist2[2*ii]
            b2=self.buttonlist2[2*ii+1]
            self.modeGroup2_list[ii].addButton(b1)
            self.modeGroup2_list[ii].addButton(b2)
            self.modeGroup2_list[ii].setId(b1,2*ii)
            self.modeGroup2_list[ii].setId(b2,2*ii+1)

#
        self.box2.setLayout(layout2)

############################
        #grid = QtWidgets.QGridLayout(self)
        #grid.addWidget(self.box1,0,0)
        #grid.addWidget(self.box2,1,0)

        layout_main = QtWidgets.QVBoxLayout(self)
        layout_main.addWidget(self.box1)
        layout_main.addWidget(self.box2)


    def setbuttons2(self):
        for ii in self.buttonlist2:
            ii.hide()
            ii.setChecked(False)
        for ii in self.labelvert:
            ii.hide()
        for ii in range(self.myax.ndims):
            label=self.labelvert[ii+1]
            label.setText(self.myax.dim_names[ii])
            label.show()
            self.buttonlist2[2*ii].setChecked(True)
            self.buttonlist2[2*ii].show()
            self.buttonlist2[2*ii+1].show()

        strl=['dimension','gridpoints']
        for ii in range(2):
            self.labelhorz[ii].setText(strl[ii])


    def setbuttons1(self):
        for ii in self.buttonlist1:
            ii.hide()
            ii.setChecked(False)
        for ii in range(self.myax.ndims):
            button=self.buttonlist1[ii]
            button.setText(self.myax.dim_names[ii])
            self.modeGroup1.setId(button,ii)
            button.show()

    def slot_doit(self):
        self.setbuttons1()
        self.setbuttons2()
        self.adjustSize()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.myax=dp.myax()
        self.main_widget=MainWidget(self.myax)
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

        axisDialog2 = QtWidgets.QAction(QtGui.QIcon('axis2.png'), 'Transforms2', self)
        axisDialog2.setShortcut('Ctrl+T')
        axisDialog2.setStatusTip('View available coordinate transforms')
        axisDialog2.triggered.connect(self.showAxisDialog)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(reloadFile)
        fileMenu.addAction(exitAction)
        axisMenu = menubar.addMenu('&Axis')
        axisMenu.addAction(axisDialog2)
        # start from command line with filename as argument
        if len(sys.argv)>1:
            self.openfile(sys.argv[1])

        # choose nc file for debugging
        debug=0
        if debug:
            ncfile='/ubuntu10.4_home/stefan/arbeit/him/run15/saves/save1.00e00.376.195.nc'
            ncfile='/ubuntu10.4_home/stefan/arbeit/him/run16/saves/save1.00e00.376.195.nc'

            #ncfile='/home/stefan/arbeit/data/WOA09/salinity_annual_1deg.nc'
            self.openfile(ncfile)

    def fileQuit(self):
        self.close()

    def openfile(self,arg):
        self.main_widget.canvas.pdata.myax.open(arg)
        self.main_widget.setcombo1()
        self.main_widget.pick_cf_var(self.main_widget.canvas.pdata.myax.keys_2d_variables()[0])

    def fileReload(self):
        fname=self.main_widget.canvas.pdata.myax.fname()
        self.openfile(fname)

    def showDialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                '/home')
        self.openfile(fname)

    def showAxisDialog(self):
        self.main_widget.showpop()

    def closeEvent(self, ce):
        self.fileQuit()


def main():
    """Main program"""
    qApp = QtWidgets.QApplication(sys.argv)

    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())

if __name__ == '__main__':
    main()
