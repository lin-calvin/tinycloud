from flask import render_template,request,make_response,Response
import errno
import base64
import json
import utils
import mimetypes
import os
class dav():
    def __init__(self,fs,auth=None,acl=None):
        self.auth=auth
        self.acl=acl
        self.fs=fs
        self.__name__=""
    def __call__(self,path=""):
        path=os.path.normpath("/"+path)
        if ".." in path:
            return "",400
        #path=utils.clean_path(path)
        if self.auth:
            if  request.headers.get("Authorization"):
                pw=request.headers["Authorization"]
                username,password=base64.b64decode(pw[6:]).decode("utf8",'ignore').split(":")
                res=self.auth.do_auth(username,password)
                if not res:
                    resp=make_response("Need auth")
                    resp.headers["WWW-Authenticate"]=r'Basic realm="Secure Area"'
                    return resp,401
            else:
                resp=make_response("Need auth")
                resp.headers["WWW-Authenticate"]=r'Basic realm="Secure Area"'
                return resp,401
        if self.acl:
            res=self.acl.check(path,username)
            if not res:
                return "",403
        if request.method=="PROPFIND": #返回目录下的文件
            ret=self.fs.list(path)
            if type(ret)==int:
                if ret==-1:
                    return "",404
            if request.args.get("json_mode"):
                return {"files":ret}
            return render_template("dav_respone",**{"files":ret}),207
        
        if request.method=="OPTIONS": #确定webdav支持
            resp=make_response()
            resp.headers["DAV"]="1,2"
            return resp
        if request.method=="GET":

            resp=self.fs.read(path)
            if path=="":
                return ""
            if resp==-1:
                return "",404
            print(mimetypes.guess_type(path)[0])
            return Response(resp,mimetype=mimetypes.guess_type(path)[0])
        if request.method=="PUT":
            print(1)
            ret=self.fs.write(path,request.stream)
            print(ret)
            if type(ret)==int:
                return '',404
            return ""
        if request.method=="DELETE":
            self.fs.delete(path)
            return ""
        if request.method=="MKCOL":
            self.fs.mkdir(path)
            return ""
