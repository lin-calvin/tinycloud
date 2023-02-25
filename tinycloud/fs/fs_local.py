import os
import time
from utils import time_as_rfc, calc_size
from aiofile import async_open
import asyncio

class FsLocal:
    def __init__(self, path):
        self.path = path

    async def isdir(self, path):
        return os.path.isdir(os.path.join(self.path, path))

    async def list(self, path="/"):
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

    async def prop(self, path):
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

    async def read(self, path):
        filesize = os.path.getsize(os.path.join(self.path, path))
        file = async_open(os.path.join(self.path, path), "rb")
        await file.file
        return file, filesize

    async def write(self, path, stream):
        file = async_open(os.path.join(self.path, path), "wb")
        chunk_size = calc_size("1M")
        while 1:
            data = await stream.read(chunk_size)
            if not data:
                await file.close()
                break
            await file.write(data)

    def delete(self, path):
        os.remove(os.path.join(self.path, path))

    def mkdir(self, path):
        os.mkdir(os.path.join(self.path, path))


PROVIDE = {"fs": FsLocal}
asyncio.Future
