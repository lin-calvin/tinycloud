from flask import Flask
import dav
import vfs
from core import auth_pam
from core import mod_manger
from core import config
import faulthandler

faulthandler.enable()

mm=mod_manger.mod_manger()



config.load_conf(  "./config.yaml")
auth_type=config.conf["auth"]["type"]
mm.load_mod(auth_type,"./core/")
auth=getattr(mm,auth_type).auth()


fs=vfs.fs(mm)
#mm.load_mod("fs_local","./fs/")
#mm.load_mod("fs_ftp","./fs/")

#fs.mount("fs_local","local",{"path":"./"})
#fs.mount("fs_ftp","ftpfs",{"host":"localhost","port":9999})

app = Flask(__name__)
dav_route=dav.dav(fs,auth=auth)

app.route("/dav/<path:subpath>",methods=["GET","PUT","PROPFIND","DELETE","MKCOL"])(dav_route.request)
app.route("/dav/",methods=["GET","PUT","PROPFIND","OPTIONS","DELETE","MKCOL"])(dav_route.request)

#@app.route('/')
#def hello_world():
#    return 'Hello, World!'
