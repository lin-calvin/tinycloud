import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
import hashlib
import argparse

from main import DEF_CONFIG


def load_users():
    config_path = TINYCLOUD.confdir
    if os.path.exists(config_path + "/users.json"):
        with open(config_path + "/users.json") as users:
            globals()["auth"] = json.load(users)

def password_hash(password:str):
    return hashlib.sha256(password.encode()).hexdigest()

def init():
    load_users()


class AuthBuiltin:
    def do_auth(self,username, password):
        if not username in auth:
            return False
        if password_hash(password)==auth[username]:
            return True


def adduser_cmd(args):
    username, password = args.username, args.password
    password = password_hash(password)
    if os.path.exists(conf_dir + "/users.json"):
        with open(conf_dir + "/users.json", "r") as userfile:
            users = json.load(userfile)
            users[username] = password
        with open(conf_dir + "/users.json", "w") as userfile:
            json.dump(users, userfile)
    else:
        with open(conf_dir + "/users.json", "w") as userfile:
            users = {username: password}
            json.dump(users, userfile)


if __name__ == "__main__":
    preaser = argparse.ArgumentParser()
    preaser.add_argument("-config", "-c")
    usermgr = preaser.add_subparsers()
    adduser = usermgr.add_parser("adduser")
    adduser.add_argument("username")
    adduser.add_argument("password")
    adduser.set_defaults(func=adduser_cmd)
    args = preaser.parse_args()
    if args.config:
        conf_dir = args.config
    else:
        for i in DEF_CONFIG:
            if os.path.exists(i):
                conf_dir = i
                break
    args.func(args)

PROVIDE = {"api": ..., "auth": AuthBuiltin}  # TODO
