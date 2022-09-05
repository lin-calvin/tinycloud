from flask import request
from utils import chk_auth


class confmgr:
    __name__ = "confmgr"

    def __init__(self, config, auth=None):
        self.config = config
        self.auth = auth

    def __call__(self):
        res = chk_auth(self.auth)
        if res:
            return res
        if request.method == "GET":
            return self.config
        if request.method == "POST":
            self.config.conf = request.json
            self.config.save_conf()
            return "OK "
