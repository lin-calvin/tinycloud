import os
import shutil
import time
from utils import *
from . import fs_local

class fs:
    def __init__(self):
        self.homes = {}
        self.fs_local=fs_local.fs(path='/')
        with open("/etc/passwd") as passwd:
            for i in passwd.readlines():
                i = i.split(":")
                self.homes[i[0]] = i[5]

    def get_home(self, user):
        if user in self.homes:
            return self.homes[user]
        raise FileNotFoundError

    def isdir(self, path):
        home = self.get_home(fs_context.username)
        path = os.path.join(home, path)
        return self.fs_local.isdir(path)

    def list(self, path="/"):
        res = []
        home = self.get_home(fs_context.username)
        real_path = home + "/" + path
        return self.fs_local.list(real_path)
    def read(self, path, chunk_size="1M"):
        home = self.get_home(fs_context.username)
        real_path=os.path.join(home, path)
        return self.fs_local.read(real_path,chunk_size)
    def write(self, path, stream, chunk_size="1M"):
        home = self.get_home(fs_context.username)
        if home == -1:
            return -1
        filename = os.path.join(home, path)
        file = open(filename, "wb")
        self.fs_local.write(filename,stream,chunk_size)
        shutil.chown(filename, user=fs_context.username)

    def delete(self, path):
        home = self.get_home(fs_context.username)
        if home == -1:
            return -1
        os.remove(os.path.join(home, path))
        return "OK"

    def mkdir(self, path):
        home = self.get_home(fs_context.username)
        if home == -1:
            return -1
        os.mkdir(os.path.join(home, path))
        return "OK"


PROVIDE = {"fs": fs}
