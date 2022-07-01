#import pam
import os
import utils
class auth():
    def __init__(self):
        pass
        """
            if os.uname().sysname!="Linux":
                raise RuntimeError("auth_pam only work on linux")
            if os.getuid()!=0:
                utils.log.box_message("Run as a non-root user,pam may not work")
        """
    def do_auth(self,user,passwd):
        return True#return pam.authenticate(user,passwd)
