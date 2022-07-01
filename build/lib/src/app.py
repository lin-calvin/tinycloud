from flask import Flask
import dav
import vfs
import auth_pam
from mod_manger import mod_manger as mm
import config
import faulthandler
import sys
from gevent.pywsgi import WSGIServer
import os
import copy

faulthandler.enable()



#Prase config
config.load_conf(os.getcwd()+"/config.yaml")
auth_type=config.conf["auth"]["type"]
if auth_type!=None:
    mm.load_mod(auth_type)
    auth=getattr(mm,auth_type).auth()
else:
    auth=None

fs=vfs.fs()
for _fs in config.conf["storages"]:
    mm.load_mod(_fs['type'])
    opts=copy.copy(_fs)
    opts.pop('type')
    opts.pop('name')
    fs.mount(_fs['type'],_fs['name'],opts)


#mm.load_mod("fs.fs_local")
#fs.mount("fs.fs_local","local",{"path":"/home/calvin"})
#fs.mount("fs_ftp","ftpfs",{"host":"localhost","port":9999})

app = Flask(__name__)
dav_route=dav.dav(fs,auth=auth)

app.route("/dav/<path:path>",methods=["GET","PUT","PROPFIND","DELETE","MKCOL"])(dav_route.request)
app.route("/dav/",methods=["GET","PUT","PROPFIND","OPTIONS","DELETE","MKCOL"])(dav_route.request)

if __name__=="__main__":

    WSGIServer(('127.0.0.1', 8988), app).serve_forever()
