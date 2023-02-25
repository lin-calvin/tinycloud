import errno
import base64
import json
import utils
import mimetypes
import os
import traceback

from quart import render_template, request, make_response, Response, Blueprint

import utils


class Dav:
    """
    The WebDav implementation
    """

    def __init__(
        self, fs, acl=None, auth=None, blueprint=True, secret=None, url_prefix="/dav"
    ):
        if blueprint:
            self.api = Blueprint("dav", "dav", url_prefix=url_prefix)
            for route in ["", "/", "/<path:path>"]:
                self.api.add_url_rule(
                    route,
                    methods=["GET", "PUT", "PROPFIND", "DELETE", "MKCOL", "OPTIONS"],
                    view_func=self.__call__,
                )
        self.url_prefix = url_prefix
        self.auth = auth
        self.acl = acl
        self.fs = fs
        self.secret = secret
        self.__name__ = ""

    async def __call__(self, path="", url_prefix_override=None):
        path = os.path.normpath("/" + path)
        if ".." in path:
            return "", 400
        if self.auth:
            try:
                res = utils.chk_auth(request,self.auth, secret=self.secret)
                if not res:
                    return Response(
                        "", 401, {"WWW-Authenticate": 'Basic realm="Tinycloud"'}
                    )
            except KeyError:
                return "", 403
            utils.fs_context.username = utils.get_passwd(request)[0]
        else:
            if not utils.fs_context.username:
                utils.fs_context.username = None
        if self.acl:
            res = self.acl.check(path, utils.fs_context.username)
            if not res:
                return "", 403
        try:
            if request.method == "PROPFIND":  # 返回目录下的文件
                ret = await self.fs.list(path)
                if type(ret) == int:
                    if ret == -1:
                        return "", 404
                if request.args.get("json_mode"):
                    return {"files": ret}
                if await self.fs.isdir(path):
                    ret.append(
                        {
                            "type": "dir",
                            "path": path,
                            "time": 0,
                            "name": "",
                        }
                    )
                    for i in ret:
                        i["path"] = path + "/" + i["name"]
                else:
                    ret[0]["path"] = path
                return (
                    await render_template(
                        "dav_respone",
                        **{
                            "files": ret,
                            "url_prefix": url_prefix_override or self.url_prefix,
                            "normpath": os.path.normpath,
                            "guess_type": mimetypes.guess_type,
                            "time_as_rfs": utils.time_as_rfc,
                        }
                    ),
                    207,
                )
            if request.method == "OPTIONS":
                resp = make_response()
                resp.headers["DAV"] = "1,2"
                return resp
            if request.method == "GET":
                file, length = await self.fs.read(path)
                if path == "":
                    return ""

                async def reader():
                    while 1:
                        data = await file.read(utils.calc_size("1M"))
                        if not data:
                            if hasattr(file, "close"):
                                await file.close()
                            break
                        yield data

                resp = Response(reader(), mimetype=mimetypes.guess_type(path)[0])
                if length >= 0:
                    resp.content_length = length
                return resp
            if request.method == "PUT":
                ret = await self.fs.write(path, request.stream)
                return ""
            if request.method == "DELETE":
                self.fs.delete(path)
                return ""
            if request.method == "MKCOL":
                self.fs.mkdir(path)
                return ""
        except Exception as e:
            e = type(e)
            if e == PermissionError:
                return "", 403
            if e == FileNotFoundError:
                return "", 404
            traceback.print_exc()
            return str(e), 500
