import ftplib
import utils
import io
import os
from dateutil import parser
import exceptions

class FsFtp:
    def __init__(self, host, user="", passwd="", port=21):
        self.connection = ftplib.FTP()
        self.connection.connect(host, port)
        if user != "":
            self.connection.login(user, passwd)
        else:
            self.connection.login()
    def error_handler(fn):
        def wrapper(*args):
            print(args)
            try:
                return fn(*args)
            except Exception as e:
                if type(e) in [ConnectionRefusedError,EOFError,BrokenPipeError]:

                    raise exceptions.ResourceTemporarilyUnavailable()

                if type(e)==ftplib.error_perm:
                    raise PermissionError()
                raise e
        return wrapper
    @error_handler
    def list(self, path):
        res = []
        if not self.isdir(path):
            for name in self.connection.mlsd(os.path.dirname(path)):
                if name[0] == os.path.split(path)[-1]:
                    fname = name[0]
                    ftype = name[1]["type"]
                    fsize = name[1]["size"]
                    ftime = int(parser.parse(name[1]["modify"]).strftime("%s"))
                    return [{"name": fname, "time": ftime, "type": ftype}]
        ftpres = self.connection.mlsd(path)
        for f in ftpres:
            fname = f[0]
            ftype = f[1]["type"]
            fsize = f[1]["size"]
            ftime = int(parser.parse(f[1]["modify"]).strftime("%s"))
            res.append({"name": fname, "path": fname, "time": ftime, "type": ftype})
        return res
    @error_handler
    def read(self,path):
        self.connection.voidcmd("TYPE I")
        buffer=self.connection.transfercmd("RETR "+path) 
        def reader():
            with  buffer:
                while 1:
                    data = buffer.recv(8192)
                    if not data:
                        self.connection.voidresp()
                        break
                    yield data
        return reader(),-1
    @error_handler
    def write(self,path,stream,chunk_size="1M"):
        chunk_size=utils.calc_size(chunk_size)
        self.connection.voidcmd("TYPE I")  
        buffer=self.connection.transfercmd("STOR "+path)
        while 1:
            data = stream.read(chunk_size)
            if not data:
                buffer.close()
                break
            buffer.send(data)
        self.connection.voidresp()
    @error_handler
    def mkdir(self,path):
        self.connection.mkd(path)

    @error_handler
    def isdir(self, path):
        if path=="":
            return True
        res = list(self.connection.mlsd("/"+os.path.dirname(path)))
        for i in res:
            if i[0]==os.path.split(path)[-1]:
                return i[1]["type"]=="dir"
PROVIDE = {"fs": FsFtp}
