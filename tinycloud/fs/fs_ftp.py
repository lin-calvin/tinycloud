import ftplib
import utils
import io
import os
from dateutil import parser


class FsFtp:
    def __init__(self, host, user="", passwd="", port=21):
        self.connection = ftplib.FTP()
        self.connection.connect(host, port)
        if user != "":
            self.connection.login(user, passwd)
        else:
            self.connection.login()

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
    def isdir(self, path):
        res = []
        self.connection.mlsd(os.path.dirname(path), res.append)
        for i in res:
            if i[0]==os.path.split(path)[-1]:
                return i[1]["type"]=="dir"
PROVIDE = {"fs": FsFtp}
