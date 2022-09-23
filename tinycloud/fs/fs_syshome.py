import os
import sys
import shutil
from utils import fs_context,time_as_rfc
from . import fs_local
import app

TINYCLOUD: app.Tinycloud


class FsSyshome:
    def __init__(self):
        self.homes = self.get_homes()
        self.fs_local = fs_local.FsLocal(path="/")

    def get_homes(self):
        homes = {}
        if (
            os.uname().sysname == "Linux"
            and type(TINYCLOUD.auth).__name__ != "AuthBuiltin"
        ):
            with open("/etc/passwd") as passwd:
                for i in passwd.readlines():
                    i = i.split(":")
                    homes[i[0]] = i[5]
        if type(TINYCLOUD.auth).__name__ == "AuthBuiltin":
                users = TINYCLOUD.mm.require_mod("auth_builtin").auth
                for i in users:
                    if "home" in users[i]:
                        homes[i] = users[i]["home"]
        return homes

    def get_home(self, user):
        if user in self.homes:
            return self.homes[user]
        raise FileNotFoundError
    def isdir(self, path):
        home = self.get_home(fs_context.username)
        path = os.path.join(home, path)
        return self.fs_local.isdir(path)

    def list(self, path="/"):
        try:
            home = self.get_home(fs_context.username)
        except FileNotFoundError:
            name="User {} dosn't have home".format(fs_context.username)
            return  [{
                        "type": "broken",
                        "name": name,
                        "path": path+"/"+name,
                        "size": 0,
                        "time": time_as_rfc(0),
                    }]
        real_path = home + "/" + path
        res = []
        for i in self.fs_local.list(real_path):
            i["path"] = i["path"][len(home) :]
            res.append(i)
        return res

    def prop(self, path):
        home = self.get_home(fs_context.username)
        path = os.path.join(home, path)
        return self.fs_local.prop(path)

    def read(self, path, chunk_size="1M"):
        home = self.get_home(fs_context.username)
        real_path = os.path.join(home, path)
        return self.fs_local.read(real_path, chunk_size)

    def write(self, path, stream, chunk_size="1M"):
        home = self.get_home(fs_context.username)
        filename = os.path.join(home, path)
        self.fs_local.write(filename, stream, chunk_size)
        shutil.chown(filename, user=fs_context.username)

    def delete(self, path):
        home = self.get_home(fs_context.username)
        os.remove(os.path.join(home, path))

    def mkdir(self, path):
        home = self.get_home(fs_context.username)
        os.mkdir(os.path.join(home, path))


PROVIDE = {"fs": FsSyshome}
