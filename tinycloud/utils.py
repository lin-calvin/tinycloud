import email.utils
import datetime
import math
import json
from flask import request,make_response
import base64
import yaml
import hmac

def calc_size(size: str):
    """
    Claculate size from a string
    """
    B = 1
    K = 1024
    M = K * 1024
    G = K * 1024
    return eval(str(int(size[:-1])) + "*" + size[-1])

def generate_jwt(payload,secret):
    payload=base64.b64encode(json.dumps(payload).encode()).decode()
    header=base64.b64encode(r'{"typ":"JWT","alg":"HS256"}'.encode()).decode()
    secret=hmac.new(secret.encode(),(".".join([header,payload])+secret).encode(),digestmod="SHA256").digest()
    secret=base64.b64encode(secret).decode()
    return ".".join([header,payload,secret])
def chk_jwt(jwt,secret):
    payload=base64.b64decode(jwt.split('.')[1]).decode()
    i=generate_jwt(json.loads(payload),secret)
    if i==jwt:
        return True
    return False
def time_as_rfc(timestamp: int):
    """
    Convert timestamp to RFC2822 format
    """
    return email.utils.format_datetime(datetime.datetime.fromtimestamp(timestamp))
def chk_auth(auth,secret=None):
    if "Authorization" in request.headers:
        pw = request.headers["Authorization"]
        if pw.startswith("Basic"):
            username, password = (
                base64.b64decode(pw[6:]).decode("utf8", "ignore").split(":")
            )
            res = auth.do_auth(username, password)
            return res
        if pw.startswith("Bearer"):
            if not secret:
                raise AttributeError("jwt authorization require a secret")
            res=chk_jwt(pw[7:],secret)
            return res
    if request.cookies['token']:
        return chk_jwt(request.cookies['token'],secret)

    raise KeyError()
def get_passwd():
    if 1:#try:
        if "Authorization" in request.headers:
            pw = request.headers["Authorization"]
            if pw.startswith("Basic"):
                return base64.b64decode(pw[6:]).decode("utf8", "ignore").split(":")
            if pw.startswith("Bearer"):
                payload=base64.b64decode(pw[6:].split(".")[1]).decode("utf8", "ignore")
                payload=json.loads(payload)
                return payload["username"],""
        if request.cookies["token"]:
            token=request.cookies["token"]
            payload=base64.b64decode(token[6:].split(".")[1]).decode("utf8", "ignore")
            payload=json.loads(payload)
            return payload["username"],""
#    except (KeyError,base64.binascii.Error):
#        raise ValueError()
#    raise ValueError()
class log:
    @staticmethod
    def box_message(txt):
        if len(txt) < 15:
            a = math.floor((15 - len(txt)) / 2)
            a = " " * a
            txt = a + txt + a
        print("#" * (len(txt) + 2))
        print("#" + txt + "#")
        print("#" * (len(txt) + 2))

def load_conf(path):
    file = open(path,"r")
    conf= yaml.safe_load(file.read())
    file.close()
    return conf
def save_conf(conf,file_name):
    file=open(file_name,"w")
    yaml.dump(conf,file)


fs_context=type.__new__(type,'fs_context',(),{'username':str()})()
