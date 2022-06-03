from flask import render_template,request,make_response,Response
import errno
import base64
import json
class dav():
    def __init__(self,fs,auth=False):
        self.auth=auth
        self.fs=fs
    def request(self,subpath=""):
        print(subpath)
        if self.auth:
            if  request.headers.get("Authorization"):
                pw=request.headers["Authorization"]
                print(pw)
                username,password=base64.b64decode(pw[6:]).decode("utf8",'ignore').split(":")
                res=self.auth.do_auth(username,password)
            else:
                resp=make_response("Need auth")
                resp.headers["WWW-Authenticate"]=r'Basic realm="Secure Area"'
                return resp,401
        if request.method=="PROPFIND": #返回目录下的文件
            ret=self.fs.list(subpath)
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
            resp=self.fs.read(subpath)
            if subpath=="":
                return ""
            if resp==-1:
                return "",404
            return Response(resp)
        if request.method=="PUT":
            if type(self.fs.write(subpath,request.stream))==int:
                return '',404
            return ""
        if request.method=="DELETE":
            self.fs.delete(subpath)
            return ""
        if request.method=="MKCOL":
            self.fs.mkdir(subpath)
