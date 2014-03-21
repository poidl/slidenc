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

    def reduce(self,var,l,guessed):
        # example: if var.shape is (5,5,2) and l[2] is not slice(None) 
        # then the third dimension is re-gridded to the center, output is of shape (5,5)
        # assumes that every index which is not a slice, is of dimension 2
        
        # `guessed` is nonzero if the indices to be reduced are from the origin or
        # end of a dimension, and the grid is staggered and extrapolated 
        # (see _get_envelope_tup)
        
        ireduce=[ind for ind,item in enumerate(l) if item != slice(None)]
        guessed=[guessed[i] for i in ireduce] 
        
        for i in ireduce:
            l[i]=slice(0,2,None) # 
            
        for i,g in zip(ireduce,guessed):
            
            l1=l[:]
            l2=l[:]
                    
            l1[i]=slice(0,1,None)
            l2[i]=slice(1,2,None)
            
            tup1=tuple(l1)
            tup2=tuple(l2)
            if g==0:
                var=0.5*(var[tup1]+var[tup2])
            elif g==1: # extrapolation at origin
                var=var[tup1]-0.5*(var[tup2]-var[tup1])
                print 'extrap. at origin'
            elif g==2: # extrapolation at end
                print 'extrap. at end'
                var=var[tup2]+0.5*(var[tup2]-var[tup1])
            
            l[i]=slice(0,1,None)    
            
        return var
         
    def reduce_test(self):
        va=np.ones([5,2,5,2])
        l=[slice(None),slice(3,5,None),slice(None),slice(3,5,None)]
        guessed=[0,0,0,0]
        out=self.reduce(va,l,guessed)
        print out.shape
    
    def d2(self,var,stag1,stag2):

        def rgrd(var,stag):
            #raise Exception('this does not make sense if regridding a coordinate in direction of itself')
            xn,yn=var.shape
            if stag==1: # linear interpolation, then append last grid point unmodified
                var[0:-1,:]=var[0:-1,:]+0.5*np.diff(var,1,0)
            if stag==2: # lin. int.
                var=var[0:-1,:]+0.5*np.diff(var,1,0)
            if stag==-1: # lin. int., then append first grid point unmodified
                var[1:,:]=var[0:-1,:]+0.5*np.diff(var,1,0)   
            if stag==-2: # lin. int, then append first and last grid point unmodified
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
        
    