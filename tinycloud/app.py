DEF_CONFIG = ["~/.config/tinycloud", "conf", "/etc/tinycloud"]

import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import os
import copy
import base64
import logging
import logging.handlers

from flask import Flask, redirect, url_for, send_file, request, make_response
from flask.logging import default_handler
import argparse
import faulthandler
from gevent.pywsgi import WSGIServer


import dav
import vfs
import mod_manger
import confmgr
import acl
import utils

faulthandler.enable()

log = logging.handlers.SysLogHandler(address="/dev/log")
# logging.getLogger().addHandler(log)
# logging.basicConfig(filename='/dev/stdout', level=logging.INFO)


class Tinycloud(Flask):
    def __init__(self, confdir):
        super().__init__(__name__)
        self.mm = mod_manger.mod_manger(self)
        self.conf = utils.load_conf(os.path.join(confdir + "/config.yaml"))
        self.secret=self.conf['secret']
        auth_type = self.conf["auth"]["type"]
        if auth_type != None:
            self.mm.load_mod(auth_type)
            self.auth = self.mm.require_mod(auth_type, "auth")()
        else:
            self.auth = None

        self.confmgr = confmgr.confmgr(self.conf, auth=self.auth)

        if os.path.exists(os.path.join(confdir, "acl.yaml")):
            self.acl = acl.acl(os.path.join(confdir, "acl.yaml"))

        self.vfs = vfs.fs(mod_manger=self.mm)
        self.dav = dav.Dav(
            fs=self.vfs, auth=self.auth, acl=self.acl, secret=self.secret
        )
        for _fs in self.conf["storages"]:
            self.mm.load_mod(_fs["type"])
            opts = copy.copy(_fs)
            opts.pop("type")
            opts.pop("name")
            fs = self.mm.require_mod(_fs["type"], "fs")
            self.vfs.mount(fs, _fs["name"], opts)
        self.mm.load_mod("share")
        share_api=self.mm.require_mod("share","api")()
        self.register_blueprint(share_api)

        self.register_blueprint(self.dav.api)

        self.add_url_rule("/", view_func=self.main_page)
        self.add_url_rule(
            "/api/confmgr", view_func=self.confmgr, methods=["GET", "POST"]
        )
        self.add_url_rule("/api/login", view_func=self.login, methods=["POST"])
        self.after_request(self.hook_request)

    def main_page(self):
        try:
            with open("static/index.html") as file:
                data = file.read()
        except FileNotFoundError:
            return "Frontend file dosn't installed"
        try:
            res = utils.chk_auth(self.auth, secret=self.conf["secret"])
        except KeyError:
            res = False
        if not res:
            data = data.replace(
                "</head>", r"<script>window.tcNeedLogin=true</script></head>"
            )
        return data

    def login(self):
        try:
            username, password = utils.get_passwd()
        except ValueError:
            return {"status": 403}, 403
        res = self.auth.do_auth(username, password)
        if not res:
            return {"status": 403}, 403
        token = utils.generate_jwt({"username": username}, self.conf["secret"])
        return {"status": 200, "token": token}

    def hook_request(self, response):
        response.headers["Server"] = "Tinycloud"
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
                conf_dir = i
                break
    if not os.path.exists(conf_dir):
        print(sys.argv[0] + ": " + conf_dir + ": No such file or directory")
        exit(255)
    tc = Tinycloud(conf_dir)
    print(
        "Server is run at http://{}:{}".format(
            tc.conf["http"]["addr"], tc.conf["http"]["port"]
        )
    )
    try:
        WSGIServer(
            (tc.conf["http"]["addr"], tc.conf["http"]["port"]), tc
        ).serve_forever()
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
