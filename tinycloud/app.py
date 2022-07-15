import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask,redirect,url_for,send_file,request,make_response
import argparse
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

class tinycloud():
    def __init__(self,confdir):
        self.app = Flask(__name__)
        config.load_conf(os.path.join(confdir+"/config.yaml"))
        auth_type=config.conf["auth"]["type"]
        if auth_type!=None:
            mm.load_mod(auth_type)
            self.auth=getattr(mm,auth_type).auth()
        else:
            self.auth=None
        self.acl=acl.acl()
        self.fs=vfs.fs()
        self.dav=dav.dav(self.fs,auth=self.auth,acl=self.acl)
        for _fs in config.conf["storages"]:
            mm.load_mod(_fs['type'])
            opts=copy.copy(_fs)
            opts.pop('type')
            opts.pop('name')
            self.fs.mount(_fs['type'],_fs['name'],opts)
        self.app.add_url_rule("/dav/<path:path>",methods=["GET","PUT","PROPFIND","DELETE","MKCOL"],view_func=self.dav)
        self.app.add_url_rule("/dav/",methods=["GET","PUT","PROPFIND","DELETE","MKCOL"],view_func=self.dav)
        self.app.add_url_rule("/",view_func=self.main_page)
    def main_page(self):
        if self.auth:
            if  request.headers.get("Authorization"):
                pw=request.headers["Authorization"]
                username,password=base64.b64decode(pw[6:]).decode("utf8",'ignore').split(":")
                res=self.auth.do_auth(username,password)
                if not res:
                    resp=make_response("Need auth")
                    resp.headers["WWW-Authenticate"]=r'Basic realm="Login required"'
                    return resp,401
            else:
                resp=make_response("Need auth")
                resp.headers["WWW-Authenticate"]=r'Basic realm="Login required"'
                return resp,401
        return send_file('static/index.html')


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--config")
    args = parser.parse_args()
    if args.config:
        conf_dir=args.config
    else:
        conf_dir="conf"
    tc=tinycloud(conf_dir)
    app=tc.app
    print("Server is run at http://{}:{}".format(config.conf["http"]["addr"], config.conf["http"]["port"]))
    WSGIServer((config.conf["http"]["addr"], config.conf["http"]["port"]), app).serve_forever()
