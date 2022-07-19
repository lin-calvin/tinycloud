import email.utils
import datetime
import math
from flask import request,make_response
import base64
def calc_size(size: str):
    """
    Claculate size from a string
    """
    B = 1
    K = 1024
    M = K * 1024
    G = K * 1024
    return eval(str(int(size[:-1])) + "*" + size[-1])


def time_as_rfc(timestamp: int):
    """
    Convert timestamp to RFC2822 format
    """
    return email.utils.format_datetime(datetime.datetime.fromtimestamp(timestamp))
def chk_auth(auth):
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


def clean_path(str):
    output = []
    for i in range(len(str)):
        if str[i] == "/" and i != len(str) and str[i + 1] == "/":
            continue
        output.append(str[i])
    return "".join(output)


fs_context=type.__new__(type,'fs_context',(),{'username':str()})()
