import os
import shutil
import time
from utils import *


class fs:
    def __init__(self):
        self.homes = {}
        with open("/etc/passwd") as passwd:
            for i in passwd.readlines():
                i = i.split(":")
                self.homes[i[0]] = i[5]

    def get_home(self, user):
        if user in self.homes:
            return self.homes[user]
        raise FileNotFoundError

    def isdir(self, path):
        home = self.get_home(fs_context.username)
        path = os.path.join(home, path)
        return os.path.isdir(path)

    def list(self, path="/"):
        res = []
        home = self.get_home(fs_context.username)
        real_path = home + "/" + path
        if os.path.isdir(home + "/" + path):
            for file in os.listdir(real_path):
                fname = file
                try:
                    ftype = ["file", "dir"][int(os.path.isdir(real_path + "/" + file))]
                    fsize = os.path.getsize(real_path + "/" + file)
                    ftime = time_as_rfc(os.stat(real_path + "/" + file).st_ctime)
                except:
                    ftype = "broken"
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
            file = real_path
            fsize = os.path.getsize(file)
            ftype = ["file", "dir"][int(os.path.isdir(file))]
            fname = file.split("/")[-1]
            fsize = os.path.getsize(file)
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
        home = self.get_home(fs_context.username)
        chunk_size = calc_size(chunk_size)
        if os.path.getsize(os.path.join(home, path)) < chunk_size:
            chunk_size = os.path.getsize(os.path.join(home, path))

        def reader():
            while 1:
                data = file.read(chunk_size)
                if not data:
                    break
                yield data

        if os.path.isfile(os.path.join(home, path)):
            file = open(os.path.join(home, path), "rb")
            return reader(), os.path.getsize(os.path.join(home, path))
        else:
            return -1

    def write(self, path, stream, chunk_size="1M"):
        home = self.get_home(fs_context.username)
        if home == -1:
            return -1
        filename = os.path.join(home, path)
        file = open(filename, "wb")
        shutil.chown(filename, user=fs_context.username)
        chunk_size = calc_size(chunk_size)
        while 1:
            data = stream.read(chunk_size)
            if not data:
                file.close()
                break
            file.write(data)

    def delete(self, path):
        home = self.get_home(fs_context.username)
        if home == -1:
            return -1
        os.remove(os.path.join(home, path))
        return "OK"

    def mkdir(self, path):
        home = self.get_home(fs_context.username)
        if home == -1:
            return -1
        os.mkdir(os.path.join(home, path))
        return "OK"


PROVIDE = {"fs": fs}
