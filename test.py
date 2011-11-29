from PyQt4 import QtGui, QtCore
import sys, os, random

class button_box_x(QtGui.QGroupBox):
    def __init__(self,title=None,parent=None):
        QtGui.QGroupBox.__init__(self,title,parent)
        #self.connect(parent, QtCore.SIGNAL('data_change'), self.__data_changes) 
        button1=QtGui.QPushButton('hoit',self)
        button1.setCheckable(True)
        button1.setChecked(True)
        button2=QtGui.QPushButton('hoit',self)
        button2.setCheckable(True)
        hbox = QtGui.QHBoxLayout() 
        hbox.addWidget(button1)
        hbox.addWidget(button2)

        self.setLayout(hbox)
          


class ApplicationWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.main_widget = QtGui.QWidget(self)
        l = QtGui.QVBoxLayout(self.main_widget)
        x=button_box_x('yax',self.main_widget)
        l.addWidget(x)
        str='horizontal'
        inds=[0,1,2,3] if str=='horizontal' else [1,2,3]
        print inds
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()
   
qApp = QtGui.QApplication(sys.argv)

aw = ApplicationWindow()
# aw.setWindowTitle("%s" % progname)
aw.show()
sys.exit(qApp.exec_())        
        


#for ii in pr.customVarNames:
#    print ii
#    print pr.custom_var(ii).shape