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

Dependencies: python, pyqt5, numpy, matplotlib, netCDF4-python

Usage: 

Start the program by changing into the slidenc folder and typing

	python slidenc.py
	
in a terminal

Stefan Riha  hoitaus@gmail.com
