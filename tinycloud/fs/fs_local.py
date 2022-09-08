import os
import time
from utils import *


class fs:
    def __init__(self, path):
        self.path = path
    def isdir(self, path):
        return os.path.isdir(os.path.join(self.path, path))

    def list(self, path="/"):
        res = []
        real_path=os.path.normpath(self.path +"/"+path)
        if os.path.isdir(real_path):
            for file in os.listdir(real_path):
                try:
                    ftype = ["file", "dir"][int(os.path.isdir(path + "/" + file))]
                    fsize = os.path.getsize(os.path.join(real_path, file))
                    ftime = time_as_rfc(os.stat(real_path + "/" + file).st_ctime)
                except:
                    ftype = "broken"
                    fsize = 0
                    ftime = time_as_rfc(0)
                res.append(
                    {
                        "type": ftype,
                        "name": file,
                        "path": os.path.join(real_path,file),
                        "size": fsize,
                        "time": ftime,
                    }
                )
            # ftype="dir"
            # fsize=os.path.getsize(path+"/"+file)
            # res.append({"type":ftype,"name":path,"path":path+"/"})
        else:
            file = real_path
            ftype = ["file", "dir"][int(os.path.isdir(file))]
            fname = file.split("/")[-1]
            fsize = os.path.getsize(real_path)
            ftime = time_as_rfc(os.stat(real_path).st_ctime)
            res.append(
                {
                    "type": ftype,
                    "name": fname,
                    "path": path,
                    "size": fsize,
                    "time": ftime,
                }
            )
        return res
    def read(self, path, chunk_size="1M"):
        chunk_size = calc_size(chunk_size)
        if os.path.getsize(os.path.join(self.path, path)) < chunk_size:
            chunk_size = os.path.getsize(os.path.join(self.path, path))

        def reader():
            while 1:
                data = file.read(chunk_size)
                if not data:
                    break
                yield data

        if os.path.isfile(os.path.join(self.path, path)):
            file = open(os.path.join(self.path, path), "rb")
            return reader(), os.path.getsize(os.path.join(self.path, path))
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
        os.remove(os.path.join(self.path, path))
        return "OK"

    def mkdir(self, path):
        os.mkdir(os.path.join(self.path, path))
        return "OK"


PROVIDE = {"fs": fs}
