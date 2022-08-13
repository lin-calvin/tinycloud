DEF_CONFIG=['~/.config/tinycloud','conf','/etc/tinycloud']

import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, redirect, url_for, send_file, request, make_response
from flask.logging import default_handler
import argparse
import faulthandler
import sys
from gevent.pywsgi import WSGIServer
import os
import copy
import base64
import logging

import dav
import vfs
import mod_manger
import confmgr

import acl
import utils

faulthandler.enable()

logging.basicConfig(filename='logger.log', level=logging.INFO)

class tinycloud(Flask):
    def __init__(self, confdir):
        super().__init__(__name__)

        self.mm = mod_manger.mod_manger()
        self.conf=utils.load_conf(os.path.join(confdir + "/config.yaml"))
        auth_type = self.conf["auth"]["type"]
        if auth_type != None:
            self.mm.load_mod(auth_type)
            self.auth = getattr(self.mm, auth_type).auth()
        else:
            self.auth = None
        self.confmgr=confmgr.confmgr(self.conf,auth=self.auth)
        if os.path.exists(os.path.join(confdir,"acl.yaml")):
            self.acl = acl.acl(os.path.join(confdir,"acl.yaml"))
        self.vfs = vfs.fs(mod_manger=self.mm)
        self.dav = dav.dav(self)
        for _fs in self.conf["storages"]:
            self.mm.load_mod(_fs["type"])
            opts = copy.copy(_fs)
            opts.pop("type")
            opts.pop("name")
            self.vfs.mount(_fs["type"], _fs["name"], opts)
        self.register_blueprint(self.dav.api)
        self.add_url_rule("/", view_func=self.main_page)
        self.add_url_rule("/api/confmgr",view_func=self.confmgr, methods=["GET","POST"])
        self.after_request(self.hook_request)
    def main_page(self):
        res=utils.chk_auth(self.auth)
        if res:
            return res
        try:
            return send_file("static/index.html")
        except FileNotFoundError:
            return 'Frontend file dosn\'t installd'
    def hook_request(self,response):
        response.headers['Server']="Tinycloud"
        return response
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config")
    args = parser.parse_args()
    if args.config:
        conf_dir = args.config
    else:
        conf_dir = "conf"
    if not os.path.exists(conf_dir):
        for i in DEF_CONFIG:
            if os.path.exists(i):
                conf_dir=i
                break
    if not os.path.exists(conf_dir):
        print(sys.argv[0]+": "+conf_dir+": No such file or directory")
        exit(255)
    tc = tinycloud(conf_dir)
    print(
        "Server is run at http://{}:{}".format(
            tc.conf["http"]["addr"], tc.conf["http"]["port"]
        )
    )
    WSGIServer(
        (tc.conf["http"]["addr"], tc.conf["http"]["port"]), tc
    ).serve_forever()


if __name__ == "__main__":
    main()
