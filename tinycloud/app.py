import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask,redirect,url_for,send_file,request,make_response
import dav
import vfs
import mod_manger
import config
import faulthandler
import sys
from gevent.pywsgi import WSGIServer
import os
import copy
import base64
import acl

faulthandler.enable()
mm=mod_manger.mod_manger


#Prase config

config.load_conf("conf"+"/config.yaml")
auth_type=config.conf["auth"]["type"]
if auth_type!=None:
    mm.load_mod(auth_type)
    auth=getattr(mm,auth_type).auth()
else:
    auth=None


acl=acl.acl()
fs=vfs.fs()
for _fs in config.conf["storages"]:
    mm.load_mod(_fs['type'])
    opts=copy.copy(_fs)
    opts.pop('type')
    opts.pop('name')
    fs.mount(_fs['type'],_fs['name'],opts)



app = Flask(__name__)
dav_route=dav.dav(fs,auth=auth,acl=acl)

app.route("/dav/<path:path>",methods=["GET","PUT","PROPFIND","DELETE","MKCOL"])(dav_route.request)
app.route("/dav/",methods=["GET","PUT","PROPFIND","OPTIONS","DELETE","MKCOL"])(dav_route.request)
@app.route("/")
def main_page():
    #path=utils.clean_path(path)
    if auth:
        if  request.headers.get("Authorization"):
            pw=request.headers["Authorization"]
            username,password=base64.b64decode(pw[6:]).decode("utf8",'ignore').split(":")
            res=auth.do_auth(username,password)
            if not res:
                resp=make_response("Need auth")
                resp.headers["WWW-Authenticate"]=r'Basic realm="Login required"'
                return resp,401
        else:
            resp=make_response("Need auth")
            resp.headers["WWW-Authenticate"]=r'Basic realm="Login required"'
            return resp,401
    return send_file('static/index.html')
@app.route("/logout")
def logout():
    resp=make_response("Need auth")
    resp.headers["WWW-Authenticate"]=r'Basic realm="Login required"'
    return resp,401
if __name__=="__main__":
    print("Server is run at http://{}:{}".format(config.conf["http"]["addr"], config.conf["http"]["port"]))
    WSGIServer((config.conf["http"]["addr"], config.conf["http"]["port"]), app).serve_forever()
