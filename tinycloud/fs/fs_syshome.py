import os
import time
from utils import *


class fs:
    def __init__(self):
        self.homes={}
        with open('/etc/passwd') as passwd:
            for i in passwd.readlines():
                i=i.split(':')
                self.homes[i[0]]=i[5]
    def get_home(self,user):
        if user in self.homes:
            return self.homes[user]
        return -1

    def list(self, path="/"):
        res = []
        home=self.get_home(username)
        if not os.path.exists(self.path + "/" + path):
            return -1
        if os.path.isdir(self.path + "/" + path):
            path = self.path + "/" + path
            for file in os.listdir(path):
                fname = file
                try:
                    ftype = ["file", "dir"][int(os.path.isdir(path + "/" + file))]
                    fsize = os.path.getsize(path + "/" + file)
                    ftime = time_as_rfc(os.stat(path + "/" + file).st_ctime)
                except:
                    ftype = "dir"
                    fsize = 0
                    ftime = time_as_rfc(0)
                res.append(
                    {
                        "type": ftype,
                        "name": fname,
                        "path": path + "/" + file,
                        "size": fsize,
                        "time": ftime,
                    }
                )
            # ftype="dir"
            # fsize=os.path.getsize(path+"/"+file)
            # res.append({"type":ftype,"name":path,"path":path+"/"})
        else:
            file = path
            fsize = os.path.getsize(file)
            ftype = ["file", "dir"][int(os.path.isdir(file))]
            fname = file.split("/")[-1]
            fsize = os.path.getsize(path + "/" + file)
            ftime = time_as_rfc(os.stat(file).st_ctime)
            res.append(
                {
                    "type": ftype,
                    "name": fname,
                    "path": fname,
                    "size": fsize,
                    "time": ftime,
                }
            )
        return res

    def read(self, path, chunk_size="1M"):
        chunk_size = calc_size(chunk_size)
        if os.path.isfile(self.path + path):
            file = open(self.path + path, "rb")
            while 1:
                data = file.read(chunk_size)
                if not data:
                    break
                yield data
        else:
            return -1

    def write(self, path, stream, chunk_size="1M"):
        file = open(os.path.join(self.path, path), "wb")
        chunk_size = calc_size(chunk_size)
        while 1:
            data = stream.read(chunk_size)
            if not data:
                file.close()
                break
            file.write(data)

    def delete(self, path):
        os.remove(self.path + path)
        return "OK"

    def mkdir(self, path):
        os.mkdir(self.path + path)
        return "OK"
