import ftplib
import utils
import io
import os
from dateutil import parser
class fs():
    def __init__(self,host,user="",passwd="",port=22):
        self.connection=ftplib.FTP()
        self.connection.connect(host,port)
        if user!="":
            self.connection.login(user,passwd)
        else:
            self.connection.login()
    def list(self,path):
        res=[]
        ftpres=self.connection.mlsd("")
        if self.isfile(path):
            print(1)
            for name in self.connection.mlsd(os.path.dirname(path)):
                if name[0]==os.path.split(path)[-1]:
                    fname=name[0]
                    ftype=name[1]["type"]
                    fsize=name[1]["size"]
                    ftime=utils.time_as_rfc(int(parser.parse(name[1]["modify"]).strftime("%s")))
                    return {"name":fname,"path":fname,"time":ftime,"type":ftype}
        for f in ftpres:
            fname=f[0]
            ftype=f[1]["type"]
            fsize=f[1]["size"]
            ftime=utils.time_as_rfc(int(parser.parse(f[1]["modify"]).strftime("%s")))
            res.append({"name":fname,"path":fname,"time":ftime,"type":ftype})
        return res
    def isfile(self,path):
        res=[]
        self.connection.dir(path,res.append)
        return res[0][0]=="-"
