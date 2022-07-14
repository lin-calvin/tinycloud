from mod_manger import mod_manger as mm
class fs():
    def __init__(self):
        self.mount_table={}
    def mount(self,module,path,args):
        """
            mount(module,mount point,args for module)
        """
        try:
            fsmod=getattr(mm,module)
        except:
            print("err")
        self.mount_table[path]=fsmod.fs(**args)
        print("Mount {} on {} success".format(module,path))
    def get_fs(self,path):
        for mount_point in self.mount_table:
            if mount_point==path[:len(mount_point)]:
                return mount_point
        return -1
    def list(self,path):
        if path=="/" or path=="":
            res=[]
            for a in self.mount_table:
                res.append({"type":"dir","name":a,"path":a,"size":4000})
            return res
        if path.startswith("/"):
            path=path[1:]
        mount_point=self.get_fs(path)
        if mount_point==-1:
            return -1
        return self.mount_table[mount_point].list(path[len(mount_point):])
    def read(self,path):
        mount_point=self.get_fs(path)
        if mount_point==-1:
            return -1
        return self.mount_table[mount_point].read(path[len(mount_point):])
    def mkdir(self,path):
        mount_point=self.get_fs(path)
        if mount_point==-1:
            return -1
        return self.mount_table[mount_point].mkdir(path[len(mount_point):])
    def write(self,path,data):
        mount_point=self.get_fs(path)
        if mount_point==-1:
            return -1
        return self.mount_table[mount_point].write(path[len(mount_point):],data)
    def delete(self,path):
        mount_point=self.get_fs(path)
        if mount_point==-1:
          return -1
        return self.mount_table[mount_point].delete(path[len(mount_point):])
