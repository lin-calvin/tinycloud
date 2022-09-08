DEF_CONFIG = ["/home/calvin/.config/tinycloud", "conf", "/etc/tinycloud"]
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import os
import copy
import logging
import logging.handlers
import json
import signal
from flask import Flask, request
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

# log = logging.handlers.SysLogHandler(address="/dev/log")
# logging.getLogger().addHandler(log)
# logging.basicConfig(filename='/dev/stdout', level=logging.INFO)


class Tinycloud(Flask):
    def __init__(self, confdir):
        super().__init__(__name__)
        self._on_exit = []
        self.mm = mod_manger.mod_manger(self)
        self.confdir = confdir
        self.conf = utils.load_conf(os.path.join(confdir + "/config.yaml"))
        self.secret = self.conf["secret"]
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
        share_api = self.mm.require_mod("share", "api")()
        self.register_blueprint(share_api)

        self.register_blueprint(self.dav.api)

        self.add_url_rule("/", view_func=self.main_page)
        self.add_url_rule(
            "/api/confmgr", view_func=self.confmgr, methods=["GET", "POST"]
        )
        self.add_url_rule("/api/auth/login", view_func=self.login, methods=["POST"])
        self.add_url_rule(
            "/api/auth/check", view_func=self.check_login, methods=["POST"]
        )
        self.after_request(self.hook_request)

    def main_page(self):
        try:
            with open(
                os.path.dirname(os.path.abspath(__file__)) + "/static/index.html"
            ) as file:
                data = file.read()
        except FileNotFoundError:
            return "Frontend file dosn't installed"
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

    def check_login(self):
        token = json.loads(request.data.decode())["token"]
        if utils.chk_jwt(token, self.secret):
            return {"status": 200}, 200
        return {"status": 403}, 403

    def hook_request(self, response):
        response.headers["Server"] = "Tinycloud"
        return response

    def on_exit(self, func):
        if not hasattr(func, "__call__"):
            raise TypeError("Func must be callable")
        self._on_exit.append(func)

    def exit(self):
        for func in self._on_exit:
            func()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config")
    args = parser.parse_args()
    if args.config:
        conf_dir = args.config
    else:
        for i in DEF_CONFIG:
            if os.path.exists(i):
                conf_dir = i
                break
    if not os.path.exists(conf_dir):
        print(sys.argv[0] + ": " + conf_dir + ": No such file or directory")
        exit(255)
    tc = Tinycloud(conf_dir)

    def on_exit(*_):
        tc.exit()
        sys.exit()

    for sig in [signal.SIGTERM, signal.SIGINT]:
        signal.signal(sig, on_exit)
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
        tc.exit()
        sys.exit()


if __name__ == "__main__":
    main()
