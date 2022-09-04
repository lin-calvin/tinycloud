from flask import render_template, request, make_response, Response, Blueprint
import errno
import base64
import json
import utils
import mimetypes
import os


class Dav:
    def __init__(self,fs,acl=None,auth=None,blueprint=True,secret=None):
        if blueprint:
            self.api=Blueprint('dav', __name__, url_prefix='/dav')
            self.api.add_url_rule(
                "/<path:path>",
                methods=["GET", "PUT", "PROPFIND", "DELETE", "MKCOL"],
                view_func=self,
            )
            self.api.add_url_rule(
                "/",
                methods=["GET", "PUT", "PROPFIND", "DELETE", "MKCOL"],
                view_func=self,
            )

        self.auth = auth
        self.acl = acl
        self.fs = fs
        self.secret=secret
        self.__name__ = ""
    def __call__(self, path=""):
        path = os.path.normpath("/" + path)
        if ".." in path:
            return "", 400
        if self.auth:
            try:
                res=utils.chk_auth(self.auth,secret=self.secret)
                if not res:
                    return "",403
            except KeyError:
                    return "", 403
            utils.fs_context.username=utils.get_passwd()[0]
        else:
            if not utils.fs_context.username:
                utils.fs_context.username = None
        if self.acl:
            res = self.acl.check(path, utils.fs_context.username)
            if not res:
                return "", 403
        try:            
            if request.method == "PROPFIND":  # 返回目录下的文件
                ret = self.fs.list(path)
                if type(ret) == int:
                    if ret == -1:
                        return "", 404
                if request.args.get("json_mode"):
                    return {"files": ret}
                return render_template("dav_respone", **{"files": ret}), 207
            if request.method == "OPTIONS":  # 确定webdav支持
                resp = make_response()
                resp.headers["DAV"] = "1,2"
                return resp
            if request.method == "GET":
                resp,length = self.fs.read(path)
                if path == "":
                    return ""
                if resp == -1:
                    return "", 404
                resp=Response(resp, mimetype=mimetypes.guess_type(path)[0])
                resp.content_length=length
                return resp
            if request.method == "PUT":
                ret = self.fs.write(path, request.stream)
                if type(ret) == int:
                    return "", 404
                return ""
            if request.method == "DELETE":
                self.fs.delete(path)
                return ""
            if request.method == "MKCOL":
                self.fs.mkdir(path)
                return ""
        except Exception as e:
            e=type(e)
            if e==PermissionError:
                return "",403
            if e==FileNotFoundError:
                return "",404
            return 400
