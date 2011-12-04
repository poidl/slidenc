
class myax_new():
    def __init__(self):
        self.dim_names=['t','z','y','x']
        self.perm=range(len(self.dim_names))        
        self.indices_ini=[1]*(len(self.dim_names)-2) 
        self.indices=self.indices_ini[:]
        
    def permute(self,ind,val):
        tmp=self.perm[:]
        self.perm[ind]=val
        self.perm[tmp.index(val)]=ind
        self.perm[:ind]=sorted(self.perm[:ind])
        
    def get_dimname(self,ind):
        return self.dim_names[self.perm[ind]]
    
    def tup(self):
        li=[]; cnt=0
        for ii in range(len(self.dim_names)):
            li.append('')   
        for ii in range(len(self.dim_names)):
            if self.perm.index(ii)>len(self.dim_names)-3:
                li[ii]=slice(None)
            else: li[ii]=self.indices[cnt];  cnt+=1 
        return tuple(li) 

ax=myax_new()
print ax.perm
ax.permute(3,2)
print ax.perm
ax.permute(3,3)
print ax.perm


