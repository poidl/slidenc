slidenc wants to become a simple NetCDF viewer, i.e. provide an easy way to 
get an overview of data stored in NetCDF files. 

A typical use case is the testing phase of numerical ocean/
atmosphere/climate models, in which the modeler is interested to get a
broad, qualitative impression of results for a large number of runs
as quick as possible.

Slidenc displays the names of all variables in the NetCDF file and, 
when the user picks a variable, draws a colour-filled 2D contour plot. 
If the variable has more than two dimensions, sliders are provided for 
each additional dimension -- slide n see:)

Dependencies: python, pyqt4, numpy, matplotlib, netCDF4

Usage: 

Start the program by changing into the slidenc folder and typing

	python slidenc.py
	
in a terminal

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
INSTALLING THE DEPENDENCIES
The packages listed below will probably be outdated when you read this. Newer versions may work too. The instructions assume that you have a newly installed operating system without any libraries (such as netcdf, python etc.) installed.

UBUNTU 12.04:

	sudo apt-get install python-numpy python-dev build-essential
	wget http://www.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.8.12.tar.gz
	tar -xzf hdf5-1.8.12.tar.gz ; cd hdf5-1.8.12
	./configure --prefix=/usr/local --enable-shared --enable-hl; make; sudo make install; cd ..
	sudo ldconfig
	wget ftp://ftp.unidata.ucar.edu/pub/netcdf/netcdf-4.3.0.tar.gz
	tar -xzf netcdf-4.3.0.tar.gz ;cd netcdf-4.3.0
	./configure --enable-netcdf-4 --enable-dap --enable-shared --prefix=/usr/local; make check; sudo make install; cd ..
	sudo ldconfig
	wget http://netcdf4-python.googlecode.com/files/netCDF4-1.0.6.tar.gz
	tar -xzf netCDF4-1.0.6.tar.gz; cd netCDF4-1.0.6
	sudo python setup.py install; cd ..
	sudo apt-get install libpng12-dev libfreetype6-dev python-pip
	sudo pip install pyparsing
	wget https://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.3.1/matplotlib-1.3.1.tar.gz
	tar -xzf matplotlib-1.3.1.tar.gz ;cd matplotlib-1.3.1
	python setup.py build
	sudo python setup.py install; cd ..
	sudo apt-get install python-qt4

WINDOWS 7:
Install python(x,y) 2.7.5.0. During the installation, select netcdf4-python as an additional component to install.

MAC OS X 10.8:
install macports 2.2.1 (check http://www.macports.org/install.php)

	sudo port install py27-ipython
	sudo port install py27-matplotlib
	sudo port install py27-pyqt4
	sudo port install py27-netcdf4
	sudo port select --set python python27
	sudo port select --set ipython ipython27

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CREATING EXECUTABLES (read this only if you want to create binary files for distribution)

The executables on [my hompage](http://www.hoitaus.com/drupal/?q=modelling_tools) are bundled with Pyinstaller (all platforms). 
If I understood the license text correctly, I’m required to provide instructions for how to create the exacutables from the source code. 
So here it is:

	wget https://pypi.python.org/packages/source/P/PyInstaller/PyInstaller-2.1.tar.gz
	
Change into the extracted directory and run

	python pyinstaller.py --onefile PATH/TO/SLIDENC/slidenc.PY
	
This will create a directory slidenc with a .spec file. Open the file and change hiddenimports=[] to hiddenimports=['netCDF4_utils','netcdftime']. Delete the ‘dist’ and ‘build’ directories and run

	python pyinstaller.py slidenc/slidenc.spec

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Good luck!

Stefan Riha  hoitaus@gmail.com



[![githalytics.com alpha](https://cruel-carlota.gopagoda.com/f60ca5536d195730c668b881179841b4 "githalytics.com")](http://githalytics.com/poidl/slidenc)




