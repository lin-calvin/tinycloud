import email.utils
import datetime
import math
import json
from flask import request
import base64
import yaml
import hmac
import random
import string


def calc_size(size: str):
    """
    Claculate size from a string
    """
    units = {"B": 1, "K": 1024, "M": 1048576, "G": 1073741824}
    return int(size[:1]) * units[size[-1]]


def generate_jwt(payload: dict, secret: str):
    """
    Generate json web token
    """
    payload = base64.b64encode(json.dumps(payload).encode()).decode()
    header = base64.b64encode(r'{"typ":"JWT","alg":"HS256"}'.encode()).decode()
    secret = hmac.new(
        secret.encode(),
        (".".join([header, payload]) + secret).encode(),
        digestmod="SHA256",
    ).digest()
    secret = base64.b64encode(secret).decode()
    return ".".join([header, payload, secret])


def chk_jwt(jwt: str, secret: str):
    """
    Check if the jwt is valid
    """
    payload = base64.b64decode(jwt.split(".")[1]).decode()
    i = generate_jwt(json.loads(payload), secret)
    if i == jwt:
        return True
    return False


def time_as_rfc(timestamp: int):
    """
    Convert timestamp to RFC2822 format
    """
    return email.utils.format_datetime(datetime.datetime.fromtimestamp(timestamp))


def chk_auth(auth, secret=None):
    """
    Check if the credentials provides by clients is valid
    """
    res = False
    if "Authorization" in request.headers:
        pw = request.headers["Authorization"]
        if pw.startswith("Basic"):
            username, password = (
                base64.b64decode(pw[6:]).decode("utf8", "ignore").split(":")
            )
            res = res | auth.do_auth(username, password)
        if pw.startswith("Bearer"):
            if not secret:
                raise AttributeError("jwt authorization require a secret")
            res = res | chk_jwt(pw[7:], secret)
    if request.cookies.get("token"):
        res = res | chk_jwt(request.cookies["token"], secret)
    return res


def get_passwd():
    """
    Get username and passwd from client
    """
    if 1:  # try:
        if "Authorization" in request.headers:
            pw = request.headers["Authorization"]
            if pw.startswith("Basic"):
                return base64.b64decode(pw[6:]).decode("utf8", "ignore").split(":")
            if pw.startswith("Bearer"):
                payload = base64.b64decode(pw[6:].split(".")[1]).decode(
                    "utf8", "ignore"
                )
                payload = json.loads(payload)
                return payload["username"], ""
        if request.cookies.get("token"):
            token = request.cookies["token"]
            payload = base64.b64decode(token[6:].split(".")[1]).decode("utf8", "ignore")
            payload = json.loads(payload)
            return payload["username"], ""


#    except (KeyError,base64.binascii.Error):
#        raise ValueError()
#    raise ValueError()


def load_conf(path):
    file = open(path, "r")
    conf = yaml.safe_load(file.read())
    file.close()
    return conf


def save_conf(conf, file_name):
    file = open(file_name, "w")
    yaml.dump(conf, file)


def random_string(length):
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )


fs_context = type.__new__(type, "fs_context", (), {"username": str()})()
