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

def generate_jwt(payload,serect):
    payload=base64.b64encode(json.dumps(payload).encode()).decode()
    header=base64.b64encode(r'{"typ":"JWT","alg":"HS256"}'.encode()).decode()
    serect=hmac.new(serect.encode(),(".".join([header,payload])+serect).encode(),digestmod="SHA256").digest()
    serect=base64.b64encode(serect).decode()
    return ".".join([header,payload,serect])
def chech_jwt(jwt,serect):
    payload=base64.b64decode(jwt.split('.')[1]).decode()
    i=generate_jwt(json.loads(payload),serect)
    if i==jwt:
        return True
    return False
def time_as_rfc(timestamp: int):
    """
    Convert timestamp to RFC2822 format
    """
    return email.utils.format_datetime(datetime.datetime.fromtimestamp(timestamp))
def chk_auth(auth,ret='Need auth'):
    if auth:
        if request.headers.get("Authorization"):
            pw = request.headers["Authorization"]

            username, password = (
                base64.b64decode(pw[6:]).decode("utf8", "ignore").split(":")
            )
            res = auth.do_auth(username, password)
            if not res:
                resp = make_response("Need auth")
                resp.headers["WWW-Authenticate"] = r'Basic realm="Secure Area"'
                return resp, 401
        else:
            resp = make_response("Need auth")
            resp.headers["WWW-Authenticate"] = r'Basic realm="Secure Area"'
            return resp, 401
def get_http_passwd():
    pw = request.headers["Authorization"]
    return base64.b64decode(pw[6:]).decode("utf8", "ignore").split(":")


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
