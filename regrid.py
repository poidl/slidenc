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

import numpy as np

class regrid:
    
    def d2(self,var,stag1,stag2):

        def rgrd(var,stag):
            xn,yn=var.shape
            if stag==1: # leave last gridpoint untouched
                var[0:-1,:]=var[0:-1,:]+0.5*np.diff(var,1,0)
            if stag==2:
                var=var[0:-1,:]+0.5*np.diff(var,1,0)
            if stag==-1: # leave first gridpoint untouched
                var[1:,:]=var[0:-1,:]+0.5*np.diff(var,1,0)   
            if stag==-2:
                vi=var[0:-1,:]+0.5*np.diff(var,1,0)
                var=var[np.r_[0,range(0,xn),:]]
                var[1:-1,:]=vi 
            return var

        if stag1!=0:        
            var=rgrd(var,stag1)            
 
        if stag2 != 0:
            var=var.transpose()
            var=rgrd(var,stag2)
            var=var.transpose()

        return var
            

            
#        if stag2==-1: # leave first gridpoint untouched
#            var[:,1:]=var[:,0:-1]+0.5*np.diff(var,1,1)   
#        if stag2==-2:
#            vi=var[:,0:-1]+0.5*np.diff(var,1,1)
#            var=var[:,np.r_[0,range(0,yn)]]
#            var[:,1:-1]=vi
        
    