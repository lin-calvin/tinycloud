import os
class fs():
    def __init__(self,mod_manger):
        self.mm=mod_manger
        self.mount_table={}
    def mount(self,module,path,args):
        """
            mount(module,mount point,args for module)
        """
        try:
            fsmod=getattr(self.mm,module)
        except:
            print("err")
        self.mount_table[path]=fsmod.fs(**args)
        print("Mount {} on {} success".format(module,path))
    def get_fs(self,path):
        for mount_point in self.mount_table:
            p=list(filter(('').__ne__,path.split('/')))
            if mount_point==p[0]:
                return self.mount_table[p[0]],'/'.join(p[1:])
        return -1
    def list(self,path):
        if path=="/" or path=="":
            res=[]
            for a in self.mount_table:
                res.append({"type":"dir","name":a,"path":a,"size":4000})
            return res
        if path.startswith("/"):
            path=path[1:]
        fs,p=self.get_fs(path)
        if fs==-1:
            return -1
        return fs.list(p)
    def read(self,path):
        fs,path=self.get_fs(path)
        if fs==-1:
            return -1
        return fs.read(path)
    def mkdir(self,path):
        fs,path=self.get_fs(path)
        if fs==-1:
            return -1
        return fs.mkdir(path)
    def write(self,path,data):
        fs,path=self.get_fs(path)
        if fs==-1:
            return -1
        return fs.write(path,data)
    def delete(self,path):
        fs,path=self.get_fs(path)
        if fs==-1:
          return -1
        return fs.delete(path)
