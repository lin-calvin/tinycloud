import os
import time
from utils import time_as_rfc, calc_size


class FsLocal:
    def __init__(self, path):
        self.path = path

    def isdir(self, path):
        return os.path.isdir(os.path.join(self.path, path))

    def list(self, path="/"):
        res = []
        real_path = os.path.normpath(self.path + "/" + path)
        if os.path.isdir(real_path):
            for file in os.listdir(real_path):
                try:
                    ftype = ["file", "dir"][int(os.path.isdir(real_path + "/" + file))]
                    fsize = os.path.getsize(os.path.join(real_path, file))
                    ftime = os.stat(real_path + "/" + file).st_ctime
                except:
                    ftype = "broken"
                    fsize = 0
                    ftime = 0
                res.append(
                    {
                        "type": ftype,
                        "name": file,
                        "size": fsize,
                        "time": ftime,
                    }
                )
            # ftype="dir"
            # fsize=os.path.getsize(path+"/"+file)
            # res.append({"type":ftype,"name":path,"path":path+"/"})
        else:
            res = self.prop(path)
        return res

    def prop(self, path):
        res = []
        file = self.path + "/" + path
        ftype = ["file", "dir"][int(os.path.isdir(file))]
        fname = file.split("/")[-1]
        fsize = os.path.getsize(file)
        ftime = os.stat(file).st_ctime
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

    def read(self, path):
        filesize = os.path.getsize(os.path.join(self.path, path))
        file = open(os.path.join(self.path, path), "rb")
        return file, filesize

    def write(self, path, stream):
        file = open(os.path.join(self.path, path), "wb")
        chunk_size = calc_size("1M")
        while 1:
            data = stream.read(chunk_size)
            if not data:
                file.close()
                break
            file.write(data)

    def delete(self, path):
        os.remove(os.path.join(self.path, path))

    def mkdir(self, path):
        os.mkdir(os.path.join(self.path, path))


PROVIDE = {"fs": FsLocal}
