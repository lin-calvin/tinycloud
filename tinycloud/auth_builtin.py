import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import json
import hashlib
import argparse

from main import DEF_CONFIG

TINYCLOUD = None
auth = None


def load_users():
    config_path = TINYCLOUD.confdir
    if os.path.exists(config_path + "/users.json"):
        with open(config_path + "/users.json") as users:
            globals()["auth"] = json.load(users)


def password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def init():
    load_users()


class AuthBuiltin:
    def do_auth(self, username, password):
        if username not in auth:
            return False
        print(password_hash(password))
        if password_hash(password) == auth[username]["password"]:
            return True
        return False


def adduser_cmd(args):
    username, password = args.username, args.password
    password = password_hash(password)
    user = {"password": password}
    if args.home:
        user["home"] = args.home
    if os.path.exists(conf_dir + "/users.json"):
        with open(conf_dir + "/users.json", "r") as userfile:
            try:
                users = json.load(userfile)
            except json.decoder.JSONDecodeError:
                print('"users.json" invlid')
                exit(255)
            users[username] = user
        with open(conf_dir + "/users.json", "w") as userfile:
            json.dump(users, userfile)
    else:
        with open(conf_dir + "/users.json", "w") as userfile:
            users = {username: user}
            json.dump(users, userfile)


def deluser_cmd(args):
    username = args.username
    if not os.path.exists(conf_dir + "/users.json"):
        print("No such user")
        exit(255)
    with open(conf_dir + "/users.json", "r") as userfile:
        try:
            users = json.load(userfile)
        except json.decoder.JSONDecodeError:
            print('"users.json" invlid')
            exit(255)
        if username not in users:
            print("No such user")
            exit(255)
        del users[username]
    with open(conf_dir + "/users.json", "w") as userfile:
        json.dump(users, userfile)


if __name__ == "__main__":
    preaser = argparse.ArgumentParser()
    preaser.add_argument("-config", "-c")
    usermgr = preaser.add_subparsers()
    adduser = usermgr.add_parser("adduser")
    adduser.add_argument("username")
    adduser.add_argument("password")
    adduser.add_argument("--home", help="Set a home that which used by fs_syshome")
    adduser.set_defaults(func=adduser_cmd)

    deluser = usermgr.add_parser("deluser")
    deluser.add_argument("username")
    deluser.set_defaults(func=deluser_cmd)

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
